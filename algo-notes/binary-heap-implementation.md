# 手写二叉堆 · Binary Heap Implementation

> 二叉堆是一棵**完全二叉树**，满足**堆序性质**：父节点 ≤ 子节点（最小堆）或 父节点 ≥ 子节点（最大堆）。
> 核心操作：**上浮 swim** 和 **下沉 sink**。这是堆排序和优先队列的基础。

---

## 一、数组存储完全二叉树

```
完全二叉树可以用数组紧凑存储，不需要指针：

            0(堆顶)
          /     \
         1       2
        / \     / \
       3   4   5   6
      / \
     7   8

索引关系（0-indexed）：
  节点 i 的左子节点 = 2i + 1
  节点 i 的右子节点 = 2i + 2
  节点 i 的父节点   = (i - 1) // 2

  最后一个非叶子节点 = (n - 1) // 2
```

---

## 二、最小堆完整实现

```python
from typing import TypeVar

T = TypeVar("T")


class MinHeap:
    """
    最小堆：堆顶是最小元素。
    操作：插入 O(log n)，弹出堆顶 O(log n)，建堆 O(n)，查看堆顶 O(1)。
    """

    def __init__(self) -> None:
        self._data: list[T] = []

    # === 核心操作：上浮和下沉 ===

    def _swim(self, i: int) -> None:
        """
        上浮：当节点比父节点小时，与父节点交换。
        用于插入操作：新元素放在末尾，上浮到正确位置。
        O(log n)
        """
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i] < self._data[parent]:
                self._data[i], self._data[parent] = self._data[parent], self._data[i]
                i = parent
            else:
                break

    def _sink(self, i: int) -> None:
        """
        下沉：当节点比子节点大时，与较小的子节点交换。
        用于删除堆顶：末尾元素移到堆顶后，下沉到正确位置。
        O(log n)
        """
        n = len(self._data)
        while True:
            smallest = i
            left = 2 * i + 1
            right = 2 * i + 2

            if left < n and self._data[left] < self._data[smallest]:
                smallest = left
            if right < n and self._data[right] < self._data[smallest]:
                smallest = right

            if smallest == i:
                break

            self._data[i], self._data[smallest] = self._data[smallest], self._data[i]
            i = smallest

    # === 公开接口 ===

    def push(self, val: T) -> None:
        """插入元素 O(log n)。"""
        self._data.append(val)
        self._swim(len(self._data) - 1)

    def pop(self) -> T:
        """弹出堆顶（最小元素）O(log n)。"""
        if not self._data:
            raise IndexError("pop from empty heap")
        if len(self._data) == 1:
            return self._data.pop()

        top = self._data[0]
        self._data[0] = self._data.pop()  # 把最后一个元素移到堆顶
        self._sink(0)                     # 下沉
        return top

    def peek(self) -> T:
        """查看堆顶 O(1)。"""
        if not self._data:
            raise IndexError("peek from empty heap")
        return self._data[0]

    def __len__(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0


# ====== 建堆的两种方式 ======

def build_heap_naive(arr: list[T]) -> MinHeap:
    """
    方法1：逐个插入 O(n log n)。
    每次插入可能上浮到堆顶。
    """
    heap = MinHeap()
    for v in arr:
        heap.push(v)
    return heap


def build_heap_floyd(arr: list[T]) -> MinHeap:
    """
    方法2：Floyd 建堆法 O(n)。
    从最后一个非叶子节点开始，逐个下沉。
    """
    heap = MinHeap()
    heap._data = arr.copy()

    # 最后一个非叶子节点 = (n-1)//2
    last_non_leaf = (len(arr) - 1) // 2
    for i in range(last_non_leaf, -1, -1):
        heap._sink(i)

    return heap
```

### Floyd 建堆复杂度分析

