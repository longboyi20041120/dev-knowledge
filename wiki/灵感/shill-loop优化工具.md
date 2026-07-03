---
tags:
  - "#用途/灵感"
  - "#类型/灵感"
  - "#状态/草稿"
  - AI-agent
  - 开源
  - 工具开发
created: 2026-06-22
updated: 2026-06-26
status: draft
---

# Shill — AI Agent Loop 优化工具

## 一句话

一个开箱即用的 AI Agent 循环控制器——一行命令安装，一句话启动，自动管好 Token 预算、收敛检测、回滚。发 GitHub 开源，任何人 30 秒内能用上。

## 产品理念

### 30 秒能用

```
npm i -g shill                  # 安装
shill "把 README 翻译成英文"     # 直接用
```

不需要配置文件，不需要选模型，不需要理解 token 是什么。默认值覆盖 90% 的场景。

### 渐进式复杂度

```
shill "重构 user-service"                     # 新手：一个命令搞定
shill "重构" --budget 200k --converge 5       # 进阶：调参数
shill loop --agent codex --config ./shill.toml # 高级：配置文件
```

不强迫新手学参数，但给老手留满操作空间。

### 兼容多种 Agent

自动检测用户装了哪些 AI CLI，按优先级选择：

```
检测顺序：claude → codex → copilot → aider → continue
          ↑ 找到就用，没找到试下一个
```

用户也可以手动指定：`shill --agent codex "xxx"`

### 跨平台

Windows、macOS、Linux 都支持。发布方式：
- **npm**：`npm i -g shill`（覆盖所有平台）
- **单文件二进制**：下载直接运行，零依赖（用 Bun 编译）

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

**Shill = Shell + Will**。像 Shell 一样控制 AI 的 Will（意志）。

不只是一个 token 计数器。Shill 的目标是**覆盖 Loop 全部五个环节**——感知、决策、执行、测量、判断——在每个环节提供关键的自动化和安全检查。

## 第一性原理：把 Loop 拆成五个环节

Loop 本质是一个**反馈控制系统**。每一轮都在重复：

```
当前状态 S(t)
    ↓
  [感知]  你看懂了当前的项目全貌了吗？
    ↓
  [决策]  你决定改什么？用户的意思你真的理解了吗？
    ↓
  [执行]  动手改代码，Token 花了多少？改得规范吗？
    ↓
  [测量]  改了之后怎么衡量？改了多少行？趋势如何？
    ↓
  [判断]  继续、回退、还是停？
    ↓
下一轮 S(t+1)  ← 或者结束
```

### 每个环节的失败模式

| 环节 | 理想状态 | 实际会出什么问题 |
|------|----------|------------------|
| **感知** | AI 正确理解全部代码 | 不知道项目结构、漏掉关键依赖、上下文太长忘记前面 |
| **决策** | AI 理解用户意图 | 误解需求、选错方向、过度设计、同时改多个不相关的东西 |
| **执行** | 精准改动 | 引入新 bug、改动范围失控、代码不规范、token 浪费 |
| **测量** | 客观量化进展 | 无法量化、误判完成度 |
| **判断** | 该停就停 | 完美主义不满足、偷懒过早停、反复改同一个地方 |

### 控制论视角：定义 E(t)

定义 E(t) = 第 t 轮 AI 改动的代码行数。这个信号是关键：

```
正常收敛：E(1)=200 → E(2)=80 → E(3)=15 → E(4)=3（比值递减）
震荡：    E(1)=200 → E(2)=180 → E(3)=210 → E(4)=190（在来回改方案）
发散：    E(1)=50 → E(2)=80 → E(3)=120 → E(4)=200（越改越大，失控）
摸鱼：    E(1)=20 → E(2)=18 → E(3)=22 → E(4)=19（无实质进展）
```

### Shill 在每个环节做什么

```
┌─ 感知 ───────────────────────────────────────┐
│ Shill 做的事：扫描项目 → 生成 PROJECT_SUMMARY  │
│ 不调 AI，纯静态分析，免费且确定               │
│ 解决：AI 不知道项目全貌 → 现在知道了           │
└──────────────────────────────────────────────┘
                    ↓
┌─ 决策 ───────────────────────────────────────┐
│ Shill 做的事：                                  │
│   项目总结 + 用户目标 → 发给 AI                │
│   AI 反问：「不确定的事」列表                   │
│   AI 生成：「任务列表」（优先级+依赖）          │
│   用户确认后才执行                              │
│ 解决：AI 不理解你的意图 → 先问清楚再做          │
└──────────────────────────────────────────────┘
                    ↓
┌─ 执行 ───────────────────────────────────────┐
│ Shill 做的事：                                  │
│   Token 预算管控（默认 $50 安全帽）             │
│   代码标准检查（无 emoji、错误处理、边界情况）   │
│   10 分钟超时 kill                              │
│ 解决：AI 乱花钱、写出不合格代码 → 被约束        │
└──────────────────────────────────────────────┘
                    ↓
┌─ 测量 + 判断 ────────────────────────────────┐
│ Shill 做的事：                                  │
│   跟踪 git diff → 计算 E(t)                     │
│   使用 LoopGain 的 5 状态分类（经 92% 验证）    │
│   收敛→完成 / 震荡→回退 / 发散→叫停             │
│ 解决：AI 不知道什么时候停 → Shill 替它判断      │
└──────────────────────────────────────────────┘
```

