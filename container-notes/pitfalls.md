# 跨语言易错点速查

这一篇不重复前面几篇的详细论证,只做一件事:把"写代码时最容易凭 A 语言的肌肉记忆去写 B 语言、结果写错"的高频点集中列成一张可以直接扫一眼查的表。每一条都能在前面的专题文章里找到详细解释和实测代码。

## 长度与判空

| 你想做的事 | 常见的错误写法(跨语言干扰) | 正确写法 |
|------------|------------------------------|----------|
| 求 Java 数组长度 | `arr.length()` (以为和 List 一样是方法) | `arr.length`(字段,无括号) |
| 求 Java List 长度 | `list.length` (以为和数组一样是字段) | `list.size()`(方法) |
| 判断 Go 字符串是不是"3个字符" | `len(s) == 3` | `len([]rune(s)) == 3`——`len(s)` 数的是字节 |
| 判断 Python 容器是否为空 | `len(x) == 0` | 更地道:`if not x:`——空容器本身就是假值(见[Python教程「基础语法」](../python/02-基础语法.md)的真值测试一节) |

## 存在性检查(见 [maps-and-sets.md](maps-and-sets.md) 详细展开)

| 语言 | 千万别用来判断存在性的写法 | 原因 |
|------|----------------------------|------|
| C++ | `if (m[k] != something)` | `operator[]` 会静默插入一个默认值,改变了容器内容 |
| Java | `if (map.get(k) != null)` | 如果 value 本身允许存 `null`,这个判断法无法区分"key不存在"和"key存在但值是null" |
| Go | `if m[k] != 0` (只看值,不接 `ok`) | 无法区分"key不存在"和"key存在但值恰好是0" |

## 拷贝语义:"改了 b,a 会不会跟着变"

| 语言 | `b := a` / `b = a` 之后 |
|------|--------------------------|
| C++ `vector`/`string`/`map` | **不会**,默认深拷贝 |
| Python `list`/`dict`/`set` | **会**,默认是别名 |
| Go `slice`/`map` | **会**(共享底层数据),但 Go 数组 `[N]T` **不会**(值类型,整体拷贝) |
| Java `List`/`Map`/数组 | **会**,默认是引用别名 |

一句话记忆:**只有 C++ 的容器默认深拷贝**,其余三门语言默认都是别名/共享;Go 的数组是这四门语言里唯一一个"看起来像基本类型、赋值却会整体拷贝一大块数据"的类型,新手很容易忘记它和 slice 完全是两种拷贝语义。

## 越界/异常处理:失败时是崩溃、异常还是静默

| 场景 | C++ | Python | Go | Java |
|------|-----|--------|-----|------|
| 数组/列表越界 | `[]`:未定义行为(可能不报错!);`.at()`:抛异常 | 抛 `IndexError` | `panic` | 抛 `IndexOutOfBoundsException` |
| map 查不存在的 key | `operator[]`:静默插入 | 抛 `KeyError` | 返回零值,不报错 | `get`返回 `null`,不报错 |
| 整数除以 0 | 未定义行为 | 抛 `ZeroDivisionError` | **整数**除零 `panic`,浮点除零得 `Inf`/`NaN` | 整数除零抛 `ArithmeticException`,浮点除零得 `Infinity`/`NaN` |

只有 C++ 存在"完全不报错、也不崩溃,就是读到脏数据"这种最危险的失败模式(`vector::operator[]` 越界、整数溢出、除零),这和 C++ "性能优先、信任程序员"的设计哲学一以贯之(详见[各语言教程「基础语法」](../python/02-基础语法.md)对这条原则的展开)。

## 修改容器时正在遍历它,会怎样

