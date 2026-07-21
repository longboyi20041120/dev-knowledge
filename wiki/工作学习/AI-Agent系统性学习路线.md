---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/ai-agent"
  - "#状态/草稿"
created: 2026-07-21
updated: 2026-07-21
---

# AI Agent 系统性学习路线

> 从零到能干活、能面试。课程全部来自 YouTube 六大权威来源：Andrew Ng、李宏毅、李沐、Andrej Karpathy、Microsoft、Hugging Face。 | **面试重要度：高** | 预计阅读：10 分钟

## RAG 为什么放在第四阶段？

先回答一个常见疑问：**RAG 不是不重要，恰恰相反——它是 Agent 的"大脑皮层"**。

没有 RAG 的 Agent = 金鱼脑（上下文满了就忘）。之所以不放在第一或者第二阶段学，是因为：

```
先理解"Agent 会做什么" → 再理解"Agent 缺什么" → 最后学"怎么补"

  Phase 1-2: Agent 能做决策、能调工具了
       ↓
  发现问题：工具调完就忘、用户偏好记不住、
           文档太长塞不进上下文
       ↓
  Phase 3: RAG 解决的是上面这些痛点的方案
       ↓
  这时候学 RAG，你知道它解决什么问题，
  而不是死记"检索→增强→生成"八个字
```

这也是 Andrew Ng 课程的设计逻辑：Reflection → Tool Use → Planning → 才深入 RAG。

---

## 六大权威来源速查

| 讲师/频道 | 身份 | 课程数 | 最适合 |
|-----------|------|--------|--------|
| **Andrew Ng** (DeepLearningAI) | DeepLearning.AI 创始人 | 5 模块 + 多门短课 | **核心系统学习，首选** |
| **李宏毅** | 台湾大学教授 | 1 门 | 零基础入门，比喻教学 |
| **李沐** | 亚马逊首席科学家 | 1 门 | 论文精读 + 工业级代码 |
| **Andrej Karpathy** | OpenAI 创始成员 | 1 门（4 小时） | 从零手写 AutoGPT |
| **Microsoft** | 官方 | 14 集 | 结构化入门，覆盖面广 |
| **Hugging Face** | 开源社区 | 10 小时 | 框架使用者 |

---

## 学习全景图

```
Phase 0  前置基础（Python / API / Git）
  │  🎥 无专门课程，靠你知识库里现有笔记
  ↓
Phase 1  认知建立（1 周）
  │  🎥 李宏毅「AI Agent 系统设计 2025」
  │  🎥 Microsoft「AI Agents for Beginners」14 集
  ↓
Phase 2  Agentic Design Patterns（3-4 周）★ 核心
  │  🎥 Andrew Ng「Agentic AI」5 模块
  │     ① Foundations    ② Reflection
  │     ③ Tool Use       ④ Planning & Evaluation
  │     ⑤ Multi-Agent Collaboration
  ↓
Phase 3  RAG 专项突破（2 周）
  │  🎥 DeepLearning.AI「Building and Evaluating Advanced RAG」
  │  🎥 DeepLearning.AI「MCP: Build Rich-Context AI Apps」
  ↓
Phase 4  框架与多 Agent（2-3 周）
  │  🎥 DeepLearning.AI「AI Agents in LangGraph」
  │  🎥 DeepLearning.AI「Multi AI Agent Systems with crewAI」
  ↓
Phase 5  底层原理与论文（3-4 周，选学）
  │  🎥 李沐「动手学 AI Agent」（论文精读 + PyTorch 实现）
  │  🎥 Andrej Karpathy「From LLMs to Agents」（从零手写）
  │  🎥 UC Berkeley CS294「LLM Agents」（研究生级）
  ↓
Phase 6  实战项目（持续）
  │  项目一：个人 RAG 知识库问答
  │  项目二：多 Agent 自动化工作流
  │  项目三：开源 Agent Skill 发布
  ↓
Phase 7  面试准备
```

---

## Phase 0：前置基础

| 技能 | 最低要求 | 你的知识库 |
|------|---------|-----------|
| Python | 函数、类、装饰器、async/await、类型注解 | [[工作学习/编程语言/Python基础\|Python 基础]] |
| HTTP & API | GET/POST、JSON、Bearer Token、SSE 流式 | ⚠️ 缺，需要补 |
| JSON Schema | 解析、校验、嵌套结构遍历 | Python 基础里有 |
| Git | clone、branch、commit、PR | [[工作学习/工程基础/Git基础与协作\|Git 基础]] |

