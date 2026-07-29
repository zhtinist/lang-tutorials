# Spring 全家桶与 SpringBoot

> 本篇覆盖 Spring 技术栈里"谁是谁、谁依赖谁"这条主线:Spring、SpringMVC、SpringBoot、SpringCloud 四者的关系,SpringBoot 解决的具体问题,Starter 机制,启动流程与自动装配原理,常用注解,以及 SpringMVC 的请求处理流程。

## 一、Spring / SpringBoot / SpringMVC / SpringCloud 关系辨析

四个名字经常被并列提起,但它们不是同一层级的四选一选项,而是一条**依赖链**:

```
        SpringCloud   (微服务治理:注册发现、配置中心、熔断、网关)
             │  基于
        SpringBoot    (脚手架:自动装配、起步依赖、内嵌容器)
             │  简化搭建
        SpringMVC     (Web 层框架:DispatcherServlet + MVC)
             │  依赖核心能力
        Spring        (地基:IOC 容器 + AOP + 事务抽象)
```

**Spring** 是最底层的地基,提供的不是某个具体功能,而是一套贯穿全家桶的编程模型:IOC 容器负责对象的创建、装配、生命周期管理;AOP 把日志、事务、权限这类横切逻辑从业务代码里抽离;在此之上还有一套统一的事务管理抽象(`PlatformTransactionManager`),屏蔽不同数据访问技术(JDBC、JPA、Hibernate)的事务差异。SpringMVC、SpringBoot、SpringCloud 都是站在这套 IOC/AOP 骨架上盖的楼,不是脱离 Spring 另起炉灶的东西。

**SpringMVC** 是 Spring 家族里专门负责 Web 层的模块,把 MVC(Model-View-Controller)模式落到 Java Web 开发上:用一个统一的前端控制器 `DispatcherServlet` 接管所有请求,再按约定把请求分发给具体的处理器方法,分离业务逻辑、数据模型与页面展示。它解决的是"传统 Servlet 开发里,每来一个 URL 就要手写一个 Servlet 类,请求分发、参数解析、视图渲染全靠手动代码"的问题——把这套模板化流程收拢成框架职责,业务代码只需要写"处理器方法"这一层。

**SpringBoot** 解决的不是某个功能领域的问题,而是"用 Spring 搭一个可运行项目太麻烦"这个工程问题:一堆 XML 配置、手动管理几十个依赖的版本号、还要自己装 Tomcat 才能跑起来。SpringBoot 用**自动装配**替代手写配置、用**起步依赖(Starter)**替代手动选版本、用**内嵌容器**替代外部部署,让开发者的注意力从"怎么把 Spring 跑起来"转回"业务逻辑怎么写"。它内部仍然是一个 Spring 应用,IOC 容器、AOP、事务这些核心机制完全没变,SpringBoot 只是在容器启动前多做了一层"猜你需要什么配置,自动帮你配好"的工作。

**SpringCloud** 站在 SpringBoot 之上,解决的是"单体应用拆成多个服务之后怎么协同"的问题:服务多了要有地方登记"谁在哪、还活着吗"(注册发现),配置分散在几十个服务里要能统一改(配置中心),某个服务挂了不能拖垮整条调用链(熔断降级),外部请求进来要有统一入口做路由和鉴权(网关)。这些能力在单体应用里根本不存在,是微服务架构特有的治理问题,SpringCloud 把 Eureka/Nacos、Config、Hystrix/Sentinel、Gateway 这些组件以 Starter 的形式整合起来,而每一个具体的微服务节点,本质上都还是一个普通的 SpringBoot 应用。

一句话理清四者定位:**Spring 提供底层编程模型,SpringMVC 是这套模型在 Web 层的应用,SpringBoot 简化"如何快速搭出一个能跑的 Spring/SpringMVC 应用",SpringCloud 解决"多个 SpringBoot 应用之间如何协同治理"**。上层永远依赖下层,不存在反向依赖。

## 二、SpringBoot 解决了什么问题

在 SpringBoot 出现之前,一个典型的 Spring Web 项目要经历这些手工劳动:在 `web.xml` 里配置 `DispatcherServlet`;写一份几十上百行的 XML 声明数据源、事务管理器、各个 Bean 的装配关系;在 `pom.xml` 里手动排查 Spring 各模块、日志框架、Web 容器相关依赖的版本兼容性,一旦选错版本组合就出现类冲突或方法找不到的运行时错误;打包完还要单独部署一个 Tomcat,把 war 包扔进去才能启动。这些工作本身和业务逻辑毫无关系,却占据了项目启动阶段的大部分精力,而且几乎每个新项目都要重复一遍。

