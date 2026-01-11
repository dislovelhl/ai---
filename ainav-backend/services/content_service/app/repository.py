from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update
from shared.models import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        query = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_id(self, id: any) -> Optional[T]:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[T]:
        query = select(self.model).where(self.model.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> T:
        db_obj = self.model(**kwargs)
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, id: any, **kwargs) -> Optional[T]:
        query = update(self.model).where(self.model.id == id).values(**kwargs).returning(self.model)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one_or_none()

    async def delete(self, id: any) -> bool:
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

from shared.models import Category, Scenario, Tool, tool_scenarios, LearningPath, LearningPathModule

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession):
        super().__init__(Category, session)

class ScenarioRepository(BaseRepository[Scenario]):
    def __init__(self, session: AsyncSession):
        super().__init__(Scenario, session)

class ToolRepository(BaseRepository[Tool]):
    def __init__(self, session: AsyncSession):
        super().__init__(Tool, session)

    async def create_with_relations(self, scenario_ids: List[any] = None, **kwargs) -> Tool:
        # Resolve scenarios first
        scenarios = []
        if scenario_ids:
            scen_query = select(Scenario).where(Scenario.id.in_(scenario_ids))
            result = await self.session.execute(scen_query)
            scenarios = list(result.scalars().all())

        tool = Tool(**kwargs)
        tool.scenarios = scenarios
        self.session.add(tool)
        await self.session.commit()
        
        # Capture ID safely
        tool_id = tool.id
        return await self.get_by_id_with_relations(tool_id)
    
    async def get_by_id_with_relations(self, id: any) -> Optional[Tool]:
        from sqlalchemy.orm import joinedload
        query = select(self.model).options(
            joinedload(self.model.category),
            joinedload(self.model.scenarios)
        ).where(self.model.id == id).execution_options(populate_existing=True)
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_all_with_relations(self, skip: int = 0, limit: int = 100) -> List[Tool]:
        from sqlalchemy.orm import selectinload
        query = select(self.model).options(
            selectinload(self.model.category),
            selectinload(self.model.scenarios)
        ).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_slug_with_relations(self, slug: str) -> Optional[Tool]:
        from sqlalchemy.orm import selectinload
        query = select(self.model).options(
            selectinload(self.model.category),
            selectinload(self.model.scenarios)
        ).where(self.model.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def associate_scenarios(self, tool_id: any, scenario_ids: List[any]):
        # Fetch the tool with scenarios properly using existing method
        tool = await self.get_by_id_with_relations(tool_id)
        if not tool:
            return

        if scenario_ids is not None:
            # Fetch scenarios
            scen_query = select(Scenario).where(Scenario.id.in_(scenario_ids))
            result = await self.session.execute(scen_query)
            # Match scenarios to tool
            tool.scenarios = list(result.scalars().all())
            await self.session.commit()
            await self.session.refresh(tool)

class LearningPathRepository(BaseRepository[LearningPath]):
    def __init__(self, session: AsyncSession):
        super().__init__(LearningPath, session)

    async def get_all_with_relations(self, skip: int = 0, limit: int = 100) -> List[LearningPath]:
        from sqlalchemy.orm import selectinload
        query = select(self.model).options(
            selectinload(self.model.modules),
            selectinload(self.model.recommended_tools)
        ).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_slug_with_modules_and_tools(self, slug: str) -> Optional[LearningPath]:
        from sqlalchemy.orm import selectinload
        query = select(self.model).options(
            selectinload(self.model.modules),
            selectinload(self.model.recommended_tools)
        ).where(self.model.slug == slug)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_with_relations(self, tool_ids: List[any] = None, **kwargs) -> LearningPath:
        # Resolve tools first
        tools = []
        if tool_ids:
            tools_query = select(Tool).where(Tool.id.in_(tool_ids))
            result = await self.session.execute(tools_query)
            tools = list(result.scalars().all())

        learning_path = LearningPath(**kwargs)
        learning_path.recommended_tools = tools
        self.session.add(learning_path)
        await self.session.commit()

        # Capture ID safely
        path_id = learning_path.id
        return await self.get_by_id_with_relations(path_id)

    async def get_by_id_with_relations(self, id: any) -> Optional[LearningPath]:
        from sqlalchemy.orm import selectinload
        query = select(self.model).options(
            selectinload(self.model.modules),
            selectinload(self.model.recommended_tools)
        ).where(self.model.id == id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def associate_tools(self, learning_path_id: any, tool_ids: List[any]):
        # Fetch the learning path with tools properly using existing method
        learning_path = await self.get_by_id_with_relations(learning_path_id)
        if not learning_path:
            return

        if tool_ids is not None:
            # Fetch tools
            tools_query = select(Tool).where(Tool.id.in_(tool_ids))
            result = await self.session.execute(tools_query)
            # Match tools to learning path
            learning_path.recommended_tools = list(result.scalars().all())
            await self.session.commit()
            await self.session.refresh(learning_path)

    async def get_published_paths(self, skip: int = 0, limit: int = 100) -> List[LearningPath]:
        from sqlalchemy.orm import selectinload
        query = select(self.model).options(
            selectinload(self.model.modules),
            selectinload(self.model.recommended_tools)
        ).where(self.model.is_published == True).offset(skip).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

class LearningPathModuleRepository(BaseRepository[LearningPathModule]):
    def __init__(self, session: AsyncSession):
        super().__init__(LearningPathModule, session)

    async def get_by_learning_path_id(self, learning_path_id: any) -> List[LearningPathModule]:
        """Get all modules for a specific learning path, ordered by order field"""
        from sqlalchemy import asc
        query = select(self.model).where(
            self.model.learning_path_id == learning_path_id
        ).order_by(asc(self.model.order))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def reorder_modules(self, module_orders: List[dict]) -> bool:
        """
        Update the order of multiple modules.
        module_orders: List of dicts with 'id' and 'order' keys
        Example: [{"id": "uuid1", "order": 1}, {"id": "uuid2", "order": 2}]
        """
        try:
            for item in module_orders:
                module_id = item.get("id")
                new_order = item.get("order")
                if module_id and new_order is not None:
                    await self.update(module_id, order=new_order)
            return True
        except Exception:
            return False
