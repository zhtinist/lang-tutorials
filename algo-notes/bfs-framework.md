# BFS 框架 · Breadth-First Search

> BFS 的核心是**队列 + visited 集合**，适合找**最短路径**（无权图中 BFS 首次到达就是最短距离）。

---

## 一、BFS vs DFS 选择指南

| 场景 | 用什么 | 原因 |
|------|--------|------|
| 树/图的最短路径 | BFS | 一层层扩展，首次到达=最短 |
| 遍历全部状态/路径 | DFS/回溯 | 代码简单，空间占用小 |
| 知道终止状态 | 双向 BFS | 空间更优（见第二章） |
| 树的高度/层次信息 | BFS | 天然按层遍历 |
| 图很大但深度小 | BFS | 不会爆栈 |
| 图深度很大 | DFS(迭代) | 避免递归栈溢出（也可用迭代DFS） |

---

## 二、通用 BFS 框架

```python
from collections import deque


def bfs(start, target) -> int:
    """
    BFS 通用框架。
    返回从 start 到 target 的最短距离（步数）。
    若找不到，返回 -1。
    """
    queue: deque = deque([start])   # 队列
    visited: set = {start}           # 避免走回头路
    step = 0

    while queue:
        size = len(queue)  # ⚠️ 当前层的节点数
        for _ in range(size):
            cur = queue.popleft()

            # 判断是否到达终点
            if cur == target:
                return step

            # 将 cur 的邻居加入队列
            for nxt in cur.neighbors():  # 需要根据题目实现
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append(nxt)

        step += 1  # 一层走完，步数+1

    return -1
```

### 关键细节

1. **`size = len(queue)`** — 必须在循环外记录，保证 `step` 按层计数
2. **`visited` 时机** — 在入队时标记，而不是出队时（避免重复入队）

---

## 三、树的 BFS（层序遍历）

### [LC 102](https://leetcode.com/problems/binary-tree-level-order-traversal/) 二叉树的层序遍历

```python
from collections import deque


class TreeNode:
    def __init__(self, val: int = 0, left: "TreeNode | None" = None, right: "TreeNode | None" = None):
        self.val = val
        self.left = left
        self.right = right


def level_order(root: TreeNode | None) -> list[list[int]]:
    """返回层序遍历结果，每层一个 list。"""
    if not root:
        return []

    ans: list[list[int]] = []
    queue: deque[TreeNode] = deque([root])

    while queue:
        level: list[int] = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        ans.append(level)

    return ans
```

### [LC 111](https://leetcode.com/problems/minimum-depth-of-binary-tree/) 二叉树的最小深度

```python
def min_depth(root: TreeNode | None) -> int:
    """BFS 找到的第一个叶子节点所在层就是最小深度。"""
    if not root:
        return 0

    queue: deque[TreeNode] = deque([root])
    depth = 1

    while queue:
        for _ in range(len(queue)):
            node = queue.popleft()
            # 叶子节点 = 最小深度
            if not node.left and not node.right:
                return depth
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        depth += 1

    return depth
```

---

## 四、图的 BFS（最短路径）

### [LC 752](https://leetcode.com/problems/open-the-lock/) 打开转盘锁

```python
from collections import deque


def open_lock(deadends: list[str], target: str) -> int:
    """
    4位转盘锁，从 '0000' 到 target。
    deadends 是不能走的密码。
    每次转一位（+1 或 -1），找最短步数。
    """
    deads = set(deadends)
    if "0000" in deads:
        return -1

    queue: deque[str] = deque(["0000"])
    visited: set[str] = {"0000"}
    step = 0

    while queue:
        for _ in range(len(queue)):
            cur = queue.popleft()

            if cur == target:
                return step

            # 每个旋钮可以转8个方向（4位 × 2方向）
            for i in range(4):
                for delta in (1, -1):
                    # 转动一位
                    digit = (int(cur[i]) + delta) % 10
                    nxt = cur[:i] + str(digit) + cur[i + 1:]

                    if nxt not in deads and nxt not in visited:
                        visited.add(nxt)
                        queue.append(nxt)

        step += 1

    return -1
```

### [LC 773](https://leetcode.com/problems/sliding-puzzle/) 滑动拼图