SpringBoot 用三根支柱把这套重复劳动消解掉:

**自动配置(Auto Configuration)**:本质是"基于条件的按需配置"——通过注解驱动 + SPI(Service Provider Interface)机制,在启动时检查类路径上有哪些依赖、容器里已经有哪些 Bean、配置文件里写了什么,据此决定要不要把某一批预先写好的 Bean 注册进容器。比如类路径上一旦发现 `spring-webmvc` 和内嵌 Tomcat 的依赖,SpringBoot 就知道这是一个要跑 Web 服务的项目,自动把 `DispatcherServlet`、`Tomcat` 相关的 Bean 配好,不需要开发者写一行 XML。这套机制遵循"自定义优先"原则:开发者手动声明的 Bean 或显式排除的配置类,永远优先于自动配置的默认结果。

**起步依赖(Starter)**:把某个功能场景所需的一整组依赖打包成一个坐标,并统一管理版本号,详见下一节。

**内嵌容器**:把 Tomcat/Jetty/Undertow 作为普通依赖打进应用,应用本身就是一个可执行 jar,`java -jar` 直接起服务,不需要额外安装和配置外部容器。

这三根支柱共同服务于一个目标:让开发者从"如何把 Spring 环境搭起来"这件事上解放出来,时间花在业务代码上。

SpringBoot 生态还配有一整套辅助工具:`spring-boot-actuator` 提供健康检查、指标暴露等生产监控能力;`spring-boot-devtools` 监听类路径变化实现修改代码后自动重启,免去开发阶段手动重启的等待;`spring-boot-test` 把测试所需的依赖和切片测试注解(如 `@SpringBootTest`、`@WebMvcTest`)整合好,覆盖从单元测试到集成测试的全生命周期。

## 三、Starter:依赖打包与版本治理机制

Starter 要解决的具体问题是:一个功能场景(比如"做 Web 开发")往往需要一组互相配合的依赖(SpringMVC、内嵌 Tomcat、Jackson 序列化器……),这些依赖之间还必须是相互兼容的版本组合。如果每个项目都自己去 Maven 仓库挑一遍这些依赖再逐个试版本,不但重复劳动量大,还极易挑出互相不兼容的组合,导致类冲突或者方法签名对不上的运行时错误。

