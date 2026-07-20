# Python 算法刷题速查表

> 算法面试中常用的 Python 标准库函数和技巧。Python 3.12+。

---

## 一、内置数据结构

### list

```python
arr = [1, 2, 3]

# 增删改查
arr.append(4)           # 尾部加 O(1)
arr.pop()               # 尾部弹出 O(1)
arr.pop(0)              # 头部弹出 O(n)
arr.insert(0, 0)        # 指定位置插入 O(n)
arr.remove(2)           # 按值删除第一个 O(n)
arr.index(3)            # 查找索引

# 切片 (浅拷贝)
arr[1:3]                # [2, 3]
arr[::-1]               # 反转
arr[-1]                 # 最后一个元素

# 其他
arr.sort()              # 原地排序 O(n log n)
arr.sort(reverse=True)  # 降序
sorted(arr)             # 返回新列表
len(arr)
sum(arr)
max(arr), min(arr)
all(x > 0 for x in arr)  # 全为真
any(x > 0 for x in arr)  # 任一为真
```

### tuple

```python
t = (1, 2, 3)  # 不可变
a, b, c = t    # 解包
```

### set

```python
s = {1, 2, 3}
s.add(4)            # O(1)
s.remove(2)         # 不存在则 KeyError
s.discard(2)        # 不存在也不报错

# 集合运算
a | b   # 并集
a & b   # 交集
a - b   # 差集
a ^ b   # 对称差
a <= b  # a 是 b 的子集
```

### dict

```python
d = {"a": 1, "b": 2}
d["c"] = 3
d.get("x", 0)            # 有则返回值，无则返回默认值
d.pop("a")               # 删除并返回值

for k, v in d.items():   # 遍历
    pass

# dict comprehension
d2 = {k: v * 2 for k, v in d.items()}

# 合并字典 (Python 3.9+)
d3 = d | d2  # d2 覆盖 d 的同名键
```

### str

```python
s = "hello world"
s.split()           # ["hello", "world"]
s.split(",")
",".join(["a","b"]) # "a,b"
s.strip()           # 去两端空格
s.lower(), s.upper()
s.isdigit(), s.isalpha(), s.isalnum()
s.find("wo")        # 返回索引，找不到返回 -1
s.count("l")        # 计数
s.replace("h", "H") # 替换
s[::-1]             # 反转

# 字符 <-> ASCII
ord("a")  # 97
chr(97)   # "a"
```

---

## 二、collections 模块

### deque（双端队列，BFS 必备）

```python
from collections import deque

q = deque([1, 2, 3])
q.append(4)        # 尾部 O(1)
q.appendleft(0)    # 头部 O(1)
q.pop()            # 尾部 O(1)
q.popleft()        # 头部 O(1)
q[0]               # 查看队首
q[-1]              # 查看队尾
```

### Counter（计数器）

```python
from collections import Counter

cnt = Counter("abracadabra")
cnt["a"]            # 5
cnt.most_common(2)  # [('a', 5), ('b', 2)]
cnt.update("abc")   # 合并计数
cnt.total()         # 总计数 (Python 3.10+)
```

### defaultdict（带默认值）

```python
from collections import defaultdict

d = defaultdict(int)       # 默认值 0
d = defaultdict(list)      # 默认值 []
d = defaultdict(set)       # 默认值 set()
d = defaultdict(lambda: 0) # 自定义默认值
```

### OrderedDict（有序字典，LRU Cache）

```python
from collections import OrderedDict

od = OrderedDict()
od["a"] = 1
od.move_to_end("a")         # 移到末尾
od.popitem(last=False)      # 弹出第一个（FIFO）
od.popitem(last=True)       # 弹出最后一个（LIFO）
```

---

## 三、heapq 模块（小顶堆）

```python
import heapq

heap = [3, 1, 4]
heapq.heapify(heap)              # 原地建堆 O(n)

heapq.heappush(heap, 2)          # O(log n)
heapq.heappop(heap)              # O(log n)
heap[0]                          # 查看堆顶 O(1)

heapq.heappushpop(heap, 5)       # push + pop
heapq.heapreplace(heap, 0)       # pop + push

heapq.nlargest(3, arr)           # 最大 k 个
heapq.nsmallest(3, arr)          # 最小 k 个

# 大顶堆技巧
max_heap = []
heapq.heappush(max_heap, -val)   # 取反
largest = -heapq.heappop(max_heap)

# 自定义优先队列元组
pq = []
heapq.heappush(pq, (priority, item))
```

---

## 四、bisect 模块（二分）

```python
import bisect

arr = [1, 2, 4, 5]

bisect.bisect_left(arr, 3)   # 2 — 第一个 ≥3 的位置
bisect.bisect_right(arr, 3)  # 2 — 第一个 >3 的位置

bisect.insort_left(arr, 3)   # 插入并保持有序 O(n)
```

