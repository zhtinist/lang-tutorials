# 最短路径进阶 · Shortest Path Advanced

> Dijkstra 和 Floyd-Warshall 已经在 [graph-basics.md](graph-basics.md) 里，这里补三个更进阶的最短路算法。

---

## 一、Bellman-Ford 算法

> 适用于含负权边的图，且能检测负环。CLRS 第 24 章。

**核心思路**：对所有边做 V-1 轮松弛。

**为什么 V-1 轮就够了**：一条最短简单路径最多包含 V-1 条边（V 个顶点最多经过 V-1 条边而不重复顶点）。每一轮松弛至少能把路径长度为 i 的最短路径正确地传播到长度为 i+1，所以 V-1 轮后，所有"简单路径"对应的最短距离都已收敛。如果图中存在从起点可达的负环，那么"最短路径"本身没有下界（可以无限绕环变小），第 V 轮松弛时一定还能找到可以继续变小的边——这就是检测负环的依据。

```python
def bellman_ford(n: int, edges: list[tuple[int, int, int]], start: int) -> list[float] | None:
    """
    单源最短路径，边列表 edges = [(u, v, w), ...]，允许负权边。
    返回 dist 数组；如果从 start 可达负环，返回 None。

    核心：最短简单路径最多经过 V-1 条边，所以 V-1 轮松弛必然让
    所有简单路径的距离收敛。第 V 轮如果还能松弛，说明存在负环。
    """
    INF = float("inf")
    dist: list[float] = [INF] * n
    dist[start] = 0

    for _ in range(n - 1):
        updated = False
        for u, v, w in edges:
            if dist[u] != INF and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                updated = True
        if not updated:  # 提前收敛，剪枝（不再有更新就可以提前退出）
            break

    # 第 V 轮：如果还能松弛，说明存在负环
    for u, v, w in edges:
        if dist[u] != INF and dist[u] + w < dist[v]:
            return None  # 存在负环

    return dist
```

| 特性 | 说明 |
|------|------|
| 复杂度 | O(V·E)，比 Dijkstra 的 O(E log V) 慢 |
| 负权边 | 支持 |
| 负环检测 | 支持（第 V 轮还能松弛 ⟺ 存在负环） |
| 输入格式 | 边列表，与 [graph-basics.md](graph-basics.md) 的 Floyd-Warshall 一致 |

---

## 二、DAG 单源最短路径

> 图是有向无环图 (DAG) 时，不需要 Dijkstra 或 Bellman-Ford ——
> 按拓扑序处理顶点，每个顶点的出边只需要松弛一次，O(V+E) 搞定，还天然支持负权边。

**为什么按拓扑序处理就够了**：拓扑序保证处理顶点 u 时，所有能到达 u 的边都已经被处理过，也就是 `dist[u]` 已经是最终值，之后不会再被更新。于是对 u 的每条出边松弛一次即可，不需要像 Dijkstra 那样反复弹队列，也不需要像 Bellman-Ford 那样跑 V-1 轮。

复用 [graph-basics.md 4.2 节](graph-basics.md) 里的 Kahn 算法风格（这里图上带权重，所以邻接表存 `(v, w)` 而不是纯 `v`）：

```python
from collections import deque


def topological_sort_kahn_weighted(graph: list[list[tuple[int, int]]]) -> list[int]:
    """
    Kahn 算法的带权版本，邻接表 graph[u] = [(v, w), ...]。
    统计入度，每次取入度为 0 的节点。如果有环，返回列表长度 < 节点数。
    """
    n = len(graph)
    indegree = [0] * n
    for u in range(n):
        for v, _ in graph[u]:
            indegree[v] += 1

    queue: deque[int] = deque(i for i in range(n) if indegree[i] == 0)
    order: list[int] = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v, _ in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)

    return order  # len(order) < n 则存在环（说明输入不是 DAG）


def dag_shortest_path(graph: list[list[tuple[int, int]]], start: int) -> list[float]:
    """
    DAG 上的单源最短路径。邻接表 graph[u] = [(v, w), ...]，w 可以为负。
    按拓扑序松弛每个顶点的出边，处理到 u 时 dist[u] 已经是最终值。
    """
    INF = float("inf")
    n = len(graph)
    order = topological_sort_kahn_weighted(graph)

    dist: list[float] = [INF] * n
    dist[start] = 0

    for u in order:
        if dist[u] == INF:
            continue
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w

    return dist
```

| 特性 | 说明 |
|------|------|
| 复杂度 | O(V+E)，三种最短路算法里最快 |
| 负权边 | 支持（只要无环） |
| 适用范围 | 仅限 DAG |
| 也可用于 | 求 DAG 上的最长路径（把权重取反再跑一遍） |

---

## 三、Johnson 算法（稀疏图全源最短路）

> 全源最短路径可以直接跑 Floyd-Warshall（O(V³)），但当图很稀疏（E ≪ V²）时，
> 对每个点跑一次 Dijkstra 总共是 O(V·E log V)，比 O(V³) 快得多。
> 问题是 Dijkstra 不支持负权边——Johnson 算法用"重新赋权"技巧把负权图转换成非负权图，再套用 Dijkstra。

**重新赋权的技巧**：

