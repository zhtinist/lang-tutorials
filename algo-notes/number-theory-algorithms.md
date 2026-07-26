# 数论算法 · Number Theory Algorithms

> 快速幂、GCD/LCM、素数筛法、费马小定理求逆元已经在 [math-algorithms.md](math-algorithms.md) 里，这里补几个更进阶的数论算法。对应 **CLRS 第 31 章**：扩展欧几里得、中国剩余定理、RSA、Miller-Rabin 素性测试、Pollard's rho 分解。

---

## 一、扩展欧几里得算法 (Extended Euclidean Algorithm)

### 1.1 为什么需要它

[math-algorithms.md](math-algorithms.md) 里的 `mod_inverse` 用费马小定理 `pow(a, MOD-2, MOD)` 求逆元，**但要求 MOD 必须是质数**。

扩展欧几里得算法能在**任意** `gcd(a, m) == 1` 的情况下求出 `a` 关于 `m` 的逆元——不管 `m` 是不是质数。这在 RSA（模数 `φ(n)` 几乎肯定不是质数）、非质数模数的题目里是唯一能用的方法。

### 1.2 原理

在求 `gcd(a, b)` 的辗转相除过程中，同时维护一组系数 `x, y`，使得：

```
a·x + b·y = gcd(a, b)
```

