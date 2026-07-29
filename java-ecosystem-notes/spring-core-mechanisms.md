# Spring 核心机制

> 本篇覆盖 Spring 框架内部真正支撑起"降耦合、少样板代码"这套编程模型的核心机制:IOC 容器如何反转对象创建的控制权、AOP 如何把横切逻辑从业务代码里剥离、Spring 常见注解怎么落地这两套思想、Bean 的完整生命周期、Bean 的作用域体系、单例 Bean 循环依赖的三级缓存解法,以及 Spring 内部大量借用的经典设计模式。

## 一、IOC:控制反转解决了什么问题

### 不用 IOC 会怎样写代码

设想一个 `OrderService` 依赖 `PaymentGateway` 和 `InventoryChecker` 两个协作对象。没有 IOC 容器时,依赖关系只能在代码里手工搭建:

```java
public class OrderService {
    private PaymentGateway paymentGateway;
    private InventoryChecker inventoryChecker;

    public OrderService() {
        // 依赖对象的创建、配置、组装全部写死在这里
        this.paymentGateway = new AlipayGateway(new HttpClient("https://api.alipay.com"));
        this.inventoryChecker = new MysqlInventoryChecker(new JdbcConnectionPool("jdbc:mysql://..."));
    }
}
```

这段代码把三件本该分开的事情耦合在一起:**谁需要这个依赖**(`OrderService`)、**依赖具体是什么实现**(`AlipayGateway`)、**依赖怎么构造**(`new HttpClient(...)`)。带来的直接后果:

- 换一个支付渠道(比如从支付宝换成微信支付),必须修改 `OrderService` 的源码而不是配置,违反开闭原则。
- 单元测试 `OrderService` 时无法用 mock 对象替换真实的 `AlipayGateway`,因为构造逻辑是硬编码的,测试会真的发起网络请求。
- 如果 `PaymentGateway` 本身还依赖别的对象,构造链条会一路手工往下拼,项目越大这类"胶水代码"越多,且分散在各个类的构造器里,没有统一的地方管理。

### 用 IOC 之后怎么写

```java
@Service
public class OrderService {
    private final PaymentGateway paymentGateway;
    private final InventoryChecker inventoryChecker;

    // 只声明"需要什么类型的依赖",不关心具体实现类和构造细节
    public OrderService(PaymentGateway paymentGateway, InventoryChecker inventoryChecker) {
        this.paymentGateway = paymentGateway;
        this.inventoryChecker = inventoryChecker;
    }
}

@Component
public class AlipayGateway implements PaymentGateway { /* ... */ }
```

`OrderService` 只表达"我依赖一个 `PaymentGateway` 类型的对象",至于这个类型背后具体是哪个实现类、怎么构造、什么时候构造,全部交给容器决定。换实现只需要换一个实现类上的 `@Component` 标注(或者干脆用 `@Primary`/`@Qualifier` 在多个实现间切换),`OrderService` 的代码一行不用改;单元测试时可以直接把 mock 对象通过构造器传进去,完全不依赖真实的支付网关。

### IOC 反转的到底是什么

IOC(Inversion of Control,控制反转)是一种设计思想,不是某个具体 API。它反转的是**对象生命周期的控制权**:传统方式里,程序员在代码中主动 `new` 对象、主动管理依赖关系、主动决定创建时机;IOC 模式下,这一整套控制权从程序员手中转移给了容器——由 **Spring IOC 容器**统一负责 Bean 的创建、初始化、依赖装配和销毁。程序员从"主动创建者"变成"声明需求的消费者",这个"控制权转移"正是"反转"二字的含义。

**依赖注入(Dependency Injection,DI)**是 IOC 思想的具体实现方式:容器在创建一个 Bean 时,把它所依赖的其他 Bean"注入"进来,而不是让这个 Bean 自己去找、去创建依赖。IOC 是理念,DI 是这套理念落地的技术手段,日常语境里两个词经常混用。

### 容器的实现:BeanFactory 与 ApplicationContext

Spring 提供两层容器接口:

