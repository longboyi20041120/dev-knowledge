---
tags:
  - 用途/前沿
  - 类型/技术
  - 技术/excalidraw
  - 状态/草稿
created: 2026-07-29
updated: 2026-07-29
---

# Excalidraw 元素 JSON 规范

基于 [官方文档](https://docs.excalidraw.com/docs/codebase/json-schema) 和社区最佳实践整理，重点解决**文本定位**、**框与文字比例**、**箭头绑定**三大痛点。

---

## 一、文本在容器内的定位公式

这是最常见的坑：文字不居中、溢出、或者和框的比例失调。

### 居中定位公式

```
text.x      = container.x + 20
text.y      = container.y + (container.height / 2) - (fontSize / 2)
text.width  = container.width - 40
text.height = fontSize × 1.25
```

> 核心：文字 width 比容器缩进 40px（左右各 20px），文字 y 从容器垂直中心往上偏移半个 fontSize，实现完美居中。

### 等价写法

```
text.x = rect.x + (rect.width  - text.width)  / 2
text.y = rect.y + (rect.height - text.height) / 2
```

### 多行文字

```json
"text": "第一行\n第二行\n第三行",
"autoResize": true
```

- `autoResize: true` — 文字横向扩展，不换行
- `autoResize: false` — 文字固定宽度，自动换行

---

## 二、框与文字的比例标准

| 文字字数 | 推荐框尺寸 | 适用场景 |
|----------|-----------|----------|
| 1-2 字 | 140 × 60 | 标签、标记 |
| 3-4 字 | 180 × 80 | 一般节点名 |
| 5-8 字 | 240 × 90 | 描述性节点 |
| 9+ 字 | 300 × 100 | 主节点 / Hero 元素 |

### 自动宽度公式

- **中文**：`width = max(140, 字数 × 18)`
- **英文**：`width = max(140, 字符数 × 9)`
- **高度**：`height = 行数 × fontSize × 1.25 + 30`

### 字号层级

| 用途 | 字号 | 说明 |
|------|------|------|
| 主标题 | 28-36px | 不加容器，自由文本 |
| 分区标题 | 24px | 自由文本 |
| 框内标签 | 20px | **最佳平衡点**，投影可读 |
| 正文/描述 | 16px | 最小可读字号 |
| 注释 | 14px | 非必须阅读的文字 |
| 底线 | 12px | 尽量不用 |

> **16px 是投影展示的已验证最小字号**，低于此字号投屏时难以辨认。

### 核心原则：不是每个文字都需要框

| 加框 | 自由文本 |
|------|----------|
| 焦点节点、需要连线的节点 | 标签、描述、注释 |
| 形状本身有意义（菱形=判断） | 分区标题、图例 |
| 要和其他元素视觉分组 | 字号/粗细本身就够区分层级 |

**经验法则**：框内文本不要超过全文的 30%。

---

## 三、箭头定位与绑定

### 绑定是双向的

箭头和形状**必须互相关联**，缺一不可：

```json
// 箭头方
{
  "startBinding": { "elementId": "box-a", "focus": 0, "gap": 5 },
  "endBinding":   { "elementId": "box-b", "focus": 0, "gap": 5 }
}

// 形状方
{
  "boundElements": [
    { "type": "arrow", "id": "arrow-1" },
    { "type": "text",  "id": "text-1"  }
  ]
}
```

### focus 参数控制箭头连接位置

`focus` 范围 `[-1, 1]`，控制箭头在形状边缘的偏移：

| focus | 位置 |
|-------|------|
| `0` | 边缘正中 |
| `-0.5` | 偏上/偏左 |
| `0.5` | 偏下/偏右 |
| `1` | 远端 |
| `-1` | 反向远端 |

> 多条箭头连同一个形状时，用不同 focus 值错开：`-0.5` 和 `0.5`。

### gap 参数

```
有效间距 = 5 + (strokeWidth / 2)
```

- 弯头箭头：`BASE_BINDING_GAP_ELBOW = 5`
- 建议 `gap: 5` 保证箭头不贴在形状边缘

### Points 坐标系

```
箭头的 (x, y) = 绝对起点坐标
points = 相对于 (x, y) 的偏移数组
```

**常用路径**：

| 方向 | points |
|------|--------|
| 水平右 | `[[0, 0], [width, 0]]` |
| 垂直下 | `[[0, 0], [0, height]]` |
| L 形右→下 | `[[0, 0], [width, 0], [width, height]]` |
| 下→右 | `[[0, 0], [0, height], [width, height]]` |

### 箭头风格语义

| 样式 | 含义 |
|------|------|
| `"solid"` 实线箭头 | 主流程、主要序列 |
| `"dashed"` 虚线箭头 | 响应、返回、可选路径、异步 |
| `"dotted"` 点线箭头 | 引用、依赖、弱关联 |
| 无线头 | 关联、分组 |

---

## 四、布局间距标准

### 网格基准

- 所有坐标取 **20px 的倍数**（50 的倍数更佳）
- 分组内元素保留 **40-60px** 间隔

### 间距参考

| 场景 | 间距 |
|------|------|
| 水平节点间距 | 200-300px |
| 垂直行间距 | 100-150px |
| 不同分区间距 | ≥ 300px |
| 分区内边距 | 50-60px |
| 带标签箭头间距 | 150-200px |
| 无标签箭头间距 | 100-120px |
| 画布边缘留白 | ≥ 50px |

### 60-30-10 法则

- **60%** 留白
- **30%** 主内容
- **10%** 高亮/强调

> 留白不是浪费，是认知呼吸空间。觉得挤的时候，先加间距而不是缩小元素。

### 流向规则

- **左→右**：流程、时间线、数据流
- **上→下**：层级、决策树、继承
- **不要在同一张图里混合两种流向**
- 最重要的元素放**顶部或中心**

---

## 五、元素通用属性速查

| 属性 | 类型 | 说明 |
|------|------|------|
| `id` | string | 唯一标识 |
| `type` | string | `"rectangle"` / `"ellipse"` / `"diamond"` / `"arrow"` / `"text"` / `"line"` |
| `x`, `y` | number | 左上角坐标（像素） |
| `width`, `height` | number | 尺寸（像素） |
| `angle` | number | 旋转角（弧度，不用） |
| `strokeColor` | string | 边框色 hex |
| `backgroundColor` | string | 填充色 hex 或 `"transparent"` |
| `fillStyle` | string | `"solid"` / `"hachure"` / `"cross-hatch"` |
| `strokeWidth` | number | 线宽，建议 2 |
| `strokeStyle` | string | `"solid"` / `"dashed"` / `"dotted"` |
| `roughness` | number | 0=整洁, 1=手绘, 2=粗糙 |
| `opacity` | number | 0-100 |
| `roundness` | object/null | `{"type":1}`=直角, `2`=微圆, `3`=全圆, 文本用 null |
| `boundElements` | array/null | 绑定到此元素的文字/箭头 |
| `containerId` | string/null | 文字专属，指向父容器 |
| `isDeleted` | boolean | 始终 `false` |
| `locked` | boolean | 是否锁定 |
| `index` | string | Z序（`"a0"`, `"a1"`...，先出现的在底层） |

## 六、字体系列

| ID | 字体 | 风格 | 用途 |
|----|------|------|------|
| 1 | Virgil | 手绘 | 非正式草图 |
| 2 | Helvetica | 整洁无衬线 | 技术文档首选 |
| 3 | Cascadia | 等宽 | 代码片段、API名 |
| 5 | Excalifont | 新手绘 | 混合图表 |

---

## 七、压缩格式

```markdown
## Drawing
```compressed-json
LZString压缩数据（每256字符换行）...
```
```

- 生成：`LZString.compressToBase64(JSON.stringify(scene))`
- 解压：`LZString.decompressFromBase64(compressed)`
- 分段：每 256 字符一组，Git diff 友好

---

## 八、常见踩坑

| 问题 | 原因 | 解决 |
|------|------|------|
| 文字不居中 | 没按居中公式算坐标 | `text.y = container.y + height/2 - fontSize/2` |
| 文字溢出框 | `autoResize: true` + 文字太宽 | 调大容器或缩短文字 |
| 箭头不跟随移动 | 只绑了一边 | 箭头和形状都要写 `boundElements` |
| 多条箭头重叠 | focus 全是 0 | 不同箭头用不同 focus 值 |
| 缩放组后文字变形 | Excalidraw bug (#8335) | 缩放前确定字号，缩放后手动调 |
| 框太多显乱 | 什么都加框 | 30% 文字才需要框，其余用自由文本 |

---

## 九、Obsidian 视觉风格

所有知识库中的 Excalidraw 绘图应遵循统一的 Obsidian 风格，保持"纸质笔记本手绘感"。

### 风格参数速查

```json
{
  "appState": { "viewBackgroundColor": "#ffffff" },
  "currentItemFontFamily": 5,
  "currentItemFontSize": 20,
  "currentItemRoughness": 1,
  "currentItemStrokeWidth": 2,
  "currentItemStrokeStyle": "solid",
  "currentItemFillStyle": "solid",
  "currentItemRoundness": "round",
  "currentItemStrokeSharpness": "round"
}
```

### 字体

| 层级 | 字号 | 字体 | 何时用 |
|------|------|------|--------|
| 主标题 | 28px | Excalifont (5) | 图顶部居中，不加容器 |
| 框内标签 | 20px | Excalifont (5) | 所有容器内的文字 |
| 注释/脚注 | 16px | Excalifont (5) | 箭头标签、补充说明 |

> **必须用 Excalifont（fontFamily: 5）**，不用 Helvetica（2）。Excalifont 有手绘感，是 Obsidian Excalidraw 的默认字体，和 Obsidian 整体"卡片式笔记"风格统一。

### 粗糙度

- **全部设 `roughness: 1`**（轻度手绘），不要太整洁（`0`）也不要太潦草（`2`）
- `strokeSharpness: "round"` 让线条边角圆润

### 配色：8 色语义调色板

和 Obsidian 图谱颜色一致，色相环均匀分布，各色区分度高：

| 颜色 | 边框 | 填充 | 用于 |
|------|------|------|------|
| 红 | `#e6194b` | `#ffe0e6` | 计算机基础、工程基础 |
| 紫 | `#911eb4` | `#f3e6ff` | 编程语言 |
| 青 | `#42d4f4` | `#e6faff` | 大数据技术 |
| 蓝 | `#4363d8` | `#e6ecff` | 数学、算法 |
| 品红 | `#f032e6` | `#ffe6fd` | 数据科学、ML |
| 绿 | `#3cb44b` | `#e6ffe8` | 项目 |
| 黄 | `#ffe119` | `#fffde6` | 前沿、灵感 |
| 橙 | `#f58231` | `#fff2e6` | 原始材料 |

**箭头颜色**：`#374151`（深灰，不抢眼）
**文字颜色**：`#1e1e1e`（近乎黑色）
**注释颜色**：`#6b7280`（中灰）

### 圆角

- **所有矩形统一 `roundness: {"type": 3}`**（全圆角）
- 箭头：`roundness: {"type": 2}`（微曲线，比硬拐角自然）

### 不要做的事

- ❌ 不要用 `roughness: 0`（过于工整，不像手绘笔记）
- ❌ 不要用 `fontFamily: 2`（Helvetica 太正式）
- ❌ 不要用 `fillStyle: "hachure"`（交叉线填充太乱）
- ❌ 不要用高饱和度、荧光色
- ❌ 不要把每个文字都放进框里

---

## 十、完整示例（Obsidian 风格）

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin/releases/tag/2.0.18",
  "elements": [
    {
      "id": "box-api",
      "type": "rectangle",
      "x": 200, "y": 200,
      "width": 180, "height": 80,
      "strokeColor": "#4363d8",
      "backgroundColor": "#e6ecff",
      "fillStyle": "solid",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "roundness": { "type": 3 },
      "boundElements": [
        { "type": "text", "id": "text-api" },
        { "type": "arrow", "id": "arrow-1" }
      ],
      "index": "a0"
    },
    {
      "id": "text-api",
      "type": "text",
      "x": 220, "y": 222,
      "width": 140, "height": 35,
      "text": "API 网关",
      "fontSize": 20,
      "fontFamily": 5,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "box-api",
      "autoResize": true,
      "lineHeight": 1.25,
      "strokeColor": "#1e1e1e",
      "roughness": 1,
      "roundness": null,
      "index": "a1"
    },
    {
      "id": "arrow-1",
      "type": "arrow",
      "x": 380, "y": 240,
      "width": 200, "height": 0,
      "points": [[0, 0], [200, 0]],
      "strokeColor": "#374151",
      "strokeWidth": 2,
      "strokeStyle": "solid",
      "roughness": 1,
      "roundness": { "type": 2 },
      "startBinding": { "elementId": "box-api", "focus": 0, "gap": 5 },
      "endBinding": { "elementId": "box-svc", "focus": 0, "gap": 5 },
      "startArrowhead": null,
      "endArrowhead": "arrow",
      "index": "a2"
    }
  ],
  "appState": { "gridSize": null, "viewBackgroundColor": "#ffffff" },
  "files": {}
}
```

> 和前面通用示例的区别：`fontFamily: 5`（Excalifont）、`roughness: 1`（手绘感）、加了 `index` 字段、使用 Obsidian 8 色调色板。

---

## 相关笔记

- [[wiki/Excalidraw可视化方案|Excalidraw 可视化方案]]
- [[wiki/踩坑记录/Excalidraw生成文件无法打开|Excalidraw 文件无法打开]]
