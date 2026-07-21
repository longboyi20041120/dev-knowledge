---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/ai-agent"
  - "#状态/草稿"
created: 2026-07-21
updated: 2026-07-21
---

# AI Agent 评估方法

> Agent 写得出来，但测不测得准才是工程能力的体现。 | **面试重要度：高** | 预计阅读：4 分钟

## 核心观点（来自 VB Transform 2026，LangChain/Conviva/CoreWeave）

### 1. 从"单 trace 评分"到"对比分析"

传统的 Agent 评估方式：跑一次对话，人工打分。问题是——**一次对话看起来完美，系统可能仍然是坏的**。

2026 年的新范式：**对比分析**（Contrastive Analysis）。把一组用户的 Agent 对话和基线对比，发现单次评分看不出的系统性缺陷。

### 2. Eval 是活的 PRD，不是一次性测试

评估标准应该像产品需求文档一样持续迭代：
- Agent 行为变了 → eval 跟着变
- 不是"写完测试就完了"，而是"eval 定义了产品规格"

### 3. 低成本裁判模型

用大模型评估 Agent 输出很贵。新做法：
- 微调小模型（如 Qwen 7B）做 guardrail 裁判
- 成本比 GPT-5 低 **10-100 倍**
- 准确率可接受（简单判断场景）

### 4. Human-in-the-Loop 仍然必须

即使 Agent 全自动运行，以下场景必须有人的位置：
- **受监管行业**：金融、医疗的合规审查
- **信任构建**：Agent 说"我做了 X"，人需要确认
- **系统记忆**：人的反馈是 Agent 长期记忆的重要来源

## 面试会怎么问

| 问题 | 回答框架 |
|------|---------|
| Agent 怎么评估好坏？ | 单 trace 评分基础 → 对比分析进阶 → eval 即 PRD |
| 怎么降低评估成本？ | 小模型做裁判（Qwen 微调），大模型只在复杂场景用 |
| Agent 上线后怎么监控？ | Human-in-the-loop + 对比分析 + 指标看板 |

## 相关笔记

- [[工作学习/AI-Agent系统性学习路线|AI Agent 系统性学习路线]] — Phase 2 Module 4: Planning & Evaluation
- [[前沿信息/Agentic-AI与RAG|Agentic AI 与 RAG]] — Agent 反思循环
