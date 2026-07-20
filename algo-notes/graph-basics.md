# 图结构基础 · Graph Basics

> 图 = 顶点(Vertices) + 边(Edges)。图比树更一般化：可以有环、可以不连通、边可以有方向有权重。

---

## 一、图的基本概念

| 术语 | 说明 |
|------|------|
| 顶点 (Vertex) | 图中的节点 |
| 边 (Edge) | 连接两个顶点的线 |
| 有向图 | 边有方向 u→v |
| 无向图 | 边无方向 u↔v |
| 权重 (Weight) | 边上的数值（距离、成本） |
| 度 (Degree) | 无向图：与顶点相连的边数 |
| 入度/出度 | 有向图：指向/离开顶点的边数 |
| 路径 (Path) | 顶点序列 v₀→v₁→...→vₙ |
| 环 (Cycle) | 起点=终点的路径 |
| 连通分量 | 无向图中互相可达的最大子图 |
| 强连通分量 | 有向图中互相可达的最大子图 |
| DAG | 有向无环图 (Directed Acyclic Graph) |

---

## 二、图的三种存储方式

### 2.1 邻接矩阵 (Adjacency Matrix)

```python
# graph[i][j] = 权重，0 表示无边
# 适合稠密图 (E ≈ V²)
class AdjacencyMatrix:
    def __init__(self, n: int):
        self.n = n
        self.matrix: list[list[int]] = [[0] * n for _ in range(n)]

    def add_edge(self, u: int, v: int, w: int = 1) -> None:
        self.matrix[u][v] = w
        # 无向图加上下一行
        # self.matrix[v][u] = w

    def neighbors(self, u: int) -> list[int]:
        return [v for v in range(self.n) if self.matrix[u][v] != 0]
```

| 操作 | 复杂度 |
|------|:---:|
| 判断 (u,v) 是否有边 | O(1) |
| 找 u 的所有邻居 | O(V) |
| 空间 | O(V²) |

### 2.2 邻接表 (Adjacency List)

```python
# 每个顶点维护一个邻居列表。最常用的图存储方式。
# 适合稀疏图 (E << V²)
class AdjacencyList:
    def __init__(self, n: int):
        self.n = n
        self.graph: list[list[tuple[int, int]]] = [[] for _ in range(n)]
        # graph[u] = [(v1, w1), (v2, w2), ...]

    def add_edge(self, u: int, v: int, w: int = 1) -> None:
        self.graph[u].append((v, w))
        # 无向图加上:
        # self.graph[v].append((u, w))

    def neighbors(self, u: int) -> list[tuple[int, int]]:
        return self.graph[u]
```

| 操作 | 复杂度 |
|------|:---:|
| 判断 (u,v) 是否有边 | O(degree(u)) |
| 找 u 的所有邻居 | O(degree(u)) |
| 空间 | O(V + E) |

### 2.3 边列表 (Edge List)

```python
# edges = [(u, v, w), ...]
# 适合 Kruskal 最小生成树等按边操作的算法
class EdgeList:
    def __init__(self):
        self.edges: list[tuple[int, int, int]] = []  # (u, v, weight)

    def add_edge(self, u: int, v: int, w: int = 1) -> None:
        self.edges.append((u, v, w))
```

---

## 三、图的遍历

### 3.1 DFS 遍历

```python
def dfs_traverse(graph: list[list[int]]) -> list[int]:
    """图的 DFS 遍历。"""
    n = len(graph)
    visited = [False] * n
    order: list[int] = []

    def dfs(u: int) -> None:
        visited[u] = True
        order.append(u)
        for v in graph[u]:
            if not visited[v]:
                dfs(v)

    # 处理多个连通分量
    for i in range(n):
        if not visited[i]:
            dfs(i)

    return order
```

### 3.2 BFS 遍历

```python
from collections import deque


def bfs_traverse(graph: list[list[int]]) -> list[int]:
    """图的 BFS 遍历。"""
    n = len(graph)
    visited = [False] * n
    order: list[int] = []

    for i in range(n):
        if not visited[i]:
            queue: deque[int] = deque([i])
            visited[i] = True
            while queue:
                u = queue.popleft()
                order.append(u)
                for v in graph[u]:
                    if not visited[v]:
                        visited[v] = True
                        queue.append(v)

    return order
```

---

## 四、环检测与拓扑排序

### 4.1 环检测（有向图）

```python
def has_cycle_directed(graph: list[list[int]]) -> bool:
    """DFS 三色标记法检测有向图环。"""
    WHITE, GRAY, BLACK = 0, 1, 2
    n = len(graph)
    color = [WHITE] * n

    def dfs(u: int) -> bool:
        color[u] = GRAY  # 正在访问
        for v in graph[u]:
            if color[v] == GRAY:
                return True  # 找到后向边 → 有环
            if color[v] == WHITE and dfs(v):
                return True
        color[u] = BLACK  # 访问完成
        return False

    for i in range(n):
        if color[i] == WHITE and dfs(i):
            return True
    return False
```

