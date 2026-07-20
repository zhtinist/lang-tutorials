# 分层架构 · Layered Architecture

> 分层架构是最常见、事实上的**默认架构**：「不知道用什么时，先用它。」——水平分层，层间接口通信，请求通常自上而下不跳层。

---

## 一、概念

分层架构（layered architecture）把软件切成若干**水平层**。每一层有清晰角色，不必了解其他层内部细节；层与层通过**接口**协作。

层数并无硬性规定，但**四层**最常见：

| 层 | 英文 | 职责 |
|----|------|------|
| 表现层 | Presentation | UI、HTTP 适配、用户交互 |
| 业务层 | Business | 业务规则与用例逻辑 |
| 持久层 | Persistence | 数据访问、SQL/ORM 封装 |
| 数据库 | Database | 数据存储 |

有的系统在业务层与持久层之间再加**服务层 (Service)**，抽出跨用例的通用能力。

---

## 二、结构与请求流

```
  Client / Browser
         │
         ▼
┌─────────────────────┐
│  Presentation Layer │  Controller / View / API Gateway 入口
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   Business Layer    │  领域规则、用例编排
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Persistence Layer   │  Repository / DAO / Mapper
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│     Database        │
└─────────────────────┘
```

**请求流**：用户请求依次经过四层，**一般不允许跳层**（例如 Controller 直接写 SQL）。  
目的是：变化被限制在层内；上层依赖下层抽象，便于替换实现（如换 ORM）。

### 2.1 Python 示意（接口边界）

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Order:
    id: str
    amount: float
    status: str


class OrderRepository(ABC):
    """持久层抽象：业务层只依赖接口，不依赖 SQL。"""

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...


class OrderService:
    """业务层：用例逻辑。"""

    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    def place_order(self, order_id: str, amount: float) -> Order:
        if amount <= 0:
            raise ValueError("amount must be positive")
        order = Order(id=order_id, amount=amount, status="PLACED")
        self._repo.save(order)
        return order


class OrderController:
    """表现层：适配 HTTP / CLI，不含业务规则。"""

    def __init__(self, service: OrderService) -> None:
        self._service = service

    def post_order(self, order_id: str, amount: float) -> dict:
        order = self._service.place_order(order_id, amount)
        return {"id": order.id, "status": order.status}
```

---

## 三、开闭与「贫血模型」注意

### 3.1 开闭原则张力

理想上：对扩展开放、对修改关闭。现实中分层系统常出现：

- 新需求同时改 Presentation + Business + Persistence（甚至库表）
- 「加一个字段」穿透所有层 —— 结构简单，但**横切变更成本高**

这不否定分层，而是提醒：分层解决的是**角色清晰与分工**，不等于天然符合开闭。

### 3.2 贫血领域模型 (Anemic Domain Model)

若 Business 层只剩「getter/setter + 过程式 Service」，领域规则散落在多处，则：

- 易测的是事务脚本，难保的是一致性
- 后续可向 **DDD 富模型** 或 **整洁架构用例层** 演进（见后续章节）

分层本身不强制贫血或充血；关键是**规则放在哪一层、能否被单测锁定**。

---

## 四、优点

对齐 Richards / 阮文归纳：

1. **结构简单**，容易理解与上手——新人能快速找到「UI / 逻辑 / 数据」落点  
2. **天然匹配多数公司组织**：前端、后端、DBA 可按层分工  
3. **层可独立测试**：下层用 mock/stub 替换，上层不必启动真库  

---

## 五、缺点

1. **环境一变，改动面大**：功能增强常跨多层，耗时  
2. **部署笨重**：小改动也可能导致整应用重新部署，难做细粒度持续发布  
3. **升级可能需停服**（视部署方式而定）  
4. **扩展性受限**：请求暴增时往往要**每一层一起扩**；层内耦合时，水平扩展更难  

---

## 六、何时使用

| 适合 | 不太适合 |
|------|----------|
| 中小型业务系统、CRUD 为主 | 需要按功能极致独立扩容 |
| 团队按技术栈分工清晰 | 要求频繁、独立、不停机发布大量特性 |
| 需要「默认、好教」的结构 | 超高并发且中央库已成瓶颈（可看空间架构） |
| 单体或模块化单体起步 | 已明确要多团队自治部署（可看微服务） |

**实践建议**：从分层单体开始；用包/模块严格守住层边界。真到发布与扩容瓶颈，再局部引入事件或拆服务——而不是一上来分布式。

---

## 七、与其他模式的关系

```
分层 (逻辑结构)
   │
   ├─ 可部署为 单体
   ├─ 可 internally 用 事件 做异步
   └─ 拆服务后，每个微服务内部仍常是 分层 / 整洁架构
```

- **整洁架构**：强调依赖方向（只向内），可视为对「分层依赖失控」的纠正  
- **微服务**：每个服务内部仍可用分层；微服务解决的是**部署与团队边界**，不是取消分层  

---

## 八、口诀

> **表现业务持久库，请求自上不跳层；**  
> **分工清晰好上手，横切变更要想全。**

---


[← 返回索引](index.md)
