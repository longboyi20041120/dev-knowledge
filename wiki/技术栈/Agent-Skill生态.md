---
tags:
  - "#类型/技术"
  - "#技术/ai-agent"
  - "#状态/草稿"
  - agent-skill
created: 2026-06-22
updated: 2026-06-22
status: draft
---

# AI Agent Skill 生态（2026年6月）

## 趋势：Skill 正在成为新的 npm 包

2026 年 6 月 GitHub Trending 上，多个 Agent Skill 仓库同时上榜，没有协调却自发走到了同一格式：

```
skill-repo/
├── SKILL.md          # 指令 + 触发条件
├── manifest          # 元数据
└── bundled-scripts/  # 辅助工具
```

这跟 2011 年的 npm 生态很像——爆发式增长、没有包管理器、没有依赖图、没有安全审查。

## 标杆项目

### addyosmani/agent-skills（58k star）

Google Chrome 团队的 Addy Osmani 发布的生产级 Agent Skill 库：
- 7 个生命周期命令：`/spec` → `/plan` → `/build` → `/test` → `/review` → `/code-simplify` → `/ship`
- 覆盖从需求到发布全流程

### taste-skill（43k star）

"反模板"前端 Skill 集，让 Agent 生成的 UI 不千篇一律：
- 布局优化、字体选择、间距调整、动画微调
- 解决 AI 生成的前端都长一样的痛点

### last30days-skill（41k star）

跨平台研究型 Agent Skill：
- Reddit、X、YouTube、HN、Polymarket 多源抓取
- 自动合成有据可查的摘要

### NVIDIA SkillSpector — Agent Skill 安全扫描

- 检测 64 种漏洞模式，16 个类别
- Prompt 注入、数据泄露、权限提升
- **26% 的 Skill 有漏洞，5% 疑似恶意**

## 和你的关系

你的 `编程知识库/CLAUDE.md` 本质上就是一个 Agent Skill——定义规则、触发条件、行为边界。你可以把它单独抽出来发布为一个 Skill 仓库。

你的 Shill 项目也可以做成一个 Skill：`/shill-loop`，其他人在 Claude Code 里安装就能用。

## 相关笔记

- [[灵感/shill-loop优化工具|Shill — Loop 优化工具]]
- [[技术栈/AI-Agent-Token优化|AI Agent Token 优化]]
