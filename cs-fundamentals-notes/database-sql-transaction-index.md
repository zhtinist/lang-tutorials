# 数据库基础:SQL、事务与索引机制

关系型数据库面试绕不开三个层次的问题:SQL 怎么写、事务怎么保证正确性、索引怎么让查询变快。这三层环环相扣——事务的隔离性依赖锁和 MVCC 实现,索引失效直接决定一条 SQL 是走索引还是走全表扫描,而存储引擎和日志文件则是这一切的底层支撑。本篇按"SQL 语句 → 执行流程 → 事务 → 索引 → 存储引擎与日志"的顺序梳理,每一节都给出可以直接对照的示例。

## 一、基本 SQL 语句速查

SQL 按功能分四类:DDL(定义)、DML(操作数据)、DQL(查询)、DCL(控制事务与权限)。下面按实际使用场景分组,而不是死记分类名称。

**查询(DQL)**

```sql
SELECT * FROM users;                                  -- 全表查询
SELECT id, name FROM users;                           -- 指定列
SELECT * FROM users WHERE age > 25;                   -- 条件过滤
SELECT * FROM users ORDER BY age DESC;                -- 排序
SELECT DISTINCT city FROM users;                      -- 去重
SELECT * FROM users LIMIT 10 OFFSET 20;               -- 分页
SELECT name AS username FROM users;                   -- 别名
SELECT * FROM users WHERE name LIKE 'A%';             -- 模糊匹配
SELECT * FROM users WHERE age BETWEEN 20 AND 30;      -- 范围查询
SELECT * FROM users WHERE age > 20 AND city = 'Beijing'; -- 多条件
```

**多表连接与子查询**

```sql
-- 内连接:只保留两表都匹配的行
SELECT u.name, o.amount FROM users u JOIN orders o ON u.id = o.user_id;

-- 左连接:左表全保留,右表无匹配则为 NULL
SELECT u.name, o.amount FROM users u LEFT JOIN orders o ON u.id = o.user_id;

-- 右连接:右表全保留
SELECT u.name, o.amount FROM users u RIGHT JOIN orders o ON u.id = o.user_id;

-- WHERE 子查询
SELECT name FROM users WHERE id IN (SELECT user_id FROM orders);

-- FROM 子查询(派生表)
SELECT t.user_id, COUNT(*) FROM (SELECT * FROM orders WHERE amount > 100) t GROUP BY t.user_id;
```

**聚合与分组**

```sql
SELECT COUNT(*) FROM users;
SELECT SUM(amount) FROM orders;
SELECT AVG(age) FROM users;
SELECT MAX(age), MIN(age) FROM users;
SELECT city, COUNT(*) FROM users GROUP BY city;
SELECT city, COUNT(*) FROM users GROUP BY city HAVING COUNT(*) > 10;  -- HAVING 过滤分组后的结果,WHERE 过滤分组前的行
```

**数据写入(DML)**

```sql
INSERT INTO users(name, age) VALUES('Alice', 30);
INSERT INTO users(name, age) VALUES ('Bob', 25), ('Cathy', 22);       -- 批量插入
INSERT INTO users(id, name) VALUES (1, 'Tom') ON DUPLICATE KEY UPDATE name='Tom';  -- 存在则更新
UPDATE users SET age = 28 WHERE id = 1;
DELETE FROM users WHERE age < 18;
```

**索引与执行计划(DDL)**

```sql
SHOW INDEX FROM users;
CREATE INDEX idx_age ON users(age);
DROP INDEX idx_age ON users;
EXPLAIN SELECT * FROM users WHERE age > 30;             -- 查看执行计划,判断是否走索引
SELECT * FROM users FORCE INDEX (idx_age) WHERE age > 25; -- 强制指定索引
```

**事务与锁(DCL 及相关)**

```sql
START TRANSACTION;   -- 或 BEGIN
COMMIT;
ROLLBACK;
SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT @@tx_isolation;

SELECT * FROM users WHERE id = 1 FOR UPDATE;                          -- 悲观锁
UPDATE users SET age = 26, version = version + 1 WHERE id = 1 AND version = 2;  -- 乐观锁(靠版本号判断冲突)
```

几个高频写法:查重复数据用 `GROUP BY ... HAVING COUNT(*) > 1`;判空用 `IS NULL`(不能用 `= NULL`);深分页优化用"上次最大 id + LIMIT"代替 `OFFSET`,避免偏移量越大扫描行数越多的问题。

