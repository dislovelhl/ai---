from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import UUID4
from typing import List
from ..dependencies import get_db
from ..repository import CategoryRepository
from ..schemas import CategoryRead, CategoryCreate, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])

@router.get("/", response_model=List[CategoryRead])
async def list_categories(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    repo = CategoryRepository(db)
    return await repo.get_all(skip=skip, limit=limit)

@router.get("/{slug}", response_model=CategoryRead)
async def get_category(slug: str, db: AsyncSession = Depends(get_db)):
    repo = CategoryRepository(db)
    category = await repo.get_by_slug(slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.post("/", response_model=CategoryRead)
async def create_category(category_in: CategoryCreate, db: AsyncSession = Depends(get_db)):
    repo = CategoryRepository(db)
    existing = await repo.get_by_slug(category_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")
    return await repo.create(**category_in.model_dump())

@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(category_id: UUID4, category_in: CategoryCreate, db: AsyncSession = Depends(get_db)):
    repo = CategoryRepository(db)
    category = await repo.update(category_id, **category_in.model_dump())
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.delete("/{category_id}")
async def delete_category(category_id: UUID4, db: AsyncSession = Depends(get_db)):
    repo = CategoryRepository(db)
    success = await repo.delete(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
