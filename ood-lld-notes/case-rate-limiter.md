# 案例：限流器 · Rate Limiter

> 在窗口内限制请求速率。算法是变化轴 → **RateLimitStrategy**；外壳负责键（用户/IP）、线程安全与可替换存储。

接口限流就像景区限流：同一个入口，单位时间内只放行一定数量的游客，超过限额的人就得在外面等一等，而不是让所有人一拥而入把景区挤垮。API 限流器解决的是同一个问题：保护后端不被某个用户/IP 的请求量瞬间打垮。

---

## 一、澄清需求

| 项目 | MVP |
|------|-----|
| API | `allow(key: str) -> bool` |
| 维度 | 按 key（user_id / IP）独立计数 |
| 算法 | 先 Token Bucket，再对比 Sliding Window |
| 运行 | 单进程多线程；提一嘴分布式 |
| 返回 | 布尔；可扩展剩余配额 / 重试等待 |

---

## 二、实体与变化轴

| 名词 | 类 |
|------|-----|
| 限流器 | `RateLimiter` |
| 算法 | `RateLimitStrategy` |
| 桶状态 | `TokenBucketState`（策略内部） |
| 时钟 | 可注入 `time` 便于测 |

变化轴：**限流算法**（Token Bucket / Sliding Window / Fixed Window / Leaky Bucket）。

---

## 三、类图

```
RateLimiter
  - strategy: RateLimitStrategy
  + allow(key) -> bool

RateLimitStrategy <<interface>>
  + allow(key) -> bool
      △
 TokenBucketStrategy
 SlidingWindowStrategy
```

如果不把限流算法抽成 `RateLimitStrategy`，`RateLimiter.allow` 内部就要直接写令牌桶的"补充令牌/扣减令牌"逻辑；想从令牌桶切换到滑动窗口做 A/B 测试对比效果时，必须直接修改这个正在生产环境处理真实流量的核心类，一旦改出并发 bug 会直接影响所有 API 的限流判断。抽成 `RateLimitStrategy` 后，切换算法只是把 `TokenBucketStrategy` 换成 `SlidingWindowStrategy` 这一行的事，`RateLimiter` 本身完全不用碰。

---

## 四、算法要点

### Token Bucket（令牌桶）

- 桶容量 `capacity`，每秒放入 `refill_rate` 个令牌
- 请求来时取 1 个令牌；没有则拒绝
- 允许短暂突发（桶满时可连续通过）

### Sliding Window Log（滑动窗口日志）

- 记录窗口内每个请求时间戳
- 丢弃窗口外时间戳；数量 < limit 则允许
- 更精确，内存随请求量涨

| | Token Bucket | Sliding Window |
|--|--------------|----------------|
| 突发 | 支持 | 相对平滑 |
| 内存 | O(键数量) | O(窗口内请求) |
| 实现 | 简单 | 略繁 |

---

## 五、代码骨架

```python
from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Callable, override


class RateLimitStrategy(ABC):
    @abstractmethod
    def allow(self, key: str) -> bool: ...


@dataclass
class _Bucket:
    tokens: float
    last_refill: float


class TokenBucketStrategy(RateLimitStrategy):
    """令牌桶：容量 + 每秒补充速率。"""

    def __init__(
        self,
        capacity: float,
        refill_rate: float,
        now: Callable[[], float] | None = None,
    ) -> None:
        if capacity <= 0 or refill_rate <= 0:
            raise ValueError("capacity/refill_rate 必须为正")
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._now = now or time.monotonic
        self._buckets: dict[str, _Bucket] = {}
        self._lock = threading.Lock()

    def _refill(self, bucket: _Bucket, now: float) -> None:
        elapsed = now - bucket.last_refill
        bucket.tokens = min(self._capacity, bucket.tokens + elapsed * self._refill_rate)
        bucket.last_refill = now

    @override
    def allow(self, key: str) -> bool:
        now = self._now()
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                bucket = _Bucket(tokens=self._capacity, last_refill=now)
                self._buckets[key] = bucket
            self._refill(bucket, now)
            if bucket.tokens >= 1.0:
                bucket.tokens -= 1.0
                return True
            return False


class SlidingWindowStrategy(RateLimitStrategy):
    """滑动窗口日志：窗口内最多 max_requests 次。"""

    def __init__(
        self,
        max_requests: int,
        window_seconds: float,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._max = max_requests
        self._window = window_seconds
        self._now = now or time.monotonic
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    @override
    def allow(self, key: str) -> bool:
        now = self._now()
        with self._lock:
            q = self._events[key]
            while q and now - q[0] >= self._window:
                q.popleft()
            if len(q) >= self._max:
                return False
            q.append(now)
            return True


class RateLimiter:
    """限流门面：可热切换策略。"""

    def __init__(self, strategy: RateLimitStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: RateLimitStrategy) -> None:
        self._strategy = strategy

    def allow(self, key: str) -> bool:
        return self._strategy.allow(key)


# 用法
limiter = RateLimiter(TokenBucketStrategy(capacity=10, refill_rate=5))
assert limiter.allow("user:42") is True
```

### 装饰器味道（可选）

```python
from collections.abc import Callable
from typing import TypeVar, ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


def rate_limited(
    limiter: RateLimiter,
    key_fn: Callable[P, str],
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def deco(fn: Callable[P, R]) -> Callable[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = key_fn(*args, **kwargs)
            if not limiter.allow(key):
                raise RuntimeError("429 Too Many Requests")
            return fn(*args, **kwargs)

        return wrapper

    return deco
```

---

## 六、线程安全要点

| 问题 | 做法 |
|------|------|
| 读改写 tokens | 策略内 `threading.Lock` |
| 多策略实例 | 每策略一把锁；或分片锁降竞争 |
| 时钟 | 测时注入 `now`；别用墙钟算间隔（NTP） |
| 性能 | 热点 key 可 `Lock` 分片：`locks[hash(key)%N]` |

分布式（口述即可）：

- Redis + Lua 做原子 Token Bucket / Sliding Window
- 网关层限流（Nginx / Envoy）与应用层限流分层

---

## 七、扩展

| 扩展 | 设计 |
|------|------|
| 返回等待时间 | `allow` → `Decision(allowed, retry_after)` |
| 多级限额 | Chain：用户级 → IP 级 → 全局 |
| 配置热更新 | 换 Strategy 或改参数（注意锁） |
| 观测 | Proxy/Decorator 包一层打点 |

```python
@dataclass(frozen=True)
class Decision:
    allowed: bool
    retry_after_ms: int = 0
```

---

## 八、面试口述

1. 接口 `allow(key)`，按 key 隔离  
2. Strategy 切换 Token Bucket / Sliding Window  
3. 锁保证并发正确；测试注入时钟  
4. 分布式用 Redis 原子脚本  
5. 与停车场对比：都是 **规则变化 → Strategy**

---

## 参考与延伸

- 限流算法综述（Token Bucket / Sliding Window）常见于系统设计笔记；本篇聚焦 LLD 类结构。
- Strategy + 线程安全是本题得分点；见 [patterns-behavioral.md](patterns-behavioral.md)。

下一篇：[习题推荐](exercises.md)

---

[← 返回索引](index.md)
