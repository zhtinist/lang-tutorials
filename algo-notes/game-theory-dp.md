# 博弈 DP · Game Theory DP

> 两人轮流取石子/选数字，都想最优 → **Minimax** 算法。
> 常见状态定义：`dp[i][j]` 表示先手面对区间 `[i, j]` 的最大净胜分。

---

## 一、核心框架：Minimax

```
你的收益 = 你选的值 + 子问题中你作为后手的收益
你的收益 = max(选项1, 选项2) → 取最大是因为你想赢

minimax本质：
  先手选择 → 最大化自己的收益
  后手收到的是 先手选完后 对方在最坏情况下给你的结果
```

### 通用定义

```
dp[i][j].first  = 面对区间 [i,j]，先手能拿到的最大总价值
dp[i][j].second = 面对区间 [i,j]，后手能拿到的最大总价值
```

---

## 二、石子游戏 · [LC 877](https://leetcode.com/problems/stone-game/)

```python
def stone_game(piles: list[int]) -> bool:
    """
    Alex 先手，每次只能取首尾。判断 Alex 是否必胜。
    此题 piles 长度是偶数，总和是奇数，总有必胜策略。
    但我们用 DP 来解。
    """
    n = len(piles)

    # dp[i][j] = (先手面对 [i,j] 的最大收益, 后手面对 [i,j] 的最大收益)
    dp: list[list[tuple[int, int]]] = [
        [(0, 0)] * n for _ in range(n)
    ]

    # base: 只有一个元素时，先手全拿
    for i in range(n):
        dp[i][i] = (piles[i], 0)

    # 区间 DP：枚举长度
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1

            # 先手选左端
            left_first = piles[i] + dp[i + 1][j][1]  # 先手拿左 + 变成后手
            left_second = dp[i + 1][j][0]  # 原来的先手变成后手

            # 先手选右端
            right_first = piles[j] + dp[i][j - 1][1]
            right_second = dp[i][j - 1][0]

            if left_first > right_first:
                dp[i][j] = (left_first, left_second)
            else:
                dp[i][j] = (right_first, right_second)

    return dp[0][n - 1][0] > dp[0][n - 1][1]


# 简化版本：只记录差值
def stone_game_diff(piles: list[int]) -> bool:
    """
    dp[i][j] = 面对 [i,j]，先手与后手的最大差值。
    dp[i][j] = max(
        piles[i] - dp[i+1][j],   # 选左端
        piles[j] - dp[i][j-1]    # 选右端
    )
    """
    n = len(piles)
    dp = [[0] * n for _ in range(n)]

    for i in range(n):
        dp[i][i] = piles[i]

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = max(piles[i] - dp[i + 1][j], piles[j] - dp[i][j - 1])

    return dp[0][n - 1] > 0
```

---

## 三、预测赢家 · [LC 486](https://leetcode.com/problems/predict-the-winner/)

```python
def predict_the_winner(nums: list[int]) -> bool:
    """
    与石子游戏相同，但数组长度不一定为偶数。
    判断先手是否 ≥ 后手（平局也算先手赢）。
    """
    n = len(nums)
    dp = [[0] * n for _ in range(n)]

    for i in range(n):
        dp[i][i] = nums[i]

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = max(
                nums[i] - dp[i + 1][j],
                nums[j] - dp[i][j - 1],
            )

    return dp[0][n - 1] >= 0
```

---

## 四、石子游戏 II · [LC 1140](https://leetcode.com/problems/stone-game-ii/)

```python
from functools import lru_cache


def stone_game_ii(piles: list[int]) -> int:
    """
    每次可以取 1 ≤ X ≤ 2M 堆石子，M 更新为 max(M, X)。
    记忆化搜索+后缀和。
    """
    n = len(piles)
    suffix = [0] * (n + 1)
    for i in range(n - 1, -1, -1):
        suffix[i] = suffix[i + 1] + piles[i]

    @lru_cache(maxsize=None)
    def dfs(i: int, m: int) -> int:
        """从 i 开始，当前 M = m，先手能拿的最大石子数。"""
        if i >= n:
            return 0
        if i + 2 * m >= n:
            return suffix[i]  # 一次拿完

        best = 0
        for x in range(1, 2 * m + 1):
            # 先手拿了 x 堆，后手从 i+x 开始取
            # 先手剩余的总数 = suffix[i] - 后手的最优结果
            best = max(best, suffix[i] - dfs(i + x, max(m, x)))

        return best

    return dfs(0, 1)
```