### 4.2 拓扑排序 (Kahn 算法 BFS)

> [LC 207](https://leetcode.com/problems/course-schedule/) / [LC 210](https://leetcode.com/problems/course-schedule-ii/)

```python
from collections import deque


def topological_sort_kahn(graph: list[list[int]]) -> list[int]:
    """
    Kahn 算法：统计入度，每次取入度为 0 的节点。
    如果有环，返回的列表长度 < 节点数。
    """
    n = len(graph)
    indegree = [0] * n
    for u in range(n):
        for v in graph[u]:
            indegree[v] += 1

    queue: deque[int] = deque(i for i in range(n) if indegree[i] == 0)
    order: list[int] = []

    while queue:
        u = queue.popleft()
        order.append(u)
        for v in graph[u]:
            indegree[v] -= 1
            if indegree[v] == 0:
                queue.append(v)

    return order  # len(order) < n 则存在环
```

### 4.3 拓扑排序 (DFS 后序逆序)

```python
def topological_sort_dfs(graph: list[list[int]]) -> list[int]:
    """DFS 后序遍历的反序 = 拓扑序。"""
    n = len(graph)
    visited = [False] * n
    on_path = [False] * n
    order: list[int] = []

    def dfs(u: int) -> bool:
        """返回 True 表示有环。"""
        if on_path[u]:
            return True
        if visited[u]:
            return False
        visited[u] = on_path[u] = True
        for v in graph[u]:
            if dfs(v):
                return True
        on_path[u] = False
        order.append(u)  # 后序
        return False

    for i in range(n):
        if dfs(i):
            return []

    return order[::-1]  # 后序的反序
```

---

## 五、最短路径算法概览

| 算法 | 适用图 | 复杂度 | 说明 |
|------|--------|--------|------|
| BFS | 无权图 | O(V+E) | 见 [BFS框架](bfs-framework.md) |
| Dijkstra | 非负权 | O(E log V) | 贪心+优先队列 |
| Bellman-Ford | 任意（可有负权） | O(VE) | 可检测负环 |
| SPFA | 任意（队列优化Bellman-Ford） | O(VE)最坏 | 实际快但可能退化 |
| Floyd-Warshall | 任意（全源最短路） | O(V³) | DP，三重循环 |
| A* | 有权图+启发式 | O(E)通常 | 有目标方向的搜索 |

### Dijkstra 算法

```python
import heapq


def dijkstra(graph: list[list[tuple[int, int]]], start: int) -> list[int]:
    """
    邻接表 graph[u] = [(v, weight), ...]
    返回 start 到所有点的最短距离。
    """
    n = len(graph)
    dist = [float("inf")] * n
    dist[start] = 0

    heap = [(0, start)]  # (距离, 节点)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:  # 懒惰删除（旧的距离已过时）
            continue
        for v, w in graph[u]:
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))

    return dist
```

### Floyd-Warshall (全源最短路)

```python
def floyd_warshall(n: int, edges: list[tuple[int, int, int]]) -> list[list[int]]:
    """
    返回所有节点对的最短距离矩阵。
    dp[k][i][j] = min(dp[k-1][i][j], dp[k-1][i][k] + dp[k-1][k][j])
    """
    INF = float("inf")
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0

    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)

    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] < INF and dist[k][j] < INF:
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    return dist
```

---

## 六、最小生成树 (MST)

> 连接所有顶点的、边权重和最小的无环子图。

| 算法 | 数据结构 | 复杂度 |
|------|---------|--------|
| Kruskal | 并查集 + 边排序 | O(E log E) |
| Prim | 优先队列 | O(E log V) |

### Kruskal

```python
def kruskal_mst(n: int, edges: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    """返回最小生成树的边列表。"""
    edges.sort(key=lambda x: x[2])  # 按权重排序
    uf = UnionFind(n)
    mst: list[tuple[int, int, int]] = []

    for u, v, w in edges:
        if uf.union(u, v):
            mst.append((u, v, w))
        if len(mst) == n - 1:
            break

    return mst
```

---

## 七、相关笔记链接

- [BFS框架](bfs-framework.md) — BFS遍历和最短路径
- [并查集](union-find.md) — 连通性 / Kruskal
- [双向BFS](bidirectional-bfs.md) — 双向搜索优化
- [堆](heap-priority-queue.md) — Dijkstra 用到的优先队列

---

[← 返回索引](index.md)
