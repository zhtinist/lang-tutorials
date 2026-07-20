# LeetCode Hot 100 索引

> 按专题分类的 LeetCode Hot 100 题目索引。标注难度和对应笔记位置。
> 🔒 = 会员题，📌 = 面试高频额外推荐。

---

## 哈希

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 1 | Two Sum | Easy | [双指针](two-pointer.md) |
| 49 | Group Anagrams | Medium | 哈希表 |
| 128 | Longest Consecutive Sequence | Medium | 哈希+UnionFind |

---

## 双指针

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 283 | Move Zeroes | Easy | [双指针](two-pointer.md) |
| 11 | Container With Most Water | Medium | [双指针](two-pointer.md) |
| 15 | 3Sum | Medium | [双指针 nSum](two-pointer.md) |
| 42 | Trapping Rain Water | Hard | [双指针/单调栈](monotonic-stack-queue.md) |

---

## 滑动窗口

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 3 | Longest Substring Without Repeating | Medium | [滑动窗口](sliding-window.md) |
| 438 | Find All Anagrams | Medium | [滑动窗口](sliding-window.md) |
| 239 | Sliding Window Maximum | Hard | [单调队列](monotonic-stack-queue.md) |
| 76 | Minimum Window Substring | Hard | [滑动窗口](sliding-window.md) |

---

## 子串

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 560 | Subarray Sum Equals K | Medium | [前缀和](prefix-sum-diff-array.md) |
| 53 | Maximum Subarray | Medium | DP / 分治 |
| 152 | Maximum Product Subarray | Medium | DP |

---

## 普通数组

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 238 | Product Except Self | Medium | [前后缀积](prefix-sum-diff-array.md) |
| 189 | Rotate Array | Medium | 数组反转 |
| 41 | First Missing Positive | Hard | 原地哈希 |
| 215 | Kth Largest Element | Medium | [快速选择/堆](miscellaneous.md) |
| 347 | Top K Frequent | Medium | [堆](heap-priority-queue.md) |
| 56 | Merge Intervals | Medium | [区间合并](intervals.md) |

---

## 矩阵

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 73 | Set Matrix Zeroes | Medium | 原地标记 |
| 54 | Spiral Matrix | Medium | 模拟 |
| 48 | Rotate Image | Medium | 转置+翻转 |
| 240 | Search a 2D Matrix II | Medium | 对角二分 |

---

## 链表

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 160 | Intersection of Two Linked Lists | Easy | [链表双指针](linked-list.md) |
| 206 | Reverse Linked List | Easy | [反转链表](linked-list.md) |
| 234 | Palindrome Linked List | Easy | [回文链表](linked-list.md) |
| 141 | Linked List Cycle | Easy | [快慢指针判环](linked-list.md) |
| 142 | Linked List Cycle II | Medium | [环入口](linked-list.md) |
| 21 | Merge Two Sorted Lists | Easy | [合并链表](linked-list.md) |
| 2 | Add Two Numbers | Medium | 链表模拟加法 |
| 19 | Remove Nth Node From End | Medium | [倒数第K个](linked-list.md) |
| 24 | Swap Nodes in Pairs | Medium | 链表交换 |
| 25 | Reverse Nodes in k-Group | Hard | [K个一组反转](linked-list.md) |
| 138 | Copy List with Random Pointer | Medium | 深拷贝链表 |
| 23 | Merge k Sorted Lists | Hard | [K路归并](heap-priority-queue.md) |
| 148 | Sort List | Medium | 归并排序链表 |
| 146 | LRU Cache | Medium | [LRU](lru-lfu-cache.md) |

---

## 二叉树

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 94 | Inorder Traversal | Easy | [中序](binary-tree.md) |
| 104 | Maximum Depth | Easy | [后序分解](binary-tree.md) |
| 226 | Invert Binary Tree | Easy | [翻转](binary-tree.md) |
| 101 | Symmetric Tree | Easy | [对称判断](binary-tree.md) |
| 543 | Diameter of Binary Tree | Easy | [后序直径](binary-tree.md) |
| 102 | Level Order Traversal | Medium | [层序](bfs-framework.md) |
| 108 | Sorted Array to BST | Easy | [BST构造](binary-search-tree.md) |
| 98 | Validate BST | Medium | [BST验证](binary-search-tree.md) |
| 230 | Kth Smallest in BST | Medium | [BST中序](binary-search-tree.md) |
| 105 | Construct from Pre+In | Medium | [构造树](binary-tree.md) |
| 114 | Flatten to Linked List | Medium | 前序展开 |
| 437 | Path Sum III | Medium | 前缀和+树 |
| 236 | LCA of Binary Tree | Medium | [LCA后序](binary-tree.md) |
| 124 | Binary Tree Max Path Sum | Hard | 后序+路径 |

---

## 图

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 200 | Number of Islands | Medium | [网格DFS/BFS](bfs-grid.md) |
| 994 | Rotting Oranges | Medium | [多源BFS](bfs-grid.md) |
| 207 | Course Schedule | Medium | 拓扑排序/环检测 |
| 208 | Implement Trie | Medium | [Trie实现](trie.md) |

---

## 回溯

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 46 | Permutations | Medium | [排列模板](backtracking.md) |
| 78 | Subsets | Medium | [子集模板](backtracking.md) |
| 17 | Letter Combinations | Medium | [回溯+字符串](backtracking.md) |
| 79 | Word Search | Medium | 回溯+网格 |
| 22 | Generate Parentheses | Medium | [回溯+合法性](dfs-backtracking.md) |
| 39 | Combination Sum | Medium | [组合可重复](backtracking.md) |
| 131 | Palindrome Partitioning | Medium | [回溯+回文](dfs-backtracking.md) |
| 51 | N-Queens | Hard | [N皇后](backtracking.md) |

