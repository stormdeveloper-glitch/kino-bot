"""
Majburiy obuna middleware (aiogram v3)
"""
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject

from keyboards.user_keyboards import subscription_kb

SKIP_COMMANDS = {"/start", "/admin", "/help"}
SKIP_CALLBACKS = {"check_sub", "cancel"}


class SubscriptionMiddleware(BaseMiddleware):
    def __init__(self, bot, db, config):
        self.bot = bot
        self.db = db
        self.config = config

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        is_callback = isinstance(event, CallbackQuery)

        if is_callback:
            user = event.from_user
            cb_data = event.data or ""
            # Obuna tekshirishni o'tkazib yuborish
            if any(cb_data == s or cb_data.startswith(s) for s in SKIP_CALLBACKS):
                return await handler(event, data)
        elif isinstance(event, Message):
            user = event.from_user
            if not user:
                return await handler(event, data)
            text = event.text or ""
            # Buyruqlarni o'tkazib yuborish
            if any(text.startswith(cmd) for cmd in SKIP_COMMANDS):
                return await handler(event, data)
        else:
            return await handler(event, data)

        if not user:
            return await handler(event, data)

        # Adminni o'tkazib yuborish
        if user.id in self.config.ADMIN_IDS:
            return await handler(event, data)

        channels = await self.db.get_channels()
        if not channels:
            return await handler(event, data)

        not_subscribed = await self._check_subscriptions(user.id, channels)
        if not not_subscribed:
            return await handler(event, data)

        # Obuna bo'lmagan — xabar yuborish
        settings = await self.db.get_settings()
        sub_text = settings.get(
            "not_subscribed_text",
            "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling!",
        )
        kb = subscription_kb(not_subscribed)

        if is_callback:
            try:
                await event.message.edit_text(sub_text, reply_markup=kb)
            except Exception:
                await self.bot.send_message(event.message.chat.id, sub_text, reply_markup=kb)
            await event.answer("⚠️ Avval kanallarga obuna bo'ling!")
        else:
            await self.bot.send_message(event.chat.id, sub_text, reply_markup=kb)

        # Handler chaqirilmaydi — update bekor qilinadi

    async def _check_subscriptions(self, user_id: int, channels: list) -> list:
        not_subscribed = []
        for channel in channels:
            try:
                member = await self.bot.get_chat_member(channel["id"], user_id)
                if member.status in ("left", "kicked"):
                    not_subscribed.append(channel)
            except Exception:
                pass
        return not_subscribed
