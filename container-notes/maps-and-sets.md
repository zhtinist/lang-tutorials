# 哈希表与集合

## 一、判断 key/元素是否存在:本专题最重要的一节

四门语言在"查一个 key 存不存在"这件事上,失败模式完全不同,而且这一处的差异会直接影响你写出的代码是否正确——不是编译器会替你把关的地方。

| 语言 | 推荐的存在性检查 | 用"取值"顺带查存在性会怎样 |
|------|------------------|----------------------------|
| C++ | `m.contains(k)`(C++20 起)或 `m.count(k) > 0` | `m[k]` 若 `k` 不存在,**会静默插入一个默认构造的值**! |
| Python | `k in d` | `d[k]` 若 `k` 不存在,**抛出 `KeyError`** |
| Go | `v, ok := m[k]`,用 `ok` | `m[k]` 若 `k` 不存在,返回值类型的**零值**,不报错也不插入 |
| Java | `map.containsKey(k)` | `map.get(k)` 若 `k` 不存在,返回 **`null`**——和"值本身存的就是 `null`"无法区分 |

逐条实测:

```cpp
// C++:operator[] 的隐式插入陷阱
unordered_map<string,int> m = {{"a", 1}};
cout << m.size();              // 1
if (m["z"] == 0) {}            // 只是"读"了一下,以为没有副作用
cout << m.size();              // 2 !! "z" 被静默插入了,值是 int 的默认值 0
```

**为什么 `operator[]` 会有这个副作用**:C++ 标准对 `map`/`unordered_map` 的 `operator[]` 明确定义为"若 key 不存在则插入一个默认构造的 value 并返回其引用"——这不是 bug,是文档化的行为,目的是让 `m[k]++`(给一个可能还不存在的计数器加一)这种惯用法能一行写完,不用先判断存在再决定插入还是更新。代价是**只读**一次 `m[k]` 也会产生插入这个副作用,`const` 的 map 甚至无法调用 `operator[]`(因为它必须能修改容器)。真正只读的查询要用 `.find(k)` 或 `.at(k)`(找不到抛异常)或 `.count(k)`/`.contains(k)`。

```python
# Python:抛异常,绝不静默插入
d = {"a": 1}
try:
    d["z"]
except KeyError:
    pass
print(len(d))   # 1,没有任何插入发生

print(d.get("z", "默认值"))   # 只读查询,不存在就返回给定默认值,同样不插入
d.setdefault("z", 99)         # 唯一"顺带插入"的方法,但是显式调用、语义写在方法名里
print(len(d))                 # 2
```

```go
// Go:zero value + comma-ok,是本表里唯一"取值失败不报错也不插入"的
m := map[string]int{"a": 1}
v, ok := m["z"]
fmt.Println(v, ok)   // 0 false —— 没有插入,len(m) 仍是 1
fmt.Println(m["z"])  // 不接 ok 直接用:得到 0,但你无法知道这个 0 是"真的存了0"还是"key不存在"
```

```java
// Java:get() 返回 null,和"存的值本身是 null"无法区分
Map<String,Integer> m = new HashMap<>();
m.put("z", null);                       // 显式存了一个 null 值
System.out.println(m.get("z"));         // null
System.out.println(m.containsKey("z")); // true —— 必须用这个才能确认"key 确实存在"
System.out.println(m.get("notexist"));  // 同样是 null
System.out.println(m.containsKey("notexist")); // false
```

**为什么 Go 和 Java 都出现了"取值结果和默认值/null 混淆"的问题,却选择了不同的解法**:两者的根源相同——都需要一个"没有更好选择"的哨兵值来表示"key 不存在"(Go 没有内建的 `Optional`,选了类型的零值;Java 的引用类型天然有 `null` 可用),但零值/null 本身也可能是一个**合法存入的值**,单看返回值无法区分这两种情况。Go 的方案是让 map 下标表达式支持"多返回值"语法(`v, ok := m[k]`),把"有没有"和"值是什么"拆成两个独立的返回值,拿到手就是显式的;Java 的方案是提供一个独立的 `containsKey` 方法,查两次(先判断存在、再取值),或者用 `getOrDefault` 一次到位。C++20 和 Python 则从设计上更倾向于"贵在方法名说清楚意图"——`contains`/`in` 只回答存在性问题,不涉及取值。

## 二、有序 vs 无序:遍历顺序的保证程度

| 语言 | 无序容器(默认) | 有序容器 |
|------|------------------|----------|
| C++ | `unordered_map`/`unordered_set`:哈希桶顺序,不保证任何顺序,标准未规定 | `map`/`set`:**始终按 key 排序**(红黑树实现) |
| Python | `dict`(3.7+):**保证插入顺序**(这是语言规范,不只是实现细节) | 需要按 key 排序时用 `sorted(d.items())` |
| Go | `map`:**故意随机化**遍历起点,每次运行顺序都可能不同 | 无内建有序 map,需自己取出 key 排序后遍历 |
| Java | `HashMap`:不保证顺序,通常按哈希桶,但**不保证**跨版本/跨 JVM 一致 | `LinkedHashMap`:插入顺序;`TreeMap`:按 key 排序(红黑树) |

