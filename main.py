import asyncio
import json
import os
import socketio
import logging
from dotenv import load_dotenv
from auth import auth_user
from logging.handlers import RotatingFileHandler
from aiohttp_socks import ProxyConnector

load_dotenv()

url = os.getenv("URL")
proxy_url = os.getenv("PROXY_URL")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler = logging.handlers.RotatingFileHandler(
    'mining_client.log',
    maxBytes=5 * 1024 * 1024,
    backupCount=1,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

class MiningClient:
    def __init__(self, url, proxy_url=None):
        self.url = url
        self.proxy_url = proxy_url
        self.sio = None
        self.last_balance_time = None
        self.timeout_minutes = 30

    async def create_sio_client(self):
        """Создание экземпляра socketio.AsyncClient с поддержкой прокси"""
        if self.sio:
            await self.sio.disconnect()
            self.sio = None

        connector = None
        if self.proxy_url:
            connector = ProxyConnector.from_url(self.proxy_url)

        self.sio = socketio.AsyncClient(http_session=connector) if connector else socketio.AsyncClient()

        self.sio.on("connect", self.on_connect)
        self.sio.on("disconnect", self.on_disconnect)
        self.sio.on("balance", self.on_balance_response)

    async def on_connect(self):
        """Обработчик успешного подключения"""
        logger.info("Подключено к серверу!")
        await self.sio.emit("startMining", {})
        logger.info("Майнинг начался.")
        asyncio.create_task(self.send_get_balance_periodically())
        asyncio.create_task(self.check_activity())

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
            if not is_mining and energy > 100:
                logger.info('Повторная отправка флага isMining')
                await self.sio.emit("startMining", {})

            self.last_balance_time = asyncio.get_event_loop().time()

        except json.JSONDecodeError:
            logger.error("Не удалось декодировать данные")

    async def check_activity(self):
        """Проверка активности клиента"""
        timeout_seconds = self.timeout_minutes * 60

        while True:
            if self.last_balance_time is None:
                await asyncio.sleep(10)
                continue

            current_time = asyncio.get_event_loop().time()
            elapsed_time = current_time - self.last_balance_time
            if elapsed_time > timeout_seconds:
                if self.sio.connected:
                    logger.warning(f"Нет активности более {self.timeout_minutes} минут. Перезапуск клиента...")
                    await self.restart_client()
                    break
                else:
                    logger.info("Клиент уже отключен. Перезапуск не требуется.")

            await asyncio.sleep(10)

    async def restart_client(self):
        """Перезапуск клиента"""
        logger.info("Перезапуск клиента...")
        if self.sio.connected:
            await self.sio.disconnect()
            await asyncio.sleep(5)
        await self.create_sio_client()
        await self.start()

    async def on_disconnect(self, sid):
        """Обработчик разрыва соединения"""
        if sid in ('transport error', 'server disconnect'):
            logger.warning(f"Соединение разорвано, причина: токен некорректный")

    async def start(self):
        """Запуск клиента"""
        while True:
            try:
                if not self.sio.connected:
                    token = await auth_user()
                    auth_data = {"token": token}
                    await self.sio.connect(self.url, transports=['websocket'], wait_timeout=5, auth=auth_data)
                    await self.sio.wait()
                else:
                    logger.info("Клиент уже подключен.")
                    await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Не удалось подключиться: {e}")
                await asyncio.sleep(10)


if __name__ == '__main__':
    client = MiningClient(url, proxy_url)

    async def main():
        await client.create_sio_client()
        await client.start()

    asyncio.run(main())