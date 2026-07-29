# Java 设计模式实现细节

> 概念、意图、UML 结构已经在 [ood-lld-notes](../ood-lld-notes/index.md) 专题讲透，本篇不重复。这里只聚焦一件事：**同一个模式，Java 语言层面到底怎么写、有哪些坑**——线程安全怎么判断、JDK 自带哪些实现、Spring 里落在哪个类上。每段代码都用本机 JDK 25（`javac` / `java`）实际编译运行过。

---

## 单例模式 · Singleton

核心思想见[「创建型模式」](../ood-lld-notes/patterns-creational.md)的 Singleton 一节。Java 里因为要面对多线程、反射、序列化这三个"破坏单例"的攻击面，衍生出 5 种写法，安全等级完全不同。

| 写法 | 懒加载 | 线程安全 | 防反射 | 防反序列化 | 说明 |
|------|--------|----------|--------|------------|------|
| 饿汉式 | 否 | 是（类加载机制保证） | 否 | 否 | 类加载时就 `new`，简单但无法延迟 |
| 懒汉式（不加锁） | 是 | **否** | 否 | 否 | `getInstance()` 里裸判断 `null`，多线程下会创建出多个实例 |
| 双重检查锁 DCL | 是 | 是 | 否 | 否 | `synchronized` + `volatile` 组合 |
| 静态内部类 | 是 | 是（JVM 类加载锁保证） | 否 | 否 | 不需要手写锁，性能最好的懒加载方案 |
| 枚举 | 否 | 是 | **是** | **是** | JVM 保证枚举常量全局唯一，天然免疫反射和反序列化攻击 |

**双重检查锁为什么必须加 `volatile`**：`instance = new DclSingleton()` 不是原子操作，会被拆成三步——① 分配内存，② 执行构造方法初始化字段，③ 把引用赋给 `instance`。JVM 和 CPU 出于优化目的可能对 ②③ 重排序，于是另一个线程可能看到 `instance != null` 但对象字段还没初始化完，即拿到一个"半初始化"对象。`volatile` 通过内存屏障禁止这种重排序，代价是每次读写都有一点点额外开销。

**为什么枚举单例最安全**：`instance.getClass().getDeclaredConstructor()` 这类反射攻击可以强行 `setAccessible(true)` 后调用私有构造器，绕过饿汉式、静态内部类等写法的单例保证；序列化场景下如果不手动重写 `readResolve()`，反序列化会走底层 `Unsafe` 分配内存，绕开构造器，生成第二个实例。而枚举类型的实例化被写死在 JVM 规范里（`Enum` 没有公开构造器可反射调用，`readObject()` 也被 JDK 针对枚举类型特殊处理成按名字查找已有常量），这两条路在语言层面直接被堵死，不需要业务代码额外防御。

```java
import java.lang.reflect.Constructor;

public class SingletonDemo {

    // 静态内部类：懒加载 + 线程安全，依赖 JVM 类加载锁
    static class HolderSingleton {
        private HolderSingleton() {}
        private static class Holder {
            private static final HolderSingleton INSTANCE = new HolderSingleton();
        }
        public static HolderSingleton getInstance() {
            return Holder.INSTANCE;
        }
    }

    // 枚举单例：JVM 保证枚举常量只会被实例化一次
    enum EnumSingleton {
        INSTANCE;
        public void doWork() { System.out.println("枚举单例工作中"); }
    }

    public static void main(String[] args) throws Exception {
        // 对静态内部类单例做反射攻击：能绕过私有构造器，破坏单例
        HolderSingleton normal1 = HolderSingleton.getInstance();
        Constructor<HolderSingleton> ctor = HolderSingleton.class.getDeclaredConstructor();
        ctor.setAccessible(true);
        HolderSingleton normal2 = ctor.newInstance();
        System.out.println("普通单例反射后仍相同? " + (normal1 == normal2)); // false，已被破坏

        // 对枚举单例做同样的反射攻击：JVM 层面直接拒绝
        try {
            Constructor<EnumSingleton> enumCtor =
                    EnumSingleton.class.getDeclaredConstructor(String.class, int.class);
            enumCtor.setAccessible(true);
            enumCtor.newInstance("FAKE", 1);
        } catch (IllegalArgumentException e) {
            System.out.println("枚举单例反射攻击被拒绝: " + e.getMessage());
        }
    }
}
```

