# 回文串算法 · Manacher's Algorithm

> **中心扩展法**：枚举每个中心暴力扩展，O(n²)，简单但够用大多数场景。
> **Manacher**：利用已计算过的回文信息避免重复扩展，把回文子串相关问题降到 O(n)。

---

## 一、中心扩展法（基准解法）

### 1.1 核心思想

```
回文串关于中心对称，分两种中心：
  奇数长度："aba"   中心是字符 'b' 本身
  偶数长度："abba"  中心是中间的空隙

枚举每个可能的中心（n 个字符中心 + n-1 个空隙中心），
从中心向两边扩展，直到不对称为止。
```

### 1.2 实现 · [LC 5](https://leetcode.com/problems/longest-palindromic-substring/)

```python
def longest_palindrome_expand(s: str) -> str:
    """中心扩展法。O(n²) 时间，O(1) 额外空间。"""
    if not s:
        return ""

    def expand(l: int, r: int) -> tuple[int, int]:
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1
            r += 1
        return l + 1, r - 1  # 回退到最后一次匹配成功的位置

    start, end = 0, 0
    for i in range(len(s)):
        l1, r1 = expand(i, i)        # 奇数长度，中心是 s[i]
        l2, r2 = expand(i, i + 1)    # 偶数长度，中心是 s[i], s[i+1] 之间
        if r1 - l1 > end - start:
            start, end = l1, r1
        if r2 - l2 > end - start:
            start, end = l2, r2

    return s[start:end + 1]
```

这个解法完全够用（LC 5 的数据范围 n ≤ 1000）。Manacher 把它优化到 O(n)，核心价值在于**理解如何复用已经计算过的信息**——这个思路在很多"避免重复计算"的场景都能用上。

---

## 二、Manacher 算法

### 2.1 核心思想

```
两个技巧：

1. 统一奇偶长度
   在每个字符之间（以及首尾）插入分隔符 '#'，
   "aba"  -> "#a#b#a#"
   "abba" -> "#a#b#b#a#"
   插入分隔符后，原串不管奇偶，处理后长度都是奇数，
   只需要处理"以某个字符为中心"这一种情况。

2. 复用已计算的回文信息，避免重复扩展
   维护"目前已知的、右边界最靠右的回文"的中心 center 和右边界 right。
   计算位置 i 的回文半径 p[i] 时：
     若 i 在 right 内，i 关于 center 的镜像位置 mirror 的 p[mirror] 已经算过，
     可以直接利用（对称性），不用从 0 开始扩展。
```

### 2.2 完整实现 · [LC 5](https://leetcode.com/problems/longest-palindromic-substring/)

```python
def longest_palindrome_manacher(s: str) -> str:
    """Manacher 算法。返回 s 中最长回文子串。O(n) 时间，O(n) 空间。"""
    if not s:
        return ""

    # 1. 预处理：插入分隔符统一奇偶；^ $ 是首尾哨兵，避免扩展时越界判断
    #    "aba" -> "^#a#b#a#$"
    t = "^#" + "#".join(s) + "#$"
    n = len(t)
    p = [0] * n  # p[i] = 以 t[i] 为中心的回文半径（不含中心自身）

    center, right = 0, 0  # 当前已知的、右边界最靠右的回文：中心 center，右边界 right（不含）
    for i in range(1, n - 1):
        mirror = 2 * center - i
        if i < right:
            p[i] = min(right - i, p[mirror])  # 复用镜像位置的信息

        # 中心扩展（哨兵 ^ $ 保证不会越界）
        while t[i + p[i] + 1] == t[i - p[i] - 1]:
            p[i] += 1

        # 更新"最右回文"
        if i + p[i] > right:
            center, right = i, i + p[i]

    # 2. p[i] 的最大值就是原串里最长回文子串的长度
    max_len, center_index = max((v, i) for i, v in enumerate(p))
    start = (center_index - max_len) // 2  # 从 t 的下标映射回 s 的下标
    return s[start:start + max_len]
```

### 2.3 图解：为什么可以复用镜像信息

