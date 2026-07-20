# 状压 DP & 数位 DP · Bitmask DP & Digit DP

> **状压 DP**：用二进制位表示集合（选/不选），状态压缩为整数。
> **数位 DP**：按位枚举数字，记忆化搜索避免重复计算。

---

## 一、状压 DP 基础

### 常用位运算

```python
# 集合操作（mask 是二进制整数）
mask |= (1 << i)         # 加入元素 i
mask &= ~(1 << i)        # 删除元素 i
mask ^= (1 << i)         # 切换元素 i
has = (mask >> i) & 1    # 判断元素 i 是否在集合中

# 枚举子集
sub = mask
while sub:
    # 处理 sub
    sub = (sub - 1) & mask

# 全集
full = (1 << n) - 1

# 统计 1 的个数
cnt = mask.bit_count()
```

---

## 二、划分为 K 个相等子集 · [LC 698](https://leetcode.com/problems/partition-to-k-equal-sum-subsets/)

```python
from functools import lru_cache


def can_partition_k_subsets(nums: list[int], k: int) -> bool:
    """
    状压 DP 或 回溯+剪枝。
    
    状压 DP: dp[mask] = 当前选取状态为 mask 时，剩余未填满的当前桶的容量。
    用 -1 表示不可达状态。
    """
    total = sum(nums)
    if total % k != 0:
        return False

    target = total // k
    n = len(nums)
    nums.sort()

    if nums[-1] > target:
        return False

    # dp[mask] = 填了 mask 中的数字后，当前桶剩余容量
    # -1 = 不可达
    dp = [-1] * (1 << n)
    dp[0] = 0

    for mask in range(1 << n):
        if dp[mask] == -1:
            continue
        for i in range(n):
            if not (mask >> i) & 1:
                new_mask = mask | (1 << i)
                remain = dp[mask] + nums[i]
                if remain <= target:
                    # 当前桶填满则重置为 0
                    dp[new_mask] = remain % target

    return dp[(1 << n) - 1] == 0


# 回溯+剪枝解法（通常更快）
def can_partition_k_subsets_bt(nums: list[int], k: int) -> bool:
    total = sum(nums)
    if total % k != 0:
        return False

    target = total // k
    nums.sort(reverse=True)
    if nums[0] > target:
        return False

    buckets = [0] * k

    def backtrack(idx: int) -> bool:
        if idx == len(nums):
            return True

        seen = set()  # 在本层跳过相同容量的桶
        for i in range(k):
            if buckets[i] in seen:
                continue
            if buckets[i] + nums[idx] > target:
                continue

            seen.add(buckets[i])
            buckets[i] += nums[idx]
            if backtrack(idx + 1):
                return True
            buckets[i] -= nums[idx]

            # 关键剪枝：如果放入第一个空桶失败，后面的空桶也一样
            if buckets[i] == 0:
                break

        return False

    return backtrack(0)
```

---

## 三、TSP 旅行商问题 · [LC 847](https://leetcode.com/problems/shortest-path-visiting-all-nodes/)（访问所有节点的最短路径）

```python
from collections import deque


def shortest_path_length(graph: list[list[int]]) -> int:
    """
    状压 BFS。状态 = (node, mask)
    mask 表示已访问节点集合。
    """
    n = len(graph)
    if n == 1:
        return 0

    full_mask = (1 << n) - 1
    queue: deque[tuple[int, int, int]] = deque()  # (node, mask, dist)
    visited: set[tuple[int, int]] = set()

    # 多源 BFS：每个节点都可以是起点
    for i in range(n):
        mask = 1 << i
        queue.append((i, mask, 0))
        visited.add((i, mask))

    while queue:
        node, mask, dist = queue.popleft()
        if mask == full_mask:
            return dist

        for nxt in graph[node]:
            new_mask = mask | (1 << nxt)
            if (nxt, new_mask) not in visited:
                visited.add((nxt, new_mask))
                queue.append((nxt, new_mask, dist + 1))

    return -1
```

---

## 四、最短超级串 · [LC 943](https://leetcode.com/problems/find-the-shortest-superstring/)（TSP 变体）

```python
from functools import lru_cache


def shortest_superstring(words: list[str]) -> str:
    """
    找包含所有单词的最短字符串。
    本质是 TSP：以单词为节点，重叠长度为边的权重。
    """
    n = len(words)

    # overlap[i][j] = words[j] 接到 words[i] 后面时，重叠的字符数
    overlap = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for k in range(min(len(words[i]), len(words[j])), 0, -1):
                if words[i].endswith(words[j][:k]):
                    overlap[i][j] = k
                    break

    # dp[mask][last] = 已选集合为 mask，最后一个单词是 last 时的最短长度
    full = (1 << n) - 1
    dp = [[float("inf")] * n for _ in range(1 << n)]
    parent: list[list[tuple[int, int]]] = [[(-1, -1)] * n for _ in range(1 << n)]

    for i in range(n):
        dp[1 << i][i] = len(words[i])

    for mask in range(1 << n):
        for last in range(n):
            if dp[mask][last] == float("inf"):
                continue
            for nxt in range(n):
                if not (mask >> nxt) & 1:
                    new_mask = mask | (1 << nxt)
                    new_len = dp[mask][last] + len(words[nxt]) - overlap[last][nxt]
                    if new_len < dp[new_mask][nxt]:
                        dp[new_mask][nxt] = new_len
                        parent[new_mask][nxt] = (last, nxt)

    # 找最短的最终状态
    best_last = min(range(n), key=lambda i: dp[full][i])

    # 重建路径
    mask, last = full, best_last
    order: list[int] = []
    while mask:
        _, nxt = parent[mask][last]
        if _ == -1:
            order.append(last)
            break
        order.append(last)
        mask &= ~(1 << last)
        last = _

    order.reverse()

    # 构建结果
    result = words[order[0]]
    for i in range(1, len(order)):
        prev, cur = order[i - 1], order[i]
        result += words[cur][overlap[prev][cur]:]

    return result
```

