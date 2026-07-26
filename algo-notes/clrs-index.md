# 《算法导论》专题速查 · CLRS Topic Index

> 本页按**算法类型**（而不是书的章节顺序）重新组织了一遍 algo-notes 里源自
> 《算法导论》（CLRS，第3版）的内容，方便按主题查找，而不用记它在书里第几章。
> 已有的 LeetCode 向笔记（如排序、堆、BST、图基础）也顺带列进对应分类，
> 这样每个类别下能看到"基础在哪、进阶在哪"的完整链路。

---

## 一、排序与顺序统计量

| 专题 | 文件 | 对应 CLRS 章节 |
|------|------|---------------|
| 十大排序算法 | [sorting-algorithms.md](sorting-algorithms.md) | 第6-8章：堆排序、快速排序、线性时间排序 |
| 顺序统计量的选择算法 | [order-statistics-selection.md](order-statistics-selection.md) | 第9章：期望线性/最坏情况线性选择 |

## 二、数据结构

| 专题 | 文件 | 对应 CLRS 章节 |
|------|------|---------------|
| 手写动态数组 | [dynamic-array.md](dynamic-array.md) | 第10章：基本数据结构 |
| 手写栈和队列 | [stack-queue-implementation.md](stack-queue-implementation.md) | 第10章：基本数据结构 |
| 手写哈希表 | [hash-table-implementation.md](hash-table-implementation.md) | 第11章：散列表 |
| 二叉搜索树 | [binary-search-tree.md](binary-search-tree.md) | 第12章：二叉搜索树 |
| 红黑树 | [red-black-tree.md](red-black-tree.md) | 第13章：红黑树（插入完整实现，删除讲思路） |
| 数据结构的扩张（顺序统计树/区间树） | [interval-tree.md](interval-tree.md) | 第14章：数据结构的扩张 |
| 二叉堆实现 | [binary-heap-implementation.md](binary-heap-implementation.md) | 第6章：堆 |
| 堆 & 优先队列 | [heap-priority-queue.md](heap-priority-queue.md) | 第6章：堆（含 heapq 用法） |
| 斐波那契堆（简化版） | [fibonacci-heap.md](fibonacci-heap.md) | 第19章：斐波那契堆 |
| B 树 | [b-tree.md](b-tree.md) | 第18章：B树（插入完整实现，删除讲思路） |
| 并查集 | [union-find.md](union-find.md) | 第21章：用于不相交集合的数据结构 |
| 线段树 & 树状数组 | [segment-tree-fenwick.md](segment-tree-fenwick.md) | （CLRS 未直接覆盖，作为区间查询的常用补充） |

## 三、高级设计与分析技术

| 专题 | 文件 | 对应 CLRS 章节 |
|------|------|---------------|
| 动态规划框架 | [dp-framework.md](dp-framework.md) | 第15章：动态规划 |
| 贪心算法 | [greedy.md](greedy.md) | 第16章：贪心算法 |
| 摊还分析 | [amortized-analysis.md](amortized-analysis.md) | 第17章：摊还分析（聚合/核算/势能三种方法） |
| 复杂度分析实战 | [complexity-analysis.md](complexity-analysis.md) | （实战补充：O(n)超时估算、递归空间复杂度） |

## 四、图算法

| 专题 | 文件 | 对应 CLRS 章节 |
|------|------|---------------|
| 图结构基础（存储、遍历、拓扑排序、Dijkstra、Floyd-Warshall、Kruskal） | [graph-basics.md](graph-basics.md) | 第22章、24-25章、23章 |
| 最小生成树补充（Prim） | [minimum-spanning-tree.md](minimum-spanning-tree.md) | 第23章：最小生成树 |
| 最短路径补充（Bellman-Ford、DAG最短路、Johnson） | [shortest-path-advanced.md](shortest-path-advanced.md) | 第24-25章：单源/全源最短路径 |
| 最大流（Edmonds-Karp、二分图匹配） | [max-flow.md](max-flow.md) | 第26章：最大流 |
| BFS 框架 | [bfs-framework.md](bfs-framework.md) | 第22章：广度优先搜索 |

## 五、数论算法

| 专题 | 文件 | 对应 CLRS 章节 |
|------|------|---------------|
| 数学算法（快速幂、GCD、筛法、模运算、卡特兰数） | [math-algorithms.md](math-algorithms.md) | 第31章（部分） |
| 数论算法补充（扩展欧几里得、CRT、RSA、Miller-Rabin、Pollard's rho） | [number-theory-algorithms.md](number-theory-algorithms.md) | 第31章：数论算法 |

## 六、字符串匹配

| 专题 | 文件 | 对应 CLRS 章节 |
|------|------|---------------|
| 字符串匹配（KMP、Rabin-Karp、有限自动机、Z函数） | [string-matching.md](string-matching.md) | 第32章：字符串匹配 |
| 回文串算法（中心扩展法、Manacher） | [manacher-palindrome.md](manacher-palindrome.md) | （CLRS 未覆盖，字符串算法的常见补充） |

## 七、计算几何

| 专题 | 文件 | 对应 CLRS 章节 |
|------|------|---------------|
| 计算几何学（线段相交、凸包、最近点对） | [computational-geometry.md](computational-geometry.md) | 第33章：计算几何学 |

## 八、多项式与数值算法

| 专题 | 文件 | 对应 CLRS 章节 |
|------|------|---------------|
| 多项式与快速傅里叶变换 | [fft-polynomial.md](fft-polynomial.md) | 第30章：多项式与快速傅里叶变换 |

## 九、复杂度理论与近似算法

| 专题 | 文件 | 对应 CLRS 章节 |
|------|------|---------------|
| NP完全性（P/NP、归约、经典NP完全问题） | [np-completeness.md](np-completeness.md) | 第34章：NP完全性 |
| 近似算法（顶点覆盖、TSP、集合覆盖） | [approximation-algorithms.md](approximation-algorithms.md) | 第35章：近似算法 |

---

## 十、略过的章节

以下 4 章内容偏数值计算/并行计算理论，跟 LeetCode 风格的算法题几乎无关，本专题没有展开成文件：

| 章节 | 内容 | 跳过原因 |
|------|------|---------|
| 第20章 | van Emde Boas 树 | 支持 O(log log n) 操作的整数集合结构，理论精巧但工程/面试场景极少直接用到 |
| 第27章 | 多线程算法 | 面向共享内存并行计算模型（fork-join），和刷题场景的单线程算法思维差异较大 |
| 第28章 | 矩阵运算（解线性方程组、矩阵求逆） | 数值线性代数范畴，工程上直接调 numpy/BLAS，不需要手写 |
| 第29章 | 线性规划（单纯形算法） | 运筹优化范畴，工程上直接调现成求解器（如 scipy.optimize），手写单纯形不是常见需求 |

---

[← 返回索引](index.md)
