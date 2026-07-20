# 并查集 · Union-Find / Disjoint Set Union (DSU)

> 并查集解决**连通性**问题。两个操作：`union`（合并）和 `find`（查找所属集合）。
> 优化：**路径压缩** + **按秩合并**，均摊时间复杂度 O(α(n)) ≈ O(1)。

---

## 一、基础实现

```python
class UnionFind:
    """带路径压缩和按秩合并的并查集。"""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))  # 每个节点的父节点
        self.rank = [0] * n           # 每棵树的秩（高度上界）
        self.count = n                 # 连通分量数

    def find(self, x: int) -> int:
        """查找 x 的根节点，带路径压缩。"""
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        """
        合并 x 和 y 所在的集合。
        返回 True 表示成功合并，False 表示已经在同一集合中。
        """
        px, py = self.find(x), self.find(y)
        if px == py:
            return False  # 已经在同一集合中

        # 按秩合并：把小的树挂到大的树上
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1

        self.count -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        """判断 x 和 y 是否连通。"""
        return self.find(x) == self.find(y)
```

### 路径压缩图解

```
find(4) 前：              find(4) 后（压缩）：
    0                         0
   /                        /|\
  1                        1 2 3
 /                          |
2                           4
|
3
|
4

压缩后 4 直接指向根节点 0，后续 find 只需 O(1)。
```

---

## 二、应用场景

### 2.1 连通分量计数 · [LC 323](https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/)（会员题）

```python
def count_components(n: int, edges: list[list[int]]) -> int:
    """无向图中连通分量的数量。"""
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.count
```

### 2.2 省份数量 · [LC 547](https://leetcode.com/problems/number-of-provinces/)

```python
def find_circle_num(is_connected: list[list[int]]) -> int:
    """省份数量 = 连通分量数。"""
    n = len(is_connected)
    uf = UnionFind(n)

    for i in range(n):
        for j in range(i + 1, n):
            if is_connected[i][j]:
                uf.union(i, j)

    return uf.count
```

### 2.3 冗余连接 · [LC 684](https://leetcode.com/problems/redundant-connection/)

```python
def find_redundant_connection(edges: list[list[int]]) -> list[int]:
    """
    一棵树多了一条边形成环，找到多余的那条边。
    策略：依次加边，如果边的两个端点已经连通，说明这条边是多余的。
    """
    n = len(edges)
    uf = UnionFind(n + 1)  # 节点从 1 开始编号

    for u, v in edges:
        if not uf.union(u, v):
            return [u, v]  # 已经连通，这条边是多余的

    return []
```

### 2.4 等式方程的可满足性 · [LC 990](https://leetcode.com/problems/satisfiability-of-equality-equations/)

```python
def equations_possible(equations: list[str]) -> bool:
    """
    先处理 '==' 把相等的变量合并，
    再处理 '!=' 检查被标记为不等的变量是否在同一个集合中。
    """
    uf = UnionFind(26)  # 26 个小写字母

    # 第一遍：合并所有等式
    for eq in equations:
        if eq[1] == "=":
            x = ord(eq[0]) - ord("a")
            y = ord(eq[3]) - ord("a")
            uf.union(x, y)

    # 第二遍：检查不等式
    for eq in equations:
        if eq[1] == "!":
            x = ord(eq[0]) - ord("a")
            y = ord(eq[3]) - ord("a")
            if uf.connected(x, y):
                return False

    return True
```

---

## 三、岛屿问题与并查集

### [LC 200](https://leetcode.com/problems/number-of-islands/) 岛屿数量（并查集解法）

```python
def num_islands_uf(grid: list[list[str]]) -> int:
    """并查集解法（通常 BFS/DFS 更简洁）。"""
    if not grid:
        return 0

    m, n = len(grid), len(grid[0])
    uf = UnionFind(m * n)
    water_count = 0

    directions = [(0, 1), (1, 0)]  # 只往右和下合并以避免重复

    for i in range(m):
        for j in range(n):
            if grid[i][j] == "0":
                water_count += 1
            else:
                for di, dj in directions:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] == "1":
                        uf.union(i * n + j, ni * n + nj)

    return uf.count - water_count  # 总连通分量 - 水域数
```

### [LC 130](https://leetcode.com/problems/surrounded-regions/) 被围绕的区域（并查集解法）

