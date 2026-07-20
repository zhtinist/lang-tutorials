# 二叉树 · Binary Tree

> 二叉树两种思维模式：
> 1. **遍历思维**：走过每个节点时做操作（前/中/后序位置）
> 2. **分解问题思维**：把大问题分解成左右子树的小问题（后序递归）

---

## 一、节点定义

```python
class TreeNode:
    def __init__(
        self,
        val: int = 0,
        left: "TreeNode | None" = None,
        right: "TreeNode | None" = None,
    ):
        self.val = val
        self.left = left
        self.right = right
```

---

## 二、遍历框架

### 2.1 三种深搜遍历

```python
# 前序遍历：根 → 左 → 右
def preorder(root: TreeNode | None) -> list[int]:
    ans: list[int] = []

    def dfs(node: TreeNode | None) -> None:
        if not node:
            return
        ans.append(node.val)   # 前序位置
        dfs(node.left)
        dfs(node.right)

    dfs(root)
    return ans


# 中序遍历：左 → 根 → 右  (BST 中序遍历 = 有序序列)
def inorder(root: TreeNode | None) -> list[int]:
    ans: list[int] = []

    def dfs(node: TreeNode | None) -> None:
        if not node:
            return
        dfs(node.left)
        ans.append(node.val)   # 中序位置
        dfs(node.right)

    dfs(root)
    return ans


# 后序遍历：左 → 右 → 根  (后序位置：可以拿到子树信息)
def postorder(root: TreeNode | None) -> list[int]:
    ans: list[int] = []

    def dfs(node: TreeNode | None) -> None:
        if not node:
            return
        dfs(node.left)
        dfs(node.right)
        ans.append(node.val)   # 后序位置

    dfs(root)
    return ans
```

### 2.2 迭代遍历

```python
from collections import deque


# 前序迭代（栈：根右左入栈）
def preorder_iter(root: TreeNode | None) -> list[int]:
    if not root:
        return []
    ans: list[int] = []
    stack = [root]
    while stack:
        node = stack.pop()
        ans.append(node.val)
        if node.right:
            stack.append(node.right)
        if node.left:
            stack.append(node.left)
    return ans


# 中序迭代（栈：一路向左）
def inorder_iter(root: TreeNode | None) -> list[int]:
    ans: list[int] = []
    stack: list[TreeNode] = []
    cur = root
    while cur or stack:
        while cur:
            stack.append(cur)
            cur = cur.left
        cur = stack.pop()
        ans.append(cur.val)
        cur = cur.right
    return ans


# 后序迭代（前序的 "根右左" 反转 = "左右根"）
def postorder_iter(root: TreeNode | None) -> list[int]:
    if not root:
        return []
    ans: list[int] = []
    stack = [root]
    while stack:
        node = stack.pop()
        ans.append(node.val)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return ans[::-1]  # 反转得到后序


# 层序（BFS）· [LC 102](https://leetcode.com/problems/binary-tree-level-order-traversal/)
def level_order(root: TreeNode | None) -> list[list[int]]:
    if not root:
        return []
    ans: list[list[int]] = []
    queue: deque[TreeNode] = deque([root])
    while queue:
        level: list[int] = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        ans.append(level)
    return ans
```

---

## 三、前/中/后序位置的区别

```
void traverse(TreeNode root) {
    // 前序位置：刚进入当前节点，往下走之前
    //   → 适合做"自上而下"的操作（如传递深度、路径）

    traverse(root.left);
    // 中序位置：左子树走完，要进右子树之前
    //   → 适合 BST（中序=有序）

    traverse(root.right);
    // 后序位置：左右子树都走完，要返回时
    //   → 适合"自下而上"的操作（如收集子树信息、计算高度）
}
```

| 位置 | 可知信息 | 适合问题 |
|------|---------|---------|
| 前序 | 只知道根，不知道子树 | 传递参数（深度、路径） |
| 中序 | 知道左子树，不知道右子树 | BST 相关 |
| 后序 | 知道完整子树信息 | 高度、直径、平衡判断、LCA |

