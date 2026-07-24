# 行为型模式 · Behavioral Patterns

> 行为型模式关注「**对象之间如何分工与通信**」：把算法、状态迁移、事件通知从硬编码 `if` 里解放出来。面试高频：**Strategy、Observer、State、Template Method、Command、Chain of Responsibility**。

---

## 一、总览

| 模式 | 意图 | 信号 |
|------|------|------|
| Strategy | 封装可互换算法 | 计费/排序/限流算法可切换 |
| Observer | 一对多通知 | 订阅、事件、GUI 监听 |
| State | 对象行为随内部状态变 | 电梯、订单、连接生命周期 |
| Template Method | 骨架固定、步骤可覆写 | 同样流程不同细节 |
| Command | 请求封装成对象 | 撤销、队列、宏命令 |
| Chain of Responsibility | 请求沿链传递 | 过滤、审批、中间件 |
| Iterator（略） | 顺序访问聚合 | `for x in agg` |
| Mediator（略） | 中介解耦网状通信 | 聊天室、对话框组件 |

---

## 二、Strategy · 策略（LLD 最常用）

### 生活类比

去外地旅游，可以选择坐飞机、坐高铁或者自驾，目的地都是同一个（到达那座城市），但走法（算法）随时能换一种，互不影响"旅行"这件事本身。计费规则、排序方式、限流算法也是同理：目标不变，具体算法可以插拔替换。

### 意图

定义算法族，分别封装，使它们可互换；算法变化独立于使用方。

### 信号

- 计费规则、推荐策略、压缩算法、限流算法
- 想符合 OCP：加新算法不改上下文类

### 不用Strategy会怎样

```python
class ParkingLotBad:
    def __init__(self, fee_kind: str) -> None:
        self._fee_kind = fee_kind

    def quote(self, hours: int) -> float:
        if self._fee_kind == "hourly":
            return hours * 5
        elif self._fee_kind == "daily":
            return -(-hours // 24) * 40
        raise ValueError(self._fee_kind)

    def refund_quote(self, hours: int) -> float:
        # 退款要用同一套计费公式，于是把上面的 if-elif 复制了一遍
        if self._fee_kind == "hourly":
            return hours * 5 * 0.5
        elif self._fee_kind == "daily":
            return -(-hours // 24) * 40 * 0.5
        raise ValueError(self._fee_kind)
```

`quote()` 和 `refund_quote()` 各自复制了一份"按小时/按天"的计费判断。产品新增一种"月租价"时，要同时改这两个方法里的 `if-elif`，一旦漏改一处（比如只改了 `quote` 忘了改 `refund_quote`），退款金额和实际收费金额的计算规则就会悄悄对不上，而这种不一致只有在用户申请退款时才会暴露。

### 结构

```
Context ──▶ Strategy(<<interface>>)
                 △
          StratA / StratB / StratC
```

### Python 代码

```python
from abc import ABC, abstractmethod
from datetime import timedelta
from typing import override


class FeeStrategy(ABC):
    @abstractmethod
    def calculate(self, duration: timedelta) -> float:
        """根据停车时长算费用。"""
        ...


class HourlyFee(FeeStrategy):
    def __init__(self, rate: float = 5.0) -> None:
        self._rate = rate

    @override
    def calculate(self, duration: timedelta) -> float:
        seconds = int(duration.total_seconds())
        hours = max(1, -(-seconds // 3600))  # 向上取整,恰好整点不多算
        return hours * self._rate


class DailyFee(FeeStrategy):
    def __init__(self, rate: float = 40.0) -> None:
        self._rate = rate

    @override
    def calculate(self, duration: timedelta) -> float:
        seconds = int(duration.total_seconds())
        days = max(1, -(-seconds // 86400))  # 向上取整,恰好整天不多算
        return days * self._rate


class ParkingLot:
    def __init__(self, fee: FeeStrategy) -> None:
        self._fee = fee

    def set_fee_strategy(self, fee: FeeStrategy) -> None:
        self._fee = fee  # 运行时可切换

    def quote(self, duration: timedelta) -> float:
        return self._fee.calculate(duration)
```

