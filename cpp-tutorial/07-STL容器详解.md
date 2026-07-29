# STL 容器详解

> STL（Standard Template Library）容器是 C++ 里最常用的部分，面试和实际开发里出现频率最高。
> 本章按"序列容器 → 容器适配器 → 关联容器 → 无序容器 → 字符串"的顺序，逐个过一遍：
> 怎么用、常用成员函数（尤其是查找）、底层怎么实现、复杂度多少、什么时候选它。

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
| `string` | 连续字符数组（本质是特化的 vector<char>） | 插入顺序 | O(1) | 文本处理 |

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

### 2.1 常用成员函数一览

```cpp
vector<int> v = {1,2,3};
v.empty();          // 是否为空
v.size();           // 元素个数
v.clear();          // 清空所有元素（size变0，capacity通常不变）
v.assign(5, 7);      // 重新赋值成5个7：{7,7,7,7,7}
vector<int> v2 = {9,9,9};
v.swap(v2);          // O(1)，只交换内部指针，不拷贝元素
int* p = v.data();   // 拿到底层连续内存的裸指针（C 接口交互常用）
```

### 2.2 查找元素

> **`vector` 没有成员函数 `.find()`**——这是新手最容易漏掉的一点：`vector` 只是连续数组，
> 查找必须用 `<algorithm>` 里的通用算法（见 [08-STL算法与迭代器.md](08-STL算法与迭代器.md)）。

```cpp
#include <algorithm>

vector<int> v = {10,20,30,40};
auto it = find(v.begin(), v.end(), 30);
bool exists = (it != v.end());
int index = it - v.begin();  // 用迭代器减法拿到下标
cout << exists << " " << index << endl;  // 1 2

auto it2 = find_if(v.begin(), v.end(), [](int x){ return x > 25; }); // 按条件查找第一个满足的
```

### 2.3 扩容机制

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

### 2.4 迭代器失效

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

### 2.5 底层实现：三个指针、扩容因子与移动语义的取舍

`vector` 内部本质上只是三个指针（以 libstdc++ 为例，`_M_start`/`_M_finish`/`_M_end_of_storage`，不同实现叫法不同但结构通用）：

```
[a][b][c][d][_][_][_]
 ^                  ^
start        end_of_storage
        ^
     finish（size() = finish - start，capacity() = end_of_storage - start）
```

`push_back` 遇到 `finish == end_of_storage` 时触发扩容，过程固定四步：分配一块更大的新内存 → 把旧元素逐个搬到新内存（拷贝或移动，见下）→ 析构旧内存里的对象、释放旧内存 → 三个指针重新指向新内存。

增长因子标准不做规定，由实现自行选择：libstdc++（GCC）和 libc++（Clang）用 2 倍，MSVC 用 1.5 倍。选指数增长而不是固定步长（每次只多分配 k 个）是均摊复杂度的直接要求——固定步长下 n 次 push_back 的总拷贝量是 O(n²/k)，均摊到每次是 O(n)；指数增长让总拷贝量收敛成几何级数 O(n)，均摊到每次是 O(1)。1.5 倍与 2 倍是空间和时间的具体权衡：因子越小扩容越频繁但峰值浪费的内存越少，这也是为什么"倍数具体是多少"从来不是语言标准强制的内容——它是实现可以自由调节的性能旋钮，而不是复杂度承诺的一部分。

扩容时"拷贝还是移动"背后有一层容易被忽略的正确性考量。如果元素类型的移动构造函数标了 `noexcept`，vector 扩容会优先用移动（把旧元素"倒"进新内存，不做深拷贝）；但如果移动构造函数**可能抛异常**且该类型同时提供了拷贝构造函数，vector 会退回去做拷贝。原因是异常安全：扩容做到一半抛出异常，拷贝路径下原始数据完好无损、可以安全回滚；移动却是破坏性操作——元素一旦被移动走，原对象就处于被掏空的状态，无法恢复。为了保证"扩容失败不破坏原数据"这个强异常安全保证，标准要求这里用 `std::move_if_noexcept`，只有移动构造函数确定不抛异常（或者这个类型压根没有拷贝构造函数可退）时才允许移动：