---

## Phase 1：认知建立（1 周）

**目标：搞懂 Agent 到底是什么，能做什么，和传统程序有什么区别。**

| 顺序 | 课程 | 频道 | 时长 | 学什么 |
|------|------|------|------|--------|
| 1 | **AI Agent 系统设计 2025** | 李宏毅 (Hung-yi Lee) | ~3h | 用复仇者联盟比喻多 Agent、用哈利波特比喻工具调用，零基础友好 |
| 2 | **AI Agents for Beginners** | Microsoft Developer (freeCodeCamp) | 14 集 | 基础架构、工具使用、记忆、规划、多 Agent、多框架对比 |

### 学完自检

- [ ] 能用一句话解释 Agent 和 Chatbot 的区别
- [ ] 能画出 Agent 的核心循环：感知 → 决策 → 执行 → 观察
- [ ] 知道 Tool Use、Memory、Planning 分别解决什么问题

### 配套阅读

- Lilian Weng: [LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/) — 必读综述

---

## Phase 2：Agentic Design Patterns（3-4 周）★ 最核心

**目标：系统掌握 Andrew Ng 总结的四大 Agentic 设计模式，这是整个学习路线的脊梁骨。**

### 🎥 课程：Andrew Ng「Agentic AI with Andrew Ng」

> **YouTube 搜：DeepLearningAI 频道，或直接去 deeplearning.ai 平台（有证书）**

| 模块 | 设计模式 | 你会做什么 | 建议时间 |
|------|---------|-----------|---------|
| **Module 1** | Foundations | 任务分解、自主程度分级、评估体系 | 3 天 |
| **Module 2** | **Reflection** | 自省 Agent（可视化、抽认卡、PII 保护、自纠正 SQL） | 5 天 |
| **Module 3** | **Tool Use** | 邮件 Agent (FastAPI)、搜索 Agent、SQL Agent、MCP 集成、Function Calling | 5 天 |
| **Module 4** | **Planning & Evaluation** | 超参数优化、F1-score 追踪、生产级评估 | 5 天 |
| **Module 5** | **Multi-Agent** | 客服流水线（Planner → Coder → Executor → Reflector） | 5 天 |

技术栈：Python + FastAPI + PostgreSQL + Docker + Tavily API + arXiv API + OpenAI API

### 学完自检

- [ ] 能手写 ReAct 循环（Think → Act → Observe → Repeat）
- [ ] 能用 OpenAI/Claude API 实现 Function Calling
- [ ] 能设计一个带自省能力的 Agent（执行 → 自查 → 修正）
- [ ] 能搭一个多 Agent 流水线

### 你的知识库里已有

- [[工作学习/AI使用技巧|AI 使用技巧]] — Prompt 方法论
- [[前沿信息/Agentic-AI与RAG|Agentic AI 与 RAG]] — Prompt/Skill/Agentic Workflow 关系

---

## Phase 3：RAG 专项突破（2 周）

**目标：解决 Agent 的记忆和知识问题。RAG 是 Agent 的"资料柜"。**

### 🎥 核心课程

| 顺序 | 课程 | 频道 | 内容 |
|------|------|------|------|
| 1 | **Building and Evaluating Advanced RAG** | DeepLearningAI (YouTube) | RAG 全流程：索引策略、检索优化、生成质量评估、生产部署 |
| 2 | **MCP: Build Rich-Context AI Apps with Anthropic** | DeepLearningAI (YouTube) | MCP 协议实操：让 Agent 连接外部工具和数据源 |

### 必学技术栈

| 技术 | 用途 | 优先级 |
|------|------|--------|
| **Embedding 模型** | 文本→向量 | ⭐⭐⭐ |
| **向量数据库** | 存储 + 检索（Chroma 入门 → Milvus/Pinecone 进阶） | ⭐⭐⭐ |
| **RAG 流程** | 索引 → 检索 → 重排 → 增强 → 生成 | ⭐⭐⭐ |
| **Agentic RAG** | Agent 主动决定检索什么、什么时候检索、怎么用检索结果 | ⭐⭐ |
| **MCP 协议** | 工具调用标准化（USB 之于外设） | ⭐⭐ |

### 记忆层级全景

```
工作记忆（上下文窗口）
  └── 短期记忆（会话摘要 + 滑动窗口）
        └── 长期记忆（向量库 + RAG）
              └── 知识库（领域文档 + SOP）
```

