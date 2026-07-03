---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/sql"
  - "#技术/数据分析"
  - "#状态/草稿"
created: 2026-06-26
updated: 2026-07-03
status: draft
---

# 常见业务 SQL 场景

面试中除了考语法，还爱给你一个业务场景让你当场写 SQL。这里覆盖最高频的几个场景，每个场景附带 EXPLAIN 分析和优化思路。

## 数据准备

```sql
-- 用户表
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    reg_date DATE,           -- 注册日期
    channel VARCHAR(20)       -- 来源渠道
);

-- 登录日志
CREATE TABLE user_login (
    user_id INT,
    login_time DATETIME
);

-- 订单表
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT,
    order_date DATE,
    amount DECIMAL(10,2)
);

-- 插入模拟数据略，以下直接写查询
```

## 场景 1：计算次日留存率

**面试题**："给我 6 月 25 日新注册用户的次日留存率。"

```sql
WITH new_users AS (
    SELECT user_id
    FROM users
    WHERE reg_date = '2026-06-25'
),
retained AS (
    SELECT DISTINCT u.user_id
    FROM new_users u
    INNER JOIN user_login l
        ON u.user_id = l.user_id
        AND DATE(l.login_time) = '2026-06-26'  -- 次日登录
)
SELECT
    (SELECT COUNT(*) FROM new_users) AS new_user_count,
    (SELECT COUNT(*) FROM retained) AS retained_count,
    ROUND(
        (SELECT COUNT(*) FROM retained) * 100.0 /
        (SELECT COUNT(*) FROM new_users), 2
    ) AS day1_retention_pct;
```

**面试话术**："先找出当天新用户，再 JOIN 次日的登录记录，交集就是留存用户。除以新增总数就是次日留存率。"

### EXPLAIN 分析

```sql
EXPLAIN WITH new_users AS (
    SELECT user_id FROM users WHERE reg_date = '2026-06-25'
),
retained AS (
    SELECT DISTINCT u.user_id
    FROM new_users u
    INNER JOIN user_login l
        ON u.user_id = l.user_id AND DATE(l.login_time) = '2026-06-26'
)
SELECT ...;
```

关注点：

| 步骤 | 可能的问题 | 说明 |
|------|-----------|------|
| `users` 表扫描 | `type=ALL` | `reg_date` 没有索引 → 全表扫描 |
| `user_login` JOIN | `DATE(login_time)` | 索引列上做函数运算 → 索引失效 |
| 临时表 | Using temporary | WITH 子查询可能物化为临时表 |

**优化建议**：
1. `reg_date` 建索引：`CREATE INDEX idx_reg_date ON users(reg_date);`
2. `login_time` 不用函数，改为范围查询：`login_time >= '2026-06-26' AND login_time < '2026-06-27'`
3. `user_login` 上建 `(user_id, login_time)` 联合索引

### 面试追问：数据量大的时候怎么优化？

> **问**："users 表 5000 万，user_login 表 5 亿，这个查询跑不动怎么办？"

**回答思路**：
1. **索引先行**：`users(reg_date)` + `user_login(user_id, login_time)` 联合索引，覆盖索引避免回表
2. **分区表**：`user_login` 按 `login_time` 做日分区，查询只扫描当天分区
3. **物化中间结果**：如果留存率是定时报表（非实时），提前用定时任务算出结果写入汇总表，业务查询直接读汇总表
4. **近似计算**：如果不需要精确到个位数，用 HyperLogLog 等基数估计方法

---

## 场景 2：计算用户复购率

**面试题**："6 月有多次购买行为的用户占比。"

```sql
WITH june_orders AS (
    SELECT user_id, COUNT(*) AS order_count
    FROM orders
    WHERE order_date BETWEEN '2026-06-01' AND '2026-06-30'
    GROUP BY user_id
)
SELECT
    COUNT(*) AS total_buyers,
    SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) AS repeat_buyers,
    ROUND(
        SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS repeat_rate_pct
FROM june_orders;
```

### 复购率多维度分析

面试官可能会追问："能不能按品类、按渠道、按时间分别算复购率？"

#### 按品类分析复购率

```sql
-- 每个品类的复购率：同一品类内购买 >= 2 次的用户占比
WITH category_orders AS (
    SELECT
        category,
        user_id,
        COUNT(*) AS order_count
    FROM orders
    WHERE order_date BETWEEN '2026-06-01' AND '2026-06-30'
    GROUP BY category, user_id
)
SELECT
    category,
    COUNT(*) AS total_buyers,
    SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) AS repeat_buyers,
    ROUND(
        SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS repeat_rate_pct
FROM category_orders
GROUP BY category
ORDER BY repeat_rate_pct DESC;
```

