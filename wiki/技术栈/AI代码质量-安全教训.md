---
tags:
  - "#类型/技术"
  - "#技术/AI"
  - "#技术/安全"
  - "#状态/草稿"
created: 2026-06-26
updated: 2026-06-26
status: draft
---

# AI 生成代码的质量和安全教训

2026 年 6 月 GitHub Trending 和 HN 上几个数据点，拼出一幅清晰的警示图。

## 两个案例

### Bun 重写：100 万行，10,000+ unsafe 块

Claude Code 用 9 天将 Bun 从 Zig 重写为 Rust：
- 6,755 次提交
- 99.8% 测试通过率
- 但：发现了 **超过 1 万个 unsafe 代码块**

教训：AI 写得快只是表象。**代码量不是瓶颈，质量和安全才是。** 一个 unsafe 块就是一个潜在的漏洞。

### NVIDIA SkillSpector：1/4 的 Skill 有漏洞

NVIDIA 发布 Agent Skill 安全扫描工具，结果触目惊心：

- 扫描了大量 Agent Skill（类似 Claude Code 的 skills/ 目录里的文件）
- **26% 有安全漏洞**
- **5% 疑似恶意**

意味着——你下载一个社区 Agent Skill，有四分之一概率带漏洞，二十分之一可能是坏的。

## 教训

1. **速度快 ≠ 质量高**。AI 可以用几小时产出人类几个月的代码量，但安全检查无法 AI 加速
2. **Agent Skill 需要安全审计**。Skill 本质上是在给 AI 赋予新能力——赋予能力 = 扩大攻击面
3. **精准控制 > 放任自动**。[[灵感/shill-loop优化工具|Shill]] 的思路是对的：不是不信任 AI，而是给 AI 加护栏

## 实践建议

- AI 生成的代码至少过一遍 `unsafe` / `eval` / `exec` 扫描
- 从社区获取 Agent Skill 前先读代码（不信任未经审计的 prompt 注入点）
- CI 里加安全扫描步骤，和 lint 一样自动化

## 相关笔记

- [[灵感/shill-loop优化工具|Shill — Loop 优化工具]]
- [[技术栈/AI-Agent-Token优化|AI Agent Token 优化]]
- [[技术栈/Agent-Skill生态|Agent Skill 生态]]
