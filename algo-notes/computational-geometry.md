# 计算几何学 · Computational Geometry

> 计算几何的题目大多要求"证明一个几何直觉是对的"，然后把证明翻译成一两个符号判断——
> 核心工具几乎只有一个：**叉积 (cross product)** 能告诉你"三个点构成左转还是右转"，
> 本文的三个经典算法（线段相交、凸包、最近点对）都是叉积的不同应用方式。

---

## 一、叉积：判断转向

```python
def cross(o: tuple[int, int], a: tuple[int, int], b: tuple[int, int]) -> int:
    """
    向量 (a-o) 与 (b-o) 的叉积。
    > 0：o->a->b 是"左转"（逆时针）
    < 0：o->a->b 是"右转"（顺时针）
    = 0：o, a, b 三点共线
    """
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
```

> 这一个函数是本文三个算法共同的基础——线段相交靠它判断"点在线段的哪一侧"，
> 凸包靠它判断"要不要把上一个点从凸包里剔除"，本质上都是同一个几何直觉的不同用法。

---

## 二、判断两条线段是否相交 · [LC 面试常见]

### 2.1 核心思路

```
线段 p1p2 和 p3p4 相交，分两种情况：

1. "标准"相交（十字交叉）：
   p1, p2 分别在直线 p3p4 的两侧，且 p3, p4 分别在直线 p1p2 的两侧。
   用叉积判断"在哪一侧"：cross(p3,p4,p1) 和 cross(p3,p4,p2) 符号相反，
   且 cross(p1,p2,p3) 和 cross(p1,p2,p4) 符号也相反。

2. "退化"情况（共线）：
   如果某个叉积算出来是 0，说明有三点共线，这时不能只看符号，
   要退化成"判断这个点是否落在另一条线段的包围盒内"（on_segment 检查）。
```

### 2.2 完整实现

```python
def on_segment(p: tuple[int, int], q: tuple[int, int], r: tuple[int, int]) -> bool:
    """已知 p, q, r 共线，判断 q 是否落在线段 pr 上（包括端点）。"""
    return (min(p[0], r[0]) <= q[0] <= max(p[0], r[0]) and
            min(p[1], r[1]) <= q[1] <= max(p[1], r[1]))


def segments_intersect(
    p1: tuple[int, int], p2: tuple[int, int],
    p3: tuple[int, int], p4: tuple[int, int],
) -> bool:
    """判断线段 p1p2 和 p3p4 是否相交（包括端点接触、共线重叠的情况）。"""
    d1 = cross(p3, p4, p1)
    d2 = cross(p3, p4, p2)
    d3 = cross(p1, p2, p3)
    d4 = cross(p1, p2, p4)

    # 标准情况：两两互相在对方两侧
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
       ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True

    # 退化情况：共线时退化成包围盒检查
    if d1 == 0 and on_segment(p3, p1, p4):
        return True
    if d2 == 0 and on_segment(p3, p2, p4):
        return True
    if d3 == 0 and on_segment(p1, p3, p2):
        return True
    if d4 == 0 and on_segment(p1, p4, p2):
        return True

    return False
```

### 2.3 正确性验证

```python
from fractions import Fraction as F


def exact_intersect_reference(p1, p2, p3, p4) -> bool:
    """
    参照答案：直接解线段的参数方程 p1+t*(p2-p1) = p3+u*(p4-p3)，
    用精确分数运算（避免浮点误差）检查 t, u 是否都落在 [0,1]。
    这是跟 segments_intersect 完全独立的另一种实现方式，用来交叉验证。
    """
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        if cross(p1, p2, p3) != 0:
            return False  # 平行但不共线
        # 共线：退化成两条线段在同一条直线上是否有重叠
        return (on_segment(p1, p3, p2) or on_segment(p1, p4, p2)
                or on_segment(p3, p1, p4) or on_segment(p3, p2, p4))
    t = F((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4), denom)
    u = F((x1 - x3) * (y1 - y2) - (y1 - y3) * (x1 - x2), denom)
    return 0 <= t <= 1 and 0 <= u <= 1


import random

random.seed(0)
fail, trials = 0, 0
for _ in range(2000):
    pts = [(random.randint(-5, 5), random.randint(-5, 5)) for _ in range(4)]
    p1, p2, p3, p4 = pts
    if p1 == p2 or p3 == p4:
        continue
    trials += 1
    if segments_intersect(p1, p2, p3, p4) != exact_intersect_reference(p1, p2, p3, p4):
        fail += 1

print(f"线段相交 vs 精确分数解方程参照答案：{trials} 次随机测试，不匹配 {fail} 次")
```

---

## 三、凸包 (Convex Hull)

### 3.1 核心思路：Andrew 单调链算法

```
凸包：包含所有点的最小凸多边形，直觉上像"用橡皮筋把所有点框起来"。

Andrew's Monotone Chain 算法：
1. 把所有点按 x 坐标排序（x 相同按 y 排序）
2. 从左到右扫描，维护一个"下凸壳"：
   每加入一个新点，只要"新点和栈顶最后两个点构成右转或共线"（不是左转），
   就把栈顶弹出——因为这说明栈顶那个点在凸包内部，不该留着。
3. 再从右到左扫描一遍（等价于把点列反过来再做一次同样的操作），得到"上凸壳"
4. 下凸壳 + 上凸壳（各自去掉重复的首尾点）就是完整的凸包

这个算法本质上和 Graham 扫描是同一个思路（用叉积判断"要不要把上一个点踢出去"），
区别只是排序方式（按坐标排序 vs 按极角排序）——按坐标排序不用处理"极角相同"这类特殊情况，更简单。
```

### 3.2 完整实现

