# 结构型模式 · Structural Patterns

> 结构型模式关注「**类与对象如何组装**」：在不改原有代码的前提下适配接口、叠加职责、统一子系统入口。面试高频：**Adapter、Decorator、Facade、Proxy、Composite**。

---

## 一、总览

| 模式 | 意图 | 信号 |
|------|------|------|
| Adapter | 把不兼容接口转换成客户端期望的接口 | 接第三方 SDK、老库 |
| Decorator | 动态给对象叠加职责 | 加日志/缓存/配料，且要可组合 |
| Facade | 为复杂子系统提供简单入口 | 启动流程、一键下单 |
| Proxy | 用替身控制访问 | 懒加载、权限、远程、限流 |
| Composite | 树形结构中统一处理叶子与容器 | 文件系统、菜单、组织架构 |
| Bridge（略） | 抽象与实现分离，各自独立扩展 | 多维度变化（形状×渲染） |
| Flyweight（略） | 共享细粒度不可变状态 | 海量相似对象省内存 |

---

## 二、Adapter · 适配器

### 意图

让原本接口不匹配的类能一起工作——「插头转换器」。

### 信号

- 业务要 `PaymentGateway.charge`，第三方却是 `pay(cents)`
- 不想改第三方，也不想污染业务代码

### 结构

```
Client ──▶ Target(<<interface>>)
                 △
            Adapter ──▶ Adaptee（已有类）
```

### Python 代码

```python
from typing import Protocol


class PaymentGateway(Protocol):
    def charge(self, amount_yuan: float) -> str: ...


class LegacyStripeSDK:
    """假想老 SDK：只认「分」。"""

    def pay(self, cents: int) -> dict[str, str]:
        return {"id": f"ch_{cents}", "status": "ok"}


class StripeAdapter:
    """把 Legacy API 适配成 PaymentGateway。"""

    def __init__(self, sdk: LegacyStripeSDK) -> None:
        self._sdk = sdk

    def charge(self, amount_yuan: float) -> str:
        cents = int(round(amount_yuan * 100))
        result = self._sdk.pay(cents)
        return result["id"]


def checkout(gateway: PaymentGateway, amount: float) -> str:
    return gateway.charge(amount)
```

**口诀**：外系统接口怪，Adapter 中间转。

---

## 三、Decorator · 装饰器

### 意图

在**不修改原类**的前提下，动态叠加功能；装饰器与组件实现同一接口，可嵌套。

### 信号

- 「基础能力 + 可选增强」，增强可任意组合
- 用继承会导致子类爆炸（见 OOP 咖啡例子）

### 结构

```
Component ◀── ConcreteComponent
    △
 Decorator ──▶ Component（持有被装饰者）
    △
 ConcreteDecoratorA / B
```

### Python 代码

```python
from abc import ABC, abstractmethod
from typing import override


class Coffee(ABC):
    @abstractmethod
    def cost(self) -> float: ...

    @abstractmethod
    def desc(self) -> str: ...


class Espresso(Coffee):
    @override
    def cost(self) -> float:
        return 10.0

    @override
    def desc(self) -> str:
        return "Espresso"


class CoffeeDecorator(Coffee, ABC):
    def __init__(self, inner: Coffee) -> None:
        self._inner = inner


class Milk(CoffeeDecorator):
    @override
    def cost(self) -> float:
        return self._inner.cost() + 2.0

    @override
    def desc(self) -> str:
        return self._inner.desc() + " +Milk"


class Sugar(CoffeeDecorator):
    @override
    def cost(self) -> float:
        return self._inner.cost() + 1.0

    @override
    def desc(self) -> str:
        return self._inner.desc() + " +Sugar"


order: Coffee = Sugar(Milk(Espresso()))
assert order.cost() == 13.0
```

### 与 Python `@decorator` 语法

语法糖装饰的是**函数/类**；本模式装饰的是**运行时对象**。面试要分清两套概念，都叫 decorator。

**口诀**：套娃加能力，接口保持不变。

---

## 四、Facade · 外观

### 意图

为复杂子系统提供一个**更高层的简单接口**，降低客户端耦合。

### 信号

- 做一件事要调 5 个服务、记一堆顺序
- 希望调用方只看到 `place_order()`

### Python 代码

```python
class Inventory:
    def reserve(self, sku: str, n: int) -> None:
        print(f"预留 {sku} x{n}")


class Payment:
    def charge(self, user: str, amount: float) -> None:
        print(f"扣款 {user} {amount}")


class Shipping:
    def schedule(self, user: str, sku: str) -> None:
        print(f"发货 {user} {sku}")


class OrderFacade:
    """外观：编排库存、支付、物流。"""

    def __init__(self) -> None:
        self._inv = Inventory()
        self._pay = Payment()
        self._ship = Shipping()

    def place_order(self, user: str, sku: str, amount: float) -> None:
        self._inv.reserve(sku, 1)
        self._pay.charge(user, amount)
        self._ship.schedule(user, sku)
```

