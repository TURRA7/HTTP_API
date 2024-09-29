"""
Модуль моделей валидации данных.

Shemas:

    UrlCheck: 
        url_info: URL от API МВИДЕО c общей ифно о товаре.
        url_price: URL от API МВИДЕО c ифно о цене товара.

    ProductId: 
        product_id: id продукта.
"""
from pydantic import BaseModel, HttpUrl


class UrlCheck(BaseModel):
    """
    Модель для валидации ссылок о товаре.

    Args:

        url_info: URL от API МВИДЕО c общей ифно о товаре.
        url_price: URL от API МВИДЕО c ифно о цене товара.
    """
    url_info: HttpUrl
    url_price: HttpUrl


class ProductId(BaseModel):
    """
    Модуль для валидации id товара.

    Args:

        product_id: id товара в базе данных.
    """
    product_id: int