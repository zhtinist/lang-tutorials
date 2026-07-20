# 回溯算法 · Backtracking

> 回溯 = **决策树的遍历**。三要素：**路径**(已选)、**选择列表**(可选)、**结束条件**(到达底部)。
> 核心：`做选择 → 递归 → 撤销选择`。本质是 DFS 在决策树上的应用。

---

## 一、回溯框架

```python
def backtrack(path, choices, *args) -> None:
    """回溯算法通用框架。"""
    # 结束条件：把路径加入结果集
    if 满足结束条件:
        result.append(path.copy())  # ⚠️ 拷贝！不能直接加 path
        return

    for choice in choices:
        # 剪枝：跳过不合法的选择
        if 不合法:
            continue

        # 做选择
        path.append(choice)
        # 或：标记选择

        # 进入下一层决策树
        backtrack(path, new_choices, *args)

        # 撤销选择
        path.pop()
        # 或：取消标记
```

---

## 二、排列问题（Permutations）

> 排列：顺序重要，[1,2] ≠ [2,1]。用 `used` 数组标记已选元素。

### [LC 46](https://leetcode.com/problems/permutations/) 全排列（无重复）

```python
def permute(nums: list[int]) -> list[list[int]]:
    """无重复元素的全排列。"""
    ans: list[list[int]] = []
    used = [False] * len(nums)

    def backtrack(path: list[int]) -> None:
        if len(path) == len(nums):
            ans.append(path.copy())
            return

        for i, val in enumerate(nums):
            if used[i]:
                continue
            # 做选择
            path.append(val)
            used[i] = True
            # 递归
            backtrack(path)
            # 撤销选择
            path.pop()
            used[i] = False

    backtrack([])
    return ans
```

### [LC 47](https://leetcode.com/problems/permutations-ii/) 全排列 II（含重复）

```python
def permute_unique(nums: list[int]) -> list[list[int]]:
    """
    含重复元素的全排列。
    去重关键：排序后，相同元素必须按顺序选取。
    即：如果 nums[i] == nums[i-1] 且 !used[i-1]，则跳过。
    """
    nums.sort()
    ans: list[list[int]] = []
    used = [False] * len(nums)

    def backtrack(path: list[int]) -> None:
        if len(path) == len(nums):
            ans.append(path.copy())
            return

        for i in range(len(nums)):
            if used[i]:
                continue
            # 去重：相同元素必须前一个被用了才能用当前这个
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue
            path.append(nums[i])
            used[i] = True
            backtrack(path)
            path.pop()
            used[i] = False

    backtrack([])
    return ans
```

> **去重口诀**：`if i > 0 and nums[i] == nums[i-1] and not used[i-1]: continue`
> 这保证相同元素在排列中的相对顺序固定。

---

## 三、组合/子集问题（Combinations / Subsets）

> 组合：顺序不重要，[1,2] = [2,1]。用 `start` 参数控制选择范围，避免重复组合。

### [LC 78](https://leetcode.com/problems/subsets/) 子集（无重复）

```python
def subsets(nums: list[int]) -> list[list[int]]:
    """所有子集（幂集）。每个元素选/不选，共 2^n 个。"""
    ans: list[list[int]] = []

    def backtrack(start: int, path: list[int]) -> None:
        # 每个节点都是一个子集（大小不限，任意路径都有效）
        ans.append(path.copy())

        for i in range(start, len(nums)):
            path.append(nums[i])
            backtrack(i + 1, path)  # 从 i+1 开始，保证不重复
            path.pop()

    backtrack(0, [])
    return ans
```

### [LC 90](https://leetcode.com/problems/subsets-ii/) 子集 II（含重复）

```python
def subsets_with_dup(nums: list[int]) -> list[list[int]]:
    """含重复元素的子集。去重：排序 + 跳过同层重复。"""
    nums.sort()
    ans: list[list[int]] = []

    def backtrack(start: int, path: list[int]) -> None:
        ans.append(path.copy())

        for i in range(start, len(nums)):
            # 去重：跳过同层的重复元素
            if i > start and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i])
            backtrack(i + 1, path)
            path.pop()

    backtrack(0, [])
    return ans
```

> **排列 vs 组合的去重区别**：
> - 排列去重用 `used` 数组 + 条件 `!used[i-1]`
> - 组合/子集去重用 `i > start and nums[i] == nums[i-1]`

### [LC 77](https://leetcode.com/problems/combinations/) 组合

```python
def combine(n: int, k: int) -> list[list[int]]:
    """从 1..n 中选 k 个数的所有组合。"""
    ans: list[list[int]] = []

    def backtrack(start: int, path: list[int]) -> None:
        if len(path) == k:
            ans.append(path.copy())
            return

        # 剪枝优化：剩余元素不够选时提前退出
        # 还需要 k - len(path) 个元素，从 start 到 n 要有足够数量
        # i <= n - (k - len(path)) + 1
        need = k - len(path)
        upper = n - need + 1
        for i in range(start, upper + 1):
            path.append(i)
            backtrack(i + 1, path)
            path.pop()

    backtrack(1, [])
    return ans
```

### [LC 39](https://leetcode.com/problems/combination-sum/) 组合总和（元素可重复用）

```python
def combination_sum(candidates: list[int], target: int) -> list[list[int]]:
    """
    每个元素可以无限次使用，找出所有和为 target 的组合。
    关键：start 不前进（允许重复选同一个），用 target 递减。
    """
    ans: list[list[int]] = []

    def backtrack(start: int, path: list[int], remain: int) -> None:
        if remain == 0:
            ans.append(path.copy())
            return
        if remain < 0:
            return

        for i in range(start, len(candidates)):
            path.append(candidates[i])
            # i 不变，下次还可以选 i（同一元素可重复用）
            backtrack(i, path, remain - candidates[i])
            path.pop()

    backtrack(0, [], target)
    return ans
```

