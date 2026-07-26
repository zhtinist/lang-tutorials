# 最大流 · Maximum Flow

> 网络流：每条边有"容量"上限，问从源点 s 到汇点 t 最多能同时"流"多少。
> 看似是一个很物理的模型（水管、电路），但大量组合优化问题（二分图匹配、任务分配、图的连通性下界）
> 都可以"翻译"成最大流问题来解决——这是它在算法竞赛/面试里真正的价值。

---

## 一、核心概念：残量网络

```
容量 capacity(u, v)：边 u→v 最多能流多少。
流量 flow(u, v)：当前实际流了多少，必须满足 0 <= flow(u,v) <= capacity(u,v)。

残量网络 (Residual Graph)：
  - 正向残量 = capacity(u,v) - flow(u,v)：还能再往这个方向流多少
  - 反向残量 = flow(u,v)：可以"反悔"，退回已经流过的量

关键技巧：即使原图没有 v→u 这条边，只要 u→v 流过东西，
残量网络里就会有一条容量为 flow(u,v) 的反向边——这条"反悔边"是 Ford-Fulkerson 方法能找到
全局最优解的核心（如果没有反悔机制，贪心地选路径可能卡在局部最优）。
```

### 1.1 Ford-Fulkerson 方法（不是具体算法，是一套框架）

```
只要残量网络里还存在一条从 s 到 t 的路径（增广路径augmenting path），
就沿着这条路径增加流量（增加量 = 路径上所有边残量的最小值），
同时更新残量网络（正向残量减少，反向残量增加）。
直到残量网络里再也找不到 s 到 t 的路径为止——此时的总流量就是最大流
（这是最大流最小割定理保证的：最大流 = 最小割的容量）。

"怎么找增广路径"是自由的——用 DFS 找，可能很慢（最坏情况下每次只增加1点流量，
如果容量是大整数，迭代次数可能是指数级）；用 BFS 找（每次找"边数最少"的增广路径），
就是下面的 Edmonds-Karp 算法，能保证多项式时间。
```

---

## 二、Edmonds-Karp（BFS 版 Ford-Fulkerson）

```python
from collections import deque, defaultdict


def edmonds_karp(n: int, edges: list[tuple[int, int, int]], s: int, t: int) -> int:
    """
    edges: (u, v, capacity) 列表。返回 s 到 t 的最大流量。
    每次用 BFS 找一条边数最少的增广路径，保证 O(VE^2)。
    """
    capacity: dict[tuple[int, int], int] = defaultdict(int)
    adj: dict[int, set[int]] = defaultdict(set)
    for u, v, c in edges:
        capacity[(u, v)] += c   # 支持重边：容量累加
        adj[u].add(v)
        adj[v].add(u)           # 反向边一开始容量是0，但残量图里必须能访问到

    max_flow = 0
    while True:
        # BFS 找一条 s -> t 的增广路径（只走残量 > 0 的边）
        parent: dict[int, int | None] = {s: None}
        queue = deque([s])
        while queue:
            u = queue.popleft()
            if u == t:
                break
            for v in adj[u]:
                if v not in parent and capacity[(u, v)] > 0:
                    parent[v] = u
                    queue.append(v)

        if t not in parent:
            break  # 找不到增广路径了，已经是最大流

        # 找这条路径上的瓶颈（最小残量）
        path_flow = float("inf")
        v = t
        while parent[v] is not None:
            u = parent[v]
            path_flow = min(path_flow, capacity[(u, v)])
            v = u

        # 沿路径更新残量：正向减少，反向增加（"反悔"的容量）
        v = t
        while parent[v] is not None:
            u = parent[v]
            capacity[(u, v)] -= path_flow
            capacity[(v, u)] += path_flow
            v = u

        max_flow += path_flow

    return max_flow
```

### 2.1 正确性验证

```python
# CLRS 图26.1 的经典例子
edges = [
    (0, 1, 16), (0, 2, 13), (1, 2, 10), (2, 1, 4), (1, 3, 12),
    (2, 4, 14), (3, 2, 9), (4, 3, 7), (3, 5, 20), (4, 5, 4),
]
print("经典例子最大流:", edmonds_karp(6, edges, 0, 5), "(书上答案是 23)")

# 用暴力枚举所有 s-t 割，通过最大流最小割定理交叉验证
import random
import itertools


def brute_force_min_cut(n: int, edges: list[tuple[int, int, int]], s: int, t: int) -> int:
    """暴力枚举所有把节点分成 (含s的一边, 含t的一边) 的方式，求最小割容量。"""
    best = float("inf")
    others = [x for x in range(n) if x != s and x != t]
    for r in range(len(others) + 1):
        for combo in itertools.combinations(others, r):
            s_side = set([s]) | set(combo)
            if t in s_side:
                continue
            cut_cap = sum(c for u, v, c in edges if u in s_side and v not in s_side)
            best = min(best, cut_cap)
    return best


random.seed(0)
fail = 0
trials = 0
for _ in range(60):
    n = random.randint(3, 6)
    s, t = 0, n - 1
    edges = [
        (u, v, random.randint(1, 10))
        for u in range(n) for v in range(n)
        if u != v and random.random() < 0.4
    ]
    if not edges:
        continue
    trials += 1
    if edmonds_karp(n, edges, s, t) != brute_force_min_cut(n, edges, s, t):
        fail += 1

print(f"最大流 vs 暴力枚举最小割：{trials} 次随机测试，不匹配 {fail} 次")
```

