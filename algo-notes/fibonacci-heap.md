# 斐波那契堆 · Fibonacci Heap（简化版）

> 斐波那契堆是一种"能拖就拖"的堆：`insert` 和 `decrease_key` 都只做 O(1) 的表面功夫，
> 把真正的整理工作（合并同度数的树）都推迟到 `extract_min` 里一次性做掉。
> 代价是均摊分析，换来的是 `decrease_key` 均摊 O(1)——这正是 [heap-priority-queue.md](heap-priority-queue.md)
> 的二叉堆做不到的（二叉堆 decrease_key 是 O(log n)），也是 Dijkstra 理论最优复杂度 O(E + V log V) 依赖的关键数据结构。

---

## 一、和二叉堆的核心区别

| 操作 | 二叉堆 | 斐波那契堆（均摊） |
|------|:---:|:---:|
| `insert` | O(log n) | O(1) |
| `find_min` | O(1) | O(1) |
| `extract_min` | O(log n) | O(log n) |
| `decrease_key` | O(log n) | **O(1)** |
| `union`（合并两个堆） | O(n) | O(1) |

```
斐波那契堆的结构：不是一棵完全二叉树，而是一组"根节点"组成一个循环双向链表，
每个根节点下面挂着一棵"堆序"的树（父节点 key ≤ 子节点 key，但树的形状不要求完全二叉）。

insert：直接把新节点作为一棵单节点树，扔进根链表——O(1)，不整理，不比较。
decrease_key：如果减小后破坏了"父 ≤ 子"，就把这个节点整棵子树剪下来，
              直接扔进根链表（而不是像二叉堆那样一路往上比较交换）——均摊 O(1)。
extract_min：这是唯一"认真干活"的操作——把最小节点的所有子节点提到根链表，
             删除最小节点本身，然后合并根链表里"度数相同"的树（度数=子节点个数），
             直到所有根的度数都不同为止。这一步就是"欠的债"集中还清的地方。
```

---

## 二、节点结构

```python
class FibNode:
    def __init__(self, key: int) -> None:
        self.key = key
        self.degree = 0                    # 子节点个数
        self.parent: "FibNode | None" = None
        self.child: "FibNode | None" = None  # 只需指向"某一个"子节点，其余通过循环链表访问
        self.left = self                     # 循环双向链表：同级兄弟节点
        self.right = self
        self.mark = False                    # 是否已经失去过一个子节点（级联剪切用）
```

> `left`/`right` 让"根节点们"和"某节点的所有子节点"都组织成循环双向链表——
> 好处是从链表里删除/插入任意一个节点都是 O(1)（不需要像数组那样搬移）。

---

## 三、insert 与 find_min

```
insert：新建一个单节点的树，直接扔进根链表，跟其他树平级——O(1)，不比较不整理。
find_min：堆里始终维护一个 self.min 指针指向当前最小的根，O(1) 直接返回。
```

## 四、extract_min：真正干活的地方

```
1. 把最小节点 z 的所有子节点，逐个提升到根链表（它们各自独立成树）
2. 把 z 本身从根链表删掉
3. 合并根链表里"度数相同"的树（度数=子节点个数）：
   任取两棵度数相同的树，key 大的那棵变成 key 小的那棵的子树，度数+1，
   重复直到根链表里所有树的度数都不相同——这一步保证下次 extract_min 前，
   根链表里最多有 O(log n) 棵树。
```

## 五、decrease_key：均摊 O(1) 的关键

```
把 node 的 key 减小。如果减小后破坏了"父节点 key <= 子节点 key"：
  把 node 整棵子树从父节点上剪下来，直接扔进根链表（不需要像二叉堆那样一路上浮比较）。

级联剪切 (cascading cut)：每个节点有一个 mark 标记，表示"是否已经失去过一个子节点"。
  一个节点第一次失去子节点时，只是打上标记，不用剪；
  如果它已经打了标记又失去一个子节点，说明它"欠了两次债"，
  这时把它自己也剪到根链表，并且递归地检查它的父节点是否也要连锁剪切。
  "每个节点最多失去一个子节点，否则就要被剪"——这条规则正是斐波那契堆均摊分析
  和"斐波那契"这个名字的由来（可以证明度数为 k 的子树至少有 F(k+2) 个节点）。
```

## 六、完整实现