---

## 五、石子游戏 III · [LC 1406](https://leetcode.com/problems/stone-game-iii/)

```python
def stone_game_iii(stone_value: list[int]) -> str:
    """
    每次取 1/2/3 堆石子。返回胜者。
    dp[i] = 从 i 开始先手拿，能得到的最大净胜分。
    """
    n = len(stone_value)
    dp = [float("-inf")] * (n + 1)
    dp[n] = 0  # 空堆

    for i in range(n - 1, -1, -1):
        take = 0
        for j in range(1, 4):
            if i + j <= n:
                take += stone_value[i + j - 1]
                dp[i] = max(dp[i], take - dp[i + j])

    if dp[0] > 0:
        return "Alice"
    elif dp[0] < 0:
        return "Bob"
    else:
        return "Tie"
```

---

## 六、我能赢吗 · [LC 464](https://leetcode.com/problems/can-i-win/)

```python
from functools import lru_cache


def can_i_win(max_choosable: int, desired_total: int) -> bool:
    """
    从 1..max_choosable 中轮流选数，谁先使总和 ≥ desired_total 谁赢。
    状态压缩 DP + 记忆化搜索。
    """
    total = (1 + max_choosable) * max_choosable // 2
    if total < desired_total:
        return False
    if desired_total <= 0:
        return True

    @lru_cache(maxsize=None)
    def dfs(mask: int, remain: int) -> bool:
        """mask 表示已选的数字，remain 为剩余需要凑的数。"""
        for i in range(1, max_choosable + 1):
            bit = 1 << (i - 1)
            if not (mask & bit):
                # 选了这个数直接赢，或者对方输了
                if i >= remain or not dfs(mask | bit, remain - i):
                    return True
        return False

    return dfs(0, desired_total)
```

---

## 七、总结

| 博弈类型 | DP 技巧 |
|----------|--------|
| 取首尾（石子游戏） | 区间DP，差值状态：`dp[i][j] = max(nums[i]-dp[i+1][j], nums[j]-dp[i][j-1])` |
| 可变取法（石子II/III） | 记忆化搜索：`suffix[i] - dfs(xxx)` |
| 选数字（我能赢吗） | 状态压缩+记忆化：枚举可选数字 |

### 核心思路

```
博弈 DP 的核心：
  我选完后，问题变成了"对方在这种局面下最优能拿多少"。
  我的得分 = 我选的 + (剩余 - 对方最优得分)
         = 总和 - 对方最优得分
```

---

## 八、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 292](https://leetcode.com/problems/nim-game/) | Nim Game | Easy | 数学(博弈论) |
| [LC 486](https://leetcode.com/problems/predict-the-winner/) | Predict the Winner | Medium | 首尾取值DP |
| [LC 877](https://leetcode.com/problems/stone-game/) | Stone Game | Medium | 首尾取值DP |
| [LC 1140](https://leetcode.com/problems/stone-game-ii/) | Stone Game II | Medium | 记忆化搜索 |
| [LC 1406](https://leetcode.com/problems/stone-game-iii/) | Stone Game III | Hard | 1/2/3取DP |
| [LC 464](https://leetcode.com/problems/can-i-win/) | Can I Win | Medium | 状压+记忆化 |
| [LC 1510](https://leetcode.com/problems/stone-game-iv/) | Stone Game IV | Hard | 平方数取 |
| [LC 1563](https://leetcode.com/problems/stone-game-v/) | Stone Game V | Hard | 区间DP |

---

[← 返回索引](index.md)
