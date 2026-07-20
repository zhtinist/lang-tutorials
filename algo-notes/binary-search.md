# 二分搜索 · Binary Search

> 核心框架：将搜索空间不断折半缩小，每次排除一半不可能的区域。关键是明确**搜索区间**的边界定义。

---

## 一、基础二分查找

### 统一模板（闭区间 `[left, right]`）

```python
from typing import TypeVar

T = TypeVar("T")


def binary_search(nums: list[int], target: int) -> int:
    """
    在有序数组 nums 中查找 target，返回索引，找不到返回 -1。
    闭区间 [left, right] 写法 —— 推荐统一使用此模板。
    """
    left, right = 0, len(nums) - 1

    while left <= right:  # 闭区间：left == right 时区间仍有1个元素
        mid = left + (right - left) // 2  # 防溢出写法

        if nums[mid] == target:
            return mid          # 找到目标，直接返回
        elif nums[mid] < target:
            left = mid + 1      # target 在右半部分
        else:  # nums[mid] > target
            right = mid - 1     # target 在左半部分

    return -1  # 搜索区间为空，未找到
```

### 开区间写法 `[left, right)` —— 了解即可

```python
def binary_search_open(nums: list[int], target: int) -> int:
    left, right = 0, len(nums)
    while left < right:  # 开区间：left == right 区间为空
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid  # 注意：右开区间，不包含 right
    return -1
```

### 细节要点

| 细节 | 说明 |
|------|------|
| `mid = left + (right - left) // 2` | 防 `(left + right)` 溢出 |
| 循环条件 `while left <= right` | 闭区间写法，最后一轮 `left == right` |
| `left = mid + 1` | 因为 `mid` 已检查过 |
| 时间复杂度 | O(log n) |
| 空间复杂度 | O(1) |

---

## 二、查找左侧边界（Lower Bound）

查找 **第一个 ≥ target** 的位置（即 `bisect_left`）。

```python
def lower_bound(nums: list[int], target: int) -> int:
    """
    返回第一个 >= target 的索引。
    若 target 大于所有元素，返回 len(nums)。
    等价于 Python bisect.bisect_left。
    """
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] >= target:
            right = mid - 1   # 收缩右边界，找更左侧的
        else:
            left = mid + 1

    return left  # left = 第一个 >= target 的位置


def search_left_bound(nums: list[int], target: int) -> int:
    """
    查找 target 的左侧边界（第一个等于 target 的索引）。
    找不到返回 -1。
    """
    idx = lower_bound(nums, target)
    if idx == len(nums) or nums[idx] != target:
        return -1
    return idx
```

### 图解

```
nums = [1, 2, 2, 2, 3]  target = 2

lower_bound 返回 1（第一个2的位置）
```

---

## 三、查找右侧边界（Upper Bound）

查找 **第一个 > target** 的位置（即 `bisect_right`）。

```python
def upper_bound(nums: list[int], target: int) -> int:
    """
    返回第一个 > target 的索引。
    等价于 Python bisect.bisect_right。
    """
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] > target:
            right = mid - 1
        else:
            left = mid + 1

    return left  # left = 第一个 > target 的位置


def search_right_bound(nums: list[int], target: int) -> int:
    """
    查找 target 的右侧边界（最后一个等于 target 的索引）。
    找不到返回 -1。
    """
    idx = upper_bound(nums, target) - 1
    if idx < 0 or nums[idx] != target:
        return -1
    return idx
```

---

## 四、二分答案（值域二分）

当问题具有**单调性**：越大越容易/越小越难，且答案在一个已知范围内时使用。

### 通用模板

```python
def binary_search_answer(check: callable, lo: int, hi: int) -> int:
    """
    在 [lo, hi] 上二分搜索，找到满足 check 的最小值。
    check(x) 表示 x 是否可行，要求 check 具有单调性：
    若 check(x) == True 则对所有 y > x 都有 check(y) == True。
    """
    left, right = lo, hi
    while left <= right:
        mid = left + (right - left) // 2
        if check(mid):
            right = mid - 1  # 可行，尝试更小的值
        else:
            left = mid + 1   # 不可行，需要更大的值
    return left  # 第一个可行的值
```

### 例题 1：[LC 875](https://leetcode.com/problems/koko-eating-bananas/) 爱吃香蕉的珂珂

```python
def min_eating_speed(piles: list[int], h: int) -> int:
    """
    返回能在 h 小时内吃完所有香蕉的最小速度 k。
    每小时只能选一堆吃，速度 k 表示每小时吃 k 根。
    """

    def can_finish(k: int) -> bool:
        hours = 0
        for pile in piles:
            hours += (pile + k - 1) // k  # 向上取整
        return hours <= h

    lo, hi = 1, max(piles)
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if can_finish(mid):
            hi = mid - 1
        else:
            lo = mid + 1
    return lo
```

### 例题 2：[LC 1011](https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/) 在 D 天内送达包裹的能力

