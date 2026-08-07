---
tags:
  - "#用途/工作学习"
  - "#类型/技术"
  - "#技术/mysql"
created: 2026-07-18
updated: 2026-08-01
status: reviewed
---

# PostgreSQL与SQLite深入

## Postgres 够用论

社区热议：**Postgres is enough for more than we admit**。

- 大多数项目不需要专门的搜索引擎（Elasticsearch）、消息队列、图数据库
- Postgres 的扩展能力（JSONB、全文搜索、pgvector）覆盖 80% 场景
- 一个工程师从 SQL Server 13 年转 Postgres 后的惊讶：功能不输商业数据库

相关阅读：[What surprised an engineer after spending 13 years on SQL Server and then working on Postgres](https://www.reddit.com/r/programming/comments/1uzerp7/what_surprised_an_engineer_after_spending_13/)

## Postgres 被 Rust 重写

[pgRust](https://github.com/malisper/pgrust) 用 Rust 重写了 Postgres，**100% 通过 Postgres 回归测试**。这是数据库领域的标志性事件——C 语言不再是系统软件的唯一选择。

## SQLite 实践要点

Julia Evans 的 [Learning a few things about running SQLite](https://jvns.ca/blog/2026/07/17/learning-about-running-sqlite/) ——必读文章：
- SQLite 不只是"测试用的小数据库"，单机场景性能远超客户端-服务器数据库
- WAL 模式是默认最佳选择
- 并发写入的坑：SQLite 是串行写入，高并发场景需要不同策略

### SQLite 的隐藏问题

- **16 年老 Bug**：用 TLA+ 形式化验证找到了 SQLite 中的一个隐藏 bug，检查 dqlite 是否受影响
- **如何损坏 SQLite 文件**：[How To Corrupt An SQLite Database File](https://www.reddit.com/r/programming/comments/1ujgzhr/how_to_corrupt_an_sqlite_database_file/) —— 了解这些场景有助于避免踩坑

## ORM vs 原生 SQL

[What ORMs have taught me: just learn SQL](https://www.reddit.com/r/programming/comments/1uo1w91/what_orms_have_taught_me_just_learn_sql/) —— ORM 方便但不能替代对 SQL 的理解。复杂查询、性能优化还是得回到 SQL 本身。

## 关键链接

- [[wiki/工作学习/数据库与SQL/SQL查询优化|SQL 查询优化]]
- [[wiki/工作学习/数据库与SQL/MySQL基础入门|MySQL 基础入门]]
- [[wiki/工作学习/数据库与SQL/MySQL面试实战盲区|MySQL 面试实战盲区]]

## Postgres 高级特性

### LISTEN/NOTIFY 的扩展性

Postgres 的 `LISTEN/NOTIFY` 机制常被低估。实际测试表明它能**优雅地扩展**到高吞吐场景，可以作为轻量级消息队列使用，避免引入 Redis/Kafka 的运维复杂度。

### PGSimCity：可视化理解 Postgres 内部原理

[PGSimCity](https://nikolays.github.io/PGSimCity/) 是一个交互式可视化工具，用城市类比展示 Postgres 的查询执行过程——解析器、规划器、执行器如何协作。对理解查询优化和执行计划非常有帮助。

### Bottomless Postgres

社区正在探索"无底"Postgres 方案：Neon、pg_mooncake、pg_tier、pg_lake、ColdFront 等项目试图将 Postgres 扩展到能存无限数据，同时保持 SQL 兼容性。核心思路是冷热分离——热数据在本地，冷数据自动卸载到对象存储。

## SQLite 补充

### STRICT 表

SQLite 支持 `STRICT` 模式建表，强制类型检查。长期以来 SQLite 的"灵活类型"（任何列可存任何类型）是常见坑点，`STRICT` 解决了这个问题。

### Rust 风格的版本（Editions）

社区提议 SQLite 采用类似 Rust 的 editions 机制——向后兼容的同时允许 breaking changes。SQLite 以"永不破坏向后兼容"著称，但 20+ 年的设计决策积累难以在不引入 edition 的情况下修复。
