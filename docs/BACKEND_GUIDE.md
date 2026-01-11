# Backend Development Guide: FastAPI & Microservices

后端采用分布式的异步微服务架构，基于 FastAPI 打造高性能的 API 服务。

## 🏗 Microservices Overview

每个服务都位于 `ainav-backend/services/` 下，共用 `shared/` 模块。

| Service              | Path                     | Purpose                  |
| -------------------- | ------------------------ | ------------------------ |
| `content-service`    | `.../content-service`    | 元数据、分类、工具管理。 |
| `search-service`     | `.../search-service`     | Meilisearch 检索。       |
| `user-service`       | `.../user-service`       | 用户、安全、鉴权。       |
| `automation-service` | `.../automation-service` | 爬虫、异步任务引擎。     |
| `agent-service`      | `.../agent-service`      | LangGraph 编排与执行。   |

## 🛠 Shared Layer (`shared/`)

为了代码复用，我们将核心模型和工具放在共享层：

- `models.py`: 全局数据库模型。
- `database.py`: 数据库连接配置。
- `config.py`: 环境配置与 Pydantic 设置。

## 🚀 API Development Pattern

### 1. Schema 定义 (Pydantic)

在服务的 `schemas/` 目录定义数据模型。

```python
class ToolCreate(BaseModel):
    name: str
    name_zh: Optional[str]
```

### 2. Router 注册

每个服务在 `app/routers/` 编写功能模块。

```python
@router.post("/")
async def create_tool(tool: ToolCreate, db: AsyncSession = Depends(get_db)):
    ...
```

### 3. Database Migration (Alembic)

变更数据库结构时：

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## ⚙️ Background Tasks (Celery)

长耗时任务（如截图生成、权重计算）应发送给 Celery：

```python
# automation-service/app/workers/tasks.py
@shared_task
def sync_github_stats(tool_id: str):
    ...
```

## 🔍 Search Integration

- 数据写入 PostgreSQL 后，对应的 Worker 会将变更推送到 Meilisearch。
- 向量搜索利用 `pgvector` 进行高效相似度匹配。

---

_Last Updated: 2026-01-09_
