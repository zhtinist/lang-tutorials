# 背包问题 · Knapsack Problems

> 背包问题是 DP 的经典应用。核心：**物品 × 容量** 的二维状态空间。
> 关键区分：**0-1背包**(反向遍历) vs **完全背包**(正向遍历)。

---

## 一、0-1 背包

> 每个物品**只能选一次**，求最大价值。

### 标准定义

```
输入: weights[], values[], capacity
输出: 在总重量 ≤ capacity 的条件下，可选的最大价值
```

### 二维 DP

```python
def knapsack_2d(
    weights: list[int], values: list[int], capacity: int
) -> int:
    """
    dp[i][w] = 前 i 个物品，背包容量 w，最大价值
    选择：选或不选第 i 个物品
    """
    n = len(weights)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        wt, val = weights[i - 1], values[i - 1]
        for w in range(capacity + 1):
            if w >= wt:
                dp[i][w] = max(dp[i - 1][w], dp[i - 1][w - wt] + val)
            else:
                dp[i][w] = dp[i - 1][w]

    return dp[n][capacity]
```

### 空间优化（一维 DP）

```python
def knapsack_1d(
    weights: list[int], values: list[int], capacity: int
) -> int:
    """
    空间优化：dp[w] 只依赖 dp[w] 和 dp[w-wt]
    ⚠️ 必须反向遍历！原因：
    dp[w] 依赖的是上一行的 dp[w-wt]，
    正向遍历会用到本行已更新的值（变成完全背包）。
    """
    dp = [0] * (capacity + 1)

    for wt, val in zip(weights, values):
        for w in range(capacity, wt - 1, -1):  # 反向！
            dp[w] = max(dp[w], dp[w - wt] + val)

    return dp[capacity]
```

---

## 二、0-1 背包应用题

### [LC 416](https://leetcode.com/problems/partition-equal-subset-sum/) 分割等和子集

```python
def can_partition(nums: list[int]) -> bool:
    """能否分成两个和相等的子集 → 0-1背包"""
    total = sum(nums)
    if total % 2 != 0:
        return False

    target = total // 2
    dp = [False] * (target + 1)
    dp[0] = True

    for num in nums:
        for w in range(target, num - 1, -1):
            dp[w] = dp[w] or dp[w - num]

    return dp[target]
```

### [LC 494](https://leetcode.com/problems/target-sum/) 目标和

```python
def find_target_sum_ways(nums: list[int], target: int) -> int:
    """
    每个数前加 + 或 -，使得总和等于 target。
    转化为 0-1 背包：
    sum(P) - sum(N) = target
    sum(P) + sum(N) = total
    → sum(P) = (target + total) / 2
    """
    total = sum(nums)
    if abs(target) > total or (target + total) % 2 != 0:
        return 0

    bag = (target + total) // 2
    dp = [0] * (bag + 1)
    dp[0] = 1

    for num in nums:
        for w in range(bag, num - 1, -1):
            dp[w] += dp[w - num]

    return dp[bag]
```

### [LC 1049](https://leetcode.com/problems/last-stone-weight-ii/) 最后一块石头的重量 II

```python
def last_stone_weight_ii(stones: list[int]) -> int:
    """
    粉碎石头的最小剩余重量。
    把石头分成两堆，使差值最小 → 0-1 背包。
    """
    total = sum(stones)
    half = total // 2

    dp = [0] * (half + 1)
    for s in stones:
        for w in range(half, s - 1, -1):
            dp[w] = max(dp[w], dp[w - s] + s)

    return total - 2 * dp[half]
```

---

## 三、完全背包

> 每个物品可以**选无限次**。与 0-1 背包的唯一区别是**遍历方向**！

```python
def unbounded_knapsack(
    weights: list[int], values: list[int], capacity: int
) -> int:
    """完全背包：正向遍历。"""
    dp = [0] * (capacity + 1)

    for wt, val in zip(weights, values):
        for w in range(wt, capacity + 1):  # 正向！
            dp[w] = max(dp[w], dp[w - wt] + val)

    return dp[capacity]
```

### 遍历顺序规律

```
0-1 背包：  for 物品: for w in reverse(0..capacity):   ← 反向
完全背包：  for 物品: for w in range(0..capacity):      ← 正向

组合数问题（只关心取哪些物品）：
  for 物品: for w in range(wt, capacity+1):           ← 先物品后容量
排列数问题（顺序也重要）：
  for w in range(capacity+1): for 物品:                ← 先容量后物品
```

### [LC 322](https://leetcode.com/problems/coin-change/) 零钱兑换（完全背包求最小值）

