# DP 基础 · Dynamic Programming Basics

> DP 入门从最简单的线性 DP 开始。掌握"定义状态 → 转移方程 → base case → 遍历方向"四步法。

---

## 一、斐波那契：从递归到 DP · [LC 509](https://leetcode.com/problems/fibonacci-number/)

```python
# 暴力递归 O(2^n)
def fib_brute(n: int) -> int:
    if n <= 1:
        return n
    return fib_brute(n - 1) + fib_brute(n - 2)


# 记忆化递归 O(n)
from functools import lru_cache


@lru_cache(maxsize=None)
def fib_memo(n: int) -> int:
    if n <= 1:
        return n
    return fib_memo(n - 1) + fib_memo(n - 2)


# 递推 O(n), O(1) 空间
def fib_dp(n: int) -> int:
    if n <= 1:
        return n
    prev, cur = 0, 1
    for _ in range(2, n + 1):
        prev, cur = cur, prev + cur
    return cur
```

---

## 二、爬楼梯 · [LC 70](https://leetcode.com/problems/climbing-stairs/) / [LC 746](https://leetcode.com/problems/min-cost-climbing-stairs/)

### [LC 70](https://leetcode.com/problems/climbing-stairs/) 爬楼梯

```python
def climb_stairs(n: int) -> int:
    """
    dp[i] = 爬到第 i 阶的方法数
    dp[i] = dp[i-1] + dp[i-2] （要么走1步，要么走2步）
    """
    if n <= 2:
        return n
    prev, cur = 1, 2
    for _ in range(3, n + 1):
        prev, cur = cur, prev + cur
    return cur
```

### [LC 746](https://leetcode.com/problems/min-cost-climbing-stairs/) 使用最小花费爬楼梯

```python
def min_cost_climbing_stairs(cost: list[int]) -> int:
    """
    dp[i] = 到达第 i 阶的最小花费
    可以从 i-1 或 i-2 到达 i
    dp[i] = min(dp[i-1] + cost[i-1], dp[i-2] + cost[i-2])
    """
    n = len(cost)
    prev, cur = 0, 0  # dp[0]=0, dp[1]=0（起点不花钱）
    for i in range(2, n + 1):
        prev, cur = cur, min(cur + cost[i - 1], prev + cost[i - 2])
    return cur
```

---

## 三、网格路径问题

### [LC 62](https://leetcode.com/problems/unique-paths/) 不同路径

```python
def unique_paths(m: int, n: int) -> int:
    """
    dp[i][j] = 到达 (i,j) 的路径数
    dp[i][j] = dp[i-1][j] + dp[i][j-1]
    空间优化：只用一行
    """
    dp = [1] * n
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]
    return dp[-1]
```

### [LC 63](https://leetcode.com/problems/unique-paths-ii/) 不同路径 II（有障碍物）

```python
def unique_paths_with_obstacles(grid: list[list[int]]) -> int:
    m, n = len(grid), len(grid[0])
    dp = [0] * n
    dp[0] = 1 if grid[0][0] == 0 else 0

    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                dp[j] = 0
            elif j > 0:
                dp[j] += dp[j - 1]
    return dp[-1]
```

### [LC 64](https://leetcode.com/problems/minimum-path-sum/) 最小路径和

```python
def min_path_sum(grid: list[list[int]]) -> int:
    """
    dp[i][j] = 到达 (i,j) 的最小路径和
    dp[i][j] = grid[i][j] + min(dp[i-1][j], dp[i][j-1])
    """
    m, n = len(grid), len(grid[0])
    dp = [0] * n
    dp[0] = grid[0][0]
    for j in range(1, n):
        dp[j] = dp[j - 1] + grid[0][j]

    for i in range(1, m):
        dp[0] += grid[i][0]
        for j in range(1, n):
            dp[j] = grid[i][j] + min(dp[j], dp[j - 1])

    return dp[-1]
```

### [LC 120](https://leetcode.com/problems/triangle/) 三角形最小路径和

```python
def minimum_total(triangle: list[list[int]]) -> int:
    """自底向上 DP，最后 triangle[0][0] 就是答案。"""
    for i in range(len(triangle) - 2, -1, -1):
        for j in range(len(triangle[i])):
            triangle[i][j] += min(triangle[i + 1][j], triangle[i + 1][j + 1])
    return triangle[0][0]
```