运行结果：`普通单例反射后仍相同? false`，`枚举单例反射攻击被拒绝: Cannot reflectively create enum objects`——一行代码就能证明为什么《Effective Java》推荐用枚举实现单例。

---

## 工厂模式 · Factory

核心思想见[「创建型模式」](../ood-lld-notes/patterns-creational.md)的 Factory Method / Abstract Factory 一节。Java 里三种工厂（简单工厂、工厂方法、抽象工厂）的落地差异主要在"新增产品类型要不要改工厂代码"。

简单工厂最常见的写法是 `if-else` 或 `switch` 按参数分发，但新增类型必须回来改这个方法体，违反开闭原则；Java 里更地道的做法是用 `Map<String, Supplier<T>>` 做注册表，把类型标识和构造函数引用（`ClassName::new`）存成键值对，新增类型只需要多注册一行，工厂方法本身不用改：

```java
import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

public class FactoryDemo {

    interface Notifier {
        void send(String msg);
    }

    static class EmailNotifier implements Notifier {
        public void send(String msg) { System.out.println("邮件发送: " + msg); }
    }

    static class SmsNotifier implements Notifier {
        public void send(String msg) { System.out.println("短信发送: " + msg); }
    }

    static class NotifierFactory {
        private static final Map<String, Supplier<Notifier>> REGISTRY = new HashMap<>();
        static {
            REGISTRY.put("email", EmailNotifier::new);
            REGISTRY.put("sms", SmsNotifier::new);
        }
        static Notifier create(String type) {
            Supplier<Notifier> supplier = REGISTRY.get(type);
            if (supplier == null) {
                throw new IllegalArgumentException("未知通知类型: " + type);
            }
            return supplier.get();
        }
    }

    public static void main(String[] args) {
        NotifierFactory.create("email").send("订单已创建");
        NotifierFactory.create("sms").send("验证码 123456");
    }
}
```

**JDK 与 Spring 里的真实例子**：`Calendar.getInstance()`、`DateFormat.getInstance()` 都是简单工厂，按地区/风格参数返回不同实现；`Collection` 体系里每种集合类都对应一个 `Iterator` 实现，`iterator()` 方法就是工厂方法模式。Spring 的 `BeanFactory` 是简单工厂与工厂方法的结合体——统一定义了 `getBean()` 这套获取 Bean 的接口，具体到某个 Bean 怎么实例化、怎么注入依赖，则由容器内部的各种 `BeanDefinition` 和后置处理器决定；`FactoryBean<T>` 接口则是典型的工厂方法模式，业务方实现 `getObject()` 封装复杂的创建逻辑（比如连接池、代理对象这种不能直接用无参构造器 `new` 出来的对象），Spring 容器负责在合适的时机调用它。

---

## 建造者模式 · Builder

核心思想见[「创建型模式」](../ood-lld-notes/patterns-creational.md)的 Builder 一节。Java 没有关键字参数（keyword argument），构造函数一旦超过 4、5 个参数，调用处全靠位置传参，可读性和安全性都会崩——这是 Java 里 Builder 模式格外常见的直接原因。

Java 里最地道的写法是**把 Builder 做成目标类的 `static` 内部类**，而不是独立的一个类：这样 Builder 可以直接访问外部类的私有构造器，构造出来的对象可以做成不可变（所有字段 `final`，只在私有构造器里赋值一次），线程安全顺带就解决了。`java.lang.StringBuilder`、`Stream.Builder`、`java.net.http.HttpRequest.Builder`（JDK 11 内置的 HTTP 客户端）都是这个套路的标准实现。

