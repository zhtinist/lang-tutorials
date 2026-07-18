# Python Tutorial · For C/C++ Programmers

> This tutorial assumes you are already comfortable with C/C++ (pointers, stack/heap, pass-by-value vs. reference, compiling and linking, manual memory management).
> So we don't rehash "what is a variable, what is a loop." Instead we focus on **what actually happens under the hood for every operation**—
> for example, when you write `a = b`, does `a` receive a reference (pointer) to an object, or is a fresh block of memory allocated? How do mutable and immutable objects differ in memory?
> How are `list` and `dict` implemented internally? Why does the GIL exist?

## Suggested Reading Order

| # | Chapter | One-line summary |
|---|------|-----------|
| 01 | [The Execution Model: How CPython Runs Your Code](01-运行模型.md) | Source → bytecode → interpreter loop; objects live on the heap |
| 02 | [Basic Syntax (Contrasted with C/C++)](02-基础语法.md) | Indentation is scope, dynamic typing, everything is an expression |
| 03 | [⭐ Variables and the Memory Model: What Really Happens in `a = b`](03-变量与内存模型.md) | Name→object reference binding, `id()`, reference counting, small-int cache |
| 04 | [Data Types and Their Underlying Layout](04-数据类型.md) | `int` is a big object; the memory structure of `float`, `str`, `bytes` |
| 05 | [Control Flow](05-控制流.md) | Truthiness testing, the iterator protocol behind `for`, `match` |
| 06 | [Functions and the Call Stack: The Truth About Argument Passing](06-函数与调用栈.md) | "Pass object references," the default-argument trap, closures and cells |
| 07 | [The Internal Implementation of Compound Data Structures](07-复合数据结构.md) | `list` growth, `dict` open addressing, `set`, `tuple` |
| 08 | [Object Orientation and the Type System](08-面向对象与类型系统.md) | Everything is an object, `__dict__`, MRO, duck typing, `__slots__` |
| 09 | [Exception Handling and Garbage Collection](09-错误处理与资源管理.md) | Reference counting + generational GC, reference cycles, `with` vs. RAII |
| 10 | [The Concurrency Model: GIL, Threads, Coroutines](10-并发模型.md) | Why multithreading doesn't speed up compute, the `asyncio` event loop, multiprocessing |
| 11 | [Algorithms and Data Structures in the Standard Library](11-标准库算法.md) | `collections`, `heapq`, `bisect`, `itertools`, Timsort behind `sort` |
| 12 | [A Quick Tour of Common Third-Party Libraries](12-常用第三方库.md) | Where numpy, requests, pandas, pydantic, etc. fit in |

## A Few "Under-the-Hood Perspectives" That Run Through the Whole Tutorial

1. **There are no "objects on the stack" in CPython**: apart from a few cases the interpreter optimizes internally, every Python value (even the integer `3`) is a heap-allocated `PyObject`, and a variable is merely a name pointing to it.
2. **A variable = a name, not a memory slot**: C's `int a` is a 4-byte block of memory; Python's `a` is a key in a namespace dictionary whose value is a pointer to an object.
3. **"Mutable vs. immutable" governs all aliasing behavior**: grasp this and you can predict the outcome of every `=`, every function call, and every copy.

> Each chapter ends with "Prev / Next" navigation, and related concepts cross-link within the body text.
