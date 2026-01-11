from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4
from typing import List
from ..dependencies import get_db
from ..repository import LearningPathRepository
from ..schemas import LearningPathRead, LearningPathCreate, LearningPathUpdate

router = APIRouter(prefix="/learning-paths", tags=["learning-paths"])

@router.get("/", response_model=List[LearningPathRead])
async def list_learning_paths(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """List all published learning paths with modules and recommended tools."""
    repo = LearningPathRepository(db)
    return await repo.get_published_paths(skip=skip, limit=limit)

@router.get("/{slug}", response_model=LearningPathRead)
async def get_learning_path(slug: str, db: AsyncSession = Depends(get_db)):
    """Get a learning path by slug with modules and recommended tools."""
    repo = LearningPathRepository(db)
    learning_path = await repo.get_by_slug_with_modules_and_tools(slug)
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return learning_path

@router.post("/", response_model=LearningPathRead)
async def create_learning_path(learning_path_in: LearningPathCreate, db: AsyncSession = Depends(get_db)):
    """Create a new learning path with tool associations (admin only)."""
    repo = LearningPathRepository(db)
    existing = await repo.get_by_slug(learning_path_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    dict_data = learning_path_in.model_dump()
    tool_ids = dict_data.pop("tool_ids", [])

    return await repo.create_with_relations(tool_ids=tool_ids, **dict_data)

@router.put("/{learning_path_id}", response_model=LearningPathRead)
async def update_learning_path(learning_path_id: UUID4, learning_path_in: LearningPathUpdate, db: AsyncSession = Depends(get_db)):
    """Update a learning path and its tool associations (admin only)."""
    repo = LearningPathRepository(db)

    update_data = learning_path_in.model_dump(exclude_unset=True)
    tool_ids = update_data.pop("tool_ids", None)

    learning_path = await repo.update(learning_path_id, **update_data)
    if not learning_path:
        raise HTTPException(status_code=404, detail="Learning path not found")

    if tool_ids is not None:
        await repo.associate_tools(learning_path_id, tool_ids)

    return await repo.get_by_id_with_relations(learning_path_id)

@router.delete("/{learning_path_id}")
async def delete_learning_path(learning_path_id: UUID4, db: AsyncSession = Depends(get_db)):
    """Delete a learning path (admin only)."""
    repo = LearningPathRepository(db)
    success = await repo.delete(learning_path_id)
    if not success:
        raise HTTPException(status_code=404, detail="Learning path not found")
    return {"message": "Learning path deleted successfully"}
