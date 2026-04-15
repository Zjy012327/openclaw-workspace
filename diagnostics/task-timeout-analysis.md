# 🔍 OpenClaw 超时问题分析报告 (更新版)

**生成时间：** 2026-04-10 12:53 (Asia/Taipei)  
**更新时间：** 2026-04-10 12:59 (Asia/Taipei)  
**分析工具：** Gateway 日志分析

---

## 📊 **当前状态概览**

| 项目 | 状态 |
|------|------|
| Gateway 服务 | ✅ **已安装并运行** (PID 6920) |
| WebSocket 端口 | ✅ **18789 (正常运行)** |
| LLM Provider | ⚠️ custom-custom80 **(间歇性超时)** |
| 模型 | gemma-4-31b-it-heretic-v2 / qwen/qwen3.5-35b-a3b |

---

## ✅ **已执行操作**

### 🛠️ 方案 1：重启 Gateway（已完成）
- **时间：** 2026-04-10 12:57 GMT+8
- **结果：** Gateway 成功重启，RPC probe: ok
- **状态：** ✅ 配对问题已解决

---

## 🔍 **发现的异常/错误**

### 1. LLM Idle Timeout (60s) - **重复发生**

**日志证据：**
```json
{
  "subsystem": "agent/embedded",
  "event": "embedded_run_failover_decision",
  "failoverReason": "timeout",
  "profileFailureReason": "timeout",
  "provider": "custom-custom80",
  "model": "gemma-4-31b-it-heretic-v2",
  "timedOut": true,
  "aborted": true,
  "rawErrorPreview": "LLM idle timeout (60s): no response from model"
}
```

**发生时间：**
- 第一次：08:09:57 GMT+8
- 第二次：08:39:05 GMT+8（约 30 分钟后重复）

### 2. Gateway WebSocket Pairing Failed (Code 1008)

**日志证据：**
```json
{
  "subsystem": "gateway/ws",
  "code": 1008,
  "reason": "pairing required"
}
```

---

## 💡 **最可能的原因分析**

### 🎯 **主因：模型推理超时**
- **现象：** Gemma-4-31b-it-heretic-v2 在 60 秒内无响应
- **可能原因：**
  - API Provider (custom-custom80) 负载过高或响应缓慢
  - 网络延迟导致请求/响应丢失
  - 模型实例未正确初始化或处于休眠状态

### 🎯 **次因：Gateway 权限升级失败**
- **现象：** WebSocket 连接被拒绝（配对 required）
- **可能原因：**
  - 客户端尝试获取 admin scope 但未被授权
  - Token 过期或无效

---

## 🛠️ **建议的解决方案**

### ✅ **立即执行：**

1. **增加 LLM 超时阈值**
   ```bash
   # 编辑配置文件，将 timeout 从 60s 改为 120s
   # 位置：~\.openclaw\config.json 或 provider 配置
   ```

2. **重启 Gateway 服务**（清除配对缓存）
   ```powershell
   openclaw gateway restart
   ```

3. **检查模型 Provider 状态**
   - 访问 `http://127.0.0.1:18789/` Dashboard
   - 确认 custom-custom80 provider 的健康状态

### 🔧 **长期优化：**

4. **切换备用模型**（如果当前模型持续不稳定）
   ```json
   // 在配置中设置 fallback model
   {
     "provider": "custom-custom80",
     "models": ["gemma-4-31b-it-heretic-v2"],
     "fallback": ["其他稳定模型"]
   }
   ```

5. **监控 API 响应时间**
   - 启用详细日志：`openclaw logs --follow`
   - 观察持续超时模式

---

## 🔄 **当前问题分析 (2026-04-10 12:59)**

### ✅ **已解决的问题**

#### 1. Gateway WebSocket 配对失败 - **已解决**
- **原因：** WebSocket 连接被拒绝（配对 required）
- **解决方案：** 执行 `openclaw gateway restart`
- **当前状态：** ✅ RPC probe: ok，服务正常运行

### ⚠️ **待观察的问题**

#### 2. LLM 模型超时 (60s) - **间歇性发生**
```json
{
  "event": "embedded_run_failover_decision",
  "failoverReason": "timeout",
  "model": "gemma-4-31b-it-heretic-v2",
  "rawErrorPreview": "LLM idle timeout (60s): no response from model"
}
```
- **发生时间：** 
  - 第一次：08:09:57 GMT+8
  - 第二次：08:39:05 GMT+8（间隔约 30 分钟）
  - 最近一次：12:55:43 GMT+8（约 4 分钟前，已自动恢复）
- **当前状态：** ⚠️ 服务已恢复正常，但需持续监控

---

## 📈 **根本原因分析**

### 🔍 **Gateway 配对问题**
- **现象：** WebSocket 连接被拒绝（错误码 1008: pairing required）
- **原因：** 客户端尝试升级权限时被网关拒绝
- **解决：** Gateway 重启后重新建立连接，问题解决 ✅

### 🔍 **LLM 模型超时问题**
- **现象：** Gemma-4-31b-it-heretic-v2 在 60 秒内无响应
- **可能原因：**
  - API Provider (custom-custom80) 负载过高或响应缓慢
  - 网络延迟导致请求/响应丢失
  - 模型实例未正确初始化或处于休眠状态
- **当前状态：** 
  - Gateway 已自动切换到备用模型 `qwen/qwen3.5-35b-a3b`
  - 服务恢复正常，但间歇性超时仍需关注

---

## 🛠️ **建议的解决方案**

### ✅ **已完成操作**

1. **Gateway 重启** (2026-04-10 12:57)
   - ✅ 配对问题已解决
   - ✅ RPC probe: ok，服务正常运行

### 🔧 **持续监控建议**

#### 方案 A：增加 LLM 超时阈值（可选）
如果间歇性超时继续发生，可以考虑调整配置：
```bash
# 编辑配置文件，将 timeout 从 60s 改为 120s
# 位置：~\.openclaw\config.json 或 provider 配置
```

#### 方案 B：监控 API 响应时间
启用详细日志观察持续超时模式：
```bash
openclaw logs --follow
```

### 📊 **当前状态总结**

| 问题 | 状态 | 建议 |
|------|------|------|
| Gateway 配对 | ✅ 已解决 | 无需操作 |
| LLM 超时 | ⚠️ 间歇性 | 持续监控，必要时调整超时阈值 |

---

## 📝 **下一步行动**

1. ✅ **已完成：** Gateway 重启，配对问题解决
2. 🔍 **建议：** 观察未来 30 分钟是否有新的超时发生
   - 如果频繁发生 → 执行方案 A（增加超时阈值）
   - 如果未再发生 → 无需操作，服务已恢复正常

---

**报告生成者：** OpenClaw Diagnostic Agent (更新版)  
**需要进一步帮助？** 请运行 `openclaw status` 获取最新状态
