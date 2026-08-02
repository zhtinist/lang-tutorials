# 算法选择思维导图 · 看题选算法

> **专治「看完题目一脸懵，想不到该用哪个算法」。**
> 打家劫舍([LC 198](https://leetcode.com/problems/house-robber/))、最长递增子序列([LC 300](https://leetcode.com/problems/longest-increasing-subsequence/))这类题，难点从来不是写代码，而是**认出它是 DP、并且是哪一种 DP**。
> 这份地图把「**题目里你能看到的特征**」直接映射到「**该用的算法 → 落到哪一个具体子分支 → 对应笔记**」。

---

## 先问自己三个问题（DP 识别口诀）

拿到题先别急着想数据结构，先套这三问，命中就大概率是 **动态规划**：

1. **求什么？** —— 是不是在求「**最值**（最长/最短/最大/最小）」「**方案总数**」或「**能不能达到 / 可行性**」？（不是"列出所有具体方案"——那是回溯）
2. **每一步有没有"选择"？** —— 每个位置/物品能"选或不选、选哪个"，且**当前选择只依赖前面已定的结果**（无后效性）。
3. **子问题会不会重复？** —— 暴力递归会把同一个子情况算很多遍（画一下递归树就能看出重叠）。

> 三问都"是" → **DP**。接着用下面的地图把它落到**线性 DP / 背包 / 子序列 / 区间 / 状压 / 数位 / 树形 / 博弈 / 状态机**里的**某一种**。
> 打家劫舍 = "选了相邻的就不能选，求最大" → **线性 DP**；最长递增子序列 = "一个序列里挑出最长的递增子序列" → **子序列 DP(LIS)**。它们表面看是数组题，本质都是上面这三问。

---

## 交互式决策地图

**用法**：在下面输入框里敲你从题面里读到的**特征词**（比如 `相邻不能选`、`最长子序列`、`最小化最大值`、`连续子数组`、`第k大`、`所有方案`、`方案数`、`最少步数`），地图会自动筛出对应算法与笔记链接；也可以直接点分类标题展开浏览。

<div id="amap">
  <div class="amap-bar">
    <input id="amap-q" class="amap-input" type="text" placeholder="🔍 输入题目特征，如：相邻不能选 / 最长子序列 / 最小化最大值 / 连续子数组 / 第k大 ..." autocomplete="off">
    <div class="amap-tools">
      <button id="amap-expand" class="amap-btn" type="button">展开全部</button>
      <button id="amap-collapse" class="amap-btn" type="button">收起全部</button>
      <span id="amap-count" class="amap-count"></span>
    </div>
    <div id="amap-chips" class="amap-chips"></div>
  </div>
  <div id="amap-tree" class="amap-tree"></div>
  <noscript><p style="color:var(--muted)">（交互地图需要 JavaScript。可直接查阅：<a href="dp-framework.html">DP 框架</a>、<a href="house-robber.html">打家劫舍</a>、<a href="subsequence-problems.html">子序列问题</a>、<a href="knapsack.html">背包</a>。）</p></noscript>
</div>

<style>
#amap{border:1px solid var(--border);border-radius:14px;background:color-mix(in srgb,var(--accent) 3%,var(--bg));padding:16px 16px 20px;margin:1.4em 0}
#amap *{box-sizing:border-box}
#amap .amap-bar{position:sticky;top:56px;z-index:5;background:color-mix(in srgb,var(--accent) 6%,var(--bg));backdrop-filter:blur(4px);padding:10px;border:1px solid var(--border);border-radius:10px;margin-bottom:14px}
#amap .amap-input{width:100%;font-size:1rem;padding:10px 12px;border:1px solid var(--border);border-radius:8px;background:var(--bg);color:var(--fg)}
#amap .amap-input:focus{outline:2px solid var(--accent);border-color:var(--accent)}
#amap .amap-tools{display:flex;align-items:center;gap:8px;margin-top:8px;flex-wrap:wrap}
#amap .amap-btn{font-size:.82rem;padding:4px 10px;border:1px solid var(--border);border-radius:20px;background:var(--bg);color:var(--accent);cursor:pointer}
#amap .amap-btn:hover{background:color-mix(in srgb,var(--accent) 12%,transparent)}
#amap .amap-count{font-size:.82rem;color:var(--muted);margin-left:auto}
#amap .amap-chips{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}
#amap .amap-chip{font-size:.78rem;padding:3px 10px;border-radius:20px;border:1px solid var(--border);background:var(--code-bg);color:var(--muted);cursor:pointer}
#amap .amap-chip:hover{color:var(--accent);border-color:var(--accent)}
#amap .amap-cat{border:1px solid var(--border);border-radius:10px;margin-bottom:10px;overflow:hidden;background:var(--bg)}
#amap .amap-cathead{display:flex;align-items:center;gap:10px;padding:12px 14px;cursor:pointer;user-select:none}
#amap .amap-cathead:hover{background:color-mix(in srgb,var(--accent) 6%,transparent)}
#amap .amap-cat-icon{font-size:1.2rem;line-height:1;flex:0 0 auto}
#amap .amap-cat-title{font-weight:700;color:var(--accent-dark);font-size:1.02rem}
#amap .amap-cat-tag{color:var(--muted);font-size:.82rem;flex:1;min-width:0}
#amap .amap-cat-n{font-size:.75rem;color:var(--muted);border:1px solid var(--border);border-radius:20px;padding:1px 8px;flex:0 0 auto}
#amap .amap-arrow{transition:transform .18s;color:var(--muted);flex:0 0 auto}
#amap .amap-cat.open .amap-arrow{transform:rotate(90deg)}
#amap .amap-catbody{display:none;padding:4px 10px 10px;border-top:1px solid var(--border)}
#amap .amap-cat.open .amap-catbody{display:block}
#amap .amap-item{display:grid;grid-template-columns:1fr auto;gap:6px 14px;align-items:start;padding:11px 8px;border-bottom:1px dashed var(--border)}
#amap .amap-item:last-child{border-bottom:none}
#amap .amap-sig{color:var(--fg);font-size:.94rem;line-height:1.55}
#amap .amap-sig::before{content:"👀 ";opacity:.7}
#amap .amap-algo{grid-column:1;color:var(--accent-dark);font-weight:600;font-size:.92rem;margin-top:2px}
#amap .amap-algo::before{content:"→ ";color:var(--accent)}
#amap .amap-tip{grid-column:1;color:var(--muted);font-size:.82rem;line-height:1.5;margin-top:2px}
#amap .amap-link{grid-column:2;grid-row:1 / span 3;align-self:center;white-space:nowrap;font-size:.82rem;padding:5px 11px;border:1px solid var(--accent);border-radius:20px;color:var(--accent)}
#amap .amap-link:hover{background:var(--accent);color:#fff;text-decoration:none}
#amap mark{background:color-mix(in srgb,var(--accent) 32%,transparent);color:inherit;border-radius:3px;padding:0 1px}
#amap .amap-empty{color:var(--muted);text-align:center;padding:24px}
@media(max-width:560px){#amap .amap-item{grid-template-columns:1fr}#amap .amap-link{grid-column:1;grid-row:auto;justify-self:start;margin-top:6px}}
</style>

<script>
(function(){
  var DATA=[
    {icon:"🎯",title:"动态规划 DP",tag:"求最值/方案数/可行性 · 每步有选择 · 子问题重叠 → 再选下面哪一种",items:[
      {sig:"每个元素“选了就不能选相邻的”，求能拿到的最大值（打家劫舍 LC198）",algo:"线性 DP · 打家劫舍",tip:"最典型的“想不到是 DP”题：dp[i]=max(dp[i-1], dp[i-2]+nums[i])。环形拆成两次线性；树上就变树形 DP。",href:"house-robber.html"},
      {sig:"爬楼梯 / 斐波那契 / 一次走 1~k 步，求方案数或最小代价",algo:"线性递推 DP",tip:"一维 dp，当前状态由前几个状态相加/取最值得到。",href:"dp-basics.html"},
      {sig:"网格从左上走到右下：路径条数 / 最小路径和 / 带障碍",algo:"二维网格 DP",tip:"dp[i][j] 由上方和左方转移，注意边界初始化。",href:"dp-framework.html"},
      {sig:"一堆物品有重量/成本，容量固定，求最大价值 / 能否装满 / 装满方案数",algo:"背包 DP",tip:"每件选一次=0-1背包；无限次=完全背包；有限次=多重背包；两种限制=二维费用背包。",href:"knapsack.html"},
      {sig:"用硬币凑总额：最少几枚 / 有多少种凑法（零钱兑换）",algo:"完全背包",tip:"求最少枚数与求方案数遍历顺序不同：方案数要“物品外层、容量内层”。",href:"knapsack.html"},
      {sig:"数组能否分成两个和相等的子集 / 目标和 / 一和零",algo:"0-1 背包（布尔 or 计数）",tip:"“能否凑出某个和”是背包的可行性版本；“目标和”转成子集划分。",href:"knapsack.html"},
      {sig:"一个序列里挑出“最长递增子序列”（可以不连续）LC300",algo:"子序列 DP · LIS",tip:"另一道经典“想不到是 DP”题！O(n²) 的 dp[i]=看前面比它小的最大 dp+1；进阶 O(n log n) 贪心+二分（耐心排序）。",href:"subsequence-problems.html"},
      {sig:"两个序列的最长公共子序列 / 最少编辑几步能变过去（编辑距离）",algo:"双序列 DP · LCS / 编辑距离",tip:"二维 dp[i][j] 表示两个前缀的答案，字符相等/不等两种转移。",href:"subsequence-problems.html"},
      {sig:"判断/统计 s 是不是 t 的子序列、不同子序列个数、通配符/正则匹配",algo:"匹配型二维 DP",tip:"和编辑距离同一家族：都是在两个串的前缀上做二维 DP。",href:"subsequence-problems.html"},
      {sig:"区间两端向内收缩、戳气球、合并石子、最后剩下什么",algo:"区间 DP",tip:"dp[i][j] 枚举分割点/最后操作点 k，由更小的区间合并；按区间长度从小到大算。",href:"interval-dp.html"},
      {sig:"数据规模 n ≤ 20，要枚举“集合的状态”，旅行商 TSP、状态子集",algo:"状压 DP",tip:"n 很小 + 需要记录“哪些已选”这种集合信息，就用一个整数的二进制位当状态。",href:"bitmask-dp.html"},
      {sig:"统计区间 [L,R] 内满足某数位性质的数字个数（不含4、各位递增…）",algo:"数位 DP",tip:"按位从高到低填，记录“是否贴上界/前导零”等状态，答案 = f(R) - f(L-1)。",href:"bitmask-dp.html"},
      {sig:"两人轮流拿、都绝顶聪明，问先手能否赢 / 最大得分差",algo:"博弈 DP（Minimax）",tip:"状态里站在“当前该谁走”的视角取对自己最有利的值。",href:"game-theory-dp.html"},
      {sig:"买卖股票：限制交易 k 次 / 有冷冻期 / 有手续费",algo:"状态机 DP",tip:"用“持有/不持有/冷冻”等状态 + 天数做二维/三维 DP，一个模板统一 6 道股票题。",href:"stock-trading.html"},
      {sig:"树上每个节点“选或不选”，选了会影响父/子节点",algo:"树形 DP",tip:"后序遍历，每个节点返回“选它/不选它”两种最优值给父节点。",href:"house-robber.html"}
    ]},
    {icon:"⚖️",title:"二分搜索 Binary Search",tag:"有序 / 答案具有单调性",items:[
      {sig:"数组有序，找目标值 / 第一个 ≥x / 最后一个 ≤x",algo:"二分（左右边界模板）",tip:"关键是把“找左边界/右边界”写对，别用一个模板套所有题。",href:"binary-search.html"},
      {sig:"“最小化最大值 / 最大化最小值 / 能否在 X 内完成”这类措辞",algo:"二分答案",tip:"看到“最大值最小”“最小值最大”几乎条件反射：二分那个答案，写个 check(x) 判可行。",href:"binary-search.html"},
      {sig:"旋转有序数组里查找 / 找峰值",algo:"二分变形",tip:"每次判断哪半边有序，再决定往哪边收缩。",href:"binary-search.html"}
    ]},
    {icon:"👉",title:"双指针 / 滑动窗口",tag:"连续区间 · 有序数组 · 快慢指针",items:[
      {sig:"有序数组两数之和、原地去重、反转、判回文",algo:"相向 / 快慢双指针",tip:"有序 + 求一对/原地操作，优先想双指针，省掉哈希表和额外空间。",href:"two-pointer.html"},
      {sig:"“连续”子数组/子串，求最长/最短/恰好满足某条件",algo:"滑动窗口",tip:"识别信号：连续 + 最长/最短/子串/子数组 + 某个约束（和、字符种类…）。",href:"sliding-window.html"},
      {sig:"链表找环、找中点、找倒数第 k 个",algo:"快慢指针",tip:"一个走一步一个走两步，或先走 k 步再同步走。",href:"linked-list.html"}
    ]},
    {icon:"➕",title:"前缀和 / 差分数组",tag:"区间和 · 区间批量修改",items:[
      {sig:"频繁查询“区间和”、子数组和为 k 的个数、和能被 k 整除",algo:"前缀和（+ 哈希表）",tip:"“子数组和 = k 的个数”= 前缀和之差，用哈希表边算边查。",href:"prefix-sum-diff-array.html"},
      {sig:"对一个区间整体加/减同一个数，最后问结果",algo:"差分数组",tip:"区间加 → 只改两端 O(1)，最后求一次前缀和还原。",href:"prefix-sum-diff-array.html"},
      {sig:"二维矩阵求任意子矩形的元素和",algo:"二维前缀和",tip:"容斥：sum = P[d]-P[u]-P[l]+P[ul]。",href:"prefix-sum-diff-array.html"}
    ]},
    {icon:"📊",title:"单调栈 / 单调队列",tag:"下一个更大更小 · 窗口最值",items:[
      {sig:"“下一个更大/更小元素”、每日温度、柱状图最大矩形、接雨水",algo:"单调栈",tip:"要为每个元素找“左边/右边第一个比它大/小”的位置，就是单调栈。",href:"monotonic-stack-queue.html"},
      {sig:"滑动窗口的最大值 / 最小值",algo:"单调队列",tip:"维护一个单调递减/递增的双端队列，队头就是窗口最值。",href:"monotonic-stack-queue.html"}
    ]},
    {icon:"⛰️",title:"堆 / 选择算法",tag:"第 k 大 · TopK · 动态中位数",items:[
      {sig:"第 k 大 / 第 k 小 / 前 K 个高频元素",algo:"堆 或 快速选择",tip:"要维护动态 TopK 用大小为 k 的堆 O(n log k)；一次性只求第 k 个用快速选择 O(n) 期望。",href:"heap-priority-queue.html"},
      {sig:"数据流里动态求中位数",algo:"对顶双堆",tip:"大顶堆放小的一半、小顶堆放大的一半，两堆顶给中位数。",href:"heap-priority-queue.html"},
      {sig:"合并 K 个有序链表/数组、多路归并",algo:"最小堆",tip:"每路的当前头进堆，弹最小再补下一个。",href:"heap-priority-queue.html"},
      {sig:"只要第 k 大那一个值，允许 O(n) 期望、可打乱原数组",algo:"快速选择（partition）",tip:"快排的 partition 只递归一侧，期望线性。",href:"order-statistics-selection.html"},
      {sig:"出现次数超过一半的元素（多数元素）",algo:"摩尔投票",tip:"O(n) 时间 O(1) 空间，抵消掉不同的元素。",href:"miscellaneous.html"}
    ]},
    {icon:"🌲",title:"回溯 / 枚举所有方案",tag:"要“列出全部”排列组合子集切割",items:[
      {sig:"要求“列出所有”排列 / 组合 / 子集 / 分割方案 / 合法括号",algo:"回溯（DFS + 撤销）",tip:"分水岭：要“所有具体方案”→回溯；只要“方案数量或最优值”→往往能改成 DP 省指数级时间。",href:"backtracking.html"},
      {sig:"棋盘类：N 皇后、数独、单词搜索、岛屿涂色",algo:"回溯 + 剪枝",tip:"关键在剪枝（可行性判断、去重、对称性）把指数搜索压下来。",href:"dfs-backtracking.html"}
    ]},
    {icon:"🌊",title:"BFS / DFS 搜索",tag:"最少步数 · 网格连通 · 层序",items:[
      {sig:"无权图/网格求“最少步数 / 最短路径 / 层序遍历”",algo:"BFS",tip:"边权都相等时，BFS 第一次到达即最短；用队列一层层扩。",href:"bfs-framework.html"},
      {sig:"网格里数岛屿 / 连通块 / 区域填充 / 感染扩散",algo:"DFS 或 BFS 或并查集",tip:"数连通块三种都行；如果还要动态合并/查询连通性，选并查集。",href:"bfs-grid.html"},
      {sig:"起点终点都已知、状态一步步变换求最短（单词接龙）",algo:"双向 BFS",tip:"从两端同时扩，相遇即止，指数级搜索空间开根号。",href:"bidirectional-bfs.html"}
    ]},
    {icon:"🕸️",title:"图论进阶",tag:"最短路 · 拓扑 · 生成树 · 网络流",items:[
      {sig:"带权（非负）图，单源最短路",algo:"Dijkstra（堆优化）",tip:"边权非负才能用；用优先队列每次取当前最近的点。",href:"shortest-path-advanced.html"},
      {sig:"有负权边 / 需要判断是否存在负环",algo:"Bellman-Ford / SPFA",tip:"松弛 V-1 轮；第 V 轮还能松弛就有负环。",href:"shortest-path-advanced.html"},
      {sig:"求任意两点间最短路，且点数不大（n≤几百）",algo:"Floyd-Warshall",tip:"三重循环 O(n³)，k 作为中转点写在最外层。",href:"graph-basics.html"},
      {sig:"任务有先后依赖 / 课程表 / 编译顺序 / 判断能否排完",algo:"拓扑排序",tip:"入度为 0 的先出队；排不满说明有环。",href:"graph-basics.html"},
      {sig:"把所有点连起来，让总连接成本最小",algo:"最小生成树 Kruskal / Prim",tip:"Kruskal 按边排序+并查集；Prim 像 Dijkstra 从点扩。",href:"minimum-spanning-tree.html"},
      {sig:"二分图匹配 / 任务分配 / 网络流量最大",algo:"最大流 / 二分图匹配",tip:"最大流最小割定理；匹配问题常转成流。",href:"max-flow.html"}
    ]},
    {icon:"🔗",title:"专用数据结构",tag:"连通性 · 前缀 · 区间修改 · 缓存",items:[
      {sig:"动态合并集合、判断两点是否连通、判环",algo:"并查集（路径压缩+按秩合并）",tip:"近乎 O(1) 的合并与查询；连通块/朋友圈/冗余连接都用它。",href:"union-find.html"},
      {sig:"大量字符串的前缀查询 / 自动补全 / 词典匹配",algo:"字典树 Trie",tip:"按字符建树，前缀共享路径。",href:"trie.html"},
      {sig:"数组要“频繁区间查询 + 单点/区间修改”",algo:"线段树 / 树状数组",tip:"只单点改+区间和用树状数组更轻；复杂区间操作用线段树。",href:"segment-tree-fenwick.html"},
      {sig:"固定容量缓存，满了淘汰“最久未用 / 最少用”的",algo:"LRU / LFU（哈希 + 双向链表）",tip:"O(1) get/put：哈希定位 + 双链表维护顺序。",href:"lru-lfu-cache.html"}
    ]},
    {icon:"💰",title:"贪心 / 区间处理",tag:"局部最优即全局 · 区间合并调度",items:[
      {sig:"区间调度、分发糖果、跳跃游戏、加油站、每步取当下最优",algo:"贪心",tip:"必须能论证“每步取局部最优不会更差”才敢用；证不出来就退回 DP。",href:"greedy.html"},
      {sig:"合并 / 插入 / 求交集重叠区间、会议室安排",algo:"区间处理（排序 + 扫描）",tip:"先按起点或终点排序，再一遍扫描合并/贪心选。",href:"intervals.html"}
    ]},
    {icon:"🔤",title:"字符串专项",tag:"模式匹配 · 回文",items:[
      {sig:"在长文本里找模式串出现的位置 / 次数",algo:"KMP / Z 函数 / Rabin-Karp",tip:"暴力 O(nm)；KMP 用 next 数组把匹配失败的回退省掉，做到 O(n+m)。",href:"string-matching.html"},
      {sig:"最长回文子串 / 回文子串计数",algo:"中心扩展 / Manacher",tip:"中心扩展 O(n²) 够用；要 O(n) 上 Manacher。",href:"manacher-palindrome.html"}
    ]},
    {icon:"🧮",title:"数学 / 位运算",tag:"位技巧 · 数论",items:[
      {sig:"只出现一次的数、子集枚举、判 2 的幂、状态压缩",algo:"位运算",tip:"异或消重、lowbit、n&(n-1) 去最低位 1 等技巧。",href:"bit-manipulation.html"},
      {sig:"快速幂、质数筛、gcd/lcm、大数取模、组合数",algo:"数学算法",tip:"a^b mod p 用快速幂；批量质数用埃氏筛/线性筛。",href:"math-algorithms.html"},
      {sig:"模逆元、扩展欧几里得、中国剩余定理、大质数判定/分解",algo:"数论算法",tip:"进阶数论：逆元、CRT、Miller-Rabin、Pollard's rho。",href:"number-theory-algorithms.html"}
    ]}
  ];

  var CHIPS=["相邻不能选","最长子序列","最小化最大值","连续子数组","下一个更大","第k大","所有方案","方案数","最少步数","区间合并","背包","最短路","前缀和","回文"];

  var tree=document.getElementById("amap-tree");
  var input=document.getElementById("amap-q");
  var countEl=document.getElementById("amap-count");
  var chipsEl=document.getElementById("amap-chips");
  var cats=[];

  function esc(s){return s.replace(/[&<>]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;"}[c];});}
  function hl(text,q){
    if(!q)return esc(text);
    var i=text.toLowerCase().indexOf(q);
    if(i<0)return esc(text);
    return esc(text.slice(0,i))+"<mark>"+esc(text.slice(i,i+q.length))+"</mark>"+esc(text.slice(i+q.length));
  }

  DATA.forEach(function(cat){
    var catEl=document.createElement("div");catEl.className="amap-cat";
    var head=document.createElement("div");head.className="amap-cathead";
    head.innerHTML='<span class="amap-arrow">▶</span><span class="amap-cat-icon">'+cat.icon+
      '</span><span class="amap-cat-title">'+esc(cat.title)+'</span><span class="amap-cat-tag">'+esc(cat.tag)+
      '</span><span class="amap-cat-n">'+cat.items.length+'</span>';
    var body=document.createElement("div");body.className="amap-catbody";
    var itemEls=cat.items.map(function(it){
      var el=document.createElement("div");el.className="amap-item";
      el.innerHTML='<div class="amap-sig">'+esc(it.sig)+'</div>'+
        '<div class="amap-algo">'+esc(it.algo)+'</div>'+
        (it.tip?'<div class="amap-tip">'+esc(it.tip)+'</div>':'')+
        '<a class="amap-link" href="'+it.href+'">查看笔记 ↗</a>';
      body.appendChild(el);
      return el;
    });
    head.addEventListener("click",function(){catEl.classList.toggle("open");});
    catEl.appendChild(head);catEl.appendChild(body);tree.appendChild(catEl);
    cats.push({data:cat,el:catEl,head:head,itemEls:itemEls});
  });

  function render(q){
    q=(q||"").trim().toLowerCase();
    var shown=0;
    cats.forEach(function(c){
      var any=false;
      c.itemEls.forEach(function(el,i){
        var it=c.data.items[i];
        var hay=(it.sig+" "+it.algo+" "+(it.tip||"")+" "+c.data.title).toLowerCase();
        var m=!q||hay.indexOf(q)>-1;
        el.style.display=m?"":"none";
        if(m){any=true;shown++;
          el.querySelector(".amap-sig").innerHTML=hl(it.sig,q);
          el.querySelector(".amap-algo").innerHTML=hl(it.algo,q);
          var tipEl=el.querySelector(".amap-tip");if(tipEl&&it.tip)tipEl.innerHTML=hl(it.tip,q);
        }
      });
      c.el.style.display=any?"":"none";
      if(q)c.el.classList.toggle("open",any);
      else c.el.classList.remove("open");
    });
    var old=tree.querySelector(".amap-empty");if(old)old.remove();
    if(shown===0){var e=document.createElement("div");e.className="amap-empty";
      e.textContent="没匹配到「"+q+"」。换个说法试试，或点上面的常见特征词。";tree.appendChild(e);}
    countEl.textContent=q?("命中 "+shown+" 条"):"";
  }

  CHIPS.forEach(function(w){
    var b=document.createElement("span");b.className="amap-chip";b.textContent=w;
    b.addEventListener("click",function(){input.value=w;render(w);input.focus();});
    chipsEl.appendChild(b);
  });

  input.addEventListener("input",function(){render(input.value);});
  document.getElementById("amap-expand").addEventListener("click",function(){cats.forEach(function(c){if(c.el.style.display!=="none")c.el.classList.add("open");});});
  document.getElementById("amap-collapse").addEventListener("click",function(){cats.forEach(function(c){c.el.classList.remove("open");});});

  render("");
})();
</script>

---

## 那些“想不到用 DP”的题，长什么样

初学者最容易卡在**认不出 DP** 上。下面这些**外表不像 DP** 的题，其实全是 DP，记住它们的"伪装"：

| 题面读起来像… | 真实身份 | 落到哪一种 | 笔记 |
|---|---|---|---|
| “偷不相邻的房子，求最多偷多少”(LC198) | **DP** 不是贪心 | 线性 DP | [house-robber.md](house-robber.md) |
| “最长的递增子序列有多长”(LC300) | **DP** 不是双指针 | 子序列 DP · LIS | [subsequence-problems.md](subsequence-problems.md) |
| “两个字符串最少改几步能相等” | **DP** 不是模拟 | 编辑距离 | [subsequence-problems.md](subsequence-problems.md) |
| “硬币凑金额有几种凑法” | **DP** 不是回溯枚举 | 完全背包 | [knapsack.md](knapsack.md) |
| “数组能不能平分成两半和相等” | **DP** 不是排序 | 0-1 背包可行性 | [knapsack.md](knapsack.md) |
| “最多买卖 k 次股票的最大利润” | **DP** 不是贪心 | 状态机 DP | [stock-trading.md](stock-trading.md) |
| “戳破所有气球的最大得分” | **DP** 不是回溯 | 区间 DP | [interval-dp.md](interval-dp.md) |
| “从左上走到右下有几条路” | **DP** 不是排列组合硬算 | 二维网格 DP | [dp-framework.md](dp-framework.md) |

**共同信号**：题目在求「**最大/最小/多少种/能不能**」，而每一步都在做「**选或不选、选哪个**」的决策——一旦发现暴力枚举会指数级爆炸且子情况重复，就该上 DP，再用上面的地图定位到**具体是哪一种 DP**。

---

## 相关笔记

- DP 通用框架与调试：[dp-framework.md](dp-framework.md)、[dp-basics.md](dp-basics.md)
- 按《算法导论》章节找算法：[clrs-index.md](clrs-index.md)
- 按专题刷题：[leetcode-hot100.md](leetcode-hot100.md)
- 返回目录：[index.md](index.md)
