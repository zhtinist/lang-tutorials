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

### 生活类比

国外买的电器插头跟国内插座形状不一样，插不进去，于是买一个「插头转换器」套在中间——电器本身不用改，插座也不用改，转换器负责两边都能对上。代码里接第三方 SDK 时经常遇到同样问题：接口形状不一样，中间加一层适配就好。

### 意图

让原本接口不匹配的类能一起工作——「插头转换器」。

### 信号

- 业务要 `PaymentGateway.charge`，第三方却是 `pay(cents)`
- 不想改第三方，也不想污染业务代码

### 不用Adapter会怎样

```python
class StripePaymentA:
    def __init__(self) -> None:
        self._sdk = LegacyStripeSDK()

    def charge(self, amount_yuan: float) -> str:
        # 每个用到 LegacyStripeSDK 的地方都要自己做"元转分"的换算
        cents = int(amount_yuan * 100)  # 忘了 round()，浮点误差可能让分数算错
        return self._sdk.pay(cents)["id"]


class StripePaymentB:
    def __init__(self) -> None:
        self._sdk = LegacyStripeSDK()

    def refund_charge(self, amount_yuan: float) -> str:
        # 另一个地方又写了一遍换算，这次用了 round()，两处逻辑不一致
        cents = int(round(amount_yuan * 100))
        return self._sdk.pay(-cents)["id"]
```

业务里只要用到第三方 SDK，就得在每个调用点各自重复一遍"元转分"的换算逻辑。`StripePaymentA` 忘了做四舍五入，`19.999` 元这种金额会因为浮点误差被截断成 `1999` 分而不是 `2000` 分；`StripePaymentB` 又用了不同的写法。两处转换逻辑各写各的，只要有一处少了 `round()` 或者进制换算写错，交易金额就会出现难以复现的对不上账问题。Adapter 把这段转换逻辑收敛到一个类里，只需要写对一次、测对一次。

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

### 生活类比

一杯咖啡可以加奶、加糖，还可以再加一份浓缩——每加一样都是在原来的基础上"套一层"，而不是为"加奶的咖啡""加奶加糖的咖啡"各开一个新品类。装饰器模式就是把这种"层层叠加"用代码表达出来。

### 意图

在**不修改原类**的前提下，动态叠加功能；装饰器与组件实现同一接口，可嵌套。

### 信号

- 「基础能力 + 可选增强」，增强可任意组合
- 用继承会导致子类爆炸（见 OOP 咖啡例子）

### 不用Decorator会怎样

```python
class CoffeeBad:
    def __init__(
        self,
        has_milk: bool = False,
        has_sugar: bool = False,
        has_extra_shot: bool = False,
    ) -> None:
        self.has_milk = has_milk
        self.has_sugar = has_sugar
        self.has_extra_shot = has_extra_shot

    def cost(self) -> float:
        price = 10.0
        if self.has_milk:
            price += 2.0
        if self.has_sugar:
            price += 1.0
        if self.has_extra_shot:
            price += 3.0
        return price

    def desc(self) -> str:
        d = "Espresso"
        if self.has_milk:
            d += " +Milk"
        if self.has_sugar:
            d += " +Sugar"
        if self.has_extra_shot:
            d += " +Shot"
        return d
```

加一种新配料（比如摩卡酱），就要在构造函数里加一个新的布尔参数，还要在 `cost()` 和 `desc()` 里各加一个新的 `if` 分支——两个方法必须保持同步更新，容易漏改一处。配料一多，构造函数的参数列表和两个方法里的 `if` 分支会同步爆炸式增长，而且大部分组合根本用不上（有人只想要"糖+摩卡酱"不要奶，构造函数却要求把三个参数都摆出来选）。Decorator 把每种配料做成一层独立的包装，配料数量增加只是多一个装饰器类，不用改任何已有类。

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

### 生活类比

去餐厅点"今日套餐"，不用自己分别点主菜、点汤、点甜点、再叮嘱厨房上菜顺序——服务员把这一堆流程打包成一句话："今日套餐一份"。Facade 就是给一堆繁琐的子系统调用包一个这样的简单入口。

### 意图

为复杂子系统提供一个**更高层的简单接口**，降低客户端耦合。

### 信号

- 做一件事要调 5 个服务、记一堆顺序
- 希望调用方只看到 `place_order()`

### 不用Facade会怎样