### 学完自检

- [ ] 能从零搭一个 RAG 系统：文档切片 → Embedding → 向量库 → 检索 → 生成
- [ ] 知道分块策略（chunk size、overlap）对检索质量的影响
- [ ] 能解释 Agentic RAG 比传统 RAG 强在哪里
- [ ] 能写一个简单 MCP Server

### 关联笔记

- [[前沿信息/Agentic-AI与RAG|Agentic AI 与 RAG]] — RAG vs Agentic RAG 对比
- [[工作学习/AI-Agent-Token优化|AI Agent Token 优化]] — Token 成本与上下文管理

---

## Phase 4：框架与多 Agent（2-3 周）

**目标：学完原生 API 后，用框架提效。多 Agent 协作处理复杂任务。**

### 🎥 核心课程

| 顺序 | 课程 | 频道 | 内容 |
|------|------|------|------|
| 1 | **AI Agents in LangGraph** | DeepLearningAI (YouTube) | ReAct 模式、状态持久化、人机协同、复杂工作流 |
| 2 | **Multi AI Agent Systems with crewAI** | DeepLearningAI (YouTube) | 角色分工、任务编排、多 Agent 协作 |

### 框架选型指南

| 框架 | 定位 | 推荐度 |
|------|------|--------|
| **LangGraph** | 状态图驱动的 Agent 编排，精确控制流程 | ⭐⭐⭐ 首选 |
| **CrewAI** | 角色分工，像管理团队一样管 Agent | ⭐⭐⭐ |
| **AutoGen** (Microsoft) | 对话驱动，聊天式多 Agent 协作 | ⭐⭐ |
| **LangChain** | Agent 全家桶，生态最大 | ⭐⭐ |
| **Claude Agent SDK** | Anthropic 官方，简洁直接 | ⭐⭐ |
| **Dify / Coze** | 低代码搭建，快速原型 | ⭐ |

### 多 Agent 协作模式

| 模式 | 怎么工作 | 场景 |
|------|---------|------|
| 顺序管道 | A → B → C | 爬虫→分析→报告 |
| 辩论评审 | 多个 Agent 各自回答，投票 | 代码审查 |
| 分工协作 | 各有专长，调度者分配 | 前后端分离开发 |
| 层次管理 | Manager → Workers | 复杂项目 |

### 学完自检

- [ ] 能用 LangGraph 搭一个多步骤 Agent 工作流
- [ ] 能用 CrewAI 搭一个多 Agent 协作系统
- [ ] 知道什么时候用框架、什么时候用原生 API

### 关联笔记

- [[前沿信息/Claude-Code进阶体系|Claude Code 进阶体系]] — Skill、子智能体、Hooks
- [[前沿信息/Agent-Skill生态|Agent Skill 生态]] — Skill 正在成为新的 npm 包

---

## Phase 5：底层原理与论文（3-4 周，选学）

**目标：源码级理解，能读论文、能手写核心组件。面试区分度的关键。**

### 🎥 三层次递进

| 层次 | 课程 | 讲师 | 内容 | 适合 |
|------|------|------|------|------|
| **论文 + 代码** | 动手学 AI Agent | 李沐 | PyTorch 实现多 Agent 框架，AutoGPT/ReAct 论文精读，Jupyter Notebook | 想看懂论文 + 会写代码的 |
| **从零手写** | From LLMs to Agents | Andrej Karpathy | 4 小时直播，VS Code 断点调试，递归任务分解，从零实现 AutoGPT | 想知道底层到底怎么跑的人 |
| **研究生级** | CS294/194-196 LLM Agents | UC Berkeley | 记忆、规划、安全、评估，学术论文深度 | 想走学术路线或进阶面试 |

### 推荐顺序

```
李沐（论文+代码）→ Karpathy（纯手写）→ Berkeley CS294（学术深度）
```

> **注意**：找工作优先，Phase 5 可以只学李沐的部分。Karpathy 和 Berkeley 等你核心能力扎实了再补。

### 学完自检

- [ ] 能手写 ReAct Agent 的主循环（不依赖框架）
- [ ] 能读 AutoGPT 源码并理解其架构
- [ ] 能说出当前 Agent 研究的 3 个开放问题

---

## Phase 6：实战项目（持续）

### 项目一：个人 RAG 知识库问答（Phase 3 结束后做，1-2 天）

- 对你自己编程知识库做语义搜索 + 问答
- 技术栈：Chroma + Claude API + Python
- 简历写法："基于 RAG + 向量检索的个人知识库问答系统，支持语义搜索和上下文回答"

