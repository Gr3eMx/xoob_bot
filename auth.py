import asyncio

import aiohttp
from dotenv import load_dotenv
import os

load_dotenv()


async def auth_user() -> str | None:
    try:
        init_data = os.getenv("INIT_DATA")
        if not init_data:
            raise ValueError("Переменная окружения INIT_DATA не установлена или пустая.")

        url = 'https://game-api-v2.xoob.gg/api/auth/auth'

        data = {
            "initData": init_data
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    response_data = await response.json()
                    return response_data.get("sessionKey")
                else:
                    print(f"Ошибка: {response.status}")
                    error_text = await response.text()
                    print("Текст ошибки:", error_text)
                    return None

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return None