#### 按渠道分析复购率

```sql
-- 需要关联 users 表获取渠道信息
WITH channel_orders AS (
    SELECT
        u.channel,
        o.user_id,
        COUNT(*) AS order_count
    FROM orders o
    INNER JOIN users u ON o.user_id = u.user_id
    WHERE o.order_date BETWEEN '2026-06-01' AND '2026-06-30'
    GROUP BY u.channel, o.user_id
)
SELECT
    channel,
    COUNT(*) AS total_buyers,
    SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) AS repeat_buyers,
    ROUND(
        SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS repeat_rate_pct
FROM channel_orders
GROUP BY channel;
```

#### 按时间（周度）看复购率趋势

```sql
-- 每周的复购率变化趋势
WITH weekly_user_orders AS (
    SELECT
        YEARWEEK(order_date, 1) AS year_week,  -- 模式1: 周一开始
        user_id,
        COUNT(*) AS order_count
    FROM orders
    WHERE order_date BETWEEN '2026-01-01' AND '2026-06-30'
    GROUP BY YEARWEEK(order_date, 1), user_id
)
SELECT
    year_week,
    COUNT(*) AS total_buyers,
    SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) AS repeat_buyers,
    ROUND(
        SUM(CASE WHEN order_count >= 2 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2
    ) AS repeat_rate_pct
FROM weekly_user_orders
GROUP BY year_week
ORDER BY year_week;
```

### EXPLAIN 分析（复购率查询）

```sql
EXPLAIN SELECT user_id, COUNT(*) AS order_count
FROM orders
WHERE order_date BETWEEN '2026-06-01' AND '2026-06-30'
GROUP BY user_id;
```

| 关键字段 | 预期值 | 说明 |
|----------|--------|------|
| `type` | `range` | `order_date` 有索引时走范围扫描 |
| `key` | `idx_order_date` | 使用 order_date 索引 |
| `Extra` | `Using where; Using index` | 若建 `(order_date, user_id)` 覆盖索引，不用回表 |

**优化**：建 `(order_date, user_id)` 联合索引 → 覆盖索引，避免了回表查完整行。

### 面试追问：数据量大怎么优化？

> **问**："orders 表上亿行，每个月复购率要 30 秒以上，怎么办？"

**回答**：
1. **汇总表**：每日/每周定时预计算复购率存入 `stats_repurchase` 表，报表直接查汇总表
2. **只算重复购买用户**：先 GROUP BY user_id HAVING COUNT(*) >= 2，再 JOIN 回原表补全信息，减少中间结果
3. **分区裁剪**：按月分区，查询只扫描目标月份分区

---

## 场景 3：用户分层（RFM 模型简化版）

RFM = Recency（最近一次购买距今多久）、Frequency（购买几次）、Monetary（花了多少钱）。面试常让你写个简单版：

```sql
WITH user_rfm AS (
    SELECT
        user_id,
        DATEDIFF('2026-06-30', MAX(order_date)) AS recency,  -- 距今天数
        COUNT(*) AS frequency,
        SUM(amount) AS monetary
    FROM orders
    WHERE order_date BETWEEN '2026-01-01' AND '2026-06-30'
    GROUP BY user_id
)
SELECT
    user_id,
    recency,
    frequency,
    monetary,
    CASE
        WHEN recency <= 30 AND frequency >= 3 AND monetary >= 1000
            THEN '高价值用户'
        WHEN recency <= 30 AND frequency < 3
            THEN '新用户/潜力用户'
        WHEN recency > 60 AND frequency >= 3
            THEN '流失的高价值用户（需召回）'
        WHEN recency > 90
            THEN '已流失'
        ELSE '一般用户'
    END AS user_segment
FROM user_rfm
ORDER BY monetary DESC;
```

### EXPLAIN 分析

```sql
EXPLAIN SELECT user_id, DATEDIFF('2026-06-30', MAX(order_date)),
    COUNT(*), SUM(amount)
FROM orders
WHERE order_date BETWEEN '2026-01-01' AND '2026-06-30'
GROUP BY user_id;
```