```cpp
struct RiskyMove {
    RiskyMove(const RiskyMove&) { /* 拷贝构造 */ }
    RiskyMove(RiskyMove&&) { /* 没标 noexcept，可能抛异常 */ }
};
struct SafeMove {
    SafeMove(const SafeMove&) { /* 拷贝构造 */ }
    SafeMove(SafeMove&&) noexcept { /* 明确承诺不抛异常 */ }
};

std::vector<RiskyMove> v1;  // 扩容时静默退化成拷贝，即使写了移动构造函数
std::vector<SafeMove>  v2;  // 扩容时才会真正用移动
```

这就是为什么自定义类型的移动构造函数应当尽量标 `noexcept`——不标的话，vector 扩容时会静默地退化成更慢的拷贝路径，编译器不会给任何警告。

内存收缩上，C++11 提供的 `shrink_to_fit()` 只是一个**非强制请求**，标准允许实现忽略它；更保险的写法是经典的 swap 技巧：

```cpp
std::vector<int> v;
// ... v 曾经很大，现在只剩少量元素，capacity() 远大于 size() ...
std::vector<int>(v).swap(v);  // 拷贝构造一个刚好等于当前 size 的临时 vector，交换后临时对象析构释放旧内存
```

---

## 三、`deque`：双端队列

```cpp
#include <deque>
deque<int> dq = {2,3,4};
dq.push_front(1);   // 头部插入 O(1)（vector 做不到）
dq.push_back(5);    // 尾部插入 O(1)
dq[2];               // 支持随机访问 O(1)，但比 vector 稍慢（多一次间接寻址）

dq.pop_front();      // 头部删除 O(1)
dq.pop_back();       // 尾部删除 O(1)
dq.empty(); dq.size(); dq.clear();  // 和 vector 用法一致
```

> **查找**：`deque` 同样没有成员 `.find()`，跟 `vector` 一样要用 `std::find`（要求随机访问迭代器，`deque` 满足）。

```
底层是"分段连续内存"：一个中控数组(map)，每个元素指向一段固定大小的连续内存块(buffer)。
这样两端都能 O(1) 扩展（只需要在中控数组两端加新的buffer块，不需要整体搬移），
但也因此不是完全连续内存，随机访问比 vector 多一次间接寻址（先定位buffer，再定位buffer内偏移）。

std::stack 和 std::queue 默认就是基于 deque 实现的容器适配器。
```

### 3.1 分段连续的实现细节

`deque` 的中控数组（部分实现称为 `map`，注意和关联容器 `std::map` 是两回事）本身是一段连续内存，里面存的是若干个指向"定长缓冲区块"的指针，每个块内部才是真正连续存放元素的地方：

```
中控数组(连续，存指向各缓冲区块的指针):
        ┌────┬────┬────┬────┬────┐
        │ p0 │ p1 │ p2 │ p3 │ p4 │
        └─┬──┴─┬──┴─┬──┴────┴────┘
          v     v     v
        ┌────┐┌────┐┌────┐
        │abcd││efgh││ijkl│   ← 每个块内部连续
        └────┘└────┘└────┘
```

libstdc++ 里定长块的大小不是固定字节数，而是按元素大小反推：`sizeof(T) < 512` 时一块能装 `512 / sizeof(T)` 个元素，`sizeof(T) >= 512` 时一块只装 1 个元素（退化情况）。块大小与"两端 O(1) 插入"的关系是：块写满时不需要移动已有元素，只需要在中控数组末尾/开头追加一个新块的指针（中控数组本身满了才需要扩容，但那时只搬指针不搬元素，代价很小）。随机访问 `dq[i]` 需要两步定位：`块索引 = (i + 起始偏移) / 块大小`，`块内偏移 = (i + 起始偏移) % 块大小`——这正是 deque 随机访问比 vector 多一次间接寻址的原因。

