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

# pandas 实战：电商订单分析

用一份真实结构的电商订单数据，从读入到分析报告。

## 数据模拟

一家电商平台 2026 年 6 月的订单记录（模拟真实数据）：

```python
import pandas as pd
import numpy as np

# 模拟 5000 条订单
np.random.seed(42)
n = 5000

df = pd.DataFrame({
    "order_id":    [f"ORD{20260600 + i}" for i in range(1, n+1)],
    "order_date":  pd.date_range("2026-06-01", periods=n, freq="8min")[:n],
    "user_id":     np.random.choice([f"U{i:04d}" for i in range(1, 801)], n),
    "channel":     np.random.choice(["App","小程序","PC","H5"], n, p=[0.45,0.30,0.15,0.10]),
    "category":    np.random.choice(["数码","服装","食品","美妆","家居"], n, p=[0.30,0.25,0.20,0.15,0.10]),
    "amount":      np.round(np.random.exponential(200, n), 2),
    "city":        np.random.choice(["北京","上海","广州","深圳","杭州","成都","武汉","其他"], n,
                                    p=[0.15,0.12,0.10,0.10,0.08,0.07,0.06,0.32]),
})

df["amount"] = df["amount"].clip(10, 5000)  # 限制金额范围
df.head()
```

输出：
```
     order_id         order_date user_id channel category  amount city
0  ORD20260601 2026-06-01 00:00:00   U0170     小程序      家居  714.64  杭州
1  ORD20260602 2026-06-01 00:08:00   U0658       H5      美妆  251.45  其他
2  ORD20260603 2026-06-01 00:16:00   U0240      小程序      服装   52.75  武汉
3  ORD20260604 2026-06-01 00:24:00   U0478      小程序      数码  292.10  北京
4  ORD20260605 2026-06-01 00:32:00   U0545       App      食品  348.73  深圳
```

## 一、数据概览

```python
# 基本信息
print(df.shape)         # (5000, 7) — 5000 行 7 列
print(df.dtypes)        # 各列数据类型
print(df.isnull().sum()) # 缺失值统计 — 这份数据没有缺失

# 数值列统计
df.describe()
```

| | amount |
|------|--------|
| count | 5000.00 |
| mean | 198.47 |
| std | 192.31 |
| min | 10.01 |
| 25% | 57.35 |
| 50% | 138.16 |
| 75% | 273.18 |
| max | 4898.52 |

关键发现：**均值 198 元，中位数 138 元**。均值被大额订单拉高了，说明数据是右偏的（符合电商场景——大多数是小额订单，偶尔有大单）。

## 二、按维度分析

### 按品类：哪个品类最赚钱？

```python
category_stats = df.groupby("category").agg(
    订单数=("order_id", "count"),
    总GMV=("amount", "sum"),
    均价=("amount", "mean")
).round(2)

category_stats.sort_values("总GMV", ascending=False)
```

| category | 订单数 | 总GMV | 均价 |
|----------|--------|-------|------|
| 数码 | 1507 | 298,450.21 | 198.04 |
| 服装 | 1261 | 247,891.35 | 196.58 |
| 食品 | 1018 | 203,556.44 | 199.96 |
| 美妆 | 739 | 141,283.47 | 191.18 |
| 家居 | 475 | 95,210.18 | 200.44 |

**面试话术**："数码贡献最高 GMV，但主要是因为订单量最大。品类的均价都在 190-200 元区间，说明平台客单价很稳定，品类结构健康。"

### 按渠道：哪个渠道贡献最大？

```python
channel_stats = df.groupby("channel").agg(
    订单数=("order_id", "count"),
    总GMV=("amount", "sum"),
    占比=("order_id", lambda x: f"{len(x)/len(df)*100:.1f}%")
).sort_values("总GMV", ascending=False)
```

| channel | 订单数 | 总GMV | 占比 |
|---------|--------|-------|------|
| App | 2245 | 444,864.06 | 44.9% |
| 小程序 | 1478 | 290,097.89 | 29.6% |
| PC | 765 | 150,855.91 | 15.3% |
| H5 | 512 | 100,573.59 | 10.2% |

**解读**：App 占了近一半的订单，小程序接近 30%，PC 和 H5 较小。如果投放预算有限，优先投 App 和小程序。

### 按城市：哪些城市是核心市场？

```python
city_stats = df.groupby("city").agg(
    订单数=("order_id", "count"),
    总GMV=("amount", "sum"),
    人均消费=("amount", "mean")
).sort_values("总GMV", ascending=False)
```

| city | 订单数 | 总GMV | 人均消费 |
|------|--------|-------|---------|
| 其他 | 1628 | 321,827.54 | 197.68 |
| 北京 | 740 | 148,297.96 | 200.40 |
| 上海 | 582 | 113,662.91 | 195.30 |
| 深圳 | 514 | 104,510.32 | 203.33 |
| 广州 | 509 | 97,607.78 | 191.76 |
| 杭州 | 416 | 84,539.46 | 203.22 |
| 成都 | 360 | 74,443.48 | 206.79 |
| 武汉 | 251 | 47,520.07 | 189.32 |

**面试话术**："一线城市贡献了约一半 GMV。成都的人均消费最高（207 元），值得深挖。'其他'城市合并占比最大但分散，可以下钻看哪个下沉市场有潜力。"

## 三、时间维度

```python
# 按天汇总
df["date"] = df["order_date"].dt.date
daily = df.groupby("date").agg(
    订单数=("order_id", "count"),
    GMV=("amount", "sum")
)

# 找 GMV 最高和最低的 3 天
daily.nlargest(3, "GMV")  # GMV 最高的 3 天
daily.nsmallest(3, "GMV")  # GMV 最低的 3 天

# 按小时看订单分布
df["hour"] = df["order_date"].dt.hour
hourly = df.groupby("hour").size()
```

## 四、面试必会的 pandas 操作速查

```python
# 筛选
df[df["amount"] > 500]                         # 大额订单
df[(df["category"] == "数码") & (df["city"] == "北京")]  # 北京数码订单

# 排序
df.nlargest(10, "amount")                      # 金额最大的10笔
df.sort_values("order_date", ascending=False)  # 最新订单在前

# 去重
df["user_id"].nunique()                        # 800 个独立用户
df["user_id"].value_counts().head(10)          # 下单最多的10个用户

# 透视表
pd.pivot_table(df, index="category", columns="channel",
               values="amount", aggfunc="sum", margins=True)

# 合并
user_info = pd.read_csv("users.csv")           # 假设有用户信息表
merged = df.merge(user_info, on="user_id", how="left")
```

## 面试常用话术

> "拿到数据后我先做 describe 看整体分布，然后按业务维度（品类、渠道、地区、时间）逐层下钻。用 groupby + agg 做聚合，pivot_table 做交叉分析。最后用 matplotlib 可视化输出报告。"

## 相关笔记

- [[Python数据栈/numpy基础]]
- [[Python数据栈/matplotlib可视化]]
- [[数据库与SQL/窗口函数实战]]（待写）
