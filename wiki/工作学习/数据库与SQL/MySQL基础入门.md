---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/mysql"
  - "#技术/sql"
  - "#状态/草稿"
created: 2026-07-03
updated: 2026-07-03
status: draft
---

# MySQL 基础入门

MySQL 是面试和工作中最常接触的关系型数据库。本文从零开始，覆盖 DDL、DML、DQL、JOIN、索引、事务，附带电商实战和面试高频考点。

---

## 一、数据库基础概念

### 1.1 什么是关系型数据库

关系型数据库把数据组织成**表（Table）**，每张表由**行（Row）**和**列（Column）**构成：

| 类比 | 数据库概念 | 说明 |
|------|-----------|------|
| Excel 文件 | Database | 一个数据库包含多张表 |
| Sheet 页 | Table | 一张表存一类实体（用户、订单） |
| 列标题 | Column / Field | 描述属性（姓名、年龄、金额） |
| 每一行数据 | Row / Record | 一条具体记录 |

**核心约束**：

| 约束 | 作用 |
|------|------|
| 主键（Primary Key） | 唯一标识一行，不能重复、不能为空 |
| 外键（Foreign Key） | 关联另一张表的主键，保证引用完整性 |

```sql
-- 用户表
CREATE TABLE users (
    user_id  INT PRIMARY KEY,        -- 主键
    name     VARCHAR(50) NOT NULL,
    email    VARCHAR(100) UNIQUE
);

-- 订单表
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id  INT NOT NULL,
    amount   DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(user_id)  -- 外键关联用户表
);
```

### 1.2 MySQL 安装与连接

**命令行连接**：

```bash
# 本地连接
mysql -u root -p

# 远程连接
mysql -h 192.168.1.100 -P 3306 -u root -p

# 连接后查看有哪些数据库
SHOW DATABASES;

# 选择数据库
USE mydb;

# 查看当前库有哪些表
SHOW TABLES;

# 查看表结构
DESC users;
```

**图形化工具推荐**：

| 工具 | 特点 |
|------|------|
| Navicat | 功能最全，付费，国产公司常用 |
| DBeaver | 免费开源，支持多种数据库 |
| MySQL Workbench | MySQL 官方工具，免费 |
| DataGrip | JetBrains 出品，和 IDEA 无缝集成 |

### 1.3 数据库 vs 表的层级关系

```
MySQL Server
  └── Database（库）
        ├── Table A（表）
        │     ├── Column 1（列）
        │     ├── Column 2（列）
        │     └── ...
        ├── Table B（表）
        ├── View（视图）
        └── Stored Procedure（存储过程）
  └── Database 2
        └── ...
```

**面试话术**："一个 MySQL 实例可以有多个数据库，一个数据库包含多张表。表是数据存储的基本单元，每行是一条记录，每列是一个字段。"

---

## 二、DDL（数据定义语言）

DDL 管"结构"——建库、建表、改表、删表。

### 2.1 CREATE DATABASE

```sql
-- 创建数据库
CREATE DATABASE shop CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 如果不存在才创建（推荐）
CREATE DATABASE IF NOT EXISTS shop;

-- 删除数据库
DROP DATABASE IF EXISTS shop;
```

`utf8mb4` 支持 emoji 和所有 Unicode 字符，`utf8mb4_unicode_ci` 是大小写不敏感的排序规则。

### 2.2 CREATE TABLE

```sql
CREATE TABLE products (
    product_id   INT AUTO_INCREMENT,        -- 自增
    name         VARCHAR(200)  NOT NULL,     -- 商品名，非空
    category     VARCHAR(50)   DEFAULT '其他', -- 默认值
    price        DECIMAL(10,2) NOT NULL,     -- 价格，2位小数
    stock        INT           DEFAULT 0,    -- 库存
    description  TEXT,                       -- 长文本
    created_at   DATETIME      DEFAULT CURRENT_TIMESTAMP,  -- 创建时间
    updated_at   DATETIME      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id),
    UNIQUE KEY uk_name (name),              -- 商品名唯一
    CHECK (price > 0),                      -- 价格必须 > 0
    CHECK (stock >= 0)                      -- 库存不能为负
);
```

### 2.3 常用数据类型