deque 的迭代器因此不是普通指针，它需要同时持有"当前元素指针、当前块的起止位置、指向中控数组对应槽位的指针"这几项信息，才能在走到块边界时知道该跳到哪个新块。这也是为什么 deque 迭代器比 vector 迭代器"重"得多——解引用和自增的常数开销更大，即使复杂度标注都是 O(1)。

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
lst.pop_front(); lst.pop_back();
lst.empty(); lst.size(); lst.clear();
```

### 4.1 list 独有的成员函数（不能用通用算法替代）

> `list` 的迭代器只是双向迭代器（不支持随机访问），所以 `std::sort`/`std::unique` 这些要求
> 随机访问迭代器的通用算法**用不了**——`list` 因此自带了一套同名但更高效的成员函数版本：

```cpp
list<int> lst = {5,3,1,4,1,5,9,2,6};
lst.sort();            // list 自己的排序（基于链表节点重排指针，不是随机访问版的快排）
// {1,1,2,3,4,5,5,6,9}

lst.unique();           // 去除相邻重复，直接修改容器，不需要像 vector 那样配合 erase
// {1,2,3,4,5,6,9}

lst.remove(9);          // 删除所有等于 9 的元素（比 remove_if + erase 更直接）
// {1,2,3,4,5,6}

lst.remove_if([](int x){ return x % 2 == 0; }); // 条件删除
// {1,3,5}

list<int> a = {100, 200}, b = {1,2,3};
b.splice(b.begin(), a);  // O(1)：把 a 的所有节点整体接到 b 开头（只改指针，不拷贝元素）
// b = {100,200,1,2,3}，a 变空
```

```
forward_list：单向链表，比 list 省一个 prev 指针的内存，只能单向遍历，C++11 引入，
              专门为了"极致省内存"的场景设计（比如实现哈希表的桶链表），
              同样有自己的 sort()/unique()/remove()/splice_after() 等成员函数。

vector vs list 怎么选：
  绝大多数场景选 vector（缓存局部性好，连续内存对现代 CPU 更友好）；
  只有"频繁在中间/头部插入删除，且不需要随机访问"时才考虑 list。
```

### 4.2 双向链表的哨兵节点实现

libstdc++ 的 `list` 是**带哨兵节点的循环双向链表**：多分配一个不存有效数据的哨兵节点，`end()` 返回的迭代器指向它，链表首尾通过它连接成环：

```
[sentinel] <-> [a] <-> [b] <-> [c] <-> 回到 sentinel
      ^
      └── begin() 指向 a，end() 指向 sentinel
```

哨兵节点存在的理由是消除边界分支：如果没有它，`begin()`/`end()`、头插/尾插都需要对"链表是否为空"单独判断；有了哨兵，所有插入统一处理成"在某节点前插入一个新节点"，空链表只是"哨兵指向自己"这一种特殊情形，不需要任何 if 分支。

`forward_list` 省掉了每个节点的前驱指针，内存更省，但只能单向遍历——标准干脆没有为它定义 `size()` 成员，因为要维护一个 O(1) 的 `size()` 就必须在每次插入删除时额外维护一个计数器，这与 `forward_list`"极致省内存、不为用不到的功能付费"的设计目标冲突；需要长度就只能自己 `std::distance(begin(), end())`，代价是 O(n)。

---

## 五、容器适配器：`stack` / `queue` / `priority_queue`

```cpp
#include <stack>
#include <queue>

stack<int> st;
st.push(1); st.push(2); st.push(3);
st.top();  // 3
st.pop();  // 弹出，无返回值（和 vector 的 pop_back 语义一致：分离了"看"和"弹"）
st.empty(); st.size();

queue<int> q;
q.push(1); q.push(2); q.push(3);
q.front(); q.back();  // 1, 3
q.pop();  // 弹出队首
q.empty(); q.size();

