---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/hive"
  - "#技术/大数据"
  - "#状态/草稿"
created: 2026-07-02
updated: 2026-07-02
status: draft
---

# Hive 基础

Hive 是 Facebook 开源的**基于 Hadoop 的数据仓库工具**，核心价值在于：把 SQL 语句翻译成 MapReduce/Tez/Spark 作业，让不懂 Java 的分析师也能处理 PB 级数据。

**一句话理解**：Hive = SQL 接口 + HDFS 存储 + 分布式计算引擎。你写 SQL，它帮你跑 MapReduce。

## 一、数据仓库 vs 数据库（OLAP vs OLTP）

这是面试第一个区分点——Hive 是数据仓库，不是数据库。

| 维度 | 数据仓库（Hive） | 数据库（MySQL/Oracle） |
|------|------------------|------------------------|
| 用途 | OLAP（分析型） | OLTP（事务型） |
| 数据量 | PB 级 | GB-TB 级 |
| 响应时间 | 秒-分钟级（批处理） | 毫秒级 |
| 事务支持 | 不支持 ACID（0.14 后有限支持） | 完整 ACID |
| 读写模式 | 一次写入、多次读取 | 频繁增删改 |
| 数据更新 | 不支持 UPDATE/DELETE（或很慢） | 支持 |
| 索引 | 不支持传统索引（有分区/分桶） | B+ 树索引 |
| 扩展性 | 水平扩展（加节点） | 垂直扩展（加配置） |
| 典型场景 | 日报/周报、用户画像、留存分析 | 订单系统、用户登录 |

**面试话术**："数据库面向事务处理（OLTP），要求低延迟、高并发、ACID；数据仓库面向分析处理（OLAP），数据量大、查询复杂、允许一定延迟。Hive 属于 OLAP，适合批量离线分析，不适合实时查询。"

### Hive 的优缺点

**优点**：
- 学习成本低：会 SQL 就会用，不需要学 MapReduce Java API
- 处理能力强：PB 级数据轻松处理
- 生态集成好：和 Hadoop/HDFS/HBase/Spark 无缝对接
- 可扩展：自定义 UDF、UDAF、UDTF
- 成本低：开源，跑在廉价机器上

**缺点**：
- 延迟高：即使换成 Tez/Spark 引擎，也是秒级起步
- 不支持实时查询：做不到毫秒级返回（用 HBase/ClickHouse 补位）
- 不支持行级更新：只能全表覆盖或分区覆盖
- SQL 能力有限：不支持子查询的某些写法，PL/SQL 能力弱

## 二、Hive 架构

```
┌──────────────────────────────────────────────┐
│                  用户接口层                    │
│   CLI (hive>)  │  JDBC/ODBC  │  HiveServer2  │
└──────────────────┬───────────────────────────┘
                   │ SQL 语句
┌──────────────────▼───────────────────────────┐
│                 Driver（驱动层）               │
│  解析器(Parser) → 编译器(Compiler)             │
│  → 优化器(Optimizer) → 执行器(Executor)        │
└──────────────────┬───────────────────────────┘
                   │ 元数据查询
┌──────────────────▼───────────────────────────┐
│              Metastore（元数据）               │
│  Derby(内嵌) / MySQL(生产) / PostgreSQL       │
│  存储：表名、列、分区、HDFS 路径、SerDe 等      │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│           Hadoop 集群（计算 + 存储）           │
│  MapReduce / Tez / Spark    │      HDFS       │
└──────────────────────────────────────────────┘
```

**关键组件说明**：

| 组件 | 角色 | 生产环境配置 |
|------|------|-------------|
| Metastore | 存储元数据（表结构、分区信息、HDFS 路径） | **必须用 MySQL**，不能用内嵌 Derby |
| Driver | 解析 SQL → 生成执行计划 → 提交作业 | 核心调度层 |
| HiveServer2 | 提供 JDBC/ODBC 服务，允许多客户端连接 | 生产环境标配，配合 beeline 使用 |
| 计算引擎 | 执行实际的分布式计算 | 生产用 Tez 或 Spark，不要用 MR |

