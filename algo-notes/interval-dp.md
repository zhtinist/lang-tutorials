# 区间 DP · Interval DP

> 区间 DP 模板：**枚举区间长度 → 枚举左端点 → 确定右端点 → 枚举分割点**。
> 适合问题：大区间的最优解依赖于它包含的小区间的最优解。

---

## 一、区间 DP 模板

```python
def interval_dp_template(n: int) -> int:
    """
    区间 DP 通用模板。
    dp[i][j] = 区间 [i, j] 上的最优解。

    核心循环：
      for length in range(2, n+1):
          for i in range(n - length + 1):
              j = i + length - 1
              for k in range(i, j):
                  dp[i][j] = merge(dp[i][k], dp[k+1][j])
    """
    dp = [[0] * n for _ in range(n)]

    # base case: 长度为 1 的区间
    # for i in range(n): dp[i][i] = ...

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            for k in range(i, j):
                dp[i][j] = min(dp[i][j], dp[i][k] + dp[k + 1][j] + cost(i, k, j))
                # 或者 max(dp[i][j], ...)

    return dp[0][n - 1]
```

---

## 二、戳气球 · [LC 312](https://leetcode.com/problems/burst-balloons/) 🔥

```python
def max_coins(nums: list[int]) -> int:
    """
    每戳破一个气球，得到 nums[i-1] * nums[i] * nums[i+1] 分。
    相当于每次从区间中删除一个元素，直到删空。
    
    反向思考：往区间里加气球！最后加的那个气球得分最高。
    dp[i][j] = 开区间 (i, j) 中戳破所有气球能得到的最大分数。
    
    设 k 是 (i,j) 区间内最后一个被戳破的气球：
    dp[i][j] = max(dp[i][k] + dp[k][j] + nums[i] * nums[k] * nums[j])
    """
    # 首尾加哨兵 1
    arr = [1] + nums + [1]
    n = len(arr)
    dp = [[0] * n for _ in range(n)]

    for length in range(2, n):
        for i in range(n - length):
            j = i + length
            for k in range(i + 1, j):
                dp[i][j] = max(
                    dp[i][j],
                    dp[i][k] + dp[k][j] + arr[i] * arr[k] * arr[j],
                )

    return dp[0][n - 1]
```

**图解**
```
nums = [3, 1, 5, 8]
arr  = [1, 3, 1, 5, 8, 1]

戳气球过程（反向思考）：
  往空区间里放气球，每次放的是当前区间最后一个被戳破的。

  放在 [1...1] 之间：最后一个放 3 → 1*3*1 = 3
  放在 [1...5] 之间：最后一个放 3 → 1*3*5 = 15
  ...
```

---

## 三、最长回文子序列 · [LC 516](https://leetcode.com/problems/longest-palindromic-subsequence/)

```python
def longest_palindrome_subseq(s: str) -> int:
    """
    dp[i][j] = s[i:j+1] 中最长回文子序列的长度。
    
    如果 s[i] == s[j]:
        dp[i][j] = dp[i+1][j-1] + 2
    否则:
        dp[i][j] = max(dp[i+1][j], dp[i][j-1])
    """
    n = len(s)
    dp = [[0] * n for _ in range(n)]

    for i in range(n):
        dp[i][i] = 1

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                dp[i][j] = dp[i + 1][j - 1] + 2
            else:
                dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])

    return dp[0][n - 1]
```

---

## 四、奇怪的打印机 · [LC 664](https://leetcode.com/problems/strange-printer/)

```python
def strange_printer(s: str) -> int:
    """
    打印机每次可以打印同一字符的一段区间。
    dp[i][j] = 打印 s[i:j+1] 的最少次数。
    
    如果 s[i] == s[j]:
        dp[i][j] = dp[i][j-1]  # 第一次打印就能覆盖 s[j]
    否则:
        dp[i][j] = min(dp[i][k] + dp[k+1][j]) for k in [i, j)
    """
    # 去重优化：连续相同字符不影响打印次数
    chars: list[str] = []
    for c in s:
        if not chars or chars[-1] != c:
            chars.append(c)
    s = "".join(chars)

    n = len(s)
    dp = [[0] * n for _ in range(n)]

    for i in range(n):
        dp[i][i] = 1

    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                dp[i][j] = dp[i][j - 1]
            else:
                dp[i][j] = float("inf")
                for k in range(i, j):
                    dp[i][j] = min(dp[i][j], dp[i][k] + dp[k + 1][j])

    return dp[0][n - 1] if n > 0 else 0
```

---

## 五、合并石子 · [LC 1000](https://leetcode.com/problems/minimum-cost-to-merge-stones/)

