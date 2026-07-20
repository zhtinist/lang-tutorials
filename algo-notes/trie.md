# 字典树 · Trie (Prefix Tree)

> Trie 用于高效存储和检索字符串集合中的**前缀**。插入和查询字符串的时间复杂度为 O(L)，L 为字符串长度。
> 核心：每个节点存一个 `children` 映射（或固定长度数组），和一个 `is_end` 标记。

---

## 一、Trie 实现 · [LC 208](https://leetcode.com/problems/implement-trie-prefix-tree/)

### 数组实现（仅小写字母）

```python
class Trie:
    """字典树，26 叉。"""

    def __init__(self) -> None:
        self.children: list["Trie | None"] = [None] * 26
        self.is_end: bool = False

    def insert(self, word: str) -> None:
        """插入单词。O(L)"""
        node = self
        for ch in word:
            idx = ord(ch) - ord("a")
            if not node.children[idx]:
                node.children[idx] = Trie()
            node = node.children[idx]
        node.is_end = True

    def search(self, word: str) -> bool:
        """精确搜索单词。"""
        node = self._find_node(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        """判断是否有以 prefix 为前缀的单词。"""
        return self._find_node(prefix) is not None

    def _find_node(self, s: str) -> "Trie | None":
        node = self
        for ch in s:
            idx = ord(ch) - ord("a")
            if not node.children[idx]:
                return None
            node = node.children[idx]
        return node
```

### 字典实现（通用字符集）

```python
class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.is_end: bool = False


class TrieDict:
    """字典树，使用 dict 存储子节点，支持任意字符。"""

    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def starts_with(self, prefix: str) -> bool:
        node = self.root
        for ch in prefix:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return True
```

---

## 二、Trie 应用

### 2.1 添加与搜索单词（含通配符）· [LC 211](https://leetcode.com/problems/design-add-and-search-words-data-structure/)

```python
class WordDictionary:
    """支持 '.' 通配符匹配任意单个字符。"""

    def __init__(self) -> None:
        self.children: list["WordDictionary | None"] = [None] * 26
        self.is_end: bool = False

    def add_word(self, word: str) -> None:
        node = self
        for ch in word:
            idx = ord(ch) - ord("a")
            if not node.children[idx]:
                node.children[idx] = WordDictionary()
            node = node.children[idx]
        node.is_end = True

    def search(self, word: str) -> bool:
        def dfs(node: WordDictionary, i: int) -> bool:
            if i == len(word):
                return node.is_end

            ch = word[i]
            if ch == ".":
                for child in node.children:
                    if child and dfs(child, i + 1):
                        return True
                return False
            else:
                idx = ord(ch) - ord("a")
                if not node.children[idx]:
                    return False
                return dfs(node.children[idx], i + 1)

        return dfs(self, 0)
```

### 2.2 单词替换 · [LC 648](https://leetcode.com/problems/replace-words/)

```python
def replace_words(dictionary: list[str], sentence: str) -> str:
    """用词根替换句子中的单词（最短前缀匹配）。"""
    trie = Trie()

    for root in dictionary:
        trie.insert(root)

    def find_shortest_root(word: str) -> str:
        node = trie
        for i, ch in enumerate(word):
            idx = ord(ch) - ord("a")
            if not node.children[idx]:
                break
            node = node.children[idx]
            if node.is_end:
                return word[: i + 1]  # 找到最短词根
        return word  # 没有词根，原样返回

    words = sentence.split()
    return " ".join(find_shortest_root(w) for w in words)
```

---

## 三、位 Trie（XOR 最大值）· [LC 421](https://leetcode.com/problems/maximum-xor-of-two-numbers-in-an-array/)

> 用二进制位构建 Trie（0/1 两个分支），用于高效查询与某个数 XOR 最大的数。