## 二、SQL 查询执行流程

一条 `SELECT` 语句从客户端发出到拿到结果,要经过七个阶段。

```
客户端
  │
  ▼
① 连接阶段        TCP 三次握手 + 账号密码认证,为连接分配独立线程
  │
  ▼
② 查询缓存(MySQL 8.0 前) 命中则直接返回;8.0 起已移除
  │
  ▼
③ 解析与预处理     词法分析→语法分析生成 AST;预处理器校验表名/字段名/权限
  │
  ▼
④ 优化器          基于统计信息和成本模型,决定用哪个索引、表连接顺序、连接算法
  │
  ▼
⑤ 执行器          按执行计划调用存储引擎接口,做过滤、排序、连接
  │
  ▼
⑥ 存储引擎(InnoDB) 实际的数据存取、事务与锁在这一层完成
  │
  ▼
⑦ 返回结果         结果集回传客户端,可能分批传输
```

**查询缓存为什么被移除**:缓存要求 SQL 文本、库、协议版本完全一致才能命中,而表一旦被写入,相关缓存立即失效。写多读少的表几乎享受不到缓存收益,反而要为维护缓存一致性付出额外锁开销,MySQL 8.0 直接砍掉了这个模块,交给应用层(如 Redis)做更灵活的缓存。

**优化器如何选索引**:参考每个索引的选择性(区分度)、表的行数统计信息,以及要扫描的数据量估算,用 `EXPLAIN` 可以看到 `possible_keys`(候选索引)和 `key`(实际选中的索引)两个字段,两者不一致时说明优化器放弃了看起来更合适的索引,往往是因为该索引的区分度或访问代价没有想象中好。

## 三、事务四大特性(ACID)

| 特性 | 定义 | 实现机制 |
|------|------|----------|
| 原子性 Atomicity | 事务内所有操作要么全部成功,要么全部回滚,不存在中间状态 | Undo Log:记录修改前的旧值,失败时反向应用回滚 |
| 一致性 Consistency | 事务执行前后,数据库都满足完整性约束(主键、外键、唯一、check、业务规则) | 是其余三个特性共同作用的**目标**,不是单独的技术手段 |
| 隔离性 Isolation | 并发事务互不干扰,每个事务感觉不到其他事务的存在 | 锁机制 + MVCC(多版本并发控制) |
| 持久性 Durability | 一旦提交,修改永久生效,即使宕机重启也不丢失 | Redo Log:提交前先写入磁盘上的日志,重启后重放已提交事务 |

四者的关系可以概括为:**原子性、隔离性、持久性是手段,一致性是目的**。做到了前三点,数据库自然就停留在一个合法的一致状态。

举例说明原子性:转账场景 `UPDATE account SET balance = balance - 100 WHERE id = 1;` 和 `UPDATE account SET balance = balance + 100 WHERE id = 2;` 必须绑定在同一个事务里——如果第一条执行成功、第二条因为断电没有执行,Undo Log 会在崩溃恢复时把第一条也撤销,保证不会出现"钱凭空消失"的中间状态。

## 四、事务隔离级别

隔离性并非非黑即白,SQL 标准定义了四个级别,级别越高并发性能越差,但能规避的并发问题越多。

| 隔离级别 | 脏读 | 不可重复读 | 幻读 | 实现方式 |
|----------|------|------------|------|----------|
| Read Uncommitted(读未提交) | 会发生 | 会发生 | 会发生 | 几乎不加控制,直接读最新值 |
| Read Committed(读已提交) | 已解决 | 会发生 | 会发生 | 每次 SELECT 生成新的 ReadView |
| Repeatable Read(可重复读,**MySQL InnoDB 默认**) | 已解决 | 已解决 | 基本解决 | 事务开始时生成一次 ReadView + Next-Key Lock |
| Serializable(串行化) | 已解决 | 已解决 | 已解决 | 所有读写操作都加锁,事实上串行执行 |

三个并发问题的准确定义:

- **脏读**:事务 A 读到了事务 B 尚未提交的修改,一旦 B 回滚,A 读到的数据就是从未真实存在过的。
- **不可重复读**:同一个事务内,两次读同一行,由于中间有其他事务提交了 `UPDATE`,两次结果不一样。
- **幻读**:同一个事务内,两次执行相同的范围查询,由于中间有其他事务 `INSERT` 了新行,两次返回的行数不一样。

