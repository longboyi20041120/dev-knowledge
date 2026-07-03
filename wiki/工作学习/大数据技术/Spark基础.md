---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/spark"
  - "#技术/大数据"
  - "#状态/草稿"
created: 2026-07-02
updated: 2026-07-02
status: draft
---

# Spark 基础

Spark 是 UC Berkeley AMPLab 开源的**基于内存的分布式计算引擎**。核心卖点：比 Hadoop MapReduce 快 10-100 倍，因为中间结果在内存中传递，不需要频繁读写 HDFS。

**一句话理解**：Spark = 更快的 MapReduce + SQL + 流处理 + 机器学习 + 图计算，一套引擎打天下。

## 一、为什么需要 Spark：MapReduce 的痛点

面试时先讲清楚"为什么会有 Spark"——MapReduce 有什么问题？

```
MapReduce 的执行过程：
Map → Shuffle(落盘) → Reduce → 下一轮 Map → Shuffle(落盘) → Reduce...

Spark 的执行过程：
Stage1 在内存中完成 → Stage2 在内存中完成 → ...只在必要时落盘
```

| 对比 | Hadoop MapReduce | Spark |
|------|-----------------|-------|
| 计算模型 | 仅 Map 和 Reduce | 丰富的算子（map/filter/join/groupBy...） |
| 中间结果 | 落 HDFS（慢） | 内存中传递（快） |
| 迭代计算 | 每轮独立启动作业（极慢） | DAG 一次性调度（快） |
| 适用场景 | 简单 ETL、排序 | 复杂分析、机器学习、流处理 |
| 编程语言 | Java | Scala/Python/R/Java/SQL |
| 交互式查询 | 不支持 | Spark Shell、Spark SQL |

**面试话术**："MapReduce 的核心问题是中间结果必须落盘，导致迭代计算（如梯度下降）每一轮都要重新启动作业。Spark 把中间结果缓存在内存中，用 DAG 调度器一次性规划好整个计算流程，避免了重复的磁盘 IO 和作业启动开销。"

## 二、Spark 架构

```
┌─────────────────────────────────────────────┐
│              Driver Program                 │
│  (main() + SparkContext/SparkSession)       │
│  解析用户代码 → 生成 DAG → 调度 Task         │
└──────────────────┬──────────────────────────┘
                   │ 申请资源
┌──────────────────▼──────────────────────────┐
│          Cluster Manager（集群管理器）        │
│  Standalone / YARN / Mesos / Kubernetes     │
└──────────────────┬──────────────────────────┘
                   │ 分配资源
    ┌──────────────┼──────────────┐
    ▼              ▼              ▼
┌────────┐  ┌────────┐  ┌────────┐
│Worker  │  │Worker  │  │Worker  │
│Executor│  │Executor│  │Executor│
│ Task   │  │ Task   │  │ Task   │
│ Task   │  │ Task   │  │ Task   │
└────────┘  └────────┘  └────────┘
```

**核心组件**：

| 组件 | 角色 | 说明 |
|------|------|------|
| Driver | 大脑 | 把用户代码转为逻辑计划 → 物理计划 → Task，调度执行 |
| Executor | 手脚 | 在 Worker 节点上执行 Task，缓存数据，返回结果 |
| Cluster Manager | 调度器 | YARN/Mesos/K8s/Standalone，管理集群资源 |
| Job | 一次完整的计算 | 每次 action 操作触发一个 Job |
| Stage | Job 的子阶段 | 以 Shuffle 为边界划分 |
| Task | 最小执行单元 | 一个 Stage 内并行执行的任务数 |

## 三、RDD（弹性分布式数据集）

RDD 是 Spark 最核心的抽象，面试**必须**讲清楚。

### 什么是 RDD

- **弹性（Resilient）**：数据丢失可自动重建（通过血统 lineage）
- **分布式（Distributed）**：数据分布在集群多个节点上
- **数据集（Dataset）**：不可变的、分区的数据集合

### RDD 的五大特性

1. **分区列表**：每个 RDD 有一组分区，是并行计算的基本单位
2. **计算函数**：对每个分区执行的计算操作
3. **依赖关系**：记录父 RDD，形成血统（lineage）
4. **分区器（可选）**：Key-Value RDD 如何分区（Hash/ Range）
5. **优先位置（可选）**：数据在哪台机器上，尽量本地计算

### 转换（Transformation）vs 行动（Action）

**这是 RDD 编程的核心概念——延迟执行（Lazy Evaluation）。**

