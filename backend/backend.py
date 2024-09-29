"""
Моудль логики парсинга товаров в магазине МВИДЕО.

Func:

    get_html: Получает на вход url (данные полученые от API магазина),
        возвращает спарсенные данные(dict).

    get_info_item: Получает на вход спарсенные данные(dict), возвращает:
        название товара, описание товара и рейтинг товара.
"""
import json
import aiohttp


async def get_html(url: str):
    """
    Функция получения данных с HTML страницы.

    Args:

        url: URL адресс товара.

    Returns:

        Возвращает словарь с данными сайта(МВИДЕО).
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Mobile Safari/537.36",
        "Cookie": "MVID_CITY_ID=CityCZ_975; MVID_REGION_ID=1; MVID_REGION_SHOP=S002; MVID_TIMEZONE_OFFSET=3;"
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            try:
                text = await response.text()
                return {"message": json.loads(text), "status_code": 200}
            except Exception as ex:
                return {'error': f"Проблема с получением данных о товаре: {ex}"}


async def get_info_item(data_info: dict) -> dict:
    """
    Функция поиска информации о продукте.

    Args:

        data_info: Словарь с данными о товаре(страница с API).

    Returns:

        Возвращает словарь с общей информацией о товаре.
    """
    try:
        return {"name": data_info['body']['name'],
                "description": data_info['body']['description'],
                "rating": data_info['body']['rating']['star'],
                "status_code": 200}
    except Exception as ex:
        return {'error': f"Проблема с получением информации о товаре: {ex}",
                "status_code": 422}