MySQL 的 Repeatable Read 之所以能"基本解决"幻读(标准定义下 RR 只解决前两个),是因为 InnoDB 用 MVCC 的一致性视图挡住了快照读能看到的新行,再用 Next-Key Lock(行锁+间隙锁)挡住当前读场景下往间隙里插入新行的动作,两者配合把幻读问题也覆盖了,这一点会在下面的 MVCC 一节详细展开。

## 五、索引的种类

索引可以从三个维度分类,面试常问的"聚簇索引 vs 非聚簇索引"和"联合索引最左前缀"都在这里。

**按数据结构**

- **B+ 树索引**:所有数据都在叶子节点,叶子节点之间用链表连接,适合范围查询和排序,是 InnoDB 的默认结构。
- **哈希索引**:通过哈希函数直接定位,等值查询是 O(1),但不支持范围查询和排序;Memory 引擎使用,InnoDB 内部也有自适应哈希索引(引擎自动维护,不能手动创建)。
- **全文索引**:基于倒排索引,面向 `CHAR`/`VARCHAR`/`TEXT` 列的关键词检索,InnoDB 和 MyISAM 都支持。

**按物理存储**

- **聚簇索引**:索引和数据存在一起,索引的叶子节点直接就是数据行,决定了数据在磁盘上的物理顺序。InnoDB 的选择规则是——有主键用主键;没有主键但有非空唯一索引,用它;都没有则由引擎生成一个隐藏的 6 字节 `ROW_ID` 列做聚簇索引。一张表只能有一个聚簇索引。
- **非聚簇索引(二级索引)**:叶子节点存的不是数据本身,而是聚簇索引的键值,查到之后还要拿这个键值再去聚簇索引查一次完整数据行,这个动作叫**回表**。一张表可以有多个非聚簇索引。

**按逻辑特性**

- **主键索引**:唯一且非空,一张表只有一个,InnoDB 中即聚簇索引。
- **普通索引**:没有唯一性限制,允许重复和空值。
- **唯一索引**:值必须唯一,但允许出现空值。
- **联合索引(复合索引)**:在多个列上建的索引,遵循**最左前缀原则**——索引 `(a, b, c)` 只有查询条件从 `a` 开始连续使用(`a`,或 `a+b`,或 `a+b+c`)才能用上索引,单独用 `b` 或 `c` 用不上。
- **覆盖索引**:查询所需的列全部包含在索引里,不需要回表,直接从索引就能返回结果,是常见的性能优化手段。
- **前缀索引**:对字符串类型只取前 N 个字符建索引,节省空间,代价是区分度下降。

## 六、为什么 MySQL 索引用 B+ 树

这是面试高频的原理题,核心是磁盘 I/O 次数。InnoDB 的一个索引节点大小设计成和磁盘页(默认 16KB)对齐,一次磁盘读取正好加载一个完整节点,查询代价基本等于"树的高度"这个数字。

**B 树 vs B+ 树结构对比**

```
B 树(每个节点都存数据,含 key 和 data):

                [ 17 | data ]
               /             \
      [ 8 | data ]      [ 25 | data ]
       /       \           /        \
   [3|data]  [12|data] [20|data]  [30|data]

── 每个节点既存 key 又存 data,同样大小的磁盘页能装下的 key 数量少,
   树更高,查询路径长且不稳定(数据可能在中间节点就命中,也可能要到叶子)


B+ 树(非叶子节点只存 key,数据全部在叶子,叶子间用链表相连):

                [ 17 ]
               /       \
          [ 8 ]         [ 17 | 25 ]
         /     \            |    \
   [3|data]→[8,12|data]→[17,20|data]→[25,30|data]
        (叶子节点之间用双向链表串联,支持顺序遍历)

── 非叶子节点不存 data,同样大小的页能装下更多 key(高扇出),
   树更矮;所有数据在同一层叶子,任何一次查询的路径长度都相同,
   性能稳定;范围查询只需定位起点,然后沿链表顺序读,无需回溯上层
```

具体到数字:假设一个 InnoDB 页 16KB,主键为 8 字节 bigint,指针 6 字节,一个索引项约占 14 字节,一页大约能存 16384/14 ≈ 1170 个索引项。三层 B+ 树可以表示 1170³ ≈ 16 亿行数据,也就是说千万级甚至十亿级的表,查询一行数据通常只需要 3 次磁盘 I/O(根节点通常常驻内存,实际只需 2 次)。如果用 B 树存同样数据,由于每个节点还要存 data,同样页大小能容纳的 key 数远少于 1170,树高会显著增加,I/O 次数随之增加。

