# 子序列问题 · Subsequence DP

> 子序列问题核心：定义 `dp[i]` 或 `dp[i][j]` 表示以某个位置**结尾**或**前缀**的最优解。
> LIS 有 O(n log n) 贪心+二分优化，LCS 和编辑距离是二维 DP 的经典模板。

---

## 一、最长递增子序列 LIS

### 1.1 基础 · [LC 300](https://leetcode.com/problems/longest-increasing-subsequence/)

```python
def length_of_lis(nums: list[int]) -> int:
    """
    dp[i] = 以 nums[i] 结尾的最长递增子序列长度
    dp[i] = max(dp[j] + 1) for j < i and nums[j] < nums[i]
    O(n²)
    """
    n = len(nums)
    dp = [1] * n

    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)

    return max(dp)
```

### 1.2 贪心 + 二分（耐心排序）O(n log n)

```python
import bisect


def length_of_lis_nlogn(nums: list[int]) -> int:
    """
    维护一个 tails 数组，tails[i] = 长度为 i+1 的 LIS 的最小末尾值。
    tails 是递增的，可以用二分查找。
    """
    tails: list[int] = []

    for x in nums:
        idx = bisect.bisect_left(tails, x)
        if idx == len(tails):
            tails.append(x)
        else:
            tails[idx] = x

    return len(tails)
```

### 1.3 LIS 个数 · [LC 673](https://leetcode.com/problems/number-of-longest-increasing-subsequence/)

```python
def find_number_of_lis(nums: list[int]) -> int:
    """
    dp_len[i] = 以 nums[i] 结尾的 LIS 长度
    dp_cnt[i] = 以 nums[i] 结尾的 LIS 个数
    """
    n = len(nums)
    dp_len = [1] * n
    dp_cnt = [1] * n
    max_len = 1

    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                if dp_len[j] + 1 > dp_len[i]:
                    dp_len[i] = dp_len[j] + 1
                    dp_cnt[i] = dp_cnt[j]
                elif dp_len[j] + 1 == dp_len[i]:
                    dp_cnt[i] += dp_cnt[j]
        max_len = max(max_len, dp_len[i])

    return sum(cnt for length, cnt in zip(dp_len, dp_cnt) if length == max_len)
```

### 1.4 俄罗斯套娃信封 · [LC 354](https://leetcode.com/problems/russian-doll-envelopes/)

```python
import bisect


def max_envelopes(envelopes: list[list[int]]) -> int:
    """
    按宽度升序、宽度相同按高度降序排序，
    然后对高度求 LIS。
    排序保证宽度递增，高度降序保证相同宽度只能选一个。
    """
    envelopes.sort(key=lambda x: (x[0], -x[1]))
    heights = [h for _, h in envelopes]
    return length_of_lis_nlogn(heights)
```

---

## 二、最长公共子序列 LCS · [LC 1143](https://leetcode.com/problems/longest-common-subsequence/)

```python
def longest_common_subsequence(text1: str, text2: str) -> int:
    """
    dp[i][j] = text1[0:i] 和 text2[0:j] 的 LCS 长度
    如果 text1[i-1] == text2[j-1]:
        dp[i][j] = dp[i-1][j-1] + 1
    否则:
        dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    """
    m, n = len(text1), len(text2)
    # 空间优化：只用两行
    prev = [0] * (n + 1)

    for i in range(1, m + 1):
        cur = [0] * (n + 1)
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur

    return prev[n]
```

### 打印 LCS 路径

```python
def print_lcs(text1: str, text2: str) -> str:
    """还原 LCS 字符串。"""
    m, n = len(text1), len(text2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if text1[i - 1] == text2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    # 回溯
    i, j = m, n
    chars: list[str] = []
    while i > 0 and j > 0:
        if text1[i - 1] == text2[j - 1]:
            chars.append(text1[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] > dp[i][j - 1]:
            i -= 1
        else:
            j -= 1

    return "".join(reversed(chars))
```

### [LC 718](https://leetcode.com/problems/maximum-length-of-repeated-subarray/) 最长公共子数组（连续）

```python
def find_length(nums1: list[int], nums2: list[int]) -> int:
    """强制连续的公共子数组。"""
    m, n = len(nums1), len(nums2)
    dp = [0] * (n + 1)
    ans = 0

    for i in range(1, m + 1):
        # 必须反向遍历（与0-1背包同理）
        for j in range(n, 0, -1):
            if nums1[i - 1] == nums2[j - 1]:
                dp[j] = dp[j - 1] + 1
                ans = max(ans, dp[j])
            else:
                dp[j] = 0

    return ans
```