### 注意点

- Facade **不新增能力**，只简化访问；子系统仍可被高级客户端直连
- 别把 Facade 做成上帝类：职责仍是「一条用例的入口」

**口诀**：子系统很吵，Facade 一个口。

---

## 五、Proxy · 代理

### 意图

为对象提供替身，以控制访问（延迟、权限、远程、计数、缓存）。

### 信号

- 真正对象创建贵，先占位
- 调用前后要统一做鉴权/日志/限流

### 与 Decorator 区别

| | Proxy | Decorator |
|--|-------|-----------|
| 目的 | 控制访问 | 叠加职责 |
| 关系 | 常在创建期就定替身 | 常运行时多层嵌套 |
| 客户端 | 常以为自己在用真对象 | 明确在「包装」 |

### Python 代码：虚拟代理 + 保护代理味道

```python
from abc import ABC, abstractmethod
from typing import override


class Image(ABC):
    @abstractmethod
    def display(self) -> str: ...


class RealImage(Image):
    def __init__(self, path: str) -> None:
        self._path = path
        self._load()

    def _load(self) -> None:
        print(f"从磁盘加载 {self._path}")  # 昂贵

    @override
    def display(self) -> str:
        return f"显示 {self._path}"


class ImageProxy(Image):
    """懒加载：第一次 display 才创建 RealImage。"""

    def __init__(self, path: str) -> None:
        self._path = path
        self._real: RealImage | None = None

    @override
    def display(self) -> str:
        if self._real is None:
            self._real = RealImage(self._path)
        return self._real.display()


class AuthImageProxy(Image):
    """保护代理：无权限则拒绝。"""

    def __init__(self, inner: Image, *, allowed: bool) -> None:
        self._inner = inner
        self._allowed = allowed

    @override
    def display(self) -> str:
        if not self._allowed:
            raise PermissionError("无权查看图片")
        return self._inner.display()
```

**口诀**：真身太重或太危，代理挡在前。

---

## 六、Composite · 组合

### 意图

把对象组成树；客户端用**统一接口**对待单个对象与组合对象。

### 信号

- 部分-整体层次：目录/文件、菜单/菜单项、部门/员工

### 结构

```
Component
  + operation()
  + add/remove（可选）
     △
 Leaf          Composite
                 ◆── children: Component[]
```

### Python 代码

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import override


class FileSystemNode(ABC):
    @abstractmethod
    def size(self) -> int: ...

    @abstractmethod
    def display(self, indent: int = 0) -> None: ...


class FileLeaf(FileSystemNode):
    def __init__(self, name: str, nbytes: int) -> None:
        self.name = name
        self._nbytes = nbytes

    @override
    def size(self) -> int:
        return self._nbytes

    @override
    def display(self, indent: int = 0) -> None:
        print("  " * indent + f"- {self.name} ({self._nbytes}B)")


class Directory(FileSystemNode):
    def __init__(self, name: str) -> None:
        self.name = name
        self._children: list[FileSystemNode] = []

    def add(self, node: FileSystemNode) -> None:
        self._children.append(node)

    @override
    def size(self) -> int:
        return sum(c.size() for c in self._children)

    @override
    def display(self, indent: int = 0) -> None:
        print("  " * indent + f"[{self.name}]")
        for c in self._children:
            c.display(indent + 1)
```

**口诀**：叶子容器同一套接口，递归自然算。

---

## 七、Bridge / Flyweight（略写）

### Bridge

抽象（如 `Shape`）与实现（如 `Renderer`）分开，避免 `RedCircle / BlueSquare` 笛卡尔积爆炸。

```python
class Renderer(ABC):
    @abstractmethod
    def draw_circle(self, radius: float) -> str: ...


class Shape(ABC):
    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer
```

### Flyweight

把**不可变共享状态**（内蕴）抽到享元，外蕴状态由外部传入——如文字编辑器中每个字符的字形缓存。

面试提到「海量对象、大量重复」即可，不必默写完整实现。

---

## 八、选型速查

```
接口不匹配 → Adapter
要叠加功能 → Decorator
子系统太复杂 → Facade
控制访问/懒加载 → Proxy
树形部分-整体 → Composite
两维独立变化 → Bridge
重复状态占内存 → Flyweight
```

| 易混 | 分辨 |
|------|------|
| Adapter vs Facade | Adapter 转接口；Facade 简化多个接口 |
| Decorator vs Proxy | 增强 vs 控制 |
| Composite vs Decorator | 树组装 vs 链式包装 |

---

限流器案例里 Proxy/Decorator 味道常与 Strategy 一起出现。

下一篇：[行为型模式](patterns-behavioral.md)

---

[← 返回索引](index.md)
