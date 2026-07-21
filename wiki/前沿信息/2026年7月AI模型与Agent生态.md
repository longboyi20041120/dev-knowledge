---
tags:
  - "#用途/前沿"
  - "#类型/技术"
  - "#技术/ai"
created: 2026-07-18
updated: 2026-07-18
status: reviewed
---

# 2026年7月AI模型与Agent生态

## 大模型竞争白热化

7月上旬连续发布多款重磅模型：

| 模型 | 发布方 | 亮点 |
|------|--------|------|
| **GPT-5.6** | OpenAI | 旗舰升级，代号 Sol，Sol Ultra 能生成数学猜想的证明（Cycle Double Cover Conjecture） |
| **Claude Sonnet 5** | Anthropic | 同期发布，与 GPT-5.6 正面竞争 |
| **GLM 5.2** | 智谱 | 安全领域基准测试击败 Claude（Semgrep 测试），有对应 Harness 工具 ZCode |
| **Qwen 3.6 27B** | 阿里 | 本地开发最佳性价比选择，被社区广泛推荐 |
| **Leanstral 1.5** | Mistral | 数学证明专用模型 |

**关键趋势**：模型能力差距在缩小，国产模型（GLM、Qwen）在特定基准上有竞争力。

## Agent 工程化成为新焦点

### 从 Prompt 到 Harness

- **Loop Engineering**：精准控制 Agent 循环，避免 token 浪费和跑偏。把 Agent 执行流当作工程系统来设计
- **AI Harness 工程化**：得物等公司已在生产中落地，从"狂野代码"转向"按目标生产"
- **Agent 评估（Evals）**：OpenAI 发文讨论如何从编码基准测试中分离信号与噪声

### 多 Agent 流水线

- Hermes Agent 社区活跃，Skill 生态类似 npm 包爆发
- 中间件系统插入 Agent 执行流成为新模式
- 安全方面：Token 级别的对齐漏洞（BPE tokenization 可被利用）、Agent 行为溯源分析

## 模型推理优化

- **Kara**：滑动窗口 KV Cache 压缩，降低长上下文推理成本
- **ELiTeFormer**：FPGA 上高效 Transformer 推理
- **Mesh LLM**：基于 iroh 的分布式 AI 计算

## 关键链接

- [[前沿信息/Agent-Skill生态|Agent Skill 生态]]
- [[前沿信息/AI基础设施-芯片竞赛|AI 基础设施：芯片竞赛]]
- [[前沿信息/Claude-Code进阶体系|Claude Code 进阶体系]]
- [[工作学习/AI底层原理|AI 底层原理]]
