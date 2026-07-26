# B 树 · B-Tree

> B 树是一棵**多路平衡搜索树**：每个节点可以存多个 key、有多个子节点，不再是"一分二"而是"一分多"。
> 专为磁盘/数据库设计——每个节点对应一次磁盘 I/O，多路能让树高大幅降低，
> 从而大幅减少查询时的磁盘读取次数。MySQL InnoDB 的索引、大多数文件系统都用它（或它的变体 B+树）。

---

## 一、定义

> 用**最小度数 (minimum degree) t** 描述一棵 B 树的"胖瘦"，t ≥ 2。

```
每个节点（除根节点外）:
  - 最多有 2t-1 个 key，最多有 2t 个子节点
  - 至少有 t-1 个 key，至少有 t 个子节点（根节点可以少于 t-1 个，只要至少有1个key）

一个内部节点的 key 把它的子树分成 (key数+1) 段，
子节点 i 的所有 key 都落在 keys[i-1] 和 keys[i] 之间（跟 BST 的性质是一致的，
只是 BST 每个节点只有1个key、2个子节点，B树把这个"1对2"推广成了"多对多"）。

所有叶子节点在同一深度——这是 B 树"绝对平衡"（不是红黑树那种近似平衡）的关键性质，
靠的是插入时"节点满了就分裂，把中间 key 弹给父节点"，而不是靠旋转。
```

> **t 越大，节点越"胖"（能存的 key 越多），树越"矮"**——这正是磁盘场景想要的：
> 让一次磁盘读取（读一个节点）尽量多做事，用最少的磁盘读取次数完成一次查找。

---

## 二、查找

```python
class BTreeNode:
    def __init__(self, leaf: bool = True) -> None:
        self.keys: list[int] = []
        self.children: list["BTreeNode"] = []
        self.leaf = leaf


class BTree:
    def __init__(self, t: int = 3) -> None:
        self.t = t  # 最小度数
        self.root = BTreeNode(leaf=True)

    def search(self, key: int, node: "BTreeNode | None" = None):
        """在节点内顺序找第一个 >= key 的位置，命中就返回，否则递归进对应子树。"""
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)  # 找到了，返回所在节点和下标
        if node.leaf:
            return None  # 已经是叶子还没找到，说明不存在
        return self.search(key, node.children[i])
```

> 复杂度 O(t · log_t n)：树高是 O(log_t n)，每层节点内部顺序查找最多扫 O(t) 个 key
> （如果节点内部也用二分查找，能优化到 O(log t · log_t n)，但工程上 t 通常不大，顺序扫描更简单也够快）。

---

## 三、插入

### 3.1 核心思路：满了就分裂，绝不"往下走的时候才发现没地方"

```
B树插入的关键技巧：从根开始往下找插入位置的过程中，
只要发现"即将进入的子节点已经满了（2t-1个key）"，就提前把它分裂，
而不是一路走到叶子才发现满了再往回处理。

这样做的好处：插入操作只需要"从上往下走一趟"，不需要任何回溯，
因为每次下降前都已经保证"要进入的节点还有空位"。

分裂一个满节点（2t-1个key）：
  - 中间的 key（第 t 个，下标 t-1）被"弹"到父节点里
  - 剩下的 t-1 个 key 留在左边（原节点），t-1 个 key 分给新建的右边节点
  - 如果原节点不是叶子，它的 2t 个子节点也对半分给左右两边（各 t 个）
```

### 3.2 完整实现

```python
class BTreeNode:
    def __init__(self, leaf: bool = True) -> None:
        self.keys: list[int] = []
        self.children: list["BTreeNode"] = []
        self.leaf = leaf


class BTree:
    def __init__(self, t: int = 3) -> None:
        self.t = t  # 最小度数
        self.root = BTreeNode(leaf=True)

    def search(self, key: int, node: "BTreeNode | None" = None):
        if node is None:
            node = self.root
        i = 0
        while i < len(node.keys) and key > node.keys[i]:
            i += 1
        if i < len(node.keys) and key == node.keys[i]:
            return (node, i)
        if node.leaf:
            return None
        return self.search(key, node.children[i])

    def insert(self, key: int) -> None:
        root = self.root
        if len(root.keys) == 2 * self.t - 1:
            # 根节点满了：新建一个根，把旧根作为它唯一的子节点，然后分裂旧根
            new_root = BTreeNode(leaf=False)
            new_root.children.append(root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._insert_nonfull(new_root, key)
        else:
            self._insert_nonfull(root, key)

    def _split_child(self, parent: "BTreeNode", i: int) -> None:
        """把 parent 的第 i 个子节点（已经是满的，2t-1个key）分裂成两个各 t-1 个 key 的节点。"""
        t = self.t
        child = parent.children[i]
        new_node = BTreeNode(leaf=child.leaf)

        mid_key = child.keys[t - 1]           # 中间的 key，弹给父节点
        new_node.keys = child.keys[t:]        # 右半部分给新节点
        child.keys = child.keys[:t - 1]       # 左半部分留在原节点

        if not child.leaf:
            new_node.children = child.children[t:]
            child.children = child.children[:t]

        parent.children.insert(i + 1, new_node)  # 新节点成为 parent 的第 i+1 个子节点
        parent.keys.insert(i, mid_key)            # 中间 key 插入 parent

    def _insert_nonfull(self, node: "BTreeNode", key: int) -> None:
        """在一个"保证不满"的节点里插入 key（叶子直接插，内部节点递归下降）。"""
        i = len(node.keys) - 1
        if node.leaf:
            node.keys.append(None)  # 占位，腾出空间
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                i -= 1
            node.keys[i + 1] = key
        else:
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1  # 要进入的子节点下标
            if len(node.children[i].keys) == 2 * self.t - 1:
                # 下降前先分裂：保证进去的子节点一定不满
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1  # 分裂后中间key上移，可能要调整进入左边还是右边
            self._insert_nonfull(node.children[i], key)

    def inorder(self) -> list[int]:
        """中序遍历应该是有序的——多路版本：node.keys[i] 前面遍历 children[i]，后面遍历 children[i+1]。"""
        result: list[int] = []

        def dfs(node: "BTreeNode") -> None:
            if node.leaf:
                result.extend(node.keys)
            else:
                for i in range(len(node.keys)):
                    dfs(node.children[i])
                    result.append(node.keys[i])
                dfs(node.children[-1])

        dfs(self.root)
        return result
```

