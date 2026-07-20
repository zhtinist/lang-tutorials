# 打家劫舍系列 · House Robber DP

> 相邻房屋不能同时偷。三种变体：**线性、环形、树形**。核心状态：
> `dp[i]` = 前 i 个房屋能偷到的最大金额。

---

## 一、线性排列 · [LC 198](https://leetcode.com/problems/house-robber/)

```python
def rob_linear(nums: list[int]) -> int:
    """
    dp[i] = max(dp[i-1], dp[i-2] + nums[i])
    偷或不偷第 i 家。
    """
    prev, cur = 0, 0  # dp[i-2], dp[i-1]
    for money in nums:
        prev, cur = cur, max(cur, prev + money)
    return cur
```

---

## 二、环形排列 · [LC 213](https://leetcode.com/problems/house-robber-ii/)

```python
def rob_circular(nums: list[int]) -> int:
    """
    首尾相连 → 拆成两个子问题：
    1. 不偷第一家：rob(nums[1:])
    2. 不偷最后一家：rob(nums[:-1])
    取较大值。
    """
    n = len(nums)
    if n == 1:
        return nums[0]
    if n == 2:
        return max(nums[0], nums[1])

    def rob_range(start: int, end: int) -> int:
        prev, cur = 0, 0
        for i in range(start, end):
            prev, cur = cur, max(cur, prev + nums[i])
        return cur

    return max(rob_range(0, n - 1), rob_range(1, n))
```

---

## 三、二叉树排列 · [LC 337](https://leetcode.com/problems/house-robber-iii/)

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


def rob_tree(root: TreeNode | None) -> int:
    """
    树形 DP，后序遍历。
    每个节点返回 (偷当前节点的最大值, 不偷当前节点的最大值)。
    """

    def dfs(node: TreeNode | None) -> tuple[int, int]:
        """返回 (rob, not_rob)。"""
        if not node:
            return (0, 0)

        left_rob, left_not = dfs(node.left)
        right_rob, right_not = dfs(node.right)

        # 偷当前节点：左右子节点都不能偷
        rob_cur = node.val + left_not + right_not

        # 不偷当前节点：左右子节点可选偷或不偷
        not_rob_cur = max(left_rob, left_not) + max(right_rob, right_not)

        return (rob_cur, not_rob_cur)

    return max(dfs(root))
```

---

## 四、粉刷房子 · [LC 256](https://leetcode.com/problems/paint-house/) / [LC 265](https://leetcode.com/problems/paint-house-ii/)

### [LC 256](https://leetcode.com/problems/paint-house/) 粉刷房子（3种颜色）

```python
def min_cost_3_colors(costs: list[list[int]]) -> int:
    """
    dp[i][c] = 刷到第 i 个房子，颜色为 c 的最小花费。
    dp[i][c] = costs[i][c] + min(dp[i-1][其他颜色])
    空间优化：只用上一行的三个值。
    """
    if not costs:
        return 0
    red, blue, green = costs[0]

    for r, b, g in costs[1:]:
        new_red = r + min(blue, green)
        new_blue = b + min(red, green)
        new_green = g + min(red, blue)
        red, blue, green = new_red, new_blue, new_green

    return min(red, blue, green)
```

### [LC 265](https://leetcode.com/problems/paint-house-ii/) 粉刷房子 II（K 种颜色）

```python
def min_cost_k_colors(costs: list[list[int]]) -> int:
    """
    K 种颜色。需要高效找到上一行除了某列外的全局最小值。
    技巧：记录最小值和次小值及其颜色索引。
    """
    if not costs:
        return 0

    n, k = len(costs), len(costs[0])
    prev = costs[0][:]  # 上一行的 dp 值

    for i in range(1, n):
        # 找到上一行的最小值和次小值
        min1 = min2 = float("inf")
        idx1 = -1
        for c, val in enumerate(prev):
            if val < min1:
                min2, min1 = min1, val
                idx1 = c
            elif val < min2:
                min2 = val

        cur = [0] * k
        for c in range(k):
            # 最小值的颜色 != c 时可以用最小值，否则用次小值
            cur[c] = costs[i][c] + (min1 if c != idx1 else min2)
        prev = cur

    return min(prev)
```

---

## 五、栅栏涂色 · [LC 276](https://leetcode.com/problems/paint-fence/)

```python
def num_ways(n: int, k: int) -> int:
    """
    n 根栅栏，k 种颜色，不能有连续 3 根同色。
    same: 当前与前一根同色的方案数
    diff: 当前与前一根不同色的方案数
    """
    if n == 0:
        return 0
    if n == 1:
        return k

    same = k          # 第2根与第1根同色的方案数
    diff = k * (k - 1)  # 第2根与第1根不同色的方案数

    for _ in range(3, n + 1):
        same, diff = diff, (same + diff) * (k - 1)
        # same: 之前 diff，这次和前一根同色
        # diff: 之前无论是same还是diff，这次选不同色（k-1 种选择）

    return same + diff
```

---

## 六、总结

| 变体 | 关键技巧 |
|------|---------|
| 线性 | `dp[i] = max(dp[i-1], dp[i-2] + nums[i])` |
| 环形 | 拆成两个线性子问题（去头/去尾） |
| 树形 | 后序遍历，返回 (偷, 不偷) 二元组 |
| 粉刷房子 | 状态是多颜色而非0/1，记录最小次小 |
| 栅栏涂色 | 同色/不同色 两类状态 |

---

## 七、习题推荐

| 题号 | 题目 | 难度 | 变体 |
|------|------|------|------|
| [LC 198](https://leetcode.com/problems/house-robber/) | House Robber | Medium | 线性 |
| [LC 213](https://leetcode.com/problems/house-robber-ii/) | House Robber II | Medium | 环形 |
| [LC 337](https://leetcode.com/problems/house-robber-iii/) | House Robber III | Medium | 树形 |
| [LC 256](https://leetcode.com/problems/paint-house/) | Paint House | Medium🔒 | 3色 |
| [LC 265](https://leetcode.com/problems/paint-house-ii/) | Paint House II | Hard🔒 | K色 |
| [LC 276](https://leetcode.com/problems/paint-fence/) | Paint Fence | Medium🔒 | 栅栏 |
| [LC 740](https://leetcode.com/problems/delete-and-earn/) | Delete and Earn | Medium | 打家劫舍变体 |

---

[← 返回索引](index.md)
