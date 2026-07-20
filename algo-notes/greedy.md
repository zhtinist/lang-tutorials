# 贪心算法 · Greedy Algorithm

> 贪心：每一步都取**当前最优**的选择，期望最终得到全局最优。
> 贪心能用的前提是问题有**贪心选择性质**和**最优子结构**。贪心不一定正确，需要证明。

---

## 一、区间调度

### 1.1 无重叠区间 · [LC 435](https://leetcode.com/problems/non-overlapping-intervals/)

```python
def erase_overlap_intervals(intervals: list[list[int]]) -> int:
    """
    最少删除多少个区间使得剩余区间不重叠。
    贪心：按 end 排序，每次选择结束最早的区间。
    等价于：总数 - 最多不重叠的区间数。
    """
    if not intervals:
        return 0

    intervals.sort(key=lambda x: x[1])  # 按 end 排序
    count = 1
    end = intervals[0][1]

    for i in range(1, len(intervals)):
        if intervals[i][0] >= end:  # 不相交
            count += 1
            end = intervals[i][1]

    return len(intervals) - count
```

### 1.2 用最少数量的箭引爆气球 · [LC 452](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/)

```python
def find_min_arrow_shots(points: list[list[int]]) -> int:
    """
    等价于"最大重叠区间数"的贪心。
    按 end 排序，每支箭射在区间的最右端。
    """
    if not points:
        return 0

    points.sort(key=lambda x: x[1])
    arrows = 1
    arrow_pos = points[0][1]

    for start, end in points[1:]:
        if start > arrow_pos:
            arrows += 1
            arrow_pos = end

    return arrows
```

---

## 二、跳跃游戏

### 2.1 能否到达终点 · [LC 55](https://leetcode.com/problems/jump-game/)

```python
def can_jump(nums: list[int]) -> bool:
    """维护当前能跳到的最远距离。"""
    farthest = 0
    for i, jump in enumerate(nums):
        if i > farthest:
            return False  # 当前位置不可达
        farthest = max(farthest, i + jump)
    return True
```

### 2.2 最少跳跃次数 · [LC 45](https://leetcode.com/problems/jump-game-ii/)

```python
def jump(nums: list[int]) -> int:
    """
    贪心：每次在可达范围内，选跳到最远的那一步。
    实际上：维护当前步数的边界 end，边界扩大时步数+1。
    """
    n = len(nums)
    if n == 1:
        return 0

    farthest = end = jumps = 0

    for i in range(n - 1):
        farthest = max(farthest, i + nums[i])
        if i == end:  # 到达当前步数的最远边界
            jumps += 1
            end = farthest

    return jumps
```

---

## 三、加油站 · [LC 134](https://leetcode.com/problems/gas-station/)

```python
def can_complete_circuit(gas: list[int], cost: list[int]) -> int:
    """
    贪心：从累积剩余油量最低点的下一个位置出发。
    如果总油量 >= 总消耗，一定存在解。
    """
    total = cur = 0
    start = 0

    for i in range(len(gas)):
        total += gas[i] - cost[i]
        cur += gas[i] - cost[i]
        if cur < 0:
            # 从 0 到 i 都不可能是起点，从 i+1 重新开始
            start = i + 1
            cur = 0

    return start if total >= 0 else -1
```

---

## 四、任务调度器 · [LC 621](https://leetcode.com/problems/task-scheduler/)

```python
from collections import Counter


def least_interval(tasks: list[str], n: int) -> int:
    """
    给定冷却时间 n，同种任务至少间隔 n 个时间单位。
    贪心：先安排频率最高的任务，用其他任务填补冷却期。
    """
    freq = list(Counter(tasks).values())
    max_freq = max(freq)
    max_count = freq.count(max_freq)  # 有多少个最高频率的任务

    # 最小长度 = (max_freq - 1) * (n + 1) + max_count
    # 或任务总长度（任务够多填满冷却期）
    return max(len(tasks), (max_freq - 1) * (n + 1) + max_count)
```

---

## 五、按身高重建队列 · [LC 406](https://leetcode.com/problems/queue-reconstruction-by-height/)

```python
def reconstruct_queue(people: list[list[int]]) -> list[list[int]]:
    """
    (h, k) = 身高 h，前面有 k 个身高 ≥ h 的人。
    贪心：按 h 降序，同 h 按 k 升序，然后按 k 插入。
    """
    people.sort(key=lambda x: (-x[0], x[1]))
    ans: list[list[int]] = []

    for p in people:
        ans.insert(p[1], p)

    return ans
```

---

## 六、分发饼干 · [LC 455](https://leetcode.com/problems/assign-cookies/)

```python
def find_content_children(g: list[int], s: list[int]) -> int:
    """g=胃口值，s=饼干大小。每个孩子最多一块饼干。"""
    g.sort()
    s.sort()
    i = j = 0
    while i < len(g) and j < len(s):
        if s[j] >= g[i]:
            i += 1  # 满足了这个孩子
        j += 1
    return i
```

---

## 七、贪心 vs DP

| 维度 | 贪心 | 动态规划 |
|------|------|---------|
| 选择 | 只看当前最优，不回头 | 枚举所有可能，选最优 |
| 正确性 | 需要证明（反证/归纳） | 只要状态转移正确 |
| 复杂度 | O(n log n) 或更小 | O(n²) 或更小 |
| 适用性 | 不广泛 | 广泛 |
| 典型问题 | 区间调度、最小生成树、哈夫曼 | 背包、LIS、编辑距离 |

> **判断标准**：是否可以证明"当前最佳选择一定是全局最佳选择的一部分"。

---

## 八、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 435](https://leetcode.com/problems/non-overlapping-intervals/) | Non-overlapping Intervals | Medium | 区间调度 |
| [LC 452](https://leetcode.com/problems/minimum-number-of-arrows-to-burst-balloons/) | Minimum Arrows to Burst Balloons | Medium | 区间调度变体 |
| [LC 55](https://leetcode.com/problems/jump-game/) | Jump Game | Medium | 最远可达 |
| [LC 45](https://leetcode.com/problems/jump-game-ii/) | Jump Game II | Medium | 最少跳跃 |
| [LC 134](https://leetcode.com/problems/gas-station/) | Gas Station | Medium | 贪心找起点 |
| [LC 621](https://leetcode.com/problems/task-scheduler/) | Task Scheduler | Medium | 冷却时间 |
| [LC 406](https://leetcode.com/problems/queue-reconstruction-by-height/) | Queue Reconstruction | Medium | 排序插入 |
| [LC 455](https://leetcode.com/problems/assign-cookies/) | Assign Cookies | Easy | 双指针贪心 |
| [LC 605](https://leetcode.com/problems/can-place-flowers/) | Can Place Flowers | Easy | 种花 |
| [LC 763](https://leetcode.com/problems/partition-labels/) | Partition Labels | Medium | 区间贪心 |

---

[← 返回索引](index.md)
