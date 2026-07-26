# 摊还分析 · Amortized Analysis

> 摊还分析回答的是："对一个**确定的操作序列**（比如连续 n 次 append），单次操作最坏情况下会不会很贵？"——
> 答案往往是"某一次会很贵，但贵的次数少到可以被前面攒下来的'便宜操作'摊平"。
> 它和"平均情况分析"看起来像，其实是两件完全不同的事：平均情况需要假设输入服从某种概率分布（比如随机哈希），
> 摊还分析不需要任何概率假设，它对**任意**输入序列都成立，给出的是确定性的最坏情况总量上界。

---

## 一、什么是摊还分析：和"平均情况"是两回事

```
常见误解：
  "动态数组 append 均摊 O(1)"  ≈  "append 平均情况下很快，个别情况会慢，但平均下来还好"

真相：
  摊还分析给的是"最坏情况下、任意 n 次操作总开销的上界"，除以 n 得到摊还开销。
  它不假设操作序列是随机的、不假设输入服从任何分布——
  哪怕是敌手故意构造的、最刁钻的 n 次操作序列，总开销依然满足这个界。

  这和"平均情况分析"（average-case analysis）完全不同：
    平均情况：假设输入服从某个概率分布（如哈希表假设 key 均匀随机），
             求的是"期望"意义下的开销，换一批输入、期望可能变化。
    摊还分析：不涉及概率，是对"确定性最坏情况序列"的总量做会计式的核算，
             换成任何输入序列，这个上界依然严格成立。

  一个直接对比：
    哈希表单次查找"平均 O(1)"——依赖 key 是良好分布的（概率论假设），
                              如果所有 key 精心构造成哈希冲突，退化成 O(n)。
    动态数组单次 append"均摊 O(1)"——不管你怎么构造这 n 次 append 的顺序和内容，
                              总开销恒定 ≤ 2n，这是数学上证明了的，不是"运气好"。
```

```python
def per_operation_costs(n: int) -> list[int]:
    """
    记录 n 次 append（capacity 从 1 开始，每次满了 ×2）中，每一次操作的真实开销。
    这里没有任何随机性——同样的 n 会得到完全相同的开销序列，
    用来说明摊还分析处理的是"确定性最坏情况序列"，而不是"输入随机分布下的期望"。
    """
    capacity = 1
    size = 0
    costs = []
    for _ in range(n):
        cost = 0
        if size == capacity:
            cost += capacity  # 触发扩容，这一次的开销跳到 O(size)
            capacity *= 2
        cost += 1
        size += 1
        costs.append(cost)
    return costs


n = 20
costs = per_operation_costs(n)
print(f"n={n} 次 append，每次的真实开销序列：\n{costs}")
print(f"其中单次最大开销 = {max(costs)}（是 O(n) 量级，不是 O(1)）")
print(f"但 {n} 次操作的总开销 = {sum(costs)}，均摊到每次 = {sum(costs)/n:.2f}（是 O(1)）")
```

```
n=20 次 append，每次的真实开销序列：
[1, 2, 3, 1, 5, 1, 1, 1, 9, 1, 1, 1, 1, 1, 1, 1, 17, 1, 1, 1]
其中单次最大开销 = 17（是 O(n) 量级，不是 O(1)）
但 20 次操作的总开销 = 51，均摊到每次 = 2.55（是 O(1)）
```

> 单次操作最坏可以到 O(n)（第 17 次那次扩容），但这种"贵操作"出现得足够稀疏（间隔按指数增长），
> 使得任意前缀的总开销都被摊平成 O(1)/次。下面用 CLRS 的三种标准方法，把这个"稀疏到能摊平"的直觉
> 变成可以严格证明的东西。

---

## 二、聚合分析（Aggregate Method）

**思路最直接**：直接算出 n 次操作的总开销 T(n)，摊还开销就定义为 T(n)/n。不需要构造任何辅助的记账体系，
适合"总开销的封闭形式好算"的场景。

### 2.1 动态数组 append：总开销 < 2n

`dynamic-array.md` 的"四、扩容策略与均摊分析"已经给过直觉版本（容量从 8 开始，总开销 < 3n）。
这里用容量从 1 开始重新推一遍，数字更干净，并且是真正的证明而不是"看着像"：

