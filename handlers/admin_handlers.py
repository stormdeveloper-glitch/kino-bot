"""
Admin panel handlerlari (aiogram v3)
FSM holatlari aiogram.fsm orqali
"""
import asyncio
import logging
from html import escape

from aiogram import Router, F, Bot
from aiogram.enums import ButtonStyle, ChatMemberStatus
from aiogram.exceptions import TelegramForbiddenError, TelegramAPIError
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
)

from keyboards.admin_keyboards import (
    admin_main_kb, admin_settings_kb, back_kb, broadcast_confirm_kb,
    cancel_admin_kb, channels_list_kb, confirm_kb,
)
from utils.database import Database
from utils.states import (
    AddMovieState, AddChannelState, BroadcastState,
    EditSettingState, DeleteMovieState,
)

logger = logging.getLogger(__name__)

router = Router()

SETTINGS_MAP = {
    "settings_welcome":      ("welcome_text", "Xush kelibsiz matni"),
    "settings_about":        ("about_text", "Bot haqida matni"),
    "settings_not_sub":      ("not_subscribed_text", "Obuna eslatma matni"),
    "settings_post_channel": ("post_channel_id", "Avto-post kanali ID (-100...)"),
}

CAPTION_LIMIT = 1024


def trim_caption(text: str, limit: int = CAPTION_LIMIT) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 18].rstrip() + "\n\n<i>Davomi botda...</i>"


def normalize_chat_identifier(value: str):
    raw = value.strip()
    if raw.lstrip("-").isdigit():
        return int(raw)
    if raw.startswith("@"):
        return raw
    return None


def can_bot_post(member) -> bool:
    if member.status == ChatMemberStatus.CREATOR:
        return True
    if member.status != ChatMemberStatus.ADMINISTRATOR:
        return False
    return bool(getattr(member, "can_post_messages", True))


async def validate_post_channel(bot: Bot, channel_identifier):
    chat = await bot.get_chat(channel_identifier)
    me = await bot.get_me()
    bot_member = await bot.get_chat_member(chat.id, me.id)
    if not can_bot_post(bot_member):
        return chat, False
    return chat, True


async def post_movie_to_channel(
    bot: Bot,
    post_channel_id,
    code: str,
    caption: str,
    file_id: str,
    file_type: str,
):
    me = await bot.get_me()
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🎬 Tomosha qilish",
                url=f"https://t.me/{me.username}?start={code}",
                style=ButtonStyle.SUCCESS,
            )
        ],
        [
            InlineKeyboardButton(
                text="🔎 Kod orqali olish",
                url=f"https://t.me/{me.username}",
                style=ButtonStyle.PRIMARY,
            )
        ],
    ])
    safe_caption = trim_caption(caption)

    if file_type == "video":
        await bot.send_video(post_channel_id, file_id, caption=safe_caption, reply_markup=kb)
    elif file_type == "photo":
        await bot.send_photo(post_channel_id, file_id, caption=safe_caption, reply_markup=kb)
    else:
        await bot.send_document(post_channel_id, file_id, caption=safe_caption, reply_markup=kb)


# ──────────────────────────── YORDAMCHI ────────────────────────────

async def back_to_admin(callback: CallbackQuery, state: FSMContext,
                        text: str = "🛠 <b>Admin Panel</b>\n\nQuyidagi bo'limlardan birini tanlang:"):
    await state.clear()
    try:
        await callback.message.edit_text(text, reply_markup=admin_main_kb())
    except Exception:
        await callback.message.answer(text, reply_markup=admin_main_kb())
    await callback.answer()


# ──────────────────────────── /admin ────────────────────────────

@router.message(Command("admin"))
async def cmd_admin(message: Message, state: FSMContext, config):
    if message.from_user.id not in config.ADMIN_IDS:
        await message.answer("❌ Sizda admin huquqi yo'q.")
        return
    await state.clear()
    await message.answer(
        "🛠 <b>Admin Panel</b>\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=admin_main_kb(),
    )


