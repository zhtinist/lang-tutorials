# OOP 基础 · OOP Fundamentals

> 面向对象不是「处处写 class」，而是用 **封装** 藏细节、用 **抽象** 定契约、用 **多态** 换实现、用 **组合** 拼行为。

---

## 一、为什么要 OOP？

过程式代码把「数据」和「操作」拆开：函数散落各处，改一处牵一片。OOP 把**相关数据与行为绑在一起**，通过边界控制复杂度。

| 对比 | 过程式 | 面向对象 |
|------|--------|----------|
| 组织方式 | 函数 + 全局/结构体 | 对象（状态 + 行为） |
| 扩展方式 | 改函数 / 加 if | 加新类 / 换实现 |
| 典型风险 | 全局状态、隐式耦合 | 过度继承、上帝类 |

**口诀**：对象 = 状态 + 行为；设计围绕「变化点」展开。

---

## 二、封装 · Encapsulation

### 生活类比

银行不会让你直接伸手去柜台后面改自己账户余额的数字，你只能通过存款、取款这些"窗口"操作，银行在背后保证余额不会被改成负数。封装就是这个道理：外部不能直接摸内部状态，只能通过受控的"窗口"（方法）打交道。

### 意图

把内部状态藏起来，只通过受控接口访问。外部不该直接改字段，否则任何调用方都能破坏不变量。

核心原则：先「把数据和方法包成对象」，再谈继承。

### 反例：公开可变状态

```python
class BankAccountBad:
    def __init__(self, balance: float) -> None:
        self.balance = balance  # 任何人都能写成负数


acc = BankAccountBad(100)
acc.balance = -999  # 不变量被破坏
```

如果 `BankAccountBad` 被后台对账脚本、月度报表脚本等十几处代码分别引用，任何一处不小心写了类似 `acc.balance -= fee` 的语句，都可能让账户余额变成负数——而且这种改动可以发生在代码库任何一个角落，出问题后很难追查是谁、在哪一次改动里弄坏了余额。用 `_balance` + `withdraw()` 之后，只有一个入口做校验，出问题只需要查这一个方法。

### 正例：私有 + 方法维护不变量

```python
class BankAccount:
    """银行账户：余额只能通过 deposit/withdraw 修改。"""

    def __init__(self, balance: float = 0.0) -> None:
        if balance < 0:
            raise ValueError("初始余额不能为负")
        self._balance = balance  # 约定：单下划线 = 内部使用

    @property
    def balance(self) -> float:
        """只读视图。"""
        return self._balance

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("存款金额必须为正")
        self._balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("取款金额必须为正")
        if amount > self._balance:
            raise ValueError("余额不足")
        self._balance -= amount
```

### 要点

| 点 | 说明 |
|----|------|
| `_name` | 约定私有，非强制 |
| `__name` | 名称改写，少用；封装靠约定与 API |
| property | 对外像字段，对内可校验 |
| 不变量 | 构造与每个写方法都要维护 |

---

## 三、继承 · Inheritance

### 生活类比

儿子继承了爸爸的手艺：会做爸爸会做的那些菜（复用了父辈的"接口"），但也可以有自己的拿手绝活。继承表达的就是这种"是一种"的类型关系——狗是一种动物，猫也是一种动物，都具备"动物"该有的基本能力，各自又有自己的实现。

### 意图

「是一个」(is-a) 关系：子类复用父类接口与实现，表达类型层次。

### 例：动物叫声

```python
from abc import ABC, abstractmethod


class Animal(ABC):
    """抽象动物：规定会叫，具体叫声由子类决定。"""

    def __init__(self, name: str) -> None:
        self.name = name

    @abstractmethod
    def speak(self) -> str:
        """发出叫声。"""
        ...

    def introduce(self) -> str:
        return f"我是 {self.name}，{self.speak()}"


class Dog(Animal):
    def speak(self) -> str:
        return "汪汪"


class Cat(Animal):
    def speak(self) -> str:
        return "喵"
```

### 危险：为了复用而继承

继承同时带来**接口承诺**。子类必须能替代父类（见 SOLID 的 LSP）。若只是想复用几行代码，优先组合。

```python
# 坏味道：Stack 继承 list —— 暴露了 insert/remove 等不该有的接口
class StackBad(list):
    def push(self, x: int) -> None:
        self.append(x)

    def pop_top(self) -> int:
        return self.pop()
```

如果调用方对 `StackBad` 实例调用了从 `list` 继承来的 `insert(0, x)`，元素会被插到栈底而不是栈顶，"后进先出"的语义就被悄悄破坏了；后续代码里但凡有逻辑依赖"`pop()` 拿到的就是最后一次 `push` 的元素"这个假设（比如一个撤销栈），就会出现顺序错乱的 bug。而且 IDE 不会对这种误用发出任何警告，因为 `insert` 本来就是 `list` 合法的公开方法，`StackBad` 继承过来后一样能调用。

---

## 四、多态 · Polymorphism

### 生活类比

同一个"播放"按钮，不管接的是 CD 机、DVD 机还是流媒体盒子，按下去执行的具体动作完全不同，但你作为使用者不需要关心内部怎么实现——这就是多态：同一个指令，不同设备各自用自己的方式响应。

### 意图

同一接口，不同实现；调用方依赖抽象，运行时绑定具体行为。