---

## 四、整数拆分 · [LC 343](https://leetcode.com/problems/integer-break/)

```python
def integer_break(n: int) -> int:
    """
    dp[i] = 拆分正整数 i 得到的最大乘积
    dp[i] = max(dp[i], j * (i-j), j * dp[i-j])
    """
    dp = [0] * (n + 1)
    dp[1] = 1  # 实际上 dp[1] 用不到

    for i in range(2, n + 1):
        for j in range(1, i):
            dp[i] = max(dp[i], j * (i - j), j * dp[i - j])

    return dp[n]
```

---

## 五、完全平方数 · [LC 279](https://leetcode.com/problems/perfect-squares/)

```python
import math


def num_squares(n: int) -> int:
    """
    dp[i] = 和为 i 的完全平方数的最少数量
    dp[i] = min(dp[i - j²] + 1)  for all j² ≤ i
    本质是硬币找零问题（硬币是平方数）。
    """
    dp = [float("inf")] * (n + 1)
    dp[0] = 0

    squares = [i * i for i in range(1, int(math.sqrt(n)) + 1)]

    for i in range(1, n + 1):
        for sq in squares:
            if i < sq:
                break
            dp[i] = min(dp[i], dp[i - sq] + 1)

    return int(dp[n])


# BFS 解法（求最短路径的思路）
from collections import deque


def num_squares_bfs(n: int) -> int:
    squares = [i * i for i in range(1, int(math.sqrt(n)) + 1)]
    queue: deque[int] = deque([n])
    visited = {n}
    level = 0

    while queue:
        level += 1
        for _ in range(len(queue)):
            remain = queue.popleft()
            for sq in squares:
                nxt = remain - sq
                if nxt == 0:
                    return level
                if nxt > 0 and nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

    return level
```

---

## 六、单词拆分 · [LC 139](https://leetcode.com/problems/word-break/)

```python
def word_break(s: str, word_dict: list[str]) -> bool:
    """
    dp[i] = s[0:i] 是否可以由字典中的单词组成
    dp[i] = dp[j] and s[j:i] in wordSet
    """
    words = set(word_dict)
    n = len(s)
    dp = [False] * (n + 1)
    dp[0] = True

    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break

    return dp[n]
```

---

## 七、DP 四步法总结

```
解题步骤:
1. 定义 dp 数组含义
   dp[i] 代表什么？
   dp[i][j] 代表什么？

2. 定义 base case
   最小子问题，直接可以算出来。

3. 找到状态转移方程
   当前状态依赖哪些之前的状态？
   需要枚举哪些选择？

4. 确定遍历方向
   - 正向：i 依赖 i-1, i-2, ...
   - 反向：i 依赖 i+1, i+2, ...（如编辑距离）
   - 斜向：区间 DP
```

---

## 八、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 509](https://leetcode.com/problems/fibonacci-number/) | Fibonacci Number | Easy | 入门 |
| [LC 70](https://leetcode.com/problems/climbing-stairs/) | Climbing Stairs | Easy | 线性DP |
| [LC 746](https://leetcode.com/problems/min-cost-climbing-stairs/) | Min Cost Climbing Stairs | Easy | 线性DP变体 |
| [LC 62](https://leetcode.com/problems/unique-paths/) | Unique Paths | Medium | 网格路径 |
| [LC 63](https://leetcode.com/problems/unique-paths-ii/) | Unique Paths II | Medium | 有障碍物 |
| [LC 64](https://leetcode.com/problems/minimum-path-sum/) | Minimum Path Sum | Medium | 最小路径和 |
| [LC 120](https://leetcode.com/problems/triangle/) | Triangle | Medium | 自底向上 |
| [LC 343](https://leetcode.com/problems/integer-break/) | Integer Break | Medium | 枚举拆分 |
| [LC 279](https://leetcode.com/problems/perfect-squares/) | Perfect Squares | Medium | 完全背包型DP |
| [LC 139](https://leetcode.com/problems/word-break/) | Word Break | Medium | 字符串DP |
| [LC 221](https://leetcode.com/problems/maximal-square/) | Maximal Square | Medium | 正方形DP |
| [LC 91](https://leetcode.com/problems/decode-ways/) | Decode Ways | Medium | 解码方式DP |

---

[← 返回索引](index.md)