# ──────────────────────────── Orqaga / Bekor ────────────────────────────

@router.callback_query(F.data == "admin_back")
async def cb_admin_back(callback: CallbackQuery, state: FSMContext):
    await back_to_admin(callback, state)


@router.callback_query(F.data == "admin_cancel_fsm")
async def cb_cancel_fsm(callback: CallbackQuery, state: FSMContext):
    await back_to_admin(callback, state, "❌ Bekor qilindi.\n\n🛠 <b>Admin Panel</b>")


@router.callback_query(F.data == "noop")
async def cb_noop(callback: CallbackQuery):
    await callback.answer()


# ════════════════════════════════════════════════════
#                    KINO QO'SHISH
# ════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_add_movie")
async def cb_add_movie(callback: CallbackQuery, state: FSMContext, config):
    if callback.from_user.id not in config.ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)
    await state.set_state(AddMovieState.code)
    try:
        await callback.message.edit_text(
            "🎬 <b>Kino qo'shish</b>\n\n"
            "📌 <b>1-qadam:</b> Kino <b>kodini</b> yuboring.\n"
            "Masalan: <code>001</code>, <code>avatar2</code>, <code>spiderman</code>\n\n"
            "⚠️ Foydalanuvchilar shu kod orqali kinoni oladi.",
            reply_markup=cancel_admin_kb(),
        )
    except Exception:
        await callback.message.answer(
            "🎬 Kino kodini yuboring:", reply_markup=cancel_admin_kb()
        )
    await callback.answer()


@router.message(AddMovieState.code, F.text)
async def fsm_movie_code(message: Message, state: FSMContext, db: Database):
    code = message.text.strip().lower()
    if len(code) > 50:
        return await message.answer("❌ Kod 50 ta belgidan oshmasin!")
    if await db.movie_exists(code):
        return await message.answer(
            f"⚠️ <code>{escape(code)}</code> kodi allaqachon mavjud!\n"
            "Boshqa kod kiriting yoki avval o'chiring.",
            reply_markup=cancel_admin_kb(),
        )
    await state.update_data(code=code)
    await state.set_state(AddMovieState.file)
    await message.answer(
        f"✅ Kod: <code>{escape(code)}</code>\n\n"
        "📌 <b>2-qadam:</b> Kino <b>faylini</b> yuboring.\n"
        "(Video yoki Hujjat sifatida)",
        reply_markup=cancel_admin_kb(),
    )


@router.message(AddMovieState.file, F.video | F.document | F.photo)
async def fsm_movie_file(message: Message, state: FSMContext):
    if message.video:
        file_id, file_type = message.video.file_id, "video"
    elif message.document:
        file_id, file_type = message.document.file_id, "document"
    elif message.photo:
        file_id, file_type = message.photo[-1].file_id, "photo"
    else:
        return

    await state.update_data(file_id=file_id, file_type=file_type)
    await state.set_state(AddMovieState.title)
    await message.answer(
        "✅ Fayl qabul qilindi!\n\n"
        "📌 <b>3-qadam:</b> Kino <b>nomini</b> yuboring.\n"
        "Masalan: <code>Avatar: The Way of Water</code>",
        reply_markup=cancel_admin_kb(),
    )


@router.message(AddMovieState.file, F.text)
async def fsm_movie_file_wrong(message: Message):
    await message.answer(
        "❌ Faqat <b>Video</b> yoki <b>Hujjat</b> yuboring!",
        reply_markup=cancel_admin_kb(),
    )


