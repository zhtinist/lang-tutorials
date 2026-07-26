# 数据结构的扩张 · Augmenting Data Structures

> CLRS 第14章的核心思想：不发明新的数据结构，而是在已有结构（这里是 BST）的每个节点上
> 附加一点"增强信息"，并保证插入/删除时能顺带把这些信息正确更新，
> 就能用同样的 O(h) 复杂度回答一些原本要 O(n) 才能回答的问题。
> 本文假设已熟悉 [binary-search-tree.md](binary-search-tree.md) 的 `TreeNode` 和基本插入/删除，不再重复讲解。

---

## 一、顺序统计树 (Order-Statistic Tree)

### 1.1 增强字段与维护规则

```
在每个节点上加一个字段 size：以该节点为根的子树中的节点总数（含自身）。

CLRS 的通用定理：给 BST 增加一个字段 f，如果 f(node) 可以只用
  - node 自己的数据（不需要看子树内部细节）
  - node.left 的增强字段 f(node.left)
  - node.right 的增强字段 f(node.right)
这三者计算出来，那么 f 就能在插入/删除本来就要走的 O(h) 路径上
"顺路"维护好，不需要额外遍历子树，总复杂度不变。

size 完全符合这个条件：
  size(node) = size(node.left) + size(node.right) + 1
所以插入/删除维护 size 仍然是 O(h)。
```

### 1.2 节点定义与插入

```python
class OSTreeNode:
    def __init__(
        self,
        val: int,
        left: "OSTreeNode | None" = None,
        right: "OSTreeNode | None" = None,
    ):
        self.val = val
        self.left = left
        self.right = right
        self.size = 1  # 增强字段：以此节点为根的子树中的节点总数（含自身）


def size(node: OSTreeNode | None) -> int:
    """空树 size 为 0，方便统一处理边界。"""
    return node.size if node else 0


def os_insert(root: OSTreeNode | None, val: int) -> OSTreeNode:
    """
    普通 BST 插入（同 binary-search-tree.md 的 insert_into_bst），
    只是回溯时顺便重新计算 size。
    """
    if root is None:
        return OSTreeNode(val)
    if val < root.val:
        root.left = os_insert(root.left, val)
    else:
        root.right = os_insert(root.right, val)
    root.size = size(root.left) + size(root.right) + 1
    return root
```

### 1.3 OS-SELECT(i)：查找第 i 小的元素

```
从根开始，看左子树大小 left_size = size(root.left)：
  - 如果 i == left_size + 1，根节点自己恰好就是第 i 小，直接返回。
  - 如果 i <= left_size，第 i 小在左子树里，递归 os_select(left, i)。
  - 否则第 i 小在右子树里，注意要把左子树和根节点都"跳过"，
    递归 os_select(right, i - left_size - 1)。
```

```python
def os_select(root: OSTreeNode | None, i: int) -> int | None:
    """OS-SELECT(i)：返回子树中第 i 小的元素（i 从 1 开始）。O(h)。"""
    if root is None:
        return None
    left_size = size(root.left)
    if i == left_size + 1:
        return root.val
    if i <= left_size:
        return os_select(root.left, i)
    return os_select(root.right, i - left_size - 1)
```

### 1.4 OS-RANK(x)：查找 x 的排名

```python
def os_rank(root: OSTreeNode | None, val: int) -> int:
    """
    OS-RANK(x)：返回 val 在树中的排名（从 1 开始）。O(h)。

    从根往下走：每往右走一步，说明当前节点以及它的整棵左子树
    都严格小于要找的值，排名要累加上 size(左子树) + 1。
    """
    rank = 0
    node = root
    while node is not None:
        if val < node.val:
            node = node.left
        elif val > node.val:
            rank += size(node.left) + 1
            node = node.right
        else:
            rank += size(node.left) + 1
            return rank
    return -1  # 未找到
```

### 1.5 正确性验证

