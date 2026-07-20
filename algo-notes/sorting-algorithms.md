# 十大排序算法 · Sorting Algorithms

> 排序是算法基础中的基础。按复杂度分三档：
> **O(n²)**: 冒泡/选择/插入、**O(n log n)**: 快排/归并/堆排、**O(n)**: 计数/桶/基数。

---

## 一、排序算法总览

| 算法 | 平均时间 | 最坏时间 | 空间 | 稳定 | 原地 |
|------|:---:|:---:|:---:|:---:|:---:|
| 冒泡排序 | O(n²) | O(n²) | O(1) | ✅ | ✅ |
| 选择排序 | O(n²) | O(n²) | O(1) | ❌ | ✅ |
| 插入排序 | O(n²) | O(n²) | O(1) | ✅ | ✅ |
| 希尔排序 | O(n log n) | O(n²) | O(1) | ❌ | ✅ |
| 归并排序 | O(n log n) | O(n log n) | O(n) | ✅ | ❌ |
| 快速排序 | O(n log n) | O(n²) | O(log n) | ❌ | ✅ |
| 堆排序 | O(n log n) | O(n log n) | O(1) | ❌ | ✅ |
| 计数排序 | O(n + k) | O(n + k) | O(k) | ✅ | ❌ |
| 桶排序 | O(n + k) | O(n²) | O(n + k) | ✅ | ❌ |
| 基数排序 | O(nk) | O(nk) | O(n + k) | ✅ | ❌ |

---

## 二、O(n²) 基础排序

### 2.1 冒泡排序 (Bubble Sort)

> 每轮把最大的元素"冒"到最后。两两比较交换。

```python
def bubble_sort(arr: list[int]) -> list[int]:
    n = len(arr)
    for i in range(n - 1):
        swapped = False
        for j in range(n - 1 - i):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                swapped = True
        if not swapped:       # 提前终止优化
            break
    return arr
```

### 2.2 选择排序 (Selection Sort)

> 每轮选最小的元素，放到已排序部分的末尾。

```python
def selection_sort(arr: list[int]) -> list[int]:
    n = len(arr)
    for i in range(n - 1):
        min_idx = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_idx]:
                min_idx = j
        arr[i], arr[min_idx] = arr[min_idx], arr[i]
    return arr
```

### 2.3 插入排序 (Insertion Sort)

> 像整理扑克牌，每次把新元素插入到已排序部分的正确位置。

```python
def insertion_sort(arr: list[int]) -> list[int]:
    n = len(arr)
    for i in range(1, n):
        key = arr[i]
        j = i - 1
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key
    return arr
```

> **小数据量时插入排序可能比快排更快**（常数因子小，缓存友好）。

---

## 三、O(n log n) 经典排序

### 3.1 快速排序 (Quick Sort) 🔥

> 选 pivot，分区，递归。平均最快，但最坏 O(n²)。

```python
import random


def quick_sort(arr: list[int]) -> list[int]:
    def _sort(lo: int, hi: int) -> None:
        if lo >= hi:
            return
        pivot_idx = partition(lo, hi)
        _sort(lo, pivot_idx - 1)
        _sort(pivot_idx + 1, hi)

    def partition(lo: int, hi: int) -> int:
        # 随机选 pivot 避免最坏情况
        pivot_idx = random.randint(lo, hi)
        arr[pivot_idx], arr[hi] = arr[hi], arr[pivot_idx]

        pivot = arr[hi]
        store_idx = lo  # store_idx 左都是 < pivot
        for i in range(lo, hi):
            if arr[i] < pivot:
                arr[store_idx], arr[i] = arr[i], arr[store_idx]
                store_idx += 1
        arr[store_idx], arr[hi] = arr[hi], arr[store_idx]
        return store_idx

    _sort(0, len(arr) - 1)
    return arr
```

**原理图解**
```
partition([3,1,4,1,5,9,2], pivot=2):
  store=0 (第一个 <2 放这)
  i=0: 3>2 跳过
  ...
  i=6: 2=pivot 跳过
  最终: [1,1,2,3,4,9,5]  2在正确位置
        <2     >2
```

### 3.2 归并排序 (Merge Sort)

> 分治：拆成两半 → 排序 → 合并。稳定，但需要 O(n) 额外空间。

