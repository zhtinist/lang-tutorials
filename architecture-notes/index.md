# 软件架构与设计 · Software Architecture & Design

> 从五种经典架构模式出发，贯通 REST、整洁架构与 DDD，学会**选型**而非背名词。

---

## 目录

### 第一章 · 架构基础

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| 软件架构概览 | [architecture-overview.md](architecture-overview.md) | 什么是架构、架构 vs 设计、质量属性、演进简述 |
| 分层架构 | [layered-architecture.md](layered-architecture.md) | 四层结构、请求流、优缺点、何时使用 |
| 事件驱动架构 | [event-driven.md](event-driven.md) | 队列/分发器/通道/处理器、Mediator vs Broker |
| 微核架构 | [microkernel.md](microkernel.md) | 内核 + 插件、IDE/浏览器例子、可扩展性 |
| 微服务架构 | [microservices.md](microservices.md) | 单体→SOA→容器、三种实现模式、拆分陷阱 |
| 基于空间的架构 | [space-based.md](space-based.md) | 处理单元、虚拟中间件、消除中央库瓶颈 |

### 第二章 · 接口与内部结构

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| RESTful 架构与 API | [restful.md](restful.md) | 资源/表现层/状态转化、路径与动词、状态码、HATEOAS |
| 整洁架构 | [clean-architecture.md](clean-architecture.md) | 依赖规则、同心圆四层、接口倒置 |
| 领域驱动设计入门 | [ddd-basics.md](ddd-basics.md) | 统一语言、限界上下文、实体/值对象/聚合/仓储 |

### 第三章 · 选型

| 专题 | 文件 | 核心内容 |
|------|------|----------|
| 架构选型 | [how-to-choose.md](how-to-choose.md) | 五模式对比表、决策口诀、反模式 |

---

## 使用建议

1. **速成路线**: 概览 → 分层 → 微服务 → REST → 选型。适合先建立「常见系统长什么样」的直觉。
2. **系统学习**: 按第一章五种模式读完，再读 REST / Clean Architecture / DDD，最后用选型篇做对照表复习。
3. **对照实践**: 读每种模式时，想想自己项目是「哪一层在变、哪一层在痛」——扩展、部署、测试还是协作。
4. **代码风格**: 小示例用 Python 3；架构图用 ASCII；对比用表格。不追求完整可运行项目。
5. **与算法笔记关系**: 本系列讲「系统怎么切、依赖怎么指」；算法笔记讲「局部怎么算」。二者互补。

---

## 推荐阅读顺序（示意）

```
architecture-overview
        │
        ├─→ layered-architecture ──┐
        ├─→ event-driven           │
        ├─→ microkernel            ├──→ how-to-choose
        ├─→ microservices          │
        └─→ space-based ───────────┘
                    │
        restful · clean-architecture · ddd-basics
```
