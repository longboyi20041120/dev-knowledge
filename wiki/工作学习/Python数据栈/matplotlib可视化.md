---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/python"
  - "#技术/数据分析"
  - "#状态/已验证"
created: 2026-06-26
updated: 2026-07-15
status: reviewed
---

# matplotlib 可视化

> 6 种图表 + 面试图表选择指南。 | **面试重要度：中** | 预计阅读：15 分钟

## 视频资源

- YouTube: [Corey Schafer: Matplotlib Tutorial](https://www.youtube.com/playlist?list=PL-osiE80TeTvipOqomVEeZ1HRrcEvtZB_) — 最清晰的 matplotlib 教程
- B站: [莫烦 Python: Matplotlib 教程](https://www.bilibili.com/video/BV1Jx411L7oD/) — 中文可视化入门

# matplotlib 可视化：数据分析师的图表工具箱

用前面 pandas 和 numpy 笔记里的真实数据画图。

## 一、快速上手

```python
import matplotlib.pyplot as plt
import numpy as np

# 设置中文字体（Windows 用 SimHei，Mac 用 PingFang SC）
plt.rcParams["font.sans-serif"] = ["SimHei", "PingFang SC"]
plt.rcParams["axes.unicode_minus"] = False  # 正常显示负号

# 数据准备（复用 numpy 笔记的温度数据）
np.random.seed(42)
temps = np.random.normal(loc=28, scale=5, size=(30, 24))
daily_avg = temps.mean(axis=1)
```

## 二、折线图：趋势分析

```python
fig, ax = plt.subplots(figsize=(10, 4))

ax.plot(range(1, 31), daily_avg, marker="o", color="#2196F3",
        linewidth=2, markersize=4, label="日均温度")
ax.axhline(y=30, color="red", linestyle="--", alpha=0.5, label="高温警戒线(30°C)")
ax.fill_between(range(1, 31), daily_avg, 30,
                where=(daily_avg > 30), color="red", alpha=0.1)

ax.set_title("6月日均温度趋势", fontsize=14, fontweight="bold")
ax.set_xlabel("日期")
ax.set_ylabel("温度 (°C)")
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()
```

**面试要点**：折线图用于趋势。`axhline` 加参考线，`fill_between` 高亮异常段——这些细节让图表从"能用"变"专业"。

## 三、柱状图：对比分析

```python
# 品类 GMV 对比（复用 pandas 笔记的电商数据）
categories = ["数码", "服装", "食品", "美妆", "家居"]
gmv = [298450, 247891, 203556, 141283, 95210]
orders = [1507, 1261, 1018, 739, 475]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

# 左图：GMV 柱状图
bars = ax1.bar(categories, gmv, color=["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"])
ax1.set_title("各品类 GMV 对比", fontsize=13)
ax1.set_ylabel("GMV (元)")
for bar, val in zip(bars, gmv):
    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3000,
             f"{val/10000:.1f}万", ha="center", fontsize=9)

# 右图：订单量占比饼图
colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]
wedges, texts, autotexts = ax2.pie(orders, labels=categories, autopct="%1.1f%%",
                                     colors=colors, startangle=90)
ax2.set_title("各品类订单量占比", fontsize=13)

plt.tight_layout()
plt.show()
```

**面试要点**：柱状图对比绝对值，饼图看占比。**数字标签**（`bar.text`）让读者不用数格子，是数据分析师的基本素养。

## 四、热力图：矩阵数据

```python
fig, ax = plt.subplots(figsize=(12, 5))

im = ax.imshow(temps, aspect="auto", cmap="coolwarm",
               vmin=15, vmax=40, interpolation="bilinear")

# 颜色条
cbar = plt.colorbar(im, ax=ax)
cbar.set_label("温度 (°C)", rotation=270, labelpad=15)

ax.set_title("6月逐时温度热力图", fontsize=14, fontweight="bold")
ax.set_xlabel("小时")
ax.set_ylabel("日期")
ax.set_xticks(range(0, 24, 3))
ax.set_xticklabels([f"{h}:00" for h in range(0, 24, 3)])
ax.set_yticks(range(0, 30, 5))
ax.set_yticklabels([f"6月{d+1}日" for d in range(0, 30, 5)])

plt.tight_layout()
plt.show()
```

**面试要点**：热力图展示二维数据的模式（比如每天哪个时段最热）。`cmap="coolwarm"` 蓝色=低温，红色=高温，直观。

## 五、直方图：分布分析

```python
# 订单金额分布（pandas 笔记的数据）
np.random.seed(42)
amounts = np.random.exponential(200, 5000)
amounts = amounts[(amounts >= 10) & (amounts <= 1000)]  # 只看 10-1000 元区间

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

ax1.hist(amounts, bins=50, color="#2196F3", edgecolor="white", alpha=0.8)
ax1.axvline(x=np.mean(amounts), color="red", linestyle="--", label=f"均值: {np.mean(amounts):.0f}元")
ax1.axvline(x=np.median(amounts), color="green", linestyle="--", label=f"中位数: {np.median(amounts):.0f}元")
ax1.set_title("订单金额分布", fontsize=13)
ax1.set_xlabel("金额 (元)")
ax1.set_ylabel("订单数")
ax1.legend()

# 箱线图：按品类
data_by_cat = [amounts[:1000], amounts[1000:2000], amounts[2000:3000],
               amounts[3000:4000], amounts[4000:]]
bp = ax2.boxplot(data_by_cat, labels=categories, patch_artist=True)
for patch, color in zip(bp["boxes"], ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7"]):
    patch.set_facecolor(color)
ax2.set_title("各品类订单金额分布（箱线图）", fontsize=13)
ax2.set_ylabel("金额 (元)")

plt.tight_layout()
plt.show()
```

**面试要点**：直方图看分布形状（右偏/正态），箱线图对比多组分布。均值 vs 中位数的差距就是偏度。

## 六、Seaborn：统计图表的快速通道

Seaborn 是基于 matplotlib 的统计可视化库，一行代码画出带统计信息的图表。

### 6.1 分组箱线图（Boxplot）

```python
import seaborn as sns
import pandas as pd

# 复用 pandas 笔记的电商数据
np.random.seed(42)
n = 5000
df_seaborn = pd.DataFrame({
    "category": np.random.choice(["数码","服装","食品","美妆","家居"], n, p=[0.30,0.25,0.20,0.15,0.10]),
    "channel":  np.random.choice(["App","小程序","PC","H5"], n, p=[0.45,0.30,0.15,0.10]),
    "amount":   np.round(np.random.exponential(200, n), 2).clip(10, 5000),
})

fig, ax = plt.subplots(figsize=(12, 5))
sns.boxplot(
    data=df_seaborn,
    x="category", y="amount",           # x=类别, y=数值
    hue="channel",                       # 按渠道分组着色
    palette="Set2",                      # 调色板
    ax=ax,
    flierprops={"marker": "x", "markersize": 3, "alpha": 0.3},  # 异常值标记样式
    showmeans=True,                      # 显示均值点（绿色三角）
    meanprops={"marker": "D", "markerfacecolor": "green", "markersize": 6},
)
ax.set_title("各品类 × 各渠道的订单金额分布", fontsize=14)
ax.set_ylabel("订单金额 (元)")
plt.xticks(rotation=15)
plt.tight_layout()
plt.show()
```

### 6.2 小提琴图（Violin Plot）

箱线图只展示分位数，小提琴图还能看到分布的形状：

```python
fig, ax = plt.subplots(figsize=(10, 5))
sns.violinplot(
    data=df_seaborn,
    x="category", y="amount",
    palette="Pastel2",
    inner="quartile",            # 内部显示四分位数线
    cut=0,                       # 不扩展到数据范围之外
    ax=ax,
)
ax.set_title("各品类订单金额分布（小提琴图）", fontsize=14)
ax.set_ylabel("订单金额 (元)")
plt.tight_layout()
plt.show()

# boxplot vs violin plot 的选择:
# - 箱线图: 简洁，适合给非技术观众看
# - 小提琴图: 能看到双峰、多峰等复杂分布，适合探索分析
```

### 6.3 相关性对图（Pairplot）

一行代码看所有数值变量之间的两两关系：

```python
# 构造多维特征数据
df_pair = pd.DataFrame({
    "温度": temps.mean(axis=1),
    "最高温": temps.max(axis=1),
    "最低温": temps.min(axis=1),
    "温差": temps.max(axis=1) - temps.min(axis=1),
    "波动": temps.std(axis=1),
})

g = sns.pairplot(
    df_pair,
    diag_kind="kde",          # 对角线用 KDE 密度曲线而不是直方图
    plot_kws={"alpha": 0.5, "s": 30},  # 散点图半透明+调大小
    corner=False,             # True = 只显示下三角（更简洁）
)
g.fig.suptitle("温度特征相关性矩阵", y=1.02, fontsize=14)
plt.show()
```

### 6.4 相关性热力图（Heatmap）

```python
fig, ax = plt.subplots(figsize=(8, 6))

# 计算相关系数矩阵
corr = df_pair.corr()

# 画热力图，带数值标注
mask = np.triu(np.ones_like(corr, dtype=bool), k=1)  # 只显示下三角
sns.heatmap(
    corr,
    annot=True,                # 显示数值
    fmt=".2f",                 # 数值格式
    cmap="RdBu_r",             # 红蓝配色（红=正相关，蓝=负相关）
    vmin=-1, vmax=1,           # 颜色范围
    center=0,                  # 0 为白色中心
    mask=mask,                 # 遮住上三角
    linewidths=0.5,            # 格子边框
    square=True,               # 正方形格子
    cbar_kws={"shrink": 0.8},  # 颜色条缩短
    ax=ax,
)
ax.set_title("温度特征相关系数热力图", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.show()
# 解读: 看对角线以下，颜色越深 = 相关性越强
# 最高温与日均温高度相关（合理），温差与最低温负相关（最低温越低温差越大）
```

## 七、图表美化专题

### 7.1 配色方案

```python
# ===== 调色板选择 =====
# matplotlib 内置 colormap:
#   连续数据: "viridis"(默认),"plasma","inferno","magma","cividis"
#   发散数据: "RdBu","coolwarm","seismic","PiYG"
#   定性数据: "Set1","Set2","Set3","Pastel1","Pastel2","tab10"

# seaborn 调色板:
#   sns.color_palette("husl", 8)       — 色相均匀分布
#   sns.color_palette("colorblind")    — 色盲友好（面试加分）
#   sns.light_palette("navy")          — 单色渐变（浅→深）
#   sns.diverging_palette(250, 30, l=65, center="dark")  — 自定义发散

# ===== 自定义色板 =====
custom_colors = ["#E63946", "#457B9D", "#2A9D8F", "#E9C46A", "#F4A261"]
fig, axes = plt.subplots(1, 3, figsize=(14, 4))

# 1. 默认配色
axes[0].bar(categories, gmv, color=plt.cm.Set1.colors)
axes[0].set_title("默认 Set1")

# 2. Seaborn colorblind 色板（色盲友好）
cb_colors = sns.color_palette("colorblind", 5)
axes[1].bar(categories, gmv, color=cb_colors)
axes[1].set_title("色盲友好配色 (colorblind)")

# 3. 自定义品牌色
axes[2].bar(categories, gmv, color=custom_colors)
axes[2].set_title("自定义配色")

plt.tight_layout()
plt.show()
```

**色盲友好配色速查**：

| 调色板 | 适用场景 | 色盲友好 |
|--------|----------|----------|
| `"colorblind"` | 多类别（最多 10 色）| 是 |
| `"Set2"` | 多类别（柔和） | 部分 |
| `"husl"` | 需要均匀色相 | 是（参数 l=50 以上）|
| `"viridis"` | 连续渐变 | 是（默认推荐）|
| `"RdBu"` | 正负对比 | 部分（红色盲看不清红色端）|

### 7.2 中文字体多种方案

Windows、Mac、Linux 三种平台显示中文的方法各不相同：

```python
# ===== 方案一: SimHei（Windows 自带，最省事）=====
plt.rcParams["font.sans-serif"] = ["SimHei"]  # 黑体
plt.rcParams["axes.unicode_minus"] = False

# ===== 方案二: 自适应（跨平台兼容）=====
import platform
system = platform.system()
if system == "Windows":
    plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei"]
elif system == "Darwin":  # macOS
    plt.rcParams["font.sans-serif"] = ["PingFang SC", "Heiti SC", "STHeiti"]
else:  # Linux
    plt.rcParams["font.sans-serif"] = ["Noto Sans CJK SC", "WenQuanYi Micro Hei"]
    # Linux 需要先安装: sudo apt install fonts-noto-cjk
plt.rcParams["axes.unicode_minus"] = False

# ===== 方案三: 查看系统有哪些中文字体 =====
from matplotlib.font_manager import FontManager
fm = FontManager()
# 只看中文字体
zh_fonts = [f.name for f in fm.ttflist if "Hei" in f.name or "Song" in f.name or "CJK" in f.name or "Sim" in f.name]
print("可用的中文字体:", zh_fonts)
```

### 7.3 数据标注与注释

图表要想专业，关键数据点必须标注清楚：

```python
fig, ax = plt.subplots(figsize=(12, 5))

# 折线图 + 标注关键点
x = range(1, 31)
y = daily_avg
ax.plot(x, y, marker="o", color="#2196F3", linewidth=2, markersize=4)

# ===== annotate: 标注关键数据点 =====
max_idx = np.argmax(y)
min_idx = np.argmin(y)
ax.annotate(
    f"最热: {y[max_idx]:.1f}°C\n(6月{max_idx+1}日)",
    xy=(max_idx+1, y[max_idx]),          # 标注点坐标
    xytext=(max_idx+1, y[max_idx]+3),    # 文字位置
    arrowprops=dict(arrowstyle="->", color="red", lw=1.5),
    fontsize=10, color="red", fontweight="bold",
    ha="center",
)
ax.annotate(
    f"最凉: {y[min_idx]:.1f}°C\n(6月{min_idx+1}日)",
    xy=(min_idx+1, y[min_idx]),
    xytext=(min_idx+1, y[min_idx]-3),
    arrowprops=dict(arrowstyle="->", color="blue", lw=1.5),
    fontsize=10, color="blue", fontweight="bold",
    ha="center",
)

# ===== text: 在任意位置加文字 =====
ax.text(0.02, 0.95, f"月均温: {y.mean():.1f}°C\n标准差: {y.std():.1f}°C",
        transform=ax.transAxes, fontsize=10, verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

ax.set_title("6月日均温度趋势（带标注）", fontsize=14, fontweight="bold")
ax.set_xlabel("日期")
ax.set_ylabel("温度 (°C)")
ax.axhline(y=30, color="red", linestyle="--", alpha=0.3)

plt.tight_layout()
plt.show()
```

### 7.4 图例位置与样式

```python
# 图例位置可以精确控制
# ax.legend(loc="upper left")  — 常用位置: best/upper right/upper left/lower left/lower right/center

# 更精确的位置控制:
fig, ax = plt.subplots()
ax.plot(x, y, label="温度")
ax.legend(
    loc="upper center",          # 大致位置
    bbox_to_anchor=(0.5, -0.15), # 精确偏移（相对于 loc 的位置）
    ncol=3,                       # 图例分几列
    frameon=True,                 # 是否有边框
    fancybox=True,                # 圆角边框
    shadow=True,                  # 阴影
    fontsize=9,
    title="图例标题",
)
```

## 八、双 Y 轴图与误差线图

### 8.1 双 Y 轴图（twinx）

当两个指标量级差异很大时非常有用：

```python
# 场景：同一天的温度和湿度（量级不同）
days = np.arange(1, 31)
humidity = 80 - daily_avg * 1.5 + np.random.normal(0, 8, 30)  # 模拟湿度
humidity = np.clip(humidity, 30, 95)

fig, ax1 = plt.subplots(figsize=(12, 5))

# 左 Y 轴：温度
color_temp = "#E63946"
ax1.plot(days, daily_avg, color=color_temp, marker="o", linewidth=2, label="温度")
ax1.set_xlabel("日期")
ax1.set_ylabel("温度 (°C)", color=color_temp)
ax1.tick_params(axis="y", labelcolor=color_temp)
ax1.fill_between(days, daily_avg, 30, where=(daily_avg > 30),
                 color=color_temp, alpha=0.1)

# 右 Y 轴：湿度（共享 X 轴）
ax2 = ax1.twinx()
color_hum = "#457B9D"
ax2.plot(days, humidity, color=color_hum, marker="s", linewidth=2, linestyle="--", label="湿度")
ax2.set_ylabel("湿度 (%)", color=color_hum)
ax2.tick_params(axis="y", labelcolor=color_hum)
ax2.set_ylim(0, 100)

# 合并图例
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

ax1.set_title("6月温度与湿度趋势（双Y轴）", fontsize=14, fontweight="bold")
ax1.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
```

### 8.2 误差线图（errorbar）

展示数据的均值和波动范围：

```python
# 计算每小时的平均温度和标准差
hourly_mean = temps.mean(axis=0)
hourly_std = temps.std(axis=0)
hours = np.arange(24)

fig, ax = plt.subplots(figsize=(12, 5))

ax.errorbar(
    hours, hourly_mean,
    yerr=hourly_std,               # 误差（标准差）
    fmt="o-",                      # 格式: 圆点+连线
    color="#2196F3",
    ecolor="#90CAF9",              # 误差线颜色
    elinewidth=2,                  # 误差线宽度
    capsize=4,                     # 误差线端点帽子大小
    capthick=1.5,                  # 帽子线宽
    markersize=5,
    linewidth=2,
    label="小时均温 ± 标准差"
)

# 标注最热和最冷时段
hottest_hour = np.argmax(hourly_mean)
coldest_hour = np.argmin(hourly_mean)
ax.annotate(f"{hourly_mean[hottest_hour]:.1f}°C",
            xy=(hottest_hour, hourly_mean[hottest_hour]),
            xytext=(hottest_hour+1, hourly_mean[hottest_hour]+1),
            arrowprops=dict(arrowstyle="->"), fontsize=10)
ax.annotate(f"{hourly_mean[coldest_hour]:.1f}°C",
            xy=(coldest_hour, hourly_mean[coldest_hour]),
            xytext=(coldest_hour+1, hourly_mean[coldest_hour]-2),
            arrowprops=dict(arrowstyle="->"), fontsize=10)

ax.set_xticks(range(0, 24, 2))
ax.set_xticklabels([f"{h}:00" for h in range(0, 24, 2)])
ax.set_xlabel("小时")
ax.set_ylabel("温度 (°C)")
ax.set_title("6月每小时平均温度（带标准差）", fontsize=14, fontweight="bold")
ax.legend()
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

# 面试话术: "errorbar 同时展示集中趋势（均值）和离散程度（标准差），
#           比单独画均值折线图信息量更大。尤其适合 A/B 测试效果对比。"
```

## 九、子图布局详解

### 9.1 subplots 常用参数

```python
# subplots 基础用法
fig, axes = plt.subplots(
    nrows=2, ncols=3,           # 2行3列，共6个子图
    figsize=(15, 8),            # 总画布大小
    sharex=True,                # 所有子图共享 X 轴刻度
    sharey="row",               # 同一行的子图共享 Y 轴
    gridspec_kw={               # 传给 GridSpec 的参数
        "hspace": 0.3,          # 行间距（高度的 30%）
        "wspace": 0.2,          # 列间距（宽度的 20%）
        "height_ratios": [2, 1],# 第一行高度是第二行的 2 倍
        "width_ratios": [2, 1, 1],  # 第一列宽度是后两列的 2 倍
    },
)

# axes 是 (2, 3) 的 ndarray，用 axes[i, j] 访问每个子图
# 如果只有一行: axes 是一维的; 如果只有一个子图: axes 是 Axes 对象本身
```

### 9.2 gridspec：不规则布局

```python
import matplotlib.gridspec as gridspec

fig = plt.figure(figsize=(14, 8))
gs = gridspec.GridSpec(3, 3, figure=fig,
                       hspace=0.4, wspace=0.3)

# 左上: 跨 2 行 2 列的大图
ax_big = fig.add_subplot(gs[0:2, 0:2])
ax_big.plot(x, y, color="#2196F3", linewidth=2)
ax_big.set_title("主图：温度趋势（占 2×2）", fontsize=12)

# 右上: 单格图
ax_topright = fig.add_subplot(gs[0, 2])
ax_topright.bar(categories, gmv, color=colors)
ax_topright.set_title("品类 GMV", fontsize=10)
ax_topright.tick_params(labelsize=7)

# 右中: 单格图
ax_midright = fig.add_subplot(gs[1, 2])
ax_midright.hist(daily_avg, bins=10, color="#4ECDC4", edgecolor="white")
ax_midright.set_title("温度分布", fontsize=10)

# 底部: 跨 3 列的宽图
ax_wide = fig.add_subplot(gs[2, :])
ax_wide.bar(hours, hourly_mean, color="#FFEAA7", edgecolor="#E9C46A")
ax_wide.set_title("每小时平均温度（跨 3 列）", fontsize=12)
ax_wide.set_xlabel("小时")

plt.suptitle("GridSpec 不规则布局示例", fontsize=14, fontweight="bold", y=0.98)
plt.tight_layout()
plt.show()
```

### 9.3 subplot2grid：更简单的不规则布局

```python
# subplot2grid 比 gridspec 更直观，适合简单的不规则布局
fig = plt.figure(figsize=(14, 10))

ax1 = plt.subplot2grid((4, 3), (0, 0), colspan=3)        # 第1行，跨3列
ax2 = plt.subplot2grid((4, 3), (1, 0), rowspan=2)        # 第2-3行，第1列
ax3 = plt.subplot2grid((4, 3), (1, 1), rowspan=2, colspan=2)  # 第2-3行，第2-3列
ax4 = plt.subplot2grid((4, 3), (3, 0), colspan=3)        # 第4行，跨3列

# 语法: subplot2grid(总网格(rows, cols), 起始位置(row, col), rowspan=, colspan=)

ax1.plot(x, y)
ax1.set_title("趋势总览")
ax2.barh(categories, gmv, color=colors)  # barh = 水平柱状图
ax2.set_title("品类 GMV 对比")
ax3.hist(amounts, bins=50, color="#2196F3")
ax3.set_title("金额分布")
ax4.errorbar(hours, hourly_mean, yerr=hourly_std, fmt="o-", capsize=3)
ax4.set_title("每小时温度（带误差线）")

plt.tight_layout()
plt.show()
```

## 十、用图表讲故事：数据分析报告四件套

面试和实际工作中，一个完整的数据分析报告通常包含四张图：

```python
# ===== 场景：6 月气温数据分析报告 =====
fig = plt.figure(figsize=(16, 12))
gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.35, wspace=0.3)

# === 图 1: 趋势 — 折线图（发生了什么？）===
ax1 = fig.add_subplot(gs[0, 0])
ax1.plot(x, y, marker="o", color="#2196F3", linewidth=2, markersize=3)
ax1.axhline(y=30, color="red", linestyle="--", alpha=0.4, label="高温线 30°C")
ax1.fill_between(x, y, 30, where=(y > 30), color="red", alpha=0.08)
ax1.set_title("图1: 6月日均温度趋势", fontsize=13, fontweight="bold")
ax1.set_xlabel("日期"); ax1.set_ylabel("°C")
ax1.legend(fontsize=8)
ax1.grid(True, alpha=0.3)

# === 图 2: 对比 — 柱状图（哪几天最热？）===
ax2 = fig.add_subplot(gs[0, 1])
top5_idx = np.argsort(y)[-5:][::-1]  # 最热的5天
ax2.bar(range(5), y[top5_idx], color=["#E63946", "#E76F51", "#F4A261", "#E9C46A", "#F4A261"])
ax2.set_xticklabels([f"6月{d+1}日" for d in top5_idx])
ax2.set_title("图2: 最热的5天对比", fontsize=13, fontweight="bold")
ax2.set_ylabel("日均温 °C")
for i, val in enumerate(y[top5_idx]):
    ax2.text(i, val + 0.3, f"{val:.1f}", ha="center", fontsize=10)

# === 图 3: 分布 — 直方图（温度如何分布？）===
ax3 = fig.add_subplot(gs[1, 0])
ax3.hist(temps.flatten(), bins=30, color="#457B9D", edgecolor="white", alpha=0.85)
ax3.axvline(temps.mean(), color="red", linestyle="--", label=f"均值 {temps.mean():.1f}°C")
ax3.axvline(np.median(temps), color="green", linestyle="--", label=f"中位数 {np.median(temps):.1f}°C")
ax3.set_title("图3: 6月全部温度记录分布", fontsize=13, fontweight="bold")
ax3.set_xlabel("°C"); ax3.set_ylabel("记录数")
ax3.legend(fontsize=8)

# === 图 4: 关系 — 散点图（最高温 vs 最低温）===
ax4 = fig.add_subplot(gs[1, 1])
daily_max_vals = temps.max(axis=1)
daily_min_vals = temps.min(axis=1)
scatter = ax4.scatter(daily_max_vals, daily_min_vals, c=range(30), cmap="coolwarm",
                      s=80, edgecolors="white", linewidth=0.5, alpha=0.8)
# 标注每一天
for i in range(30):
    ax4.annotate(str(i+1), (daily_max_vals[i], daily_min_vals[i]),
                 textcoords="offset points", xytext=(3, 3), fontsize=7, alpha=0.7)
ax4.set_title("图4: 日最高温 vs 日最低温", fontsize=13, fontweight="bold")
ax4.set_xlabel("日最高温 °C"); ax4.set_ylabel("日最低温 °C")
cbar = plt.colorbar(scatter, ax=ax4, shrink=0.8)
cbar.set_label("日期", rotation=270, labelpad=12)

plt.suptitle("6月气温数据分析报告", fontsize=16, fontweight="bold", y=1.01)
plt.tight_layout()
plt.show()
```

**面试话术**："我用四张图讲一个分析故事：趋势折线图回答'发生了什么'，对比柱状图回答'哪几天最突出'，分布直方图回答'整体什么水平'，关系散点图回答'两个变量什么关系'。这样既有纵向观察又有横向对比，给业务方一目了然。"

## 十一、保存高清图专题

```python
# ===== 不同保存格式的选择 =====
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(x, y)
ax.set_title("示例图表")

# PNG — 通用格式，适合文档/PPT/网页
fig.savefig(
    "chart.png",
    dpi=300,                    # 分辨率（默认 100，打印用 300，屏幕用 150）
    bbox_inches="tight",        # 裁掉多余白边（推荐始终开启）
    facecolor="white",          # 画布背景色
    edgecolor="none",           # 画布边框色
    pad_inches=0.1,             # tight 模式下额外留白
    transparent=False,          # 是否透明背景
)

# SVG — 矢量格式，适合网页嵌入/后期编辑（AI/Figma）
fig.savefig(
    "chart.svg",
    format="svg",
    bbox_inches="tight",
    # SVG 无限放大不失真，文件小
)

# PDF — 矢量格式，适合论文/报告/印刷
fig.savefig(
    "chart.pdf",
    format="pdf",
    bbox_inches="tight",
    dpi=300,
)

# ===== 格式对比表 =====
```

| 格式 | 类型 | 文件大小 | 放大失真 | 最佳场景 |
|------|------|----------|----------|----------|
| PNG | 位图 | 中（dpi 越高越大） | 会模糊 | PPT、Word、网页、微信 |
| SVG | 矢量 | 小 | 不失真 | 网页嵌入、AI 编辑 |
| PDF | 矢量 | 中 | 不失真 | 论文插入（LaTeX）、打印 |
| JPG | 位图 | 小（有损压缩） | 会模糊 | 照片类、不推荐纯图表用 |

```python
# ===== dpi, bbox_inches, figsize 的配合 =====
# figsize 决定"画布有多大"，dpi 决定"每英寸多少像素"
# 最终像素 = figsize(dpi) × dpi
# 例: figsize=(12,6), dpi=300 → 输出图片 3600×1800 像素

# 经验值:
#   屏幕查看: dpi=150, figsize=(10, 5)
#   PPT 演示: dpi=200, figsize=(12, 6)
#   打印/论文: dpi=300, figsize=(8, 4)
#   官网展示: SVG, figsize 随便

# 面试话术: "给业务方看用 PNG 150dpi 就够了；插入论文用 PDF；网页嵌入用 SVG。
#            bbox_inches='tight' 可以剪掉多余白边，几乎每张图都应该加。"
```

## 十二、面试图表选择决策树（详细版）

原来的选择表太粗糙了。面试官可能会追问"为什么不用箱线图而用直方图"这类问题。

从三个维度交叉判断：

```
                            你要看什么？
                                 │
              ┌──────────────────┼──────────────────┐
            趋势/变化         比较/排序           分布/关系
              │                  │                  │
        数据是连续的？      几个类别？         数据类型？
         │       │          │      │           │       │
       是       否        ≤6     >6        数值    两个数值
        │       │         │      │           │        │
     折线图   柱状图    饼图   柱状图      ┌──┴──┐  散点图
   (时间轴)  (离散点)  (占比) (横向)   样本   样本   (+回归线
              │                        <100   ≥100   看相关性)
           注意:                       │      │
           数据量>1000              箱线图  直方图
           用折线图也可           (看离群值) (看形状)

数据有三个以上维度时:
  二维 + 分组 → 分组箱线图/分组柱状图
  三维 → 气泡图 (x, y, 气泡大小) 或 三维散点图
  多维 → 平行坐标图 / 雷达图 / 相关性热力图
```

**面试对话**：
> Q: "为什么这里用箱线图而不是直方图？"
> A: "因为要对比5个品类的分布，5个直方图不好对齐比较，箱线图排在一行，中位数、四分位数、异常值一目了然。"
>
> Q: "饼图有什么坑？"
> A: "第一，类别超过6个饼图就分不清了（碎成渣），改用柱状图。第二，人眼对角度不敏感，对比不精确，关键数据要在旁边标数值。第三，3D饼图不要用——透视变形让某些扇形看起来比实际大。"

## 十三、三种风格模板

```python
# 1. 基础风格（日常分析）
plt.style.use("default")

# 2. 学术风格（报告/论文）
plt.style.use("seaborn-v0_8-whitegrid")

# 3. 深色风格（PPT演示）
plt.style.use("dark_background")
```

## 十四、面试必答的图表选择（速查版）

> "给你一份数据，你会选什么图表？"

| 想看什么 | 用什么图 | 原因 |
|----------|---------|------|
| 变化趋势 | 折线图 | 时间序列首选，一眼看走势 |
| 大小对比 | 柱状图 | 类别间绝对值比较 |
| 占比构成 | 饼图/环形图 | 看谁多谁少（< 6 个类别时用） |
| 分布形状 | 直方图/箱线图 | 看数据集中在哪、有没有异常值 |
| 相互关系 | 散点图 | 两个变量是否相关 |
| 矩阵模式 | 热力图 | 二维数据看聚类和模式 |

## 面试高频考点小结

| 考点 | 考察频率 | 关键点 |
|------|----------|--------|
| 图表选择原则 | ★★★★★ | 趋势→折线，对比→柱状，占比→饼图，分布→直方图/箱线图 |
| 中文显示设置 | ★★★★★ | font.sans-serif + axes.unicode_minus，三平台方案 |
| subplots 子图布局 | ★★★★☆ | nrows/ncols/sharex/sharey/figsize/gridspec_kw |
| 配色与美化 | ★★★★☆ | seaborn 色板、色盲友好配色、annotate 标注 |
| 保存参数 | ★★★★☆ | dpi/bbox_inches/figsize 配合，PNG vs SVG vs PDF |
| 热力图 | ★★★☆☆ | imshow + colorbar + cmap 选择 |
| Seaborn 图表 | ★★★☆☆ | boxplot/violinplot/heatmap/pairplot |
| 双 Y 轴 | ★★★☆☆ | twinx() + 颜色区分 + 合并图例 |
| 误差线图 | ★★★☆☆ | errorbar(x, y, yerr=std) 展示均值和波动 |
| GridSpec 不规则布局 | ★★☆☆☆ | gridspec.GridSpec + add_subplot(slice) |
| subplot2grid | ★★☆☆☆ | 比 gridspec 更直观的不规则布局 |
| 3D 饼图/伪 3D | ★★☆☆☆ | 不要用——透视变形误导读者 |
| annotate/text 标注 | ★★★☆☆ | xy 定位点 + xytext 文字位置 + arrowprops 箭头 |

## 相关笔记

- [[工作学习/Python数据栈/numpy基础]]
- [[工作学习/Python数据栈/pandas实战-电商订单分析]]
