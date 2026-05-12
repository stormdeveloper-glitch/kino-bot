"""
Foydalanuvchi handlerlari (aiogram v3)
"""
import logging
from html import escape

from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery

from keyboards.user_keyboards import main_menu_kb, subscription_kb
from keyboards.admin_keyboards import admin_main_kb
from utils.database import Database

logger = logging.getLogger(__name__)

router = Router()


# ──────────────────────────── /start ────────────────────────────
@router.message(Command("start"))
async def cmd_start(message: Message, bot: Bot, db: Database, config):
    await db.upsert_user(
        user_id=message.from_user.id,
        name=message.from_user.full_name,
        username=message.from_user.username,
    )

    settings = await db.get_settings()
    welcome_text = settings.get(
        "welcome_text",
        "🍿 <b>Kino Botga xush kelibsiz!</b>\n\n🟡 Kino kodini yuboring, bot darhol faylni topib beradi.",
    )

    is_admin = message.from_user.id in config.ADMIN_IDS
    is_developer = message.from_user.id == config.DEVELOPER_ID

    # Deep link argumentini olish
    args = message.text.split(maxsplit=1)
    deep_arg = args[1].strip().lower() if len(args) > 1 else None

    if deep_arg:
        # Deep link orqali kelgan — obuna tekshiruvi
        channels = await db.get_channels()
        if channels and not is_admin and not is_developer:
            not_subscribed = []
            for channel in channels:
                try:
                    member = await bot.get_chat_member(channel["id"], message.from_user.id)
                    if member.status in ("left", "kicked"):
                        not_subscribed.append(channel)
                except Exception:
                    pass
            if not_subscribed:
                sub_text = settings.get(
                    "not_subscribed_text",
                    "⚠️ Iltimos, quyidagi kanallarga obuna bo'ling:",
                )
                await message.answer(sub_text, reply_markup=subscription_kb(not_subscribed))
                return

        await _send_movie(bot, db, message, deep_arg)
        return

    await message.answer(
        welcome_text,
        reply_markup=main_menu_kb(is_admin=is_admin, is_developer=is_developer),
    )


# ──────────────────────────── /help ────────────────────────────
@router.message(Command("help"))
async def cmd_help(message: Message, config):
    await _send_help(message, config)


async def _send_help(message: Message, config):
    text = (
        "🟡 <b>Yordam markazi</b>\n\n"
        "🍿 <b>Kino olish:</b>\n"
        "Bot sizga kino kodini beradi yoki e'londa kod yozilgan bo'ladi.\n"
        "Shu kodni botga yuboring — kino darhol keladi.\n\n"
        "🔎 <b>Misol:</b>\n"
        "Agar kino kodi <code>001</code> bo'lsa, shunchaki:\n"
        "<code>001</code> deb yuboring.\n\n"
        "⚠️ <b>Eslatma:</b>\n"
        "Botdan foydalanish uchun barcha kanallarga obuna bo'lishingiz shart.\n\n"
        f"📞 <b>Muammo bo'lsa admin bilan bog'laning: {config.ADMIN_USERNAME}</b>"
    )
    await message.answer(text)


# ──────────────────────────── Bot haqida tugmasi ────────────────────────────
@router.message(F.text.in_({"ℹ️ Bot haqida", "🔵 Bot haqida"}))
async def btn_about(message: Message, db: Database, config):
    settings = await db.get_settings()
    about_text = settings.get("about_text", "🍿 Kino Bot Pro")
    if "@admin" in about_text:
        about_text = about_text.replace("@admin", config.ADMIN_USERNAME)
    await message.answer(about_text)


# ──────────────────────────── Kino olish tugmasi ────────────────────────────
@router.message(F.text.in_({"🎬 Kino olish", "🍿 Kino olish"}))
async def btn_get_movie(message: Message):
    await message.answer(
        "🍿 <b>Kino kodini yuboring</b>\n\n"
        "🟡 Misol: <code>001</code> yoki <code>spiderman</code>",
    )


# ──────────────────────────── Yordam tugmasi ────────────────────────────
@router.message(F.text.in_({"❓ Yordam", "🟡 Yordam"}))
async def btn_help(message: Message, config):
    await _send_help(message, config)


