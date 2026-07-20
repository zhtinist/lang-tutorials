# 线段树 & 树状数组 · Segment Tree & Fenwick Tree

> 两者都解决**区间查询**与**单点/区间更新**问题。树状数组代码少但只支持可逆运算（和、XOR），线段树功能更强（支持任何可结合运算，包括 max/min）。

---

## 一、树状数组 · Fenwick Tree (BIT)

> 核心：`tree[i]` 存储 `[i - lowbit(i) + 1, i]` 区间的和。
> `lowbit(x) = x & (-x)`

### 基础实现

```python
class FenwickTree:
    """树状数组：单点更新 O(log n)，前缀和查询 O(log n)。"""

    def __init__(self, n: int):
        self.n = n
        self.tree = [0] * (n + 1)  # 1-indexed

    @staticmethod
    def lowbit(x: int) -> int:
        return x & -x

    def add(self, idx: int, delta: int) -> None:
        """在位置 idx 加 delta。O(log n)"""
        i = idx
        while i <= self.n:
            self.tree[i] += delta
            i += self.lowbit(i)

    def prefix_sum(self, idx: int) -> int:
        """查询 [1, idx] 的和。O(log n)"""
        s = 0
        i = idx
        while i > 0:
            s += self.tree[i]
            i -= self.lowbit(i)
        return s

    def range_sum(self, left: int, right: int) -> int:
        """查询 [left, right] 的和。O(log n)"""
        return self.prefix_sum(right) - self.prefix_sum(left - 1)
```

### 建树

```python
def build_fenwick(nums: list[int]) -> FenwickTree:
    """O(n) 建树。"""
    n = len(nums)
    bit = FenwickTree(n)
    # 方法1：O(n log n)
    # for i, v in enumerate(nums, 1):
    #     bit.add(i, v)

    # 方法2：O(n) 直接填充
    for i in range(1, n + 1):
        bit.tree[i] += nums[i - 1]
        j = i + bit.lowbit(i)
        if j <= n:
            bit.tree[j] += bit.tree[i]
    return bit
```

### [LC 307](https://leetcode.com/problems/range-sum-query-mutable/) 区域和检索（数组可修改）

```python
class NumArray:
    def __init__(self, nums: list[int]):
        self.nums = nums
        self.bit = build_fenwick(nums)

    def update(self, index: int, val: int) -> None:
        delta = val - self.nums[index]
        self.nums[index] = val
        self.bit.add(index + 1, delta)

    def sum_range(self, left: int, right: int) -> int:
        return self.bit.range_sum(left + 1, right + 1)
```

---

## 二、树状数组应用

### 2.1 逆序对计数 · [LC 315](https://leetcode.com/problems/count-of-smaller-numbers-after-self/)（计算右侧小于当前元素的个数）

```python
def count_smaller(nums: list[int]) -> list[int]:
    """
    从右往左遍历，用 BIT 统计已遍历的元素中小于当前值的个数。
    需要离散化。
    """
    # 离散化
    sorted_unique = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(sorted_unique)}  # 1-indexed

    bit = FenwickTree(len(sorted_unique))
    ans = [0] * len(nums)

    for i in range(len(nums) - 1, -1, -1):
        r = rank[nums[i]]
        ans[i] = bit.prefix_sum(r - 1)  # 小于当前值的个数
        bit.add(r, 1)  # 把当前值加入 BIT

    return ans
```

### 2.2 区间和的个数 · [LC 327](https://leetcode.com/problems/count-of-range-sum/)

```python
def count_range_sum(nums: list[int], lower: int, upper: int) -> int:
    """前缀和 + BIT + 离散化。"""
    pre = [0]
    for v in nums:
        pre.append(pre[-1] + v)

    # 离散化所有可能的值：pre[i], pre[i]-upper, pre[i]-lower
    all_vals: set[int] = set()
    for s in pre:
        all_vals.add(s)
        all_vals.add(s - upper)
        all_vals.add(s - lower)
    sorted_vals = sorted(all_vals)
    rank = {v: i + 1 for i, v in enumerate(sorted_vals)}

    bit = FenwickTree(len(sorted_vals))
    ans = 0

    for s in pre:
        # 找满足 lower <= s - pre[j] <= upper 的 pre[j] 的数量
        left = rank[s - upper]
        right = rank[s - lower]
        ans += bit.range_sum(left, right)
        bit.add(rank[s], 1)

    return ans
```

---

## 三、线段树 · Segment Tree

> 线段树是一棵平衡二叉树，每个节点存储一个区间的聚合值。
> 支持：**区间查询** O(log n)、**单点更新** O(log n)、**区间更新（懒标记）** O(log n)。

### 3.1 基础线段树（数组实现）

