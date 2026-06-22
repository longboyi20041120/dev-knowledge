---
tags:
  - "#类型/技术"
  - "#技术/ai-agent"
  - "#状态/草稿"
  - token优化
created: 2026-06-22
updated: 2026-06-22
status: draft
---

# AI Agent Token 优化生态

## 为什么重要

AI Agent 循环执行时最大的成本是 Token 消耗。你正在做的 Shill 项目本质上就是一个 Token 控制器——所以理解这个生态很关键。

## 关键项目

### headroom — LLM Token 压缩引擎

- GitHub: `chopratejas/headroom`
- 本周 +10k star，总 26k
- 6 种压缩算法：上下文剪枝、冗余检测、语义压缩等
- 削减率：60-95%
- **与 Shill 的关系**：可以作为 Shill 的底层压缩模块。Shill 控制"是否跑"，headroom 控制"跑得省不省"

### LMCache — KV-Cache 复用

- 跨 GPU/CPU/SSD/Redis/S3 的 KV-cache 缓存
- 减少长上下文和 RAG 场景的推理延迟
- 降低重复计算，间接省 Token

### agentsview — Agent 会话账本

- 本地 SQLite 记录 20+ 种 Agent 的调用
- 追踪：cost、tokens、sessions
- **与 Shill 的关系**：如果 Shill 要监控 Loop 开销，agentsview 的思路可以复用

## Token 浪费的根因分析

| 根因 | 占比 | 解决思路 |
|------|------|----------|
| 重复上下文 | 40% | headroom 式压缩 |
| 无效循环 | 30% | Shill 收敛检测 |
| 提示词过长 | 20% | 精简系统提示词 |
| 其他 | 10% | 日志分析 |

## 相关笔记

- [[灵感/shill-loop优化工具|Shill — Loop 优化工具]]
- [[灵感/自动知识采集工作流|自动知识采集工作流]]
