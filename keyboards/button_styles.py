"""
Avtomatik rangli tugmalar.

Yangi tugma qo'shilganda to'g'ridan-to'g'ri InlineKeyboardButton yoki
KeyboardButton ishlatish o'rniga ibtn/kbtn helperlaridan foydalaning.
Helper matn va callback_data bo'yicha style rangini o'zi tanlaydi.
"""
from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo


SUCCESS_HINTS = (
    "add", "create", "save", "send", "submit", "confirm", "check", "start",
    "watch", "download", "upload", "post", "broadcast", "test",
    "qo'sh", "qosh", "saqla", "yubor", "tasdiq", "tekshir", "ulash",
    "tomosha", "yuklash", "boshlash", "web", "katalog",
)

DANGER_HINTS = (
    "delete", "del_", "remove", "cancel", "close", "exit", "stop", "danger",
    "o'chir", "ochir", "bekor", "yopish", "chiqish",
)

PRIMARY_HINTS = (
    "list", "stats", "settings", "guide", "help", "about", "back", "menu",
    "ro'yxat", "royxat", "statistika", "sozlama", "qo'llanma", "qollanma",
    "yordam", "haqida", "orqaga", "panel", "developer",
)


def auto_style(*values: object) -> ButtonStyle:
    text = " ".join(str(value or "") for value in values).casefold()

    if any(hint in text for hint in DANGER_HINTS):
        return ButtonStyle.DANGER
    if any(hint in text for hint in SUCCESS_HINTS):
        return ButtonStyle.SUCCESS
    if any(hint in text for hint in PRIMARY_HINTS):
        return ButtonStyle.PRIMARY
    return ButtonStyle.PRIMARY


def ibtn(
    text: str,
    callback_data: str | None = None,
    url: str | None = None,
    style: ButtonStyle | None = None,
) -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=text,
        callback_data=callback_data,
        url=url,
        style=style or auto_style(text, callback_data, url),
    )


def kbtn(
    text: str,
    style: ButtonStyle | None = None,
    web_app_url: str | None = None,
) -> KeyboardButton:
    web_app = WebAppInfo(url=web_app_url) if web_app_url else None
    return KeyboardButton(
        text=text,
        web_app=web_app,
        style=style or auto_style(text, web_app_url),
    )
