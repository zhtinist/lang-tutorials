# STL 容器详解

> STL（Standard Template Library）容器是 C++ 里最常用的部分，面试和实际开发里出现频率最高。
> 本章按"序列容器 → 容器适配器 → 关联容器 → 无序容器"的顺序，逐个过一遍：怎么用、底层怎么实现、复杂度多少、什么时候选它。

---

## 一、容器总览

| 容器 | 底层结构 | 有序性 | 随机访问 | 典型场景 |
|------|---------|--------|:---:|---------|
| `vector` | 连续内存数组 | 插入顺序 | O(1) | 默认首选容器 |
| `deque` | 分段连续内存 | 插入顺序 | O(1) | 两端频繁增删 |
| `list` | 双向链表 | 插入顺序 | ❌ | 中间频繁增删 |
| `forward_list` | 单向链表 | 插入顺序 | ❌ | 极致省内存的单向遍历 |
| `stack`/`queue`/`priority_queue` | 容器适配器（默认基于 `deque`） | — | — | LIFO/FIFO/堆 |
| `array` | 定长数组（栈上） | 插入顺序 | O(1) | 编译期已知大小的数组 |
| `map`/`set` | 红黑树 | 按 key 排序 | ❌ | 需要有序遍历/范围查询 |
| `multimap`/`multiset` | 红黑树 | 按 key 排序 | ❌ | key 允许重复 |
| `unordered_map`/`unordered_set` | 哈希表 | 无序 | ❌ | 只要 O(1) 查找，不关心顺序 |

---

## 二、`vector`：默认首选容器

```cpp
#include <vector>
using namespace std;

vector<int> v = {1, 2, 3};
v.push_back(4);       // 尾部插入，均摊 O(1)
v.emplace_back(5);    // 原地构造，避免一次拷贝/移动（对自定义对象更明显）
v.insert(v.begin() + 1, 99); // 任意位置插入 O(n)（要搬移后面的元素）
v.erase(v.begin());          // 任意位置删除 O(n)
v.front(); v.back();         // O(1) 访问首尾
v[2]; v.at(2);                // [] 不做越界检查，at() 越界抛 std::out_of_range
```

### 2.1 扩容机制

```
push_back 到容量满时触发扩容：分配一块更大的内存（通常 ×2），
把旧元素全部拷贝/移动过去，释放旧内存。
均摊分析：n 次 push_back 的总拷贝次数 < 2n，所以均摊 O(1)（详见 algo-notes/amortized-analysis.md）。

reserve(n)：预分配至少 n 个元素的容量，不改变 size。提前知道大概要装多少元素时应该用它，
           避免反复触发扩容拷贝。
resize(n)：改变 size（n > 当前size 时用默认值填充新元素，n < 当前size 时截断），可能改变 capacity。
size()：当前元素个数。capacity()：当前分配的容量，size() <= capacity()。
```

实测扩容序列（libc++，翻倍策略）：

```cpp
vector<int> v2;
for (int i = 0; i < 20; i++) v2.push_back(i);
// size/capacity 变化: 1/1 2/2 3/4 4/4 5/8 6/8 7/8 8/8 9/16 ... 16/16 17/32 ... 20/32
```

> 不同标准库实现的扩容因子不同：libstdc++（GCC）是 2 倍，libc++（Clang/macOS）也是 2 倍，
> MSVC 是 1.5 倍——不要依赖具体数值，只依赖"均摊 O(1)"这个复杂度结论。

### 2.2 迭代器失效

```
会让 vector 的迭代器失效的操作：
  - push_back/insert 触发扩容 → 所有迭代器、指针、引用全部失效（内存搬了家）
  - push_back/insert 没触发扩容 → 插入点之后的迭代器失效（元素被后移了）
  - erase → 删除点之后的迭代器失效

安全删除写法（erase 返回下一个有效迭代器）：
```

```cpp
vector<int> v = {1,2,3,4,5,6};
for (auto it = v.begin(); it != v.end(); ) {
    if (*it % 2 == 0) it = v.erase(it);  // 用返回值更新 it，不要 ++it
    else ++it;
}
// v = {1, 3, 5}
```

> **常见坑**：`for (auto it = v.begin(); it != v.end(); ++it) { if(cond) v.erase(it); }`
> —— erase 之后 it 已经失效，再 ++it 是未定义行为。正确写法必须用 erase 的返回值。

---

## 三、`deque`：双端队列

```cpp
#include <deque>
deque<int> dq = {2,3,4};
dq.push_front(1);   // 头部插入 O(1)（vector 做不到）
dq.push_back(5);    // 尾部插入 O(1)
dq[2];               // 支持随机访问 O(1)，但比 vector 稍慢（多一次间接寻址）
```

```
底层是"分段连续内存"：一个中控数组(map)，每个元素指向一段固定大小的连续内存块(buffer)。
这样两端都能 O(1) 扩展（只需要在中控数组两端加新的buffer块，不需要整体搬移），
但也因此不是完全连续内存，随机访问比 vector 多一次间接寻址（先定位buffer，再定位buffer内偏移）。

std::stack 和 std::queue 默认就是基于 deque 实现的容器适配器。
```

---

## 四、`list` / `forward_list`：链表

```cpp
#include <list>
list<int> lst = {1,2,3};
lst.push_front(0);
lst.push_back(4);
auto it = lst.begin();
advance(it, 2);
lst.insert(it, 99);  // 已知迭代器位置时，插入/删除是 O(1)（只改指针，不搬移元素）
```