**面试话术**："Hive 的 Metastore 是整个系统的元数据中心，存储了表名、列类型、分区、数据在 HDFS 上的路径等信息。生产环境用 MySQL 存 Metastore，不能使用内嵌的 Derby，因为 Derby 不支持并发连接。"

## 三、数据类型

### 基本类型

```sql
-- 数值
TINYINT    -- 1 字节，-128~127
SMALLINT   -- 2 字节
INT        -- 4 字节
BIGINT     -- 8 字节
FLOAT      -- 单精度
DOUBLE     -- 双精度
DECIMAL(precision, scale)  -- 精确小数，金额必须用这个

-- 字符串
STRING     -- 最常用，无长度限制
VARCHAR(n) -- 变长字符串，有长度限制
CHAR(n)    -- 定长字符串

-- 日期时间
DATE       -- 日期，如 '2026-07-02'
TIMESTAMP  -- 时间戳，精确到纳秒

-- 布尔
BOOLEAN    -- TRUE/FALSE
```

### 复杂类型

```sql
-- ARRAY：一组相同类型的值
-- 如用户标签：['新用户', '高消费', '数码偏好']
CREATE TABLE user_tags (
    user_id INT,
    tags ARRAY<STRING>
);

-- 查询 ARRAY
SELECT tags[0] FROM user_tags;  -- 取第一个标签

-- MAP：键值对
-- 如用户属性：{'age': '25', 'city': '北京', 'level': 'vip'}
CREATE TABLE user_props (
    user_id INT,
    props MAP<STRING, STRING>
);
SELECT props['city'] FROM user_props;

-- STRUCT：一组命名字段（类似 C 的 struct）
CREATE TABLE order_info (
    order_id INT,
    address STRUCT<province:STRING, city:STRING, street:STRING>
);
SELECT address.city FROM order_info;
```

## 四、表类型（面试核心考点）

### 内部表 vs 外部表

**这是 Hive 面试最高频问题，必须能画图讲清楚。**

```sql
-- 内部表（Managed Table）：Hive 完全掌控数据
CREATE TABLE orders (
    order_id INT,
    amount DECIMAL(10,2)
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE;

-- 加载数据：数据移动到 Hive 仓库目录
LOAD DATA LOCAL INPATH '/home/data/orders.csv' INTO TABLE orders;

-- 外部表（External Table）：Hive 只管元数据，不管文件
CREATE EXTERNAL TABLE orders_ext (
    order_id INT,
    amount DECIMAL(10,2)
)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
LOCATION '/user/hive/external/orders/';  -- 指向 HDFS 已有目录

-- 区别：删除表时
DROP TABLE orders;       -- 内部表：元数据 + HDFS 数据全删
DROP TABLE orders_ext;   -- 外部表：只删元数据，HDFS 数据保留
```

| 对比维度 | 内部表 | 外部表 |
|---------|--------|--------|
| 数据归属 | Hive 独占管理 | 多个工具共享（Hive/Pig/Spark） |
| DROP 表 | 删除元数据 + 数据文件 | 只删除元数据，数据文件保留 |
| 数据位置 | 默认 `/user/hive/warehouse/` | 自定义 LOCATION |
| 适用场景 | 临时表、中间计算结果 | 原始日志、共享数据集 |
| 创建语句 | `CREATE TABLE` | `CREATE EXTERNAL TABLE` |

**面试话术**："内部表的数据由 Hive 全权管理，删除表时数据也删除。外部表只管理元数据，数据文件可以为多个工具共享。生产上原始数据用外部表（安全），中间计算结果用内部表（临时）。"

### 分区表（Partition）

