# 手写栈和队列 · Stack & Queue Implementation

> 栈 (Stack)：LIFO（后进先出）。队列 (Queue)：FIFO（先进先出）。
> 都有**链表实现**和**数组实现**两种方式。

---

## 一、栈的实现

### 1.1 链表实现栈

```python
from typing import TypeVar, Generic

T = TypeVar("T")


class StackNode(Generic[T]):
    def __init__(self, val: T, next: "StackNode[T] | None" = None) -> None:
        self.val = val
        self.next = next


class LinkedListStack(Generic[T]):
    """链表栈：push/pop 都在头部，O(1)。"""

    def __init__(self) -> None:
        self._head: StackNode[T] | None = None
        self._size: int = 0

    def push(self, val: T) -> None:
        self._head = StackNode(val, self._head)
        self._size += 1

    def pop(self) -> T:
        if not self._head:
            raise IndexError("pop from empty stack")
        val = self._head.val
        self._head = self._head.next
        self._size -= 1
        return val

    def peek(self) -> T:
        if not self._head:
            raise IndexError("peek from empty stack")
        return self._head.val

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0
```

### 1.2 数组实现栈

```python
class ArrayStack(Generic[T]):
    """数组栈：尾部是栈顶，push/pop O(1)"""

    def __init__(self) -> None:
        self._data: list[T] = []
        # 直接用 Python list，append/pop 都是 O(1)

    def push(self, val: T) -> None:
        self._data.append(val)

    def pop(self) -> T:
        return self._data.pop()

    def peek(self) -> T:
        return self._data[-1]

    def __len__(self) -> int:
        return len(self._data)

    def is_empty(self) -> bool:
        return len(self._data) == 0
```

---

## 二、队列的实现

### 2.1 链表实现队列

```python
class QueueNode(Generic[T]):
    def __init__(self, val: T, next: "QueueNode[T] | None" = None):
        self.val = val
        self.next = next


class LinkedListQueue(Generic[T]):
    """
    链表队列：
    - enqueue: 尾部插入 O(1)（维护 tail 指针）
    - dequeue: 头部删除 O(1)
    """

    def __init__(self) -> None:
        self._head: QueueNode[T] | None = None
        self._tail: QueueNode[T] | None = None
        self._size: int = 0

    def enqueue(self, val: T) -> None:
        node = QueueNode(val)
        if not self._tail:
            self._head = self._tail = node
        else:
            self._tail.next = node
            self._tail = node
        self._size += 1

    def dequeue(self) -> T:
        if not self._head:
            raise IndexError("dequeue from empty queue")
        val = self._head.val
        self._head = self._head.next
        if not self._head:
            self._tail = None
        self._size -= 1
        return val

    def peek(self) -> T:
        if not self._head:
            raise IndexError("peek from empty queue")
        return self._head.val

    def __len__(self) -> int:
        return self._size
```

### 2.2 环形数组实现队列

```python
class CircularQueue(Generic[T]):
    """
    用数组 + 环形指针实现队列，避免 dequeue 时的 O(n) 搬移。
    两个指针：front（队首）, rear（队尾的下一个空位）。
    浪费一个位置来区分空和满。
    """

    def __init__(self, capacity: int) -> None:
        self._data: list[T | None] = [None] * (capacity + 1)  # +1 用于区分
        self._front: int = 0       # 队首索引
        self._rear: int = 0        # 队尾的下一个空位
        self._capacity: int = capacity

    def enqueue(self, val: T) -> None:
        if self.is_full():
            raise RuntimeError("queue is full")
        self._data[self._rear] = val
        self._rear = (self._rear + 1) % len(self._data)

    def dequeue(self) -> T:
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        val = self._data[self._front]  # type: ignore
        self._data[self._front] = None
        self._front = (self._front + 1) % len(self._data)
        return val

    def peek(self) -> T:
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._data[self._front]  # type: ignore

    def is_empty(self) -> bool:
        return self._front == self._rear

    def is_full(self) -> bool:
        return (self._rear + 1) % len(self._data) == self._front

    def __len__(self) -> int:
        if self._rear >= self._front:
            return self._rear - self._front
        return len(self._data) - self._front + self._rear
```

