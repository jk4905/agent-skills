---
name: database-standards
description: 使用团队数据库规范审核和设计 MySQL 与 Redis。适用于 MySQL 5.7/8.0 的建表、改表、DDL 审批、索引设计、字段设计、Schema 评审，以及 Redis 的 key、value、TTL、命令使用和缓存设计审核；当 Codex 需要按团队口径约束 AI 产出的数据库设计时使用。
---

# 数据库规范

## 概述

当 AI 在项目编码过程中需要设计 MySQL 表结构、索引、字段类型，或设计 Redis key/value、TTL、缓存方案时，优先使用这个 skill 作为数据库规范护栏。这个 skill 的核心目标不是做审批流审核，而是在 AI 产出数据库设计方案时，及时对不符合团队规范的内容进行提醒，并提示需要人工干预或确认。

## 规则优先级

- 如果当前用户消息给了明确规则，优先级最高。
- 其次遵循本 skill 内的 reference 文件。
- 通用的 MySQL / Redis 最佳实践只能用于补空白，不能覆盖团队明确规则。
- 如果历史规范、旧文档与当前规则冲突，以当前规则为准。

## 请求分流

1. 如果任务是 MySQL 建表、改表、DDL 审批、索引设计、字段设计或 Schema 评审，读取：
- [references/mysql.md](references/mysql.md)

2. 如果任务是 Redis key、value、TTL、命令使用或缓存设计，读取：
- [references/redis.md](references/redis.md)

3. 如果任务同时涉及 MySQL 作为数据真源、Redis 作为缓存或派生存储，同时读取 MySQL 和 Redis reference。

## 使用方式

### MySQL 场景

- 优先检查命名、字段类型、主键、非空、默认值、注释、索引、DDL 风险。
- 严格执行团队规则，不要自动放宽成“通用最佳实践”。
- 用户没有明确指定版本时，默认按 MySQL 8.0 理解。
- 对高风险 DDL，例如 `DROP`、`TRUNCATE`、缩容改型、批量 `ALTER`，保持保守结论。

### Redis 场景

- 先判断 Redis 是否适合这个场景，而不是默认用 Redis。
- 重点检查 key 命名、value 大小、TTL、禁用命令、db0 约束、bigkey 和 hotkey 风险。
- 如果业务本质上需要长期持久化或复杂查询，优先提醒回到 MySQL。

## 不可违反的规则

- 不要通过存在明显语法错误、缺少主键、缺少注释、或索引理由不充分的 DDL。
- 不要因为 SQL 语法合法，就忽略 `DROP`、`TRUNCATE`、缩容类型变更这类高风险操作。
- 不要把 Redis 当成 MySQL 持久业务数据的默认替代品。
- 不要隐藏不确定性。如果 online DDL 安全性或数据兼容性依赖表数据量、现有数据分布、引擎细节，必须明确说出来。

## 默认立场

- 审批结论倾向保守。
- 明确披露风险，优先于乐观猜测。
- 优先选择可演进、可维护的 Schema，而不是为了省事做短期取巧。
