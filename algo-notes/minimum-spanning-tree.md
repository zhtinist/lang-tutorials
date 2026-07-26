# 最小生成树补充 · Prim's Algorithm

> Kruskal 算法已经在 [graph-basics.md](graph-basics.md) 的「六、最小生成树」一节里，这里只补 Prim。

---

## 一、核心思想：与 Kruskal 的对比

两种算法都是贪心，但贪心的对象不同：

- **Kruskal**：维护一个**森林**（多棵树），每次从全局边集中挑最小的一条边，只要它不会在森林里形成环就加入——森林逐渐合并成一棵树。
- **Prim**：只维护**一棵树**，从任意一个起点开始生长，每一步从"树内顶点"到"树外顶点"的所有跨界边中，挑权重最小的一条加入——树逐渐吞并所有顶点。

一句话对比：Kruskal 是"按边的全局顺序贪心"，Prim 是"按当前树的边界贪心"。

---

## 二、堆实现（邻接表）

> 邻接表表示与 [graph-basics.md](graph-basics.md) 的 Dijkstra 完全一致：`graph[u] = [(v, weight), ...]`（无向图需要双向建边）。这让 Prim 和 Dijkstra 成为直接的类比：Dijkstra 维护"起点到每个点的最短距离"，Prim 维护"树到每个点的最小连接权重"，两者都用小根堆 + 懒惰删除实现。

```python
import heapq


def prim_mst(
    graph: list[list[tuple[int, int]]], start: int = 0
) -> tuple[int, list[tuple[int, int, int]]]:
    """
    邻接表 graph[u] = [(v, weight), ...]（无向图，需双向建边）。
    从 start 出发生长一棵树，每步用堆取出当前树到树外的最小跨界边。
    返回 (MST 总权重, MST 边列表)。图必须连通，否则返回的边数 < n-1。
    """
    n = len(graph)
    visited = [False] * n
    mst_edges: list[tuple[int, int, int]] = []
    total_weight = 0

    heap: list[tuple[int, int, int]] = [(0, start, -1)]  # (weight, vertex, from)

    while heap and len(mst_edges) < n - 1:
        w, u, parent = heapq.heappop(heap)
        if visited[u]:  # 懒惰删除：这个堆条目已经过时（和 Dijkstra 的 if d > dist[u]: continue 同一个套路）
            continue
        visited[u] = True
        if parent != -1:
            mst_edges.append((parent, u, w))
            total_weight += w

        for v, weight in graph[u]:
            if not visited[v]:
                heapq.heappush(heap, (weight, v, u))

    return total_weight, mst_edges
```

和 Dijkstra 的对照：

| | Dijkstra | Prim |
|---|---|---|
| 堆里存什么 | `(距离, 节点)` | `(权重, 节点, 来源)` |
| 贪心的量 | 起点到该点的**最短距离** | 树到该点的**最小连接权重** |
| 松弛条件 | `nd < dist[v]` 才入堆 | 只要 `v` 未访问就入堆（不比较，靠懒惰删除去重） |
| 懒惰删除 | `if d > dist[u]: continue` | `if visited[u]: continue` |

---

## 三、复杂度

| 实现 | 复杂度 |
|------|--------|
| 二叉堆（本文实现） | O(E log V) —— 和 Dijkstra 的二叉堆版本同阶 |
| 斐波那契堆 | O(E + V log V) |

用二叉堆时每条边最多入堆一次，堆操作 O(log V)，所以是 O(E log V)。如果换成斐波那契堆（`decrease-key` 均摊 O(1)），可以把复杂度降到 O(E + V log V)，做法和结构见 [fibonacci-heap.md](fibonacci-heap.md)。

---

## 四、Kruskal vs Prim 该用哪个

| | Kruskal | Prim |
|------|---------|------|
| 维护结构 | 并查集 + 排序后的边表 | 一棵树 + 优先队列 |
| 适合的图 | **稀疏图**（E 接近 V），或者数据天然是边表 | **稠密图**（E 接近 V²） |
| 复杂度瓶颈 | 排序边：O(E log E) | 出堆/入堆：O(E log V) |
| 直觉 | 全局看边，不关心顶点顺序 | 局部扩张，天然适合"从某个点开始" |
| 实现复杂度 | 需要并查集 | 需要邻接表 + 堆 |

E 和 V log V 接近时两者差不多；E 远小于 V² 时优先 Kruskal（排序成本低）；图很稠密（邻接矩阵级别）或图本身就是邻接表结构时优先 Prim。

---

## 五、相关笔记链接

- [graph-basics.md](graph-basics.md) — Kruskal 实现、Dijkstra、图的存储方式
- [union-find.md](union-find.md) — Kruskal 依赖的并查集
- [heap-priority-queue.md](heap-priority-queue.md) — Prim/Dijkstra 用到的优先队列
- [fibonacci-heap.md](fibonacci-heap.md) — Prim 的斐波那契堆优化版本

---

[← 返回索引](index.md)
