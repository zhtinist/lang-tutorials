# 堆 & 优先队列 · Heap & Priority Queue

> 堆是一棵**完全二叉树**，满足：父节点 ≤ 子节点（小顶堆）或 父节点 ≥ 子节点（大顶堆）。
> Python `heapq` 是小顶堆，大顶堆用负值实现。

---

## 一、heapq 标准库用法

```python
import heapq

# --- 小顶堆 ---
heap: list[int] = []
heapq.heappush(heap, 3)      # 插入
heapq.heappush(heap, 1)
heapq.heappush(heap, 2)

heapq.heappop(heap)           # 弹出最小值 → 1
heap[0]                        # 查看最小值（不弹出）→ 2

# 批量建堆 (O(n))
nums = [3, 1, 4, 1, 5]
heapq.heapify(nums)           # 原地转为堆

# 替换操作
heapq.heappushpop(heap, 0)    # push 后 pop（比分开调用快）
heapq.heapreplace(heap, 6)    # pop 后 push

# TopK
heapq.nlargest(3, nums)       # 最大的 3 个
heapq.nsmallest(3, nums)      # 最小的 3 个


# --- 大顶堆（用负数） ---
max_heap: list[int] = []
heapq.heappush(max_heap, -val)  # 插入负数
largest = -heapq.heappop(max_heap)  # 弹出最大值


# --- 自定义优先队列（元组） ---
# (priority, item) — 先按 priority 排
pq: list[tuple[int, str]] = []
heapq.heappush(pq, (1, "task_a"))
heapq.heappush(pq, (0, "task_b"))  # 优先级高（数值小）
priority, task = heapq.heappop(pq)  # (0, "task_b")


# --- 元组进阶：处理 tie-break ---
# (priority, counter, item) 确保优先级相同时不比较 item
from itertools import count
counter = count()
heapq.heappush(pq, (1, next(counter), "task_a"))
heapq.heappush(pq, (1, next(counter), "task_b"))
```

### heapq 操作复杂度

| 操作 | 复杂度 |
|------|--------|
| `heappush` | O(log n) |
| `heappop` | O(log n) |
| `heapify` | O(n) |
| `heappushpop` | O(log n) |
| `heapreplace` | O(log n) |
| 查看堆顶 `heap[0]` | O(1) |

---

## 二、堆的实现原理

> 数组存储完全二叉树：节点 i 的左子 = `2i+1`，右子 = `2i+2`，父 = `(i-1)//2`

```python
class MinHeap:
    """小顶堆的手动实现（理解原理用，实际用 heapq）。"""

    def __init__(self) -> None:
        self.heap: list[int] = []

    def parent(self, i: int) -> int:
        return (i - 1) // 2

    def left(self, i: int) -> int:
        return 2 * i + 1

    def right(self, i: int) -> int:
        return 2 * i + 2

    def push(self, val: int) -> None:
        """插入：放到末尾，上浮。"""
        self.heap.append(val)
        self._swim(len(self.heap) - 1)

    def pop(self) -> int:
        """弹出堆顶：把末尾元素换到堆顶，下沉。"""
        if not self.heap:
            raise IndexError("empty heap")
        top = self.heap[0]
        self.heap[0] = self.heap[-1]
        self.heap.pop()
        if self.heap:
            self._sink(0)
        return top

    def _swim(self, i: int) -> None:
        """上浮：节点 < 父节点时交换。"""
        while i > 0 and self.heap[i] < self.heap[self.parent(i)]:
            p = self.parent(i)
            self.heap[i], self.heap[p] = self.heap[p], self.heap[i]
            i = p

    def _sink(self, i: int) -> None:
        """下沉：节点 > 子节点时与较小的子节点交换。"""
        n = len(self.heap)
        while True:
            smallest = i
            l = self.left(i)
            r = self.right(i)
            if l < n and self.heap[l] < self.heap[smallest]:
                smallest = l
            if r < n and self.heap[r] < self.heap[smallest]:
                smallest = r
            if smallest == i:
                break
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]
            i = smallest

    def peek(self) -> int:
        if not self.heap:
            raise IndexError("empty heap")
        return self.heap[0]
```

