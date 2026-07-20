# 前缀和 & 差分数组 · Prefix Sum & Difference Array

> **前缀和**：快速求子数组和，O(n) 预处理后 O(1) 查询。
> **差分数组**：快速对区间进行增减操作，O(n) 预处理后 O(1) 区间修改。

---

## 一、一维前缀和

### 模板

```python
class PrefixSum:
    """前缀和：pre_sum[i] = nums[0] + ... + nums[i-1]"""

    def __init__(self, nums: list[int]) -> None:
        self.pre_sum = [0] * (len(nums) + 1)
        for i, v in enumerate(nums):
            self.pre_sum[i + 1] = self.pre_sum[i] + v

    def query(self, left: int, right: int) -> int:
        """
        查询 nums[left..right] (闭区间) 的和。O(1)
        使用：pre_sum[right+1] - pre_sum[left]
        """
        return self.pre_sum[right + 1] - self.pre_sum[left]
```

### 基本原理

```
nums  = [3, 5, 2, -1, 4]
      ↓
pre   = [0, 3, 8, 10, 9, 13]  # pre[i] = sum(nums[0..i-1])

sum(nums[1..3]) = pre[4] - pre[1] = 9 - 3 = 6  (5 + 2 + -1 = 6)
```

### [LC 303](https://leetcode.com/problems/range-sum-query-immutable/) 区域和检索（数组不可变）

```python
class NumArray:
    def __init__(self, nums: list[int]):
        self.pre_sum = [0]
        for v in nums:
            self.pre_sum.append(self.pre_sum[-1] + v)

    def sum_range(self, left: int, right: int) -> int:
        return self.pre_sum[right + 1] - self.pre_sum[left]
```

---

## 二、和为 K 的子数组 · [LC 560](https://leetcode.com/problems/subarray-sum-equals-k/)

> 前缀和 + 哈希表：`pre_sum[j] - pre_sum[i] = k` → 等价于 `pre_sum[i] = pre_sum[j] - k`

```python
from collections import defaultdict


def subarray_sum(nums: list[int], k: int) -> int:
    """统计和为 k 的子数组个数。O(n)"""
    pre_sum_count: dict[int, int] = defaultdict(int)
    pre_sum_count[0] = 1  # 空子数组和为0

    cur_sum = ans = 0
    for v in nums:
        cur_sum += v
        # 找前面出现过的 pre_sum[j] - k
        target = cur_sum - k
        if target in pre_sum_count:
            ans += pre_sum_count[target]
        pre_sum_count[cur_sum] += 1

    return ans
```

