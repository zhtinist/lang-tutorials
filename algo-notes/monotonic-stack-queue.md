# 单调栈 & 单调队列 · Monotonic Stack & Queue

> **单调栈**：维护一个单调递增/递减的栈，快速找到**下一个更大/更小元素**。
> **单调队列**：维护一个单调递减/递增的队列，快速找到**滑动窗口中的最值**。

---

## 一、单调栈

### 1.1 核心思想

```
普通解法：对每个元素，往右扫描找下一个更大元素 → O(n²)
单调栈：  从后往前遍历，维护一个"候选人栈" → O(n)

栈中维护的是"还没有找到下一个更大元素的元素"。
遍历到一个新元素时，比它小的栈中元素找到了自己的下一个更大（就是当前元素）。
```

### 1.2 下一个更大元素 I · [LC 496](https://leetcode.com/problems/next-greater-element-i/)

```python
def next_greater_element(
    nums1: list[int], nums2: list[int],
) -> list[int]:
    """
    nums1 是 nums2 的子集。
    对 nums1 中每个元素，找它在 nums2 中右侧第一个更大的元素。
    """
    # 1. 对 nums2 用单调栈预处理
    nxt_greater: dict[int, int] = {}
    stack: list[int] = []

    for v in reversed(nums2):  # 从后往前！
        # 比 v 小的元素都不可能是后面元素的"下一个更大"
        while stack and stack[-1] <= v:
            stack.pop()
        # 栈顶就是 v 的下一个更大（如果有）
        nxt_greater[v] = stack[-1] if stack else -1
        stack.append(v)

    return [nxt_greater[v] for v in nums1]
```

### 1.3 下一个更大元素 II · [LC 503](https://leetcode.com/problems/next-greater-element-ii/)（循环数组）

```python
def next_greater_elements(nums: list[int]) -> list[int]:
    """循环数组。技巧：遍历两遍，下标取模。"""
    n = len(nums)
    ans = [-1] * n
    stack: list[int] = []  # 存的是索引！

    for i in range(2 * n - 1, -1, -1):
        idx = i % n
        while stack and nums[stack[-1]] <= nums[idx]:
            stack.pop()
        ans[idx] = nums[stack[-1]] if stack else -1
        stack.append(idx)

    return ans
```

### 1.4 每日温度 · [LC 739](https://leetcode.com/problems/daily-temperatures/)

```python
def daily_temperatures(temperatures: list[int]) -> list[int]:
    """找到等待多少天后温度更高。返回天数，没有则 0。"""
    n = len(temperatures)
    ans = [0] * n
    stack: list[int] = []  # 存索引

    for i in range(n - 1, -1, -1):
        while stack and temperatures[stack[-1]] <= temperatures[i]:
            stack.pop()
        ans[i] = (stack[-1] - i) if stack else 0
        stack.append(i)

    return ans
```

---

## 二、单调栈经典难题

### 2.1 柱状图中最大的矩形 · [LC 84](https://leetcode.com/problems/largest-rectangle-in-histogram/) 🔥

```python
def largest_rectangle_area(heights: list[int]) -> int:
    """
    对每个柱子，以它为高的最大矩形宽度 = 左右两边第一个比它矮的柱子之间的距离。
    单调递增栈，新元素比栈顶矮时，栈顶找到了右边界，左边界是栈顶的下一个元素。
    """
    # 前后补 0，作为哨兵
    heights = [0] + heights + [0]
    n = len(heights)
    stack: list[int] = []  # 存索引，栈中元素对应的高度递增
    ans = 0

    for i in range(n):
        # 当遇到比栈顶矮的柱子时，栈顶柱子的右边界找到了
        while stack and heights[i] < heights[stack[-1]]:
            h = heights[stack.pop()]
            # 左边界 = 栈顶的下一个（因为栈内递增）
            w = i - stack[-1] - 1 if stack else i
            ans = max(ans, h * w)
        stack.append(i)

    return ans
```

**图解**：
```
heights = [0, 2, 1, 5, 6, 2, 3, 0]

遇到 i=2 (高度1) 时：
  栈中 [0(0), 1(2)]
  当前高度 1 < 栈顶高度 2
  弹出高度2: 宽度 = 2 - 0 - 1 = 1, 面积 = 2*1 = 2

遇到 i=5 (高度2) 时：
  栈中 [0(0), 2(1), 3(5), 4(6)]
  当前高度 2 < 6, 弹出6: 宽度 = 5-3-1 = 1, 面积 = 6*1 = 6
  当前高度 2 < 5, 弹出5: 宽度 = 5-2-1 = 2, 面积 = 5*2 = 10
  ...
```

### 2.2 接雨水 · [LC 42](https://leetcode.com/problems/trapping-rain-water/)（单调栈解法）

```python
def trap_mono_stack(height: list[int]) -> int:
    """
    单调递减栈。遇到比栈顶高的柱子时，
    栈顶柱子可以接到水：左右两边的较高柱子围成了一个凹槽。
    """
    ans = 0
    stack: list[int] = []

    for i, h in enumerate(height):
        while stack and h > height[stack[-1]]:
            bottom = stack.pop()  # 凹槽底部
            if not stack:
                break  # 左边没有柱子，接不住水
            left = stack[-1]
            # 宽度 = i - left - 1
            # 高度 = min(left高, right高) - bottom高
            w = i - left - 1
            h_diff = min(height[left], h) - height[bottom]
            ans += w * h_diff
        stack.append(i)

    return ans
```