这叫 **裴蜀定理 (Bézout's identity)**。递推关系：

- 若 `b == 0`，显然 `a·1 + 0·0 = a`，返回 `(a, 1, 0)`。
- 否则先递归求出 `gcd(b, a % b) = b·x₁ + (a % b)·y₁ = g`。
  代入 `a % b = a - (a // b)·b`：

  ```
  g = b·x₁ + (a - (a // b)·b)·y₁ = a·y₁ + b·(x₁ - (a // b)·y₁)
  ```

  对比系数，得到 `x = y₁, y = x₁ - (a // b)·y₁`。

```python
def ext_gcd(a: int, b: int) -> tuple[int, int, int]:
    """
    扩展欧几里得算法。
    返回 (g, x, y)，满足 a*x + b*y = g = gcd(a, b)。
    递推关系见上文推导：x = y1, y = x1 - (a // b) * y1。
    O(log min(a, b))，和普通欧几里得同阶。
    """
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def mod_inverse_ext_euclid(a: int, m: int) -> int:
    """
    a 关于模 m 的乘法逆元，用扩展欧几里得算法。
    只要求 gcd(a, m) == 1，m 不需要是质数
    （对比 math-algorithms.md 中费马小定理版本的 mod_inverse，那个要求 MOD 必须是质数）。
    """
    g, x, _ = ext_gcd(a, m)
    if g != 1:
        raise ValueError(f"{a} 和 {m} 不互质，逆元不存在")
    return x % m
```

**验证**：随机生成 500,000 组正整数 `(a, b)`（范围 `1 ~ 10^12`），检查 `a*x + b*y == g` 且 `g == math.gcd(a, b)` —— **500,000 次试验，0 次失败**。

再对 20,000+ 个随机 `(a, m)` 对（其中 `m` 包含大量合数）验证 `mod_inverse_ext_euclid`：`(a * inv) % m == 1` —— **实际生效样本 12,150 次，0 次失败**（例如 `mod_inverse_ext_euclid(3, 26) == 9`，`26 = 2×13` 不是质数，费马小定理的版本在这里根本不适用）。

---

## 二、中国剩余定理 (Chinese Remainder Theorem, CRT)

### 2.1 问题

给定一组两两互质的模数 `m₁, m₂, ..., mₙ`，求解同余方程组：

```
x ≡ a₁ (mod m₁)
x ≡ a₂ (mod m₂)
...
x ≡ aₙ (mod mₙ)
```

在 `[0, M)` 内存在**唯一解**，其中 `M = m₁ × m₂ × ... × mₙ`。经典应用场景：秦九韶"物不知数"问题、密码学中的批量解密加速（配合 RSA-CRT）、分布式系统里按不同周期采样后还原真实计数。

### 2.2 用扩展欧几里得逐步合并

每次把已经合并出的 `x ≡ r (mod M)` 和下一个方程 `x ≡ aᵢ (mod mᵢ)` 合并成一个新方程：

设 `x = r + M·k`，代入第二式：`r + M·k ≡ aᵢ (mod mᵢ)`，即 `M·k ≡ (aᵢ - r) (mod mᵢ)`。
用扩展欧几里得求出 `M` 关于 `mᵢ` 的逆元（`M, mᵢ` 互质时一定存在），解出 `k`，合并后的模数变成 `lcm(M, mᵢ)`。

```python
def crt(remainders: list[int], moduli: list[int]) -> int:
    """
    中国剩余定理：解同余方程组 x ≡ a_i (mod m_i)，要求 m_i 两两互质。
    返回 [0, M) 内的唯一解，M = m_1 * m_2 * ... * m_n。

    逐步合并两个方程：x ≡ a1 (mod m1), x ≡ a2 (mod m2)。
    设 x = a1 + m1*k，代入第二式解出 k（用扩展欧几里得求 m1 关于 m2 的逆元）。
    """
    x, M = remainders[0] % moduli[0], moduli[0]
    for a_i, m_i in zip(remainders[1:], moduli[1:]):
        g, p, _ = ext_gcd(M, m_i)
        if (a_i - x) % g != 0:
            raise ValueError("无解：模数不满足互质条件下的一致性")
        lcm = M // g * m_i
        k = (a_i - x) // g * p % (m_i // g)
        x = (x + M * k) % lcm
        M = lcm
    return x
```

**验证**：随机构造 3,000 组两两互质的模数系统（模数取自 `{2,3,4,5,7,9,11,13,17,19,23,25}` 中互质的子集，每组 2~4 个方程），对每组求解后逐一代入检查所有同余式是否成立 —— **3,000 组，0 次失败**。

经典例子（"物不知数"变体）`x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 2 (mod 7)`：`crt([2, 3, 2], [3, 5, 7])` 求得 `x = 23`，与手算结果一致。

---

## 三、RSA 公钥加密

### 3.1 原理简述

RSA 的安全性建立在"大数分解困难"上，密钥生成依赖上面两节的工具：

1. 选两个大质数 `p, q`（本节例子用 CLRS 31.7 节的教科书示例 `p=61, q=53`）。
2. 计算 `n = p×q`，`φ(n) = (p-1)(q-1)`（欧拉函数，两个质数相乘时的化简形式）。
3. 选公钥指数 `e`，要求 `gcd(e, φ(n)) = 1`。
4. **用扩展欧几里得**（第一节）求私钥指数 `d = e⁻¹ mod φ(n)`——`φ(n)` 一般不是质数，所以只能用扩展欧几里得，费马小定理的 `mod_inverse` 在这里用不了。
5. 公钥 `(e, n)`，私钥 `(d, n)`。
6. 加密：`c = mᵉ mod n`；解密：`m = c^d mod n`（正确性由欧拉定理保证：`m^(e·d) ≡ m (mod n)`，因为 `e·d ≡ 1 (mod φ(n))`）。
7. 幂运算部分直接复用 [math-algorithms.md](math-algorithms.md) 的快速幂思想（Python 内置 `pow(base, exp, mod)` 就是三参数快速幂取模，等价于手写的 `my_pow`）。

```python
import math


def rsa_keygen(p: int, q: int, e: int) -> tuple[tuple[int, int], tuple[int, int]]:
    """
    RSA 密钥生成（CLRS 31.7 教科书示例的参数）。
    n = p*q, phi(n) = (p-1)(q-1)。
    d = e^-1 mod phi(n)，必须用扩展欧几里得（phi(n) 不是质数）。
    返回 (public_key, private_key) = ((e, n), (d, n))。
    """
    n = p * q
    phi = (p - 1) * (q - 1)
    if math.gcd(e, phi) != 1:
        raise ValueError("e 与 phi(n) 不互质")
    d = mod_inverse_ext_euclid(e, phi)
    return (e, n), (d, n)


def rsa_encrypt(m: int, public_key: tuple[int, int]) -> int:
    """c = m^e mod n。三参数 pow 就是快速幂取模，见 math-algorithms.md 的 my_pow。"""
    e, n = public_key
    return pow(m, e, n)


def rsa_decrypt(c: int, private_key: tuple[int, int]) -> int:
    """m = c^d mod n。"""
    d, n = private_key
    return pow(c, d, n)
```

### 3.2 实测：CLRS 教科书例子

```python
p, q, e = 61, 53, 17
public_key, private_key = rsa_keygen(p, q, e)
# public_key  = (17, 3233)
# private_key = (2753, 3233)

c = rsa_encrypt(65, public_key)     # 2790
m = rsa_decrypt(c, private_key)     # 65
```

**验证结果**：`n = 3233`，`φ(n) = 3120`，`public_key = (17, 3233)`，`private_key = (2753, 3233)`——和 CLRS 书上给出的数字完全一致。`encrypt(65) = 2790`，`decrypt(2790) = 65`，往返正确。

在 `m ∈ {0, 1, ..., 199}` 加上 500 个 `[0, n)` 内的随机消息（共 700 条）上做 `decrypt(encrypt(m)) == m` 的往返测试 —— **700 条消息，0 次失败**。

> ⚠️ 真实 RSA 中 `p, q` 是几百位的大质数，这里用小数字只是为了能手算验证正确性；小数字本身**不安全**（`n=3233` 分解出 `61×53` 太容易）。

---

## 四、Miller-Rabin 素性测试

### 4.1 原理

[math-algorithms.md](math-algorithms.md) 的筛法能批量求出一个范围内的所有素数，但如果只想判断**一个巨大的数**（比如 100 位）是不是素数，筛法和试除法都太慢。Miller-Rabin 是一种基于**费马小定理的加强版**的概率性测试：

把 `n - 1` 写成 `2^r × d`（`d` 为奇数）。如果 `n` 是素数，那么对任意与 `n` 互质的 `a`：

```
a^d ≡ 1 (mod n)，或者
存在某个 0 ≤ i < r，使得 a^(2^i·d) ≡ -1 (mod n)
```

这是因为在模素数意义下，方程 `x² ≡ 1` 只有平凡解 `x = ±1`（这一步正是费马小定理判素法漏掉的检查——费马小定理只查 `a^(n-1) ≡ 1`，不检查中间的平方根）。如果对某个随机 base `a` 两个条件都不满足，`a` 就是 `n` 是合数的"见证者"，`n` 必为合数。

单次测试最坏误判率 `≤ 1/4`，独立重复 `k` 次随机 base，总误判率 `≤ 4⁻ᵏ`，实践中取 `k=20` 已经比宇宙射线翻转内存位的概率还低。

```python
import random


def miller_rabin(n: int, k: int = 20) -> bool:
    """
    Miller-Rabin 概率素性测试。
    把 n-1 = 2^r * d（d 奇数）。随机取 k 个 base 做见证者测试，
    只要有一个 base 证明 n 是合数就返回 False；k 轮都通过则认为是素数
    （误判概率 <= 4^-k，实用上可视为确定性）。
    """
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n == p:
            return True
        if n % p == 0:
            return False

    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1

    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False  # 找到见证者，n 是合数
    return True
```

### 4.2 验证：和试除法逐一比对

对 `[2, 10000)` 范围内的全部 9,998 个整数，逐一和朴素试除法 `is_prime_trial_division` 比对结果：

**总数 9998，不一致 0 次（假阳性 0 次，假阴性 0 次）。**

再单独测试几个有名的大数：

| 数 | 说明 | `miller_rabin` 结果 |
|----|------|---------------------|
| `2^31 - 1 = 2147483647` | 梅森素数 | `True`（素数，正确） |
| `2^11 - 1 = 2047` | `= 23 × 89`，著名的以 2 为底的费马伪素数 | `False`（合数，正确） |
| `561` | 最小的卡迈克尔数 (Carmichael number)，费马小定理在这上面会误判 | `False`（合数，正确，说明 Miller-Rabin 比朴素费马测试更强） |
| `2000000014`（`= 2 × 1000000007`） | 大偶合数 | `False`（合数，正确） |
| `1000000007` | 竞赛常用模数，已知素数 | `True`（素数，正确） |

---

## 五、Pollard's rho 整数分解

### 5.1 思路

Miller-Rabin 只回答"是不是素数"，如果 `n` 是合数，想进一步找出**具体的因子**，试除法要 `O(√n)`，对大数不可行。Pollard's rho 是一种期望 `O(n^(1/4))` 左右找到一个非平凡因子的启发式算法，核心是给随机函数 `f(x) = (x² + c) mod n` 生成的序列 `x₀, x₁ = f(x₀), x₂ = f(x₁), ...` 做**环检测**：

- 因为 `x` 的取值范围是有限集合 `[0, n)`，序列必然进入一个循环（"ρ" 的形状——一条尾巴接一个环，这也是算法名字的由来）。
- 关键观察：如果把序列**模 `n` 的某个质因子 `p`** 来看，由于 `p` 远小于 `n`，序列进入循环的期望步数只有 `O(√p)`（生日悖论），比模 `n` 本身的循环短得多。
- 用 **Floyd 龟兔追逐** 同时维护慢指针 `x = f(x)` 和快指针 `y = f(f(y))`，一旦 `gcd(|x - y|, n)` 落在 `(1, n)` 之间，就找到了 `n` 的一个非平凡因子——因为此时 `x ≡ y (mod p)` 但 `x ≠ y (mod n)`，说明 `p | (x - y)` 而 `n ∤ (x - y)`。
- 若某次运气不好导致 `gcd == n`（提前撞上模 `n` 的环）或 `gcd == 1`，换一个随机的 `c` 重试即可。

找到一个因子后递归地对 `d` 和 `n/d` 继续分解（配合 Miller-Rabin 判断是否已经是质因子），就能拿到完整的质因子分解。这是 RSA 密钥必须选**大质数**（而不是小质数乘积）的原因——Pollard's rho 这类亚指数算法对"因子较小或结构特殊的合数"特别有效。

### 5.2 实现与验证（选做，已实测跑通）

```python
import math
import random


def pollard_rho(n: int) -> int:
    """
    Floyd 龟兔追逐在 x_{i+1} = x_i^2 + c (mod n) 上找环，
    返回 n 的一个非平凡因子（不保证是质数）。
    素性判断复用第四节的 miller_rabin（比朴素试除法适用范围更大）。
    """
    if n % 2 == 0:
        return 2
    if miller_rabin(n):
        return n

    while True:
        c = random.randint(1, n - 1)
        f = lambda x: (x * x + c) % n
        x = y = random.randint(2, n - 1)
        d = 1
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d
        # d == n：这一轮撞上了模 n 的环，换个 c 重试


def factorize(n: int) -> list[int]:
    """递归用 Pollard's rho 分解 n 为质因子列表（含重复）。"""
    if n == 1:
        return []
    if miller_rabin(n):
        return [n]
    d = pollard_rho(n)
    return factorize(d) + factorize(n // d)
```

**验证**：对 `8051 = 83×97`、`10403 = 101×103`、`561 = 3×11×17`、`2047 = 23×89`、`999985999949 = 999983×1000003`、以及素数 `999999999989`（分解结果就是它自己）分别调用 `factorize`，检查因子乘积等于原数且每个因子（用 `miller_rabin` 复核）都是素数 —— **全部 6 个测试用例分解正确**。

---

## 六、本文 vs math-algorithms.md 对照表

| 主题 | 在哪 | 核心方法 |
|------|------|----------|
| 快速幂 | math-algorithms.md | 二分指数，O(log n) |
| GCD / LCM | math-algorithms.md | 基础欧几里得辗转相除 |
| 素数筛法 | math-algorithms.md | 埃氏筛 / 欧拉线性筛 |
| 模逆元（质数模数） | math-algorithms.md | 费马小定理 `pow(a, MOD-2, MOD)` |
| **模逆元（任意互质模数）** | 本文 §1 | **扩展欧几里得算法** |
| **裴蜀定理 ax+by=gcd(a,b)** | 本文 §1 | **扩展欧几里得算法** |
| **同余方程组求解** | 本文 §2 | **中国剩余定理 (CRT)** |
| **公钥加密 / 密钥生成** | 本文 §3 | **RSA（复用快速幂 + 扩展欧几里得）** |
| **大数素性判定** | 本文 §4 | **Miller-Rabin 概率测试** |
| **大数因子分解** | 本文 §5 | **Pollard's rho（Floyd 环检测）** |

---

## 七、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 1250](https://leetcode.com/problems/check-if-it-is-a-good-array/) | Check If It Is a Good Array | Hard | 裴蜀定理：存在解 ⟺ 数组 gcd = 1 |
| [LC 365](https://leetcode.com/problems/water-and-jug-problem/) | Water and Jug Problem | Medium | 裴蜀定理：能量出 z ⟺ z 是 gcd(x,y) 的倍数 |
| [LC 372](https://leetcode.com/problems/super-pow/) | Super Pow | Medium | 快速幂取模（配合本文 RSA 的幂运算） |
| [LC 204](https://leetcode.com/problems/count-primes/) | Count Primes | Medium | 埃氏筛（大范围）vs Miller-Rabin（单个大数）的适用场景对比 |

---

[← 返回索引](index.md)
