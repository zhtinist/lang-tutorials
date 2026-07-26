# NP完全性 · NP-Completeness

> "这题多项式能不能做出来" 和 "这题能不能在多项式时间内验证一个答案对不对" 是两个不同的问题——前者是 P，后者是 NP，把它们混为一谈是刷题时最容易踩的坑。
> 本篇不追求严谨的 NP 完全性证明（那是教科书和论文的工作），而是把"顶点覆盖 ⟺ 独立集"这类可以用暴力代码验证的等价关系跑通、跑对，再把这套理论翻译成"看到 n ≤ 20 该怎么反应"这种刷题直觉。

---

## 一、P vs NP 直观定义

### 1.1 两个不同的问题

```
P（Polynomial time）：
  存在一个多项式时间的算法，能够"解决"这个问题——
  即：给定输入，直接算出答案（是/否，或者具体的解）。

NP（Nondeterministic Polynomial time）：
  给定一个"候选答案"（有人已经把解算好了，拿给你），
  你能在多项式时间内"验证"这个候选答案是否正确。
  注意：NP 不要求你能快速算出解，只要求"验证"够快。
```

一个直觉例子：数独。自己从空盘解出一个数独可能很费时间（尝试、回溯），但如果有人已经填好了一整盘数独给你看，你只需要逐行逐列逐宫检查一遍（多项式时间）就能确认它对不对。"验证"和"求解"的难度可以天差地别，这正是 NP 这个定义存在的意义。

### 1.2 用代码体会"验证"和"求解"的区别

以子集和问题（Subset Sum：给定一组数字和一个目标值 `target`，判断是否存在一个子集的和恰好等于 `target`）为例：

```python
def verify_subset_sum_solution(nums: list[int], target: int, candidate_indices: list[int]) -> bool:
    """验证器：给定一个"候选解"（一组下标），O(n) 时间内验证它是否满足和为 target。
    这正是 NP 的核心含义——不要求你能想出这个候选解，只要求"验证"足够快。
    """
    return sum(nums[i] for i in candidate_indices) == target


nums = [3, 34, 4, 12, 5, 2]
target = 9

candidate = [0, 2]  # nums[0] + nums[2] = 3 + 4 = 7，不对
print(verify_subset_sum_solution(nums, target, candidate))  # False

candidate = [0, 4]  # nums[0] + nums[4] = 3 + 5 = 8，也不对
print(verify_subset_sum_solution(nums, target, candidate))  # False

candidate = [2, 4]  # nums[2] + nums[4] = 4 + 5 = 9  ✓
print(verify_subset_sum_solution(nums, target, candidate))  # True
```

`verify_subset_sum_solution` 只做一次加法求和，是 O(n) 的——不管 `nums` 有多少种子集组合，验证任何一个给定候选解都很快。但如果没人告诉你候选解是 `[2, 4]`，你要自己"找"出这个子集，已知的通用做法是遍历所有 2ⁿ 个子集（或者用后面会讲的伪多项式 DP）。"验证"简单不代表"求解"简单，这就是 NP 这个类别存在的原因。

### 1.3 P 与 NP 的关系

```
P ⊆ NP 是显然的：
  如果一个问题能在多项式时间内"解决"，
  那么验证一个候选答案，只需要重新跑一遍这个多项式算法、
  再比较结果是否一致即可——这本身就是多项式时间的验证过程。

反过来，NP 中的问题是否都能在多项式时间内"解决"（即 P 是否等于 NP），
是悬而未决的世纪难题——克雷数学研究所"千禧年七大难题"之一，
悬赏 100 万美元，至今没有人证明 P = NP 或 P ≠ NP。

绝大多数计算机科学家的直觉是 P ≠ NP
（即"验证比求解容易"是真实存在的鸿沟），
但这只是直觉，不是已证明的事实。
```

---

## 二、归约 (Reduction)：用顶点覆盖 ⟺ 独立集 体会等价关系

### 2.1 什么是归约

"问题 A 可以归约到问题 B"的意思是：只要你有一个能解决 B 的算法（黑盒），再加上一段**多项式时间**的转换代码（把 A 的输入转换成 B 的输入、把 B 的输出转换回 A 的答案），你就能解决 A。

```
A 可归约到 B（记作 A ≤p B）：
  存在多项式时间函数 f，使得
  "x 是 A 的 yes 实例" 当且仅当 "f(x) 是 B 的 yes 实例"

意义：如果 A ≤p B，那么 B 至少和 A 一样难
（B 有多项式解法 => A 也有；A 没有多项式解法 => B 也没有）。

NP 完全问题的证明套路：
  1. 证明问题本身在 NP 中（给个解能快速验证）；
  2. 找一个已知的 NP 完全问题，把它归约到这个新问题上。
  这一篇不做严格的归约证明，而是挑一对能直接用暴力代码验证的等价关系来体会归约的味道。
```