1. 加一个虚拟源点 `s`，向图中每个顶点连一条权重为 0 的边。
2. 以 `s` 为起点跑一次 Bellman-Ford，得到每个顶点的势 `h(v)`（即 s 到 v 的最短距离）。如果检测到负环，说明原图有负环，Johnson 算法不适用，直接返回失败。
3. 对每条原边 `(u, v, w)` 重新赋权：`w'(u, v) = w(u, v) + h(u) - h(v)`。
   由三角不等式 `h(v) <= h(u) + w(u, v)`，可以保证 `w'(u, v) >= 0`。
4. 用重新赋权后的图，对每个顶点跑一次 Dijkstra，得到 `d'(u, v)`。
5. 还原真实距离：`d(u, v) = d'(u, v) - h(u) + h(v)`
   （这一步成立是因为任意一条 u 到 v 的路径，重新赋权后总代价变化量恒为 `h(u) - h(v)`，与具体走哪条路径无关，所以最短路径的相对大小关系不变，只需要减回偏移量）。

```python
import heapq


def johnson(n: int, edges: list[tuple[int, int, int]]) -> list[list[float]] | None:
    """
    Johnson 算法：稀疏图的全源最短路径，支持负权边（但不能有负环）。
    edges = [(u, v, w), ...]，返回 dist[u][v]；如果存在负环，返回 None。

    比 Floyd-Warshall 的 O(V^3) 更适合 E << V^2 的稀疏图：
    整体复杂度 O(V*E + V*E*log(V))（一次 Bellman-Ford + V 次 Dijkstra）。
    """
    INF = float("inf")

    def bellman_ford_from(source: int, m: int, es: list[tuple[int, int, int]]) -> list[float] | None:
        dist: list[float] = [INF] * m
        dist[source] = 0
        for _ in range(m - 1):
            updated = False
            for u, v, w in es:
                if dist[u] != INF and dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    updated = True
            if not updated:
                break
        for u, v, w in es:
            if dist[u] != INF and dist[u] + w < dist[v]:
                return None
        return dist

    def dijkstra_local(graph: list[list[tuple[int, int]]], start: int) -> list[float]:
        m = len(graph)
        dist: list[float] = [INF] * m
        dist[start] = 0
        heap: list[tuple[int, int]] = [(0, start)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for v, w in graph[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v))
        return dist

    # 1. 加虚拟源点 n，向所有真实顶点连 0 权边
    aug_edges = list(edges) + [(n, v, 0) for v in range(n)]
    h = bellman_ford_from(n, n + 1, aug_edges)
    if h is None:
        return None  # 原图存在负环

    # 2. 重新赋权：w'(u,v) = w(u,v) + h(u) - h(v)，保证非负
    graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for u, v, w in edges:
        graph[u].append((v, w + h[u] - h[v]))

    # 3. 对每个顶点跑 Dijkstra，再还原真实距离
    dist = [[INF] * n for _ in range(n)]
    for u in range(n):
        d = dijkstra_local(graph, u)
        for v in range(n):
            if d[v] < INF:
                dist[u][v] = d[v] - h[u] + h[v]  # 4. 还原

    return dist
```

| 特性 | 说明 |
|------|------|
| 复杂度 | O(V·E + V·E·log V)，稀疏图下优于 Floyd-Warshall 的 O(V³) |
| 负权边 | 支持（前提是无负环） |
| 负环检测 | 通过第一步的 Bellman-Ford 完成 |
| 依赖 | 内部复用 Bellman-Ford（求势 h）+ Dijkstra（多源查询） |

---

## 四、最短路径算法对比总结

| 算法 | 适用图 | 复杂度 | 单源/全源 | 负权 | 负环检测 | 出处 |
|------|--------|--------|:---:|:---:|:---:|------|
| BFS | 无权图 | O(V+E) | 单源 | - | - | [BFS框架](bfs-framework.md) |
| Dijkstra | 非负权 | O(E log V) | 单源 | 否 | 否 | [graph-basics.md](graph-basics.md) |
| Bellman-Ford | 任意 | O(V·E) | 单源 | 是 | 是 | 本文一 |
| DAG 最短路 | 有向无环图 | O(V+E) | 单源 | 是 | 不适用（无环） | 本文二 |
| Floyd-Warshall | 任意（稠密图更优） | O(V³) | 全源 | 是 | 是（对角线变负） | [graph-basics.md](graph-basics.md) |
| Johnson | 任意（稀疏图更优） | O(V·E + V·E log V) | 全源 | 是 | 是 | 本文三 |

**怎么选**：

- 无权图 → BFS。
- 有权、无负边 → Dijkstra（单源）。
- 有负权边、需要单源 → Bellman-Ford；如果确定是 DAG，直接用拓扑序做 O(V+E) 的 DAG 最短路。
- 全源最短路 → 稠密图 (E ≈ V²) 用 Floyd-Warshall；稀疏图 (E ≪ V²) 用 Johnson。

---

## 五、相关笔记链接

- [graph-basics.md](graph-basics.md) — Dijkstra、Floyd-Warshall、拓扑排序（Kahn / DFS）
- [BFS框架](bfs-framework.md) — 无权图最短路径
- [堆](heap-priority-queue.md) — Dijkstra / Johnson 用到的优先队列

---

[← 返回索引](index.md)