| 类型 | 用途 | 示例 |
|------|------|------|
| `INT` | 整数 | `age INT` |
| `BIGINT` | 大整数（ID、时间戳） | `id BIGINT` |
| `VARCHAR(N)` | 变长字符串，最大 N 个字符 | `name VARCHAR(50)` |
| `CHAR(N)` | 定长字符串，固定占 N 个字符 | `gender CHAR(1)` |
| `TEXT` | 长文本（最大 64KB） | `description TEXT` |
| `LONGTEXT` | 超大文本（最大 4GB） | `content LONGTEXT` |
| `DECIMAL(M,D)` | 定点小数，M 位总长，D 位小数 | `price DECIMAL(10,2)` |
| `FLOAT` / `DOUBLE` | 浮点数（不精确，别用来存钱） | `score FLOAT` |
| `DATE` | 日期（年-月-日） | `birthday DATE` |
| `DATETIME` | 日期+时间 | `created_at DATETIME` |
| `TIMESTAMP` | 时间戳（自动时区转换，2038 年溢出） | `updated_at TIMESTAMP` |
| `BOOLEAN` | 布尔（实际存为 TINYINT(1)） | `is_active BOOLEAN` |
| `ENUM('a','b','c')` | 枚举，只允许列出的值 | `status ENUM('上架','下架')` |

> **钱用 DECIMAL 不用 FLOAT**：FLOAT 有精度损失，`0.1 + 0.2 != 0.3` 问题在金融场景不可接受。

### 2.4 约束详解

```sql
CREATE TABLE demo_constraints (
    id        INT PRIMARY KEY,                    -- 主键（非空 + 唯一）
    email     VARCHAR(100) UNIQUE,                -- 唯一约束
    age       INT NOT NULL,                       -- 非空约束
    gender    CHAR(1) DEFAULT 'U',                 -- 默认值
    score     INT CHECK (score BETWEEN 0 AND 100),-- 检查约束（MySQL 8.0+ 才强制）
    dept_id   INT,
    FOREIGN KEY (dept_id) REFERENCES dept(id)     -- 外键约束
);
```

### 2.5 ALTER TABLE / DROP TABLE

```sql
-- 添加列
ALTER TABLE products ADD COLUMN brand VARCHAR(100);

-- 修改列类型
ALTER TABLE products MODIFY COLUMN price DECIMAL(12,2);

-- 重命名列
ALTER TABLE products CHANGE COLUMN name product_name VARCHAR(200);

-- 删除列
ALTER TABLE products DROP COLUMN brand;

-- 添加索引
ALTER TABLE products ADD INDEX idx_category (category);

-- 删除表（数据全丢，不可恢复）
DROP TABLE IF EXISTS products;

-- 只清空数据，保留表结构
TRUNCATE TABLE products;
```

---

## 三、DML（数据操作语言）

DML 管"数据"——增、改、删。

### 3.1 INSERT

```sql
-- 单行插入
INSERT INTO products (name, category, price, stock)
VALUES ('iPhone 15', '数码', 5999.00, 100);

-- 多行插入（比逐行插快很多）
INSERT INTO products (name, category, price, stock) VALUES
('MacBook Pro', '数码', 14999.00, 50),
('Nike Air Max', '运动', 899.00, 200),
('可乐', '食品', 3.50, 1000);

-- INSERT INTO SELECT：把查询结果插入另一张表
INSERT INTO products_backup (name, category, price, stock)
SELECT name, category, price, stock FROM products
WHERE stock > 0;

-- 插入或更新（如果主键/唯一键冲突就更新）
INSERT INTO products (name, category, price, stock)
VALUES ('iPhone 15', '数码', 6199.00, 120)
ON DUPLICATE KEY UPDATE price = 6199.00, stock = stock + 120;
```

### 3.2 UPDATE

```sql
-- 更新单列，一定要带 WHERE！
UPDATE products SET price = 6299.00 WHERE name = 'iPhone 15';

-- 更新多列
UPDATE products
SET price = price * 0.9, stock = stock - 1
WHERE category = '数码' AND stock > 0;

-- 多表更新
UPDATE orders o
JOIN users u ON o.user_id = u.user_id
SET o.status = 'VIP'
WHERE u.level = 'VIP';
```

> **血的教训**：执行 UPDATE / DELETE **之前先写 SELECT 确认受影响的行**，忘写 WHERE 全表更新是数据库事故排行第一的原因。

### 3.3 DELETE vs TRUNCATE

```sql
-- 删除指定行
DELETE FROM products WHERE stock = 0;

-- 多表删除
DELETE o FROM orders o
JOIN users u ON o.user_id = u.user_id
WHERE u.status = '已注销';

-- 清空表
TRUNCATE TABLE products;
```

