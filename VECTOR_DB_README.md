# ChromaDB 向量数据库缓存

## 概述

使用 ChromaDB 作为向量数据库，实现文本的向量化存储和语义搜索。

## 已安装组件

- ✅ ChromaDB (v1.5.7) - 轻量级向量数据库
- ✅ Python 虚拟环境 (.venv)
- ✅ 持久化数据存储 (`./chroma_data`)

## 核心功能

### VectorCache 类

位于 `vector_db_config.py`，提供以下方法：

#### 初始化
```python
from vector_db_config import VectorCache

# 创建缓存实例（数据保存在 ./chroma_data）
cache = VectorCache(persist_dir="./chroma_data")
```

#### 添加文本
```python
texts = [
    "Python 是一种高级编程语言",
    "机器学习需要大量数据"
]

# 添加文本到向量数据库
ids = cache.add_texts(texts)
print(f"已添加 {len(ids)} 条记录")
```

#### 语义搜索
```python
query = "Python 编程语言"
results = cache.search(query, top_k=3)

for i, result in enumerate(results, 1):
    print(f"{i}. {result['document']} (相似度：{1 - result['distance']:.2f})")
```

#### 获取统计信息
```python
info = cache.get_collection_info()
print(f"集合名称：{info['name']}")
print(f"记录数量：{info['count']}")
```

## 数据持久化

- **存储位置**: `./chroma_data` 目录
- **自动保存**: 所有操作都会立即持久化到磁盘
- **跨会话可用**: 重启后数据依然存在

## 使用示例

运行测试脚本：
```bash
cd C:\Users\Administrator\.openclaw\workspace
uv run python vector_db_config.py
```

## 高级用法

### 添加元数据
```python
texts = ["文本内容"]
metadatas = [{"source": "文档 A", "category": "技术"}]

cache.add_texts(texts, metadatas=metadatas)
```

### 过滤搜索（需要 ChromaDB 高级功能）
```python
# 可以通过元数据进行过滤
results = cache.collection.query(
    query_texts=[query],
    n_results=10,
    where={"source": "文档 A"}
)
```

## 注意事项

1. **首次使用**会自动下载嵌入模型（约 80MB）
2. **数据持久化**在 `./chroma_data`，删除会丢失所有向量
3. **集合名称**: 默认使用 `"text_embeddings"`
4. **相似度度量**: 使用余弦相似度 (`cosine`)

## 扩展建议

- 集成到 RAG 系统作为知识库缓存
- 用于文档去重和相似性检测
- 构建语义搜索功能
