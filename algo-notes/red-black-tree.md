# 红黑树 · Red-Black Tree

> 红黑树是一棵**近似平衡**的二叉搜索树：靠 5 条性质保证从根到任意叶子的路径，
> 最长不超过最短的 2 倍，从而把查找/插入/删除都限制在 O(log n)。
> 语言标准库大量用它实现有序容器：C++ `std::map`/`std::set`、Java `TreeMap`/`TreeSet`。
> [binary-search-tree.md](binary-search-tree.md) 提到过它但没写实现，这里补上。

---

## 一、五条性质

```
1. 每个节点是红色或黑色
2. 根节点是黑色
3. 每个叶子节点（NIL，空节点）是黑色
4. 如果一个节点是红色，它的两个子节点都是黑色（不能有两个连续的红节点）
5. 从任意节点到其所有后代叶子的路径，经过的黑色节点数相同（黑高相同）

性质 4+5 一起保证了"最长路径 ≤ 最短路径 × 2"：
最短路径全是黑节点，最长路径是黑红交替，长度最多是黑节点数的 2 倍。
```

### 1.1 哨兵节点 NIL

CLRS 的技巧：所有空叶子指向**同一个哨兵节点** `NIL`（颜色为黑），而不是用 `None`。
好处是所有"空节点"都有统一的颜色和 parent 指针，旋转/修复代码不用到处判断 `if node is None`。

```python
RED = "RED"
BLACK = "BLACK"


class RBNode:
    __slots__ = ("val", "color", "left", "right", "parent")

    def __init__(self, val=None, color=BLACK, left=None, right=None, parent=None):
        self.val = val
        self.color = color
        self.left = left
        self.right = right
        self.parent = parent
```

---

## 二、旋转

> 旋转是红黑树维持平衡的基本操作：局部调整子树结构，但**不破坏 BST 的中序有序性质**。

```
左旋：x 变成 x.right 的左子树（右旋是镜像操作）。
      x                  y
     / \                / \
    a   y      ->      x   c
       / \            / \
      b   c          a   b
```

---

## 三、插入

### 3.1 思路

```
先按普通 BST 插入，插入的节点染成【红色】。

为什么染红不染黑：如果染成黑色，会立刻破坏性质5（这条路径的黑高变了，其他路径没变）。
染成红色只可能破坏性质4（父节点也是红色的情况），而性质4的违反比性质5好修
（局部旋转+染色就能搞定，不需要动整棵树的黑高）。
```

新节点 z 是红色。只有当 `z.parent` 也是红色时，性质4 才被破坏，需要修复。
设 z 的父节点是红色，看 z 的"叔叔"（uncle，即祖父的另一个子节点）：

```
情况1：叔叔是红色
  祖父、父亲、叔叔三个节点重新染色：父亲和叔叔变黑，祖父变红。
  然后把"当前处理的节点"跳到祖父，继续往上检查——因为祖父变红了，
  可能和"曾祖父"又形成红红冲突，需要继续修复。

情况2：叔叔是黑色，且 z 是父亲的"内侧"子节点（z-parent-grandparent 形成"之字形"）
  先对父节点做一次旋转，把情况2转化成情况3（z 变成外侧子节点）。

情况3：叔叔是黑色，且 z 是父亲的"外侧"子节点（z-parent-grandparent 是一条直线）
  父亲染黑，祖父染红，对祖父做一次旋转。修复完成，不需要再往上传播。
```

### 3.2 完整实现

```python
class RedBlackTree:
    def __init__(self) -> None:
        self.NIL = RBNode(color=BLACK)  # 哨兵：所有叶子和根的父指针都指向它
        self.root = self.NIL

    def left_rotate(self, x: RBNode) -> None:
        y = x.right
        x.right = y.left
        if y.left is not self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is self.NIL:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y

    def right_rotate(self, x: RBNode) -> None:
        """左旋的镜像操作。"""
        y = x.left
        x.left = y.right
        if y.right is not self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is self.NIL:
            self.root = y
        elif x is x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y

    def insert(self, val: int) -> None:
        z = RBNode(val=val, color=RED, left=self.NIL, right=self.NIL, parent=self.NIL)
        y = self.NIL
        x = self.root
        while x is not self.NIL:  # 普通 BST 插入，找到插入位置
            y = x
            if z.val < x.val:
                x = x.left
            else:
                x = x.right
        z.parent = y
        if y is self.NIL:
            self.root = z
        elif z.val < y.val:
            y.left = z
        else:
            y.right = z

        self._insert_fixup(z)  # 新节点是红色，可能破坏性质4，需要修复

    def _insert_fixup(self, z: RBNode) -> None:
        while z.parent.color == RED:
            if z.parent is z.parent.parent.left:
                y = z.parent.parent.right  # 叔叔节点
                if y.color == RED:
                    # 情况1：叔叔红 -> 重新染色，把问题上移到祖父
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z is z.parent.right:
                        # 情况2：叔叔黑，z 是内侧子节点 -> 转成情况3
                        z = z.parent
                        self.left_rotate(z)
                    # 情况3：叔叔黑，z 是外侧子节点
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self.right_rotate(z.parent.parent)
            else:
                # 镜像：父亲是祖父的右子节点
                y = z.parent.parent.left
                if y.color == RED:
                    z.parent.color = BLACK
                    y.color = BLACK
                    z.parent.parent.color = RED
                    z = z.parent.parent
                else:
                    if z is z.parent.left:
                        z = z.parent
                        self.right_rotate(z)
                    z.parent.color = BLACK
                    z.parent.parent.color = RED
                    self.left_rotate(z.parent.parent)
            if z is self.root:
                break
        self.root.color = BLACK  # 根节点始终染黑（性质2），不管上面循环怎么改的

    def inorder(self) -> list[int]:
        result: list[int] = []

        def dfs(node: RBNode) -> None:
            if node is self.NIL:
                return
            dfs(node.left)
            result.append(node.val)
            dfs(node.right)

        dfs(self.root)
        return result
```