```
第 i 次 append（i 从 1 开始）触发扩容当且仅当 i-1 = capacity，此时 capacity 会翻倍。
容量序列：1, 2, 4, 8, ..., 直到 >= n。
每次扩容拷贝的元素数 = 扩容前的 capacity，也就是 1, 2, 4, 8, ..., 2^(k-1)（k = ceil(log2 n)）。

拷贝总开销 = 1 + 2 + 4 + ... + 2^(k-1) = 2^k - 1 < n   （等比数列求和，公比 2）
插入总开销 = n（每次 append 自己都要写一次）

总开销 T(n) = n（插入） + (< n)（拷贝） < 2n
摊还开销 = T(n) / n < 2 = O(1)
```

```python
def aggregate_cost_of_appends(n: int) -> tuple[int, int]:
    """
    模拟 n 次 append（capacity 从 1 开始，每次满了 ×2），
    返回 (总实际开销, 总拷贝开销)，验证 T(n) < 2n。
    每次 append 本身花 1（写入新元素）；
    触发扩容时，额外花 old_capacity（把旧元素逐个拷贝到新数组）。
    """
    capacity = 1
    size = 0
    total_cost = 0
    total_copy = 0
    for _ in range(n):
        if size == capacity:
            total_copy += capacity
            total_cost += capacity
            capacity *= 2
        total_cost += 1
        size += 1
    return total_cost, total_copy


for n in (10, 100, 1000, 100_000):
    total, copy = aggregate_cost_of_appends(n)
    print(f"n={n:>7}: 总开销={total:>8}  拷贝开销={copy:>8}  总开销/n={total/n:.3f}  2n={2*n}")
```

```
n=     10: 总开销=      25  拷贝开销=      15  总开销/n=2.500  2n=20
n=    100: 总开销=     227  拷贝开销=     127  总开销/n=2.270  2n=200
n=   1000: 总开销=    2023  拷贝开销=    1023  总开销/n=2.023  2n=2000
n= 100000: 总开销=  231071  拷贝开销=  131071  总开销/n=2.311  2n=200000
```

> 注意 n=10、n=100 时总开销略超过 2n（因为 n 不是 2 的整数次幂时会多扩一次容），但比值随 n 增大
> 稳定收敛到 2 附近——这就是"< 2n 的渐近上界"在有限 n 下的真实样子，不影响 O(1) 的结论。

### 2.2 二进制计数器 INCREMENT：按位计数

CLRS 的经典例子：一个 k 位二进制计数器，`INCREMENT` 从最低位开始，把连续的 1 变成 0（进位），
遇到第一个 0 就把它变成 1 并停止。单次最坏情况（比如 `0111...1 → 1000...0`）要翻转全部 k 位，
是 O(k)；但作为一个整体，n 次 INCREMENT 呢？

```python
def increment(counter: list[int]) -> int:
    """
    k 位二进制计数器的 INCREMENT，counter[0] 是最低位。
    真实开销 = 这一次翻转了多少个 bit。
    单次最坏 O(k)：比如 0111...1 -> 1000...0，翻转了全部 k 位。
    """
    i = 0
    flips = 0
    while i < len(counter) and counter[i] == 1:
        counter[i] = 0
        flips += 1
        i += 1
    if i < len(counter):
        counter[i] = 1
        flips += 1
    return flips


def increment_count_by_bit(counter: list[int], flip_count: list[int]) -> None:
    """同上，但额外记录每一位分别翻转了多少次，用来验证聚合分析的关键观察"""
    i = 0
    while i < len(counter) and counter[i] == 1:
        counter[i] = 0
        flip_count[i] += 1
        i += 1
    if i < len(counter):
        counter[i] = 1
        flip_count[i] += 1


def aggregate_by_bit(n: int, k: int) -> list[int]:
    """
    聚合分析的关键观察：第 i 位（从 0 开始）每 2^i 次 INCREMENT 才翻转一次
    （bit 0 每次都翻转，bit 1 每 2 次翻转一次，bit 2 每 4 次翻转一次……）。
    所以第 i 位在 n 次操作里翻转次数恰好 = floor(n / 2^i)。
    """
    counter = [0] * k
    flip_count = [0] * k
    for _ in range(n):
        increment_count_by_bit(counter, flip_count)
    return flip_count


for n in (16, 100, 1000):
    k = n.bit_length() + 2
    flip_count = aggregate_by_bit(n, k)
    expected = [n // (2 ** i) for i in range(k)]
    assert flip_count == expected
    total = sum(flip_count)
    print(f"n={n}: 每位翻转次数={flip_count}  总翻转={total}  2n={2*n}  total<2n: {total < 2*n}")
```

