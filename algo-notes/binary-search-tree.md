# 二叉搜索树 · Binary Search Tree (BST)

> BST 定义：左子树所有节点 < 根 < 右子树所有节点。**中序遍历 = 升序序列**。

---

## 一、BST 基本操作

### 1.1 查找 · [LC 700](https://leetcode.com/problems/search-in-a-binary-search-tree/)

```python
class TreeNode:
    def __init__(
        self,
        val: int = 0,
        left: "TreeNode | None" = None,
        right: "TreeNode | None" = None,
    ):
        self.val = val
        self.left = left
        self.right = right


def search_bst(root: TreeNode | None, val: int) -> TreeNode | None:
    """利用 BST 性质二分查找。"""
    if not root:
        return None
    if root.val == val:
        return root
    if val < root.val:
        return search_bst(root.left, val)
    return search_bst(root.right, val)


def search_bst_iter(root: TreeNode | None, val: int) -> TreeNode | None:
    """迭代版本。"""
    cur = root
    while cur:
        if cur.val == val:
            return cur
        cur = cur.left if val < cur.val else cur.right
    return None
```

### 1.2 插入 · [LC 701](https://leetcode.com/problems/insert-into-a-binary-search-tree/)

```python
def insert_into_bst(root: TreeNode | None, val: int) -> TreeNode:
    """总是插到叶子节点。"""
    if not root:
        return TreeNode(val)
    if val < root.val:
        root.left = insert_into_bst(root.left, val)
    else:
        root.right = insert_into_bst(root.right, val)
    return root
```

### 1.3 删除 · [LC 450](https://leetcode.com/problems/delete-node-in-a-bst/)

```python
def delete_node(root: TreeNode | None, key: int) -> TreeNode | None:
    """
    三种情况：
    1. 叶子节点：直接删
    2. 有一个子节点：用子节点替换
    3. 有两个子节点：用右子树最小节点（后继）替换
    """
    if not root:
        return None

    if key < root.val:
        root.left = delete_node(root.left, key)
    elif key > root.val:
        root.right = delete_node(root.right, key)
    else:
        # 情况 1 & 2
        if not root.left:
            return root.right
        if not root.right:
            return root.left

        # 情况 3：找后继（右子树最小值）
        successor = get_min(root.right)
        root.val = successor.val
        # 删除后继
        root.right = delete_node(root.right, successor.val)

    return root


def get_min(node: TreeNode) -> TreeNode:
    while node.left:
        node = node.left
    return node
```

---

## 二、BST 常见问题

### 2.1 验证 BST · [LC 98](https://leetcode.com/problems/validate-binary-search-tree/)

```python
def is_valid_bst(root: TreeNode | None) -> bool:
    """
    用上下界约束。每个节点必须在 (lo, hi) 范围内。
    不是只比较左右子节点！要保证整个子树都在范围内。
    """

    def validate(node: TreeNode | None, lo: float, hi: float) -> bool:
        if not node:
            return True
        if not (lo < node.val < hi):
            return False
        return (
            validate(node.left, lo, node.val)
            and validate(node.right, node.val, hi)
        )

    return validate(root, float("-inf"), float("inf"))
```

### 2.2 第 K 小元素 · [LC 230](https://leetcode.com/problems/kth-smallest-element-in-a-bst/)

```python
def kth_smallest(root: TreeNode | None, k: int) -> int:
    """中序遍历到第 k 个节点即为答案。"""
    ans = 0
    rank = 0

    def inorder(node: TreeNode | None) -> None:
        nonlocal ans, rank
        if not node:
            return
        inorder(node.left)
        rank += 1
        if rank == k:
            ans = node.val
            return
        inorder(node.right)

    inorder(root)
    return ans
```

> **优化**：若 BST 频繁增删且频繁查询第 k 小，可在每个节点维护 `size`（子树节点数），O(log n) 查询。

### 2.3 BST 转累加树 · [LC 538](https://leetcode.com/problems/convert-bst-to-greater-tree/)

```python
def convert_bst(root: TreeNode | None) -> TreeNode | None:
    """反序中序遍历（右→根→左），维护累加和。"""
    total = 0

    def traverse(node: TreeNode | None) -> None:
        nonlocal total
        if not node:
            return
        traverse(node.right)
        total += node.val
        node.val = total
        traverse(node.left)

    traverse(root)
    return root
```

---

## 三、不同 BST 的数量 / 生成 · [LC 96](https://leetcode.com/problems/unique-binary-search-trees/) / [LC 95](https://leetcode.com/problems/unique-binary-search-trees-ii/)