```python
class FibonacciHeap:
    def __init__(self) -> None:
        self.min: "FibNode | None" = None
        self.count = 0

    def is_empty(self) -> bool:
        return self.min is None

    def minimum(self) -> "int | None":
        return self.min.key if self.min else None

    def _insert_into_root_list(self, node: "FibNode") -> None:
        """把 node 作为独立一棵树插入根链表（O(1)，不做任何整理）。"""
        if self.min is None:
            node.left = node.right = node
            self.min = node
        else:
            node.left = self.min.left
            node.right = self.min
            self.min.left.right = node
            self.min.left = node
            if node.key < self.min.key:
                self.min = node

    def insert(self, key: int) -> "FibNode":
        node = FibNode(key)
        self._insert_into_root_list(node)
        self.count += 1
        return node

    def _remove_from_list(self, node: "FibNode") -> None:
        """把 node 从它所在的循环双向链表里摘掉。"""
        node.left.right = node.right
        node.right.left = node.left

    def _add_child(self, parent: "FibNode", child: "FibNode") -> None:
        """把 child 变成 parent 的子节点（加入 parent 的子节点循环链表）。"""
        child.parent = parent
        if parent.child is None:
            child.left = child.right = child
            parent.child = child
        else:
            child.left = parent.child.left
            child.right = parent.child
            parent.child.left.right = child
            parent.child.left = child
        parent.degree += 1
        child.mark = False

    def _link(self, y: "FibNode", x: "FibNode") -> None:
        """两棵度数相同的树合并：key 大的那棵变成 key 小的那棵的子树。"""
        self._remove_from_list(y)
        self._add_child(x, y)

    def extract_min(self) -> "int | None":
        z = self.min
        if z is None:
            return None

        # 1. z 的所有子节点直接提到根链表（它们各自成为独立的树）
        if z.child is not None:
            children = []
            c = z.child
            while True:
                children.append(c)
                c = c.right
                if c is z.child:
                    break
            for c in children:
                self._remove_from_list(c)
                c.parent = None
                self._insert_into_root_list(c)

        # 2. 把 z 本身从根链表删掉
        if z.right is z:
            self.min = None
        else:
            self._remove_from_list(z)
            self.min = z.right
            self._consolidate()  # 3. 合并同度数的树（欠的债在这里还清）

        self.count -= 1
        return z.key

    def _consolidate(self) -> None:
        """合并根链表里度数相同的树，直到每个度数最多只有一棵树。"""
        import math
        max_degree = int(math.log2(self.count + 1)) + 2 if self.count > 0 else 1
        degree_table: list["FibNode | None"] = [None] * (max_degree + 5)

        roots = []
        start = self.min
        c = start
        while True:
            roots.append(c)
            c = c.right
            if c is start:
                break

        for w in roots:
            x = w
            d = x.degree
            while degree_table[d] is not None:
                y = degree_table[d]
                if x.key > y.key:
                    x, y = y, x  # 保证 x 是 key 更小的那个
                self._link(y, x)
                degree_table[d] = None
                d += 1
            degree_table[d] = x

        # 用合并后剩下的树重建根链表 + 找新的 min
        self.min = None
        for node in degree_table:
            if node is not None:
                node.left = node.right = node
                self._insert_into_root_list(node)

    def decrease_key(self, node: "FibNode", new_key: int) -> None:
        if new_key > node.key:
            raise ValueError("新 key 必须比当前 key 小")
        node.key = new_key
        parent = node.parent
        if parent is not None and node.key < parent.key:
            # 破坏了"父 <= 子"，把 node 整棵子树剪下来扔进根链表
            self._cut(node, parent)
            self._cascading_cut(parent)
        if node.key < self.min.key:
            self.min = node

    def _cut(self, node: "FibNode", parent: "FibNode") -> None:
        """把 node 从 parent 的子节点链表里剪下来，扔进根链表。"""
        if parent.child is node and node.right is node:
            parent.child = None
        else:
            if parent.child is node:
                parent.child = node.right
            self._remove_from_list(node)
        parent.degree -= 1
        node.parent = None
        node.mark = False
        self._insert_into_root_list(node)

    def _cascading_cut(self, node: "FibNode") -> None:
        parent = node.parent
        if parent is not None:
            if not node.mark:
                node.mark = True  # 第一次失去子节点：只做标记，不剪
            else:
                self._cut(node, parent)       # 第二次：连锁剪掉
                self._cascading_cut(parent)    # 继续往上检查
```

---

## 七、正确性验证

```python
import random
import heapq

random.seed(1)
fail_basic = 0
for _ in range(100):
    n = random.randint(0, 200)
    vals = [random.randint(-1000, 1000) for _ in range(n)]
    fh = FibonacciHeap()
    for v in vals:
        fh.insert(v)
    got = []
    while not fh.is_empty():
        got.append(fh.extract_min())
    if got != sorted(vals):
        fail_basic += 1
print(f"insert+extract_min 正确性：100 次随机测试，失败 {fail_basic} 次")

random.seed(2)
fail_decrease = 0
for _ in range(100):
    n = random.randint(1, 100)
    vals = [random.randint(0, 1000) for _ in range(n)]
    fh = FibonacciHeap()
    nodes = [fh.insert(v) for v in vals]
    for i in range(len(nodes)):
        if random.random() < 0.5:
            new_val = vals[i] - random.randint(0, 500)
            fh.decrease_key(nodes[i], new_val)
            vals[i] = new_val
    got = []
    while not fh.is_empty():
        got.append(fh.extract_min())
    if got != sorted(vals):
        fail_decrease += 1
print(f"decrease_key 正确性：100 次随机测试（含级联剪切），失败 {fail_decrease} 次")
```

---

## 八、什么时候真的需要斐波那契堆

> 现实中大多数场景，二叉堆（`heapq`）已经够快，斐波那契堆的常数因子其实更大（更多指针操作、更多对象分配）。
> 它的价值主要在**理论复杂度**上：Dijkstra 用斐波那契堆能做到 O(E + V log V)，
> 比二叉堆版本的 O(E log V) 在**稠密图**（E 接近 V²）时更有优势；
> Prim 算法同理（见 [minimum-spanning-tree.md](minimum-spanning-tree.md)）。
> 工程实践中，除非有实测证明堆操作是瓶颈且图足够大/稠密，通常还是优先用更简单的二叉堆。

---

[← 返回索引](index.md)