Starter 把"某个功能场景需要哪些依赖、用什么版本"这件事沉淀成一个坐标,项目里引入这一个坐标,相当于引入了整组已验证兼容的依赖:

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</dependency>
```

引入 `spring-boot-starter-web` 就等于同时拿到了 SpringMVC、内嵌 Tomcat、Jackson 等一整套 Web 开发依赖,且不需要在 `<dependency>` 里写版本号——版本号由父工程 `spring-boot-dependencies`(通常通过继承 `spring-boot-starter-parent` 间接引入)统一管理,保证同一个 SpringBoot 版本下所有 Starter 的依赖版本都是互相验证过的组合,这是 Starter 能"解决版本冲突"的根本原因:不是 Starter 本身有什么魔法,而是把版本选择这件事从"开发者逐个试"收拢成"官方统一验证一次,所有人复用"。

一个 Starter 内部通常由三部分组成:**自动配置类**(`XxxAutoConfiguration`,决定往容器里注册哪些 Bean、在什么条件下注册)、**依赖 jar 包**(功能场景实际需要的第三方库)、**配置属性类**(`XxxProperties`,用 `@ConfigurationProperties` 绑定配置文件里的自定义参数,让默认配置可以被用户覆盖)。

常见 Starter 一览:

| Starter | 用途 |
|---|---|
| `spring-boot-starter-web` | Web 开发:SpringMVC + 内嵌 Tomcat + Jackson |
| `spring-boot-starter-security` | 认证与授权基础配置 |
| `mybatis-spring-boot-starter` | 自动配置 MyBatis 的 `SqlSessionFactory`、`MapperScannerConfigurer` |
| `spring-boot-starter-data-jpa` | JPA(Hibernate 实现)+ 数据库连接池 |
| `spring-boot-starter-jdbc` | 基础 JDBC 支持 + 连接池,不含 ORM |
| `spring-boot-starter-data-redis` | Redis 客户端(默认 Lettoce)+ Spring Data Redis |
| `spring-boot-starter-test` | JUnit、Mockito、Hamcrest 等测试依赖集合 |

当官方 Starter 无法覆盖业务特定场景时,可以自定义 Starter:新建一个 Maven 模块,编写 `XxxAutoConfiguration`(标注 `@Configuration`,并用 `@ConditionalOnClass` 之类的条件注解控制生效时机)、编写 `XxxProperties` 绑定自定义配置项,再把自动配置类的全限定名注册到约定的元数据文件里(见下一节的两种注册方式),即可让其他项目引入这个坐标后自动获得对应能力。

## 四、SpringBoot 启动流程与自动装配原理

启动一个 SpringBoot 应用只是调用一行 `SpringApplication.run(Application.class, args)`,但这一行背后分两个阶段:**构造 `SpringApplication` 实例**和**执行 `run()`**。

### 4.1 构造阶段

```java
public static void main(String[] args) {
    SpringApplication.run(Application.class, args);
}
```

`SpringApplication` 的构造函数在真正启动之前先确定三件事:

- **推断应用类型**:通过检查类路径上是否存在 `DispatcherServlet`、Reactive 相关类等特征类,决定这是一个非 Web 应用(`NONE`)、基于 Servlet 的 Web 应用(`SERVLET`,会启动内嵌 Tomcat)还是响应式应用(`REACTIVE`)。
- **加载初始化器与监听器**:通过 SPI 机制读取所有 `ApplicationContextInitializer` 和 `ApplicationListener` 的实现类名,实例化后按顺序保存,供后续各个启动阶段回调。
- **推断主类**:通过分析调用栈找到包含 `main` 方法的类,作为组件扫描的起点包。

### 4.2 run() 阶段

`run()` 方法依次做:启动计时器并设置 `java.awt.headless=true`;初始化并启动全生命周期监听器(`SpringApplicationRunListener`),发布"启动准备中"事件;把命令行参数封装进 `Environment`;创建并准备环境对象(依次加载系统属性、环境变量、配置文件,遵循外部化配置的优先级规则);打印 Banner;根据应用类型创建对应的 `ApplicationContext`(Web 应用对应 `AnnotationConfigServletWebServerApplicationContext`);把环境对象绑定进上下文、执行所有 `ApplicationContextInitializer`;然后进入整个流程里最关键的一步——**刷新上下文**(`refreshContext`)。

刷新上下文这一步,就是 Spring 容器完成自动装配的地方:扫描主类所在包及子包下的组件、加载并筛选自动配置类、注册和初始化所有 Bean;如果是 Web 应用,还会在这一步创建并启动内嵌 Tomcat。刷新完成后触发 `afterRefresh()` 供用户扩展,随后停止计时、打印启动耗时、发布"启动完成"事件,调用用户自定义的 `ApplicationRunner`/`CommandLineRunner`,最后发布"就绪"事件——内嵌容器此时才真正开始监听端口对外提供服务。

### 4.3 自动装配的核心:@EnableAutoConfiguration

`@SpringBootApplication` 是一个组合注解,内部由三个注解构成:

```java
@SpringBootConfiguration   // 本质是 @Configuration,标记这是一个配置类
@EnableAutoConfiguration   // 开启自动装配
@ComponentScan             // 扫描当前包及子包下的组件
public @interface SpringBootApplication { ... }
```

真正驱动自动装配的是 `@EnableAutoConfiguration`。它内部有一个 `@Import(AutoConfigurationImportSelector.class)`,`AutoConfigurationImportSelector` 实现了 `ImportSelector` 接口——这个接口的语义是"返回一批类名,交给 Spring 当作额外的配置类导入"。启动时,`AutoConfigurationImportSelector` 会去类路径上按约定路径查找"候选自动配置类清单",这个查找机制经历过一次实现方式的演进:

- **旧机制(SpringBoot 2.7 之前)**:清单写在每个 jar 包的 `META-INF/spring.factories` 文件里,格式是 `key=value` 的 properties 文件,`EnableAutoConfiguration` 作为 key,value 是一长串用逗号分隔的自动配置类全限定名。
- **新机制(SpringBoot 2.7+ 引入,3.x 起为主流)**:清单改为独立文件 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`,每行一个类名。这个改动把"自动配置类清单"从 `spring.factories` 这个承载多种用途(监听器、初始化器等注册信息也塞在同一个文件里)的大杂烩文件中拆分出来,职责更单一,加载时也不需要再解析整份 properties 再按 key 过滤。