| 对比维度 | DELETE | TRUNCATE |
|---------|--------|----------|
| 删除方式 | 逐行删除 | 直接释放整个数据页 |
| 是否可回滚 | 可以（在事务中） | **不可以**（DDL，隐式提交） |
| WHERE 条件 | 支持 | 不支持 |
| 自增计数重置 | 不重置 | 重置为 1 |
| 触发触发器 | 触发 | 不触发 |
| 速度 | 慢 | 快 |

**面试话术**："DELETE 是 DML，逐行删除，可回滚。TRUNCATE 是 DDL，直接释放数据页，不可回滚，速度快得多。如果需要清空大表且不需要回滚，用 TRUNCATE。"

---

## 四、DQL（数据查询语言）

DQL 是面试和工作中用得最多的部分。

### 4.1 SELECT 基础

```sql
-- 查所有列（生产环境禁止 SELECT * ，只取需要的列）
SELECT product_id, name, price FROM products;

-- 别名（AS 可省略）
SELECT name AS 商品名, price AS 价格 FROM products;

-- DISTINCT 去重
SELECT DISTINCT category FROM products;

-- 计算列
SELECT name, price, stock, price * stock AS 库存市值 FROM products;

-- LIMIT + OFFSET 分页
SELECT * FROM products ORDER BY product_id LIMIT 10 OFFSET 20;  -- 第21-30条
```

### 4.2 WHERE 条件

```sql
-- 比较运算
SELECT * FROM products WHERE price > 1000;
SELECT * FROM products WHERE category = '数码';

-- LIKE 模糊匹配
SELECT * FROM products WHERE name LIKE '%iPhone%';   -- 包含 iPhone
SELECT * FROM products WHERE name LIKE 'iPhon_';      -- _ 匹配单个字符

-- IN
SELECT * FROM products WHERE category IN ('数码', '运动', '食品');

-- BETWEEN（闭区间）
SELECT * FROM products WHERE price BETWEEN 100 AND 1000;

-- AND / OR（AND 优先级 > OR，复杂条件加括号！）
SELECT * FROM products
WHERE (category = '数码' OR category = '运动')
  AND price < 5000
  AND stock > 0;

-- IS NULL / IS NOT NULL（不能用 = NULL）
SELECT * FROM products WHERE description IS NULL;
```

### 4.3 ORDER BY

```sql
-- 默认升序 ASC，降序用 DESC
SELECT * FROM products ORDER BY price DESC;

-- 多字段排序：先按分类升序，同类内按价格降序
SELECT * FROM products ORDER BY category ASC, price DESC;

-- 配合 LIMIT 取 Top N
SELECT name, price FROM products ORDER BY price DESC LIMIT 5;  -- 最贵 5 件
```

### 4.4 GROUP BY + 聚合函数

```sql
-- 每个分类的商品数量和平均价格
SELECT
    category,
    COUNT(*)        AS 商品数,
    AVG(price)      AS 均价,
    MAX(price)      AS 最高价,
    MIN(price)      AS 最低价,
    SUM(stock)      AS 总库存
FROM products
GROUP BY category;

-- 聚合函数会忽略 NULL 值（COUNT(*) 除外）
```

**常见聚合函数**：

| 函数 | 作用 | 注意 |
|------|------|------|
| `COUNT(*)` | 统计行数（含 NULL） | 最常用 |
| `COUNT(column)` | 统计该列非 NULL 的行数 | NULL 不计数 |
| `SUM(column)` | 求和 | 忽略 NULL |
| `AVG(column)` | 平均值 | 忽略 NULL |
| `MAX(column)` | 最大值 | |
| `MIN(column)` | 最小值 | |

### 4.5 HAVING vs WHERE

```sql
-- 查询均价 > 500 的分类
-- 错误写法：WHERE AVG(price) > 500  ❌ WHERE 里不能用聚合函数
-- 正确写法：
SELECT category, AVG(price) AS avg_price
FROM products
GROUP BY category
HAVING AVG(price) > 500;
```

| 对比维度 | WHERE | HAVING |
|---------|-------|--------|
| 过滤时机 | **分组前**过滤行 | **分组后**过滤组 |
| 能否用聚合函数 | 不能 | 能 |
| 执行顺序 | FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY |
| 性能 | 优先用 WHERE 过滤，减少分组的数据量 | HAVING 处理聚合后的结果 |