```sql
-- 按日期分区：每个分区对应 HDFS 的一个子目录
CREATE TABLE orders_partitioned (
    order_id INT,
    user_id INT,
    amount DECIMAL(10,2)
)
PARTITIONED BY (dt STRING)  -- 分区列，不在数据文件中
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ',';

-- 加载数据到指定分区
LOAD DATA LOCAL INPATH '/data/orders_20260701.csv'
INTO TABLE orders_partitioned
PARTITION (dt='2026-07-01');

-- 查询时会自动分区裁剪，只扫描相关分区
SELECT SUM(amount) FROM orders_partitioned
WHERE dt BETWEEN '2026-07-01' AND '2026-07-07';
-- Hive 只扫描 7 个分区目录，跳过其他日期的数据

-- 查看分区
SHOW PARTITIONS orders_partitioned;

-- 添加分区
ALTER TABLE orders_partitioned ADD PARTITION (dt='2026-07-02');

-- 二级分区（按日期 + 城市）
CREATE TABLE orders_multi_part (
    order_id INT,
    amount DECIMAL(10,2)
)
PARTITIONED BY (dt STRING, city STRING);
-- HDFS 结构：/warehouse/orders/dt=2026-07-01/city=北京/
```

**面试话术**："分区表就是把数据按某个字段（通常是日期）分目录存储。查询时 WHERE 条件里有分区字段，Hive 就会只扫描相关目录，跳过无关数据，这就是分区裁剪（Partition Pruning）。这是 Hive 查询优化最基本的操作。"

### 分桶表（Bucket）

```sql
-- 分桶：按某列的 hash 值分文件
CREATE TABLE orders_bucketed (
    order_id INT,
    user_id INT,
    amount DECIMAL(10,2)
)
CLUSTERED BY (user_id) INTO 16 BUCKETS
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ',';

-- 写入数据前需要手动开启分桶
SET hive.enforce.bucketing = true;
```

### 分区 vs 分桶

| 对比 | 分区 | 分桶 |
|------|------|------|
| 数据结构 | 不同的目录 | 同一目录下不同的文件 |
| 划分方式 | 按列值（通常是日期） | 按列的 hash 值 |
| 查询优化 | 分区裁剪（减少扫描目录） | 分桶 JOIN（SMB Join） |
| 适用场景 | 按时间维度查询 | 大表 JOIN 大表、抽样查询 |
| 数量建议 | 不要超过 1000 个 | 一般 2 的 N 次方 |

**面试话术**："分区是按值分目录，用于减少扫描范围；分桶是按 hash 分文件，用于优化 JOIN 和抽样。分区太多会打爆 HDFS（小文件问题），建议分区数不超过 1000 个。"

## 五、HiveQL 基础

### DDL（数据定义）

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS dw;
USE dw;

-- 创建表（生产环境常用写法）
CREATE EXTERNAL TABLE dw.user_behavior (
    user_id         INT         COMMENT '用户ID',
    item_id         INT         COMMENT '商品ID',
    category_id     INT         COMMENT '品类ID',
    behavior        STRING      COMMENT '行为类型: pv/buy/cart/fav',
    behavior_time   BIGINT      COMMENT '行为时间戳'
)
COMMENT '用户行为日志表'
PARTITIONED BY (dt STRING)
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\n'
STORED AS ORC
TBLPROPERTIES ('orc.compress'='SNAPPY');

-- 修改表
ALTER TABLE user_behavior ADD COLUMNS (device_type STRING COMMENT '设备类型');
ALTER TABLE user_behavior CHANGE COLUMN device_type device STRING;
ALTER TABLE user_behavior RENAME TO user_behavior_bak;

-- 删除表
DROP TABLE IF EXISTS user_behavior_bak;
```

### DML（数据操作）

```sql
-- LOAD DATA：从本地或 HDFS 加载文件
LOAD DATA LOCAL INPATH '/home/data/user_behavior.csv'
OVERWRITE INTO TABLE user_behavior
PARTITION (dt='2026-07-02');