```python
from pyspark import SparkContext
sc = SparkContext("local", "WordCount")

text_file = sc.textFile("hdfs://node1:9000/data/words.txt")

# ===== 转换（Transformation）：延迟，不立即执行 =====
# 只记录计算逻辑，不触发实际计算
words = text_file.flatMap(lambda line: line.split(" "))     # 每行→单词
word_pairs = words.map(lambda word: (word, 1))              # 每个单词→(word, 1)

# ===== 行动（Action）：触发真正的计算 =====
# 触发 DAG 调度，开始执行
word_counts = word_pairs.reduceByKey(lambda a, b: a + b)    # 按 key 聚合
result = word_counts.collect()                               # Action！收集结果
print(result)
```

**面试话术**："RDD 的转换是惰性的——map、filter、flatMap 等操作只记录计算逻辑，不真正执行。只有遇到 Action（collect、count、saveAsTextFile）才会触发计算。这样做的好处是 Spark 可以先看到完整的计算图，做全局优化后再执行。"

### 常用 Transformation

```python
# map：每个元素应用函数，1:1
rdd.map(lambda x: x * 2)                    # [1,2,3] → [2,4,6]

# flatMap：每个元素→0到多个元素，1:N
rdd.flatMap(lambda x: x.split(" "))          # ["Hello World"] → ["Hello","World"]

# filter：保留满足条件的元素
rdd.filter(lambda x: x > 0)                 # [1,-1,3] → [1,3]

# distinct：去重（慎用，触发 Shuffle）
rdd.distinct()

# union：合并两个 RDD（不去重，无 Shuffle）
rdd1.union(rdd2)

# intersection：交集（触发 Shuffle）
rdd1.intersection(rdd2)

# groupByKey：按 key 分组（性能差，用 reduceByKey 替代）
rdd.groupByKey()                            # ❌ 大数据耗时
rdd.reduceByKey(lambda a, b: a + b)         # ✅ 先局部聚合再 shuffle

# reduceByKey vs groupByKey：
# reduceByKey：Map 端先局部聚合 → Shuffle 数据量小
# groupByKey：所有数据无脑 Shuffle → 数据量大

# sortBy / sortByKey：排序（触发 Shuffle）
rdd.sortBy(lambda x: x[1], ascending=False)

# join / leftOuterJoin / rightOuterJoin（触发 Shuffle）
rdd1.join(rdd2)                             # JOIN 两个 K-V RDD
```

### 常用 Action

```python
rdd.collect()            # 将所有数据收集到 Driver（慎用，可能 OOM）
rdd.count()              # 计数
rdd.first()              # 取第一条
rdd.take(10)             # 取前 10 条（比 collect 安全）
rdd.top(10)              # 取最大的 10 条
rdd.reduce(lambda a, b: a + b)  # 聚合
rdd.saveAsTextFile("hdfs://...")  # 保存到 HDFS
rdd.foreach(lambda x: print(x))  # 对每个元素执行操作
```

### 窄依赖 vs 宽依赖（面试必问）

```
窄依赖（Narrow Dependency）：一个父 RDD 的 partition 最多被一个子 RDD partition 使用
  map / filter / union / mapPartitions

宽依赖（Wide Dependency / Shuffle）：一个父 RDD 的 partition 被多个子 RDD partition 使用
  groupByKey / reduceByKey / join / sortByKey
```

| 对比维度 | 窄依赖 | 宽依赖 |
|---------|--------|--------|
| 数据流动 | 1 对 1 | 1 对 多（Shuffle） |
| 计算位置 | Pipeline 执行，不需要等 | 必须等父阶段全部完成 |
| 故障恢复 | 只丢失的分区重算 | 可能需要整个父阶段重算 |
| Stage 划分 | 在一个 Stage 内 | 产生新的 Stage |

**面试话术**："窄依赖和宽依赖的核心区别是是否发生 Shuffle。窄依赖的子 RDD 分区只依赖一个父分区，可以在一个 Stage 内流水线执行。宽依赖需要跨节点传输数据，Spark 会在这里切分 Stage，等宽依赖前的所有 Task 完成后才开始下一个 Stage。"

## 四、DataFrame / Dataset

RDD 是底层 API，DataFrame 和 Dataset 是高层次 API（Spark SQL 的基础）。