```python
def ship_within_days(weights: list[int], days: int) -> int:
    """返回能在 days 天内运完所有包裹的最小运载能力。"""

    def can_ship(capacity: int) -> bool:
        day_count, cur_weight = 1, 0
        for w in weights:
            if cur_weight + w > capacity:
                day_count += 1
                cur_weight = 0
            cur_weight += w
        return day_count <= days

    lo, hi = max(weights), sum(weights)
    while lo <= hi:
        mid = lo + (hi - lo) // 2
        if can_ship(mid):
            hi = mid - 1
        else:
            lo = mid + 1
    return lo
```

---

## 五、旋转数组二分

### [LC 33](https://leetcode.com/problems/search-in-rotated-sorted-array/) 搜索旋转排序数组（无重复元素）

```python
def search_rotated(nums: list[int], target: int) -> int:
    """
    在旋转排序数组中搜索 target，返回索引或 -1。
    关键：每次二分，mid 至少有一侧是有序的。
    """
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid

        # 判断哪一侧有序
        if nums[left] <= nums[mid]:  # 左侧有序
            if nums[left] <= target < nums[mid]:
                right = mid - 1  # target 在左侧
            else:
                left = mid + 1   # target 在右侧
        else:  # 右侧有序
            if nums[mid] < target <= nums[right]:
                left = mid + 1   # target 在右侧
            else:
                right = mid - 1  # target 在左侧

    return -1
```

### [LC 81](https://leetcode.com/problems/search-in-rotated-sorted-array-ii/) 搜索旋转排序数组 II（含重复元素）

```python
def search_rotated_ii(nums: list[int], target: int) -> bool:
    """
    含重复元素时，当 nums[left] == nums[mid] == nums[right]，
    无法判断哪侧有序，只能 left += 1, right -= 1 缩小区间。
    """
    left, right = 0, len(nums) - 1

    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return True

        # 无法判断哪侧有序时，缩小范围
        if nums[left] == nums[mid] == nums[right]:
            left += 1
            right -= 1
        elif nums[left] <= nums[mid]:  # 左侧有序
            if nums[left] <= target < nums[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # 右侧有序
            if nums[mid] < target <= nums[right]:
                left = mid + 1
            else:
                right = mid - 1

    return False
```

### [LC 153](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/) 寻找旋转排序数组中的最小值

```python
def find_min_rotated(nums: list[int]) -> int:
    """旋转排序数组中的最小值，无重复元素。"""
    left, right = 0, len(nums) - 1

    while left < right:
        mid = left + (right - left) // 2
        if nums[mid] > nums[right]:
            left = mid + 1  # 最小值在右侧
        else:
            right = mid     # 最小值在左侧（含 mid）

    return nums[left]
```

---

## 六、总结对比

| 场景 | 模板 | 循环条件 | 返回值 |
|------|------|----------|--------|
| 精确查找 | `binary_search` | `left <= right` | `mid` 或 `-1` |
| 左边界 | `lower_bound` | `left <= right` | `left` |
| 右边界 | `upper_bound` | `left <= right` | `left`（结果需 `-1`） |
| 二分答案 | `binary_search_answer` | `left <= right` | `left` |
| 旋转数组 | 判断有序侧 | `left <= right` | `mid` 或 `-1` |

> **核心口诀**：闭区间 `[left, right]`，`left <= right`，`left = mid + 1`，`right = mid - 1`。

---

## 七、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 704](https://leetcode.com/problems/binary-search/) | Binary Search | Easy | 基础模板 |
| [LC 34](https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/) | Find First and Last Position | Medium | 左边界 + 右边界 |
| [LC 35](https://leetcode.com/problems/search-insert-position/) | Search Insert Position | Easy | lower_bound |
| [LC 69](https://leetcode.com/problems/sqrtx/) | Sqrt(x) | Easy | 二分答案 |
| [LC 162](https://leetcode.com/problems/find-peak-element/) | Find Peak Element | Medium | 二分 + 局部单调性 |
| [LC 33](https://leetcode.com/problems/search-in-rotated-sorted-array/) | Search in Rotated Sorted Array | Medium | 旋转数组二分 |
| [LC 81](https://leetcode.com/problems/search-in-rotated-sorted-array-ii/) | Search in Rotated Sorted Array II | Medium | 旋转 + 重复元素 |
| [LC 153](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/) | Find Minimum in Rotated Sorted Array | Medium | 旋转数组找最小值 |
| [LC 154](https://leetcode.com/problems/find-minimum-in-rotated-sorted-array-ii/) | Find Minimum in Rotated Sorted Array II | Hard | 旋转 + 重复 + 最小值 |
| [LC 875](https://leetcode.com/problems/koko-eating-bananas/) | Koko Eating Bananas | Medium | 二分答案 |
| [LC 1011](https://leetcode.com/problems/capacity-to-ship-packages-within-d-days/) | Capacity To Ship Packages | Medium | 二分答案 |
| [LC 410](https://leetcode.com/problems/split-array-largest-sum/) | Split Array Largest Sum | Hard | 二分答案（难题） |

---

[← 返回索引](index.md)
