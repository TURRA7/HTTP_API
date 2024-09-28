from pydantic import BaseModel, HttpUrl


class UrlCheck(BaseModel):
    url_info: HttpUrl
    url_price: HttpUrl