**面试话术**："WHERE 在 GROUP BY 之前执行，过滤原始行；HAVING 在 GROUP BY 之后执行，过滤聚合结果。能用 WHERE 就不要用 HAVING，减少分组的数据量。"

### 4.6 SQL 执行顺序（面试必问）

```
FROM  →  ON  →  JOIN  →  WHERE  →  GROUP BY  →  HAVING  →  SELECT  →  DISTINCT  →  ORDER BY  →  LIMIT
```

这个顺序解释了为什么 WHERE 不能用别名，而 ORDER BY 可以。

---

## 五、JOIN 详解

JOIN 是 SQL 的灵魂，面试必考。先准备两张演示表：

```sql
-- 学生表
CREATE TABLE student (
    id   INT PRIMARY KEY,
    name VARCHAR(20)
);
INSERT INTO student VALUES
(1, '张三'), (2, '李四'), (3, '王五'), (4, '赵六');

-- 选课表
CREATE TABLE course (
    id         INT PRIMARY KEY,
    student_id INT,
    course     VARCHAR(20)
);
INSERT INTO course VALUES
(1, 1, '数学'), (2, 1, '语文'),
(3, 2, '数学'),
(4, 5, '英语');   -- student_id=5，学生表里没有
```

**数据概览**：
| student | | course | |
|---------|---------|--------|------|
| id=1 张三 | | id=1, sid=1, 数学 |
| id=2 李四 | | id=2, sid=1, 语文 |
| id=3 王五 | | id=3, sid=2, 数学 |
| id=4 赵六 | | id=4, sid=5, 英语 |

### 5.1 INNER JOIN（内连接 — 取交集）

```sql
SELECT s.id, s.name, c.course
FROM student s
INNER JOIN course c ON s.id = c.student_id;
```

结果：

| id | name | course |
|----|------|--------|
| 1  | 张三 | 数学 |
| 1  | 张三 | 语文 |
| 2  | 李四 | 数学 |

- 只返回两表都匹配的行
- 王五 (id=3) 没选课 → 不出现
- 赵六 (id=4) 没选课 → 不出现
- 英语课 (sid=5) 学生不存在 → 不出现

**面试话术**："INNER JOIN 返回两表的交集，只有满足 ON 条件的行才会出现在结果中。这是最常用的 JOIN 类型。"

### 5.2 LEFT JOIN（左连接 — 左表全保留）

```sql
SELECT s.id, s.name, c.course
FROM student s
LEFT JOIN course c ON s.id = c.student_id;
```

结果：

| id | name | course |
|----|------|--------|
| 1  | 张三 | 数学 |
| 1  | 张三 | 语文 |
| 2  | 李四 | 数学 |
| 3  | 王五 | **NULL** |
| 4  | 赵六 | **NULL** |

- 左表（student）所有行都保留
- 右表没有匹配的填 NULL
- 王五、赵六虽然是 NULL 但出现了

**面试话术**："LEFT JOIN 以左表为主，左表所有行都出现，右表匹配不上就填空（NULL）。常用于'查所有用户及其订单（包括没有订单的用户）'这类场景。"

### 5.3 RIGHT JOIN（右连接 — 右表全保留）

```sql
SELECT s.id, s.name, c.course
FROM student s
RIGHT JOIN course c ON s.id = c.student_id;
```

结果：

| id | name | course |
|----|------|--------|
| 1  | 张三 | 数学 |
| 1  | 张三 | 语文 |
| 2  | 李四 | 数学 |
| **NULL** | **NULL** | 英语 |

- 右表（course）所有行保留
- 左表匹配不上填空
- "英语"课的 student_id=5 在 student 表不存在，但仍出现

> **实际开发中大家几乎只用 LEFT JOIN**，把"主表"放左边，RIGHT JOIN 改成 LEFT JOIN 换一下表顺序就行，更直观。

### 5.4 FULL OUTER JOIN（全外连接）

MySQL **不直接支持** FULL OUTER JOIN，用 UNION 模拟：

```sql
-- MySQL 写法：LEFT JOIN + RIGHT JOIN 的结果合并（去重）
SELECT s.id, s.name, c.course
FROM student s
LEFT JOIN course c ON s.id = c.student_id

UNION   -- UNION 自带去重

SELECT s.id, s.name, c.course
FROM student s
RIGHT JOIN course c ON s.id = c.student_id;
```

结果：

| id | name | course |
|----|------|--------|
| 1  | 张三 | 数学 |
| 1  | 张三 | 语文 |
| 2  | 李四 | 数学 |
| 3  | 王五 | NULL |
| 4  | 赵六 | NULL |
| NULL | NULL | 英语 |

