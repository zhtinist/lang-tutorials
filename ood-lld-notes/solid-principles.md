# SOLID 原则 · SOLID Principles

> SOLID 是五个**可扩展、可测试**的设计检查点：单一职责、开闭、里氏替换、接口隔离、依赖倒置。面试时用来自检类图，不是教条。

---

## 一、总览

| 字母 | 原则 | 一句话 |
|------|------|--------|
| S | Single Responsibility | 一个类只有一个引起它变化的理由 |
| O | Open/Closed | 对扩展开放，对修改关闭 |
| L | Liskov Substitution | 子类必须能替换父类而不破坏程序 |
| I | Interface Segregation | 不要强迫客户端依赖用不到的方法 |
| D | Dependency Inversion | 依赖抽象，不要依赖具体实现 |

---

## 二、SRP · 单一职责原则

### 生活类比

一个人又要当厨师、又要当收银员、又要当保洁，忙的时候一件事没做好，其他事全跟着乱。餐厅分工明确——厨师专心做菜、收银员专心结账——出问题时容易定位是哪个环节。类的职责也一样：一个类揽的事太杂，改一处容易牵连另一处。

### 意图

一个模块/类只负责一块业务变化。职责混杂 → 改 A 功能却弄坏 B。

### 反例

```python
class UserServiceBad:
    """既管用户，又管邮件，又管持久化 —— 三个变化理由。"""

    def create_user(self, email: str) -> None:
        # 写数据库
        print(f"INSERT user {email}")
        # 发欢迎邮件
        print(f"SMTP send to {email}")
        # 打审计日志
        print(f"AUDIT create {email}")
```

```python
def send_welcome_email(email: str) -> None:
    raise TimeoutError("SMTP 超时")  # 假设邮件服务这次超时了


class UserServiceBad2:
    def create_user(self, email: str) -> None:
        print(f"INSERT user {email}")   # 用户已经成功写入数据库
        send_welcome_email(email)        # 这里抛出异常
        print(f"AUDIT create {email}")   # 这一行永远不会被执行到
```

写库、发邮件、记审计日志三件事绑在同一个方法里，其中任何一步出错都会连累另外两步。这里 SMTP 超时的异常本该只影响"发欢迎邮件"这一件次要的事，却因为写在同一个方法里，把调用方对`create_user` 的整体调用直接打断——调用方看到的是"建号失败"的异常，但其实用户已经写进数据库了，审计日志这一步也被跳过、以后查不到这条创建记录。拆成 `UserService` + `EmailSender` + `Auditor` 之后，`EmailSender` 出错不会波及 `UserRepository.save()` 已经完成的部分。

### 正例

```python
from typing import Protocol


class UserRepository(Protocol):
    def save(self, email: str) -> None: ...


class EmailSender(Protocol):
    def send_welcome(self, email: str) -> None: ...


class Auditor(Protocol):
    def log_create(self, email: str) -> None: ...


class UserService:
    """只编排「创建用户」用例，细节交给协作对象。"""

    def __init__(
        self,
        repo: UserRepository,
        mailer: EmailSender,
        auditor: Auditor,
    ) -> None:
        self._repo = repo
        self._mailer = mailer
        self._auditor = auditor

    def create_user(self, email: str) -> None:
        self._repo.save(email)
        self._mailer.send_welcome(email)
        self._auditor.log_create(email)
```

**口诀**：一个类，一件事；变化理由数一数。

---

## 三、OCP · 开闭原则

### 生活类比

手机想要新功能，是装一个新 App，而不是拆开手机去改主板电路。已经跑得好好的老代码最好也这样对待：新增一个能力时优先"装个新插件"（新类），而不是把已经验证过的老逻辑翻出来改一遍、担心改出新 bug。

### 意图

加新能力时，优先**新增代码**（新类），而不是改遍已有 `if/else`。

### 反例

```python
def discount_bad(customer_type: str, price: float) -> float:
    if customer_type == "normal":
        return price
    elif customer_type == "vip":
        return price * 0.9
    elif customer_type == "svip":
        return price * 0.8
    # 每加一种客户，都要改这个函数
    raise ValueError(customer_type)
```

