# 链表 · Linked List

> 链表是基础数据结构，核心操作：**反转、双指针、合并**。链表题的递归写法往往更优雅。

---

## 一、链表节点定义

```python
class ListNode:
    def __init__(self, val: int = 0, next: "ListNode | None" = None):
        self.val = val
        self.next = next
```

---

## 二、反转链表系列

### 2.1 完全反转（迭代+递归）· [LC 206](https://leetcode.com/problems/reverse-linked-list/)

```python
# 迭代写法
def reverse_list(head: ListNode | None) -> ListNode | None:
    """迭代反转：维护 prev, cur, nxt 三个指针。"""
    prev = None
    cur = head
    while cur:
        nxt = cur.next    # 暂存下一个
        cur.next = prev   # 反转指针
        prev = cur        # 前进
        cur = nxt
    return prev


# 递归写法
def reverse_list_recursive(head: ListNode | None) -> ListNode | None:
    """
    递归反转：
    reverse(1→2→3→null)
    = 3→2→1→null
    """
    if not head or not head.next:
        return head

    last = reverse_list_recursive(head.next)
    # head.next 现在指向 last 的尾节点
    head.next.next = head  # 把 head 接到反转后的链表尾部
    head.next = None       # head 现在成尾节点
    return last
```

### 2.2 反转前 N 个节点

```python
successor: ListNode | None = None  # 记录第 N+1 个节点

def reverse_first_n(head: ListNode | None, n: int) -> ListNode | None:
    """反转链表的前 n 个节点。"""
    global successor
    if n == 1:
        successor = head.next
        return head
    if not head:
        return None

    last = reverse_first_n(head.next, n - 1)
    head.next.next = head
    head.next = successor
    return last
```

### 2.3 区间反转 · [LC 92](https://leetcode.com/problems/reverse-linked-list-ii/)

```python
def reverse_between(head: ListNode | None, left: int, right: int) -> ListNode | None:
    """
    反转从 left 到 right 的部分。
    1. 找到 left 的前驱
    2. 反转 left 到 right
    3. 重新连接
    """
    dummy = ListNode(0, head)

    # 找到 left 的前驱
    pre = dummy
    for _ in range(left - 1):
        pre = pre.next

    # 反转 [left, right] 区间
    # 头插法：cur 始终指向被反转区间的第一个节点
    cur = pre.next
    for _ in range(right - left):
        nxt = cur.next
        cur.next = nxt.next
        nxt.next = pre.next
        pre.next = nxt

    return dummy.next


# 递归写法（更简洁）
def reverse_between_recursive(
    head: ListNode | None, left: int, right: int
) -> ListNode | None:
    """递归区间反转。"""
    if left == 1:
        return reverse_first_n(head, right)

    if head:
        head.next = reverse_between_recursive(head.next, left - 1, right - 1)
    return head
```

### 2.4 K 个一组反转 · [LC 25](https://leetcode.com/problems/reverse-nodes-in-k-group/)

```python
def reverse_k_group(head: ListNode | None, k: int) -> ListNode | None:
    """
    K 个一组反转链表。
    1. 找到第 k 个节点（区间尾部）
    2. 反转区间
    3. 递归处理剩余部分
    """

    # 找第 k 个节点
    def find_kth(node: ListNode | None, k: int) -> ListNode | None:
        cur = node
        for _ in range(k):
            if not cur:
                return None
            cur = cur.next
        return cur

    # 反转整个区间 [a, b)，b 不包含在区间内
    def reverse(a: ListNode, b: ListNode | None) -> ListNode:
        prev, cur = None, a
        while cur != b:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        return prev

    if not head:
        return None

    # 找到第 k 个节点（下一组的开始）
    kth = find_kth(head, k - 1)  # 本组的最后一个节点
    if not kth:
        return head  # 不足 k 个，不反转

    nxt_group = kth.next  # 下一组的头

    # 反转当前组（head 到 kth）
    reverse(head, nxt_group)

    # head 现在是当前组的尾节点，连接下一组
    head.next = reverse_k_group(nxt_group, k)

    return kth  # 返回新头（原区间尾）
```

---

## 三、快慢指针

### 3.1 判断回文链表 · [LC 234](https://leetcode.com/problems/palindrome-linked-list/)

```python
def is_palindrome(head: ListNode | None) -> bool:
    """快慢指针找中点 + 反转后半段 + 逐节点比较。"""

    # 找中点（偶数时找第一个中点）
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next

    # 反转后半段
    prev = None
    while slow:
        nxt = slow.next
        slow.next = prev
        prev = slow
        slow = nxt

    # 比较前后两段
    left, right = head, prev
    while right:  # 后半段可能短1个（奇数情况）
        if left.val != right.val:
            return False
        left = left.next
        right = right.next

    return True
```