**和其他结构的对比**

| 结构 | 局限 |
|------|------|
| 哈希表 | 等值查询 O(1) 很快,但不支持范围查询、排序,`ORDER BY`/`BETWEEN` 用不上 |
| 二叉查找树 | 数据有序插入时会退化成链表,查询复杂度退化到 O(n) |
| 红黑树 | 平衡性比二叉树好,但本质是二叉结构,同样数据量下树高远大于 B+ 树的多叉结构,不适合做磁盘索引(内存索引如 Java `TreeMap` 用它没问题,磁盘场景下 I/O 次数和树高强相关) |
| B 树 | 数据分散在所有节点,单节点扇出比 B+ 树低,树更高,范围查询需要中序遍历回溯多个节点 |

一句话总结:B+ 树用"非叶子节点不存数据"换来更高的扇出、更矮的树、更少的磁盘 I/O,又用"叶子节点链表相连"解决了范围查询效率的问题,这两点结合正好命中磁盘存储和 SQL 查询模式(大量范围查询和排序)的需求。

## 七、什么时候该建索引

- **WHERE 条件列**:高频过滤字段建索引可以避免全表扫描,直接定位符合条件的行。
- **JOIN 的连接列**:两表关联时,连接列有索引才能高效匹配,否则每次连接都要做嵌套扫描。
- **ORDER BY 的排序列**:如果索引顺序和排序顺序一致,可以直接按索引顺序读取,省掉额外的排序步骤。
- **GROUP BY 的分组列**:利用索引的有序性加速分组统计。
- **数据量大的表**:表越大,索引带来的收益相对全表扫描越明显。
- **主键和唯一约束列**:数据库会自动创建索引来保证唯一性并加速查找。
- **外键列**:提升关联查询效率,也便于维护引用完整性。

## 八、什么时候不该建索引

- **数据量很小的表**:全表扫描本身开销就很低,索引查找再回表反而更慢,索引维护成本得不偿失。
- **写多读少的表**:每次 `INSERT`/`UPDATE`/`DELETE` 都要同步维护索引结构,索引越多写入越慢。
- **区分度很低的列**:比如性别、布尔值这种只有几个取值的列,即使建了索引,一次查询也可能命中一半以上的数据,优化器往往直接放弃索引选择全表扫描。
- **很少出现在查询条件里的列**:用不上的索引纯粹是浪费空间和维护成本。
- **查询会返回大部分数据的场景**:结果集超过全表 20%~30% 时,先走索引再回表的总成本可能超过直接顺序扫描全表。
- **索引列上做函数运算、模糊前缀匹配等注定用不上索引的场景**:建了也白建,详见下一节。

## 九、索引失效场景(附反例)

以下是索引建了却不会被优化器使用的典型 SQL,逐条给出反例和原因。

**1. 对索引列做函数运算或表达式计算**

```sql
-- 反例:DATE_FORMAT() 把索引列包在函数里,索引存的是原始值,函数结果对不上
SELECT * FROM users WHERE DATE_FORMAT(create_time, '%Y-%m-%d') = '2023-10-26';

-- 反例:对索引列做算术运算同样失效
SELECT * FROM products WHERE price * 0.8 < 100;

-- 正确写法:把运算移到常量一侧,索引列保持原始形态
SELECT * FROM users WHERE create_time >= '2023-10-26 00:00:00' AND create_time < '2023-10-27 00:00:00';
SELECT * FROM products WHERE price < 100 / 0.8;
```

**2. 模糊查询以通配符开头**

```sql
-- 反例:% 在前,B+ 树的有序性用不上,只能全表扫描
SELECT * FROM users WHERE user_name LIKE '%zhang%';

-- 可以走索引:% 在后,相当于范围查询
SELECT * FROM users WHERE user_name LIKE 'zhang%';
```

**3. 使用 `!=` 或 `<>`**

```sql
-- 反例:不等于条件命中的数据范围不确定,优化器通常倾向全表扫描
SELECT * FROM orders WHERE status != 'completed';
```

**4. `OR` 连接了不同的列,且并非都有索引**