**面试话术**："MySQL 不支持 FULL OUTER JOIN，实际中用 UNION 连接 LEFT JOIN 和 RIGHT JOIN 的结果来模拟。UNION 会去重，UNION ALL 不去重。"

### 5.5 CROSS JOIN（笛卡尔积）

```sql
-- 隐式写法
SELECT s.name, c.course FROM student s, course c;

-- 显式写法（推荐）
SELECT s.name, c.course FROM student s CROSS JOIN course c;
```

结果：4 个学生 x 4 门课 = 16 行。**很少直接用**，通常配合 WHERE 条件变成 INNER JOIN。

### 5.6 自连接（SELF JOIN）

同一张表自己连自己，处理"同一张表内的层级/关联关系"。

```sql
-- 员工表：查每个员工及其上级
SELECT e.name AS 员工, m.name AS 上级
FROM employee e
LEFT JOIN employee m ON e.manager_id = m.id;
```

### 5.7 JOIN 总结表格

| JOIN 类型 | 结果 | 一句话 |
|-----------|------|--------|
| INNER JOIN | 两表匹配的行 | 交集 |
| LEFT JOIN | 左表全部 + 右表匹配 | 左表为主 |
| RIGHT JOIN | 右表全部 + 左表匹配 | 右表为主 |
| FULL OUTER JOIN | 两表全部 | 并集（MySQL 用 UNION 模拟） |
| CROSS JOIN | 两表所有组合 | 笛卡尔积 |
| SELF JOIN | 表连自己 | 层级关系 |

---

## 六、索引

### 6.1 索引原理（B+ 树）

没有索引，MySQL 只能逐行扫描（全表扫描）。有了索引，走 B+ 树查找：

- **B+ 树**：所有数据存在叶子节点，叶子节点之间用链表连接
- 查找时从根节点出发，每次比较决定走哪个分支，3-4 次查找就能找到任意数据
- 时间复杂度 O(log n)，全表扫描是 O(n)

**为什么 B+ 树而不是二叉树？**
二叉树在数据递增插入时会退化成链表；B+ 树是平衡多路树，一个节点可以存很多 key，树高很低，适合磁盘 IO（一次 IO 读一整页）。

**面试话术**："索引是 B+ 树结构，叶子节点存所有数据且用双向链表连接，支持快速查找和范围查询。索引减少磁盘 IO 次数，但会降低写操作速度（增删改需要同时维护索引）。"

### 6.2 创建索引

```sql
-- 单列索引
CREATE INDEX idx_category ON products(category);

-- 唯一索引（值不能重复）
CREATE UNIQUE INDEX uk_name ON products(name);

-- 联合索引（多列组合成一个索引）
CREATE INDEX idx_cat_price ON products(category, price);

-- 全文索引（用于大文本搜索）
CREATE FULLTEXT INDEX ft_description ON products(description);

-- 删除索引
DROP INDEX idx_category ON products;
```

### 6.3 索引类型对比

| 索引类型 | 特点 | 每表数量 |
|---------|------|---------|
| 主键索引 | 唯一、非空、聚簇索引（数据按主键物理排序） | 1 个 |
| 唯一索引 | 值不能重复，允许 NULL | 多个 |
| 普通索引 | 加速查询，无约束 | 多个 |
| 联合索引 | 多列组合，遵循最左前缀原则 | 多个 |
| 全文索引 | 大文本模糊搜索 | 多个 |

### 6.4 联合索引 + 最左前缀原则

```sql
-- 建联合索引
CREATE INDEX idx_a_b_c ON demo(a, b, c);

-- 以下走索引：
WHERE a = 1;                    -- ✅ 匹配最左列 a
WHERE a = 1 AND b = 2;          -- ✅ a → b，匹配到 b
WHERE a = 1 AND b = 2 AND c = 3;-- ✅ 全部匹配
WHERE a = 1 AND c = 3;          -- ✅ a 匹配，但 c 不走索引（跳过了 b）

-- 以下不走索引：
WHERE b = 2;                    -- ❌ 跳过了最左列 a
WHERE c = 3;                    -- ❌ 跳过了 a 和 b
WHERE a = 1 AND b > 2 AND c = 3;-- ⚠️ a=1 走索引，b>2 走索引（范围），c 不走
```

