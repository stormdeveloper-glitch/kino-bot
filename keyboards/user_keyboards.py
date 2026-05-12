"""
Foydalanuvchi klaviaturalari (aiogram v3)
"""
from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup

from keyboards.button_styles import ibtn, kbtn


def main_menu_kb(is_admin: bool = False, is_developer: bool = False) -> ReplyKeyboardMarkup:
    """Asosiy menyu (reply keyboard)"""
    keyboard = [[kbtn("🍿 Kino olish")]]
    keyboard.append([kbtn("❓ Yordam"), kbtn("ℹ️ Bot haqida")])
    if is_admin:
        keyboard.append([kbtn("🛠 Admin panel")])
    if is_developer:
        keyboard.append([kbtn("💻 Developer")])
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
        buttons.append([ibtn(f"📢 {title}", url=url)])
    buttons.append([ibtn("✅ Obunani tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