> 每种情况最多做 2 次旋转，情况1 会继续往上循环，但情况2/3 修复后循环立即结束——
> 这就是"插入最多 O(log n) 次颜色调整 + O(1) 次旋转"的由来（旋转次数有严格常数上界，颜色调整才可能有 O(log n) 次）。

### 3.3 正确性验证

```python
import random


def check_properties(tree: "RedBlackTree") -> None:
    """校验红黑树的全部5条性质。"""
    assert tree.root.color == BLACK, "根节点必须是黑色"

    def check(node: RBNode) -> int:
        if node is tree.NIL:
            return 1  # NIL 记一次黑高贡献
        if node.color == RED:
            assert node.left.color == BLACK and node.right.color == BLACK, "红节点不能有红色子节点"
        left_bh = check(node.left)
        right_bh = check(node.right)
        assert left_bh == right_bh, f"黑高不一致: {left_bh} vs {right_bh}"
        return left_bh + (1 if node.color == BLACK else 0)

    check(tree.root)


random.seed(0)
fail = 0
for _ in range(200):
    n = random.randint(0, 200)
    vals = random.sample(range(-1000, 1000), n)
    tree = RedBlackTree()
    for v in vals:
        tree.insert(v)
    check_properties(tree)                       # 5条性质全部满足
    assert tree.inorder() == sorted(vals)         # 仍然是一棵合法 BST

print("200 次随机插入测试全部通过（含黑高、红黑冲突、BST有序性校验）")
```

---

## 四、删除（只讲思路，不实现）

删除比插入复杂得多——原因是删除一个黑色节点必然破坏性质 5（这条路径少了一个黑节点），
且修复时会遇到 **4 种情况**（比插入的 3 种情况更多），因为删除时"兄弟节点"的颜色和其子节点的颜色组合更多样。

```
大致思路：
1. 按普通 BST 删除。如果被删除节点有两个子节点，用后继节点的值替换，
   转化成"删除一个最多只有一个子节点的节点"的子问题（这一步和 binary-search-tree.md 的删除完全一样）。
2. 如果被删除的节点是红色，直接删掉，不影响任何性质（红色节点不计入黑高）。
3. 如果被删除的节点是黑色，用它的子节点顶替它的位置后，
   这个子节点会带着一个"额外的黑色"标记（术语：double black），
   需要通过一系列旋转+染色操作把这个"多余的黑色"沿着树往上传递/消除，
   根据兄弟节点和兄弟节点子节点的颜色分 4 种情况处理（其中 2 种能直接终止，2 种需要继续往上传播或转化）。

这部分因为情况分支多、边界条件密集，实际面试/笔试里几乎不会要求手写，
记住"删除黑色节点会破坏黑高，需要把多余的黑色沿树传播消除"这个核心思想即可。
完整的 4 种情况推导见 CLRS 第13.4节。
```

---

## 五、与其他平衡树的对比

| 结构 | 平衡方式 | 插入/删除开销 | 查找 | 应用 |
|------|---------|---------------|------|------|
| AVL 树 | 严格平衡（平衡因子 -1/0/1） | 插入最多1-2次旋转，删除最多 O(log n) 次旋转 | O(log n)，比红黑树略快（更平衡） | 查找远多于增删的场景 |
| 红黑树 | 近似平衡（黑高相同） | 插入最多2次旋转，删除最多3次旋转，旋转次数有常数上界 | O(log n) | 增删频繁的场景（各语言标准库的首选） |
| B 树 | 多路平衡 | 见 [b-tree.md](b-tree.md) | O(log n) | 磁盘/数据库索引（每个节点对应一次磁盘读取，多路能减少树高） |

> AVL 树更"平衡"所以查找略快，但插入/删除时为了维持严格平衡因子可能触发更多旋转；
> 红黑树放宽了平衡要求换来更少的旋转次数，是"查找 vs 增删"之间更常见的折中选择。

---

[← 返回索引](index.md)