-- INSERT：从查询结果写入
-- 静态分区
INSERT OVERWRITE TABLE user_behavior
PARTITION (dt='2026-07-02')
SELECT user_id, item_id, category_id, behavior, behavior_time
FROM temp_behavior;

-- 动态分区
SET hive.exec.dynamic.partition = true;
SET hive.exec.dynamic.partition.mode = nonstrict;

INSERT OVERWRITE TABLE user_behavior
PARTITION (dt)
SELECT user_id, item_id, category_id, behavior, behavior_time, dt
FROM temp_behavior;

-- INSERT INTO（追加）vs INSERT OVERWRITE（覆盖）
INSERT INTO TABLE user_behavior PARTITION (dt='2026-07-02')
SELECT * FROM today_behavior;       -- 追加数据

INSERT OVERWRITE TABLE user_behavior PARTITION (dt='2026-07-02')
SELECT * FROM today_behavior;       -- 覆盖分区数据
```

### Hive vs 标准 SQL 差异

| 特性 | 标准 SQL (MySQL) | HiveQL |
|------|-----------------|--------|
| UPDATE/DELETE | 支持 | 不支持（或需开启事务） |
| 子查询 | 随处可用 | 只支持 FROM 中的子查询（需别名） |
| IN/EXISTS | 支持 | 0.13 后部分支持，推荐用 LEFT SEMI JOIN |
| 等值连接 | `=` | `=`，非等值连接有限制 |
| GROUP BY | 字段名或表达式 | 字段名或位置编号（Hive 0.11 后不推荐位置） |
| TOP/LIMIT | `LIMIT n` | `LIMIT n` |
| DISTINCT | 支持 | 支持，大表用 GROUP BY 效率更高 |

```sql
-- LEFT SEMI JOIN：替代 IN/EXISTS 子查询
-- 语义：返回左表中在右表有匹配的记录（只返回左表列，类似 IN）
SELECT a.*
FROM orders a
LEFT SEMI JOIN users b
ON a.user_id = b.user_id
WHERE b.vip_level > 3;
-- 等价于 SELECT * FROM orders WHERE user_id IN (
--     SELECT user_id FROM users WHERE vip_level > 3)
```

## 六、常用内置函数

### 聚合函数

```sql
-- 基础聚合
SELECT
    category_id,
    COUNT(*) AS cnt,
    COUNT(DISTINCT user_id) AS uv,             -- 去重计数
    SUM(amount) AS total_amount,
    AVG(amount) AS avg_amount,
    MAX(amount) AS max_amount,
    MIN(amount) AS min_amount,
    VARIANCE(amount) AS var_amount,            -- 方差
    STDDEV(amount) AS std_amount,              -- 标准差
    PERCENTILE_APPROX(amount, 0.5) AS median   -- 近似中位数
FROM orders
WHERE dt = '2026-07-02'
GROUP BY category_id;
```

### 字符串函数

```sql
SELECT
    -- 拼接
    CONCAT(user_id, '_', item_id) AS union_key,
    CONCAT_WS(',', col1, col2, col3) AS csv_line,  -- 指定分隔符拼接

    -- 分割
    SPLIT('a,b,c', ',') AS arr,                     -- ['a','b','c']

    -- 提取
    SUBSTR('Hello World', 1, 5) AS sub,             -- 'Hello'（从 1 开始）
    GET_JSON_OBJECT('{"name":"张三","age":25}', '$.name') AS name,  -- JSON 提取

    -- 查找替换
    INSTR('Hello World', 'World') AS pos,           -- 7（找不到返回 0）
    REGEXP_REPLACE('2026-07-02', '-', '') AS date_clean,  -- 正则替换 → '20260702'

    -- 条件与格式化
    NVL(amount, 0) AS amount_filled,                -- NULL 替换
    COALESCE(col1, col2, 0) AS first_not_null,      -- 第一个非空
    -- CASE WHEN：分段统计
    CASE WHEN amount < 50   THEN '低消费'
         WHEN amount < 200  THEN '中消费'
         WHEN amount < 500  THEN '高消费'
         ELSE '超高消费'
    END AS amount_level
