# BFS & 网格问题 · BFS & Grid Problems

> 网格问题是一类特殊的图问题。DFS 适合**遍历**(岛屿系列)，BFS 适合**最短路径**。
> 多源 BFS：从多个起点同时开始搜索。

---

## 一、网格 DFS 模板（岛屿系列）

### 通用模板

```python
def dfs_grid(grid: list[list[str]], i: int, j: int) -> None:
    """网格 DFS，淹没岛屿 / 标记访问。"""
    m, n = len(grid), len(grid[0])

    # 越界或不是目标格子
    if i < 0 or i >= m or j < 0 or j >= n:
        return
    if grid[i][j] != "1":  # 根据题目修改条件
        return

    # 标记为已访问（淹没）
    grid[i][j] = "0"  # 或 "#"

    # 四个方向
    for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        dfs_grid(grid, i + di, j + dj)
```

### 1.1 岛屿数量 · [LC 200](https://leetcode.com/problems/number-of-islands/)

```python
def num_islands(grid: list[list[str]]) -> int:
    """每遇到一块陆地就 DFS 淹没整个岛屿，计数+1。"""
    if not grid:
        return 0
    m, n = len(grid), len(grid[0])
    count = 0

    def dfs(i: int, j: int) -> None:
        if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] != "1":
            return
        grid[i][j] = "0"
        dfs(i + 1, j)
        dfs(i - 1, j)
        dfs(i, j + 1)
        dfs(i, j - 1)

    for i in range(m):
        for j in range(n):
            if grid[i][j] == "1":
                count += 1
                dfs(i, j)

    return count
```

### 1.2 岛屿最大面积 · [LC 695](https://leetcode.com/problems/max-area-of-island/)

```python
def max_area_of_island(grid: list[list[int]]) -> int:
    """DFS 返回每个岛屿的面积，取最大。"""
    if not grid:
        return 0
    m, n = len(grid), len(grid[0])

    def dfs(i: int, j: int) -> int:
        if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] != 1:
            return 0
        grid[i][j] = 0
        return 1 + dfs(i + 1, j) + dfs(i - 1, j) + dfs(i, j + 1) + dfs(i, j - 1)

    ans = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1:
                ans = max(ans, dfs(i, j))
    return ans
```

### 1.3 封闭岛屿数量 · [LC 1254](https://leetcode.com/problems/number-of-closed-islands/)

```python
def closed_island(grid: list[list[int]]) -> int:
    """四周被水包围的岛屿（不靠边界）。先用 DFS 淹没边界的岛屿。"""
    m, n = len(grid), len(grid[0])

    def dfs(i: int, j: int) -> None:
        if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] != 0:
            return
        grid[i][j] = 1
        dfs(i + 1, j)
        dfs(i - 1, j)
        dfs(i, j + 1)
        dfs(i, j - 1)

    # 淹没边界上的岛屿（及与边界相连的）
    for i in range(m):
        dfs(i, 0)
        dfs(i, n - 1)
    for j in range(n):
        dfs(0, j)
        dfs(m - 1, j)

    # 统计剩余的岛屿
    count = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 0:
                count += 1
                dfs(i, j)
    return count
```

---

## 二、网格 BFS（最短路径）

### 2.1 腐烂橘子 · [LC 994](https://leetcode.com/problems/rotting-oranges/)（多源 BFS）

```python
from collections import deque


def oranges_rotting(grid: list[list[int]]) -> int:
    """
    多源 BFS：所有初始腐烂橘子同时开始扩散。
    返回全部腐烂所需的最少分钟数。
    """
    m, n = len(grid), len(grid[0])
    queue: deque[tuple[int, int]] = deque()
    fresh = 0

    for i in range(m):
        for j in range(n):
            if grid[i][j] == 2:
                queue.append((i, j))
            elif grid[i][j] == 1:
                fresh += 1

    if fresh == 0:
        return 0

    minutes = -1
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        for _ in range(len(queue)):
            i, j = queue.popleft()
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] == 1:
                    grid[ni][nj] = 2
                    fresh -= 1
                    queue.append((ni, nj))
        minutes += 1

    return -1 if fresh > 0 else minutes
```

### 2.2 01 矩阵 · [LC 542](https://leetcode.com/problems/01-matrix/)（多源 BFS 求到 0 的距离）

```python
from collections import deque


def update_matrix(mat: list[list[int]]) -> list[list[int]]:
    """
    多源 BFS：将所有 0 作为起点入队，
    dist 初始化为 -1（未访问），0 的位置 dist=0。
    """
    m, n = len(mat), len(mat[0])
    dist = [[-1] * n for _ in range(m)]
    queue: deque[tuple[int, int]] = deque()

    for i in range(m):
        for j in range(n):
            if mat[i][j] == 0:
                dist[i][j] = 0
                queue.append((i, j))

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        i, j = queue.popleft()
        for di, dj in directions:
            ni, nj = i + di, j + dj
            if 0 <= ni < m and 0 <= nj < n and dist[ni][nj] == -1:
                dist[ni][nj] = dist[i][j] + 1
                queue.append((ni, nj))

    return dist
```

