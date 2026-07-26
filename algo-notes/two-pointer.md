# 双指针技巧 · Two Pointers

> 双指针分为三类：**快慢指针**（链表）、**左右指针**（数组）、**前后指针**（原地修改）。本质是用两个指针维护一个区间或关系，将 O(n²) 降到 O(n)。

---

## 一、快慢指针（链表专用）

### 1.1 判断链表是否有环 · [LC 141](https://leetcode.com/problems/linked-list-cycle/)

```python
class ListNode:
    def __init__(self, x: int = 0, next: "ListNode | None" = None):
        self.val = x
        self.next = next


def has_cycle(head: ListNode | None) -> bool:
    """快指针每次走2步，慢指针走1步，相遇则有环。"""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            return True
    return False
```

### 1.2 找环的起点 · [LC 142](https://leetcode.com/problems/linked-list-cycle-ii/)

```python
def detect_cycle(head: ListNode | None) -> ListNode | None:
    """
    1. 快慢指针相遇确认有环
    2. 相遇后，一个指针回到 head，两个指针同速前进
    3. 再次相遇处就是环起点
    """
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow == fast:
            # 找环起点
            slow2 = head
            while slow2 != slow:
                slow2 = slow2.next
                slow = slow.next
            return slow2
    return None
```

**证明**：设 head 到环起点距离为 `a`，环起点到相遇点距离为 `b`，相遇点到环起点距离为 `c`（环长 = `b + c`）。相遇时：`2(a+b) = a + b + n(b+c)` → `a = (n-1)(b+c) + c`。所以从 head 出发一个指针，从相遇点出发一个指针，同速前进，会在环起点相遇。

### 1.3 找链表中点 · [LC 876](https://leetcode.com/problems/middle-of-the-linked-list/)

```python
def middle_node(head: ListNode | None) -> ListNode | None:
    """快指针到终点时，慢指针刚好在中点。"""
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
    return slow
```

> 若有两个中点（偶数长度），此写法返回**第二个**中点。若要第一个中点，用 `fast.next and fast.next.next`。

### 1.4 删除倒数第 K 个节点 · [LC 19](https://leetcode.com/problems/remove-nth-node-from-end-of-list/)

```python
def remove_nth_from_end(head: ListNode | None, n: int) -> ListNode | None:
    """
    让 fast 先走 n 步，然后 slow 和 fast 同步走。
    当 fast 到末尾时，slow 在倒数第 n 个节点的前驱。
    """
    dummy = ListNode(0, head)
    slow = fast = dummy

    for _ in range(n):
        fast = fast.next

    while fast.next:
        slow = slow.next
        fast = fast.next

    slow.next = slow.next.next  # 删除倒数第 n 个
    return dummy.next
```

---

## 二、左右指针（有序数组 nSum）

### 2.1 两数之和 II · [LC 167](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/)

```python
def two_sum(numbers: list[int], target: int) -> list[int]:
    """有序数组，O(n) 两数之和，返回的是 1-based 索引。"""
    left, right = 0, len(numbers) - 1
    while left < right:
        s = numbers[left] + numbers[right]
        if s == target:
            return [left + 1, right + 1]
        elif s < target:
            left += 1
        else:
            right -= 1
    return [-1, -1]
```

### 2.2 nSum 通用模板

```python
def n_sum(
    nums: list[int], n: int, start: int, target: int
) -> list[list[int]]:
    """
    通用 nSum 模板：在 nums[start:] 中找到 n 个数之和为 target。
    调用前需对 nums 排序。
    """
    size = len(nums)
    res: list[list[int]] = []

    # base case: n < 2 或 数组长度不足
    if n < 2 or size - start < n:
        return res

    # twoSum 是递归基
    if n == 2:
        left, right = start, size - 1
        while left < right:
            s = nums[left] + nums[right]
            lo_val, hi_val = nums[left], nums[right]
            if s < target:
                while left < right and nums[left] == lo_val:
                    left += 1
            elif s > target:
                while left < right and nums[right] == hi_val:
                    right -= 1
            else:
                res.append([lo_val, hi_val])
                # 跳过重复元素
                while left < right and nums[left] == lo_val:
                    left += 1
                while left < right and nums[right] == hi_val:
                    right -= 1
    else:
        # n > 2: 递归
        i = start
        while i < size:
            sub_results = n_sum(nums, n - 1, i + 1, target - nums[i])
            for sub in sub_results:
                res.append([nums[i]] + sub)
            # 跳过重复元素
            val = nums[i]
            while i < size and nums[i] == val:
                i += 1

    return res


# 使用示例
def three_sum(nums: list[int]) -> list[list[int]]:
    """[LC 15](https://leetcode.com/problems/3sum/) 三数之和 = 0"""
    nums.sort()
    return n_sum(nums, 3, 0, 0)


def four_sum(nums: list[int], target: int) -> list[list[int]]:
    """[LC 18](https://leetcode.com/problems/4sum/) 四数之和"""
    nums.sort()
    return n_sum(nums, 4, 0, target)
```

