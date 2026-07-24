# 创建型模式 · Creational Patterns

> 创建型模式解决「**对象怎么被创建**」：控制实例数量、隐藏构造细节、让创建逻辑可扩展。面试高频：**Singleton、Factory Method、Builder**。

---

## 一、总览

| 模式 | 意图 | 一句话信号 |
|------|------|------------|
| Singleton | 全局唯一实例 | 配置、日志、连接池「只要一个」 |
| Factory Method | 子类决定创建哪种产品 | 「new 哪种」会变，调用方不该 if |
| Abstract Factory | 创建一整族相关对象 | UI 主题、跨平台组件成套出现 |
| Builder | 分步构造复杂对象 | 构造参数爆炸 / 可选步骤多 |
| Prototype | 克隆已有对象 | 创建昂贵，或要基于模板复制 |

---

## 二、Singleton · 单例

### 生活类比

一个班级只需要一个班长，全班同学有事都找同一个人签字盖章，而不是每人自己"造"一个班长出来。程序里的全局配置、日志器、连接池也是这个道理：整个进程共用同一份，不需要也不该有第二份。

### 意图

保证一个类仅一个实例，并提供全局访问点。

### 信号

- 进程内共享的配置、指标收集器
- 面试里常被追问：**线程安全、测试污染、是否真需要**

### 结构

```
┌──────────────────┐
│    Singleton     │
├──────────────────┤
│ - _instance      │
│ + get_instance() │
└──────────────────┘
```

### Python 代码（推荐：模块单例）

```python
# config.py —— 模块本身就是单例（最 Pythonic）
APP_NAME = "parking-lot"
MAX_FLOORS = 5


# 需要类形式时：线程安全懒加载
from __future__ import annotations

import threading
from typing import Self


class AppConfig:
    """线程安全懒汉式单例。"""

    _instance: Self | None = None
    _lock = threading.Lock()

    def __init__(self) -> None:
        self.debug = False

    @classmethod
    def instance(cls) -> Self:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # double-check
                    cls._instance = cls()
        return cls._instance
```

### 注意点

| 点 | 说明 |
|----|------|
| 测试 | 全局状态难隔离；可考虑注入替代 |
| 多进程 | 每进程一个，不是分布式唯一 |
| `__new__` | 可实现，但模块级通常更清晰 |
| 滥用 | 「方便全局拿」≠ 该用单例 |

**口诀**：真要唯一再用；能注入就别全局。

---

## 三、Factory Method · 工厂方法

### 生活类比

点奶茶时你只说"要一杯珍珠奶茶"，至于用哪台机器、按什么配方去做，是店员（子类）的事，你不需要、也不该关心具体怎么造出来的。代码里同理：调用方只想要一个"产品"，创建哪个具体类交给工厂去决定。

### 意图

定义创建对象的接口，让**子类决定**实例化哪一个类。

### 信号

- 一堆 `if typ == "a": return A()` 散落业务代码
- 产品类型会扩展（OCP）

### 结构

```
Creator
  + factory_method()  ← 抽象
  + some_operation()  ← 调用 factory_method
      △
 ConcreteCreatorA / B
  + factory_method() → ProductA / B
```

### Python 代码

```python
from abc import ABC, abstractmethod
from typing import override


class Button(ABC):
    @abstractmethod
    def render(self) -> str: ...


class PrimaryButton(Button):
    @override
    def render(self) -> str:
        return "[Primary]"


class LinkButton(Button):
    @override
    def render(self) -> str:
        return "link→"


class Dialog(ABC):
    """创建者：业务逻辑依赖抽象 Button。"""

    @abstractmethod
    def create_button(self) -> Button:
        """工厂方法：子类决定具体按钮。"""
        ...

    def render(self) -> str:
        btn = self.create_button()
        return f"Dialog({btn.render()})"


class LoginDialog(Dialog):
    @override
    def create_button(self) -> Button:
        return PrimaryButton()


class AboutDialog(Dialog):
    @override
    def create_button(self) -> Button:
        return LinkButton()
```

### 简易版：函数/注册表工厂（面试常用）

```python
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def vehicle_factory(kind: str) -> "Vehicle":
    """简单工厂：集中 if；新类型仍改一处（可再升级为注册表）。"""
    table: dict[str, Callable[[], Vehicle]] = {
        "car": Car,
        "truck": Truck,
    }
    try:
        return table[kind]()
    except KeyError as e:
        raise ValueError(f"未知车型: {kind}") from e


class Vehicle(ABC):
    @abstractmethod
    def spot_size(self) -> int: ...


class Car(Vehicle):
    @override
    def spot_size(self) -> int:
        return 1


class Truck(Vehicle):
    @override
    def spot_size(self) -> int:
        return 2
```

**口诀**：new 藏进工厂；业务只认抽象产品。

---

## 四、Abstract Factory · 抽象工厂

### 生活类比

装修风格要统一：选了"北欧风"这个系列，沙发、灯具、窗帘就都从这一套里出，不会出现北欧沙发配美式灯具的违和感。代码里也是同理——要成套创建一族互相搭配的对象，而不是让调用方自己东拼西凑。

### 意图

提供一个接口，创建**一系列相关或依赖**的对象，而无需指定具体类。

### 信号

- 「成套」产品：深色主题按钮+输入框、Windows 风格全家桶
- 换一族实现，而不是换单个产品

### 结构

```
GUIFactory
  + create_button()
  + create_checkbox()
      △
 WinFactory / MacFactory
```

### Python 代码