### 2.2 顶点覆盖 与 独立集：同一张图上的镜像关系

- **顶点覆盖 (Vertex Cover)**：给定图 G = (V, E) 和整数 k，是否存在一个大小为 k 的顶点子集 S，使得**每一条边**至少有一个端点在 S 中。
- **独立集 (Independent Set)**：给定图 G = (V, E) 和整数 k，是否存在一个大小为 k 的顶点子集 I，使得 I 内部**任意两点之间都没有边**。

这两个问题在**同一张图 G 上**（不需要补图）有一个精确的等价关系：

```
S 是 G 的一个顶点覆盖  ⟺  V∖S 是 G 的一个独立集

直觉：
  S 是顶点覆盖 <=> 每条边至少一个端点在 S 中
              <=> 不存在一条边的两个端点都在 V∖S 中
              <=> V∖S 内部没有边
              <=> V∖S 是独立集
```

由此立刻得到：G 中存在大小为 k 的顶点覆盖，当且仅当 G 中存在大小为 (n − k) 的独立集（n = |V|）。这就是"顶点覆盖 ≤p 独立集"以及反过来"独立集 ≤p 顶点覆盖"的具体内容——两个问题互相归约，复杂度地位完全等价。

### 2.3 暴力验证：对随机小图枚举所有子集

下面的代码不是"证明"，而是对随机生成的小图，暴力枚举**每一个**顶点子集 S，同时检查"S 是不是顶点覆盖"和"V∖S 是不是独立集"，验证这两个命题在所有子集上都同真同假。

```python
import itertools
import random


def is_vertex_cover(edges: list[tuple[int, int]], s: set[int]) -> bool:
    """S 是顶点覆盖：每条边至少一个端点在 S 中。"""
    return all(u in s or v in s for u, v in edges)


def is_independent_set(edges: list[tuple[int, int]], s: set[int]) -> bool:
    """S 是独立集：S 内任意两点之间都没有边。"""
    return all(not (u in s and v in s) for u, v in edges)


def random_graph(n: int, p: float) -> list[tuple[int, int]]:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if random.random() < p:
                edges.append((u, v))
    return edges


def check_equivalence(n: int, edges: list[tuple[int, int]]) -> tuple[bool, int]:
    """对顶点集合的每一个子集 S，验证 'S 是顶点覆盖 <=> V∖S 是独立集'。
    返回 (是否全部成立, 检查了多少个子集)。
    """
    vertices = set(range(n))
    checked = 0
    for r in range(n + 1):
        for combo in itertools.combinations(range(n), r):
            s = set(combo)
            complement = vertices - s
            vc = is_vertex_cover(edges, s)
            ind = is_independent_set(edges, complement)
            checked += 1
            if vc != ind:
                return False, checked
    return True, checked


def main() -> None:
    random.seed(42)
    total_graphs = 0
    total_subsets_checked = 0
    all_ok = True
    for _ in range(30):
        n = random.randint(2, 10)
        p = random.choice([0.2, 0.3, 0.4, 0.5, 0.6, 0.7])
        edges = random_graph(n, p)
        ok, checked = check_equivalence(n, edges)
        total_graphs += 1
        total_subsets_checked += checked
        if not ok:
            all_ok = False
            print(f"FAIL: n={n}, edges={edges}")
    print(f"图数量: {total_graphs}")
    print(f"验证的子集总数: {total_subsets_checked}")
    print(f"全部等价关系是否成立: {all_ok}")


if __name__ == "__main__":
    main()
```

实际跑出来的结果：

```
图数量: 30
验证的子集总数: 7444
全部等价关系是否成立: True
```

30 张随机小图（顶点数 2~10，边密度 0.2~0.7），一共 7444 个子集，"S 是顶点覆盖 ⟺ V∖S 是独立集"这条命题无一例外全部成立。这也说明：如果哪天有人发明了顶点覆盖的多项式算法，独立集立刻也有了（反之亦然）——两者难度完全绑定，这就是归约的威力：不需要重新研究一遍独立集，直接复用顶点覆盖的解法（补集操作是 O(n) 的，不影响多项式这个大类别）。

---

## 三、经典 NP 完全问题清单

以下问题均已被证明是 NP 完全的（证明过程略，只给出问题描述——完整的归约证明可以参考 CLRS 第 34 章或任何算法教材）：