### 2.3 盛水最多容器 · [LC 11](https://leetcode.com/problems/container-with-most-water/)

```python
def max_area(height: list[int]) -> int:
    """左右指针向中间收缩，谁矮谁移动。"""
    left, right = 0, len(height) - 1
    ans = 0
    while left < right:
        area = min(height[left], height[right]) * (right - left)
        ans = max(ans, area)
        if height[left] < height[right]:
            left += 1
        else:
            right -= 1
    return ans
```

### 2.4 接雨水 · [LC 42](https://leetcode.com/problems/trapping-rain-water/)

```python
def trap(height: list[int]) -> int:
    """双指针法，O(n) 时间 O(1) 空间。"""
    left, right = 0, len(height) - 1
    left_max = right_max = ans = 0

    while left < right:
        left_max = max(left_max, height[left])
        right_max = max(right_max, height[right])

        if left_max < right_max:
            ans += left_max - height[left]
            left += 1
        else:
            ans += right_max - height[right]
            right -= 1

    return ans
```

---

## 三、前后指针（原地修改）

### 3.1 删除有序数组中的重复项 · [LC 26](https://leetcode.com/problems/remove-duplicates-from-sorted-array/)

```python
def remove_duplicates(nums: list[int]) -> int:
    """返回新长度，slow 维护去重后的尾部。"""
    if not nums:
        return 0

    slow = 0  # 指向最后一个不重复的位置
    for fast in range(1, len(nums)):
        if nums[fast] != nums[slow]:
            slow += 1
            nums[slow] = nums[fast]
    return slow + 1
```

### 3.2 移除元素 · [LC 27](https://leetcode.com/problems/remove-element/)

```python
def remove_element(nums: list[int], val: int) -> int:
    """原地移除所有值等于 val 的元素，返回新长度。"""
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != val:
            nums[slow] = nums[fast]
            slow += 1
    return slow
```

### 3.3 移动零 · [LC 283](https://leetcode.com/problems/move-zeroes/)

```python
def move_zeroes(nums: list[int]) -> None:
    """把所有 0 移到末尾，保持非零元素相对顺序。"""
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1
```

---

## 四、字符串反转技巧（整体反转 + 局部反转）

> 双指针原地反转（`while l < r: swap; l+=1; r-=1`）不仅能反转整个字符串，
> 组合起来还能做"只反转一部分""调整顺序但不改变每部分内部顺序"这类操作，
> 不需要额外的数组/栈就能原地完成。

### 4.1 反转字符串里的单词 · [LC 151](https://leetcode.com/problems/reverse-words-in-a-string/)

```python
def reverse_words(s: str) -> str:
    """
    要把单词顺序反转，同时单词内部字母顺序不能变。
    技巧：先反转整个字符串（这样单词顺序对了，但每个单词内部也被反转了），
         再把每个单词单独反转回来（修正单词内部顺序）。
    额外要处理多余空格（连续空格/首尾空格），先原地压缩掉。
    """
    chars = list(s)
    n = len(chars)

    # 1. 双指针原地去除多余空格：只保留单词间恰好一个空格
    slow = fast = 0
    while fast < n and chars[fast] == " ":       # 跳过开头空格
        fast += 1
    while fast < n:
        if chars[fast] != " ":
            chars[slow] = chars[fast]
            slow += 1
            fast += 1
        else:
            chars[slow] = " "
            slow += 1
            while fast < n and chars[fast] == " ":  # 跳过单词间的连续空格
                fast += 1
    if slow > 0 and chars[slow - 1] == " ":          # 去掉结尾可能剩的一个空格
        slow -= 1
    chars = chars[:slow]

    def reverse(arr: list[str], l: int, r: int) -> None:
        while l < r:
            arr[l], arr[r] = arr[r], arr[l]
            l += 1
            r -= 1

    # 2. 整体反转
    reverse(chars, 0, len(chars) - 1)

    # 3. 每个单词各自反转回来
    start = 0
    for i in range(len(chars) + 1):
        if i == len(chars) or chars[i] == " ":
            reverse(chars, start, i - 1)
            start = i + 1

    return "".join(chars)
```