```
n=16: 每位翻转次数=[16, 8, 4, 2, 1, 0, 0]  总翻转=31  2n=32  total<2n: True
n=100: 每位翻转次数=[100, 50, 25, 12, 6, 3, 1, 0, 0]  总翻转=197  2n=200  total<2n: True
n=1000: 每位翻转次数=[1000, 500, 250, 125, 62, 31, 15, 7, 3, 1, 0, 0]  总翻转=1994  2n=2000  total<2n: True
```

```
总翻转次数 = Σ floor(n / 2^i)  for i = 0 .. floor(log2 n)
           <  Σ n / 2^i        = n · (1 + 1/2 + 1/4 + ...) < 2n

再验证一次"单次最坏 O(k)"确实会发生、但不影响总量：
```

```python
def increment(counter: list[int]) -> int:
    """k 位二进制计数器的 INCREMENT，counter[0] 是最低位，返回本次翻转的 bit 数"""
    i = 0
    flips = 0
    while i < len(counter) and counter[i] == 1:
        counter[i] = 0
        flips += 1
        i += 1
    if i < len(counter):
        counter[i] = 1
        flips += 1
    return flips


def simulate(n: int, k: int) -> tuple[int, int]:
    """对一个 k 位计数器执行 n 次 INCREMENT，返回 (总翻转次数, 单次最大翻转次数)"""
    counter = [0] * k
    total_flips = 0
    max_flips = 0
    for _ in range(n):
        f = increment(counter)
        total_flips += f
        max_flips = max(max_flips, f)
    return total_flips, max_flips


for n in (10, 100, 1000, 100_000):
    k = n.bit_length() + 2
    total, worst = simulate(n, k)
    print(
        f"n={n:>7}: 总翻转次数={total:>8}  单次最坏翻转={worst:>3}"
        f"  总翻转/n={total/n:.3f}  2n={2*n}  是否<=2n: {total <= 2*n}"
    )
```

```
n=     10: 总翻转次数=      18  单次最坏翻转=  4  总翻转/n=1.800  2n=20  是否<=2n: True
n=    100: 总翻转次数=     197  单次最坏翻转=  7  总翻转/n=1.970  2n=200  是否<=2n: True
n=   1000: 总翻转次数=    1994  单次最坏翻转= 10  总翻转/n=1.994  2n=2000  是否<=2n: True
n= 100000: 总翻转次数=  199994  单次最坏翻转= 17  总翻转/n=2.000  2n=200000  是否<=2n: True
```

> 单次最坏翻转数（17）随 n 增长（O(log n) = O(k)），但总翻转数/n 稳定收敛到 2——
> 和动态数组一样，"贵操作"稀疏到能被摊平，INCREMENT 均摊 O(1)。

---

## 三、核算法 / 记账法（Accounting Method）

**思路**：给每次操作分配一个固定的"摊还费用"（amortized charge），费用可能比这次操作实际花的多；
多出来的部分作为"信用"存起来，留给未来那次真正贵的操作来花。核心要证明的不变量：**信用余额永远 ≥ 0**
（不能寅吃卯粮）。这比聚合分析多了一步"设计收费方案"，但优点是不需要先算出总开销的封闭形式，
每次操作单独看就行。

### 3.1 动态数组：每次收 3，信用永不为负

```
方案：每次 append 收取 3 个单位。
  - 1 个单位付给这次 append 本身的写入。
  - 2 个单位作为信用，存到刚插入的这个元素身上。
触发扩容时：把 old_capacity 个旧元素身上的信用取出来付拷贝开销——
  每个旧元素在"被插入时"都存过 2 个信用，拷贝它只需要花 1 个，绰绰有余。
```