```java
public class BuilderDemo {

    static final class HttpRequest {
        private final String url;
        private final String method;
        private final int timeout;
        private final boolean retry;

        private HttpRequest(Builder b) {
            this.url = b.url;
            this.method = b.method;
            this.timeout = b.timeout;
            this.retry = b.retry;
        }

        @Override
        public String toString() {
            return "HttpRequest{url=%s, method=%s, timeout=%d, retry=%b}"
                    .formatted(url, method, timeout, retry);
        }

        static final class Builder {
            private String url;
            private String method = "GET";
            private int timeout = 30;
            private boolean retry = false;

            Builder url(String url) { this.url = url; return this; }
            Builder method(String method) { this.method = method; return this; }
            Builder timeout(int seconds) { this.timeout = seconds; return this; }
            Builder retry(boolean retry) { this.retry = retry; return this; }

            HttpRequest build() {
                if (url == null || url.isEmpty()) {
                    throw new IllegalStateException("url 必填");
                }
                return new HttpRequest(this);
            }
        }
    }

    public static void main(String[] args) {
        HttpRequest req = new HttpRequest.Builder()
                .url("https://api.example.com/pay")
                .method("POST")
                .timeout(10)
                .retry(true)
                .build();
        System.out.println(req);
    }
}
```

**实践提醒**：手写这套模板代码重复度很高，实际项目里通常用 Lombok 的 `@Builder` 注解自动生成上面这一整套 Builder 代码，省去样板代码；本篇不引入 Lombok 依赖，但了解手写版本的结构，才看得懂 `@Builder` 展开之后生成了什么。`build()` 里做非空/非法值校验（如上面的 `url` 必填检查）是 Java Builder 的惯例，比 Python 版本更强调"构造完成前就要拦住非法状态"，因为 Java 对象一旦 `new` 出来通常被当作已经可用。

---

## 代理模式 · Proxy

核心思想见[「结构型模式」](../ood-lld-notes/patterns-structural.md)的 Proxy 一节。Java 里代理有三种实现路径，区别主要在"代理类什么时候生成"和"能不能代理没有接口的类"。

| | 静态代理 | JDK 动态代理 | CGLIB 动态代理 |
|--|----------|--------------|----------------|
| 代理类生成时机 | 编译期，手写代码 | 运行期，反射生成 `.class` | 运行期，字节码生成子类 |
| 依赖 | 无 | JDK 自带 `java.lang.reflect.Proxy` | 第三方库（Spring 内嵌了一份） |
| 前提条件 | 手动实现同一接口 | 目标类必须实现至少一个接口 | 目标类不能是 `final`，方法不能是 `final`/`private`/`static` |
| 原理 | 手写一个类实现相同接口，持有目标对象引用 | 生成 `$ProxyN` 类实现目标接口，方法调用转发给 `InvocationHandler.invoke()` | 生成目标类的子类，重写方法插入增强逻辑，`super.method()` 调用原方法 |
| 扩展性 | 差，每个真实类对应一个代理类 | 好，一个 `InvocationHandler` 可代理任意接口 | 好，但无法代理没有接口且被 `final` 修饰的类 |

**Spring AOP 用哪种、什么时候降级到 CGLIB**：Spring AOP 默认规则是"目标类实现了至少一个接口就用 JDK 动态代理，否则自动降级为 CGLIB"；但从 Spring Boot 2.0 开始，`spring.aop.proxy-target-class` 默认被设为 `true`，也就是**默认统一使用 CGLIB**，即便目标类实现了接口——这是为了避免"注入的字段类型是具体类、但容器里放的是只实现了接口的 JDK 代理"导致的 `ClassCastException`，用一致的行为换取更少的踩坑。这也是为什么 `@Transactional`、`@Cacheable` 标注的类**不能是 `final` 类，方法也不能是 `final`/`private`**——CGLIB 需要能继承并重写这些方法，一旦是 `final` 或 `private`，代理会静默失效（方法调用不经过代理，直接执行原始逻辑，事务/缓存增强逻辑不生效）。

```java
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

public class ProxyDemo {

    interface UserService {
        void save(String name);
    }

    static class UserServiceImpl implements UserService {
        @Override
        public void save(String name) {
            System.out.println("保存用户: " + name);
        }
    }

    // JDK 动态代理必须实现 InvocationHandler，所有接口方法调用都会走 invoke
    static class LogInvocationHandler implements InvocationHandler {
        private final Object target;
        LogInvocationHandler(Object target) { this.target = target; }

        @Override
        public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
            System.out.println("[JDK代理] 前置日志: 调用 " + method.getName());
            Object result = method.invoke(target, args);
            System.out.println("[JDK代理] 后置日志: 调用完成");
            return result;
        }
    }

    public static void main(String[] args) {
        UserService target = new UserServiceImpl();

        // Proxy.newProxyInstance 三个参数：类加载器、要实现的接口数组、InvocationHandler
        UserService proxy = (UserService) Proxy.newProxyInstance(
                UserService.class.getClassLoader(),
                new Class<?>[]{UserService.class},
                new LogInvocationHandler(target)
        );

        proxy.save("Ada");
        System.out.println("是否为 Proxy 生成的类: " + Proxy.isProxyClass(proxy.getClass()));
    }
}
```