```python
def merge_stones(stones: list[int], k: int) -> int:
    """
    每次合并连续的 K 堆石子成一堆，代价为合并堆的和。
    判断能否合并成一堆： (n - 1) % (k - 1) == 0
    
    dp[i][j][m] = 把 [i,j] 合并成 m 堆的最小代价
    优化后可以去掉 m 维度：
    dp[i][j] = 把 [i,j] 合并到不能再合并的最小代价 + 剩余堆数
    """
    n = len(stones)
    if (n - 1) % (k - 1) != 0:
        return -1

    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + stones[i]

    # dp[i][j] = 区间 [i,j] 合并到最少堆数的最小代价
    dp = [[0] * n for _ in range(n)]

    for length in range(k, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float("inf")

            # 每 k 堆合并一次，(length - 1) % (k - 1) == 0 说明可以合并成 1 堆
            if (length - 1) % (k - 1) == 0:
                for m in range(i, j, k - 1):
                    dp[i][j] = min(
                        dp[i][j],
                        dp[i][m] + dp[m + 1][j],
                    )
                dp[i][j] += prefix[j + 1] - prefix[i]
            else:
                for m in range(i, j, k - 1):
                    dp[i][j] = min(
                        dp[i][j],
                        dp[i][m] + dp[m + 1][j],
                    )

    return dp[0][n - 1]
```

---

## 六、多边形三角剖分 · [LC 1039](https://leetcode.com/problems/minimum-score-triangulation-of-polygon/)

```python
def min_score_triangulation(values: list[int]) -> int:
    """
    dp[i][j] = 多边形 i..j 的最低三角剖分分数。
    取 k 为 (i,j) 之间的顶点，形成三角形 (i, k, j)。
    
    dp[i][j] = min(dp[i][k] + dp[k][j] + values[i] * values[k] * values[j])
    """
    n = len(values)
    dp = [[0] * n for _ in range(n)]

    for length in range(3, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = float("inf")
            for k in range(i + 1, j):
                dp[i][j] = min(
                    dp[i][j],
                    dp[i][k] + dp[k][j] + values[i] * values[k] * values[j],
                )

    return dp[0][n - 1]
```

---

## 七、总结

| 问题 | 状态 | 转移关键 |
|------|------|---------|
| 戳气球 [LC 312](https://leetcode.com/problems/burst-balloons/) | `dp[i][j]` 开区间 | 最后一个戳破的 k |
| 最长回文子序列 [LC 516](https://leetcode.com/problems/longest-palindromic-subsequence/) | `dp[i][j]` 闭区间 | 两端相等等于中间+2 |
| 打印机 [LC 664](https://leetcode.com/problems/strange-printer/) | `dp[i][j]` 闭区间 | s[i]==s[j] 则 dp[i][j-1] |
| 合并石子 [LC 1000](https://leetcode.com/problems/minimum-cost-to-merge-stones/) | `dp[i][j]` 闭区间 | K路合并，判断能否合并 |
| 三角剖分 [LC 1039](https://leetcode.com/problems/minimum-score-triangulation-of-polygon/) | `dp[i][j]` 闭区间 | 枚举中间顶点形成三角形 |

### 三重循环模板

```python
for length in range(2, n + 1):           # 枚举区间长度
    for i in range(n - length + 1):       # 枚举左端点
        j = i + length - 1                 # 计算右端点
        for k in range(i, j):              # 枚举分割点
            dp[i][j] = merge(dp[i][k], dp[k+1][j])
```

---

## 八、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 312](https://leetcode.com/problems/burst-balloons/) | Burst Balloons | Hard | 反向加气球 |
| [LC 516](https://leetcode.com/problems/longest-palindromic-subsequence/) | Longest Palindromic Subsequence | Medium | 两端相等 |
| [LC 664](https://leetcode.com/problems/strange-printer/) | Strange Printer | Hard | 去重优化 |
| [LC 1000](https://leetcode.com/problems/minimum-cost-to-merge-stones/) | Minimum Cost to Merge Stones | Hard | K路合并 |
| [LC 1039](https://leetcode.com/problems/minimum-score-triangulation-of-polygon/) | Minimum Score Triangulation | Medium | 枚举顶点 |
| [LC 1130](https://leetcode.com/problems/minimum-cost-tree-from-leaf-values/) | Minimum Cost Tree From Leaf Values | Medium | 区间DP |
| [LC 5](https://leetcode.com/problems/longest-palindromic-substring/) | Longest Palindromic Substring | Medium | 回文子串(连续) |
| [LC 647](https://leetcode.com/problems/palindromic-substrings/) | Palindromic Substrings | Medium | 回文计数 |

---

[← 返回索引](index.md)
