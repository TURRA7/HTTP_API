from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import (DB_USER, DB_PASS, DB_HOST, DB_NAME)

# URL базы данных.
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
# Создание асинхронного движка.
engine = create_async_engine(DATABASE_URL)
# Создание асинхронной сессии.
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Базовый декларотивный класс.
class Base(DeclarativeBase):
    pass


async def create_tables() -> None:
    """Функция создания таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables() -> None:
    """Функция удаления таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)