运行结果确认了 `proxy.getClass().getName()` 是 JVM 生成的 `$Proxy0`，`Proxy.isProxyClass(...)` 返回 `true`——代理类是运行期真实生成的一个类，不是简单的转发包装。

---

## 策略模式 · Strategy

核心思想见[「行为型模式」](../ood-lld-notes/patterns-behavioral.md)的 Strategy 一节。Java 8 之前，策略模式几乎总是"一个策略接口 + N 个实现类"；有了函数式接口和 Lambda 之后，只要策略逻辑是单一方法、无状态的，完全可以用 `java.util.function` 包下的现成接口（`Function`、`Predicate`、`DoubleUnaryOperator`……）配合 Lambda 表达式代替具体策略类，省掉一整批只有一个方法的样板类。

Java 标准库里最经典的策略模式实践是 `Comparator`：它本身就是一个策略接口，`List.sort(Comparator)`、`Collections.sort` 都是依赖这个策略接口的 Context；`Comparator.comparingInt(...).thenComparing(...)` 这类链式组合方法，本质是把多个策略组合成一个新策略。

```java
import java.util.Comparator;
import java.util.List;
import java.util.function.DoubleUnaryOperator;

public class StrategyDemo {

    public static void main(String[] args) {
        // 1. 用函数式接口 + Lambda 表达策略，省掉具体策略类
        DoubleUnaryOperator noDiscount = price -> price;
        DoubleUnaryOperator ninePercentOff = price -> price * 0.9;
        DoubleUnaryOperator cashback50 = price -> price >= 200 ? price - 50 : price;

        System.out.println("原价策略: " + noDiscount.applyAsDouble(100));
        System.out.println("九折策略: " + ninePercentOff.applyAsDouble(100));
        System.out.println("满减策略: " + cashback50.applyAsDouble(200));

        // 2. JDK 自带的策略模式实践：Comparator 本身就是一个策略接口
        List<String> names = new java.util.ArrayList<>(List.of("Charlie", "Ada", "Bob"));
        names.sort(Comparator.comparingInt(String::length).thenComparing(Comparator.naturalOrder()));
        System.out.println("按长度再按字典序: " + names);
    }
}
```

**什么时候仍然要用具体策略类而不是 Lambda**：策略本身需要维护内部状态、需要被 Spring 容器管理（依赖注入、切面增强）、或者策略逻辑本身很复杂需要拆成多个私有方法时，Lambda 会力不从心，这时仍然应该退回"策略接口 + 具体实现类 + Spring 按 `@Qualifier`/`Map<String, Strategy>` 注入"这套写法，用类型安全换取可维护性。

---

## 装饰器模式 · Decorator

核心思想见[「结构型模式」](../ood-lld-notes/patterns-structural.md)的 Decorator 一节。Java 里要特别分清两个同名不同义的概念：**注解（`@Override`、自定义 `@interface`）编译期装饰的是类/方法的元数据**，而**本模式装饰的是运行时对象**，两者除了都叫"装饰"外没有任何关系，面试容易被搞混。

Java 标准库里最经典、也是解释装饰器模式时最常被引用的实现就是 `java.io` 的流体系：`FileInputStream`/`ByteArrayInputStream` 是基础组件，只提供最原始的字节读取；`BufferedInputStream` 是缓冲装饰器，叠加了缓冲区批量读取的能力；`InputStreamReader` 把字节流装饰成字符流；再往外套一层 `BufferedReader` 才有 `readLine()` 这种按行读取的能力。每一层都实现同一套读取语义（都能当作输入源使用），却在原有能力上叠加了新职责——这正是装饰器模式"不改变接口、层层叠加"的意图。