```python
from pyspark.sql import SparkSession

# SparkSession 是入口（包含了 SparkContext、SQLContext）
spark = SparkSession.builder \
    .appName("DataFrameExample") \
    .master("local[*]") \
    .getOrCreate()

# 从各种数据源创建 DataFrame
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("hdfs://node1:9000/data/orders.csv")

# 常见操作
df.show(5)                     # 预览前 5 行
df.printSchema()               # 打印 Schema
df.select("user_id", "amount") # 选列
df.filter(df.amount > 100)     # 过滤
df.groupBy("category").agg({"amount": "sum"})  # 分组聚合
df.orderBy(df.amount.desc())   # 排序
df.withColumn("amount2", df.amount * 2)  # 新增列
df.dropDuplicates(["user_id"]) # 按列去重
```

### RDD vs DataFrame vs Dataset

| 对比维度 | RDD | DataFrame | Dataset |
|---------|-----|-----------|---------|
| API 风格 | 函数式（map/filter） | 声明式（SQL 风格） | 两者皆可 |
| 编译时类型安全 | 有（Scala） | 无（知道列名，不知道类型） | 有 |
| 性能优化 | 无（手动优化） | Catalyst 优化器自动优化 | Catalyst 优化器 |
| 序列化 | Java/Kryo | Tungsten 二进制格式 | Tungsten 编码器 |
| Spark SQL | 不直接支持 | 直接支持 | 直接支持 |
| 使用建议 | 底层操作、非结构化数据 | **Python 用户首选** | Scala/Java 用户首选 |

**面试话术**："DataFrame 是不带类型信息的、以列组织的分布式数据集合，底层有 Catalyst 优化器和 Tungsten 执行引擎加持，比 RDD 快。Dataset 是带类型的 DataFrame（Scala/Java 中有，Python 没有）。Python 环境下直接用 DataFrame。"

## 五、Spark SQL 实战

### 读多种数据源

```python
# CSV
df = spark.read.csv("file.csv", header=True, inferSchema=True)

# JSON
df = spark.read.json("file.json")

# Parquet（列存，推荐）
df = spark.read.parquet("file.parquet")

# ORC
df = spark.read.orc("file.orc")

# JDBC（直连数据库）
df = spark.read.format("jdbc") \
    .option("url", "jdbc:mysql://host:3306/db") \
    .option("dbtable", "orders") \
    .option("user", "root") \
    .option("password", "xxx") \
    .load()

# Hive 表
spark.sql("SELECT * FROM dw.orders WHERE dt='2026-07-02'")
```

### Table 操作：Spark SQL 方式

```python
# 注册临时视图
df.createOrReplaceTempView("orders")

# 写纯 SQL（和 Hive 语法 99% 兼容）
result = spark.sql("""
    SELECT
        category,
        COUNT(DISTINCT user_id) AS uv,
        SUM(amount) AS gmv,
        AVG(amount) AS avg_amount
    FROM orders
    WHERE dt = '2026-07-02'
    GROUP BY category
    ORDER BY gmv DESC
""")

result.show()
result.write.mode("overwrite").parquet("hdfs://node1:9000/output/report/")
```

### 实战：WordCount（经典面试题）

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("WordCount") \
    .getOrCreate()

# 方法 1：RDD 方式
text_rdd = spark.sparkContext.textFile("hdfs://node1:9000/data/input.txt")
word_counts = text_rdd \
    .flatMap(lambda line: line.split(" ")) \
    .map(lambda word: (word, 1)) \
    .reduceByKey(lambda a, b: a + b) \
    .sortBy(lambda x: x[1], ascending=False) \
    .take(10)
print("Top 10 单词:", word_counts)

# 方法 2：DataFrame + SQL 方式
df = spark.read.text("hdfs://node1:9000/data/input.txt")
df.createOrReplaceTempView("lines")
result = spark.sql("""
    SELECT word, COUNT(*) AS cnt
    FROM (
        SELECT EXPLODE(SPLIT(value, ' ')) AS word
        FROM lines
    )
    GROUP BY word
    ORDER BY cnt DESC
    LIMIT 10
""")
result.show()
```

### 实战：用户订单聚合分析

```python
# 读取订单数据
orders = spark.read.parquet("hdfs://node1:9000/dw/orders/")

# 计算每个用户的消费统计
user_stats = orders.groupBy("user_id").agg(
    F.count("order_id").alias("order_cnt"),
    F.sum("amount").alias("total_amount"),
    F.avg("amount").alias("avg_amount"),
    F.max("amount").alias("max_amount"),
    F.min("amount").alias("min_amount"),
    F.collect_list("category").alias("categories"),  # 所有购买品类
    F.countDistinct("category").alias("category_cnt")
)

# 按消费层级分群
user_stats = user_stats.withColumn("level",
    F.when(F.col("total_amount") > 1000, "高价值")
     .when(F.col("total_amount") > 500, "中价值")
     .otherwise("低价值")
)

