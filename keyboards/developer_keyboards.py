"""
Developer klaviaturalari (aiogram v3)
"""
from aiogram.types import InlineKeyboardMarkup

from keyboards.button_styles import ibtn


def developer_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [ibtn("📊 Tizim statistikasi", callback_data="dev_stats")],
        [ibtn("⚙️ Muhit o'zgaruvchilari", callback_data="dev_env")],
        [ibtn("🔙 Chiqish", callback_data="dev_exit")],
    ])


def dev_back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [ibtn("🔙 Orqaga", callback_data="dev_menu")],
    ])
