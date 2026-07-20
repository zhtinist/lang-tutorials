# 手写哈希表 · Hash Table Implementation

> 哈希表 = 数组 + 哈希函数 + 冲突解决。核心：O(1) 的增删查。
> 两种冲突解决：**拉链法** (Chaining) 和 **线性探查法** (Linear Probing)。

---

## 一、哈希函数

```python
def hash_func(key, capacity: int) -> int:
    """
    把 key 映射到 [0, capacity-1]。
    Python 的 hash() 内置了好的哈希算法，
    这里展示基本思路。
    """
    if isinstance(key, int):
        return key % capacity
    if isinstance(key, str):
        h = 0
        for ch in key:
            h = (h * 31 + ord(ch)) % capacity
        return h
    return hash(key) % capacity
```

**好的哈希函数**：计算快、分布均匀、相同 key 产生相同 hash。

---

## 二、拉链法 (Separate Chaining)

> 每个桶是一个链表。冲突的元素追加到链表后面。
> Java HashMap, Python dict (CPython 3.6+ 更复杂但原理相通)。

```python
from typing import TypeVar, Generic

K = TypeVar("K")
V = TypeVar("V")


class ChainHashNode(Generic[K, V]):
    def __init__(self, key: K, val: V, next: "ChainHashNode[K, V] | None" = None):
        self.key = key
        self.val = val
        self.next = next


class ChainingHashMap(Generic[K, V]):
    """拉链法哈希表。"""

    LOAD_FACTOR = 0.75

    def __init__(self, capacity: int = 16) -> None:
        self._capacity = capacity
        self._size = 0
        self._table: list[ChainHashNode[K, V] | None] = [None] * capacity

    def _hash(self, key: K) -> int:
        return hash(key) % self._capacity

    def put(self, key: K, val: V) -> None:
        idx = self._hash(key)
        node = self._table[idx]

        # 查找 key 是否已存在
        while node:
            if node.key == key:
                node.val = val
                return
            node = node.next

        # 不存在，头插法插入新节点
        self._table[idx] = ChainHashNode(key, val, self._table[idx])
        self._size += 1

        # 扩容
        if self._size >= self._capacity * self.LOAD_FACTOR:
            self._resize(self._capacity * 2)

    def get(self, key: K) -> V | None:
        idx = self._hash(key)
        node = self._table[idx]
        while node:
            if node.key == key:
                return node.val
            node = node.next
        return None

    def remove(self, key: K) -> bool:
        idx = self._hash(key)
        node = self._table[idx]
        prev = None

        while node:
            if node.key == key:
                if prev:
                    prev.next = node.next
                else:
                    self._table[idx] = node.next
                self._size -= 1
                return True
            prev = node
            node = node.next

        return False

    def _resize(self, new_capacity: int) -> None:
        """扩容：重新哈希所有元素。"""
        old_table = self._table
        self._capacity = new_capacity
        self._size = 0
        self._table = [None] * new_capacity

        for head in old_table:
            node = head
            while node:
                self.put(node.key, node.val)  # 重新哈希
                node = node.next

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: K) -> bool:
        return self.get(key) is not None
```

---

## 三、线性探查法 (Linear Probing / Open Addressing)

> 所有元素存在数组里。冲突时往后找空位。没有链表，更省内存。
> Python 的 dict 在 3.6 之前用这个方法（3.6+ 改用更紧凑的布局）。