**面试话术**："联合索引遵循最左前缀原则——查询条件必须从索引定义的最左列开始，中间不能跳过。范围查询后面的列不走索引。建索引时把等值查询列放前面，范围查询列放后面。"

### 6.5 EXPLAIN 解读

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 101;
```

关键字段：

| 字段 | 含义 | 怎么算好 |
|------|------|---------|
| `type` | 访问类型 | `const` > `eq_ref` > `ref` > `range` > `index` > **`ALL`** |
| `key` | 实际使用的索引 | NULL = 没走索引，有问题 |
| `key_len` | 索引使用长度 | 越大说明联合索引利用越充分 |
| `rows` | 预估扫描行数 | 越小越好 |
| `Extra` | 额外信息 | `Using index`（覆盖索引，好）；`Using filesort`（额外排序，差）；`Using temporary`（临时表，差） |

**重点 type 值**：

| type | 含义 | 举例 |
|------|------|------|
| `const` | 主键或唯一索引等值查询 | `WHERE id = 1` |
| `eq_ref` | JOIN 时用主键/唯一键关联 | 每行只匹配一行 |
| `ref` | 普通索引等值查询 | `WHERE user_id = 101` |
| `range` | 索引范围扫描 | `WHERE id > 10 AND id < 100` |
| `index` | 全索引扫描（比全表好一点） | 遍历整个索引树 |
| `ALL` | **全表扫描（最差）** | 没走索引 |

### 6.6 索引失效场景

```sql
-- 假设有索引 idx_phone(phone)

-- ❌ 1. 对列做函数运算
SELECT * FROM users WHERE LEFT(phone, 3) = '138';   -- 失效
SELECT * FROM users WHERE phone LIKE '138%';         -- ✅ 等价且走索引

-- ❌ 2. 隐式类型转换
-- phone 是 VARCHAR，用整数比较
SELECT * FROM users WHERE phone = 13800000001;       -- 失效
SELECT * FROM users WHERE phone = '13800000001';     -- ✅ 用字符串

-- ❌ 3. LIKE 以 % 开头
SELECT * FROM users WHERE phone LIKE '%138';         -- 失效
SELECT * FROM users WHERE phone LIKE '138%';         -- ✅ 前缀匹配走索引

-- ❌ 4. OR 条件中有未索引的列
SELECT * FROM users WHERE phone = '138' OR name = '张三';
-- 如果 name 没有索引 → 全表
-- 改进：给 name 也建索引，或用 UNION

-- ❌ 5. 不等于 / NOT IN 通常不走索引
SELECT * FROM users WHERE status != '已注销';        -- 不走索引

-- ❌ 6. IS NULL 在部分情况不走索引
```

**面试话术**："索引失效的常见场景：对列做函数运算、隐式类型转换、LIKE 以 % 开头、OR 条件中有未索引列、联合索引不满足最左前缀。排查方法是用 EXPLAIN 看 type 是否为 ALL。"

### 6.7 什么时候建索引 / 什么时候不建

| 该建索引 | 不该建索引 |
|---------|-----------|
| WHERE / JOIN / ORDER BY 常用列 | 表很小（几千行以下） |
| 选择性高的列（值分布广） | 选择性低的列（性别：只有男女） |
| 外键列 | 频繁更新的列（维护索引成本高） |
| 联合查询中经常一起用的多列 | 大字段 TEXT / BLOB |
| 覆盖查询的所有列（覆盖索引） | 增删改远多于查的表 |

---

## 七、事务

### 7.1 ACID 四大特性

| 特性 | 含义 | 举例 |
|------|------|------|
| **A**tomicity 原子性 | 要么全做，要么全不做 | 转账：扣钱 + 加钱 必须同时成功 |
| **C**onsistency 一致性 | 事务前后数据都符合约束 | 转账前后总金额不变 |
| **I**solation 隔离性 | 并发事务互不干扰 | A 转账时 B 看不到未提交的中间态 |
| **D**urability 持久性 | 提交后数据永久保存 | 断电重启后钱还在 |

### 7.2 事务操作

```sql
-- 开启事务
BEGIN;   -- 或 START TRANSACTION;

-- 操作
UPDATE accounts SET balance = balance - 100 WHERE user_id = 1;
UPDATE accounts SET balance = balance + 100 WHERE user_id = 2;

-- 没问题就提交
COMMIT;

-- 出问题就回滚
ROLLBACK;