| 关注点 | 说明 |
|--------|------|
| `type=range` | `order_date` 有索引 → 范围扫描，好 |
| `Extra: Using filesort` | GROUP BY user_id 需要额外排序 → 考虑建 `(user_id, order_date)` 索引 |
| 全表聚合 | 半年数据量大时仍可能慢，建议用汇总表 |

**优化方案**：
- 建 `(user_id, order_date, amount)` 覆盖索引，避免回表
- 如果 RFM 是周期性报表（非实时），提前用定时任务把每个用户的 `最近购买日期`、`累计次数`、`累计金额` 维护在 `user_rfm_summary` 汇总表里

### 面试追问：数据量大怎么优化？

> **问**："一亿用户，半年订单 10 亿行，这个 RFM 能实时算吗？"

**回答**："不能实时算，也不该实时算。RFM 是用户画像标签，T+1 更新就够了。方案是用离线任务（Spark/Hive）每天凌晨跑一次，结果写入 `user_tags` 表。业务查询时直接查标签表，毫秒级返回。"

---

## 场景 4：漏斗分析

**面试题**："计算从'浏览商品→加入购物车→下单→支付'的转化率。"

```sql
WITH funnel AS (
    SELECT
        COUNT(DISTINCT CASE WHEN event = 'view' THEN user_id END) AS view_users,
        COUNT(DISTINCT CASE WHEN event = 'cart' THEN user_id END) AS cart_users,
        COUNT(DISTINCT CASE WHEN event = 'order' THEN user_id END) AS order_users,
        COUNT(DISTINCT CASE WHEN event = 'pay' THEN user_id END) AS pay_users
    FROM user_events
    WHERE event_date = '2026-06-25'
)
SELECT
    view_users,
    cart_users,
    order_users,
    pay_users,
    ROUND(cart_users * 100.0 / view_users, 2) AS view_to_cart_pct,
    ROUND(order_users * 100.0 / cart_users, 2) AS cart_to_order_pct,
    ROUND(pay_users * 100.0 / order_users, 2) AS order_to_pay_pct,
    ROUND(pay_users * 100.0 / view_users, 2) AS overall_conversion_pct
FROM funnel;
```

输出示例：
```
view_users: 5000 → cart: 1500(30%) → order: 600(40%) → pay: 480(80%)
整体转化率: 9.6%
```

**面试话术**："漏斗分析用 CASE WHEN 做条件计数，每一层的 COUNT DISTINCT 除以上一层的值就是该步转化率。如果某一步转化率异常低，说明那一步是瓶颈。"

### 面试追问：数据量大怎么优化？

> **问**："user_events 表每天上亿条，单日漏斗分析也很慢怎么办？"

**回答**：
1. **索引**：`(event_date, event, user_id)` 联合索引，WHERE 走 `event_date`，覆盖索引避免回表
2. **物化视图**：如果是固定漏斗（每天都是这四个步骤），可以每天凌晨预计算各层 UV 写入 `funnel_daily` 表
3. **列式存储**：如果用的是 ClickHouse / Doris 等 OLAP 引擎，COUNT DISTINCT 天然比 MySQL 快几十倍——这种场景适合换引擎
4. **Bitmap 优化**：如果用户 ID 是连续整数，可以用 RoaringBitmap 做交集运算，比 COUNT DISTINCT 快很多

---

## 场景 5：连续登录天数

**面试题**："找出连续登录超过 7 天的用户。"（比较难，但面试爱问）

### 解法一：ROW_NUMBER 差值法（经典解法）

```sql
WITH daily_login AS (
    SELECT DISTINCT user_id, DATE(login_time) AS login_date
    FROM user_login
),
numbered AS (
    SELECT
        user_id,
        login_date,
        ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn
    FROM daily_login
),
grouped AS (
    SELECT
        user_id,
        DATE_SUB(login_date, INTERVAL rn DAY) AS base_date,
        -- 如果连续登录，login_date - rn 会相同
        COUNT(*) AS consecutive_days
    FROM numbered
    GROUP BY user_id, base_date
)
SELECT user_id, consecutive_days
FROM grouped
WHERE consecutive_days >= 7;
```

**核心思路**：如果 6/1, 6/2, 6/3 连续登录，配上 rn=1,2,3，`login_date - rn` 都等于 5/31，同一个基准日期 → 说明是连续段。

### 解法二：LAG 日期差法

