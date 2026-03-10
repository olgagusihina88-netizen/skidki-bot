import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

# Токен бота из Telegram
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Строка подключения к PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')

# Telegram ID администратора (для доступа к админке)
ADMIN_ID = int(os.getenv('ADMIN_ID'))