-- 设置保存点（回滚到指定位置）
SAVEPOINT sp1;
UPDATE accounts SET balance = balance - 50 WHERE user_id = 1;
-- 发现不对，回滚到保存点
ROLLBACK TO sp1;
```

### 7.3 隔离级别

```sql
-- 查看当前隔离级别
SELECT @@transaction_isolation;

-- 设置隔离级别
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 性能 |
|---------|:----:|:--------:|:----:|------|
| READ UNCOMMITTED | 会 | 会 | 会 | 最快 |
| READ COMMITTED | 不会 | 会 | 会 | 较快 |
| **REPEATABLE READ**（MySQL 默认） | 不会 | 不会 | 基本不会 | 中等 |
| SERIALIZABLE | 不会 | 不会 | 不会 | 最慢 |

**三种并发问题**：

| 问题 | 描述 | 举例 |
|------|------|------|
| 脏读 | 读到别的事务未提交的数据 | A 改了钱但没提交，B 读到了，A 回滚了，B 读的是脏数据 |
| 不可重复读 | 同一事务两次读结果不同（被别的事务更新了） | A 读了价 100，B 改成 200 并提交，A 再读变成 200 |
| 幻读 | 同一事务两次查询，行数不同（被别的事务插入了） | A 查了 3 条，B 插入 1 条并提交，A 再查变成 4 条 |

**MySQL 的 REPEATABLE READ 如何解决幻读**：通过 **MVCC（多版本并发控制）+ Gap Lock（间隙锁）**，在可重复读级别下，MySQL 的 InnoDB 引擎也能避免幻读。

**面试话术**："MySQL 默认隔离级别是 REPEATABLE READ，通过 MVCC 实现。MVCC 给每行保留多个版本，读操作读快照，写操作加锁，读写不互斥。READ COMMITTED 每次读最新快照，REPEATABLE READ 整个事务用同一个快照。"

---

## 八、实战：电商数据库设计

### 8.1 建表

```sql
-- 用户表
CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    phone         VARCHAR(20)  NOT NULL,
    register_date DATETIME     DEFAULT CURRENT_TIMESTAMP,
    level         ENUM('普通','VIP','SVIP') DEFAULT '普通',
    INDEX idx_phone (phone),
    INDEX idx_level (level)
);

-- 商品表
CREATE TABLE products (
    product_id  INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(200) NOT NULL,
    category    VARCHAR(50)  NOT NULL,
    price       DECIMAL(10,2) NOT NULL,
    stock       INT DEFAULT 0,
    status      ENUM('上架','下架') DEFAULT '上架',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_category (category),
    INDEX idx_price (price),
    INDEX idx_cat_price (category, price)   -- 联合索引：分类内按价格筛选
);

-- 订单表
CREATE TABLE orders (
    order_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,
    status      ENUM('待支付','已支付','已发货','已完成','已取消') DEFAULT '待支付',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
);

-- 订单明细表
CREATE TABLE order_items (
    item_id    INT AUTO_INCREMENT PRIMARY KEY,
    order_id   INT NOT NULL,
    product_id INT NOT NULL,
    quantity   INT NOT NULL DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,    -- 冗余单价，避免商品调价影响历史订单
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_order_id (order_id)
);
```

### 8.2 测试数据

```sql
INSERT INTO users (username, phone, level) VALUES
('alice', '13800000001', 'VIP'),
('bob',   '13800000002', '普通'),
('cathy', '13800000003', 'SVIP'),
('david', '13800000004', '普通');

INSERT INTO products (name, category, price, stock) VALUES
('iPhone 15',       '数码', 5999.00, 100),
('MacBook Pro',     '数码', 14999.00, 50),
('Nike Air Max',    '运动', 899.00, 200),
('Adidas T恤',      '运动', 199.00, 300),
('三只松鼠坚果',    '食品', 49.90, 500),
('可口可乐',        '食品', 3.50, 1000);

INSERT INTO orders (user_id, total_amount, status) VALUES
(1, 6897.00, '已完成'),
(2, 199.00,  '已支付'),
(1, 899.00,  '待支付'),
(3, 53.40,  '已完成');

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
(1, 1, 1, 5999.00),
(1, 3, 1, 898.00),
(2, 4, 1, 199.00),
(3, 3, 1, 899.00),
(4, 6, 4, 3.50),
(4, 5, 2, 49.90);
```

### 8.3 常见业务查询

**查询 1：每个用户的消费总额（含未消费用户）**