**口诀**：变化的算法抽接口；Context 只调抽象。

---

## 三、Observer · 观察者

### 生活类比

就像你订阅了一个博主：博主发新内容会主动通知所有订阅者，而不是每个订阅者自己每隔几分钟跑去刷新页面问"更新了吗"。Observer 模式就是把这种"一方变化、自动通知多方"的关系写成代码。

### 意图

对象状态变化时，自动通知所有依赖者（发布-订阅）。

### 信号

- 库存变更通知 UI / 邮件 / 指标
- 解耦「事件源」与「反应方」

### 不用Observer会怎样

```python
class OrderServiceBad:
    def place(self, order_id: str) -> None:
        print(f"创建订单 {order_id}")  # 订单已经创建成功
        email_service.send(order_id)
        metrics_service.record("order_placed")
        sms_service.send(order_id)  # 假设短信服务网络超时，这里抛出异常
        print("这行代码不会被执行到")
```

发邮件、发短信、记指标这些"附加动作"和"创建订单"这个核心业务逻辑写在同一个方法里。如果短信服务网络超时抛出异常，整个 `place()` 方法会跟着中断退出——用户的订单其实已经创建成功，调用方却因为发短信失败而收到"下单失败"的报错。而且以后每加一个新通知渠道（比如 Slack 群通知），都要回来改这个核心下单方法，改错了同样可能连累下单本身。

### Python 代码

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import override


class Observer(ABC):
    @abstractmethod
    def update(self, event: str, payload: dict[str, str]) -> None: ...


class Subject:
    def __init__(self) -> None:
        self._observers: list[Observer] = []

    def attach(self, obs: Observer) -> None:
        self._observers.append(obs)

    def detach(self, obs: Observer) -> None:
        self._observers.remove(obs)

    def notify(self, event: str, payload: dict[str, str]) -> None:
        for obs in list(self._observers):
            obs.update(event, payload)


class OrderService(Subject):
    def place(self, order_id: str) -> None:
        # ... 下单逻辑
        self.notify("order_placed", {"order_id": order_id})


class EmailNotifier(Observer):
    @override
    def update(self, event: str, payload: dict[str, str]) -> None:
        if event == "order_placed":
            print(f"邮件: 订单 {payload['order_id']} 已创建")


class MetricsNotifier(Observer):
    @override
    def update(self, event: str, payload: dict[str, str]) -> None:
        print(f"指标 +1: {event}")
```

### 注意点

- 通知顺序、异常隔离（一个观察者失败别拖垮整链）
- 与消息队列：进程内 Observer；跨服务用 MQ（思想类似）

**口诀**：主题发事件，观察者各自忙。

---

## 四、State · 状态

### 生活类比

电梯门开着、正在维保的时候，你按"上楼"按钮是没反应的；只有电梯处于"空闲"状态时，同样的按钮才会生效——同一个操作，在不同状态下反应完全不同。与其写一大堆 `if state == "idle"` 判断当前处于哪个状态，不如把每个状态各自封装成一个类，各管各的行为。

### 意图

对象在不同状态下有不同行为；把每个状态封装成类，去掉巨大 `if state ==`。

### 信号

- 电梯：停靠/上行/下行/维护
- 订单：已创建→已支付→已发货→完成
- TCP：监听/已连接/关闭

### 不用State会怎样

```python
class ElevatorBad:
    def __init__(self) -> None:
        self.state = "idle"  # 用字符串表示状态
        self.floor = 1

    def request(self, to_floor: int) -> None:
        if self.state == "idle":
            if to_floor == self.floor:
                return
            print(f"从 {self.floor} 前往 {to_floor}")
            self.state = "moving"
            self.floor = to_floor
            self.state = "idle"
            print("到达，空闲")
        elif self.state == "moving":
            print("移动中，请求入队（示意）")
        elif self.state == "maintenance":
            print("维护中，拒绝请求")
        # 新增一种 "door_open" 状态时，上面每个分支都可能需要跟着改一遍
        # 哪个分支漏加了对应判断，电梯门开着的时候就可能被派发新任务
