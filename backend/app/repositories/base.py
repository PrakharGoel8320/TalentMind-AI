from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.base_class import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, *, obj_in: Any) -> ModelType:
        if hasattr(obj_in, "model_dump"):
            obj_in_data = obj_in.model_dump()
        else:
            obj_in_data = dict(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[Any, Dict[str, Any]],
    ) -> ModelType:
        if hasattr(obj_in, "model_dump"):
            obj_in_data = obj_in.model_dump()
        elif isinstance(obj_in, dict):
            obj_in_data = obj_in
        else:
            obj_in_data = dict(obj_in)
        for c in self.model.__table__.columns:
            if c.name in obj_in_data:
                setattr(db_obj, c.name, obj_in_data[c.name])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).filter(self.model.id == id))
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            await db.commit()
        return obj