```python
def greet_all(animals: list[Animal]) -> None:
    """调用方只认 Animal，不关心 Dog/Cat。"""
    for a in animals:
        print(a.introduce())


greet_all([Dog("旺财"), Cat("咪咪")])
```

### Python 中的多态形态

| 形态 | 含义 | 例子 |
|------|------|------|
| 子类型多态 | 继承/实现同一抽象 | `Animal.speak` |
| 鸭子类型 | 有同名方法即可 | `len` / `__len__` |
| 协议 Protocol | 静态检查的鸭子类型 | `typing.Protocol` |

```python
from typing import Protocol


class Drawable(Protocol):
    def draw(self) -> str: ...


class Circle:
    def draw(self) -> str:
        return "○"


def render(items: list[Drawable]) -> None:
    for item in items:
        print(item.draw())
```

---

## 五、抽象 · Abstraction

### 生活类比

点外卖时你只关心"下单、收到餐"这件事，完全不关心后厨具体怎么炒的菜、用了几个锅。抽象就是只暴露"做什么"（下单接口），把"怎么做"（具体烹饪过程）交给背后的实现去负责。

### 意图

抓住「做什么」，隐藏「怎么做」。抽象类 / 接口定义契约；具体类负责实现。

```python
from abc import ABC, abstractmethod
from typing import override


class PaymentGateway(ABC):
    """支付网关抽象：业务只依赖这个接口。"""

    @abstractmethod
    def charge(self, amount: float, currency: str) -> str:
        """扣款，返回交易 id。"""
        ...


class StripeGateway(PaymentGateway):
    @override
    def charge(self, amount: float, currency: str) -> str:
        # 真实环境会调 SDK；这里示意
        return f"stripe_{amount}_{currency}"


class CheckoutService:
    def __init__(self, gateway: PaymentGateway) -> None:
        self._gateway = gateway  # 依赖抽象

    def pay(self, amount: float) -> str:
        return self._gateway.charge(amount, "CNY")
```

**口诀**：业务依赖抽象；细节关在实现类里。

---

## 六、组合优于继承 · Composition over Inheritance

### 生活类比

搭乐高积木时，你是把一个个零件拼在一起、想换随时拆下来换一块；而不是把积木刻成一整块实心雕像，改一处就得重新雕。组合就是"拼零件"：把行为拆成一个个独立组件，装进对象里，需要换的时候直接换掉那个组件。

### 为什么？

继承是编译期绑死的「白箱」复用：父类改动，所有子类受影响。组合是「黑箱」：把行为委托给组件，可运行时替换。

### 反例：用继承堆功能

```python
class Coffee:
    def cost(self) -> float:
        return 10.0


class MilkCoffee(Coffee):
    def cost(self) -> float:
        return super().cost() + 2.0


class SugarMilkCoffee(MilkCoffee):
    def cost(self) -> float:
        return super().cost() + 1.0
# 配料一多，子类爆炸
```

如果奶、糖、加浓缩之外，还要支持摩卡酱、椰奶、燕麦奶……N 种配料理论上有 `2^N` 种组合方式；如果每种组合都对应继承树上的一个子类，配料每增加一种，子类数量就成倍增长——加到第 10 种配料时，理论组合数已经超过 1000 种，没人会真的为每种组合都建一个子类，最后往往是"想要的组合没有对应的类，只好现改代码"。

### 正例：组合配料

```python
from dataclasses import dataclass, field


@dataclass
class Coffee:
    base_price: float = 10.0
    addons: list[float] = field(default_factory=list)

    def add(self, price: float) -> None:
        self.addons.append(price)

    def cost(self) -> float:
        return self.base_price + sum(self.addons)


c = Coffee()
c.add(2.0)  # 牛奶
c.add(1.0)  # 糖
assert c.cost() == 13.0
```

更完整的「动态加配料」见结构型模式里的 Decorator。

### 决策表

| 问自己 | 选继承 | 选组合 |
|--------|--------|--------|
| 是严格 is-a？ | ✓ | |
| 只是想复用代码？ | | ✓ |
| 行为要运行时切换？ | | ✓ |
| 子类会推翻父类约定？ | 别继承 | ✓ |

---

## 七、Python 面向对象速查

```python
from dataclasses import dataclass
from enum import Enum, auto


class Role(Enum):
    ADMIN = auto()
    USER = auto()


@dataclass(frozen=True, slots=True)
class UserId:
    """值对象：不可变身份标识。"""
    value: str


@dataclass
class User:
    id: UserId
    name: str
    role: Role = Role.USER

    def is_admin(self) -> bool:
        return self.role is Role.ADMIN
```

| 工具 | 用途 |
|------|------|
| `@dataclass` | 少写样板 `__init__` |
| `Enum` | 有限集合状态/角色 |
| `ABC` + `@abstractmethod` | 抽象基类 |
| `Protocol` | 结构化类型 |
| `@override` (3.12+) | 标明重写，防拼写错误 |

---

## 八、小结口诀

```
封装藏状态，抽象定契约；
多态换实现，组合拼变化。
先问 is-a 真不真，再谈要不要继承。
```

| 特性 | 一句话 |
|------|--------|
| 封装 | 不让外部乱改内部状态 |
| 继承 | is-a 层次复用 |
| 多态 | 同一接口多种实现 |
| 抽象 | 只暴露必要契约 |
| 组合 | 把变化的部分嵌进来 |

---

下一篇：[SOLID 原则](solid-principles.md)

---

[← 返回索引](index.md)
