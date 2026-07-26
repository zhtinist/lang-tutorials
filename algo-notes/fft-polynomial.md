# 多项式与快速傅里叶变换 · Polynomial Multiplication & FFT

> 两个 n 次多项式相乘，暴力算法是 O(n²)（每一项乘每一项）。FFT 能把它降到 O(n log n)——
> 靠的是"换一种方式表示多项式"：不用系数表示，而用"多项式在 n 个点上的取值"表示，
> 点值表示下乘法是逐点相乘 O(n)，只是"求值"和"插值"这两步的转换需要 FFT 加速。

---

## 一、系数表示 vs 点值表示

```
一个 n-1 次多项式，可以用两种等价的方式表示：

1. 系数表示：[a0, a1, ..., a(n-1)]，多项式是 a0 + a1*x + ... + a(n-1)*x^(n-1)
   两个多项式相乘（卷积）：O(n²)，每一项乘每一项再合并同类项。

2. 点值表示：[(x0,y0), (x1,y1), ..., (x(n-1),y(n-1))]，n 个不同的点能唯一确定一个 n-1 次多项式
   两个多项式相乘：只要用同一组 x 坐标分别求出两个多项式的点值，
   对应的 y 值相乘就是乘积多项式在这些点上的取值——O(n)！

问题变成：怎么快速地"系数->点值"（求值）和"点值->系数"（插值）？
朴素求值 n 个点每个 O(n)，总共 O(n²)，没有比暴力乘法快。
FFT 的贡献：如果选的 n 个点是"n 次单位复根"，求值和插值都能做到 O(n log n)。
```

---

## 二、单位复根与 DFT

```
n 次单位复根：满足 w^n = 1 的复数，一共有 n 个，均匀分布在复平面单位圆上。
w_n = e^(2πi/n)，其余的根是 w_n 的幂次：1, w_n, w_n², ..., w_n^(n-1)。

离散傅里叶变换 DFT：在这 n 个单位复根上对多项式求值，就是 DFT。
逆离散傅里叶变换 IDFT：从这 n 个点值反推回系数，本质是在 1/w_n 这组根上再做一次类似的变换（除以 n）。

为什么选单位复根：它们有"周期性"和"折半"的对称性质（w^2 是 n/2 次单位根），
这正是分治能够把 O(n²) 降到 O(n log n) 的关键——下面 FFT 部分会用到这个折半技巧。
```

---

## 三、FFT：分治求值

### 3.1 核心思路

```
把多项式 A(x) = a0 + a1*x + a2*x² + ... 按下标奇偶拆成两个约一半大小的多项式：
  A_even(x) = a0 + a2*x + a4*x² + ...   （偶数下标系数）
  A_odd(x)  = a1 + a3*x + a5*x² + ...   （奇数下标系数）
  A(x) = A_even(x²) + x * A_odd(x²)

要在 n 个单位复根 {w^0, w^1, ..., w^(n-1)} 上对 A 求值，
注意到 w^k 和 w^(k+n/2) 满足 (w^k)² = (w^(k+n/2))²（因为 w^(n/2) = -1），
也就是说，对 A_even 和 A_odd 只需要在 n/2 个点（各自的单位复根）上求值，
就能同时算出 A 在全部 n 个点上的取值——这就是分治：
  T(n) = 2T(n/2) + O(n)  =>  O(n log n)
```

### 3.2 完整实现

```python
import cmath


def fft(a: list[complex], invert: bool = False) -> list[complex]:
    """
    对系数数组 a 做 DFT（invert=False）或 IDFT（invert=True）。
    len(a) 必须是 2 的幂。递归版本，思路直接对应上面的分治推导。
    """
    n = len(a)
    if n == 1:
        return a[:]

    even = fft(a[0::2], invert)
    odd = fft(a[1::2], invert)

    result = [0j] * n
    angle_sign = -1 if not invert else 1
    for k in range(n // 2):
        angle = angle_sign * 2 * cmath.pi * k / n
        w = cmath.exp(1j * angle)  # w = e^(iθ)，第 k 个（或逆变换的共轭）单位复根
        result[k] = even[k] + w * odd[k]           # 对应 w^k
        result[k + n // 2] = even[k] - w * odd[k]  # 对应 w^(k+n/2) = -w^k

    if invert:
        result = [x / 2 for x in result]  # 每层递归除以2，log n 层合起来正好是除以 n

    return result
```

