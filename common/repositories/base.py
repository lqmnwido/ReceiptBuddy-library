"""Generic repository pattern with CRUD operations for any model."""
from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func

from common.models.base import Base
from common.exceptions import NotFoundException, ConflictException

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic CRUD repository with common query patterns."""

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    # ─── CREATE ────────────────────────────────────

    def create(self, **kwargs) -> ModelType:
        """Create a new record."""
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def create_from_schema(self, schema, exclude_unset: bool = False) -> ModelType:
        """Create from a Pydantic schema."""
        data = schema.model_dump(exclude_unset=exclude_unset)
        return self.create(**data)

    def bulk_create(self, items: List[Dict[str, Any]]) -> List[ModelType]:
        """Create multiple records in bulk."""
        instances = [self.model(**item) for item in items]
        self.db.add_all(instances)
        self.db.commit()
        for instance in instances:
            self.db.refresh(instance)
        return instances

    # ─── READ ──────────────────────────────────────

    def get(self, id: int) -> Optional[ModelType]:
        """Get by primary key."""
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_or_404(self, id: int) -> ModelType:
        """Get by primary key or raise NotFoundException."""
        instance = self.get(id)
        if instance is None:
            raise NotFoundException(f"{self.model.__name__} with id {id} not found")
        return instance

    def get_by(self, **kwargs) -> Optional[ModelType]:
        """Get first record matching filters."""
        return self.db.query(self.model).filter_by(**kwargs).first()

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None,
        descending: bool = False,
        **filters,
    ) -> List[ModelType]:
        """List records with pagination and optional filters."""
        query = self.db.query(self.model).filter_by(**filters)
        if order_by:
            column = getattr(self.model, order_by, None)
            if column is not None:
                query = query.order_by(column.desc() if descending else column)
        return query.offset(skip).limit(limit).all()

    def count(self, **filters) -> int:
        """Count records matching optional filters."""
        return self.db.query(self.model).filter_by(**filters).count()

    def exists(self, **kwargs) -> bool:
        """Check if a record exists matching the given filters."""
        return self.db.query(self.model).filter_by(**kwargs).first() is not None

    # ─── UPDATE ────────────────────────────────────

    def update(self, id: int, **kwargs) -> ModelType:
        """Update a record by id."""
        instance = self.get_or_404(id)
        for key, value in kwargs.items():
            if value is not None:  # Don't overwrite with None unless explicit
                setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def update_from_schema(self, id: int, schema, exclude_unset: bool = True) -> ModelType:
        """Update from a Pydantic schema, only setting provided fields."""
        data = schema.model_dump(exclude_unset=exclude_unset)
        return self.update(id, **data)

    # ─── DELETE ────────────────────────────────────

    def delete(self, id: int) -> bool:
        """Hard delete by id."""
        instance = self.get_or_404(id)
        self.db.delete(instance)
        self.db.commit()
        return True

    def delete_by(self, **kwargs) -> int:
        """Delete all records matching filters. Returns count deleted."""
        deleted = self.db.query(self.model).filter_by(**kwargs).delete()
        self.db.commit()
        return deleted