```sql
-- 反例:product_name 有索引、category 没有索引,OR 会导致整体放弃索引
SELECT * FROM products WHERE product_name = 'honor' OR category = 'electronics';

-- OR 连接同一列的不同取值通常可以正常走索引(等价于 IN)
SELECT * FROM products WHERE product_name = 'honor' OR product_name = 'huawei';
```

**5. 隐式类型转换**

```sql
-- 反例:phone 是 VARCHAR,右侧写成数字,MySQL 会对索引列做隐式转换,索引失效
SELECT * FROM users WHERE phone = 12345678900;

-- 正确写法:保持类型一致
SELECT * FROM users WHERE phone = '12345678900';
```

**6. 违反联合索引的最左前缀原则**

假设联合索引为 `(a, b, c)`:

```sql
SELECT * FROM t WHERE b = 2;                 -- 失效:跳过了最左列 a
SELECT * FROM t WHERE c = 3;                 -- 失效:同上
SELECT * FROM t WHERE b = 2 AND c = 3;       -- 失效:仍然没有从 a 开始
SELECT * FROM t WHERE a = 1 AND c = 3;       -- 部分生效:只能用上 a 这一列,c 用不上
SELECT * FROM t WHERE a = 1 AND b = 2;       -- 完全生效
```

**7. 范围查询之后的列失效**

```sql
-- 联合索引 (a, b, c);对 a 做范围查询后,b 无法再利用索引的有序性
SELECT * FROM t WHERE a > 1 AND b = 2;   -- a 用上索引,b 相当于在结果集里过滤,没有用上索引
```

原因是 B+ 树按 `a, b, c` 的顺序整体排序,一旦 `a` 是范围条件,`b` 在这个范围内不再是严格有序的,索引对 `b` 失去了排序意义(等值查询除外,`a` 若是等值条件则 `b` 仍然有效,这也是最左前缀原则的一部分)。

**8. `IS NULL` / `IS NOT NULL`**

```sql
-- 索引对 NULL 值的处理因数据分布而异,NULL 较多时优化器可能放弃索引
SELECT * FROM users WHERE phone IS NULL;
```

是否失效取决于 `NULL` 值在该列中的比例——如果 `NULL` 是少数,索引仍然有效;如果占比很高,和"区分度低"的道理一样,优化器会放弃索引。

**9. 优化器基于成本判断主动放弃索引**

即使索引本身可用,当查询会返回表中大部分数据、或索引列区分度过低、或统计信息不准确导致预估代价失真时,优化器也可能主动选择全表扫描——这不是索引"失效",而是优化器判断全表扫描的成本更低。用 `EXPLAIN` 观察 `possible_keys` 和 `key` 是否一致,可以验证这种情况。

## 十、MVCC 机制

MVCC(Multi-Version Concurrency Control,多版本并发控制)是 InnoDB 用来实现"读不加锁、读写不冲突"的核心机制。它的核心思想只有一句话:**给每一行数据保留多个历史版本,不同事务按各自的可见性规则读取属于自己的那个版本**,而不是所有事务抢同一份最新数据。

### 版本链:数据是怎么"存多份"的

InnoDB 给每一行数据额外挂两个隐藏列:

- `DB_TRX_ID`:最近一次修改这行数据的事务 ID。
- `DB_ROLL_PTR`(回滚指针):指向 Undo Log 里这一行的上一个版本。

每次事务修改一行数据,旧版本不会被直接覆盖,而是写进 Undo Log,同时把这一行的 `DB_ROLL_PTR` 指向刚写入的旧版本记录。多次修改之后,同一行数据在 Undo Log 里形成一条链表:

```
当前行(最新版本,DB_TRX_ID = 103)
   │ DB_ROLL_PTR
   ▼
Undo Log 版本(DB_TRX_ID = 102,name = 'v2')
   │ DB_ROLL_PTR
   ▼
Undo Log 版本(DB_TRX_ID = 101,name = 'v1')
   │ DB_ROLL_PTR
   ▼
NULL(链表终点,最初插入的版本或已不再需要的版本)
```

这就是"版本链"——最新版本在链头,顺着回滚指针往回找,能找到这一行历史上任意一次提交后的样子。

### ReadView:决定"我能看见链上的哪个版本"

一个事务开始读数据时,会生成一个 ReadView,它记录了当时数据库的"活跃事务快照",包含四个字段:

