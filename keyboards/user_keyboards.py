"""
Foydalanuvchi klaviaturalari (aiogram v3)
"""
from aiogram.enums import ButtonStyle
from aiogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton,
)


def main_menu_kb(is_admin: bool = False, is_developer: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu (reply keyboard)"""
    keyboard = [[KeyboardButton(text="🍿 Kino olish", style=ButtonStyle.SUCCESS)]]
    keyboard.append([
        KeyboardButton(text="❓ Yordam", style=ButtonStyle.PRIMARY),
        KeyboardButton(text="ℹ️ Bot haqida", style=ButtonStyle.PRIMARY),
    ])
    if is_admin:
        keyboard.append([KeyboardButton(text="🛠 Admin panel", style=ButtonStyle.PRIMARY)])
    if is_developer:
        keyboard.append([KeyboardButton(text="💻 Developer", style=ButtonStyle.PRIMARY)])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def subscription_kb(channels: list) -> InlineKeyboardMarkup:
    """Obuna bo'lish klaviaturasi"""
    buttons = []
    for ch in channels:
        username = ch.get("username", "").lstrip("@")
        title = ch.get("title", "Kanal")
        ch_id = ch.get("id", 0)
        if username:
            url = f"https://t.me/{username}"
        else:
            clean_id = str(ch_id).replace("-100", "")
            url = f"https://t.me/c/{clean_id}"
        buttons.append([InlineKeyboardButton(text=f"📢 {title}", url=url, style=ButtonStyle.PRIMARY)])
    buttons.append([
        InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub", style=ButtonStyle.SUCCESS)
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