priority_queue<int> pq;             // 默认大顶堆
pq.push(3); pq.push(1); pq.push(4);
pq.top();  // 4（当前最大值）
pq.empty(); pq.size();

priority_queue<int, vector<int>, greater<int>> minpq;  // 小顶堆写法
```

> `stack`/`queue`/`priority_queue` 不是独立的数据结构，是"容器适配器"——
> 内部包一个真正的容器（默认 `deque`，`priority_queue` 默认 `vector`），只暴露一部分接口。
> 这也是为什么它们没有迭代器、也没有 `find()`：适配器的设计意图就是"只能按固定方式访问"（栈顶/队首/堆顶），
> 如果需要在里面查找任意元素，说明这个场景本来就不该用适配器，应该直接用底层容器。

---

## 六、`array`：定长数组

```cpp
#include <array>
array<int, 5> arr = {1,2,3,4,5};  // 编译期定长数组，栈上分配，比裸数组多了 size()/迭代器等接口
arr.size();          // 5（固定不变）
arr.at(2);           // 带边界检查的访问
arr.data();          // 拿到底层裸指针
arr.fill(7);         // 把所有元素都设成同一个值：{7,7,7,7,7}
```

> **查找**：`array` 同样没有 `.find()`，跟 `vector` 一样用 `std::find(arr.begin(), arr.end(), val)`。

---

## 七、`map` / `set`：有序关联容器（红黑树）

```cpp
#include <map>
map<string,int> m;
m["a"] = 1;                    // [] 找不到 key 时会插入一个默认值（这是常见的坑！）
m.insert({"b", 2});
m.emplace("c", 3);             // 原地构造，避免临时 pair 对象
for (auto& [k, v] : m) { /* 按 key 字典序遍历 */ }
```

### 7.1 查找与存在性判断

```cpp
map<string,int> m = {{"a",1},{"b",2},{"c",3}};

// 方式一：contains()（C++20，最推荐，语义最直观）
if (m.contains("a")) { /* ... */ }

// 方式二：find()，找到时可以顺手拿到 value，找不到返回 end()
auto it = m.find("b");
if (it != m.end()) cout << it->second;

// 方式三：count()，map/set 的 count 只会是 0 或 1（因为 key 唯一）
if (m.count("x") == 0) { /* 不存在 */ }

// ⚠️ 不要用 m["key"] 来判断是否存在！找不到时 [] 会自动插入一个默认值再返回引用，
//    副作用是让 size() 变大、还塞进了一条垃圾数据。
```

### 7.2 范围查询：`lower_bound` / `upper_bound` / `equal_range`

```cpp
map<int,string> m2 = {{1,"a"},{3,"b"},{5,"c"},{7,"d"}};
auto lb = m2.lower_bound(4);   // 第一个 key >= 4 的位置 -> key=5
auto ub = m2.upper_bound(4);   // 第一个 key >  4 的位置 -> key=5（4本身不存在，两者相同）
cout << lb->first << " " << ub->first << endl;
```

### 7.3 删除

```cpp
map<string,int> m = {{"a",1},{"b",2}};
m.erase("a");            // 按 key 删除，返回删除的个数（map里是0或1）
auto it = m.find("b");
if (it != m.end()) m.erase(it);  // 按迭代器删除，O(1)（已经定位到节点，不用再搜一次）
```

```
map/set 底层是红黑树（近似平衡二叉搜索树，见 algo-notes/red-black-tree.md），
所有操作 O(log n)：插入、删除、查找。中序遍历天然有序，这是它相对哈希表最大的优势——
需要"按 key 排序遍历"或者"范围查询"时必须用它。
```

`set` 的查找接口和 `map` 完全对应（只是没有 value，只判断 key 存在与否）：

```cpp
#include <set>
set<int> s = {5,3,1,4,1,5,9,2,6};
// 遍历结果自动有序去重: 1 2 3 4 5 6 9
s.contains(4);   // C++20
s.count(4);      // 0 或 1
s.find(4) != s.end();
```

### 7.4 `multimap` / `multiset`：允许 key 重复

```cpp
multimap<string,int> mm = {{"a",1},{"a",2},{"a",3},{"b",4}};
mm.count("a");   // 3（不再只是 0/1，因为可以重复）

