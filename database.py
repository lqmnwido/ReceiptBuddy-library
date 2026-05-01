"""Database connection management with session-per-service isolation."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from contextlib import contextmanager
from typing import Generator


class DatabaseManager:
    """Manages database connections with configurable schema isolation."""

    def __init__(self, database_url: str, pool_size: int = 10, max_overflow: int = 20):
        self.engine = create_engine(
            database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            echo=False,
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_session(self) -> Generator[Session, None, None]:
        """Dependency injection compatible session generator."""
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_all(self, base):
        """Create all tables registered on the given Base."""
        base.metadata.create_all(bind=self.engine)

    def drop_all(self, base):
        """Drop all tables (use with caution)."""
        base.metadata.drop_all(bind=self.engine)


# Create default instances with lazy initialization
_default_database: DatabaseManager = None


def get_database() -> DatabaseManager:
    """Get or create the default database manager."""
    global _default_database
    if _default_database is None:
        from common.config import ServiceSettings
        settings = ServiceSettings()
        _default_database = DatabaseManager(settings.DATABASE_URL, settings.DB_POOL_SIZE, settings.DB_MAX_OVERFLOW)
    return _default_database


def get_db() -> Generator[Session, None, None]:
    """Dependency for FastAPI — yields a database session."""
    db = get_database()
    yield from db.get_session()
