"""Base model classes with timestamping, soft delete, and common columns."""
from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, func
from sqlalchemy.orm import declarative_base, declared_attr

Base = declarative_base()


class TimestampedBase(Base):
    """Abstract base model with id, created_at, and updated_at."""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"


class SoftDeleteMixin:
    """Adds is_deleted and deleted_at columns for soft deletes."""

    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
