# DFS & 回溯深度详解 · DFS & Backtracking

> 回溯 = 决策树上的 DFS。每个节点代表一个**状态**，每条边代表一个**选择**。
> 本章在 ch00 回溯框架基础上深入**剪枝技巧、复杂度分析、回溯转DP**。

---

## 一、排列/组合/子集模板总结

回溯问题分为三类，每类的区别在于**如何避免重复**：

| 类型 | 元素顺序 | 避免重复方式 | 核心参数 |
|------|---------|-------------|---------|
| 排列 | 有顺序 | `used` 数组 | `used[i]` |
| 排列含重复 | 有顺序 | `used` + 排序跳过 `nums[i]==nums[i-1] && !used[i-1]` | `used[i]` |
| 组合/子集 | 无顺序 | `start` 索引保证只往后选 | `start` |
| 组合含重复 | 无顺序 | `start` + 排序跳过 `i > start && nums[i]==nums[i-1]` | `start` |
| 元素可重复选 | — | `start` 不进位（允许重复选自己） | `start` |

---

## 二、剪枝策略

### 2.1 可行性剪枝

```python
# [LC 40](https://leetcode.com/problems/combination-sum-ii/) 组合总和 II：当前和超过 target 直接停止
def combination_sum2(candidates: list[int], target: int) -> list[list[int]]:
    candidates.sort()
    ans: list[list[int]] = []

    def backtrack(start: int, path: list[int], remain: int) -> None:
        if remain == 0:
            ans.append(path.copy())
            return
        # 剪枝1：remain < 0 提前退出
        if remain < 0:
            return

        for i in range(start, len(candidates)):
            # 剪枝2：排序后，当前元素 > remain，后面更大的也不会满足
            if candidates[i] > remain:
                break
            # 剪枝3：同层去重
            if i > start and candidates[i] == candidates[i - 1]:
                continue
            path.append(candidates[i])
            backtrack(i + 1, path, remain - candidates[i])
            path.pop()

    backtrack(0, [], target)
    return ans
```

### 2.2 数量剪枝

```python
# [LC 77](https://leetcode.com/problems/combinations/) 组合：剩余元素不够选 k 个时直接跳过
def combine(n: int, k: int) -> list[list[int]]:
    ans: list[list[int]] = []

    def backtrack(start: int, path: list[int]) -> None:
        if len(path) == k:
            ans.append(path.copy())
            return

        need = k - len(path)
        # 剪枝：i 最大到 n - need + 1
        for i in range(start, n - need + 2):  # 注意+1变+2
            path.append(i)
            backtrack(i + 1, path)
            path.pop()

    backtrack(1, [])
    return ans
```

### 2.3 对称性剪枝（N皇后）

```python
# [LC 51](https://leetcode.com/problems/n-queens/) N皇后可以利用对称性只搜一半
# （未展开完整实现）
```

### 2.4 状态压缩剪枝（解数独 · [LC 37](https://leetcode.com/problems/sudoku-solver/)）

```python
def solve_sudoku(board: list[list[str]]) -> None:
    """回溯解数独，选择最少的空格优先填。"""

    rows = [[False] * 10 for _ in range(9)]
    cols = [[False] * 10 for _ in range(9)]
    boxes = [[False] * 10 for _ in range(9)]

    # 预处理已填数字
    spaces: list[tuple[int, int]] = []
    for i in range(9):
        for j in range(9):
            if board[i][j] == ".":
                spaces.append((i, j))
            else:
                d = int(board[i][j])
                rows[i][d] = cols[j][d] = boxes[3 * (i // 3) + j // 3][d] = True

    def dfs(pos: int) -> bool:
        if pos == len(spaces):
            return True

        i, j = spaces[pos]
        box_idx = 3 * (i // 3) + j // 3
        for d in range(1, 10):
            if not rows[i][d] and not cols[j][d] and not boxes[box_idx][d]:
                rows[i][d] = cols[j][d] = boxes[box_idx][d] = True
                board[i][j] = str(d)
                if dfs(pos + 1):
                    return True
                rows[i][d] = cols[j][d] = boxes[box_idx][d] = False
                board[i][j] = "."
        return False

    dfs(0)
```

---

## 三、回溯转 DP 的条件

> 当回溯的子问题具有**重叠性**（不同路径到达同一状态），且状态只依赖参数（不依赖路径），就可以用记忆化转为 DP。

### 示例：[LC 139](https://leetcode.com/problems/word-break/) 单词拆分