```python
def convex_hull(points: list[tuple[int, int]]) -> list[tuple[int, int]]:
    """Andrew 单调链算法，返回凸包顶点（逆时针顺序）。"""
    points = sorted(set(points))
    if len(points) <= 2:
        return points

    def half_hull(pts: list[tuple[int, int]]) -> list[tuple[int, int]]:
        hull: list[tuple[int, int]] = []
        for p in pts:
            # 只要新点让最后两个点变成"右转或共线"，就说明栈顶那个点不在凸包边界上
            while len(hull) >= 2 and cross(hull[-2], hull[-1], p) <= 0:
                hull.pop()
            hull.append(p)
        return hull

    lower = half_hull(points)          # 下凸壳：从左到右
    upper = half_hull(points[::-1])    # 上凸壳：从右到左
    return lower[:-1] + upper[:-1]     # 首尾点在两条链里各出现一次，去掉重复
```

### 3.3 正确性验证

```python
def is_convex_hull_valid(points: list[tuple[int, int]], hull: list[tuple[int, int]]) -> bool:
    """验证：hull 的每一条边，所有输入点都必须在它的左侧（逆时针凸包的定义）。"""
    if len(hull) < 3:
        return True
    n = len(hull)
    for i in range(n):
        a, b = hull[i], hull[(i + 1) % n]
        for p in points:
            if cross(a, b, p) < 0:
                return False
    return True


random.seed(1)
fail_hull = 0
for _ in range(100):
    n = random.randint(3, 30)
    pts = [(random.randint(0, 20), random.randint(0, 20)) for _ in range(n)]
    hull = convex_hull(pts)
    if not is_convex_hull_valid(pts, hull):
        fail_hull += 1

print(f"凸包有效性验证（所有点都在凸包内侧）：100 次随机测试，不匹配 {fail_hull} 次")
```

---

## 四、最近点对 (Closest Pair of Points)

### 4.1 核心思路：分治

```
暴力做法 O(n²)：两两算距离取最小。分治能做到 O(n log n)：

1. 按 x 坐标排序后，从中间切一刀分成左右两半，各自递归求最近点对
2. 设左右两半分别求出的最近距离是 d，真正的答案要么是 d，
   要么是"一左一右、跨越中线"的一对点，距离比 d 还小
3. 关键剪枝：跨中线的点对，只需要检查"距中线不超过 d"的一个窄条 (strip) 内的点，
   而且可以证明这个窄条按 y 坐标排序后，每个点只需要往后检查最多 7 个点
   （这个条依赖一个平面几何事实：宽为 2d、高为 d 的矩形里最多能塞进 8 个"两两距离 >= d"的点）
   这一步保证了合并两侧结果的复杂度是 O(n)，总递归式 T(n) = 2T(n/2) + O(n) = O(n log n)
```

### 4.2 完整实现

```python
def closest_pair(points: list[tuple[int, int]]) -> tuple[int, tuple | None]:
    """返回 (最近距离的平方, 对应的点对)。用平方避免浮点开方。"""
    pts = sorted(points)

    def dist2(p, q):
        return (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2

    def rec(pts_x):
        n = len(pts_x)
        if n <= 3:
            best, best_pair = float("inf"), None
            for i in range(n):
                for j in range(i + 1, n):
                    d = dist2(pts_x[i], pts_x[j])
                    if d < best:
                        best, best_pair = d, (pts_x[i], pts_x[j])
            return best, best_pair

        mid = n // 2
        midx = pts_x[mid][0]
        d_left, pair_left = rec(pts_x[:mid])
        d_right, pair_right = rec(pts_x[mid:])
        d, best_pair = (d_left, pair_left) if d_left <= d_right else (d_right, pair_right)

        # 只检查距离中线不超过 sqrt(d) 的"窄条"里的点
        strip = [p for p in pts_x if (p[0] - midx) ** 2 < d]
        strip.sort(key=lambda p: p[1])

        for i in range(len(strip)):
            j = i + 1
            while j < len(strip) and (strip[j][1] - strip[i][1]) ** 2 < d:
                dd = dist2(strip[i], strip[j])
                if dd < d:
                    d, best_pair = dd, (strip[i], strip[j])
                j += 1

        return d, best_pair

    return rec(pts)
```

### 4.3 正确性验证

```python
def closest_pair_brute(points: list[tuple[int, int]]) -> tuple[int, tuple | None]:
    n = len(points)
    best, best_pair = float("inf"), None
    for i in range(n):
        for j in range(i + 1, n):
            d = (points[i][0] - points[j][0]) ** 2 + (points[i][1] - points[j][1]) ** 2
            if d < best:
                best, best_pair = d, (points[i], points[j])
    return best, best_pair


random.seed(2)
fail_cp = 0
for _ in range(100):
    n = random.randint(2, 50)
    pts = [(random.randint(-100, 100), random.randint(-100, 100)) for _ in range(n)]
    d1, _ = closest_pair(pts)
    d2, _ = closest_pair_brute(pts)
    if d1 != d2:
        fail_cp += 1

print(f"最近点对分治 vs 暴力枚举：100 次随机测试，不匹配 {fail_cp} 次")
```

---

## 五、复杂度总结

| 问题 | 暴力 | 优化后 | 关键工具 |
|------|------|--------|---------|
| 线段相交 | — | O(1) | 叉积判断左右转 + 共线退化到包围盒检查 |
| 凸包 | O(n³)（枚举每条边判断是否所有点都在同侧） | O(n log n) | 排序 + 叉积单调栈 |
| 最近点对 | O(n²) | O(n log n) | 分治 + "窄条最多检查7个点"的剪枝 |

---

[← 返回索引](index.md)
