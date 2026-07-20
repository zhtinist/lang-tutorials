# 习题推荐 · Practice Problems

> 先自己按 [LLD 框架](lld-framework.md) 走 5 步，再对答案或讨论。表中「建议模式」是提示不是唯一解。

---

## 一、怎么练

1. 限时 30–40 分钟：澄清 → 实体 → 类图 → 主方法伪代码  
2. 只允许查本系列笔记，不直接翻完整题解  
3. 结束后用 SOLID 清单自检，补「变化轴」  
4. 每周 2 题，覆盖 State / Strategy / 资源分配三类

---

## 二、题目表

| 题目 | 难度 | 考察点 | 建议模式 |
|------|------|--------|----------|
| Parking Lot | 中 | 资源分配、计费 | Strategy、Factory |
| Library Management | 中 | 状态、借阅约束 | Strategy、Facade |
| Rate Limiter | 中 | 算法可替换、并发 | Strategy、Proxy |
| Elevator System | 中高 | 多电梯调度、状态机 | State、Strategy |
| Vending Machine | 中 | 投币/选货状态迁移 | State |
| Chess Game | 中高 | 棋子规则、走法生成 | Strategy、Command（悔棋） |
| Snake & Ladder | 中 | 桌游回合、玩家 | 组合；可选 Template |
| Movie Ticket Booking | 中高 | 选座、锁座、下单 | Facade；锁/并发 |
| Notification System | 中 | 多渠道发送 | Observer、Factory、Adapter |
| ATM / Banking | 中 | 取款流程、账户 | State、Command |
| Hotel Booking | 中 | 房间库存、预订 | Strategy（定价） |
| Splitwise / Expense | 中高 | 分账、结算图 | 领域模型为主 |
| Traffic Light | 低中 | 灯色切换 | State |
| Coffee Machine | 低中 | 配方与制作步骤 | Template、Decorator |
| File System | 中 | 目录树 | Composite |
| LRU Cache | 中 | 数据结构 + OOD | 哈希 + 双向链表（可作类设计） |
| Online Auction | 中高 | 出价、结束事件 | Observer、State |
| Ride Sharing（简化） | 高 | 匹配司机 | Strategy；注意别做成纯 HLD |
| Food Delivery（简化） | 高 | 订单状态 | State、Observer |
| Parking Lot + EV/预约 | 中高 | 在基础题上扩展 | 原设计是否 OCP |

---

## 三、分组练习路线

### 路线 A：状态机专精

```
Vending Machine → Traffic Light → Elevator → Order/ATM
```

每题画出**状态迁移图**再写类。

### 路线 B：策略与资源

```
Rate Limiter → Parking Lot → Hotel Booking → Notification
```

每题明确一个 `XxxStrategy` 接口。

### 路线 C：树与结构

```
File System → Menu（公司组织） → Chess 棋盘组合
```

练习 Composite 与「统一接口对待叶子/容器」。

---

## 四、电梯题提示（高频）

| 澄清 | 几部电梯？外呼/内呼？目标：等待时间还是简单轮询？ |
|------|------|
| 实体 | Elevator, ElevatorController, Request, Display |
| 状态 | Idle / MovingUp / MovingDown / Maintenance |
| 策略 | 调度：最近电梯 / 分区 |
| 并发 | 请求队列线程安全 |

不要一上来设计分布式集群；MVP 单控制器即可。

---

## 五、售票选座提示

| 风险 | 设计点 |
|------|--------|
| 超卖 | 座位状态 + 事务/锁；`hold` 超时释放 |
| 搜索场次 | `Show` / `Screen` / `Seat` 模型 |
| 支付 | 端口 `PaymentGateway`（DIP） |
| 变化 | 定价 Strategy；通知 Observer |

---

## 六、更多题干速写（自己补全澄清）

### Snake & Ladder

- 棋盘格、蛇/梯传送、多玩家轮流掷骰  
- 实体：`Board`, `Cell`, `Snake`, `Ladder`, `Player`, `Dice`, `Game`  
- 注意：终点精确到达？可扩展「特殊格」用策略  

### Chess（简化）

- MVP：双人对弈、合法走子校验、将军检测可后置  
- `Piece` 抽象 + `move_pattern` Strategy；棋盘 `Board` 组合 64 格  
- 悔棋：`Command` 保存走子前后状态  

### Notification System

- 渠道：Email / SMS / Push；用户订阅偏好  
- `Notifier` 接口 + Factory 创建；失败重试可用 Decorator  
- 事件源 `Subject` → Observer 多渠道  

### Movie Ticket Booking（口述加分）

```
Show -- Screen -- Seat
Booking hold 座位 N 分钟
PaymentGateway 端口
PricingStrategy（工作日/周末）
```

### Vending Machine 状态提示

```
Idle → HasCoin → ItemSelected → Dispensing → Idle
         ↘ 退币 /
缺货 / 金额不足 为旁路事件
```

---

## 七、白板 35 分钟检查清单

```
[ ] 开口先确认 MVP（1 min）
[ ] 写下 4–8 个名词（2 min）
[ ] 画出组合关系 + 1 个策略接口（10 min）
[ ] 写主用例伪代码（12 min）
[ ] 主动提 2 个异常 + 1 个并发点（5 min）
[ ] 留时间答「如何扩展 XXX」（5 min）
```

---

## 八、自评表（做完打分）

| 项 | 0–2 分标准 |
|----|------------|
| 需求是否划清 MVP | |
| 类图关系是否正确 | |
| 变化轴是否接口化 | |
| 主路径是否写清 | |
| 异常与并发是否提到 | |

总分 ≥ 8：可进入下一题；< 8：对照本系列案例改一版。

---

练完可回看：[停车场](case-parking-lot.md)、[图书馆](case-library.md)、[限流器](case-rate-limiter.md)。

---

[← 返回索引](index.md)