- **BeanFactory**:最原始的 IOC 容器接口,只提供最基础的 Bean 管理和依赖注入能力,采用**懒加载**——Bean 在第一次被 `getBean()` 请求时才实例化,启动快、占用内存少。
- **ApplicationContext**:`BeanFactory` 的超集,在此基础上扩展了国际化支持、事件发布订阅、资源加载等企业级特性,采用**预加载**——容器启动时就把所有单例 Bean 一次性实例化完毕,把"第一次调用时才发现依赖缺失"这类问题提前暴露在启动阶段而不是运行期。实际项目中几乎总是使用 `ApplicationContext` 及其实现类(如 `ClassPathXmlApplicationContext`、`AnnotationConfigApplicationContext`)。

### Bean 的注册方式

早期 Spring 用 **XML 配置**在 `<bean>` 标签里显式声明每一个 Bean 及其属性,配置与代码完全分离,但项目稍大配置文件就迅速膨胀。现在的主流方式是**注解注册**:`@Component`(以及它的语义化变体 `@Service`、`@Repository`、`@Controller`)标注在类上,配合组件扫描(`@ComponentScan`)让容器自动发现并注册;对于无法直接标注(比如第三方库里的类)的场景,用 `@Configuration` 类里的 `@Bean` 方法手动定义 Bean,返回值交给容器管理。两种方式可以混用,`@Bean` 属于显式声明,优先级高于扫描发现的 `@Component`。

### 依赖注入的三种方式

- **字段注入**:`@Autowired` 直接标在字段上,代码最短,但字段无法声明为 `final`,且脱离容器时(比如 new 出来做测试)该字段永远是 `null`,隐蔽性最强,通常不推荐在生产代码中作为首选方式。
- **构造器注入**:依赖作为构造器参数传入,可以把字段声明为 `final`,保证对象一旦构造完成依赖就不可变、不为空;Spring 4.3 之后,如果类只有一个构造器,`@Autowired` 注解本身可以省略,容器会自动使用这个唯一构造器完成注入,这也是当前官方推荐的默认注入方式。
- **Setter 注入**:依赖通过 setter 方法注入,适合可选依赖或者需要运行期重新装配的场景。

### IOC 容器启动流程

```
创建容器(ApplicationContext / BeanFactory)
        │
        ▼
ResourceLoader 加载配置文件 → ResourceResolver 解析为 Resource 对象
        │
        ▼
BeanDefinitionReader 解析 Resource → 生成 BeanDefinition(Bean 的元信息:类、作用域、依赖关系等)
        │
        ▼
BeanRegistry 将 BeanDefinition 注册进容器 → 容器初始化完成
        │
        ▼
(ApplicationContext 场景)预加载所有单例 Bean:反射实例化 → 依赖注入 → 初始化回调
```