# 写入结果
user_stats.write.mode("overwrite").parquet("hdfs://node1:9000/dw/user_report/")
```

## 六、Spark Streaming 基础

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .appName("KafkaStreaming") \
    .getOrCreate()

# Structured Streaming：从 Kafka 读取实时数据
df_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka1:9092,kafka2:9092") \
    .option("subscribe", "order_topic") \
    .load()

# 解析 JSON
parsed = df_stream.selectExpr(
    "CAST(value AS STRING) as json_str"
).select(
    F.get_json_object("json_str", "$.order_id").alias("order_id"),
    F.get_json_object("json_str", "$.amount").cast("double").alias("amount"),
    F.get_json_object("json_str", "$.category").alias("category"),
    F.get_json_object("json_str", "$.event_time").cast("timestamp").alias("event_time")
)

# 滚动窗口聚合（每 5 分钟统计各品类 GMV）
window_result = parsed \
    .withWatermark("event_time", "10 minutes") \
    .groupBy(
        F.window("event_time", "5 minutes"),
        "category"
    ) \
    .agg(F.sum("amount").alias("gmv"))

# 输出到控制台（生产环境改 HDFS/MySQL/Kafka）
query = window_result.writeStream \
    .outputMode("append") \
    .format("console") \
    .trigger(processingTime="1 minute") \
    .start()

query.awaitTermination()
```

### DStream vs Structured Streaming

| 对比 | DStream（旧） | Structured Streaming（新） |
|------|--------------|--------------------------|
| 抽象层 | RDD | DataFrame/Dataset |
| 事件时间 | 需要手动处理 | 内置 watermark |
| 容错 | 需要配置 checkpoint | 自动 |
| API 一致性 | 批量/流是不同的 API | 同一套 API |
| 使用建议 | 已过时 | **当前标准** |

## 七、MLlib 机器学习库概览

```python
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml import Pipeline

# 1. 特征工程
# 将字符串列转为数值列
indexer = StringIndexer(inputCol="city", outputCol="city_idx")

# 组装特征向量
assembler = VectorAssembler(
    inputCols=["age", "amount", "city_idx", "order_cnt"],
    outputCol="features"
)

# 2. 训练模型
rf = RandomForestClassifier(
    labelCol="is_churn",
    featuresCol="features",
    numTrees=50
)

# 3. 构建 Pipeline
pipeline = Pipeline(stages=[indexer, assembler, rf])

# 4. 训练/测试划分
train, test = df.randomSplit([0.7, 0.3], seed=42)
model = pipeline.fit(train)

# 5. 预测与评估
predictions = model.transform(test)
evaluator = BinaryClassificationEvaluator(labelCol="is_churn")
auc = evaluator.evaluate(predictions)
print(f"AUC: {auc:.4f}")
```

**面试话术**："MLlib 的优势是可以在分布式集群上训练模型，处理单机装不下的数据。但实际工作中，特征工程阶段用 Spark，模型训练阶段如果数据量不大（几 GB 以内），会导出到 Python 用 sklearn/lightgbm，因为现有的单机 ML 库生态更成熟。"

## 八、性能调优

### 1. 缓存 / Persist

```python
# cache() = persist(MEMORY_ONLY)
df.cache()                        # 缓存到内存，后续用缓存的
rdd.persist(StorageLevel.MEMORY_AND_DISK)  # 内存不够就溢写磁盘

# 适用场景：一个 DataFrame 被多次使用
orders = spark.read.parquet("data/").cache()  # 缓存后
orders.filter(...).count()    # 从缓存读
orders.groupBy(...).count()   # 从缓存读
orders.groupBy(...).agg(...)  # 从缓存读

# 用完释放
orders.unpersist()
```

### 2. 广播变量

```python
# 小表 JOIN 大表：把小的 broadcast 到每个 Executor
from pyspark.sql.functions import broadcast

# 自动 broadcast（小于 spark.sql.autoBroadcastJoinThreshold，默认 10MB）
result = orders.join(broadcast(user_dict), "user_id")

# 或者传普通 Python dict
city_map = {"BJ": "北京", "SH": "上海", "GZ": "广州"}
broadcast_map = spark.sparkContext.broadcast(city_map)

# Executor 中直接使用
def map_city(code):
    return broadcast_map.value.get(code, "未知")
```

### 3. Shuffle 优化