```sql
SELECT
    u.username,
    COALESCE(SUM(o.total_amount), 0) AS 总消费
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id AND o.status != '已取消'
GROUP BY u.user_id, u.username
ORDER BY 总消费 DESC;
```

**查询 2：每个商品分类的销量 Top 3**

```sql
SELECT category, name, sales
FROM (
    SELECT
        p.category, p.name,
        SUM(oi.quantity) AS sales,
        RANK() OVER (PARTITION BY p.category ORDER BY SUM(oi.quantity) DESC) AS rk
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.status != '已取消'
    GROUP BY p.category, p.product_id, p.name
) t
WHERE rk <= 3;
```

**查询 3：过去 30 天没下单的用户**

```sql
SELECT u.username, u.phone
FROM users u
WHERE u.user_id NOT IN (
    SELECT DISTINCT user_id
    FROM orders
    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
);
```

**查询 4：客单价最高的前 3 个用户**

```sql
SELECT
    u.username,
    COUNT(o.order_id) AS 订单数,
    ROUND(AVG(o.total_amount), 2) AS 客单价
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.status != '已取消'
GROUP BY u.user_id, u.username
ORDER BY 客单价 DESC
LIMIT 3;
```

**查询 5：库存低于 10 的商品（报警）**

```sql
SELECT name, category, stock
FROM products
WHERE stock < 10 AND status = '上架'
ORDER BY stock ASC;
```

### 8.4 用 EXPLAIN 分析慢查询

```sql
-- 假设这个查询很慢
EXPLAIN SELECT
    u.username,
    o.order_id,
    o.total_amount
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE u.level = 'VIP'
  AND o.created_at >= '2026-06-01'
ORDER BY o.created_at DESC;
```

解读：

| 字段 | 可能的值 | 分析 |
|------|---------|------|
| type（users） | ref | `idx_level` 走了索引，OK |
| type（orders） | ref | `user_id` 走外键索引，OK |
| Extra | Using filesort | 对 `created_at` 排序需要建联合索引 |

优化方案：
```sql
-- 建覆盖索引避免 filesort
CREATE INDEX idx_user_created ON orders(user_id, created_at, total_amount);
```

---

## 九、面试高频考点

| 序号 | 问题 | 简短答案 |
|:----:|------|---------|
| 1 | **SQL 执行顺序** | FROM → ON → JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT |
| 2 | **WHERE vs HAVING** | WHERE 分组前过滤行，不能用聚合；HAVING 分组后过滤组，能用聚合 |
| 3 | **DELETE vs TRUNCATE** | DELETE 逐行删可回滚；TRUNCATE 释放数据页不可回滚，速度更快 |
| 4 | **JOIN 类型** | INNER=交集，LEFT=左全+右匹配，RIGHT=右全+左匹配，FULL=并集(UNION 模拟)，CROSS=笛卡尔积 |
| 5 | **最左前缀原则** | 联合索引必须从最左列开始匹配，中间不能跳过，范围查询后面的列失效 |
| 6 | **索引失效场景** | 函数运算、隐式转换、LIKE '%x'、OR 有未索引列、联合索引不满足最左前缀 |
| 7 | **ACID** | 原子性、一致性、隔离性、持久性 |
| 8 | **隔离级别** | 读未提交→读已提交→可重复读(MySQL 默认)→可串行化；级别越高并发越低 |
| 9 | **脏读/不可重复读/幻读** | 脏读=读未提交；不可重复读=同事务两次读值不同(被更新)；幻读=行数不同(被插入) |
| 10 | **B+ 树为什么快** | 平衡多路，树高低，一次 IO 读一页，叶子节点链表支持范围查询，O(log n) vs O(n) |
| 11 | **覆盖索引** | 索引包含了查询需要的所有列，不回表，Extra 显示 Using index |
| 12 | **EXPLAIN 关注什么** | type（ALL 最差）、key（NULL 不走索引）、rows（越大越慢）、Extra（filesort/temporary 差） |

---

## 相关笔记

- [[工作学习/数据库与SQL/窗口函数实战|窗口函数实战]]
- [[工作学习/数据库与SQL/SQL查询优化|SQL 查询优化]]
- [[工作学习/数据库与SQL/常见业务SQL场景|常见业务 SQL 场景]]
- [[工作学习/大数据技术/Hive基础|Hive 基础]]
- [[工作学习/大数据技术/HBase基础|HBase 基础]]
- [[工作学习/Python数据栈/pandas实战-电商订单分析|pandas 实战]]
- [[工作学习/书架与学习路线|书架与学习路线]]