实测对比(同样插入 banana/apple/cherry 三个 key):

```
C++  std::map:        apple banana cherry   (总是排序)
C++  unordered_map:    apple cherry banana   (哈希桶顺序,不保证)
Python dict:          banana apple cherry   (总是插入序)
Go map(第一次运行):     banana apple cherry
Go map(第二次运行):     cherry banana apple   ← 同一份代码,两次结果不同!
Java HashMap:          banana apple cherry   (凑巧和插入序一样,但不保证)
Java LinkedHashMap:    banana apple cherry   (保证插入序)
Java TreeMap:          apple banana cherry   (保证key排序)
```

**为什么只有 Go 把遍历顺序做成"故意随机"而不是"不作保证但实现上凑巧固定"**:C++ 的 `unordered_map`、Java 的 `HashMap` 都只是"标准不承诺顺序",但同一份代码跑多次、顺序通常是稳定的(只要不触发扩容重哈希),这反而容易让人误以为"看起来稳定=可以依赖",事后一旦升级语言版本或换一批数据导致哈希桶分布变化,顺序说变就变,排查起来非常隐蔽。Go 语言设计者选择在运行时**主动**打乱起始遍历位置,让"以为 map 遍历顺序稳定"这种错误假设在开发阶段就必然暴露、而不是留到生产环境才因为一次哈希表扩容而突然出现顺序变化——用"提前让你摔一跤"换"生产环境更少的意外"。

## 三、Set 怎么实现

只有 C++ 和 Java 有语言/标准库原生的 `set` 类型,Python 有 `set` 类型但和 dict 是平级的独立类型,**Go 完全没有内建 set,靠 map 模拟**:

```go
// Go 惯用法:用 map[T]struct{} 或 map[T]bool 模拟 set
set := map[int]struct{}{1: {}, 2: {}, 3: {}}
_, exists := set[2]
fmt.Println(exists)   // true
```

**为什么用 `struct{}` 作为 value 类型而不是 `bool`**:`struct{}`(空结构体)不占用任何内存(大小为 0),而 `bool` 至少占 1 字节;当 value 本身没有任何信息量、你只关心 key 存在与否时,`map[T]struct{}` 是"内存零开销的存在性标记",这是 Go 社区从"map 只是键值对容器,没有专门 set 类型"这个语言约束下发展出的惯用法,反映了 Go"少即是多"的取舍——不是缺陷,而是刻意不为一个可以用现有类型模拟出来的东西再造一个新类型。

## 四、集合运算(交集/并集/差集)

```python
# Python:唯一原生支持运算符重载的
s1 = {1,2,3,4}; s2 = {3,4,5,6}
s1 & s2   # 交集 {3, 4}
s1 | s2   # 并集 {1,2,3,4,5,6}
s1 - s2   # 差集 {1, 2}
```

```cpp
// C++:算法函数 + 迭代器,没有运算符
set<int> s1={1,2,3,4}, s2={3,4,5,6}, inter;
set_intersection(s1.begin(),s1.end(), s2.begin(),s2.end(), inserter(inter, inter.begin()));
```

```java
// Java:显式方法调用,且会【原地修改】调用者(除非先拷贝一份)
Set<Integer> inter = new HashSet<>(s1);
inter.retainAll(s2);   // 交集;还有 addAll(并集)、removeAll(差集)
```

Go 标准库和语言层面都没有集合运算,需要手写循环或引入第三方库。**为什么只有 Python 允许用 `&`/`|`/`-` 表达集合运算**:这正是[Java教程「基础语法」](../java/02-基础语法.md)里讨论过的"运算符重载"话题在这里的具体体现——Python 语言层面允许类型自定义 `__and__`/`__or__`/`__sub__` 等魔术方法,内建 `set` 利用了这个机制;C++ 虽然也支持运算符重载,但标准库选择让集合运算走通用的 `<algorithm>` 函数模板(`set_intersection` 等),以统一处理有序区间上的多种运算,而不是给 `set` 单开运算符;Java 从语言层面直接不支持运算符重载(见 Java 教程「基础语法」的相关论证),集合运算只能是方法调用。

## 小结

- 存在性检查的安全写法:C++ `contains`/`count`、Python `in`、Go `v, ok := m[k]`、Java `containsKey`——四门语言里只有 C++ 的 `operator[]` 会在"只读"时产生插入副作用,务必避免用 `m[k]` 做存在性判断。
- 遍历顺序:C++ `map`/Java `TreeMap` 按 key 排序;Python `dict`(3.7+)按插入序;C++ `unordered_map`/Java `HashMap` 不保证顺序但可能"看似稳定";只有 Go 主动随机化,逼你不能依赖顺序。
- Go 没有原生 set,惯用 `map[T]struct{}`;只有 Python 支持用运算符做集合运算。

---
[← 上一篇:数组与动态数组](arrays-and-lists.md) · [返回索引](index.md) · [下一篇:字符串](strings.md)
