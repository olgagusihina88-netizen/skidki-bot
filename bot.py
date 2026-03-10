import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from config import BOT_TOKEN, ADMIN_ID
from database import (
    connect_to_db, 
    disconnect_from_db, 
    get_promotions_by_category, 
    get_promotion_by_id,
    increment_views,
    increment_clicks
)
from keyboards import (
    main_menu_keyboard, 
    promo_list_keyboard, 
    offer_action_keyboard,
    admin_keyboard
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ==========================================
# КОМАНДА /start - Главное меню
# ==========================================
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработка команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or "Неизвестный"
    
    logging.info(f"Пользователь {username} (ID: {user_id}) запустил бота")
    
    await message.answer(
        f"👋 Привет, {username}!\n\n"
        "🔥 Я бот с выгодными акциями в твоем городе!\n"
        "Выбери категорию и экономь на любимых услугах:",
        reply_markup=main_menu_keyboard()
    )


# ==========================================
# ОБРАБОТКА КАТЕГОРИЙ
# ==========================================
@dp.callback_query(F.data == "cat_food")
@dp.callback_query(F.data == "cat_beauty")
@dp.callback_query(F.data == "cat_auto")
async def show_category(callback: CallbackQuery):
    """Показ акций выбранной категории"""
    category_map = {
        "cat_food": "🍣 Еда",
        "cat_beauty": "💅 Красота",
        "cat_auto": "🚗 Авто"
    }
    
    category_key = callback.data
    category_name = category_map.get(category_key, "Акции")
    
    # Получаем акции из базы
    promotions = await get_promotions_by_category(category_key.replace("cat_", ""), limit=10)
    
    if not promotions:
        await callback.message.answer(
            f"{category_name}\n\n"
            "😔 Пока нет активных акций в этой категории.\n"
            "Загляни позже!",
            reply_markup=main_menu_keyboard()
        )
    else:
        await callback.message.answer(
            f"{category_name}\n\n"
            f"🔥 Найдено акций: {len(promotions)}",
            reply_markup=promo_list_keyboard(promotions)
        )
    
    await callback.answer()


# ==========================================
# ПРОСМОТР АКЦИИ
# ==========================================
@dp.callback_query(F.data.startswith("view_"))
async def show_promotion(callback: CallbackQuery):
    """Показ подробной информации об акции"""
    # Извлекаем ID акции из callback_data (view_123 -> 123)
    promo_id = int(callback.data.split("_")[1])
    
    # Получаем данные из базы
    promo = await get_promotion_by_id(promo_id)
    
    if not promo:
        await callback.message.answer("❌ Акция не найдена или неактивна")
        await callback.answer()
        return
    
    # Увеличиваем счетчик просмотров
    await increment_views(promo_id)
    
    # Формируем текст
    text = f"🔥 {promo['title']}\n\n"
    
    if promo['description']:
        text += f"{promo['description']}\n\n"
    
    text += "📍 Доступно прямо сейчас!"
    
    # Отправляем с кнопками действий
    await callback.message.answer(
        text,
        reply_markup=offer_action_keyboard(
            website=promo.get('website_url'),
            phone=promo.get('phone_number')
        )
    )
    
    await callback.answer()


# ==========================================
# НАЗАД В МЕНЮ
# ==========================================
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.answer(
        "📋 Главное меню:",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()


@dp.callback_query(F.data == "back_to_list")
async def back_to_list(callback: CallbackQuery):
    """Назад к списку акций (заглушка - возвращает в меню)"""
    await callback.message.answer(
        "📋 Выберите категорию:",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()


# ==========================================
# АДМИН-ПАНЕЛЬ
# ==========================================
@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    """Админ-панель (доступ только для ADMIN_ID)"""
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступ запрещен")
        return
    
    await message.answer(
        "🔧 Админ-панель",
        reply_markup=admin_keyboard()
    )


@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: CallbackQuery):
    """Показ статистики (заглушка)"""
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    await callback.message.answer(
        "📊 Статистика:\n\n"
        "Функция в разработке..."
    )
    await callback.answer()


# ==========================================
# ЗАПУСК БОТА
# ==========================================
async def main():
    """Основная функция запуска"""
    logging.info("🚀 Запуск бота...")
    
    # Подключаемся к базе данных
    await connect_to_db()
    
    # Удаляем вебхук (на случай если использовался ранее)
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем polling (постоянный опрос Telegram)
    logging.info("✅ Бот запущен и слушает обновления...")
    await dp.start_polling(bot)
    
    # При остановке отключаемся от базы
    await disconnect_from_db()


if __name__ == "__main__":
    asyncio.run(main())