```

状态用字符串保存，判断散落在一个大 `if-elif` 里。系统要加一个新状态"门已打开"时，需要回头检查每一个已有分支要不要拒绝这个新状态下的请求——漏掉一个分支，电梯门开着的时候仍然会响应楼层请求。State 模式把每个状态封装成独立的类，新增状态只需要新增一个类，不用逐个检查所有旧分支。

### 与 Strategy 区别

| | Strategy | State |
|--|----------|-------|
| 谁决定切换 | 常由客户端注入 | 常由状态对象内部触发 |
| 语义 | 可互换算法 | 生命周期状态机 |
| 面试话术 | 「换算法」 | 「换状态」 |

### Python 代码（简化电梯）

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import override


class Elevator:
    def __init__(self) -> None:
        self._state: ElevatorState = IdleState(self)
        self.floor = 1

    def set_state(self, state: ElevatorState) -> None:
        self._state = state

    def request(self, to_floor: int) -> None:
        self._state.handle_request(to_floor)


class ElevatorState(ABC):
    def __init__(self, ctx: Elevator) -> None:
        self._ctx = ctx

    @abstractmethod
    def handle_request(self, to_floor: int) -> None: ...


class IdleState(ElevatorState):
    @override
    def handle_request(self, to_floor: int) -> None:
        if to_floor == self._ctx.floor:
            return
        print(f"从 {self._ctx.floor} 前往 {to_floor}")
        self._ctx.set_state(MovingState(self._ctx))
        self._ctx.floor = to_floor
        self._ctx.set_state(IdleState(self._ctx))
        print("到达，空闲")


class MovingState(ElevatorState):
    @override
    def handle_request(self, to_floor: int) -> None:
        print("移动中，请求入队（示意）")
```

**口诀**：状态成类，迁移清晰；告别状态枚举大 if。

---

## 五、Template Method · 模板方法

### 生活类比

泡茶和泡咖啡的步骤骨架是一样的：烧水 → 冲泡 → 倒出来。骨架不用每次重写，只是"冲泡"这一步具体做法不同（茶叶闷多久、咖啡怎么萃取）。Template Method 就是把这个固定流程写在父类，把因人而异的步骤留给子类去填。

### 意图

在父类定义算法骨架，将某些步骤延迟到子类；固定流程、开放细节。

### 信号

- 数据导入：校验→转换→写入，各源细节不同
- 游戏 AI 回合：感知→决策→执行

### 不用Template Method会怎样

```python
class CsvImporterBad:
    def run(self, data: list[dict[str, str]] | None) -> int:
        if not data:  # 空列表或 None 都算异常
            raise ValueError("空数据")
        return len(data)


class JsonImporterBad:
    def run(self, data: list[dict[str, str]] | None) -> int:
        # 从 CsvImporterBad 复制过来，但校验条件写成了只判断 None
        if data is None:
            raise ValueError("空数据")
        return len(data)  # 传入空列表 [] 时不会报错，直接返回 0
```

两个导入器的流程骨架（读取→解析→校验→写入）几乎一样，是复制粘贴出来的。后来 `CsvImporterBad` 把校验规则从"是否为 None"升级成了"是否为空"，但改的时候忘了同步到 `JsonImporterBad`，导致 JSON 导入器碰到空列表时会静默写入 0 行数据、不报任何错——两个看起来一样的流程在校验细节上悄悄跑偏了。Template Method 把固定流程写在父类里只维护一份，子类只覆写真正因数据源而异的步骤。

### Python 代码

