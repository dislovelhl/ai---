---
name: backend-dev-enhanced
description: Enhanced backend development skill with chain-of-thought reasoning
version: "2.0.0"
triggers:
  - "backend"
  - "api"
  - "fastapi"
  - "python"
  - "database"
supersedes: backend-dev
---

# Backend Development Skill (Enhanced)

Enhanced backend development with structured reasoning and self-verification.

## Chain-of-Thought Protocol

Before ANY backend code generation or modification:

```markdown
### Step 1: Understand the Context
- What is the business requirement?
- What existing endpoints/services are related?
- What database models are involved?

### Step 2: Design the Solution
- What's the API contract (request/response)?
- What service layer logic is needed?
- What database queries are required?
- What error cases need handling?

### Step 3: Verify the Approach
- Does this follow existing patterns in the codebase?
- Are there security considerations?
- What about performance implications?

### Step 4: Implement with Checkpoints
- Write schema first, validate structure
- Write service logic, verify business rules
- Write router, check endpoint conventions
- Write tests, confirm coverage
```

## Few-Shot Examples

### Example 1: Adding a New API Endpoint (GOOD)

**Request:** "Add an endpoint to get tools by category with pagination"

**Reasoning Process:**
```
1. UNDERSTAND: Need a paginated list endpoint filtering by category
2. CHECK EXISTING: Look at /v1/tools/ endpoint for pagination pattern
3. DESIGN:
   - Input: category_id (path), page/size (query)
   - Output: PaginatedResponse[Tool] with total count
4. IMPLEMENTATION ORDER: Schema → Service → Router → Tests
```

**Implementation:**

```python
# 1. Schema (ainav-backend/services/content_service/app/schemas.py)
from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List
from uuid import UUID

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

class ToolListParams(BaseModel):
    """Query parameters for tool listing"""
    page: int = Field(default=1, ge=1, description="页码")
    size: int = Field(default=20, ge=1, le=100, description="每页数量")


# 2. Service (ainav-backend/services/content_service/app/services/tool_service.py)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

class ToolService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_category(
        self,
        category_id: UUID,
        page: int = 1,
        size: int = 20
    ) -> PaginatedResponse[ToolResponse]:
        """
        Get tools by category with pagination.

        按分类获取工具列表（分页）
        """
        # Count total
        count_stmt = (
            select(func.count())
            .select_from(Tool)
            .where(Tool.category_id == category_id)
        )
        total = (await self.db.execute(count_stmt)).scalar() or 0

        # Get page
        offset = (page - 1) * size
        stmt = (
            select(Tool)
            .where(Tool.category_id == category_id)
            .order_by(Tool.created_at.desc())
            .offset(offset)
            .limit(size)
        )
        result = await self.db.execute(stmt)
        tools = result.scalars().all()

        return PaginatedResponse(
            items=[ToolResponse.model_validate(t) for t in tools],
            total=total,
            page=page,
            size=size,
            pages=(total + size - 1) // size
        )


# 3. Router (ainav-backend/services/content_service/app/routers/categories.py)
from fastapi import APIRouter, Depends, Path, Query
from uuid import UUID

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get(
    "/{category_id}/tools",
    response_model=PaginatedResponse[ToolResponse],
    summary="获取分类下的工具",
    description="Get paginated tools for a specific category"
)
async def get_category_tools(
    category_id: UUID = Path(..., description="分类ID"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
):
    """Get tools belonging to a category with pagination."""
    service = ToolService(db)
    return await service.get_by_category(category_id, page, size)
```

**Why this is GOOD:**
- Follows existing pagination pattern
- Uses proper type hints
- Has Chinese + English documentation
- Validates input parameters
- Uses async/await correctly

---

### Example 2: Adding Database Query (BAD → GOOD)

**Request:** "Add a method to find tools by name search"

**BAD Implementation:**
```python
# DON'T DO THIS
async def search_tools(self, query: str):
    # SQL injection vulnerability!
    sql = f"SELECT * FROM tools WHERE name LIKE '%{query}%'"
    result = await self.db.execute(text(sql))
    return result.fetchall()
```

**Why it's BAD:**
- SQL injection vulnerability
- No type hints
- No pagination
- Returns raw rows instead of models