---

## 三、编辑距离的三步铺垫

> 编辑距离（插入/删除/替换取 min）的转移方程第一次见容易觉得"背下来就行"，但不知道它从哪来。
> 下面三道题由简到难，每一道都是前一道去掉一个操作/加一个操作，最后自然推出编辑距离的完整方程。

### 3.1 第一步：只判断"是不是子序列" · [LC 392](https://leetcode.com/problems/is-subsequence/)

```python
def is_subsequence(s: str, t: str) -> bool:
    """
    判断 s 是否是 t 的子序列（只能删除 t 中的字符，不能增/改）。
    dp[i][j] = s[0:i] 能在 t[0:j] 里匹配到的最长前缀长度。
    - 字符相等：dp[i][j] = dp[i-1][j-1] + 1（都往前推一格）
    - 不相等：dp[i][j] = dp[i][j-1]（t 跳过这个字符，s 不动，只能从 t 少一个字符的情况延续）
    最后看 dp[m][n] 是否等于 len(s)：s 是否整个被匹配完。
    """
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = dp[i][j - 1]  # 只有"t 删除一个字符"这一种操作

    return dp[m][n] == m
```

### 3.2 第二步：子序列计数 · [LC 115](https://leetcode.com/problems/distinct-subsequences/)

```python
def num_distinct(s: str, t: str) -> int:
    """
    s 的子序列中，有多少种不同的删除方式能得到 t。
    比 LC 392 进一步：不再是"能不能匹配"，而是"有多少种匹配方式"，
    所以 dp[i][j] 从布尔值变成计数，转移从"取更优的一支"变成"把两支加起来"。

    dp[i][j] = s[0:i] 中有多少种子序列等于 t[0:j]
    - s[i-1] == t[j-1]：s 的这个字符「可以选，也可以不选」
        选它匹配 t[j-1]  -> dp[i-1][j-1] 种方式
        不选它（留着它不用，指望 s 前面的字符凑出 t[0:j]）-> dp[i-1][j] 种方式
        两者相加
    - 不相等：s 的这个字符只能不用 -> dp[i-1][j]

    base case：dp[i][0] = 1（把 s 前 i 个字符全部删掉，唯一一种方式凑出空串 t=""）
    """
    m, n = len(s), len(t)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = 1

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s[i - 1] == t[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + dp[i - 1][j]
            else:
                dp[i][j] = dp[i - 1][j]

    return dp[m][n]
```

> **从 LC 392 到 LC 115 到编辑距离的演化逻辑**：
> LC 392 只有"删除"一种操作，状态是布尔值（能不能匹配完）；
> LC 115 还是只有"删除"，但状态从布尔值变成计数（有几种删除方式能匹配完）；
> 编辑距离（下面）在"删除"基础上加上"插入"和"替换"两种操作，状态又从计数变回"最少操作次数"，
> 三种操作分别对应三个可以转移过来的方向，取最小值——这就是为什么编辑距离的方程里有 3 项 `min(...)`。

---

## 四、编辑距离 · [LC 72](https://leetcode.com/problems/edit-distance/)

```python
def min_distance(word1: str, word2: str) -> int:
    """
    dp[i][j] = word1[0:i] 转换为 word2[0:j] 的最少操作数
    插入: dp[i][j-1] + 1
    删除: dp[i-1][j] + 1
    替换: dp[i-1][j-1] + (word1[i-1] != word2[j-1])
    """
    m, n = len(word1), len(word2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    # base case
    for i in range(m + 1):
        dp[i][0] = i  # 全部删除
    for j in range(n + 1):
        dp[0][j] = j  # 全部插入

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],    # 删除
                    dp[i][j - 1],    # 插入
                    dp[i - 1][j - 1],  # 替换
                )

    return dp[m][n]
```

### 编辑距离空间优化

```python
def min_distance_1d(word1: str, word2: str) -> int:
    m, n = len(word1), len(word2)
    dp = list(range(n + 1))

    for i in range(1, m + 1):
        prev = dp[0]
        dp[0] = i
        for j in range(1, n + 1):
            temp = dp[j]
            if word1[i - 1] == word2[j - 1]:
                dp[j] = prev
            else:
                dp[j] = 1 + min(dp[j], dp[j - 1], prev)
            prev = temp

    return dp[n]
```

