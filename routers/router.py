from fastapi import APIRouter, Depends

from database.FDataBase import (add_item_info, add_item_price, delete_item, select_history_price,
                                select_item, get_session)
from backend.backend import get_html, get_info_item
from models.model import UrlCheck, ProductId
from sqlalchemy.ext.asyncio import AsyncSession

app_parsing = APIRouter(prefix="/parsing")


@app_parsing.post("/add_product")
async def add_product(url: UrlCheck,
                      session: AsyncSession = Depends(get_session)) -> dict:
    """
    Функция добавления товара на мониторинг.

    Args:
        
        url_info: URL от API МВИДЕО c общей ифно о товаре.
        url_price: URL от API МВИДЕО c ифно о цене товара.

    returns:

        Добавляет товар в базу данных,
        для последующего мониторинга.
    """
    data_info = await get_html(url=str(url.url_info))

    if not data_info:
        return {"message": "Отсутствует ссылка на API с информацией о товаре!",
                "status_code": 422}
    elif "error" in data_info:
        return {"error": data_info["error"],
                "status_code": 422}
    else:
        data = await get_info_item(data_info=data_info['message'])
        if data['status_code'] == 200:
            resault = await add_item_info(name=data['name'],
                                          description=data['description'],
                                          rating=data['rating'],
                                          url_info=str(url.url_info),
                                          url_price=str(url.url_price),
                                          session=session)
            return {"message": resault['message'],
                    'status_code': resault['status_code']}
        else:
            return {"error": data["error"], "status_code": data["status_code"]}
        

@app_parsing.delete("/delete_product/{item_id}")
async def delete_product(item_id: int,
                         session: AsyncSession = Depends(get_session)) -> dict:
    """
    Функция удаления товара с мониторинга.

    Args:

        item_id: id товара в базе данных.

    Returns:
        
        Удаляет товар и его историю цен из базы данных.
    """
    product = ProductId(product_id=item_id)
    if await select_item(product_id=product.product_id, session=session):
        resault = await delete_item(product_id=product.product_id,
                                    session=session)
        return {"message": resault['message'],
                'status_code': resault['status_code']}
    else:
        return {"message": "Товар не найден в базе данных."}


@app_parsing.get("/get_list_monitoring/{item_id}")
async def get_list_monitoring(
    session: AsyncSession = Depends(get_session)) -> dict:
    """
    Функция получения товаров, находящихся на мониторинге.

    Returns:

        Возвращает словарь со списком товаров,
        находящихся в данный момент на мониторинге.
    """
    pass


@app_parsing.get("/get_history_price_item{item_id}")
async def get_history_price_item(
    item_id: int,
    session: AsyncSession = Depends(get_session)) -> dict:
    """
    Функция получения истории цен заданного товара.

    Args:

        item_id: id товара в базе данных.

    Returns:

        Возвращает словарь со списком истории цен на заданный товар.
    """
    product = ProductId(product_id=item_id)
    if await select_item(product_id=product.product_id, session=session):
        resault = await select_history_price(product_id=product.product_id,
                                             session=session)
        return {"message": resault['message'],
                'status_code': resault['status_code']}
    else:
        return {"message": "Товар не найден в базе данных."}


# Перенос в модуль с мониторингом или же удаление!...
@app_parsing.get("/add_price")
async def add_price(
    item_id: int,
    price: float,
    session: AsyncSession = Depends(get_session)):
    """
    Функция добавления цены на товар.

    Args:
        
        item_id: id товара.
        price: Актуальная цена на товар.

    returns:

        Добавляет цену на товар в базу.
    """
    product = ProductId(product_id=item_id)
    if await select_item(product_id=product.product_id, session=session):
        resault = await add_item_price(product_id=product.product_id,
                                       price=price, session=session)
        return {"message": resault['message'],
                'status_code': resault['status_code']}
    else:
        return {"message": "Товар не найден в базе данных."}

    