> **同类扩展**：[LC 974](https://leetcode.com/problems/subarray-sums-divisible-by-k/) 和可被 K 整除的子数组（同余数技巧），[LC 523](https://leetcode.com/problems/continuous-subarray-sum/) 连续子数组和为 K 的倍数。

---

## 三、二维前缀和

### 模板

```python
class PrefixSum2D:
    """
    二维前缀和：pre[i][j] = sum(matrix[0..i-1][0..j-1])
    公式：
      pre[i][j] = pre[i-1][j] + pre[i][j-1] - pre[i-1][j-1] + matrix[i-1][j-1]
    查询 (r1,c1) 到 (r2,c2):
      pre[r2+1][c2+1] - pre[r1][c2+1] - pre[r2+1][c1] + pre[r1][c1]
    """

    def __init__(self, matrix: list[list[int]]) -> None:
        m, n = len(matrix), len(matrix[0])
        self.pre = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                self.pre[i][j] = (
                    self.pre[i - 1][j]
                    + self.pre[i][j - 1]
                    - self.pre[i - 1][j - 1]
                    + matrix[i - 1][j - 1]
                )

    def query(self, r1: int, c1: int, r2: int, c2: int) -> int:
        """查询子矩阵 (r1,c1) 到 (r2,c2) 闭区间的和。O(1)"""
        return (
            self.pre[r2 + 1][c2 + 1]
            - self.pre[r1][c2 + 1]
            - self.pre[r2 + 1][c1]
            + self.pre[r1][c1]
        )
```

### 图解

```
pre[i-1][j-1]    pre[i-1][j]
       ↓              ↓
  ┌─────────┐  ┌──────────┐
  │  A      │  │   B      │
  └─────────┘  └──────────┘

pre[i][j-1]     matrix[i-1][j-1]
       ↓              ↓
  ┌─────────┐  ┌──────────┐
  │  C      │  │   D ★    │   ★ = D = pre[i-1][j] + pre[i][j-1] - pre[i-1][j-1] + val
  └─────────┘  └──────────┘

查询区域 = pre[r2+1][c2+1] - 上面 - 左边 + 左上角（被减了两次）
```

### [LC 304](https://leetcode.com/problems/range-sum-query-2d-immutable/) 二维区域和检索

```python
class NumMatrix:
    def __init__(self, matrix: list[list[int]]):
        m, n = len(matrix), len(matrix[0])
        self.pre = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(m):
            for j in range(n):
                self.pre[i + 1][j + 1] = (
                    self.pre[i][j + 1]
                    + self.pre[i + 1][j]
                    - self.pre[i][j]
                    + matrix[i][j]
                )

    def sum_region(self, r1: int, c1: int, r2: int, c2: int) -> int:
        return (
            self.pre[r2 + 1][c2 + 1]
            - self.pre[r1][c2 + 1]
            - self.pre[r2 + 1][c1]
            + self.pre[r1][c1]
        )
```

---

## 四、差分数组

> 差分数组 `diff[i] = nums[i] - nums[i-1]`。对区间 `[l, r]` 统一加 `val` 只需 `diff[l] += val`, `diff[r+1] -= val`。最后做前缀和还原。

### 模板

```python
class Difference:
    """差分数组：支持区间增减操作，O(1) 修改。"""

    def __init__(self, nums: list[int]) -> None:
        self.diff = [0] * len(nums)
        self.diff[0] = nums[0]
        for i in range(1, len(nums)):
            self.diff[i] = nums[i] - nums[i - 1]

    def increment(self, left: int, right: int, val: int) -> None:
        """对区间 [left, right] 所有元素加 val。O(1)"""
        self.diff[left] += val
        if right + 1 < len(self.diff):
            self.diff[right + 1] -= val

    def result(self) -> list[int]:
        """还原为原数组。O(n)"""
        res = [0] * len(self.diff)
        res[0] = self.diff[0]
        for i in range(1, len(self.diff)):
            res[i] = res[i - 1] + self.diff[i]
        return res
```

### 流程示例

```
nums  = [8, 2, 6, 3, 1]
diff  = [8, -6, 4, -3, -2]  # diff[i] = nums[i] - nums[i-1]

对 [1, 3] 每个元素 +3:
  diff[1] += 3  →  diff = [8, -3, 4, -3, -2]
  diff[4] -= 3  →  diff = [8, -3, 4, -3, -5]

还原（前缀和）:
  res   = [8, 5, 9, 6, 1]
          ↓   ↓   ↓   ↓   ↓
原 nums  [8, 2, 6, 3, 1]→ +3 → [8, 5, 9, 6, 1] ✓
```

### [LC 1109](https://leetcode.com/problems/corporate-flight-bookings/) 航班预订统计

```python
def corp_flight_bookings(bookings: list[list[int]], n: int) -> list[int]:
    """
    bookings[i] = [first, last, seats] 表示从 first 到 last 每个航班预订 seats 个座位。
    返回每个航班的总预订数。
    """
    diff = [0] * n
    for first, last, seats in bookings:
        diff[first - 1] += seats
        if last < n:
            diff[last] -= seats

    # 前缀和还原
    for i in range(1, n):
        diff[i] += diff[i - 1]

    return diff
```

### [LC 1094](https://leetcode.com/problems/car-pooling/) 拼车

```python
def car_pooling(trips: list[list[int]], capacity: int) -> bool:
    """
    trips[i] = [num_passengers, from, to]
    判断是否能在整个行程中不超过 capacity。
    """
    stations = 1001  # 题目限制
    diff = [0] * stations

    for num, fr, to in trips:
        diff[fr] += num    # 上车
        diff[to] -= num    # 下车（注意是 to 不是 to+1！）

    cur = 0
    for d in diff:
        cur += d
        if cur > capacity:
            return False
    return True
```

---

## 五、前缀积

> 类似前缀和，但不支持查询（因为要除以零的问题）。常用于 "除自身外的数组乘积"。

### [LC 238](https://leetcode.com/problems/product-of-array-except-self/) 除自身外数组的乘积

```python
def product_except_self(nums: list[int]) -> list[int]:
    """前后缀分解：answer[i] = 左边乘积 × 右边乘积"""
    n = len(nums)
    ans = [1] * n

    # 左侧乘积
    prefix = 1
    for i in range(n):
        ans[i] = prefix
        prefix *= nums[i]

    # 右侧乘积
    suffix = 1
    for i in range(n - 1, -1, -1):
        ans[i] *= suffix
        suffix *= nums[i]

    return ans
```

---

## 六、总结

| 技巧 | 预处理 | 查询/修改 | 应用 |
|------|--------|-----------|------|
| 一维前缀和 | O(n) | O(1) 区间和 | 子数组和 |
| 二维前缀和 | O(mn) | O(1) 子矩阵和 | 矩阵区域和 |
| 前缀和+哈希 | - | O(n) 整体 | 和为 K 的子数组 |
| 差分数组 | O(n) | O(1) 区间修改 | 区间增减、订票、拼车 |
| 前后缀积 | O(n) | O(1) 查某个位置 | 除自身外的乘积 |

---

## 七、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 303](https://leetcode.com/problems/range-sum-query-immutable/) | Range Sum Query (Immutable) | Easy | 一维前缀和模板 |
| [LC 304](https://leetcode.com/problems/range-sum-query-2d-immutable/) | Range Sum Query 2D | Medium | 二维前缀和模板 |
| [LC 560](https://leetcode.com/problems/subarray-sum-equals-k/) | Subarray Sum Equals K | Medium | 前缀和+哈希表 |
| [LC 974](https://leetcode.com/problems/subarray-sums-divisible-by-k/) | Subarray Sums Divisible by K | Medium | 前缀和+同余 |
| [LC 523](https://leetcode.com/problems/continuous-subarray-sum/) | Continuous Subarray Sum | Medium | 前缀和+同余+索引 |
| [LC 525](https://leetcode.com/problems/contiguous-array/) | Contiguous Array | Medium | 前缀和+变换(0→-1) |
| [LC 238](https://leetcode.com/problems/product-of-array-except-self/) | Product of Array Except Self | Medium | 前后缀积 |
| [LC 370](https://leetcode.com/problems/range-addition/) | Range Addition | Medium🔒 | 差分数组模板 |
| [LC 1109](https://leetcode.com/problems/corporate-flight-bookings/) | Corporate Flight Bookings | Medium | 差分数组 |
| [LC 1094](https://leetcode.com/problems/car-pooling/) | Car Pooling | Medium | 差分数组 |
| [LC 724](https://leetcode.com/problems/find-pivot-index/) | Find Pivot Index | Easy | 前缀和 |

---

[← 返回索引](index.md)