```python
class BitTrie:
    """二进制 Trie，用于 XOR 最大化查询。"""

    def __init__(self, max_bits: int = 31) -> None:
        self.children: list["BitTrie | None"] = [None, None]
        self.max_bits = max_bits

    def insert(self, num: int) -> None:
        node = self
        for i in range(self.max_bits, -1, -1):
            bit = (num >> i) & 1
            if not node.children[bit]:
                node.children[bit] = BitTrie(0)  # max_bits 不重要了
            node = node.children[bit]

    def max_xor(self, num: int) -> int:
        """查询与 num XOR 最大的值。"""
        node = self
        ans = 0
        for i in range(self.max_bits, -1, -1):
            bit = (num >> i) & 1
            # 尽量走相反方向以最大化 XOR
            opposite = 1 - bit
            if node.children[opposite]:
                ans |= 1 << i  # 此位 XOR 结果为 1
                node = node.children[opposite]
            else:
                node = node.children[bit]
        return ans


def find_maximum_xor(nums: list[int]) -> int:
    """数组中两个数的最大 XOR 值。"""
    bit_trie = BitTrie()
    ans = 0
    for num in nums:
        bit_trie.insert(num)
        ans = max(ans, bit_trie.max_xor(num))
    return ans
```

---

## 四、Trie + DFS（单词搜索 II）· [LC 212](https://leetcode.com/problems/word-search-ii/)

```python
def find_words(board: list[list[str]], words: list[str]) -> list[str]:
    """
    在二维网格中搜索单词列表中的单词。
    Trie 用于剪枝：DFS 过程中若前缀不在 Trie 中，立即回溯。
    """
    trie = Trie()
    for word in words:
        trie.insert(word)

    m, n = len(board), len(board[0])
    ans: list[str] = []

    def dfs(i: int, j: int, node: Trie, path: str) -> None:
        ch = board[i][j]
        idx = ord(ch) - ord("a")
        if not node.children[idx]:
            return

        node = node.children[idx]
        path += ch

        if node.is_end:
            ans.append(path)
            node.is_end = False  # 去重：已经加入的不重复加

        board[i][j] = "#"  # 标记已访问

        for di, dj in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < m and 0 <= nj < n and board[ni][nj] != "#":
                dfs(ni, nj, node, path)

        board[i][j] = ch  # 恢复

    for i in range(m):
        for j in range(n):
            dfs(i, j, trie, "")

    return ans
```

---

## 五、复杂度分析

| 操作 | 时间复杂度 | 空间复杂度 |
|------|-----------|-----------|
| 插入 | O(L) | O(L × 字符集大小) |
| 搜索 | O(L) | O(1) |
| 前缀搜索 | O(L) | O(1) |
| 通配符搜索 | O(26^M) 最坏 | O(M) 递归栈 |

L = 单词长度，M = 通配符个数

---

## 六、总结

| 应用场景 | 关键技巧 |
|----------|---------|
| 前缀匹配/自动补全 | 标准 Trie |
| 通配符搜索 | DFS 遍历所有分枝 |
| XOR 最大值 | 二进制位 Trie |
| 单词搜索 II | Trie + 网格 DFS |
| 键值映射 | 每个节点存 value |
| 按字典序遍历所有单词 | DFS 遍历 Trie |

---

## 七、习题推荐

| 题号 | 题目 | 难度 | 技巧 |
|------|------|------|------|
| [LC 208](https://leetcode.com/problems/implement-trie-prefix-tree/) | Implement Trie | Medium | 基本实现 |
| [LC 211](https://leetcode.com/problems/design-add-and-search-words-data-structure/) | Design Add and Search Words | Medium | 通配符搜索 |
| [LC 648](https://leetcode.com/problems/replace-words/) | Replace Words | Medium | 最短前缀 |
| [LC 677](https://leetcode.com/problems/map-sum-pairs/) | Map Sum Pairs | Medium | 带值 Trie |
| [LC 421](https://leetcode.com/problems/maximum-xor-of-two-numbers-in-an-array/) | Maximum XOR of Two Numbers | Medium | 位 Trie |
| [LC 212](https://leetcode.com/problems/word-search-ii/) | Word Search II | Hard | Trie+DFS剪枝 |
| [LC 720](https://leetcode.com/problems/longest-word-in-dictionary/) | Longest Word in Dictionary | Easy | Trie+DFS |
| [LC 745](https://leetcode.com/problems/prefix-and-suffix-search/) | Prefix and Suffix Search | Hard | 前后缀Trie |
| [LC 336](https://leetcode.com/problems/palindrome-pairs/) | Palindrome Pairs | Hard | Trie+回文 |
| [LC 472](https://leetcode.com/problems/concatenated-words/) | Concatenated Words | Hard | Trie+DP |

---

[← 返回索引](index.md)
