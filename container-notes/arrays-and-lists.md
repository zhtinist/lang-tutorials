# 数组与动态数组

## 一、定长数组 vs 动态数组:概念先分清

四门语言都有"定长数组"和"动态数组"两种东西,但只有 C++ 和 Go 在语法上把它们做成了两种不同的类型,Python 和 Java 事实上只提供动态数组:

| | 定长数组 | 动态数组 |
|---|---|---|
| C++ | `int a[5]` / `std::array<int,5>` | `std::vector<int>` |
| Python | (无此类型) | `list` |
| Go | `[5]int`(**值类型**,赋值即整体拷贝) | `[]int` slice(表头 + 底层数组) |
| Java | `int[] a = new int[5]`(创建后不能变长) | `ArrayList<Integer>` / `List<Integer>` |

Go 的定长数组是本表里最反直觉的一项:`var b = a`(`a` 是 `[5]int`)会把 5 个元素**整体拷贝一份**给 `b`,这与 C++ 的 `int a[5]` 赋值给另一个数组变量时同样是整体拷贝语义一致,但和 Go 自己的 `slice`(拷贝表头、共享底层数据)行为完全相反——这也是 Go 新手最容易搞混的两个类型。

## 二、创建

```cpp
// C++
int arr[5] = {1, 2, 3, 4, 5};             // 栈上定长数组
std::array<int, 5> arr2 = {1,2,3,4,5};    // 定长,但有 STL 接口(.size()等)
std::vector<int> v = {1, 2, 3};           // 动态数组,堆上管理
std::vector<int> v2(10, 0);               // 10 个元素,初值都是 0
```

```python
# Python
lst = [1, 2, 3]
lst2 = [0] * 10          # 10 个 0(注意:元素是可变对象时这是浅拷贝陷阱的常见来源)
lst3 = list(range(5))    # [0, 1, 2, 3, 4]
```

```go
// Go
arr := [5]int{1, 2, 3, 4, 5}   // 定长数组,长度是类型的一部分([5]int 和 [10]int 是不同类型)
s := []int{1, 2, 3}            // slice 字面量
s2 := make([]int, 10)          // 长度10,初值全是0
s3 := make([]int, 0, 10)       // 长度0、容量10,预分配但暂无元素
```

```java
// Java
int[] arr = {1, 2, 3, 4, 5};                 // 数组字面量,长度固定
int[] arr2 = new int[10];                    // 10 个 int,默认值 0
List<Integer> list = new ArrayList<>(List.of(1, 2, 3));  // 动态数组
```

## 三、下标越界访问:四种完全不同的失败方式

这是四门语言里语义差异最大、也最危险的一处:

| 语言 | 越界访问的后果 |
|------|----------------|
| C++ `v[i]`(`operator[]`) | **未定义行为**,不做边界检查,可能读到脏数据、可能崩溃、也可能"看起来正常" |
| C++ `v.at(i)` | 抛出 `std::out_of_range` 异常(有边界检查,但比 `[]` 慢) |
| Python `lst[i]` | 抛出 `IndexError` |
| Go `s[i]` | **`panic`**(运行时检测到并主动终止,不是像 C++ 那样悄悄读脏内存) |
| Java `list.get(i)` | 抛出 `IndexOutOfBoundsException` |

```cpp
// C++ 实测
vector<int> v = {1,2,3,4,5};
try { v.at(10); } catch (out_of_range& e) { cout << e.what(); }  // 抛异常,有检查
v[10];  // 未定义行为:不会自动报错,这是 C 系语言"信任程序员"哲学的直接体现——
        // 边界检查有运行时代价,operator[] 为了追求和 C 数组同等的零开销,把安全性完全交给调用者
```

```go
// Go 实测:panic 输出
// s[10] with len(s)=5 →
// panic: runtime error: index out of range [10] with length 5
```

**为什么只有 C++ 的 `operator[]` 允许真正的未定义行为、其余三门语言都至少会终止程序**:C++ 的设计哲学是"你不用的特性不必为它付费"(zero-overhead principle)——数组下标访问在性能敏感场景(比如内层数值计算循环)必须能被编译器优化到等价于裸指针运算,插入边界检查会牺牲这个目标,于是 C++ 提供了两套 API 让程序员自己选:`operator[]` 不检查、`.at()` 检查。Python/Go/Java 都选择了"默认安全",越界一律终止当前执行路径(异常或 panic),不允许静默读到不属于该容器的内存——这与[各语言教程「基础语法」章节](../python/02-基础语法.md)里"能确定性地报错就不留不确定行为"的整体设计取向一致,只是 C++ 单独在这一点上为性能开了后门。

