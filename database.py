import asyncpg
from config import DATABASE_URL

# Глобальная переменная для пула подключений
db_pool = None


async def connect_to_db():
    """Подключение к базе данных PostgreSQL"""
    global db_pool
    db_pool = await asyncpg.create_pool(DATABASE_URL)
    print("✅ Успешное подключение к базе данных")
    
    # При старте проверяем/создаем таблицы
    await create_tables()


async def disconnect_from_db():
    """Отключение от базы данных"""
    global db_pool
    if db_pool:
        await db_pool.close()
        print("❌ Отключение от базы данных")


async def get_db_connection():
    """Получить подключение из пула"""
    return await db_pool.acquire()


async def release_db_connection(conn):
    """Вернуть подключение в пул"""
    await db_pool.release(conn)


async def create_tables():
    """
    Создание таблиц, если их нет.
    Запускается автоматически при старте.
    """
    async with db_pool.acquire() as conn:
        # Таблица пользователей
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица бизнесов
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS businesses (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                contact_info TEXT,
                tariff VARCHAR(20) DEFAULT 'micro',
                active_until TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Таблица акций (ОБНОВЛЕННАЯ: без промокодов, с кнопками)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS promotions (
                id SERIAL PRIMARY KEY,
                business_id INTEGER REFERENCES businesses(id),
                category VARCHAR(50) NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                website_url TEXT,
                phone_number TEXT,
                views_count INTEGER DEFAULT 0,
                clicks_count INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
        """)
        print("🗄️ Таблицы проверены/созданы")


# --- Функции для работы с акциями ---

async def get_promotions_by_category(category: str, limit: int = 10):
    """Получить список активных акций по категории"""
    async with db_pool.acquire() as conn:
        rows = await conn.fetch(
            "SELECT id, title, description, website_url, phone_number FROM promotions "
            "WHERE category = $1 AND is_active = TRUE AND (expires_at IS NULL OR expires_at > NOW()) "
            "ORDER BY created_at DESC LIMIT $2",
            category, limit
        )
        # Превращаем записи в список словарей
        return [dict(row) for row in rows]


async def get_promotion_by_id(promo_id: int):
    """Получить полную информацию об одной акции"""
    async with db_pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM promotions WHERE id = $1 AND is_active = TRUE",
            promo_id
        )
        return dict(row) if row else None


async def increment_views(promo_id: int):
    """Увеличить счетчик просмотров"""
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE promotions SET views_count = views_count + 1 WHERE id = $1",
            promo_id
        )


async def increment_clicks(promo_id: int):
    """Увеличить счетчик кликов (переходов на сайт/звонок)"""
    async with db_pool.acquire() as conn:
        await conn.execute(
            "UPDATE promotions SET clicks_count = clicks_count + 1 WHERE id = $1",
            promo_id
        )