FROM source_table;
```

### 日期函数

```sql
SELECT
    CURRENT_DATE,                             -- 当前日期 2026-07-02
    CURRENT_TIMESTAMP,                        -- 当前时间戳
    DATE_ADD('2026-07-02', 7) AS next_week,   -- '2026-07-09'
    DATE_SUB('2026-07-02', 7) AS last_week,   -- '2026-06-25'
    DATEDIFF('2026-07-02', '2026-06-25') AS diff,  -- 7（前减后）

    -- 时间戳转换（行为时间戳是秒级 → 日期）
    FROM_UNIXTIME(CAST(behavior_time AS BIGINT), 'yyyy-MM-dd') AS behavior_date,

    -- 提取日期部分
    YEAR('2026-07-02') AS year,
    MONTH('2026-07-02') AS month,
    DAY('2026-07-02') AS day,
    HOUR('2026-07-02 14:30:00') AS hour;

-- 常用：将时间戳转为具体日期
SELECT
    FROM_UNIXTIME(CAST(behavior_time AS BIGINT), 'yyyy-MM-dd') AS dt,
    COUNT(*) AS pv
FROM user_behavior
WHERE dt = '2026-07-02'
GROUP BY FROM_UNIXTIME(CAST(behavior_time AS BIGINT), 'yyyy-MM-dd');
```

### 窗口函数

Hive 支持完整窗口函数语法，但大表计算很慢，注意性能。

```sql
-- 示例：每品类按金额排名
SELECT
    category_id,
    order_id,
    amount,
    ROW_NUMBER()  OVER (PARTITION BY category_id ORDER BY amount DESC) AS rn,
    RANK()        OVER (PARTITION BY category_id ORDER BY amount DESC) AS rk,
    DENSE_RANK()  OVER (PARTITION BY category_id ORDER BY amount DESC) AS dr,
    SUM(amount)   OVER (PARTITION BY category_id) AS category_total,
    amount / SUM(amount) OVER (PARTITION BY category_id) AS ratio
FROM orders
WHERE dt = '2026-07-02';
```

### UDF 自定义函数

```sql
-- UDF：一进一出，如 UPPER/LOWER
-- UDAF：多进一出，如 SUM/COUNT
-- UDTF：一进多出，如 explode

-- explode 示例：展开 ARRAY
SELECT user_id, tag
FROM user_tags
LATERAL VIEW explode(tags) t AS tag;
-- 结果：user_id=101, tag='新用户'
--       user_id=101, tag='高消费'
--       user_id=101, tag='数码偏好'
```

```java
// 自定义 UDF（Java）
import org.apache.hadoop.hive.ql.exec.UDF;

public class ToUpperCase extends UDF {
    public String evaluate(String input) {
        if (input == null) return null;
        return input.toUpperCase();
    }
}
```

```sql
-- 注册使用
ADD JAR /path/to/my-udf.jar;
CREATE TEMPORARY FUNCTION my_upper AS 'com.example.ToUpperCase';
SELECT my_upper(user_name) FROM users;
```

## 七、数据导入导出

### 导入数据

```sql
-- 1. LOAD DATA：从文件加载（最快）
LOAD DATA LOCAL INPATH '/home/data/file.csv'
OVERWRITE INTO TABLE target_table
PARTITION (dt='2026-07-02');

-- 2. INSERT + SELECT：从查询结果加载
INSERT OVERWRITE TABLE target_table PARTITION (dt='2026-07-02')
SELECT col1, col2, col3 FROM source_table WHERE dt = '2026-07-02';

