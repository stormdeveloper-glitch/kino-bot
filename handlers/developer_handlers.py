"""
Developer handlerlari (aiogram v3)
"""
import os
import platform
from datetime import datetime

import psutil

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery

from keyboards.developer_keyboards import developer_main_kb, dev_back_kb

router = Router()


@router.message(F.text == "💻 Developer")
async def cmd_developer(message: Message, config):
    if message.from_user.id != config.DEVELOPER_ID:
        return
    await message.answer(
        "💻 <b>Developer Tizimi</b>\n\nBoshqarish uchun bo'limni tanlang:",
        reply_markup=developer_main_kb(),
    )


@router.callback_query(F.data == "dev_menu")
async def cb_dev_menu(callback: CallbackQuery, config):
    if callback.from_user.id != config.DEVELOPER_ID:
        return await callback.answer("❌ Ruxsat berilmagan", show_alert=True)
    await callback.message.edit_text(
        "💻 <b>Developer Tizimi</b>\n\nBoshqarish uchun bo'limni tanlang:",
        reply_markup=developer_main_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "dev_stats")
async def cb_dev_stats(callback: CallbackQuery, config):
    if callback.from_user.id != config.DEVELOPER_ID:
        return await callback.answer("❌ Ruxsat berilmagan", show_alert=True)
    process = psutil.Process(os.getpid())
    mem_info = process.memory_info()
    text = (
        "📊 <b>Tizim statistikasi</b>\n\n"
        f"🖥 <b>OS:</b> <code>{platform.system()} {platform.release()}</code>\n"
        f"🐍 <b>Python:</b> <code>{platform.python_version()}</code>\n"
        f"📈 <b>RAM:</b> <code>{mem_info.rss / 1024 / 1024:.2f} MB</code>\n"
        f"⏱ <b>Uptime:</b> <code>{datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')}</code> dan beri\n"
        f"🆔 <b>Process ID:</b> <code>{os.getpid()}</code>"
    )
    await callback.message.edit_text(text, reply_markup=dev_back_kb())
    await callback.answer()


@router.callback_query(F.data == "dev_env")
async def cb_dev_env(callback: CallbackQuery, config):
    if callback.from_user.id != config.DEVELOPER_ID:
        return await callback.answer("❌ Ruxsat berilmagan", show_alert=True)
    text = (
        "⚙️ <b>Muhit o'zgaruvchilari (Xavfsiz)</b>\n\n"
        f"🆔 <b>Developer ID:</b> <code>{config.DEVELOPER_ID}</code>\n"
        f"👮 <b>Adminlar:</b> <code>{config.ADMIN_IDS}</code>\n"
        f"📁 <b>Data Dir:</b> <code>{config.DATA_DIR}</code>\n"
        f"🌐 <b>Environment:</b> <code>{os.getenv('RAILWAY_ENVIRONMENT', 'Local')}</code>"
    )
    await callback.message.edit_text(text, reply_markup=dev_back_kb())
    await callback.answer()


@router.callback_query(F.data == "dev_exit")
async def cb_dev_exit(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer("Chiqildi")
