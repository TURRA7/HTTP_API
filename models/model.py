from pydantic import BaseModel, HttpUrl


class UrlCheck(BaseModel):
    url: HttpUrl