// 取出某个 key 的所有值：equal_range 一次拿到 [lower_bound, upper_bound) 整个区间
auto [lo, hi] = mm.equal_range("a");
for (auto it = lo; it != hi; ++it) cout << it->second << " ";
// 输出: 1 2 3
```

### 7.5 红黑树实现细节

`map`/`set` 底层是红黑树——一种通过给节点染色（红/黑）维护平衡的二叉搜索树，核心规则：根节点是黑色；红色节点的两个子节点必须是黑色（不允许两个红色节点相邻）；从任一节点到其所有后代空叶子节点的路径上，经过的黑色节点数目相同（黑高一致）。这几条规则联合起来保证树中最长路径不超过最短路径的 2 倍，由此推出树高上界是 O(log n)。插入、删除、查找因此都稳定在 O(log n)——不像哈希表那样区分"平均 O(1)、最坏 O(n)"，红黑树的最坏情况就是它的平均情况，这正是它被选为 `map` 底层结构而非哈希表的原因之一：关联容器的语义承诺是稳定、可预测的复杂度，而不是追求最快的平均速度。

`map` 节点内部存的是 `pair<const Key, Value>`——key 部分是 `const`，即便拿到指向元素的引用也不能修改 key（改了 key 会破坏树的有序性），只能通过 `it->second` 修改 value。`set` 本质上是"只存 key、没有 value"的红黑树，libstdc++ 里 `map` 和 `set` 共享同一套红黑树模板，`map` 只是把每个节点的数据类型定成了 `pair<const Key, Value>`。

删除节点时只有被删除的那个节点对应的迭代器失效，其余节点的迭代器全部保持有效——这是所有基于节点、指针链接的数据结构的通性：节点一旦分配，内存地址在其生命周期内不会因为树的旋转、重新平衡而改变，红黑树的"旋转"调整的是指针指向关系，而不是搬移节点本身。插入同理不会使已有迭代器失效，因为插入只是新增指针链接，不触碰已有节点的地址。

---

## 八、`unordered_map` / `unordered_set`：哈希表

```cpp
#include <unordered_map>
unordered_map<string,int> um;
um["x"] = 10;
um["y"] = 20;
// 遍历顺序不保证（取决于哈希桶布局），平均 O(1) 增删查
um.load_factor();  // 当前负载因子 = size / bucket_count
```

### 8.1 查找与删除（接口和 map 完全一致，只是没有顺序）

```cpp
unordered_map<string,int> um = {{"x",1},{"y",2}};
um.contains("x");                       // C++20
um.find("y") != um.end();
um.count("x");                          // 0 或 1
um.erase("x");                          // 按 key 删除

unordered_set<int> us = {1,2,3};
us.contains(2);
```

```
底层是哈希表（拉链法，详见 algo-notes/hash-table-implementation.md），
平均情况 O(1)，最坏情况（哈希冲突严重）O(n)。

map vs unordered_map 怎么选：
  只要 O(1) 平均查找、不关心顺序 -> unordered_map（更快）
  需要有序遍历、范围查询（比如"找所有大于x的key"）-> map（unordered_map 没有 lower_bound/upper_bound）
  key 类型是自定义类型时，unordered_map 需要提供哈希函数（std::hash 特化或传自定义 hasher），
  map 只需要 < 运算符（或自定义 comparator），后者通常更省事。
