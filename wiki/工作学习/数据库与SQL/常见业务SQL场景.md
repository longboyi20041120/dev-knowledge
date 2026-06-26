---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/sql"
  - "#技术/数据分析"
  - "#状态/草稿"
created: 2026-06-26
updated: 2026-06-26
status: draft
---

# 常见业务 SQL 场景

面试中除了考语法，还爱给你一个业务场景让你当场写 SQL。这里覆盖最高频的三个。

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

## 场景 5：连续登录天数

**面试题**："找出连续登录超过 7 天的用户。"（比较难，但面试爱问）

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

## 相关笔记

- [[数据库与SQL/窗口函数实战]]
- [[数据库与SQL/SQL查询优化]]
- [[业务分析/留存分析实战]]
