# 复杂度分析实战 · Complexity Analysis in Practice

> Big-O 只告诉你增长趋势，不告诉你**会不会超时**。判断超时需要结合数据规模 n 和真实的每秒操作数。
> 递归算法的时间复杂度看"调用次数"，空间复杂度看"调用栈深度"——这两者不是一回事，容易搞混。

---

## 一、O(n) 的算法也会超时：n 到底能有多大

### 1.1 核心思想

```
"时间复杂度是 O(n)"不等于"一定跑得很快"。
LeetCode/OJ 的时限通常是 1~2 秒，实际能跑多少次基本操作，
取决于语言、硬件、以及"一次操作"到底有多重。

粗略经验值（现代 CPU，1 秒时限）：
  O(n)       能处理到 n ~ 10^8~10^9   （简单操作，如加法/比较）
  O(n log n) 能处理到 n ~ 10^6~10^7
  O(n²)      能处理到 n ~ 10^4
  O(n³)      能处理到 n ~ 500
  O(2^n)     能处理到 n ~ 20~25
  O(n!)      能处理到 n ~ 10~11

这不是理论值，是"拿秒表实测"得到的数量级估计——
下面这段代码你可以直接跑一下，在自己的机器上量出真实数字。
```

### 1.2 实测代码

```python
import time


def benchmark_linear(n: int) -> float:
    """O(n)：单层循环。"""
    start = time.perf_counter()
    total = 0
    for i in range(n):
        total += i
    return time.perf_counter() - start


def benchmark_quadratic(n: int) -> float:
    """O(n²)：双层循环。"""
    start = time.perf_counter()
    total = 0
    for i in range(n):
        for j in range(n):
            total += 1
    return time.perf_counter() - start


if __name__ == "__main__":
    n1 = 100_000_000
    t1 = benchmark_linear(n1)
    print(f"O(n)  n={n1:,}: {t1:.3f}s -> {n1/t1:.2e} 次/秒")

    n2 = 5_000
    t2 = benchmark_quadratic(n2)
    ops2 = n2 * n2
    print(f"O(n²) n={n2:,} ({ops2:.2e} 次操作): {t2:.3f}s -> {ops2/t2:.2e} 次/秒")
```

在一台普通笔记本上跑出来大致是：

```
O(n)  n=100,000,000: 1.8s  -> 5.6e+07 次/秒
O(n²) n=5,000 (2.5e+07 次操作): 0.4s -> 6.6e+07 次/秒
```

**关键结论**：Python 解释执行，每次循环迭代的开销比 C++ 编译后的机器码大 10~50 倍，所以 Python 的"每秒操作数"比很多复杂度分析文章里给的 C++ 经验值（~5×10^8/秒）低一个数量级。**这不是坏事，而是提醒你：Big-O 一样的两段代码，语言和常数因子能决定它在 OJ 上是 AC 还是 TLE。**

### 1.3 怎么用这个估算法

```
拿到一道题，先看 n 的范围（题目会给），反推允许的复杂度：

  n ≤ 10        -> O(n!) 或 O(2^n × n) 都可以（全排列/位压缩枚举）
  n ≤ 20~25     -> O(2^n) 可以（状压 DP、子集枚举）
  n ≤ 500       -> O(n³) 可以
  n ≤ 5000      -> O(n²) 可以，O(n² log n) 勉强
  n ≤ 10^5~10^6 -> O(n log n) 需要，O(n²) 会超时
  n ≤ 10^8      -> 只能 O(n) 甚至 O(1)

看到 n = 10^5 还想用双重循环暴力，基本可以直接排除这个思路了——
这比"先写出来跑一下 TLE 再优化"要快得多。
```

---

## 二、递归算法的时间与空间复杂度

### 2.1 核心思想

```
时间复杂度：整棵递归树一共"访问"了多少个节点（调用了多少次函数）。
空间复杂度：调用栈同时存在的最大帧数 = 递归调用的最大深度。

这两者不同步！
一个函数可能调用次数是指数级（时间 O(2^n)），
但因为是"一条链往下走到底才回溯"，同一时刻栈上只有线性个帧（空间 O(n)）。
```

### 2.2 例子：暴力斐波那契 —— 时间 O(2ⁿ)，空间只有 O(n)

```python
call_count = 0


def fib_naive(n: int) -> int:
    """
    时间 O(2^n)：递归树有约 2^n 个节点（每次分叉出 2 个子调用）。
    空间 O(n)：虽然调用了指数多次，但任意时刻栈上最多只有 n 层
              （因为是深度优先，一路递归到底才开始返回，不会同时存在两条分支）。
    """
    global call_count
    call_count += 1
    if n <= 1:
        return n
    return fib_naive(n - 1) + fib_naive(n - 2)


fib_naive(20)
print(f"fib_naive(20) 一共调用了 {call_count} 次（时间 O(2^n)）")
print("但任意时刻的调用栈深度不会超过 20（空间 O(n)）")
```

```
fib_naive(20) 一共调用了 21891 次（时间 O(2^n)）
但任意时刻的调用栈深度不会超过 20（空间 O(n)）
```

### 2.3 例子：递归二分查找 —— 时间 O(log n)，空间 O(log n)（但要看传参方式）

```python
def binary_search(arr: list[int], target: int, lo: int, hi: int) -> int:
    """
    时间 O(log n)：每次递归区间减半，最多 log n 层。
    空间 O(log n)：调用栈深度 = 递归层数 = log n。

    ⚠️ 前提：arr 是按引用传递（Python/Java/Go 都是——传的是同一个列表对象）。
    如果某种语言/写法在每次递归时都拷贝一份 arr[lo:hi]（切片产生新列表），
    那么空间会退化成 O(n log n)：每层额外多花 O(该层区间长度) 的拷贝空间，
    n/2 + n/4 + ... + 1 ≈ n，再乘上 log n 层就是 O(n log n)。
    """
    if lo > hi:
        return -1
    mid = (lo + hi) // 2
    if arr[mid] == target:
        return mid
    elif arr[mid] < target:
        return binary_search(arr, target, mid + 1, hi)
    else:
        return binary_search(arr, target, lo, mid - 1)


arr = list(range(1_000_000))
print(binary_search(arr, 999_999, 0, len(arr) - 1))  # 999999，递归深度约 log2(10^6) ≈ 20
```

> **常见坑**：写递归函数时用 `arr[lo:hi]` 切片传参（而不是传 `lo, hi` 两个下标），
> 时间复杂度不变，但空间复杂度会从 O(log n) 劣化成 O(n log n)——因为每层都在拷贝数组。
> 这也是为什么 `binary-search.md` 里的实现都传 `left, right` 下标而不是切片。

### 2.4 空间复杂度速查表

| 递归模式 | 时间复杂度 | 空间复杂度（栈深度） |
|----------|-----------|---------------------|
| 单链递归（如阶乘、链表反转） | O(n) | O(n) |
| 二分递归（如二分查找、快速幂） | O(log n) | O(log n) |
| 二叉树递归（每个节点访问一次） | O(n) | O(树高)，最坏 O(n)，平衡树 O(log n) |
| 暴力二叉递归（无剪枝的斐波那契/子集枚举） | O(2^n) | O(n)（树的深度，不是节点数） |
| 回溯（排列/组合） | O(n! ) 或 O(2^n) | O(n)（路径长度，即递归深度） |

> 一句话记忆：**空间复杂度只看"最深一条路径走了多少层"，时间复杂度看"一共走了多少个节点"。**

---

[← 返回索引](index.md)
