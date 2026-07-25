# 栈、队列与双端队列

栈(后进先出)、队列(先进先出)、双端队列(两端都能进出)是刷题和实际工程里最常用的三种线性结构。只有 C++ 在标准库里给了专门的类型名,其余三门语言都是"用别的容器模拟"。

## 一、语言支持程度一览

| 语言 | 栈 | 队列 | 双端队列 |
|------|-----|------|----------|
| C++ | `std::stack` | `std::queue` | `std::deque` |
| Python | `list`(`append`/`pop`) | `collections.deque` | `collections.deque` |
| Go | 无内建类型,用 `slice` 模拟 | 无内建类型,用 `slice` 模拟(有坑,见下) | 无内建类型,`container/list` 或 `slice` |
| Java | `Deque` 接口(`ArrayDeque` 实现);遗留的 `Stack` 类不推荐 | `Deque` 接口(`ArrayDeque` 实现) | `Deque` 接口(`ArrayDeque` 实现) |

Java 是四门语言里"用一个接口统一三种结构"做得最彻底的——`Deque`(double-ended queue)本身就同时支持栈的 `push`/`pop` 和队列的 `offer`/`poll`,`ArrayDeque` 一个实现类可以当栈用、当队列用、也可以当双端队列用。C++ 反而是"分得最细"的,`stack`/`queue` 甚至不是独立容器,而是**容器适配器**(默认包着一个 `deque`,只是限制了能调用的接口)。

## 二、栈:各语言怎么写

```cpp
// C++
stack<int> st;
st.push(1); st.push(2); st.push(3);
int top = st.top();   // 查看栈顶,不弹出
st.pop();             // 弹出栈顶(注意:pop() 不返回值!要先 top() 再 pop()
```

```python
# Python:官方推荐直接用 list 当栈,不需要引入额外类型
stack = []
stack.append(1); stack.append(2); stack.append(3)
top = stack[-1]     # 查看栈顶
stack.pop()         # 弹出栈顶(注意:Python的 pop() 【会】返回被弹出的值,和C++不同)
```

```go
// Go:slice 天然适合当栈,尾部操作均摊 O(1)
stack := []int{}
stack = append(stack, 1, 2, 3)
top := stack[len(stack)-1]
stack = stack[:len(stack)-1]  // "弹出":重新切片,底层数组内存不会立刻释放
```

```java
// Java:官方推荐 Deque,而不是遗留的 Stack 类
Deque<Integer> stack = new ArrayDeque<>();
stack.push(1); stack.push(2); stack.push(3);
int top = stack.peek();   // 查看栈顶
stack.pop();              // 弹出栈顶(【会】返回值,和C++的stack不同)
```

**为什么 C++ 的 `stack::pop()` 不返回值,而 Python/Java 的弹出操作都返回值**:这是 C++ 从异常安全角度做出的设计——如果 `pop()` 既要弹出元素又要返回它,那么"返回值"这一步涉及拷贝构造,一旦拷贝构造函数抛出异常,容器就会陷入一个不一致的状态(元素到底算弹出了没有?)。C++ 标准库把"看一眼"(`top()`,只读、不改变容器)和"弹出"(`pop()`,只做删除、不涉及拷贝)拆成两个不会互相干扰的独立操作,牺牲了"一步到位"的书写便利,换取"每一步操作要么完全成功要么完全不生效"的异常安全保证。Python 的 `list.pop()`、Java 的 `Deque.pop()` 都没有这层顾虑——两门语言的错误处理机制(异常)本身就假定"操作失败会抛出,不会留下一半状态",不需要为"返回值时抛异常"这种情况特别设计接口。

**为什么 Java 官方文档明确不推荐用 `java.util.Stack`**:这个类是 Java 1.0 就有的遗留类,继承自 `Vector`,而 `Vector` 的所有方法都是 `synchronized`(每次调用都要加锁),这在单线程场景下是纯粹的性能浪费;`ArrayDeque` 是后来(Java 6)补上的、专门为"当栈或队列用"设计的实现,没有不必要的同步开销,官方 Javadoc 直接写着"A more complete and consistent set of LIFO stack operations is provided by the Deque interface"。这是一个"接口设计后来居上、但旧类型因为兼容性不能删除"的典型历史遗留案例。

## 三、队列:最容易踩性能坑的一节

```python
# Python:错误写法 vs 正确写法
lst = [1, 2, 3]
lst.pop(0)   # 能工作,但是 O(n)!要把剩下所有元素往前搬一位

from collections import deque
q = deque([1, 2, 3])
q.popleft()  # 正确写法,O(1)
```

```go
// Go:queue[1:] 看起来是 O(1),但有隐藏代价
queue := []int{1, 2, 3}
queue = queue[1:]   // 表面上"出队"很快,但底层数组的内存不会被回收/复用,
                    // 长时间大量出队会导致底层数组持续增长、内存占用只增不减
```

**为什么 `list.pop(0)`(Python)和 `queue[1:]`(Go)都不是队列的正确实现,尽管两者表现形式不同**:两者的根源相同——数组/切片的数据在内存里是**连续存储**的,"从头部拿走一个元素"要么需要把后面所有元素向前搬一位(`list.pop(0)` 的做法,代价是 O(n) 时间),要么只移动一个指向起始位置的指针、不搬数据(`queue[1:]` 的做法,代价是**空间**——被跳过的那部分内存虽然逻辑上不再属于这个 slice,但只要还有其他引用指着同一个底层数组,GC 就无法回收它,而这个 slice 本身也不会随着不断切片而收缩总容量)。**真正的队列需要头尾都是 O(1) 的数据结构**,这正是 `collections.deque`(Python)、`container/list`(Go 的双向链表)、`ArrayDeque`(Java,内部是循环缓冲区而非直接连续数组)存在的意义——它们要么用双向链表避免"搬移",要么用环形缓冲区复用已经越界的空间,专门解决"数组结构做队列头部操作天生低效"这个问题。C++ 的 `std::queue` 默认底层是 `std::deque`,同样是分块结构而非单一连续数组,从设计上就避免了这个坑,这也是为什么它敢于叫"queue"而不需要额外提醒使用者。

## 四、双端队列

```python
from collections import deque
dq = deque()
dq.append(1); dq.appendleft(0); dq.append(2)
print(list(dq))   # [0, 1, 2]
```

```java
Deque<Integer> deque = new ArrayDeque<>();
deque.addLast(1); deque.addFirst(0); deque.addLast(2);
System.out.println(deque);   // [0, 1, 2]
```

四门语言的双端队列在概念上完全一致(两端都能 O(1) 增删),只是命名不同:C++/Python 直接叫 `push_front`/`push_back`(或 `appendleft`/`append`),Java 用 `addFirst`/`addLast`,语义上没有分歧,纯粹是命名习惯差异。

## 小结

- C++ 的 `top()`/`pop()` 分离是异常安全的产物;Python/Java 的弹出操作直接返回值,是两者错误处理机制不同带来的接口设计差异。
- Python `list.pop(0)` 和 Go `queue[1:]` 都不是队列的正确实现——数组/切片结构的头部操作天生代价高(时间或空间),真正的队列要用双向链表或环形缓冲区。
- Java 用统一的 `Deque` 接口覆盖栈/队列/双端队列三种用法,是四门语言里接口设计最统一的;遗留的 `Stack` 类因历史包袱(继承自加锁的 `Vector`)已不推荐使用。

---
[← 上一篇:字符串](strings.md) · [返回索引](index.md) · [下一篇:跨语言易错点速查](pitfalls.md)