```java
public class DecoratorDemo {

    interface Coffee {
        String describe();
        double cost();
    }

    static class Espresso implements Coffee {
        public String describe() { return "Espresso"; }
        public double cost() { return 10.0; }
    }

    static abstract class CoffeeDecorator implements Coffee {
        protected final Coffee inner;
        CoffeeDecorator(Coffee inner) { this.inner = inner; }
    }

    static class Milk extends CoffeeDecorator {
        Milk(Coffee inner) { super(inner); }
        public String describe() { return inner.describe() + " + Milk"; }
        public double cost() { return inner.cost() + 2.0; }
    }

    static class Sugar extends CoffeeDecorator {
        Sugar(Coffee inner) { super(inner); }
        public String describe() { return inner.describe() + " + Sugar"; }
        public double cost() { return inner.cost() + 1.0; }
    }

    public static void main(String[] args) throws Exception {
        Coffee order = new Sugar(new Milk(new Espresso()));
        System.out.println(order.describe() + " -> " + order.cost());

        // JDK 自身最经典的装饰器案例：java.io 里 InputStream 家族层层包装
        try (java.io.BufferedReader reader = new java.io.BufferedReader(
                new java.io.InputStreamReader(
                        new java.io.ByteArrayInputStream("line1\nline2".getBytes())))) {
            String line;
            while ((line = reader.readLine()) != null) {
                System.out.println("读到一行: " + line);
            }
        }
    }
}
```

`Sugar(Milk(Espresso()))` 输出 `Espresso + Milk + Sugar -> 13.0`；`BufferedReader` 包 `InputStreamReader` 包 `ByteArrayInputStream` 这三层嵌套，成功按行读出了字节数组里的内容——两段代码验证的是同一个结构。Spring 里 `BeanWrapper`、`DecoratingProxy` 这类接口也是用装饰器思路给 Bean 动态叠加访问能力。

---

## 观察者模式 · Observer

核心思想见[「行为型模式」](../ood-lld-notes/patterns-behavioral.md)的 Observer 一节。JDK 曾经在 `java.util` 包内置过一套观察者模式的现成实现——`Observable` 类 + `Observer` 接口——但从 **Java 9 开始被标记为 `@Deprecated`**，原因是设计上的硬伤：`Observable` 是一个具体类而不是接口，Java 不支持多继承，一旦业务类已经继承了别的父类就无法再继承 `Observable`；状态变更还必须先手动调用 `setChanged()` 做标记，再调 `notifyObservers()` 才会真正触发通知，这一步很容易被忘记，通知也没有分级、没有异步支持。

```java
import java.util.List;
import java.util.concurrent.CopyOnWriteArrayList;

public class ObserverDemo {

    interface OrderObserver {
        void onOrderPlaced(String orderId);
    }

    // 用 CopyOnWriteArrayList 而不是 ArrayList：遍历通知的同时允许安全地增删观察者，
    // 避免并发场景下抛 ConcurrentModificationException
    static class OrderSubject {
        private final List<OrderObserver> observers = new CopyOnWriteArrayList<>();

        void attach(OrderObserver o) { observers.add(o); }
        void detach(OrderObserver o) { observers.remove(o); }

        void place(String orderId) {
            System.out.println("创建订单 " + orderId);
            for (OrderObserver o : observers) {
                o.onOrderPlaced(orderId);
            }
        }
    }

    public static void main(String[] args) {
        OrderSubject subject = new OrderSubject();
        OrderObserver email = id -> System.out.println("[邮件] 订单 " + id + " 已创建");
        OrderObserver metrics = id -> System.out.println("[指标] order_placed +1");

        subject.attach(email);
        subject.attach(metrics);
        subject.place("A1001");

        subject.detach(metrics);
        subject.place("A1002");
    }
}
```

现代 Java 项目里，`java.util.Observable`/`Observer` 已经不建议使用，实践中的替代方案：自己定义观察者接口（如上）是最直接的方式；GUI/Bean 场景可以用 `java.beans.PropertyChangeSupport` + `PropertyChangeListener`，语义上专门针对"某个属性变化时通知"；Spring 容器里 `ApplicationEvent` + `ApplicationListener` 是框架级的发布-订阅实现，`ApplicationContext.publishEvent()` 对应发布动作，标了 `@EventListener` 的方法对应观察者，`ApplicationContext` 本身承担了原来 `Subject` 维护观察者列表并遍历通知的职责。

---

[返回索引](index.md)
