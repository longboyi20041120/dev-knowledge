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

# SQL 查询优化

面试不会让你调优生产数据库，但会问：**"这个查询为什么慢？怎么优化？"**

---

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

### type 字段从好到差完整排序

```
system > const > eq_ref > ref > range > index > ALL
 最好                                最差（全表扫描）
```

| type | 含义 | 例子 |
|------|------|------|
| `const` | 主键或唯一索引的等值查询，最多返回一行 | `WHERE id = 1` |
| `eq_ref` | JOIN 时用主键或唯一索引关联 | `JOIN users ON orders.user_id = users.id` |
| `ref` | 非唯一索引的等值查询 | `WHERE user_id = 101` |
| `range` | 索引范围扫描 | `WHERE order_date BETWEEN ...` |
| `index` | 全索引扫描（比 ALL 快，但仍慢） | 覆盖索引查询没有 WHERE 时 |
| `ALL` | **全表扫描，最差** | 没有索引的查询 |

---

## 二、B+ 树索引结构

面试经常会问"为什么 MySQL 用 B+ 树而不是二叉树"，这里用图解说明。

### B+ 树结构示意

```
                     [30 | 60]                    ← 非叶子节点（只存 key，不存数据）
                    /    |    \
           [10|20]    [40|50]   [70|80|90]        ← 非叶子节点
           /  |  \     /  |  \    /  |  |  \
         [1] [10] [20] [30] [40] ... [70][80][90] ← 叶子节点（存完整数据 + 链表）
          |    |    |    |    |         |   |   |
        数据  数据  数据  数据 数据     数据 数据 数据
         
        叶子节点之间用双向链表连接 →
        范围查询直接沿着链表往后扫，不需要回到上层
```

### 为什么 B+ 树适合磁盘存储？

| 对比维度 | 二叉树 | B+ 树 |
|----------|--------|-------|
| **树的高度** | 100 万数据 → 约 20 层 | 100 万数据 → 约 3 层 |
| **磁盘 IO 次数** | 每次查找 ≈ 20 次 IO | 每次查找 ≈ 3 次 IO |
| **节点大小** | 一个节点存一个 key + 两个指针 | 一个节点存几百个 key（对齐磁盘页 16KB） |
| **范围查询** | 需要中序遍历（多次 IO） | 叶子节点有链表，顺着扫即可 |

**核心原理**：磁盘 IO 是数据库的性能瓶颈，不是 CPU。B+ 树的每个节点大小设计为恰好填满一个磁盘页（16KB），一次 IO 就能加载几百个 key。树的高度极低（3 层就能存百万级数据），意味着任意查找最多 3 次 IO。

**面试话术**："B+ 树比二叉树适合数据库，核心原因是磁盘 IO 远慢于内存计算。B+ 树一个节点能存几百个 key，树的高度通常只有 3-4 层，每次查找只需 3-4 次磁盘 IO。而二叉树高度 20+，就是 20+ 次 IO。另外 B+ 树叶子节点有双向链表，范围查询非常快，不用回到上层遍历。"

---

## 三、索引策略

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

### 覆盖索引详解（带 EXPLAIN 对比）

覆盖索引是指**查询需要的所有列都在索引里**，不需要回表查数据行。

```sql
-- 建一个覆盖索引
CREATE INDEX idx_user_date_amount ON orders(user_id, order_date, amount);
```

**不覆盖的情况（需要回表）**：

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 101;
-- +----+------+-------+------+---------+
-- | id | type | key   | rows | Extra   |
-- +----+------+-------+------+---------+
-- |  1 | ref  | idx_u | 5    | NULL    |  ← Extra=NULL，需要回表查 *
-- +----+------+-------+------+---------+
```

**覆盖索引的情况（不用回表）**：

```sql
EXPLAIN SELECT user_id, order_date, amount
FROM orders WHERE user_id = 101;
-- +----+------+------------------+------+---------------+
-- | id | type | key              | rows | Extra         |
-- +----+------+------------------+------+---------------+
-- |  1 | ref  | idx_user_date_a  | 5    | Using index   | ← 覆盖索引！
-- +----+------+------------------+------+---------------+
```

**原理**：
```
非覆盖索引查询流程：
  索引 → 找到主键 ID → 回表查完整行 → 返回
  （两次查找：一次在索引树，一次在主键树）