---

## 三、应用：最大二分图匹配

```
二分图匹配（左边 L 个点，右边 R 个点，只在允许的 (u,v) 对之间连边，
求最多能同时匹配多少对，每个点最多被匹配一次）可以直接"翻译"成最大流问题：

  建一个虚拟源点 S，虚拟汇点 T
  S -> 每个左边节点，容量 1（每个左边节点最多被用一次）
  每个右边节点 -> T，容量 1（每个右边节点最多被用一次）
  原图里允许的 (u, v) -> 容量 1

这张图的最大流 = 二分图的最大匹配数。直觉：一条 S->u->v->T 的完整流路径
恰好对应"左边 u 匹配右边 v"这一对，因为每条边容量都是1，一条路径用满了
就不能再有第二条路径经过同一个 u 或 v。
```

```python
def max_bipartite_matching(left_n: int, right_n: int, edges: list[tuple[int, int]]) -> int:
    """edges: (左节点下标, 右节点下标)。返回最大匹配数。"""
    S, T = "S", "T"
    flow_edges: list[tuple] = []
    for u in range(left_n):
        flow_edges.append((S, ("L", u), 1))
    for v in range(right_n):
        flow_edges.append((("R", v), T, 1))
    for u, v in edges:
        flow_edges.append((("L", u), ("R", v), 1))

    # 直接内联一份支持任意可哈希节点标签的 Edmonds-Karp（跟上面逻辑完全一样，只是节点不限于整数）
    capacity: dict[tuple, int] = defaultdict(int)
    adj: dict = defaultdict(set)
    for u, v, c in flow_edges:
        capacity[(u, v)] += c
        adj[u].add(v)
        adj[v].add(u)

    max_flow = 0
    while True:
        parent = {S: None}
        queue = deque([S])
        while queue:
            u = queue.popleft()
            if u == T:
                break
            for v in adj[u]:
                if v not in parent and capacity[(u, v)] > 0:
                    parent[v] = u
                    queue.append(v)
        if T not in parent:
            break
        path_flow = float("inf")
        v = T
        while parent[v] is not None:
            u = parent[v]
            path_flow = min(path_flow, capacity[(u, v)])
            v = u
        v = T
        while parent[v] is not None:
            u = parent[v]
            capacity[(u, v)] -= path_flow
            capacity[(v, u)] += path_flow
            v = u
        max_flow += path_flow

    return max_flow
```

### 3.1 正确性验证（对照暴力枚举匹配）

```python
def brute_force_matching(left_n: int, right_n: int, edges: list[tuple[int, int]]) -> int:
    adj: dict[int, list[int]] = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
    best = 0

    def backtrack(u: int, used_right: set[int], count: int) -> None:
        nonlocal best
        if u == left_n:
            best = max(best, count)
            return
        backtrack(u + 1, used_right, count)  # 不匹配 u
        for v in adj[u]:
            if v not in used_right:
                used_right.add(v)
                backtrack(u + 1, used_right, count + 1)
                used_right.remove(v)

    backtrack(0, set(), 0)
    return best


random.seed(1)
fail2 = 0
trials2 = 0
for _ in range(40):
    left_n = random.randint(1, 5)
    right_n = random.randint(1, 5)
    edges_bm = [(u, v) for u in range(left_n) for v in range(right_n) if random.random() < 0.5]
    trials2 += 1
    got = max_bipartite_matching(left_n, right_n, edges_bm)
    want = brute_force_matching(left_n, right_n, edges_bm)
    if got != want:
        fail2 += 1

print(f"二分图匹配 vs 暴力枚举：{trials2} 次随机测试，不匹配 {fail2} 次")
```

---

## 四、推送-重贴标签算法（简介，不实现）

Edmonds-Karp 每次只找一条增广路径，效率受限于"找路径"这个串行过程。
**推送-重贴标签 (Push-Relabel)** 换了个思路：不找完整路径，而是让每个节点维护一个"高度"标签
和"超额流量"（比流入多流出的部分），让超额流量像水一样只往"更低"的相邻节点推送，
配合"重贴标签"（抬高一个节点的高度，让它能继续往外推送）逐步收敛到最大流。

不需要一次性想清楚"整条路径"，只需要局部地看"这个点和它邻居的高度差"，
复杂度可以做到 O(V²E) 甚至更优（前置重贴标签变体是 O(V³)）——但实现和调试比 Edmonds-Karp 复杂得多，
工程上只有在 Edmonds-Karp/Dinic 效率明显不够时才会考虑。

---

## 五、复杂度与选择

| 算法 | 复杂度 | 特点 |
|------|--------|------|
| Ford-Fulkerson（DFS找增广路） | O(E · max_flow) | 只保证整数容量下终止，容量大时可能很慢 |
| Edmonds-Karp（BFS找增广路） | O(VE²) | 实现简单，多项式时间有保证，本文实现的版本 |
| Dinic 算法 | O(V²E)，二分图上 O(E√V) | 用分层图+多路增广，比 Edmonds-Karp 快，实现更复杂，未在本文实现 |
| 推送-重贴标签 | O(V²E) ~ O(V³) | 局部操作，理论最优，实现复杂 |

---

[← 返回索引](index.md)
