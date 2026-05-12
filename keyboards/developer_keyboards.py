"""
Developer klaviaturalari (aiogram v3)
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def developer_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Tizim statistikasi", callback_data="dev_stats")],
        [InlineKeyboardButton(text="⚙️ Muhit o'zgaruvchilari", callback_data="dev_env")],
        [InlineKeyboardButton(text="🔙 Chiqish", callback_data="dev_exit")],
    ])


def dev_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="dev_menu")],
    ])