```sql
WITH daily_login AS (
    SELECT DISTINCT user_id, DATE(login_time) AS login_date
    FROM user_login
),
with_diff AS (
    SELECT
        user_id,
        login_date,
        DATEDIFF(
            login_date,
            LAG(login_date) OVER (PARTITION BY user_id ORDER BY login_date)
        ) AS day_diff
    FROM daily_login
),
-- 标记每个连续段的起点：day_diff > 1 或 NULL（第一行）说明是新段
segment_marked AS (
    SELECT
        user_id,
        login_date,
        SUM(CASE WHEN day_diff > 1 OR day_diff IS NULL THEN 1 ELSE 0 END)
            OVER (PARTITION BY user_id ORDER BY login_date
                  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS segment_id
    FROM with_diff
)
SELECT user_id, segment_id, COUNT(*) AS consecutive_days
FROM segment_marked
GROUP BY user_id, segment_id
HAVING COUNT(*) >= 7;
```

**核心思路**：先用 LAG 算出相邻两次登录的间隔天数，间隔 > 1 天的就是新连续段的起点，再对起点做累计标记分组。

### 两种解法对比

| 维度 | 解法一（ROW_NUMBER 差值法） | 解法二（LAG 日期差法） |
|------|--------------------------|---------------------|
| **思路直观性** | 巧妙但不直观，用日期减行号的数学性质 | 直观：相邻日期差 > 1 就是断点 |
| **处理重复日期** | 必须先 DISTINCT 去重，否则同一日期多个 rn 会破坏差值性质 | 同样需要去重 |
| **处理隔天登录** | 隔 2 天登录也会被分到不同的 base_date（因为差值变了） | 天然支持：day_diff > 1 就标记新段 |
| **性能** | 一次 ROW_NUMBER + 一次 GROUP BY，较轻量 | LAG + 累计 SUM 窗口函数，多一层窗口计算 |
| **可读性** | 对面试官需要解释原理 | 更直白好懂 |
| **扩展性** | 判断"连续 N 天"很好用 | 可以灵活定义"连续"：如间隔 ≤ 2 天也算连续 |

**面试话术**："两种解法我都会。ROW_NUMBER 差值法更简洁，面试和笔试推荐用这个。LAG 法更灵活——如果需求改成'间隔不超过 2 天也算连续'，LAG 改个判断条件就行，差值法就不好处理了。"

---

## 场景 6：累计指标计算

面试常问："用一条 SQL 算出每天的累计 GMV 和累计下单用户数。"

### 累计 GMV（按天）

```sql
WITH daily_gmv AS (
    SELECT
        order_date,
        SUM(amount) AS daily_gmv
    FROM orders
    GROUP BY order_date
)
SELECT
    order_date,
    daily_gmv,
    SUM(daily_gmv) OVER (
        ORDER BY order_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_gmv
FROM daily_gmv
ORDER BY order_date;
```

### 累计用户数（首次购买用户）

```sql
-- 累计到每天为止，有多少"不同"的用户下过单
WITH first_purchase AS (
    SELECT
        user_id,
        MIN(order_date) AS first_date
    FROM orders
    GROUP BY user_id
),
daily_new_users AS (
    SELECT
        first_date AS order_date,
        COUNT(*) AS new_users
    FROM first_purchase
    GROUP BY first_date
)
SELECT
    order_date,
    new_users,
    SUM(new_users) OVER (ORDER BY order_date) AS cumulative_users
FROM daily_new_users
ORDER BY order_date;
```

**面试话术**："累计指标的核心是用 `SUM() OVER (ORDER BY date)` 窗口函数，加上 `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` 明确从最早到当前行。窗口聚合比自连接实现累计，代码更简洁，执行计划也更优——只需要一次扫描 + 一次排序。"

### 窗口函数 vs 自连接实现累计

```sql
-- 自连接方式（不推荐，但要知道）
SELECT
    a.order_date,
    a.daily_gmv,
    SUM(b.daily_gmv) AS cumulative_gmv
FROM daily_gmv a
JOIN daily_gmv b ON b.order_date <= a.order_date
GROUP BY a.order_date, a.daily_gmv
ORDER BY a.order_date;
-- 时间复杂度 O(n²)，每天都要重新扫一遍之前的所有行
```

| 方式 | 复杂度 | 适用场景 |
|------|--------|----------|
| 窗口函数 | O(n log n)（排序） | 推荐，所有场景 |
| 自连接 | O(n²) | 仅数据量极小（< 100行）时可用 |

---

## 场景 7：环比与同比计算

