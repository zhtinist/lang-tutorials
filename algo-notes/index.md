# 算法笔记 · 完整版

---

## 目录

### 第零章前半 · 数据结构手写实现 

> 对应 labuladong 会员章节"基础：数据结构及排序精讲"。

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| 动态数组 | [dynamic-array.md](dynamic-array.md) | 扩容机制、均摊分析、环形数组 |
| 单/双链表实现 | [linked-list-implementation.md](linked-list-implementation.md) | 单链表完整CRUD、双链表、复杂度对比 |
| 栈和队列实现 | [stack-queue-implementation.md](stack-queue-implementation.md) | 链表/数组实现、环形队列、双端队列、互相实现 |
| 哈希表实现 | [hash-table-implementation.md](hash-table-implementation.md) | 拉链法、线性探查法、布隆过滤器 |
| 二叉堆实现 | [binary-heap-implementation.md](binary-heap-implementation.md) | swim/sink、建堆O(n)证明、最大堆、堆排序 |
| 十大排序算法 | [sorting-algorithms.md](sorting-algorithms.md) | 冒泡/选择/插入/希尔/快排/归并/堆排/计数/桶/基数 |
| 图结构基础 | [graph-basics.md](graph-basics.md) | 邻接矩阵/表、DFS/BFS、拓扑排序、Dijkstra、MST |

### 第零章 · 核心刷题框架

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| 二分搜索 | [binary-search.md](binary-search.md) | 基础二分、左右边界、二分答案 |
| 双指针 | [two-pointer.md](two-pointer.md) | 快慢指针、左右指针、nSum模板 |
| 滑动窗口 | [sliding-window.md](sliding-window.md) | 定长/变长窗口、哈希表辅助 |
| 前缀和 & 差分数组 | [prefix-sum-diff-array.md](prefix-sum-diff-array.md) | 前缀和、二维前缀和、差分数组 |
| BFS 框架 | [bfs-framework.md](bfs-framework.md) | 树的BFS、图的BFS、最短路径 |
| 回溯框架 | [backtracking.md](backtracking.md) | 排列、组合、子集、N皇后 |
| 动态规划框架 | [dp-framework.md](dp-framework.md) | DP三要素、自顶向下/自底向上、状态转移 |

### 第一章 · 经典数据结构

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| 链表 | [linked-list.md](linked-list.md) | 反转链表、快慢指针、合并/拆分 |
| 二叉树 | [binary-tree.md](binary-tree.md) | 遍历框架、构造树、最近公共祖先 |
| 二叉搜索树 | [binary-search-tree.md](binary-search-tree.md) | BST操作、AVL/红黑树简介 |
| 堆 & 优先队列 | [heap-priority-queue.md](heap-priority-queue.md) | 堆实现、TopK、多路归并 |
| 并查集 (Union-Find) | [union-find.md](union-find.md) | 路径压缩、按秩合并、应用场景 |
| 字典树 (Trie) | [trie.md](trie.md) | 前缀树实现、应用 |
| 单调栈 & 单调队列 | [monotonic-stack-queue.md](monotonic-stack-queue.md) | 下一个更大元素、滑动窗口最大值 |
| LRU & LFU 缓存 | [lru-lfu-cache.md](lru-lfu-cache.md) | 哈希链表、频次桶 |
| 线段树 & 树状数组 | [segment-tree-fenwick.md](segment-tree-fenwick.md) | 区间查询、单点/区间更新 |

### 第二章 · 暴力搜索算法

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| DFS & 回溯精讲 | [dfs-backtracking.md](dfs-backtracking.md) | 排列/组合/子集模板、剪枝优化 |
| BFS & 网格问题 | [bfs-grid.md](bfs-grid.md) | 网格BFS/DFS、岛屿问题、最短路径 |
| 双向 BFS | [bidirectional-bfs.md](bidirectional-bfs.md) | 双向搜索优化、单词接龙 |

### 第三章 · 动态规划

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| DP 基础 | [dp-basics.md](dp-basics.md) | 斐波那契、爬楼梯、打家劫舍 |
| 背包问题 | [knapsack.md](knapsack.md) | 0-1背包、完全背包、多重背包 |
| 子序列问题 | [subsequence-problems.md](subsequence-problems.md) | LCS、LIS、编辑距离、正则匹配 |
| 股票交易系列 | [stock-trading.md](stock-trading.md) | 6道股票题的状态机DP统一解法 |
| 打家劫舍系列 | [house-robber.md](house-robber.md) | 线性、环形、树形DP |
| 博弈 DP | [game-theory-dp.md](game-theory-dp.md) | Minimax、石子游戏 |
| 区间 DP | [interval-dp.md](interval-dp.md) | 戳气球、矩阵链乘 |
| 状压 DP & 数位 DP | [bitmask-dp.md](bitmask-dp.md) | 状态压缩、旅行商、数位DP模板 |

### 第四章 · 其他算法技巧

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| 贪心算法 | [greedy.md](greedy.md) | 区间调度、跳跃游戏、哈夫曼编码 |
| 位运算 | [bit-manipulation.md](bit-manipulation.md) | 位运算技巧、状态压缩、Brian Kernighan |
| 数学算法 | [math-algorithms.md](math-algorithms.md) | 快速幂、筛法、GCD、模运算 |
| 区间问题 | [intervals.md](intervals.md) | 区间合并、插入、交集、扫描线 |
| 字符串匹配 | [string-matching.md](string-matching.md) | KMP、Rabin-Karp、Z函数 |
| 杂项技巧 | [miscellaneous.md](miscellaneous.md) | 快速选择、摩尔投票、蓄水池抽样 |

### 附录

| 内容 | 文件 | 说明 |
|------|------|------|
| Python 算法库速查 | [python-cheatsheet.md](python-cheatsheet.md) | 算法专用：collections/heapq/itertools/functools |
| LeetCode Hot 100 索引 | [leetcode-hot100.md](leetcode-hot100.md) | 按专题分类的题目索引 |

---

## 使用建议

1. **速成路线**: 第零章前半(数据结构原理) → 第零章框架 → 第一章核心结构 → 第三章基础DP → 第四章高频技巧
2. **系统学习**: 从头按章节顺序完整阅读，每章框架代码默写 3 遍（特别是二叉树遍历和DP框架）
3. **刷题配合**: 每个专题末尾有 LeetCode 题目推荐，题号都是可点击的英文站链接，建议先看框架再做题
4. **代码风格**: 所有代码使用 Python 3.12+ 语法，含类型注解（`typing`），遵循 PEP 8
5. **附录查询**: 忘记算法库函数时查 `python-cheatsheet.md`；想按专题刷题查 `leetcode-hot100.md`

---

