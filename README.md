# Xoob_Bot

Автоматизированный бот для игры [Xoobgames](https://t.me/xoobgames_bot) в Telegram.

## 🚀 Установка

### 🔹 Клонирование репозитория
```sh
git clone https://github.com/Gr3eMx/xoob_bot.git
cd xoob_bot
```

### 🐧 Установка на Linux
```sh
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
cp .env-example .env
nano .env  # Укажите ваш INIT_DATA, который можно взять с https://game-api-v2.xoob.gg/api/auth/auth в Web версии Telegram
python3 main.py
```

### 🖥 Установка на Windows
```sh
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env-example .env
# Откройте файл .env и укажите ваш INIT_DATA, который можно взять с https://game-api-v2.xoob.gg/api/auth/auth в Web версии Telegram
python main.py
```

## ⚙️ Конфигурация
Перед запуском необходимо настроить `.env` файл, скопировав шаблон `.env-example` и указав необходимые параметры.

## 🛠 Использование
После установки и настройки бота просто запустите его:
```sh
python main.py
```
![Repo Views](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/helloWat3r/xoob_bot&count_bg=%2379C83D&title_bg=%23555555&icon=github.svg&icon_color=%23FFFFFF&title=views&edge_flat=false)