### 3.3 正确性验证

```python
import random


def check_btree_properties(tree: "BTree") -> None:
    """校验 B 树的结构性质：key数量上下界、节点内有序、子节点数、所有叶子同深度。"""
    t = tree.t
    leaf_depths: list[int] = []

    def check(node: "BTreeNode", depth: int, is_root: bool) -> None:
        assert len(node.keys) <= 2 * t - 1, "单节点key数超过上限"
        if not is_root:
            assert len(node.keys) >= t - 1, "单节点key数低于下限"
        assert node.keys == sorted(node.keys), "节点内key未排序"
        if node.leaf:
            leaf_depths.append(depth)
        else:
            assert len(node.children) == len(node.keys) + 1, "子节点数应该等于key数+1"
            for child in node.children:
                check(child, depth + 1, False)

    check(tree.root, 0, True)
    assert len(set(leaf_depths)) == 1, f"叶子深度不一致: {set(leaf_depths)}"


random.seed(0)
fail = 0
for _ in range(100):
    t = random.choice([2, 3, 4])
    n = random.randint(0, 300)
    vals = random.sample(range(-2000, 2000), n)
    tree = BTree(t=t)
    for v in vals:
        tree.insert(v)

    check_btree_properties(tree)                  # 结构性质全部满足
    assert tree.inorder() == sorted(vals)          # 中序遍历有序
    assert all(tree.search(v) is not None for v in vals)  # 所有插入的key都能查到

print("100 次随机插入测试全部通过（不同 t、不同规模，结构性质 + 有序性 + 查找全部校验）")
```

---

## 四、删除（只讲思路，不实现）

B 树删除比插入更麻烦——插入只需要"往下走的时候把满节点分裂掉"，删除却要保证
"往下走的时候经过的每个节点都至少有 t 个 key"（否则删完可能不满足最小 key 数限制），
所以要在往下走的路上，遇到"只有 t-1 个 key（already 最小）的节点"就要先做点什么。

```
大致思路（往下走的过程中，维护"当前节点至少有 t 个 key"这个不变量）：
1. 如果要删除的 key 在当前节点里，且当前节点是叶子——直接删除。
2. 如果要删除的 key 在当前节点里，且当前节点不是叶子——
   用前驱或后继 key 替换它（跟普通 BST 删除同样的思路），
   转化成"在子树里删除前驱/后继"的子问题。
3. 如果要删除的 key 不在当前节点，需要往下走：
   如果即将进入的子节点恰好只有 t-1 个 key（最小值，不能再减了），
   要先"借"一个 key（从兄弟节点借，前提是兄弟节点 key 数 > t-1）
   或者"合并"（跟兄弟节点及父节点的分隔 key 合并成一个节点），
   保证进入的子节点至少有 t 个 key，才能安全地继续往下删。

跟红黑树删除一样：情况分支多、边界密集，面试/笔试基本不会要求手写，
记住"删除要保证经过的节点都够'胖'，不够就先借/合并"这个核心思想即可。
```

---

## 五、B 树与红黑树对比

| 维度 | 红黑树 | B 树 |
|------|--------|------|
| 每节点 key 数 | 1 个 | 多个（t-1 到 2t-1 个） |
| 每节点子节点数 | 2 个 | 多个（t 到 2t 个） |
| 树高 | O(log₂ n) | O(log_t n)，t 越大树越矮 |
| 平衡方式 | 旋转 + 染色 | 节点分裂/合并 |
| 典型场景 | 内存中的有序容器（`std::map` 等） | 磁盘索引（数据库、文件系统）——降低磁盘 I/O 次数是首要目标 |

> 内存访问速度和磁盘访问速度差几个数量级，所以内存数据结构（红黑树）优化的是"比较次数"，
> 磁盘数据结构（B树）优化的是"访问节点（=磁盘读取）的次数"——这也是为什么 B树选择"胖节点、矮树"。

---

[← 返回索引](index.md)
