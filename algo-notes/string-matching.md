# 字符串匹配 · String Matching

> **KMP**：利用匹配失败的信息避免重复比较，O(n+m)。
> **Rabin-Karp**：滚动哈希，适合多模式匹配。

---

## 一、KMP 算法

### 1.1 核心思想

```
KMP 的核心是 next 数组（也称前缀函数/部分匹配表）。
next[j] = 模式串 p[0:j] 的最长公共前后缀长度。

匹配 s[i] 和 p[j] 失败时：
  j = next[j-1] — 而不是 j = 0
  跳过已经匹配过的前缀。
```

### 1.2 完整实现 · [LC 28](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/)

```python
def str_str_kmp(haystack: str, needle: str) -> int:
    """KMP 算法实现。返回 needle 在 haystack 中首次出现的位置。"""
    if not needle:
        return 0

    n, m = len(haystack), len(needle)

    # 1. 构建 next 数组
    nxt = [0] * m
    j = 0  # j = 当前匹配的前缀长度
    for i in range(1, m):
        while j > 0 and needle[i] != needle[j]:
            j = nxt[j - 1]  # 回退
        if needle[i] == needle[j]:
            j += 1
        nxt[i] = j

    # 2. 匹配
    j = 0
    for i in range(n):
        while j > 0 and haystack[i] != needle[j]:
            j = nxt[j - 1]
        if haystack[i] == needle[j]:
            j += 1
        if j == m:
            return i - m + 1  # 匹配成功

    return -1
```

### 1.3 next 数组图解

```
needle = "aabaaf"
         a a b a a f
next   = [0,1,0,1,2,0]

next[1] = 1: "aa" 的最长公共前后缀是 "a" (长度1)
next[4] = 2: "aabaa" 的最长公共前后缀是 "aa" (长度2)

匹配失败时:
  s: "aabaaca..."
  p: "aabaaf"
          ^ 这里 p[5]='f' vs s[5]='c'
  j = next[4] = 2 → 回退到 j=2

  s: "aabaaca..."
  p:   "aab..."     ← 跳过已匹配的前缀，继续比较
```

---

## 二、Rabin-Karp 算法

### 2.1 滚动哈希

```python
def str_str_rk(haystack: str, needle: str) -> int:
    """
    Rabin-Karp 滚动哈希。
    hash(s[i:i+L]) = (hash(s[i-1:i-1+L]) * base - s[i-1] * base^L + s[i+L-1]) % MOD
    """
    if not needle:
        return 0

    n, m = len(haystack), len(needle)
    if n < m:
        return -1

    BASE = 256   # 基数 (ASCII范围)
    MOD = 10**9 + 7

    # 计算 BASE^(m-1) % MOD
    power = 1
    for _ in range(m - 1):
        power = (power * BASE) % MOD

    # 计算 needle 的哈希值
    needle_hash = 0
    for c in needle:
        needle_hash = (needle_hash * BASE + ord(c)) % MOD

    # 计算 haystack 第一个窗口的哈希值
    window_hash = 0
    for i in range(m):
        window_hash = (window_hash * BASE + ord(haystack[i])) % MOD

    if window_hash == needle_hash and haystack[:m] == needle:
        return 0  # 注意：哈希碰撞需要二次确认

    # 滑动窗口
    for i in range(m, n):
        # 去掉最左字符
        window_hash = (window_hash - ord(haystack[i - m]) * power) % MOD
        # 加上最右字符
        window_hash = (window_hash * BASE + ord(haystack[i])) % MOD

        if window_hash == needle_hash and haystack[i - m + 1 : i + 1] == needle:
            return i - m + 1

    return -1
```

---

## 三、KMP 应用

### 3.1 重复的子字符串 · [LC 459](https://leetcode.com/problems/repeated-substring-pattern/)

