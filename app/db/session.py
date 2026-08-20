from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings


@lru_cache
def get_engine() -> Engine:
    """Create the PostgreSQL engine used by the API and migrations."""
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL must be configured before using the database.")
    return create_engine(settings.database_url, pool_pre_ping=True, pool_recycle=1800)


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    return sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False)


def get_db_session() -> Generator[Session, None, None]:
    """FastAPI dependency that commits/rolls back database work safely."""
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
