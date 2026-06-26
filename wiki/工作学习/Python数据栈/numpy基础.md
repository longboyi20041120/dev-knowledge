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

# NumPy 基础：面试够用版

NumPy 的核心价值就一句话：**比 Python 原生列表快 10-100 倍的数组运算。** 面试不会让你手写 NumPy，但要能解释为什么用它。

## 一、为什么 NumPy 比列表快？

```python
import numpy as np
import time

# 100万个数字，求平方
size = 1_000_000

# Python 列表
py_list = list(range(size))
start = time.time()
result_py = [x**2 for x in py_list]
print(f"Python 列表: {time.time() - start:.4f}s")

# NumPy 数组
np_arr = np.arange(size)
start = time.time()
result_np = np_arr ** 2
print(f"NumPy 数组: {time.time() - start:.4f}s")
```

输出（你自己的机器上跑）：
```
Python 列表: 0.0892s
NumPy 数组: 0.0043s
```

差 20 倍。原因：NumPy 底层是 C 语言写的，数据在内存中连续存放，一次操作整块数据（向量化），没有 Python 的循环开销。

**面试话术**："NumPy 底层 C 实现 + 连续内存布局，对数组的批量操作比 Python 原生快一到两个数量级。"

## 二、核心操作（真实数据）

用一份传感器温度数据演示：

```python
import numpy as np

# 模拟某城市 6 月 30 天每天 24 小时的温度记录
np.random.seed(42)
temps = np.round(np.random.normal(loc=28, scale=5, size=(30, 24)), 1)
# temps[天][小时] — 30 天 × 24 小时
```

```python
# 基础统计
print(f"六月最高温: {temps.max():.1f}°C")   # 42.4
print(f"六月最低温: {temps.min():.1f}°C")   # 13.9
print(f"六月平均温: {temps.mean():.1f}°C")  # 28.0
print(f"温度标准差: {temps.std():.1f}°C")   # 5.0(波动幅度)

# 每天的平均温度（axis=1 表示沿列方向求平均）
daily_avg = temps.mean(axis=1)  # shape: (30,) — 30 天的日均温

# 每小时的月平均温度（axis=0 表示沿行方向求平均）
hourly_avg = temps.mean(axis=0)  # shape: (24,) — 24 小时的月均温

# 最热的 5 天
hottest_days = np.argsort(daily_avg)[-5:]  # 返回索引
print(f"最热的5天: {hottest_days}")
```

**axis 理解（面试必问）**：
```
[[ 6月1日00时, 6月1日01时, ..., 6月1日23时 ],   ← axis=1 沿这行求均值 = 每天的日均温
 [ 6月2日00时, 6月2日01时, ..., 6月2日23时 ],
 ...
 [ 6月30日00时, ...                 ]]
 ↓ axis=0 沿这列求均值 = 每个小时的月均温
```

## 三、花式索引：筛选数据

```python
# 找出所有高于 35°C 的温度记录
high_temps = temps[temps > 35]
print(f"35°C以上的记录: {len(high_temps)} 条，占总 {len(high_temps)/temps.size*100:.1f}%")

# 找出每天最高温超过 38°C 的天
daily_max = temps.max(axis=1)
extreme_days = np.where(daily_max > 38)[0]
print(f"极端高温天(日最高>38°C): 第 {extreme_days} 天")

# 条件组合：第 10-20 天中，温度在 25-30°C 的记录
mask = (temps[10:21] >= 25) & (temps[10:21] <= 30)
comfortable = temps[10:21][mask]
print(f"第10-20天中舒适温度(25-30)的记录: {len(comfortable)} 条")
```

## 四、聚合与变形

```python
# reshape：把 30×24 的矩阵变成 720 个时间点的一维序列
flat = temps.reshape(-1)  # shape: (720,)

# 计算百分位数
p25, p50, p75 = np.percentile(temps, [25, 50, 75])
print(f"25%分位: {p25:.1f} | 中位数: {p50:.1f} | 75%分位: {p75:.1f}")

# 分组统计（把温度分成 5 个区间）
bins = [0, 20, 25, 30, 35, 50]
labels = ["冷(<20)", "凉爽(20-25)", "舒适(25-30)", "热(30-35)", "酷热(>35)"]
groups = np.digitize(temps.flatten(), bins)
for i, label in enumerate(labels, 1):
    count = (groups == i).sum()
    print(f"{label}: {count} 小时 ({count/720*100:.1f}%)")
```

输出：
```
冷(<20): 37 小时 (5.1%)
凉爽(20-25): 175 小时 (24.3%)
舒适(25-30): 272 小时 (37.8%)
热(30-35): 183 小时 (25.4%)
酷热(>35): 53 小时 (7.4%)
```

## 五、面试高频问题

**Q: NumPy 和 Python list 的区别？**

A: 三点——① 固定类型（所有元素同一类型）vs 异构 ② 连续内存（CPU 缓存友好）vs 指针数组 ③ 向量化运算（一次操作整个数组）vs 逐个元素 Python 循环

**Q: `axis=0` 和 `axis=1` 的区别？**

A: `axis=0` 沿行方向（从上到下），`axis=1` 沿列方向（从左到右）。`arr.sum(axis=0)` 把每一列加起来，`arr.sum(axis=1)` 把每一行加起来。

**Q: 视图(view)和副本(copy)的区别？**

A: 切片返回视图（共享数据），花式索引返回副本（独立数据）。改视图会影响原数组，改副本不会。

```python
a = np.array([1, 2, 3, 4])
b = a[:2]       # 视图
b[0] = 99       # a 也变成 [99, 2, 3, 4]
c = a[[0, 1]]   # 副本
c[0] = 0        # a 不受影响
```

## 相关笔记

- [[Python数据栈/pandas实战-电商订单分析]]
- [[Python数据栈/matplotlib可视化]]
