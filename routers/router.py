"""
Модуль обработчиков маршрутов FastAPI.

Func:
    
    add_product: Маршрут добавления товара. Получает на вход:
        валидированные URL и объект сессии, парсит их,
        добавляет спарсенную информацию в базу данных,
        возвращает сообщение об успехе или об ошибке и статус код.

    delete_product: Маршрут удаление товара. Получает на вход:
        id товара и объект сессии, удаляет товар,
        возвращает сообщение об успехе или об ошибке и статус код.

    get_list_monitoring: Маршрут получения товаров, находящихся на мониторинге.
        Получает на вход: объект сессии, возвращает(dict) со списком товаров
        и статус кодом, иначе ошибку и статус код.

    get_history_price_item: Маршрут получения истории цен, на заданый товар.
        Получает на вход: id товара и объект сессии, возвращает всю историю цен
        на товар, в том числе и время добавления цены, а так же и статус код.
"""
from fastapi import APIRouter, Depends

from database.FDataBase import (add_item_info, delete_item,
                                select_history_price, select_item,
                                get_session, select_all_item)
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


@app_parsing.get("/get_list_monitoring")
async def get_list_monitoring(
    session: AsyncSession = Depends(get_session)) -> dict:
    """
    Функция получения товаров, находящихся на мониторинге.

    Returns:

        Возвращает словарь со списком товаров,
        находящихся в данный момент на мониторинге.
    """
    resault = await select_all_item(session=session)
    return {"message": resault['message'],
                'status_code': resault['status_code']}


@app_parsing.get("/get_history_price_item/{item_id}")
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
   