---

## 五、itertools 模块

```python
import itertools

# 排列
list(itertools.permutations([1,2,3]))      # n! 种排列
list(itertools.permutations([1,2,3], 2))   # 部分排列

# 组合
list(itertools.combinations([1,2,3], 2))   # C(n,k) 无序
list(itertools.combinations_with_replacement([1,2,3], 2))  # 可重复

# 笛卡尔积
list(itertools.product([1,2], ["a","b"]))  # [(1,'a'), (1,'b'), (2,'a'), (2,'b')]

# 累积和（前缀和）
list(itertools.accumulate([1,2,3,4]))      # [1, 3, 6, 10]

# 链式拼接
list(itertools.chain([1,2], [3,4]))        # [1, 2, 3, 4]

# 分组
list(itertools.groupby("aabbbc"))  # 连续相同元素分组

# 相邻对 (Python 3.10+)
list(itertools.pairwise([1,2,3,4]))  # [(1,2), (2,3), (3,4)]

# 无限迭代器
itertools.count(start=0, step=1)
itertools.cycle([1,2,3])
itertools.repeat("x", 5)
```

---

## 六、functools 模块

```python
from functools import lru_cache, cache, cmp_to_key, reduce

# 记忆化（DP 必备）
@lru_cache(maxsize=None)
def fib(n: int) -> int:
    return n if n < 2 else fib(n - 1) + fib(n - 2)

# Python 3.9+: 无限制缓存
@cache
def fib2(n: int) -> int:
    return n if n < 2 else fib2(n - 1) + fib2(n - 2)

# 自定义比较器转 key
def cmp(a, b):
    return a - b
arr.sort(key=cmp_to_key(cmp))

# reduce
reduce(lambda a, b: a * b, [1, 2, 3, 4])  # 24
```

---

## 七、math 模块

```python
import math

math.inf                    # 正无穷
-math.inf                   # 负无穷
math.ceil(3.2)              # 4
math.floor(3.8)             # 3
math.isqrt(10)              # 3 — 整数平方根
math.sqrt(4.0)              # 2.0
math.gcd(12, 8)             # 4
math.lcm(12, 8)             # 24 (Python 3.9+)
math.comb(5, 2)             # 10 — C(n,k)
math.perm(5, 2)             # 20 — P(n,k)
math.factorial(5)           # 120
math.log2(8)                # 3.0
pow(2, 10, 1000000007)      # 带模快速幂
```

---

## 八、位运算速查

```python
# 基本运算
a & b   # AND
a | b   # OR
a ^ b   # XOR
~a      # NOT (补码)
a << 1  # 左移 ×2
a >> 1  # 右移 ÷2

# 常用操作
n & (n - 1)       # 去掉最低位的 1
n & -n            # lowbit = 最低位的 1
n.bit_count()     # 1 的个数 (Python 3.8+)
n.bit_length()    # 二进制长度
(1 << n) - 1      # n 位全 1

# 集合操作
s |= (1 << i)              # 加入元素
s &= ~(1 << i)             # 删除元素
s ^= (1 << i)              # 翻转
bool((s >> i) & 1)         # 检查元素
sub = (sub - 1) & mask     # 枚举子集
```

---

## 九、自定义排序

```python
# 单 key
arr.sort(key=lambda x: x[1])

# 多 key（元组）
arr.sort(key=lambda x: (x[0], -x[1]))  # 第一个升序，第二个降序

# 按自定义比较器
from functools import cmp_to_key
arr.sort(key=cmp_to_key(lambda a, b: a - b))

# 稳定排序 vs 不稳定
arr.sort()       # 不稳定（TimSort 有稳定性保证但不要依赖）
sorted(arr)      # 稳定
```

---

## 十、常用代码片段

```python
# 深拷贝
import copy
new = copy.deepcopy(old)

# 二维数组
grid = [[0] * n for _ in range(m)]  # 正确写法
# grid = [[0] * n] * m               # BUG: 所有行引用同一个 list

# 无穷大
INF = float("inf")
abs(-INF)  # inf — 注意

# 枚举
for i, val in enumerate(arr):
    pass
for i, val in enumerate(arr, start=1):  # 从 1 开始
    pass

# zip
for a, b in zip(arr1, arr2):
    pass

# 转置矩阵
list(zip(*matrix))

# 判定空
if not arr:      # 空 list/dict/set/str
if arr:          # 非空

# 快速输入模板 (ACM模式)
import sys
data = sys.stdin.read().split()
# 或逐行
for line in sys.stdin:
    pass
```

---

[← 返回索引](index.md)