```python
def coin_change(coins: list[int], amount: int) -> int:
    """最少硬币数。完全背包求最小值。"""
    dp = [float("inf")] * (amount + 1)
    dp[0] = 0

    for coin in coins:
        for a in range(coin, amount + 1):
            dp[a] = min(dp[a], dp[a - coin] + 1)

    return int(dp[amount]) if dp[amount] != float("inf") else -1
```

### [LC 518](https://leetcode.com/problems/coin-change-ii/) 零钱兑换 II（完全背包求方案数）

```python
def change(amount: int, coins: list[int]) -> int:
    """凑出 amount 的组合数（完全背包）。"""
    dp = [0] * (amount + 1)
    dp[0] = 1

    for coin in coins:
        for a in range(coin, amount + 1):
            dp[a] += dp[a - coin]

    return dp[amount]
```

### [LC 377](https://leetcode.com/problems/combination-sum-iv/) 组合总和 IV（排列数）

```python
def combination_sum4(nums: list[int], target: int) -> int:
    """
    顺序不同的序列视为不同的组合 → 排列数问题。
    先遍历容量，再遍历物品！
    """
    dp = [0] * (target + 1)
    dp[0] = 1

    for t in range(1, target + 1):
        for num in nums:
            if t >= num:
                dp[t] += dp[t - num]

    return dp[target]
```

---

## 四、多重背包

> 每个物品有**数量限制**。优化：二进制拆分。

```python
def bounded_knapsack(
    weights: list[int], values: list[int], counts: list[int], capacity: int
) -> int:
    """多重背包：二进制拆分后转为 0-1 背包。"""
    # 二进制拆分
    items: list[tuple[int, int]] = []  # (weight, value)
    for wt, val, cnt in zip(weights, values, counts):
        k = 1
        while cnt > 0:
            take = min(k, cnt)
            items.append((wt * take, val * take))
            cnt -= take
            k *= 2

    # 0-1 背包
    dp = [0] * (capacity + 1)
    for wt, val in items:
        for w in range(capacity, wt - 1, -1):
            dp[w] = max(dp[w], dp[w - wt] + val)

    return dp[capacity]
```

---

## 五、二维费用背包 · [LC 474](https://leetcode.com/problems/ones-and-zeroes/) 一和零

```python
def find_max_form(strs: list[str], m: int, n: int) -> int:
    """
    每个字符串需要消耗一定数量的 0 和 1。
    dp[j][k] = 使用 j 个 0 和 k 个 1 时，最多的字符串数量。
    二维费用 0-1 背包。
    """
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for s in strs:
        zeros = s.count("0")
        ones = len(s) - zeros
        # 反向遍历（0-1 背包）
        for j in range(m, zeros - 1, -1):
            for k in range(n, ones - 1, -1):
                dp[j][k] = max(dp[j][k], dp[j - zeros][k - ones] + 1)

    return dp[m][n]
```

---

## 六、总结表格

| 背包类型 | 遍历顺序 | 核心特征 |
|----------|---------|---------|
| 0-1 背包 | 反向 for w in reversed(range) | 每个物品最多选1次 |
| 完全背包 | 正向 for w in range | 每个物品可选无限次 |
| 多重背包 | 二进制拆分 → 0-1 背包 | 每个物品有限制次数 |
| 组合数 | 先物品后容量 | 顺序不重要 |
| 排列数 | 先容量后物品 | 顺序重要 |

---

## 七、习题推荐

| 题号 | 题目 | 难度 | 类型 |
|------|------|------|------|
| [LC 416](https://leetcode.com/problems/partition-equal-subset-sum/) | Partition Equal Subset Sum | Medium | 0-1背包 |
| [LC 494](https://leetcode.com/problems/target-sum/) | Target Sum | Medium | 0-1背包 |
| [LC 1049](https://leetcode.com/problems/last-stone-weight-ii/) | Last Stone Weight II | Medium | 0-1背包 |
| [LC 474](https://leetcode.com/problems/ones-and-zeroes/) | Ones and Zeroes | Medium | 二维费用0-1 |
| [LC 322](https://leetcode.com/problems/coin-change/) | Coin Change | Medium | 完全背包(min) |
| [LC 518](https://leetcode.com/problems/coin-change-ii/) | Coin Change II | Medium | 完全背包(count) |
| [LC 377](https://leetcode.com/problems/combination-sum-iv/) | Combination Sum IV | Medium | 排列数背包 |
| [LC 279](https://leetcode.com/problems/perfect-squares/) | Perfect Squares | Medium | 完全背包 |
| [LC 139](https://leetcode.com/problems/word-break/) | Word Break | Medium | 字符串背包 |
| [LC 1155](https://leetcode.com/problems/number-of-dice-rolls-with-target-sum/) | Number of Dice Rolls | Medium | 分组背包 |

---

[← 返回索引](index.md)