| 问题 | 判定版描述 |
|------|-----------|
| 团问题 (Clique) | 图 G 中是否存在一个大小为 k 的团（任意两点都有边相连的顶点子集）|
| 顶点覆盖 (Vertex Cover) | 图 G 中是否存在大小为 k 的顶点子集，覆盖所有边（见第二节）|
| 哈密顿回路 (Hamiltonian Cycle) | 图 G 中是否存在一条经过每个顶点恰好一次、最后回到起点的回路 |
| 旅行商问题判定版 (TSP Decision) | 给定带权图和阈值 B，是否存在一条经过所有顶点恰好一次、总权重 ≤ B 的回路 |
| 子集和问题 (Subset Sum) | 给定一组整数和目标值 target，是否存在一个子集的和恰好等于 target |
| 3-SAT | 给定一个"若干个恰好 3 个文字组成的子句"的合取范式（CNF），是否存在一组真值赋值使整个公式为真 |

这些问题表面上八竿子打不着（图论、数论、逻辑），但都能互相归约到彼此——这正是"NP 完全"这个类别的定义：类中任意一个问题如果被找到多项式解法，所有 NP 中的问题都会有多项式解法（因为 NP 完全问题是 NP 中"最难"的一批，NP 里的任何问题都可以归约到它们）。

### 3.1 子集和问题：为什么"数值很大"会让它变成指数级

子集和有一个经典的**伪多项式 (pseudo-polynomial)** 动态规划解法：设 `dp[t]` 表示"能否用当前考虑过的数字凑出和为 t"，时间和空间复杂度都是 O(n × target)。

```python
import itertools
import random


def subset_sum_brute(nums: list[int], target: int) -> bool:
    """暴力枚举所有 2^n 个子集，检查是否有子集和恰好等于 target。"""
    n = len(nums)
    for r in range(n + 1):
        for combo in itertools.combinations(nums, r):
            if sum(combo) == target:
                return True
    return False


def subset_sum_dp(nums: list[int], target: int) -> bool:
    """伪多项式 DP：O(n * target) 时间/空间。
    dp[t] 表示"用当前已经考虑过的数字，能否凑出和为 t"。
    """
    if target < 0:
        return False
    dp = [False] * (target + 1)
    dp[0] = True
    for num in nums:
        for t in range(target, num - 1, -1):
            if dp[t - num]:
                dp[t] = True
    return dp[target]


def main() -> None:
    random.seed(7)
    trials = 25
    all_match = True
    for _ in range(trials):
        n = random.randint(1, 12)
        nums = [random.randint(1, 15) for _ in range(n)]
        target = random.randint(0, sum(nums))
        brute = subset_sum_brute(nums, target)
        dp = subset_sum_dp(nums, target)
        if brute != dp:
            all_match = False
            print(f"MISMATCH: nums={nums}, target={target}, brute={brute}, dp={dp}")
    print(f"随机实例数: {trials}")
    print(f"DP 与暴力结果是否全部一致: {all_match}")

    print()
    print("同一个 n，target 数量级不同 -> DP 数组大小(和内存占用)对比：")
    for n in [10, 20, 30, 40, 50]:
        target = 2 ** n  # 构造一个 target 随 n 指数增长的极端实例
        dp_bytes = (target + 1) * 8  # 假设每个元素占 8 字节，量级估算
        dp_gb = dp_bytes / (1024 ** 3)
        print(f"n={n:2d}: target=2^{n}={target:,}, dp数组约需 {dp_gb:,.2f} GB")


if __name__ == "__main__":
    main()
```

实际跑出来的结果：

```
随机实例数: 25
DP 与暴力结果是否全部一致: True

同一个 n，target 数量级不同 -> DP 数组大小(和内存占用)对比：
n=10: target=2^10=1,024, dp数组约需 0.00 GB
n=20: target=2^20=1,048,576, dp数组约需 0.01 GB
n=30: target=2^30=1,073,741,824, dp数组约需 8.00 GB
n=40: target=2^40=1,099,511,627,776, dp数组约需 8,192.00 GB
n=50: target=2^50=1,125,899,906,842,624, dp数组约需 8,388,608.00 GB
```

25 个随机实例上，DP 和暴力枚举结果完全一致，说明 DP 实现是对的。但后半段的对比才是关键：**O(n × target) 是"伪多项式"而不是"多项式"**——它对 target 的**数值**是多项式，但 target 的数值可以用 O(log target) 位二进制编码表示，也就是说相对于"输入规模"（bit 数）而言，O(target) 是**指数级**的。当 target 随 n 指数增长（比如 target = 2ⁿ）时，n 只从 10 涨到 50，DP 数组需要的内存却从几 KB 暴涨到 8 PB——这正是子集和问题被归入 NP 完全、而不是"P 问题"的原因：它没有真正对输入规模（bit 长度）多项式的算法。