> **为什么 IDFT 每层除以 2 就够了**：IDFT 的公式是 `a_k = (1/n) * Σ y_j * w^(-jk)`，
> 总共要除以 n。这个函数是递归的，从最底层（n=1）到最顶层一共有 log₂n 层，
> 每层都把当前子问题的结果除以 2，log₂n 层各除以 2，累计起来正好是除以 n = 2^(log₂n)。

### 3.3 多项式乘法

```python
def multiply_polynomials(a: list[int], b: list[int]) -> list[int]:
    """a, b: 系数列表（低次到高次）。返回 a*b 的系数列表。"""
    result_size = 1
    while result_size < len(a) + len(b):
        result_size *= 2  # FFT 需要长度是 2 的幂，且要能装下乘积（次数=len(a)+len(b)-2）

    fa = [complex(x) for x in a] + [0j] * (result_size - len(a))
    fb = [complex(x) for x in b] + [0j] * (result_size - len(b))

    fa = fft(fa)
    fb = fft(fb)
    fc = [x * y for x, y in zip(fa, fb)]  # 点值表示下，乘法就是逐点相乘，O(n)
    fc = fft(fc, invert=True)

    result = [round(x.real) for x in fc]  # 系数是整数时，浮点误差四舍五入即可还原
    while len(result) > len(a) + len(b) - 1:
        result.pop()  # 去掉补零多出来的高次项（理论上应该是0，四舍五入后也是0）
    return result
```

### 3.4 正确性验证

```python
def multiply_naive(a: list[int], b: list[int]) -> list[int]:
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return result


import random

random.seed(0)
fail = 0
for _ in range(200):
    na, nb = random.randint(1, 20), random.randint(1, 20)
    a = [random.randint(-50, 50) for _ in range(na)]
    b = [random.randint(-50, 50) for _ in range(nb)]
    if multiply_polynomials(a, b) != multiply_naive(a, b):
        fail += 1
print(f"FFT 多项式乘法 vs 暴力乘法：200 次随机测试，不匹配 {fail} 次")

# 规模更大的例子（暴力是 O(n²)，FFT 是 O(n log n)，n=500 时差距已经很明显）
a = [random.randint(-9, 9) for _ in range(500)]
b = [random.randint(-9, 9) for _ in range(500)]
print("n=500 大规模测试一致:", multiply_polynomials(a, b) == multiply_naive(a, b))
```

---

## 四、应用：大整数乘法 / 字符串形式的数字相乘

```
把一个大整数看成一个多项式（每一位是一个系数，x=10），
"两个大整数相乘"就变成了"两个多项式相乘，再处理进位"——
用 FFT 做多项式乘法部分，可以把大整数乘法从朴素的 O(n²)（n=位数）降到 O(n log n)。
LeetCode 上 43. Multiply Strings 数据范围小（n ≤ 200），暴力 O(n²) 竖式乘法完全够用，
但如果 n 是 10^5、10^6 级别（大数库/密码学场景），FFT 乘法就是必需的优化。
```

---

## 五、复杂度总结

| 方法 | 复杂度 | 说明 |
|------|--------|------|
| 暴力多项式乘法 | O(n²) | 直接按定义展开 |
| FFT 多项式乘法 | O(n log n) | 系数->点值(FFT)->逐点相乘->点值->系数(IFFT) |
| NTT（数论变换） | O(n log n) | FFT 的整数取模版本，避免浮点误差，常用于模数下的多项式乘法 |

> 本文的递归 FFT 简单直观但有额外的列表切片开销；工程实现通常用"迭代 + 位逆序置换"版本，
> 常数因子更小，但原理跟这里的分治推导完全一样。

---

[← 返回索引](index.md)
