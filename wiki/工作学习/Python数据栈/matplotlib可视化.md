---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/python"
  - "#技术/数据分析"
  - "#状态/草稿"
created: 2026-06-26
updated: 2026-06-26
status: draft
---

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

## 六、面试必答的图表选择

> "给你一份数据，你会选什么图表？"

| 想看什么 | 用什么图 | 原因 |
|----------|---------|------|
| 变化趋势 | 折线图 | 时间序列首选，一眼看走势 |
| 大小对比 | 柱状图 | 类别间绝对值比较 |
| 占比构成 | 饼图/环形图 | 看谁多谁少（< 6 个类别时用） |
| 分布形状 | 直方图/箱线图 | 看数据集中在哪、有没有异常值 |
| 相互关系 | 散点图 | 两个变量是否相关 |
| 矩阵模式 | 热力图 | 二维数据看聚类和模式 |

## 三种风格模板

```python
# 1. 基础风格（日常分析）
plt.style.use("default")

# 2. 学术风格（报告/论文）
plt.style.use("seaborn-v0_8-whitegrid")

# 3. 深色风格（PPT演示）
plt.style.use("dark_background")
```

## 相关笔记

- [[Python数据栈/pandas实战-电商订单分析]]
- [[Python数据栈/numpy基础]]