---

## 四、这跟刷 LeetCode 有什么关系

理论说了这么多，落到刷题上就是一句话：**看数据范围，反推期望复杂度，反推题目的"真实身份"。**

```
n ≤ 15~20 左右      -> 大概率是 O(2^n) 状压 DP，题目本质是某个 NP-hard 问题的小规模实例
n ≤ 20~25，且是排列 -> 大概率是 O(n × 2^n)（旅行商式状压 DP），本质是 TSP
n ≤ 40，值域也不大   -> 可能是"折半枚举"（meet in the middle），把 2^n 拆成 2 × 2^(n/2)
n ≤ 10^5 甚至更大    -> 基本可以排除 NP-hard 的"完整版"思路，
                        说明这题一定存在多项式解法（贪心/DP/双指针/单调栈等）
```

具体例子：

- **[416. 分割等和子集 (Partition Equal Subset Sum)](https://leetcode.com/problems/partition-equal-subset-sum/)**：本质就是子集和问题（target = 总和的一半）。题目允许 `nums.length ≤ 200` 且 `nums[i] ≤ 100`，看起来"n"不小，但注意 target 的数值上限只有 `200 × 100 / 2 = 10000`——正是因为出题人利用了"伪多项式 DP 在 target 数值可控时其实很快"这个特性，把一个 NP-hard 问题出成了能过的题。如果 `nums[i]` 允许到 `10^9`，这题立刻就无法用背包 DP 通过。**看到子集和/背包类问题，先看数值范围（不只是数组长度），这是判断"伪多项式 DP 能不能过"的关键。**
- **[139/140. 单词拆分 (Word Break I/II)](https://leetcode.com/problems/word-break/)**：Word Break I（能否拆分，布尔答案）是标准区间 DP，多项式可解。但 Word Break II（要求返回所有拆分方案）在最坏情况下答案数量本身就是指数级的（比如全部由单字符单词构成的字符串），这不是"没找到多项式算法"，而是"答案数量决定了输出规模下限是指数级"——这提示我们枚举所有方案类的题目要对输出规模保持警惕，跟纯判定性 NP-hard 问题不完全是一回事，但"警惕指数爆炸"的直觉是相通的。
- **旅行商类题目**（如"访问所有节点的最短路径" [847. Shortest Path Visiting All Nodes](https://leetcode.com/problems/shortest-path-visiting-all-nodes/)）：题目给出 `n ≤ 12`，这几乎是在明示"用状压 DP，状态是 (当前节点, 已访问集合)"——因为 TSP 判定版是 NP 完全的，`n ≤ 12` 这种反常的小上限就是在暗示"别指望多项式解法，指数级状压 DP 就是标准答案"。

反过来，如果看到一道图论或组合类题目给出 `n, m ≤ 10^5`，而它长得很像团问题/顶点覆盖/哈密顿回路，那么要么是题目本身有特殊约束（比如图是一棵树、是二分图、是区间图——很多 NP-hard 问题在特殊图类上有多项式算法），要么是我们把问题读错了、真正要求的是一个多项式可解的简化版本。**"NP-hard 问题的一般形式配上 10 万级别的数据范围"这个组合几乎不会出现在正常的 OJ 题目里**，遇到了应该先怀疑自己的建模，而不是怀疑出题人。

---

## 五、总结表格

| 问题 | 是否已知多项式解法 | 近似算法是否存在 |
|------|---------------------|-------------------|
| 团问题 (Clique) | 否（NP 完全） | 已知很难近似（在标准复杂度假设下无常数因子近似），细节见 `approximation-algorithms.md` |
| 顶点覆盖 (Vertex Cover) | 否（NP 完全） | 是，存在简单的 2-近似算法，见 `approximation-algorithms.md` |
| 独立集 (Independent Set) | 否（NP 完全，与顶点覆盖等价） | 与团问题类似，近似很难 |
| 哈密顿回路 (Hamiltonian Cycle) | 否（NP 完全） | 判定版一般不谈近似（是/否问题），优化版见 TSP |
| 旅行商问题判定版 (TSP Decision) | 否（NP 完全） | 三角不等式成立时有常数因子近似（如 Christofides 算法），一般情况下无界，见 `approximation-algorithms.md` |
| 子集和问题 (Subset Sum) | 否（NP 完全，伪多项式 DP 可用但非真正多项式） | 有全多项式时间近似方案 (FPTAS)，见 `approximation-algorithms.md` |
| 3-SAT | 否（NP 完全） | 判定版无近似概念，但 MAX-3SAT（最大化满足子句数）有近似算法 |

---

[← 返回索引](index.md)
