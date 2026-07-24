# 案例：停车场 · Parking Lot

> 用五步框架走通经典题：多车型占位、多费率、进出场。变化轴落在 **FeeStrategy** 与 **车位分配**；ParkingLot 做门面编排。

去过商场停车场就知道整个流程：车牌拍照/取票进场，找个空位停下；离场时扫码算一下停了多久该交多少钱，闸机抬杆放行。这一案例要做的，就是把这套大家都熟悉的流程，拆成一组职责清楚的类。

---

## 一、澄清需求

### 假设（与面试官对齐）

| 项目 | MVP 假设 |
|------|----------|
| 结构 | 多层楼，每层多个车位 |
| 车型 | 摩托 / 小车 / 大车（占位不同） |
| 流程 | 进场发 Ticket，出场按时长计费 |
| 费率 | 先实现按时长单价；可扩展日票 |
| 运行 | 单机内存；讨论时提线程安全 |
| 不做 | 预约、支付网关、跨停车场调度 |

### 核心用例

1. `park(vehicle) -> Ticket`
2. `leave(ticket_id) -> Receipt`（含费用）
3. 查询剩余车位（可选）

---

## 二、识别实体

| 名词 | 类 | 职责 |
|------|-----|------|
| 停车场 | `ParkingLot` | 编排进场/出场 |
| 楼层 | `ParkingFloor` | 管理本层车位 |
| 车位 | `ParkingSpot` | 类型、占用状态 |
| 车 | `Vehicle` | 车牌、所需车位类型 |
| 票 | `Ticket` | 进场时间、车位、车辆 |
| 费率 | `FeeStrategy` | 按时长算钱 |

动词 → 方法：`assign_spot`、`park`、`leave`、`calculate`。

变化轴：费率公式、分配策略（最近空位 / 按车型）。

---

## 三、类设计（ASCII）

```
┌──────────────┐     ◆     ┌──────────────┐     ◆     ┌──────────────┐
│  ParkingLot  │───────────│ ParkingFloor │───────────│ ParkingSpot  │
├──────────────┤           ├──────────────┤           ├──────────────┤
│ floors       │           │ floor_no     │           │ id, spot_type│
│ fee_strategy │           │ spots[]      │           │ vehicle?     │
│ tickets{}    │           │ find_spot()  │           │ assign/clear │
│ park/leave   │           └──────────────┘           └──────────────┘
└───────┬──────┘
        │ 依赖
        ▼
┌──────────────┐         ┌──────────────┐
│ FeeStrategy  │◁········│   Ticket     │
│  calc(dur)   │         │ id, in_time  │
└──────△───────┘         │ spot, vehicle│
       │                 └──────────────┘
 HourlyFee / DailyFee

 Vehicle <<abstract>>
    △
 Bike / Car / Truck     （或 Enum + size，二选一讲清即可）
```

设计选择说明：

- **组合**：Lot ◆ Floor ◆ Spot
- **策略**：Lot 持有 `FeeStrategy`（OCP）
- 车型用继承演示多态；也可用 `VehicleType` 枚举避免浅继承——面试说清权衡

如果不把计费公式抽成 `FeeStrategy`，而是把 `if vehicle.vtype == VehicleType.CAR: fee = hours * 5` 这类判断直接写死在 `ParkingLot.leave()` 内部，以后想加"会员日票价"或者"节假日双倍收费"，就必须回去改这个已经在生产环境跑着、被 `park`/`leave` 两条主路径共用的核心方法，一旦改错还可能连累原本工作正常的小时计费逻辑。`FeeStrategy` 把公式抽出去后，新增计费规则只是新增一个类，`ParkingLot` 本身不用动。

---

## 四、代码骨架

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import override
from uuid import uuid4


class SpotType(Enum):
    MOTORCYCLE = auto()
    COMPACT = auto()
    LARGE = auto()


class VehicleType(Enum):
    BIKE = auto()
    CAR = auto()
    TRUCK = auto()


# 车型 → 可停的车位（简化规则）
CAN_FIT: dict[VehicleType, set[SpotType]] = {
    VehicleType.BIKE: {SpotType.MOTORCYCLE, SpotType.COMPACT, SpotType.LARGE},
    VehicleType.CAR: {SpotType.COMPACT, SpotType.LARGE},
    VehicleType.TRUCK: {SpotType.LARGE},
}


@dataclass
class Vehicle:
    plate: str
    vtype: VehicleType


@dataclass
class ParkingSpot:
    spot_id: str
    spot_type: SpotType
    vehicle: Vehicle | None = None

    @property
    def is_free(self) -> bool:
        return self.vehicle is None

    def can_fit(self, vehicle: Vehicle) -> bool:
        return self.is_free and self.spot_type in CAN_FIT[vehicle.vtype]

    def assign(self, vehicle: Vehicle) -> None:
        if not self.can_fit(vehicle):
            raise ValueError("车位不可用或不匹配")
        self.vehicle = vehicle

    def clear(self) -> None:
        self.vehicle = None


