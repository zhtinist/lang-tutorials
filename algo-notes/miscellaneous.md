# 杂项技巧 · Miscellaneous Techniques

> 包含面试中不太属于标准分类的高频技巧：**快速选择、摩尔投票、蓄水池抽样、洗牌**。

---

## 一、快速选择 · Quick Select

> 找第 K 大/小元素，期望 O(n)。与快速排序的区别：每次 partition 后只递归一侧。

### 第 K 大元素 · [LC 215](https://leetcode.com/problems/kth-largest-element-in-an-array/)

```python
import random


def find_kth_largest(nums: list[int], k: int) -> int:
    """O(n) 期望时间。"""

    def partition(lo: int, hi: int, pivot_idx: int) -> int:
        pivot = nums[pivot_idx]
        nums[pivot_idx], nums[hi] = nums[hi], nums[pivot_idx]
        store_idx = lo
        for i in range(lo, hi):
            if nums[i] > pivot:  # 大元素放左边（第K大）
                nums[store_idx], nums[i] = nums[i], nums[store_idx]
                store_idx += 1
        nums[store_idx], nums[hi] = nums[hi], nums[store_idx]
        return store_idx

    def quickselect(lo: int, hi: int, k_idx: int) -> int:
        if lo == hi:
            return nums[lo]
        pivot_idx = random.randint(lo, hi)
        pivot_idx = partition(lo, hi, pivot_idx)
        if pivot_idx == k_idx:
            return nums[pivot_idx]
        elif pivot_idx < k_idx:
            return quickselect(pivot_idx + 1, hi, k_idx)
        else:
            return quickselect(lo, pivot_idx - 1, k_idx)

    return quickselect(0, len(nums) - 1, k - 1)
```

### 对比

| 方法 | 复杂度 | 适用 |
|------|--------|------|
| 排序 | O(n log n) | 多次查询 |
| 堆 | O(n log k) | k 很小 |
| 快速选择 | O(n) 期望 | 单次查询 |
| 桶排序/计数 | O(n) | 值域有限 |

---

## 二、摩尔投票 · Boyer-Moore Majority Vote

> 求出现次数 > n/2（或 > n/3）的元素。O(n) 时间 O(1) 空间。

### 2.1 多数元素 · [LC 169](https://leetcode.com/problems/majority-element/)

```python
def majority_element(nums: list[int]) -> int:
    """找出现次数 > n/2 的元素。"""
    candidate = 0
    count = 0

    for v in nums:
        if count == 0:
            candidate = v
        count += 1 if v == candidate else -1

    return candidate
```

**原理**：不同的元素两两抵消，最后剩下的一定是多数元素。

### 2.2 求众数 II · [LC 229](https://leetcode.com/problems/majority-element-ii/)

```python
def majority_element_ii(nums: list[int]) -> list[int]:
    """找出现次数 > n/3 的元素（最多 2 个）。"""
    cand1 = cand2 = 0
    cnt1 = cnt2 = 0

    for v in nums:
        if cnt1 > 0 and v == cand1:
            cnt1 += 1
        elif cnt2 > 0 and v == cand2:
            cnt2 += 1
        elif cnt1 == 0:
            cand1, cnt1 = v, 1
        elif cnt2 == 0:
            cand2, cnt2 = v, 1
        else:
            cnt1 -= 1
            cnt2 -= 1

    # 验证
    ans: list[int] = []
    n = len(nums)
    if cnt1 > 0 and nums.count(cand1) > n // 3:
        ans.append(cand1)
    if cnt2 > 0 and nums.count(cand2) > n // 3:
        ans.append(cand2)
    return ans
```

---

## 三、蓄水池抽样 · Reservoir Sampling

> 从流式数据中用 O(1) 空间**等概率**随机选出 k 个元素。

### [LC 382](https://leetcode.com/problems/linked-list-random-node/) 链表随机节点（k=1）

