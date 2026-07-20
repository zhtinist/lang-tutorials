# 区间问题 · Interval Problems

> 区间问题的核心技巧：**排序**（按 start 或 end）、**合并/分割/扫描线**。

---

## 一、区间合并 · [LC 56](https://leetcode.com/problems/merge-intervals/)

```python
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """
    合并所有重叠区间。按 start 排序，依次扩展。
    O(n log n)
    """
    if not intervals:
        return []

    intervals.sort(key=lambda x: x[0])
    ans: list[list[int]] = [intervals[0]]

    for start, end in intervals[1:]:
        last = ans[-1]
        if start <= last[1]:  # 重叠
            last[1] = max(last[1], end)  # 扩展
        else:
            ans.append([start, end])  # 新区间

    return ans
```

---

## 二、区间插入 · [LC 57](https://leetcode.com/problems/insert-interval/)

```python
def insert_interval(
    intervals: list[list[int]], new_interval: list[int]
) -> list[list[int]]:
    """
    在有序不重叠的区间列表中插入新区间。
    分三部分：不重叠的左侧、合并中间、不重叠的右侧。
    """
    ans: list[list[int]] = []
    i = 0
    n = len(intervals)
    s, e = new_interval

    # 1. 不重叠的左侧
    while i < n and intervals[i][1] < s:
        ans.append(intervals[i])
        i += 1

    # 2. 合并重叠区间
    while i < n and intervals[i][0] <= e:
        s = min(s, intervals[i][0])
        e = max(e, intervals[i][1])
        i += 1
    ans.append([s, e])

    # 3. 不重叠的右侧
    while i < n:
        ans.append(intervals[i])
        i += 1

    return ans
```

---

## 三、区间交集 · [LC 986](https://leetcode.com/problems/interval-list-intersections/)

```python
def interval_intersection(
    first: list[list[int]], second: list[list[int]]
) -> list[list[int]]:
    """
    两个区间列表的交集。双指针扫描。
    """
    ans: list[list[int]] = []
    i = j = 0

    while i < len(first) and j < len(second):
        a1, a2 = first[i]
        b1, b2 = second[j]

        lo = max(a1, b1)
        hi = min(a2, b2)

        if lo <= hi:  # 有交集
            ans.append([lo, hi])

        # 谁结束得早谁移动
        if a2 < b2:
            i += 1
        else:
            j += 1

    return ans
```

---

## 四、会议室问题

### 4.1 会议是否冲突 · [LC 252](https://leetcode.com/problems/meeting-rooms/)（会员题）

```python
def can_attend_meetings(intervals: list[list[int]]) -> bool:
    """判断是否所有会议可以不冲突地参加。"""
    intervals.sort(key=lambda x: x[0])
    for i in range(1, len(intervals)):
        if intervals[i][0] < intervals[i - 1][1]:
            return False
    return True
```

### 4.2 最少会议室数量 · [LC 253](https://leetcode.com/problems/meeting-rooms-ii/)（会员题/扫描线）

```python
import heapq


def min_meeting_rooms(intervals: list[list[int]]) -> int:
    """
    最少需要多少个会议室。
    解法1：扫描线（差分数组）
    解法2：最小堆（存结束时间）
    """
    if not intervals:
        return 0

    # 解法2：最小堆
    intervals.sort(key=lambda x: x[0])
    heap: list[int] = []  # 存各会议室的结束时间
    ans = 0

    for start, end in intervals:
        # 弹出所有已结束的会议
        while heap and heap[0] <= start:
            heapq.heappop(heap)
        heapq.heappush(heap, end)
        ans = max(ans, len(heap))

    return ans


def min_meeting_rooms_scan(intervals: list[list[int]]) -> int:
    """扫描线解法。"""
    events: list[tuple[int, int]] = []
    for s, e in intervals:
        events.append((s, 1))   # 开始
        events.append((e, -1))  # 结束
    events.sort()

    cur = ans = 0
    for _, delta in events:
        cur += delta
        ans = max(ans, cur)
    return ans
```

---

## 五、删除覆盖区间 · [LC 1288](https://leetcode.com/problems/remove-covered-intervals/)

```python
def remove_covered_intervals(intervals: list[list[int]]) -> int:
    """
    删除被覆盖的区间。按 start 升序，同 start 按 end 降序。
    """
    intervals.sort(key=lambda x: (x[0], -x[1]))
    ans = 0
    max_end = 0

    for start, end in intervals:
        if end > max_end:
            ans += 1
            max_end = end
        # 若 end <= max_end，当前区间被覆盖

    return ans
```

---

## 六、天际线问题 · [LC 218](https://leetcode.com/problems/the-skyline-problem/) 🔥

```python
import heapq


def get_skyline(buildings: list[list[int]]) -> list[list[int]]:
    """
    扫描线 + 最大堆。
    关键点：每个建筑物的左右边界。
    """
    # 把建筑物拆成事件：(x, height, type)
    # type: 0=开始, 1=结束
    events: list[tuple[int, int, int]] = []
    for left, right, height in buildings:
        events.append((left, height, 0))
        events.append((right, height, 1))

    # 排序：x 小的先处理；x 相同时开始优先于结束
    events.sort(key=lambda e: (e[0], e[2], -e[1] if e[2] == 0 else e[1]))

    # 最大堆：(-height, x_end)
    heap: list[tuple[int, int]] = [(0, float("inf"))]  # 地面
    ans: list[list[int]] = []

    for x, h, typ in events:
        if typ == 0:  # 开始
            heapq.heappush(heap, (-h, 0))  # 简化版
        else:  # 结束
            # 标记删除（惰性删除）
            pass

        # 当前最高高度
        cur_max = -heap[0][0]
        if not ans or cur_max != ans[-1][1]:
            if ans and ans[-1][0] == x:
                ans[-1][1] = max(ans[-1][1], cur_max)
            else:
                ans.append([x, cur_max])

    return ans
```

---

## 七、总结

| 问题 | 方法 | 复杂度 |
|------|------|--------|
| 合并区间 | 排序 + 一次遍历 | O(n log n) |
| 插入区间 | 三步骤（左/中/右） | O(n) |
| 区间交集 | 双指针 | O(m+n) |
| 会议室 | 最小堆 / 扫描线 | O(n log n) |
| 覆盖区间 | 按start升序end降序 | O(n log n) |
| 天际线 | 扫描线 + 最大堆 | O(n log n) |

---

## 八、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 56](https://leetcode.com/problems/merge-intervals/) | Merge Intervals | Medium | 排序合并 |
| [LC 57](https://leetcode.com/problems/insert-interval/) | Insert Interval | Medium | 三分法 |
| [LC 986](https://leetcode.com/problems/interval-list-intersections/) | Interval List Intersections | Medium | 双指针 |
| [LC 252](https://leetcode.com/problems/meeting-rooms/) | Meeting Rooms | Easy🔒 | 排序判断 |
| [LC 253](https://leetcode.com/problems/meeting-rooms-ii/) | Meeting Rooms II | Medium🔒 | 堆/扫描线 |
| [LC 1288](https://leetcode.com/problems/remove-covered-intervals/) | Remove Covered Intervals | Medium | 排序贪心 |
| [LC 218](https://leetcode.com/problems/the-skyline-problem/) | The Skyline Problem | Hard | 扫描线 |
| [LC 759](https://leetcode.com/problems/employee-free-time/) | Employee Free Time | Hard🔒 | 合并间隔 |
| [LC 1229](https://leetcode.com/problems/meeting-scheduler/) | Meeting Scheduler | Medium🔒 | 双指针找公共空闲 |

---

[← 返回索引](index.md)