```python
class LinearProbingHashMap(Generic[K, V]):
    """线性探查法哈希表（开放寻址）。"""

    LOAD_FACTOR = 0.5  # 开放寻址需要更低的负载因子

    # 哨兵
    _EMPTY = object()
    _DELETED = object()

    def __init__(self, capacity: int = 16) -> None:
        self._capacity = capacity
        self._size = 0
        self._keys: list[object] = [self._EMPTY] * capacity
        self._vals: list[V | None] = [None] * capacity

    def _hash(self, key: K) -> int:
        return hash(key) % self._capacity

    def put(self, key: K, val: V) -> None:
        if self._size >= self._capacity * self.LOAD_FACTOR:
            self._resize(self._capacity * 2)

        idx = self._hash(key)

        # 线性探查：往后找空位或 key
        while True:
            k = self._keys[idx]
            if k is self._EMPTY or k is self._DELETED:
                # 找到了空位
                self._keys[idx] = key
                self._vals[idx] = val
                self._size += 1
                return
            if k == key:
                # key 已存在，更新
                self._vals[idx] = val
                return
            idx = (idx + 1) % self._capacity  # 线性探查

    def get(self, key: K) -> V | None:
        idx = self._hash(key)
        while True:
            k = self._keys[idx]
            if k is self._EMPTY:
                return None  # 遇到空位说明 key 不存在
            if k == key:
                return self._vals[idx]
            idx = (idx + 1) % self._capacity

    def remove(self, key: K) -> bool:
        idx = self._hash(key)
        while True:
            k = self._keys[idx]
            if k is self._EMPTY:
                return False
            if k == key:
                self._keys[idx] = self._DELETED  # 用 DELETED 墓碑标记
                self._vals[idx] = None
                self._size -= 1
                return True
            idx = (idx + 1) % self._capacity

    def _resize(self, new_capacity: int) -> None:
        old_keys = self._keys
        old_vals = self._vals
        old_cap = self._capacity

        self._capacity = new_capacity
        self._size = 0
        self._keys = [self._EMPTY] * new_capacity
        self._vals = [None] * new_capacity

        for i in range(old_cap):
            if old_keys[i] not in (self._EMPTY, self._DELETED):
                self.put(old_keys[i], old_vals[i])  # type: ignore

    def __len__(self) -> int:
        return self._size
```

> **墓碑 (Tombstone)**：删除元素时不直接置空，用 DELETED 标记。否则查找链会断裂。
> 插入时遇到墓碑可以复用，但查找时遇到墓碑需要继续往后找。

---

## 四、两种冲突解决对比

| 维度 | 拉链法 (Chaining) | 线性探查 (Open Addressing) |
|------|:---:|:---:|
| 数据存储 | 桶数组 + 链表 | 全部在数组里 |
| 内存 | 多占链表节点空间 | 更紧凑 |
| 缓存友好 | 差（链表不连续） | 好（连续数组） |
| 负载因子 | 可以 >1 | 必须 <1（通常 0.5-0.7） |
| 删除 | 简单 | 需要墓碑 |
| 实现 | Java HashMap, Go map | Python dict (早期) |

---

## 五、哈希表的扩展结构

| 结构 | 特点 |
|------|------|
| LinkedHashMap | 哈希表 + 双向链表，保持插入顺序。Python: OrderedDict |
| ArrayHashMap | 每个桶用动态数组存冲突元素。当冲突多时比链表更快 |
| 布隆过滤器 | 概率型结构，快速判断 key 是否"可能存在"。省空间但会误判 |

### 布隆过滤器 (Bloom Filter) 原理

```
核心：k 个哈希函数 + 一个位数组。
插入：对 key 计算 k 个哈希值，把对应位都置为 1。
查询：如果 k 个位全是 1 → "可能存在"（有误判）。
      如果任一为 0 → "一定不存在"（无误判）。

适合：缓存穿透防护、垃圾邮件过滤。
```

```python
class BloomFilter:
    def __init__(self, size: int, hash_count: int):
        self._bits = [0] * size
        self._hash_count = hash_count
        self._size = size

    def _hashes(self, key: str) -> list[int]:
        h = hash(key)
        return [(h + i * 0x9E3779B9) % self._size for i in range(self._hash_count)]

    def add(self, key: str) -> None:
        for idx in self._hashes(key):
            self._bits[idx] = 1

    def might_contain(self, key: str) -> bool:
        return all(self._bits[idx] for idx in self._hashes(key))
```

---

## 六、哈希表复杂度

| 操作 | 平均情况 | 最坏情况 |
|------|:---:|:---:|
| 插入 | O(1) | O(n) |
| 查找 | O(1) | O(n) |
| 删除 | O(1) | O(n) |

> 最坏情况发生在所有 key 哈希冲突到同一个桶。好的哈希函数 + 低负载因子可以避免。

---

[← 返回索引](index.md)
