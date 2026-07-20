# LRU & LFU 缓存 · LRU & LFU Cache

> **LRU** (Least Recently Used)：淘汰**最久未使用**的。用哈希表 + 双向链表实现 O(1) 操作。
> **LFU** (Least Frequently Used)：淘汰**使用频次最低**的。用哈希表 + 频次桶实现 O(1) 操作。

---

## 一、LRU Cache · [LC 146](https://leetcode.com/problems/lru-cache/)

### 数据结构设计

```
哈希表: key → Node (O(1) 查找)
双向链表: 头部=最近使用, 尾部=最久未使用

get(key):
  1. 哈希表查找 key
  2. 将该节点移到链表头部 (标记为最近使用)
  3. 返回 value

put(key, value):
  1. 如果 key 已存在：更新 value，移到头部
  2. 如果 key 不存在：
     a. 容量满了 → 删除链表尾部节点 (最久未使用)
     b. 创建新节点，插入头部
```

### 完整实现

```python
class ListNode:
    """双向链表节点。"""

    def __init__(self, key: int = 0, val: int = 0):
        self.key = key
        self.val = val
        self.prev: "ListNode | None" = None
        self.next: "ListNode | None" = None


class LRUCache:
    """O(1) get, O(1) put。"""

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict[int, ListNode] = {}

        # 虚拟头尾节点，简化边界处理
        self.head = ListNode()  # 头部 → 最近使用
        self.tail = ListNode()  # 尾部 → 最久未使用
        self.head.next = self.tail
        self.tail.prev = self.head

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._move_to_head(node)  # 标记为最近使用
        return node.val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            node = self.cache[key]
            node.val = value
            self._move_to_head(node)
        else:
            if len(self.cache) >= self.capacity:
                self._evict_lru()
            node = ListNode(key, value)
            self.cache[key] = node
            self._add_to_head(node)

    # --- 链表操作 ---

    def _add_to_head(self, node: ListNode) -> None:
        """在头部插入节点。"""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def _remove_node(self, node: ListNode) -> None:
        """从链表中移除节点。"""
        node.prev.next = node.next
        node.next.prev = node.prev

    def _move_to_head(self, node: ListNode) -> None:
        """将节点移到头部（标记为最近使用）。"""
        self._remove_node(node)
        self._add_to_head(node)

    def _evict_lru(self) -> None:
        """淘汰最久未使用的节点（链表尾部的前一个）。"""
        lru = self.tail.prev
        self._remove_node(lru)
        del self.cache[lru.key]
```

### OrderedDict 简化版

```python
from collections import OrderedDict


class LRUCacheSimple:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict[int, int] = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)  # 移到末尾 = 最近使用
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # 弹出第一个 = 最久未使用
```

---

## 二、LFU Cache · [LC 460](https://leetcode.com/problems/lfu-cache/)

### 数据结构设计

```
key_table:    key → Node (O(1) 按 key 查找)
freq_table:   freq → DoubleLinkedList (O(1) 按频次找到对应桶)
min_freq:     记录当前最小频次（用于淘汰）

每个 Node 存：key, val, freq
freq_table 中每个 freq 对应一个双向链表（同一频次的节点按时间排列）
```

### 完整实现

```python
class LFUNode:
    def __init__(self, key: int = 0, val: int = 0, freq: int = 1):
        self.key = key
        self.val = val
        self.freq = freq
        self.prev: "LFUNode | None" = None
        self.next: "LFUNode | None" = None


class DoublyLinkedList:
    """双向链表，用于同一频次的节点集合。"""

    def __init__(self):
        self.head = LFUNode()
        self.tail = LFUNode()
        self.head.next = self.tail
        self.tail.prev = self.head
        self.size = 0

    def add_to_head(self, node: LFUNode) -> None:
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
        self.size += 1

    def remove(self, node: LFUNode) -> None:
        node.prev.next = node.next
        node.next.prev = node.prev
        self.size -= 1

    def remove_tail(self) -> LFUNode:
        """删除并返回最后一个节点（最久未使用的）。"""
        if self.size == 0:
            raise RuntimeError("empty list")
        node = self.tail.prev
        self.remove(node)
        return node

    def is_empty(self) -> bool:
        return self.size == 0


class LFUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.min_freq = 0
        self.key_table: dict[int, LFUNode] = {}
        self.freq_table: dict[int, DoublyLinkedList] = {}

    def get(self, key: int) -> int:
        if key not in self.key_table:
            return -1
        node = self.key_table[key]
        self._increase_freq(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        if self.capacity == 0:
            return

        if key in self.key_table:
            node = self.key_table[key]
            node.val = value
            self._increase_freq(node)
        else:
            if len(self.key_table) >= self.capacity:
                self._evict_lfu()
            node = LFUNode(key, value, 1)
            self.key_table[key] = node
            if 1 not in self.freq_table:
                self.freq_table[1] = DoublyLinkedList()
            self.freq_table[1].add_to_head(node)
            self.min_freq = 1

    def _increase_freq(self, node: LFUNode) -> None:
        """增加节点的访问频次。"""
        old_freq = node.freq
        # 从旧频次链表移除
        self.freq_table[old_freq].remove(node)
        if self.freq_table[old_freq].is_empty():
            del self.freq_table[old_freq]
            if old_freq == self.min_freq:
                self.min_freq += 1

        # 加入新频次链表
        node.freq += 1
        new_freq = node.freq
        if new_freq not in self.freq_table:
            self.freq_table[new_freq] = DoublyLinkedList()
        self.freq_table[new_freq].add_to_head(node)

    def _evict_lfu(self) -> None:
        """淘汰频次最低且最久未使用的节点。"""
        lst = self.freq_table[self.min_freq]
        node = lst.remove_tail()
        del self.key_table[node.key]
        if lst.is_empty():
            del self.freq_table[self.min_freq]
```

---

## 三、LRU vs LFU 对比

| 维度 | LRU | LFU |
|------|-----|-----|
| 淘汰策略 | 最久未使用 | 使用次数最少 |
| 数据结构 | 哈希表 + 双向链表 | 哈希表 + 频次桶(DLL) |
| get 复杂度 | O(1) | O(1) |
| put 复杂度 | O(1) | O(1) |
| 空间 | O(capacity) | O(capacity) |
| 适用场景 | 时间局部性 | 频率局部性 |
| 缺点 | 周期性访问会被淘汰 | 历史热点长期占据 |

---

## 四、常见变体

### 4.1 带 TTL 的缓存

```python
import time


class LRUCacheWithTTL:
    """带过期时间的 LRU Cache。"""

    def __init__(self, capacity: int, ttl: float):
        self.capacity = capacity
        self.ttl = ttl
        self.cache: dict[int, tuple[int, float]] = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        val, expire_time = self.cache[key]
        if time.time() > expire_time:
            del self.cache[key]
            return -1
        self.cache.move_to_end(key)
        return val

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (value, time.time() + self.ttl)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

---

## 五、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 146](https://leetcode.com/problems/lru-cache/) | LRU Cache | Medium | 哈希+双向链表 |
| [LC 460](https://leetcode.com/problems/lfu-cache/) | LFU Cache | Hard | 频次桶 |
| [LC 432](https://leetcode.com/problems/all-oone-data-structure/) | All O(1) Data Structure | Hard | 频次桶变体 |
| [LC 380](https://leetcode.com/problems/insert-delete-getrandom-o1/) | Insert Delete GetRandom O(1) | Medium | 哈希表+数组 |

---

[← 返回索引](index.md)
