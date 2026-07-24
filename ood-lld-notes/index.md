# 面向对象与低层设计笔记 · OOD / LLD Notes

---

## 目录

### 第零章 · OOP 基础与原则

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| OOP 基础 | [oop-basics.md](oop-basics.md) | 封装/继承/多态/抽象、组合优于继承、Python 示例 |
| SOLID 原则 | [solid-principles.md](solid-principles.md) | SRP/OCP/LSP/ISP/DIP：意图、反例、正例、口诀 |
| UML 类图基础 | [uml-basics.md](uml-basics.md) | 类/接口/关联聚合组合、ASCII 类图、白板画法 |

### 第一章 · 设计模式精讲

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| 创建型模式 | [patterns-creational.md](patterns-creational.md) | Singleton、Factory Method、Abstract Factory、Builder、Prototype |
| 结构型模式 | [patterns-structural.md](patterns-structural.md) | Adapter、Decorator、Facade、Proxy、Composite |
| 行为型模式 | [patterns-behavioral.md](patterns-behavioral.md) | Strategy、Observer、State、Template Method、Command、Chain |

### 第二章 · LLD 面试框架

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| LLD 面试框架 | [lld-framework.md](lld-framework.md) | 5 步流程、时间预算、评分维度、模式触发信号表 |

### 第三章 · 经典案例分析

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| 停车场 | [case-parking-lot.md](case-parking-lot.md) | 完整走通框架：FeeStrategy、类图、扩展点 |
| 图书管理系统 | [case-library.md](case-library.md) | 借还书、会员、库存、搜索 |
| 限流器 | [case-rate-limiter.md](case-rate-limiter.md) | Token Bucket / Sliding Window、线程安全 |

### 附录 · 习题

| 内容 | 文件 | 说明 |
|------|------|------|
| 习题推荐 | [exercises.md](exercises.md) | Elevator、Vending、Chess、Ticket Booking 等 |

---

## 使用建议

1. **速成面试路线**: OOP 基础 → SOLID → LLD 框架 → 停车场案例 → 限流器 → 习题表挑 2 题白板练习
2. **系统学习**: 按章节顺序阅读；每学完一个模式，用「意图 + 信号 + 一句话结构」口头复述
3. **做案例时**: 先自己按 [lld-framework.md](lld-framework.md) 走完 5 步，再对照案例文；重点对比「变化轴」是否抽成接口
4. **代码风格**: Python 3.12+ 类型注解、docstring、中文行内注释；面试白板可省略类型，但心里要清楚
5. **模式不是目的**: 先把需求与实体说清楚，再谈模式；能用组合解决的，不要硬套继承树
6. **阅读顺序**: 每篇/每个模式都是「先大白话类比讲清是什么问题，再看 UML 图和代码」；如果类比部分已经很熟，可以直接跳到「意图」往后看细节