新增一种客户类型时，工程师要在 `discount_bad` 这同一个函数里插入新的 `elif`。如果不小心把已有的 `elif customer_type == "vip"` 那一行顺手改动了一下（比如复制粘贴时误改了返回值），`vip` 客户的折扣就会被新逻辑覆盖掉——而这个改动是在做"新增 svip"这个完全不相关的需求时引入的。测试如果只覆盖了新增的 svip 场景，没有重新跑一遍所有老客户类型的回归用例，这个错误就会被放过直接上线。`Checkout` 依赖 `DiscountPolicy` 接口后，新增 `SvipDiscount` 是一个全新的类，不会碰到 `VipDiscount` 已经写好并测试过的代码。

### 正例：策略扩展

```python
from abc import ABC, abstractmethod
from typing import override


class DiscountPolicy(ABC):
    @abstractmethod
    def apply(self, price: float) -> float: ...


class NormalDiscount(DiscountPolicy):
    @override
    def apply(self, price: float) -> float:
        return price


class VipDiscount(DiscountPolicy):
    @override
    def apply(self, price: float) -> float:
        return price * 0.9


class Checkout:
    def __init__(self, policy: DiscountPolicy) -> None:
        self._policy = policy

    def total(self, price: float) -> float:
        return self._policy.apply(price)


# 新客户类型：新增类即可，Checkout 不用改
class SvipDiscount(DiscountPolicy):
    @override
    def apply(self, price: float) -> float:
        return price * 0.8
```

**口诀**：新需求加新类；少改老代码。

---

## 四、LSP · 里氏替换原则

### 生活类比

如果说明书写着"这台机器认硬币"，那换一台"认硬币"的新机器进去，行为应该照旧能用，不能突然要求投纸币才行。子类替换父类也是同理：调用方原本对父类的假设，换成子类后不能被打破，否则这个"is-a"关系就是假的。

### 意图

凡是用父类型的地方，换成子类型，行为仍满足父类型的契约（前置不加强、后置不削弱、不变量保持）。

### 经典反例：正方形不是可可变长宽的矩形

```python
class Rectangle:
    def __init__(self, w: float, h: float) -> None:
        self._w, self._h = w, h

    def set_width(self, w: float) -> None:
        self._w = w

    def set_height(self, h: float) -> None:
        self._h = h

    def area(self) -> float:
        return self._w * self._h


class Square(Rectangle):
    """看似 is-a，却破坏了「可独立改宽高」的契约。"""

    def set_width(self, w: float) -> None:
        self._w = self._h = w

    def set_height(self, h: float) -> None:
        self._w = self._h = h


def enlarge_width(rect: Rectangle) -> None:
    """调用方假设：只改宽，高不变。"""
    old_h = rect._h
    rect.set_width(rect._w + 10)
    assert rect._h == old_h  # Square 会失败
```

如果 `enlarge_width` 是某个批量调整报表列宽功能的一部分，一旦传入的 `Rectangle` 列表里混入了一个 `Square` 实例，这一列的宽高就会被同步改乱，报表在这一列上出现错误的版式——而这个 bug 只有在数据里恰好出现了 `Square` 时才会触发，代码审查阶段很难被发现，因为 `Square(Rectangle)` 这行继承声明本身看起来完全合理。

### 正例：取消错误继承，用共同抽象

```python
from abc import ABC, abstractmethod


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class RectangleShape(Shape):
    def __init__(self, w: float, h: float) -> None:
        self._w, self._h = w, h

    def area(self) -> float:
        return self._w * self._h


class SquareShape(Shape):
    def __init__(self, side: float) -> None:
        self._side = side

    def area(self) -> float:
        return self._side * self._side
```

**口诀**：能替换才继承；契约不能偷梁换柱。

---

## 五、ISP · 接口隔离原则

### 生活类比

办一张健身卡，结果被要求连游泳、瑜伽、拳击课全部一起签约，哪怕你只想举铁。接口也是同理：接口太"胖"，会强迫实现它的类被迫接下一堆自己根本用不到的方法。

### 意图

接口要小而专。胖接口逼着实现类写一堆空方法或 `NotImplementedError`。

### 反例

```python
from abc import ABC, abstractmethod


class WorkerBad(ABC):
    @abstractmethod
    def work(self) -> None: ...

    @abstractmethod
    def eat(self) -> None: ...


class Robot(WorkerBad):
    def work(self) -> None:
        print("焊接")

    def eat(self) -> None:
        raise NotImplementedError("机器人不吃饭")  # 被迫实现
```

```python
workers: list[WorkerBad] = [Robot(), Robot()]
for w in workers:
    w.work()
    w.eat()  # 循环到第一个 Robot 就在这里抛出 NotImplementedError
```