```python
class SegmentTree:
    """线段树：区间求和。1-indexed 数组存储完全二叉树。"""

    def __init__(self, nums: list[int]):
        self.n = len(nums)
        self.tree = [0] * (4 * self.n)  # 4n 空间保证足够
        self._build(nums, 1, 0, self.n - 1)

    def _build(self, nums: list[int], node: int, start: int, end: int) -> None:
        """递归建树。O(n)"""
        if start == end:
            self.tree[node] = nums[start]
            return
        mid = start + (end - start) // 2
        left = 2 * node
        right = 2 * node + 1
        self._build(nums, left, start, mid)
        self._build(nums, right, mid + 1, end)
        self.tree[node] = self.tree[left] + self.tree[right]

    def query(self, ql: int, qr: int) -> int:
        """查询 [ql, qr] 的区间和。O(log n)"""
        return self._query(1, 0, self.n - 1, ql, qr)

    def _query(
        self, node: int, start: int, end: int, ql: int, qr: int
    ) -> int:
        if ql > end or qr < start:
            return 0  # 无交集
        if ql <= start and end <= qr:
            return self.tree[node]  # 完全覆盖
        mid = start + (end - start) // 2
        left = self._query(2 * node, start, mid, ql, qr)
        right = self._query(2 * node + 1, mid + 1, end, ql, qr)
        return left + right

    def update(self, idx: int, val: int) -> None:
        """单点更新：将 nums[idx] 改为 val。O(log n)"""
        self._update(1, 0, self.n - 1, idx, val)

    def _update(
        self, node: int, start: int, end: int, idx: int, val: int
    ) -> None:
        if start == end:
            self.tree[node] = val
            return
        mid = start + (end - start) // 2
        left = 2 * node
        right = 2 * node + 1
        if idx <= mid:
            self._update(left, start, mid, idx, val)
        else:
            self._update(right, mid + 1, end, idx, val)
        self.tree[node] = self.tree[left] + self.tree[right]
```

### 3.2 带懒标记的线段树（区间更新）

```python
class LazySegmentTree:
    """带懒标记的线段树：支持区间增减和区间查询。"""

    def __init__(self, nums: list[int]):
        self.n = len(nums)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)  # 懒标记
        self._build(nums, 1, 0, self.n - 1)

    def _build(self, nums: list[int], node: int, start: int, end: int) -> None:
        if start == end:
            self.tree[node] = nums[start]
            return
        mid = start + (end - start) // 2
        self._build(nums, 2 * node, start, mid)
        self._build(nums, 2 * node + 1, mid + 1, end)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def _push_down(self, node: int, start: int, end: int) -> None:
        """将懒标记下推到子节点。"""
        if self.lazy[node] == 0:
            return
        mid = start + (end - start) // 2
        left, right = 2 * node, 2 * node + 1

        # 左子节点
        self.tree[left] += self.lazy[node] * (mid - start + 1)
        self.lazy[left] += self.lazy[node]

        # 右子节点
        self.tree[right] += self.lazy[node] * (end - mid)
        self.lazy[right] += self.lazy[node]

        self.lazy[node] = 0  # 清除当前节点的懒标记

    def range_add(self, ql: int, qr: int, delta: int) -> None:
        """区间 [ql, qr] 所有元素加 delta。O(log n)"""
        self._range_add(1, 0, self.n - 1, ql, qr, delta)

    def _range_add(
        self, node: int, start: int, end: int, ql: int, qr: int, delta: int
    ) -> None:
        if ql > end or qr < start:
            return
        if ql <= start and end <= qr:
            self.tree[node] += delta * (end - start + 1)
            self.lazy[node] += delta
            return

        self._push_down(node, start, end)
        mid = start + (end - start) // 2
        self._range_add(2 * node, start, mid, ql, qr, delta)
        self._range_add(2 * node + 1, mid + 1, end, ql, qr, delta)
        self.tree[node] = self.tree[2 * node] + self.tree[2 * node + 1]

    def query(self, ql: int, qr: int) -> int:
        """区间 [ql, qr] 求和。O(log n)"""
        return self._query(1, 0, self.n - 1, ql, qr)

    def _query(
        self, node: int, start: int, end: int, ql: int, qr: int
    ) -> int:
        if ql > end or qr < start:
            return 0
        if ql <= start and end <= qr:
            return self.tree[node]

        self._push_down(node, start, end)
        mid = start + (end - start) // 2
        left = self._query(2 * node, start, mid, ql, qr)
        right = self._query(2 * node + 1, mid + 1, end, ql, qr)
        return left + right
```

---

## 四、BIT vs 线段树 对比

| 维度 | 树状数组 BIT | 线段树 Segment Tree |
|------|-------------|-------------------|
| 代码量 | 少（~15行） | 多（~60行） |
| 空间 | O(n) | O(4n) |
| 单点更新 | O(log n) | O(log n) |
| 区间查询 | O(log n) | O(log n) |
| 区间更新 | ❌ 本身不支持（需扩展） | ✅ 懒标记 |
| 支持运算 | 可逆运算（+, XOR） | 任何可结合运算（+, ×, max, min） |
| 常量因子 | 小 | 大 |

> **首选 BIT**，除非需要区间更新或不可逆运算（如最大值）。

---

## 五、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 307](https://leetcode.com/problems/range-sum-query-mutable/) | Range Sum Query (Mutable) | Medium | BIT/线段树 |
| [LC 315](https://leetcode.com/problems/count-of-smaller-numbers-after-self/) | Count of Smaller Numbers After Self | Hard | BIT+离散化 |
| [LC 327](https://leetcode.com/problems/count-of-range-sum/) | Count of Range Sum | Hard | BIT+离散化 |
| [LC 493](https://leetcode.com/problems/reverse-pairs/) | Reverse Pairs | Hard | BIT+离散化 |
| [LC 308](https://leetcode.com/problems/range-sum-query-2d-mutable/) | Range Sum Query 2D (Mutable) | Hard🔒 | 2D BIT |
| [LC 218](https://leetcode.com/problems/the-skyline-problem/) | The Skyline Problem | Hard | 线段树/扫描线 |
| [LC 699](https://leetcode.com/problems/falling-squares/) | Falling Squares | Hard | 线段树+最大值 |
| [LC 715](https://leetcode.com/problems/range-module/) | Range Module | Hard | 线段树(动态开点) |
| [LC 732](https://leetcode.com/problems/my-calendar-iii/) | My Calendar III | Hard | 线段树(动态开点) |

---

[← 返回索引](index.md)
