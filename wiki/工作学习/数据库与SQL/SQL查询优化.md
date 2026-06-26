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

# SQL 查询优化

面试不会让你调优生产数据库，但会问：**"这个查询为什么慢？怎么优化？"**

## 一、先看执行计划

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 101;
```

MySQL 输出关键字段：

| 字段 | 含义 | 关注点 |
|------|------|--------|
| type | 访问类型 | **ALL = 全表扫描（最差）**，ref/eq_ref = 走索引（好） |
| key | 使用的索引 | NULL 表示没走索引 |
| rows | 预估扫描行数 | 越大越慢 |
| Extra | 额外信息 | **Using filesort = 需要额外排序（差）**，Using index = 覆盖索引（好）|

**面试话术**："先用 EXPLAIN 看执行计划，确认有没有走索引。type=ALL 全表扫描是最常见的慢查询原因。"

## 二、索引策略

### 最左前缀原则（面试最爱问）

```sql
-- 建联合索引
CREATE INDEX idx_user_date ON orders(user_id, order_date);

-- 走索引（匹配最左列）
SELECT * FROM orders WHERE user_id = 101;                  -- ✅
SELECT * FROM orders WHERE user_id = 101 AND order_date > '2026-06-01'; -- ✅

-- 不走索引（跳过了最左列）
SELECT * FROM orders WHERE order_date > '2026-06-01';      -- ❌

-- 范围查询后索引失效
SELECT * FROM orders
WHERE user_id = 101 AND order_date > '2026-06-01' AND amount > 100;
-- user_id ✅ → order_date ✅(范围) → amount ❌(范围列之后的列不走索引)
```

**面试话术**："联合索引遵循最左前缀原则。查询条件必须从索引的最左列开始匹配，不能跳过。范围查询（> < BETWEEN LIKE）后面的列不走索引。"

### 覆盖索引

```sql
-- 假设索引 idx_user_date_amount ON orders(user_id, order_date, amount)

-- 覆盖索引：所有需要的列都在索引里，不需要回表
SELECT user_id, order_date, amount
FROM orders
WHERE user_id = 101;
-- Extra: Using index ← 好！

-- 需要回表
SELECT * FROM orders WHERE user_id = 101;
-- Extra: NULL ← 需要回表查完整行
```

### 什么情况索引失效

```sql
-- 1. 索引列上做函数或运算
WHERE YEAR(order_date) = 2026        -- ❌ 函数破坏了索引
WHERE order_date >= '2026-01-01'     -- ✅ 直接比较走索引

-- 2. 前导模糊查询
WHERE user_name LIKE '%张三'          -- ❌ % 在前不走索引
WHERE user_name LIKE '张三%'          -- ✅ % 在后走索引

-- 3. 隐式类型转换
WHERE user_id = '101'                -- ❌ 字符串和 INT 列比较，MySQL 会做类型转换
WHERE user_id = 101                  -- ✅

-- 4. OR 条件（不是全部列都有索引）
WHERE user_id = 101 OR amount > 500  -- ❌ amount 没索引，可能全表扫描
-- 改写成 UNION
SELECT * FROM orders WHERE user_id = 101
UNION
SELECT * FROM orders WHERE amount > 500;
```

## 三、常见慢查询场景与解法

### 场景 1：大表分页越翻越慢

```sql
-- 慢：OFFSET 100000 → MySQL 要扫描并丢弃前 100000 行
SELECT * FROM orders ORDER BY order_id LIMIT 100000, 20;

-- 快：基于索引的游标分页
SELECT * FROM orders
WHERE order_id > 100000   -- 上次最后一条的 ID
ORDER BY order_id
LIMIT 20;
```

### 场景 2：大表 JOIN

```sql
-- 慢：驱动表太大
SELECT o.*, u.name
FROM orders o
JOIN users u ON o.user_id = u.id
WHERE o.amount > 100;

-- 优化思路：
-- 1. 先缩小驱动表：WHERE 条件先过滤
-- 2. 确保 JOIN 列有索引（users.id 主键自带，orders.user_id 需建索引）
-- 3. 小表驱动大表
```

### 场景 3：COUNT 性能

```sql
-- MyISAM: COUNT(*) 有优化，很快
-- InnoDB: COUNT(*) 需要扫描，大表很慢

-- 如果需要频繁 COUNT，考虑：
-- 1. 用汇总表定期更新
-- 2. 用 EXPLAIN 估算（近似值）
EXPLAIN SELECT COUNT(*) FROM orders;
-- 3. 如果可以接受近似值，查 information_schema
SELECT TABLE_ROWS FROM information_schema.TABLES
WHERE TABLE_NAME = 'orders';
```

## 四、优化清单（面试速答）

| 优先级 | 方法 | 效果 |
|--------|------|------|
| 1 | **加索引**（WHERE/JOIN/ORDER BY 列） | 最大提升（全表扫描→索引查找） |
| 2 | **减少返回列**（不要 SELECT *） | 减少 IO |
| 3 | **覆盖索引** | 避免回表 |
| 4 | **LIMIT** 限制返回行数 | 减少网络传输 |
| 5 | **优化 JOIN 顺序**（小表驱动大表） | 减少中间结果集 |
| 6 | **避免子查询**，改用 JOIN | 子查询可能物化临时表 |
| 7 | **分区表**（按时间分区） | 减少扫描范围 |

## 相关笔记

- [[数据库与SQL/窗口函数实战]]
- [[数据库与SQL/常见业务SQL场景]]