@router.message(AddMovieState.title, F.text)
async def fsm_movie_title(message: Message, state: FSMContext):
    title = message.text.strip()
    await state.update_data(title=title)
    await state.set_state(AddMovieState.caption)
    await message.answer(
        f"✅ Nom: <b>{escape(title)}</b>\n\n"
        "📌 <b>4-qadam (ixtiyoriy):</b> Kino haqida <b>qo'shimcha matn</b> yuboring.\n"
        "Masalan: janr, yil, til, rejissor...\n\n"
        "⏭ Kerak bo'lmasa <code>-</code> yuboring.",
        reply_markup=cancel_admin_kb(),
    )


@router.message(AddMovieState.caption, F.text)
async def fsm_movie_caption(message: Message, state: FSMContext):
    caption_text = message.text.strip()
    if caption_text == "-":
        caption_text = ""
    await state.update_data(caption_text=caption_text)
    await state.set_state(AddMovieState.post_media)
    await message.answer(
        "✅ Izoh qabul qilindi.\n\n"
        "📌 <b>5-qadam:</b> Avto-post uchun <b>rasm (poster)</b> yoki "
        "<b>qisqa video (treyler)</b> yuboring.\n\n"
        "⏭ Kerak bo'lmasa <code>-</code> yuboring.",
        reply_markup=cancel_admin_kb(),
    )


@router.message(AddMovieState.post_media, F.text | F.photo | F.video)
async def fsm_movie_post_media(message: Message, state: FSMContext, bot: Bot, db: Database):
    post_file_id = None
    post_file_type = None

    if message.content_type == "text" and message.text.strip() == "-":
        pass
    elif message.photo:
        post_file_id = message.photo[-1].file_id
        post_file_type = "photo"
    elif message.video:
        post_file_id = message.video.file_id
        post_file_type = "video"
    elif message.text:
        return await message.answer(
            "❌ Faqat rasm, video yoki <code>-</code> yuboring!",
            reply_markup=cancel_admin_kb(),
        )

    data = await state.get_data()
    code = data["code"]
    title = data["title"]
    file_id = data["file_id"]
    file_type = data["file_type"]
    caption_text = data["caption_text"]

    # To'liq caption
    if caption_text:
        full_caption = (
            f"🍿 <b>{escape(title)}</b>\n\n"
            f"{escape(caption_text)}\n\n"
            f"🟡 Kod: <code>{escape(code)}</code>\n"
            f"━━━━━━━━━━━━━━\n"
            f"📲 Kinoni olish uchun kodni botga yuboring."
        )
    else:
        full_caption = (
            f"🍿 <b>{escape(title)}</b>\n\n"
            f"🟡 Kod: <code>{escape(code)}</code>\n"
            f"━━━━━━━━━━━━━━\n"
            f"📲 Kinoni olish uchun kodni botga yuboring."
        )

    success = await db.add_movie(
        code=code, title=title, file_id=file_id,
        file_type=file_type, added_by=message.from_user.id, caption=full_caption,
    )

    await state.clear()

    if success:
        auto_post_note = "ℹ️ Avto-post kanali sozlanmagan."

        # Auto-post
        settings = await db.get_settings()
        post_channel_id = settings.get("post_channel_id")
        if post_channel_id:
            raw_ch = str(post_channel_id).strip()
            if raw_ch.lstrip("-").isdigit():
                post_channel_id = int(raw_ch)

            try:
                pf_id = post_file_id or file_id
                pf_type = post_file_type or file_type
                await post_movie_to_channel(bot, post_channel_id, code, full_caption, pf_id, pf_type)
                auto_post_note = "✅ Avto-post kanalga yuborildi."
            except TelegramForbiddenError:
                auto_post_note = "⚠️ Avto-post yuborilmadi: bot kanalda admin emas."
                await message.answer(
                    "⚠️ Kino saqlandi, lekin auto-post amalga oshmadi.\n"
                    "❗ Botni kanalga <b>admin</b> qilib qo'shing.",
                )
            except TelegramAPIError as e:
                auto_post_note = "⚠️ Avto-post yuborilmadi: kanal sozlamasini tekshiring."
                await message.answer(
                    f"⚠️ Kino saqlandi, lekin auto-post amalga oshmadi.\n"
                    f"❗ Kanal ID noto'g'ri yoki bot kanalda admin emas.\n"
                    f"<code>{escape(str(e))}</code>",
                )
            except Exception as e:
                auto_post_note = "⚠️ Avto-post yuborilmadi: kutilmagan xatolik."
                logger.error(f"Avto-post xatosi: {e}")
                await message.answer(f"⚠️ Kino saqlandi, lekin auto-post qilishda xato: {e}")

        await message.answer(
            f"✅ <b>Kino muvaffaqiyatli qo'shildi!</b>\n\n"
            f"🟡 Kod: <code>{escape(code)}</code>\n"
            f"🍿 Nom: <b>{escape(title)}</b>\n"
            f"📁 Tur: {file_type}\n"
            f"{auto_post_note}",
            reply_markup=admin_main_kb(),
        )
    else:
        await message.answer(
            "❌ Xato! Bu kod allaqachon mavjud.",
            reply_markup=admin_main_kb(),
        )