**GOOD Implementation:**
```python
async def search_tools(
    self,
    query: str,
    page: int = 1,
    size: int = 20
) -> PaginatedResponse[ToolResponse]:
    """
    Search tools by name (Chinese and English).

    搜索工具（支持中英文名称模糊匹配）
    """
    # Parameterized query - safe from injection
    search_pattern = f"%{query}%"

    count_stmt = (
        select(func.count())
        .select_from(Tool)
        .where(
            or_(
                Tool.name.ilike(search_pattern),
                Tool.name_zh.ilike(search_pattern)
            )
        )
    )
    total = (await self.db.execute(count_stmt)).scalar() or 0

    stmt = (
        select(Tool)
        .where(
            or_(
                Tool.name.ilike(search_pattern),
                Tool.name_zh.ilike(search_pattern)
            )
        )
        .order_by(Tool.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
    )
    result = await self.db.execute(stmt)
    tools = result.scalars().all()

    return PaginatedResponse(
        items=[ToolResponse.model_validate(t) for t in tools],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )
```

---

## Service Structure Patterns

### Standard Service Class

```python
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime, timezone

class BaseService:
    """Base service with common CRUD operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def _commit_and_refresh(self, obj):
        """Commit transaction and refresh object."""
        await self.db.commit()
        await self.db.refresh(obj)
        return obj


class ToolService(BaseService):
    """Tool management service. 工具管理服务"""

    async def get_by_id(self, tool_id: UUID) -> Optional[Tool]:
        """Get a single tool by ID."""
        stmt = select(Tool).where(Tool.id == tool_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, data: ToolCreate) -> Tool:
        """Create a new tool."""
        tool = Tool(
            **data.model_dump(),
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(tool)
        return await self._commit_and_refresh(tool)

    async def update(
        self,
        tool_id: UUID,
        data: ToolUpdate
    ) -> Optional[Tool]:
        """Update an existing tool."""
        tool = await self.get_by_id(tool_id)
        if not tool:
            return None

        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.now(timezone.utc)

        for field, value in update_data.items():
            setattr(tool, field, value)

        return await self._commit_and_refresh(tool)

    async def delete(self, tool_id: UUID) -> bool:
        """Soft delete a tool."""
        stmt = (
            update(Tool)
            .where(Tool.id == tool_id)
            .values(
                is_deleted=True,
                deleted_at=datetime.now(timezone.utc)
            )
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0
```

## Error Handling Patterns

```python
from fastapi import HTTPException, status

# Custom exceptions
class ToolNotFoundError(Exception):
    """Tool not found in database."""
    pass

class DuplicateToolError(Exception):
    """Tool with same URL already exists."""
    pass


# Service with proper error handling
class ToolService(BaseService):
    async def get_or_raise(self, tool_id: UUID) -> Tool:
        """Get tool or raise 404."""
        tool = await self.get_by_id(tool_id)
        if not tool:
            raise ToolNotFoundError(f"Tool {tool_id} not found")
        return tool

    async def create(self, data: ToolCreate) -> Tool:
        """Create tool with duplicate check."""
        # Check for existing
        existing = await self._get_by_url(data.url)
        if existing:
            raise DuplicateToolError(f"Tool with URL {data.url} exists")

        # Create new
        tool = Tool(**data.model_dump())
        self.db.add(tool)
        return await self._commit_and_refresh(tool)


# Router with exception handling
@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific tool by ID. 根据ID获取工具详情"""
    try:
        service = ToolService(db)
        return await service.get_or_raise(tool_id)
    except ToolNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": "工具不存在", "message_en": "Tool not found"}
        )
```

## Verification Checklist

Before submitting backend code:

```yaml
pre_submit_checks:
  - [ ] All functions have type hints
  - [ ] Public functions have docstrings (Chinese + English)
  - [ ] Database queries use parameterized values
  - [ ] Error cases are handled explicitly
  - [ ] Async/await is used correctly for I/O
  - [ ] No N+1 query patterns
  - [ ] datetime.now(timezone.utc) used, not utcnow()
  - [ ] Responses follow existing patterns
  - [ ] Input is validated via Pydantic
  - [ ] Sensitive data not logged
```

## Common Mistakes to Avoid

1. **Forgetting async context:**
   ```python
   # BAD: Calling sync function in async context
   await db.commit()  # Wrong if db is sync session

   # GOOD: Use async session methods
   await self.db.commit()
   ```

2. **Missing error handling:**
   ```python
   # BAD: No handling for missing data
   tool = (await self.db.execute(stmt)).scalar_one()  # Raises if missing

   # GOOD: Handle missing gracefully
   tool = (await self.db.execute(stmt)).scalar_one_or_none()
   if not tool:
       raise ToolNotFoundError(...)
   ```

3. **Hardcoded values:**
   ```python
   # BAD
   limit = 100

   # GOOD
   from app.core.config import settings
   limit = settings.MAX_PAGE_SIZE
   ```
