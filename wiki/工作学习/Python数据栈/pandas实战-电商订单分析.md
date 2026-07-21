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

# pandas 实战：电商订单分析

> 用 5000 条真实结构电商订单数据，从读入到分析报告。面试问"pandas 熟吗"就用这篇回答。 | **面试重要度：高** | 预计阅读：20 分钟

## 视频资源

- YouTube: [Data School: pandas Q&A](https://www.youtube.com/@dataschool) — Kevin Markham，pandas 教学最系统
- B站: [黑马程序员 pandas 教程](https://www.bilibili.com/video/BV1Rx4y1G7zN/) — 中文 pandas 入门

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

## 一、数据读取：从各种来源拿到数据

### 1.1 CSV 读写

```python
# ===== 读取 CSV =====
df = pd.read_csv(
    "orders.csv",
    encoding="utf-8",            # 编码（中文数据常用 utf-8 或 gbk）
    sep=",",                     # 分隔符，默认逗号
    header=0,                    # 第几行做列名，0 表示第一行
    index_col=0,                 # 第几列做行索引，None 表示自动生成
    usecols=["order_id", "amount", "category"],  # 只读这 3 列
    dtype={"amount": float},     # 指定列的数据类型
    parse_dates=["order_date"],  # 自动解析为日期类型
    nrows=10000,                 # 只读前 10000 行（大文件预览）
    na_values=["NA", "NULL", ""],# 把这些值当成缺失值
)

# ===== 写入 CSV =====
df.to_csv(
    "output.csv",
    index=False,                 # 不写行号
    encoding="utf-8-sig",        # utf-8-sig 带 BOM，Excel 打开不乱码
)
```

**常见参数速查**：

| 参数 | 读取时含义 | 写入时含义 |
|------|-----------|-----------|
| `encoding` | 文件编码 | 输出编码（utf-8-sig 兼容 Excel）|
| `index_col` / `index` | 指定行索引列 | 是否写入行索引 |
| `usecols` | 只读指定列 | 不适用（用 `columns` 参数）|
| `nrows` | 限制读取行数 | 不适用 |
| `dtype` | 指定列类型 | 不适用 |

### 1.2 Excel 读写

```python
# ===== 读取 Excel =====
df = pd.read_excel(
    "orders.xlsx",
    sheet_name="6月订单",        # 指定 sheet，可以是名字或索引（0,1,2...）
    # sheet_name=None  →  读取所有 sheet，返回 dict {sheet名: DataFrame}
    header=0,
    usecols="A:G",               # Excel 列范围
    nrows=5000,
)

# ===== 写入 Excel =====
with pd.ExcelWriter("report.xlsx", engine="openpyxl") as writer:
    df.to_excel(writer, sheet_name="原始数据", index=False)
    df.groupby("category").sum().to_excel(writer, sheet_name="品类汇总")
    # 一个文件里写多个 sheet

# ===== 面试要点 =====
# Excel 读取比 CSV 慢 3-5 倍，大文件优先用 CSV。
# 但是给业务方看结果，Excel 是最通用的格式。
```

### 1.3 从数据库读取（SQLAlchemy + pd.read_sql）

```python
from sqlalchemy import create_engine
import pandas as pd

# 创建数据库连接
# MySQL:  mysql+pymysql://user:password@host:port/database
# PostgreSQL: postgresql://user:password@host:port/database
# SQLite: sqlite:///path/to/database.db
engine = create_engine("mysql+pymysql://root:password@localhost:3306/ecommerce")

# 读取整张表
df = pd.read_sql_table("orders", engine)

# 写 SQL 查询
query = """
    SELECT category, DATE(order_date) as date, SUM(amount) as gmv
    FROM orders
    WHERE order_date >= '2026-06-01'
    GROUP BY category, DATE(order_date)
"""
df = pd.read_sql(query, engine)

# 写入数据库
df.to_sql("order_summary", engine, if_exists="replace", index=False)
# if_exists: "fail"=报错, "replace"=删表重建, "append"=追加
```

## 二、数据概览

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

## 三、数据清洗完整流程

真实数据从来不是干干净净的。下面模拟一份"脏数据"，然后走完整清洗流程。

### 3.1 模拟脏数据

```python
# 在原始数据基础上加一些"脏东西"
df_dirty = df.copy()

# 1. 随机插入缺失值
np.random.seed(1)
for col in ["channel", "category", "amount"]:
    mask = np.random.random(n) < 0.03
    df_dirty.loc[mask, col] = np.nan

# 2. 插入重复行
dups = df_dirty.sample(15, random_state=2)
df_dirty = pd.concat([df_dirty, dups], ignore_index=True)

# 3. 插入异常值（超高金额）
df_dirty.loc[df_dirty.sample(5, random_state=3).index, "amount"] = 99999

# 4. 插入日期格式异常
df_dirty.loc[0, "order_date"] = "2026/06/01"  # 用 / 而不是 -

print(f"脏数据: {df_dirty.shape[0]} 行 {df_dirty.shape[1]} 列")
```

### 3.2 缺失值处理

```python
# ===== 第一步：查看缺失情况 =====
missing = df_dirty.isnull().sum()
missing_pct = (missing / len(df_dirty) * 100).round(2)
missing_df = pd.DataFrame({"缺失数": missing, "缺失比例%": missing_pct})
print(missing_df[missing_df["缺失数"] > 0])

# ===== 第二步：选择填充策略 =====

# 策略 A: 类别列 → 用"未知"填充
df_dirty["channel"].fillna("未知", inplace=True)
df_dirty["category"].fillna("未知", inplace=True)
# 场景: 缺失比例小（< 5%），不想丢数据

# 策略 B: 数值列 → 用中位数填充（对异常值更鲁棒）
median_amount = df_dirty["amount"].median()
df_dirty["amount"].fillna(median_amount, inplace=True)
# 场景: 数据有偏，中位数比均值更稳定

# 策略 C: 缺失严重 → 直接删除
# 比如某列缺失 > 50%，直接 drop 掉这一列
# df_dirty.drop(columns=["某列"], inplace=True)

# 策略 D: 删除含缺失的行
# df_dirty.dropna(subset=["channel", "amount"], inplace=True)
# 场景: 关键列不能缺，且缺失行很少
```

**缺失值处理决策表**：

| 缺失比例 | 数值列 | 类别列 | 关键列（如主键） |
|----------|--------|--------|-----------------|
| < 5% | 均值/中位数填充 | 众数填充 | 删行 |
| 5% - 20% | 分组均值填充 | "未知"填充 | 删行 |
| 20% - 50% | 建模预测填充 | "未知"填充 | 评估后决定 |
| > 50% | 考虑删列 | 考虑删列 | 数据质量有问题 |

```python
# ===== 第三步：重复值检测与删除 =====
print(f"重复行: {df_dirty.duplicated().sum()} 行")
# 按 order_id 查重（订单号不应该重复）
print(f"order_id 重复: {df_dirty['order_id'].duplicated().sum()} 条")

# 删除完全重复的行
df_dirty.drop_duplicates(inplace=True)
# 只按 order_id 去重（保留第一次出现的）
# df_dirty.drop_duplicates(subset=["order_id"], keep="first", inplace=True)

print(f"去重后: {df_dirty.shape[0]} 行")
```

### 3.3 异常值处理

```python
# ===== IQR 方法检测 =====
q1 = df_dirty["amount"].quantile(0.25)
q3 = df_dirty["amount"].quantile(0.75)
iqr = q3 - q1
lower = q1 - 1.5 * iqr
upper = q3 + 1.5 * iqr

outliers = df_dirty[(df_dirty["amount"] < lower) | (df_dirty["amount"] > upper)]
print(f"异常订单: {len(outliers)} 笔")
print(f"异常金额范围: < {lower:.0f} 或 > {upper:.0f}")

# ===== 异常值处理策略 =====
# 策略 A: 截尾（Winsorize）— 把异常值拉到边界上
df_clean = df_dirty.copy()
df_clean["amount"] = df_clean["amount"].clip(lower, upper)
print(f"截尾后最大值: {df_clean['amount'].max():.0f}")

# 策略 B: 直接删除 — 适用于异常确实是错误数据的场景
# df_clean = df_dirty[(df_dirty["amount"] >= lower) & (df_dirty["amount"] <= upper)]

# 策略 C: 标记后保留 — 如果是双十一订单，高金额其实是合理的
# df_dirty["is_outlier"] = (df_dirty["amount"] < lower) | (df_dirty["amount"] > upper)
```

### 3.4 数据类型修正

```python
# 修正日期列
df_clean["order_date"] = pd.to_datetime(
    df_clean["order_date"],
    format="mixed",       # pandas 2.0+ 支持混合格式自动推断
    errors="coerce",      # 解析失败的变成 NaT
    dayfirst=False,       # 日在前还是月在前的格式
)
# to_datetime 常用参数:
#   format="%Y-%m-%d"     明确指定格式，速度最快
#   errors="raise"        解析失败报错（默认）
#   errors="coerce"       解析失败变 NaT
#   errors="ignore"       解析失败保持原样

# 修正类别列为 category 类型（节省内存）
df_clean["channel"] = df_clean["channel"].astype("category")
df_clean["category"] = df_clean["category"].astype("category")
df_clean["city"] = df_clean["city"].astype("category")

# 查看内存占用
print(df_clean.memory_usage(deep=True))
# category 类型比 object 类型省 5-10 倍内存
```

## 四、按维度分析

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

## 五、时间维度

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

## 六、RFM 用户分层（完整实现）

RFM 是电商数据分析面试必问模型。R = 最近一次消费（Recency），F = 消费频率（Frequency），M = 消费金额（Monetary）。

```python
import datetime

# 设定参考日期（分析当天）
ref_date = df["order_date"].max() + pd.Timedelta(days=1)

rfm = df.groupby("user_id").agg(
    R=("order_date", lambda x: (ref_date - x.max()).days),   # 距今天数
    F=("order_id", "count"),                                  # 下单次数
    M=("amount", "sum")                                       # 总消费金额
).reset_index()

print(f"RFM 表: {rfm.shape[0]} 个用户")
print(rfm.describe())
#        R       F       M
# mean  12.5    6.2    1240
# 解读: 平均 12.5 天前最后一次下单，人均 6.2 单，人均消费 1240 元

# ===== 打分（用分位数做 1-4 分） =====
rfm["R_score"] = pd.qcut(rfm["R"], q=4, labels=[4, 3, 2, 1])  # R 越小越好 → 小值高分
rfm["F_score"] = pd.qcut(rfm["F"], q=4, labels=[1, 2, 3, 4])  # F 越大越好
rfm["M_score"] = pd.qcut(rfm["M"], q=4, labels=[1, 2, 3, 4])  # M 越大越好

# 综合分
rfm["RFM_score"] = (
    rfm["R_score"].astype(int) +
    rfm["F_score"].astype(int) +
    rfm["M_score"].astype(int)
)

# ===== 用户分群 =====
def rfm_segment(score):
    if score >= 10:
        return "高价值用户"
    elif score >= 7:
        return "潜力用户"
    elif score >= 5:
        return "一般用户"
    else:
        return "流失用户"

rfm["segment"] = rfm["RFM_score"].apply(rfm_segment)
print(rfm["segment"].value_counts())
# 高价值用户   ~200
# 潜力用户     ~200
# 一般用户     ~200
# 流失用户     ~200

# ===== 各分群消费特征 =====
segment_profile = rfm.groupby("segment").agg(
    用户数=("user_id", "count"),
    平均R=("R", "mean"),
    平均F=("F", "mean"),
    平均M=("M", "mean"),
    总GMV=("M", "sum")
).round(1)
print(segment_profile)
```

**面试话术**："RFM 是做用户分层的经典模型。R、F、M 分别打 1-4 分（用四分位数），加总后 3-5 分=流失用户，6-8 分=一般/潜力用户，9-12 分=高价值用户。分层后针对不同群体做差异化运营。"

## 七、复购率多维度分析

```python
# ===== 整体复购率 =====
user_order_count = df.groupby("user_id").size()
repurchase_users = (user_order_count > 1).sum()
total_users = len(user_order_count)
print(f"整体复购率: {repurchase_users}/{total_users} = {repurchase_users/total_users*100:.1f}%")

# ===== 按品类看复购率 =====
# 每个用户在每个品类下的订单数
user_cat = df.groupby(["user_id", "category"]).size().reset_index(name="count")
# 复购用户定义：在该品类下单 > 1 次的用户
repurchase_by_cat = user_cat[user_cat["count"] > 1].groupby("category")["user_id"].nunique()
total_by_cat = user_cat.groupby("category")["user_id"].nunique()
cat_repurchase_rate = (repurchase_by_cat / total_by_cat * 100).round(1)
print("品类复购率:")
print(cat_repurchase_rate.sort_values(ascending=False))
# 食品复购率最高（日常消耗品），数码最低（耐用品）

# ===== 按渠道看复购率 =====
user_chan = df.groupby(["user_id", "channel"]).size().reset_index(name="count")
repurchase_by_chan = user_chan[user_chan["count"] > 1].groupby("channel")["user_id"].nunique()
total_by_chan = user_chan.groupby("channel")["user_id"].nunique()
chan_repurchase_rate = (repurchase_by_chan / total_by_chan * 100).round(1)
print("\n渠道复购率:")
print(chan_repurchase_rate.sort_values(ascending=False))

# ===== 按周看复购趋势 =====
df["week"] = df["order_date"].dt.isocalendar().week
weekly_users = df.groupby("week")["user_id"].nunique()
weekly_orders = df.groupby("week")["order_id"].count()
weekly_avg = (weekly_orders / weekly_users).round(2)
print("\n每周人均下单次数（反映复购活跃度）:")
print(weekly_avg)
```

**面试话术**："复购率 = 下单 > 1 次的用户数 / 总用户数。分析时要拆维度——食品复购高是正常的（消耗品），数码复购低不代表差（耐用品）。关键是同类目环比趋势。"

## 八、用户生命周期分析

```python
# ===== 首单到末单的天数分布 =====
user_lifecycle = df.groupby("user_id").agg(
    首单日期=("order_date", "min"),
    末单日期=("order_date", "max"),
    订单数=("order_id", "count"),
    总消费=("amount", "sum")
).reset_index()

user_lifecycle["生命周期(天)"] = (
    (user_lifecycle["末单日期"] - user_lifecycle["首单日期"]).dt.days
)

# 只看下单 2 次以上的用户（才有"生命周期"可言）
multi_order = user_lifecycle[user_lifecycle["订单数"] > 1]
print("多单用户生命周期分布:")
print(multi_order["生命周期(天)"].describe())
# 25% 分位: 8 天,  50%: 16 天,  75%: 23 天
# 说明一半的复购用户在 16 天内再次下单

# ===== 生命周期分段 =====
bins = [0, 7, 14, 21, 30]
labels = ["0-7天(高频)", "8-14天(中频)", "15-21天(低频)", "22天+"]
multi_order["活跃度"] = pd.cut(multi_order["生命周期(天)"], bins=bins, labels=labels)
print(multi_order["活跃度"].value_counts().sort_index())
```

## 九、merge / concat / join 三种合并方式对比

### 9.1 对比表格

| | merge | concat | join |
|------|-------|--------|------|
| 合并方向 | 按列（基于键值） | 按行堆叠或按列拼接 | 基于索引的按列合并 |
| 类比 SQL | JOIN | UNION / 横向拼接 | JOIN ON index |
| 关键参数 | `on`, `how`, `left_on`, `right_on` | `axis`, `join`, `ignore_index` | `on`, `how`, `lsuffix`, `rsuffix` |
| 多表合并 | 两张表 | 多张表（列表） | 两张表 |
| 使用场景 | 两张表有共同字段时横向关联 | 多张结构相同的表纵向堆叠 | 两张表用索引对齐 |
| 去重处理 | 笛卡尔积（一个键对应多个值时会膨胀） | 不处理 | 不处理 |

### 9.2 merge 示例（最常用）

```python
# 模拟用户信息表
user_info = pd.DataFrame({
    "user_id": [f"U{i:04d}" for i in range(1, 801)],
    "注册日期": pd.date_range("2025-01-01", periods=800, freq="D"),
    "会员等级": np.random.choice(["普通","银卡","金卡","钻石"], 800, p=[0.5,0.3,0.15,0.05]),
})

# 内连接：只保留两边都有的用户
merged_inner = df.merge(user_info, on="user_id", how="inner")

# 左连接：保留所有订单，用户信息缺的填空
merged_left = df.merge(user_info, on="user_id", how="left")

# 连接键不同名时
# df.merge(user_info, left_on="user_id", right_on="uid", how="left")

print(f"内连接: {merged_inner.shape}, 左连接: {merged_left.shape}")
```

### 9.3 concat 示例

```python
# 按行堆叠：多个 Excel 文件合并
# df_all = pd.concat([df1, df2, df3], axis=0, ignore_index=True)

# 按列拼接：特征拼接
df_num = df[["amount"]]
df_cat = df[["channel", "category"]]
# df_combined = pd.concat([df_num, df_cat], axis=1)

# concat 的 join 参数（不是 merge 的 join）
# join="outer" → 列名的并集（缺的填 NaN）
# join="inner" → 列名的交集（只保留共有的列）
```

### 9.4 join 示例

```python
# join 是基于索引的合并
df_by_user = df.groupby("user_id")["amount"].sum()
df_by_user.name = "总消费"
user_info_indexed = user_info.set_index("user_id")
joined = df_by_user.to_frame().join(user_info_indexed, how="left")
# 用 merge 等价写法: df_by_user.to_frame().merge(user_info, left_index=True, right_on="user_id")
```

## 十、groupby 进阶：transform / filter / apply

这三个方法经常在面试中被问到区别。

```python
# ==== transform: 保持原形状，用于做"组内计算后广播回原表" ====
# 场景：算每个品类平均价，然后看每笔订单高于还是低于品类均价
df["cat_avg"] = df.groupby("category")["amount"].transform("mean")
df["高于均价"] = df["amount"] > df["cat_avg"]
print("transform 结果: 保持了 (5000,) 形状，每行对应自己的品类均值")
# transform 返回值长度和原 DataFrame 一样

# ==== filter: 按组过滤，保留或丢弃整个组 ====
# 场景：只看订单数 >= 100 的品类
df_filtered = df.groupby("category").filter(lambda g: len(g) >= 1000)
print(f"filter 后: {df_filtered.shape[0]} 行，只剩大品类")
# filter 返回的是原始行的子集

# ==== apply: 最灵活的自定义聚合 ====
# 场景：给每个品类做"第一名和第二名金额差值"
def top2_diff(group):
    """返回组内金额第一和第二的差值"""
    top2 = group["amount"].nlargest(2)
    if len(top2) >= 2:
        return top2.iloc[0] - top2.iloc[1]
    return 0

diff_by_cat = df.groupby("category").apply(top2_diff)
print("apply 示例 — 各品类 Top1 vs Top2 金额差:")
print(diff_by_cat)
```

**三者的区别一句话总结**：

| 方法 | 输入 | 输出 | 典型场景 |
|------|------|------|----------|
| `transform` | 每组 → 函数 | 与输入等长 | 组均值填充、标准化 |
| `filter` | 每组 → True/False | 原数据的子集 | 保留符合条件的组 |
| `apply` | 每组 → 任意值 | 任意形状 | 自定义复杂聚合逻辑 |

## 十一、面试必会的 pandas 操作速查

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

## 十二、面试话术："拿到一份新数据你首先做什么？"

**完整回答模板**（照着念就行）：

> 我的检查流程分五步：
>
> **第一步：看概览。** `df.info()` 看列名、数据类型、行数。`df.head()` 看前几行长什么样。`df.describe()` 看数值列的均值、分位数、极值。这一步我就能判断数据规模、有没有明显的格式问题。
>
> **第二步：查缺失和重复。** `df.isnull().sum() / len(df)` 算缺失比例。缺失多的列要想办法补或删，缺失少的直接填充。`df.duplicated().sum()` 查重复行，按主键去重。
>
> **第三步：处理数据类型。** 日期列转 datetime（`pd.to_datetime`），类别列转 category 省内存，金额列确认是数值不是字符串。
>
> **第四步：异常值检测。** 用 IQR 方法或直接看 describe 的 min/max。金额为负的、日期超范围的、数量不合逻辑的，根据业务判断是修正还是剔除。
>
> **第五步：建派生字段。** 从日期提取年/月/周/星期几，从金额做分箱，从用户 ID 做行为统计。这些派生字段是后续分析的基础。
>
> 这五步做完，数据就可以用于分析了。

**追问："如果数据量很大怎么办？"**
>
> "先 `nrows=10000` 读前 1 万行做探索性分析。确认清洗逻辑后，用 `chunksize` 分块读取处理，或直接用 SQL 在数据库层面做聚合再导入 pandas。"

## 面试高频考点小结

| 考点 | 考察频率 | 关键点 |
|------|----------|--------|
| 数据读取 (read_csv/excel/sql) | ★★★★★ | encoding、parse_dates、dtype、nrows |
| 缺失值处理 (dropna/fillna) | ★★★★★ | 方法参数、策略选择（删除 vs 填充） |
| groupby 聚合 | ★★★★★ | agg 多函数、transform/filter/apply 区别 |
| merge 合并方式 | ★★★★☆ | how 参数（inner/left/right/outer）、on 参数 |
| RFM 用户分层 | ★★★★☆ | R/F/M 含义、打分方法、分群策略 |
| 数据清洗流程 | ★★★★☆ | 缺失→重复→异常值→类型→派生字段 |
| pivot_table 透视表 | ★★★☆☆ | index/columns/values/aggfunc/margins |
| 日期处理 (to_datetime/dt) | ★★★☆☆ | format/errors/dt.year/dt.weekday |
| 重复值处理 | ★★★☆☆ | duplicated/drop_duplicates/subset/keep |
| concat vs merge vs join | ★★★☆☆ | 按行/按列/按索引三种合并的区别 |
| 异常值处理 (IQR) | ★★☆☆☆ | IQR 公式 + clip 截尾法 |
| 复购率分析 | ★★☆☆☆ | 定义（>1 单/总用户）、多维度拆解 |

## 相关笔记

- [[工作学习/Python数据栈/numpy基础]]
- [[工作学习/Python数据栈/matplotlib可视化]]
- [[工作学习/数据库与SQL/窗口函数实战]]（待写）
