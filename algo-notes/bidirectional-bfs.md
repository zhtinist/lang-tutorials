# 双向 BFS · Bidirectional BFS

> 当**知道目标状态**时，同时从起点和终点开始 BFS，在中间相遇时结束。
> 复杂度从 O(b^d) 降到 O(2 × b^(d/2))。b=分支因子，d=最短距离。

---

## 一、双向 BFS 框架

### 核心思想

```
单向 BFS：           双向 BFS：
    S                    S           T
   / \                  / \         / \
  O   O                O   O       O   O
 / \ / \               |   |       |   |
... ...          相遇→ O - O ←相遇 O   O
  \ /                   \ /       \ /
   T                     O--- ... --O
```

### 通用模板

```python
from collections import deque


def bidirectional_bfs(start, target):
    """双向 BFS 通用模板。"""

    # 用 set 代替 queue，方便判断"相遇"
    q1: set = {start}   # 从起点开始的搜索层
    q2: set = {target}  # 从终点开始的搜索层
    visited: set = set()
    step = 0

    while q1 and q2:
        # ⚠️ 每次都扩展较小的集合（关键优化！）
        if len(q1) > len(q2):
            q1, q2 = q2, q1

        # 扩展 q1 的一层
        next_q: set = set()
        for cur in q1:
            # 判断相遇
            if cur in q2:
                return step

            visited.add(cur)

            for nxt in get_neighbors(cur):  # 根据题目实现
                if nxt not in visited:
                    next_q.add(nxt)

        q1 = next_q
        step += 1

    return -1
```

> **关键**：用 `set` 表示一层的节点，方便 O(1) 判断相遇。每次都扩较小的集合，让两边的搜索量尽量均匀。

---

## 二、单词接龙 · [LC 127](https://leetcode.com/problems/word-ladder/)

```python
from collections import deque


def ladder_length(begin_word: str, end_word: str, word_list: list[str]) -> int:
    """
    从 beginWord 到 endWord，每次只能改一个字母。
    返回最短转换序列的长度（包括起点）。
    """
    word_set = set(word_list)
    if end_word not in word_set:
        return 0

    # 双向 BFS
    q1, q2 = {begin_word}, {end_word}
    word_set.discard(begin_word)  # visited 直接通过移除实现
    step = 1  # beginWord 计入长度

    while q1 and q2:
        # 扩展较小的集合
        if len(q1) > len(q2):
            q1, q2 = q2, q1

        nxt_set: set[str] = set()
        for word in q1:
            word_chars = list(word)
            for i in range(len(word_chars)):
                old = word_chars[i]
                for c in "abcdefghijklmnopqrstuvwxyz":
                    if c == old:
                        continue
                    word_chars[i] = c
                    new_word = "".join(word_chars)

                    if new_word in q2:
                        return step + 1

                    if new_word in word_set:
                        nxt_set.add(new_word)
                        word_set.remove(new_word)  # 相当于 visited
                word_chars[i] = old

        q1 = nxt_set
        step += 1

    return 0
```

### 单向 vs 双向对比

```
单词接龙 [LC 127](https://leetcode.com/problems/word-ladder/) 当单词数=5000时：
- 单向 BFS：可能需要搜索到深度为 10+ 的所有状态
- 双向 BFS：每边只搜 5 层，中间相遇

实测：双向 BFS 在 LeetCode 上比单向快 3-10 倍。
```

---

## 三、开锁问题 · [LC 752](https://leetcode.com/problems/open-the-lock/)（双向 BFS）

```python
def open_lock_bi(deadends: list[str], target: str) -> int:
    """双向 BFS 解开锁。"""
    deads = set(deadends)
    if "0000" in deads:
        return -1

    q1, q2 = {"0000"}, {target}
    visited: set[str] = deads  # 把 deadends 当 visited
    step = 0

    while q1 and q2:
        if len(q1) > len(q2):
            q1, q2 = q2, q1

        nxt_set: set[str] = set()
        for cur in q1:
            if cur in q2:
                return step

            visited.add(cur)

            # 8 种转动方向
            for i in range(4):
                for delta in (1, -1):
                    digit = (int(cur[i]) + delta) % 10
                    nxt = cur[:i] + str(digit) + cur[i + 1:]
                    if nxt not in visited:
                        nxt_set.add(nxt)

        q1 = nxt_set
        step += 1

    return -1
```

---

## 四、滑动拼图 · [LC 773](https://leetcode.com/problems/sliding-puzzle/)（双向 BFS）

```python
def sliding_puzzle_bi(board: list[list[int]]) -> int:
    """2×3 滑动拼图，双向 BFS。"""
    neighbors = [
        [1, 3], [0, 2, 4], [1, 5],
        [0, 4], [1, 3, 5], [2, 4],
    ]

    start = "".join(str(c) for row in board for c in row)
    target = "123450"

    if start == target:
        return 0

    q1, q2 = {start}, {target}
    visited: set[str] = set()
    step = 0

    while q1 and q2:
        if len(q1) > len(q2):
            q1, q2 = q2, q1

        nxt_set: set[str] = set()
        for state in q1:
            if state in q2:
                return step

            visited.add(state)
            zero_idx = state.index("0")

            for nxt_idx in neighbors[zero_idx]:
                state_list = list(state)
                state_list[zero_idx], state_list[nxt_idx] = (
                    state_list[nxt_idx],
                    state_list[zero_idx],
                )
                nxt_state = "".join(state_list)
                if nxt_state not in visited:
                    nxt_set.add(nxt_state)

        q1 = nxt_set
        step += 1

    return -1
```

---

## 五、适用条件与局限性

### 适用条件

1. **知道终点状态**（这是双向 BFS 的前提）
2. **状态空间大**（单向 BFS 会很慢）
3. **分支因子大**（每层扩展很多节点）
4. **可以反向搜索**（从终点也能往前找邻居）

### 不适用场景

- 不知道终点在哪（如：在图中找最近的目标节点）
- 起点到终点很近（双向 BFS 的 set 操作有常数开销）
- 搜索树很深但很窄（BFS 本身就很快）

---

## 六、复杂度对比

| 场景 | 单向 BFS | 双向 BFS |
|------|---------|---------|
| 分支因子 b，深度 d | O(b^d) 时间 | O(b^(d/2)) 时间 |
|  | O(b^d) 空间 | O(b^(d/2)) 空间 |

```
例：b=10, d=6
单向: 10^6 = 1,000,000
双向: 2 × 10^3 = 2,000  → 500倍提升！
```

---

## 七、实现细节

| 细节 | 推荐做法 |
|------|---------|
| 数据结构 | `set` 而非 `deque`（方便 O(1) 判断相遇） |
| 扩展方向 | 每次都扩较小的集合 |
| visited | 可以用一个 set，也可以利用原数据结构的删除 |
| 相遇判断 | 生成新状态时判断是否在对方集合中 |
| 步数计算 | 每次扩展一层（一层 = 一个 set）step++ |

---

## 八、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 127](https://leetcode.com/problems/word-ladder/) | Word Ladder | Hard | 双向BFS经典题 |
| [LC 126](https://leetcode.com/problems/word-ladder-ii/) | Word Ladder II | Hard | 双向BFS+路径还原 |
| [LC 752](https://leetcode.com/problems/open-the-lock/) | Open the Lock | Medium | 双向BFS |
| [LC 773](https://leetcode.com/problems/sliding-puzzle/) | Sliding Puzzle | Hard | 双向BFS |
| [LC 433](https://leetcode.com/problems/minimum-genetic-mutation/) | Minimum Genetic Mutation | Medium | 双向BFS |

---

[← 返回索引](index.md)