# ════════════════════════════════════════════════════
#                    KINO O'CHIRISH
# ════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_del_movie")
async def cb_del_movie(callback: CallbackQuery, state: FSMContext, config):
    if callback.from_user.id not in config.ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)
    await state.set_state(DeleteMovieState.code)
    try:
        await callback.message.edit_text(
            "🗑 <b>Kino o'chirish</b>\n\nO'chirmoqchi bo'lgan kinoning <b>kodini</b> yuboring:",
            reply_markup=cancel_admin_kb(),
        )
    except Exception:
        await callback.message.answer("🗑 Kino kodini yuboring:", reply_markup=cancel_admin_kb())
    await callback.answer()


@router.message(DeleteMovieState.code, F.text)
async def fsm_delete_movie(message: Message, state: FSMContext, db: Database):
    code = message.text.strip().lower()
    movies = await db.get_all_movies()
    movie = movies.get(code)
    if not movie:
        return await message.answer(
            f"❌ <code>{escape(code)}</code> kodi bilan kino topilmadi.",
            reply_markup=cancel_admin_kb(),
        )
    await state.clear()
    await message.answer(
        f"⚠️ <b>Tasdiqlang!</b>\n\n"
        f"🎬 Kino: <b>{escape(movie['title'])}</b>\n"
        f"🔖 Kod: <code>{escape(code)}</code>\n\n"
        f"Bu kinoni o'chirmoqchimisiz?",
        reply_markup=confirm_kb("movie", code),
    )


@router.callback_query(F.data.startswith("confirm_movie_"))
async def confirm_delete_movie(callback: CallbackQuery, db: Database):
    code = callback.data.replace("confirm_movie_", "")
    success = await db.delete_movie(code)
    text = f"✅ <code>{escape(code)}</code> kodi bilan kino o'chirildi." if success else "❌ Kino topilmadi."
    try:
        await callback.message.edit_text(text, reply_markup=admin_main_kb())
    except Exception:
        await callback.message.answer(text, reply_markup=admin_main_kb())
    await callback.answer()


# ════════════════════════════════════════════════════
#                  KINOLAR RO'YXATI
# ════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_movie_list")
async def cb_movie_list(callback: CallbackQuery, db: Database):
    movies = await db.get_all_movies()
    if not movies:
        try:
            await callback.message.edit_text("📋 Hozircha hech qanday kino yo'q.", reply_markup=back_kb())
        except Exception:
            pass
        return await callback.answer()

    lines = [
        f"{i}. 🎬 <b>{escape(m['title'])}</b> — <code>{escape(code)}</code> ({m.get('views', 0)} marta ko'rilgan)"
        for i, (code, m) in enumerate(list(movies.items())[:50], 1)
    ]
    total = len(movies)
    text = f"📋 <b>Kinolar ro'yxati</b> ({min(total,50)}/{total}):\n\n" + "\n".join(lines)
    if len(text) > 4000:
        text = text[:4000] + "\n\n..."
    try:
        await callback.message.edit_text(text, reply_markup=back_kb())
    except Exception:
        await callback.message.answer(text, reply_markup=back_kb())
    await callback.answer()


