---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/hbase"
  - "#技术/大数据"
  - "#状态/已验证"
created: 2026-07-02
updated: 2026-07-15
status: reviewed
---

# HBase 基础

> 基于 HDFS 的分布式列式 NoSQL 数据库，毫秒级随机读写。RowKey 设计是面试重点。 | **面试重要度：中** | 预计阅读：15 分钟

## 视频资源

- YouTube: [HBase Tutorial for Beginners](https://www.youtube.com/watch?v=J6oY1xNqRIA) — HBase 原理最直观的解释
- B站: [尚硅谷 HBase 教程](https://www.bilibili.com/video/BV1Y4411B7Jy/) — 中文 HBase 入门首选

**一句话理解**：HBase = HDFS 做存储 + 内存做缓存 + LSM 树做写入优化 + RowKey 做索引。适合海量数据的随机读写和实时查询。

## 一、HBase 在生态中的位置

```
┌──────────────────────────────────────────────┐
│              业务层 / 服务层                    │
│   Hive (离线分析)    Spark (计算)              │
│   Phoenix (SQL 查询 HBase)                    │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│               HBase（实时读写层）               │
│   毫秒级随机读写，适用于海量数据的点查和范围扫描   │
└──────────────────┬───────────────────────────┘
                   │
┌──────────────────▼───────────────────────────┐
│          HDFS（分布式文件系统，持久化存储）       │
└──────────────────────────────────────────────┘
```

| 场景 | 适用工具 | 原因 |
|------|---------|------|
| 离线日报、ETL | Hive | 批处理，不要求实时 |
| 复杂分析、机器学习 | Spark | 内存计算，迭代快 |
| 实时点查（某用户的所有订单） | **HBase** | RowKey 索引，毫秒级返回 |
| 全文搜索 | Elasticsearch | 倒排索引 |
| OLTP 事务 | MySQL | ACID 事务支持 |

## 二、HBase 数据模型

**这是面试的必问到内容——必须能画出 HBase 的存储结构。**

### 核心概念

```
HBase 表 = 排序的 Map<RowKey, Map<ColumnFamily, Map<ColumnQualifier, Map<Timestamp, Value>>>>
```

但面试时这样说太抽象了，用实际例子讲：

```
想象一张用户表 user：

RowKey: user_101
├── ColumnFamily: info（基本信息）
│   ├── info:name    → @ts=3  "张三"
│   ├── info:age     → @ts=3  "25"
│   └── info:city    → @ts=2  "北京"
│                    → @ts=1  "上海"    ← 旧版本保留
├── ColumnFamily: order（订单信息）
│   ├── order:total  → @ts=3  "5000.00"
│   └── order:last   → @ts=3  "2026-07-01"
```

### 四个核心组件

| 组件 | 说明 | 类比 |
|------|------|------|
| **RowKey** | 行的唯一标识，按字典序排序 | MySQL 的主键，但决定了物理存储顺序 |
| **Column Family** | 列族，物理上分开存储 | 表的"子表"，影响 IO 性能 |
| **Column Qualifier** | 列限定符，列族下面的具体列 | MySQL 的列名 |
| **Timestamp** | 版本号，每个值保留多个版本 | 数据版本控制 |

### 关键特性

1. **稀疏性**：空列不占空间，不同行可以有完全不同的列
2. **多版本**：每个 Cell 可以保留多个时间戳版本（默认 3 个）
3. **排序**：RowKey 按字典序排列，扫描时按序返回
4. **列族设计**：列族在物理上是分开存储的，不要超过 2-3 个

```bash
# HBase Shell 中创建表，指定列族
hbase(main):001:0> create 'user', {NAME => 'info', VERSIONS => 3}, {NAME => 'order', VERSIONS => 1}

# 查看表
hbase(main):002:0> describe 'user'
# Table user is ENABLED
# COLUMN FAMILIES DESCRIPTION
# {NAME => 'info', VERSIONS => '3', ...}
# {NAME => 'order', VERSIONS => '1', ...}
```

## 三、HBase 架构

```
┌──────────────────────────────────────────────────────┐
│                    ZooKeeper 集群                      │
│   存储元数据位置（meta 表在哪个 RegionServer 上）        │
│   保证任何时候只有一个活跃的 HMaster                     │
└───────┬──────────────────────────────┬───────────────┘
        │                              │
┌───────▼────────┐            ┌───────▼────────┐
│   HMaster      │            │   HMaster      │
│  (Active)      │            │  (Standby)     │
│ 建表/删表/      │            │  故障时切换      │
│ 负载均衡/       │            │                │
│ Region 分配    │            │                │
└───────┬────────┘            └────────────────┘
        │ 管理 Region 分配
┌───────┼──────────────────────────────────────┐
│       │        RegionServer 集群              │
│  ┌────▼──────────────────────────────────┐   │
│  │ RegionServer 1                        │   │
│  │  ┌─────────┐    ┌─────────┐          │   │
│  │  │ Region  │    │ Region  │          │   │
│  │  │ user,   │    │ user,  │          │   │
│  │  │ a~m     │    │ n~z    │          │   │
│  │  │         │    │         │          │   │
│  │  │┌───────┐│    │┌───────┐│          │   │
│  │  ││Store  ││    ││Store  ││          │   │
│  │  ││MemStore│    ││MemStore│          │   │
│  │  │├───────┤│    │├───────┤│          │   │
│  │  ││HFile  ││    ││HFile  ││          │   │
│  │  ││HFile  ││    ││HFile  ││          │   │
│  │  │└───────┘│    │└───────┘│          │   │
│  │  └─────────┘    └─────────┘          │   │
│  └──────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
        │
┌───────▼──────────────────────────────────────┐
│                  HDFS                         │
│   HFile 最终的持久化存储，利用 HDFS 副本机制     │
└──────────────────────────────────────────────┘
```

**核心角色**：

| 角色 | 职责 | 备注 |
|------|------|------|
| **ZooKeeper** | 存储 meta 表位置、HMaster 选举 | HBase 的神经中枢 |
| **HMaster** | 建表删表、Region 分配、负载均衡 | 不处理数据读写 |
| **RegionServer** | 处理客户端的读写请求、管理 Region | 真正的干活的 |
| **Region** | 表的水平分片（按 RowKey 范围） | 类似 MySQL 分库分表的分片 |
| **Store** | 一个 Region 里一个列族的数据 | MemStore + 多个 HFile |
| **MemStore** | 写缓存（内存） | 写先到这里，满了刷成 HFile |
| **HFile** | 持久化的排序文件 | 存在 HDFS 上，不可变 |

**面试话术**："HMaster 只管元数据操作（建表、删表、Region 分配），不处理读写。客户端的读写直接和 RegionServer 通信，ZooKeeper 告诉客户端 meta 表在哪个 RegionServer 上，meta 表再告诉它目标 RowKey 在哪个 RegionServer。"

### 数据写入流程

```
Client → ZooKeeper（找 meta 表位置）
      → RegionServer of meta table（找目标 RowKey 在哪个 RegionServer）
      → 目标 RegionServer
        → 先写 WAL（Write-Ahead Log，预写日志，HDFS）
        → 再写 MemStore（写缓存，内存）
        → 返回写入成功（MemStore 满了就刷到 HFile）
```

**面试话术**："HBase 写数据时先写 WAL 保证不丢数据，再写 MemStore 返回成功。MemStore 满了或手动 flush 时，排序后写入 HFile。因为 HFile 是不可变的，所以 HBase 没有随机更新，只有追加——这是 LSM 树的核心思想。"

### 数据读取流程

```
Client → ZooKeeper → meta 表 → 目标 RegionServer
  → 同时查 MemStore + BlockCache + HFile
    → 合并结果（所有 HFile 的结果可能都有部分数据）
    → 按时间戳取最新版本
    → 返回
```

## 四、RowKey 设计（面试核心）

**RowKey 设计是 HBase 使用的关键——决定了数据分布和查询效率。**

### 设计原则

| 原则 | 说明 | 为什么 |
|------|------|--------|
| **散列性** | RowKey 要均匀分布在各个 Region | 避免热点（某台机器被打爆） |
| **长度适中** | 一般 16-64 字节 | 太短信息少，太长浪费空间 |
| **唯一性** | 每行有唯一 RowKey | 重复会覆盖 |
| **查询优先** | RowKey 里包含常用查询条件 | HBase 只能高效查 RowKey |

### 避免热点的方法

```bash
# ❌ 坏设计：直接用递增的订单 ID 做 RowKey
# 新订单都在最新的一个 Region 上 → 热点
10001, 10002, 10003, ...

# ✅ 方案 1：Hash 前缀
# 取 user_id 的 hash 值前 4 位做前缀，打散到多个 Region
# RowKey = hash(user_id)[0:4] + '_' + user_id + '_' + timestamp
a3f2_U1001_20260701120000, 7b81_U1002_20260701120000, ...

# ✅ 方案 2：反转
# 把递增的 ID 反转，让相近 ID 分散到不同 Region
# RowKey = reverse(order_id)
10001→10001, 10002→20001, 10003→30001

# ✅ 方案 3：加盐（Salt）
# RowKey = salt + user_id + timestamp
# salt = random(0, n-1)，后面查的时候要遍历 n 个分区
```

### 设计实例

```bash
# 场景：用户行为表，需要查询
#   1. 某个用户在某个时间段的行为（高频）
#   2. 某个时间段的所有用户行为（偶尔）

# RowKey 设计：hash(user_id)[0:4] + user_id + (Long.MAX_VALUE - timestamp)
# 设计理由：
#   - hash 前缀散列避免热点
#   - user_id 放前面，方便按用户范围扫描
#   - 时间戳取反（Long.MAX_VALUE - ts），同一用户内时间从新到旧排列

# 创建表并预分区
create 'user_behavior',
  {NAME => 'info', VERSIONS => 1, COMPRESSION => 'SNAPPY'},
  {SPLITS => [
    '0000|', '1000|', '2000|', '3000|', '4000|',
    '5000|', '6000|', '7000|', '8000|', '9000|'
  ]}
```

**面试话术**："RowKey 设计的第一原则是散列性——避免热点。常用方法是用 Hash 前缀或加盐让数据均匀分布。第二原则是业务查询优先——把常用的查询条件编码到 RowKey 里，因为 HBase 高效查询只支持 RowKey 的精确查询和范围扫描。"

## 五、基本操作

### Shell 命令

```bash
# 进入 Shell
hbase shell

# ===== DDL =====
# 查看所有表
list

# 创建表（指定列族）
create 'student', 'info', 'score'

# 创建表（详细配置）
create 'student',
  {NAME => 'info', VERSIONS => 5, COMPRESSION => 'SNAPPY', BLOCKCACHE => true},
  {NAME => 'score', VERSIONS => 1, COMPRESSION => 'SNAPPY'}

# 查看表结构
describe 'student'

# 禁用/启用/删除表
disable 'student'
enable 'student'
drop 'student'                 # 删除前需先 disable

# 修改表（添加列族）
alter 'student', {NAME => 'address', VERSIONS => 1}

# ===== DML =====
# 插入/更新（Put）
put 'student', '1001', 'info:name', '张三'
put 'student', '1001', 'info:age', '20'
put 'student', '1001', 'score:math', '95'
put 'student', '1001', 'score:english', '88'

# 读取一行（Get）
get 'student', '1001'
get 'student', '1001', 'info'           # 只读 info 列族
get 'student', '1001', 'info:name'      # 只读 name 列
get 'student', '1001', {COLUMN => 'info:name', VERSIONS => 3}  # 读 3 个版本

# 扫描（Scan）
scan 'student'                           # 全表扫描（慎用）
scan 'student', {COLUMNS => ['info:name', 'info:age']}
scan 'student', {STARTROW => '1001', STOPROW => '1005'}

# 删除数据
delete 'student', '1001', 'info:name'   # 删除指定 Cell
deleteall 'student', '1001'              # 删除整行

# 计数
count 'student'

# 清空表
truncate 'student'                       # = disable + drop + create
```

### Java API（面试常问）

```java
import org.apache.hadoop.hbase.*;
import org.apache.hadoop.hbase.client.*;
import org.apache.hadoop.hbase.util.Bytes;

Configuration conf = HBaseConfiguration.create();
conf.set("hbase.zookeeper.quorum", "node1,node2,node3");

// 建立连接
Connection conn = ConnectionFactory.createConnection(conf);
Table table = conn.getTable(TableName.valueOf("student"));

// ===== Put：插入/更新 =====
Put put = new Put(Bytes.toBytes("1001"));
put.addColumn(Bytes.toBytes("info"), Bytes.toBytes("name"), Bytes.toBytes("张三"));
put.addColumn(Bytes.toBytes("info"), Bytes.toBytes("age"), Bytes.toBytes("20"));
table.put(put);

// ===== Get：读取一行 =====
Get get = new Get(Bytes.toBytes("1001"));
get.addFamily(Bytes.toBytes("info"));
Result result = table.get(get);
// 遍历结果
for (Cell cell : result.rawCells()) {
    String family = Bytes.toString(CellUtil.cloneFamily(cell));
    String qualifier = Bytes.toString(CellUtil.cloneQualifier(cell));
    String value = Bytes.toString(CellUtil.cloneValue(cell));
    System.out.println(family + ":" + qualifier + " = " + value);
}

// ===== Scan：范围扫描 =====
Scan scan = new Scan();
scan.withStartRow(Bytes.toBytes("1001"));
scan.withStopRow(Bytes.toBytes("1005"), true);  // 包含 1005
scan.addColumn(Bytes.toBytes("info"), Bytes.toBytes("name"));

ResultScanner scanner = table.getScanner(scan);
for (Result r : scanner) {
    String row = Bytes.toString(r.getRow());
    String name = Bytes.toString(r.getValue(
        Bytes.toBytes("info"), Bytes.toBytes("name")));
    System.out.println(row + " -> " + name);
}
scanner.close();

// ===== Delete =====
Delete del = new Delete(Bytes.toBytes("1001"));
del.addColumn(Bytes.toBytes("info"), Bytes.toBytes("name"));
table.delete(del);

table.close();
conn.close();
```

## 六、HBase vs MySQL vs Redis

| 对比维度 | HBase | MySQL | Redis |
|---------|-------|-------|-------|
| 数据规模 | PB 级 | TB 级 | GB 级（受内存限制） |
| 数据模型 | 列式，稀疏 | 关系型 | Key-Value + 多种数据结构 |
| 查询方式 | RowKey 精确查/范围扫描 | SQL | Key 精确查 |
| 事务 | 行级原子性 | ACID | 有限事务（MULTI/EXEC） |
| 持久化 | HDFS（多副本） | 磁盘 | RDB 快照 + AOF 日志 |
| 扩展 | 水平扩展（加节点） | 垂直扩展为主 | 集群模式支持 |
| 写入速度 | 快（顺序写 + 内存） | 中 | 极快（纯内存） |
| 读取延迟 | ms 级 | ms 级 | us 级 |
| 适用场景 | 海量日志、用户画像、时序数据 | 订单系统、用户系统 | 缓存、排行榜、分布式锁 |

## 七、与 Hadoop/Hive/Spark 集成

```sql
-- Hive 中创建映射到 HBase 的外部表
CREATE EXTERNAL TABLE hbase_student(
    id INT,
    name STRING,
    age INT,
    math_score INT,
    english_score INT
)
STORED BY 'org.apache.hadoop.hive.hbase.HBaseStorageHandler'
WITH SERDEPROPERTIES (
    "hbase.columns.mapping" = ":key,info:name,info:age,score:math,score:english"
)
TBLPROPERTIES ("hbase.table.name" = "student");

-- 现在可以直接用 Hive SQL 查询 HBase 数据
SELECT id, name, math_score FROM hbase_student WHERE id = 1001;
-- 按 RowKey 范围查（利用 HBase 的 scan）
SELECT * FROM hbase_student WHERE id BETWEEN 1001 AND 2000;
```

```python
# Spark 读写 HBase
# 需要在 Spark 配置中加入 HBase 连接信息
# 或者使用 Spark-HBase 连接器（shc）

# 读取 HBase 数据到 Spark DataFrame
df = spark.read \
    .format("org.apache.hadoop.hbase.spark") \
    .option("hbase.table", "student") \
    .option("hbase.columns.mapping",
            "id STRING :key, name STRING info:name, age INT info:age") \
    .load()
df.show()

# 将 Spark DataFrame 写入 HBase
user_report.write \
    .format("org.apache.hadoop.hbase.spark") \
    .option("hbase.table", "user_report") \
    .option("hbase.columns.mapping",
            "user_id STRING :key, total DECIMAL info:total, level STRING info:level") \
    .mode("overwrite") \
    .save()
```

## 八、LSM 树原理（面试加分项）

HBase 写入快的根本原因是 **LSM 树**（Log-Structured Merge Tree）。

```
写入流程：
  Write → WAL(磁盘顺序写，恢复用) → MemStore(内存排序) → 返回成功
                                     ↓ (满了 128MB)
                                     Flush → HFile(有序，不可变)
                                     ↓ (小文件多了)
                                     Minor Compaction(合并几个 HFile)
                                     ↓ (大文件多了)
                                     Major Compaction(合并所有 HFile)

读取流程：
  Read → 查 MemStore → 查 BlockCache(读缓存) → 查所有 HFile
          → 拿到所有版本 → 按 timestamp 取最新 → 返回
```

**LSM vs B+ 树（MySQL InnoDB）**：

| 对比 | LSM 树（HBase） | B+ 树（MySQL InnoDB） |
|------|----------------|----------------------|
| 写性能 | **极好**：顺序写 + 批量刷盘 | 一般：随机写（需找位置） |
| 读性能 | 需要合并多个文件 | 读一条数据路径短 |
| 空间放大 | 有（旧版本等待 GC） | 较小 |
| 适合场景 | 写多读少（日志、时序） | 读写均衡（OLTP） |

**面试话术**："HBase 底层用 LSM 树，写入是顺序追加到内存，满了批量排序刷盘，所以写入极快。读取时需要合并内存和多个文件的结果，这也是为什么 HBase 的读比写慢。LSM 树通过牺牲部分读性能来换取极致的写性能，非常适合写多读少的场景。"

## 九、面试高频考点

### 考点 1：RowKey 设计

**问题**："HBase 的 RowKey 怎么设计？有哪些原则？"

**回答**：核心原则是散列 + 业务查询优先。散列（Hash 前缀、反转、加盐）是为了避免热点 Region。业务查询优先是因为 HBase 高效查询只有 RowKey 精确查和范围扫描两种方式，不按 RowKey 的查询只能全表扫描或用二级索引（Phoenix）。

### 考点 2：HBase 数据模型

**问题**："画出 HBase 的数据模型，RowKey / ColumnFamily / Column / Timestamp 分别是什么？"

**回答**：RowKey 是主键，决定了物理存储顺序。Column Family 是列族，物理上分开存储，建议不超过 2-3 个。Column Qualifier 是列族下的具体列，可以动态增删。Timestamp 是版本号，每个值可以保留多个版本。

### 考点 3：LSM 树

**问题**："为什么 HBase 写入这么快？什么是 LSM 树？"

**回答**：LSM 树把随机写变成顺序写——先写内存（MemStore），满了再批量排序刷盘（HFile）。缺点是读的时候要合并多个文件的结果，所以 HBase 是写快读慢的设计。适合写多读少的场景（日志、时序数据）。

### 考点 4：HBase 架构

**问题**："HMaster 挂掉会影响读写吗？"

**回答**：不会。HMaster 只负责元数据管理（建表、删表、Region 分配），不影响数据读写。读写是客户端直接和 RegionServer 交互，通过 ZooKeeper 定位 meta 表即可，不经过 HMaster。所以 HMaster 挂掉不影响在线服务，只是不能建表删表。

### 考点 5：HBase vs Hive

**问题**："HBase 和 Hive 有什么区别？什么场景用哪个？"

**回答**：Hive 是数据仓库，做离线批量分析，SQL 转分布式计算，延迟秒级起步。HBase 是 NoSQL 数据库，用 RowKey 做毫秒级的点查和范围扫描。通常用 Hive 做日报和周度分析，用 HBase 做实时的用户画像查询和日志检索。

## 相关笔记

- [[工作学习/大数据技术/Hive基础|Hive 基础]] — Hive 做离线分析，HBase 做实时查询，两者互补
- [[工作学习/大数据技术/Spark基础|Spark 基础]] — Spark 可以读写 HBase 数据
- [[工作学习/数据库与SQL/SQL查询优化|SQL 查询优化]] — MySQL 对比 HBase 的 B+ 树 vs LSM 树
- [[工作学习/统计学基础/概率分布基础|概率分布基础]] — Hash 散列原理可以联想到均匀分布