无论走哪种机制,找到候选类名清单之后,流程是一致的:对清单里的每一个自动配置类,逐个应用条件注解做筛选——最常见的是 `@ConditionalOnClass`(类路径上存在指定类才生效,例如 `DataSourceAutoConfiguration` 只在存在 `DataSource` 相关类时才生效)、`@ConditionalOnMissingBean`(容器里还没有同类型 Bean 时才生效,这正是"用户自定义优先于自动配置"的实现手段——只要用户自己声明了同名或同类型 Bean,自动配置类里对应的 `@ConditionalOnMissingBean` 就会判定失败,自动配置让位)、`@ConditionalOnProperty`(配置文件里某个属性等于指定值才生效)。只有条件全部满足的自动配置类才会真正被注册进容器参与 Bean 定义的加载。

条件注解的判定顺序是从类级别到方法级别逐层进行,同一层级内部按代码书写顺序执行,只要某一层的条件不满足,这个类或方法整体失效,不再继续判断内部更细粒度的条件。

想要关闭某个自动配置,可以在 `@SpringBootApplication` 上排除:

```java
@SpringBootApplication(exclude = {DataSourceAutoConfiguration.class})
```

或者在配置文件里声明:

```properties
spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration
```

两种方式效果等价,前者是编译期强类型引用,后者是运行期按全限定名字符串匹配,便于不同环境用不同配置文件切换排除项而不用改代码。

## 五、SpringBoot 常用注解

SpringBoot 的注解可以分为几类,大体是在 Spring 原生注解之上做了"场景化封装"——原生能力不变,但把常见组合和默认值预设好,减少重复声明。

**启动与扫描**

| 注解 | 作用 |
|---|---|
| `@SpringBootApplication` | 启动类核心注解,组合了配置声明 + 自动装配 + 组件扫描 |
| `@ComponentScan` | 指定组件扫描范围,`@SpringBootApplication` 默认扫描当前包及子包 |
| `@MapperScan("com.example.mapper")` | 扫描 MyBatis 映射接口所在包,替代逐个接口标 `@Mapper` |

**配置读取**

| 注解 | 作用 |
|---|---|
| `@ConfigurationProperties(prefix = "app.datasource")` | 按前缀批量绑定配置文件属性到 Bean 字段 |
| `@Value("${server.port:8080}")` | 读取单个配置值,支持 `:` 后跟默认值 |

**Web 层**

| 注解 | 作用 |
|---|---|
| `@GetMapping` / `@PostMapping` / `@PutMapping` / `@DeleteMapping` | `@RequestMapping` 按 HTTP 方法收窄的简化写法 |
| `@RestControllerAdvice` | `@ControllerAdvice` + `@ResponseBody` 的组合,配合 `@ExceptionHandler` 实现返回 JSON 格式的全局异常处理 |
| `@ExceptionHandler(NullPointerException.class)` | 在 `@RestControllerAdvice` 类中声明,指定处理的异常类型 |
| `@PathVariable` / `@RequestParam` | 分别提取 URL 路径变量与查询参数 |

**条件装配**

| 注解 | 生效条件 |
|---|---|
| `@ConditionalOnClass` / `@ConditionalOnMissingClass` | 类路径存在/不存在指定类 |
| `@ConditionalOnBean` / `@ConditionalOnMissingBean` | 容器中存在/不存在指定 Bean,后者常用于让自定义 Bean 覆盖默认配置 |
| `@ConditionalOnProperty` | 配置文件中某属性等于指定值 |

**功能开关**

`@EnableTransactionManagement` 开启声明式事务(引入 `spring-boot-starter-jdbc`/`orm` 后 SpringBoot 会自动开启,通常不需要手动加);`@Async` 标记方法异步执行,需配合 `@EnableAsync`;`@EnableCaching` 开启缓存注解(`@Cacheable`/`@CachePut`/`@CacheEvict`)。