覆盖索引查询流程：
  索引 → 所有数据都在索引里 → 直接返回
  （一次查找，不用回表）
```

**面试话术**："覆盖索引避免了回表，减少一次磁盘 IO。在 OLAP 查询中建议 SELECT 具体列而不是 SELECT *，这样配合覆盖索引性能提升明显。Extra 显示 Using index 就是覆盖索引。"

### 索引下推（ICP, Index Condition Pushdown）

MySQL 5.6+ 的特性。在索引扫描时，**把 WHERE 条件中可以由索引判断的部分下推到存储引擎层过滤**，减少回表次数。

```sql
-- 假设索引为 idx_name_age ON users(name, age)
SELECT * FROM users
WHERE name LIKE '张%' AND age = 25;
```

**没有 ICP**（MySQL 5.6 之前）：
```
1. 存储引擎通过索引找出所有 name LIKE '张%' 的行
2. 全部返回给 Server 层
3. Server 层再过滤 age = 25
→ 如果匹配 1000 行但只有 10 行 age=25，就做了 990 次多余回表
```

**有 ICP**（MySQL 5.6+）：
```
1. 存储引擎在索引扫描时直接判断 age = 25
2. 只有同时满足 name 和 age 条件的行才回表
→ 只回表 10 次，减少 99% 的回表
```

EXPLAIN 中 Extra 显示 `Using index condition` 就表示用了 ICP。

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

### 索引设计原则总结

| 原则 | 说明 | 反例 |
|------|------|------|
| **选择度高** | 列的不同值越多，索引效果越好。性别只有 3-4 个值 → 不适合单独建索引 | 性别列单独建索引无效 |
| **联合索引列顺序** | 等值查询的列放前面，范围查询的列放后面 | `(order_date, user_id)` 比 `(user_id, order_date)` 差 |
| **最左前缀匹配** | 联合索引的列顺序要和查询顺序一致 | 跳过了最左列 |
| **不要过多索引** | 索引不是免费的：写入变慢、占磁盘空间 | 一个表 20 个索引 |
| **冗余索引要删除** | `(a,b)` 已经覆盖了 `(a)` 的功能 | 同时存在 `(a)` 和 `(a,b)` 两个索引 |
| **用覆盖索引** | 把 SELECT 的列也加进联合索引 | `SELECT a,b,c` 但只有 `(a,b)` |
| **长字符串用前缀索引** | `INDEX (content(20))` 只索引前 20 个字符 | 对 TEXT 列建全文索引 |

---

## 四、常见慢查询场景与解法

### 场景 1：大表分页越翻越慢

```sql
-- 慢：OFFSET 100000 → MySQL 要扫描并丢弃前 100000 行
SELECT * FROM orders ORDER BY order_id LIMIT 100000, 20;
```

**问题原理**：`LIMIT 100000, 20` 不是直接跳到第 100000 行——MySQL 必须扫描前 100000 行，逐行丢弃，然后取 20 行。越往后翻页扫描丢弃的行越多，所以越来越慢。

#### 方案一：延迟关联（Deferred Join）

```sql
-- 先在索引中找出要返回的 ID，再回表取完整数据
SELECT o.*
FROM orders o
INNER JOIN (
    SELECT order_id
    FROM orders
    ORDER BY order_id
    LIMIT 100000, 20
) t ON o.order_id = t.order_id;
-- 子查询只扫描索引（覆盖索引），快很多
-- 外层 JOIN 只回表 20 次
```

#### 方案二：游标分页（推荐）

```sql
-- 记录上一页最后一条的 order_id，下次从它之后开始
SELECT * FROM orders
WHERE order_id > 100000   -- 上次最后一条的 ID
ORDER BY order_id
LIMIT 20;
-- 直接走主键索引定位，O(1) 跳到指定位置
```

#### 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| `LIMIT OFFSET` | 写法简单 | 越翻越慢，大 OFFSET 不可用 |
| **延迟关联** | 不改接口，兼容现有分页 | 多一层子查询，中等数据量够用 |
| **游标分页** | 性能恒定，大数据量首选 | 不能跳页，必须顺序翻；需要前端配合传游标 |

**面试话术**："小数据量用 LIMIT OFFSET 没问题。超过几十万行建议用游标分页，让前端把上一页最后一条的 ID 传回来，WHERE id > last_id 直接走主键索引。如果不能改接口，用延迟关联方案也可以缓解。"

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

---

## 五、慢查询日志配置与分析

### 开启慢查询日志

```sql
-- 查看当前配置
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';