# ──────────────────────────── Admin Panel Tugmasi ────────────────────────────
@router.message(F.text.in_({"🛠 Boshqarish", "🛠 Admin panel"}))
async def btn_admin_panel(message: Message, config):
    if message.from_user.id not in config.ADMIN_IDS:
        return
    await message.answer(
        "🛠 <b>Admin Panel</b>\n\nKerakli bo'limni tanlang:",
        reply_markup=admin_main_kb(),
    )


# ──────────────────────────── Obunani tekshirish ────────────────────────────
@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery, bot: Bot, db: Database, config):
    channels = await db.get_channels()
    not_subscribed = []
    for channel in channels:
        try:
            member = await bot.get_chat_member(channel["id"], callback.from_user.id)
            if member.status in ("left", "kicked"):
                not_subscribed.append(channel)
        except Exception:
            pass

    if not_subscribed:
        settings = await db.get_settings()
        text = settings.get(
            "not_subscribed_text",
            "⚠️ <b>Botdan foydalanish uchun kanallarga obuna bo'ling.</b>",
        )
        try:
            await callback.message.edit_text(text, reply_markup=subscription_kb(not_subscribed))
        except Exception:
            pass
        await callback.answer("❌ Hali obuna bo'lmagan kanallar bor!", show_alert=True)
    else:
        settings = await db.get_settings()
        welcome_text = settings.get(
            "welcome_text",
            "🍿 <b>Kino Botga xush kelibsiz!</b>\n\n🟡 Kino kodini yuboring.",
        )
        try:
            await callback.message.edit_text(
                "✅ <b>Obuna tasdiqlandi!</b>\n\nEndi botdan foydalanishingiz mumkin.",
            )
        except Exception:
            pass
        await callback.answer("✅ Obuna tasdiqlandi!")
        is_admin = callback.from_user.id in config.ADMIN_IDS
        is_developer = callback.from_user.id == config.DEVELOPER_ID
        await callback.message.answer(
            welcome_text,
            reply_markup=main_menu_kb(is_admin=is_admin, is_developer=is_developer),
        )


# ──────────────────────────── Kino kodi (state=None) ────────────────────────────
SKIP_TEXTS = {
    "🎬 Kino olish", "🍿 Kino olish",
    "❓ Yordam", "🟡 Yordam",
    "ℹ️ Bot haqida", "🔵 Bot haqida",
    "🛠 Boshqarish", "🛠 Admin panel",
    "💻 Developer",
}


@router.message(default_state, F.text)
async def handle_movie_code(message: Message, bot: Bot, db: Database):
    if message.text in SKIP_TEXTS or message.text.startswith("/"):
        return
    code = message.text.strip().lower()
    await _send_movie(bot, db, message, code)


# ──────────────────────── Yordamchi: kino yuborish ────────────────────────
async def _send_movie(bot: Bot, db: Database, message: Message, code: str):
    movie = await db.get_movie(code)
    if not movie:
        await message.answer(
            f"❌ <b>{escape(code)}</b> kodi bilan kino topilmadi.\n\n"
            "🔎 Kodni to'g'ri yozganingizni tekshiring.\n"
            "🟡 Yordam uchun /help",
        )
        return

    await db.increment_searches(message.from_user.id)

    file_id = movie["file_id"]
    file_type = movie.get("file_type", "document")
    title = movie.get("title", "Kino")
    caption = movie.get("caption") or f"🍿 <b>{escape(title)}</b>\n🟡 Kod: <code>{escape(code)}</code>"

    try:
        if file_type == "video":
            await bot.send_video(message.chat.id, file_id, caption=caption)
        elif file_type == "photo":
            await bot.send_photo(message.chat.id, file_id, caption=caption)
        else:
            await bot.send_document(message.chat.id, file_id, caption=caption)
    except TelegramAPIError as e:
        logger.error(f"Kino yuborishda xato ({code}): {e}")
        await message.answer("❌ Kinoni yuborishda xato yuz berdi.\nAdmin bilan bog'laning.")