| 语言 | 遍历时增删元素的后果 |
|------|------------------------|
| C++ | 大多数容器的迭代器会**失效**(iterator invalidation),继续用会导致未定义行为 |
| Python | `list`/`dict` 遍历时增删,轻则跳过/重复元素,`dict` 在 3.6+ 会直接抛 `RuntimeError: dictionary changed size during iteration` |
| Go | `slice`/`map` 遍历时修改行为不确定(map 新增的 key 可能被遍历到也可能不会),但**不会** panic |
| Java | 用 `Iterator` 遍历时若不通过 `Iterator.remove()` 而直接调用集合的 `remove`,**通常**会抛 `ConcurrentModificationException`(fail-fast 机制,靠内部计数器 `modCount` 检测)——但**不保证**每次都能测到,见下 |

Java 是四门语言里唯一**主动设计了运行时检测机制**来专门捕获"遍历中被意外修改"这类 bug 的,其余三门语言要么是未定义行为(C++)、要么效果不确定但不报错(Go)、要么只在特定容器上有部分检测(Python 的 dict)。但这个检测机制本身有个实测出来的盲区:`ArrayList` 遍历时删除**倒数第二个**元素,`hasNext()` 会在删除后误判"已经遍历完",导致本该抛出的异常被漏掉:

```java
List<Integer> list = new ArrayList<>(List.of(1,2,3,4));
for (Integer x : list) { if (x == 2) list.remove(x); }
// 抛出 ConcurrentModificationException(4个元素,删的不是倒数第二个,能测到)

List<Integer> list2 = new ArrayList<>(List.of(1,2,3));
for (Integer x : list2) { if (x == 2) list2.remove(x); }
// 【不抛异常】,结果是 [1, 3]——3个元素删中间那个,恰好是"倒数第二个",漏检!
```

原因是 `ArrayList` 迭代器的 `hasNext()` 只是简单比较"当前遍历到第几个"和"容器当前大小"两个数字,删除元素后容器变小,这两个数字可能提前相等,导致循环在检测到修改之前就已经正常退出——**这也是 Java 官方文档里"fail-fast 机制只应该用于发现 bug,不能当成保证"这句话的具体体现**,不能因为大多数时候会抛异常就误以为它绝对可靠。

## 排序:原地 or 返回新容器,升序 or 降序,怎么传自定义比较逻辑

| 语言 | 原地排序 | 自定义排序规则 |
|------|----------|------------------|
| C++ | `sort(v.begin(), v.end())` | 传函数/lambda 作为第三个参数:`sort(v.begin(),v.end(), greater<int>())` |
| Python | `lst.sort()` | `lst.sort(key=lambda x: x[1])`——是 `key` 不是 `cmp` |
| Go | `slices.Sort(s)` | `slices.SortFunc(s, func(a,b int) int {...})` |
| Java | `Collections.sort(list)` / `list.sort(null)` | `list.sort(Comparator.comparing(...))` 或实现 `Comparable` |

Python 的 `key=` 参数是这四门语言里唯一"只需要告诉排序函数按什么值比较,不需要自己写比较逻辑"的设计——`key=lambda x: x[1]` 只需返回一个可比较的值,底层排序算法负责怎么比较;其余三门语言的自定义排序都要求你直接提供"两个元素谁排前面"的完整比较函数(接受两个参数、返回大小关系或布尔值),这是"提取排序键"和"提供比较逻辑"这两种不同抽象层次的接口设计取舍。

## 一张表记住"这门语言默认容不容许某种直觉"

| 直觉 | C++ | Python | Go | Java |
|------|-----|--------|-----|------|
| 数组下标越界会自动报错吗 | 否(`[]`) | 是 | 是(panic) | 是 |
| 容器赋值默认是深拷贝吗 | 是 | 否 | 部分(slice共享,数组不共享) | 否 |
| 哈希表遍历顺序稳定吗 | 否(unordered) | 是(3.7+ 插入序) | 否(故意随机) | 否(HashMap) |
| 字符串可以原地改吗 | 是 | 否 | 否 | 否 |
| 支持运算符重载吗 | 是 | 是(部分类型) | 否 | 否(仅 `+` 拼接字符串) |
| 有没有内建 set 类型 | 有 | 有 | 无(用 map 模拟) | 有 |

---
[← 上一篇:栈、队列与双端队列](stacks-queues-deques.md) · [返回索引](index.md)