-- 开启慢查询日志
SET GLOBAL slow_query_log = ON;
SET GLOBAL long_query_time = 1;         -- 超过 1 秒的查询记录
SET GLOBAL log_queries_not_using_indexes = ON;  -- 记录没走索引的查询
SET GLOBAL slow_query_log_file = '/var/log/mysql/slow.log';
```

| 参数 | 含义 | 建议值 |
|------|------|--------|
| `slow_query_log` | 是否开启 | ON |
| `long_query_time` | 慢查询阈值（秒） | 0.5 ~ 1 |
| `log_queries_not_using_indexes` | 记录未使用索引的查询 | ON（会发现很多优化点） |
| `log_slow_admin_statements` | 记录 DDL 慢语句 | ON |

### mysqldumpslow 工具使用

```bash
# MySQL 自带的慢日志分析工具
# 查询最慢的 10 条 SQL
mysqldumpslow -s t -t 10 /var/log/mysql/slow.log

# 查询返回行数最多的 10 条 SQL
mysqldumpslow -s r -t 10 /var/log/mysql/slow.log

# 查询出现次数最多的 10 条 SQL（最值得优化的！）
mysqldumpslow -s c -t 10 /var/log/mysql/slow.log

# 按查询时间排序，倒序
mysqldumpslow -s at -t 10 /var/log/mysql/slow.log
```

| 参数 | 含义 |
|------|------|
| `-s t` | 按总查询时间排序 |
| `-s at` | 按平均查询时间排序 |
| `-s c` | 按出现次数排序 |
| `-s r` | 按返回行数排序 |
| `-t 10` | 只显示 top 10 |

### pt-query-digest 简介

Percona Toolkit 中的明星工具，比 mysqldumpslow 分析更详细：

```bash
# 分析慢查询日志，生成报告
pt-query-digest /var/log/mysql/slow.log > slow_report.log

# 分析指定时间范围的慢查询
pt-query-digest --since '2026-06-01' --until '2026-06-30' slow.log
```

报告包含：查询的响应时间分布、最耗时的 SQL 排名、每类 SQL 的执行次数/锁等待时间/行扫描数等。

---

## 六、实际优化案例（3 条慢 SQL 完整优化过程）

### 案例 1：全表扫描 → 索引优化

**原始 SQL**（线上发现平均执行 3.2 秒）：

```sql
SELECT * FROM orders
WHERE YEAR(order_date) = 2026 AND user_id = 101;
```

**EXPLAIN 分析**：

```
+----+------+-------+------+---------+-------------+
| id | type | key   | rows | Extra   |             |
+----+------+-------+------+---------+-------------+
|  1 | ALL  | NULL  | 50万 | Using where |          |
+----+------+-------+------+---------+-------------+
-- type=ALL 全表扫描，key=NULL 没走索引
-- 原因：YEAR() 函数破坏了 order_date 索引
```

**问题分析**：索引列上使用 `YEAR()` 函数导致索引失效，扫描全表 50 万行。

**优化后 SQL**：

```sql
SELECT * FROM orders
WHERE order_date >= '2026-01-01'
  AND order_date < '2027-01-01'
  AND user_id = 101;
```

**优化后 EXPLAIN**：

```
+----+------+-----------------+------+-------------+
| id | type | key             | rows | Extra       |
+----+------+-----------------+------+-------------+
|  1 | ref  | idx_user_date   | 12   | Using where |
+----+------+-----------------+------+-------------+
-- type=ref，走了联合索引 (user_id, order_date)，rows 从 50万 → 12
-- 执行时间 3.2s → 0.01s
```

---

### 案例 2：回表过多 → 覆盖索引

**原始 SQL**（平均执行 1.8 秒）：

```sql
SELECT user_id, order_date, amount
FROM orders
WHERE user_id = 101 AND order_date >= '2026-01-01'
ORDER BY order_date;
```

**EXPLAIN 分析**：

```
+----+------+-----------------+------+-----------------------------+
| id | type | key             | rows | Extra                       |
+----+------+-----------------+------+-----------------------------+
|  1 | ref  | idx_user_date   | 5000 | Using where; Using filesort |
+----+------+-----------------+------+-----------------------------+
-- 走了 idx_user_date(user_id, order_date) 索引，但 Extra 有 Using filesort
-- 原因：amount 不在索引里，需要回表 5000 次；还需要额外排序
```

**问题分析**：查询列包含 `amount`，不在 `(user_id, order_date)` 索引中，需要回表。虽然 order_date 在索引里，但排序时还是产生了 filesort。

**优化后 SQL**（不改 SQL，只改索引）：

```sql
-- 重建为覆盖索引：把 SELECT 的列都加进索引
CREATE INDEX idx_user_date_amount ON orders(user_id, order_date, amount);

