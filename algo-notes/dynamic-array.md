# 手写动态数组 · Dynamic Array

> 静态数组容量固定。动态数组自动扩容，Python 的 `list` 本质上就是动态数组。
> 核心操作：随机访问 O(1)、尾部插入均摊 O(1)、中间插入 O(n)。

---

## 一、核心原理

```
静态数组：int arr[10];  → 容量固定为 10
动态数组：自动扩容。当元素数量 = 容量时，分配更大的数组（通常是 2 倍），
         把旧元素拷贝过去。

扩容策略：
  容量满 → new_capacity = old_capacity * 2
  均摊分析：每次扩容 O(n)，但 n 次插入触发 log n 次扩容，
           总 = n + n + n/2 + n/4 + ... ≈ 2n → 均摊 O(1)
```

---

## 二、完整实现

```python
from typing import TypeVar, Generic

T = TypeVar("T")


class DynamicArray(Generic[T]):
    """
    手写动态数组。Python 的 list 就是动态数组，但了解原理有助理解复杂度。
    capacity 策略：初始 8，满了 ×2。
    """

    def __init__(self, initial_capacity: int = 8) -> None:
        self._data: list[T | None] = [None] * initial_capacity
        self._size: int = 0         # 当前元素个数
        self._capacity: int = initial_capacity

    # === 访问 ===

    def __getitem__(self, index: int) -> T:
        """随机访问 O(1)"""
        if index < 0:
            index += self._size
        if not 0 <= index < self._size:
            raise IndexError(f"index {index} out of range")
        return self._data[index]  # type: ignore

    def __setitem__(self, index: int, value: T) -> None:
        """随机写入 O(1)"""
        if index < 0:
            index += self._size
        if not 0 <= index < self._size:
            raise IndexError(f"index {index} out of range")
        self._data[index] = value

    # === 增删 ===

    def append(self, value: T) -> None:
        """尾部追加。均摊 O(1)"""
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._data[self._size] = value
        self._size += 1

    def pop(self) -> T:
        """尾部弹出 O(1)"""
        if self._size == 0:
            raise IndexError("pop from empty array")
        self._size -= 1
        val = self._data[self._size]  # type: ignore
        self._data[self._size] = None  # 帮助 GC
        # 缩容（惰性）：size < capacity/4 时缩到一半
        if self._size > 0 and self._size <= self._capacity // 4:
            self._resize(self._capacity // 2)
        return val

    def insert(self, index: int, value: T) -> None:
        """指定位置插入 O(n)。需要搬移元素。"""
        if index < 0:
            index += self._size
        if not 0 <= index <= self._size:
            raise IndexError(f"insert index {index} out of range")

        if self._size == self._capacity:
            self._resize(self._capacity * 2)

        # 把 [index..size-1] 往后移一位
        for i in range(self._size, index, -1):
            self._data[i] = self._data[i - 1]
        self._data[index] = value
        self._size += 1

    def remove_at(self, index: int) -> T:
        """删除指定位置元素 O(n)。"""
        if index < 0:
            index += self._size
        if not 0 <= index < self._size:
            raise IndexError(f"remove index {index} out of range")

        val = self._data[index]  # type: ignore
        # 把 [index+1..size-1] 往前移一位
        for i in range(index, self._size - 1):
            self._data[i] = self._data[i + 1]
        self._data[self._size - 1] = None
        self._size -= 1

        # 缩容
        if self._size > 0 and self._size <= self._capacity // 4:
            self._resize(self._capacity // 2)
        return val

    # === 内部 ===

    def _resize(self, new_capacity: int) -> None:
        """扩容/缩容：分配新数组并拷贝元素 O(n)"""
        new_data: list[T | None] = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[i]
        self._data = new_data
        self._capacity = new_capacity

    # === 工具 ===

    def __len__(self) -> int:
        return self._size

    def __repr__(self) -> str:
        items = [str(self._data[i]) for i in range(self._size)]
        return f"DynamicArray([{', '.join(items)}])"
```

---

## 三、操作复杂度

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| 随机访问 `[i]` | O(1) | 数组地址直接计算 |
| 尾部 `append` | 均摊 O(1) | 偶尔触发扩容 O(n) |
| 尾部 `pop` | O(1) | |
| `insert(i)` | O(n) | 搬移 [i..n-1] |
| `remove_at(i)` | O(n) | 搬移 [i+1..n-1] |
| 查找 | O(n) | 需要遍历 |

---

## 四、扩容策略与均摊分析

```
假设每次扩容 ×2：

插入第 i 个元素：
  i = 1~8:   没有扩容
  i = 9:     扩容 8→16，拷贝 8 个
  i = 10~16: 没有扩容
  i = 17:    扩容 16→32，拷贝 16 个
  ...

总拷贝次数 = 8 + 16 + 32 + ... + n/2 + n
            = n + n/2 + n/4 + ... + 8
            < 2n

所以 n 次插入的总时间为 n(插入) + 2n(拷贝) = 3n
均摊每次插入 = O(1)
```

> **Java ArrayList** 扩容因子 = 1.5；**Python list** 扩容因子 ≈ 1.125（有更精细的策略）。

---

## 五、环形数组简介

> 解决 `insert(0)` 和 `pop(0)` 的 O(n) 问题 → 用 `start` 指针表示逻辑起点，取模定位。

```python
class CircularArray(Generic[T]):
    """环形数组：头部插入/删除 O(1)。"""

    def __init__(self, capacity: int = 8) -> None:
        self._data: list[T | None] = [None] * capacity
        self._start: int = 0  # 逻辑起点的物理索引
        self._size: int = 0
        self._capacity: int = capacity

    def _physical_index(self, logical_idx: int) -> int:
        return (self._start + logical_idx) % self._capacity

    def add_first(self, value: T) -> None:
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._start = (self._start - 1) % self._capacity
        self._data[self._start] = value
        self._size += 1

    def remove_first(self) -> T:
        if self._size == 0:
            raise IndexError("empty")
        val = self._data[self._start]  # type: ignore
        self._data[self._start] = None
        self._start = (self._start + 1) % self._capacity
        self._size -= 1
        return val

    def _resize(self, new_capacity: int) -> None:
        new_data: list[T | None] = [None] * new_capacity
        for i in range(self._size):
            new_data[i] = self._data[(self._start + i) % self._capacity]
        self._data = new_data
        self._start = 0
        self._capacity = new_capacity
```

---

## 六、关键概念

| 概念 | 说明 |
|------|------|
| 数组(Array) | 连续内存，索引 O(1)，插入删除 O(n) |
| 动态数组 | 自动扩容的数组，均摊 O(1) append |
| 扩容因子 | 通常是 2 倍，控制空间换时间的平衡 |
| 环形数组 | 用取模实现头部 O(1)，是 deque 的基础 |
| 随机访问 | `arr[i]` = `base + i * sizeof(T)` — 只需一次乘法 |

---

[← 返回索引](index.md)
