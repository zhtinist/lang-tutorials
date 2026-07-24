# 案例：图书管理系统 · Library Management

> 借还书 + 会员上限 + 目录搜索。变化轴：**搜索策略、通知方式、借阅规则**；Library 编排，Catalog / Loan 管数据。

去图书馆借书就是这么回事：一本书可能有好几本副本在架上，你借走一本，架上的库存就少一本；每个人能同时借的本数有上限，超期还可能要交罚款。这一案例就是把"借、还、搜、限额"这套日常流程建成模型。

---

## 一、澄清需求

| 项目 | MVP |
|------|-----|
| 角色 | 会员、图书管理员（管理员可登记书） |
| 书 | ISBN 逻辑书 + 多本馆藏副本 `BookItem` |
| 借阅 | 有上限与期限；逾期可罚款（先接口占位） |
| 搜索 | 按书名 / ISBN |
| 运行 | 单机内存 |
| 暂缓 | 预约队列、多馆互借、支付 |

### 用例

1. 添加书目与副本  
2. `borrow(member_id, barcode)`  
3. `return_item(barcode)`  
4. `search(query)`

---

## 二、实体

| 名词 | 类 | 说明 |
|------|-----|------|
| 图书馆 | `Library` | Facade |
| 会员 | `Member` | 借阅上限 |
| 书目 | `Book` | ISBN、书名、作者 |
| 副本 | `BookItem` | 条码、状态 |
| 借阅记录 | `Loan` | 会员、副本、到期日 |
| 目录 | `Catalog` | 索引与搜索 |

变化轴：搜索算法、逾期策略、通知（邮件/短信）→ 接口。

---

## 三、类图

```
Library ◆── Catalog
Library ◆── members: Map
Catalog ──○ Book (isbn)
Book ◇── BookItem
Member ◇── active_loans: Loan
Loan ----> BookItem
Loan ----> Member

SearchStrategy <<interface>>
 Catalog 依赖 SearchStrategy（可选）
```

状态：`BookItemStatus = AVAILABLE | LOANED | LOST`

如果不把搜索规则抽成 `SearchStrategy`，`Catalog.search` 内部就要直接写死"`query.lower() in title.lower()`"这一种匹配方式；以后想支持按作者搜索、或者支持更宽松的模糊匹配，就得改这个已经在被"借书页面搜索"和"管理员后台搜索"两处调用的同一个方法，稍有不慎就会把原本按书名搜索的用户体验也改坏。`SearchStrategy` 让 `search` 方法本身保持不变，只需要传入不同的匹配策略。

---

## 四、代码骨架

```python
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from enum import Enum, auto
from typing import Protocol
from uuid import uuid4


class BookItemStatus(Enum):
    AVAILABLE = auto()
    LOANED = auto()
    LOST = auto()


@dataclass
class Book:
    isbn: str
    title: str
    authors: list[str]


@dataclass
class BookItem:
    barcode: str
    book: Book
    status: BookItemStatus = BookItemStatus.AVAILABLE


@dataclass
class Member:
    member_id: str
    name: str
    max_loans: int = 5
    active_loan_ids: list[str] = field(default_factory=list)

    def can_borrow(self) -> bool:
        return len(self.active_loan_ids) < self.max_loans


@dataclass
class Loan:
    loan_id: str
    member_id: str
    barcode: str
    borrowed_on: date
    due_on: date
    returned_on: date | None = None


class SearchStrategy(Protocol):
    def match(self, book: Book, query: str) -> bool: ...


class TitleSearch:
    def match(self, book: Book, query: str) -> bool:
        return query.lower() in book.title.lower()


class Catalog:
    def __init__(self) -> None:
        self._books: dict[str, Book] = {}
        self._items: dict[str, BookItem] = {}

    def add_book(self, book: Book) -> None:
        self._books[book.isbn] = book

    def add_item(self, item: BookItem) -> None:
        if item.book.isbn not in self._books:
            self.add_book(item.book)
        self._items[item.barcode] = item

    def get_item(self, barcode: str) -> BookItem:
        return self._items[barcode]

    def search(self, query: str, strategy: SearchStrategy | None = None) -> list[Book]:
        strategy = strategy or TitleSearch()
        return [b for b in self._books.values() if strategy.match(b, query)]


class Library:
    """图书系统门面。"""

    def __init__(self, catalog: Catalog, loan_days: int = 14) -> None:
        self._catalog = catalog
        self._members: dict[str, Member] = {}
        self._loans: dict[str, Loan] = {}
        self._loan_days = loan_days

    def register_member(self, name: str, max_loans: int = 5) -> Member:
        m = Member(str(uuid4()), name, max_loans)
        self._members[m.member_id] = m
        return m

    def borrow(self, member_id: str, barcode: str, today: date | None = None) -> Loan:
        today = today or date.today()
        member = self._members[member_id]
        item = self._catalog.get_item(barcode)

        if not member.can_borrow():
            raise RuntimeError("已达借阅上限")
        if item.status is not BookItemStatus.AVAILABLE:
            raise RuntimeError("该书不可借")

        item.status = BookItemStatus.LOANED
        loan = Loan(
            loan_id=str(uuid4()),
            member_id=member_id,
            barcode=barcode,
            borrowed_on=today,
            due_on=today + timedelta(days=self._loan_days),
        )
        self._loans[loan.loan_id] = loan
        member.active_loan_ids.append(loan.loan_id)
        return loan

    def return_item(self, barcode: str, today: date | None = None) -> Loan:
        today = today or date.today()
        loan = self._find_active_loan(barcode)
        item = self._catalog.get_item(barcode)
        item.status = BookItemStatus.AVAILABLE
        loan.returned_on = today
        member = self._members[loan.member_id]
        member.active_loan_ids.remove(loan.loan_id)
        return loan

    def _find_active_loan(self, barcode: str) -> Loan:
        for loan in self._loans.values():
            if loan.barcode == barcode and loan.returned_on is None:
                return loan
        raise KeyError("无对应借阅记录")

    def search(self, query: str) -> list[Book]:
        return self._catalog.search(query)
```

---

## 五、异常与扩展

| 场景 | 处理 |
|------|------|
| 超上限 | `can_borrow` 拦截 |
| 书已借出 | 状态检查 |
| 归还未借出条码 | `_find_active_loan` 失败 |
| 逾期罚款 | `FinePolicy.calculate(loan, today)` |
| 预约 | `ReservationQueue` + Observer 通知 |

```python
class FinePolicy(Protocol):
    def calculate(self, loan: Loan, today: date) -> float: ...


class DailyFine:
    def __init__(self, per_day: float = 1.0) -> None:
        self._per_day = per_day

    def calculate(self, loan: Loan, today: date) -> float:
        if today <= loan.due_on:
            return 0.0
        return (today - loan.due_on).days * self._per_day
```

并发：对同一 `BookItem` 借还加锁；或条码级锁。

---

## 六、与停车场对比（加深框架）

| | 停车场 | 图书馆 |
|--|--------|--------|
| 资源 | Spot | BookItem |
| 会话 | Ticket | Loan |
| 策略 | Fee | Search / Fine |
| 约束 | 车型匹配 | 借阅上限 |

**口诀**：资源有状态，会话连用户；规则走策略。

---

## 参考与延伸

- 搜索用 Strategy；通知可用 Observer（见行为型篇）。
- 完整五步见 [lld-framework.md](lld-framework.md)。

下一篇：[案例：限流器](case-rate-limiter.md)

---

[← 返回索引](index.md)
