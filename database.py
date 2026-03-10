import aiomysql
from config import DATABASE_URL

# Глобальная переменная для пула подключений
db_pool = None


async def connect_to_db():
    """Подключение к базе данных MySQL"""
    global db_pool
    
    # Парсим DATABASE_URL (формат: mysql://user:pass@host:port/dbname)
    # Railway предоставляет URL в формате mysql://...
    import urllib.parse
    
    parsed = urllib.parse.urlparse(DATABASE_URL)
    
    db_pool = await aiomysql.create_pool(
        host=parsed.hostname,
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password,
        db=parsed.path.lstrip('/'),
        autocommit=True,
        cursorclass=aiomysql.DictCursor
    )
    print("✅ Успешное подключение к базе данных MySQL")
    
    # При старте проверяем/создаем таблицы
    await create_tables()


async def disconnect_from_db():
    """Отключение от базы данных"""
    global db_pool
    if db_pool:
        db_pool.close()
        await db_pool.wait_closed()
        print("❌ Отключение от базы данных")


async def get_db_connection():
    """Получить подключение из пула"""
    return await db_pool.acquire()


async def release_db_connection(conn):
    """Вернуть подключение в пул"""
    db_pool.release(conn)


async def create_tables():
    """
    Создание таблиц, если их нет.
    Запускается автоматически при старте.
    """
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            # Таблица пользователей
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    telegram_id BIGINT UNIQUE NOT NULL,
                    username VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица бизнесов
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS businesses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name TEXT NOT NULL,
                    contact_info TEXT,
                    tariff VARCHAR(20) DEFAULT 'micro',
                    active_until TIMESTAMP NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица акций
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS promotions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    business_id INT,
                    category VARCHAR(50) NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    website_url TEXT,
                    phone_number TEXT,
                    views_count INT DEFAULT 0,
                    clicks_count INT DEFAULT 0,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NULL,
                    FOREIGN KEY (business_id) REFERENCES businesses(id)
                )
            """)
            
            print("🗄️ Таблицы MySQL проверены/созданы")


# --- Функции для работы с акциями ---

async def get_promotions_by_category(category: str, limit: int = 10):
    """Получить список активных акций по категории"""
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """SELECT id, title, description, website_url, phone_number 
                   FROM promotions 
                   WHERE category = %s 
                   AND is_active = TRUE 
                   AND (expires_at IS NULL OR expires_at > NOW()) 
                   ORDER BY created_at DESC 
                   LIMIT %s""",
                (category, limit)
            )
            rows = await cur.fetchall()
            return rows


async def get_promotion_by_id(promo_id: int):
    """Получить полную информацию об одной акции"""
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT * FROM promotions WHERE id = %s AND is_active = TRUE",
                (promo_id,)
            )
            row = await cur.fetchone()
            return row


async def increment_views(promo_id: int):
    """Увеличить счетчик просмотров"""
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE promotions SET views_count = views_count + 1 WHERE id = %s",
                (promo_id,)
            )


async def increment_clicks(promo_id: int):
    """Увеличить счетчик кликов (переходов на сайт/звонок)"""
    async with db_pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "UPDATE promotions SET clicks_count = clicks_count + 1 WHERE id = %s",
                (promo_id,)
            )
