# RESTful 架构与 API 设计 · RESTful Design

> REST = **表现层状态转化**。资源用 URI 标识，用表现层传递，用 HTTP 动词完成状态变化——再落到一套可落地的 API 约定。

---

## 一、REST 从哪来

Roy Fielding 在 2000 年博士论文提出 REST（Representational State Transfer）。他是 HTTP/1.x 重要设计者之一；REST 是对**网络化应用架构约束**的总结，而非某个具体框架。

互联网软件特点：C/S、分布式、高延迟、高并发。RESTful 因结构清晰、贴近 Web 标准而流行。

---

## 二、三要素：资源 · 表现层 · 状态转化

名称「表现层状态转化」省略了主语——主语是**资源**。

### 2.1 资源 (Resources)

网络上的实体/信息：一段文本、一张图、一种服务……  
每个资源用 **URI** 唯一标识；「上网」即与一系列资源互动。

### 2.2 表现层 (Representation)

资源可有多种外在形式：JSON / XML / HTML / 二进制等。  
**URI 标识资源本身，不标识表现形式。**  
形式应由请求/响应头中的 `Accept`、`Content-Type` 等描述（严格 REST 视角下，URI 末尾 `.html` 并不必要）。

### 2.3 状态转化 (State Transfer)

HTTP 无状态；状态在服务器。客户端通过 HTTP 动词触发服务器**状态变化**，且变化建立在表现层之上 → 表现层状态转化。

常用动词直觉：

| 动词 | 作用 |
|------|------|
| GET | 获取 |
| POST | 新建（亦有人用于更新，但不推荐混淆） |
| PUT | 更新（完整替换语义常见） |
| DELETE | 删除 |

### 2.4 一句话定义 RESTful

1. 每个 URI 代表一种资源  
2. 传递的是该资源的某种表现层  
3. 用 HTTP 动词操作资源，完成表现层状态转化  

---

## 三、常见误区：URI 里不要放动词

资源是名词实体，**动词应体现在 HTTP 方法上**。

```
❌  GET /posts/show/1
✅  GET /posts/1

❌  POST /accounts/1/transfer/500/to/2
✅  POST /transactions
    Body: from=1&to=2&amount=500.00
```

转账这类动作：把「动词」建模成**名词资源**（如 transaction），用 POST 创建一次交易。

---

## 四、API 设计指南精华

以下对齐《RESTful API 设计指南》，偏工程落地。

### 4.1 协议与域名

- 通信使用 **HTTPS**  
- API 尽量独立域名：`https://api.example.com`  
- 极简时可：`https://example.org/api/`

### 4.2 路径：复数名词

路径表示资源集合，名词常用**复数**（常对应表/集合）：

```
https://api.example.com/v1/zoos
https://api.example.com/v1/animals
https://api.example.com/v1/employees
```

### 4.3 HTTP 动词对照

| 动词 | 近似 SQL | 含义 |
|------|----------|------|
| GET | SELECT | 取资源（一项或多项） |
| POST | CREATE | 新建 |
| PUT | UPDATE | 更新（客户端给完整资源） |
| PATCH | UPDATE | 更新（只给变更字段） |
| DELETE | DELETE | 删除 |
| HEAD | — | 取元数据 |
| OPTIONS | — | 探测允许的操作 |

示例：

```
GET    /zoos
POST   /zoos
GET    /zoos/{id}
PUT    /zoos/{id}
PATCH  /zoos/{id}
DELETE /zoos/{id}
GET    /zoos/{id}/animals
DELETE /zoos/{id}/animals/{aid}
```

### 4.4 过滤与分页参数

| 参数例 | 含义 |
|--------|------|
| `?limit=10` | 返回条数 |
| `?offset=10` | 起始偏移 |
| `?page=2&per_page=100` | 页码分页 |
| `?sortby=name&order=asc` | 排序 |
| `?animal_type_id=1` | 过滤条件 |

允许适度冗余：`GET /zoos/{id}/animals` 与 `GET /animals?zoo_id={id}` 可并存。

### 4.5 状态码（常用）

| 码 | 场景 |
|----|------|
| 200 OK | GET 成功（幂等） |
| 201 Created | POST/PUT/PATCH 创建或修改成功 |
| 202 Accepted | 已接受，异步排队 |
| 204 No Content | DELETE 成功 |
| 400 | 请求错误，未修改 |
| 401 | 未认证 |
| 403 | 已认证但禁止 |
| 404 | 资源不存在 |
| 406 | 不可接受的格式 |
| 410 Gone | 永久删除且不再有 |
| 422 | 校验失败 |
| 500 | 服务器错误 |

### 4.6 错误体

4xx 时返回明确错误信息，常见形态：

```json
{ "error": "Invalid API key" }
```

### 4.7 返回结果约定

| 操作 | 返回 |
|------|------|
| GET /collection | 列表（数组） |
| GET /collection/id | 单个对象 |
| POST /collection | 新建出的对象 |
| PUT/PATCH .../id | 完整对象 |
| DELETE .../id | 空文档（配合 204） |

### 4.8 其他实践

- 认证优先考虑 **OAuth 2.0**（指南建议）  
- 响应格式优先 **JSON**  

---

## 五、HATEOAS（Hypermedia）

理想 RESTful API 在响应中带**链接**，引导下一步可调用的操作（HATEOAS）。客户端少硬编码 URL。

```json
{
  "link": {
    "rel": "collection https://www.example.com/zoos",
    "href": "https://api.example.com/zoos",
    "title": "List of zoos",
    "type": "application/vnd.yourformat+json"
  }
}
```

GitHub API 根资源返回大量 `*_url` 即此思想的工程化版本。现实中完整 HATEOAS 成本高，团队常折中：关键关联给链接，其余靠文档。

---

## 六、版本号争议：Accept 头 vs URL

版本号有两种主流取向，需要显式做 tradeoff：

| 取向 | 做法 |
|------|------|
| 更「纯」REST | 版本是同资源的不同表现 → 用 `Accept` 头区分，URI 不掺版本 |
| 更工程便利 | 版本放进 URL：`/v1/`，直观、易调试；头方案不如 URL 方便 |

```
# 纯 REST 风格（Accept 头）
Accept: application/vnd.example.foo+json; version=1.0

# URL 版本风格——业界更常见
https://api.example.com/v1/zoos
```

**如何选：**

| 维度 | URL `/v1/` | Accept 头 |
|------|------------|-----------|
| 可见性 / 调试 | 高 | 低 |
| 缓存与网关 | 简单 | 要正确处理 Vary 等 |
| REST 纯度 | 较低 | 较高 |
| 团队习惯 | 多数公开 API | 少数严格场景 |

实战建议：对外 API 多用 URL 版本；同时保持资源名词化与动词在 HTTP 上。接受「纯度 vs 可用性」的权衡，并在团队规范里写死一种。

---

## 七、Python 路由示意（非框架绑定）

```python
# 仅示意「复数名词 + 动词在方法上」，非完整 Web 框架代码
ROUTES = {
    ("GET", "/zoos"): "list_zoos",
    ("POST", "/zoos"): "create_zoo",
    ("GET", "/zoos/{id}"): "get_zoo",
    ("PATCH", "/zoos/{id}"): "patch_zoo",
    ("DELETE", "/zoos/{id}"): "delete_zoo",
}
```

---

## 八、口诀

> **URI 名词动词在方法，表现用头状态靠动词；**  
> **版本 URL 易落地，HATEOAS 量力而行。**

---


[← 返回索引](index.md)
