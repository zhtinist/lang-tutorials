# 整洁架构 · Clean Architecture

> **依赖规则**：源代码依赖只能指向**内圈**。业务规则不依赖 UI、数据库、框架——框架是细节，可替换。

---

## 一、概念

可以把整洁架构想成一颗洋葱：一层包着一层，最中心那圈才是最重要的东西——业务规则本身。外层的皮（用哪种数据库、哪个网页框架、界面长什么样）随时可以剥掉换新的，只要不动到芯，业务逻辑就不受影响。

Uncle Bob（Robert C. Martin）提出的整洁架构（Clean Architecture）用同心圆表达系统：内层是企业业务规则，外层是机制（Web、DB、UI）。越往内，越独立、越少变、越可测。

目标：

- 业务规则可**脱离框架**测试  
- UI / DB / 外部代理可替换，而不伤领域  
- 系统围绕**用例**组织，而非围绕技术组件堆砌  

---

## 二、同心圆与四层职责

```
      ┌─────────────────────────────────────────┐
      │     Frameworks & Drivers                │  Web, DB, UI, Devices
      │   ┌─────────────────────────────────┐   │
      │   │   Interface Adapters            │   │  Controllers, Presenters, Gateways
      │   │  ┌───────────────────────────┐  │   │
      │   │  │   Application Business    │  │   │  Use Cases
      │   │  │  ┌─────────────────────┐  │  │   │
      │   │  │  │  Enterprise Business│  │  │   │  Entities
      │   │  │  │     Rules           │  │  │   │
      │   │  │  └─────────────────────┘  │  │   │
      │   │  └───────────────────────────┘  │   │
      │   └─────────────────────────────────┘   │
      └─────────────────────────────────────────┘

              依赖方向：外 → 内  （只许向内指）
```

| 层 | 职责 |
|----|------|
| **Entities** | 企业级业务规则：最通用、最不易变的对象与不变式 |
| **Use Cases** | 应用业务规则：编排实体，实现「一个用户故事/用例」 |
| **Interface Adapters** | 转换数据：Controller / Presenter / Gateway，适配内外格式 |
| **Frameworks & Drivers** | 框架与驱动：Web 框架、ORM、UI、设备——最外圈细节 |

圆圈是**示意**：实际项目可用包结构表达同一依赖方向，层数可微调，但规则不变。

---

## 三、依赖规则（Dependency Rule）

> 内层**不得**知道外层任何东西：外层类名、外层数据格式、外层框架注解，都不应泄漏进内层。

违反信号：

- Entity 里出现 `import flask` / SQL 注解  
- Use Case 直接操作 HttpRequest 对象  
- 领域模块依赖具体 MySQL 驱动  

允许：外层调用内层；外层实现内层定义的接口（依赖倒置）。

---

## 四、跨越边界的数据

跨边界传递的应是**简单数据结构**（DTO、字典、基本类型），而非外层框架对象。

典型流向：

```
Request DTO → Use Case → Entity 操作 → Response DTO → Presenter → View Model
```

数据库行对象、ORM Session、HTTP Request **停在适配器层**，不要穿进用例与实体。

---

## 五、与分层、六边形的关系

| 风格 | 强调 |
|------|------|
| 传统分层 | 技术角色（表现/业务/持久）水平切开 |
| 六边形 / Ports & Adapters | 应用核心 + 端口；适配器接外部 |
| 整洁架构 | 同心依赖规则 + 用例为中心 |

三者常**兼容**：六边形的「端口」≈ 内层接口；整洁架构把「谁依赖谁」说得更死。传统分层若依赖方向反了（业务依赖 ORM 细节），可用整洁规则纠正。

```
传统分层坏味道：  Controller → Service → OrderEntity(ORM) → MySQL
整洁方向：        Controller → PlaceOrderUseCase → Order(Entity)
                         ↑ 实现
                   SqlOrderRepository (外层)
```

---

## 六、Python 示意：接口倒置

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass


# ── 内层：Entity ─────────────────────────────────
@dataclass
class Order:
    id: str
    amount: float

    def discount(self, rate: float) -> None:
        if not 0 <= rate <= 1:
            raise ValueError("invalid rate")
        self.amount *= 1 - rate


# ── 内层：Use Case 依赖抽象，不依赖框架 ───────────
class OrderRepository(ABC):
    @abstractmethod
    def get(self, order_id: str) -> Order: ...

    @abstractmethod
    def save(self, order: Order) -> None: ...


class ApplyDiscountUseCase:
    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo

    def execute(self, order_id: str, rate: float) -> Order:
        order = self._repo.get(order_id)
        order.discount(rate)
        self._repo.save(order)
        return order


# ── 外层：适配器实现接口 ─────────────────────────
class InMemoryOrderRepository(OrderRepository):
    def __init__(self) -> None:
        self._store: dict[str, Order] = {}

    def get(self, order_id: str) -> Order:
        return self._store[order_id]

    def save(self, order: Order) -> None:
        self._store[order.id] = order


# ── 最外层：框架入口只做适配 ─────────────────────
def http_apply_discount(order_id: str, rate: float) -> dict:
    uc = ApplyDiscountUseCase(InMemoryOrderRepository())
    order = uc.execute(order_id, rate)
    return {"id": order.id, "amount": order.amount}
```

要点：`ApplyDiscountUseCase` 可在无 Web、无 DB 的情况下单测；换 Postgres 实现只需新写一个 `OrderRepository`。

---

## 七、优点与代价

| 优点 | 代价 |
|------|------|
| 业务可测、框架可换 | 类/包数量增加，入门曲线 |
| 依赖方向清晰 | 过度拆分小项目会显得啰嗦 |
| 长期演进友好 | 需团队纪律，否则边界回潮 |

**小工具、脚本**：不必强行四层。  
**寿命长、规则多、技术栈可能换的系统**：依赖规则回报高。

---

## 八、何时使用 / 口诀

适合：领域规则复杂、需要长期演进、希望单测不启动框架。  
不适合：一次性脚本、纯 CRUD 且无行为的薄系统（简单分层即可）。

> **依赖只许向内指，实体用例在核心；**  
> **框架数据库都是细节，跨界只传简单数据。**

---


[← 返回索引](index.md)
