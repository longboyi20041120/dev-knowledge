---
tags:
  - 用途/工作学习
  - 类型/技术
  - 技术/excalidraw
  - 状态/草稿
created: 2026-07-29
updated: 2026-07-29
---

# Excalidraw 可视化方案

Obsidian 中 Excalidraw 插件的使用方案，涵盖文件格式、压缩编码、JSON 结构以及知识图谱集成。

## 文件格式

Excalidraw 绘图保存为 `.excalidraw.md` 文件，表面是 Markdown，实际包含两类内容：

1. **Frontmatter**：标记 `excalidraw-plugin: parsed` 和 `tags: [excalidraw]`
2. **Drawing 数据**：压缩后的 JSON，位于 `## Drawing` 标题下

```markdown
---
excalidraw-plugin: parsed
tags: [excalidraw]
---
# Drawing
LZString压缩数据...
```

## 压缩编码

- Excalidraw 使用 **LZString** 算法压缩 JSON 数据
- 默认 `LZString.compressToBase64()` 输出 Base64 编码
- 最大单次压缩限制 256 字符（超出需分段）

## JSON 元素结构

每个绘图元素遵循 Excalidraw 元素 JSON 规范（详见 [[wiki/前沿信息/Excalidraw元素JSON规范]]）：

| 元素类型 | 关键属性 |
|----------|----------|
| 文本 | `type: "text"`, `containerId`, `autoResize`, `lineHeight`, `textAlign`, `verticalAlign` |
| 矩形 | `type: "rectangle"`, `roundness`, `boundElements` |
| 箭头 | `type: "arrow"`, `points`, `endArrowhead` |
| 通用 | `strokeSharpness`, `fillStyle`, `roughness`, `isDeleted` |

## 在知识图谱中的表现

- `.excalidraw.md` 文件在 Graph View 中显示为 **独立节点**
- 通过 frontmatter 的 `tags: [excalidraw]` 可统一过滤或着色
- 建议图谱搜索排除绘图文件：`-tag:excalidraw`

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 文件无法打开 | LZString 压缩数据损坏 | 检查 frontmatter 是否有 `excalidraw-plugin: parsed` |
| 图谱中出现空白节点 | 文件缺少 frontmatter 或标签 | 补全 `tags: [excalidraw]` |
| 中文乱码 | 编码不对 | 确保文件为 UTF-8 编码 |

## 相关笔记

- [[wiki/前沿信息/Excalidraw元素JSON规范|Excalidraw 元素 JSON 规范]]
- [[wiki/踩坑记录/Excalidraw生成文件无法打开|Excalidraw 文件无法打开踩坑]]
