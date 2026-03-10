from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard():
    """
    Главное меню с категориями акций
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍣 Еда", callback_data="category_food")],
        [InlineKeyboardButton(text="💅 Красота", callback_data="category_beauty")],
        [InlineKeyboardButton(text="🚗 Авто", callback_data="category_auto")],
    ])
    return keyboard


def get_promo_keyboard(promo_code: str):
    """
    Кнопка для получения промокода
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Получить промокод", callback_data=f"get_promo_{promo_code}")],
    ])
    return keyboard


def admin_keyboard():
    """
    Кнопки админ-панели
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить акцию", callback_data="admin_add_promo")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
    ])
    return keyboard


def category_keyboard():
    """
    Выбор категории при добавлении акции
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍣 Еда", callback_data="cat_food")],
        [InlineKeyboardButton(text="💅 Красота", callback_data="cat_beauty")],
        [InlineKeyboardButton(text="🚗 Авто", callback_data="cat_auto")],
    ])
    return keyboard