```python
import random

random.seed(0)
mismatches_select = 0
mismatches_rank = 0
trials = 0

for _ in range(300):
    n = random.randint(1, 200)
    vals = random.sample(range(-10_000, 10_000), n)
    os_root: OSTreeNode | None = None
    for v in vals:
        os_root = os_insert(os_root, v)

    sorted_vals = sorted(vals)

    def check_size(node: OSTreeNode | None) -> int:
        if node is None:
            return 0
        left_count = check_size(node.left)
        right_count = check_size(node.right)
        assert node.size == left_count + right_count + 1, "size 字段维护错误"
        return left_count + right_count + 1

    check_size(os_root)
    assert size(os_root) == n

    for i in range(1, n + 1):
        trials += 1
        got = os_select(os_root, i)
        want = sorted_vals[i - 1]
        if got != want:
            mismatches_select += 1
        if os_rank(os_root, want) != i:
            mismatches_rank += 1

print(f"OS-Tree: {trials} 次单点校验，OS-SELECT 不匹配 {mismatches_select} 次，OS-RANK 不匹配 {mismatches_rank} 次")
# OS-Tree: 30116 次单点校验，OS-SELECT 不匹配 0 次，OS-RANK 不匹配 0 次
```

---

## 二、区间树 (Interval Tree)

### 2.1 增强字段：max

```
每个节点存一个区间 [low, high]，用 low 当作普通 BST 的 key（按 low 排序）。
再加一个增强字段 max：以该节点为根的子树中，所有区间 high 端点的最大值。

同样满足"通用定理"的条件：
  max(node) = max(node.high, max(node.left), max(node.right))
只依赖自己的数据 + 左右孩子的增强字段，所以插入时能在 O(h) 内维护好。
```

### 2.2 节点定义与插入

```python
class IntervalNode:
    def __init__(
        self,
        low: int,
        high: int,
        left: "IntervalNode | None" = None,
        right: "IntervalNode | None" = None,
    ):
        self.low = low
        self.high = high
        self.left = left
        self.right = right
        self.max = high  # 增强字段：以此节点为根的子树中所有区间 high 端点的最大值


def node_max(node: IntervalNode | None) -> float:
    return node.max if node else float("-inf")


def interval_insert(root: IntervalNode | None, low: int, high: int) -> IntervalNode:
    """按 low 值当作 BST key 插入，回溯时维护 max。"""
    if root is None:
        return IntervalNode(low, high)
    if low < root.low:
        root.left = interval_insert(root.left, low, high)
    else:
        root.right = interval_insert(root.right, low, high)
    root.max = max(root.high, node_max(root.left), node_max(root.right))
    return root
```

### 2.3 interval_search：查找任意一个重叠区间

```
两个闭区间 [a_low, a_high] 与 [b_low, b_high] 重叠，当且仅当：
  a_low <= b_high 且 b_low <= a_high
（等价于：不满足"一个区间完全在另一个区间左边"或"完全在右边"）

从根开始走：
  - 如果当前节点的区间就和查询区间重叠，直接返回它。
  - 否则看左孩子：
      若 node.left 存在且 node.left.max >= query.low，去左子树找；
      否则去右子树找。

为什么"否则去右子树"是安全的（不会漏掉左子树里真正重叠的区间）？
  - 若 node.left 不存在，左边本来就没有任何区间，只能去右边。
  - 若 node.left 存在但 node.left.max < query.low：
    node.left.max 是左子树里"最大的 high 端点"。
    如果左子树里存在某个区间 [a, b] 与 query 重叠，
    重叠条件要求 query.low <= b，但 b <= node.left.max < query.low，矛盾。
    所以左子树里不可能有任何区间与 query 重叠，可以放心跳过整棵左子树。

注意这个算法只保证找到"任意一个"重叠区间，不是"所有"重叠区间——
这正是 CLRS 对 INTERVAL-SEARCH 的原始定义。
```

```python
def _overlaps(a_low: int, a_high: int, b_low: int, b_high: int) -> bool:
    """两个闭区间 [a_low, a_high] 与 [b_low, b_high] 是否重叠。"""
    return a_low <= b_high and b_low <= a_high


def interval_search(root: IntervalNode | None, low: int, high: int) -> IntervalNode | None:
    """返回树中任意一个与查询区间 [low, high] 重叠的区间节点，不存在则返回 None。O(h)。"""
    node = root
    while node is not None and not _overlaps(node.low, node.high, low, high):
        if node.left is not None and node.left.max >= low:
            node = node.left
        else:
            node = node.right
    return node
```

