---
tags:
  - "#类型/灵感"
  - "#状态/草稿"
  - AI-agent
  - 开源
  - 工具开发
created: 2026-06-22
updated: 2026-06-22
status: draft
---

# Shill — AI Agent Loop 优化工具

## 一句话

一个精准控制 AI Agent 循环执行的工具，解决 Loop 模式的 token 浪费、跑偏失控、无法收敛等问题。发 GitHub 开源。

## 背景

"Loop"（AI Agent 自主循环）是 2025-2026 年最火的 AI 编程模式——让 AI 不断迭代直到完成任务。但实际使用中问题很大：

| 问题 | 表现 |
|------|------|
| Token 浪费 | Loop 在无关细节上反复消耗 token，一次循环烧掉几万 |
| 跑偏失控 | AI 改着改着偏离了原始目标，越改越错 |
| 无法收敛 | 永远不会说"够了"，一直改下去 |
| 缺乏可见性 | 你不知道 AI 在第几轮、改了什么、还剩多少 token |
| 难以调试 | Loop 出了问题不知道是哪一轮引入的 |

## Shill 的核心思路

**Shill = Shell + Will**。像 Shell 一样控制 AI 的 Will（意志），让 Loop 可控、可观测、可终止。

## 核心机制

### 1. Token 预算硬限制

```
shill loop --budget 100k "帮我重构这个模块"
→ 剩余 80k 时提醒
→ 剩余 20k 时强制总结收尾
→ 耗尽时自动 commit 当前进度，不给 AI 继续跑
```

### 2. 收敛检测

每轮循环后自动检测：
- **输出变化量**：这轮改动和上轮相比，diff 行数 < 阈值？→ 收敛了
- **语义相似度**：AI 连续两轮输出内容高度相似？→ 在打转，终止
- **目标偏离度**：检查当前输出和原始目标的关联度 → 偏了拉回来

### 3. 检查点机制

```
Round 1 → checkpoint → Round 2 → checkpoint → Round 3 (跑偏) → rollback to Round 2
```

每轮自动 commit git，跑偏了能回滚。

### 4. 实时面板

```
┌─ Shill Loop Monitor ────────────────────┐
│ Rounds: 5/20         Budget: 62k/100k    │
│ 本轮改动: +120 -45 行                     │
│ 收敛度: 87% (▊▊▊▊▊▊▊▊▊▊)               │
│ 目标偏离: 低  ✓                          │
│ 预估剩余: 3 轮                            │
│ [pause] [skip] [stop]                    │
└──────────────────────────────────────────┘
```

## 技术方案

### 定位

不是一个独立 Agent，而是**包裹在现有 Agent 外面的一层控制器**。

```
用户 → Shill → AI Agent (Claude Code / Codex / etc.)
         ↓
    监控、计量、收敛检测、回滚
```

### 实现方式

两种可能路径：

**路径 A: CLI 工具（推荐先做）**
- 独立二进制/脚本，调用 AI Agent CLI
- 解析输出、管理状态、控制执行
- 语言：Rust 或 Go（性能 + 单二进制发布）
- 优点：简单、通用、好发布

**路径 B: MCP Server**
- 作为一个 MCP 工具注册到 Claude Desktop
- Agent 自己调用 Shill 工具来检查预算和收敛
- 优点：深度集成

### 核心代码结构

```
shill/
├── src/
│   ├── loop.rs         # 循环控制器
│   ├── budget.rs       # Token 预算管理
│   ├── converge.rs     # 收敛检测
│   ├── observer.rs     # 输出监控和 diff
│   └── ui.rs           # 实时面板 (TUI)
├── examples/
└── README.md
```

## 差异化

和现有方案的对比：

| | raw loop | Shill |
|------|----------|-------|
| Token 控制 | 无 | 硬预算 + 预警 |
| 跑偏检测 | 无 | 语义相似度 + 目标对比 |
| 回滚 | 手动 git | 自动 checkpoint |
| 可见性 | 黑盒 | 实时面板 |
| 收敛 | 靠 prompt | 自动检测 |

## 2026年6月 市场验证

本周 GitHub Trending 和 HN 多个信号确认了这个方向：

- **Loop Engineering 崛起**：Claude Code 之父 Boris Cherny 已转向"只写循环，不写 prompt"
- **headroom**（26k star）：Token 压缩 60-95%，可以直接作为 Shill 的底层压缩模块
- **SkillSpector**（NVIDIA）：26% 的 Agent Skill 有安全漏洞——精准控制不是可选项，是必需品
- **agentsview**：Agent 会话账本（cost/token/session 追踪），Shill 的监控面板可以参考

## 下一步

- [ ] 调研 headroom 的压缩算法，评估能否集成到 Shill
- [ ] 研究 Boris Cherny 的 Loop Engineering 文章
- [ ] 确定用路径 A（CLI）还是 B（MCP）
- [ ] 先做一个 MVP：只做 token 预算管理 + 收敛检测
- [ ] 写 README，定义 CLI 接口
- [ ] 创建 GitHub 仓库
- [ ] 考虑做成 Agent Skill 格式（`/shill-loop`），方便分发

## 相关笔记

- [[技术栈/AI-Agent-Token优化|AI Agent Token 优化生态]]
- [[技术栈/Agent-Skill生态|Agent Skill 生态]]