```
list：双向链表，insert/erase 在已知位置时是 O(1)，但没有随机访问（it+n 需要 O(n) 遍历）。
forward_list：单向链表，比 list 省一个 prev 指针的内存，只能单向遍历，C++11 引入，
              专门为了"极致省内存"的场景设计（比如实现哈希表的桶链表）。

vector vs list 怎么选：
  绝大多数场景选 vector（缓存局部性好，连续内存对现代 CPU 更友好）；
  只有"频繁在中间/头部插入删除，且不需要随机访问"时才考虑 list。
```

---

## 五、容器适配器：`stack` / `queue` / `priority_queue`

```cpp
#include <stack>
#include <queue>

stack<int> st;
st.push(1); st.push(2); st.push(3);
st.top();  // 3
st.pop();  // 弹出，无返回值（和 vector 的 pop_back 语义一致：分离了"看"和"弹"）

queue<int> q;
q.push(1); q.push(2); q.push(3);
q.front(); q.back();  // 1, 3
q.pop();  // 弹出队首

priority_queue<int> pq;             // 默认大顶堆
pq.push(3); pq.push(1); pq.push(4);
pq.top();  // 4（当前最大值）

priority_queue<int, vector<int>, greater<int>> minpq;  // 小顶堆写法
```

> `stack`/`queue`/`priority_queue` 不是独立的数据结构，是"容器适配器"——
> 内部包一个真正的容器（默认 `deque`，`priority_queue` 默认 `vector`），只暴露一部分接口。
> 这也是为什么它们没有迭代器：适配器的设计意图就是"只能按固定方式访问"（栈顶/队首/堆顶）。

---

## 六、`map` / `set`：有序关联容器（红黑树）

```cpp
#include <map>
map<string,int> m;
m["a"] = 1;                    // [] 找不到 key 时会插入一个默认值（这是常见的坑！）
m.insert({"b", 2});
for (auto& [k, v] : m) { /* 按 key 字典序遍历 */ }

auto it = m.find("a");         // O(log n)，找不到返回 m.end()
if (m.count("x") == 0) { /* "x" 不存在 */ }  // map 的 count 只会是 0 或 1
```

```cpp
#include <set>
set<int> s = {5,3,1,4,1,5,9,2,6};
// 遍历结果自动有序去重: 1 2 3 4 5 6 9
```

```
map/set 底层是红黑树（近似平衡二叉搜索树，见 algo-notes/red-black-tree.md），
所有操作 O(log n)：插入、删除、查找。中序遍历天然有序，这是它相对哈希表最大的优势——
需要"按 key 排序遍历"或者"范围查询"（lower_bound/upper_bound 找区间）时必须用它。

⚠️ m["key"] 的坑：如果 key 不存在，[] 会自动插入一个 value 默认构造的新元素再返回引用。
   只是"查询是否存在"时不要用 []，要用 find() 或 count()，否则会意外插入垃圾数据、
   还会让 map 的 size() 变大。
```

`multimap`/`multiset` 是允许 key 重复的版本：

```cpp
multimap<string,int> mm;
mm.insert({"a", 1});
mm.insert({"a", 2});
mm.count("a");  // 2（不再只是 0/1）
```

---

## 七、`unordered_map` / `unordered_set`：哈希表

```cpp
#include <unordered_map>
unordered_map<string,int> um;
um["x"] = 10;
um["y"] = 20;
// 遍历顺序不保证（取决于哈希桶布局），平均 O(1) 增删查
um.load_factor();  // 当前负载因子 = size / bucket_count
```

```
底层是哈希表（拉链法，详见 algo-notes/hash-table-implementation.md），
平均情况 O(1)，最坏情况（哈希冲突严重）O(n)。

map vs unordered_map 怎么选：
  只要 O(1) 平均查找、不关心顺序 -> unordered_map（更快）
  需要有序遍历、范围查询（比如"找所有大于x的key"）-> map
  key 类型是自定义类型时，unordered_map 需要提供哈希函数（std::hash 特化或传自定义 hasher），
  map 只需要 < 运算符（或自定义 comparator），后者通常更省事。
```

---

## 八、`pair` / `tuple` / `array`：轻量组合类型

```cpp
pair<int,string> p = {1, "one"};
p.first; p.second;

tuple<int,string,double> t = {1, "two", 3.0};
get<0>(t); get<1>(t); get<2>(t);
auto [a, b, c] = t;  // C++17 结构化绑定，比 get<N> 可读得多

array<int, 5> arr = {1,2,3,4,5};  // 编译期定长数组，栈上分配，比裸数组多了 size()/迭代器等接口
```

---

## 九、复杂度速查表

| 操作 | vector | deque | list | map/set | unordered_map/set |
|------|:---:|:---:|:---:|:---:|:---:|
| 随机访问 `[i]` | O(1) | O(1) | ❌ | ❌ | ❌ |
| 头部插入 | O(n) | O(1) | O(1) | — | — |
| 尾部插入 | 均摊O(1) | O(1) | O(1) | — | — |
| 中间插入（已知迭代器） | O(n) | O(n) | O(1) | — | — |
| 插入（按 key） | — | — | — | O(log n) | 平均O(1) |
| 查找（按 key/值） | O(n) | O(n) | O(n) | O(log n) | 平均O(1) |
| 删除 | O(n) | O(n) | O(1) | O(log n) | 平均O(1) |

---

## 十、容器选择决策树

```
需要按下标随机访问？
  是 -> 需要频繁在两端插入删除？
          是 -> deque
          否 -> vector（默认首选）
  否 -> 需要 key-value 或去重？
          是 -> 需要有序/范围查询？
                  是 -> map / set
                  否 -> unordered_map / unordered_set（更快）
          否 -> 需要在中间频繁插入删除？
                  是 -> list
                  否 -> vector（大多数"序列"场景 vector 仍然是最优默认选择）
```

---

[← 返回索引](index.md)
