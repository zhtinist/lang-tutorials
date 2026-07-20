# 股票交易系列 · Stock Trading DP

> 6 道股票题用**同一个状态机 DP 模板**统一解决。
> 核心状态：`dp[i][k][0/1]` = 第 i 天，最多交易 k 次，持有/不持有 时的最大利润。

---

## 一、通用框架

### 状态定义

```
dp[i][k][0] = 第 i 天，最多进行 k 次交易，手里 不持有 股票的最大利润
dp[i][k][1] = 第 i 天，最多进行 k 次交易，手里 持有 股票的最大利润

交易：一次买入 + 一次卖出 = 1 次交易（仅在买入时消耗 k）
```

### 状态转移

```python
# 通用模板
dp[i][k][0] = max(
    dp[i-1][k][0],            # 昨天就不持有，今天不动
    dp[i-1][k][1] + prices[i]  # 昨天持有，今天卖出
)

dp[i][k][1] = max(
    dp[i-1][k][1],            # 昨天就持有，今天不动
    dp[i-1][k-1][0] - prices[i]  # 昨天不持有，今天买入（消耗一次交易）
)
```

### Base Case

```
dp[-1][*][0] = 0           # 还没开始，不持有，利润0
dp[-1][*][1] = -inf        # 还没开始，不可能持有
dp[*][0][0] = 0            # 不允许交易，不持有，利润0
dp[*][0][1] = -inf         # 不允许交易，不可能持有
```

---

## 二、[LC 121](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) 交易 1 次

```python
def max_profit_1(prices: list[int]) -> int:
    """
    k=1。dp[i][1][0] = max(dp[i-1][1][0], dp[i-1][1][1]+price)
    dp[i][1][1] = max(dp[i-1][1][1], dp[i-1][0][0]-price) = max(dp[i-1][1][1], -price)
    空间优化后只需两个变量。
    """
    dp0 = 0              # 不持有
    dp1 = float("-inf")  # 持有

    for price in prices:
        dp0 = max(dp0, dp1 + price)
        dp1 = max(dp1, -price)  # k=1，买入前利润为0

    return dp0
```

---

## 三、[LC 122](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/) 交易无限次

```python
def max_profit_2(prices: list[int]) -> int:
    """
    k=inf，k和k-1没有区别。
    dp[i][0] = max(dp[i-1][0], dp[i-1][1]+price)
    dp[i][1] = max(dp[i-1][1], dp[i-1][0]-price)
    """
    dp0 = 0
    dp1 = float("-inf")

    for price in prices:
        prev_dp0 = dp0
        dp0 = max(dp0, dp1 + price)
        dp1 = max(dp1, prev_dp0 - price)  # 依赖旧的dp0

    return dp0
```

---

## 四、[LC 123](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/) 交易 2 次

```python
def max_profit_3(prices: list[int]) -> int:
    """
    k=2。需要维护 k=1 和 k=2 的状态。
    """
    # dp[i][k][0/1]
    dp10 = dp20 = 0
    dp11 = dp21 = float("-inf")

    for price in prices:
        # k=2 要先更新（依赖旧的 k=1 状态）
        dp20 = max(dp20, dp21 + price)
        dp21 = max(dp21, dp10 - price)

        # k=1
        dp10 = max(dp10, dp11 + price)
        dp11 = max(dp11, -price)

    return dp20
```

---

## 五、[LC 188](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/) 交易 K 次（通用）

```python
def max_profit_4(k: int, prices: list[int]) -> int:
    """
    通用 K 次交易。当 k >= n/2 时等价于无限次。
    """
    n = len(prices)
    if n == 0:
        return 0

    # k >= n/2 等价于无限次（每天都可以交易）
    if k >= n // 2:
        dp0, dp1 = 0, float("-inf")
        for price in prices:
            prev = dp0
            dp0 = max(dp0, dp1 + price)
            dp1 = max(dp1, prev - price)
        return dp0

    # dp[i][k][0/1] → 一维优化
    dp_ik0 = [0] * (k + 1)
    dp_ik1 = [float("-inf")] * (k + 1)

    for price in prices:
        for j in range(k, 0, -1):  # 反向遍历
            dp_ik0[j] = max(dp_ik0[j], dp_ik1[j] + price)
            dp_ik1[j] = max(dp_ik1[j], dp_ik0[j - 1] - price)

    return dp_ik0[k]
```

---

## 六、[LC 309](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/) 含冷冻期

```python
def max_profit_freeze(prices: list[int]) -> int:
    """
    卖出后有一天冷冻期不能买入。
    卖出时状态来自 dp[i-2] 的不持有。
    """
    n = len(prices)
    if n < 2:
        return 0

    dp0 = 0                 # 不持有
    dp1 = float("-inf")     # 持有
    dp0_pre = 0             # dp[i-2][0]

    for price in prices:
        prev_dp0 = dp0
        dp0 = max(dp0, dp1 + price)
        dp1 = max(dp1, dp0_pre - price)  # 买入时依赖 i-2 天
        dp0_pre = prev_dp0

    return dp0
```

---

## 七、[LC 714](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/) 含手续费

```python
def max_profit_fee(prices: list[int], fee: int) -> int:
    """每笔交易需要 fee 手续费。卖出时扣除。"""
    dp0 = 0
    dp1 = float("-inf")

    for price in prices:
        prev = dp0
        dp0 = max(dp0, dp1 + price)
        dp1 = max(dp1, prev - price - fee)  # 买入时考虑手续费

    return dp0
```

---

## 八、6 题对比总结

| 题目 | k 限制 | 额外约束 | 核心差异 |
|------|--------|---------|---------|
| [LC 121](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | k=1 | 无 | dp1 = max(dp1, -price) |
| [LC 122](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/) | k=inf | 无 | dp1 = max(dp1, dp0-price) |
| [LC 123](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/) | k=2 | 无 | 两个 k 状态 |
| [LC 188](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/) | 任意 k | 无 | k >= n/2 退化为 inf |
| [LC 309](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/) | k=inf | 冷冻期 | dp1 依赖 dp[i-2][0] |
| [LC 714](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/) | k=inf | 手续费 | 买入时多减 fee |

### 统一记忆法

```
dp0 = max(dp0, dp1 + price)    ← 卖出（不变）
dp1 = max(dp1, ??? - price)    ← 买入（??? 不同）

k=1:    ?? = 0
k=inf:  ?? = dp0 (旧的dp0, 先保存)
冷冻期: ?? = dp0_pre (i-2天的dp0)
手续费: ??? 处用 -price - fee
```

---

## 九、习题推荐

| 题号 | 题目 | 难度 | 类型 |
|------|------|------|------|
| [LC 121](https://leetcode.com/problems/best-time-to-buy-and-sell-stock/) | Best Time to Buy and Sell Stock | Easy | k=1 |
| [LC 122](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-ii/) | Best Time to Buy and Sell Stock II | Medium | k=inf |
| [LC 123](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iii/) | Best Time to Buy and Sell Stock III | Hard | k=2 |
| [LC 188](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-iv/) | Best Time to Buy and Sell Stock IV | Hard | 任意k |
| [LC 309](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/) | Best Time with Cooldown | Medium | 冷冻期 |
| [LC 714](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-transaction-fee/) | Best Time with Transaction Fee | Medium | 手续费 |

---

[← 返回索引](index.md)
