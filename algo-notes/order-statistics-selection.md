# 顺序统计量的选择算法 · Order-Statistics Selection

> 找第 k 小/大的元素，不需要完整排序。期望线性时间的快速选择已经在 [heap-priority-queue.md](heap-priority-queue.md)
> 的「TopK 问题」一节里；这里补 CLRS 的另一半——**最坏情况也保证线性时间**的选择算法（中位数的中位数）。

---

## 一、期望线性时间：快速选择（回顾）

> 完整实现见 [heap-priority-queue.md](heap-priority-queue.md) 的 `find_kth_largest_quickselect`。

```
核心思路：跟快排一样 partition，但只递归"包含第 k 个元素"的那一边，不管另一边。
随机选 pivot 时，期望 O(n)（每次至少丢掉常数比例的元素，等比数列求和收敛）。

问题：如果每次都选到"最差的 pivot"（比如输入本身是精心构造的对抗数据），
partition 可能每次只排除 1 个元素，退化成 O(n²)——虽然发生概率极低，
但如果这段代码要跑在"输入可能被恶意构造"的场景（比如对外提供的服务），
O(n²) 的最坏情况就是一个真实的风险（拒绝服务攻击的一种手法）。
```

---

## 二、最坏情况线性时间：中位数的中位数 (Median of Medians)

### 2.1 核心思想

```
快速选择慢的根源是"pivot 选得不够好"。中位数的中位数是一种
不依赖随机性、用确定性方法选出一个"足够好"的 pivot 的算法：

1. 把 n 个元素分成 ⌈n/5⌉ 组，每组 5 个（最后一组可能不足5个）
2. 对每一组排序，取出中位数 —— 一共得到 ⌈n/5⌉ 个"组中位数"
3. 递归调用本算法，求出这些组中位数的中位数，作为 pivot
4. 用这个 pivot 对整个数组做三路划分（小于/等于/大于）
5. 根据 k 落在哪一部分，递归到对应的一边（跟快速选择一样）

关键性质：这样选出的 pivot，可以证明至少有 30% 的元素 ≤ pivot，
且至少有 30% 的元素 ≥ pivot —— 所以每次递归，问题规模至少缩小 30%，
这保证了总时间是线性的（见 2.3 的递归式分析）。
```

### 2.2 完整实现

```python
def median_of_medians_select(arr: list[int], k: int) -> int:
    """
    返回 arr 中第 k 小的元素（k 从 1 开始计数）。worst-case O(n)。
    """
    def select(lst: list[int], k: int) -> int:
        n = len(lst)
        if n <= 5:
            return sorted(lst)[k - 1]  # 小数组直接排序（组内也是这样处理的）

        # 1~2. 分组（每组5个），取每组中位数
        medians = [sorted(lst[i:i + 5])[len(lst[i:i + 5]) // 2] for i in range(0, n, 5)]

        # 3. 递归求"中位数的中位数"作为 pivot（这里的 k 是取中位数，即第 (len+1)//2 小）
        pivot = select(medians, (len(medians) + 1) // 2)

        # 4. 用 pivot 做三路划分
        less = [x for x in lst if x < pivot]
        equal = [x for x in lst if x == pivot]
        greater = [x for x in lst if x > pivot]

        # 5. 根据 k 落在哪一部分递归
        if k <= len(less):
            return select(less, k)
        elif k <= len(less) + len(equal):
            return pivot  # k 恰好落在等于 pivot 的这一段
        else:
            return select(greater, k - len(less) - len(equal))

    return select(list(arr), k)
```

### 2.3 为什么是"分成 5 个一组"

```
这是这个算法里最反直觉的一步——为什么不是 3 个一组，或者 7 个一组？

设一组大小为 g。可以证明：至少有一半的"组中位数"是 ≥ pivot 的，
而每个 ≥ pivot 的组中位数所在的那一组，至少有 ⌈g/2⌉ 个元素 ≥ 它的组中位数
（即 ≥ pivot，忽略最后不满一组的情况）。所以至少有约
  (n/g) × (1/2) × (g/2) = n/4   个元素 ≥ pivot（另一侧同理 ≥ n/4 个元素 ≤ pivot）。

g 越大，这个下界占比越高（更能保证"扔掉"足够多元素），
但求组中位数本身的排序成本（O(g log g) 每组）也越高，
且递归子问题 T(n/g) 的规模也要考虑进总递归式。

- g=3 时：下界只能保证约 n/6 的元素被排除，不够——总递归式化简后不收敛为 O(n)
  （T(n) = T(n/3) + T(2n/3) + O(n) 这类形式在 g=3 时的具体系数无法保证线性，
  详见 CLRS 习题 9.3-1 的分析）。
- g=5 时：下界是 3n/10（每边），递归式 T(n) ≤ T(n/5) + T(7n/10) + O(n)，
  用代入法可以证明 T(n) = O(n)（n/5 + 7n/10 = 9n/10 < n，两个递归子问题的规模之和
  严格小于 n，留出的 "1/10 的余量" 正好够吸收每层 O(n) 的划分/找中位数开销）。
- g=7 及更大：同样能保证线性，但每组排序的常数更大，5 是"够用且最省"的选择。

一句话记忆：**5 是能让 T(n) = T(n/5) + T(7n/10) + O(n) 收敛到 O(n) 的最小分组大小。**
```

---

## 三、验证正确性

```python
import random

def brute_force_select(arr: list[int], k: int) -> int:
    return sorted(arr)[k - 1]

random.seed(42)
mismatches = 0
for _ in range(500):
    n = random.randint(1, 200)
    arr = [random.randint(-50, 50) for _ in range(n)]
    k = random.randint(1, n)
    if median_of_medians_select(arr, k) != brute_force_select(arr, k):
        mismatches += 1

print(f"500 次随机测试，不匹配次数：{mismatches}")
# 500 次随机测试，不匹配次数：0
```

---

## 四、两种选择算法对比

| 算法 | 平均时间 | 最坏时间 | pivot 选取方式 |
|------|:---:|:---:|------|
| 快速选择（随机 pivot） | O(n) | O(n²)（概率极低） | 随机选一个元素 |
| 中位数的中位数 | O(n) | **O(n)** | 分组取中位数的中位数，确定性 |

> **实际怎么选**：面试/LeetCode 场景下，随机 pivot 的快速选择几乎总是更快（常数因子小得多），
> 中位数的中位数的意义在于**理论上的最坏情况保证**——需要对抗恶意构造输入、
> 或者是需要严格 worst-case 复杂度保证的系统场景（比如实时系统），才真正用得上。
> 这也是为什么 [heap-priority-queue.md](heap-priority-queue.md) 的 LC 215 题解直接用随机 pivot 版本，
> 而这个更复杂的版本只是作为"理论上更优"的补充放在这里。

---

[← 返回索引](index.md)