### 2.3 二进制矩阵中的最短路径 · [LC 1091](https://leetcode.com/problems/shortest-path-in-binary-matrix/)

```python
from collections import deque


def shortest_path_binary_matrix(grid: list[list[int]]) -> int:
    """8 方向 BFS，从左上到右下的最短路径。"""
    if grid[0][0] == 1 or grid[-1][-1] == 1:
        return -1

    n = len(grid)
    queue: deque[tuple[int, int, int]] = deque([(0, 0, 1)])  # (r, c, dist)
    grid[0][0] = 1  # 标记已访问

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    while queue:
        r, c, d = queue.popleft()
        if r == n - 1 and c == n - 1:
            return d
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and grid[nr][nc] == 0:
                grid[nr][nc] = 1
                queue.append((nr, nc, d + 1))

    return -1
```

---

## 三、BFS 路径还原

```python
from collections import deque


def bfs_with_path_reconstruction(
    maze: list[list[int]], start: tuple[int, int], end: tuple[int, int]
) -> list[tuple[int, int]] | None:
    """BFS 最短路径 + 还原路径。"""
    m, n = len(maze), len(maze[0])
    queue: deque[tuple[int, int]] = deque([start])
    visited = {start}
    parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    while queue:
        pos = queue.popleft()
        if pos == end:
            # 回溯路径
            path: list[tuple[int, int]] = []
            while pos is not None:
                path.append(pos)
                pos = parent[pos]
            return path[::-1]

        for di, dj in directions:
            nxt = (pos[0] + di, pos[1] + dj)
            if (
                0 <= nxt[0] < m
                and 0 <= nxt[1] < n
                and maze[nxt[0]][nxt[1]] == 0
                and nxt not in visited
            ):
                visited.add(nxt)
                parent[nxt] = pos
                queue.append(nxt)

    return None
```

---

## 四、0-1 BFS 简介

> 当边权只有 0 和 1 时，用 `deque` 替代优先队列：
> 走 0 权边 → 加到队首，走 1 权边 → 加到队尾。

```python
from collections import deque


def zero_one_bfs(grid: list[list[int]]) -> int:
    """0-1 BFS 模板。"""
    m, n = len(grid), len(grid[0])
    dist = [[float("inf")] * n for _ in range(m)]
    dist[0][0] = 0
    queue: deque[tuple[int, int]] = deque([(0, 0)])

    while queue:
        i, j = queue.popleft()
        for di, dj, cost in [(0, 1, 0), (1, 0, 1)]:  # 示例
            ni, nj = i + di, j + dj
            if 0 <= ni < m and 0 <= nj < n:
                nd = dist[i][j] + cost
                if nd < dist[ni][nj]:
                    dist[ni][nj] = nd
                    if cost == 0:
                        queue.appendleft((ni, nj))
                    else:
                        queue.append((ni, nj))
    return int(dist[m - 1][n - 1])
```

---

## 五、总结

| 场景 | 方法 | 特点 |
|------|------|------|
| 岛屿面积/数量 | DFS | 递归简洁，可能爆栈 |
| 岛屿问题（统一框架） | BFS/DFS | BFS 不会爆栈 |
| 最短路径（无权） | BFS | 首次到达=最短 |
| 最短路径（需要还原） | BFS + parent | 记录每个节点的前驱 |
| 多源最短路径 | 多源 BFS | 所有起点同时入队 |
| 0-1 边权 | 0-1 BFS | deque 维护优先 |
| 一般权重 | Dijkstra | 优先队列 |

---

## 六、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 200](https://leetcode.com/problems/number-of-islands/) | Number of Islands | Medium | 岛屿DFS模板 |
| [LC 463](https://leetcode.com/problems/island-perimeter/) | Island Perimeter | Easy | 遍历边界 |
| [LC 695](https://leetcode.com/problems/max-area-of-island/) | Max Area of Island | Medium | DFS求面积 |
| [LC 1254](https://leetcode.com/problems/number-of-closed-islands/) | Number of Closed Islands | Medium | 淹边界+计数 |
| [LC 1020](https://leetcode.com/problems/number-of-enclaves/) | Number of Enclaves | Medium | 同封闭岛屿 |
| [LC 1905](https://leetcode.com/problems/count-sub-islands/) | Count Sub Islands | Medium | 同时DFS两个网格 |
| [LC 994](https://leetcode.com/problems/rotting-oranges/) | Rotting Oranges | Medium | 多源BFS |
| [LC 542](https://leetcode.com/problems/01-matrix/) | 01 Matrix | Medium | 多源BFS |
| [LC 1162](https://leetcode.com/problems/as-far-from-land-as-possible/) | As Far from Land as Possible | Medium | 多源BFS |
| [LC 1091](https://leetcode.com/problems/shortest-path-in-binary-matrix/) | Shortest Path in Binary Matrix | Medium | 8方向BFS |
| [LC 1293](https://leetcode.com/problems/shortest-path-in-a-grid-with-obstacles-elimination/) | Shortest Path with Obstacles | Hard | BFS+状态层 |

---

[← 返回索引](index.md)
