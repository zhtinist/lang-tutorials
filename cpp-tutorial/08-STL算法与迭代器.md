# STL 算法与迭代器

> `<algorithm>` 和 `<numeric>` 头文件提供了上百个通用算法，全部通过**迭代器区间** `[begin, end)` 操作，
> 不关心具体容器类型——这正是"泛型编程"的核心：同一个 `sort()` 既能排 `vector`，也能排数组，只要给它一对迭代器。

---

## 一、迭代器分类

```
STL 迭代器分 5 类，能力依次递增（后面的类别包含前面的能力）：

  输入迭代器 (Input Iterator)：只能读、只能单趟向前走一次（如 istream_iterator）
  输出迭代器 (Output Iterator)：只能写、只能单趟向前走一次（如 back_insert_iterator）
  前向迭代器 (Forward Iterator)：能读写，能多趟遍历（如 forward_list 的迭代器）
  双向迭代器 (Bidirectional Iterator)：还能往回走 --it（如 list、map、set 的迭代器）
  随机访问迭代器 (Random Access Iterator)：还支持 it+n、it[n]、迭代器间做减法（如 vector、deque、array）

判断一个算法能不能用在某个容器上，本质是看该算法要求的迭代器能力，
容器的迭代器是否满足——比如 sort() 要求随机访问迭代器（因为快排要能跳着比较），
所以 sort(list.begin(), list.end()) 编译不过；list 有自己的成员函数 list::sort() 专门用链表友好的方式实现排序。
```

```cpp
#include <list>
#include <algorithm>
using namespace std;

list<int> lst = {1,2,3,4,5};
auto it = lst.begin();
advance(it, 2);   // advance 对任何迭代器都能用（内部按类别选择 O(1) 跳转还是循环 ++）
// *(lst.begin() + 2) 编译不过：list 的迭代器不支持 operator+

vector<int> vv = {1,2,3,4,5};
auto vit = vv.begin();
vit += 2;         // vector 迭代器是随机访问迭代器，支持 +=
```

---

## 二、排序与查找

```cpp
#include <algorithm>
using namespace std;

vector<int> v = {5,3,1,4,1,5,9,2,6};
sort(v.begin(), v.end());                    // O(n log n)，默认升序
sort(v.begin(), v.end(), greater<int>());     // 降序：传自定义比较器

auto it = find(v.begin(), v.end(), 4);        // O(n) 线性查找，找不到返回 end()
int cnt = count(v.begin(), v.end(), 1);       // O(n) 统计出现次数

// 有序区间上的二分查找，O(log n)——前提是区间必须已经有序！
vector<int> sorted_v = {1,3,3,5,7,9};
lower_bound(sorted_v.begin(), sorted_v.end(), 3);  // 指向第一个 >= 3 的位置
upper_bound(sorted_v.begin(), sorted_v.end(), 3);  // 指向第一个 > 3 的位置
binary_search(sorted_v.begin(), sorted_v.end(), 5); // 返回 bool，只判断存在与否

*max_element(v.begin(), v.end());   // 最大值（返回迭代器，要解引用）
*min_element(v.begin(), v.end());

nth_element(v.begin(), v.begin()+3, v.end());  // O(n) 平均，让第3个位置变成"排序后应在那的值"
                                                 // 比完整 sort 快，只需要"第k小"时用它（本质是 quickselect）
```

---

## 三、变换与去重

```cpp
vector<int> src = {1,2,3,4,5}, dst(src.size());
transform(src.begin(), src.end(), dst.begin(), [](int x){ return x * x; });
// dst = {1,4,9,16,25}

vector<int> v = {1,1,2,2,3,3,3,4};
auto last = unique(v.begin(), v.end());  // 只去掉"连续"重复元素，返回新逻辑末尾
v.erase(last, v.end());                   // 必须配合 erase 才能真正缩小容器（unique 不改变 size）
// v = {1,2,3,4}
// ⚠️ unique 前提：重复元素必须相邻，通常先 sort() 再 unique()

vector<int> v2 = {1,2,3,4,5};
v2.erase(remove_if(v2.begin(), v2.end(), [](int x){ return x % 2 == 0; }), v2.end());
// v2 = {1,3,5}  ——"erase-remove idiom"：remove_if 只是把要删的元素移到末尾并返回新逻辑末尾，
//                真正释放内存/缩小 size 还得调用 erase，这是 STL 里最经典的固定搭配写法
```