- `m_ids`:生成 ReadView 那一刻,系统里所有**未提交**(活跃)事务的 ID 列表。
- `min_trx_id`:`m_ids` 中最小的那个值。
- `max_trx_id`:即将分配给下一个新事务的 ID(比当前所有已存在事务 ID 都大)。
- `creator_trx_id`:生成这个 ReadView 的事务自己的 ID。

拿到某个版本的 `DB_TRX_ID` 后,按下面的规则判断这个版本对当前事务是否可见:

1. `DB_TRX_ID < min_trx_id`:这个版本在 ReadView 生成前就已经提交了,**可见**。
2. `DB_TRX_ID >= max_trx_id`:这个版本是 ReadView 生成之后才出现的事务改的,**不可见**。
3. `min_trx_id <= DB_TRX_ID < max_trx_id`:需要进一步判断——
   - 如果 `DB_TRX_ID` 在 `m_ids` 列表里,说明改这行数据的事务在 ReadView 生成时还没提交,**不可见**;
   - 如果不在 `m_ids` 里,说明这个事务在 ReadView 生成前就已经提交了,**可见**。

如果当前版本判定不可见,就顺着 `DB_ROLL_PTR` 往版本链的上一层走,重复上面的判断,直到找到一个可见版本为止(有可能一路找到链表尾部都没有可见版本,意味着这一行在事务开始前还不存在)。

### RC 和 RR 的核心区别就是 ReadView 什么时候生成一次

| 隔离级别 | ReadView 生成时机 | 效果 |
|----------|--------------------|------|
| Read Committed | **每次 SELECT** 都重新生成一个 ReadView | 每次都能看到最新已提交的数据,所以会出现不可重复读 |
| Repeatable Read | **事务开始时生成一次**,整个事务期间复用同一个 ReadView | 事务全程看到的是同一个快照,不会有不可重复读 |

这也是为什么面试常问"MVCC 是怎么实现可重复读的"——答案就是 RR 只在事务第一次执行快照读时生成 ReadView,之后所有的快照读都复用它,不管其间有没有别的事务提交新数据,当前事务看到的版本判断规则完全不变。

### MVCC 解决幻读,还要靠锁配合

单靠 MVCC 只能保证**快照读**(普通 `SELECT`)不会看到幻读现象——因为读的是事务开始那一刻的快照,后续别的事务插入的新行天然不在快照里。但**当前读**(`SELECT ... FOR UPDATE`、`UPDATE`、`DELETE`)必须读最新数据,MVCC 保护不了这种场景下的幻读,这时候要靠 **Next-Key Lock**(行锁 + 间隙锁)在物理上锁住索引记录之间的间隙,阻止其他事务往这个范围里插入新行。所以准确的说法是:MySQL RR 级别下"基本解决"幻读,是 MVCC(负责快照读)和 Next-Key Lock(负责当前读)两种机制协同的结果,而不是 MVCC 单独做到的。

普通 `SELECT` 属于快照读,通常不加锁,可以和写操作并发执行;`SELECT ... FOR UPDATE`、`SELECT ... LOCK IN SHARE MODE` 以及所有写操作属于当前读,仍然需要加锁。

## 十一、数据库锁

锁按作用范围从大到小分三层。

**全局锁**:锁住整个实例,让数据库变成只读,典型用途是全库逻辑备份。`FLUSH TABLES WITH READ LOCK` 加锁,`UNLOCK TABLES` 或断开连接释放。

**表级锁**

| 类型 | 说明 |
|------|------|
| 表锁 | `LOCK TABLES table_name READ/WRITE`,开销最小但并发度最差,MyISAM 默认用这个 |
| 元数据锁(MDL) | 访问表时自动加,保证 DDL 不会和正在进行的 DML 冲突 |
| 意向锁(IS/IX) | 表示"事务接下来要对表里的某些行加共享/排他锁",让"要不要给整张表加锁"这类判断不必逐行扫描,提高兼容性检查效率 |
| AUTO-INC 锁 | 插入自增列时使用,保证并发插入时自增值唯一且递增,插入完成立即释放 |

**行级锁**(InnoDB 特有,基于索引实现,没有索引会退化成锁整张表)

