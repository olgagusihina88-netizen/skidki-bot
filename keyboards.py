from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard():
    """
    Главное меню с категориями акций
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🍣 Еда", callback_data="cat_food")],
        [InlineKeyboardButton(text="💅 Красота", callback_data="cat_beauty")],
        [InlineKeyboardButton(text="🚗 Авто", callback_data="cat_auto")],
    ])
    return keyboard


def promo_list_keyboard(promotions: list):
    """
    Генерирует кнопки для списка акций.
    promotions: список словарей из базы данных [{'id': 1, 'title': '...'}, ...]
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    for promo in promotions:
        # Кнопка с названием акции, которая передает ID акции при нажатии
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=f"🔥 {promo['title']}", 
                callback_data=f"view_{promo['id']}"
            )
        ])
    
    # Кнопка "Назад"
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")
    ])
    
    return keyboard


def offer_action_keyboard(website: str = None, phone: str = None):
    """
    Кнопки действий для акции (без промокода).
    Можно добавить ссылку на сайт или телефон.
    """
    buttons = []
    
    if website:
        buttons.append([InlineKeyboardButton(text="🌐 Перейти на сайт", url=website)])
    
    if phone:
        buttons.append([InlineKeyboardButton(text="📞 Позвонить", url=f"tel:{phone}")])
    
    # Кнопка "В избранное" или "Поделиться" (опционально)
    buttons.append([InlineKeyboardButton(text="⭐ В избранное", callback_data="favorite_add")])
    
    # Кнопка "Назад к списку"
    buttons.append([InlineKeyboardButton(text="🔙 Другие акции", callback_data="back_to_list")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_keyboard():
    """
    Кнопки админ-панели
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить акцию", callback_data="admin_add")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📂 Категории", callback_data="admin_categories")],
    ])
    return keyboard
