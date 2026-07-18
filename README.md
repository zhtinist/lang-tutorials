# 面向 C/C++ 程序员的其他语言教程

> 三套教程:**Python / Java / Go**,写给**已经精通 C/C++** 的工程师。
> 不重复"什么是变量、什么是循环",而是讲清 **每一个操作在底层到底发生了什么**,并处处与 C/C++ 对照。

📖 **在线阅读(GitHub Pages)**:https://zhtinist.github.io/lang-tutorials/

## 内容

| 教程 | 入口 | 侧重 |
|------|------|------|
| **Python** | [python-tutorial/](python-tutorial/index.md) | 一切皆堆上对象、名字即引用、引用计数 + GC、GIL 与 free-threading |
| **Java** | [java-tutorial/](java-tutorial/index.md) | 基本类型 vs 引用类型、对象头与逃逸分析(标量替换)、JMM 与虚拟线程、GC 演进 |
| **Go** | [go-tutorial/](go-tutorial/index.md) | 一切皆值拷贝、slice/map/channel 的表头结构、逃逸分析、GMP 调度、Swiss Tables |

每套 12 章 + 目录,章节间可互相跳转;主题统一为:运行模型 → 基础语法 → **变量与内存模型(核心)** → 数据类型 → 控制流 → 函数与调用栈 → 复合数据结构 → 面向对象/类型系统 → 错误处理与 GC → 并发模型 → 标准库算法 → 常用第三方库。

## 每套贯穿的"底层视角"

- **Python**:CPython 里除少数优化外一切值都是堆上的 `PyObject`,变量只是指向它的名字;`a = b` 拷的是指针不是数据。
- **Java**:基本类型把值放进栈帧局部变量表,对象永远在堆上、变量存"受管指针";Java 只有值传递。
- **Go**:赋值/传参永远是值拷贝,slice/map/channel"像引用"是因为它们是含指针的小表头;逃逸分析决定栈还是堆。

## 本地把 Markdown 生成静态站点

```bash
python3 build_site.py       # 依赖 pandoc;输出到 docs/,可用作 GitHub Pages
```

## 关于创作与署名

本教程内容在创作过程中**借助了 [Claude](https://claude.com/claude-code) 与 [Cursor](https://cursor.com) 辅助**撰写、校对与勘误;
所有事实性结论均经作者复核(如 CPython 3.14 的字节码/内存池、Go 1.24 的 Swiss Tables、JDK 24 的虚拟线程 pinning 等)。
作者 / 维护者:**HTZHU**(zhu.h4@northeastern.edu,GitHub [@zhtinist](https://github.com/zhtinist))。

## 许可证

[MIT](LICENSE) © HTZHU
