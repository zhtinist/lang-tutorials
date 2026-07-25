# 字符串

字符串本质上也是一种容器(字符的序列),但四门语言在"可变性"和"索引的计数单位"这两件事上分歧极大,是从 C/C++ 转过来最容易吃亏的地方。

## 一、可变性:只有 C++ 的 `std::string` 是可变的

| 语言 | 字符串是否可变 |
|------|------------------|
| C++ `std::string` | **可变**,`s[0] = 'H'` 合法,原地修改 |
| Python `str` | **不可变**,任何"修改"操作都返回新字符串 |
| Go `string` | **不可变**,`s[0] = 'H'` 编译错误 |
| Java `String` | **不可变**,没有按下标赋值的方法 |

```cpp
// C++:唯一可以原地改的
string s = "hello";
s[0] = 'H';
cout << s;   // Hello,原地改了
```

```python
# Python:抛异常
s = "hello"
s[0] = 'H'   # TypeError: 'str' object does not support item assignment
s2 = s.replace('h', 'H')   # 只能这样:产生新对象
```

```java
// Java:没有这样的 API,想改字符必须转成 char[] 或用 StringBuilder
String s = "hello";
String replaced = s.replace('h', 'H');  // 返回新的 String 对象
```

**为什么 Python/Go/Java 都选择不可变字符串**:三个共同的收益——字符串常量可以安全共享(不用担心某处代码悄悄改了它,C++ 的可变字符串一旦被多处引用就必须考虑这一层)、可以缓存哈希值加速用作 dict/map 的 key、多线程读同一个字符串不需要加锁。这几点在[Python教程「数据类型」](../python/04-数据类型.md)和 Java 教程「基础语法」里都有更详细的论证。C++ 的 `std::string` 保留可变性,是为了贴近它作为"手动管理的字符缓冲区"这一定位——C++ 程序员经常需要原地拼接、原地替换来避免额外的内存分配,可变性带来的性能收益在 C++ 的场景里被认为比共享安全更重要。

## 二、索引:四种完全不同的计数单位

这是最容易踩坑的一处,同一个字符串 `"中文😀"` 在四门语言里"长度"和"按下标取到什么"完全不同:

| 语言 | 索引/长度的单位 | `"中文😀"` 的长度 |
|------|------------------|---------------------|
| C++ `std::string` | 字节(`char`) | 7(UTF-8:中=3字节,文=3字节,😀=4字节的一部分被截断,不建议直接用 `std::string` 处理非ASCII) |
| Python `str` | Unicode 码点(codepoint) | 3(中、文、😀 各算 1) |
| Go `string` | 字节(UTF-8 编码后) | 10(中3+文3+😀4) |
| Java `String` | UTF-16 code unit | 4(中=1、文=1、😀 是增补平面字符,用**代理对**占 2 个 unit) |

```python
# Python:len() 数的是"人眼看到的字符"(码点),最符合直觉
s = "中文😀"
print(len(s))      # 3
print(s[0])         # 中,完整的一个字符
```

```go
// Go: len() 数字节, range 才按 rune(码点)解码
s := "中文😀"
fmt.Println(len(s))              // 10 (UTF-8字节数)
fmt.Println(len([]rune(s)))      // 3  (要转成 []rune 才是"字符数")
for i, r := range s {
    fmt.Println(i, string(r))    // 按 rune 遍历,下标是字节偏移
}
```

```java
// Java: length() 数 UTF-16 code unit,增补平面字符(如emoji)会"多算"
String s = "中文😀";
System.out.println(s.length());               // 4,不是3!(😀占2个unit)
System.out.println(s.codePointCount(0, s.length()));  // 3,这才是真正的字符数
```

**为什么 Java 的计数单位是这四门语言里最"意外"的**:Java 在 1995 年发布时,Unicode 还只定义了 65536 个字符(基本多文种平面,BMP),`char` 被设计成正好 16 位来一一对应一个 Unicode 码点,`String.length()` 数的正是这些 16 位单元。后来 Unicode 扩展出了增补平面(表情符号、生僻字等),超出 16 位表示范围的字符在 UTF-16 里必须用一对 16 位单元(代理对,surrogate pair)拼出来——但 `String.length()` 的语义早已固定为"数 code unit",没法在不破坏兼容性的前提下悄悄改成"数码点"。这是一个典型的历史遗留:语言诞生时的技术选择(UTF-16 定长假设)被后来的现实(Unicode 突破了 16 位)打破,只能靠新增 `codePointCount` 这样的方法打补丁,而不能修改 `length()` 本身的语义。Go 和 C++ 选择按字节计数,恰好绕开了这个问题——UTF-8 从设计上就是变长编码,从没许诺过"下标访问=字符访问",于是"按字节数"从一开始就是唯一自洽的选择,反而不需要事后打补丁。Python 是唯一从头到尾把"字符串是码点序列"作为语言语义、而不是某种编码细节的语言(PEP 393,见[Python教程「数据类型」](../python/04-数据类型.md)的紧凑存储讨论),索引直接给你"人类认为的一个字符"。

