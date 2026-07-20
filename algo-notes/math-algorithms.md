# 数学算法 · Math Algorithms

> 面试常见：**快速幂、GCD/LCM、筛法求素数、模运算**。代码简短，思路巧。

---

## 一、快速幂

### 1.1 Pow(x, n) · [LC 50](https://leetcode.com/problems/powx-n/)

```python
def my_pow(x: float, n: int) -> float:
    """
    快速幂 (快速幂取模) — 二分思想。
    x^n = x^(n/2) × x^(n/2)（n 偶）
    x^n = x × x^(n/2) × x^(n/2)（n 奇）
    O(log n)
    """
    if n == 0:
        return 1.0
    if n < 0:
        x = 1 / x
        n = -n

    ans = 1.0
    while n:
        if n & 1:  # 奇数
            ans *= x
        x *= x
        n >>= 1

    return ans
```

### 1.2 超级次方 · [LC 372](https://leetcode.com/problems/super-pow/)

```python
def super_pow(a: int, b: list[int]) -> int:
    """
    a^b mod 1337，其中 b 是一个非常大的数组。
    利用性质：
    (a×b) % k = ((a%k) × (b%k)) % k
    a^[1,2,3] = (a^[1,2])^10 × a^3
    """
    MOD = 1337

    def pow_mod(x: int, n: int) -> int:
        ans = 1
        x %= MOD
        for _ in range(n):
            ans = (ans * x) % MOD
        return ans

    if not b:
        return 1
    last = b.pop()
    return pow_mod(super_pow(a, b), 10) * pow_mod(a, last) % MOD
```

---

## 二、最大公约数与最小公倍数

```python
import math


def gcd(a: int, b: int) -> int:
    """
    欧几里得算法（辗转相除法）。
    gcd(a, b) = gcd(b, a % b)
    当 b=0 时，a 就是最大公约数。
    """
    while b:
        a, b = b, a % b
    return a


def gcd_recursive(a: int, b: int) -> int:
    return a if b == 0 else gcd_recursive(b, a % b)


def lcm(a: int, b: int) -> int:
    """最小公倍数 = a × b / gcd(a, b)"""
    return a // gcd(a, b) * b  # 先除后乘以防溢出


# Python 3.9+ 内置
# math.gcd(a, b)
# math.lcm(a, b)
```

---

## 三、筛法求素数 · [LC 204](https://leetcode.com/problems/count-primes/)

### 3.1 埃氏筛 (Sieve of Eratosthenes) O(n log log n)

```python
def count_primes_eratosthenes(n: int) -> int:
    """统计 < n 的素数个数。"""
    if n < 2:
        return 0

    is_prime = [True] * n
    is_prime[0] = is_prime[1] = False

    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            # 从 i*i 开始标记（更小的倍数已经被其他素数标记）
            for j in range(i * i, n, i):
                is_prime[j] = False

    return sum(is_prime)
```

### 3.2 欧拉筛（线性筛）O(n)

```python
def count_primes_euler(n: int) -> int:
    """线性筛：每个合数只被它的最小质因子筛掉一次。"""
    if n < 2:
        return 0

    is_prime = [True] * n
    primes: list[int] = []
    is_prime[0] = is_prime[1] = False

    for i in range(2, n):
        if is_prime[i]:
            primes.append(i)
        for p in primes:
            if i * p >= n:
                break
            is_prime[i * p] = False
            if i % p == 0:
                break  # p 是 i 的最小质因子，后面的质数更大的 p 会重复筛

    return len(primes)
```

---

## 四、丑数系列

### 4.1 判断丑数 · [LC 263](https://leetcode.com/problems/ugly-number/)

```python
def is_ugly(n: int) -> bool:
    """质因子只包含 2, 3, 5。"""
    if n <= 0:
        return False
    for factor in (2, 3, 5):
        while n % factor == 0:
            n //= factor
    return n == 1
```

### 4.2 第 N 个丑数 · [LC 264](https://leetcode.com/problems/ugly-number-ii/)