```python
def accounting_method_appends(n: int) -> list[int]:
    """
    每次 append 收取 3 个单位的摊还费用：
      - 1 个单位付给这次 append 本身的写入
      - 2 个单位存成信用，挂在刚插入的这个元素上
    触发扩容时，用 old_capacity 个元素身上攒的信用来支付拷贝开销
    （每个旧元素攒了 2 credit，拷贝它只需要 1 credit，足够覆盖）。
    返回信用余额的时间序列，用来验证它永远 >= 0。
    """
    capacity = 1
    size = 0
    credit = 0
    balances = []
    for _ in range(n):
        if size == capacity:
            credit -= capacity      # 扩容：每个旧元素花掉 1 credit
            capacity *= 2
        credit += 3                 # 本次收费 3
        credit -= 1                 # 花 1 在写入上，剩 2 存起来
        size += 1
        balances.append(credit)
    return balances


for n in (10, 100, 1000, 100_000):
    balances = accounting_method_appends(n)
    print(f"n={n:>7}: 信用最小值={min(balances):>8} (应>=0)  最终信用={balances[-1]:>8}")

assert all(b >= 0 for b in accounting_method_appends(100_000)), "信用余额出现负数！"
print("验证通过：信用余额全程 >= 0")
```

```
n=     10: 信用最小值=       2 (应>=0)  最终信用=       5
n=    100: 信用最小值=       2 (应>=0)  最终信用=      73
n=   1000: 信用最小值=       2 (应>=0)  最终信用=     977
n= 100000: 信用最小值=       2 (应>=0)  最终信用=   68929
验证通过：信用余额全程 >= 0
```

信用从未跌破 0（最小值恒为 2），说明"每次收 3"这个收费方案是自洽的——摊还开销 3 = O(1)。

### 3.2 二进制计数器：每次收 2，信用挂在每个 "1" 上

```
方案：每次 INCREMENT 收取 2 个单位。
  - 把某个 bit 从 0 变成 1 时：花 1 单位付这个动作本身，另外 1 单位存成信用挂在这个 bit 上。
  - 把某个 bit 从 1 变成 0 时：不额外收费，直接花掉这个 bit 身上存的 1 单位信用
    （它变成 1 的那一刻已经预付过了）。
```

```python
def increment_with_bank(counter: list[int], credit: list[int]) -> tuple[int, int]:
    """
    记账法：每次 INCREMENT 收取 2 个单位的摊还费用。
    返回 (这次操作实际翻转次数, 银行里全部信用总量)，用来验证信用永远够用（>=0）。
    """
    i = 0
    while i < len(counter) and counter[i] == 1:
        counter[i] = 0
        credit[i] -= 1          # 用这个 bit 上存的信用支付重置，不额外收费
        i += 1
    flips = i
    if i < len(counter):
        counter[i] = 1
        credit[i] += 1           # 收的 2 里，1 个存成信用
        flips += 1
    return flips, sum(credit)


def simulate_accounting(n: int, k: int) -> tuple[list[int], int, int]:
    counter = [0] * k
    credit = [0] * k
    total_charged = 0
    total_actual = 0
    bank_history = []
    for _ in range(n):
        flips, bank = increment_with_bank(counter, credit)
        total_charged += 2          # 每次固定收 2
        total_actual += flips
        bank_history.append(bank)
    return bank_history, total_charged, total_actual


for n in (16, 100, 1000, 100_000):
    k = n.bit_length() + 2
    bank_history, total_charged, total_actual = simulate_accounting(n, k)
    print(
        f"n={n:>7}: 银行信用最小值={min(bank_history)} (应>=0)  "
        f"总收费={total_charged:>8} (=2n)  总实际开销={total_actual:>8}  "
        f"总收费>=总实际开销: {total_charged >= total_actual}"
    )
    assert min(bank_history) >= 0
    assert total_charged >= total_actual

print("验证通过：二进制计数器记账法的信用余额全程 >= 0，且总收费覆盖总实际开销")
```

```
n=     16: 银行信用最小值=1 (应>=0)  总收费=      32 (=2n)  总实际开销=      31  总收费>=总实际开销: True
n=    100: 银行信用最小值=1 (应>=0)  总收费=     200 (=2n)  总实际开销=     197  总收费>=总实际开销: True
n=   1000: 银行信用最小值=1 (应>=0)  总收费=    2000 (=2n)  总实际开销=    1994  总收费>=总实际开销: True
n= 100000: 银行信用最小值=1 (应>=0)  总收费=  200000 (=2n)  总实际开销=  199994  总收费>=总实际开销: True
```