容器初始化完成之后,才进入下一节要讲的"Bean 管理"环节——按 [Bean 生命周期](#四bean-的生命周期) 描述的顺序把 `BeanDefinition` 变成真正可用的 Bean 实例。

**常见追问**:

- **BeanFactory 和 ApplicationContext 的区别**:`ApplicationContext` 是 `BeanFactory` 的增强版,提供资源加载、国际化、事件发布等额外能力,`BeanFactory` 懒加载、`ApplicationContext` 默认预加载单例 Bean。
- **单例 Bean 想延迟实例化怎么办**:在类或 `@Bean` 方法上加 `@Lazy`,该 Bean 会推迟到第一次被使用时才实例化。`@Lazy` 只对单例 Bean 有意义,原型(prototype)Bean 本身每次获取都新建实例,天然就是懒加载的。

## 二、AOP:面向切面编程解决了什么问题

### 不用 AOP 会怎样写代码

假设系统里若干个 Service 方法都需要记录执行日志、做权限校验、包一层事务:

```java
public class OrderService {
    public void createOrder(Order order) {
        log.info("createOrder start, order={}", order);      // 日志:横切逻辑
        checkPermission();                                     // 权限:横切逻辑
        Transaction tx = transactionManager.begin();           // 事务:横切逻辑
        try {
            // 真正的业务逻辑只有这一行
            doCreateOrder(order);
            tx.commit();
        } catch (Exception e) {
            tx.rollback();
            throw e;
        }
        log.info("createOrder end");                           // 日志:横切逻辑
    }
}
```

日志、权限、事务这类逻辑与"创建订单"这个核心业务毫无关系,却要在每一个需要这些能力的方法里重复书写一遍。这类代码有个共同特征:**它们不属于任何一个业务模块,却横向散布在几乎所有业务模块中**——面向对象的封装、继承、多态能建立清晰的"纵向"类层次,但完全没有办法表达这种"横向"重复,这正是"横切关注点(cross-cutting concern)"这个名字的来源。后果是:业务代码被大量非业务代码稀释,可读性下降;想统一修改日志格式或事务策略,需要改遍所有调用点,极易遗漏。

### 用 AOP 之后怎么写

```java
public class OrderService {
    public void createOrder(Order order) {
        doCreateOrder(order);   // 只剩业务逻辑本身
    }
}

@Aspect
@Component
public class LoggingAspect {
    @Around("execution(* com.example.service.*.*(..))")
    public Object logAround(ProceedingJoinPoint pjp) throws Throwable {
        log.info("{} start", pjp.getSignature());
        Object result = pjp.proceed();
        log.info("{} end", pjp.getSignature());
        return result;
    }
}
```

日志逻辑被抽到一个独立的**切面(Aspect)**类里,通过**切入点表达式**(`execution(* com.example.service.*.*(..))`)描述"作用于哪些方法",容器在运行期把这段逻辑动态"织入"到匹配的方法调用前后。`OrderService` 的代码里不再出现任何一行日志代码,想修改日志格式只需要改 `LoggingAspect` 这一处。这就是 AOP 的核心价值:**把核心关注点(业务逻辑)和横切关注点(日志、事务、权限等)彻底分离**,分别独立开发、独立维护,再由容器负责在运行期"缝合"起来。

### AOP 术语

| 术语 | 含义 |
|---|---|
| 横切关注点 | 对哪些方法进行拦截、拦截后要执行什么处理 |
| 切面(Aspect) | 对横切关注点的抽象和封装,相当于面向对象里"类"对物体特征的抽象 |
| 连接点(JoinPoint) | 程序执行中可能被拦截的点;Spring AOP 只支持方法级别的连接点(理论上还可以是字段、构造器,但 Spring 未实现) |
| 切入点(Pointcut) | 对连接点进行筛选的规则,描述"具体拦截哪些连接点" |
| 通知(Advice) | 拦截到连接点之后真正要执行的代码,见下表 |
| 目标对象 | 被代理、被增强的原始对象 |
| 代理对象 | 执行切面逻辑,再调用目标对象原始方法的对象 |
| 织入(Weave) | 把切面应用到目标对象、生成代理对象的过程 |
| 引入(Introduction) | 不修改原有代码,在运行期为类动态添加新方法或字段 |

### 五种通知类型

| 通知类型 | 执行时机 |
|---|---|
| 前置通知(`@Before`) | 目标方法执行**之前**执行 |
| 后置通知(`@After`) | 目标方法执行**之后**执行(无论是否抛异常都会执行) |
| 返回通知(`@AfterReturning`) | 目标方法**正常返回结果后**执行 |
| 异常通知(`@AfterThrowing`) | 目标方法**抛出异常**时执行 |
| 环绕通知(`@Around`) | 包裹目标方法执行前后,能决定目标方法是否执行、修改返回值,功能最强 |

前四种通知只能在目标方法执行的前后插入逻辑,环绕通知通过 `ProceedingJoinPoint.proceed()` 显式控制目标方法本身的执行时机甚至是否执行,因此可以实现"目标方法抛异常就不重试""缓存命中就不调用真实方法"这类前四种通知做不到的效果。

### 实现原理:动态代理

Spring AOP 在运行期通过**动态代理**生成代理对象,而不是在编译期修改字节码(这是它与 AspectJ 等编译期/类加载期织入方案的关键区别)。具体有两种代理方式:

- **JDK 动态代理**:只能代理实现了接口的类,核心是 `InvocationHandler` 和 `Proxy`。`Proxy` 在运行期动态生成一个实现目标接口的代理类,方法调用统一转发到 `InvocationHandler.invoke()`,由它反射调用目标对象的真实方法,并在调用前后插入横切逻辑。
- **CGLIB 动态代理**:当目标类没有实现任何接口时使用。CGLIB 是一个字节码生成库,在运行期动态生成目标类的一个**子类**,覆盖父类方法并织入增强逻辑——正因为原理是继承,被 `final` 修饰的类和方法都无法被 CGLIB 代理。

Spring 的选择规则:**默认优先使用 JDK 动态代理**(只要目标类实现了接口);目标类没有实现接口时**自动切换为 CGLIB**;也可以通过配置强制全局使用 CGLIB(`spring.aop.proxy-target-class=true`)。

对比静态代理:静态代理由开发者手写或工具在编译期生成,被代理的类在编译时就已固定;动态代理则是运行期通过反射动态生成,同一套代理逻辑可以套用在任意符合条件的类上,不需要为每个目标类手写一个代理类。

### AOP 与 IOC 的关系

Spring AOP 生成的代理对象本身也是由 **IOC 容器**创建和管理的,它的依赖关系同样通过依赖注入来装配。这意味着容器里某个 Bean 一旦被 AOP 切面命中,其他 Bean 注入到的实际上是**代理对象**而非原始对象——这也是循环依赖一节里"提前暴露的引用形态必须与代理形态一致"这个问题的根源(见第六节)。

### 常用 AOP 注解

`@Aspect`(声明切面类)、`@Pointcut`(定义可复用的切入点表达式)、`@Before`、`@After`、`@Around`、`@AfterReturning`、`@AfterThrowing`(五类通知),以及通用的 `@Advice`。

## 三、Spring 常见注解

Spring 注解按用途大致分为五类:**Bean 注册、依赖注入、AOP/事务、配置、Web**。

### Bean 注册类

- `@Component`:通用组件注解,配合类路径扫描自动实例化,依赖无参构造器(或唯一构造器,见前文)。
- `@Service` / `@Repository` / `@Controller`:功能上都是 `@Component` 的语义化特化,分别标记服务层、持久层、控制层,便于代码分层一目了然。其中 `@Repository` 有一个真实的额外行为:Spring 会为标注了它的 Bean 注册异常转译处理器,把各种数据访问框架抛出的原生异常(如 JDBC 的 `SQLException`)统一转换为 Spring 定义的 `DataAccessException` 体系,屏蔽底层持久化技术差异。
- `@Bean`:标注在 `@Configuration` 类的方法上,通过方法返回值手动定义 Bean,适合无法直接在类上加注解的第三方类。

**`@Component` 与 `@Bean` 的本质区别**:`@Component` 靠类路径扫描自动实例化;`@Bean` 靠开发者手写的方法体自定义实例化逻辑。如果同一类型的 Bean 被两种方式同时注册且产生名称冲突,`@Bean` 的显式声明会覆盖 `@Component` 扫描得到的结果,因为前者优先级更高。

### 依赖注入类

- `@Autowired`:Spring 原生注解,默认**按类型**匹配注入,可用于字段、构造器、Setter。找不到匹配类型的 Bean 时默认抛出异常,设置 `required = false` 可以允许为 `null`,但调用方需要自行判空。
- `@Qualifier`:与 `@Autowired` 搭配使用,按名称在多个同类型 Bean 中指定注入哪一个。
- `@Resource`:JDK(JSR-250)标准注解,默认**按名称**匹配,找不到再退化为按类型匹配,和 `@Autowired` 的匹配优先级正好相反。
- `@Primary`:未显式使用 `@Qualifier` 时,多个同类型候选 Bean 里优先注入被标记为 `@Primary` 的那个。
- `@Value`:从属性文件或配置源读取值,注入到字段。

### 配置类

`@Configuration` 定义配置类,替代传统 XML 配置文件,类中 `@Bean` 方法返回的实例交由容器管理。

### Web 类

- `@Controller`:标记控制器,处理 HTTP 请求,方法默认返回视图名。
- `@RestController`:等价于 `@Controller` + `@ResponseBody` 的组合,类中所有方法的返回值默认序列化为 JSON 写入响应体。
- `@RequestMapping`:将 HTTP 路径映射到处理方法,可指定 URL、请求方法、参数等匹配条件;`@GetMapping`、`@PostMapping`、`@PutMapping`、`@DeleteMapping` 是针对具体 HTTP 方法的简化写法。
- `@RequestBody`:把请求体(JSON/XML)反序列化绑定到 Java 对象参数上。
- `@ResponseBody`:把方法返回值序列化后直接写入响应体,而不是解析为视图名。
- `@PathVariable`:从 URL 路径中提取占位符参数。

**常见追问**:

- **一个类同时被 `@Service` 标注、又在 `@Configuration` 里用 `@Bean` 定义了实例,容器里有几个 Bean?** 若两者的默认名称相同(`@Service` 默认取类名首字母小写,`@Bean` 默认取方法名)且发生冲突,`@Bean` 覆盖 `@Service`,容器里只有一个;若 `@Bean` 显式指定了不同名称,则两个都会存在。

## 四、Bean 的生命周期

Bean 的生命周期由 Spring 容器全程接管,大致分为容器初始化、实例化、依赖注入、初始化、使用、销毁六个阶段,其中"初始化"阶段内部又细分为 Aware 回调、前置处理、自定义初始化、后置处理四步。完整流程:

```
┌─────────────────────────────────────────────────────────────────┐
│ 容器初始化阶段                                                     │
│   扫描 XML / 注解 → 封装为 BeanDefinition → 注册进 BeanFactory       │
└───────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 1. 实例化(Instantiation)                                          │
│    通过构造器反射创建 Bean 实例(此时是"裸对象",字段尚未赋值)          │
└───────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. 属性赋值(Populate Properties / 依赖注入)                        │
│    通过 @Autowired / @Resource / XML 配置,把依赖的其他 Bean 或值       │
│    注入到当前实例的字段中                                           │
└───────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Aware 接口回调                                                 │
│    若实现 BeanNameAware      → 回调 setBeanName()                  │
│    若实现 BeanFactoryAware   → 回调 setBeanFactory()               │
│    若实现 ApplicationContextAware → 回调 setApplicationContext()   │
└───────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. BeanPostProcessor 前置处理                                      │
│    postProcessBeforeInitialization()                              │
└───────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. 初始化(Initialization)                                          │
│    a) @PostConstruct 标注的方法                                     │
│    b) InitializingBean.afterPropertiesSet()                       │
│    c) 自定义 init-method(XML 配置 / @Bean(initMethod=...))          │
└───────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. BeanPostProcessor 后置处理                                      │
│    postProcessAfterInitialization()                                │
│    (AOP 代理正是在这一步由 AbstractAutoProxyCreator 这个             │
│     BeanPostProcessor 生成并替换原始实例的)                          │
└───────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ Bean 就绪,存入一级缓存,可通过 getBean() 或依赖注入正常使用            │
└───────────────────────────────┬─────────────────────────────────┘
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ 销毁(容器关闭时,仅 singleton 作用域由容器负责)                       │
│    a) @PreDestroy 标注的方法                                        │
│    b) DisposableBean.destroy()                                    │
│    c) 自定义 destroy-method                                        │
└─────────────────────────────────────────────────────────────────┘
```

### 三种初始化回调的执行顺序

`@PostConstruct`、`InitializingBean`、自定义 `init-method` 都能实现"初始化后做点什么",三者可以同时存在,执行顺序固定为:

1. **`@PostConstruct`** 最先执行——它由 `CommonAnnotationBeanPostProcessor` 这个 `BeanPostProcessor` 在前置处理阶段解析并回调,本质上依附于 `BeanPostProcessor` 机制。
2. **`InitializingBean.afterPropertiesSet()`** 次之——这是 Spring 框架的内置接口,容器直接识别并调用,优先级高于用户在配置里声明的自定义方法。
3. **自定义 `init-method`** 最后执行——属于 XML/注解配置层面的自定义扩展点,优先级最低。

这个顺序本质上反映了"框架内建机制 > 用户自定义配置"的设计原则:越是深度嵌入 Spring 处理链路的机制(`BeanPostProcessor`)执行得越早,越是上层、越贴近用户配置的方式执行得越晚。

**常见追问**:

- **Bean 的作用域对生命周期有什么影响?** singleton 由容器管理完整生命周期(初始化后进容器缓存,容器关闭时销毁);prototype 只由容器负责实例化、注入、初始化,后续容器不再追踪,销毁交给 JVM 垃圾回收或使用者手动处理;request/session 等 Web 作用域生命周期与对应的请求/会话保持一致。
- **怎么监听 Bean 的生命周期?** 实现 `BeanPostProcessor` 在前置/后置钩子里插入逻辑;让 Bean 自身实现 `Aware`/`InitializingBean`/`DisposableBean` 接口;或者用 `@EventListener` 监听 `ContextRefreshedEvent`(容器初始化完成)、`ContextClosedEvent`(容器关闭)等容器级事件。

## 五、Bean 的作用域

作用域决定一个 Bean 定义对应到多少个实际实例、这些实例的可见范围和生命周期边界。

| 作用域 | 说明 | 适用场景 |
|---|---|---|
| `singleton`(默认) | 容器内**唯一**共享实例,所有获取请求返回同一对象 | 无状态的 Service、DAO 等绝大多数 Bean |
| `prototype` | 每次请求都创建**全新**实例 | 有可变内部状态、不能共享的瞬时对象 |
| `request` | 每次 HTTP 请求创建一个实例,仅在该请求内有效 | 需要绑定单次请求上下文的数据 |
| `session` | 每个 HTTP 会话创建一个实例,仅在该会话内有效 | 用户会话级别的状态 |
| `application` | 整个 `ServletContext` 内唯一实例 | 应用级共享状态(Web 环境) |
| `websocket` | 每个 WebSocket 会话创建一个实例 | WebSocket 连接级别的状态 |

以上 6 种是当前 Spring 官方文档明确列出的标准作用域(其中后 4 种只在 Web 环境下的 `ApplicationContext` 中生效)。此外 Spring 还支持通过实现 `Scope` 接口自定义作用域,再用 `CustomScopeConfigurer` 注册到容器,在 Bean 上用 `@Scope("自定义名称")` 使用。

### singleton 与 prototype 的生命周期差异

`singleton` Bean 与容器同生共死:容器启动时创建(或按 `@Lazy` 延迟到首次使用),容器关闭时执行销毁回调,容器全程持有引用、全程管理。`prototype` Bean 每次请求都会得到一个新实例,但容器**只负责实例化和依赖注入这两步**,初始化回调之后容器就不再持有该实例的任何引用,后续既不会追踪它,也不会在容器关闭时调用它的销毁方法——销毁完全交给 JVM 垃圾回收,或者使用者在 `@PreDestroy` 里自行处理资源释放,容器不会主动调用。

### 常见追问

- **singleton Bean 是线程安全的吗?** 默认**不是**。单例 Bean 是全局共享的,如果内部持有可变的成员变量,多线程并发读写会导致数据错乱。应对方式:避免在 Bean 里存储可变状态,用局部变量代替成员变量、用 `ThreadLocal` 隔离每个线程的数据、必要时加锁,或者干脆采用无状态设计。
- **在 singleton Bean 里直接用 `@Autowired` 注入 prototype Bean,会有什么问题?** 会变成"伪多例"——singleton Bean 只在自己被创建时被注入一次 prototype 实例,之后每次调用用的都是同一个实例,完全违背了 prototype "每次都是新对象"的语义。解决办法包括:用 `@Lookup` 注解(Spring 动态生成子类重写该方法,每次调用都返回新实例)、直接注入 `ApplicationContext` 后手动 `getBean()`,或者使用 Scoped Proxy(作用域代理,注入一个代理对象,代理内部每次方法调用都转发到当前真正需要的实例)。

## 六、循环依赖的解决方案:三级缓存

### 什么是循环依赖

两个或多个 Bean 相互引用形成闭环,例如 A 依赖 B、B 又依赖 A。Spring 中循环依赖分两种:

- **属性(字段/Setter)循环依赖**:实例化和依赖注入是两个独立步骤,可以被 Spring 解决。
- **构造器循环依赖**:构造器注入要求实例化的同时就完成依赖注入,而依赖的对象又要求先构造出当前对象,两者互相等待,**无法解决**,Spring 会直接抛出 `BeanCurrentlyInCreationException`。

这个区分是理解三级缓存能解决什么、不能解决什么问题的前提:三级缓存的解法本质是"提前暴露一个还没装配完的半成品对象引用",而构造器注入的语义决定了对象在构造完成之前根本不存在任何可暴露的引用——这是"能不能提前暴露"这件事在两种注入方式下的根本差异。

### 为什么两级缓存不够

如果只用两级缓存(一级存放成品 Bean,二级存放提前暴露的早期引用),看起来似乎已经能解决普通对象的循环依赖了:A 实例化后立刻把自身引用放进二级缓存,B 注入时从二级缓存拿到 A 的引用即可。但这个方案在 Spring AOP 场景下会出错:

假设 A 需要被 AOP 代理(比如标注了 `@Transactional`)。按照正常的 [Bean 生命周期](#四bean-的生命周期),AOP 代理是在 **`BeanPostProcessor` 后置处理阶段**(初始化完成之后)才生成的——也就是说,一个 Bean 到底最终会不会变成代理对象,理论上要等到它初始化完毕才能"官方确定"。如果只有两级缓存,为了让 B 能在循环依赖发生时提前拿到 A,就必须在 A **实例化后、还远没有走到后置处理阶段**时就把某个形态的引用塞进二级缓存——这时候要么塞入原始对象(还没决定要不要代理),要么被迫把生成代理这个动作提前到实例化阶段来做,打乱了本该统一在后置处理阶段完成的代理生成时机。

后果是:如果塞入的是 A 的**原始对象**,B 就持有了 A 的原始对象;但容器最终在一级缓存里存放的却是 A 的**代理对象**(因为 A 真正完成生命周期后必须被替换为代理)。于是系统里同时存在 A 的两份不同实例——原始对象和代理对象——B 拿到的和容器里实际管理的不是同一个对象,这直接违反了单例 Bean"容器内有且只有一个实例"的基本约定。

### 三级缓存怎么解决这个问题

三级缓存(在 `DefaultSingletonBeanRegistry` 中维护)分别是:

| 缓存 | 名称 | 存放内容 |
|---|---|---|
| 一级缓存 | `singletonObjects` | 完全创建好、可以直接使用的成品 Bean |
| 二级缓存 | `earlySingletonObjects` | 提前暴露的早期引用(原始对象或已确定形态的代理对象),已实例化但未完成依赖注入和初始化 |
| 三级缓存 | `singletonFactories` | Bean 的 `ObjectFactory`(工厂对象),而不是 Bean 本身 |

关键设计在**三级缓存存放的是一个工厂(`ObjectFactory`),而不是一个确定形态的对象**。Bean 实例化后立刻把一个 `ObjectFactory` 放入三级缓存,这个工厂对象封装了"如果现在需要提前暴露这个 Bean,应该返回什么"这个决策,但**并不立即执行**这个决策——只有真正发生循环依赖、有其他 Bean 提前来请求它时,才会调用这个工厂的 `getObject()` 方法(即 `getEarlyBeanReference()`),在这一刻才真正决定:如果这个 Bean 需要 AOP 代理,就在这里生成代理对象并返回;不需要代理,就返回原始对象。三级缓存因此把"**是否需要提前暴露**"和"**暴露时到底给出什么形态的引用**"这两件事解耦开:

- 没有被提前引用的 Bean,依然按部就班走到 `BeanPostProcessor` 后置处理阶段才生成代理,生命周期顺序完全不受影响。
- 一旦被提前引用,提前生成的代理对象会被存入二级缓存并从三级缓存移除,后续该 Bean 走完初始化流程后,不会再重复生成代理,直接复用二级缓存里已经决定好的这一份引用。

无论是否发生循环依赖,同一个 Bean 最终对外暴露的都是**同一个**实例(可能是原始对象,也可能是代理对象),单例约定始终成立——这正是三级缓存相对两级缓存多解决的问题。

### 完整处理流程(A、B 互相依赖)

```
1. 容器开始创建 A:调用构造函数实例化 A(此时 A 是"裸对象")
                     │
                     ▼
   属性注入前,为 A 创建 ObjectFactory,放入三级缓存 singletonFactories
                     │
                     ▼
2. 开始给 A 做属性注入,发现 A 依赖 B,三级缓存中没有 B → 容器转去创建 B
                     │
                     ▼
   调用构造函数实例化 B,同样为 B 创建 ObjectFactory 放入三级缓存
                     │
                     ▼
3. 开始给 B 做属性注入,发现 B 依赖 A
   → 在三级缓存中找到 A 的 ObjectFactory,调用 getObject()
   → 按需生成 A 的早期引用(原始对象或代理对象),存入二级缓存 earlySingletonObjects
   → 同时清除三级缓存中 A 对应的工厂
   → 用这个早期引用完成 B 对 A 的依赖注入
                     │
                     ▼
4. B 的属性注入完成 → 执行 B 的初始化回调 → B 成为完整 Bean
   → 存入一级缓存 singletonObjects,清除 B 在二、三级缓存中的痕迹
                     │
                     ▼
5. 流程返回 A 的属性注入环节:直接从一级缓存拿到已就绪的 B,完成 A 对 B 的注入
                     │
                     ▼
6. A 的属性注入完成 → 执行 A 的初始化回调(若二级缓存中已有 A 的早期引用/代理,
   此处复用而不重新生成)→ A 成为完整 Bean → 存入一级缓存,清理二、三级缓存
                     │
                     ▼
                循环依赖解决,A、B 都是唯一实例
```

### 检测机制

Spring 在 Bean 开始创建时把它的名字加入一个"正在创建中"的标记集合(`singletonsCurrentlyInCreation`)。如果在创建依赖链条往下走的过程中,又递归回到了这个仍然处于"正在创建中"状态的 Bean,就说明出现了循环依赖。对构造器循环依赖而言,由于这种情况根本无法通过提前暴露引用解决,检测到后直接抛出 `BeanCurrentlyInCreationException`。

### 常见追问

- **两级缓存不能解决问题的根本原因是什么?** 因为需要正确处理"Bean 是否会被 AOP 代理"这个只有走到后置处理阶段才能确定的信息,两级缓存做不到"延迟决定暴露形态",会导致同一个 Bean 出现原始对象和代理对象两份不同实例,破坏单例。
- **提前暴露对象的前提是什么?** Bean 必须是 singleton 作用域,且循环依赖必须发生在字段/Setter 注入上。其他作用域(如 prototype)每次获取都要重新创建,无法复用"提前暴露的半成品"这个概念,容器直接检测到递归创建并报错;构造器依赖则完全无法提前暴露引用。
- **实际开发中怎么规避循环依赖?** 把两个 Bean 共同依赖的逻辑抽成独立的第三方服务,打破直接的相互引用;用 `@Lazy` 标注依赖,把某一方的实例化推迟到首次真正使用时;把构造器注入改为字段注入或 Setter 注入,让 Spring 有机会提前暴露引用。

## 七、Spring 中的设计模式

Spring 框架内部大量使用经典设计模式来组织自身实现,核心机制与这些模式一一对应:**工厂模式**(`BeanFactory`/`ApplicationContext` 负责 Bean 的创建,解耦对象的创建和使用,对应本文第一节的 IOC 容器)、**单例模式**(Bean 默认作用域为 singleton,由容器而非私有构造器保证唯一性)、**代理模式**(Spring AOP 基于 JDK/CGLIB 动态代理实现,对应本文第二节)、**模板方法模式**(`JdbcTemplate` 等以 Template 结尾的类固定算法骨架,把可变步骤通过 Callback 接口暴露给用户)、**观察者模式**(`ApplicationEvent`/`ApplicationListener`/`ApplicationEventPublisher` 构成的事件驱动模型)、**适配器模式**(AOP 通知适配到统一的 `MethodInterceptor` 接口;`HandlerAdapter` 把不同类型 Controller 的调用接口适配成 `DispatcherServlet` 能识别的统一形式)以及**装饰者模式**(多数据源动态切换等场景)。

这些模式各自的具体实现细节、与传统教科书写法的差异,详见 [「Java设计模式」](java-design-patterns.md)。

[返回索引](index.md)
