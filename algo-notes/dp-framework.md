# 动态规划框架 · Dynamic Programming Framework

> DP 的本质是**带记忆的穷举**。三要素：**重叠子问题、最优子结构、状态转移方程**。
> 核心：**base case → 状态 → 选择 → dp 数组/函数定义**。

---

## 一、DP 解题框架

```
1. 定义 dp[i] / dp[i][j] / ... 的含义
2. 写出 base case（最简单的情况）
3. 找出状态转移方程（当前状态如何从之前的状态推导）
4. 确定遍历方向（正向/反向/斜向）
5. （可选）空间优化（滚动数组）
```

### 自顶向下 vs 自底向上

| 方式 | 实现 | 优点 | 缺点 |
|------|------|------|------|
| 记忆化递归（自顶向下） | 递归 + memo | 思路直观，按需计算 | 递归栈开销 |
| 递推（自底向上） | 循环 + dp数组 | 无递归栈，可空间优化 | 需确定遍历方向 |

---

## 二、例题：斐波那契数列 · [LC 509](https://leetcode.com/problems/fibonacci-number/)

### 2.1 暴力递归（O(2^n)）

```python
def fib_brute(n: int) -> int:
    """暴力递归——有大量重复计算。"""
    if n <= 1:
        return n
    return fib_brute(n - 1) + fib_brute(n - 2)
```

### 2.2 记忆化递归（自顶向下，O(n)）

```python
def fib_memo(n: int) -> int:
    """记忆化递归——用 memo 消除重复子问题。"""
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def dp(i: int) -> int:
        if i <= 1:
            return i
        return dp(i - 1) + dp(i - 2)

    return dp(n)


# 或手动写 memo
def fib_memo_manual(n: int) -> int:
    memo: dict[int, int] = {0: 0, 1: 1}

    def dp(i: int) -> int:
        if i not in memo:
            memo[i] = dp(i - 1) + dp(i - 2)
        return memo[i]

    return dp(n)
```

### 2.3 递推（自底向上，O(n)，空间 O(1)）

```python
def fib_dp(n: int) -> int:
    """递推——从 base case 向上构建。"""
    if n <= 1:
        return n
    prev, cur = 0, 1
    for _ in range(2, n + 1):
        prev, cur = cur, prev + cur
    return cur
```

---

## 三、零钱兑换 · [LC 322](https://leetcode.com/problems/coin-change/)

> **最优子结构**：凑出 amount 的最少硬币数 = 1 + min(凑出 amount-coin 的最少硬币数)

```python
def coin_change(coins: list[int], amount: int) -> int:
    """返回凑出 amount 所需的最少硬币数，不可能则返回 -1。"""

    # dp[i] = 凑出金额 i 所需的最少硬币数
    dp = [amount + 1] * (amount + 1)  # amount+1 相当于正无穷
    dp[0] = 0  # base case: 凑0元不需要硬币

    for i in range(1, amount + 1):
        for coin in coins:
            if i >= coin:
                dp[i] = min(dp[i], dp[i - coin] + 1)

    return dp[amount] if dp[amount] != amount + 1 else -1
```

### 记忆化递归版本

```python
def coin_change_memo(coins: list[int], amount: int) -> int:
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def dp(remain: int) -> int:
        if remain == 0:
            return 0
        if remain < 0:
            return -1

        best = float("inf")
        for coin in coins:
            sub = dp(remain - coin)
            if sub != -1:
                best = min(best, sub + 1)

        return int(best) if best != float("inf") else -1

    return dp(amount)
```

---

## 四、最优子结构

> **最优子结构**：一个问题的最优解包含其子问题的最优解。

### 判断方法

```
设求最优解的问题是 A，子问题是 B。

当 A 的最优解可以由 B 的最优解直接构造出来时 → 有最优子结构。
否则 → 没有最优子结构，不能用 DP，可能需要回溯/贪心。
```

### 反例：最长简单路径

图中找最长简单路径（不重复经过节点）没有最优子结构。因为 A 的最优解可能在 B 中用了一个路径，而 A 需要另一个路径。

### 正例：最短路径

有最优子结构。从 A 到 C 的最短路径一定经过 A 到 B 的最短路径。

---

## 五、DP 数组的遍历方向

```
关键原则：计算 dp[i][j] 时，其依赖的状态必须已经计算过。

1. 从左到右，从上到下（最常见的正向遍历）
   for i in range(n):
       for j in range(n):
           dp[i][j] = f(dp[i-1][j], dp[i][j-1])

2. 从右到左（0-1背包的空间优化！）
   for i in range(n-1, -1, -1):
       dp[i] = f(dp[i], dp[i+1])

3. 斜向遍历（区间 DP，最长回文子串）
   for length in range(2, n+1):
       for i in range(n - length + 1):
           j = i + length - 1
           dp[i][j] = f(dp[i+1][j-1], ...)

4. 从后往前（编辑距离等）
   for i in range(m-1, -1, -1):
       for j in range(n-1, -1, -1):
           dp[i][j] = f(dp[i+1][j], dp[i][j+1])
```

---