```python
def repeated_substring_pattern(s: str) -> bool:
    """
    判断 s 是否由某个子串重复多次构成。
    方法：s+s 去掉首尾字符，如果包含 s，则满足。
    也可以用 KMP 的 next 数组。
    """
    # KMP 解法
    n = len(s)
    nxt = [0] * n
    j = 0
    for i in range(1, n):
        while j > 0 and s[i] != s[j]:
            j = nxt[j - 1]
        if s[i] == s[j]:
            j += 1
        nxt[i] = j

    # 最长公共前后缀长度 = nxt[-1]
    lps = nxt[-1]
    return lps > 0 and n % (n - lps) == 0
```

### 3.2 最长快乐前缀 · [LC 1392](https://leetcode.com/problems/longest-happy-prefix/)

```python
def longest_prefix(s: str) -> str:
    """
    最长的既是前缀又是后缀（但不是整个字符串）的子串。
    就是 next 数组的最后一个值。
    """
    n = len(s)
    nxt = [0] * n
    j = 0
    for i in range(1, n):
        while j > 0 and s[i] != s[j]:
            j = nxt[j - 1]
        if s[i] == s[j]:
            j += 1
        nxt[i] = j

    return s[: nxt[-1]]
```

### 3.3 最短回文串 · [LC 214](https://leetcode.com/problems/shortest-palindrome/)

```python
def shortest_palindrome(s: str) -> str:
    """
    在 s 前面添加最少字符使之成为回文串。
    等价于找 s 的最长回文前缀。

    KMP 解法：s + '#' + reverse(s)，用 next 数组。
    """
    rev = s[::-1]
    combined = s + "#" + rev

    # 构建 next 数组
    n = len(combined)
    nxt = [0] * n
    j = 0
    for i in range(1, n):
        while j > 0 and combined[i] != combined[j]:
            j = nxt[j - 1]
        if combined[i] == combined[j]:
            j += 1
        nxt[i] = j

    # s 的最长回文前缀长度 = nxt[-1]
    lps_len = nxt[-1]
    # 把 s 去掉回文前缀后的部分的逆序加到前面
    return rev[: len(s) - lps_len] + s
```

---

## 四、Z 函数

```python
def z_function(s: str) -> list[int]:
    """
    z[i] = s 和 s[i:] 的最长公共前缀长度。
    O(n)
    """
    n = len(s)
    z = [0] * n
    l = r = 0  # z-box 的边界 [l, r)

    for i in range(1, n):
        if i < r:
            z[i] = min(r - i, z[i - l])
        while i + z[i] < n and s[z[i]] == s[i + z[i]]:
            z[i] += 1
        if i + z[i] > r:
            l, r = i, i + z[i]

    return z
```

---

## 五、算法对比

| 算法 | 预处理 | 匹配 | 适用场景 |
|------|--------|------|---------|
| KMP | O(m) | O(n) | 单模式匹配 |
| Rabin-Karp | O(1) | O(n) 平均 | 多模式匹配 |
| Z 函数 | O(n) | O(n) | 字符串周期性 |
| 暴力 | O(1) | O(nm) | 仅短串 |

---

## 六、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 28](https://leetcode.com/problems/find-the-index-of-the-first-occurrence-in-a-string/) | Implement strStr() | Easy | KMP/RK |
| [LC 459](https://leetcode.com/problems/repeated-substring-pattern/) | Repeated Substring Pattern | Easy | KMP next |
| [LC 1392](https://leetcode.com/problems/longest-happy-prefix/) | Longest Happy Prefix | Hard | KMP next |
| [LC 214](https://leetcode.com/problems/shortest-palindrome/) | Shortest Palindrome | Hard | KMP + 逆串 |
| [LC 686](https://leetcode.com/problems/repeated-string-match/) | Repeated String Match | Medium | KMP/RK |
| [LC 796](https://leetcode.com/problems/rotate-string/) | Rotate String | Easy | 拼接+KMP |

---

[← 返回索引](index.md)