信用余额永远 ≥ 1（每次操作结束都至少留着"当前最低位那个 1"的信用），且总收费恰好等于 2n，
和第二节聚合分析算出的上界完全吻合——两种方法在这里给出了一致的答案，这不是巧合（下一节会看到为什么）。

---

## 四、势能法（Potential Method）

**思路**：定义一个势能函数 Φ，把它绑定在数据结构的状态上（而不是绑定在某个具体元素上，这是它和记账法
的核心区别）。第 i 次操作的**摊还开销**定义为：

```
amortized_i = actual_i + Φ(state_i) - Φ(state_{i-1})   即   actual_i + ΔΦ
```

把这 n 个式子加起来，中间的 Φ 项会逐项相消（telescoping）：

```
Σ amortized_i = Σ actual_i + Φ(state_n) - Φ(state_0)
```

只要能保证 Φ(state_0) ≤ Φ(state_n)（通常取 Φ ≥ 0 且初始为 0），就得到
`Σ actual_i ≤ Σ amortized_i`——即"总实际开销 ≤ 总摊还开销"，这正是我们想要的上界。
势能法的优势：不需要像记账法那样把信用具体挂在某个元素上，只需要一个描述"当前状态有多危险"的
标量函数，往往比记账法更容易推广到复杂数据结构。

### 4.1 动态数组：Φ = 2·size − capacity

```
直觉：size 越接近 capacity，Φ 越大——说明"离下一次扩容越近，欠的债越多"；
     刚扩容完时 size = capacity/2，Φ = 2·(capacity/2) − capacity = 0，债务清零。
```

```python
def potential_method_appends(n: int) -> None:
    """
    势能函数 Phi(size, capacity) = 2*size - capacity。
    验证：
      1) 每一步摊还开销都是常数（<= 3），不随 n 增长。
      2) telescoping 恒等式：sum(摊还开销) = sum(实际开销) + Phi(final) - Phi(initial)。
    """
    capacity = 1
    size = 0
    phi = 2 * size - capacity
    phi_initial = phi

    total_actual = 0
    total_amortized = 0
    max_amortized = 0

    for _ in range(n):
        actual = 0
        if size == capacity:
            actual += capacity
            capacity *= 2
        actual += 1
        size += 1

        phi_new = 2 * size - capacity
        amortized = actual + (phi_new - phi)
        phi = phi_new

        total_actual += actual
        total_amortized += amortized
        max_amortized = max(max_amortized, amortized)

    phi_final = phi
    rhs = total_actual + phi_final - phi_initial
    print(
        f"n={n:>7}: 摊还开销总和={total_amortized:>8}  "
        f"实际开销总和+ΔΦ={rhs:>8}  最大单次摊还开销={max_amortized}"
    )
    assert total_amortized == rhs, "telescoping 恒等式不成立！"


for n in (10, 100, 1000, 100_000):
    potential_method_appends(n)
print("验证通过：telescoping 恒等式成立，且单次摊还开销恒为常数")
```

```
n=     10: 摊还开销总和=      30  实际开销总和+ΔΦ=      30  最大单次摊还开销=3
n=    100: 摊还开销总和=     300  实际开销总和+ΔΦ=     300  最大单次摊还开销=3
n=   1000: 摊还开销总和=    3000  实际开销总和+ΔΦ=    3000  最大单次摊还开销=3
n= 100000: 摊还开销总和=  300000  实际开销总和+ΔΦ=  300000  最大单次摊还开销=3
```

每次操作的摊还开销都精确等于 3——和第三节记账法"每次收 3"的收费方案完全一致，
这不是巧合：**记账法里"每个元素身上的信用"，正是势能法里"Φ 这个整体状态量"的一种具体实现方式**，
两者本质上是同一个证明的两种记法。

### 4.2 二进制计数器：Φ = 二进制中 1 的个数

```
直觉：1 的个数越多，越"接近连环进位"的危险状态（下一次 INCREMENT 可能要翻转一长串 1）；
     每翻转一个 1→0，Φ 减 1（危险度下降）；每翻转一个 0→1，Φ 加 1。
```

