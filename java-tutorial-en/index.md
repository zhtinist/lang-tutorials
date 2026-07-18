# Java Tutorial · For C/C++ Programmers

> This tutorial assumes you are already comfortable with C/C++ (pointers, stack/heap, pass-by-value vs. by-reference, compile-and-link, manual memory management).
> We won't dwell on "what is a class, what is a loop." Instead we focus on **what actually happens inside the JVM for every operation**—
> for example, what does `a = b` mean for a primitive type versus a reference type? What does an object's in-heap memory layout look like (object header, mark word)?
> How are `ArrayList` and `HashMap` structured internally? And what are JIT, GC, and happens-before all about?

## Reading Order (recommended)

| # | Chapter | One-line summary |
|---|------|-----------|
| 01 | [Runtime Model: javac, bytecode, the JVM, and JIT](01-运行模型.md) | Source → `.class` bytecode → interpretation + hot-spot JIT compilation |
| 02 | [Basic Syntax (contrasted with C/C++)](02-基础语法.md) | Everything lives in a class, statically typed, no header files or preprocessor |
| 03 | [⭐ Variables and the Memory Model: what really happens in `a = b`](03-变量与内存模型.md) | Primitives store values, reference types store "pointer values," stack frames and the heap |
| 04 | [Data Types and Memory Layout](04-数据类型.md) | The 8 primitive types, boxing cache, object header, string constant pool |
| 05 | [Control Flow](05-控制流.md) | `switch`'s tableswitch/lookupswitch, the enhanced for, `switch` pattern matching |
| 06 | [Methods and the Call Stack: the truth about parameter passing](06-函数与调用栈.md) | Java is pass-by-value only, stack-frame structure, method dispatch |
| 07 | [The Internals of the Collections Framework](07-复合数据结构.md) | Arrays, `ArrayList` growth, `HashMap` buckets + red-black trees, `LinkedList` |
| 08 | [Object Orientation and the Type System](08-面向对象与类型系统.md) | Inheritance, interfaces, virtual method tables, generic erasure, `record`/`sealed` |
| 09 | [Exception Handling and Garbage Collection](09-错误处理与资源管理.md) | Checked exceptions, `try-with-resources`, generational GC and the various collectors |
| 10 | [The Concurrency Model: threads, memory model, locks](10-并发模型.md) | JMM, `volatile`, `synchronized`, `java.util.concurrent`, virtual threads |
| 11 | [Algorithms and Data Structures in the Standard Library](11-标准库算法.md) | `Collections`, `Arrays.sort` (dual-pivot quicksort/Timsort), `PriorityQueue`, `Stream` |
| 12 | [A Quick Tour of Common Third-Party Libraries](12-常用第三方库.md) | Where Guava, Jackson, Spring, JUnit, etc. fit in |

## A Few "Under-the-Hood Perspectives" That Run Through the Whole Tutorial

1. **Distinguishing "primitive types" from "reference types" is the key to understanding Java**: an `int` puts its value directly in the stack frame's local variable table; objects always live on the heap, and a variable holds a "reference value pointing to the heap" (think of it as a managed pointer).
2. **Java has exactly one way to pass arguments: by value**—it's just that for a reference type, what gets passed is a copy of the "value that references the object," so you can change the object's contents but not what the caller's variable points to.
3. **The JVM does for you what you do manually in C/C++**: memory allocation, reclamation (GC), bounds checking, type safety—but the costs and behavior are all observable and tunable.

> Every chapter ends with "Prev / Next" navigation, and related concepts cross-link to one another within the body text.