```python
def solve_surrounded(board: list[list[str]]) -> None:
    """
    把所有被 'X' 围绕的 'O' 改成 'X'。
    思路：边界上的 'O' 与一个虚拟节点相连，最后不与虚拟节点连通的 'O' 就是被围绕的。
    """
    if not board:
        return

    m, n = len(board), len(board[0])
    uf = UnionFind(m * n + 1)  # 多一个虚拟节点
    dummy = m * n

    for i in range(m):
        for j in range(n):
            if board[i][j] == "O":
                # 边界上的 O 连到虚拟节点
                if i == 0 or i == m - 1 or j == 0 or j == n - 1:
                    uf.union(i * n + j, dummy)
                # 与相邻的 O 合并
                for di, dj in [(0, 1), (1, 0)]:
                    ni, nj = i + di, j + dj
                    if 0 <= ni < m and 0 <= nj < n and board[ni][nj] == "O":
                        uf.union(i * n + j, ni * n + nj)

    for i in range(m):
        for j in range(n):
            if board[i][j] == "O" and not uf.connected(i * n + j, dummy):
                board[i][j] = "X"
```

---

## 四、变体：带权并查集

> 每个边有**权重**，需要维护节点到根的路径和。用于解决**变量除法**等问题。

### [LC 399](https://leetcode.com/problems/evaluate-division/) 除法求值

```python
from collections import defaultdict


def calc_equation(
    equations: list[list[str]],
    values: list[float],
    queries: list[list[str]],
) -> list[float]:
    """带权并查集。"""
    parent: dict[str, str] = {}
    weight: dict[str, float] = {}  # weight[x] = x / parent[x]

    def find(x: str) -> str:
        if parent[x] != x:
            orig_parent = parent[x]
            parent[x] = find(parent[x])
            weight[x] *= weight[orig_parent]  # 路径压缩时更新权重
        return parent[x]

    def union(x: str, y: str, val: float) -> None:
        """x / y = val"""
        px, py = find(x), find(y)
        if px == py:
            return
        # 把 px 挂到 py 上
        parent[px] = py
        # weight[px] = (x / y) * (y / py) / (x / px) = val * weight[y] / weight[x]
        weight[px] = val * weight[y] / weight[x]

    # 初始化
    for a, b in equations:
        if a not in parent:
            parent[a] = a
            weight[a] = 1.0
        if b not in parent:
            parent[b] = b
            weight[b] = 1.0

    # 构建
    for (a, b), val in zip(equations, values):
        union(a, b, val)

    # 查询
    ans: list[float] = []
    for a, b in queries:
        if a not in parent or b not in parent:
            ans.append(-1.0)
        else:
            pa, pb = find(a), find(b)
            if pa != pb:
                ans.append(-1.0)  # 不连通
            else:
                ans.append(weight[a] / weight[b])  # a/b

    return ans
```

---

## 五、总结

| 操作 | 复杂度 | 说明 |
|------|--------|------|
| `find(x)` | 均摊 O(α(n)) | 路径压缩 |
| `union(x, y)` | 均摊 O(α(n)) | 按秩合并 |
| `connected(x, y)` | 均摊 O(α(n)) | 两次 find |
| 总体 | ≈ O(1) | α(n) 增长极慢 |

### 应用场景清单

| 场景 | 说明 |
|------|------|
| 连通分量计数 | 初始 count=n，每次合并 count-- |
| 检测图中的环 | 合并前判断 connected |
| 动态连通性 | 在线查询连通性 |
| 等式/不等式 | 先合并等式，再验证不等式 |
| 岛屿问题 | 可作为 DFS/BFS 的替代 |
| 除法求值 | 带权并查集 |

---

## 六、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 547](https://leetcode.com/problems/number-of-provinces/) | Number of Provinces | Medium | 连通分量 |
| [LC 323](https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/) | Number of Connected Components | Medium🔒 | 连通分量 |
| [LC 684](https://leetcode.com/problems/redundant-connection/) | Redundant Connection | Medium | 检测环 |
| [LC 685](https://leetcode.com/problems/redundant-connection-ii/) | Redundant Connection II | Hard | 有向图环 |
| [LC 990](https://leetcode.com/problems/satisfiability-of-equality-equations/) | Satisfiability of Equations | Medium | 等式不等式 |
| [LC 200](https://leetcode.com/problems/number-of-islands/) | Number of Islands | Medium | BFS/DFS/UF |
| [LC 130](https://leetcode.com/problems/surrounded-regions/) | Surrounded Regions | Medium | 边界+虚拟节点 |
| [LC 399](https://leetcode.com/problems/evaluate-division/) | Evaluate Division | Medium | 带权并查集 |
| [LC 721](https://leetcode.com/problems/accounts-merge/) | Accounts Merge | Medium | 字符串并查集 |
| [LC 1202](https://leetcode.com/problems/smallest-string-with-swaps/) | Smallest String With Swaps | Medium | 连通组内排序 |
| [LC 952](https://leetcode.com/problems/largest-component-size-by-common-factor/) | Largest Component Size | Hard | 因数+并查集 |

---

[← 返回索引](index.md)