```python
def merge_sort(arr: list[int]) -> list[int]:
    def _sort(lo: int, hi: int, temp: list[int]) -> None:
        if lo >= hi:
            return
        mid = lo + (hi - lo) // 2
        _sort(lo, mid, temp)
        _sort(mid + 1, hi, temp)
        _merge(lo, mid, hi, temp)

    def _merge(lo: int, mid: int, hi: int, temp: list[int]) -> None:
        # 合并两个有序区间 [lo, mid] 和 [mid+1, hi]
        i, j, k = lo, mid + 1, lo
        while i <= mid and j <= hi:
            if arr[i] <= arr[j]:
                temp[k] = arr[i]
                i += 1
            else:
                temp[k] = arr[j]
                j += 1
            k += 1
        while i <= mid:
            temp[k] = arr[i]; i += 1; k += 1
        while j <= hi:
            temp[k] = arr[j]; j += 1; k += 1
        arr[lo:hi + 1] = temp[lo:hi + 1]

    _sort(0, len(arr) - 1, [0] * len(arr))
    return arr
```

**归并排序的应用**：
- [LC 148](https://leetcode.com/problems/sort-list/) 排序链表（不能用快排，因为链表无法随机访问）
- [LC 493](https://leetcode.com/problems/reverse-pairs/) 逆序对/翻转对计数

### 3.3 堆排序 (Heap Sort)

> 见 [二叉堆实现](binary-heap-implementation.md) 中的 `heap_sort` 函数。

---

## 四、O(n) 线性排序

> 不基于比较，利用数据的范围限制。

### 4.1 计数排序 (Counting Sort)

```python
def counting_sort(arr: list[int]) -> list[int]:
    """要求：元素都是非负整数。O(n + max_val)。"""
    if not arr:
        return arr
    max_val = max(arr)

    # 统计每个值的出现次数
    count = [0] * (max_val + 1)
    for v in arr:
        count[v] += 1

    # 还原
    idx = 0
    for val in range(max_val + 1):
        for _ in range(count[val]):
            arr[idx] = val
            idx += 1
    return arr
```

> [LC 75](https://leetcode.com/problems/sort-colors/) 颜色分类本质上就是 3-计数排序。

### 4.2 桶排序 (Bucket Sort)

```python
def bucket_sort(arr: list[float]) -> list[float]:
    """把元素分到多个桶里，每个桶分别排序。适用于均匀分布的数据。"""
    if not arr:
        return arr
    n = len(arr)
    buckets: list[list[float]] = [[] for _ in range(n)]

    for v in arr:
        idx = int(v * n)  # 0≤v<1
        buckets[idx].append(v)

    for bucket in buckets:
        bucket.sort()  # 桶内用插入排序或内置排序

    return [v for bucket in buckets for v in bucket]
```

### 4.3 基数排序 (Radix Sort)

```python
def radix_sort(arr: list[int]) -> list[int]:
    """从最低位到最高位，对每一位做稳定的计数排序。"""
    if not arr:
        return arr

    max_val = max(arr)
    exp = 1  # 当前处理的位数（1=个位, 10=十位...）

    while max_val // exp > 0:
        # 对当前位做计数排序
        count = [0] * 10
        output = [0] * len(arr)

        for v in arr:
            digit = (v // exp) % 10
            count[digit] += 1

        for i in range(1, 10):
            count[i] += count[i - 1]  # 前缀和转为位置

        # 从后往前保证稳定性
        for v in reversed(arr):
            digit = (v // exp) % 10
            count[digit] -= 1
            output[count[digit]] = v

        arr = output  # type: ignore
        exp *= 10

    return arr
```

---

## 五、希尔排序 (Shell Sort)

> 插入排序的改进：先对远距离元素排序（gap递减），最终 gap=1 时就是插入排序。
> 此时数组已经基本有序，插入排序接近 O(n)。

```python
def shell_sort(arr: list[int]) -> list[int]:
    n = len(arr)
    gap = n // 2

    while gap > 0:
        for i in range(gap, n):
            key = arr[i]
            j = i
            while j >= gap and arr[j - gap] > key:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = key
        gap //= 2

    return arr
```

---

## 六、排序算法选择指南

| 场景 | 推荐算法 |
|------|---------|
| 一般情况 | 快速排序（随机 pivot） |
| 需要稳定 | 归并排序 / Timsort (Python内置) |
| 链表排序 | 归并排序 |
| 数据量小 (n<50) | 插入排序 |
| 数据范围小 | 计数排序 |
| 外部排序 | 归并排序 |
| 内存极有限 | 堆排序（原地） |
| Python 内置 | `arr.sort()` = Timsort（归并+插入的混合） |

> **Python `list.sort()` 使用 Timsort**：归并排序 + 插入排序的混合，稳定，最坏 O(n log n)，实际性能很好。

---

[← 返回索引](index.md)
