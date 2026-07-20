# 手写链表实现 · Linked List Implementation

> 链表是非连续存储。每个节点存数据和指向下一个的指针。
> 优势：头部插入 O(1)，不需要扩容。劣势：无法随机访问，多占内存存指针。

---

## 一、单链表 (Singly Linked List)

```python
from typing import TypeVar, Generic

T = TypeVar("T")


class SinglyNode(Generic[T]):
    """单链表节点。"""

    def __init__(self, val: T, next: "SinglyNode[T] | None" = None) -> None:
        self.val: T = val
        self.next: "SinglyNode[T] | None" = next


class SinglyLinkedList(Generic[T]):
    """单链表（带头节点）。"""

    def __init__(self) -> None:
        self._head: SinglyNode[T] | None = None
        self._size: int = 0

    # === 增 ===

    def add_first(self, val: T) -> None:
        """头部插入 O(1)"""
        self._head = SinglyNode(val, self._head)
        self._size += 1

    def add_last(self, val: T) -> None:
        """尾部插入 O(n)。若维护 tail 指针可达 O(1)。"""
        if not self._head:
            self._head = SinglyNode(val)
        else:
            cur = self._head
            while cur.next:
                cur = cur.next
            cur.next = SinglyNode(val)
        self._size += 1

    def insert(self, index: int, val: T) -> None:
        """指定位置插入 O(index)。"""
        if index < 0 or index > self._size:
            raise IndexError(f"index {index} out of range")
        if index == 0:
            self.add_first(val)
            return

        cur = self._head
        for _ in range(index - 1):
            cur = cur.next  # type: ignore
        cur.next = SinglyNode(val, cur.next)  # type: ignore
        self._size += 1

    # === 删 ===

    def remove_first(self) -> T:
        """头部删除 O(1)"""
        if not self._head:
            raise IndexError("remove from empty list")
        val = self._head.val
        self._head = self._head.next
        self._size -= 1
        return val

    def remove_at(self, index: int) -> T:
        """删除指定位置 O(index)。"""
        if index < 0 or index >= self._size:
            raise IndexError(f"index {index} out of range")
        if index == 0:
            return self.remove_first()

        cur = self._head
        for _ in range(index - 1):
            cur = cur.next  # type: ignore
        val = cur.next.val  # type: ignore
        cur.next = cur.next.next  # type: ignore
        self._size -= 1
        return val

    def remove_value(self, val: T) -> bool:
        """删除第一个等于 val 的节点 O(n)。"""
        if not self._head:
            return False
        if self._head.val == val:
            self._head = self._head.next
            self._size -= 1
            return True

        cur = self._head
        while cur.next:
            if cur.next.val == val:
                cur.next = cur.next.next
                self._size -= 1
                return True
            cur = cur.next
        return False

    # === 查 ===

    def get(self, index: int) -> T:
        """按索引查找 O(index)。"""
        if index < 0 or index >= self._size:
            raise IndexError(f"index {index} out of range")
        cur = self._head
        for _ in range(index):
            cur = cur.next  # type: ignore
        return cur.val  # type: ignore

    def contains(self, val: T) -> bool:
        """判断是否存在 O(n)。"""
        cur = self._head
        while cur:
            if cur.val == val:
                return True
            cur = cur.next
        return False

    # === 工具 ===

    def __len__(self) -> int:
        return self._size

    def __iter__(self):
        cur = self._head
        while cur:
            yield cur.val
            cur = cur.next

    def __repr__(self) -> str:
        items = [str(v) for v in self]
        return f"LinkedList([{' -> '.join(items)}])"
```

---

## 二、双链表 (Doubly Linked List)

```python
class DoublyNode(Generic[T]):
    """双链表节点。"""

    def __init__(
        self,
        val: T,
        prev: "DoublyNode[T] | None" = None,
        next: "DoublyNode[T] | None" = None,
    ) -> None:
        self.val: T = val
        self.prev: "DoublyNode[T] | None" = prev
        self.next: "DoublyNode[T] | None" = next


class DoublyLinkedList(Generic[T]):
    """
    双链表（带头尾哨兵）。
    比单链表多的：可以从后往前遍历，删除节点时不需要找前驱。
    """

    def __init__(self) -> None:
        self._head = DoublyNode[T](None)  # type: ignore  # 头哨兵
        self._tail = DoublyNode[T](None)  # type: ignore  # 尾哨兵
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size: int = 0

    def add_last(self, val: T) -> None:
        """尾部插入 O(1)（因为有 tail 哨兵）"""
        node = DoublyNode(val, self._tail.prev, self._tail)
        self._tail.prev.next = node  # type: ignore
        self._tail.prev = node
        self._size += 1

    def add_first(self, val: T) -> None:
        """头部插入 O(1)"""
        node = DoublyNode(val, self._head, self._head.next)
        self._head.next.prev = node  # type: ignore
        self._head.next = node
        self._size += 1

    def remove_node(self, node: DoublyNode[T]) -> None:
        """删除给定节点 O(1)。不需要找前驱！"""
        node.prev.next = node.next  # type: ignore
        node.next.prev = node.prev  # type: ignore
        self._size -= 1

    def remove_last(self) -> T:
        if self._size == 0:
            raise IndexError("empty")
        node = self._tail.prev
        self.remove_node(node)  # type: ignore
        return node.val  # type: ignore

    def remove_first(self) -> T:
        if self._size == 0:
            raise IndexError("empty")
        node = self._head.next
        self.remove_node(node)  # type: ignore
        return node.val  # type: ignore

    def __len__(self) -> int:
        return self._size
```

---

## 三、复杂度对比

| 操作 | 单链表（无tail） | 单链表（有tail） | 双链表 |
|------|:---:|:---:|:---:|
| 头部插入 | O(1) | O(1) | O(1) |
| 尾部插入 | O(n) | O(1) | O(1) |
| 中间插入 | O(n) | O(n) | O(n) |
| 删除给定节点 | O(n)* | O(n)* | O(1) |
| 头部删除 | O(1) | O(1) | O(1) |
| 尾部删除 | O(n) | O(n) | O(1) |
| 按索引查找 | O(n) | O(n) | O(n) |

> \* 单链表删除给定节点需要找到前驱。双链表可以从节点自身找到前驱。

---

## 四、数组 vs 链表

| 维度 | 数组 | 链表 |
|------|------|------|
| 内存 | 连续，无额外指针 | 不连续，每个节点多一个/两个指针 |
| 随机访问 | O(1) | O(n) |
| 头部插入/删除 | O(n) | O(1) |
| 尾部插入 | 均摊O(1) | O(1) (有tail) |
| CPU缓存 | 友好（局部性原理） | 不友好 |

---

[← 返回索引](index.md)