---

## 四、经典问题

### 4.1 最大深度 · [LC 104](https://leetcode.com/problems/maximum-depth-of-binary-tree/)

```python
# 遍历思维（前序 + 记录深度）
def max_depth_traverse(root: TreeNode | None) -> int:
    ans = 0
    def dfs(node: TreeNode | None, depth: int) -> None:
        nonlocal ans
        if not node:
            return
        ans = max(ans, depth)  # 前序：刚进入节点
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)
    dfs(root, 1)
    return ans


# 分解问题思维（后序）
def max_depth(root: TreeNode | None) -> int:
    """一棵树的最大深度 = 1 + max(左子树深度, 右子树深度)。"""
    if not root:
        return 0
    return 1 + max(max_depth(root.left), max_depth(root.right))
```

### 4.2 直径 · [LC 543](https://leetcode.com/problems/diameter-of-binary-tree/)

```python
def diameter_of_binary_tree(root: TreeNode | None) -> int:
    """
    直径 = 最长路径的边数。
    后序位置：穿过当前节点的最大路径 = 左深度 + 右深度。
    """
    ans = 0

    def max_depth(node: TreeNode | None) -> int:
        nonlocal ans
        if not node:
            return 0
        left = max_depth(node.left)
        right = max_depth(node.right)
        # 后序位置：更新直径
        ans = max(ans, left + right)
        return 1 + max(left, right)

    max_depth(root)
    return ans
```

### 4.3 翻转二叉树 · [LC 226](https://leetcode.com/problems/invert-binary-tree/)

```python
def invert_tree(root: TreeNode | None) -> TreeNode | None:
    """前序/后序都可以，交换左右子树。"""
    if not root:
        return None
    root.left, root.right = root.right, root.left  # 前序位置交换
    invert_tree(root.left)
    invert_tree(root.right)
    return root
```

### 4.4 对称二叉树 · [LC 101](https://leetcode.com/problems/symmetric-tree/)

```python
def is_symmetric(root: TreeNode | None) -> bool:
    """判断是否轴对称。"""

    def check(left: TreeNode | None, right: TreeNode | None) -> bool:
        if not left and not right:
            return True
        if not left or not right:
            return False
        return (
            left.val == right.val
            and check(left.left, right.right)
            and check(left.right, right.left)
        )

    return check(root.left, root.right) if root else True
```

---

## 五、构造二叉树

### 5.1 前序 + 中序 构造 · [LC 105](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/)

```python
def build_tree_pre_in(
    preorder: list[int], inorder: list[int],
) -> TreeNode | None:
    """前序第一个是根，在中序中找到根来分割左右子树。"""
    in_map = {val: i for i, val in enumerate(inorder)}

    def build(pre_start: int, pre_end: int, in_start: int, in_end: int) -> TreeNode | None:
        if pre_start > pre_end:
            return None

        root_val = preorder[pre_start]
        root = TreeNode(root_val)
        in_idx = in_map[root_val]
        left_size = in_idx - in_start

        root.left = build(
            pre_start + 1, pre_start + left_size,
            in_start, in_idx - 1,
        )
        root.right = build(
            pre_start + left_size + 1, pre_end,
            in_idx + 1, in_end,
        )
        return root

    return build(0, len(preorder) - 1, 0, len(inorder) - 1)
```

### 5.2 中序 + 后序 构造 · [LC 106](https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/)

```python
def build_tree_in_post(
    inorder: list[int], postorder: list[int],
) -> TreeNode | None:
    """后序最后一个是根。"""
    in_map = {val: i for i, val in enumerate(inorder)}

    def build(in_start: int, in_end: int, post_start: int, post_end: int) -> TreeNode | None:
        if in_start > in_end:
            return None

        root_val = postorder[post_end]
        root = TreeNode(root_val)
        in_idx = in_map[root_val]
        left_size = in_idx - in_start

        root.left = build(
            in_start, in_idx - 1,
            post_start, post_start + left_size - 1,
        )
        root.right = build(
            in_idx + 1, in_end,
            post_start + left_size, post_end - 1,
        )
        return root

    return build(0, len(inorder) - 1, 0, len(postorder) - 1)
```