### 项目二：多 Agent 自动化工作流（Phase 4 结束后做，1-2 周）

- 每日抓取 AI 领域 GitHub Trending → Agent 分析趋势 → 生成日报 → 邮件推送
- 技术栈：CrewAI / LangGraph + GitHub API + 邮件 API
- 简历写法："使用 CrewAI 构建的多 Agent 自动化信息采集与分析系统"

### 项目三（进阶）：发布开源 Agent Skill（Phase 4+ 做）

- 参考 [[前沿信息/Agent-Skill生态|Agent Skill 生态]] 里的 SKILL.md 格式
- 往 Claude Code 社区发布一个 Skill
- 简历亮点：有开源贡献，理解 Agent 生态和 MCP 协议

### 你已经有的

- [[灵感/shill-loop优化工具|Shill]] — 就是一个 Agent 项目（目标→拆解→执行→反思），面试可讲

---

## Phase 7：面试准备

### 高频基础题

| 题目 | 你的回答框架 |
|------|------------|
| 什么是 AI Agent？和 Chatbot 的区别？ | Agent = LLM + 工具 + 记忆 + 决策循环；Chatbot 是被动问答，Agent 能主动规划执行 |
| Function Calling 原理？ | 模型输出工具名+参数 JSON → 程序执行 → 结果回传模型 → 模型继续推理 |
| RAG 流程和常见问题？ | 索引→检索→重排→增强→生成；幻觉、检索不准、分块策略不当 |
| Agent 怎么防跑偏？ | 最大步数限制、token 预算、人工审核节点、评估反馈 |
| Agentic RAG 比传统 RAG 强在哪？ | 主动推理 + 动态工具选择 + 反思纠错 |

### 进阶题（区分度）

| 题目 | 加分点 |
|------|--------|
| MCP 协议的价值？ | 工具调用标准化，解决 Agent 与外部工具的集成问题 |
| Token 成本怎么优化？ | 缓存策略、摘要压缩、合适模型选择、批量处理 |
| 多 Agent 什么时候用？单 Agent 什么时候够？ | 任务可并行/需多视角→多Agent；线性任务→单Agent |

### 项目话术模板

> 我做了一个 **[项目名]**，解决 **[具体痛点]**。
> Agent 架构是 **[用了什么循环、什么工具、什么记忆方案]**。
> 最大的技术难点是 **[具体问题]**，通过 **[你的解法]** 解决。
> 技术栈：**[列表]**。

---

## 持续跟进

| 来源 | 干什么 | 频率 |
|------|--------|------|
| **DeepLearningAI YouTube** | Andrew Ng 新课程首发 | 每月检查 |
| **李沐 YouTube** | 论文精读系列 | 每篇都值得看 |
| **Lilian Weng 博客** | OpenAI 研究员，Agent 方向必读 | 每篇 |
| **Anthropic 官方文档** | Claude API、MCP、Agent SDK | 版本更新时 |
| **GitHub Trending** | 搜 agent、skill、mcp | 每周扫一遍 |
| **Sam Witteveen、AI Jason** YouTube | Agent 最新动态解读 | 碎片时间 |

---

## 相关笔记

- [[前沿信息/Agentic-AI与RAG|Agentic AI 与 RAG]] — Prompt→Skill→Agentic Workflow 演进全景
- [[前沿信息/Agent-Skill生态|Agent Skill 生态]] — Skill 生态趋势，2026 年爆发
- [[前沿信息/Claude-Code进阶体系|Claude Code 进阶体系]] — Claude Code 的 Agent 工程实现
- [[前沿信息/2026年7月AI模型与Agent生态|2026年7月AI模型与Agent生态]] — 最新模型与 Agent 动态
- [[工作学习/AI底层原理|AI 底层原理]] — 神经网络、Transformer 基础
- [[工作学习/AI使用技巧|AI 使用技巧]] — Prompt 方法论与 AI 能力边界
- [[工作学习/AI-Agent-Token优化|AI Agent Token 优化]] — Token 成本控制实操
- [[工作学习/书架与学习路线|书架与学习路线]] — 整体知识体系
- [[灵感/shill-loop优化工具|Shill — Loop 优化工具]] — 你的第一个 Agent 项目
- [[灵感/钢铁侠星期五AI-现有技术栈实现路径|钢铁侠星期五 AI 实现路径]] — Agent 技术栈全景图
