"""Модуль для работы с базой данных."""
import datetime
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, select
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession)
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase

from config import (DB_USER, DB_PASS, DB_HOST, DB_NAME)

# URL базы данных.
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
# Создание асинхронного движка.
engine = create_async_engine(DATABASE_URL)
# Создание асинхронной сессии.
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовый декларотивный класс.
class Base(DeclarativeBase):
    pass


class Product(Base):
    """
    Таблица с общей информацией о продукте.

    Args:

        id: id товара.
        name: Название товара.
        description: Описание товара.
        rating: Рейтинг товара.
        url_info: Ссылка на API с общей информацией о товаре.
        url_price: Ссылка на API с информацией о цене товара.
        price_history: Связь с таблицей истории цен на товар.
    """
    __tablename__ = "products"
    

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    rating = Column(Float)
    url_info = Column(String, nullable=False)
    url_price = Column(String, nullable=False)

    price_history = relationship("PriceHistory",
                                 back_populates="product",
                                 cascade="all, delete")


class PriceHistory(Base):
    """
    Таблица истории цен на товары.

    Args:

        id: id записи.
        product_id: id продукта.
        price: Цена продукта.
        timestamp: Время добавления цены.
        product: Связь с таблицей общей информации о продукте.
    """
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="price_history")


async def create_tables() -> None:
    """Функция создания таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables() -> None:
    """Функция удаления таблиц."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
            yield session


async def add_item_info(name: str, description: str,
                   rating: float, url_info: str,
                   url_price: str,
                   session: AsyncSession = Depends(get_session)) -> bool:
    """
    Функция добавления товара.

    Args:
        name: Название товара.
        description: Описание товара.
        rating: Рейтинг товара.
        url_info: Ссылка на API с общей информацией о товаре.
        url_price: Ссылка на API с информацией о цене товара.
    
    Returns:
        Добавляет информацию о товаре в базе данных,
        в случае успеха возвращает True,
        иначе False, если товар не найден в базе данных.
    """
    result = Product(name=name, description=description,
                    rating=rating, url_info=url_info, url_price=url_price)
    if not result:
        return None
    session.add(result)
    await session.commit()
    return True


async def add_item_price(product_id: int, price: float,
                         session: AsyncSession = Depends(get_session)) -> bool:
    """
    Функция добавления цены на товар.

    Args:

        product_id: id товара, к которому добавляется цена
        price: Цена на товар.
    
    Returns:
        Добавляет цену к товару в базе данных, в случае успеха возвращает True,
        иначе False, если товар не найден в базе данных.
    """
    result = PriceHistory(product_id=product_id, price=price)
    if not result:
        return None
    session.add(result)
    await session.commit()
    return True


async def delete_item(product_id: int,
                      session: AsyncSession = Depends(get_session)) -> bool:
    """
    Функция удаления товара и его истории цен.

    Args:

        product_id: id товара
    
    Notes:

        Удаляет товар и его историю цен по переданному id, в случае успеха
        возвращает True, иначе False, если товар не найден в базе данных.

    """
    result = session.scalars(select(Product).filter_by(id=product_id)).first()
    if not result:
        return None
    session.delete(result)
    await session.commit()
    return True


async def select_item(product_id: int,
                      session: AsyncSession = Depends(get_session)) -> bool:
    """
    Функция получения данных о товаре.

    Args:

        product_id: id товара
    
    Returns:

        Возвращает булево значение, которое говорит от наличие
        товара в базе данных.
    """
    result = await session.scalars(
        select(Product).filter_by(id=product_id)).first()
    return bool(result.first())


async def select_history_price(
        product_id: int,
        session: AsyncSession = Depends(get_session)) -> bool:
    """
    Функция получения истории цен товара.

    Args:

        product_id: id товара
    
    Returns:

        Возвращает историю цен на товар и время появления эти цен.
    """
    result = await session.scalars(
        select(PriceHistory).filter_by(product_id=product_id))
    if not result:
        return None
    return result