### 3.1 不同 BST 的数量（卡特兰数）

```python
def num_trees(n: int) -> int:
    """
    DP: dp[n] = Σ dp[i-1] × dp[n-i]   (i从1到n)
    dp[i-1]: 左子树组合数
    dp[n-i]: 右子树组合数
    这就是卡特兰数。
    """
    dp = [0] * (n + 1)
    dp[0] = dp[1] = 1

    for i in range(2, n + 1):
        for j in range(1, i + 1):
            dp[i] += dp[j - 1] * dp[i - j]

    return dp[n]
```

### 3.2 生成所有 BST · [LC 95](https://leetcode.com/problems/unique-binary-search-trees-ii/)

```python
def generate_trees(n: int) -> list[TreeNode | None]:
    """生成所有可能的 BST。"""

    def build(lo: int, hi: int) -> list[TreeNode | None]:
        if lo > hi:
            return [None]

        result: list[TreeNode | None] = []
        for i in range(lo, hi + 1):
            # 以 i 为根，递归生成左右子树
            left_trees = build(lo, i - 1)
            right_trees = build(i + 1, hi)
            for left in left_trees:
                for right in right_trees:
                    root = TreeNode(i)
                    root.left = left
                    root.right = right
                    result.append(root)
        return result

    return build(1, n) if n > 0 else []
```

### 3.3 有序数组转 BST · [LC 108](https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/)

```python
def sorted_array_to_bst(nums: list[int]) -> TreeNode | None:
    """每次都取中间元素作为根，保证平衡。"""

    def build(lo: int, hi: int) -> TreeNode | None:
        if lo > hi:
            return None
        mid = lo + (hi - lo) // 2
        root = TreeNode(nums[mid])
        root.left = build(lo, mid - 1)
        root.right = build(mid + 1, hi)
        return root

    return build(0, len(nums) - 1)
```

---

## 四、平衡二叉树简介

| 类型 | 特性 | 应用 |
|------|------|------|
| AVL 树 | 严格平衡，每个节点记录平衡因子（-1/0/1）。插入删除需旋转 | 查找密集场景 |
| 红黑树 | 近似平衡，调整开销小（最多3次旋转）。5条性质约束 | 语言标准库（Java TreeMap, C++ map） |
| B 树 | 多路搜索树，适合磁盘 I/O | 数据库索引 |

> **面试重点**：知道概念即可，手写实现很少考。重点是 BST 的中序有序性质 + 验证 + 基本操作。

---

## 五、总结

| 操作/问题 | 方法 | 复杂度 |
|-----------|------|--------|
| 查找 | 二分往下走 | O(h) = O(log n)~O(n) |
| 插入 | 找叶子插入 | O(h) |
| 删除 | 找后继替换 | O(h) |
| 验证 | 递归传上下界 | O(n) |
| 第K小 | 中序遍历 | O(n) / O(h)维护size |
| 不同BST数量 | DP + 卡特兰数 | O(n²) |

---

## 六、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 98](https://leetcode.com/problems/validate-binary-search-tree/) | Validate BST | Medium | 上下界递归 |
| [LC 700](https://leetcode.com/problems/search-in-a-binary-search-tree/) | Search in BST | Easy | 二分查找 |
| [LC 701](https://leetcode.com/problems/insert-into-a-binary-search-tree/) | Insert into BST | Medium | 叶子插入 |
| [LC 450](https://leetcode.com/problems/delete-node-in-a-bst/) | Delete Node in BST | Medium | 三种情况 |
| [LC 230](https://leetcode.com/problems/kth-smallest-element-in-a-bst/) | Kth Smallest Element | Medium | 中序遍历 |
| [LC 538](https://leetcode.com/problems/convert-bst-to-greater-tree/) | Convert BST to Greater Tree | Medium | 反序中序 |
| [LC 96](https://leetcode.com/problems/unique-binary-search-trees/) | Unique BST | Medium | 卡特兰数DP |
| [LC 95](https://leetcode.com/problems/unique-binary-search-trees-ii/) | Unique BST II | Medium | 递归生成 |
| [LC 108](https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/) | Sorted Array to BST | Easy | 二分构造 |
| [LC 109](https://leetcode.com/problems/convert-sorted-list-to-binary-search-tree/) | Sorted List to BST | Medium | 中位二分 |
| [LC 235](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-search-tree/) | LCA of BST | Medium | 利用BST性质 |
| [LC 530](https://leetcode.com/problems/minimum-absolute-difference-in-bst/) | Minimum Absolute Diff in BST | Easy | 中序相邻差 |

---

[← 返回索引](index.md)