## 设计：从五个阶段到六个模块

```
shill/
├── src/
│   ├── index.ts          ← CLI + 主流程编排
│   ├── perceive.ts       ← 阶段 0：扫描项目，生成 PROJECT_SUMMARY.md
│   ├── decide.ts         ← 阶段 1：AI 反问 + 任务列表 + 用户确认
│   ├── execute.ts        ← 阶段 2：调用 AI CLI，token 管控，代码标准检查
│   ├── measure.ts        ← 阶段 3：LoopGain 5 状态分类（控制论方法）
│   └── judge.ts          ← 阶段 4：状态→策略 映射
├── package.json
└── tsconfig.json
```

技术选型：TypeScript + Node.js 内置模块，零外部依赖。总代码 < 350 行。

### 阶段 0：感知（perceive.ts）

**不调 AI，纯静态分析。** 递归扫描项目文件 → 生成 `PROJECT_SUMMARY.md`。

内容包含：项目类型、目录树、各模块职责、关键依赖、入口文件。限制 ~500 行，防止 token 浪费。

快、免费、确定性。这份文档成为后续所有 AI 交互的上下文基础。

### 阶段 1：决策（decide.ts）

项目总结 + 用户目标 → 发给 AI。AI 必须输出两样东西：

```markdown
## 需要确认的问题
1. "重构"指的是改架构还是只改命名？
2. 是否需要保持向后兼容？

## 任务列表
- [ ] 提取公共函数到 utils.ts（优先级：高，预估 ~50 行）
- [ ] 统一命名规范（优先级：中，依赖：任务 1）
- [ ] 加单元测试（优先级：中，预估 ~80 行）
```

用户确认/修改后才进入执行阶段。这一步只消耗一次 token，但阻断了后续方向性错误的巨大浪费。

关键设计：AI 被**强制**要求输出"不确定的事"——不给跳过这个环节的机会。

### 阶段 2：执行（execute.ts）

包装 AI CLI 调用 + Token 预算 + 代码标准检查。

**代码标准检查（行业级）**：
- 不允许 emoji 和装饰性符号
- 错误处理覆盖率：每个外部调用都有错误处理
- 超时控制：所有网络/IO 操作有超时
- 风格一致性：不破坏项目现有代码风格
- 边界处理：null/undefined/空数组/空字符串
- 不引入不必要的依赖

检查不通过 → 把问题告诉 AI 让它自己修，不追求 100% 自动。

**默认安全帽**：$50 预算上限。Token 解析不到时用字符数/4 估算，宁可高估早触发。

**贡献来源**：burnstop 的默认安全帽、tightloop 的每 action 检查。

### 阶段 3：测量（measure.ts）

**直接使用 LoopGain 的思路**（pypi.org/project/loopgain/）。控制论方法，经实测减少 92% API 花费。

5 种轨迹分类：
- `FAST_CONVERGE`：E(t) 快速递减，斜率陡
- `CONVERGING`：E(t) 持续递减中
- `STALLING`：E(t) 稳定在小值，无进一步改善
- `OSCILLATING`：E(t) 反复波动，方向翻转
- `DIVERGING`：E(t) 持续增长，失控

TypeScript 重写，~30 行。核心算法：取最近 3 轮 E(t) 值，判断比值趋势。

**贡献来源**：LoopGain 的 Barkhausen 判据法（1921 年控制论）。

### 阶段 4：判断（judge.ts）

状态 → 策略映射：

| 检测到 | 动作 |
|--------|------|
| fast_converge | 当前任务完成，继续下一个任务 |
| converging | 继续当前任务，给 AI 一轮时间 |
| stalling | 当前已达最佳状态，标记完成 |
| oscillating | 回退到 E(t) 最小的那轮 commit，修改 prompt 方向，重试 |
| diverging | 停止，警告用户"AI 失控了，建议缩小任务范围" |