```python
# 控制 Shuffle 分区数（默认 200，需要根据数据量调整）
spark.conf.set("spark.sql.shuffle.partitions", 500)

# 避免不必要的 Shuffle
# - 去重：如果可以接受不严格去重，用 approx_count_distinct
# - groupByKey → reduceByKey / aggregateByKey
# - 多次 Shuffle 合并成一次

# 加盐：处理数据倾斜
from pyspark.sql.functions import rand

df = df.withColumn("salt", (rand() * 10).cast("int"))  # 0-9 随机盐
df.createOrReplaceTempView("orders_salted")
# 第一阶段：加盐聚合
spark.sql("""
    SELECT user_id, salt, SUM(amount) AS partial_sum
    FROM orders_salted
    GROUP BY user_id, salt
""")
# 第二阶段：去盐终聚合
# GROUP BY user_id SUM(partial_sum)
```

### 优化清单

| 优先级 | 方法 | 效果 |
|--------|------|------|
| 1 | **用 DataFrame/Dataset 替代 RDD** | Catalyst 自动优化 |
| 2 | **用 Parquet/ORC + SNAPPY** | 列存 + 压缩 |
| 3 | **缓存重复使用的 RDD/DF** | 避免重复计算 |
| 4 | **广播小表** | 避免 Shuffle |
| 5 | **调整 Shuffle 分区数** | 避免单分区过大或过多 |
| 6 | **减少 Shuffle**（用 reduceByKey 不用 groupByKey） | 减少网络 IO |
| 7 | **处理数据倾斜** | 消除长尾任务 |

## 九、面试高频考点

### 考点 1：RDD vs DataFrame vs Dataset

**问题**："RDD、DataFrame、Dataset 有什么区别？什么时候用哪个？"

**回答**：RDD 是最底层的 API，适合非结构化数据和底层操作，但没有内置优化。DataFrame 以列组织，有 Schema，通过 Catalyst 优化器自动优化，是 Python 用户的首选。Dataset 给 DataFrame 加了编译时类型安全，但目前只有 Scala/Java 支持。实际工作中 Python 用户主要用 DataFrame。

### 考点 2：宽依赖 vs 窄依赖

**问题**："Spark 中宽依赖和窄依赖有什么区别？为什么重要？"

**回答**：窄依赖是父 RDD 的一个分区只被子 RDD 的一个分区使用，不需要 Shuffle，可以流水线执行。宽依赖是父 RDD 的一个分区被子 RDD 的多个分区使用，需要 Shuffle。Spark 以宽依赖为边界划分 Stage，宽依赖前的所有窄依赖可以在一个 Stage 内执行。另外宽依赖的故障恢复代价更大。

### 考点 3：为什么 Spark 比 MapReduce 快

**问题**："Spark 为什么比 MapReduce 快？真的是 100 倍吗？"

**回答**：核心原因是 Spark 的内存计算——中间结果存在内存而非磁盘，减少了 IO 开销。另外 Spark 的 DAG 调度器可以一次性规划整个计算流程，避免 MR 那种反复启停作业。但"快 100 倍"只针对迭代计算（如机器学习），对简单 ETL 可能只有 2-3 倍提升。

### 考点 4：reduceByKey vs groupByKey

**问题**："reduceByKey 和 groupByKey 有什么区别？为什么说 groupByKey 性能差？"

**回答**：reduceByKey 在 Map 端会做局部聚合（combiner），Shuffle 传的数据量小。groupByKey 把全部数据原样 Shuffle，网络 IO 大，而且容易 OOM。能用 reduceByKey / aggregateByKey 就不要用 groupByKey。

### 考点 5：数据倾斜怎么处理

**问题**："Spark 作业出现数据倾斜怎么办？"

**回答**：先确认倾斜的 key。如果是 NULL 值多，先过滤 NULL。如果是某个热点 key 数据量大，用加盐（加随机前缀）打散到多个分区，聚合后再去盐做全局汇总。也可以用 broadcast join 替代 common join 来避免 Shuffle。

## 相关笔记

- [[工作学习/大数据技术/Hive基础|Hive 基础]] — Hive 是 SQL-on-Hadoop，Spark 可以替代 Hive 的计算引擎
- [[工作学习/大数据技术/HBase基础|HBase 基础]] — Spark 可以读写 HBase
- [[工作学习/Python数据栈/pandas实战-电商订单分析|pandas 实战：电商订单分析]] — pandas 的单机 API 和 Spark DataFrame 概念类似
- [[工作学习/机器学习/模型评估与调参|模型评估与调参]] — Spark MLlib 可以分布式训练
- [[工作学习/数据库与SQL/SQL查询优化|SQL 查询优化]] — Spark SQL 的优化原理参考