---

## 六、最近公共祖先 LCA · [LC 236](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/)

```python
def lowest_common_ancestor(
    root: TreeNode | None, p: TreeNode, q: TreeNode,
) -> TreeNode | None:
    """
    后序遍历。若左右子树各含 p 和 q，则当前节点是 LCA。
    若其中一个为空，说明 p 和 q 都在另一边。
    """
    if not root:
        return None
    if root == p or root == q:
        return root  # 找到 p 或 q

    left = lowest_common_ancestor(root.left, p, q)
    right = lowest_common_ancestor(root.right, p, q)

    if left and right:
        return root  # p 和 q 在两侧，当前就是 LCA
    return left or right  # p 和 q 在同一侧
```

---

## 七、序列化与反序列化 · [LC 297](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/)

```python
from collections import deque


class Codec:
    """二叉树的序列化与反序列化。用前序遍历 + '#' 表示空节点。"""

    def serialize(self, root: TreeNode | None) -> str:
        vals: list[str] = []

        def dfs(node: TreeNode | None) -> None:
            if not node:
                vals.append("#")
                return
            vals.append(str(node.val))
            dfs(node.left)
            dfs(node.right)

        dfs(root)
        return ",".join(vals)

    def deserialize(self, data: str) -> TreeNode | None:
        vals = deque(data.split(","))

        def dfs() -> TreeNode | None:
            if not vals:
                return None
            val = vals.popleft()
            if val == "#":
                return None
            node = TreeNode(int(val))
            node.left = dfs()
            node.right = dfs()
            return node

        return dfs()
```

---

## 八、总结

| 思维模式 | 代码位置 | 适合场景 |
|----------|---------|---------|
| 遍历思维 | 前序 | 自上而下传球（深度、路径和） |
| 分解思维 | 后序 | 自下而上收集（高度、直径、平衡、LCA） |
| 中序 | 中序 | BST 有序性质 |

---

## 九、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 144](https://leetcode.com/problems/binary-tree-preorder-traversal/) | Preorder Traversal | Easy | 前序 |
| [LC 94](https://leetcode.com/problems/binary-tree-inorder-traversal/) | Inorder Traversal | Easy | 中序 |
| [LC 145](https://leetcode.com/problems/binary-tree-postorder-traversal/) | Postorder Traversal | Easy | 后序 |
| [LC 102](https://leetcode.com/problems/binary-tree-level-order-traversal/) | Level Order Traversal | Medium | 层序 |
| [LC 104](https://leetcode.com/problems/maximum-depth-of-binary-tree/) | Maximum Depth | Easy | 后序分解 |
| [LC 543](https://leetcode.com/problems/diameter-of-binary-tree/) | Diameter | Easy | 后序+直径 |
| [LC 226](https://leetcode.com/problems/invert-binary-tree/) | Invert Binary Tree | Easy | 前序交换 |
| [LC 101](https://leetcode.com/problems/symmetric-tree/) | Symmetric Tree | Easy | 双指针检查 |
| [LC 105](https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/) | Construct from Pre+In | Medium | 构造模板 |
| [LC 106](https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/) | Construct from In+Post | Medium | 构造模板 |
| [LC 236](https://leetcode.com/problems/lowest-common-ancestor-of-a-binary-tree/) | Lowest Common Ancestor | Medium | 后序遍历 |
| [LC 297](https://leetcode.com/problems/serialize-and-deserialize-binary-tree/) | Serialize and Deserialize | Hard | 序列化 |
| [LC 124](https://leetcode.com/problems/binary-tree-maximum-path-sum/) | Binary Tree Max Path Sum | Hard | 后序+路径 |
| [LC 110](https://leetcode.com/problems/balanced-binary-tree/) | Balanced Binary Tree | Easy | 后序判断 |

---

[← 返回索引](index.md)
