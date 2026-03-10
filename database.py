import asyncpg
from config import DATABASE_URL

# Глобальная переменная для пула подключений
db_pool = None


async def connect_to_db():
    """
    Подключение к базе данных PostgreSQL
    Вызывается один раз при старте бота
    """
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    print("✅ Успешное подключение к базе данных")


async def disconnect_from_db():
    """
    Отключение от базы данных
    Вызывается при остановке бота
    """
    global db_pool
    if db_pool:
        await db_pool.close()
        print("❌ Отключение от базы данных")


async def get_db_connection():
    """
    Получить подключение из пула
    Используется для выполнения запросов
    """
    return await db_pool.acquire()


async def release_db_connection(conn):
    """
    Вернуть подключение в пул после использования
    """
    await db_pool.release(conn)
