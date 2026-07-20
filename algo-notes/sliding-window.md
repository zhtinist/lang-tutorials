# 滑动窗口 · Sliding Window

> 滑动窗口解决**子串/子数组**类问题。核心：右指针扩张窗口 → 左指针收缩窗口。窗口内维护一个状态（计数器、和等），在满足/不满足条件时移动指针。

---

## 一、通用框架

```python
from collections import defaultdict, Counter


def sliding_window(s: str) -> None:
    """滑动窗口通用伪代码框架。"""
    window: dict[str, int] = defaultdict(int)  # 窗口内数据
    left = right = 0

    while right < len(s):
        # 1. 右指针扩张，加入窗口
        c = s[right]
        window[c] += 1
        right += 1

        # 2. 窗口内数据更新...（根据题目需求）

        # 3. 判断是否需要收缩窗口
        while window_needs_shrink(window):  # 替换为具体条件
            d = s[left]
            window[d] -= 1
            left += 1

            # 4. 窗口收缩后的更新...

        # 5. 更新答案...
```

**核心要点**：
- `right` 指针一直向右移动，每次循环 `right++`
- `left` 指针在 `while` 条件满足时移动（shrink 阶段）
- 窗口 `[left, right)` 左闭右开：长度为 `right - left`

---

## 二、变长窗口

### 2.1 最小覆盖子串 · [LC 76](https://leetcode.com/problems/minimum-window-substring/)

```python
def min_window(s: str, t: str) -> str:
    """
    在 s 中找到包含 t 所有字符的最小子串。
    目标：need 字典，窗口：window 字典。
    用 valid 计数已满足的字符数。
    """
    from collections import defaultdict

    need: dict[str, int] = defaultdict(int)
    window: dict[str, int] = defaultdict(int)
    for c in t:
        need[c] += 1

    left = right = 0
    valid = 0  # 窗口中满足 need 条件的字符数
    start, min_len = 0, float("inf")

    while right < len(s):
        # 扩展窗口
        c = s[right]
        right += 1
        if c in need:
            window[c] += 1
            if window[c] == need[c]:
                valid += 1

        # 收缩窗口（当所有字符都满足条件时）
        while valid == len(need):
            # 更新答案
            if right - left < min_len:
                start, min_len = left, right - left

            d = s[left]
            left += 1
            if d in need:
                if window[d] == need[d]:
                    valid -= 1
                window[d] -= 1

    return "" if min_len == float("inf") else s[start:start + min_len]
```

### 2.2 无重复字符的最长子串 · [LC 3](https://leetcode.com/problems/longest-substring-without-repeating-characters/)

```python
def length_of_longest_substring(s: str) -> int:
    """找到不含重复字符的最长子串长度。"""
    window: dict[str, int] = defaultdict(int)
    left = right = 0
    ans = 0

    while right < len(s):
        c = s[right]
        right += 1
        window[c] += 1

        # 出现重复时收缩
        while window[c] > 1:
            d = s[left]
            left += 1
            window[d] -= 1

        # 此时窗口内无重复字符
        ans = max(ans, right - left)

    return ans
```

> **优化**：由于只有重复时才收缩，可以用 `left = max(left, last_pos[c] + 1)` 优化到一次遍历无需 while 内循环。

### 2.3 长度最小的子数组 · [LC 209](https://leetcode.com/problems/minimum-size-subarray-sum/)

```python
def min_sub_array_len(target: int, nums: list[int]) -> int:
    """和 >= target 的最短子数组长度。"""
    left = cur_sum = 0
    ans = float("inf")

    for right in range(len(nums)):
        cur_sum += nums[right]

        while cur_sum >= target:
            ans = min(ans, right - left + 1)
            cur_sum -= nums[left]
            left += 1

    return 0 if ans == float("inf") else ans
```

---

## 三、定长窗口

### 3.1 找到字符串中所有字母异位词 · [LC 438](https://leetcode.com/problems/find-all-anagrams-in-a-string/)

```python
def find_anagrams(s: str, p: str) -> list[int]:
    """
    在 s 中找所有 p 的字母异位词的起始索引。
    维护固定长度的窗口。
    """
    from collections import Counter

    need = Counter(p)
    window: dict[str, int] = defaultdict(int)
    left = right = 0
    valid = 0
    ans: list[int] = []

    while right < len(s):
        c = s[right]
        right += 1
        if c in need:
            window[c] += 1
            if window[c] == need[c]:
                valid += 1

        # 窗口大小 >= len(p) 时收缩（保持固定长度）
        while right - left >= len(p):
            if valid == len(need):
                ans.append(left)

            d = s[left]
            left += 1
            if d in need:
                if window[d] == need[d]:
                    valid -= 1
                window[d] -= 1

    return ans
```