几个容易在面试和实践中踩坑的细节:`@Async` 标注的方法本质是靠 Spring AOP 生成代理来拦截调用、切换到异步线程执行的,而 AOP 代理**无法代理 `private` 或 `static` 方法**(代理对象是目标类的子类或接口实现,子类覆写不了 `private` 方法,`static` 方法也不参与实例级别的方法分派),所以 `@Async` 方法必须是 `public` 的实例方法。`@Transactional` 同理依赖 AOP 代理,失效的常见场景有三种:方法被 `private`/`static`/`final` 修饰导致无法被代理;同一个类内部方法互相调用(`this.otherMethod()` 不经过代理对象,直接是普通方法调用,绕过了事务拦截逻辑);异常被 `catch` 住没有继续抛出,或者抛出的是受检异常而非默认回滚的运行时异常。

## 六、SpringMVC 执行流程

SpringMVC 的设计核心是**前端控制器模式**:所有请求先统一进入一个控制器(`DispatcherServlet`),由它协调各个组件完成分发,业务代码只需要关注"处理器方法"这一层,不需要关心请求怎么路由过来、视图怎么渲染出去。完整流程:

```
客户端请求
   │
   ▼
DispatcherServlet(前端控制器,统一入口)
   │  调用
   ▼
HandlerMapping ── 根据 URL/方法/参数找到匹配的处理器
   │  返回
   ▼
HandlerExecutionChain(处理器 + 拦截器链)
   │  DispatcherServlet 用 supports() 找到匹配的适配器
   ▼
HandlerAdapter ── 统一不同类型处理器(注解式/接口式/Servlet式)的调用方式
   │
   ├─ 拦截器 preHandle()
   ├─ 调用具体 Handler(Controller 方法)
   ├─ 拦截器 postHandle()
   ▼
ModelAndView(或直接是数据,若为 @ResponseBody/@RestController)
   │
   ▼
ViewResolver ── 按视图名解析出具体 View 实例
   │
   ▼
View.render(model) ── 结合模型数据渲染
   │
   ├─ 拦截器 afterCompletion()
   ▼
响应返回客户端
```

逐步展开:

1. 请求先经 Tomcat 等 Web 容器接收,转发给 `DispatcherServlet`。
2. `DispatcherServlet` 拿到请求的 URL、方法、参数信息后,调用 **`HandlerMapping`** 查找匹配的处理器。
3. `HandlerMapping` 依据注解(`@RequestMapping` 系列)或历史上的 XML 配置,定位到具体处理器,并把处理器与其对应的拦截器打包成 **`HandlerExecutionChain`** 返回。
4. `DispatcherServlet` 再调用 **`HandlerAdapter`**,通过 `supports()` 判断哪个适配器能处理当前这种类型的处理器——这一步存在的意义是,SpringMVC 支持注解式、实现特定接口式、Servlet 式等多种处理器写法,调用方式各不相同,`HandlerAdapter` 把这些差异封装掉,`DispatcherServlet` 只需要面对统一的适配器接口,新增一种处理器类型时只需新增一个适配器实现,不用改动 `DispatcherServlet` 本身,这是开闭原则的直接应用。
5. 适配器先执行拦截器链的 `preHandle()`,再真正调用处理器的业务方法。
6. 处理器执行完毕返回 `ModelAndView`;如果是 REST 接口(`@RestController` 或方法标了 `@ResponseBody`),则直接返回待序列化的数据对象,不走视图解析这条路径。
7. 适配器执行拦截器链的 `postHandle()`,把结果交回 `DispatcherServlet`。
8. `DispatcherServlet` 把 `ModelAndView` 交给 **`ViewResolver`**,按视图名解析出具体的 `View` 实例。
9. `View` 结合模型数据渲染出最终响应内容。
10. 拦截器链的 `afterCompletion()` 执行完毕,响应返回客户端。

`DispatcherServlet` 本身是一个标准 Servlet,容器启动时执行其 `init()` 方法,在这一步加载 SpringMVC 配置并把 `HandlerMapping`、`HandlerAdapter`、`ViewResolver` 等核心组件初始化并缓存好,后续每次请求直接复用这些已初始化的组件,不重复创建。

`@RestController` 等价于 `@Controller` + `@ResponseBody` 的组合,类中所有方法的返回值都会经由消息转换器(`HttpMessageConverter`)序列化后直接写入响应体,不再经过视图解析这一整套流程;如果一个类标注了普通 `@Controller` 却想让某个方法返回 JSON,只需要在该方法上单独加 `@ResponseBody`。

[返回索引](index.md)