-- 同样的查询，不再需要回表
SELECT user_id, order_date, amount
FROM orders
WHERE user_id = 101 AND order_date >= '2026-01-01'
ORDER BY order_date;
```

**优化后 EXPLAIN**：

```
+----+------+------------------------+------+-------------+
| id | type | key                    | rows | Extra       |
+----+------+------------------------+------+-------------+
|  1 | ref  | idx_user_date_amount   | 5000 | Using index |
+----+------+------------------------+------+-------------+
-- Extra: Using index → 覆盖索引，不用回表
-- Using filesort 消失：索引已经按 (user_id, order_date) 排好序
-- 执行时间 1.8s → 0.05s
```

---

### 案例 3：大表分页 → 游标分页

**原始 SQL**（翻到第 50 万页时执行 8 秒）：

```sql
SELECT * FROM orders
ORDER BY order_id
LIMIT 1000000, 20;
```

**EXPLAIN 分析**：

```
+----+------+---------+------+-------------+
| id | type | key     | rows  | Extra       |
+----+------+---------+------+-------------+
|  1 | ALL  | PRIMARY | 100万 |             |
+----+------+---------+------+-------------+
-- type=ALL？这就奇怪了，ORDER BY order_id 为什么还全表扫描？
-- 原因：SELECT * 需要回表，MySQL 优化器认为全表扫描比"索引扫描 + 100万次回表"更划算
```

**问题分析**：`LIMIT 1000000, 20` 需要扫描并丢弃前 100 万行。MySQL 需要在"走索引排序后回表"和"全表扫描排序"之间选择，都不快。

**优化方案：延迟关联**：

```sql
-- 第一步：只从索引中找出 20 个 order_id（覆盖索引扫描）
-- 第二步：回表取完整数据
SELECT o.*
FROM orders o
INNER JOIN (
    SELECT order_id
    FROM orders
    ORDER BY order_id
    LIMIT 1000000, 20
) AS tmp ON o.order_id = tmp.order_id;
```

**优化后 EXPLAIN（子查询部分）**：

```
+----+------+---------+------+-------------+
| id | type | key     | rows | Extra       |
+----+------+---------+------+-------------+
|  1 | index| PRIMARY | 100万| Using index |
+----+------+---------+------+-------------+
-- type=index 全索引扫描（只扫 order_id，比全表快）
-- 然后只对 20 行回表
-- 执行时间 8s → 0.3s
```

**更优方案：游标分页**：

```sql
-- 前端记录上一页最大 order_id = 1000000
SELECT * FROM orders
WHERE order_id > 1000000
ORDER BY order_id
LIMIT 20;
-- 直接走主键索引定位，rows=20，执行时间 <0.01s
```

---

## 七、大表优化策略

### 水平拆分 vs 垂直拆分

```
                    拆分前（单表 5000 万行）
        ┌──────────────────────────────────────┐
        │  orders (order_id, user_id, ...,     │
        │          order_detail TEXT ...)      │
        └──────────────────────────────────────┘

        垂直拆分（按列拆分）              水平拆分（按行拆分）
        ┌──────────────┐                 ┌─ orders_2024 ─┐
        │ orders_main  │                 ├─ orders_2025 ─┤
        │ order_id     │                 ├─ orders_2026H1┤
        │ user_id      │                 └─ orders_2026H2┘
        │ order_date   │                 按时间或 user_id
        │ amount       │                 哈希取模分表
        └──────────────┘
        ┌──────────────┐
        │ orders_ext   │
        │ order_id     │
        │ order_detail │  ← TEXT 大字段
        │ logistics    │
        └──────────────┘