# ════════════════════════════════════════════════════
#                     STATISTIKA
# ════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_stats")
async def cb_stats(callback: CallbackQuery, db: Database):
    stats = await db.get_stats()
    text = (
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{stats['total_users']}</b>\n"
        f"🎬 Kinolar: <b>{stats['total_movies']}</b>\n"
        f"📡 Obuna kanallari: <b>{stats['total_channels']}</b>\n"
        f"👁 Umumiy ko'rishlar: <b>{stats['total_views']}</b>"
    )
    try:
        await callback.message.edit_text(text, reply_markup=back_kb())
    except Exception:
        await callback.message.answer(text, reply_markup=back_kb())
    await callback.answer()


# ════════════════════════════════════════════════════
#                   KANAL QO'SHISH
# ════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_add_channel")
async def cb_add_channel(callback: CallbackQuery, state: FSMContext, config):
    if callback.from_user.id not in config.ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)
    await state.set_state(AddChannelState.channel)
    try:
        await callback.message.edit_text(
            "📡 <b>Majburiy obuna kanali qo'shish</b>\n\n"
            "Kanal <b>username</b> yoki <b>ID</b> sini yuboring:\n\n"
            "📌 Misollar:\n"
            "• <code>@mening_kanalim</code>\n"
            "• <code>-1001234567890</code>\n\n"
            "⚠️ <b>Muhim:</b> Bot kanalda <b>admin</b> bo'lishi kerak!",
            reply_markup=cancel_admin_kb(),
        )
    except Exception:
        await callback.message.answer("📡 Kanal username yoki ID sini yuboring:", reply_markup=cancel_admin_kb())
    await callback.answer()


@router.message(AddChannelState.channel, F.text)
async def fsm_add_channel(message: Message, state: FSMContext, bot: Bot, db: Database):
    raw = message.text.strip()
    if raw.startswith("@"):
        chat_identifier = raw
    elif raw.lstrip("-").isdigit():
        chat_identifier = int(raw)
    else:
        return await message.answer(
            "❌ Noto'g'ri format!\nUsername: <code>@channel</code>\nID: <code>-1001234567890</code>",
            reply_markup=cancel_admin_kb(),
        )

    try:
        chat = await bot.get_chat(chat_identifier)
    except TelegramForbiddenError:
        return await message.answer(
            "❌ Botni kanalga admin qilib qo'shing, keyin qayta urinib ko'ring!",
            reply_markup=cancel_admin_kb(),
        )
    except TelegramAPIError:
        return await message.answer(
            "❌ Kanal topilmadi!\n• Username to'g'riligini tekshiring\n• Bot kanalda admin bo'lishi kerak",
            reply_markup=cancel_admin_kb(),
        )

    channel_id = chat.id
    username = f"@{chat.username}" if chat.username else ""
    title = chat.title or "Kanal"

    success = await db.add_channel(channel_id=channel_id, username=username, title=title)
    await state.clear()

    if success:
        await message.answer(
            f"✅ <b>Kanal muvaffaqiyatli qo'shildi!</b>\n\n"
            f"📡 Nom: <b>{escape(title)}</b>\n"
            f"🆔 ID: <code>{channel_id}</code>\n"
            f"👤 Username: {username or 'Mavjud emas (private kanal)'}",
            reply_markup=admin_main_kb(),
        )
    else:
        await message.answer(
            f"⚠️ <b>{escape(title)}</b> kanali allaqachon qo'shilgan!",
            reply_markup=admin_main_kb(),
        )