@dataclass
class ParkingFloor:
    floor_no: int
    spots: list[ParkingSpot] = field(default_factory=list)

    def find_spot(self, vehicle: Vehicle) -> ParkingSpot | None:
        for spot in self.spots:
            if spot.can_fit(vehicle):
                return spot
        return None


@dataclass
class Ticket:
    ticket_id: str
    vehicle: Vehicle
    spot: ParkingSpot
    entry_time: datetime


class FeeStrategy(ABC):
    @abstractmethod
    def calculate(self, duration: timedelta) -> float: ...


class HourlyFee(FeeStrategy):
    def __init__(self, rate: float = 5.0) -> None:
        self._rate = rate

    @override
    def calculate(self, duration: timedelta) -> float:
        # 不足 1 小时按 1 小时计
        hours = max(1, -(-int(duration.total_seconds()) // 3600))  # ceil div
        return hours * self._rate


@dataclass
class Receipt:
    ticket_id: str
    plate: str
    fee: float
    duration: timedelta


class ParkingLot:
    """停车场门面：进场/出场编排。"""

    def __init__(self, floors: list[ParkingFloor], fee: FeeStrategy) -> None:
        self._floors = floors
        self._fee = fee
        self._tickets: dict[str, Ticket] = {}

    def park(self, vehicle: Vehicle, now: datetime | None = None) -> Ticket:
        now = now or datetime.now()
        for floor in self._floors:
            spot = floor.find_spot(vehicle)
            if spot is None:
                continue
            spot.assign(vehicle)
            ticket = Ticket(str(uuid4()), vehicle, spot, now)
            self._tickets[ticket.ticket_id] = ticket
            return ticket
        raise RuntimeError("停车场已满")

    def leave(self, ticket_id: str, now: datetime | None = None) -> Receipt:
        now = now or datetime.now()
        ticket = self._tickets.pop(ticket_id, None)
        if ticket is None:
            raise KeyError("无效票据")
        duration = now - ticket.entry_time
        fee = self._fee.calculate(duration)
        plate = ticket.vehicle.plate
        ticket.spot.clear()
        return Receipt(ticket_id, plate, fee, duration)

    def set_fee_strategy(self, fee: FeeStrategy) -> None:
        self._fee = fee
```

### 使用示例

```python
spots = [
    ParkingSpot("1-A", SpotType.COMPACT),
    ParkingSpot("1-B", SpotType.LARGE),
]
lot = ParkingLot([ParkingFloor(1, spots)], HourlyFee(5.0))
t = lot.park(Vehicle("浙A12345", VehicleType.CAR))
# ... 若干小时后
# receipt = lot.leave(t.ticket_id)
```

---

## 五、异常与并发

| 场景 | 处理 |
|------|------|
| 满位 | `park` 抛业务异常 / 返回 Result |
| 重复进场同车牌 | 可选：登记表检查 |
| 无效票 / 重复出场 | `leave` 查不到 ticket |
| 并发占同一车位 | 对 `spot.assign` 加锁，或 Lot 级锁；乐观：CAS 状态 |
| 时钟 | 注入 `now` 便于测试 |

```python
import threading

class ThreadSafeParkingLot(ParkingLot):
    def __init__(self, floors: list[ParkingFloor], fee: FeeStrategy) -> None:
        super().__init__(floors, fee)
        self._lock = threading.RLock()

    def park(self, vehicle: Vehicle, now: datetime | None = None) -> Ticket:
        with self._lock:
            return super().park(vehicle, now)

    def leave(self, ticket_id: str, now: datetime | None = None) -> Receipt:
        with self._lock:
            return super().leave(ticket_id, now)
```

---

## 六、扩展点（展示 OCP）

| 扩展 | 怎么做 |
|------|--------|
| 日票 / 会员价 | 新 `FeeStrategy`，`set_fee_strategy` |
| 电动车位 | `SpotType.EV` + 适配规则 |
| 最优车位 | `SpotAssignmentStrategy` 接口 |
| 持久化 | `TicketRepository` 注入（DIP） |
| 多入口闸机 | 闸机依赖 Lot Facade，不直接改 Spot |

```python
class SpotAssignmentStrategy(ABC):
    @abstractmethod
    def find(self, floors: list[ParkingFloor], vehicle: Vehicle) -> ParkingSpot | None: ...
```

---

## 七、面试口述要点

1. MVP：多层、多车型、进出计费  
2. 组合建模空间；策略建模费率  
3. 主路径 `park`/`leave` 走通  
4. 满位与并发锁  
5. 扩展不加 if，加策略类  

---

## 用到的模式

费率部分对应 Strategy（行为型）；Lot 具 Facade 味道。对照练习：[图书管理系统](case-library.md)、[限流器](case-rate-limiter.md)。

---

[← 返回索引](index.md)