---

## 三、TopK 问题

### 3.1 数组中的第 K 个最大元素 · [LC 215](https://leetcode.com/problems/kth-largest-element-in-an-array/)

```python
import heapq
import random


# 解法1：堆 O(n log k)
def find_kth_largest_heap(nums: list[int], k: int) -> int:
    """用大小为 k 的小顶堆维护最大的 k 个元素。"""
    heap: list[int] = []
    for v in nums:
        heapq.heappush(heap, v)
        if len(heap) > k:
            heapq.heappop(heap)
    return heap[0]


# 解法2：快速选择 O(n) 期望时间
def find_kth_largest_quickselect(nums: list[int], k: int) -> int:
    """快速选择：partition 后只在一边递归。"""

    def partition(lo: int, hi: int, pivot_idx: int) -> int:
        pivot = nums[pivot_idx]
        nums[pivot_idx], nums[hi] = nums[hi], nums[pivot_idx]  # 把 pivot 移到末尾
        store_idx = lo
        for i in range(lo, hi):
            if nums[i] > pivot:  # 大元素放左边
                nums[store_idx], nums[i] = nums[i], nums[store_idx]
                store_idx += 1
        nums[store_idx], nums[hi] = nums[hi], nums[store_idx]
        return store_idx

    def quickselect(lo: int, hi: int, k_idx: int) -> int:
        if lo == hi:
            return nums[lo]
        pivot_idx = random.randint(lo, hi)
        pivot_idx = partition(lo, hi, pivot_idx)
        if pivot_idx == k_idx:
            return nums[pivot_idx]
        elif pivot_idx < k_idx:
            return quickselect(pivot_idx + 1, hi, k_idx)
        else:
            return quickselect(lo, pivot_idx - 1, k_idx)

    return quickselect(0, len(nums) - 1, k - 1)
```

### 3.2 前 K 个高频元素 · [LC 347](https://leetcode.com/problems/top-k-frequent-elements/)

```python
from collections import Counter


def top_k_frequent(nums: list[int], k: int) -> list[int]:
    """用大小为 k 的堆（按频次）。"""
    count = Counter(nums)
    heap: list[tuple[int, int]] = []  # (频次, 元素)

    for num, freq in count.items():
        heapq.heappush(heap, (freq, num))
        if len(heap) > k:
            heapq.heappop(heap)

    return [num for _, num in heap]
```

---

## 四、数据流中位数 · [LC 295](https://leetcode.com/problems/find-median-from-data-stream/)

```python
import heapq


class MedianFinder:
    """
    双堆技巧：
    - small: 大顶堆（存较小的一半元素，取反存入）
    - large: 小顶堆（存较大的一半元素）
    平衡：len(small) == len(large) 或 len(small) == len(large) + 1
    """

    def __init__(self):
        self.small: list[int] = []  # 大顶堆（存负数）
        self.large: list[int] = []  # 小顶堆

    def add_num(self, num: int) -> None:
        # 先加入 small（较小的一半），再把最大值移到 large
        heapq.heappush(self.small, -num)

        # 保证 small 的最大值 <= large 的最小值
        if self.small and self.large and -self.small[0] > self.large[0]:
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)

        # 平衡大小
        if len(self.small) > len(self.large) + 1:
            val = -heapq.heappop(self.small)
            heapq.heappush(self.large, val)
        if len(self.large) > len(self.small):
            val = heapq.heappop(self.large)
            heapq.heappush(self.small, -val)

    def find_median(self) -> float:
        if len(self.small) > len(self.large):
            return float(-self.small[0])
        return (-self.small[0] + self.large[0]) / 2
```

