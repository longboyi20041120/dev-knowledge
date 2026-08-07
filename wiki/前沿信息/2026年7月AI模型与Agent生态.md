---
tags:
  - "#用途/前沿"
  - "#类型/技术"
  - "#技术/ai"
created: 2026-07-18
updated: 2026-08-01
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
| **Kimi K3** | 月之暗面 | 开源旗舰，综合能力对标 Claude Fable，1M 上下文窗口，开发者评价极高 |
| **Claude Opus 5** | Anthropic | 7月25日发布，编码与推理大幅提升，配套发布 Claude 5 上下文工程新规 |
| **Gemini 3.6 Flash** | Google | 7月22日同步发布 Flash / Flash-Lite / Flash Cyber 三个变体 |
| **Bonsai 27B** | PrismML | 27B 参数能在手机上跑的模型，推理效率突破 |
| **Inkling** | Thinking Machines | 开源权重模型，社区反响热烈（838赞） |

**关键趋势**：模型能力差距在缩小，国产模型（GLM、Qwen、Kimi K3）在特定基准上有竞争力；开源权重模型的追赶速度超预期。

### 7月下旬补充

- **GPT-5.6 数学突破**：用 prompt 闭合了凸优化领域 30 年未解问题，陶哲轩验证了反例的正确性（Jacobi 猜想）
- **GigaToken**：约 1000 倍加速的 tokenization，开源实现
- **Echo**：用开源模型达到 Fable 级别效果，成本只要 1/3
- **Gemma 4 26B**：可在 2GB RAM 的 M 系列 Mac 上运行
- **Kimi Work**：月之暗面推出 AI 工作台产品，Kimi K3 + 百万 token 上下文

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

- [[wiki/前沿信息/Agent-Skill生态|Agent Skill 生态]]
- [[wiki/前沿信息/AI基础设施-芯片竞赛|AI 基础设施：芯片竞赛]]
- [[wiki/前沿信息/Claude-Code进阶体系|Claude Code 进阶体系]]
- [[wiki/工作学习/AI底层原理|AI 底层原理]]
