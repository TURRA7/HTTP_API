from fastapi import APIRouter

from database.FDataBase import add_item_info, select_history_price, select_item
from backend.backend import get_html, get_info_item
from models.model import UrlCheck, ProductId


app_parsing = APIRouter(prefix="/parsing")


@app_parsing.post("/add_item")
async def add_item(url: UrlCheck) -> dict:
    """
    Функция добавления товара на мониторинг.

    Args:
        
        url_info: URL от API МВИДЕО c общей ифно о товаре.
        url_price: URL от API МВИДЕО c ифно о цене товара.

    returns:

        Добавляет товар в базу данных,
        для последующего мониторинга.
    """
    data_info = await get_html(url.url_info)
    data_price = await get_html(url.url_info)

    if not data_info:
        return {"message": "Отсутствует ссылка на API с информацией о товаре!"}
    if not data_price:
        return {"message": "Отсутствует ссылка на API с информацией о цене!"}
    
    try:
        data = await get_info_item(data_info=data_info)
        await add_item_info(name=data['name'], description=data['description'],
                   rating=['rating'], url_info=url.url_info,
                   url_price=url.url_price)
        return {"message": "Товар добавлен!"}
    except Exception as ex:
        return {"message": f"Ошибка получения данных о товаре: {ex}"}


@app_parsing.delete("/delete_item/{item_id}")
async def delete_item(item_id: int) -> dict:
    """
    Функция удаления товара с мониторинга.

    Args:

        item_id: id товара в базе данных.

    Returns:
        
        Удаляет товар и его историю цен из базы данных.
    """
    product = ProductId(product_id=item_id)
    if await select_item(product_id=product.product_id):
        await delete_item(product_id=product.product_id)
        return {"message": "Товар удалён из базы данных."}
    else:
        return {"message": "Товар не найден в базе данных."}


@app_parsing.get("/get_list_monitoring/{item_id}")
async def get_list_monitoring() -> dict:
    """
    Функция получения товаров, находящихся на мониторинге.

    Returns:
        Возвращает словарь со списком товаров,
        находящихся в данный момент на мониторинге.
    """
    pass


@app_parsing.post("/get_history_price_item{item_id}")
async def get_history_price_item(item_id) -> dict:
    """
    Функция получения истории цен заданного товара.

    Args:

        item_id: id товара в базе данных.

    Returns:

        Возвращает словарь со списком истории цен на заданный товар.
    """
    product = ProductId(product_id=item_id)
    if await select_item(product_id=product.product_id):
        data = await select_history_price(product_id=product.product_id)
        return {"message": data}
    else:
        return {"message": "Товар не найден в базе данных."}
    