```python
from abc import ABC, abstractmethod
from typing import override


class Button(ABC):
    @abstractmethod
    def paint(self) -> str: ...


class Checkbox(ABC):
    @abstractmethod
    def paint(self) -> str: ...


class WinButton(Button):
    @override
    def paint(self) -> str:
        return "WinBtn"


class MacButton(Button):
    @override
    def paint(self) -> str:
        return "MacBtn"


class WinCheckbox(Checkbox):
    @override
    def paint(self) -> str:
        return "WinCb"


class MacCheckbox(Checkbox):
    @override
    def paint(self) -> str:
        return "MacCb"


class GUIFactory(ABC):
    @abstractmethod
    def create_button(self) -> Button: ...

    @abstractmethod
    def create_checkbox(self) -> Checkbox: ...


class WinFactory(GUIFactory):
    @override
    def create_button(self) -> Button:
        return WinButton()

    @override
    def create_checkbox(self) -> Checkbox:
        return WinCheckbox()


class MacFactory(GUIFactory):
    @override
    def create_button(self) -> Button:
        return MacButton()

    @override
    def create_checkbox(self) -> Checkbox:
        return MacCheckbox()


def render_ui(factory: GUIFactory) -> str:
    """客户端依赖抽象工厂，保证一族组件风格一致。"""
    return f"{factory.create_button().paint()}+{factory.create_checkbox().paint()}"
```

### 与 Factory Method 对比

| | Factory Method | Abstract Factory |
|--|----------------|------------------|
| 焦点 | 一个产品层次 | 多个产品族 |
| 扩展 | 新创者子类 | 新工厂 + 一组产品 |
| 面试 | 更常见 | 讲清「族」即可 |

**口诀**：一家工厂出一套；风格不混搭。

---

## 五、Builder · 建造者

### 生活类比

点赛百味三明治：面包、蔬菜、酱料一步步选，最后组装成一份三明治。这比让你一次性把几十个参数（面包类型、五种蔬菜要不要、三种酱料放多少）塞进一个构造函数里舒服得多——复杂对象适合分步搭建，最后再一次性交付。

### 意图

将复杂对象的**构造过程**与表示分离；同一步骤可产出不同表示。

### 信号

- 构造函数 8+ 参数，还有很多可选
- 需要「流式」可读配置（URL、SQL、HTTP 请求）

### Python 代码（流式 Builder）

```python
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HttpRequest:
    method: str
    url: str
    headers: dict[str, str]
    body: str | None


class HttpRequestBuilder:
    """分步装配，最后 build 出不可变请求。"""

    def __init__(self) -> None:
        self._method = "GET"
        self._url = ""
        self._headers: dict[str, str] = {}
        self._body: str | None = None

    def method(self, m: str) -> HttpRequestBuilder:
        self._method = m
        return self

    def url(self, u: str) -> HttpRequestBuilder:
        self._url = u
        return self

    def header(self, k: str, v: str) -> HttpRequestBuilder:
        self._headers[k] = v
        return self

    def body(self, b: str) -> HttpRequestBuilder:
        self._body = b
        return self

    def build(self) -> HttpRequest:
        if not self._url:
            raise ValueError("url 必填")
        return HttpRequest(self._method, self._url, dict(self._headers), self._body)


req = (
    HttpRequestBuilder()
    .method("POST")
    .url("https://api.example.com/pay")
    .header("Content-Type", "application/json")
    .body('{"amount":10}')
    .build()
)
```

### 注意点

- Python 可用 `dataclass` + 默认值简化；参数极多时 Builder 仍更清晰
- Director（指挥者）可选：把固定步骤顺序封进类，面试提一句即可

**口诀**：步骤拆开建，最后再组装。

---

## 六、Prototype · 原型

### 生活类比

复印一份已经填好的表格，再在复印件上改几个字段，比从空白表格重新填一遍快得多。当创建一个对象要走很多初始化步骤或很贵时，直接"克隆"一份现成的，再改改需要变的地方，就是这个思路。

### 意图

通过**克隆**已有实例来创建新对象，避免昂贵初始化或复杂配置。

### 信号

- 对象创建成本高（游戏单位、文档模板）
- 需要「基于当前状态复制一份再改」

### Python 代码

```python
from __future__ import annotations

import copy
from dataclasses import dataclass, field


@dataclass
class Document:
    title: str
    paragraphs: list[str] = field(default_factory=list)
    meta: dict[str, str] = field(default_factory=dict)

    def clone(self) -> Document:
        """深拷贝：嵌套 list/dict 一并复制。"""
        return copy.deepcopy(self)


template = Document("周报模板", ["本周完成：", "风险："], {"owner": "team"})
report = template.clone()
report.title = "第42周周报"
report.paragraphs.append("下周计划：")
```

### 注意点

| 点 | 说明 |
|----|------|
| 浅拷贝 vs 深拷贝 | 可变嵌套结构通常要深拷贝 |
| `__dict__` / `copy` | 含文件句柄等不可随意 clone |
| 登记原型 | 可用字典缓存多种原型再 clone |

**口诀**：贵的别重做，拷一份再改。

---

## 七、面试怎么讲

| 模式 | 30 秒讲法 |
|------|-----------|
| Singleton | 「保证唯一，注意线程安全与可测性」 |
| Factory Method | 「把 new 藏起来，开闭扩展新产品」 |
| Abstract Factory | 「一次创建一族相关对象」 |
| Builder | 「复杂对象分步构造，避免巨型构造器」 |
| Prototype | 「克隆模板，避免重复初始化」 |

### 模式触发速查

```
只有一个？ → Singleton（先质疑）
类型分支多？ → Factory
成套主题？ → Abstract Factory
参数/步骤多？ → Builder
复制改改？ → Prototype
```

---

实战串联：停车场用简单工厂创建 Vehicle；计费用 Strategy（行为型）。

下一篇：[结构型模式](patterns-structural.md)

---

[← 返回索引](index.md)
