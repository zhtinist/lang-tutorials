# 位运算 · Bit Manipulation

> 位运算在节省空间、优化速度、状态压缩中有广泛应用。Python 的整数是任意精度的（补码表示下 `~x = -x-1`）。

---

## 一、常用位操作速查表

| 操作 | 代码 | 说明 |
|------|------|------|
| 取第 k 位 | `(n >> k) & 1` | 0-indexed |
| 设置第 k 位为 1 | `n \|= (1 << k)` | |
| 设置第 k 位为 0 | `n &= ~(1 << k)` | |
| 翻转第 k 位 | `n ^= (1 << k)` | |
| lowbit（最低位的1） | `n & -n` | 树状数组核心 |
| 去掉最低位的 1 | `n & (n - 1)` | Brian Kernighan |
| 统计 1 的个数 | `n.bit_count()` | Python 3.8+ |
| 判断 2 的幂 | `n > 0 and (n & (n - 1)) == 0` | |
| 判断奇偶 | `n & 1` | 1=奇数, 0=偶数 |
| 交换两数 | `a ^= b; b ^= a; a ^= b` | 无临时变量 |
| 取反 | `~n` | 注意是补码：~0 = -1 |
| 右移（算术/逻辑） | `n >> k` 或 `n << k` | Python 无符号右移用掩码 |

---

## 二、Brian Kernighan 算法 · [LC 191](https://leetcode.com/problems/number-of-1-bits/)

```python
def hamming_weight(n: int) -> int:
    """统计二进制中 1 的个数（汉明重量）。"""
    count = 0
    while n:
        n &= n - 1  # 每次消去最低位的 1
        count += 1
    return count

# Python 内置写法
def hamming_weight_builtin(n: int) -> int:
    return n.bit_count()
```

---

## 三、异或的妙用

### 3.1 只出现一次的数字 · [LC 136](https://leetcode.com/problems/single-number/)

```python
def single_number(nums: list[int]) -> int:
    """所有数字都出现两次，找出只出现一次的。"""
    ans = 0
    for v in nums:
        ans ^= v
    return ans
```

### 3.2 只出现一次的数字 II · [LC 137](https://leetcode.com/problems/single-number-ii/)

```python
def single_number_ii(nums: list[int]) -> int:
    """
    所有数字出现 3 次，找出只出现 1 次的。
    用两个变量模拟三进制计数器。
    """
    ones = twos = 0
    for v in nums:
        ones = (ones ^ v) & ~twos
        twos = (twos ^ v) & ~ones
    return ones
```

### 3.3 只出现一次的数字 III · [LC 260](https://leetcode.com/problems/single-number-iii/)

```python
def single_number_iii(nums: list[int]) -> list[int]:
    """
    有两个数字各出现 1 次，其他出现 2 次，找出这两个数字。
    1. XOR 所有数 → 两个目标值的 XOR
    2. 取 XOR 的最低位 1 → 区分两组
    3. 每组内 XOR 得到两个数
    """
    xor_all = 0
    for v in nums:
        xor_all ^= v

    # 找到区分位（最低位的 1）
    diff_bit = xor_all & -xor_all

    a = b = 0
    for v in nums:
        if v & diff_bit:
            a ^= v
        else:
            b ^= v

    return [a, b]
```

### 3.4 丢失的数字 · [LC 268](https://leetcode.com/problems/missing-number/)

```python
def missing_number(nums: list[int]) -> int:
    """0..n 中少了一个数。XOR 索引和值。"""
    ans = len(nums)
    for i, v in enumerate(nums):
        ans ^= i ^ v
    return ans
```

---

## 四、枚举子集

```python
def enumerate_subsets(mask: int) -> None:
    """枚举 mask 的所有非空子集（O(3^n) 枚举所有子集的子集）。"""
    sub = mask
    while sub:
        # 处理子集 sub
        sub = (sub - 1) & mask
```

### [LC 78](https://leetcode.com/problems/subsets/) 求所有子集（位运算版）

```python
def subsets_bitmask(nums: list[int]) -> list[list[int]]:
    """用位运算枚举子集，O(2^n × n)。"""
    n = len(nums)
    ans: list[list[int]] = []
    for mask in range(1 << n):
        subset = [nums[i] for i in range(n) if (mask >> i) & 1]
        ans.append(subset)
    return ans
```

---

## 五、加法器（位运算模拟）

```python
def get_sum(a: int, b: int) -> int:
    """
    [LC 371](https://leetcode.com/problems/sum-of-two-integers/) 不用 +- 实现加法。
    a ^ b = 无进位的加法
    a & b << 1 = 进位
    Python 中需要考虑 32 位截断。
    """
    MASK = 0xFFFFFFFF
    MAX_INT = 0x7FFFFFFF

    while b != 0:
        a, b = (a ^ b) & MASK, ((a & b) << 1) & MASK

    return a if a <= MAX_INT else ~(a ^ MASK)
```

---

## 六、数字范围按位与 · [LC 201](https://leetcode.com/problems/bitwise-and-of-numbers-range/)

```python
def range_bitwise_and(left: int, right: int) -> int:
    """
    [left, right] 中所有数字的按位与。
    等价于找 left 和 right 的最长公共前缀。
    """
    shift = 0
    while left < right:
        left >>= 1
        right >>= 1
        shift += 1
    return left << shift
```

---

## 七、总结

| 场景 | 技巧 |
|------|------|
| 统计 1 的个数 | `n & (n-1)` 消除最低位 1 |
| 找到唯一的单个数字 | XOR |
| 判断 2 的幂 | `n & (n-1) == 0` |
| 获取/设置/清除 某一位 | `>>`, `\|`, `& ~` |
| lowbit | `n & -n` |
| 子集枚举 | `sub = (sub-1) & mask` |

---

## 八、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 191](https://leetcode.com/problems/number-of-1-bits/) | Number of 1 Bits | Easy | Brian Kernighan |
| [LC 231](https://leetcode.com/problems/power-of-two/) | Power of Two | Easy | n&(n-1) |
| [LC 136](https://leetcode.com/problems/single-number/) | Single Number | Easy | XOR |
| [LC 137](https://leetcode.com/problems/single-number-ii/) | Single Number II | Medium | 三进制模拟 |
| [LC 260](https://leetcode.com/problems/single-number-iii/) | Single Number III | Medium | XOR分组 |
| [LC 268](https://leetcode.com/problems/missing-number/) | Missing Number | Easy | XOR索引+值 |
| [LC 201](https://leetcode.com/problems/bitwise-and-of-numbers-range/) | Bitwise AND of Numbers Range | Medium | 公共前缀 |
| [LC 371](https://leetcode.com/problems/sum-of-two-integers/) | Sum of Two Integers | Medium | 位运算加法 |
| [LC 78](https://leetcode.com/problems/subsets/) | Subsets | Medium | 位枚举子集 |
| [LC 190](https://leetcode.com/problems/reverse-bits/) | Reverse Bits | Easy | 位翻转 |
| [LC 338](https://leetcode.com/problems/counting-bits/) | Counting Bits | Easy | DP+位运算 |

---

[← 返回索引](index.md)