---

## 四、累加与生成

```cpp
#include <numeric>
using namespace std;

vector<int> v = {1,2,3,4,5};
int sum = accumulate(v.begin(), v.end(), 0);              // 求和，初值 0
int product = accumulate(v.begin(), v.end(), 1, multiplies<int>());  // 自定义操作：求积

vector<int> v2(5);
iota(v2.begin(), v2.end(), 10);   // 依次填入 10,11,12,13,14（"iota"取名自APL语言的同名算子）

int counter = 0;
vector<int> v3(5);
generate(v3.begin(), v3.end(), [&counter]{ return counter++; });  // 用一个可调用对象逐个生成元素

vector<int> v4(5);
fill(v4.begin(), v4.end(), 7);    // 全部填成同一个值
```

---

## 五、区间操作

```cpp
vector<int> v = {3,1,4,1,5,9,2,6};
reverse(v.begin(), v.end());                              // 原地反转

vector<int> v2 = {1,2,3,4,5};
rotate(v2.begin(), v2.begin() + 2, v2.end());              // 把 [begin,mid) 转到末尾，相当于左旋
// v2 = {3,4,5,1,2}

vector<int> v3 = {1,2,3,4,5,6,7,8};
auto pit = partition(v3.begin(), v3.end(), [](int x){ return x % 2 == 0; });
// 所有偶数被划到前面，奇数在后面（各自内部顺序不保证），pit 指向分界点
```

---

## 六、谓词类算法（all_of / any_of / none_of / for_each）

```cpp
vector<int> v = {3,1,4,1,5,9,2,6};
all_of(v.begin(), v.end(), [](int x){ return x > 0; });   // 是否全部满足条件
any_of(v.begin(), v.end(), [](int x){ return x > 8; });   // 是否存在满足条件的
none_of(v.begin(), v.end(), [](int x){ return x < 0; });  // 是否全都不满足条件

for_each(v.begin(), v.end(), [](int x){ cout << x << " "; });  // 对每个元素执行操作
// 大多数场景下，range-based for 循环 `for (int x : v)` 更直观，for_each 在需要传函数对象/
// 或者要配合算法风格代码统一时更常用
```

---

## 七、迭代器适配器

```cpp
#include <iterator>

vector<int> src = {1,2,3,4,5};
vector<int> dst;
copy(src.begin(), src.end(), back_inserter(dst));
// back_inserter(dst) 返回一个特殊的输出迭代器，每次赋值都会调用 dst.push_back(...)，
// 这样 copy() 就能"边遍历边追加"到一个原本为空的容器里，而不需要提前 resize
```

| 适配器 | 作用 |
|--------|------|
| `back_inserter(c)` | 赋值时调用 `c.push_back()` |
| `front_inserter(c)` | 赋值时调用 `c.push_front()`（要求容器支持 push_front，如 list/deque） |
| `inserter(c, it)` | 赋值时调用 `c.insert(it, ...)`，通用但比前两者慢 |
| `istream_iterator<T>` | 把输入流包装成迭代器，可以直接用算法处理 `cin` 里的数据流 |
| `ostream_iterator<T>` | 把输出流包装成迭代器，配合 `copy` 可以直接把容器打印出来 |

---

## 八、常用算法速查表

| 算法 | 作用 | 复杂度 |
|------|------|--------|
| `sort` | 排序（要求随机访问迭代器） | O(n log n) |
| `stable_sort` | 稳定排序（相等元素保持相对顺序） | O(n log n) |
| `nth_element` | 找第k小（不完全排序） | O(n) 平均 |
| `find` / `count` | 线性查找/计数 | O(n) |
| `lower_bound` / `upper_bound` / `binary_search` | 有序区间二分 | O(log n) |
| `max_element` / `min_element` | 找最值 | O(n) |
| `accumulate` | 累加（可自定义操作） | O(n) |
| `transform` | 逐元素映射生成新序列 | O(n) |
| `unique` | 去除相邻重复（需配合 sort + erase） | O(n) |
| `remove_if` + `erase` | 条件删除（erase-remove idiom） | O(n) |
| `reverse` / `rotate` | 反转/旋转区间 | O(n) |
| `partition` | 按条件划分两部分 | O(n) |
| `all_of`/`any_of`/`none_of` | 谓词判断 | O(n) |

---

[← 返回索引](index.md)
