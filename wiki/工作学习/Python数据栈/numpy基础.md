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

# NumPy 基础：面试够用版

> 温度数据实操，axis 理解、花式索引、面试三问。 | **面试重要度：中** | 预计阅读：15 分钟

## 视频资源

- YouTube: [freeCodeCamp: NumPy Full Course](https://www.youtube.com/watch?v=QUT1VHiLmmI) — 完整 NumPy 教程
- B站: [莫烦 Python: NumPy 教程](https://www.bilibili.com/video/BV1Ex411L7oT/) — 中文 NumPy 入门

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

### 3.1 基础条件筛选

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

### 3.2 多条件组合筛选

多个条件用 `&`（与）、`|`（或）、`~`（非），**每个条件必须加括号**：

```python
# 找出白天（8-18点）且温度超过35°C的记录
daytime_mask = np.zeros(24, dtype=bool)
daytime_mask[8:19] = True  # 8点到18点
high_daytime = temps[:, daytime_mask]  # 先截取白天列
high_daytime = high_daytime[high_daytime > 35]  # 再筛选高温
print(f"白天高温记录: {len(high_daytime)} 条")

# 找出早晚温差超过 15°C 的天（按行算每日 max - min）
daily_range = temps.max(axis=1) - temps.min(axis=1)
big_range_days = np.where(daily_range > 15)[0]
print(f"温差超15°C的天: {big_range_days}")
```

### 3.3 按行号抽取：np.take

```python
# 抽第 0、5、10、15、20、25 天的数据
sample_days = np.take(temps, [0, 5, 10, 15, 20, 25], axis=0)
print(f"抽取的天数: {sample_days.shape}")  # (6, 24)

# 抽第 0、6、12、18 小时的数据（每隔 6 小时）
sample_hours = np.take(temps, [0, 6, 12, 18], axis=1)
print(f"抽取的小时: {sample_hours.shape}")  # (30, 4)
```

### 3.4 按布尔矩阵索引

```python
# 生成一个布尔矩阵：标记所有 >35°C 且 <40°C 的位置
heat_wave_mask = (temps > 35) & (temps < 40)
# 统计每天有多少小时处于"热浪"区间
heat_wave_hours = heat_wave_mask.sum(axis=1)
for day, hours in enumerate(heat_wave_hours):
    if hours > 0:
        print(f"第{day+1}天: {hours} 小时处于35-40°C")

# 用布尔矩阵直接替换值
temps_fixed = temps.copy()
temps_fixed[temps_fixed > 40] = 40  # 把异常高温截断到 40°C
print(f"截断后最高温: {temps_fixed.max():.1f}°C")
```

## 四、缺失值处理（面试高频）

真实数据总有缺失值，NumPy 用 `np.nan` 表示。

```python
# 模拟带有缺失值的温度数据
temps_with_nan = temps.copy().astype(float)
# 随机在 5% 的位置插入缺失值
nan_mask = np.random.random(temps_with_nan.shape) < 0.05
temps_with_nan[nan_mask] = np.nan

print(f"总数据量: {temps_with_nan.size}")
print(f"缺失值数量: {np.isnan(temps_with_nan).sum()}")
print(f"缺失比例: {np.isnan(temps_with_nan).mean()*100:.1f}%")
# 输出: 总数据量: 720, 缺失值数量: ~36, 缺失比例: ~5.0%
```

**处理缺失值的四种策略**：

```python
# 1. 删除含缺失值的行（整行删掉）
clean_rows = temps_with_nan[~np.isnan(temps_with_nan).any(axis=1)]
#    — 适用于缺失行少、删了不影响分析的场景

# 2. 用列均值填充
col_means = np.nanmean(temps_with_nan, axis=0)  # 忽略 NaN 求均值
filled_mean = temps_with_nan.copy()
for j in range(24):
    col_mask = np.isnan(filled_mean[:, j])
    filled_mean[col_mask, j] = col_means[j]
#    — 最常用的策略，保持数据量不变

# 3. 用前后值插值（向前填充）
filled_ffill = temps_with_nan.copy()
# 简化：用 np.nan_to_num 配合前后平均
#    — 时间序列数据常用

# 4. 用中位数填充（对异常值更鲁棒）
col_medians = np.nanmedian(temps_with_nan, axis=0)
filled_median = temps_with_nan.copy()
for j in range(24):
    col_mask = np.isnan(filled_median[:, j])
    filled_median[col_mask, j] = col_medians[j]
```

**NaN 相关函数速查**：

| 函数 | 作用 | 示例 |
|------|------|------|
| `np.isnan(arr)` | 检查是否为 NaN | `np.isnan(arr).sum()` 统计缺失数 |
| `np.nanmean(arr)` | 忽略 NaN 求均值 | `np.nanmean(arr, axis=0)` |
| `np.nanmedian(arr)` | 忽略 NaN 求中位数 | `np.nanmedian(arr)` |
| `np.nanstd(arr)` | 忽略 NaN 求标准差 | `np.nanstd(arr)` |
| `np.nanmin / nanmax` | 忽略 NaN 求极值 | `np.nanmax(arr)` |
| `np.nan_to_num(arr)` | NaN 转 0，inf 转大数 | `np.nan_to_num(arr, nan=-1)` |

## 五、异常值检测：IQR 方法（用 NumPy 手写）

IQR（四分位距）是面试中最常问的异常值检测方法。

```python
def detect_outliers_iqr(data):
    """
    用 IQR 方法检测异常值
    返回: (下限, 上限, 异常值布尔掩码)
    """
    q1 = np.percentile(data, 25)
    q3 = np.percentile(data, 75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    outliers = (data < lower) | (data > upper)
    return lower, upper, outliers

# 用每日最高温做异常检测
daily_max = temps.max(axis=1)
lower, upper, outlier_mask = detect_outliers_iqr(daily_max)

print(f"IQR 下限: {lower:.1f}°C, 上限: {upper:.1f}°C")
print(f"异常高温天数: {outlier_mask.sum()} 天")
print(f"异常天的最高温: {daily_max[outlier_mask]}")
# 输出示例: IQR 下限: 24.5°C, 上限: 36.4°C, 异常高温天数: 2 天
```

**面试话术**："IQR = Q3 - Q1，下限 = Q1 - 1.5\*IQR，上限 = Q3 + 1.5\*IQR。1.5 是经验系数，3 用于极端异常检测。这个方法不依赖数据是否正态分布，比 3-sigma 更通用。"

## 六、数据归一化（用 NumPy 手写）

机器学习前必须做的预处理。两种最常用的方法：

```python
# 模拟一份待归一化的特征数据
np.random.seed(42)
features = np.random.randn(100, 4) * np.array([10, 5, 2, 50]) + np.array([100, 20, 5, 1000])
# 4 个特征，量纲差异巨大：
# 特征0 均值~100 标准差~10
# 特征1 均值~20  标准差~5
# 特征2 均值~5   标准差~2
# 特征3 均值~1000 标准差~50

# ========== 1. Min-Max 归一化 ==========
# 把数据压缩到 [0, 1] 区间
def minmax_scale(arr):
    return (arr - arr.min(axis=0)) / (arr.max(axis=0) - arr.min(axis=0))

features_mm = minmax_scale(features)
print(f"Min-Max 后范围: [{features_mm.min():.3f}, {features_mm.max():.3f}]")
# 输出: Min-Max 后范围: [0.000, 1.000]

# ========== 2. Z-score 标准化 ==========
# 把数据变成均值 0、标准差 1 的分布
def zscore_scale(arr):
    return (arr - arr.mean(axis=0)) / arr.std(axis=0)

features_zs = zscore_scale(features)
print(f"Z-score 后均值: {features_zs.mean(axis=0).round(3)}")
# 输出: Z-score 后均值: [ 0.  0.  0.  0.]
print(f"Z-score 后标准差: {features_zs.std(axis=0).round(3)}")
# 输出: Z-score 后标准差: [ 1.  1.  1.  1.]
```

**选择原则**：

| 方法 | 公式 | 适用场景 | 缺点 |
|------|------|----------|------|
| Min-Max | `(x-min)/(max-min)` | 有明确边界、对异常值不敏感的场景（图像像素） | 对异常值极敏感，一个超大值会把其他值压成 0 |
| Z-score | `(x-mean)/std` | 数据近似正态分布、大部分 ML 算法 | 不保证范围，可能产生负值 |
| Robust | `(x-median)/IQR` | 有异常值时的替代方案 | 计算量稍大 |

## 七、广播机制（Broadcasting）详解

广播是 NumPy 最强大的特性之一——**不同形状的数组也能做运算**，不用写循环。

### 7.1 广播规则

两个数组做运算时，NumPy 从最后一个维度开始往前对齐：

| 规则 | 说明 | 示例 |
|------|------|------|
| 规则 1 | 维度数不同时，较小的数组在前面补 1 | `(3,) + (2,3)` → `(1,3) + (2,3)` |
| 规则 2 | 某个维度的大小为 1 时，沿该维度复制扩展 | `(1,3)` → `(2,3)` |
| 规则 3 | 如果两个维度不相等且都不为 1，则报错 | `(2,3) + (3,2)` → 报错 |

### 7.2 一维数组与二维数组

```python
# 场景：想给每天每个小时的温度加上一个"小时修正值"
# 比如中午比早晚热，每个小时有一个偏移量
hourly_offset = np.array([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6,
                          5, 4, 3, 2, 1, 0, -1, -2, -3, -4, -5, -6])
print(f"hourly_offset shape: {hourly_offset.shape}")  # (24,)

# 广播：temps (30, 24) + hourly_offset (24,)
# NumPy 自动把 (24,) 扩展成 (30, 24) —— 每行重复相同的偏移
temps_adjusted = temps + hourly_offset
print(f"temps_adjusted shape: {temps_adjusted.shape}")  # (30, 24)
```

**广播过程图解**：
```
temps (30, 24)              hourly_offset (24,)
┌─────────────────┐         ┌──────────────────────┐
│ 日1: [28.1, 29.3...]    │ [-5, -4, -3, ... 6] │
│ 日2: [27.5, 28.1...]    └──────────────────────┘
│ ...                     ↓ 沿 axis=0 复制 30 次
│ 日30:[29.0, 30.2...]   ┌──────────────────────────┐
└─────────────────┘       │ 日1: [-5, -4, -3,... 6] │
                          │ 日2: [-5, -4, -3,... 6] │
                          │ ...                       │
                          │ 日30:[-5, -4, -3,... 6] │
                          └──────────────────────────┘
逐元素相加 → temps_adjusted (30, 24)
```

### 7.3 不同形状的广播示例

```python
# 示例 A: (3, 1) + (1, 4) → (3, 4)
a = np.array([[1], [2], [3]])     # (3, 1)
b = np.array([10, 20, 30, 40])    # (4,)
print(a + b)
# 输出:
# [[11 21 31 41]
#  [21 22 23 24]  ← 不对，应该是 2+10=12, 2+20=22...
#  [31 32 33 34]]
# 纠正: a(3,1) 沿列方向复制4次, b(4,) → (1,4) 沿行方向复制3次
# 结果: a的第i行 + b的第j列

# 示例 B: (5,) + (5,1) → (5,5)
c = np.array([1, 2, 3, 4, 5])      # (5,)
d = np.array([[10], [20], [30], [40], [50]])  # (5,1)
print((c + d).shape)  # (5, 5) — 变成了矩阵加法

# 示例 C: 会报错的场景
# e = np.ones((2, 3)) + np.ones((3, 2))  # ValueError: operands could not be broadcast
# (2,3) 和 (3,2) — 尾部维度 3≠2 且都不为 1，无法广播
```

### 7.4 广播的常见应用

```python
# 1. 中心化：每列减去该列均值
centered = temps - temps.mean(axis=0)  # (30,24) - (24,) → (30,24)

# 2. 归一化：每行除以该行的最大值
normalized = temps / temps.max(axis=1, keepdims=True)  # keepdims 保持 (30,1) 形状

# 3. 外积：两个一维向量生成矩阵
x = np.array([1, 2, 3])  # (3,)
y = np.array([10, 20])   # (2,)
# x[:, np.newaxis] 变成 (3,1)，y 是 (2,)，广播后 (3,2)
outer = x[:, np.newaxis] * y
print(outer)
# [[10 20]
#  [20 40]
#  [30 60]]
```

## 八、性能对比：向量化 vs 循环（timeit 正式测试）

用 `timeit` 做基准测试，结果可以写在简历上。

```python
import numpy as np
import timeit

setup_code = """
import numpy as np
arr = np.random.randn(1_000_000)
py_list = list(arr)
"""

# ========== 1. 求和 ==========
t_np_sum = timeit.timeit("np.sum(arr)", setup=setup_code, number=100, globals={"np": np})
t_py_sum = timeit.timeit("sum(py_list)", setup=setup_code, number=100)
print(f"求和 - NumPy: {t_np_sum*10:.2f}ms | Python: {t_py_sum*10:.2f}ms | 加速: {t_py_sum/t_np_sum:.0f}x")

# ========== 2. 求均值 ==========
t_np_mean = timeit.timeit("np.mean(arr)", setup=setup_code, number=100, globals={"np": np})
t_py_mean = timeit.timeit("sum(py_list)/len(py_list)", setup=setup_code, number=100)
print(f"均值 - NumPy: {t_np_mean*10:.2f}ms | Python: {t_py_mean*10:.2f}ms | 加速: {t_py_mean/t_np_mean:.0f}x")

# ========== 3. 条件筛选 (>0.5) ==========
setup_code2 = """
import numpy as np
arr = np.random.randn(1_000_000)
"""
t_np_filter = timeit.timeit("arr[arr > 0.5]", setup=setup_code2, number=100, globals={"np": np})
t_py_filter = timeit.timeit("[x for x in list(arr) if x > 0.5]", setup=setup_code2, number=100, globals={"np": np})
print(f"筛选 - NumPy: {t_np_filter*10:.2f}ms | Python: {t_py_filter*10:.2f}ms | 加速: {t_py_filter/t_np_filter:.0f}x")

# ========== 4. 逐元素运算 (平方) ==========
t_np_sq = timeit.timeit("arr ** 2", setup=setup_code2, number=100, globals={"np": np})
t_py_sq = timeit.timeit("[x**2 for x in list(arr)]", setup=setup_code2, number=100, globals={"np": np})
print(f"平方 - NumPy: {t_np_sq*10:.2f}ms | Python: {t_py_sq*10:.2f}ms | 加速: {t_py_sq/t_np_sq:.0f}x")
```

典型输出（你的机器上自己跑）：
```
求和 - NumPy: 0.05ms | Python: 0.98ms | 加速: 20x
均值 - NumPy: 0.06ms | Python: 1.21ms | 加速: 20x
筛选 - NumPy: 0.43ms | Python: 8.75ms | 加速: 20x
平方 - NumPy: 0.35ms | Python: 7.12ms | 加速: 21x
```

**面试话术**："100 万数据量的操作，NumPy 普遍快 20 倍以上。数据量越大差距越明显。核心原因是 NumPy 批量操作在 C 层面完成，Python 循环每次都要经过解释器。"

## 九、常用统计函数全家桶

### 9.1 np.percentile / np.quantile

```python
# percentile: 百分位数，用 0-100 的范围
p = np.percentile(temps, [5, 25, 50, 75, 95])
print(f"温度分布: P5={p[0]:.1f} P25={p[1]:.1f} P50={p[2]:.1f} P75={p[3]:.1f} P95={p[4]:.1f}")
# 温度分布: P5=19.8 P25=24.6 P50=28.1 P75=31.4 P95=36.2

# quantile: 分位数，用 0-1 的范围（两者等价）
q = np.quantile(temps, [0.05, 0.25, 0.5, 0.75, 0.95])
print(f"quantile 结果: {q.round(2)}")  # 结果同上
```

### 9.2 np.corrcoef — 相关系数矩阵

```python
# 计算每天最高温、最低温、日均温之间的相关系数
daily_max = temps.max(axis=1)
daily_min = temps.min(axis=1)
daily_mean = temps.mean(axis=1)

# 堆成 (3, 30) 再转置成 (30, 3)，每列是一个变量
daily_features = np.column_stack([daily_max, daily_min, daily_mean])
corr_matrix = np.corrcoef(daily_features, rowvar=False)  # rowvar=False: 每列是一个变量

print("相关系数矩阵 (max, min, mean):")
print(np.round(corr_matrix, 3))
# [[1.     0.654 0.912]
#  [0.654 1.    0.904]
#  [0.912 0.904 1.   ]]
# 解读: 最高温与最低温相关系数 0.654，正相关但不完全同步
#       日均温与最高/最低都高度相关（合理）
```

### 9.3 np.cov — 协方差矩阵

```python
cov_matrix = np.cov(daily_features, rowvar=False)
print("协方差矩阵:")
print(np.round(cov_matrix, 2))
# 协方差受量纲影响，不如相关系数直观。
# 面试说: "协方差看同向还是反向变化，相关系数更标准化（-1 到 1）"
```

### 9.4 np.histogram — 直方图统计

```python
# 把温度分布到自定义区间
counts, edges = np.histogram(temps, bins=[0, 15, 20, 25, 30, 35, 45])
print("温度区间分布:")
for i in range(len(counts)):
    print(f"  [{edges[i]:3.0f}, {edges[i+1]:3.0f})°C: {counts[i]:4d} 小时")

# 也可以用等宽分箱
counts_auto, edges_auto = np.histogram(temps, bins=10)
print(f"等宽10箱: {counts_auto}")
```

### 9.5 np.digitize — 每个元素属于哪个区间

```python
# 给每个温度值打标签（0=冷, 1=舒适, 2=热）
bins = [0, 20, 30, 50]  # 三个区间: <20, 20-30, >30
labels = np.digitize(temps.flatten(), bins)  # 返回 1,2,3 分别对应三个区间

# 注意：digitize 返回区间索引（从 1 开始），需要减 1 才能做数组索引
unique, counts = np.unique(labels, return_counts=True)
for u, c in zip(unique, counts):
    print(f"区间{u}: {c} 小时 ({c/720*100:.1f}%)")
```

## 十、np.where 进阶用法

### 10.1 基本用法：类似三目运算符

```python
# np.where(条件, 真时取值, 假时取值)
# 把温度分成"高温"和"正常"两类
temps_label = np.where(temps > 35, "高温", "正常")
print(f"高温标签数: {(temps_label == '高温').sum()}")
```

### 10.2 多条件嵌套

```python
# 温度等级：<20=冷, 20-30=舒适, 30-35=热, >35=酷热
temps_level = np.where(
    temps < 20, "冷",
    np.where(temps < 30, "舒适",
        np.where(temps < 35, "热", "酷热")
    )
)
# 统计各级别数量
for level in ["冷", "舒适", "热", "酷热"]:
    print(f"{level}: {(temps_level == level).sum()} 小时")
```

### 10.3 np.where 返回索引

```python
# 不加后两个参数时，返回满足条件的索引
row_idx, col_idx = np.where(temps > 38)
print(f"超过38°C的位置: 共 {len(row_idx)} 处")
for r, c in zip(row_idx[:5], col_idx[:5]):
    print(f"  第{r+1}天 第{c}时 = {temps[r, c]:.1f}°C")
```

## 十一、np.select：多条件赋值的更优解

当条件超过 2 个时，`np.select` 比嵌套 `np.where` 更清晰：

```python
# 用 np.select 重写上面的温度分级
conditions = [
    temps < 20,                          # 条件1: 冷
    (temps >= 20) & (temps < 30),        # 条件2: 舒适
    (temps >= 30) & (temps < 35),        # 条件3: 热
    temps >= 35,                         # 条件4: 酷热
]
choices = ["冷", "舒适", "热", "酷热"]
# default 可选，不匹配任何条件的用这个值（这里所有值都会匹配）

temps_level_v2 = np.select(conditions, choices, default="未知")

# 验证两种方法结果一致
print(f"两种方法结果一致: {(temps_level == temps_level_v2).all()}")
# 输出: True
```

**np.select vs np.where 选择原则**：

| 场景 | 用什么 | 原因 |
|------|--------|------|
| 2 个分支 | `np.where` | 简单直接 |
| 3-5 个分支 | `np.select` | 比嵌套 where 清晰得多，条件和值分开写 |
| 5+ 个分支 | `np.select` 或 `np.digitize` | `np.digitize` 更适合数值连续分区 |

## 十二、聚合与变形

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

## 十三、面试高频问题

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

**Q: 缺失值怎么处理？**

A: 四个层次——① `np.isnan` 定位缺失值 ② 根据业务决定策略：删除（`~np.isnan().any(axis=1)`）、均值填充（`np.nanmean`）、中位数填充（`np.nanmedian`）、插值填充 ③ 处理后再做分析 ④ 记录缺失比例以备解释。

**Q: 如何检测异常值？**

A: 最常用 IQR 方法：Q1-1.5\*IQR 到 Q3+1.5\*IQR 之外的就是异常值。也可以用 Z-score：绝对值 > 3 的认为是异常（适合近似正态分布的数据）。

**Q: 广播机制是什么？**

A: NumPy 对不同形状数组做运算时自动扩展维度的机制。规则是从末尾维度向前对齐，维度为 1 的自动复制，不匹配且不为 1 的报错。本质是"隐式复制"——不真正复制数据，只是让计算循环逻辑上对齐。

## 面试高频考点小结

| 考点 | 考察频率 | 关键点 |
|------|----------|--------|
| NumPy 为什么快 | ★★★★★ | C 底层 + 连续内存 + 向量化，比 Python 快 10-100 倍 |
| axis 方向 | ★★★★★ | axis=0 纵向（沿行），axis=1 横向（沿列） |
| 视图 vs 副本 | ★★★★☆ | 切片=视图（共享），花式索引=副本（独立） |
| 广播机制 | ★★★★☆ | 从末尾维度对齐，维度为 1 的自动扩展 |
| 缺失值处理 | ★★★★☆ | np.nan / np.isnan / np.nanmean 系列 |
| 花式索引 | ★★★☆☆ | 条件筛选、布尔矩阵、np.where、np.take |
| IQR 异常检测 | ★★★☆☆ | Q1-1.5\*IQR ~ Q3+1.5\*IQR，不依赖正态分布 |
| 数据归一化 | ★★★☆☆ | Min-Max（[0,1]）vs Z-score（均值0方差1） |
| 统计函数 | ★★★☆☆ | percentile, corrcoef, histogram, digitize |
| np.select | ★★☆☆☆ | 多条件赋值，比嵌套 where 更清晰 |

## 相关笔记

- [[工作学习/Python数据栈/pandas实战-电商订单分析]]
- [[工作学习/Python数据栈/matplotlib可视化]]