```
s = "babcbabcba"
t = "^#b#a#b#c#b#a#b#c#b#a#$"

假设已经算到 center=7(对应 t 中的 'c'), right=12，
即 t[2..12] 这段是回文（以 7 为中心，半径 5）。

现在要算 i=10（在 right=12 之内）：
  mirror = 2*7 - 10 = 4
  p[10] 至少等于 min(right-i, p[mirror]) = min(12-10, p[4])
  因为 [2,12] 是回文，i=10 关于 center=7 的镜像 4 一定"长得一样"，
  p[4] 已经算过，直接复用下界，再尝试继续扩展即可 —— 不用从 0 开始。

这就是均摊 O(n) 的来源：center/right 只会单调右移，
每个字符最多被"新扩展"一次。
```

### 2.4 复杂度

- 时间：O(n) —— 虽然内层 `while` 看起来会重复扫描，但 `right` 指针单调不减，均摊下来总扩展次数是 O(n)。
- 空间：O(n) —— 预处理后的字符串 t 和 p 数组。

---

## 三、Manacher 的应用

### 3.1 回文子串个数 · [LC 647](https://leetcode.com/problems/palindromic-substrings/)

```python
def count_palindromic_substrings(s: str) -> int:
    """统计 s 中回文子串的个数。复用 Manacher 的 p 数组，O(n)。"""
    if not s:
        return 0

    t = "^#" + "#".join(s) + "#$"
    n = len(t)
    p = [0] * n
    center, right = 0, 0
    for i in range(1, n - 1):
        mirror = 2 * center - i
        if i < right:
            p[i] = min(right - i, p[mirror])
        while t[i + p[i] + 1] == t[i - p[i] - 1]:
            p[i] += 1
        if i + p[i] > right:
            center, right = i, i + p[i]

    # 以 t[i] 为中心、半径为 p[i] 的回文，在原串 s 中贡献 (p[i]+1)//2 个回文子串
    # （因为 t 里一半的位置是插入的 '#'，实际字符中心只占一半的"扩展步数"）
    return sum((v + 1) // 2 for v in p)
```

**为什么是 `(p[i]+1)//2`**：`p[i]` 是在**插入分隔符之后**的字符串 `t` 里量出来的半径。分隔符位置每扩展 2 步，才对应原串里"多一个回文子串"；所以奇偶各自的贡献要除以 2 取整（`(p[i]+1)//2` 同时兼容以字符为中心和以空隙为中心两种情况，可以手动代入 `"aaa"` 验证）。

### 3.2 与其他解法的对比

`[LC 5]` `[LC 647]` 这两题也可以用区间 DP 解（`dp[i][j] = s[i]==s[j] and dp[i+1][j-1]`），思路更直白但是 O(n²) 时间 O(n²) 空间；中心扩展法把空间降到 O(1) 但仍是 O(n²) 时间；只有 Manacher 能做到 O(n) 时间。三种解法在 `interval-dp.md` 和本文件 1.2 节都能找到对应实现，可以对照着看它们如何一步步优化。

---

## 四、算法对比

| 算法 | 时间 | 空间 | 备注 |
|------|------|------|------|
| 区间 DP | O(n²) | O(n²) | 思路最直白，`dp[i][j]` 直接对应"子串是否回文" |
| 中心扩展 | O(n²) | O(1) | 实现简单，LC 5 的数据规模下完全够用 |
| Manacher | O(n) | O(n) | 复用镜像信息，回文相关题目的最优解 |

---

## 五、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 5](https://leetcode.com/problems/longest-palindromic-substring/) | Longest Palindromic Substring | Medium | Manacher / 中心扩展 |
| [LC 647](https://leetcode.com/problems/palindromic-substrings/) | Palindromic Substrings | Medium | Manacher / 中心扩展 |
| [LC 214](https://leetcode.com/problems/shortest-palindrome/) | Shortest Palindrome | Hard | KMP（见 [string-matching.md](string-matching.md) 3.3） |
| [LC 336](https://leetcode.com/problems/palindrome-pairs/) | Palindrome Pairs | Hard | Manacher + 字典树/哈希 |
| [LC 1332](https://leetcode.com/problems/remove-palindromic-subsequences/) | Remove Palindromic Subsequences | Easy | 回文性质判断，非 Manacher |

---

[← 返回索引](index.md)