## 三、拼接开销:循环里 `+=` 几乎处处是坑

四门语言的字符串都不可变或"可变但重新分配代价大",在循环里反复用 `+`/`+=` 拼接字符串,时间复杂度通常是 **O(n²)**(每次拼接都要整体拷贝之前已经拼好的内容),正确写法是使用可增长的缓冲区一次性构建、最后再转换成字符串:

| 语言 | 循环拼接的正确写法 |
|------|---------------------|
| C++ | `std::string` 本身可变,`s += x` 对同一个对象是均摊 O(1)(类似 vector 扩容),反而不是坑 |
| Python | `"".join(parts)`,而不是循环 `s += x` |
| Go | `strings.Builder`,而不是循环 `s += x` |
| Java | `StringBuilder`,而不是循环 `s += x` |

```python
parts = ["a", "b", "c"]
result = "".join(parts)   # 一次性分配,而不是每次拼接都造一个新字符串
```

**为什么 C++ 反而没有这个坑**:因为 `std::string` 本身就是可变的、内部像 `vector<char>` 一样有容量管理,`s += x` 是在已有缓冲区后面追加,只有容量不够时才重新分配(和 `vector::push_back` 均摊 O(1) 是同一个道理,见 [arrays-and-lists.md](arrays-and-lists.md))。Python/Go/Java 的字符串不可变,`s = s + x` 语义上必须产生一个全新对象,没有"原地追加"这个选项,只能靠专门的可变缓冲区类型(`str` 的列表再 `join`、`strings.Builder`、`StringBuilder`)把"多次拼接"降级成"一次性拼接",避免每次都重新分配整个字符串。

## 四、常见转换

| 操作 | C++ | Python | Go | Java |
|------|-----|--------|-----|------|
| 数字转字符串 | `std::to_string(42)` | `str(42)` | `strconv.Itoa(42)` | `String.valueOf(42)` / `Integer.toString(42)` |
| 字符串转数字 | `std::stoi("42")` | `int("42")` | `strconv.Atoi("42")` | `Integer.parseInt("42")` |
| 拆分 | `stringstream` 手写,或 C++20 `views::split` | `s.split(",")` | `strings.Split(s, ",")` | `s.split(",")` |
| 大小写转换 | `toupper`/`tolower` 逐字符 | `s.upper()`/`s.lower()` | `strings.ToUpper(s)` | `s.toUpperCase()` |
| 去除首尾空白 | 无原生方法,需手写 | `s.strip()` | `strings.TrimSpace(s)` | `s.strip()`(Java 11+,老写法是 `.trim()`) |

C++ 在字符串处理的便利程度上明显落后于其余三门语言——没有原生的 `split`,数字转换要么用 `to_string`/`stoi`,要么用较繁琐的 `stringstream`。这不是疏漏,而是 C++ 标准库一贯"提供底层构件、复杂功能靠组合"的风格,与 Python/Go/Java 标准库直接内置大量字符串便利方法的"电池齐全"哲学形成对比。

## 小结

- 可变性:只有 C++ 的 `std::string` 可变,其余三门语言的字符串都不可变。
- 索引单位是本节最大的坑:C++/Go 按字节、Python 按码点、Java 按 UTF-16 code unit——处理非 ASCII 文本(尤其是 emoji)时这四种计数会给出完全不同的"长度"。
- 循环拼接:除了 C++ 的可变字符串,其余三门语言都必须用专门的可变缓冲区(`join`/`strings.Builder`/`StringBuilder`)避免 O(n²)。

---
[← 上一篇:哈希表与集合](maps-and-sets.md) · [返回索引](index.md) · [下一篇:栈、队列与双端队列](stacks-queues-deques.md)