```

### 8.2 哈希表实现与 rehash 机制

`unordered_map` 底层是"桶数组（bucket array）+ 处理哈希冲突的链表"。插入一个 key 时，先算出 `hash(key)`，对桶数量取模得到桶下标，把新节点挂到该桶对应的链表里；查找同样先定位桶，再在桶内链表线性比较。

libstdc++ 有一处值得单独一提的实现细节：它不是每个桶各自维护一条独立链表，而是把**所有元素**串成一条全局单链表，桶数组里存的只是"指向该桶第一个节点前驱位置"的指针，用来标记桶的边界。这样设计的好处是遍历整个 `unordered_map` 可以直接沿着这条全局链表走一遍、严格 O(n)，不需要跳过大量空桶——如果每个桶单独维护链表，遍历退化情况下要访问所有桶（哪怕大部分是空的）才能收集到全部元素。这是标准没有强制规定、但主流实现出于遍历效率做的优化。

**负载因子**：`load_factor() = size() / bucket_count()`，标准默认的 `max_load_factor()` 是 **1.0**；作为对比，Java `HashMap` 默认是 0.75。两者都是空间和时间的具体权衡点，0.75 更倾向牺牲内存换更少冲突，1.0 更倾向节省内存，不存在谁对谁错。

**rehash 触发与过程**：每次插入后，如果 `load_factor() > max_load_factor()`，自动触发 rehash：分配一个更大的新桶数组（通常约为原来的 2 倍，并向上取整到下一个质数，用质数做桶数是为了让 `hash % bucket_count` 的分布更均匀，减少某些哈希函数在特定桶数下的规律性碰撞）→ 遍历旧数据每个节点，重新计算 `hash(key) % new_bucket_count`，把节点摘下来挂到新桶 → 释放旧桶数组。整个过程是 O(n)，n 是当前元素总数——这正是为什么 `unordered_map` 插入被称为"均摊 O(1)"而不是严格 O(1)：绝大多数插入只是简单的链表头插，只有触发 rehash 的那一次插入需要付出 O(n) 的代价，均摊下来仍是常数。

**rehash 前后迭代器与引用/指针的失效情况不同**：rehash 会让**所有迭代器失效**（桶数组本身被替换成新的一份，迭代器内部记录的桶位置信息全部作废），但**指向元素的引用和指针仍然有效**——`unordered_map` 是基于节点的结构，rehash 只是把节点从旧桶摘下、挂到新桶，节点本身的内存地址从未改变。这与 `vector` 扩容时引用/指针也一起失效形成鲜明对比，根源在于 `vector` 是连续内存、扩容必须整体搬迁数据，`unordered_map` 是节点式结构、rehash 只是重新排列指针关系。

`reserve(n)` 与 `rehash(n)` 的区别：`rehash(n)` 直接把桶数量设置为至少 n；`reserve(n)` 从"元素数量"角度出发，保证插入 n 个元素之前不会触发 rehash，内部大致相当于 `rehash(ceil(n / max_load_factor()))`。已知即将插入的元素数量时，提前 `reserve` 可以避免插入过程中多次 rehash 造成的性能抖动。

---

## 九、`string`：字符串容器

> `std::string` 本质上是一个专门为字符设计的连续容器（类似 `vector<char>` 但接口丰富得多），
> 是实际项目里用得最多、却在很多"STL总结"里被忽略的一个容器。

```cpp
#include <string>
string s = "Hello, World!";
s.size(); s.length();   // 两者完全等价，都是 O(1)
s.empty();
```

### 9.1 拼接

```cpp
string s = "Hello";
string s2 = s + ", World!";  // + 拼接生成新字符串
s2 += " Bye.";                // += 原地追加
```

### 9.2 子串与查找

```cpp
string s = "Hello, World!";
s.substr(7, 5);    // "World"：从下标7开始取5个字符
s.substr(7);       // "World!"：从下标7取到末尾

s.find("World");                 // 7：第一次出现的下标
s.find("xyz");                   // 找不到返回 string::npos（一个很大的哨兵值，size_t的最大值）
s.find("xyz") != string::npos;   // 判断是否存在的标准写法