```python
from collections import deque


def sliding_puzzle(board: list[list[int]]) -> int:
    """
    2×3 滑动拼图，每次把 0 与相邻数字交换。
    求拼成 [[1,2,3],[4,5,0]] 的最少步数。
    """
    # 邻接索引表：每个位置可以交换到的位置
    neighbors = [
        [1, 3],       # 0 → 位置1,3
        [0, 2, 4],    # 1
        [1, 5],       # 2
        [0, 4],       # 3
        [1, 3, 5],    # 4
        [2, 4],       # 5
    ]

    start = "".join(str(c) for row in board for c in row)
    target = "123450"

    queue: deque[tuple[str, int]] = deque([(start, start.index("0"))])
    visited: set[str] = {start}
    step = 0

    while queue:
        for _ in range(len(queue)):
            state, zero_idx = queue.popleft()
            if state == target:
                return step

            for nxt_idx in neighbors[zero_idx]:
                # 交换 0 和相邻位置
                state_list = list(state)
                state_list[zero_idx], state_list[nxt_idx] = state_list[nxt_idx], state_list[zero_idx]
                nxt_state = "".join(state_list)

                if nxt_state not in visited:
                    visited.add(nxt_state)
                    queue.append((nxt_state, nxt_idx))

        step += 1

    return -1
```

---

## 五、BFS 路径还原

> 在 BFS 过程中记录每个节点的父节点，最后从终点回溯到起点。

```python
from collections import deque


def bfs_with_path(graph, start, target):
    """BFS 找最短路径，同时还原路径。"""
    queue: deque = deque([start])
    visited: set = {start}
    parent: dict = {start: None}  # 记录父节点

    while queue:
        cur = queue.popleft()
        if cur == target:
            # 回溯路径
            path = []
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            return path[::-1]  # 反转得到从 start 到 target

        for nxt in graph[cur]:
            if nxt not in visited:
                visited.add(nxt)
                parent[nxt] = cur
                queue.append(nxt)

    return []  # 无路径
```

---

## 六、双向 BFS（简介）

> 当知道起点和终点时，两边同时 BFS，相遇即结束。复杂度从 O(b^d) 降到 O(2 × b^(d/2))。

```python
from collections import deque


def bidirectional_bfs(start, target):
    """双向 BFS 模板。详见第二章双向BFS专题。"""
    q1, q2 = {start}, {target}
    visited: set = set()
    step = 0

    while q1 and q2:
        # 每次都扩展较小的队列
        if len(q1) > len(q2):
            q1, q2 = q2, q1

        tmp: set = set()
        for cur in q1:
            if cur in q2:
                return step
            visited.add(cur)
            for nxt in get_neighbors(cur):
                if nxt not in visited:
                    tmp.add(nxt)

        q1 = tmp
        step += 1

    return -1
```

---

## 七、总结

| 要点 | 说明 |
|------|------|
| 数据结构 | 队列 (deque) |
| 状态标记 | visited 集合，**入队时**标记 |
| 步数计算 | 按层循环：`for _ in range(len(queue))` |
| 路径还原 | 记录 parent 字典 |
| 空间复杂度 | O(b^d) — 宽搜索，b=分支因子，d=深度 |
| 时间优化 | 双向 BFS（知道目标时） |

---

## 八、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 102](https://leetcode.com/problems/binary-tree-level-order-traversal/) | Binary Tree Level Order | Medium | 基础层序遍历 |
| [LC 107](https://leetcode.com/problems/binary-tree-level-order-traversal-ii/) | Binary Tree Level Order II | Medium | 层序+反转 |
| [LC 103](https://leetcode.com/problems/binary-tree-zigzag-level-order-traversal/) | Zigzag Level Order | Medium | 层序+交替方向 |
| [LC 111](https://leetcode.com/problems/minimum-depth-of-binary-tree/) | Minimum Depth of Binary Tree | Easy | BFS 最短路径 |
| [LC 752](https://leetcode.com/problems/open-the-lock/) | Open the Lock | Medium | 状态BFS |
| [LC 773](https://leetcode.com/problems/sliding-puzzle/) | Sliding Puzzle | Hard | 状态BFS+路径压缩 |
| [LC 127](https://leetcode.com/problems/word-ladder/) | Word Ladder | Hard | 双向BFS更优 |
| [LC 433](https://leetcode.com/problems/minimum-genetic-mutation/) | Minimum Genetic Mutation | Medium | 状态BFS |
| [LC 279](https://leetcode.com/problems/perfect-squares/) | Perfect Squares | Medium | BFS(转成图) |
| [LC 542](https://leetcode.com/problems/01-matrix/) | 01 Matrix | Medium | 多源BFS |
| [LC 994](https://leetcode.com/problems/rotting-oranges/) | Rotting Oranges | Medium | 多源BFS |

---

[← 返回索引](index.md)
