import asyncio
import json
import os
import socketio
import logging
from dotenv import load_dotenv
from auth import auth_user

load_dotenv()

url = os.getenv("URL")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MiningClient:
    def __init__(self, url):
        self.url = url
        self.sio = socketio.AsyncClient()

        # Регистрация обработчиков событий
        self.sio.on("connect", self.on_connect)
        self.sio.on("disconnect", self.on_disconnect)
        self.sio.on("balance", self.on_balance_response)

    async def on_connect(self):
        """Обработчик успешного подключения"""
        logger.info("Подключено к серверу!")
        await self.sio.emit("startMining", {})
        logger.info("Майнинг начался.")
        asyncio.create_task(self.send_get_balance_periodically())

    async def send_get_balance_periodically(self):
        """Периодическая отправка запроса getBalance"""
        interval = 30
        while True:
            try:
                await self.sio.emit("getBalance", {})
                logger.info("Отправлен запрос getBalance")
            except Exception as e:
                logger.error(f"Ошибка при отправке getBalance: {e}")
            await asyncio.sleep(interval)

    async def on_balance_response(self, data):
        """Обработчик ответа на запрос getBalance"""
        try:
            data = json.loads(data)
            is_mining = data.get("isMining", False)
            energy = data.get("energy", 0)
            logger.info(data)
            if not is_mining and energy > 6000:
                logger.info('Повторная отправка флага isMining')
                await self.sio.emit("startMining", {})

        except json.JSONDecodeError:
            logger.error("Не удалось декодировать данные")

    async def on_disconnect(self, sid):
        """Обработчик разрыва соединения"""
        if sid in ('transport error', 'server disconnect'):
            logger.warning(f"Соединение разорвано, причина: токен некорректный")

    async def start(self):
        """Запуск клиента"""
        try:
            token = await auth_user()
            auth_data = {"token": token}
            await self.sio.connect(self.url, transports=['websocket'], wait_timeout=5, auth=auth_data)
            await self.sio.wait()
        except Exception as e:
            logger.error(f"Не удалось подключиться: {e}")


if __name__ == '__main__':
    client = MiningClient(url)
    asyncio.run(client.start())