### 2.4 正确性验证（与暴力线性扫描交叉校验）

```python
import random

def brute_force_any_overlap(intervals: list[tuple[int, int]], low: int, high: int) -> bool:
    return any(_overlaps(a, b, low, high) for a, b in intervals)

random.seed(1)
it_trials = 0
wrong_hit = 0             # interval_search 返回了一个实际上不重叠的区间
wrong_miss = 0            # interval_search 返回 None，但真实存在重叠区间
wrong_false_positive = 0  # brute force 说没有重叠，但 interval_search 返回了非 None
it_correct = 0

for _ in range(300):
    n = random.randint(1, 150)
    intervals: list[tuple[int, int]] = []
    it_root: IntervalNode | None = None
    for _ in range(n):
        a = random.randint(0, 200)
        b = a + random.randint(0, 30)
        intervals.append((a, b))
        it_root = interval_insert(it_root, a, b)

    for _ in range(30):
        it_trials += 1
        qlow = random.randint(-10, 210)
        qhigh = qlow + random.randint(0, 30)

        result = interval_search(it_root, qlow, qhigh)
        truth = brute_force_any_overlap(intervals, qlow, qhigh)

        if result is None:
            if truth:
                wrong_miss += 1
            else:
                it_correct += 1
        elif not _overlaps(result.low, result.high, qlow, qhigh):
            wrong_hit += 1
        elif not truth:
            wrong_false_positive += 1
        else:
            it_correct += 1

print(f"Interval-Tree: {it_trials} 次随机查询，正确 {it_correct} 次，"
      f"返回不重叠区间 {wrong_hit} 次，漏报 {wrong_miss} 次，误报 {wrong_false_positive} 次")
# Interval-Tree: 9000 次随机查询，正确 9000 次，返回不重叠区间 0 次，漏报 0 次，误报 0 次
```

---

## 三、关于旋转再平衡的说明

为了聚焦增强技术本身，下面用普通 BST 演示，不做旋转再平衡；生产实现通常在红黑树之上做同样的扩张（见 [red-black-tree.md](red-black-tree.md)，该文件里实现了红黑树插入）— 两者结合就是 CLRS 原书的完整方案。

```
额外要注意的一点：如果底层换成红黑树，插入/删除时的"旋转"操作本身
也会改变某些节点的子树结构（左右孩子互换位置），所以旋转代码里
除了维护红黑性质，还要在旋转发生的地方顺手重新计算增强字段
（比如 left_rotate 交换 x 和 y 的位置后，要先更新 x 的字段，
再更新 y 的字段——顺序不能反，因为 y 的字段依赖新的 x）。
这也是 CLRS 定理里"O(h) 可维护"这句话的完整含义：
不仅插入/删除路径要维护，旋转这种O(1)的局部操作也要维护，
但因为旋转次数有常数上界，所以不影响总的 O(log n) 复杂度。
```

---

## 四、总结

| 结构 | 增强字段 | 维护规则 | 支持的查询 | 复杂度 |
|------|---------|---------|-----------|--------|
| 顺序统计树 | `size`（子树节点数） | `size(node) = size(left) + size(right) + 1` | OS-SELECT(第 i 小)、OS-RANK(排名) | O(h) |
| 区间树 | `max`（子树中最大 high 端点） | `max(node) = max(node.high, max(left), max(right))` | interval_search（任意一个重叠区间） | O(h) |

> 两者的共同点：增强字段都能仅由"自身数据 + 左右孩子的增强字段"计算得出，
> 这正是 CLRS 通用定理成立的关键条件，也是设计其他"扩张数据结构"时该遵循的原则——
> 先问自己"这个字段能不能只看孩子的同名字段 + 自己的数据就算出来"，
> 能的话，插入/删除的 O(h) 复杂度就不会被破坏。

---

[← 返回索引](index.md)