---

## 三、单调队列

### 3.1 滑动窗口最大值 · [LC 239](https://leetcode.com/problems/sliding-window-maximum/) 🔥

```python
from collections import deque


def max_sliding_window(nums: list[int], k: int) -> list[int]:
    """
    单调递减队列，队首始终是当前窗口的最大值。
    队列存的是索引，保证队首索引始终在窗口内。
    """
    ans: list[int] = []
    queue: deque[int] = deque()  # 存索引，对应值递减

    for i, v in enumerate(nums):
        # 1. 维护队列的递减性：新元素入队，比它小的都弹出
        while queue and nums[queue[-1]] <= v:
            queue.pop()
        queue.append(i)

        # 2. 移除窗口外的元素（队首索引 < i - k + 1）
        if queue[0] <= i - k:
            queue.popleft()

        # 3. 窗口形成后记录结果（i >= k - 1）
        if i >= k - 1:
            ans.append(nums[queue[0]])

    return ans
```

**复杂度**：O(n)。每个元素入队一次、出队一次。

### 3.2 最短子数组（和 ≥ K）· [LC 862](https://leetcode.com/problems/shortest-subarray-with-sum-at-least-k/)

```python
from collections import deque


def shortest_subarray(nums: list[int], k: int) -> int:
    """
    前缀和 + 单调递增队列。
    找 pre[j] - pre[i] >= k → pre[i] <= pre[j] - k。
    队列维护递增的 pre 值。
    """
    n = len(nums)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + nums[i]

    ans = float("inf")
    queue: deque[int] = deque()  # 存索引，对应 pre 值递增

    for i in range(n + 1):
        # 1. 队首满足条件时更新答案并弹出（更好的答案不会再从旧索引产生）
        while queue and pre[i] - pre[queue[0]] >= k:
            ans = min(ans, i - queue.popleft())

        # 2. 维护队列递增性
        while queue and pre[i] <= pre[queue[-1]]:
            queue.pop()
        queue.append(i)

    return int(ans) if ans != float("inf") else -1
```

---

## 四、总结

| 数据结构 | 维护的单调性 | 典型问题 |
|----------|------------|---------|
| 单调递增栈 | 从底到顶递增 | 下一个更大元素 |
| 单调递减栈 | 从底到顶递减 | 下一个更小元素 |
| 单调栈（递增） | 递增 | 柱状图最大矩形 |
| 单调队列（递减） | 递减 | 滑动窗口最大值 |
| 单调队列（递增） | 递增 | 最短和≥K子数组 |

### 模板对照

```
单调栈模板（从后往前遍历）：
  for v in reversed(arr):
      while stack and stack[-1] <= v:
          stack.pop()
      ans = stack[-1] if stack else default
      stack.append(v)

单调队列模板（滑动窗口）：
  for i, v in enumerate(arr):
      while queue and nums[queue[-1]] <= v:  # 维护递减
          queue.pop()
      queue.append(i)
      if queue[0] <= i - k:  # 移出窗口
          queue.popleft()
      if i >= k - 1:          # 记录结果
          ans.append(nums[queue[0]])
```

---

## 五、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 496](https://leetcode.com/problems/next-greater-element-i/) | Next Greater Element I | Easy | 单调栈基础 |
| [LC 503](https://leetcode.com/problems/next-greater-element-ii/) | Next Greater Element II | Medium | 循环数组 |
| [LC 739](https://leetcode.com/problems/daily-temperatures/) | Daily Temperatures | Medium | 存索引 |
| [LC 84](https://leetcode.com/problems/largest-rectangle-in-histogram/) | Largest Rectangle in Histogram | Hard | 单调栈+哨兵 |
| [LC 42](https://leetcode.com/problems/trapping-rain-water/) | Trapping Rain Water | Hard | 单调栈/双指针 |
| [LC 239](https://leetcode.com/problems/sliding-window-maximum/) | Sliding Window Maximum | Hard | 单调队列 |
| [LC 862](https://leetcode.com/problems/shortest-subarray-with-sum-at-least-k/) | Shortest Subarray Sum ≥ K | Hard | 前缀和+单调队列 |
| [LC 901](https://leetcode.com/problems/online-stock-span/) | Online Stock Span | Medium | 单调栈 |
| [LC 402](https://leetcode.com/problems/remove-k-digits/) | Remove K Digits | Medium | 单调栈 |
| [LC 316](https://leetcode.com/problems/remove-duplicate-letters/) | Remove Duplicate Letters | Medium | 单调栈+计数 |
| [LC 1081](https://leetcode.com/problems/smallest-subsequence-of-distinct-characters/) | Smallest Subsequence of Distinct | Medium | 同[LC 316](https://leetcode.com/problems/remove-duplicate-letters/) |

---

[← 返回索引](index.md)
