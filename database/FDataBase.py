"""
Модуль для работы с базой данных.

Models:

    Product: Содержит основную инфу о товаре:
        id, название, описание, рейтинг,
        URL на API с основными данными,
        URL на API с данными о цене.
        Так же связь с таблицей истории цен.

    PriceHistory: Содержит:
        id записи, id товара к которому она прикреплена,
        цена на товар, время добавления цены, а так же связь
        с таблицей информации о продукте.

Func:

    get_session: Создаёт асинхронную сессию,
        для работы с базой данных
    
    create_tables: Создаёт таблицы в базе данных.
    delete_tables: Удаляет таблицы из базы данных.

    add_item_info: Получает на вход:
        название товара, описание товара, рейтинг товара,
        URL от API с общей информацией о товаре,
        URL от API с информацией о цене товара, объект сессии,
        сохраняет эти данные в базу, возвращает сообщение об
        успехе или ошибке и статус код.

    delete_item: Получает на вход: id товара и объект сессии,
        удаляет товар из базы данных, возвращает сообщение об
        успехе или ошибке и статус код.

    select_item: Получает на вход: id товара и объект сессии,
        проверяет наличие товара в базе данных, 
        возвращает булево значение True если товар есть в базе, иначе False.

    select_history_price: Получает на вход: id товара и объект сессии,
        возвращает историю цен на заданый товар и статус код(dict).

    select_all_item: Получает на вход: объект сессии, возвращает
        все товары, находящиеся в базе данных то есть на мониторинге(dict).
"""
from typing import AsyncGenerator
from fastapi import Depends
from sqlalchemy import (Column, DateTime, ForeignKey,
                        Integer, String, Float, select)
from sqlalchemy.ext.asyncio import (
    create_async_engine, AsyncSession)
from sqlalchemy.orm import sessionmaker, relationship, DeclarativeBase
from sqlalchemy import func

from config import (DB_USER, DB_PASS, DB_HOST, DB_NAME)

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


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
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now())

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
    """Функция получения асинхронной сессии."""
    async with AsyncSessionLocal() as session:
            yield session


async def add_item_info(name: str, description: str,
                        rating: float, url_info: str,
                        url_price: str,
                        session: AsyncSession = Depends(get_session)) -> dict:
    """
    Функция добавления товара.

    Args:

        name: Название товара.
        description: Описание товара.
        rating: Рейтинг товара.
        url_info: Ссылка на API с общей информацией о товаре.
        url_price: Ссылка на API с информацией о цене товара.
        session: Асинхронная сессия для базы данных.
    
    Returns:
    
        Добавляет информацию о товаре в базе данных,
        возвращает сообщение об успехе или ошибке и статус код.
    """
    result = Product(name=name, description=description,
                    rating=rating, url_info=url_info, url_price=url_price)
    try:
        session.add(result)
        await session.commit()
        return {"message": f"Товар {name} добавлен!", "status_code": 200}
    except Exception as ex:
        return {"message": f"Проблемы с добавлением товара: {ex}",
                "status_code": 422}


async def delete_item(product_id: int,
                      session: AsyncSession = Depends(get_session)) -> dict:
    """
    Функция удаления товара и его истории цен.

    Args:

        product_id: id товара
        session: Асинхронная сессия для базы данных.
    
    Notes:

        Удаляет товар и его историю цен по переданному id,
        возвращает сообщение об успехе или ошибке и статус код.

    """
    result = await session.scalars(select(Product).filter_by(id=product_id))
    try:
        product = result.first()
        if product:
            await session.delete(product)
            await session.commit()
            return {"message": f"Товар с id: {product_id} удалён!",
                    "status_code": 200}
    except Exception as ex:
        return {"message": f"Проблемы с удалением товара: {ex}",
                "status_code": 422}


async def select_item(product_id: int,
                      session: AsyncSession = Depends(get_session)) -> bool:
    """
    Функция получения данных о товаре.

    Args:

        product_id: id товара
        session: Асинхронная сессия для базы данных.
    
    Returns:

        Возвращает булево значение, которое говорит от наличие
        товара в базе данных.
    """
    result = await session.scalars(
        select(Product).filter_by(id=product_id))
    return bool(result.first())


async def select_history_price(
        product_id: int,
        session: AsyncSession = Depends(get_session)) -> dict:
    """
    Функция получения истории цен товара.

    Args:

        product_id: id товара
        session: Асинхронная сессия для базы данных.
    
    Returns:

        Возвращает историю цен на товар и время появления этих цен в базе,
        так же возвращает статус код, иначе возвращает
        сообщение об ошибке и статус кода.
    """
    try:
        result = await session.scalars(
            select(PriceHistory).filter_by(product_id=product_id))
        history = [{"product_id": res.product_id,
                    "price": res.price,
                    "date": res.timestamp} for res in result]

        return {"message": history, "status_code": 200}
    except Exception as ex:
        return {"message": f"Ошибка получения истории цен товара: {ex}",
                "status_code": 422}


async def select_all_item(
        session: AsyncSession = Depends(get_session)) -> dict:
    """
    Функция получения товаров на мониторинге.

    Args:

        session: Асинхронная сессия для базы данных.
    
    Returns:

        Возвращает список(словарь) товаров, находящихся на мониторинге
    """
    try:
        result = await session.scalars(select(Product))
        products = [{"id": res.id, "name": res.name,
                    "description": res.description,
                    "rating": round(res.rating, 1)} for res in result]
        return {"message": products, "status_code": 200}
    except Exception as ex:
        return {"message": f"Ошибка получения товаров на мониторинге: {ex}",
                "status_code": 422}