```

| 维度 | 水平拆分（Sharding） | 垂直拆分 |
|------|---------------------|----------|
| **拆分依据** | 按行（如 user_id 取模、按时间） | 按列（常用的列放主表，大字段放扩展表） |
| **目的** | 单表行数太大 → 分散到多个表 | 行宽太大 → 把不常用或不常更新的列拆出去 |
| **典型场景** | 订单表按年/月分表，用户表按 user_id 哈希 | order_detail TEXT 字段拆到扩展表 |
| **复杂度** | 高：跨分片查询、分布式事务 | 较低：JOIN 回主表即可 |
| **中间件** | ShardingSphere、Vitess、MyCat | 一般不需要额外中间件 |

### 读写分离架构

```
              应用程序
                 │
        ┌────────┴────────┐
        ▼                 ▼
    写请求             读请求
        │                 │
        ▼                 ▼
   ┌─────────┐    ┌─────────────┐
   │ Master  │───▶│ Slave 1     │  ← 异步复制
   │ (写)    │    │ (读)        │
   └─────────┘    ├─────────────┤
                  │ Slave 2     │
                  │ (读)        │
                  └─────────────┘
```

**核心要点**：
- 写操作走 Master，读操作走 Slave
- Slave 通过 binlog 异步复制，有延迟（通常 < 1s）
- 读到旧数据的问题：对实时性要求高的查询仍走 Master
- 适合读多写少的场景（大多数 Web 应用都是）

### 数据归档策略

```
活跃数据              冷数据
(近 3 个月)          (3 个月以前)
     │                    │
     ▼                    ▼
  orders 表          orders_archive 表
 (高性能存储)        (廉价存储 / 对象存储)
 保持 500 万行       定期迁移
```

**常见的归档策略**：
1. **定时任务迁移**：每天凌晨把 3 个月前且状态为"已完成"的订单迁到归档表
2. **分区表**：MySQL 原生分区，按月份分区 → 查询自动裁剪，删除旧分区比 DELETE 快得多
3. **冷热分离存储**：热数据在 MySQL，冷数据迁到 Hive / ClickHouse / Parquet 文件

---

## 八、优化清单（面试速答）

| 优先级 | 方法 | 效果 |
|--------|------|------|
| 1 | **加索引**（WHERE/JOIN/ORDER BY 列） | 最大提升（全表扫描→索引查找） |
| 2 | **减少返回列**（不要 SELECT *） | 减少 IO |
| 3 | **覆盖索引** | 避免回表 |
| 4 | **LIMIT** 限制返回行数 | 减少网络传输 |
| 5 | **优化 JOIN 顺序**（小表驱动大表） | 减少中间结果集 |
| 6 | **避免子查询**，改用 JOIN | 子查询可能物化临时表 |
| 7 | **分区表**（按时间分区） | 减少扫描范围 |

---

## 面试高频考点小结

| 考点 | 出现频率 | 关键知识点 |
|------|----------|-----------|
| EXPLAIN 字段解读 | 极高 | type/key/rows/Extra，ALL 最差 |
| B+ 树索引结构 | 高 | 为何比二叉树适合磁盘、3 层存百万数据 |
| 最左前缀原则 | 极高 | 联合索引匹配顺序、范围列之后失效 |
| 覆盖索引 | 很高 | Using index、避免回表 |
| 索引失效场景 | 很高 | 函数/前导模糊/类型转换/OR |
| 索引下推（ICP） | 中高 | 存储引擎层过滤、减少回表 |
| 慢查询日志 | 中 | 配置参数、mysqldumpslow 工具 |
| 分页优化 | 高 | LIMIT 原理、延迟关联、游标分页 |
| 大表 JOIN 优化 | 高 | 小表驱动大表、JOIN 列建索引 |
| COUNT 性能 | 中 | InnoDB vs MyISAM、汇总表替代 |
| 分库分表 | 中高 | 水平拆分 vs 垂直拆分 |
| 读写分离 | 中 | binlog 复制、主从延迟 |
| 索引设计原则 | 高 | 选择度、列顺序、不用过多索引 |

---

## 相关笔记

- [[数据库与SQL/窗口函数实战]]
- [[数据库与SQL/常见业务SQL场景]]
