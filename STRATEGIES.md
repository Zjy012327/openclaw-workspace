# OpenClaw API Rate Limit & Timeout 避免策略

## 🎯 核心原则
减少高频访问，优化参数设置，选择可靠来源，监控状态。

---

## 1. 减少高频访问
- ✅ **页面截图代替抓取** - 用 `browser snapshot` 获取视觉信息，而非连续 web_fetch
- ✅ **限制调用次数** - 每次任务不超过 5-8 个工具调用
- ✅ **等待前一个完成** - 不要并行执行多个 web_search/web_fetch

## 2. 优化参数设置
- ✅ **maxChars 控制** - 每个 fetch 设置合理上限（3000-5000）
- ✅ **timeoutMs 设置** - 给 browser/snapshot 设置 timeout（如 10000ms）
- ✅ **safeSearch 调整** - moderate/off 根据需求，避免 strict 导致延迟

## 3. 选择可靠来源
- ✅ **优先 AP News、Reuters、BBC** - 这些网站稳定性高
- ✅ **避免盲目搜索** - 先选定几个关键源，而不是随机尝试
- ✅ **用 web_search 定位 URL** - 先用 search 找到目标页面，再用 fetch/snapshot

## 4. 使用 subagent
- ✅ **长时间任务交给子代理** - 避免主 session token 累积过多
- ✅ **隔离执行** - subagent 有独立上下文和 token 限制

## 5. 监控状态
- ✅ **定期 openclaw status** - 检查 Gateway、Sessions、Token 使用情况
- ✅ **观察 fetch failed 频率** - 超过 30% 失败率时及时止损换策略

## 6. 缓存策略
- ✅ **重复内容不重查** - 同一页面多次访问前检查是否已有缓存
- ✅ **memory 记录结果** - 将新闻摘要保存到 memory/文件，下次直接读取

---

## 📝 执行流程模板

### 新闻查找任务：
1. `openclaw status` → 检查当前状态（Gateway、Token）
2. `browser start` → 启动浏览器
3. `browser open` → 打开 AP News / Reuters
4. `browser snapshot` → 获取页面截图识别头条
5. 如有需要，`web_fetch` → 抓取特定文章详情（限制 maxChars=3000）
6. `write memory/YYYY-MM-DD.md` → 保存结果

### 长时间任务：
1. `sessions_spawn` → 创建 subagent
2. 子代理执行多步骤操作
3. `subagents list` → 检查进度（按需）
4. 收到完成事件后汇总

---

## ⚠️ 失败信号识别
- web_search 连续返回 "fetch failed" → 换策略
- fetch failed 频率 > 30% → 止损
- Token 使用 > 80% → 用 subagent
- 等待时间 > 10s → 设置 timeout

---

## 🌐 **备选搜索：Tavily API**

### **API Key**
```
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
```

### **触发条件**
1. ✅ 先执行上述 6 大策略（browser snapshot + web_search/web_fetch）
2. ⚠️ 如果失败或未得到满意结果
3. 💬 **提示用户：** "是否使用 Tavily API 搜索？"
4. 📝 **等待用户回复** - 只有回复"搜索"后才实际调用
5. ✅ **调用 tavily-search** - 使用上述 API Key

### **执行流程**
```
1. 执行常规策略 → 失败/不满意
2. message send: "是否使用 Tavily API 搜索？"
3. 等待用户回复
4. 如果回复"搜索" → tavily-search(query, count=5)
5. 保存结果到 memory/YYYY-MM-DD.md
```

---

_这个文件我定了。每次执行任务前读取它，遵循这些策略。你觉得行吗？_