如果这段代码原本是想批量巡检所有 `Worker` 的工作状态，一旦遍历到 `Robot`，`eat()` 抛出的 `NotImplementedError` 会让整个循环直接中断——不仅这一台 Robot 没检查完，后面排在它之后的所有 worker 都不会被处理到。拆成 `Workable` / `Eatable` 两个小接口后，`Robot` 只实现 `Workable`，巡检代码只需要遍历 `Workable`，天然不会调用到 `Robot` 没有的 `eat()`。

### 正例

```python
from abc import ABC, abstractmethod
from typing import override


class Workable(ABC):
    @abstractmethod
    def work(self) -> None: ...


class Eatable(ABC):
    @abstractmethod
    def eat(self) -> None: ...


class Human(Workable, Eatable):
    @override
    def work(self) -> None:
        print("写代码")

    @override
    def eat(self) -> None:
        print("吃饭")


class Robot(Workable):
    @override
    def work(self) -> None:
        print("焊接")
```

**口诀**：接口宜细不宜肥；用不到就别塞。

---

## 六、DIP · 依赖倒置原则

### 生活类比

家里的插座是标准接口，你可以插台灯、插风扇、插充电器，插座不用管你具体插的是什么品牌的电器；反过来，只要电器插头符合标准，也不用关心背后是哪家电网供电。高层代码依赖的应该是这样的"标准接口"，而不是死死绑定某个具体实现。

### 意图

高层模块不依赖低层模块的具体类；双方都依赖抽象。控制权反转：谁实现细节，由外部注入。

### 反例

```python
class MySQLOrderRepo:
    def save(self, order_id: str) -> None:
        print(f"mysql save {order_id}")


class OrderServiceBad:
    def __init__(self) -> None:
        self._repo = MySQLOrderRepo()  # 高层钉死低层

    def place(self, order_id: str) -> None:
        self._repo.save(order_id)
```

如果团队决定把数据库从 MySQL 换成 PostgreSQL，或者只是想在单元测试里不真的连数据库，`OrderServiceBad.__init__` 里 `self._repo = MySQLOrderRepo()` 这一行把具体实现焊死在了构造函数内部——测试 `place()` 的业务逻辑时也必须先启动一个真实的 MySQL、清空数据、再断言，每条测试都又慢又脆弱。`OrderService` 改成接收 `OrderRepository` 接口之后，测试时注入 `InMemoryOrderRepo` 即可，不用连真实数据库。

### 正例

```python
from typing import Protocol


class OrderRepository(Protocol):
    def save(self, order_id: str) -> None: ...


class MySQLOrderRepo:
    def save(self, order_id: str) -> None:
        print(f"mysql save {order_id}")


class InMemoryOrderRepo:
    def __init__(self) -> None:
        self._data: list[str] = []

    def save(self, order_id: str) -> None:
        self._data.append(order_id)


class OrderService:
    def __init__(self, repo: OrderRepository) -> None:
        self._repo = repo  # 依赖抽象，测试可注入内存实现

    def place(self, order_id: str) -> None:
        self._repo.save(order_id)
```

**口诀**：细节跟抽象走；注入替换实现。

---

## 七、面试自检清单

画完类图或写完骨架，快速过一遍：

| # | 问题 | 对应原则 |
|---|------|----------|
| 1 | 这个类有几个「变化理由」？能否拆？ | SRP |
| 2 | 新需求是改 `if` 还是加新类？ | OCP |
| 3 | 子类替换父类后，测试/断言还成立吗？ | LSP |
| 4 | 有没有实现类对某接口方法直接 `raise`？ | ISP |
| 5 | 高层是否 `new` 了具体基础设施类？ | DIP |
| 6 | 继承树是否可用组合 + 接口代替？ | 组合优先 |

### 和设计模式的关系

| 原则 | 常搭模式 |
|------|----------|
| OCP | Strategy、Decorator、Factory |
| DIP | Factory、Abstract Factory、DI 容器 |
| ISP | 拆接口；Facade 对外仍可粗 |
| LSP | 慎用继承；State/Strategy 常更安全 |

---

## 八、小结口诀

```
单责拆干净，开闭加新类；
替换守契约，接口别太胖；
依赖倒向抽象，组合胜继承。
```

---

下一篇：[UML 类图基础](uml-basics.md)

---

[← 返回索引](index.md)