面试常考："算一下 GMV 的环比增长率和同比增长率。"

```sql
WITH monthly_gmv AS (
    SELECT
        DATE_FORMAT(order_date, '%Y-%m') AS ym,
        SUM(amount) AS gmv
    FROM orders
    GROUP BY DATE_FORMAT(order_date, '%Y-%m')
),
with_lag AS (
    SELECT
        ym,
        gmv,
        LAG(gmv, 1) OVER (ORDER BY ym) AS prev_month_gmv,     -- 上月
        LAG(gmv, 12) OVER (ORDER BY ym) AS prev_year_gmv      -- 去年同月
    FROM monthly_gmv
)
SELECT
    ym,
    gmv,
    prev_month_gmv,
    prev_year_gmv,
    -- 环比增长率 = (本月 - 上月) / 上月
    ROUND((gmv - prev_month_gmv) * 100.0 / prev_month_gmv, 2) AS mom_pct,
    -- 同比增长率 = (本月 - 去年同月) / 去年同月
    ROUND((gmv - prev_year_gmv) * 100.0 / prev_year_gmv, 2) AS yoy_pct
FROM with_lag
ORDER BY ym DESC;
```

**输出示例**：
```
ym      | gmv      | prev_month_gmv | prev_year_gmv | mom_pct | yoy_pct
2026-06 | 580000   | 520000         | 450000        | 11.54   | 28.89
2026-05 | 520000   | 480000         | 410000        | 8.33    | 26.83
...
```

### 面试追问：LAG(12) 可靠吗？

> **问**："如果某个月没有订单，LAG(12) 取的就不是去年同月了，怎么办？"

**回答**："确实，LAG 是按物理行偏移的，不是按时间。如果数据有缺失月份，应该先生成一个完整的月份序列（用 recursive CTE 或日期维度表），LEFT JOIN 实际数据，把缺失月份的 GMV 填 0，再做 LAG。"

```sql
-- 生成完整月份序列的写法
WITH RECURSIVE all_months AS (
    SELECT '2025-01' AS ym
    UNION ALL
    SELECT DATE_FORMAT(DATE_ADD(STR_TO_DATE(CONCAT(ym, '-01'), '%Y-%m-%d'), INTERVAL 1 MONTH), '%Y-%m')
    FROM all_months
    WHERE ym < '2026-06'
),
actual_gmv AS (
    SELECT DATE_FORMAT(order_date, '%Y-%m') AS ym, SUM(amount) AS gmv
    FROM orders GROUP BY DATE_FORMAT(order_date, '%Y-%m')
)
SELECT
    m.ym,
    COALESCE(a.gmv, 0) AS gmv  -- 缺失月份填 0
FROM all_months m
LEFT JOIN actual_gmv a ON m.ym = a.ym
ORDER BY m.ym;
```

---

## 面试高频考点小结

| 考点 | 出现频率 | 关键知识点 | 对应场景 |
|------|----------|-----------|----------|
| 留存率 | 很高 | CTE + JOIN + DISTINCT 去重 | 场景 1 |
| 复购率 | 高 | GROUP BY + CASE WHEN + 多维度拆解 | 场景 2 |
| RFM 分层 | 高 | 聚合 + CASE WHEN 分段 | 场景 3 |
| 漏斗分析 | 高 | CASE WHEN + COUNT DISTINCT 条件计数 | 场景 4 |
| 连续登录 | 很高（难题） | ROW_NUMBER 差值法 / LAG 日期差法 | 场景 5 |
| 累计指标 | 中 | SUM() OVER (ORDER BY) 窗口累计 | 场景 6 |
| 环比同比 | 高 | LAG 偏移 + 缺失月份处理 | 场景 7 |
| EXPLAIN 分析 | 很高 | type/key/rows/Extra 字段解读 | 场景 1/2/3 |
| 大数据优化 | 很高 | 索引、分区、汇总表、换引擎 | 各场景追问 |

**面试通用思路**：
1. 先写出能跑的 SQL（不用追求完美）
2. 主动说可以怎么加索引
3. 主动说 EXPLAIN 会看到什么
4. 主动说大数据量下怎么做（汇总表 / 分区 / 换 OLAP 引擎）
5. 前三步已经超过 80% 的候选人

---

## 相关笔记

- [[数据库与SQL/窗口函数实战]]
- [[数据库与SQL/SQL查询优化]]
- [[业务分析/留存分析实战]]