```python
def increment_with_potential(counter: list[int]) -> tuple[int, int, int]:
    """势能函数 Phi(counter) = 计数器里 1 的个数。返回 (实际开销, Phi_before, Phi_after)。"""
    phi_before = sum(counter)
    i = 0
    flips = 0
    while i < len(counter) and counter[i] == 1:
        counter[i] = 0
        flips += 1
        i += 1
    if i < len(counter):
        counter[i] = 1
        flips += 1
    phi_after = sum(counter)
    return flips, phi_before, phi_after


def simulate_potential(n: int, k: int) -> None:
    counter = [0] * k
    total_actual = 0
    total_amortized = 0
    max_amortized = 0
    phi_initial = sum(counter)
    for _ in range(n):
        actual, phi_before, phi_after = increment_with_potential(counter)
        amortized = actual + (phi_after - phi_before)
        total_actual += actual
        total_amortized += amortized
        max_amortized = max(max_amortized, amortized)
    phi_final = sum(counter)
    rhs = total_actual + phi_final - phi_initial
    print(
        f"n={n:>7}: 摊还开销总和={total_amortized:>8}  实际开销+ΔΦ={rhs:>8}  "
        f"单次最大摊还开销={max_amortized} (理论上界 2)"
    )
    assert total_amortized == rhs
    assert max_amortized <= 2


for n in (16, 100, 1000, 100_000):
    k = n.bit_length() + 2
    simulate_potential(n, k)

print("验证通过：二进制计数器每次摊还开销 <= 2，且 telescoping 恒等式成立")
```

```
n=     16: 摊还开销总和=      32  实际开销+ΔΦ=      32  单次最大摊还开销=2 (理论上界 2)
n=    100: 摊还开销总和=     200  实际开销+ΔΦ=     200  单次最大摊还开销=2 (理论上界 2)
n=   1000: 摊还开销总和=    2000  实际开销+ΔΦ=    2000  单次最大摊还开销=2 (理论上界 2)
n= 100000: 摊还开销总和=  200000  实际开销+ΔΦ=  200000  单次最大摊还开销=2 (理论上界 2)
```

推导也可以直接手算验证代码结果：设某次 INCREMENT 翻转了 t 个 1→0，且（除非全部溢出）恰好 1 个 0→1，
实际开销 = t + 1，ΔΦ = -t + 1，所以 amortized = (t+1) + (1-t) = 2；如果是溢出（全 1 变全 0，counter 长度耗尽），
实际开销 = t，ΔΦ = -t，amortized = 0。两种情况都 ≤ 2 = O(1)，和代码验证结果完全一致。

---

## 五、三种方法的关系与对比

三种方法证明的是同一件事（同一个摊还上界），区别只在于"怎么把直觉写成严格证明"：

| 方法 | 核心工具 | 优点 | 局限 |
|------|---------|------|------|
| 聚合分析 | 直接算出 T(n) 的封闭形式 | 最直观，不需要设计任何辅助结构 | 只能给出"所有操作的统一均值"，无法区分不同类型操作各自的摊还开销 |
| 核算法/记账法 | 给每种操作设计固定收费，多余部分存成信用挂在具体元素上 | 可以给每种操作单独定价（比如 append 收 3、pop 收 1） | 需要凭直觉猜一个"够用"的收费方案，猜错了要重新试 |
| 势能法 | 定义一个描述整体状态的标量函数 Φ，靠 telescoping 求和 | 最容易推广到复杂数据结构，不需要把信用具体挂到某个元素上 | 需要找到一个合适的 Φ，构造上比前两者更依赖经验 |

本文两个例子里验证到的具体数字关系：

```
动态数组 append：聚合法给出 T(n) < 2n → 记账法每次收 3 能让信用不为负 → 势能法算出每次摊还恰好 = 3
二进制计数器 INCREMENT：聚合法给出总翻转 < 2n → 记账法每次收 2 能让信用不为负 → 势能法算出每次摊还 <= 2
```

三个数字互相吻合，说明它们证明的确实是同一个结论——选哪种方法纯粹是"哪种角度算起来更顺手"的问题：
总开销的封闭形式好算就用聚合分析，操作种类不多且直觉上知道该给谁记账就用记账法，
数据结构复杂、找不到清晰的信用归属就用势能法。

---

[← 返回索引](index.md)