```python
from abc import ABC, abstractmethod
from typing import override


class DataImporter(ABC):
    def run(self, path: str) -> int:
        """模板方法：流程固定。"""
        raw = self.read(path)
        data = self.parse(raw)
        self.validate(data)
        return self.write(data)

    @abstractmethod
    def read(self, path: str) -> str: ...

    @abstractmethod
    def parse(self, raw: str) -> list[dict[str, str]]: ...

    def validate(self, data: list[dict[str, str]]) -> None:
        """钩子：默认校验，子类可覆写。"""
        if not data:
            raise ValueError("空数据")

    @abstractmethod
    def write(self, data: list[dict[str, str]]) -> int: ...


class CsvImporter(DataImporter):
    @override
    def read(self, path: str) -> str:
        return "name,age\nAda,30"

    @override
    def parse(self, raw: str) -> list[dict[str, str]]:
        lines = raw.strip().splitlines()
        keys = lines[0].split(",")
        return [dict(zip(keys, row.split(","))) for row in lines[1:]]

    @override
    def write(self, data: list[dict[str, str]]) -> int:
        print(f"写入 {len(data)} 行")
        return len(data)
```

**口诀**：骨架父类写，步骤子类填。

---

## 六、Command · 命令

### 生活类比

智能家居遥控器上，每个按钮背后绑定的其实是一个"指令"对象（开灯、关灯、调亮度），按下就执行；而且这些指令可以被记录下来，一步步撤销，就像文档编辑器里 Ctrl+Z 能撤回你刚才的操作一样。

### 意图

将请求封装为对象，从而支持排队、撤销、日志、宏。

### 信号

- 编辑器 Undo/Redo
- 任务队列、智能家居遥控器

### 不用Command会怎样

```python
class EditorBad:
    def __init__(self) -> None:
        self.text = ""
        self._last_typed = ""  # 只能记住"最近一次"输入，撑不住连续多步撤销

    def type_text(self, chunk: str) -> None:
        self.text += chunk
        self._last_typed = chunk

    def undo(self) -> None:
        if self._last_typed:
            self.text = self.text[: -len(self._last_typed)]
            self._last_typed = ""  # 撤销之后就再也想不起上一步是什么了
```

这种写法只能撤销"最近一次"输入。连续打了两段文字后，第一次 `undo()` 能撤掉最后一段，但再调用第二次 `undo()` 什么也不会发生——因为整个历史只保留了一个变量，早前那次输入已经被覆盖、无从追溯。要支持多步撤销，只能不停加更多变量或者维护一个专门的历史列表；与其临时打补丁，不如一开始就把每次操作封装成一个 `Command` 对象放进栈里，天然支持任意步数的撤销。

### Python 代码

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import override


class Command(ABC):
    @abstractmethod
    def execute(self) -> None: ...

    @abstractmethod
    def undo(self) -> None: ...


class Editor:
    def __init__(self) -> None:
        self.text = ""


class TypeCommand(Command):
    def __init__(self, editor: Editor, chunk: str) -> None:
        self._editor = editor
        self._chunk = chunk

    @override
    def execute(self) -> None:
        self._editor.text += self._chunk

    @override
    def undo(self) -> None:
        n = len(self._chunk)
        if n:  # 防坑:text[:-0] 等价于 text[:0],会把全部文本清空
            self._editor.text = self._editor.text[:-n]


class CommandHistory:
    def __init__(self) -> None:
        self._stack: list[Command] = []

    def run(self, cmd: Command) -> None:
        cmd.execute()
        self._stack.append(cmd)

    def undo(self) -> None:
        if self._stack:
            self._stack.pop().undo()