-- 3. CREATE TABLE AS SELECT (CTAS)
CREATE TABLE result_table AS
SELECT category_id, COUNT(*) AS cnt
FROM orders
GROUP BY category_id;
```

### 导出数据

```sql
-- 1. INSERT OVERWRITE DIRECTORY：导出到 HDFS/本地
INSERT OVERWRITE LOCAL DIRECTORY '/tmp/export/'
ROW FORMAT DELIMITED FIELDS TERMINATED BY ','
SELECT * FROM orders WHERE dt = '2026-07-02';

-- 2. hive -e 命令行重定向
-- $ hive -e "SELECT * FROM orders WHERE dt='2026-07-02'" > result.csv

-- 3. Sqoop：Hive ↔ RDBMS
-- 从 MySQL 导入到 Hive
-- sqoop import \
--   --connect jdbc:mysql://node1:3306/db \
--   --username root --password xxx \
--   --table orders \
--   --hive-import --hive-table dw.orders \
--   --hive-partition-key dt --hive-partition-value '2026-07-02' \
--   -m 4

-- 从 Hive 导出到 MySQL
-- sqoop export \
--   --connect jdbc:mysql://node1:3306/db \
--   --username root --password xxx \
--   --table report_daily \
--   --export-dir /user/hive/warehouse/dw.db/report/dt=2026-07-02/ \
--   -m 1
```

## 八、性能优化

### 1. 分区裁剪（最基本）

```sql
-- 差：全表扫描
SELECT * FROM orders;

-- 好：只扫描指定分区
SELECT * FROM orders WHERE dt = '2026-07-02';
```

### 2. 列裁剪

```sql
-- 差：读全部列
SELECT * FROM orders WHERE dt = '2026-07-02';

-- 好：只读需要的列（尤其 ORC/Parquet 格式效果明显）
SELECT order_id, amount FROM orders WHERE dt = '2026-07-02';
```

### 3. MapJoin（大表 JOIN 小表）

```sql
-- 普通 JOIN：Shuffle 大量数据
SELECT /*+ MAPJOIN(b) */ a.*, b.user_name
FROM orders a
JOIN users b ON a.user_id = b.user_id;

-- 手动开启
SET hive.auto.convert.join = true;
SET hive.mapjoin.smalltable.filesize = 25000000;  -- 25MB 以下的小表自动 MapJoin
```

**面试话术**："MapJoin 把小表加载到每个 Map 的内存中，在 Map 端完成 JOIN，避免了 Shuffle。条件是有一张表足够小（默认 25MB 以下），能放进内存。"

### 4. 存储格式选择

```sql
-- TEXTFILE：纯文本，压缩比低，查询慢
STORED AS TEXTFILE;

-- ORC：列式存储，压缩比高，查询快（生产推荐）
STORED AS ORC;
TBLPROPERTIES ('orc.compress'='SNAPPY');

-- Parquet：另一种列式存储，与 Spark 兼容性好
STORED AS PARQUET;
```

| 格式 | 压缩比 | 查询速度 | 适用场景 |
|------|--------|---------|---------|
| TEXTFILE | 无压缩 | 慢 | 临时数据、调试 |
| SEQUENCEFILE | 一般 | 中 | 已过时 |
| ORC | 高 | 快 | **Hive 首选** |
| Parquet | 高 | 快 | **Spark 首选** |

### 5. 数据倾斜处理

```sql
-- 现象：某个 key 的数据量远大于其他 key
-- 解决：
-- a) 单独处理倾斜 key
-- b) 加盐（加随机前缀分散到多个 Reduce）

-- 示例：GROUP BY 倾斜
SET hive.groupby.skewindata = true;
-- Hive 会启动两轮 MR 作业：第一轮随机分发打散，第二轮真聚合

-- JOIN 倾斜：单独处理
SELECT * FROM orders a JOIN users b
ON a.user_id = b.user_id
WHERE a.user_id != 'hot_key'   -- 正常数据