```
为什么是 O(n)？

第 0 层 (堆顶): 1个节点，最多下沉 h 层
第 1 层:       2个节点，最多下沉 h-1 层
第 2 层:       4个节点，最多下沉 h-2 层
...

总下沉次数 = Σ (i层节点数 × 下沉深度)
            = 1×h + 2×(h-1) + 4×(h-2) + ... + 2^h×0
            < n  （数学归纳法可证）

所以 Floyd 建堆是 O(n)，而非逐个插入的 O(n log n)。
```

---

## 三、最大堆

```python
class MaxHeap:
    """最大堆：堆顶是最大元素。只需把比较符号反一下。"""

    def __init__(self) -> None:
        self._data: list[T] = []

    def _swim(self, i: int) -> None:
        while i > 0:
            parent = (i - 1) // 2
            if self._data[i] > self._data[parent]:  # > 放在这里
                self._data[i], self._data[parent] = self._data[parent], self._data[i]
                i = parent
            else:
                break

    def _sink(self, i: int) -> None:
        n = len(self._data)
        while True:
            largest = i
            left = 2 * i + 1
            right = 2 * i + 2
            if left < n and self._data[left] > self._data[largest]:
                largest = left
            if right < n and self._data[right] > self._data[largest]:
                largest = right
            if largest == i:
                break
            self._data[i], self._data[largest] = self._data[largest], self._data[i]
            i = largest

    def push(self, val: T) -> None:
        self._data.append(val)
        self._swim(len(self._data) - 1)

    def pop(self) -> T:
        if not self._data:
            raise IndexError("empty")
        if len(self._data) == 1:
            return self._data.pop()
        top = self._data[0]
        self._data[0] = self._data.pop()
        self._sink(0)
        return top

    def peek(self) -> T:
        return self._data[0]
```

---

## 四、堆排序

```python
def heap_sort(arr: list[T]) -> list[T]:
    """
    堆排序 O(n log n)，空间 O(1) 原地排序。
    1. Floyd 建最大堆（O(n)）
    2. 每次把堆顶(最大)与末尾交换，然后下沉新的堆顶（O(n log n)）
    """
    n = len(arr)

    # 1. 建堆（从最后一个非叶子节点往前下沉）
    for i in range(n // 2 - 1, -1, -1):
        _sink_in_place(arr, n, i)

    # 2. 排序
    for i in range(n - 1, 0, -1):
        arr[0], arr[i] = arr[i], arr[0]  # 堆顶(最大值)移到末尾
        _sink_in_place(arr, i, 0)        # 对剩余部分重新下沉

    return arr


def _sink_in_place(arr: list[T], heap_size: int, i: int) -> None:
    """在数组上原地执行下沉操作。"""
    while True:
        largest = i
        left = 2 * i + 1
        right = 2 * i + 2
        if left < heap_size and arr[left] > arr[largest]:
            largest = left
        if right < heap_size and arr[right] > arr[largest]:
            largest = right
        if largest == i:
            break
        arr[i], arr[largest] = arr[largest], arr[i]
        i = largest
```

---

## 五、堆 vs 其他数据结构

| 操作 | 堆 | 有序数组 | 平衡BST |
|------|:---:|:---:|:---:|
| 插入 | O(log n) | O(n) | O(log n) |
| 找最小 | O(1) | O(1) | O(log n) |
| 删除最小 | O(log n) | O(n) | O(log n) |
| 建堆 | O(n) | O(n log n) | O(n log n) |

> 堆是专门为"快速获取最值"设计的数据结构。不需要全排序，只需要最值。

---

## 六、可视化理解

```
操作     堆变化
push(2)  [2]
push(5)  [2, 5]          ← 5 比父节点 2 大，不上浮
push(1)  [1, 5, 2]       ← 1 比父节点 2 小，上浮到堆顶
push(3)  [1, 3, 2, 5]    ← 3 比父节点 5 小，上浮
push(0)  [0, 1, 2, 5, 3] ← 0 一路浮到堆顶

pop()    [1, 3, 2, 5]    ← 堆顶 0 弹出，5 移到堆顶后下沉
pop()    [2, 3, 5]       ← 堆顶 1 弹出
```

---

[← 返回索引](index.md)