## 四、插入与删除

```cpp
// C++
vector<int> v = {5, 3, 1, 4, 2};
v.insert(v.begin() + 2, 99);   // 在下标2插入99:{5,3,99,1,4,2}
v.erase(v.begin() + 2);        // 删除下标2那个元素
v.push_back(100);              // 尾部追加,均摊 O(1)
```

```python
# Python
lst = [5, 3, 1, 4, 2]
lst.insert(2, 99)     # 在下标2插入99
del lst[2]            # 按下标删除
lst.append(100)       # 尾部追加,均摊 O(1)
lst.remove(100)       # 按【值】删除第一个匹配项——注意和 del lst[i] 的区别!
```

```go
// Go:标准库长期没有 insert/delete,Go 1.21 起 slices 包补上了
import "slices"
s := []int{5, 3, 1, 4, 2}
s = slices.Insert(s, 2, 99)   // 在下标2插入99
s = slices.Delete(s, 2, 3)    // 删除区间[2,3),即下标2那一个
s = append(s, 100)            // 尾部追加,均摊 O(1)
```

```java
// Java
List<Integer> list = new ArrayList<>(List.of(5, 3, 1, 4, 2));
list.add(2, 99);              // 在下标2插入99
list.remove(2);               // 【按下标】删除!remove(int) 走的是下标重载
list.add(100);
list.remove(Integer.valueOf(100));  // 【按值】删除,必须显式装箱成 Integer 才会走值重载
```

Java 的 `remove` 是本节最容易踩的坑:`List<Integer>` 上 `remove(2)` 和 `remove(Integer.valueOf(2))` 是两个**不同的重载方法**——前者匹配 `remove(int index)`(按下标),后者匹配 `remove(Object o)`(按值)。**为什么会有这个二义性**:`List<Integer>` 里的元素类型是 `Integer`(引用类型),`int` 字面量 `2` 在传给 `remove` 时,编译器优先选择参数类型完全匹配的重载(`remove(int)`),而不会做"先装箱成 Integer 再匹配 `remove(Object)`"这一步——这是 Java 方法重载决议规则的固定优先级(基本类型精确匹配优先于装箱转换),而非运行时按值查找,所以只能通过显式装箱 `Integer.valueOf(2)` 强迫编译器选中按值删除的那个重载。C++/Python/Go 都不存在这个问题,因为它们对"删除第 i 个"和"删除值为 x 的元素"从一开始就是完全不同的方法名(`erase(iterator)` vs 无原生按值删除;`del lst[i]` vs `.remove(x)`;`slices.Delete` 按下标、无原生按值删除)。

## 五、切片/子区间

| 语言 | 语法 | 返回的是拷贝还是视图 |
|------|------|----------------------|
| C++ | 无原生语法,需用迭代器构造 `vector<int> sub(v.begin()+1, v.begin()+3)` | 拷贝 |
| Python | `lst[1:3]`、`lst[-2:]`、`lst[::2]`(步长) | **拷贝**(浅拷贝) |
| Go | `s[1:3]` | **视图**,与原 slice 共享底层数组! |
| Java | `list.subList(1, 3)` | **视图**,修改 sub 会改到原 list! |

```python
# Python:切片总是产生新的 list 对象
lst = [5,3,1,4,2]
sub = lst[1:3]   # [3, 1],新对象
sub[0] = -1
print(lst)       # [5, 3, 1, 4, 2],原list不受影响
```

```java
// Java:subList 是视图,这是一个真实的坑
List<Integer> list = new ArrayList<>(List.of(5,3,1,4,2));
List<Integer> sub = list.subList(1, 3);   // [3, 1]
sub.set(0, -1);
System.out.println(list);   // [5, -1, 1, 4, 2] —— 原list被改了!
```

Go 的切片同理是视图(`s[1:3]` 和原 slice 共享同一段底层数组),这在[Go 教程「复合数据结构」](../go/07-复合数据结构.md)里有更详细的表头结构图解释。Python 反而是这四门语言里唯一"切片默认就是拷贝"的,原因是 Python 的 `list` 本身语义上是"一个持有对象引用的连续数组",切片操作被设计成返回一个新的、独立的 `list` 对象(哪怕内部装的对象引用还是共享的——那是浅拷贝层面的另一件事,见 [maps-and-sets.md](maps-and-sets.md) 里可变默认值那类讨论)。

## 六、排序

