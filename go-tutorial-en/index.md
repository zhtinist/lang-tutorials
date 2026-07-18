# Go Tutorial · For C/C++ Programmers

> This tutorial assumes you are already comfortable with C/C++ (pointers, stack/heap, pass-by-value vs. reference, compilation and linking, manual memory management).
> Go is the "friendliest" language for C/C++ programmers—it has real pointers, value types, structs, and compiles to native machine code;
> but there are also many places where you need to see through to the underlying layer: **what exactly happens on every operation**—
> for example, `a = b` is a byte-for-byte copy for value types, but for a slice/map it copies only the "header"?
> How does a slice's `len/cap/underlying-array-pointer` triple work? Why are goroutines cheap? How does escape analysis decide stack vs. heap?

## Reading Order (suggested)

| # | Chapter | One-line summary |
|---|------|-----------|
| 01 | [Runtime Model: Compilation, Linking, Runtime](01-运行模型.md) | Compiles to a static native binary, ships with a runtime (scheduler + GC) |
| 02 | [Basic Syntax (contrasted with C/C++)](02-基础语法.md) | Packages, `:=`, multiple return values, no implicit conversion, type comes last |
| 03 | [⭐ Variables and the Memory Model: what exactly happens in `a = b`](03-变量与内存模型.md) | Everything is a value copy, pointers are explicit, escape analysis decides stack/heap |
| 04 | [Data Types and Memory Layout](04-数据类型.md) | Fixed-width numerics, `struct` alignment, read-only `string` header, two-word `interface` |
| 05 | [Control Flow](05-控制流.md) | Only `for`, `switch` with no fallthrough, the mechanics of `defer` |
| 06 | [Functions, Methods, and the Call Stack: the truth about parameter passing](06-函数与调用栈.md) | Everything is pass-by-value, value vs. pointer receivers, growable goroutine stacks |
| 07 | [The Internal Implementation of Composite Data Structures](07-复合数据结构.md) | ⭐ The slice triple and its growth, the map's hash buckets, the channel's ring queue |
| 08 | [The Type System: Structs, Interfaces, Method Sets](08-面向对象与类型系统.md) | Composition over inheritance, the interface `(type, value)` two-word, generics |
| 09 | [Error Handling and Garbage Collection](09-错误处理与资源管理.md) | `error` is a value, `panic/recover`, the concurrent tricolor mark GC |
| 10 | [The Concurrency Model: goroutines and channels](10-并发模型.md) | The GMP scheduler, CSP, `select`, the memory model and `sync` |
| 11 | [Algorithms and Data Structures in the Standard Library](11-标准库算法.md) | `sort`, `slices`/`maps` (generic), `container/heap`, `container/list` |
| 12 | [A Quick Tour of Common Third-Party Libraries](12-常用第三方库.md) | Ecosystem landscape: web frameworks, serialization, logging, testing, etc. |

## A Few "Under-the-Hood Perspectives" That Run Through the Whole Tutorial

1. **In Go, assignment and argument passing are always a "value copy"**—once you internalize this, the "looks-like-a-reference" behavior of slice/map/channel all becomes explainable: what they copy is a very small "header struct," and that header contains a pointer to the underlying data.
2. **Pointers are explicit and safe**: you have `&` and `*`, but there is no pointer arithmetic; the compiler uses **escape analysis** to decide whether a variable goes on the stack or the heap, and the GC handles reclamation.
3. **Concurrency is built into the language**: `go f()` launches a goroutine that the runtime schedules onto OS threads, and a `channel` is a lock-protected, type-safe queue—not a library, but a language primitive.

> Every chapter ends with "Prev / Next" navigation, and related concepts in the body cross-link to one another.
