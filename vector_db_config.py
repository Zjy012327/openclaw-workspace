"""
向量数据库缓存配置 - ChromaDB
用于存储和检索文本的向量表示
"""

import chromadb
from chromadb.config import Settings
from pathlib import Path
import requests


class VectorCache:
    """ChromaDB 向量缓存封装类"""
    
    def __init__(
        self,
        persist_dir: str = "./chroma_data",
        embedding_endpoint: str = None
    ):
        """
        初始化向量数据库
        
        Args:
            persist_dir: 数据持久化目录
        """
        self.persist_path = Path(persist_dir)
        self.persist_path.mkdir(exist_ok=True)
        
        # 创建持久化客户端
        self.client = chromadb.PersistentClient(
            path=str(self.persist_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # 嵌入模型端点配置
        self.embedding_endpoint = embedding_endpoint or "http://localhost:1234/v1/embeddings"
        self._embed_model = None
        
        # 默认集合
        self.collection = self.client.get_or_create_collection(
            name="text_embeddings",
            metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
        )
    
    def _get_embeddings(self, texts: list[str]) -> list[list[float]]:
        """
        获取向量嵌入
        
        Args:
            texts: 文本文本列表
            
        Returns:
            向量列表
        """
        if self.embedding_endpoint and "localhost" not in self.embedding_endpoint:
            # 使用外部嵌入服务
            response = requests.post(
                self.embedding_endpoint,
                json={
                    "input": texts,
                    "model": "text-embedding-nomic-embed-text-v2",
                    "encoding_format": "float"
                },
                timeout=60
            )
            response.raise_for_status()
            data = response.json()
            return [item["embedding"] for item in data["data"]]
        else:
            # 使用 ChromaDB 内置嵌入 (all-MiniLM-L6-v2)
            from chromadb.utils import embedding_functions
            ef = embedding_functions.DefaultEmbeddingFunction()
            return ef(texts)
    
    def add_texts(self, texts: list[str], metadatas: list[dict] = None):
        """
        添加文本到向量数据库
        
        Args:
            texts: 文本文本列表
            metadatas: 元数据列表（可选）
        """
        if not texts:
            return []
        
        # ChromaDB 需要 ID，这里用索引生成
        ids = [f"text_{i}" for i in range(len(texts))]
        
        # ChromaDB 新版本要求元数据不能为空字典
        metas = metadatas if metadatas else [{"source": "default"} for _ in texts]
        
        # 获取向量嵌入
        embeddings = self._get_embeddings(texts)
        
        self.collection.add(
            documents=texts,
            ids=ids,
            metadatas=metas,
            embeddings=embeddings if self.embedding_endpoint else None
        )
        
        return ids
    
    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        搜索最相似的文本
        
        Args:
            query: 查询文本
            top_k: 返回结果数量
            
        Returns:
            搜索结果列表，包含文档、距离和元数据
        """
        # 如果使用外部嵌入服务，需要先获取查询向量
        if self.embedding_endpoint:
            query_embeddings = self._get_embeddings([query])[0]
            results = self.collection.query(
                query_embeddings=[query_embeddings],
                n_results=top_k,
                include=["metadatas", "distances", "documents"]
            )
        else:
            results = self.collection.query(
                query_texts=[query],
                n_results=top_k,
                include=["metadatas", "distances", "documents"]
            )
        
        # 检查结果是否为空
        if not results["documents"] or not results["documents"][0]:
            return []
        
        docs = results["documents"][0]
        dists = results["distances"][0] if results["distances"] else [0.0] * len(docs)
        metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
        
        return [
            {
                "document": doc,
                "distance": dist,
                "metadata": meta
            }
            for doc, dist, meta in zip(docs, dists, metas)
        ]
    
    def get_collection_info(self) -> dict:
        """获取集合信息"""
        return {
            "name": self.collection.name,
            "count": self.collection.count(),
            "metadata": self.collection.metadata
        }


# 使用示例
if __name__ == "__main__":
    # 初始化缓存（恢复使用内置的 all-MiniLM-L6-v2 嵌入模型）
    cache = VectorCache(persist_dir="./chroma_data")
    
    # 添加一些测试文本
    test_texts = [
        "Python 是一种高级编程语言，适合数据科学和 Web 开发",
        "机器学习需要大量的数据和计算资源",
        "向量数据库用于存储和检索高维向量",
        "ChromaDB 是一个轻量级的向量数据库",
        "自然语言处理是人工智能的重要分支"
    ]
    
    cache.add_texts(test_texts)
    print(f"已添加 {cache.get_collection_info()['count']} 条记录")
    
    # 搜索测试
    query = "Python 编程语言"
    results = cache.search(query, top_k=3)
    
    print(f"\n搜索 '{query}' 的结果:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['document']} (距离: {result['distance']:.4f})")