# ════════════════════════════════════════════════════
#                  KANAL O'CHIRISH
# ════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_del_channel")
async def cb_del_channel(callback: CallbackQuery, db: Database):
    channels = await db.get_channels()
    if not channels:
        try:
            await callback.message.edit_text("📋 Hozircha hech qanday kanal yo'q.", reply_markup=back_kb())
        except Exception:
            pass
        return await callback.answer()
    try:
        await callback.message.edit_text(
            "❌ <b>O'chirish uchun kanalni tanlang:</b>",
            reply_markup=channels_list_kb(channels, for_delete=True),
        )
    except Exception:
        await callback.message.answer("❌ Kanalni tanlang:", reply_markup=channels_list_kb(channels, for_delete=True))
    await callback.answer()


@router.callback_query(F.data.startswith("del_channel_"))
async def confirm_del_channel(callback: CallbackQuery, db: Database):
    ch_id = int(callback.data.replace("del_channel_", ""))
    success = await db.remove_channel(ch_id)
    text = "✅ Kanal muvaffaqiyatli o'chirildi!" if success else "❌ Kanal topilmadi."
    try:
        await callback.message.edit_text(text, reply_markup=admin_main_kb())
    except Exception:
        await callback.message.answer(text, reply_markup=admin_main_kb())
    await callback.answer()


# ════════════════════════════════════════════════════
#                 KANALLAR RO'YXATI
# ════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_channel_list")
async def cb_channel_list(callback: CallbackQuery, db: Database):
    channels = await db.get_channels()
    if not channels:
        try:
            await callback.message.edit_text(
                "📋 Hech qanday majburiy obuna kanali yo'q.\nAdmin paneldan kanal qo'shing.",
                reply_markup=back_kb(),
            )
        except Exception:
            pass
        return await callback.answer()
    try:
        await callback.message.edit_text(
            f"📡 <b>Majburiy obuna kanallari ({len(channels)} ta):</b>",
            reply_markup=channels_list_kb(channels, for_delete=False),
        )
    except Exception:
        pass
    await callback.answer()


# ════════════════════════════════════════════════════
#                    BROADCAST
# ════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_broadcast")
async def cb_broadcast(callback: CallbackQuery, state: FSMContext, config):
    if callback.from_user.id not in config.ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)
    await state.set_state(BroadcastState.message)
    try:
        await callback.message.edit_text(
            "📢 <b>Broadcast</b>\n\n"
            "Barcha foydalanuvchilarga yuboriladigan xabarni yuboring.\n"
            "(Matn, rasm, video — hammasi qo'llab-quvvatlanadi)",
            reply_markup=cancel_admin_kb(),
        )
    except Exception:
        await callback.message.answer("📢 Xabarni yuboring:", reply_markup=cancel_admin_kb())
    await callback.answer()


@router.message(BroadcastState.message)
async def fsm_broadcast_msg(message: Message, state: FSMContext):
    await state.update_data(broadcast_msg_id=message.message_id, broadcast_chat_id=message.chat.id)
    await state.set_state(BroadcastState.confirm)
    await message.answer(
        "📢 <b>Tasdiqlash</b>\n\n"
        "Yuqoridagi xabar barcha foydalanuvchilarga yuboriladi.\n"
        "Davom etasizmi?",
        reply_markup=broadcast_confirm_kb(),
    )