s.rfind('o');                    // 从后往前找，最后一个 'o' 的下标
s.find_first_of("lo");           // 第一个"是l或者o"的字符的下标
s.find_last_of("lo");            // 最后一个"是l或者o"的字符的下标
s.find_first_not_of("Hel");      // 第一个"不是H/e/l"的字符的下标（跳过指定字符集合）
```

### 9.3 修改

```cpp
string s = "Hello World";
s.replace(6, 5, "There");  // 从下标6起的5个字符换成"There" -> "Hello There"
s.insert(5, ",");           // 在下标5处插入 -> "Hello, There"
s.erase(5, 1);              // 从下标5删1个字符 -> "Hello There"
s.clear();                  // 清空
```

### 9.4 比较与转换

```cpp
string("abc") == "abc";       // 直接支持和 const char* 比较
string("abc") < string("abd"); // 字典序比较

int n = stoi("  42abc");      // 42：自动跳过前导空格，遇到非数字停止
double d = stod("3.14xyz");   // 3.14
string s = to_string(123);    // "123"：数字转字符串

const char* cs = s.c_str();   // 拿到 C 风格字符串（以 '\0' 结尾），和 C API 交互时用
```

### 9.5 整行读取

```cpp
string line;
getline(cin, line);  // 读取一整行（包含空格），直到遇到换行符——>> 运算符遇到空白就停，两者不能混用取整行
```

---

## 十、查找元素速查表

> 面试最容易被追问的点：**"怎么判断一个元素是否在容器里"**——不同容器的正确写法完全不同：

| 容器 | 推荐写法 | 说明 |
|------|---------|------|
| `vector`/`deque`/`array` | `find(c.begin(), c.end(), val) != c.end()` | 没有成员函数，O(n) 线性查找，需要 `<algorithm>` |
| 已排序的 `vector` | `binary_search(c.begin(), c.end(), val)` | O(log n)，前提是区间已经有序 |
| `list`/`forward_list` | `find(c.begin(), c.end(), val) != c.end()` | 同样没有成员函数，且只能 O(n)（没有随机访问，无法二分） |
| `map`/`set` | `c.contains(val)`（C++20）或 `c.find(val) != c.end()` | O(log n) |
| `unordered_map`/`unordered_set` | `c.contains(val)`（C++20）或 `c.find(val) != c.end()` | 平均 O(1) |
| `string` | `s.find(sub) != string::npos` | O(n·m)（朴素查找，大字符串场景可用 KMP，见 algo-notes/string-matching.md） |

> C++20 之前没有 `contains()`，只能用 `count() > 0` 或 `find() != end()`；C++20 之后关联容器优先用 `contains()`，
> 语义最清楚（不像 `count` 那样让人误以为是在数数量）。

---

## 十一、复杂度速查表

| 操作 | vector | deque | list | map/set | unordered_map/set | string |
|------|:---:|:---:|:---:|:---:|:---:|:---:|
| 随机访问 `[i]` | O(1) | O(1) | ❌ | ❌ | ❌ | O(1) |
| 头部插入 | O(n) | O(1) | O(1) | — | — | O(n) |
| 尾部插入 | 均摊O(1) | O(1) | O(1) | — | — | 均摊O(1) |
| 中间插入（已知迭代器） | O(n) | O(n) | O(1) | — | — | O(n) |
| 插入（按 key） | — | — | — | O(log n) | 平均O(1) | — |
| 查找（按 key/值） | O(n) | O(n) | O(n) | O(log n) | 平均O(1) | O(n·m) |
| 删除 | O(n) | O(n) | O(1) | O(log n) | 平均O(1) | O(n) |

---

## 十二、`pair` / `tuple`：轻量组合类型

```cpp
pair<int,string> p = {1, "one"};
p.first; p.second;

tuple<int,string,double> t = {1, "two", 3.0};
get<0>(t); get<1>(t); get<2>(t);
auto [a, b, c] = t;  // C++17 结构化绑定，比 get<N> 可读得多
```

---

## 十三、容器选择决策树

```
需要处理文本？
  是 -> string
  否 -> 需要按下标随机访问？
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