```python
class WebCheckout:
    def place_order(self, user: str, sku: str, amount: float) -> None:
        Inventory().reserve(sku, 1)
        Payment().charge(user, amount)
        Shipping().schedule(user, sku)


class MobileCheckout:
    def place_order(self, user: str, sku: str, amount: float) -> None:
        # 从 WebCheckout 复制过来，但顺序被改动了：先扣款，再占库存
        Payment().charge(user, amount)
        Inventory().reserve(sku, 1)
        Shipping().schedule(user, sku)
```

Web 端和移动端各自实现了一遍"下单"的调用顺序。`MobileCheckout` 里顺序反了：如果这时候库存其实已经不够，`Web` 端会在 `reserve` 失败时提前退出、不会真的扣款；但 `Mobile` 端因为先执行了 `charge`，等发现没货时用户已经被扣了钱，还得额外走一次退款流程。两处下单逻辑各自维护，只要有一处的调用顺序写错，就会出现这种资损风险。用 `OrderFacade.place_order()` 统一编排后，所有入口共用同一套正确顺序，不会出现"两个入口行为不一致"的情况。

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

### 生活类比

明星有经纪人挡在前面：粉丝找经纪人对接，经纪人决定要不要、什么时候把请求转给明星本人，中间还能顺便帮忙筛选、计费、安排日程。Proxy 就是给真正的对象安一个"经纪人"，调用方以为在跟真身打交道，实际先经过代理。

### 意图

为对象提供替身，以控制访问（延迟、权限、远程、计数、缓存）。

### 信号

- 真正对象创建贵，先占位
- 调用前后要统一做鉴权/日志/限流

### 不用Proxy会怎样

```python
class GalleryBad:
    """一次性把所有图片都真实加载，不管用户会不会翻到最后一张。"""

    def __init__(self, paths: list[str]) -> None:
        self._images = [RealImage(p) for p in paths]  # 1000 张图片,1000 次昂贵加载


gallery = GalleryBad([f"photo_{i}.jpg" for i in range(1000)])
# 还没显示任何一张图，构造 GalleryBad 就已经把 1000 次磁盘加载全跑完了
```

哪怕用户一张图都没翻到，构造 `GalleryBad` 时就要为全部 1000 张图片各付一次加载成本；如果用户只看了前 3 张就退出页面，后面 997 次加载完全是浪费的时间和内存。`ImageProxy` 把"真正加载"推迟到第一次调用 `display()` 才发生，没被用到的图片永远不会付出加载成本。

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

### 生活类比

文件夹里既可以放文件，也可以放文件夹（里面还能再放文件/文件夹），但不管你在处理一个文件还是一整个文件夹，"查看大小""删除"这些操作用起来都一样。Composite 就是把"部分"和"整体"用同一套接口对待，调用方不用区分自己拿到的是叶子还是一整棵树。

### 意图

把对象组成树；客户端用**统一接口**对待单个对象与组合对象。

### 信号

- 部分-整体层次：目录/文件、菜单/菜单项、部门/员工

### 不用Composite会怎样

```python
class FileLeafBad:
    def __init__(self, name: str, nbytes: int) -> None:
        self.name = name
        self.nbytes = nbytes


class DirectoryBad:
    def __init__(self, name: str) -> None:
        self.name = name
        self.children: list[object] = []


def total_size_bad(node: object) -> int:
    if isinstance(node, FileLeafBad):
        return node.nbytes
    elif isinstance(node, DirectoryBad):
        return sum(total_size_bad(c) for c in node.children)
    raise TypeError("未知节点类型")


def display_bad(node: object, indent: int = 0) -> None:
    if isinstance(node, FileLeafBad):
        print("  " * indent + f"- {node.name}")
    elif isinstance(node, DirectoryBad):
        print("  " * indent + f"[{node.name}]")
        for c in node.children:
            display_bad(c, indent + 1)
    else:
        raise TypeError("未知节点类型")
```

`total_size_bad` 和 `display_bad` 各写了一遍 `isinstance` 判断链。以后再加一种 `SymlinkNode` 节点类型，这两个函数、以及未来任何一个新写的"遍历文件树"的函数，都要记得同步加一个 `elif` 分支——漏掉一处就会在运行时抛 `TypeError`，或者悄悄漏算了某一类节点的大小却不报错。Composite 让 `FileLeaf` 和 `Directory` 实现同一个接口，新增操作只需要在这个接口里加一个方法，不用在调用方到处加分支。

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

生活类比：遥控器（抽象）和电视品牌（实现）是两回事——同一个遥控器的按键逻辑不用跟着每个电视品牌重写一遍，遥控器和电视各自能独立升级、独立扩展。

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

生活类比：印一本书时，重复出现的汉字不需要每次都重新画一份字形，大家共用同一份字形数据，只是打印的位置（外蕴状态）不同。

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