---

## 二分查找

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 35 | Search Insert Position | Easy | [lower_bound](binary-search.md) |
| 74 | Search a 2D Matrix | Medium | 二维二分 |
| 34 | Find First and Last Position | Medium | [左右边界](binary-search.md) |
| 33 | Search in Rotated Sorted Array | Medium | [旋转数组二分](binary-search.md) |
| 153 | Find Min in Rotated Sorted Array | Medium | [旋转找最小值](binary-search.md) |
| 4 | Median of Two Sorted Arrays | Hard | 二分排除 |

---

## 贪心

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 121 | Best Time to Buy and Sell Stock | Easy | [股票DP简化](stock-trading.md) |
| 55 | Jump Game | Medium | [贪心跳跃](greedy.md) |
| 45 | Jump Game II | Medium | [最少跳跃](greedy.md) |
| 763 | Partition Labels | Medium | 区间贪心 |

---

## 动态规划

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 70 | Climbing Stairs | Easy | [线性DP](dp-basics.md) |
| 118 | Pascal's Triangle | Easy | 递推 |
| 198 | House Robber | Medium | [打家劫舍](house-robber.md) |
| 279 | Perfect Squares | Medium | [完全背包/DP](dp-basics.md) |
| 322 | Coin Change | Medium | [完全背包](knapsack.md) |
| 139 | Word Break | Medium | [字符串DP](dp-basics.md) |
| 300 | LIS | Medium | [子序列DP](subsequence-problems.md) |
| 152 | Maximum Product Subarray | Medium | DP |
| 416 | Partition Equal Subset Sum | Medium | [0-1背包](knapsack.md) |
| 32 | Longest Valid Parentheses | Hard | DP/栈 |

---

## 多维动态规划

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 62 | Unique Paths | Medium | [网格路径](dp-basics.md) |
| 64 | Minimum Path Sum | Medium | [最小路径和](dp-basics.md) |
| 5 | Longest Palindromic Substring | Medium | 区间DP/中心扩展 |
| 1143 | Longest Common Subsequence | Medium | [LCS](subsequence-problems.md) |
| 72 | Edit Distance | Medium | [编辑距离](subsequence-problems.md) |
| 10 | Regular Expression Matching | Hard | [正则匹配](subsequence-problems.md) |

---

## 技巧

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| 136 | Single Number | Easy | [XOR](bit-manipulation.md) |
| 169 | Majority Element | Easy | [摩尔投票](miscellaneous.md) |
| 75 | Sort Colors | Medium | 三指针荷兰旗 |
| 31 | Next Permutation | Medium | 字典序 |
| 287 | Find the Duplicate Number | Medium | 快慢指针/二分 |
| 394 | Decode String | Medium | 栈/递归 |
| 739 | Daily Temperatures | Medium | [单调栈](monotonic-stack-queue.md) |
| 84 | Largest Rectangle in Histogram | Hard | [单调栈](monotonic-stack-queue.md) |
| 295 | Find Median from Data Stream | Hard | [双堆](heap-priority-queue.md) |
| 297 | Serialize and Deserialize | Hard | [序列化](binary-tree.md) |
| 621 | Task Scheduler | Medium | [贪心](greedy.md) |

---

## 📌 额外推荐（高频但不在 Hot 100）

| 题号 | 题目 | 难度 | 笔记参考 |
|------|------|------|----------|
| [LC 91](https://leetcode.com/problems/decode-ways/) | Decode Ways | Medium | [字符串DP](dp-basics.md) |
| [LC 50](https://leetcode.com/problems/powx-n/) | Pow(x,n) | Medium | [快速幂](math-algorithms.md) |
| [LC 82](https://leetcode.com/problems/remove-duplicates-from-sorted-list-ii/) | Remove Duplicates II | Medium | 链表 |
| [LC 210](https://leetcode.com/problems/course-schedule-ii/) | Course Schedule II | Medium | 拓扑排序 |
| [LC 204](https://leetcode.com/problems/count-primes/) | Count Primes | Medium | [埃氏筛](math-algorithms.md) |
| [LC 337](https://leetcode.com/problems/house-robber-iii/) | House Robber III | Medium | [树形DP](house-robber.md) |
| [LC 309](https://leetcode.com/problems/best-time-to-buy-and-sell-stock-with-cooldown/) | Best Time w/Cooldown | Medium | [股票DP冷冻期](stock-trading.md) |
| [LC 460](https://leetcode.com/problems/lfu-cache/) | LFU Cache | Hard | [LFU实现](lru-lfu-cache.md) |
| [LC 127](https://leetcode.com/problems/word-ladder/) | Word Ladder | Hard | [双向BFS](bidirectional-bfs.md) |
| [LC 212](https://leetcode.com/problems/word-search-ii/) | Word Search II | Hard | [Trie+DFS](trie.md) |
| [LC 312](https://leetcode.com/problems/burst-balloons/) | Burst Balloons | Hard | [区间DP](interval-dp.md) |
| [LC 773](https://leetcode.com/problems/sliding-puzzle/) | Sliding Puzzle | Hard | [BFS](bfs-framework.md) |
| [LC 752](https://leetcode.com/problems/open-the-lock/) | Open the Lock | Medium | [BFS](bfs-framework.md) |
| [LC 399](https://leetcode.com/problems/evaluate-division/) | Evaluate Division | Medium | [带权并查集](union-find.md) |
| [LC 494](https://leetcode.com/problems/target-sum/) | Target Sum | Medium | [0-1背包](knapsack.md) |

---

[← 返回索引](index.md)