```python
def nth_ugly_number(n: int) -> int:
    """三指针动态规划。三个子问题分别乘2/3/5。"""
    dp = [1] * n
    p2 = p3 = p5 = 0

    for i in range(1, n):
        n2 = dp[p2] * 2
        n3 = dp[p3] * 3
        n5 = dp[p5] * 5
        dp[i] = min(n2, n3, n5)

        if dp[i] == n2:
            p2 += 1
        if dp[i] == n3:
            p3 += 1
        if dp[i] == n5:
            p5 += 1

    return dp[-1]
```

### 4.3 超级丑数 · [LC 313](https://leetcode.com/problems/super-ugly-number/)

```python
import heapq


def nth_super_ugly_number(n: int, primes: list[int]) -> int:
    """K 个质因子版本。堆解法。"""
    heap = [(p, 0, p) for p in primes]  # (value, idx, prime)
    heapq.heapify(heap)

    dp = [1] * n
    for i in range(1, n):
        dp[i] = heap[0][0]
        while heap[0][0] == dp[i]:
            val, idx, p = heapq.heappop(heap)
            heapq.heappush(heap, (p * dp[idx + 1], idx + 1, p))

    return dp[-1]
```

---

## 五、阶乘后的零 · [LC 172](https://leetcode.com/problems/factorial-trailing-zeroes/)

```python
def trailing_zeroes(n: int) -> int:
    """
    n! 末尾有多少个零。
    零 = 2×5，2 比 5 多，所以只计数 5 的个数。
    """
    count = 0
    while n:
        n //= 5
        count += n
    return count
```

---

## 六、模运算性质

```python
MOD = 10**9 + 7  # 常见模数

# 加法
(a + b) % MOD

# 乘法
(a * b) % MOD

# 除法（乘逆元）- 使用费马小定理（MOD 为质数时）
def mod_inverse(a: int) -> int:
    """a 关于 MOD 的乘法逆元。MOD 必须是质数。"""
    return pow(a, MOD - 2, MOD)

def mod_divide(a: int, b: int) -> int:
    """(a / b) % MOD"""
    return a * mod_inverse(b) % MOD

# 减法
def mod_sub(a: int, b: int) -> int:
    return (a - b + MOD) % MOD
```

---

## 七、卡特兰数

```python
def catalan(n: int) -> int:
    """第 n 个卡特兰数。C(2n, n) / (n+1)"""
    from math import comb
    return comb(2 * n, n) // (n + 1)


def catalan_dp(n: int) -> list[int]:
    """DP 求前 n 个卡特兰数。"""
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        dp[i] = dp[i - 1] * 2 * (2 * i - 1) // (i + 1)
    return dp
```

---

## 八、总结

| 问题 | 方法 | 复杂度 |
|------|------|--------|
| 快速幂 | 二分指数 | O(log n) |
| GCD | 欧几里得算法 | O(log min(a,b)) |
| LCM | a×b / gcd | O(log min(a,b)) |
| 素数筛选 | 埃氏筛 / 欧拉筛 | O(n log log n) / O(n) |
| 丑数 | 三指针DP / 堆 | O(n) / O(n log k) |
| 模运算 | 乘逆元代替除法 | O(log MOD) |

---

## 九、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 50](https://leetcode.com/problems/powx-n/) | Pow(x, n) | Medium | 快速幂 |
| [LC 372](https://leetcode.com/problems/super-pow/) | Super Pow | Medium | 模运算+幂 |
| [LC 204](https://leetcode.com/problems/count-primes/) | Count Primes | Medium | 埃氏筛 |
| [LC 263](https://leetcode.com/problems/ugly-number/) | Ugly Number | Easy | 因式分解 |
| [LC 264](https://leetcode.com/problems/ugly-number-ii/) | Ugly Number II | Medium | 三指针DP |
| [LC 313](https://leetcode.com/problems/super-ugly-number/) | Super Ugly Number | Medium | K个质因子的丑数 |
| [LC 172](https://leetcode.com/problems/factorial-trailing-zeroes/) | Factorial Trailing Zeroes | Medium | 因子计数 |
| [LC 793](https://leetcode.com/problems/preimage-size-of-factorial-zeroes-function/) | Preimage of Factorial Zeroes | Hard | 二分+阶乘零 |
| [LC 96](https://leetcode.com/problems/unique-binary-search-trees/) | Unique Binary Search Trees | Medium | 卡特兰数 |

---

[← 返回索引](index.md)
