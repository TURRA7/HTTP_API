import asyncio
from fastapi import FastAPI
import uvicorn

from database.FDataBase import create_tables
from backend.backend import get_html


# Приложение FastAPI
app = FastAPI()


async def main() -> None:
    """
    Стартовая функция.

    func:
        create_tables: создаёт таблицы в базе.
    """
    await create_tables()


if __name__ == "__main__":
    asyncio.run(main())
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)