```python
# 回溯版本（可能超时）
def word_break_backtrack(s: str, word_dict: list[str]) -> bool:
    words = set(word_dict)

    def dfs(start: int) -> bool:
        if start == len(s):
            return True
        for end in range(start + 1, len(s) + 1):
            if s[start:end] in words and dfs(end):
                return True
        return False

    return dfs(0)


# 记忆化回溯 → 本质是 DP
def word_break_memo(s: str, word_dict: list[str]) -> bool:
    words = set(word_dict)
    from functools import lru_cache

    @lru_cache(maxsize=None)
    def dfs(start: int) -> bool:
        if start == len(s):
            return True
        for end in range(start + 1, len(s) + 1):
            if s[start:end] in words and dfs(end):
                return True
        return False

    return dfs(0)
```

---

## 四、时间复杂度公式

| 问题 | 决策树大小 | 时间复杂度 |
|------|-----------|-----------|
| 排列（无重复） | n! 个叶节点 | O(n! × n) |
| 组合 C(n, k) | C(n, k) 个叶节点 | O(C(n,k) × k) |
| 子集 | 2^n 个节点 | O(2^n × n) |
| N皇后 | ≤ n! 个节点 | O(n!) |
| 解数独 | 9^空格数 最坏 | 指数级，剪枝后实际很快 |

> 括号中的 ×n 或 ×k 是拷贝 path/检查合法性的开销。

---

## 五、括号生成 · [LC 22](https://leetcode.com/problems/generate-parentheses/)

```python
def generate_parenthesis(n: int) -> list[str]:
    """
    回溯 + 合法性约束：
    - 左括号数量 < n 时可以加 (
    - 右括号数量 < 左括号数量时可以加 )
    """
    ans: list[str] = []

    def backtrack(path: list[str], open_cnt: int, close_cnt: int) -> None:
        if len(path) == 2 * n:
            ans.append("".join(path))
            return

        if open_cnt < n:
            path.append("(")
            backtrack(path, open_cnt + 1, close_cnt)
            path.pop()

        if close_cnt < open_cnt:
            path.append(")")
            backtrack(path, open_cnt, close_cnt + 1)
            path.pop()

    backtrack([], 0, 0)
    return ans
```

---

## 六、分割回文串 · [LC 131](https://leetcode.com/problems/palindrome-partitioning/)

```python
def partition_palindrome(s: str) -> list[list[str]]:
    """分割字符串使得每个子串都是回文。"""

    ans: list[list[str]] = []

    def is_palindrome(i: int, j: int) -> bool:
        while i < j:
            if s[i] != s[j]:
                return False
            i += 1
            j -= 1
        return True

    def backtrack(start: int, path: list[str]) -> None:
        if start == len(s):
            ans.append(path.copy())
            return

        for end in range(start, len(s)):
            if is_palindrome(start, end):
                path.append(s[start : end + 1])
                backtrack(end + 1, path)
                path.pop()

    backtrack(0, [])
    return ans


# 优化：预处理回文判断
def partition_palindrome_opt(s: str) -> list[list[str]]:
    n = len(s)
    # dp[i][j] = s[i:j+1] 是否是回文
    dp = [[False] * n for _ in range(n)]
    for j in range(n):
        for i in range(j + 1):
            if s[i] == s[j] and (j - i <= 2 or dp[i + 1][j - 1]):
                dp[i][j] = True

    ans: list[list[str]] = []

    def backtrack(start: int, path: list[str]) -> None:
        if start == n:
            ans.append(path.copy())
            return
        for end in range(start, n):
            if dp[start][end]:
                path.append(s[start : end + 1])
                backtrack(end + 1, path)
                path.pop()

    backtrack(0, [])
    return ans
```

---

## 七、总结

| 技巧 | 说明 |
|------|------|
| 可行性剪枝 | 当前状态不可能到达答案时直接返回 |
| 数量剪枝 | 剩余选择不够时提前退出 |
| 排序+跳过重复 | 排列用 `used`，组合用 `start` |
| 状态压缩 | bitset 替代 visited 数组 |
| 转 DP | 重叠子问题 + 参数无路径依赖 → 记忆化 |

---

## 八、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 22](https://leetcode.com/problems/generate-parentheses/) | Generate Parentheses | Medium | 回溯+合法性 |
| [LC 131](https://leetcode.com/problems/palindrome-partitioning/) | Palindrome Partitioning | Medium | 回溯+回文 |
| [LC 79](https://leetcode.com/problems/word-search/) | Word Search | Medium | 回溯+网格 |
| [LC 37](https://leetcode.com/problems/sudoku-solver/) | Sudoku Solver | Hard | 回溯+剪枝 |
| [LC 140](https://leetcode.com/problems/word-break-ii/) | Word Break II | Hard | 回溯+记忆化 |
| [LC 332](https://leetcode.com/problems/reconstruct-itinerary/) | Reconstruct Itinerary | Hard | 欧拉路径 |

---

[← 返回索引](index.md)
