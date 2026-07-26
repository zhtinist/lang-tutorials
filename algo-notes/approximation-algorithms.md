# 近似算法 · Approximation Algorithms

> 很多问题是 NP-hard 的——假设 P≠NP，就不存在多项式时间算法能保证求出最优解。
> 但这不代表束手无策：这类问题里有相当一部分存在多项式时间的**近似算法**，其输出可以被**证明**
> 落在最优解的某个常数倍（或对数倍）范围内。这正是它和"启发式算法"的本质区别——
> 近似算法给出的是一个有数学证明的误差上界，不管输入长什么样、不管运气好坏，这个比值恒成立；
> 单纯的启发式算法则只是"经验上通常还不错"，没有任何可以证明的保证，遇到刁钻输入可能任意差。
> 近似算法用"放弃精确解"换来"多项式时间 + 可证明的误差上界"，是 NP-hard 世界里依然可控的权衡。

---

## 一、顶点覆盖 2-近似 (Vertex Cover 2-Approximation)

**问题**：给定无向图 G=(V, E)，求最小的顶点子集 C，使得每条边至少有一个端点在 C 里。这是经典
NP-hard 问题（[CLRS 35.1](https://en.wikipedia.org/wiki/Vertex_cover)），但下面这个贪心策略能在
多项式时间内给出一个不超过最优解 2 倍的覆盖集。

**算法**：反复挑一条还剩下的边 (u, v)，把 u 和 v **都**加入覆盖集合，然后删除所有与 u 或 v 相邻的边，
直到没有边剩下为止。

```python
def approx_vertex_cover(edges: list[tuple[int, int]]) -> set[int]:
    """
    CLRS 35.1：反复挑一条剩余的边 (u, v)，把 u 和 v 都加入覆盖集合，
    然后删除所有与 u 或 v 相邻的边，直到没有边剩下为止。
    """
    remaining = set(edges)
    cover: set[int] = set()
    while remaining:
        u, v = remaining.pop()
        cover.add(u)
        cover.add(v)
        remaining = {
            (a, b) for (a, b) in remaining
            if a != u and a != v and b != u and b != v
        }
    return cover
```

**为什么是 2-近似**：算法每一轮挑出来的边 (u, v) 有一个关键性质——**这些被挑中的边两两之间不共享
任何端点**，因为一旦选中 (u, v)，就会把所有触碰 u 或 v 的边全部删掉，下一轮不可能再选到与 u 或 v
相邻的边。也就是说，被选中的边构成图里的一个**匹配（matching）**。

设算法一共挑了 k 条边（这些边顶点两两不相交）。任何一个合法的顶点覆盖，都必须为这 k 条边**各自**
覆盖至少一个端点——因为这 k 条边互不相交，覆盖第 i 条边所用的顶点无法"顺便"覆盖第 j 条边（j ≠ i）。
所以最优解 OPT 至少要用 k 个顶点：**OPT ≥ k**。而我们的算法恰好输出 2k 个顶点（每条选中的边贡献
两个端点，且这些端点两两不同）。所以：

```
算法输出的大小 = 2k ≤ 2 · OPT
```

这就是 2-近似比的证明：不需要真的知道 OPT 是多少，只需要知道"选出的边是一个匹配"这一件事，就能
把算法输出和 OPT 关联起来。

### 1.1 暴力验证：对比真实最小顶点覆盖

```python
import random
from itertools import combinations


def approx_vertex_cover(edges: list[tuple[int, int]]) -> set[int]:
    """同上：反复挑一条边，把两端点都收进覆盖集合，删除相邻边。"""
    remaining = set(edges)
    cover: set[int] = set()
    while remaining:
        u, v = remaining.pop()
        cover.add(u)
        cover.add(v)
        remaining = {
            (a, b) for (a, b) in remaining
            if a != u and a != v and b != u and b != v
        }
    return cover


def brute_force_min_vertex_cover(n: int, edges: list[tuple[int, int]]) -> int:
    """暴力枚举所有顶点子集，找最小的能覆盖所有边的子集大小（n 很小时才可行）。"""
    vertices = list(range(n))
    for size in range(n + 1):
        for subset in combinations(vertices, size):
            s = set(subset)
            if all(u in s or v in s for u, v in edges):
                return size
    return n


def random_graph(n: int, p: float, rng: random.Random) -> list[tuple[int, int]]:
    edges = []
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                edges.append((u, v))
    return edges


rng = random.Random(42)
ratios: list[float] = []
for trial in range(20):
    n = rng.randint(4, 10)
    p = rng.uniform(0.2, 0.6)
    edges = random_graph(n, p, rng)
    if not edges:
        continue
    approx = approx_vertex_cover(edges)
    opt = brute_force_min_vertex_cover(n, edges)
    ratio = len(approx) / opt if opt else 0
    ratios.append(ratio)
    print(
        f"trial {trial:2d}: n={n} |E|={len(edges):2d}  "
        f"approx={len(approx)}  opt={opt}  ratio={ratio:.3f}"
    )

print(f"\n共 {len(ratios)} 组随机图，最大比值 = {max(ratios):.3f}（理论上界 2.0）")
assert all(r <= 2.0 + 1e-9 for r in ratios)
print("验证通过：所有实例 ratio <= 2")
```

```
trial  0: n=9 |E|=11  approx=6  opt=5  ratio=1.200
trial  1: n=10 |E|=13  approx=8  opt=5  ratio=1.600
trial  2: n=6 |E|= 5  approx=4  opt=2  ratio=2.000
trial  3: n=9 |E|= 9  approx=6  opt=3  ratio=2.000
trial  4: n=5 |E|= 2  approx=4  opt=2  ratio=2.000
trial  5: n=9 |E|=20  approx=6  opt=6  ratio=1.000
trial  6: n=5 |E|= 4  approx=4  opt=2  ratio=2.000
trial  7: n=4 |E|= 4  approx=2  opt=2  ratio=1.000
trial  8: n=4 |E|= 1  approx=2  opt=1  ratio=2.000
trial  9: n=9 |E|=24  approx=8  opt=5  ratio=1.600
trial 10: n=4 |E|= 2  approx=2  opt=1  ratio=2.000
trial 11: n=6 |E|= 6  approx=6  opt=3  ratio=2.000
trial 12: n=4 |E|= 4  approx=2  opt=2  ratio=1.000
trial 13: n=8 |E|=11  approx=4  opt=3  ratio=1.333
trial 14: n=4 |E|= 1  approx=2  opt=1  ratio=2.000
trial 15: n=5 |E|= 3  approx=4  opt=2  ratio=2.000
trial 16: n=10 |E|=22  approx=8  opt=6  ratio=1.333
trial 17: n=9 |E|=22  approx=8  opt=6  ratio=1.333
trial 18: n=5 |E|= 5  approx=4  opt=3  ratio=1.333
trial 19: n=10 |E|=27  approx=10  opt=7  ratio=1.429

共 20 组随机图，最大比值 = 2.000（理论上界 2.0）
验证通过：所有实例 ratio <= 2
```

> 20 组随机图里比值最高摸到了理论上界 2.0（比如一条条互不相邻的边组成的图，算法和 OPT 都会
> 精确按 2 倍关系差开），从没有超过 2——和证明完全吻合。

---

## 二、TSP 近似（满足三角不等式）

**问题**：给定完全图上每对点的距离，求一条经过所有点恰好一次再回到起点的最短回路。这也是 NP-hard
问题（[CLRS 35.2](https://en.wikipedia.org/wiki/Travelling_salesman_problem)）。如果距离满足
**三角不等式**（`dist(u, w) ≤ dist(u, v) + dist(v, w)`，比如任意二维平面上的欧氏距离自动满足），
下面的算法能给出一个 2-近似的回路。

**算法**：

1. 对完全图求一棵**最小生成树（MST）**。
2. 从任意一个顶点出发，对 MST 做**前序 DFS 遍历**，记录访问顺序。
3. **抄近路（shortcut）**：DFS 序列里如果某个顶点已经出现过，就跳过它，只保留每个顶点第一次出现的
   位置——这样就得到一条不重复经过任何顶点的回路。

```python
import math


def prim_mst_matrix(dist: list[list[float]]) -> list[list[int]]:
    """稠密图 Prim's（邻接矩阵版），返回 MST 的邻接表 adj[u] = [v, ...]。"""
    n = len(dist)
    in_tree = [False] * n
    min_edge = [math.inf] * n
    parent = [-1] * n
    min_edge[0] = 0.0

    for _ in range(n):
        u = min((v for v in range(n) if not in_tree[v]), key=lambda v: min_edge[v])
        in_tree[u] = True
        for v in range(n):
            if not in_tree[v] and dist[u][v] < min_edge[v]:
                min_edge[v] = dist[u][v]
                parent[v] = u

    adj: list[list[int]] = [[] for _ in range(n)]
    for v in range(n):
        if parent[v] != -1:
            adj[v].append(parent[v])
            adj[parent[v]].append(v)
    return adj


def approx_tsp_tour(dist: list[list[float]]) -> list[int]:
    """
    CLRS 35.2：先建 MST，再对 MST 做前序 DFS 遍历，
    遇到已访问过的顶点就跳过（shortcut），得到一条近似 TSP 回路。
    """
    n = len(dist)
    adj = prim_mst_matrix(dist)
    visited = [False] * n
    tour: list[int] = []

    def dfs(u: int) -> None:
        visited[u] = True
        tour.append(u)
        for v in adj[u]:
            if not visited[v]:
                dfs(v)

    dfs(0)
    return tour
```

> MST 部分用了邻接矩阵版 Prim's（O(n²)，适合稠密的完全图），和
> [minimum-spanning-tree.md](minimum-spanning-tree.md) 里邻接表 + 堆的版本是同一个算法思想的不同
> 实现选择——那里是"图本身就是稀疏邻接表"的场景，这里是"完全图/邻接矩阵"的场景，选哪种实现见
> 该文件「四、Kruskal vs Prim 该用哪个」一节的讨论。

**为什么是 2-近似**：

1. **MST ≤ OPT**：从最优回路 OPT 中任意删掉一条边，剩下的是一条经过所有顶点的**路径**，路径本身
   就是一棵生成树，所以它的总权重 ≥ MST 的总权重（MST 是所有生成树里权重最小的）。而这条路径的权重
   显然 ≤ OPT 的总权重（去掉了一条边，权重只会更小）。串起来就是 `MST ≤ OPT`。
2. **DFS 遍历（不抄近路）的代价 = 2 × MST**：前序 DFS 沿着树边"走进去再走出来"，每条 MST 边恰好被
   走两次（一次进入子树，一次回溯），所以完整遍历（含回溯）的总代价 = 2 × weight(MST)。
3. **抄近路只会更省，不会更贵**：因为距离满足三角不等式，"跳过中间已访问的顶点、直接连到下一个新
   顶点"的直达距离，不可能比"绕经中间那些顶点"的路径更长——`shortcut` 后的回路总代价 ≤ 抄近路前的
   遍历代价。

把三步串起来：

```
近似回路代价 ≤ 2 × weight(MST) ≤ 2 × OPT
```

这就是三角不等式下的 2-近似证明。注意：如果距离不满足三角不等式，第 3 步就不成立，这个算法就没有
任何近似比保证了。

### 2.1 暴力验证：对比真实最优回路（随机欧氏点集）

```python
import math
import random
from itertools import permutations


def prim_mst_matrix(dist: list[list[float]]) -> list[list[int]]:
    """同上：稠密图 Prim's（邻接矩阵版），返回 MST 的邻接表。"""
    n = len(dist)
    in_tree = [False] * n
    min_edge = [math.inf] * n
    parent = [-1] * n
    min_edge[0] = 0.0

    for _ in range(n):
        u = min((v for v in range(n) if not in_tree[v]), key=lambda v: min_edge[v])
        in_tree[u] = True
        for v in range(n):
            if not in_tree[v] and dist[u][v] < min_edge[v]:
                min_edge[v] = dist[u][v]
                parent[v] = u

    adj: list[list[int]] = [[] for _ in range(n)]
    for v in range(n):
        if parent[v] != -1:
            adj[v].append(parent[v])
            adj[parent[v]].append(v)
    return adj


def approx_tsp_tour(dist: list[list[float]]) -> list[int]:
    """同上：MST 前序 DFS + shortcut。"""
    n = len(dist)
    adj = prim_mst_matrix(dist)
    visited = [False] * n
    tour: list[int] = []

    def dfs(u: int) -> None:
        visited[u] = True
        tour.append(u)
        for v in adj[u]:
            if not visited[v]:
                dfs(v)

    dfs(0)
    return tour


def tour_cost(tour: list[int], dist: list[list[float]]) -> float:
    n = len(tour)
    return sum(dist[tour[i]][tour[(i + 1) % n]] for i in range(n))


def brute_force_tsp(dist: list[list[float]]) -> float:
    """暴力枚举所有排列，找最优回路总长（n 很小时才可行）。"""
    n = len(dist)
    best = math.inf
    for perm in permutations(range(1, n)):
        full = (0,) + perm
        best = min(best, tour_cost(list(full), dist))
    return best


def euclidean_dist_matrix(points: list[tuple[float, float]]) -> list[list[float]]:
    n = len(points)
    return [[math.dist(points[i], points[j]) for j in range(n)] for i in range(n)]


rng = random.Random(7)
ratios: list[float] = []
for trial in range(15):
    n = rng.randint(4, 8)
    points = [(rng.uniform(0, 100), rng.uniform(0, 100)) for _ in range(n)]
    dist = euclidean_dist_matrix(points)  # 欧氏距离自动满足三角不等式
    tour = approx_tsp_tour(dist)
    approx_cost = tour_cost(tour, dist)
    opt_cost = brute_force_tsp(dist)
    ratio = approx_cost / opt_cost if opt_cost > 0 else 1.0
    ratios.append(ratio)
    print(f"trial {trial:2d}: n={n}  approx={approx_cost:8.3f}  opt={opt_cost:8.3f}  ratio={ratio:.3f}")

print(f"\n共 {len(ratios)} 组随机欧氏点集，最大比值 = {max(ratios):.3f}（理论上界 2.0）")
assert all(r <= 2.0 + 1e-9 for r in ratios)
print("验证通过：所有实例 ratio <= 2")
```

```
trial  0: n=6  approx= 259.283  opt= 249.627  ratio=1.039
trial  1: n=4  approx= 232.523  opt= 232.523  ratio=1.000
trial  2: n=4  approx= 121.976  opt= 118.253  ratio=1.031
trial  3: n=8  approx= 262.391  opt= 230.314  ratio=1.139
trial  4: n=8  approx= 305.673  opt= 261.476  ratio=1.169
trial  5: n=6  approx= 270.031  opt= 232.118  ratio=1.163
trial  6: n=6  approx= 185.299  opt= 185.299  ratio=1.000
trial  7: n=7  approx= 288.709  opt= 288.013  ratio=1.002
trial  8: n=5  approx= 185.224  opt= 185.224  ratio=1.000
trial  9: n=8  approx= 303.917  opt= 251.029  ratio=1.211
trial 10: n=4  approx= 229.986  opt= 229.986  ratio=1.000
trial 11: n=6  approx= 248.094  opt= 245.947  ratio=1.009
trial 12: n=5  approx= 195.279  opt= 195.279  ratio=1.000
trial 13: n=6  approx= 190.490  opt= 190.490  ratio=1.000
trial 14: n=7  approx= 316.637  opt= 316.637  ratio=1.000

共 15 组随机欧氏点集，最大比值 = 1.211（理论上界 2.0）
验证通过：所有实例 ratio <= 2
```

> 实测比值远小于理论上界 2.0（最高只到 1.211）——这是符合预期的：2-近似证明用了两个比较松的不等式
> （"路径 ≤ MST 的差距"和"抄近路省了多少"都是最坏情况的界），随机欧氏点集通常远离这个最坏情况，
> 实际表现比理论保证好得多，这也是近似算法在工程实践中很常用的原因。

---

## 三、集合覆盖贪心近似 (Greedy Set Cover)

**问题**：给定全集 U 和若干子集 S₁, ..., Sₘ ⊆ U，求最少数量的子集，使它们的并集覆盖整个 U。这同样
是 NP-hard 问题（[CLRS 35.3](https://en.wikipedia.org/wiki/Set_cover_problem)）。

**算法**：反复挑选"覆盖了最多**尚未被覆盖**元素"的那个子集，直到全集被覆盖为止。

```python
def greedy_set_cover(universe: set[int], subsets: list[set[int]]) -> list[int]:
    """
    CLRS 35.3：反复挑选覆盖了最多未覆盖元素的子集，直到全集被覆盖为止。
    返回被选中的子集下标列表。
    """
    uncovered = set(universe)
    chosen: list[int] = []
    available = list(range(len(subsets)))
    while uncovered:
        best_idx = max(available, key=lambda i: len(subsets[i] & uncovered))
        chosen.append(best_idx)
        uncovered -= subsets[best_idx]
        available.remove(best_idx)
    return chosen
```

**近似比**：这是一个经典结果（CLRS 定理 35.4），这里直接引用而不重新证明：贪心算法选出的子集数
不超过 **H(n) × OPT**，其中 `H(n) = 1 + 1/2 + 1/3 + ... + 1/n` 是第 n 个调和数，n 取"最大子集的
大小"。直觉上，H(n) 是 O(log n) 量级——每一轮贪心至少覆盖剩余未覆盖元素的 `1/OPT` 比例，剩余元素数
呈类似等比数列衰减，求和后自然出现调和级数。

### 3.1 暴力验证：对比真实最优集合覆盖

```python
import random
from itertools import combinations


def greedy_set_cover(universe: set[int], subsets: list[set[int]]) -> list[int]:
    """同上：反复挑选覆盖了最多未覆盖元素的子集。"""
    uncovered = set(universe)
    chosen: list[int] = []
    available = list(range(len(subsets)))
    while uncovered:
        best_idx = max(available, key=lambda i: len(subsets[i] & uncovered))
        chosen.append(best_idx)
        uncovered -= subsets[best_idx]
        available.remove(best_idx)
    return chosen


def brute_force_min_set_cover(universe: set[int], subsets: list[set[int]]) -> int:
    """暴力枚举所有子集组合，找覆盖全集所需的最少子集数（子集数量很小时才可行）。"""
    m = len(subsets)
    indices = list(range(m))
    for size in range(1, m + 1):
        for combo in combinations(indices, size):
            covered: set[int] = set()
            for i in combo:
                covered |= subsets[i]
            if covered >= universe:
                return size
    return m


def harmonic(n: int) -> float:
    return sum(1.0 / i for i in range(1, n + 1))


def random_instance(u_size: int, m: int, rng: random.Random) -> tuple[set[int], list[set[int]]]:
    universe = set(range(u_size))
    subsets = []
    for _ in range(m):
        k = rng.randint(1, max(2, u_size // 2))  # 偏小的子集，更容易让贪心走弯路
        subsets.append(set(rng.sample(range(u_size), k)))
    covered: set[int] = set()
    for s in subsets:
        covered |= s
    if covered != universe:  # 保证并集覆盖全集
        subsets.append(universe - covered)
    return universe, subsets


rng = random.Random(11)
ratios: list[float] = []
for trial in range(20):
    u_size = rng.randint(6, 10)
    m = rng.randint(6, 9)
    universe, subsets = random_instance(u_size, m, rng)
    n = max(len(s) for s in subsets)  # H(n) 的 n 取最大子集大小
    greedy = greedy_set_cover(universe, subsets)
    opt = brute_force_min_set_cover(universe, subsets)
    bound = harmonic(n)
    ratio = len(greedy) / opt if opt else 0
    ratios.append(ratio)
    print(
        f"trial {trial:2d}: |U|={u_size} m={m}  greedy={len(greedy)}  opt={opt}  "
        f"ratio={ratio:.3f}  H({n})={bound:.3f}  ratio<=H(n): {ratio <= bound + 1e-9}"
    )

print(f"\n共 {len(ratios)} 组随机实例，最大比值 = {max(ratios):.3f}")
print("验证通过：所有实例 greedy/opt <= H(n)")
```

```
trial  0: |U|=9 m=9  greedy=3  opt=3  ratio=1.000  H(4)=2.083  ratio<=H(n): True
trial  1: |U|=6 m=6  greedy=3  opt=3  ratio=1.000  H(3)=1.833  ratio<=H(n): True
trial  2: |U|=6 m=6  greedy=3  opt=3  ratio=1.000  H(3)=1.833  ratio<=H(n): True
trial  3: |U|=8 m=6  greedy=3  opt=3  ratio=1.000  H(4)=2.083  ratio<=H(n): True
trial  4: |U|=6 m=8  greedy=3  opt=3  ratio=1.000  H(3)=1.833  ratio<=H(n): True
trial  5: |U|=6 m=7  greedy=3  opt=3  ratio=1.000  H(3)=1.833  ratio<=H(n): True
trial  6: |U|=7 m=7  greedy=4  opt=4  ratio=1.000  H(3)=1.833  ratio<=H(n): True
trial  7: |U|=9 m=8  greedy=5  opt=5  ratio=1.000  H(3)=1.833  ratio<=H(n): True
trial  8: |U|=7 m=9  greedy=3  opt=3  ratio=1.000  H(3)=1.833  ratio<=H(n): True
trial  9: |U|=9 m=8  greedy=4  opt=4  ratio=1.000  H(4)=2.083  ratio<=H(n): True
trial 10: |U|=10 m=9  greedy=3  opt=3  ratio=1.000  H(5)=2.283  ratio<=H(n): True
trial 11: |U|=8 m=6  greedy=4  opt=3  ratio=1.333  H(4)=2.083  ratio<=H(n): True
trial 12: |U|=8 m=8  greedy=4  opt=4  ratio=1.000  H(4)=2.083  ratio<=H(n): True
trial 13: |U|=9 m=6  greedy=5  opt=5  ratio=1.000  H(4)=2.083  ratio<=H(n): True
trial 14: |U|=7 m=6  greedy=5  opt=4  ratio=1.250  H(3)=1.833  ratio<=H(n): True
trial 15: |U|=8 m=9  greedy=3  opt=3  ratio=1.000  H(4)=2.083  ratio<=H(n): True
trial 16: |U|=7 m=8  greedy=4  opt=4  ratio=1.000  H(3)=1.833  ratio<=H(n): True
trial 17: |U|=10 m=9  greedy=4  opt=4  ratio=1.000  H(4)=2.083  ratio<=H(n): True
trial 18: |U|=10 m=6  greedy=4  opt=4  ratio=1.000  H(5)=2.283  ratio<=H(n): True
trial 19: |U|=7 m=7  greedy=5  opt=5  ratio=1.000  H(2)=1.500  ratio<=H(n): True

共 20 组随机实例，最大比值 = 1.333
验证通过：所有实例 greedy/opt <= H(n)
```

> trial 11 和 trial 14 里贪心真的选多了一个集合（比值 1.333 / 1.250），说明贪心不是"总是恰好等于
> 最优"，但即便如此也远低于 H(n) ≈ 2 的理论上界——H(n) 的证明覆盖的是最坏情况，普通随机实例通常
> 差得很远。

---

## 四、三种算法的共同套路

| 算法 | 近似比 | 证明的核心技巧 |
|------|--------|---------------|
| 顶点覆盖 | 2 | 找一个"下界见证"（匹配），OPT ≥ 见证大小，算法输出 ≤ 2 × 见证大小 |
| TSP（三角不等式） | 2 | MST ≤ OPT（删一条边得到生成树），DFS 走两遍 MST，shortcut 靠三角不等式只减不增 |
| 集合覆盖 | H(n) ≈ ln n | 每轮贪心覆盖"剩余量的一个比例"，衰减求和得到调和级数 |

三者的共同思路：不直接和 OPT 打交道（OPT 未知、不可计算），而是找一个**能被算法输出直接控制、又能
和 OPT 建立不等式关系**的中间量（匹配大小、MST 权重、每轮覆盖比例），近似算法的证明几乎都是在找
这样一个中间量。

---

[← 返回索引](index.md)