UNION ALL

SELECT * FROM orders a
JOIN (SELECT * FROM users UNION ALL SELECT 'hot_key' AS user_id) b
ON a.user_id = b.user_id
WHERE a.user_id = 'hot_key';   -- 倾斜 key 单独处理（用 MapJoin）
```

### 优化清单速查

| 优先级 | 方法 | 效果 |
|--------|------|------|
| 1 | **加分区过滤**（WHERE dt = '...'） | 极大减少扫描量 |
| 2 | **用列式存储**（ORC/Parquet + SNAPPY） | 减少 IO + 快速读 |
| 3 | **小表 JOIN 用 MapJoin** | 避免 Shuffle |
| 4 | **只 SELECT 需要的列** | 减少 IO |
| 5 | **用 Tez/Spark 引擎替代 MR** | 2-10 倍提升 |
| 6 | **开启向量化执行** | 批量处理，提速 2-3 倍 |
| 7 | **处理数据倾斜**（加盐/分步聚合） | 消除长尾任务 |

## 九、面试高频考点

### 考点 1：内部表 vs 外部表

**问题**："内部表和外部表有什么区别？什么时候用哪种？"

**回答**：内部表数据由 Hive 全权管理，DROP 表时数据也删除。外部表只管元数据，数据可以共享，DROP 不影响数据。生产上：原始数据用外部表（安全，不怕误删），ETL 中间结果和报表用内部表。

### 考点 2：分区 vs 分桶

**问题**："分区和分桶有什么区别？分别解决什么问题？"

**回答**：分区是按列值（通常是日期）分目录存储，目的是减少扫描范围（分区裁剪）。分桶是按列的 hash 值分文件存储，目的是优化大表 JOIN（SMB Join）和抽样查询。分区数不要超过 1000，分桶数一般 2 的 N 次方。

### 考点 3：数据倾斜

**问题**："Hive 查询出现数据倾斜怎么办？"

**回答**：先确认是哪个环节倾斜（GROUP BY 或者 JOIN）。GROUP BY 倾斜用 `hive.groupby.skewindata=true` 两阶段聚合。JOIN 倾斜把大 key 单独拆出来用 MapJoin 处理，或者给 key 加随机盐分散到多个 Reduce。

### 考点 4：Hive 为什么慢

**问题**："为什么 Hive 查询这么慢？怎么优化？"

**回答**：根本原因是 Hive 底层是 MapReduce，启动开销大。优化方向：1) 用 ORC/Parquet 列式存储，2) 分区裁剪，3) 用 Tez/Spark 引擎替代 MR，4) 开 Vectorization，5) MapJoin 代替 Common Join，6) 处理数据倾斜。

### 考点 5：Hive vs Spark SQL

**问题**："Hive 和 Spark SQL 有什么区别？为什么 Spark 更快？"

**回答**：Hive 默认基于 MapReduce，中间结果落盘，迭代计算慢。Spark 基于内存计算，中间结果在内存中传递，对多轮迭代场景（如机器学习）快几十倍。但 Hive 的 SQL 生态更成熟，很多企业仍然用 Hive 做 ETL，Spark SQL 做复杂分析。

## 相关笔记

- [[工作学习/数据库与SQL/SQL查询优化|SQL 查询优化]] — 索引、最左前缀、执行计划
- [[工作学习/数据库与SQL/窗口函数实战|窗口函数实战]] — ROW_NUMBER/RANK/LAG，Hive 也支持
- [[工作学习/数据库与SQL/常见业务SQL场景|常见业务 SQL 场景]] — 留存率、复购率等业务 SQL，可以移植到 Hive
- [[工作学习/大数据技术/Spark基础|Spark 基础]] — Spark 与 Hive 的对比和互补
- [[工作学习/大数据技术/HBase基础|HBase 基础]] — HBase 补位 Hive 的实时查询短板
