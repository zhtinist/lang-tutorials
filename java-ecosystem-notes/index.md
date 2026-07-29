# Java 生态 · Spring 与设计模式实践

本专题补充 `java-tutorial` 里没有覆盖的框架生态部分：Spring 全家桶的定位关系与核心机制、设计模式在 Java 语言层面的具体写法。不重复讲 JVM 内存模型、类加载、GC 这类语言底层内容——那些属于 `java-tutorial` 的范畴。

---

## 目录

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| Spring 全家桶与 SpringBoot | [spring-boot-overview.md](spring-boot-overview.md) | Spring/SpringMVC/SpringBoot/SpringCloud 关系辨析、Starter 机制、自动装配、启动流程、SpringMVC 请求处理链路 |
| Spring 核心机制 | [spring-core-mechanisms.md](spring-core-mechanisms.md) | IOC 容器与 Bean 生命周期、依赖注入方式、AOP 实现原理、常用注解底层行为 |
| Java 设计模式实现细节 | [java-design-patterns.md](java-design-patterns.md) | 单例的 5 种 Java 写法与线程安全对比、工厂/建造者的 Java 惯用法、JDK 动态代理与 CGLIB 的区别、策略模式的 Lambda 化、装饰器与 java.io、观察者模式的替代方案 |

---

## 使用建议

1. 设计模式的**概念、意图、UML 结构、生活类比**已经在 [ood-lld-notes](../ood-lld-notes/index.md) 专题详细讲过，本专题的 `java-design-patterns.md` 只讲"用 Java 怎么落地、有哪些语言特有的坑"，两个专题配合读效果最好：先去 ood-lld-notes 建立概念，再回来看 Java 实现。
2. Spring 相关的两篇建议按顺序读：先 `spring-boot-overview.md` 建立"谁是谁"的框架，再读 `spring-core-mechanisms.md` 深入容器内部机制。
3. `java-design-patterns.md` 里的每段代码都用 JDK 实际编译运行验证过，遇到疑惑可以直接复制到本地跑一遍。
