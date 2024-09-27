import asyncio
import json
import aiohttp


async def get_html(url: str):
    """
    Функция получения данных с HTML страницы.

    args:

        url: URL адресс товара.

    returns:

        Возвращает словарь с данными сайта.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        "Cookie": "MVID_CITY_ID=CityCZ_975; MVID_REGION_ID=1; MVID_REGION_SHOP=S002; MVID_TIMEZONE_OFFSET=3;"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            text = await response.text()
            return json.loads(text)


async def get_element(data_info: dict, data_price: dict) -> dict:
    """
    Функция поиска значения элемента.

    args:

        data_info: Словарь с данными о товаре(страница с API).
        data_price: Словарь с данными о цене(страница с API).

    returns:
        Возвращает словарь с распарсенными данными о товаре.
    """
    return {"name": data_info['body']['name'],
            "price": data_price['body']['materialPrices'][0]['price']['salePrice'],
            "description": data_info['body']['description'],
            "rating": data_info['body']['rating']['star']}