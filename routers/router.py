from fastapi import APIRouter

from models.model import UrlCheck


app_parsing = APIRouter(prefix="/parsing")


@app_parsing.post("/add_item")
async def add_item(url_info: UrlCheck) -> None:
    """
    Функция добавления товара на мониторинг.

    returns:
        Добавляет товар в базу данных,
        для последующегомониторинга.
    """
    pass


@app_parsing.post("/delete_item/{item_id}")
async def add_item(item_id: int) -> None:
    """
    Функция удаления товара с мониторинга.

    returns:
        Добавляет товар в базу данных,
        для последующегомониторинга.
    """
    pass


@app_parsing.get("/get_list_monitoring")
async def get_list_monitoring() -> dict:
    """
    Функция получения товаров, находящихся на мониторинге.

    returns:
        Возвращает словарь со списком товаров,
        находящихся в данный момент на мониторинге.
    """
    pass


@app_parsing.post("/get_history_price_item{item_id}")
async def get_history_price_item(item_id) -> dict:
    """
    Функция получения истории цен заданного товара.

    returns:
        Возвращает словарь со списком истории цен на заданный товар.
    """
    pass