## 六、状态压缩（滚动数组）

> 当 `dp[i][...]` 只依赖 `dp[i-1][...]` 时，可以只用一维或二维数组。

### 0-1 背包的空间优化

```python
# 二维 DP（原始版本）
def knapsack_2d(weights: list[int], values: list[int], capacity: int) -> int:
    n = len(weights)
    # dp[i][w] = 前 i 个物品，容量 w，最大价值
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(capacity + 1):
            if w >= weights[i - 1]:
                dp[i][w] = max(
                    dp[i - 1][w],                          # 不选
                    dp[i - 1][w - weights[i - 1]] + values[i - 1]  # 选
                )
            else:
                dp[i][w] = dp[i - 1][w]

    return dp[n][capacity]


# 一维 DP（空间优化！要注意遍历方向）
def knapsack_1d(weights: list[int], values: list[int], capacity: int) -> int:
    n = len(weights)
    dp = [0] * (capacity + 1)

    for i in range(n):
        # ⚠️ 必须反向遍历！因为 dp[w] 依赖上一行的 dp[w - wt]
        for w in range(capacity, weights[i] - 1, -1):
            dp[w] = max(dp[w], dp[w - weights[i]] + values[i])

    return dp[capacity]
```

> **0-1 背包反向遍历，完全背包正向遍历。** 原因：反向保证每个物品只取一次，正向允许取多次。

---

## 七、经典 DP 问题一览

| 问题类型 | 状态定义 | 例题 |
|----------|---------|------|
| 爬楼梯/斐波那契 | `dp[i]` 到第 i 级 | [LC 70](https://leetcode.com/problems/climbing-stairs/), 509 |
| 路径问题 | `dp[i][j]` 到 (i,j) | [LC 62](https://leetcode.com/problems/unique-paths/), 63, 64 |
| 背包 0-1 | `dp[w]` 容量 w | [LC 416](https://leetcode.com/problems/partition-equal-subset-sum/), 494 |
| 背包完全 | `dp[w]` 容量 w | [LC 322](https://leetcode.com/problems/coin-change/), 518 |
| LIS | `dp[i]` 以 i 结尾 | [LC 300](https://leetcode.com/problems/longest-increasing-subsequence/) |
| LCS | `dp[i][j]` s1前i, s2前j | [LC 1143](https://leetcode.com/problems/longest-common-subsequence/) |
| 编辑距离 | `dp[i][j]` 转换成本 | [LC 72](https://leetcode.com/problems/edit-distance/) |
| 股票交易 | `dp[i][k][0/1]` 天数/次数/持有 | [LC 121](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/)-188 |
| 打家劫舍 | `dp[i]` 到第 i 家 | [LC 198](https://leetcode.com/problems/house-robber/), 213, 337 |
| 区间 DP | `dp[i][j]` 区间 [i,j] | [LC 312](https://leetcode.com/problems/burst-balloons/), 516 |
| 博弈 DP | dp[先手/后手] | [LC 486](https://leetcode.com/problems/predict-the-winner/), 877 |

---

## 八、DP 与回溯的关系

> DP 解的问题都可以用回溯暴力解。回溯多了记忆化就是 DP（自顶向下），递推是反向的 DFS。

```python
# 回溯（暴力）
def coin_change_backtrack(coins, amount):
    ans = [float("inf")]

    def dfs(remain, count):
        if remain == 0:
            ans[0] = min(ans[0], count)
            return
        for coin in coins:
            if coin <= remain:
                dfs(remain - coin, count + 1)

    dfs(amount, 0)
    return ans[0] if ans[0] != float("inf") else -1

# DP（记忆化 = 回溯+memo）
# DP（递推 = 从底部往上算）
```

---

## 九、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 509](https://leetcode.com/problems/fibonacci-number/) | Fibonacci Number | Easy | 基础框架 |
| [LC 70](https://leetcode.com/problems/climbing-stairs/) | Climbing Stairs | Easy | 基础线性DP |
| [LC 322](https://leetcode.com/problems/coin-change/) | Coin Change | Medium | 最优子结构 |
| [LC 300](https://leetcode.com/problems/longest-increasing-subsequence/) | Longest Increasing Subsequence | Medium | 子序列DP |
| [LC 62](https://leetcode.com/problems/unique-paths/) | Unique Paths | Medium | 网格路径 |
| [LC 64](https://leetcode.com/problems/minimum-path-sum/) | Minimum Path Sum | Medium | 网格路径 |
| [LC 279](https://leetcode.com/problems/perfect-squares/) | Perfect Squares | Medium | DP+BFS双解 |
| [LC 139](https://leetcode.com/problems/word-break/) | Word Break | Medium | 字符串DP |
| [LC 120](https://leetcode.com/problems/triangle/) | Triangle | Medium | 三角路径 |
| [LC 416](https://leetcode.com/problems/partition-equal-subset-sum/) | Partition Equal Subset Sum | Medium | 0-1背包 |
| [LC 518](https://leetcode.com/problems/coin-change-ii/) | Coin Change II | Medium | 完全背包 |

---

[← 返回索引](index.md)