### 3.2 链表交点 · [LC 160](https://leetcode.com/problems/intersection-of-two-linked-lists/)

```python
def get_intersection_node(
    head_a: ListNode | None, head_b: ListNode | None,
) -> ListNode | None:
    """
    双指针各走自己的链表，走到末尾后切换到对方链表。
    两指针相遇时就是交点（或都是 None 表示无交点）。
    """
    pa, pb = head_a, head_b
    while pa != pb:
        pa = pa.next if pa else head_b
        pb = pb.next if pb else head_a
    return pa
```

---

## 四、合并链表

### 4.1 合并两个有序链表 · [LC 21](https://leetcode.com/problems/merge-two-sorted-lists/)

```python
def merge_two_lists(
    l1: ListNode | None, l2: ListNode | None,
) -> ListNode | None:
    """迭代合并。"""
    dummy = ListNode()
    cur = dummy

    while l1 and l2:
        if l1.val < l2.val:
            cur.next = l1
            l1 = l1.next
        else:
            cur.next = l2
            l2 = l2.next
        cur = cur.next

    cur.next = l1 or l2  # 接上剩余部分
    return dummy.next


# 递归写法
def merge_two_lists_recursive(
    l1: ListNode | None, l2: ListNode | None,
) -> ListNode | None:
    if not l1:
        return l2
    if not l2:
        return l1
    if l1.val < l2.val:
        l1.next = merge_two_lists_recursive(l1.next, l2)
        return l1
    else:
        l2.next = merge_two_lists_recursive(l1, l2.next)
        return l2
```

### 4.2 合并 K 个升序链表 · [LC 23](https://leetcode.com/problems/merge-k-sorted-lists/)

```python
import heapq


def merge_k_lists(lists: list[ListNode | None]) -> ListNode | None:
    """
    用小顶堆做 K 路归并。每次取出最小的节点。
    O(N log K)，N = 总节点数，K = 链表数。
    """
    heap: list[tuple[int, int, ListNode]] = []

    for i, node in enumerate(lists):
        if node:
            heapq.heappush(heap, (node.val, i, node))
            # i 用于处理 val 相同的 tie-break

    dummy = ListNode()
    cur = dummy

    while heap:
        _, i, node = heapq.heappop(heap)
        cur.next = node
        cur = cur.next
        if node.next:
            heapq.heappush(heap, (node.next.val, i, node.next))

    return dummy.next
```

---

## 五、总结

| 操作 | 方法 | 复杂度 |
|------|------|--------|
| 反转链表 | 迭代/递归 | O(n) |
| 找中点 | 快慢指针 | O(n) |
| 判环 | 快慢指针 | O(n) |
| 合并两个有序链表 | 双指针 | O(n+m) |
| 合并K个有序链表 | 堆 | O(N log K) |
| 删除倒数第K个 | 快慢指针间隔K | O(n) |

---

## 六、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 206](https://leetcode.com/problems/reverse-linked-list/) | Reverse Linked List | Easy | 反转模板 |
| [LC 92](https://leetcode.com/problems/reverse-linked-list-ii/) | Reverse Linked List II | Medium | 区间反转 |
| [LC 25](https://leetcode.com/problems/reverse-nodes-in-k-group/) | Reverse Nodes in k-Group | Hard | K个一组反转 |
| [LC 141](https://leetcode.com/problems/linked-list-cycle/) | Linked List Cycle | Easy | 快慢指针判环 |
| [LC 142](https://leetcode.com/problems/linked-list-cycle-ii/) | Linked List Cycle II | Medium | 环入口 |
| [LC 876](https://leetcode.com/problems/middle-of-the-linked-list/) | Middle of Linked List | Easy | 快慢指针中点 |
| [LC 19](https://leetcode.com/problems/remove-nth-node-from-end-of-list/) | Remove Nth Node From End | Medium | 间隔N快慢指针 |
| [LC 21](https://leetcode.com/problems/merge-two-sorted-lists/) | Merge Two Sorted Lists | Easy | 合并两个 |
| [LC 23](https://leetcode.com/problems/merge-k-sorted-lists/) | Merge k Sorted Lists | Hard | 堆K路归并 |
| [LC 160](https://leetcode.com/problems/intersection-of-two-linked-lists/) | Intersection of Two Linked Lists | Easy | 双指针交点 |
| [LC 234](https://leetcode.com/problems/palindrome-linked-list/) | Palindrome Linked List | Easy | 中点+反转+比较 |
| [LC 143](https://leetcode.com/problems/reorder-list/) | Reorder List | Medium | 中点+反转+合并 |
| [LC 148](https://leetcode.com/problems/sort-list/) | Sort List | Medium | 归并排序链表 |

---

[← 返回索引](index.md)