```python
import random


class Solution:
    """从链表中等概率随机返回一个节点值。"""

    def __init__(self, head: "ListNode | None"):
        self.head = head

    def get_random(self) -> int:
        """
        蓄水池抽样 k=1：
        第 i 个元素以 1/i 的概率替换当前结果。
        """
        ans = 0
        i = 1
        cur = self.head
        while cur:
            if random.randint(1, i) == 1:
                ans = cur.val
            cur = cur.next
            i += 1
        return ans
```

### 通用蓄水池抽样（k > 1）

```python
import random


def reservoir_sample(stream: list[int], k: int) -> list[int]:
    """从 stream 中等概率选出 k 个元素。"""
    reservoir = stream[:k]

    for i in range(k, len(stream)):
        j = random.randint(0, i)
        if j < k:
            reservoir[j] = stream[i]

    return reservoir
```

---

## 四、洗牌算法 · Fisher-Yates Shuffle

### [LC 384](https://leetcode.com/problems/shuffle-an-array/) 打乱数组

```python
import random


class Shuffle:
    def __init__(self, nums: list[int]):
        self.nums = nums
        self.original = nums.copy()

    def reset(self) -> list[int]:
        self.nums = self.original.copy()
        return self.nums

    def shuffle(self) -> list[int]:
        """
        Fisher-Yates 洗牌：
        从后往前，每个位置与前面的随机位置交换。
        """
        for i in range(len(self.nums) - 1, 0, -1):
            j = random.randint(0, i)
            self.nums[i], self.nums[j] = self.nums[j], self.nums[i]
        return self.nums
```

---

## 五、随机权重选择 · [LC 528](https://leetcode.com/problems/random-pick-with-weight/)

```python
import random
import bisect


class PickIndex:
    """按权重随机选择。前缀和 + 二分。"""

    def __init__(self, w: list[int]):
        self.prefix = [0]
        for weight in w:
            self.prefix.append(self.prefix[-1] + weight)
        self.total = self.prefix[-1]

    def pick_index(self) -> int:
        target = random.randint(1, self.total)  # 1..total
        return bisect.bisect_left(self.prefix, target) - 1
```

---

## 六、前缀树 + DFS（单词搜索 II）· [LC 212](https://leetcode.com/problems/word-search-ii/)

> 已在 Trie 章节详述。这里是回顾：Trie 剪枝 + 网格 DFS = 高效单词搜索。

核心思路：
1. 把所有单词插入 Trie
2. 遍历网格的每个位置，DFS搜索
3. 若当前前缀不在Trie中，立即剪枝
4. 找到单词后从Trie中删除以去重

---

## 七、总结

| 技巧 | 场景 | 复杂度 |
|------|------|--------|
| 快速选择 | TopK 单次查询 | O(n) 期望 |
| 摩尔投票 | 找 > n/2 或 > n/3 的元素 | O(n), O(1) |
| 蓄水池抽样 | 流式数据等概率随机选 | O(n), O(1) |
| 洗牌算法 | 等概率随机排列 | O(n) |
| 按权重随机选 | 前缀和+二分 | O(log n) 每次 |

---

## 八、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 215](https://leetcode.com/problems/kth-largest-element-in-an-array/) | Kth Largest Element | Medium | 快速选择 |
| [LC 169](https://leetcode.com/problems/majority-element/) | Majority Element | Easy | 摩尔投票 |
| [LC 229](https://leetcode.com/problems/majority-element-ii/) | Majority Element II | Medium | 双候选摩尔投票 |
| [LC 382](https://leetcode.com/problems/linked-list-random-node/) | Linked List Random Node | Medium | 蓄水池抽样 |
| [LC 384](https://leetcode.com/problems/shuffle-an-array/) | Shuffle an Array | Medium | Fisher-Yates |
| [LC 528](https://leetcode.com/problems/random-pick-with-weight/) | Random Pick with Weight | Medium | 前缀和+二分 |
| [LC 398](https://leetcode.com/problems/random-pick-index/) | Random Pick Index | Medium | 蓄水池抽样 |
| [LC 212](https://leetcode.com/problems/word-search-ii/) | Word Search II | Hard | Trie+DFS |

---

[← 返回索引](index.md)