| 语言 | 原地排序 | 返回新容器 |
|------|----------|------------|
| C++ | `sort(v.begin(), v.end())` | (`std::ranges::to`等需要手动构造) |
| Python | `lst.sort()` | `sorted(lst)` |
| Go | `slices.Sort(s)` | (需手动 `slices.Clone` 后再排) |
| Java | `Collections.sort(list)` / `list.sort(null)` | (需先拷贝再排) |

Python 是四门语言里唯一原生提供"原地排序"和"返回新容器排序"两个平行 API(`.sort()` vs `sorted()`)的语言,其余三门语言默认都只提供原地排序,想要一份"排序后的副本"都得自己先显式拷贝。

## 七、拷贝语义:这是本节最重要的一条

四门语言在"`b = a` 之后,改 b 会不会影响 a"这件事上分成两派,这直接决定了上面所有操作的别名行为:

| 语言 | `b = a` 之后 | 原因 |
|------|--------------|------|
| C++ `vector` | **深拷贝**,a、b 互不影响 | `vector` 是值类型,拷贝构造函数递归复制所有元素 |
| Python `list` | **别名**,b 改 a 也跟着变 | 变量是名字到堆对象的引用绑定,`=` 只拷贝引用(见[Python教程「变量与内存模型」](../python/03-变量与内存模型.md)) |
| Go `[]T` slice | **共享底层数组**(表头独立,数据共享) | slice 是"指针+长度+容量"的表头,`=` 拷贝表头但表头里的指针指向同一块数据(见[Go教程「复合数据结构」](../go/07-复合数据结构.md)) |
| Java `List` | **别名**,b 改 a 也跟着变 | 一切非基本类型变量都是引用,`=` 拷贝的是引用(见[Java教程「变量与内存模型」](../java/03-变量与内存模型.md)) |

```cpp
vector<int> a = {1,2,3};
vector<int> b = a;   // 深拷贝
b[0] = 999;
// a[0] 仍是 1
```

```python
a = [1,2,3]
b = a       # 别名
c = a[:]    # 想要真拷贝,必须显式切片/list()/copy.copy()
b[0] = 999
# a[0] 现在也是 999
```

```go
a := []int{1,2,3}
b := a                // 表头拷贝,底层数组共享
c := slices.Clone(a)  // 想要真拷贝,必须显式 Clone
b[0] = 999
// a[0] 现在也是 999(和 Python 表现一致,但原理不同:一个是纯引用绑定,一个是表头共享指针)
```

```java
List<Integer> a = new ArrayList<>(List.of(1,2,3));
List<Integer> b = a;                       // 别名
List<Integer> c = new ArrayList<>(a);       // 想要真拷贝,必须用拷贝构造函数
b.set(0, 999);
// a.get(0) 现在也是 999
```

**只有 C++ 的 `vector` 默认是深拷贝**,这是 C++ 坚持"值语义优先"设计哲学的直接体现——`vector` 被设计成行为上尽量贴近内置数组和基本类型,赋值/传参默认拷贝一份独立数据,这也是为什么 C++ 要专门发明"移动语义"(C++11 的 `std::move`)来避免不必要的深拷贝开销。Python/Java 选择"一切非基本类型都是引用"的统一模型,赋值天然是别名,想要独立副本必须显式调用拷贝方法。Go 比较特殊:它既不是纯值语义(数组是)也不是纯引用语义,slice/map/channel 这几个"引用类型"本质上是"值语义的表头,包着一个共享的指针",这也是为什么 Go 教程反复强调"一切都是值传递"这条公理——slice 的别名效果不是特例,而是这条公理应用在"表头里恰好有个指针"这一具体情况下的自然结果。

## 小结

- 长度:C++ `.size()`、Python `len()`、Go `len()`、Java 数组 `.length` 字段/容器 `.size()` 方法。
- 越界访问:C++ `[]` 是唯一允许静默未定义行为的,其余三门语言(以及 C++ 自己的 `.at()`)都会终止执行路径。
- 插入删除:Java 的 `remove(int)` vs `remove(Integer)` 重载二义性是本节最容易踩的坑。
- 切片:Python 切片是拷贝,Go/Java 的切片/`subList` 都是共享底层数据的视图,C++ 无原生切片语法。
- 拷贝语义是理解一切别名行为的根:C++ `vector` 默认深拷贝,Python/Java 默认别名,Go 的"值语义表头 + 共享底层指针"是介于两者之间的第三种模式。

---
[← 返回索引](index.md) · [下一篇:哈希表与集合](maps-and-sets.md)
