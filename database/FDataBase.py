"""Модуль для работы с базой данных."""
import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession)
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase

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


class Product(Base):
    """
    Таблица с общей информацией о продукте.

    args:

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

    price_history = relationship("PriceHistory", back_populates="product")


class PriceHistory(Base):
    """
    Таблица истории цен на товары.

    args:

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


async def add_item(name: str, description: str,
                   rating: float, url_info: str,
                   url_price: str) -> None:
    """
    Функция добавления товара.

    args:
        name: Название товара.
        description: Описание товара.
        rating: Рейтинг товара.
        url_info: Ссылка на API с общей информацией о товаре.
        url_price: Ссылка на API с информацией о цене товара.
    """
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = Product(name=name, description=description,
                            rating=rating, url_info=url_info, url_price=url_price)
            session.add(result)
            await session.commit()


async def add_item(product_id: int, price: float):
    """
    Функция добавления цены на товар.

    args:

        product_id: id товара, к которому добавляется цена
        price: Цена на товар.
    """
    async with AsyncSession(engine) as session:
        async with session.begin():
            result = PriceHistory(product_id=product_id, price=price)
            session.add(result)
            await session.commit()