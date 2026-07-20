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

### 意图

定义算法族，分别封装，使它们可互换；算法变化独立于使用方。

### 信号

- 计费规则、推荐策略、压缩算法、限流算法
- 想符合 OCP：加新算法不改上下文类

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

### 意图

对象状态变化时，自动通知所有依赖者（发布-订阅）。

### 信号

- 库存变更通知 UI / 邮件 / 指标
- 解耦「事件源」与「反应方」

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

### 意图

对象在不同状态下有不同行为；把每个状态封装成类，去掉巨大 `if state ==`。

### 信号

- 电梯：停靠/上行/下行/维护
- 订单：已创建→已支付→已发货→完成
- TCP：监听/已连接/关闭

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

### 意图

在父类定义算法骨架，将某些步骤延迟到子类；固定流程、开放细节。

### 信号

- 数据导入：校验→转换→写入，各源细节不同
- 游戏 AI 回合：感知→决策→执行

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

### 意图

将请求封装为对象，从而支持排队、撤销、日志、宏。

### 信号

- 编辑器 Undo/Redo
- 任务队列、智能家居遥控器

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

### 意图

请求沿着处理器链传递，直到被处理；发送者不知道谁处理。

### 信号

- HTTP 中间件、日志级别过滤、审批流（经理→总监→CEO）

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

- **Iterator**：统一遍历方式；Python 实现 `__iter__` / `__next__` 即是。
- **Mediator**：组件不互相直连，经中介转发，降低网状依赖。对话框里按钮与输入框通过 Dialog 中介通信是经典例子。

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

下一章把模式嵌进完整面试流程。

下一篇：[LLD 面试框架](lld-framework.md)

---

[← 返回索引](index.md)