---

## 五、数位 DP

> 数位 DP 模板：按位枚举，`is_limit` 表示受原数约束，`is_num` 表示前面是否选了非零数字。

### 通用模板

```python
from functools import lru_cache


def digit_dp_template(n: int) -> int:
    """数位 DP 通用框架。"""
    s = str(n)

    @lru_cache(maxsize=None)
    def dfs(pos: int, mask: int, is_limit: bool, is_num: bool) -> int:
        """
        pos: 当前处理的位置（从高到低）
        mask: 状态（根据题目不同）
        is_limit: 之前是否都取了上限（当前位是否受 n 约束）
        is_num: 之前是否已经选了非零数（跳过前导零）
        """
        if pos == len(s):
            return 1 if is_num else 0  # 合法数字

        ans = 0
        if not is_num:
            # 可以跳过当前位（继续选前导零）
            ans += dfs(pos + 1, mask, False, False)

        up = int(s[pos]) if is_limit else 9
        lo = 1 if not is_num else 0
        for d in range(lo, up + 1):
            # 检查 d 是否合法（根据 mask）
            if mask_ok(mask, d):   # 根据题目实现
                ans += dfs(
                    pos + 1,
                    new_mask(mask, d),  # 根据题目实现
                    is_limit and d == up,
                    True,
                )

        return ans

    return dfs(0, 0, True, False)
```

### [LC 902](https://leetcode.com/problems/numbers-at-most-n-given-digit-set/) 最大为 N 的数字组合

```python
def at_most_n_given_digit_set(digits: list[str], n: int) -> int:
    """
    用给定数字能组成的 ≤ n 的数的个数。
    记忆化搜索：pos, is_limit, is_num。
    """
    s = str(n)
    digits_set = set(int(d) for d in digits)

    @lru_cache(maxsize=None)
    def dfs(pos: int, is_limit: bool, is_num: bool) -> int:
        if pos == len(s):
            return 1 if is_num else 0

        ans = 0
        if not is_num:
            ans += dfs(pos + 1, False, False)

        up = int(s[pos]) if is_limit else 9
        for d in digits_set:
            if d > up:
                break
            ans += dfs(pos + 1, is_limit and d == up, True)

        return ans

    return dfs(0, True, False)
```

### [LC 600](https://leetcode.com/problems/non-negative-integers-without-consecutive-ones/) 不含连续 1 的非负整数

```python
def find_integers(n: int) -> int:
    """
    [0, n] 中二进制表示不含连续 1 的数字个数。
    """
    s = bin(n)[2:]  # 二进制字符串

    @lru_cache(maxsize=None)
    def dfs(pos: int, prev_one: bool, is_limit: bool) -> int:
        if pos == len(s):
            return 1  # 都算合法（含0）

        up = int(s[pos]) if is_limit else 1
        ans = 0
        for d in range(up + 1):
            if prev_one and d == 1:
                continue  # 不能连续两个 1
            ans += dfs(pos + 1, d == 1, is_limit and d == up)
        return ans

    return dfs(0, False, True)
```

---

## 六、总结

| 类型 | 技巧 | 典型复杂度 |
|------|------|-----------|
| 状压 DP | `dp[mask]` 递推或记忆化 | O(2^n × n) |
| TSP | `dp[mask][last]` 表示路径 | O(2^n × n²) |
| 数位 DP | 记忆化搜索 + is_limit + is_num | O(位数 × 状态) |

---

## 七、习题推荐

| 题号 | 题目 | 难度 | 类型 |
|------|------|------|------|
| [LC 698](https://leetcode.com/problems/partition-to-k-equal-sum-subsets/) | Partition to K Equal Sum Subsets | Medium | 状压DP/回溯 |
| [LC 847](https://leetcode.com/problems/shortest-path-visiting-all-nodes/) | Shortest Path Visiting All Nodes | Hard | 状压BFS(TSP) |
| [LC 943](https://leetcode.com/problems/find-the-shortest-superstring/) | Find the Shortest Superstring | Hard | 状压DP(TSP) |
| [LC 1434](https://leetcode.com/problems/number-of-ways-to-wear-different-hats-to-each-other/) | Number of Ways to Wear Different Hats | Hard | 状压DP |
| [LC 1655](https://leetcode.com/problems/distribute-repeating-integers/) | Distribute Repeating Integers | Hard | 状压DP |
| [LC 902](https://leetcode.com/problems/numbers-at-most-n-given-digit-set/) | Numbers At Most N Given Digit Set | Hard | 数位DP |
| [LC 600](https://leetcode.com/problems/non-negative-integers-without-consecutive-ones/) | Non-negative Integers without 1's | Hard | 数位DP |
| [LC 1012](https://leetcode.com/problems/numbers-with-repeated-digits/) | Numbers With Repeated Digits | Hard | 数位DP(补集) |
| [LC 233](https://leetcode.com/problems/number-of-digit-one/) | Number of Digit One | Hard | 数位DP/数学 |

---

[← 返回索引](index.md)