```

**口诀**：请求变对象，可排队可撤销。

---

## 七、Chain of Responsibility · 职责链

### 生活类比

请假审批：先给组长看，金额超了组长权限就往上转给经理，经理搞不定再转总监。请求沿着一条链往上传，直到有人能处理，而提交请假申请的人根本不用关心最终是谁批的。

### 意图

请求沿着处理器链传递，直到被处理；发送者不知道谁处理。

### 信号

- HTTP 中间件、日志级别过滤、审批流（经理→总监→CEO）

### 不用Chain of Responsibility会怎样

```python
def approve_expense(amount: float) -> str:
    if amount <= 1000:
        return f"经理批准 {amount}"
    elif amount <= 10000:
        return f"总监批准 {amount}"
    else:
        return f"CEO 批准 {amount}"


def approve_travel(amount: float) -> str:
    # 差旅审批走另一套流程，复制了同一段金额分级判断
    if amount <= 1000:
        return f"经理批准（差旅）{amount}"
    elif amount <= 10000:
        return f"总监批准（差旅）{amount}"
    else:
        return f"CEO 批准（差旅）{amount}"
```

报销审批和差旅审批各自复制了一份"金额分级"判断。后来财务把总监的审批额度上限从 10000 调到 20000，只改了 `approve_expense`，`approve_travel` 忘了同步更新，两条审批线的额度从此不一致，只能靠人工发现。用 Chain of Responsibility 把每一级审批抽成一个 `Handler` 后，调整某一级的额度只需要改那一个 `Handler` 类，所有引用这条链的业务都会同步生效。

### Python 代码

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import override


@dataclass
class Request:
    amount: float
    reason: str


class Handler(ABC):
    def __init__(self) -> None:
        self._next: Handler | None = None

    def set_next(self, handler: Handler) -> Handler:
        self._next = handler
        return handler

    def handle(self, req: Request) -> str:
        result = self._try(req)
        if result is not None:
            return result
        if self._next:
            return self._next.handle(req)
        return "无人审批"

    @abstractmethod
    def _try(self, req: Request) -> str | None: ...


class Manager(Handler):
    @override
    def _try(self, req: Request) -> str | None:
        if req.amount <= 1000:
            return f"经理批准 {req.amount}"
        return None


class Director(Handler):
    @override
    def _try(self, req: Request) -> str | None:
        if req.amount <= 10000:
            return f"总监批准 {req.amount}"
        return None


class CEO(Handler):
    @override
    def _try(self, req: Request) -> str | None:
        return f"CEO 批准 {req.amount}"


mgr, director, ceo = Manager(), Director(), CEO()
mgr.set_next(director).set_next(ceo)
```

**口诀**：请求丢进链，谁能处理谁接住。

---

## 八、Iterator / Mediator（略）

- **Iterator**：不管底层是数组、链表还是树，你只要写 `for x in xxx` 去遍历，不用关心内部到底怎么存的——统一遍历方式；Python 实现 `__iter__` / `__next__` 即是。
- **Mediator**：机场塔台就是飞机之间的中介——飞机不会互相直接联系商量降落顺序，都是找塔台协调，减少飞机与飞机之间乱七八糟的直接通信。组件不互相直连，经中介转发，降低网状依赖。如果 4 个组件两两直接通信，最多要维护 6 条连接；加到 5 个组件就变成 10 条——连接数以 `N×(N-1)/2` 的速度增长，组件稍微一多，谁跟谁通信就理不清了。改成都通过中介转发后，连接数量退化成跟组件数量线性相关。对话框里按钮与输入框通过 Dialog 中介通信是经典例子。

---

## 九、行为型选型速查

```
算法可替换 → Strategy
事件通知多人 → Observer
行为随状态变 → State
流程固定细节变 → Template Method
要撤销/排队 → Command
过滤/审批链路 → Chain
遍历集合 → Iterator
网状改星状 → Mediator
```

| LLD 场景 | 常用模式 |
|----------|----------|
| 停车场计费 | Strategy |
| 通知系统 | Observer / 可加 Queue |
| 电梯 / 自动售货机 | State |
| 限流算法切换 | Strategy |
| 审批 / 中间件 | Chain |

---

下一篇：[LLD 面试框架](lld-framework.md)

---

[← 返回索引](index.md)