---

## 三、双端队列 (Deque)

```python
class DequeNode(Generic[T]):
    def __init__(
        self,
        val: T,
        prev: "DequeNode[T] | None" = None,
        next: "DequeNode[T] | None" = None,
    ):
        self.val = val
        self.prev = prev
        self.next = next


class LinkedListDeque(Generic[T]):
    """双端队列：头部和尾部都可以 O(1) 插入和删除。"""

    def __init__(self) -> None:
        self._head = DequeNode[T](None)  # type: ignore
        self._tail = DequeNode[T](None)  # type: ignore
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size: int = 0

    def add_first(self, val: T) -> None:
        node = DequeNode(val, self._head, self._head.next)
        self._head.next.prev = node  # type: ignore
        self._head.next = node
        self._size += 1

    def add_last(self, val: T) -> None:
        node = DequeNode(val, self._tail.prev, self._tail)
        self._tail.prev.next = node  # type: ignore
        self._tail.prev = node
        self._size += 1

    def remove_first(self) -> T:
        if self._size == 0:
            raise IndexError("empty")
        node = self._head.next
        self._head.next = node.next  # type: ignore
        node.next.prev = self._head  # type: ignore
        self._size -= 1
        return node.val  # type: ignore

    def remove_last(self) -> T:
        if self._size == 0:
            raise IndexError("empty")
        node = self._tail.prev
        self._tail.prev = node.prev  # type: ignore
        node.prev.next = self._tail  # type: ignore
        self._size -= 1
        return node.val  # type: ignore

    def __len__(self) -> int:
        return self._size
```

---

## 四、栈和队列相互实现

### 用两个栈实现队列 ([LC 232](https://leetcode.com/problems/implement-queue-using-stacks/))

```python
class MyQueue:
    """
    push: O(1) 到 s1
    pop/peek: s2 不为空则从 s2 pop，否则把 s1 全部倒到 s2 再 pop
    均摊 O(1)
    """

    def __init__(self):
        self.s1: list[int] = []  # 输入栈
        self.s2: list[int] = []  # 输出栈

    def push(self, x: int) -> None:
        self.s1.append(x)

    def _transfer(self) -> None:
        """当 s2 为空时，把 s1 全部倒到 s2。"""
        if not self.s2:
            while self.s1:
                self.s2.append(self.s1.pop())

    def pop(self) -> int:
        self._transfer()
        return self.s2.pop()

    def peek(self) -> int:
        self._transfer()
        return self.s2[-1]

    def empty(self) -> bool:
        return not self.s1 and not self.s2
```

### 用两个队列实现栈 ([LC 225](https://leetcode.com/problems/implement-stack-using-queues/))

```python
from collections import deque


class MyStack:
    """
    push: O(n) — 入队后把前面所有元素重新排队
    或 push O(1)，pop O(n)
    """

    def __init__(self):
        self.q: deque[int] = deque()

    def push(self, x: int) -> None:
        self.q.append(x)
        # 把前面 n-1 个元素移到队尾
        for _ in range(len(self.q) - 1):
            self.q.append(self.q.popleft())

    def pop(self) -> int:
        return self.q.popleft()

    def top(self) -> int:
        return self.q[0]

    def empty(self) -> bool:
        return not self.q
```

---

## 五、复杂度总结

| 数据结构 | 实现方式 | push/enqueue | pop/dequeue |
|----------|---------|:---:|:---:|
| 栈 | 链表 | O(1) | O(1) |
| 栈 | 数组 | 均摊O(1) | O(1) |
| 队列 | 链表(有tail) | O(1) | O(1) |
| 队列 | 环形数组 | O(1) | O(1) |
| 双端队列 | 双链表 | O(1) | O(1) |

---

[← 返回索引](index.md)