### 编辑距离变体

| 题目 | 操作 | 核心修改 |
|------|------|---------|
| [LC 72](https://leetcode.com/problems/edit-distance/) 编辑距离 | 插入/删除/替换 | 标准模板 |
| [LC 583](https://leetcode.com/problems/delete-operation-for-two-strings/) 两个字符串的删除 | 只能删除 | 删除=dp[i-1][j]+1, 删除=dp[i][j-1]+1 |
| [LC 712](https://leetcode.com/problems/minimum-ascii-delete-sum-for-two-strings/) 最小 ASCII 删除和 | 只能删除 | 代价改为 ASCII 值 |

---

## 五、正则表达式匹配 · [LC 10](https://leetcode.com/problems/regular-expression-matching/)

```python
def is_match(s: str, p: str) -> bool:
    """
    dp[i][j] = s[0:i] 是否匹配 p[0:j]
    '.' 匹配任意单个字符
    '*' 匹配前一个字符 0 次或多次
    """
    m, n = len(s), len(p)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True

    # p 中 a*b*c* 这样的模式可以匹配空字符串
    for j in range(2, n + 1):
        if p[j - 1] == "*":
            dp[0][j] = dp[0][j - 2]

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if p[j - 1] == "*":
                # 0 次：忽略 a*
                zero = dp[i][j - 2]
                # 多次：前提是 s[i-1] 匹配 p[j-2]
                prev_match = p[j - 2] in (s[i - 1], ".")
                more = prev_match and dp[i - 1][j]
                dp[i][j] = zero or more
            else:
                # 普通字符或 '.'
                if p[j - 1] in (s[i - 1], "."):
                    dp[i][j] = dp[i - 1][j - 1]

    return dp[m][n]
```

---

## 六、总结

| 问题 | 状态定义 | 转移核心 | 复杂度 |
|------|---------|---------|--------|
| LIS | `dp[i]` 以i结尾 | 遍历前面更小的 | O(n²) / O(n log n) |
| LCS | `dp[i][j]` 前缀 | 相等对角+1，不等取max | O(mn) |
| 公共子数组 | `dp[i][j]` 前缀 | 相等加1，不等归零 | O(mn) |
| 编辑距离 | `dp[i][j]` 前缀 | 三种操作取min | O(mn) |
| 正则匹配 | `dp[i][j]` 前缀 | 处理 * 的特殊逻辑 | O(mn) |

---

## 七、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 300](https://leetcode.com/problems/longest-increasing-subsequence/) | Longest Increasing Subsequence | Medium | LIS模板 |
| [LC 673](https://leetcode.com/problems/number-of-longest-increasing-subsequence/) | Number of LIS | Medium | LIS计数 |
| [LC 354](https://leetcode.com/problems/russian-doll-envelopes/) | Russian Doll Envelopes | Hard | 二维LIS |
| [LC 1143](https://leetcode.com/problems/longest-common-subsequence/) | Longest Common Subsequence | Medium | LCS模板 |
| [LC 718](https://leetcode.com/problems/maximum-length-of-repeated-subarray/) | Max Length of Repeated Subarray | Medium | 连续子数组 |
| [LC 72](https://leetcode.com/problems/edit-distance/) | Edit Distance | Medium | 编辑距离模板 |
| [LC 583](https://leetcode.com/problems/delete-operation-for-two-strings/) | Delete Operation for Two Strings | Medium | 编辑距离变体 |
| [LC 712](https://leetcode.com/problems/minimum-ascii-delete-sum-for-two-strings/) | Min ASCII Delete Sum | Medium | 编辑距离变体 |
| [LC 10](https://leetcode.com/problems/regular-expression-matching/) | Regular Expression Matching | Hard | 正则匹配 |
| [LC 44](https://leetcode.com/problems/wildcard-matching/) | Wildcard Matching | Hard | 通配符匹配 |
| [LC 115](https://leetcode.com/problems/distinct-subsequences/) | Distinct Subsequences | Hard | 子序列计数 |
| [LC 392](https://leetcode.com/problems/is-subsequence/) | Is Subsequence | Easy | 简单子序列判断 |

---

[← 返回索引](index.md)
