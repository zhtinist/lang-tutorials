# Python 面试八股文

> 本文是 Python 后端面试的高密度背诵材料,采用经典的"问 - 答"八股格式,面向准备字节、阿里、腾讯等公司后端/技术面试的读者,不假设任何 C/C++ 背景。内容主要参考并整理自 GitHub 上最著名的 Python 面试题仓库 [taizilongxu/interview_python](https://github.com/taizilongxu/interview_python)(17k+ star,"Python语言特性"部分几乎是国内 Python 面试题的事实标准),并与 Snailclimb/JavaGuide-Interview、lengyue1024/BAT_interviews、zhengjianglong915/note-of-interview 等多个千星级面试题仓库交叉校对,补充了上下文管理器、异常处理、`__slots__`、类型注解、标准库等常见追问点。所有代码示例均已在本机 Python 环境实际运行验证。

## 目录

- [一、基础语法与数据模型](#一基础语法与数据模型)
- [二、面向对象](#二面向对象)
- [三、函数式编程与装饰器](#三函数式编程与装饰器)
- [四、并发与并行](#四并发与并行)
- [五、内存管理与垃圾回收](#五内存管理与垃圾回收)
- [六、异常处理与上下文管理器](#六异常处理与上下文管理器)
- [七、类型注解与常用标准库](#七类型注解与常用标准库)

---

## 一、基础语法与数据模型

### 1. 函数参数传递:值传递还是引用传递?

**问:Python 函数参数是值传递还是引用传递?**

都不是,准确说法是**对象引用传递(pass by object reference)**,也常被称为"传对象"。调用函数时,实参和形参会绑定到同一个对象上;之后发生什么取决于**对象是否可变**以及函数内部是"修改对象"还是"重新绑定变量":

- 对**不可变对象**(int、str、tuple、frozenset...)做任何"修改"操作,实际上都是创建了新对象并让局部变量重新绑定到新对象,不会影响调用者手里的引用。
- 对**可变对象**(list、dict、set 等)调用其原地修改方法(`append`、`update` 等),会通过共享的引用改到同一块内存,调用者能看到变化;但如果在函数内部用 `=` 给形参重新赋值(重新绑定),只是让局部变量指向了别的对象,不影响外部变量。

```python
def modify_immutable(x):
    x = x + 1
    return x

def modify_mutable(lst):
    lst.append(4)

a = 10
modify_immutable(a)
print("a after func:", a)  # 10,不受影响

b = [1, 2, 3]
modify_mutable(b)
print("b after func:", b)  # [1, 2, 3, 4],被原地修改

def rebind_list(lst):
    lst = lst + [99]  # 重新绑定局部变量,不影响外部
    return lst

c = [1, 2, 3]
rebind_list(c)
print("c after rebind:", c)  # [1, 2, 3],未变
```

一句话记忆:**函数收到的是对象的引用副本,能否"看到外部变化"取决于对象可变性,而不是传递机制本身**。

### 2. `*args` 和 `**kwargs`

**问:`*args` 和 `**kwargs` 分别是什么?怎么用?**

它们是 Python 函数定义中用来接收**可变数量参数**的语法糖:

- `*args`:把多余的**位置参数**收集成一个 `tuple`。
- `**kwargs`:把多余的**关键字参数**收集成一个 `dict`。
- 命名不是强制的(`args`/`kwargs` 只是约定俗成),真正起作用的是 `*` 和 `**` 这两个符号。
- 反过来,在**调用**函数时,`*seq` 和 `**mapping` 用于把序列/字典**解包**成位置参数和关键字参数传进去。

```python
def demo(a, b, *args, **kwargs):
    print("a =", a, "b =", b)
    print("args =", args)
    print("kwargs =", kwargs)

demo(1, 2, 3, 4, x=5, y=6)
# a = 1 b = 2
# args = (3, 4)
# kwargs = {'x': 5, 'y': 6}

def add3(a, b, c):
    return a + b + c

args = (1, 2, 3)
kwargs = {"a": 1, "b": 2, "c": 3}
print(add3(*args))    # 6,解包元组作为位置参数
print(add3(**kwargs)) # 6,解包字典作为关键字参数
```

常见应用场景:装饰器里透传任意签名的函数参数、写通用的 `*args/**kwargs` 转发接口、子类 `__init__` 里 `super().__init__(*args, **kwargs)`。

### 3. `is` 与 `==` 的区别

**问:`is` 和 `==` 有什么区别?**

- `==` 比较的是**值是否相等**,底层调用的是 `__eq__` 方法,可以被类重写。
- `is` 比较的是**身份(identity)**,即两个引用是否指向内存中同一个对象,等价于 `id(a) == id(b)`,不能被重写。

```python
a = [1, 2, 3]
b = [1, 2, 3]
print(a == b)  # True,值相等
print(a is b)  # False,不是同一个对象

c = a
print(c is a)  # True,同一个对象

m = 1000
n = int("1000")  # 运行时构造,避开编译期常量折叠
print(m is n)  # False:超出小整数池范围,是两个不同对象
print(m == n)  # True
```

延伸考点:CPython 出于性能考虑,会缓存 `-5 ~ 256` 的小整数以及部分短字符串(字符串驻留),所以小范围内的 `int`/`str` 字面量用 `is` 判断可能"恰好"为 `True`,但这是**实现细节而非语言保证**,业务代码判断值相等一律用 `==`,`is` 只用来判断 `None`、单例等场景(例如 `if x is None`)。

### 4. 浅拷贝与深拷贝

**问:浅拷贝和深拷贝的区别?**

- **浅拷贝(shallow copy)**:创建一个新的容器对象,但容器内部的元素仍然是**同一个引用**,只拷贝了"第一层"。常见方式:切片 `lst[:]`、`list(lst)`、`dict.copy()`、`copy.copy()`。
- **深拷贝(deep copy)**:递归地拷贝所有层级的对象,新对象和原对象完全独立、互不影响。用 `copy.deepcopy()`。
- 对于只包含不可变元素的容器(如 `[1, 2, 3]`),浅拷贝和深拷贝表现一样;区别只在嵌套了可变对象(列表套列表、字典套字典)时才会体现出来。

```python
import copy

original = {"name": "Ann", "scores": [90, 80], "meta": {"vip": True}}

shallow = copy.copy(original)
deep = copy.deepcopy(original)

original["scores"].append(70)
original["meta"]["vip"] = False

print("original:", original)
print("shallow: ", shallow)   # scores 和 meta 是共享引用,跟着变了
print("deep:    ", deep)      # 完全独立,不受影响
```

输出:

```
original: {'name': 'Ann', 'scores': [90, 80, 70], 'meta': {'vip': False}}
shallow:  {'name': 'Ann', 'scores': [90, 80, 70], 'meta': {'vip': False}}
deep:     {'name': 'Ann', 'scores': [90, 80], 'meta': {'vip': True}}
```

### 5. 命名约定:单下划线、双下划线、`__xxx__`

**问:Python 里 `_x`、`__x`、`__x__` 这几种命名有什么区别?**

| 写法 | 含义 |
|---|---|
| `_x`(单前导下划线) | **约定**上表示"内部使用/受保护",纯君子协定,解释器不做任何特殊处理,外部仍可正常访问;`from module import *` 时会被排除。 |
| `__x`(双前导下划线,无双后导) | 触发**名字改写(name mangling)**:在类体内 `__x` 会被解释器自动改写为 `_ClassName__x`,用来避免子类不小心覆盖父类的"私有"属性,不是真正意义上的私有,只是加大了误用成本。 |
| `__x__`(双前导 + 双后导下划线) | **魔术方法/魔术属性(dunder)**,由 Python 解释器保留,如 `__init__`、`__len__`、`__name__`,不要自己发明新的这类名字。 |
| `x_`(单尾随下划线) | 单纯为了避开和关键字冲突,如 `class_`、`type_`,没有特殊语义。 |

```python
class Demo:
    public_attr = "public"
    _protected_attr = "protected (约定不要在外部访问,但技术上仍可访问)"
    __private_attr = "private (会被名字改写)"

    def __init__(self):
        self.__value = 42  # 也会被 name mangling

    def get_value(self):
        return self.__value

d = Demo()
print(d.public_attr)
print(d._protected_attr)          # 能访问,只是君子协定
print(d.get_value())               # 42
try:
    print(d.__private_attr)        # 直接访问会报错
except AttributeError as e:
    print("AttributeError:", e)
print(d._Demo__private_attr)       # name mangling 后的真实属性名,依然能访问到
```

### 6. 字符串格式化:`%`、`.format()`、f-string

**问:Python 有哪几种字符串格式化方式,推荐用哪种?**

```python
name, score = "Ann", 92.5

# 1. % 旧式格式化,类似 C 的 printf,Python 2 时代主流
print("Name: %s, Score: %.1f" % (name, score))

# 2. str.format(),Python 2.6+ 引入,可读性更好,支持按位置/关键字取值
print("Name: {}, Score: {:.1f}".format(name, score))
print("Name: {n}, Score: {s:.1f}".format(n=name, s=score))

# 3. f-string,Python 3.6+ 引入,推荐首选:可读性最好、性能最快(编译期直接生成字节码)
print(f"Name: {name}, Score: {score:.1f}")
print(f"Sum: {1 + 2 = }")  # 3.8+ 的自文档化写法,等价于 "Sum: 1 + 2 = 3"
```

三者都支持 `{:.2f}`、`{:>10}`、`{:,}` 等格式规格(format spec),现代 Python 代码里 f-string 是事实标准,`%` 格式化基本只在日志模块(`logging.info("%s", x)`,延迟求值省性能)里还常见。

### 7. 列表推导式与字典推导式

**问:什么是推导式(comprehension)?列表推导式和生成器表达式有什么区别?**

推导式是用一行表达式从可迭代对象生成新容器的语法糖,本质是 `for` 循环 + 条件过滤 + 表达式映射的紧凑写法,可读性和执行效率通常都优于手写 `for` 循环 `append`。Python 支持四种:列表推导式 `[]`、字典推导式 `{k: v}`、集合推导式 `{}`、生成器表达式 `()`。

```python
squares = [x * x for x in range(6)]
print(squares)  # [0, 1, 4, 9, 16, 25]

evens_squares = [x * x for x in range(10) if x % 2 == 0]
print(evens_squares)  # [0, 4, 16, 36, 64]

d = {x: x * x for x in range(5)}
print(d)  # {0: 0, 1: 1, 2: 4, 3: 9, 4: 16}

s = {x % 3 for x in range(10)}  # 集合推导式,自动去重
print(s)  # {0, 1, 2}

gen = (x * x for x in range(6))  # 生成器表达式:惰性求值,不会一次性生成全部结果
print(list(gen))  # [0, 1, 4, 9, 16, 25]
```

关键区别:`[]` 和 `{}` 推导式会**立即**把所有结果计算出来存进内存;`()` 生成器表达式返回一个生成器对象,**按需惰性求值**,处理大数据集/无限序列时更省内存,但只能遍历一次。

### 8. 文件读取:`read()` / `readline()` / `readlines()`

**问:`read()`、`readline()`、`readlines()` 有什么区别?实际工作中应该怎么读大文件?**

- `f.read()`:一次性读取**整个文件**内容为一个字符串(或 `bytes`,二进制模式下),文件很大时会占用大量内存。
- `f.readline()`:每次只读**一行**(含末尾换行符),适合边读边处理、控制内存占用。
- `f.readlines()`:一次性读取所有行,返回一个**列表**,每个元素是一行,同样有内存压力。
- 更推荐的写法是**直接对文件对象做 `for` 迭代**,内部按行读取但不会把整个文件都加载进内存,是读大文件最常用也是最省内存的方式。

```python
with open("sample.txt", "w", encoding="utf-8") as f:
    f.write("line1\nline2\nline3\n")

with open("sample.txt", "r", encoding="utf-8") as f:
    content = f.read()
print(repr(content))  # 'line1\nline2\nline3\n'

with open("sample.txt", "r", encoding="utf-8") as f:
    first_line = f.readline()
    second_line = f.readline()
print(repr(first_line), repr(second_line))  # 'line1\n' 'line2\n'

with open("sample.txt", "r", encoding="utf-8") as f:
    lines = f.readlines()
print(lines)  # ['line1\n', 'line2\n', 'line3\n']

with open("sample.txt", "r", encoding="utf-8") as f:
    for line in f:  # 推荐:逐行迭代,内存友好
        print("iter:", line.strip())
```

### 9. `range` 与 `xrange`(Python 2 vs 3)

**问:`range` 和 `xrange` 有什么区别?**

这是个 Python 2 遗留问题:Python 2 里 `range()` 会立即生成一个包含所有元素的 `list`,而 `xrange()` 返回一个惰性的可迭代对象,按需生成数值,省内存。**Python 3 直接把 Python 2 的 `xrange` 行为并入了 `range`**,`range()` 现在返回的是一个惰性的 `range` 对象(不是列表),`xrange` 被彻底移除了。

```python
r = range(1_000_000_000_000)  # Python 3 的 range 是惰性对象,瞬间创建,不占用巨大内存
print(type(r), r[5], len(r))
# <class 'range'> 5 1000000000000
print(r)  # range(0, 1000000000000),对象本身,不是列表
```

`range` 对象支持 `len()`、下标索引、切片、`in` 判断(内部用数学公式 O(1) 计算,不需要遍历),但不支持 `append` 等列表操作,如果确实需要一个列表,要显式 `list(range(...))`。

### 10. Python 2 与 Python 3 的主要区别

**问:Python 2 和 Python 3 有哪些关键区别?**

| 维度 | Python 2 | Python 3 |
|---|---|---|
| `print` | 语句(`print "x"`) | 内置函数(`print("x")`) |
| 整数除法 | `/` 对两个 int 做地板除 | `/` 恒为真除法(浮点),地板除用 `//` |
| 字符串模型 | `str` 即字节串,`unicode` 是另一种类型,中文处理经常踩坑 | `str` 统一是 Unicode 文本,`bytes` 单独表示二进制数据,编解码边界清晰 |
| `range`/`xrange` | 并存,`range` 立即生成列表 | 只有 `range`,行为等价于原来的 `xrange`(惰性) |
| 整数类型 | `int` 和 `long` 两种 | 统一为 `int`,自动支持任意精度大整数 |
| 迭代器 API | `dict.keys()`/`values()`/`items()` 返回 `list` | 返回**视图对象**,惰性、随字典变化而变化,更省内存 |
| 异常语法 | `except Exception, e:` | 统一为 `except Exception as e:` |
| 编码 | 默认源码编码是 ASCII,常需手动声明 `# -*- coding: utf-8 -*-` | 源码默认 UTF-8 |
| 生命周期 | 2020 年 1 月 1 日官方 EOL,不再维护 | 现行主线版本 |

工程上的结论:新项目一律用 Python 3,老项目如果还在用 Python 2,应尽快用 `2to3`/`six` 等工具迁移,面试更多是考察"是否了解这些差异及其背后原因",而不是要求会写 Python 2。

---

## 二、面向对象

### 11. 类变量与实例变量

**问:类变量和实例变量有什么区别?**

- **类变量**定义在类体内、方法之外,属于类本身,**所有实例共享同一份**,通过 `ClassName.attr` 或 `instance.attr`(只读时)都能访问。
- **实例变量**通常在 `__init__` 里通过 `self.attr = ...` 定义,**每个实例各自独立**一份。
- 通过实例对**类变量赋值**(`instance.attr = value`)不会改到类变量,而是给这个实例新建了一个**同名的实例变量**,把类变量"遮蔽"掉了。
- 常见坑:把**可变对象**(list、dict)用作类变量的默认值,所有实例会共享同一个对象,一个实例改了,其他实例也会跟着变。

```python
class Student:
    school = "清华大学"  # 类变量:所有实例共享

    def __init__(self, name):
        self.name = name  # 实例变量:每个实例独立

s1 = Student("Ann")
s2 = Student("Bob")
print(s1.school, s2.school)  # 清华大学 清华大学

Student.school = "北京大学"  # 通过类修改,所有实例可见
print(s1.school, s2.school)  # 北京大学 北京大学

s1.school = "复旦大学"  # 给 s1 新建了一个同名实例变量,遮蔽了类变量
print(s1.school, s2.school, Student.school)  # 复旦大学 北京大学 北京大学

class Bad:
    items = []  # 危险:可变对象作为类变量,所有实例共享同一个
    def add(self, x):
        self.items.append(x)

b1, b2 = Bad(), Bad()
b1.add(1)
print(b2.items)  # [1],b2 也被影响了
```

### 12. `@staticmethod` 与 `@classmethod`

**问:`@staticmethod` 和 `@classmethod` 有什么区别?**

- 普通实例方法第一个参数是 `self`,自动绑定当前实例,能访问实例状态和类状态。
- `@classmethod` 第一个参数是 `cls`,自动绑定**类本身**(不是实例),访问不到具体实例的数据,但能访问/修改类变量,常用作"备用构造器"(工厂方法),且对子类友好——子类调用时 `cls` 会是子类本身。
- `@staticmethod` 不自动绑定任何参数,本质上就是一个"放在类命名空间里"的普通函数,和类/实例状态都无关,只是逻辑上归属于这个类,便于组织代码。

```python
class Circle:
    count = 0  # 类变量,记录已创建的实例数

    def __init__(self, radius):
        self.radius = radius
        Circle.count += 1

    def area(self):  # 普通实例方法,需要 self
        return 3.14159 * self.radius ** 2

    @staticmethod
    def is_valid_radius(radius):  # 不依赖实例或类状态,像个工具函数
        return radius > 0

    @classmethod
    def from_diameter(cls, diameter):  # 依赖类本身(cls),常用作"备用构造器"
        return cls(diameter / 2)

c1 = Circle(2)
c2 = Circle.from_diameter(10)  # 通过类方法构造,cls 会是 Circle
print(c1.area(), c2.radius, Circle.count)  # 12.56636 5.0 2
print(Circle.is_valid_radius(-1), Circle.is_valid_radius(5))  # False True

# 静态方法:类和实例都能调用,不会自动传 self/cls
print(Circle.is_valid_radius(3))  # True
print(c1.is_valid_radius(3))      # True
```

### 13. 元类(metaclass)

**问:什么是元类?有什么用?**

"类是对象的模板,元类是类的模板"——在 Python 里**类本身也是对象**,而创建这个"类对象"的东西就是元类。默认情况下所有类都是内置元类 `type` 创建的实例。理解这一点后,元类的两种典型用法就很自然:

1. 直接用 `type(名字, 基类元组, 属性字典)` 动态创建类。
2. 自定义一个继承自 `type` 的元类,重写 `__new__`/`__init__`/`__call__`,从而在**类被定义的那一刻**插手改造它(比如自动注册子类、校验字段命名规范、给类自动加方法),这是 ORM 框架(如 Django Model、SQLAlchemy)实现"声明式" API 的核心机制。

```python
class Foo:
    pass

print(type(Foo))     # <class 'type'>
print(type(Foo()))   # <class '__main__.Foo'>

# 用 type() 动态创建一个类
Bar = type("Bar", (object,), {"x": 1, "greet": lambda self: "hi"})
b = Bar()
print(b.x, b.greet())  # 1 hi

# 自定义元类:控制类的"创建过程"
class UpperAttrMeta(type):
    def __new__(mcs, name, bases, namespace):
        new_namespace = {
            (key.upper() if not key.startswith("__") else key): value
            for key, value in namespace.items()
        }
        return super().__new__(mcs, name, bases, new_namespace)

class Config(metaclass=UpperAttrMeta):
    host = "localhost"
    port = 8080

print(Config.HOST, Config.PORT)  # localhost 8080,属性名被元类改成了大写
```

一般业务代码很少需要自己写元类,但**理解 `class` 语句背后也是"调用元类来生产类对象"**,是理解 ORM、ABCMeta(抽象基类)、`dataclass` 等框架级机制的关键。

### 14. `__new__` 与 `__init__` 的区别

**问:`__new__` 和 `__init__` 有什么区别?**

- `__new__(cls, ...)` 是**静态方法**(隐式声明为 staticmethod),真正负责**创建并返回**一个实例,是构造过程的第一步;它拿到的第一个参数是类本身 `cls`。
- `__init__(self, ...)` 是**实例方法**,在 `__new__` 返回了一个该类的实例之后被自动调用,负责**初始化**这个已经存在的实例(给属性赋值等),不负责创建对象,也不需要返回值(必须返回 `None`)。
- 如果 `__new__` **没有返回该类(或其子类)的实例**,`__init__` 就不会被自动调用。这也是实现单例模式的常见切入点——控制 `__new__` 让它每次都返回同一个实例。

```python
class Point:
    def __new__(cls, *args, **kwargs):
        print("__new__ 被调用:负责创建并返回实例")
        instance = super().__new__(cls)
        return instance

    def __init__(self, x, y):
        print("__init__ 被调用:负责初始化已创建的实例")
        self.x = x
        self.y = y

p = Point(1, 2)
print(p.x, p.y)  # 1 2

class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self, value=None):
        if value is not None:
            self.value = value

s1 = Singleton(1)
s2 = Singleton(2)
print(s1 is s2, s1.value, s2.value)  # True 2 2,同一个对象
```

### 15. 新式类与旧式类

**问:什么是新式类(new-style class)和旧式类(old-style class)?**

这也是 Python 2 的历史遗留概念:Python 2 里默认 `class Foo:` (不显式继承任何东西)创建的是**旧式类**,不继承自 `object`,没有 `__new__`、没有描述符协议、MRO(方法解析顺序)用简单的深度优先,容易在多重继承下出现二义性;而显式写 `class Foo(object):` 才是**新式类**,拥有统一的对象模型、`__new__`、`property`、更合理的 C3 线性化 MRO 算法。**Python 3 里这个区分彻底消失了——所有类都自动是新式类**,不管写不写 `(object)`,面试问到这个更多是考察对 Python 发展历史的了解。

```python
class Foo:  # Python 3 里,不管是否显式继承 object,都是新式类
    pass

class Bar(object):
    pass

print(Foo.__mro__)  # (<class '__main__.Foo'>, <class 'object'>)
print(Bar.__mro__)  # (<class '__main__.Bar'>, <class 'object'>)
print(issubclass(Foo, object))  # True
```

### 16. `super().__init__()` 的作用

**问:子类里为什么要调用 `super().__init__()`?**

`super()` 返回一个代理对象,按照 MRO(方法解析顺序)把方法调用委托给"下一个"类,`super().__init__()` 就是显式触发父类的初始化逻辑。子类重写 `__init__` 后,**父类的 `__init__` 不会被自动调用**,如果父类里有设置关键属性、注册资源等逻辑,忘记调用 `super().__init__()` 会导致这些属性根本不存在,访问时抛 `AttributeError`。在多重继承下,`super()` 沿着 C3 线性化的 MRO 顺序逐层调用,而不是简单地"调父类",这也是它比直接写 `Animal.__init__(self, ...)` 更安全、更推荐的原因。

```python
class Animal:
    def __init__(self, name):
        self.name = name
        print(f"Animal.__init__ 初始化 name={name}")

class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name)  # 显式调用父类构造器
        self.breed = breed
        print(f"Dog.__init__ 初始化 breed={breed}")

d = Dog("旺财", "柯基")
print(d.name, d.breed)  # 旺财 柯基

class BadDog(Animal):
    def __init__(self, breed):
        self.breed = breed  # 忘记调用 super().__init__()

bd = BadDog("哈士奇")
try:
    print(bd.name)
except AttributeError as e:
    print("AttributeError:", e)  # 'BadDog' object has no attribute 'name'
```

### 17. 单例模式的四种实现

**问:Python 里怎么实现单例模式?**

单例模式保证一个类**全局只有一个实例**。Python 里常见的四种实现方式:

```python
import threading

# 方式一:重写 __new__(最常见,基础版没考虑线程安全)
class Singleton1:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

print(Singleton1() is Singleton1())  # True

# 方式二:装饰器实现
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Singleton2:
    pass

print(Singleton2() is Singleton2())  # True

# 方式三:模块级单例——Python 的 import 机制自带 sys.modules 缓存,
# 一个模块无论被 import 多少次都只会执行一次、只创建一份对象,
# 把需要单例的实例定义在模块顶层,其他地方 import 该变量即可,这是最"Pythonic"的方式

# 方式四:基于元类,拦截类的"调用"(即实例化)过程
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Singleton3(metaclass=SingletonMeta):
    pass

print(Singleton3() is Singleton3())  # True

# 生产级实现还要考虑多线程安全,用双重检查锁定(double-checked locking)
class Singleton4:
    _instance = None
    _lock = threading.Lock()
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
```

### 18. 鸭子类型(Duck Typing)

**问:什么是鸭子类型?**

"如果一只鸟走起来像鸭子、叫起来像鸭子,那它就可以被当作鸭子"——鸭子类型指的是 Python **不关心对象的具体类型,只关心它有没有需要的方法/属性**,这是动态类型语言实现多态的主要方式,和 Java/C++ 靠继承同一个接口/基类来实现多态不同,Python 里只要"长得像"就能用,不需要显式声明实现了某个接口。

```python
class Duck:
    def quack(self):
        print("嘎嘎嘎")

class Person:
    def quack(self):
        print("学鸭子叫:嘎嘎嘎")

def make_it_quack(thing):
    # 不关心 thing 是什么类型,只要它有 quack 方法就行
    thing.quack()

make_it_quack(Duck())
make_it_quack(Person())

# 标准库大量依赖鸭子类型:任何实现了 __len__/__getitem__ 的对象都能被当序列用
class FakeList:
    def __len__(self):
        return 3
    def __getitem__(self, idx):
        if idx >= 3:
            raise IndexError
        return idx * 10

fl = FakeList()
print(len(fl), fl[2], list(fl))  # 3 20 [0, 10, 20]
```

### 19. Python 有没有函数重载?

**问:Python 支持方法重载吗?**

**不支持**像 Java/C++ 那样"同名方法、不同参数列表"共存的重载——Python 里同一个类定义两个同名方法,后面的会直接覆盖前面的,不会按参数个数/类型分派。

```python
class Greeter:
    def hello(self):
        print("hello")
    def hello(self, name):  # 覆盖了上面无参的版本
        print(f"hello {name}")

g = Greeter()
try:
    g.hello()
except TypeError as e:
    print("TypeError:", e)  # hello() missing 1 required positional argument: 'name'
g.hello("Ann")  # hello Ann
```

常见替代方案:

1. **默认参数 / `*args`+判断**模拟不同参数个数的调用。
2. `functools.singledispatch`(普通函数)/ `singledispatchmethod`(类方法)按**参数类型**做分派,是标准库提供的最接近"重载"的机制:

```python
from functools import singledispatchmethod

class Formatter:
    @singledispatchmethod
    def format(self, value):
        return f"unknown: {value}"

    @format.register
    def _(self, value: int):
        return f"int: {value}"

    @format.register
    def _(self, value: str):
        return f"str: {value}"

f = Formatter()
print(f.format(1))    # int: 1
print(f.format("x"))  # str: x
print(f.format(1.5))  # unknown: 1.5
```

### 20. `__slots__`

**问:`__slots__` 是什么,有什么用?**

默认情况下,每个实例都自带一个 `__dict__` 用来存放实例属性,这带来了随时加属性的灵活性,但也有内存开销(字典本身有额外的哈希表结构)。在类里定义 `__slots__ = (...)` 后,该类的实例就**不再拥有 `__dict__`**,只能拥有 `__slots__` 里声明过的固定属性,访问未声明的属性会直接报 `AttributeError`。好处是**显著节省内存**(适合需要创建海量实例的场景,如解析大量结构化数据)、属性访问也略快;代价是失去了动态加属性的灵活性,且多继承、和某些依赖 `__dict__` 的库配合时会有额外的坑。

```python
class NormalPoint:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class SlotPoint:
    __slots__ = ("x", "y")  # 声明该类实例只允许有这两个属性
    def __init__(self, x, y):
        self.x = x
        self.y = y

n = NormalPoint(1, 2)
n.z = 99  # 普通类默认有 __dict__,可以随意加新属性
print(n.__dict__)  # {'x': 1, 'y': 2, 'z': 99}

s = SlotPoint(1, 2)
try:
    s.z = 99  # __slots__ 类没有 __dict__,加不存在的属性会报错
except AttributeError as e:
    print("AttributeError:", e)

print(hasattr(n, "__dict__"), hasattr(s, "__dict__"))  # True False

import sys
print("NormalPoint 相关内存:", sys.getsizeof(n) + sys.getsizeof(n.__dict__))  # 152
print("SlotPoint 内存:", sys.getsizeof(s))  # 48,明显更省
```

### 21. Python 自省(introspection)

**问:什么是 Python 的自省(introspection)?常用哪些函数?**

自省指程序在**运行期**检查对象的类型、属性、方法等元信息的能力,是动态类型语言的核心特性之一。Python 提供了丰富的内置自省手段:

- `type(obj)` / `isinstance(obj, cls)`:查看/判断类型。
- `hasattr(obj, name)` / `getattr(obj, name, default)` / `setattr(obj, name, value)`:动态地判断、读取、设置属性,是实现通用框架代码(如 ORM、序列化库)的基础。
- `dir(obj)`:列出对象所有可用的属性和方法名。
- `obj.__dict__`:对象自身的属性字典。
- `callable(obj)`:判断对象是否可调用。
- `inspect` 模块:更强大的自省能力,如 `inspect.signature()` 拿函数签名、`inspect.getmembers()` 列出成员、`inspect.getsource()` 拿源码。

```python
class Person:
    """一个简单的 Person 类"""
    def __init__(self, name, age):
        self.name = name
        self.age = age
    def greet(self):
        return f"Hi, I'm {self.name}"

p = Person("Ann", 20)

print(type(p))                        # <class '__main__.Person'>
print(isinstance(p, Person))          # True
print(hasattr(p, "greet"))            # True
print(getattr(p, "name"), getattr(p, "nonexist", "默认值"))  # Ann 默认值
setattr(p, "age", 21)
print(p.age)                          # 21
print(p.__dict__)                     # {'name': 'Ann', 'age': 21}
print(Person.__doc__)                 # 一个简单的 Person 类
print(callable(p.greet), callable(p)) # True False

import inspect
print(inspect.signature(p.greet))     # ()
```

---

## 三、函数式编程与装饰器

### 22. 作用域与 LEGB 规则

**问:Python 的变量作用域查找规则是什么?**

Python 用 **LEGB** 规则,按顺序从内到外查找一个变量名:

- **L(Local)**:当前函数内部的局部作用域。
- **E(Enclosing)**:外层函数(闭包场景)的作用域,但不包括全局。
- **G(Global)**:当前模块的全局作用域。
- **B(Built-in)**:Python 内置命名空间(`len`、`print` 等)。

找到即停止,找不到则逐层往外找,最外层还找不到就抛 `NameError`。**默认情况下函数内部只能读外层变量,不能直接赋值修改**——在函数内给一个变量赋值,Python 会默认它是新的局部变量;要修改全局/外层变量,必须显式用 `global`/`nonlocal` 声明。

```python
x = "global x"

def outer():
    y = "enclosing y"
    def inner():
        z = "local z"
        print(x, y, z)  # 依次在 Local -> Enclosing -> Global -> Built-in 中查找
    inner()

outer()  # global x enclosing y local z

count = 0
def increment():
    global count  # 显式声明要修改全局变量,否则会被当作新的局部变量
    count += 1

increment(); increment()
print(count)  # 2

def outer2():
    total = 0
    def inner2():
        nonlocal total  # 显式声明要修改闭包外层(非全局)的变量
        total += 1
    inner2(); inner2()
    return total

print(outer2())  # 2
```

### 23. 闭包(Closure)

**问:什么是闭包?有什么典型陷阱?**

闭包指一个**内部函数引用了外部函数作用域中的变量**,并且这个内部函数被返回或传递到了外部函数作用域之外,但依然能"记住"并访问那些外层变量——外层函数虽然已经执行完毕,它的局部变量却被内部函数捕获,不会被回收。Python 里内层函数如果要**修改**(而不仅是读取)外层变量,需要 `nonlocal` 声明。

```python
def make_counter():
    count = 0
    def counter():
        nonlocal count  # 闭包:内层函数引用了外层函数的局部变量
        count += 1
        return count
    return counter

c1 = make_counter()
c2 = make_counter()
print(c1(), c1(), c1())  # 1 2 3
print(c2())               # 1,c2 有自己独立的 count,互不干扰

print(c1.__closure__[0].cell_contents)  # 3,闭包变量实际存在 __closure__ 里
```

**经典陷阱:循环中创建闭包/lambda,变量是延迟绑定的**——闭包捕获的是变量本身而不是当时的值,循环结束后所有闭包看到的都是同一个变量的最终值:

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])  # [2, 2, 2],不是期望的 [0, 1, 2]

funcs_fixed = [lambda i=i: i for i in range(3)]  # 用默认参数在定义时就把当前值拷贝进去
print([f() for f in funcs_fixed])  # [0, 1, 2]
```

### 24. `lambda` 表达式

**问:`lambda` 是什么,和 `def` 有什么区别?**

`lambda` 是定义**匿名函数**的表达式语法,`lambda 参数: 表达式` 等价于一个只有 `return 表达式` 的函数,但**只能包含单个表达式**,不能写多条语句、赋值语句、`for`/`if` 语句块(条件表达式 `a if cond else b` 除外),函数体的结果自动作为返回值。它的主要用途是在需要"临时传一个小函数"的地方(如 `sort` 的 `key`、`map`/`filter` 的第一个参数)避免专门定义一个具名函数。

```python
add = lambda a, b: a + b
print(add(2, 3))  # 5

students = [("Ann", 92), ("Bob", 85), ("Cathy", 99)]
students.sort(key=lambda s: s[1], reverse=True)
print(students)  # [('Cathy', 99), ('Ann', 92), ('Bob', 85)]

squared = list(map(lambda x: x ** 2, range(5)))
print(squared)  # [0, 1, 4, 9, 16]
```

### 25. 函数式编程:`map` / `filter` / `reduce`

**问:Python 中函数式编程的常见写法有哪些?**

Python 不是纯函数式语言,但支持"把函数当一等公民"的函数式编程风格——函数可以赋值给变量、作为参数传递、作为返回值。标准库里 `map`/`filter`/`functools.reduce` 是最常用的三件套:

- `map(func, iterable)`:对每个元素应用 `func`,返回惰性的 map 对象。
- `filter(func, iterable)`:保留 `func` 返回真值的元素,返回惰性的 filter 对象。
- `functools.reduce(func, iterable, initializer)`:把序列"累积"成一个值。

```python
from functools import reduce

nums = [1, 2, 3, 4, 5]

doubled = list(map(lambda x: x * 2, nums))       # 对每个元素做变换
print(doubled)  # [2, 4, 6, 8, 10]

evens = list(filter(lambda x: x % 2 == 0, nums)) # 按条件过滤
print(evens)  # [2, 4]

total = reduce(lambda acc, x: acc + x, nums, 0)  # 累积成单个结果
print(total)  # 15

def apply_twice(func, value):  # 函数作为参数,函数作为返回值也同理
    return func(func(value))

print(apply_twice(lambda x: x + 3, 10))  # 16
```

实际工程中,`map`/`filter` 很多时候用列表推导式改写会更 Pythonic、可读性更好(如 `[x*2 for x in nums]`),但在面试里仍然是高频考点,尤其是和 `reduce`、装饰器、纯函数(不产生副作用、相同输入恒定同样输出)概念一起被问到。

### 26. 装饰器与 AOP

**问:装饰器的原理是什么?和 AOP 有什么关系?**

装饰器本质是一个**接收函数、返回函数**的高阶函数,`@decorator` 语法糖等价于 `func = decorator(func)`。它是 **AOP(面向切面编程,Aspect-Oriented Programming)** 思想在 Python 里最自然的落地方式:把日志记录、权限校验、耗时统计、重试、缓存这些和业务逻辑本身无关、却横切多个函数的"切面"逻辑抽出来,在**不修改原函数代码**的前提下"织入"进去。

```python
import functools
import time

def log_calls(func):
    @functools.wraps(func)  # 保留原函数的 __name__/__doc__,不加会被 wrapper 覆盖掉
    def wrapper(*args, **kwargs):
        print(f"调用 {func.__name__},参数: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} 返回: {result}")
        return result
    return wrapper

@log_calls
def add(a, b):
    """返回两数之和"""
    return a + b

print(add(2, 3))
print(add.__name__, add.__doc__)  # add 返回两数之和,因为用了 functools.wraps

# 带参数的装饰器:本质是"装饰器工厂",外面再包一层函数用来接收参数
def retry(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except ValueError as e:
                    print(f"第 {attempt} 次失败: {e}")
                    if attempt == times:
                        raise
        return wrapper
    return decorator

counter = {"n": 0}

@retry(times=3)
def flaky():
    counter["n"] += 1
    if counter["n"] < 3:
        raise ValueError("暂时失败")
    return "成功"

print(flaky())  # 打印两次失败提示后,最终输出 "成功"

# 耗时统计也是典型的 AOP 切面
def timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} 耗时 {elapsed:.6f}s")
        return result
    return wrapper

@timing
def slow_square(n):
    return n * n

print(slow_square(9))  # 81
```

面试常问的两个细节:`functools.wraps` 的作用是保留被装饰函数的 `__name__`/`__doc__`/`__module__` 等元信息,否则 `add.__name__` 会变成 `"wrapper"`;类装饰器和函数装饰器同理,`@classmethod`/`@staticmethod`/`@property` 本质也都是装饰器。

### 27. 迭代器与生成器

**问:迭代器和生成器分别是什么?有什么关系和区别?**

- **迭代器(iterator)**:实现了 `__iter__`(返回自身)和 `__next__`(返回下一个值,没有更多值时抛 `StopIteration`)这两个方法的对象,是 Python `for` 循环、`in` 判断等背后的统一协议。
- **可迭代对象(iterable)**:实现了 `__iter__` 方法、能通过 `iter()` 产出一个迭代器的对象(如 `list`、`dict`、`str`),可迭代对象本身不一定是迭代器。
- **生成器(generator)**:一种特殊的迭代器,不需要手写 `__iter__`/`__next__`,只要函数体内出现 `yield` 关键字,调用它就会返回一个生成器对象;每次 `next()` 会执行到下一个 `yield` 处暂停并"冻结"当前所有局部变量和执行位置,下次调用再从暂停处继续。

```python
# 手写迭代器
class CountUp:
    def __init__(self, limit):
        self.limit = limit
        self.current = 0
    def __iter__(self):
        return self
    def __next__(self):
        if self.current >= self.limit:
            raise StopIteration
        self.current += 1
        return self.current

for x in CountUp(3):
    print("iterator:", x)  # 1 2 3

# 用 yield 写生成器,效果等价但代码简洁得多
def count_up(limit):
    current = 0
    while current < limit:
        current += 1
        yield current

gen = count_up(3)
print(type(gen))  # <class 'generator'>
print(next(gen), next(gen), next(gen))  # 1 2 3
try:
    next(gen)
except StopIteration:
    print("生成器耗尽")

# 核心优势:惰性求值,天然支持无限序列而不会撑爆内存
def infinite_naturals():
    n = 1
    while True:
        yield n
        n += 1

gen2 = infinite_naturals()
print([next(gen2) for _ in range(5)])  # [1, 2, 3, 4, 5]

# yield from 把生成过程委托给另一个可迭代对象,常用于生成器组合
def chain(*iterables):
    for it in iterables:
        yield from it

print(list(chain([1, 2], (3, 4), "ab")))  # [1, 2, 3, 4, 'a', 'b']
```

面试常见追问:生成器为什么省内存(不用一次性把所有元素放进列表,而是按需产出一个算一个)、`return` 语句在生成器里的含义(相当于抛出 `StopIteration` 并携带返回值,可通过 `StopIteration.value` 或 `yield from` 拿到)、协程和生成器的渊源(早期 Python 协程 `async`/`await` 就是在生成器 `yield`/`send` 机制基础上演化出来的)。

---

## 四、并发与并行

### 28. GIL 全局解释器锁

**问:什么是 GIL?为什么 Python 要有它?**

GIL(Global Interpreter Lock,全局解释器锁)是 **CPython 解释器**(注意:这是 CPython 的实现细节,不是 Python 语言规范的一部分,PyPy/Jython 等实现不一定有)内部的一把互斥锁,保证**同一时刻只有一个线程在执行 Python 字节码**,即便在多核 CPU 上开了再多线程,CPU 密集型代码也无法利用多核并行。它存在的历史原因是 CPython 用**引用计数**做垃圾回收(见后文),如果不加锁,多线程同时修改同一个对象的引用计数会产生竞态条件(race condition),导致内存被提前释放或永远无法释放;GIL 用一把全局大锁简单粗暴地解决了这个线程安全问题,代价是牺牲了多线程在 CPU 密集任务上的并行能力。

```python
import threading
import time

def cpu_bound(n):
    while n > 0:
        n -= 1

start = time.perf_counter()
cpu_bound(20_000_000)
cpu_bound(20_000_000)
print("单线程总耗时:", time.perf_counter() - start)  # 约 0.73s

start = time.perf_counter()
t1 = threading.Thread(target=cpu_bound, args=(20_000_000,))
t2 = threading.Thread(target=cpu_bound, args=(20_000_000,))
t1.start(); t2.start()
t1.join(); t2.join()
print("多线程总耗时(受 GIL 限制,不会明显更快):", time.perf_counter() - start)  # 约 0.73s
```

两组耗时几乎一样,证明两个线程并没有真正并行执行 CPU 密集型代码——同一时刻始终只有一个线程持有 GIL 在跑字节码,另一个在等待。

### 29. GIL 与多线程 / 多进程 / asyncio 的关系

**问:既然有 GIL,Python 的多线程、多进程、asyncio 应该怎么选?**

- **多线程(`threading`)**:受 GIL 限制,**不适合 CPU 密集型**任务(算不动就是算不动,多线程反而有切换开销);但对 **I/O 密集型**任务(网络请求、磁盘读写、数据库查询)非常有效——因为线程在等待 I/O 时会**主动释放 GIL**,让别的线程获得执行机会,多个线程的等待时间可以重叠。
- **多进程(`multiprocessing`)**:每个进程有**独立的解释器和独立的 GIL**,能真正利用多核并行,适合 CPU 密集型任务;代价是进程间通信(IPC)成本更高、内存不共享、创建开销比线程大。
- **`asyncio`(协程)**:单线程内基于事件循环做**协作式多任务**,同样只适合 I/O 密集型场景(必须配合 `async`/`await` 生态的库,如 `aiohttp`),优势是没有线程切换和锁的开销,能用很小的资源支撑海量并发连接,是目前 Python 高并发网络服务的主流方案。

```python
def io_bound():
    time.sleep(0.3)  # 模拟网络/磁盘 IO,阻塞时会释放 GIL

start = time.perf_counter()
io_bound(); io_bound()
print("单线程总耗时:", time.perf_counter() - start)  # 约 0.6s

threads = [threading.Thread(target=io_bound) for _ in range(2)]
start = time.perf_counter()
for t in threads: t.start()
for t in threads: t.join()
print("多线程总耗时(IO 密集型场景,多线程仍能明显加速):", time.perf_counter() - start)  # 约 0.3s
```

多进程能绕开 GIL 实现真并行(同样的 CPU 密集任务,两个进程耗时约 0.39s,明显快于两个线程/单线程的约 0.73s),但注意 `multiprocessing` 需要在 `if __name__ == "__main__":` 保护下运行,且进程间传数据需要序列化(`pickle`),开销不可忽视。一句话选型口诀:**CPU 密集用多进程,I/O 密集用多线程或 asyncio,能用 asyncio 处理海量连接就优先 asyncio**。

### 30. 协程(Coroutine)

**问:什么是协程?和线程有什么区别?**

协程(coroutine)是一种**用户态、单线程内**的并发方式:代码在遇到 I/O 等待点时**主动让出**执行权,由一个事件循环(event loop)去调度下一个就绪的协程,等 I/O 完成后再择机切回来继续执行。与线程相比,协程的切换发生在用户代码层面而非操作系统内核态,没有线程上下文切换的开销,也不需要加锁防止竞态(因为同一时刻单线程里只有一个协程在跑),因此能用极低的资源开销支撑成千上万的并发连接,非常适合网络 I/O 密集型服务。

Python 现代协程基于 `async def` 定义、`await` 挂起等待点,底层由 `asyncio` 事件循环调度:

```python
import asyncio
import time

async def fetch_data(name, delay):
    print(f"{name} 开始请求")
    await asyncio.sleep(delay)  # 模拟 IO 等待,期间把控制权交还给事件循环
    print(f"{name} 请求完成")
    return f"{name} 的结果"

async def main():
    start = time.perf_counter()
    r1 = await fetch_data("任务A", 0.3)  # 顺序 await,耗时约等于两者相加
    r2 = await fetch_data("任务B", 0.3)
    print("顺序执行耗时:", time.perf_counter() - start)  # 约 0.6s

    start = time.perf_counter()
    results = await asyncio.gather(       # 并发调度,单线程内实现并发等待
        fetch_data("任务C", 0.3),
        fetch_data("任务D", 0.3),
    )
    print(results)
    print("并发执行耗时:", time.perf_counter() - start)  # 约 0.3s

asyncio.run(main())
```

补充一点历史脉络:早期 Python(2.5+)就已经能用生成器的 `yield`/`send` 手工模拟协程,`asyncio` + `async`/`await`(3.5+ 正式语法)是在此基础上标准化、语言层面原生支持后的产物,面试时如果被问"协程和生成器的关系",可以提到二者共享同一套底层的"可暂停/可恢复执行"机制。

---

## 五、内存管理与垃圾回收

### 31. 引用计数

**问:CPython 的垃圾回收(GC)是怎么工作的?**

CPython 的内存管理主要靠**引用计数(reference counting)**打底,再用**标记-清除(mark-sweep)+ 分代回收(generational)**处理引用计数解决不了的循环引用问题,三者结合构成完整的 GC 体系。

每个对象内部都有一个引用计数字段,记录当前有多少个引用指向它:新增一个引用(赋值、作为参数传递、放入容器等)计数加一,引用消失(变量被 `del`、离开作用域、被重新赋值等)计数减一,**一旦计数归零,对象占用的内存会被立即回收**,不需要等待任何"回收周期"——这也是 CPython 相比 Java 等语言 GC 的一个显著特点:内存释放通常是即时的、可预测的。

```python
import sys

a = []
print(sys.getrefcount(a) - 1)  # 1(减 1 是排除 getrefcount 自身参数传递引入的临时引用)

b = a  # 新增一个引用
print(sys.getrefcount(a) - 1)  # 2

del b  # 减少一个引用
print(sys.getrefcount(a) - 1)  # 1

class Tracked:
    def __del__(self):
        print("对象被销毁")

t = Tracked()
print("准备删除")
del t  # 引用计数归零,__del__ 立即被调用,内存立即回收
print("删除完毕")
```

引用计数的代价:每次引用增减都要维护这个计数器,有一定性能开销;而且**无法处理循环引用**——如果 A 引用 B、B 又引用 A,即便外部不再有任何变量指向它们俩,彼此之间的引用计数也永远不会归零,单靠引用计数会造成内存泄漏,这就需要下面的分代回收器来兜底。

### 32. 标记-清除与分代回收(循环引用怎么办)

**问:循环引用会造成内存泄漏吗?Python 怎么解决?**

会,但 CPython 内置了专门的**分代垃圾回收器**(`gc` 模块)来解决这个问题,它只需要负责跟踪**可能产生循环引用的容器类型对象**(自定义类实例、list、dict、set 等,不包括 int、str 这类不可能引用自身的简单对象),定期用**标记-清除**算法:从一组根对象出发遍历所有可达对象打上标记,遍历结束后没被标记到的对象就是"垃圾"(通常是彼此循环引用、但外部已不可达的对象),整体清除掉。

为了减少每次全量扫描的开销,CPython 把对象按存活时间分为**三代(0/1/2 代)**:新创建的对象放进第 0 代,每熬过一次那一代的回收扫描还存活,就晋升到下一代;**新对象更可能很快变成垃圾**(弱代假设),所以第 0 代扫描最频繁,第 2 代(存活最久、最稳定的对象)扫描最少,用这种"分代"策略平衡了 GC 开销和及时性。

```python
import gc

class Node:
    def __init__(self, name):
        self.name = name
        self.ref = None
    def __del__(self):
        print(f"{self.name} 被销毁")

gc.disable()  # 先关掉自动 GC,方便观察引用计数单独工作的效果

a = Node("A")
b = Node("B")
a.ref = b
b.ref = a  # 循环引用:a 引用 b,b 也引用 a

del a
del b
print("del 之后,如果只靠引用计数,循环引用的对象不会被销毁(因为互相还有一个引用)")

gc.collect()  # 手动触发分代垃圾回收器,专门用来找到并打破这种循环引用
print("手动 gc.collect() 之后,循环引用被检测到并清理")
# 实际输出顺序:两条"被销毁"的打印,恰好发生在 gc.collect() 之后

gc.enable()
print("当前分代阈值:", gc.get_threshold())  # (700, 10, 10),三代对应不同的回收触发频率
```

### 33. 小整数池与字符串驻留(intern)

**问:小整数池和字符串驻留是什么?**

这是 CPython 出于性能考虑做的两类**对象复用优化**,本质都是"避免重复创建相同的、不可变的小对象":

- **小整数池**:CPython 启动时会预先创建好 `-5 ~ 256` 这个区间的所有 `int` 对象并常驻,任何用到这个范围整数的地方都直接复用同一份对象,不会重新分配内存,因为这个范围的整数在程序里出现频率极高(计数器、索引、布尔判断等)。
- **字符串驻留(interning)**:形如合法标识符的字符串字面量(不含空格特殊字符,编译期能确定的常量)会被自动"驻留"到一张全局表里复用;运行时动态拼接出来的字符串一般不会自动驻留,可以用 `sys.intern()` 手动请求驻留。驻留的好处是相同内容的字符串只占一份内存,且用 `is` 比较(在明确驻留的前提下)比逐字符比较 `==` 更快。

```python
a = 100
b = 100
print(a is b)  # True,都指向小整数池里的同一个对象

x2 = int("257")  # 用运行时构造避开编译期常量折叠
y2 = int("257")
print(x2 is y2)  # False,257 超出小整数池范围([-5, 256]),是两个独立对象

s1 = "hello"
s2 = "hello"
print(s1 is s2)  # True,字面量驻留

s3 = "".join(["hel", "lo"])
s4 = "".join(["hel", "lo"])
print(s3 is s4)  # False,运行时拼接产生的字符串通常不会自动驻留
print(s3 == s4)  # True,值相等,== 才是判断内容相等该用的方式

print(sys.intern(s3) is sys.intern(s4))  # True,手动 intern 后可以强制复用同一份
```

**这些都是 CPython 的实现细节和性能优化,不是语言语义保证**,业务代码永远不应该依赖 `is` 来判断两个 `int`/`str` 是否"值相等"——正确的值比较方式永远是 `==`。

### 34. `list` 的底层实现

**问:Python 的 `list` 底层是怎么实现的?为什么 `append` 快、头部插入慢?**

CPython 的 `list` 底层是一个**动态数组(over-allocating array)**,不是链表:内部维护一段**连续内存**,存放的是指向各元素对象的指针数组。这决定了它的几个关键性能特征:

- **随机访问 `lst[i]`**:O(1),直接按下标算偏移量取指针。
- **尾部 `append`**:均摊(amortized) O(1)——CPython 在扩容时不是每次只多分配一个位置,而是按照一定的**超量分配策略**一次多申请一些富余空间,这样接下来的几次 `append` 不需要重新分配内存和拷贝,只有当富余空间用完时才会触发一次"扩容 + 整体拷贝"到更大的新内存块。
- **头部或中间 `insert(0, x)` / `pop(0)`**:O(n),因为要把插入点之后的所有元素**整体往后(或往前)搬移一位**,元素越多越慢——这也是为什么"频繁从头部操作"的场景应该用 `collections.deque` 而不是 `list`。

```python
import sys

lst = []
prev_size = sys.getsizeof(lst)
print(f"空列表大小: {prev_size} 字节")  # 56
for i in range(10):
    lst.append(i)
    size = sys.getsizeof(lst)
    if size != prev_size:
        print(f"添加第 {i+1} 个元素后,容量扩张,占用变为 {size} 字节")
        prev_size = size
# 可以看到容量不是每加一个元素就长一点,而是跳跃式增长——这就是超量分配

print(lst[5])           # O(1) 随机访问
lst.insert(0, "x")      # O(n),需要搬移所有元素
print(lst[:3])
```

---

## 六、异常处理与上下文管理器

### 35. 异常处理机制

**问:Python 异常处理的 `try`/`except`/`else`/`finally` 分别在什么时候执行?怎么自定义异常?**

- `try`:放可能出错的代码。
- `except`:捕获并处理指定类型的异常,可以写多个分支按类型精确处理,也可以用元组一次捕获多种类型;越具体的异常类型应该写在越前面(因为是从上往下第一个匹配的分支生效)。
- `else`:**只有 `try` 块完全没有抛出异常**才会执行,用来存放"确认成功后才需要做"的逻辑,好处是把它和 `try` 里可能抛异常的代码区分开,避免 `else` 里的代码本身的异常被误当成 `try` 块的异常捕获。
- `finally`:**无论是否发生异常都会执行**,常用来做资源释放(关文件、断连接、解锁)等收尾工作,即使 `try`/`except` 里有 `return`,`finally` 也会在函数真正返回前执行。

```python
def divide(a, b):
    try:
        result = a / b
    except ZeroDivisionError as e:
        print(f"捕获到除零错误: {e}")
        result = None
    except (TypeError, ValueError) as e:
        print(f"捕获到类型/值错误: {e}")
        result = None
    else:
        print("没有异常发生,else 块执行")
    finally:
        print("finally 总会执行,常用来释放资源")
    return result

print(divide(10, 2))  # else 执行、finally 执行,返回 5.0
print(divide(10, 0))  # except 执行、finally 执行,返回 None
```

**自定义异常**:继承 `Exception`(或更贴近语义的内置异常类,如 `ValueError`),在 `__init__` 里附加业务需要的上下文信息,便于上层针对性捕获和处理:

```python
class InsufficientBalanceError(Exception):
    def __init__(self, balance, amount):
        self.balance = balance
        self.amount = amount
        super().__init__(f"余额 {balance} 不足以支付 {amount}")

def withdraw(balance, amount):
    if amount > balance:
        raise InsufficientBalanceError(balance, amount)
    return balance - amount

try:
    withdraw(100, 200)
except InsufficientBalanceError as e:
    print("自定义异常:", e)
```

**异常链**:用 `raise NewError(...) from original_error` 可以在包装异常的同时保留原始异常的上下文(存在 `__cause__` 里),方便排查根因而不丢失现场信息:

```python
def parse_config(raw):
    try:
        return int(raw)
    except ValueError as e:
        raise RuntimeError("配置解析失败") from e

try:
    parse_config("abc")
except RuntimeError as e:
    print("外层异常:", e)          # 配置解析失败
    print("原始异常:", e.__cause__) # invalid literal for int() with base 10: 'abc'
```

### 36. 上下文管理器:`with` 语句 / `__enter__` / `__exit__`

**问:`with` 语句是怎么工作的?怎么自己实现一个上下文管理器?**

`with` 语句是管理"需要成对获取/释放"的资源(文件句柄、锁、数据库连接、网络连接等)的标准写法,本质是一层语法糖:进入 `with` 块时自动调用对象的 `__enter__`,离开 `with` 块时(不管是正常结束还是抛出了异常)**保证**自动调用 `__exit__`——比手写 `try`/`finally` 更简洁,也更不容易漏写释放逻辑。

- `__enter__(self)`:返回值会绑定到 `with ... as x` 的 `x` 上。
- `__exit__(self, exc_type, exc_value, traceback)`:如果 `with` 块内抛了异常,这三个参数会带上异常信息;`__exit__` 返回 `True` 表示"我已经处理好这个异常了,不要再往外传播",返回 `False`/`None`(默认)则异常会继续正常向外抛出。

```python
import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        elapsed = time.perf_counter() - self.start
        print(f"耗时: {elapsed:.6f}s")
        if exc_type is not None:
            print(f"发生了异常: {exc_type.__name__}: {exc_value}")
        return True  # 吞掉异常,不再向外传播

with Timer() as t:
    total = sum(range(1000))
    print(total)  # 499500

with Timer():
    raise ValueError("出错了")  # __exit__ 返回 True,这里异常不会往外传播

print("程序继续正常运行")
```

除了手写类,更轻量的方式是用 `contextlib.contextmanager` 装饰器把一个生成器函数变成上下文管理器:`yield` 之前的代码相当于 `__enter__`,`yield` 之后(通常放在 `finally` 里)的代码相当于 `__exit__`。

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(name):
    print(f"获取资源: {name}")
    try:
        yield name
    finally:
        print(f"释放资源: {name}")

with managed_resource("数据库连接") as res:
    print(f"使用资源: {res}")
# 获取资源: 数据库连接
# 使用资源: 数据库连接
# 释放资源: 数据库连接
```

---

## 七、类型注解与常用标准库

### 37. 类型注解(typing)

**问:Python 的类型注解是什么?运行期会强制检查吗?**

类型注解(type hint,`typing` 模块)让 Python 这门动态类型语言可以在函数签名、变量上**标注期望的类型**,提升代码可读性、方便 IDE 做智能提示,并配合静态检查工具(`mypy`、`pyright`)在**编码阶段**(而非运行期)提前发现类型错误。**关键点:类型注解只是提示信息,Python 解释器本身在运行时完全不会因为类型不匹配而报错**——这是它和 TypeScript、Java 泛型等"真正做编译期类型检查"的语言的本质区别。

```python
from typing import List, Dict, Optional, Union, Callable

def greet(name: str, times: int = 1) -> str:
    return ("hi " + name + "! ") * times

def process(items: List[int]) -> Dict[str, int]:
    return {"count": len(items), "sum": sum(items)}

def find_user(uid: int) -> Optional[str]:  # 等价于 Union[str, None]
    return "Ann" if uid == 1 else None

def add(a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
    return a + b

Handler = Callable[[int, int], int]  # 类型别名:描述一个函数签名
def apply(handler: Handler, a: int, b: int) -> int:
    return handler(a, b)

print(apply(lambda x, y: x + y, 3, 4))  # 7

def bad(x: int) -> int:
    return x

print(bad("这其实是个字符串,解释器不会报错"))  # 运行时不会因为类型不符而报错

print(greet.__annotations__)  # 注解信息保存在函数的 __annotations__ 属性里
```

现代 Python(3.9+)可以直接用内置的 `list[int]`、`dict[str, int]` 代替 `typing.List[int]`/`typing.Dict[str, int]`,`typing` 模块的这些泛型别名逐渐成为历史写法但仍然常见于现存代码中。

### 38. `collections` 模块

**问:`collections` 模块提供了哪些常用容器?**

`collections` 提供了一批比内置 `list`/`dict` 更专用、更高效的数据结构,是刷题和实际业务代码里都极高频出现的模块:

- `namedtuple`:轻量级、不可变、带字段名的元组,比自定义类省事,适合表示简单的数据记录。
- `defaultdict`:访问不存在的 key 时自动用工厂函数生成默认值,省去 `if key not in dict` 的样板代码。
- `Counter`:专门用于计数,`most_common(n)` 直接拿到出现频率最高的前 n 项。
- `deque`:双端队列,头尾两端的插入/删除都是 O(1)(底层是双向链表式的分块结构),需要频繁从头部操作时应该用它代替 `list`。
- `OrderedDict`:保证顺序并提供 `move_to_end` 等额外方法(Python 3.7+ 起普通 `dict` 本身已保证插入顺序,但 `OrderedDict` 仍有额外的顺序操作能力,且比较相等时会考虑顺序)。

```python
from collections import namedtuple, defaultdict, Counter, deque, OrderedDict

Point = namedtuple("Point", ["x", "y"])
p = Point(1, 2)
print(p.x, p.y, p)  # 1 2 Point(x=1, y=2)

dd = defaultdict(list)
dd["fruits"].append("apple")
dd["fruits"].append("banana")
print(dict(dd))  # {'fruits': ['apple', 'banana']}

c = Counter("abracadabra")
print(c)  # Counter({'a': 5, 'b': 2, 'r': 2, 'c': 1, 'd': 1})
print(c.most_common(2))  # [('a', 5), ('b', 2)]

dq = deque([1, 2, 3])
dq.appendleft(0)
dq.append(4)
print(dq)  # deque([0, 1, 2, 3, 4])
dq.popleft()
print(dq)  # deque([1, 2, 3, 4])

od = OrderedDict()
od["a"] = 1
od["b"] = 2
od.move_to_end("a")
print(od)  # OrderedDict([('b', 2), ('a', 1)])
```

### 39. `itertools` 模块

**问:`itertools` 模块有哪些常用工具?**

`itertools` 提供了一系列用于**高效处理迭代器**的组合子,全都是惰性求值(返回迭代器而不是立即算出所有结果),特别适合处理大数据量或组合数学类问题:

```python
import itertools

print(list(itertools.chain([1, 2], [3, 4], [5])))  # 串联多个可迭代对象:[1, 2, 3, 4, 5]

print(list(itertools.permutations([1, 2, 3], 2)))  # 排列(考虑顺序)
print(list(itertools.combinations([1, 2, 3], 2)))  # 组合(不考虑顺序)

print(list(itertools.product([1, 2], ["a", "b"])))  # 笛卡尔积

counter = itertools.count(start=10, step=2)  # 无限计数器,惰性
print([next(counter) for _ in range(4)])  # [10, 12, 14, 16]

print(list(itertools.islice(itertools.count(1), 5)))  # 对无限迭代器切片,取前 5 个

for key, group in itertools.groupby([1, 1, 2, 2, 2, 3]):  # 对相邻相同元素分组
    print(key, list(group))

print(list(itertools.accumulate([1, 2, 3, 4])))  # 累加(前缀和):[1, 3, 6, 10]
```

### 40. `functools` 模块

**问:`functools` 模块有哪些常用工具?**

`functools` 提供了操作"函数本身"的高阶工具,前面装饰器一节已经用到过 `functools.wraps`,其他几个高频考点:

- `lru_cache`:自动给函数结果加缓存(memoization),按参数组合缓存返回值,常用来加速递归(如斐波那契数列)或幂等的重复计算。
- `reduce`:把序列累积成一个值(前面函数式编程一节已介绍)。
- `partial`:固定一个函数的部分参数,生成一个参数更少的新函数,常用于简化回调函数的调用签名。
- `total_ordering`:类只需实现 `__eq__` 和其中一个比较方法(如 `__lt__`),就能自动补全其余的比较运算符(`__le__`/`__gt__`/`__ge__`),避免手写全部六个比较方法。

```python
import functools

@functools.lru_cache(maxsize=None)  # 自动缓存函数调用结果,按参数做 memoization
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(30))  # 832040
print(fib.cache_info())  # 查看缓存命中情况

def add(a, b, c):
    return a + b + c

add_five = functools.partial(add, 5)  # 固定部分参数,生成一个新的、参数更少的函数
print(add_five(10, 20))  # 35,等价于 add(5, 10, 20)

@functools.total_ordering  # 只需实现 __eq__ 和一个比较方法,自动补全其余比较运算符
class Money:
    def __init__(self, amount):
        self.amount = amount
    def __eq__(self, other):
        return self.amount == other.amount
    def __lt__(self, other):
        return self.amount < other.amount

print(Money(10) < Money(20), Money(10) <= Money(10), Money(20) > Money(10))  # True True True
```

---

[← 返回索引](index.md)