@router.callback_query(F.data == "broadcast_confirm", BroadcastState.confirm)
async def fsm_broadcast_confirm(callback: CallbackQuery, state: FSMContext, bot: Bot, db: Database):
    data = await state.get_data()
    msg_id = data.get("broadcast_msg_id")
    chat_id = data.get("broadcast_chat_id")
    await state.clear()

    user_ids = await db.get_user_ids()
    total = len(user_ids)

    try:
        progress_msg = await callback.message.edit_text(f"📤 Yuborilmoqda... 0/{total}")
    except Exception:
        progress_msg = await callback.message.answer(f"📤 Yuborilmoqda... 0/{total}")

    sent = failed = 0
    for uid in user_ids:
        try:
            await bot.forward_message(chat_id=uid, from_chat_id=chat_id, message_id=msg_id)
            sent += 1
        except Exception:
            failed += 1

        if (sent + failed) % 30 == 0:
            try:
                await progress_msg.edit_text(f"📤 Yuborilmoqda... {sent + failed}/{total}")
            except Exception:
                pass
        await asyncio.sleep(0.05)

    try:
        await progress_msg.edit_text(
            f"✅ <b>Broadcast yakunlandi!</b>\n\n"
            f"✔️ Muvaffaqiyatli: <b>{sent}</b>\n"
            f"❌ Xato: <b>{failed}</b>\n"
            f"📊 Jami: <b>{total}</b>",
            reply_markup=back_kb(),
        )
    except Exception:
        pass
    await callback.answer("✅ Broadcast yakunlandi!")


# ════════════════════════════════════════════════════
#                    SOZLAMALAR
# ════════════════════════════════════════════════════

@router.callback_query(F.data == "admin_settings")
async def cb_settings(callback: CallbackQuery):
    try:
        await callback.message.edit_text(
            "⚙️ <b>Sozlamalar markazi</b>\n\n"
            "Matnlarni yangilang yoki kanalga avto-post ishlashini tekshiring.",
            reply_markup=admin_settings_kb(),
        )
    except Exception:
        await callback.message.answer("⚙️ Sozlamalar:", reply_markup=admin_settings_kb())
    await callback.answer()


@router.callback_query(F.data == "settings_test_post")
async def cb_test_post_channel(callback: CallbackQuery, bot: Bot, db: Database, config):
    if callback.from_user.id not in config.ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)

    settings = await db.get_settings()
    raw_channel = str(settings.get("post_channel_id", "")).strip()
    if not raw_channel:
        await callback.message.edit_text(
            "⚠️ <b>Avto-post kanali ulanmagan.</b>\n\n"
            "Avval <b>Avto-post kanalini ulash</b> bo'limidan kanal ID yoki username kiriting.",
            reply_markup=admin_settings_kb(),
        )
        return await callback.answer()

    channel_id = normalize_chat_identifier(raw_channel)
    if channel_id is None:
        await callback.message.edit_text(
            "❌ <b>Saqlangan avto-post kanali formati noto'g'ri.</b>\n\n"
            "Kanalni qaytadan ulang: <code>-1001234567890</code> yoki <code>@kanal</code>.",
            reply_markup=admin_settings_kb(),
        )
        return await callback.answer()

    try:
        chat, is_ready = await validate_post_channel(bot, channel_id)
        if not is_ready:
            await callback.message.edit_text(
                "❌ <b>Avto-post tayyor emas.</b>\n\n"
                "Bot kanal admini bo'lishi va <b>post yuborish</b> huquqiga ega bo'lishi kerak.",
                reply_markup=admin_settings_kb(),
            )
            return await callback.answer()

        await bot.send_message(
            chat.id,
            "🧪 <b>Avto-post testi</b>\n\n"
            "✅ Bot kanalga post yubora oladi.\n"
            "Keyingi qo'shilgan kinolar shu kanalga avtomatik chiqadi.",
        )
    except TelegramForbiddenError:
        await callback.message.edit_text(
            "❌ <b>Bot kanalga kira olmayapti.</b>\n\n"
            "Botni kanalga admin qilib qo'shing va qayta tekshiring.",
            reply_markup=admin_settings_kb(),
        )
        return await callback.answer()
    except TelegramAPIError as e:
        await callback.message.edit_text(
            "❌ <b>Avto-post testi muvaffaqiyatsiz.</b>\n\n"
            f"<code>{escape(str(e))}</code>",
            reply_markup=admin_settings_kb(),
        )
        return await callback.answer()

    await callback.message.edit_text(
        f"✅ <b>Avto-post ishlayapti!</b>\n\n"
        f"📡 Kanal: <b>{escape(chat.title or str(chat.id))}</b>\n"
        f"🆔 ID: <code>{chat.id}</code>\n"
        f"🟢 Test xabar kanalga yuborildi.",
        reply_markup=admin_settings_kb(),
    )
    await callback.answer("✅ Avto-post tekshirildi!")