### [LC 40](https://leetcode.com/problems/combination-sum-ii/) 组合总和 II（元素只能用一次，含重复）

```python
def combination_sum2(candidates: list[int], target: int) -> list[list[int]]:
    """每个元素只能用一次，且含重复元素。排序+同层去重。"""
    candidates.sort()
    ans: list[list[int]] = []

    def backtrack(start: int, path: list[int], remain: int) -> None:
        if remain == 0:
            ans.append(path.copy())
            return
        if remain < 0:
            return

        for i in range(start, len(candidates)):
            # 同层去重
            if i > start and candidates[i] == candidates[i - 1]:
                continue
            path.append(candidates[i])
            backtrack(i + 1, path, remain - candidates[i])  # i+1（每个元素只用一次）
            path.pop()

    backtrack(0, [], target)
    return ans
```

---

## 四、N 皇后 · [LC 51](https://leetcode.com/problems/n-queens/)

```python
def solve_n_queens(n: int) -> list[list[str]]:
    """N皇后：返回所有解。"""
    ans: list[list[str]] = []
    # 棋盘，'.' 表示空，'Q' 表示皇后
    board = [["."] * n for _ in range(n)]

    def is_valid(row: int, col: int) -> bool:
        """检查 (row, col) 是否可以放皇后。只需检查上半部分。"""
        # 检查同列
        for i in range(row):
            if board[i][col] == "Q":
                return False
        # 检查左上对角线
        i, j = row - 1, col - 1
        while i >= 0 and j >= 0:
            if board[i][j] == "Q":
                return False
            i -= 1
            j -= 1
        # 检查右上对角线
        i, j = row - 1, col + 1
        while i >= 0 and j < n:
            if board[i][j] == "Q":
                return False
            i -= 1
            j += 1
        return True

    def backtrack(row: int) -> None:
        if row == n:
            ans.append(["".join(r) for r in board])
            return

        for col in range(n):
            if not is_valid(row, col):
                continue
            board[row][col] = "Q"  # 做选择
            backtrack(row + 1)     # 进入下一行
            board[row][col] = "."  # 撤销选择

    backtrack(0)
    return ans
```

---

## 五、复杂度分析

| 问题类型 | 解的数量 | 时间复杂度 | 例题 |
|----------|---------|-----------|------|
| 排列 (n个不同) | n! | O(n! × n) | [LC 46](https://leetcode.com/problems/permutations/) |
| 排列 (含重复) | n! / (重复次数乘积) | O(上述) | [LC 47](https://leetcode.com/problems/permutations-ii/) |
| 组合 (n选k) | C(n, k) | O(C(n,k) × k) | [LC 77](https://leetcode.com/problems/combinations/) |
| 子集 (n个不同) | 2^n | O(2^n × n) | [LC 78](https://leetcode.com/problems/subsets/) |
| N皇后 | ≤ n! | O(n!) | [LC 51](https://leetcode.com/problems/n-queens/) |

> 回溯算法一般是指数/阶乘级别。剪枝可以大幅减少实际运行时间，但不改变最坏复杂度。

---

## 六、总结

| 问题类型 | 避免重复的方式 | 核心参数 |
|----------|--------------|---------|
| 排列 | `used` 数组标记 | `used[i]` |
| 排列去重 | 排序 + `!used[i-1]` 跳过 | `used[i]` |
| 组合/子集 | `start` 索引控制顺序 | `start` |
| 组合/子集去重 | 排序 + `i > start` 跳过同层 | `start` |
| 元素可重复选 | `start` 不进 `i+1` | `start` |
| N皇后 | 按行放置，检查列+对角线 | `row` |

---

## 七、习题推荐

| 题号 | 题目 | 难度 | 类型 |
|------|------|------|------|
| [LC 46](https://leetcode.com/problems/permutations/) | Permutations | Medium | 排列无重复 |
| [LC 47](https://leetcode.com/problems/permutations-ii/) | Permutations II | Medium | 排列有重复 |
| [LC 78](https://leetcode.com/problems/subsets/) | Subsets | Medium | 子集无重复 |
| [LC 90](https://leetcode.com/problems/subsets-ii/) | Subsets II | Medium | 子集有重复 |
| [LC 77](https://leetcode.com/problems/combinations/) | Combinations | Medium | 组合 |
| [LC 39](https://leetcode.com/problems/combination-sum/) | Combination Sum | Medium | 组合可重复选 |
| [LC 40](https://leetcode.com/problems/combination-sum-ii/) | Combination Sum II | Medium | 组合不可重+去重 |
| [LC 216](https://leetcode.com/problems/combination-sum-iii/) | Combination Sum III | Medium | 组合定长 |
| [LC 17](https://leetcode.com/problems/letter-combinations-of-a-phone-number/) | Letter Combinations | Medium | 回溯×字符串 |
| [LC 22](https://leetcode.com/problems/generate-parentheses/) | Generate Parentheses | Medium | 回溯+括号合法性 |
| [LC 131](https://leetcode.com/problems/palindrome-partitioning/) | Palindrome Partitioning | Medium | 回溯+字符串分割 |
| [LC 51](https://leetcode.com/problems/n-queens/) | N-Queens | Hard | 经典回溯 |
| [LC 37](https://leetcode.com/problems/sudoku-solver/) | Sudoku Solver | Hard | 回溯+剪枝 |
| [LC 79](https://leetcode.com/problems/word-search/) | Word Search | Medium | 回溯+网格 |

---

[← 返回索引](index.md)