### 4.2 左旋转字符串 · [剑指 Offer 58-II](https://leetcode.cn/problems/zuo-xuan-zhuan-zi-fu-chuan-lcof/)

```python
def left_rotate(s: str, n: int) -> str:
    """
    把字符串前 n 个字符移到末尾，例如 "abcdefg" 左旋 2 位 -> "cdefgab"。
    技巧（三次反转）：
      1. 反转前 n 个字符： "abcdefg" -> "bacdefg"
      2. 反转剩下的字符：           -> "bagfedc"
      3. 反转整个字符串：           -> "cdefgab"
    直觉：把两段各自"倒过来"再整体"倒过来"，相当于两段互换了位置，
         且每段内部顺序被复原——这和"反转单词顺序"是同一个思路的镜像用法。
    """
    chars = list(s)
    length = len(chars)
    n %= length

    def reverse(arr: list[str], l: int, r: int) -> None:
        while l < r:
            arr[l], arr[r] = arr[r], arr[l]
            l += 1
            r -= 1

    reverse(chars, 0, n - 1)
    reverse(chars, n, length - 1)
    reverse(chars, 0, length - 1)
    return "".join(chars)
```

> 这两题是同一个"反转组合技"的两种用法：LC 151 是"先整体反转、再修正每一段内部顺序"；
> 左旋转字符串是反过来"先修正每一段内部顺序、再整体反转"——遇到"原地调整顺序但不能用额外空间"的字符串/数组题，可以想想能不能拆成几段反转来做。

---

## 五、总结

| 类型 | 适用场景 | 核心技巧 |
|------|----------|----------|
| 快慢指针 | 链表环检测、中点、倒数第K个 | 快指针一次两步，慢指针一步 |
| 左右指针 | 有序数组、nSum、盛水/接雨水 | 相向而行，根据条件移动左或右 |
| 前后指针 | 原地去重、移除、移动 | slow 指向结果尾部，fast 扫描 |
| 反转组合 | 单词反转、字符串左旋 | 整体反转 + 局部反转的组合 |

---

## 六、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 141](https://leetcode.com/problems/linked-list-cycle/) | Linked List Cycle | Easy | 快慢指针判环 |
| [LC 142](https://leetcode.com/problems/linked-list-cycle-ii/) | Linked List Cycle II | Medium | 判环 + 找起点 |
| [LC 876](https://leetcode.com/problems/middle-of-the-linked-list/) | Middle of the Linked List | Easy | 快慢指针找中点 |
| [LC 19](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) | Remove Nth Node From End | Medium | 间隔 n 步快慢指针 |
| [LC 167](https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/) | Two Sum II | Medium | 左右指针 |
| [LC 15](https://leetcode.com/problems/3sum/) | 3Sum | Medium | nSum 递归 |
| [LC 18](https://leetcode.com/problems/4sum/) | 4Sum | Medium | nSum 递归 |
| [LC 11](https://leetcode.com/problems/container-with-most-water/) | Container With Most Water | Medium | 左右指针 |
| [LC 42](https://leetcode.com/problems/trapping-rain-water/) | Trapping Rain Water | Hard | 双指针 / 单调栈 |
| [LC 26](https://leetcode.com/problems/remove-duplicates-from-sorted-array/) | Remove Duplicates | Easy | 快慢指针原地去重 |
| [LC 27](https://leetcode.com/problems/remove-element/) | Remove Element | Easy | 快慢指针原地移除 |
| [LC 283](https://leetcode.com/problems/move-zeroes/) | Move Zeroes | Easy | 快慢指针原地移动 |
| [LC 160](https://leetcode.com/problems/intersection-of-two-linked-lists/) | Intersection of Two Linked Lists | Easy | 双指针走完自己的链表 |
| [LC 234](https://leetcode.com/problems/palindrome-linked-list/) | Palindrome Linked List | Easy | 中点 + 反转 + 对比 |
| [LC 151](https://leetcode.com/problems/reverse-words-in-a-string/) | Reverse Words in a String | Medium | 整体反转+单词反转 |
| [剑指 Offer 58-II](https://leetcode.cn/problems/zuo-xuan-zhuan-zi-fu-chuan-lcof/) | 左旋转字符串 | Easy | 三次反转 |

---

[← 返回索引](index.md)