---

## 五、多路归并

### 5.1 合并 K 个有序链表 · [LC 23](https://leetcode.com/problems/merge-k-sorted-lists/)

```python
def merge_k_lists(lists: list["ListNode | None"]) -> "ListNode | None":
    """堆维护每个链表当前的头节点，每次取最小的。"""
    import heapq
    from itertools import count

    counter = count()
    heap: list[tuple[int, int, "ListNode"]] = []

    for node in lists:
        if node:
            heapq.heappush(heap, (node.val, next(counter), node))

    dummy = ListNode(0)
    cur = dummy
    while heap:
        _, _, node = heapq.heappop(heap)
        cur.next = node
        cur = cur.next
        if node.next:
            heapq.heappush(heap, (node.next.val, next(counter), node.next))

    return dummy.next
```

### 5.2 有序矩阵中第 K 小的元素 · [LC 378](https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/)

```python
def kth_smallest_matrix(matrix: list[list[int]], k: int) -> int:
    """多路归并：每行一个指针。"""
    import heapq

    n = len(matrix)
    # (value, row, col)
    heap = [(matrix[i][0], i, 0) for i in range(n)]
    heapq.heapify(heap)

    for _ in range(k - 1):
        _, r, c = heapq.heappop(heap)
        if c + 1 < n:
            heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))

    return heap[0][0]


# 更优解法：二分搜索值域
def kth_smallest_matrix_binary(matrix: list[list[int]], k: int) -> int:
    """二分搜索答案，统计 ≤ mid 的元素个数。"""
    n = len(matrix)

    def count_le(mid: int) -> int:
        """统计 ≤ mid 的元素个数。O(n)"""
        cnt = 0
        r, c = n - 1, 0
        while r >= 0 and c < n:
            if matrix[r][c] <= mid:
                cnt += r + 1
                c += 1
            else:
                r -= 1
        return cnt

    lo, hi = matrix[0][0], matrix[-1][-1]
    while lo < hi:
        mid = lo + (hi - lo) // 2
        if count_le(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
```

---

## 六、总结

| 场景 | 方法 | 复杂度 |
|------|------|--------|
| TopK 小数据量 | 排序 | O(n log n) |
| TopK (k << n) | 大小为 k 的堆 | O(n log k) |
| TopK 任意情况 | 快速选择 | O(n) 期望 |
| 数据流中位数 | 双堆 | O(log n) 每次 |
| K 路归并 | 堆 | O(N log K) |
| nlargest/nsmallest | heapq 内置 | O(n log k) |

---

## 七、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 215](https://leetcode.com/problems/kth-largest-element-in-an-array/) | Kth Largest Element | Medium | 堆/快速选择 |
| [LC 347](https://leetcode.com/problems/top-k-frequent-elements/) | Top K Frequent | Medium | 堆 |
| [LC 295](https://leetcode.com/problems/find-median-from-data-stream/) | Find Median from Data Stream | Hard | 双堆 |
| [LC 23](https://leetcode.com/problems/merge-k-sorted-lists/) | Merge k Sorted Lists | Hard | K路归并 |
| [LC 378](https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/) | Kth Smallest in Sorted Matrix | Medium | 归并/二分 |
| [LC 373](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/) | Find K Pairs with Smallest Sums | Medium | K路归并 |
| [LC 692](https://leetcode.com/problems/top-k-frequent-words/) | Top K Frequent Words | Medium | 堆+字典序 |
| [LC 703](https://leetcode.com/problems/kth-largest-element-in-a-stream/) | Kth Largest in a Stream | Easy | 堆 |
| [LC 1046](https://leetcode.com/problems/last-stone-weight/) | Last Stone Weight | Easy | 最大堆 |
| [LC 767](https://leetcode.com/problems/reorganize-string/) | Reorganize String | Medium | 最大堆+贪心 |

---

[← 返回索引](index.md)