@router.callback_query(F.data.in_(set(SETTINGS_MAP.keys())))
async def cb_edit_setting(callback: CallbackQuery, state: FSMContext, config):
    if callback.from_user.id not in config.ADMIN_IDS:
        return await callback.answer("❌ Ruxsat yo'q", show_alert=True)
    key, label = SETTINGS_MAP[callback.data]
    await state.set_state(EditSettingState.value)
    await state.update_data(setting_key=key, setting_label=label)
    try:
        await callback.message.edit_text(
            f"✏️ <b>{label}</b>\n\n"
            "Yangi matnni yuboring.\n"
            "HTML teglardan foydalanishingiz mumkin: "
            "<code>&lt;b&gt;</code>, <code>&lt;i&gt;</code>, <code>&lt;code&gt;</code>",
            reply_markup=cancel_admin_kb(),
        )
    except Exception:
        await callback.message.answer(
            f"✏️ {label} uchun yangi matn yuboring:",
            reply_markup=cancel_admin_kb(),
        )
    await callback.answer()


@router.message(EditSettingState.value, F.text)
async def fsm_save_setting(message: Message, state: FSMContext, bot: Bot, db: Database):
    data = await state.get_data()
    key = data["setting_key"]
    label = data["setting_label"]
    value = message.text.strip()

    # post_channel_id — maxsus validatsiya
    if key == "post_channel_id":
        raw = value.strip()
        if raw in ("-", ""):
            await db.update_setting(key, "")
            await state.clear()
            return await message.answer(
                "✅ <b>Avto-post kanali o'chirildi.</b>",
                reply_markup=admin_main_kb(),
            )

        channel_id = normalize_chat_identifier(raw)
        if channel_id is None:
            return await message.answer(
                "❌ Noto'g'ri format!\n"
                "• Kanal ID: <code>-1001234567890</code>\n"
                "• Username: <code>@kanalim</code>\n"
                "• O'chirish uchun: <code>-</code>",
                reply_markup=cancel_admin_kb(),
            )

        try:
            chat, is_bot_admin = await validate_post_channel(bot, channel_id)
        except TelegramForbiddenError:
            return await message.answer(
                "❌ Botni kanalga <b>admin</b> qilib qo'shing!",
                reply_markup=cancel_admin_kb(),
            )
        except TelegramAPIError:
            return await message.answer(
                "❌ Kanal topilmadi! ID yoki username to'g'riligini tekshiring.",
                reply_markup=cancel_admin_kb(),
            )

        if not is_bot_admin:
            return await message.answer(
                "❌ Bot kanalda post joylay olmaydi.\n\n"
                "Botni kanalga <b>admin</b> qiling va <b>post yuborish</b> huquqini yoqing.",
                reply_markup=cancel_admin_kb(),
            )

        await db.update_setting(key, str(chat.id))
        await state.clear()
        return await message.answer(
            f"✅ <b>Avto-post kanali saqlandi!</b>\n\n"
            f"📡 Kanal: <b>{escape(chat.title or str(chat.id))}</b>\n"
            f"🆔 ID: <code>{chat.id}</code>\n"
            f"🟢 Holat: <b>post yuborishga tayyor</b>",
            reply_markup=admin_main_kb(),
        )

    await db.update_setting(key, value)
    await state.clear()
    await message.answer(
        f"✅ <b>{escape(label)}</b> muvaffaqiyatli yangilandi!",
        reply_markup=admin_main_kb(),
    )