### 3.2 字符串的排列 · [LC 567](https://leetcode.com/problems/permutation-in-string/)

```python
def check_inclusion(s1: str, s2: str) -> bool:
    """判断 s2 是否包含 s1 的某种排列。与 [LC 438](https://leetcode.com/problems/find-all-anagrams-in-a-string/) 几乎相同。"""
    from collections import Counter

    need = Counter(s1)
    window: dict[str, int] = defaultdict(int)
    left = right = 0
    valid = 0

    while right < len(s2):
        c = s2[right]
        right += 1
        if c in need:
            window[c] += 1
            if window[c] == need[c]:
                valid += 1

        while right - left >= len(s1):
            if valid == len(need):
                return True
            d = s2[left]
            left += 1
            if d in need:
                if window[d] == need[d]:
                    valid -= 1
                window[d] -= 1

    return False
```

---

## 四、滑动窗口 + 哈希

### 至多包含 K 个不同字符的最长子串 · [LC 340](https://leetcode.com/problems/longest-substring-with-at-most-k-distinct-characters/)（会员题）

```python
def length_of_longest_substring_k_distinct(s: str, k: int) -> int:
    """至多包含 k 个不同字符的最长子串。"""
    window: dict[str, int] = defaultdict(int)
    left = ans = 0

    for right in range(len(s)):
        window[s[right]] += 1

        while len(window) > k:
            window[s[left]] -= 1
            if window[s[left]] == 0:
                del window[s[left]]
            left += 1

        ans = max(ans, right - left + 1)

    return ans
```

---

## 五、高频变体总结

| 问题类型 | 窗口收缩条件 | 窗口内维护 | 例题 |
|----------|-------------|-----------|------|
| 最小覆盖子串 | 满足 need 条件 | valid 计数器 | [LC 76](https://leetcode.com/problems/minimum-window-substring/) |
| 最长无重复子串 | 出现重复字符 | 字符计数 | [LC 3](https://leetcode.com/problems/longest-substring-without-repeating-characters/) |
| 字母异位词 | 窗口大小超过模式串 | valid 计数器 | [LC 438](https://leetcode.com/problems/find-all-anagrams-in-a-string/), 567 |
| 最短子数组和 | `cur_sum >= target` | 窗口和 | [LC 209](https://leetcode.com/problems/minimum-size-subarray-sum/) |
| 至多K个不同字符 | `len(window) > k` | 字符种类数 | [LC 340](https://leetcode.com/problems/longest-substring-with-at-most-k-distinct-characters/) |

---

## 六、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 3](https://leetcode.com/problems/longest-substring-without-repeating-characters/) | Longest Substring Without Repeating | Medium | 基础变长窗口 |
| [LC 76](https://leetcode.com/problems/minimum-window-substring/) | Minimum Window Substring | Hard | 覆盖子串模板 |
| [LC 209](https://leetcode.com/problems/minimum-size-subarray-sum/) | Minimum Size Subarray Sum | Medium | 和≥target缩窗 |
| [LC 438](https://leetcode.com/problems/find-all-anagrams-in-a-string/) | Find All Anagrams | Medium | 定长窗口+Counter |
| [LC 567](https://leetcode.com/problems/permutation-in-string/) | Permutation in String | Medium | 同[LC 438](https://leetcode.com/problems/find-all-anagrams-in-a-string/) |
| [LC 239](https://leetcode.com/problems/sliding-window-maximum/) | Sliding Window Maximum | Hard | 单调队列(见单调队列篇) |
| [LC 395](https://leetcode.com/problems/longest-substring-with-at-least-k-repeating-characters/) | Longest Substring with At Least K Repeating | Medium | 枚举字符种类 |
| [LC 424](https://leetcode.com/problems/longest-repeating-character-replacement/) | Longest Repeating Character Replacement | Medium | 字符替换 |
| [LC 713](https://leetcode.com/problems/subarray-product-less-than-k/) | Subarray Product Less Than K | Medium | 乘积<target缩窗 |
| [LC 992](https://leetcode.com/problems/subarrays-with-k-different-integers/) | Subarrays with K Different Integers | Hard | 恰好K个=至多K个-至多K-1个 |
| [LC 340](https://leetcode.com/problems/longest-substring-with-at-most-k-distinct-characters/) | Longest Substring with At Most K Distinct | Medium🔒 | toK个不同字符 |

---

[← 返回索引](index.md)