**最优轮追踪**：每轮 git commit 存 hash。震荡/发散时回退到 E(t) 最小的那轮（不是上一轮）。

**贡献来源**：tightloop 的最佳输出追踪、LoopGain 的 best-so-far rollback。

### 差异化总结

| | 竞品 | Shill |
|------|------|------|
| 感知 | 无（AI 自己看） | 自动生成项目总结 |
| 决策 | 无（直接干活） | AI 反问 + 任务确认 |
| 执行 | token 统计 | token + 代码标准双检查 |
| 测量 | 阈值判断 | LoopGain 控制论方法 |
| 判断 | 停/继续 | 5 种状态 5 种策略 |
| 安装 | YAML/配置 | 一行命令

## 2026年6月 市场验证与竞品分析

本周 GitHub Trending 和 HN 多个信号确认了这个方向：

- **Loop Engineering 崛起**：Claude Code 之父 Boris Cherny 已转向"只写循环，不写 prompt"
- **headroom**（26k star）：Token 压缩 60-95%，可以作为 Shill 的底层压缩模块
- **SkillSpector**（NVIDIA）：26% 的 Agent Skill 有安全漏洞——精准控制不是可选项，是必需品

### 已有竞品

| 项目 | 亮点 | Shill 可以借鉴的 |
|------|------|-----------------|
| **[LoopGain](https://pypi.org/project/loopgain/)** | 控制论收敛检测（Barkhausen 判据，1921），把收敛状态分成 5 级：快速收敛/收敛中/停滞/震荡/发散，92% 更少 API 花费 | 收敛检测不应只看"变化行数是否低于阈值"，要看**变化趋势的斜率**。震荡和发散比停滞更可怕 |
| **[burnstop](https://github.com/phuryn/burnstop)** | 自动设 $50 安全上限，用 Claude Code hook 系统拦截 | 新用户最容易忽略的就是"没设预算"。默认安全帽能防小白炸号 |
| **[tightloop](https://pypi.org/project/tightloop/)** | 每个 action 前都检查预算（不是每轮），跟踪"最佳输出"自动回滚 | 回滚不该只回退到上一轮，应该回退到**全局最优轮** |
| **[Rimuru](https://github.com/rohitg00/rimuru)** | 自动发现 6 种 Agent，4 种循环模式检测（重复调用/错误爆炸/震荡/token 激增） | Shill 的 Agent 自动检测和它思路一样；循环检测可以加模式识别 |
| **[LoopBuster](https://github.com/liuchunwei732-cmyk/loopbuster)** | 4 种检测策略 + 自适应阈值 + 零依赖 | 多重检测比单一阈值可靠 |
| **[MartinLoop](https://github.com/Keesan12/martin-loop)** | 预算上限 + 验证门 + 回滚 + 审计追踪 | 功能最全，但太"重"——Shill 要做的是它的极简版 |
| **[PrismoDev](https://github.com/shanirsh/prismodev)** | `npx getprismo protect` 一行命令启动 | Shill 追求的"30 秒能用"体验 |

### Shill 的差异化

竞品都在堆功能、配 YAML、写 policy 文件。Shill 走反方向：**一行命令，默认值覆盖 90% 场景，代码量控制在实际可维护的范围。**

从竞品学到的最重要的三件事，直接改进了 Shill 的设计：
1. **收敛检测升级**（来自 LoopGain）——不看绝对行数，看变化趋势
2. **自动安全帽**（来自 burnstop）——默认 $50 上限防止炸号
3. **回退到最优轮**（来自 tightloop）——不是回退上一轮，是回退到全局最佳

## 实现

代码仓库：`C:\Users\14778\Desktop\shill\src\`，全部 824 行，TypeScript 编译零错误，零外部依赖。

```
src/
├── perceive.ts   148 行   阶段 0：三级文件重要性分类 + 自适应阈值 + 项目规模检测
├── decide.ts     105 行   阶段 1：JSON 结构任务列表 + 依赖 DAG 排序 + m87 确认模式
├── execute.ts    152 行   阶段 2：多 Agent 检测 + Token/$ 转换 + 代码标准检查（emoji/边界/超时）
├── measure.ts    108 行   阶段 3：LoopGain 5 状态分类 + 几何平均比值 + 自适应阈值动态调整
├── judge.ts       96 行   阶段 4：checkpoint 管理 + best-so-far rollback + 有限重试（GitHub 2026 playbook）
└── index.ts      215 行   五阶段编排：感知→决策→执行→测量→判断
```

### 关键设计决策

| 决策 | 来自 | 实现位置 |
|------|------|---------|
| 5 状态控制论分类 + 几何平均比值 | LoopGain | `measure.ts:measure()` |
| 默认 $50 安全帽 | burnstop | `index.ts:totalSpent >= cap` |
| best-so-far rollback | tightloop | `judge.ts:gitRollback(best.hash)` |
| 自适应阈值动态调整 | LoopBuster | `measure.ts:adaptThreshold()` |
| 依赖感知 DAG 任务排序 | Supergoal | `decide.ts:orderTasks()` |
| Preview → Confirm 确认模式 | m87 | `index.ts:stdin confirm` |
| aider 传 --no-git | git-lanes + aider docs | `execute.ts:AGENTS.aider.args` |
| 三级文件重要性分类 | PrismoDev | `perceive.ts:perceive()` |
| 有限重试（每任务最多 1 次） | GitHub 2026 playbook | `judge.ts:taskRetries >= maxRetries` |
| 代码标准检查（emoji/boundary/timeout）| 用户要求 | `execute.ts:checkStandards()` |

### 测试方式

```bash
# 1. 类型检查（免费，0 秒）
cd C:\Users\14778\Desktop\shill && npx tsc --noEmit

# 2. 测试感知阶段（免费，不需要 AI）
node -e "const {perceive} = require('./dist/perceive.js'); console.log(perceive('.'))"

# 3. 全流程实战（~$0.2，用 Claude CLI）
node dist/index.js "add a one-line comment to README" --cap 1
```

### 使用效果

```bash
$ npm i -g shill

$ shill "add unit tests for user-service" --cap 50
=== Phase 0: Scanning project ===
Project: medium (147 files). Adaptive threshold: 25 lines.

=== Phase 1: Planning ===
Using: claude

[Questions to clarify]
1. Jest or Mocha for testing?
2. Mock database or use in-memory?

[Task list]
- [task-1] [high] Install test dependencies (~5 lines)
- [task-2] [high] Write 3 test cases for createUser (~80 lines, requires: task-1)
- [task-3] [medium] Write 2 test cases for deleteUser (~40 lines, requires: task-1)

确认？> y

=== Phase 2: Executing 3 tasks ===

--- Task: task-1 [high] ---
Round 1 | Budget: $0.00/$50
  2.1s | +5 -0 lines | $0.032 | fast_converge
  Task completed.

--- Task: task-2 [high] ---
Round 1 | Budget: $0.03/$50
  12.3s | +85 -3 lines | $0.124 | converging
Round 2 | Budget: $0.15/$50
  4.1s | +6 -1 lines | $0.037 | fast_converge
  Task completed.

--- Task: task-3 [medium] ---
Round 1 | Budget: $0.19/$50
  6.5s | +42 -0 lines | $0.068 | fast_converge
  Task completed.

=== Summary ===
Budget: $0.26 used / $50 cap
All tasks completed.

## 实战教训

### DeepSeek 不支持文件工具

`claude -p` 指向 DeepSeek 时，模型只能文本对话，不能调用 Write/Edit 工具。表现为 3 轮零改动后停止。

**解决方案**：绕开 CLI，直接调 DeepSeek Anthropic-compatible HTTP API，prompt 通过 HTTP body 发送，不会被 shell 截断。API 返回精确 token 数。

### 核心策略演进

```
v1: claude -p "prompt" → 聊天模式，无文件编辑
v2: claude -p (stdin传prompt) → prompt被shell截断，AI 收到"Current"一个字
v3: HTTP API 直调 → 完美工作！
```

**最终方案**：API 调用内联在 `execute.ts` 中，不依赖外部配置文件。简洁 prompt，不包含文件当前内容（新文件无需），AI 输出代码块 → `extractCode()` 提取 → 写入磁盘。

### 测试结果（2026-06-27）

```
shill "create README.md with: # Shill - AI Agent Loop Controller" --cap 3

Phase 0: 10 files scanned
Phase 1: AI 生成任务列表 (含文件路径)
Phase 2: Round 1 — 4.2s, Wrote README.md (303 chars), $0.004
         Done (first round success)

结果: README.md 正确创建，专业英文描述
```

总花费 $0.004，一轮完成。五阶段全流程验证通过。

## 下一步

- [x] 项目骨架 + 全部源文件
- [x] DeepSeek API 直调方案
- [x] 五阶段全流程跑通
- [ ] 修 decide.ts JSON 解析（AI 常不输出纯 JSON）
- [ ] 多文件编辑支持
- [ ] 去掉 `shell:true` deprecation warning
- [ ] 真实项目验证
- [ ] 发布 npm

## 相关笔记

- [[工作学习/AI-Agent-Token优化|AI Agent Token 优化]]
- [[前沿信息/Agent-Skill生态|Agent Skill 生态]]