| 类型 | 说明 |
|------|------|
| 记录锁(Record Lock) | 锁住单条索引记录本身,读加共享锁、写加排他锁 |
| 间隙锁(Gap Lock) | 锁住索引记录之间的"间隙"而非记录本身,专门用来防止幻读;两个事务的间隙锁之间互相兼容,但都会阻止第三方在间隙里插入新记录 |
| 临键锁(Next-Key Lock) | 记录锁 + 间隙锁的组合,锁住一条记录本身以及它前面的间隙,是 InnoDB **默认**的行锁实现,兼顾"防止幻读"和"保证索引记录唯一性" |
| 插入意向锁 | 一种特殊的间隙锁,执行 `INSERT` 时产生;多个事务只要插入位置不冲突,可以同时持有同一间隙的插入意向锁 |

从加锁方式的角度,行级锁还可以分成**乐观锁**(不预先加锁,更新时靠版本号或时间戳比对是否冲突,冲突就重试,适合读多写少)和**悲观锁**(`SELECT ... FOR UPDATE`,先加锁再操作,适合写冲突频繁的场景)两种实现思路,这属于应用层设计模式而不是 InnoDB 内部的锁类型。

## 十二、MySQL 存储引擎

| 引擎 | 事务 | 锁粒度 | 外键 | 特点 |
|------|------|--------|------|------|
| **InnoDB**(默认) | 支持 ACID | 行锁 | 支持 | Redo Log + Undo Log 做崩溃恢复,自带缓冲池,高并发场景首选 |
| MyISAM | 不支持 | 表锁 | 不支持 | 索引和数据分开存储,读取快,但写操作会锁整张表,不适合高并发写 |
| Memory | 不支持持久化 | 表锁 | 不支持 | 数据全部在内存,重启即丢失,适合临时表和小规模缓存数据 |
| Archive | 不支持事务 | - | 不支持 | 高压缩率、只支持插入和查询、不支持索引,适合归档只写不查的历史数据 |

选择依据:需要事务和高并发写,选 InnoDB(目前绝大多数场景的默认选择);纯读多写少且不要求数据一致性,可以考虑 MyISAM;需要极致读写速度且能接受数据易失,用 Memory;只是堆积日志类历史数据几乎不查,用 Archive。

## 十三、MySQL 日志文件

MySQL 涉及的日志分为 Server 层和存储引擎层两部分。

| 日志 | 所在层 | 作用 |
|------|--------|------|
| 错误日志(Error Log) | Server | 记录启动、运行、关闭过程中的错误与警告,是排查系统级问题的第一入口 |
| 二进制日志(Binlog) | Server | 记录所有对数据表的逻辑修改,支持 Statement/Row/Mixed 三种格式,用于主从复制和基于时间点的数据恢复,只追加不覆盖 |
| 慢查询日志(Slow Query Log) | Server | 记录执行时间超过 `long_query_time` 阈值的 SQL,配合 `mysqldumpslow` 定位性能瓶颈 |
| 中继日志(Relay Log) | Server(从库) | 从库的 I/O 线程把主库 Binlog 写入中继日志,再由 SQL 线程读取执行,完成主从复制 |
| 重做日志(Redo Log) | InnoDB 引擎层 | 记录事务对数据页做的物理修改,循环写,保证**持久性**,崩溃后靠它恢复已提交事务 |
| 回滚日志(Undo Log) | InnoDB 引擎层 | 记录修改前的旧版本,支撑事务**回滚**和 **MVCC** 的版本链,让读操作不必阻塞写操作 |

**Redo Log 与 Binlog 的本质区别**:Redo Log 是 InnoDB 引擎层的日志,只服务于崩溃恢复,采用固定大小的循环写(写满后从头覆盖);Binlog 是 Server 层的通用日志,不依赖具体存储引擎,面向复制和基于时间点恢复,只追加不覆盖。二者记录的粒度也不同——Redo Log 是物理级的数据页修改,Binlog 是逻辑级的 SQL 操作或行变更。

**两阶段提交**:因为 Redo Log 和 Binlog 是两个独立的系统各自写日志,如果只写完其中一个就崩溃,主库自身的数据状态和它传播给从库/备份的记录就会不一致。InnoDB 用两阶段提交解决:先写 Redo Log 并标记为 `prepare` 状态,再写 Binlog,Binlog 写成功后才把 Redo Log 标记为 `commit`。崩溃恢复时,如果 Redo Log 是 `prepare` 状态且没有对应完整的 Binlog 记录,直接回滚这个事务;如果 Binlog 完整,则将 Redo Log 提交,保证两份日志内容最终对齐。

---
[返回索引](index.md)
