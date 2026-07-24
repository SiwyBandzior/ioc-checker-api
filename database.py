from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import get_settings


class Base(DeclarativeBase):
    """Wspolna klasa bazowa dla wszystkich modeli (tabel)."""


engine = create_async_engine(get_settings().database_url)
AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def init_db() -> None:
    """Tworzy tabele, jesli jeszcze nie istnieja."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Zaleznosc FastAPI: jedna sesja bazy na jedno zadanie HTTP."""
    async with AsyncSessionLocal() as session:
        yield session
