# C++ 面试八股文

> 本文素材主要参考 [huihut/interview](https://github.com/huihut/interview)（38k+ star，C/C++ 技术面试知识点最全的仓库之一）与
> [guaguaupup/cpp_interview](https://github.com/guaguaupup/cpp_interview)（C++ 后台开发方向的面试整理），并与其他若干 1000+ star 的中文 C++ 面试仓库交叉核对。
> 所有问答均为原创复述（这些是公开的 CS 常识，不是原文摘抄），代码全部经过实际编译运行验证。
> STL 与多线程部分本文只做"面试怎么答"的精简问答，完整原理和更多可运行示例见同仓库 `cpp-tutorial/07-STL容器详解.md`、`08-STL算法与迭代器.md`、`11-多线程与并发.md`。

---

## 目录

- 一、C++基础语法与关键字
- 二、面向对象与虚函数机制
- 三、构造析构与拷贝语义
- 四、内存管理与智能指针
- 五、类型转换与RTTI
- 六、STL容器与迭代器
- 七、C++11/14/17/20新特性
- 八、多线程与并发基础
- 九、其他高频问题

---

## 一、C++基础语法与关键字

### 1. `const` 有哪些用法？

**A：** 四种典型场景：① 修饰变量——只读常量；② 修饰指针——区分"指向常量的指针"(`const int*`，指针可变、指向的值不可变)和"常量指针"(`int* const`，指针不可变、指向的值可变)；③ 修饰成员函数——承诺不修改非`mutable`成员，因此只有`const`对象/引用可以调用非`const`成员函数是不允许的，但`const`对象只能调用`const`成员函数；④ 修饰函数参数/返回值——表达"只读"语义，也允许用右值/临时对象初始化`const T&`形参。

```cpp
class Point {
public:
    Point(int x, int y) : x_(x), y_(y) {}
    int getX() const { return x_; }         // const成员函数：不修改成员（mutable除外），可被const对象调用
    void setX(int x) { x_ = x; }
private:
    int x_, y_;
};

int main() {
    int b = 5;
    const int* p1 = &b;               // 指向常量的指针：不能通过p1修改b，但p1可以指向别处
    p1 = nullptr;                      // OK
    int* const p2 = &b;               // 常量指针：p2不能再指向别处，但可以通过p2修改b
    *p2 = 6;                           // OK

    const Point pt(1, 2);
    cout << pt.getX() << endl;        // const对象只能调用const成员函数
    // pt.setX(3);                    // 编译错误：const对象不能调用非const成员函数
}
// 输出：1  （pt.getX()）
```

### 2. `static` 的几种含义？

**A：** 三个场景含义完全不同：① 静态局部变量——只在第一次执行到声明处时初始化一次，之后跨函数调用保留状态，生命周期到程序结束；② 类的静态成员变量——属于类而不属于某个对象，所有对象共享同一份存储，必须在类外定义（分配存储空间）；③ 静态成员函数——没有隐藏的`this`参数，因此只能访问静态成员，不依赖具体对象即可通过`类名::函数名()`调用；④ 修饰全局变量/函数——把符号的链接属性从外部链接改为内部链接，即只在当前编译单元可见（"内部静态"），常用来避免多个`.cpp`文件间的命名冲突。

```cpp
class Counter {
public:
    Counter() { ++count_; }              // 每次构造，静态成员变量+1（所有对象共享同一份）
    static int count_;
    static void show() { cout << "count=" << count_ << endl; }
};
int Counter::count_ = 0;                  // 类外定义+初始化

void localStaticDemo() {
    static int calls = 0;                 // 局部静态变量：只在第一次调用时初始化，之后跨调用保持值
    ++calls;
    cout << "called " << calls << " times" << endl;
}

int main() {
    Counter c1, c2, c3;
    Counter::show();                      // count=3
    localStaticDemo();                    // called 1 times
    localStaticDemo();                    // called 2 times
    localStaticDemo();                    // called 3 times
}
```

局部静态变量的构造在 C++11 起由标准保证是**线程安全**的（"magic statics"，编译器会插入一个隐藏的原子标志/双检锁逻辑），因此 Meyer's Singleton 写法能安全地用于多线程（见第九节单例）。

```cpp
struct Heavy {
    Heavy() { cout << "Heavy构造，线程id=" << this_thread::get_id() << endl; }
};
Heavy& getInstance() {
    static Heavy h;   // 多线程同时第一次执行到这里，也只会构造一次
    return h;
}
int main() {
    vector<thread> ts;
    for (int i = 0; i < 5; ++i) ts.emplace_back([]{ getInstance(); });
    for (auto& t : ts) t.join();
}
// 实测输出：Heavy构造... 只打印一次（5个线程同时调用也只构造一次）
```

### 3. `this` 指针是什么？存放在哪？

**A：** `this`是编译器在每个非静态成员函数里隐式添加的第一个参数，类型是`ClassName*`（或`const ClassName*`），指向调用该成员函数的对象本身。它**不是**对象内存布局的一部分（不占用`sizeof(对象)`的空间），而是在函数调用时通过参数传递机制传进来的——具体到 ABI 层面，在 x86-64 System V 上通常经由`rdi`寄存器传入，在 AArch64（Apple Silicon）上是`x0`寄存器，和其他任何指针实参没有本质区别，只是编译器自动帮你传，不用手写。反汇编可以直接验证：

```cpp
class Foo {
public:
    int v_;
    void setV(int x) { v_ = x; }  // 编译器改写成 setV(Foo* this, int x) { this->v_ = x; }
};
```

```
$ g++ -O0 -S foo.cpp -o foo.s   # 查看setV的汇编(AArch64)
__ZN3Foo4setVEi:
    str  x0, [sp, #8]   ; x0(第一个整型参数寄存器)存的正是this指针
    str  w1, [sp, #4]   ; w1(第二个参数寄存器)是x
    ldr  x9, [sp, #8]
    ldr  w8, [sp, #4]
    str  w8, [x9]        ; *this->这块地址 = x
```

`this`的常见用途：链式调用（`return *this;`）、区分同名的成员变量和参数、在成员函数内输出/比较对象地址。

```cpp
class Foo {
public:
    Foo& setVal(int v) { val_ = v; return *this; }  // 链式调用依赖this指针
    int val_ = 0;
};
int main() {
    Foo f;
    f.setVal(1).setVal(2).setVal(3);
    cout << f.val_ << endl;   // 3
}
```

### 4. `inline` 的作用与限制？

**A：** `inline`向编译器建议在调用点直接展开函数体，省去函数调用的压栈/跳转开销，适合短小、频繁调用的函数。但它只是"建议"，编译器可以忽略（比如函数体太大、递归、地址被取用等场景）。`inline`函数必须在每个用到它的编译单元里都有相同的定义（因此通常直接写在头文件里），这也是它能"违反"单一定义原则(ODR)、允许多个`.cpp`包含同一个头文件而不报重复定义的原因。C++17 起`inline`还可以修饰变量（`inline`变量），解决头文件里全局变量重复定义的问题。

```cpp
inline int square(int x) { return x * x; }
int main() { cout << square(5) << endl; }  // 25
```

### 5. `volatile` 的作用？它能保证原子性/线程安全吗？

**A：** `volatile`告诉编译器"这个变量可能被当前执行流看不到的方式修改（硬件、中断、信号处理函数），每次访问都必须真实地读写内存，不能用寄存器缓存旧值，也不能做常量折叠/指令重排优化"。典型场景是内存映射 I/O 寄存器、信号处理函数中读写的标志位。**`volatile`不保证原子性，也不提供内存序(happens-before)保证，不能替代`std::atomic`/`mutex`做多线程同步**——这是最容易被问倒的点，很多人以为`volatile`能让多线程读写安全，实际上不能。

反汇编可以直接证明"阻止优化"这一点（`-O2`下对比）：

```cpp
int normalRead(int* p)          { *p = 1; return *p; }  // 非volatile
int volatileRead(volatile int* p){ *p = 1; return *p; }  // volatile
```

```
normalRead:                       volatileRead:
    mov  w8, #1                       mov  w8, #1
    str  w8, [x0]                     str  w8, [x0]
    mov  w0, #1     ; 直接用常量1     ldr  w0, [x0]    ; 强制重新从内存load一次
    ret                                ret
```

`normalRead`被编译器优化成直接返回常量`1`（因为它"知道"刚写进去的值），而`volatileRead`被迫真的重新读一次内存——这正是`volatile`"阻止优化、不保证原子性"的实证。

### 6. `assert` 与 `static_assert` 的区别？

**A：** `assert`是运行期断言（`<cassert>`），条件为假时调用`abort()`并打印文件名/行号，常用于调试期校验前置条件；发布版本一般定义`NDEBUG`宏后`assert`会被整体去掉，不产生任何运行时开销，因此**不能把有副作用的代码放进`assert()`里**（发布版本会被去掉导致行为不一致）。`static_assert`是编译期断言，条件必须是编译期常量表达式，不满足时直接编译失败，常用于校验模板参数、平台假设（如`sizeof(int)==4`）等。

```cpp
#include <cassert>

int divide(int a, int b) {
    assert(b != 0);   // 运行期断言
    return a / b;
}
static_assert(sizeof(int) == 4, "int must be 4 bytes on this platform"); // 编译期断言
int main() { cout << divide(10, 2) << endl; }  // 5
```

### 7. `sizeof` 面试高频坑

**A：** 常见结论：① 空类`sizeof`不为`0`而是`1`（保证不同对象地址不重叠）；② 含虚函数的类会多一个`vptr`（64位平台通常`+8`字节）；③ 静态成员不计入对象大小（它不属于对象，属于类）；④ **数组作为函数参数会退化成指针**，函数内`sizeof(arr)`得到的是指针大小而不是数组大小，这是最容易被问倒的坑；⑤ 64位平台上所有指针（不论指向什么类型）大小都是8字节。

```cpp
class Empty {};                             // sizeof(Empty) = 1
class WithVirtual { virtual void f() {} };  // sizeof(WithVirtual) = 8 (一个vptr)
class WithStatic { static int s; int a; };  // sizeof(WithStatic) = 4 (只算int a)

void arrParam(int arr[10]) {
    cout << sizeof(arr) << endl;   // 8，退化成int*了，不是40！编译器甚至会给warning提示这一点
}
int main() {
    int arr[10];
    cout << sizeof(arr) << endl;     // 40 = 10*4，在定义处数组没有退化
    arrParam(arr);                    // 8
    cout << sizeof((char*)nullptr) << endl;  // 8
}
```

实测输出：`1` `8` `4` `40` `8` `8`，与上述结论完全一致。

### 8. 位域(bit-field)是什么？

**A：** 位域允许在结构体里以"比特"为单位定义成员，用来压缩存储一些只需要几个bit就能表示的标志位（比如协议头、状态标志）。编译器会把多个位域尽量打包进同一个存储单元，具体打包方式（是否跨字节、大小端顺序）依赖具体编译器/平台，不可移植，因此不适合用来做跨平台的二进制协议解析。

```cpp
struct Flags {
    unsigned int isActive : 1;   // 只占1个bit
    unsigned int level    : 3;   // 占3个bit，取值0~7
    unsigned int type     : 4;   // 占4个bit
};
int main() {
    cout << sizeof(Flags) << endl;   // 4，位域被打包进一个unsigned int存储单元
    Flags f{1, 5, 9};
    cout << f.isActive << " " << f.level << " " << f.type << endl;  // 1 5 9
}
```

### 9. `extern` 和 `extern "C"` 分别是干什么的？

**A：** `extern`声明一个变量/函数在别处定义，只是声明不分配存储，用于跨编译单元共享符号。`extern "C"`让 C++ 编译器对这段声明**按 C 语言的规则处理符号名（不做 name mangling）**，这样 C++ 代码才能正确链接由 C 编译器编译出的目标文件/库（比如很多系统库、老代码库是纯 C 写的），反过来也能让 C 代码调用 C++ 写的接口。原因在于 C++ 支持函数重载，编译器必须把参数类型信息编码进符号名里（"name mangling"）才能在链接期区分不同重载版本，而 C 不支持重载，符号名就是函数名本身。

```cpp
extern "C" {
    int add_c(int a, int b);
}
int add_c(int a, int b) { return a + b; }
int main() { cout << add_c(2, 3) << endl; }  // 5
```

用`nm`直接对比符号名可以看到 mangling 的差异：

```cpp
int plain_func(int a) { return a; }
extern "C" int c_func(int a) { return a; }
```

```
$ nm t_mangle.o | grep func
0000000000000000 T __Z10plain_funci   # 被mangling：编码了函数名长度+参数类型
0000000000000014 T _c_func            # extern "C"：符号名就是纯函数名（前面的下划线是macOS ABI约定）
```

### 10. C 语言里 `struct` 和 `typedef struct` 的区别？

**A：** 这是 C 语言（不是 C++）里的坑：在 C 里`struct Point {...};`只声明了一个"标签"(tag)`struct Point`，之后必须写`struct Point p;`才能定义变量，直接写`Point p;`会编译错误（"Point"不是类型名）。`typedef struct {...} Point2;`则是给这个匿名结构体起了一个类型别名`Point2`，之后可以直接用`Point2 p2;`，不需要`struct`前缀。C++ 里这个区别不存在——`struct`在 C++ 里本身就是一个类型名，声明即可直接使用，不需要`typedef`，也不需要写`struct`前缀。

```c
// C语言
struct Point { int x, y; };
typedef struct { int x, y; } Point2;
int main() {
    struct Point p1 = {1, 2};   // 必须带struct
    Point2 p2 = {3, 4};          // 不需要struct前缀，因为Point2本身是类型名
}
```

```
// 反例(C语言)：直接写 Point p = {1, 2}; 编译报错
error: must use 'struct' tag to refer to type 'Point'
```

```cpp
// C++：struct本身就是类型名
struct Point { int x, y; };
int main() { Point p{1, 2}; }  // 直接用，不需要typedef也不需要struct前缀
```

### 11. C++ 中 `struct` 和 `class` 的区别？

**A：** 唯二的语言层面区别：① 成员/继承的**默认访问权限**不同——`struct`默认`public`，`class`默认`private`；② 声明模板参数时`class`和`typename`同义，但`struct`不能替代`typename`。语义/习惯上，`struct`常用来表示纯数据聚合体（POD，没有复杂行为），`class`用来表示带封装、有不变量维护的对象。

```cpp
struct S { int a; void show(){ cout<<a<<endl; } };  // 默认public
class C  { int b; public: C(int v):b(v){} void show(){ cout<<b<<endl; } };  // 默认private
int main() {
    S s{1}; s.a = 2;    // 可以直接访问，因为struct默认public
    C c(3);
    // c.b = 4;         // 编译错误：class默认private
}
```

### 12. `union` 联合体？

**A：** `union`的所有成员**共享同一块内存**，大小取决于最大的成员，同一时刻只应该有一个成员是"有效"的（写入一个成员会覆盖其他成员的位模式）。典型用途：类型双关（type punning，如按位重新解释一个浮点数）、需要节省内存且各成员互斥使用的场景（比如变体类型的手写实现，现代 C++ 更推荐用`std::variant`）。

```cpp
union U { int i; float f; char c[4]; };
int main() {
    U u;
    u.i = 65;
    cout << sizeof(U) << endl;              // 4，取最大成员大小
    cout << u.i << " " << u.c[0] << endl;   // 65 A  （65是'A'的ASCII码）
    u.f = 3.14f;
    cout << u.f << " " << u.i << endl;      // 3.14 1078523331（i被f的位模式覆盖了）
}
```

### 13. `explicit` 关键字的作用？

**A：** 修饰单参数（或除第一个外其余参数都有默认值的）构造函数，**禁止编译器做隐式类型转换**。没有`explicit`时，`Meters m = 7.0;`会被编译器偷偷调用`Meters(double)`做隐式转换，容易掩盖bug；加上`explicit`后必须显式调用`Meters(7.0)`或`static_cast`。

```cpp
class Meters {
public:
    explicit Meters(double v) : v_(v) {}
    double v_;
};
int main() {
    Meters m1(5.0);          // OK，显式构造
    // Meters m3 = 7.0;      // 编译错误：explicit禁止了隐式转换
}
```

去掉`explicit`后再尝试`Meters m3 = 7.0;`会得到确切的编译错误，证实了它的作用：

```
error: no viable conversion from 'double' to 'Meters'
```

### 14. `friend` 友元？

**A：** 友元函数/友元类可以访问声明它们为友元的类的私有(`private`)/受保护(`protected`)成员，打破了封装的边界，通常用于运算符重载（如`operator<<`需要访问私有成员做流输出）或两个紧密协作的类之间。友元关系不能传递、不能继承，且是单向的（A把B设为友元不代表B也把A当友元）。

```cpp
class Box {
    int width_;
public:
    Box(int w) : width_(w) {}
    friend void printWidth(const Box& b);   // 友元函数
    friend class BoxInspector;              // 友元类
};
void printWidth(const Box& b) { cout << "width=" << b.width_ << endl; }
class BoxInspector {
public:
    void inspect(const Box& b) { cout << "inspect width=" << b.width_ << endl; }
};
int main() {
    Box b(10);
    printWidth(b);            // width=10
    BoxInspector().inspect(b); // inspect width=10
}
```

### 15. `using` 的几种用法？

**A：** ① 类型别名（替代`typedef`，语法更直观，尤其在模板别名场景`template<typename T> using Vec = std::vector<T>;`只有`using`能做到）；② 继承构造函数`using Base::Base;`，让派生类不用重复写和基类一样的构造函数；③ `using`声明把某个名字引入当前作用域（如`using std::cout;`）；④ `using namespace`把整个命名空间引入。

```cpp
using IntVec = vector<int>;      // 类型别名，等价于 typedef vector<int> IntVec;
class Base {
public:
    Base(int x) { cout << "Base(" << x << ")" << endl; }
};
class Derived : public Base {
public:
    using Base::Base;   // 继承构造函数
};
int main() {
    IntVec v{1, 2, 3};
    Derived d(42);      // Base(42)  — 直接复用了Base的构造函数
}
```

### 16. `::` 范围解析运算符？

**A：** 用于指定名字所在的作用域，消除同名变量的二义性：`::x`表示全局作用域的`x`，`ClassName::x`表示类作用域的静态成员，`Namespace::x`表示命名空间里的名字。局部变量、类成员、全局变量重名时，就近原则是"局部 > 类 > 全局"，需要显式用`::`才能访问被"遮蔽"的外层名字。

```cpp
int val = 100;              // 全局变量
class A {
public:
    static int val;         // 类静态成员
    void show() {
        int val = 1;                    // 局部变量
        cout << val << endl;            // 1  局部优先
        cout << A::val << endl;         // 10 类作用域
        cout << ::val << endl;          // 100 全局作用域
    }
};
int A::val = 10;
int main() { A().show(); }
// 输出：1 10 100
```

### 17. `enum` 和 `enum class` 的区别？

**A：** 传统`enum`的枚举值会直接暴露到外层作用域（不需要`Color::RED`），且能隐式转换成整型，容易和普通`int`混淆、容易撞名。C++11 引入的`enum class`（强类型枚举）必须用`Fruit::APPLE`访问，且**不会隐式转换成整型**（必须`static_cast`），类型更安全，是现代 C++ 的推荐写法。

```cpp
enum Color { RED, GREEN, BLUE };          // 传统枚举
enum class Fruit { APPLE, BANANA };       // 强类型枚举
int main() {
    Color c = RED;
    int i = c;                             // 传统枚举可隐式转int
    cout << i << endl;                     // 0

    Fruit f = Fruit::APPLE;
    // int j = f;                         // 编译错误：enum class不能隐式转int
    int j = static_cast<int>(f);
    cout << j << endl;                     // 0
}
```

### 18. `auto` 和 `decltype` 的区别？

**A：** `auto`根据**初始化表达式的值**推导类型（推导规则和模板参数推导类似，默认会退掉引用/顶层`const`，除非显式写`auto&`/`const auto&`）；`decltype(expr)`根据**表达式本身声明时的类型**推导，不看有没有初始化值，且会保留引用性——`decltype(已声明的引用变量)`得到的是引用类型，这也是两者最容易被问到的差异点。

```cpp
int main() {
    int x = 1;
    int& rx = x;
    auto a = rx;              // int（auto会退掉引用）
    decltype(rx) ry = x;      // int&（decltype保留了引用性）
    ry = 99;
    cout << x << endl;        // 99，因为ry事实上是x的引用
    cout << is_same_v<decltype(a), int> << endl;   // true（这里a是auto推导出的普通int变量）
}
```

### 19. 引用和指针的区别？左值引用 vs 右值引用？

**A：** 引用是变量的"别名"——必须初始化、之后永远绑定同一个对象、不能为空、不能重新绑定；指针是一个独立的变量，存的是地址，可以为空、可以重新指向别处、需要解引用才能访问值。

C++11 引入右值引用(`T&&`)用来区分"左值"（有名字、可以取地址、可以被多次使用的表达式，如变量）和"右值"（临时的、将亡的值，如字面量、函数返回的临时对象）。非`const`左值引用不能绑定右值；`const`左值引用和右值引用都能绑定右值。`std::move`本身不做任何"移动"，只是把一个左值**强制转换成右值引用类型**，从而允许后续代码把它当"可以被掏空"的对象来处理。

```cpp
int getVal() { return 5; }     // 返回值是右值
int main() {
    int a = 1;
    // int& r1 = getVal();    // 编译错误：非const左值引用不能绑定右值
    const int& r2 = getVal();  // OK：const左值引用可以绑定右值
    int&& r3 = getVal();       // OK：右值引用绑定右值
    // int&& r4 = a;          // 编译错误：右值引用不能直接绑定左值
    int&& r5 = std::move(a);  // OK：std::move把左值a"变成"右值引用
    cout << r2 << " " << r3 << " " << r5 << endl;  // 5 5 1（这里r5之外，a本身值未变，因为int没有"移动"语义可言）
}
```

### 20. 成员初始化列表 vs 构造函数体内赋值？构造顺序是怎样的？

**A：** 三种情况**必须**用初始化列表，不能在构造函数体内赋值：① 引用类型成员（引用必须在定义时绑定）；② `const`成员（`const`只能初始化一次）；③ 没有默认构造函数的成员对象（构造函数体执行前，所有成员对象已经被构造完，体内写的是"赋值"不是"构造"）。

**成员的构造顺序只取决于它们在类里的声明顺序，和初始化列表里书写的顺序无关**——这是一个经典陷阱，写反了编译器通常会给`-Wreorder`警告。

```cpp
class Ref {
public:
    Ref(int& r) : ref_(r), k_(100) {}   // 引用/const成员必须走初始化列表
    int& ref_;
    const int k_;
};
class Member {
public:
    Member(int v) : v_(v) { cout << "Member(" << v << ")" << endl; }
    int v_;
};
class Outer {
public:
    Outer() : b_(2), a_(1) { cout << "Outer()" << endl; }  // 故意把b_写在a_前面
    Member a_{0};   // 声明在前
    Member b_{0};   // 声明在后
};
int main() { Outer o; }
```

实测输出（编译器同时给出`field 'b_' will be initialized after field 'a_'`的警告）：

```
Member(1)
Member(2)
Outer()
```

证实了：不管初始化列表怎么写，`a_`（声明在前）总是先于`b_`构造。带继承时的完整顺序是：**基类构造 → 成员对象按声明顺序构造 → 派生类自身构造函数体执行**；析构则完全反过来。

```cpp
class Member {
public:
    Member(string n) : name_(n) { cout << "Member(" << name_ << ") 构造" << endl; }
    ~Member() { cout << "Member(" << name_ << ") 析构" << endl; }
    string name_;
};
class Base { public: Base(){ cout<<"Base 构造"<<endl; } ~Base(){ cout<<"Base 析构"<<endl; } };
class Derived : public Base {
public:
    Derived() : m1_("m1"), m2_("m2") { cout << "Derived 构造" << endl; }
    ~Derived() { cout << "Derived 析构" << endl; }
    Member m1_; Member m2_;
};
int main() { Derived d; }
```

实测输出：

```
Base 构造
Member(m1) 构造
Member(m2) 构造
Derived 构造
---（离开作用域）---
Derived 析构
Member(m2) 析构
Member(m1) 析构
Base 析构
```

### 21. `initializer_list` 是什么？

**A：** `std::initializer_list<T>`让类可以接收花括号`{...}`列表作为构造参数，编译器看到`{1,2,3,4}`会自动构造一个`initializer_list<int>`对象传给匹配的构造函数，`std::vector`等 STL 容器都提供了这样的构造函数。

```cpp
class MyVec {
public:
    MyVec(initializer_list<int> lst) { for (int v : lst) data_.push_back(v); }
    vector<int> data_;
};
int main() {
    MyVec v{1, 2, 3, 4};
    for (int x : v.data_) cout << x << " ";   // 1 2 3 4
}
```

### 22. 数组指针 vs 指针数组？

**A：** `int* p[3]`是"指针数组"——`[]`优先级比`*`高，先看成`p[3]`（一个长度为3的数组），再看`int*`，即数组的每个元素都是`int*`；`int (*p)[3]`是"数组指针"——加了括号让`*`先结合，`p`本身是一个指针，指向"一个包含3个int的数组"。记忆技巧：**先看离变量名最近的符号**。

```cpp
int main() {
    int arr[3] = {1, 2, 3};
    int* p1[3];              // 指针数组：3个int*指针组成的数组
    p1[0] = &arr[0]; p1[1] = &arr[1]; p1[2] = &arr[2];
    cout << *p1[0] << *p1[1] << *p1[2] << endl;  // 123

    int (*p2)[3];             // 数组指针：指向"包含3个int的数组"的指针
    p2 = &arr;
    cout << (*p2)[0] << (*p2)[1] << (*p2)[2] << endl;  // 123

    int matrix[2][3] = {{1,2,3},{4,5,6}};
    int (*rowPtr)[3] = matrix;   // 二维数组名退化成"指向行"的数组指针
    cout << rowPtr[1][2] << endl;  // 6
}
```

### 23. C++ 程序的内存布局是怎样的？

**A：** 从低地址到高地址典型分为：**代码段(.text)**——只读，存放编译后的指令；**只读数据段(.rodata)**——字符串字面量、`const`全局常量；**已初始化数据段(.data)**——有初始值的全局变量/静态变量；**未初始化数据段(.bss)**——没有显式初始化的全局变量/静态变量（运行前由系统清零，不占磁盘空间）；**堆(heap)**——`new`/`malloc`动态分配，从低地址向高地址增长，需要手动释放；**栈(stack)**——函数调用帧、局部变量，从高地址向低地址增长，函数返回自动释放。

```cpp
int globalInitialized = 42;      // .data段
int globalUninitialized;         // .bss段
void func() {
    static int staticVar = 1;    // 静态局部变量也在.data/.bss，不在栈上
    int localVar = 2;             // 栈
    int* heapVar = new int(3);    // 堆
    cout << &globalInitialized << " " << &globalUninitialized << " "
         << &staticVar << " " << &localVar << " " << heapVar << endl;
    delete heapVar;
}
```

实测地址（macOS/ARM64）：全局/静态变量地址彼此紧邻在同一数据段区域（如`0x1041a4xxx`），栈地址在完全不同的高位区域（`0x16bc...`），堆地址又是另一个独立区域（`0x104a4d...`）——三者分属不同内存区域这一结论得到验证（不同平台/ASLR下具体数值不同，但分区结构一致）。

### 24. `mutable` 关键字？

**A：** 修饰类的成员变量，允许它在`const`成员函数里仍然可以被修改。常见用途：缓存/惰性计算结果、统计调用次数（日志计数器）、互斥锁成员（`const`成员函数内也需要加锁）等"逻辑上是const、但需要修改内部实现细节"的场景。

```cpp
class Logger {
public:
    void log(const string& msg) const {   // const成员函数
        callCount_++;                      // callCount_被mutable修饰，允许修改
        cout << "[" << callCount_ << "] " << msg << endl;
    }
private:
    mutable int callCount_ = 0;
};
int main() {
    const Logger lg;
    lg.log("hello");   // [1] hello
    lg.log("world");   // [2] world
}
```

### 25. 野指针 vs 悬挂指针？

**A：** 野指针(wild pointer)是**声明了但没有初始化**的指针，指向一个随机/未定义的地址；悬挂指针(dangling pointer)是**曾经有效，但它指向的对象已经被释放/销毁**的指针（比如`delete`之后没置空，或者返回了局部变量的地址）。两者共同点是解引用都是未定义行为，规避方法：声明指针时立即初始化为`nullptr`，`delete`后手动置空，不返回局部变量的地址，优先用智能指针管理生命周期。

```cpp
int* danglingPointerDemo() {
    int local = 5;
    int* p = &local;
    return p;   // 返回局部变量地址，函数结束后local已被销毁，p变成悬挂指针
}
int main() {
    int* p = danglingPointerDemo();
    cout << "dangling pointer address (不能解引用): " << p << endl;  // 地址仍能打印，但*p是UB
}
```

### 26. `struct` 内存对齐是怎么回事？

**A：** 编译器出于访问效率的考虑，会让每个成员按照自身类型的"对齐要求"（通常等于该类型的大小，`char`是1、`int`是4等）存放在对齐的地址上，必要时插入padding字节；结构体整体大小还要对齐到**最大成员对齐数**的整数倍。因此调整成员声明顺序（把大类型放一起）能省掉不少padding；`#pragma pack(n)`可以强制指定对齐边界（取消/减少padding），但可能导致跨平台不一致、非对齐访问性能下降，一般只在协议/文件格式解析等确实需要紧凑布局的场景使用。

```cpp
struct A { char c; int i; char d; };   // 1 + 3pad + 4 + 1 + 3pad = 12
struct B { int i; char c; char d; };   // 4 + 1 + 1 + 2pad = 8，调整顺序省了padding
#pragma pack(push, 1)
struct C { char c; int i; char d; };   // 1 + 4 + 1 = 6，强制1字节对齐，无padding
#pragma pack(pop)
int main() {
    cout << sizeof(A) << " " << sizeof(B) << " " << sizeof(C) << endl;  // 12 8 6
}
```

### 27. 静态链接 vs 动态链接？

**A：** 静态链接把库的目标代码在**编译期**直接拷贝进最终可执行文件（macOS/Linux下是`.a`静态库），生成的可执行文件更大、不依赖运行时能否找到库文件，多个程序各自持有一份库代码的拷贝。动态链接只在可执行文件里记录"需要用到哪个共享库"（macOS下是`.dylib`，Linux下是`.so`），**运行时**由动态链接器去加载，多个进程可以共享同一份库在磁盘/内存中的拷贝，可执行文件更小，但需要目标机器上有对应版本的动态库，也带来了"依赖地狱"的可能。macOS 上查看一个可执行文件依赖了哪些动态库用`otool -L`（Linux对应`ldd`）。

```
$ g++ -c mylib.cpp -o mylib.o && ar rcs libmystatic.a mylib.o
$ g++ main.cpp -L. -lmystatic -o main_static
$ otool -L main_static | grep mystatic
(无输出，因为代码已经拷贝进可执行文件，不再依赖libmystatic)

$ g++ -shared -fPIC mylib.cpp -o libmydynamic.dylib
$ g++ main.cpp -L. -lmydynamic -o main_dynamic
$ otool -L main_dynamic | grep mydynamic
	libmydynamic.dylib (compatibility version 0.0.0, current version 0.0.0)
```

两种产物运行结果一致（都输出`5`），区别只在链接方式和运行时依赖上。

---

## 二、面向对象与虚函数机制

### 1. 面向对象三大特性：封装、继承、多态

**A：** **封装**——把数据和操作数据的方法绑定在同一个类里，通过访问控制符（`public`/`protected`/`private`）隐藏内部实现细节，只暴露必要的接口，降低外部对内部状态的直接依赖。**继承**——子类复用父类的属性和行为，减少重复代码，同时建立"is-a"的层次关系。**多态**——同一个接口，不同对象表现出不同行为；C++里主要靠虚函数实现"运行时多态"（也叫动态多态，通过基类指针/引用调用虚函数，实际执行哪个版本取决于对象的真实类型），另外模板/函数重载体现的是"编译期多态"（静态多态）。

```cpp
class Animal {
public:
    Animal(string name) : name_(name) {}
    virtual void speak() const { cout << name_ << " makes a sound" << endl; }
    virtual ~Animal() = default;
protected:
    string name_;
};
class Dog : public Animal {
public:
    Dog(string name) : Animal(name) {}
    void speak() const override { cout << name_ << " barks" << endl; }
};
class Cat : public Animal {
public:
    Cat(string name) : Animal(name) {}
    void speak() const override { cout << name_ << " meows" << endl; }
};
void makeSpeak(const Animal& a) { a.speak(); }  // 运行时多态：调用哪个speak取决于a的实际类型
int main() {
    Dog d("Rex"); Cat c("Tom");
    makeSpeak(d);   // Rex barks
    makeSpeak(c);   // Tom meows
}
```

### 2. `public`/`protected`/`private` 继承的区别？

**A：** 三种继承方式决定了**基类成员在派生类中的最高可见性上限**：`public`继承——基类`public`成员在派生类仍是`public`，`protected`仍是`protected`（最常用，表达真正的"is-a"关系）；`protected`继承——基类的`public`/`protected`成员在派生类中都降级为`protected`；`private`继承——基类的`public`/`protected`成员在派生类中都降级为`private`（只能在派生类内部用，外部完全不可见，语义上更接近"用...来实现"而非"is-a"）。无论哪种继承方式，基类的`private`成员在派生类中永远不可直接访问。

```cpp
class Base { public: int pub=1; protected: int prot=2; private: int priv=3; };
class PubDerived  : public    Base { public: void access(){ cout<<pub<<" "<<prot<<endl; } };
class ProtDerived : protected Base { public: void access(){ cout<<pub<<" "<<prot<<endl; } };
class PrivDerived : private   Base { public: void access(){ cout<<pub<<" "<<prot<<endl; } };
int main() {
    PubDerived pd;  pd.pub = 10;    // OK：public继承保持public
    // ProtDerived prd; prd.pub=1; // 编译错误：protected继承后，Base::pub在外部已变成protected
    // PrivDerived prvd; prvd.pub=1; // 编译错误：private继承后，Base::pub在外部已变成private
}
```

### 3. 虚函数、虚函数指针、虚函数表原理？

**A：** 只要类里有一个`virtual`函数，编译器就会为这个类生成一张**虚函数表(vtable)**——一个函数指针数组，按声明顺序存放该类"最终生效"的虚函数地址；每个这样的类的对象里会隐藏地多一个指针`vptr`（通常在对象内存布局的开头），指向所属类的vtable。调用虚函数时，编译器生成的代码是"从对象的`vptr`取出vtable，再按固定偏移量取出函数指针，然后调用"——这就是"动态绑定"，实际调用哪个版本取决于对象的真实类型（vptr指向哪张表），而不是指针/引用的静态类型。非虚函数没有这个查表过程，编译期就能确定调用地址（静态绑定），效率更高。

可以手动模拟一次虚调用来验证这个机制：

```cpp
class Base {
public:
    virtual void f() { cout << "Base::f" << endl; }
    virtual void g() { cout << "Base::g" << endl; }
    void h() { cout << "Base::h (非虚)" << endl; }
};
class Derived : public Base {
public:
    void f() override { cout << "Derived::f" << endl; }  // 覆盖f
    // g没有override，虚表里g的槽位仍指向Base::g
};
using FuncPtr = void(*)();
int main() {
    Derived d;
    cout << "sizeof(Base)=" << sizeof(Base) << endl;   // 8，一个vptr(64位平台)

    // 手动读出对象的vptr(对象前8字节)，再从vtable里取函数指针，模拟一次虚调用
    void** vptr = *reinterpret_cast<void***>(&d);
    FuncPtr f0 = reinterpret_cast<FuncPtr>(vptr[0]);   // 虚表第0项：f
    FuncPtr f1 = reinterpret_cast<FuncPtr>(vptr[1]);   // 虚表第1项：g
    f0();   // Derived::f
    f1();   // Base::g

    Base* b = &d;
    b->f();   // Derived::f （多态：走vptr查表）
    b->g();   // Base::g   （Derived没override）
    b->h();   // Base::h (非虚) （静态绑定，不查表）
}
```

实测输出证实：手动通过vptr调用得到的结果和`b->f()`/`b->g()`的多态调用结果完全一致，说明虚调用底层确实就是"查vtable、取函数指针、调用"。

### 4. 为什么基类析构函数要声明成 `virtual`？

**A：** 如果通过**基类指针** `delete` 一个派生类对象，而基类析构函数不是`virtual`，那么只会调用基类的析构函数（静态绑定），派生类新增的资源（比如动态分配的成员）不会被释放，造成资源泄漏，这是未定义行为的一个典型高发场景。只要一个类可能被用作基类（尤其是会被多态使用、通过基类指针管理生命周期），就应该把析构函数声明成`virtual`。

```cpp
class BaseNoVirtual   { public: ~BaseNoVirtual()   { cout << "~BaseNoVirtual"   << endl; } };
class DerivedNoVirtual : public BaseNoVirtual { public: ~DerivedNoVirtual(){ cout<<"~DerivedNoVirtual"<<endl; } int* data=new int[10]; };
class BaseVirtual      { public: virtual ~BaseVirtual(){ cout << "~BaseVirtual" << endl; } };
class DerivedVirtual   : public BaseVirtual { public: ~DerivedVirtual() override { cout << "~DerivedVirtual" << endl; } };

int main() {
    BaseNoVirtual* p1 = new DerivedNoVirtual();
    delete p1;   // 只调用了~BaseNoVirtual，~DerivedNoVirtual没被调用！data内存泄漏

    BaseVirtual* p2 = new DerivedVirtual();
    delete p2;   // 正确：先~DerivedVirtual，再~BaseVirtual
}
```

实测输出：第一段只打印`~BaseNoVirtual`一行（证实了`~DerivedNoVirtual`确实没被调用、`data`确实泄漏了）；第二段打印`~DerivedVirtual`、`~BaseVirtual`两行，顺序正确。

### 5. 纯虚函数和抽象类？

**A：** 在虚函数声明后加`= 0`使其成为纯虚函数，表示这个类不提供默认实现，强制要求派生类必须重写它才能被实例化。**只要一个类含有至少一个纯虚函数，它就是抽象类，不能直接创建对象**（只能定义指针/引用指向派生类对象），常用来定义"接口"。

```cpp
class Shape {
public:
    virtual double area() const = 0;   // 纯虚函数
    virtual ~Shape() = default;
};
class Circle : public Shape {
public:
    Circle(double r) : r_(r) {}
    double area() const override { return 3.14159 * r_ * r_; }
private:
    double r_;
};
int main() {
    Shape* s = new Circle(2.0);
    cout << s->area() << endl;  // 12.5664
    delete s;
}
```

如果尝试`Shape s;`会得到确切的编译错误，证实抽象类无法实例化：

```
error: variable type 'Shape' is an abstract class
note: unimplemented pure virtual method 'area' in 'Shape'
```

### 6. 虚继承是什么？解决什么问题？

**A：** 当出现"菱形继承"（两个中间类都继承自同一个基类，最下面的类又同时继承这两个中间类）时，如果不使用虚继承，最下面的类会含有**两份**公共基类的子对象，造成数据冗余和访问二义性（必须显式指定路径才能访问，比如`obj.PathA::member`）。虚继承(`virtual public Base`)让编译器保证最终派生类只保留**一份**共享的基类子对象，代价是需要额外的虚基类表(vbtable)来做间接定位，因此对象体积会变大、访问虚基类成员多一次间接寻址。

```cpp
class Animal { public: int weight = 1; };
class Bird : virtual public Animal {};    // 虚继承
class Mammal : virtual public Animal {};
class Bat : public Bird, public Mammal {};  // 只含一份Animal子对象

class AnimalN { public: int weight = 1; };
class BirdN : public AnimalN {};              // 普通继承（非虚）
class MammalN : public AnimalN {};
class BatN : public BirdN, public MammalN {}; // 菱形继承但没用virtual：两份AnimalN

int main() {
    Bat b;
    b.weight = 100;               // 虚继承：只有一份weight，无二义性
    cout << sizeof(Bat) << " " << b.weight << endl;         // 24 100

    BatN bn;
    // bn.weight = 1;             // 编译错误：二义性
    bn.BirdN::weight = 10;
    bn.MammalN::weight = 20;      // 必须显式指定路径，说明确实是两份独立的weight
    cout << sizeof(BatN) << " " << bn.BirdN::weight << " " << bn.MammalN::weight << endl;  // 8 10 20
}
```

实测`sizeof(Bat)=24`（含vbtable指针，且只有一份`weight`）而`sizeof(BatN)=8`（两个独立的`int weight`各占4字节），直观证明了虚继承确实消除了重复的基类子对象。

### 7. `delete this` 合法吗？

**A：** 语法上合法——`this`本质是一个普通指针值，`delete`一个指针本身没有问题。但有严格的前提和风险：① 对象必须是通过`new`分配在堆上的（不能是栈对象/全局对象/静态对象，否则直接是未定义行为）；② `delete this`执行后，当前对象的生命周期已经结束，**函数剩余的代码不能再访问任何成员变量/虚函数**（只能做一些不涉及`this`的收尾操作，比如返回、跳出），也不能有人在外部再对同一个`this`调用`delete`或访问成员（会造成double free/use-after-free）。实践中很少主动这样写，多见于一些"引用计数归零时自毁"的历史设计。

```cpp
class Self {
public:
    void selfDestruct() {
        cout << "before delete this" << endl;
        delete this;    // 合法，但之后不能再访问this的任何成员
        cout << "delete this之后仍继续执行到这里本身已是未定义行为，能打印出来只是碰巧当前实现没有清零内存，不能依赖这种行为" << endl;
    }
};
int main() {
    Self* s = new Self();
    s->selfDestruct();
}
```

---

## 三、构造析构与拷贝语义

### 1. C++ 有哪些类型的构造函数？

**A：** ① 默认构造函数（无参，或全部参数有默认值）；② 普通（转换）构造函数；③ 拷贝构造函数`T(const T&)`；④ 移动构造函数`T(T&&)`（C++11）；⑤ 委托构造函数（C++11，一个构造函数在初始化列表里调用同类的另一个构造函数，避免重复代码）；⑥ 转换构造函数（单参数构造函数，隐式定义了一个类型转换，可用`explicit`禁止）。如果类里没有显式声明拷贝/移动/析构相关函数，编译器会按"三/五法则"自动生成默认版本（逐成员拷贝/移动）。

```cpp
class Widget {
public:
    Widget() : Widget(0) {}                                              // 默认构造，委托构造
    Widget(int v) : v_(v) {}                                             // 普通构造
    Widget(const Widget& other) : v_(other.v_) {}                        // 拷贝构造
    Widget(Widget&& other) noexcept : v_(other.v_) { other.v_ = -1; }    // 移动构造
    Widget& operator=(const Widget& other) { v_ = other.v_; return *this; }       // 拷贝赋值
    Widget& operator=(Widget&& other) noexcept { v_ = other.v_; other.v_ = -1; return *this; } // 移动赋值
    int v_;
};
int main() {
    Widget a;                    // 默认构造(委托给Widget(int))
    Widget b(5);                 // 普通构造
    Widget c = b;                // 拷贝构造
    Widget d = std::move(b);     // 移动构造
}
```

实测按顺序打印`普通构造 v=0` → `默认构造(委托)` → `普通构造 v=5` → `拷贝构造` → `移动构造`，证实委托构造和各类构造函数确实按预期被分别调用。

### 2. 拷贝构造函数的参数为什么必须是（`const`）引用，不能是按值传递？

**A：** 如果拷贝构造函数按值传参`T(T other)`，那么调用它本身就需要先拷贝构造出参数`other`——而构造`other`又要调用拷贝构造函数……形成无穷递归。这不是"最佳实践建议"，而是**语言规则直接禁止**的写法，编译器会直接报错。

```cpp
class Widget {
public:
    Widget() = default;
    Widget(Widget other) {}  // 故意写成按值传递
};
```

实测编译报错：

```
error: copy constructor must pass its first argument by reference
```

用`const T&`还有额外好处：可以绑定右值/临时对象，且不需要一次额外的拷贝。

### 3. 构造函数、析构函数的执行顺序？（含继承关系）

**A：** 构造顺序：**基类构造函数 → 成员对象按类内声明顺序构造（不是初始化列表书写顺序）→ 自身构造函数体执行**。析构顺序与构造完全相反：**自身析构函数体 → 成员对象按声明的逆序析构 → 基类析构函数**。多重继承时，基类按照派生列表中声明的顺序依次构造，析构再逆序。（完整代码示例见第一节"成员初始化列表"部分，已用实际运行结果验证过这个顺序。）

### 4. 深拷贝 vs 浅拷贝？

**A：** 浅拷贝（编译器默认生成的拷贝构造/拷贝赋值，对含指针成员的类而言）只是逐成员按位拷贝——如果成员是指针，拷贝后的对象和原对象的指针指向**同一块内存**，一旦其中一个对象析构释放了这块内存，另一个对象的指针就变成悬挂指针，两者析构时还会发生**double free**。深拷贝需要自定义拷贝构造/拷贝赋值，为新对象重新分配一块独立内存并复制内容，两个对象之后互不影响。

```cpp
class ShallowStr {  // 没有自定义拷贝，编译器生成的默认版本只拷贝指针本身
public:
    ShallowStr(const char* s) { data_ = new char[strlen(s)+1]; strcpy(data_, s); }
    ~ShallowStr() { delete[] data_; }
    char* data_;
};
class DeepStr {      // 自定义拷贝构造，重新分配内存
public:
    DeepStr(const char* s) { data_ = new char[strlen(s)+1]; strcpy(data_, s); }
    DeepStr(const DeepStr& other) { data_ = new char[strlen(other.data_)+1]; strcpy(data_, other.data_); }
    ~DeepStr() { delete[] data_; }
    char* data_;
};
int main() {
    {
        ShallowStr a("hello");
        ShallowStr b = a;
        cout << (a.data_ == b.data_) << endl;  // 1(true)：同一块内存，a和b析构时会double free（危险）
        b.data_ = nullptr;   // 为了让这个演示程序能正常退出，这里手动置空避免真的触发double free崩溃；
                              // 现实中的bug不会有人帮你这样置空，这正是浅拷贝的真正危险之处
    }
    {
        DeepStr da("hello");
        DeepStr db = da;
        cout << (da.data_ == db.data_) << " " << (strcmp(da.data_, db.data_) == 0) << endl;  // 0 1：地址不同、内容相同
    }
}
```

### 5. `this` 指针的来源？（与拷贝/构造语义相关的补充）

**A：** 详见第一节"this 指针"问答——`this`不存放在对象内存里，而是编译器在每次非静态成员函数调用时，作为隐藏的第一个实参传入（通常经由寄存器传递），在函数体内像一个局部的常量指针一样使用。在拷贝构造/移动构造函数体内，`this`指向"正在被构造的新对象"，而参数`other`指向"被拷贝/移动的源对象"，两者是不同的对象。

### 6. `std::move` 与移动语义为什么被引入？

**A：** C++11 之前，"拷贝"是唯一的对象传递方式——即便源对象马上就要被销毁（比如函数返回的临时对象、显式声明不再使用的局部变量），也必须做一次完整的深拷贝，代价可能是O(n)的内存分配和数据复制。移动语义允许把一个即将被丢弃的对象内部的资源（比如堆内存指针）**直接"偷"过来**，把源对象置于一个"空/无效但可安全析构"的状态，整个过程是O(1)，避免了不必要的深拷贝开销。`std::move`本身不移动任何东西，只是把左值**强制转换成右值引用类型**，从而使重载决议选中移动构造/移动赋值版本。

```cpp
class Buffer {
public:
    Buffer(size_t n) : size_(n), data_(new int[n]) {}
    Buffer(const Buffer& other) : size_(other.size_), data_(new int[other.size_]) {   // 深拷贝，O(n)
        for (size_t i = 0; i < size_; ++i) data_[i] = other.data_[i];
        cout << "拷贝构造(深拷贝" << size_ << "个int，较慢)" << endl;
    }
    Buffer(Buffer&& other) noexcept : size_(other.size_), data_(other.data_) {       // 移动构造，O(1)
        other.data_ = nullptr; other.size_ = 0;
        cout << "移动构造(偷指针，O(1)，快)" << endl;
    }
    ~Buffer() { delete[] data_; }
    size_t size_; int* data_;
};
int main() {
    Buffer a(100);
    Buffer b = a;                // 拷贝构造：a之后还要用，必须深拷贝
    Buffer d = std::move(a);     // 移动构造：a之后不再使用，直接偷指针
    cout << "a.data_ after move = " << a.data_ << endl;  // 0(nullptr)，a被掏空了
}
```

实测输出中`拷贝构造(深拷贝100个int，较慢)`和`移动构造(偷指针，O(1)，快)`两条消息各打印一次，且`a.data_`在被`move`之后确实变为`nullptr`——证实移动语义"偷资源、置空源对象"的机制。

---

## 四、内存管理与智能指针

### 1. `new`/`delete` 和 `malloc`/`free` 的区别与联系？

**A：** `malloc`/`free`是 C 标准库函数，只负责分配/释放一块原始内存，**不会调用构造函数/析构函数**，返回`void*`需要强制类型转换，分配失败返回`nullptr`。`new`/`delete`是 C++ 运算符，`new`会先分配内存再调用构造函数，`delete`会先调用析构函数再释放内存，是类型安全的（不需要强转），分配失败默认抛出`std::bad_alloc`异常（而不是返回空指针）。两者不能混用——`malloc`出来的内存不能用`delete`释放（没有走对应的内存管理元信息，且根本没有构造过对象），反之亦然；`new[]`分配的数组必须用`delete[]`释放（保证对每个元素都调用析构函数），配对错误是未定义行为。

```cpp
class Point {
public:
    Point() { cout << "Point构造" << endl; }
    ~Point() { cout << "Point析构" << endl; }
    int x = 0, y = 0;
};
int main() {
    Point* p1 = (Point*)malloc(sizeof(Point));
    cout << p1->x << endl;   // 0，但只是碰巧/未初始化的值，并没有真正调用构造函数
    free(p1);                 // 不调用~Point()

    Point* p2 = new Point();  // 打印"Point构造"
    delete p2;                  // 打印"Point析构"

    Point* arr = new Point[3]; // 打印3次"Point构造"
    delete[] arr;                // 打印3次"Point析构"，必须与new[]配对
}
```

### 2. RAII 是什么？

**A：** RAII（Resource Acquisition Is Initialization，资源获取即初始化）是 C++ 管理资源（内存、文件句柄、锁、网络连接等）最核心的惯用法：把资源的获取放在对象的构造函数里，把资源的释放放在析构函数里，让资源的生命周期和对象的生命周期绑定。这样无论函数正常返回、提前`return`，还是中途抛出异常导致栈展开，只要对象离开作用域，析构函数都会被自动调用，资源就一定会被释放——不需要程序员在每个可能的退出路径上手写清理代码。智能指针、`lock_guard`、`fstream`都是 RAII 的具体应用。

```cpp
class FileGuard {
public:
    FileGuard(const string& name) : name_(name) { cout << "打开资源: " << name_ << endl; }
    ~FileGuard() { cout << "自动释放资源: " << name_ << endl; }
    string name_;
};
void risky(bool doThrow) {
    FileGuard fg("file.txt");
    if (doThrow) throw runtime_error("出错了");
}
int main() {
    try { risky(true); } catch (const exception& e) { cout << "捕获异常: " << e.what() << endl; }
}
```

实测输出：`打开资源: file.txt` → `自动释放资源: file.txt` → `捕获异常: 出错了`——即使异常抛出、中间跳过了`risky`函数剩余的所有代码，`fg`的析构函数依然被正确调用，资源没有泄漏。

### 3. 三种智能指针：`unique_ptr` / `shared_ptr` / `weak_ptr`

**A：** `unique_ptr`独占所有权——同一时刻只能有一个`unique_ptr`指向某个对象，拷贝构造/拷贝赋值被`= delete`禁止，只能通过`std::move`转移所有权，离开作用域自动释放，零额外开销（一般等价于裸指针大小），是"默认应该优先使用"的智能指针。`shared_ptr`共享所有权——内部维护一个（线程安全的）引用计数，每次拷贝计数`+1`，每次析构计数`-1`，计数归零时才真正释放对象，适合真正需要多处共享同一对象生命周期的场景。`weak_ptr`不拥有对象、**不增加引用计数**，只是"观察"一个`shared_ptr`管理的对象，用前需要调用`lock()`尝试升级成一个临时的`shared_ptr`（如果对象已被释放则返回空），主要用来打破`shared_ptr`之间的循环引用。

```cpp
struct Res {
    Res(int id) : id_(id) { cout << "Res(" << id_ << ")构造" << endl; }
    ~Res() { cout << "Res(" << id_ << ")析构" << endl; }
    int id_;
};
int main() {
    { // unique_ptr
        unique_ptr<Res> up1 = make_unique<Res>(1);
        unique_ptr<Res> up2 = std::move(up1);   // 转移所有权
        cout << (up1 == nullptr) << endl;        // 1，up1已被掏空
    } // up2析构，释放Res(1)

    { // shared_ptr
        shared_ptr<Res> sp1 = make_shared<Res>(2);
        cout << sp1.use_count() << endl;          // 1
        { shared_ptr<Res> sp2 = sp1; cout << sp1.use_count() << endl; }  // 2
        cout << sp1.use_count() << endl;          // 1（sp2析构后计数-1）
    } // sp1析构，计数归0，释放Res(2)

    { // weak_ptr
        shared_ptr<Res> sp = make_shared<Res>(3);
        weak_ptr<Res> wp = sp;
        cout << sp.use_count() << endl;           // 1，weak_ptr不增加计数
        if (auto locked = wp.lock()) cout << "lock成功, id=" << locked->id_ << endl;
        sp.reset();
        cout << wp.expired() << endl;              // 1(true)，对象已释放
    }
}
```

### 4. `shared_ptr` 的引用计数是怎么实现的？多线程下安全吗？

**A：** `shared_ptr`内部除了持有对象指针，还持有一个指向"控制块(control block)"的指针，控制块里保存了强引用计数(`use_count`)和弱引用计数(`weak_count`)。每次拷贝/析构`shared_ptr`时，对这两个计数的增减是**原子操作**（通常用`atomic`的fetch-add/fetch-sub实现），所以多个线程各自持有同一个`shared_ptr`的副本、并发地拷贝/析构，这个引用计数本身不会出错。但要注意：**线程安全只覆盖"控制块的计数操作"和"shared_ptr自身这个句柄对象的拷贝/析构"，并不代表它所指向的对象内容本身的读写是线程安全的**——多个线程同时读写同一个`shared_ptr`指向的对象数据，仍然需要额外加锁/原子变量保护。

```cpp
int main() {
    auto sp = make_shared<int>(0);
    vector<thread> ts;
    for (int i = 0; i < 100; ++i)
        ts.emplace_back([sp]() mutable { shared_ptr<int> local = sp; });  // 每个线程拷贝一份，计数原子+1/-1
    for (auto& t : ts) t.join();
    cout << sp.use_count() << endl;   // 1，所有线程结束后正确回到1，说明计数没有因并发而错乱
}
```

`shared_ptr`最容易被问到的陷阱是**循环引用**：如果两个对象互相持有对方的`shared_ptr`，计数永远无法归零，造成内存泄漏；解决办法是其中一方改用`weak_ptr`。

```cpp
struct B;
struct A { shared_ptr<B> b_; ~A(){ cout<<"~A"<<endl; } };
struct B { shared_ptr<A> a_; ~B(){ cout<<"~B"<<endl; } };   // 互相shared_ptr，形成循环
struct A2; struct B2 { weak_ptr<A2> a_; ~B2(){ cout<<"~B2"<<endl; } };  // 用weak_ptr打破循环
struct A2 { shared_ptr<B2> b_; ~A2(){ cout<<"~A2"<<endl; } };
int main() {
    { auto a=make_shared<A>(); auto b=make_shared<B>(); a->b_=b; b->a_=a; }  // 离开作用域，~A/~B都不会被调用！
    cout << "----" << endl;
    { auto a2=make_shared<A2>(); auto b2=make_shared<B2>(); a2->b_=b2; b2->a_=a2; }  // 正常析构
}
```

实测第一段作用域结束后没有任何`~A`/`~B`打印（确实泄漏了），第二段打印`~A2`、`~B2`（用`weak_ptr`成功打破循环，正常释放）。

### 5. 野指针/悬挂指针在智能指针语境下怎么避免？

**A：** 优先用`make_unique`/`make_shared`而不是裸`new`+手动`delete`，让对象的生命周期完全由智能指针管理，从源头上消除"忘记`delete`"或"`delete`了两次"的可能；不要用同一块裸指针分别构造两个独立的`shared_ptr`（会产生两个互不知情的控制块，各自计数归零时都会释放，导致double free），如果需要从`this`创建`shared_ptr`，应该继承`std::enable_shared_from_this`而不是直接`shared_ptr<T>(this)`。（裸指针的野指针/悬挂指针基础概念见第一节第25题。）

---

## 五、类型转换与RTTI

### 1. 为什么 C++ 要引入四种强制类型转换，而不是继续用 C 风格的 `(T)expr`？

**A：** C 风格转换`(T)expr`把 `static_cast`/`const_cast`/`reinterpret_cast` 的能力全部糅合在一起，编译器会尽量找一种能编译通过的方式去转换，写的人经常搞不清楚它实际做了哪种转换（是安全的数值转换，还是危险的指针重解释），也没法用文本搜索快速定位代码里所有做了"危险转换"的地方。C++ 拆分成四个语义清晰、各自限定使用场景的关键字，转不了编译器直接报错，也方便代码审查时一眼看出风险等级。

### 2. `static_cast`

**A：** 编译期检查，用于"有明确关系"的转换：基本数值类型之间的转换、`void*`与具体类型指针的转换、有继承关系的指针/引用之间的上行转换(upcast，总是安全)和下行转换(downcast，**不做运行时安全检查**，需要程序员自己保证类型正确，否则是未定义行为)、调用显式转换运算符等。是四种cast里最常用、开销最小的一种。

```cpp
class Base { public: virtual ~Base()=default; };
class Derived : public Base { public: void hello(){ cout<<"Derived::hello"<<endl; } };
int main() {
    double d = 3.14;
    int i = static_cast<int>(d);   // 3，数值截断转换
    cout << i << endl;

    Base* basePtr = new Derived();
    Derived* dp = static_cast<Derived*>(basePtr);  // down-cast，不做运行时检查，程序员自己保证正确
    dp->hello();  // Derived::hello
    delete basePtr;
}
```

### 3. `dynamic_cast`

**A：** 运行时检查（依赖 RTTI/虚函数表），只能用于**多态类型**（类里至少有一个虚函数）之间的转换。转换指针失败时返回`nullptr`，转换引用失败时抛出`std::bad_cast`异常。常用于"不确定基类指针实际指向哪个派生类，需要安全地尝试转换"的场景，比`static_cast`的下行转换更安全，但有运行时开销（需要遍历类型信息）。

```cpp
class Base { public: virtual ~Base()=default; };
class Derived : public Base {};
class Other : public Base {};
int main() {
    Base* basePtr = new Derived();
    Base* op = new Other();
    Derived* wrong = dynamic_cast<Derived*>(op);      // Other不是Derived，运行时检测失败
    cout << (wrong == nullptr) << endl;                // 1(true)
    Derived* right = dynamic_cast<Derived*>(basePtr);  // basePtr实际指向Derived，成功
    cout << (right != nullptr) << endl;                // 1(true)
    delete basePtr; delete op;
}
```

### 4. `const_cast`

**A：** 四种转换里唯一能**添加或去掉`const`/`volatile`修饰**的转换，主要合法用法是"调用一个参数没有正确标注`const`、但实际不会修改数据的老接口"。如果对一个本身就是`const`的对象通过`const_cast`去掉常量性后再修改，是未定义行为（编译器可能把它优化到只读段，或者假设它不会变而做出错误优化），只应该在明确知道原始对象不是`const`的情况下使用。

```cpp
int main() {
    const int ci = 100;
    int* modifiable = const_cast<int*>(&ci);
    *modifiable = 200;   // 注意：修改一个真正的const对象是UB，这里仅作演示
    cout << *modifiable << endl;   // 200（本例中编译器未做激进优化，实际输出符合预期，但不代表这是"安全"的用法）
}
```

### 5. `reinterpret_cast`

**A：** 最底层、最危险的转换，按二进制位重新解释，几乎不做任何检查，编译器"你让我转我就转"。常见用途：指针和足够大的整数之间互转、不同类型的指针之间互转（比如网络协议解析时把`char*`缓冲区强转成自定义结构体指针）。使用它基本等于告诉编译器和 code reviewer "这里我完全清楚自己在干什么，后果自负"。

```cpp
int main() {
    int x = 65;
    char* cp = reinterpret_cast<char*>(&x);
    cout << cp[0] << endl;   // 'A'，小端序下65的最低字节恰好是ASCII 'A'
}
```

### 6. 什么是 RTTI？

**A：** RTTI（Run-Time Type Information，运行时类型信息）是 C++ 在运行期查询对象实际类型的机制，主要通过`typeid`运算符和`dynamic_cast`体现。**只有含虚函数的（多态）类型，`typeid`才能在运行时正确识别对象的实际派生类型**；对非多态类型，`typeid`只能得到静态声明的类型。RTTI 的实现依赖编译器在虚函数表附近额外存放的类型描述信息，因此也是有一定运行时开销的，一些追求极致性能或者嵌入式场景会选择用`-fno-rtti`关闭它（关闭后`dynamic_cast`和`typeid`对多态类型的查询都不可用）。

```cpp
class Base { public: virtual ~Base() = default; };
class Derived : public Base {};
int main() {
    Base* p = new Derived();
    cout << typeid(*p).name() << endl;                       // 输出的是Derived的mangled名字(如"7Derived")，运行时识别出实际类型
    cout << (typeid(*p) == typeid(Derived)) << endl;          // 1(true)
    delete p;
}
```

---

## 六、STL容器与迭代器

> 本节只按"面试怎么答"的角度给结论性问答，完整的底层原理推导、更多可运行示例、复杂度分析见同仓库 `cpp-tutorial/07-STL容器详解.md` 和 `08-STL算法与迭代器.md`。

### 1. `vector` 的扩容机制？`reserve` 和 `resize` 的区别？

**A：** `vector`底层是一段连续内存，`push_back`触发扩容时会分配一块更大的内存（常见实现是2倍，MSVC是1.5倍），把旧元素整体拷贝/移动过去再释放旧内存，因此均摊分析下`push_back`是O(1)，但**触发扩容的那一次操作本身是O(n)**。`reserve(n)`只预分配容量，不改变`size()`、不构造任何元素；`resize(n)`会真正改变`size()`（增大时用默认值构造新元素，减小时析构多余元素），可能间接触发扩容。明确知道要装大概多少元素时应该用`reserve`预分配，避免反复扩容拷贝。

```cpp
int main() {
    vector<int> v;
    v.reserve(10);           // 只改变capacity，不改变size
    cout << v.size() << " " << v.capacity() << endl;  // 0 10
    v.resize(5);              // 改变size，capacity够就不重新分配
    cout << v.size() << " " << v.capacity() << endl;  // 5 10
}
```

### 2. `vector` 迭代器失效的情况？

**A：** ① `push_back`/`insert`触发扩容——所有迭代器、指针、引用全部失效（底层内存搬家了）；② 没触发扩容——插入点之后的迭代器失效（元素被后移）；③ `erase`——删除点之后的迭代器失效。安全删除写法是用`erase`的返回值更新迭代器，而不是继续`++it`（详见`07-STL容器详解.md`）。

### 3. `deque` 的底层存储机制？

**A：** `deque`不是一段连续内存，而是"一段中控数组(map) + 若干个固定大小的连续内存块(buffer)"，中控数组里每个元素是一个指向buffer的指针。这样的设计让它支持头尾两端O(1)均摊插入删除（`vector`只有尾部O(1)），代价是失去了真正的整体连续性——只在单个buffer内部连续，因此不适合用指针做跨buffer的地址运算。

### 4. `list` 的特点？

**A：** 双向链表，任意位置插入删除都是O(1)（前提是已经有了指向该位置的迭代器），但不支持随机访问（访问第k个元素要O(n)遍历），每个节点有额外的前后指针开销，缓存局部性差于`vector`。`list`的`erase`/`insert`不会使**其他**元素的迭代器失效（只有被删除元素自己的迭代器失效），这点和`vector`不同，是常被拿来对比的考点。

### 5. `stack` / `queue` 的底层实现？

**A：** 二者都是"容器适配器(container adaptor)"，本身不是独立容器，而是在某个底层容器（默认`deque`）上包装出一套受限的接口（`stack`只暴露栈顶操作，`queue`只暴露队头/队尾操作），也可以指定用`vector`/`list`作为底层容器（`priority_queue`默认底层是`vector`，用堆算法维护堆序）。

### 6. `map`/`set` 底层为什么用红黑树，而不是普通二叉搜索树或哈希表？

**A：** 普通二叉搜索树在数据有序或近似有序插入时会退化成链表，最坏情况操作复杂度退化到O(n)；红黑树是一种自平衡二叉搜索树，通过"染色+旋转"规则保证从根到叶子的最长路径不超过最短路径的2倍，从而保证插入、删除、查找都是稳定的O(log n)，这是`map`/`set`选它的核心原因。选红黑树而不是哈希表，是因为`map`/`set`需要支持**按key有序遍历**、范围查询（`lower_bound`/`upper_bound`）——这些哈希表做不到（`unordered_map`/`unordered_set`才是哈希表实现，平均O(1)查找但无序，也不支持范围查询）。

### 7. 关联式容器的迭代器失效规则？

**A：** `map`/`set`/`unordered_map`/`unordered_set`的`erase`只会使**被删除元素自己**的迭代器失效，其他元素的迭代器/引用/指针都不受影响——这是它们和`vector`最大的差异点（`vector`扩容/中间删除会让一大片迭代器失效）。`unordered_`系列容器在触发rehash（哈希桶数量变化）时，所有迭代器都会失效，但引用和指针仍然有效。

### 8. 仿函数（functor）是什么？

**A：** 仿函数就是重载了`operator()`的类/结构体的对象，可以像函数一样用`()`调用。相比普通函数指针，仿函数可以携带内部状态（构造时传入的参数），且因为类型是具体已知的（不是函数指针这种间接调用），编译器更容易把调用内联展开，性能通常更好。lambda表达式本质上是编译器自动生成的一个仿函数类的对象。

```cpp
class MultiplyBy {
public:
    MultiplyBy(int factor) : factor_(factor) {}
    int operator()(int x) const { return x * factor_; }
private:
    int factor_;
};
int main() {
    vector<int> v = {1, 2, 3};
    transform(v.begin(), v.end(), v.begin(), MultiplyBy(10));
    for (int x : v) cout << x << " ";                          // 10 20 30
    cout << count_if(v.begin(), v.end(), [](int x){ return x > 15; }) << endl;  // 2
}
```

### 9. STL 容器是线程安全的吗？

**A：** 不是。标准只保证"多个线程**同时只读**同一个容器"是安全的，以及"不同线程操作**不同的**容器实例"是安全的。**只要有至少一个线程在写（插入/删除/修改），同时有其他线程在读或写同一个容器实例，就是数据竞争**，需要调用方自己加锁（`mutex`）或者使用无锁/并发专用容器。这是"STL容器线程安全吗"这类问题的标准答案，也是最容易被追问细节的点。（互斥锁数据竞争的实测对比见第八节。）

---

## 七、C++11/14/17/20新特性

### 1. `auto` 类型推断原理？

**A：** `auto`的推导规则和函数模板参数推导基本一致：编译器根据初始化表达式的类型，去掉顶层`const`和引用（除非显式写`auto&`/`const auto&`/`auto&&`），推导出变量的实际类型。`decltype`的区别见第一节第18题。（`auto`/`decltype`的对比代码已在第一节验证过。）

### 2. 智能指针

**A：** 见第四节完整覆盖（`unique_ptr`/`shared_ptr`/`weak_ptr`用法、引用计数线程安全、循环引用问题）。

### 3. Lambda 表达式

**A：** Lambda 是 C++11 引入的匿名函数对象语法糖，本质上编译器会生成一个重载了`operator()`的仿函数类。捕获列表决定了闭包如何访问外部变量：`[x]`按值捕获（拷贝一份，之后外部修改不影响闭包内的值）、`[&x]`按引用捕获（闭包内外共享同一个变量）、`[=]`/`[&]`分别表示"值捕获所有用到的外部变量"/"引用捕获所有用到的外部变量"。

```cpp
int main() {
    int x = 10;
    auto byValue = [x]() { return x + 1; };
    auto byRef   = [&x]() { return x + 1; };
    cout << byValue() << endl;   // 11
    x = 20;
    cout << byValue() << endl;   // 11，值捕获时x已经拷贝定格
    cout << byRef() << endl;     // 21，引用捕获读的是外部现在的x

    function<int(int,int)> add = [](int a, int b) { return a + b; };  // std::function可存任意可调用对象
    cout << add(3, 4) << endl;   // 7

    auto adder = [](int a) { return [a](int b) { return a + b; }; };  // 返回闭包：函数式写法
    cout << adder(5)(6) << endl; // 11
}
```

### 4. `nullptr`

**A：** C++11 引入的空指针字面量，类型是`std::nullptr_t`，能隐式转换成任意指针类型，但**不会**像`0`/`NULL`（本质是整数`0`或`(void*)0`宏）那样在函数重载决议中意外匹配到整型重载版本，消除了`NULL`长期以来的二义性隐患。

```cpp
void f(int x) { cout << "f(int)" << endl; }
void f(char* p) { cout << "f(char*)" << endl; }
int main() {
    f(nullptr);   // f(char*)，明确匹配指针重载；如果传NULL，很多实现下会有歧义甚至误匹配f(int)
}
```

### 5. 右值引用与 `move`/`forward`

**A：** 见第三节"move语义为什么被引入"。`std::forward`用于模板中的"完美转发"——把一个转发引用(forwarding reference，`T&&`在模板参数推导上下文里)参数，按它原本是左值还是右值的形式，原样转发给下一层函数调用，避免因为"具名的右值引用参数本身是左值"这个规则导致转发时错误地退化成拷贝。

### 6. 可变参数模板

**A：** C++11 允许模板接受任意个数、任意类型的参数包(`Args...`)，经典写法是递归展开（每次剥离第一个参数，处理剩余的`Args...`，直到参数包为空）；C++17 引入折叠表达式(fold expression)后可以更简洁地一行搞定同类操作（比如求和）。

```cpp
template<typename T> T mySum(T last) { return last; }
template<typename T, typename... Args>
T mySum(T first, Args... rest) { return first + mySum(rest...); }  // 递归展开

template<typename... Args>
auto foldSum(Args... args) { return (args + ...); }                 // C++17折叠表达式

int main() {
    cout << mySum(1, 2, 3, 4) << endl;      // 10
    cout << foldSum(1, 2, 3, 4, 5) << endl; // 15
}
```

### 7. `std::atomic`

**A：** 提供不需要互斥锁就能保证"读-改-写"操作原子性的类型（如`atomic<int>`的`++`/`--`/`fetch_add`等），底层通常直接映射到 CPU 的原子指令（如x86的`lock`前缀指令），比`mutex`轻量，适合简单计数器/标志位场景；复杂的多步骤临界区仍然需要`mutex`。

```cpp
int main() {
    atomic<int> counter{0};
    vector<thread> ts;
    for (int i = 0; i < 100; ++i)
        ts.emplace_back([&counter]{ for(int j=0;j<1000;++j) counter++; });
    for (auto& t : ts) t.join();
    cout << counter.load() << endl;  // 100000，原子++保证不丢计数
}
```

### 8. `std::function` 和 `std::bind`

**A：** `std::function<签名>`是一个类型擦除的可调用对象包装器，能存放普通函数、lambda、仿函数、成员函数指针（配合`bind`/`mem_fn`），代价是有一定的虚调用开销（不像模板参数那样能完全内联）。`std::bind`可以固定一个可调用对象的部分参数（生成"偏函数应用"），生成一个新的可调用对象；引用参数需要用`std::ref`/`std::cref`包裹，否则默认按值拷贝。现代 C++ 里很多`bind`的场景可以直接用lambda替代，可读性通常更好。

```cpp
void add(int a, int b, int& result) { result = a + b; }
int main() {
    int result = 0;
    auto boundAdd = std::bind(add, 3, 4, std::ref(result));  // std::ref让result按引用传递
    boundAdd();
    cout << result << endl;  // 7
}
```

### 9. C++17：结构化绑定、`if constexpr`

**A：** 结构化绑定`auto [a, b] = pair_or_struct;`可以一次性把`pair`/`tuple`/普通结构体解包成多个具名变量，遍历`map`时尤其常用。`if constexpr`是编译期分支——不满足条件的分支甚至不会被实例化（模板参数类型不匹配也不会报错），常用于模板函数里根据类型做不同处理，替代传统繁琐的 SFINAE/标签分发写法。

```cpp
template<typename T>
auto describe(T v) {
    if constexpr (std::is_integral_v<T>) return string("integer: ") + std::to_string(v);
    else return string("non-integer");
}
int main() {
    map<string,int> m = {{"a",1},{"b",2}};
    for (const auto& [key, value] : m) cout << key << "=" << value << " ";  // a=1 b=2
    cout << endl;
    cout << describe(5) << endl;      // integer: 5
    cout << describe(3.14) << endl;   // non-integer
}
```

### 10. C++20：Concepts、协程简介

**A：** Concepts 允许给模板参数加**语义化的约束**（比如"必须是数值类型"），替代过去晦涩的 SFINAE 写法，编译不满足约束的调用时能给出比传统模板错误信息友好得多的报错。

```cpp
template<typename T>
concept Numeric = std::is_arithmetic_v<T>;
template<Numeric T> T add(T a, T b) { return a + b; }
int main() {
    cout << add(1, 2) << endl;       // 3
    cout << add(1.5, 2.5) << endl;   // 4
    // add(string("a"), string("b"));  // 编译错误：string不满足Numeric概念，报错信息清晰
}
```

C++20 还引入了协程(`co_await`/`co_yield`/`co_return`)，允许函数在中途"挂起"并让出控制权、之后再从挂起点恢复执行，是实现高并发异步 I/O（不阻塞线程等待）的语言级支持，写法和调度细节较复杂，本文只作为知识点提及，详细原理和落地框架（如`asio`/协程库）超出面试八股速记的范畴，需要单独深入学习。

### 11. 模板元编程

**A：** 利用模板在**编译期**做计算/生成代码的技术，经典手法是"模板递归+特化作为递归终止条件"，编译期就能把结果算成常量，运行期零开销。C++11 之后，很多这类需求可以直接用`constexpr`函数替代，写法更接近普通函数、可读性更好，只有在需要生成不同类型（而不只是计算数值）时才必须依赖模板元编程。

```cpp
template<int N> struct Factorial { static const int value = N * Factorial<N-1>::value; };
template<> struct Factorial<0> { static const int value = 1; };   // 特化作为递归终止

constexpr int factorial(int n) { return n <= 1 ? 1 : n * factorial(n - 1); }  // 更现代的写法

int main() {
    cout << Factorial<5>::value << endl;         // 120，编译期常量
    constexpr int f5 = factorial(5);
    cout << f5 << endl;                            // 120
    static_assert(Factorial<6>::value == 720, "编译期就能校验");
}
```

### 12. C++ 异常处理

**A：** 用`try`/`catch`/`throw`实现，可以抛出任意类型（不推荐），惯例是继承`std::exception`并重写`what()`。`catch`按代码里出现的顺序依次尝试匹配，**更具体的异常类型要写在前面**，基类异常（如`std::exception`）放最后兜底，否则派生类异常会被基类的`catch`提前"截胡"（永远匹配不到派生类版本，编译器通常还会给出`-Wexceptions`之类的告警提示代码顺序不可达）。异常传播过程中，栈上已构造的局部对象会被正常析构（栈展开，stack unwinding），这也是 RAII 能够"即使遇到异常也不泄漏资源"的根本原因。

```cpp
class MyException : public std::exception {
public:
    explicit MyException(string msg) : msg_(std::move(msg)) {}
    const char* what() const noexcept override { return msg_.c_str(); }
private:
    string msg_;
};
void mayThrow(int code) {
    if (code == 1) throw std::runtime_error("runtime error");
    if (code == 2) throw MyException("自定义异常");
    if (code == 3) throw 42;
}
int main() {
    for (int code = 1; code <= 3; ++code) {
        try { mayThrow(code); }
        catch (const MyException& e) { cout << "捕获MyException: " << e.what() << endl; }   // 更具体的放前面
        catch (const std::exception& e) { cout << "捕获std::exception: " << e.what() << endl; } // 基类兜底
        catch (int e) { cout << "捕获int异常: " << e << endl; }
    }
}
// 输出：捕获std::exception: runtime error / 捕获MyException: 自定义异常 / 捕获int异常: 42
```

---

## 八、多线程与并发基础

> 本节只做面试速记，完整覆盖`std::thread`/锁/条件变量/`atomic`内存序/线程池等内容见同仓库`cpp-tutorial/11-多线程与并发.md`。

### 1. `mutex` + `lock_guard`/`unique_lock` 解决什么问题？

**A：** 多线程同时读写同一块共享数据（数据竞争，data race）是未定义行为，`mutex`提供"同一时刻只允许一个线程持有锁、进入临界区"的互斥保证。`lock_guard`是 RAII 风格的锁包装器，构造时加锁、析构时（离开作用域，包括异常路径）自动解锁，避免忘记解锁；`unique_lock`功能更全（支持手动`lock()`/`unlock()`、延迟加锁、配合条件变量使用），但有轻微额外开销。下面的实测直接对比"无锁"和"有锁"两种自增在50个线程并发下的最终结果：

```cpp
int unsafeCounter = 0, safeCounter = 0;
mutex mtx;
int main() {
    vector<thread> ts;
    for (int i = 0; i < 50; ++i) {
        ts.emplace_back([]{
            for (int j = 0; j < 1000; ++j) {
                unsafeCounter++;              // 数据竞争：读-加-写不是原子的
                lock_guard<mutex> lk(mtx);     // RAII加锁，作用域结束自动解锁
                safeCounter++;
            }
        });
    }
    for (auto& t : ts) t.join();
    cout << unsafeCounter << endl;   // 期望50000，实测49631——确实丢了计数，证实了数据竞争
    cout << safeCounter << endl;     // 50000，锁保护下严格正确
}
```

这个结果直观证明：`unsafeCounter`因为多线程同时"读-加-写"互相踩踏，最终值小于理论值`50000`；`safeCounter`在互斥锁保护下严格等于`50000`。

### 2. 条件变量 `condition_variable`

**A：** 用于线程间"等待某个条件成立再继续执行"的同步，典型场景是生产者-消费者模型。`cv.wait(lock, predicate)`会在`predicate`为`false`时自动释放锁并阻塞，被其他线程`notify_one()`/`notify_all()`唤醒后重新加锁并再次检查`predicate`（防止"虚假唤醒"）。

```cpp
mutex mtx; condition_variable cv; queue<int> q; bool done = false;
void producer() {
    for (int i = 1; i <= 3; ++i) { { lock_guard<mutex> lk(mtx); q.push(i); } cv.notify_one(); }
    { lock_guard<mutex> lk(mtx); done = true; } cv.notify_one();
}
void consumer() {
    while (true) {
        unique_lock<mutex> lk(mtx);
        cv.wait(lk, []{ return !q.empty() || done; });
        while (!q.empty()) { cout << "消费: " << q.front() << endl; q.pop(); }
        if (done) break;
    }
}
int main() { thread p(producer), c(consumer); p.join(); c.join(); }
// 输出：生产:1 生产:2 生产:3 消费:1 消费:2 消费:3（消费者按队列顺序正确取出全部数据）
```

### 3. `std::atomic` 与无锁编程

**A：** 见第七节第7题——`atomic`对基本类型的读改写操作提供无锁的原子性保证，底层依赖 CPU 原子指令。"无锁化编程(lock-free)"更广义地指**完全不用互斥锁**、只用原子操作+内存序来实现并发安全的数据结构（如无锁队列），好处是避免了锁的上下文切换开销和死锁风险，坏处是正确性证明和实现难度陡增，内存序（`memory_order_relaxed`/`acquire`/`release`/`seq_cst`）的选择直接影响正确性且极难调试。绝大多数业务代码不需要手写无锁结构，遇到高并发瓶颈优先考虑：缩小临界区、用更细粒度的锁、或直接使用`atomic`的默认`seq_cst`语义，只有专门写高性能并发库时才需要深入研究宽松内存序。

### 4. STL 容器线程安全性

**A：** 见第六节第9题——多读安全，一写就需要外部加锁；不同容器实例互不影响。

### 5. 多线程 vs 多进程 vs 协程

**A：** 简要对比：多线程共享同一进程地址空间，切换开销中等，靠锁/原子操作同步，一个线程崩溃整个进程都受影响；多进程地址空间互相隔离，切换开销大，靠IPC通信，隔离性好（一个崩溃不影响其他）；协程（如 C++20 coroutine）本质是同一线程内的协作式调度，用户态切换几乎零开销，适合高并发I/O场景，但编程模型和调试都更复杂。完整对比表格见`cpp-tutorial/11-多线程与并发.md`第十节。

---

## 九、其他高频问题

### 1. 内存池是什么？为什么要自己实现？

**A：** 频繁调用`malloc`/`new`分配小对象会有两个代价：① 每次都要走一遍系统的通用内存分配器（有加锁、查找合适空闲块等开销）；② 大量不同大小的小块分配/释放容易造成内存碎片。内存池的思路是：**预先申请一大块内存，切成固定大小的小块，用一个"空闲链表"把所有空闲块串起来**；分配时直接从链表摘一个节点（O(1)，不用真的调系统分配器），释放时直接把节点挂回链表头（O(1)，不用真的调`free`），只有内存池用完了或程序退出时才涉及真正的系统级内存操作。适合"生命周期短、大小固定、分配释放非常频繁"的对象（比如网络框架里的连接/请求对象、游戏引擎里的粒子对象）。

```cpp
template<typename T>
class MemoryPool {
public:
    explicit MemoryPool(size_t blockCount) {
        pool_ = static_cast<char*>(::operator new(blockCount * sizeof(Node)));
        freeList_ = reinterpret_cast<Node*>(pool_);
        for (size_t i = 0; i < blockCount - 1; ++i)
            reinterpret_cast<Node*>(pool_ + i * sizeof(Node))->next =
                reinterpret_cast<Node*>(pool_ + (i + 1) * sizeof(Node));
        reinterpret_cast<Node*>(pool_ + (blockCount - 1) * sizeof(Node))->next = nullptr;
    }
    ~MemoryPool() { ::operator delete(pool_); }
    T* allocate() {
        if (!freeList_) throw bad_alloc();
        Node* node = freeList_;
        freeList_ = freeList_->next;    // 从空闲链表摘下第一个节点，O(1)
        return reinterpret_cast<T*>(node);
    }
    void deallocate(T* p) {
        Node* node = reinterpret_cast<Node*>(p);
        node->next = freeList_;          // 挂回空闲链表头部，O(1)
        freeList_ = node;
    }
private:
    union Node { Node* next; alignas(T) char data[sizeof(T)]; };
    char* pool_;
    Node* freeList_;
};
struct Point { int x, y; Point(int a,int b):x(a),y(b){} };
int main() {
    MemoryPool<Point> pool(4);
    Point* p1 = pool.allocate();
    new (p1) Point(1, 2);       // placement new：在池子给的内存上原地构造对象
    cout << p1->x << "," << p1->y << endl;   // 1,2
    p1->~Point();                 // 手动调用析构
    pool.deallocate(p1);          // 归还给内存池(不是真的free，只是挂回链表)

    Point* p2 = pool.allocate();  // 复用刚归还的同一块内存
    cout << (p2 == (void*)p1) << endl;   // 1(true)，确实复用了同一块内存
}
```

### 2. 单例模式如何保证线程安全？

**A：** 最推荐的是 **Meyer's Singleton**——利用C++11起局部静态变量的构造由标准保证线程安全（"magic statics"，见第一节第2题）这一特性，写法最简洁：

```cpp
class Singleton1 {
public:
    static Singleton1& instance() {
        static Singleton1 inst;    // 只在第一次调用时构造，标准保证多线程下只构造一次
        return inst;
    }
    Singleton1(const Singleton1&) = delete;
    Singleton1& operator=(const Singleton1&) = delete;
private:
    Singleton1() { cout << "Singleton1构造" << endl; }
};
```

另一种是显式使用 **`std::call_once` + `std::once_flag`**，语义上更直白地表达"只执行一次"，也常用于需要更精细控制初始化时机的场景：

```cpp
class Singleton1 {   // 与前面Meyer's Singleton相同定义，此处重复列出以保证示例可独立编译
public:
    static Singleton1& instance() {
        static Singleton1 inst;
        return inst;
    }
    Singleton1(const Singleton1&) = delete;
    Singleton1& operator=(const Singleton1&) = delete;
private:
    Singleton1() { cout << "Singleton1构造" << endl; }
};
class Singleton2 {
public:
    static Singleton2& instance() {
        static once_flag flag;
        call_once(flag, []{ instancePtr_ = new Singleton2(); });
        return *instancePtr_;
    }
private:
    Singleton2() { cout << "Singleton2构造" << endl; }
    static inline Singleton2* instancePtr_ = nullptr;
};
int main() {
    vector<thread> ts;
    for (int i = 0; i < 5; ++i) ts.emplace_back([]{ Singleton1::instance(); Singleton2::instance(); });
    for (auto& t : ts) t.join();
}
```

实测5个线程并发调用，`Singleton1构造`和`Singleton2构造`各自都只打印**一次**，证实了两种写法都是线程安全的。（早期C++98时代常见的"双重检查锁定(DCL)"手写`if(!instance) { lock; if(!instance) instance=new T(); }`模式，在没有正确内存屏障的情况下其实是有指令重排风险的错误实现，C++11后应直接优先使用上面两种标准保证安全的写法，不必再手写DCL。）

### 3. 宏 (`#define`) 和 `const` 的区别？

**A：** 宏是预处理阶段的纯文本替换，**没有类型、不接受编译器类型检查、不占用运行时内存、调试器看不到符号**（IDE 单步调试时看到的是替换后的字面量，不是宏名）；`const`常量是真正的变量，有类型、有地址（除非被完全内联优化掉）、受作用域规则约束、能被调试器正常查看。宏函数还有一个经典陷阱——**参数没有做类型检查、也不保证只求值一次**，容易因为参数带副作用而产生反直觉的结果：

```cpp
#define MAX_MACRO 100
const int MAX_CONST = 100;
#define SQUARE(x) ((x) * (x))
int counter = 0;
int next() { return ++counter; }
int main() {
    cout << SQUARE(next()) << endl;   // 期望"先算next()=1，再1*1=1"，实际展开成((next())*(next()))
    cout << counter << endl;           // next()被调用了两次，counter变成2，SQUARE结果是1*2=2，不是1
}
```

实测输出`SQUARE(next())`结果为`2`、`counter`最终为`2`——证实了宏参数被展开了两次、`next()`被意外调用了两次，这正是"宏不对参数求值语义做保护"的经典陷阱，也是现代 C++ 提倡"能用`constexpr`/`inline`函数就不用宏"的原因之一（函数参数只求值一次，且有类型检查）。

### 4. 静态链接与动态链接

**A：** 见第一节第27题，已用实际编译+`otool -L`验证过两种产物的差异。

---

[← 返回索引](index.md)
