"""
Admin klaviaturalari (aiogram v3)
"""
from aiogram.types import InlineKeyboardMarkup

from keyboards.button_styles import ibtn


def admin_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            ibtn("🎬 Kino qo'shish", callback_data="admin_add_movie"),
            ibtn("🗑 Kino o'chirish", callback_data="admin_del_movie"),
        ],
        [
            ibtn("📋 Kinolar ro'yxati", callback_data="admin_movie_list"),
            ibtn("📊 Statistika", callback_data="admin_stats"),
        ],
        [
            ibtn("📡 Kanal qo'shish", callback_data="admin_add_channel"),
            ibtn("❌ Kanal o'chirish", callback_data="admin_del_channel"),
        ],
        [
            ibtn("📋 Kanallar ro'yxati", callback_data="admin_channel_list"),
            ibtn("📢 Broadcast", callback_data="admin_broadcast"),
        ],
        [ibtn("⚙️ Sozlamalar va avto-post", callback_data="admin_settings")],
        [ibtn("📖 Pro qo'llanma", callback_data="guide_main")],
    ])


def admin_settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [ibtn("✏️ Xush kelibsiz matni", callback_data="settings_welcome")],
        [ibtn("✏️ Bot haqida matni", callback_data="settings_about")],
        [ibtn("✏️ Obuna eslatma matni", callback_data="settings_not_sub")],
        [ibtn("📢 Avto-post kanalini ulash", callback_data="settings_post_channel")],
        [ibtn("🧪 Avto-postni tekshirish", callback_data="settings_test_post")],
        [ibtn("◀️ Orqaga", callback_data="admin_back")],
    ])


def confirm_kb(action: str, item_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            ibtn("✅ Ha, o'chirish", callback_data=f"confirm_{action}_{item_id}"),
            ibtn("❌ Yo'q", callback_data="admin_back"),
        ]
    ])


def channels_list_kb(channels: list, for_delete: bool = False) -> InlineKeyboardMarkup:
    buttons = []
    for ch in channels:
        ch_id = ch["id"]
        title = ch.get("title", "Kanal")
        username = ch.get("username", "")
        label = f"📡 {title} ({username})" if username else f"📡 {title}"
        if for_delete:
            buttons.append([ibtn(f"🗑 {label}", callback_data=f"del_channel_{ch_id}")])
        else:
            buttons.append([ibtn(label, callback_data="noop")])
    buttons.append([ibtn("◀️ Orqaga", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [ibtn("◀️ Orqaga", callback_data="admin_back")]
    ])


def cancel_admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [ibtn("❌ Bekor qilish", callback_data="admin_cancel_fsm")]
    ])


def broadcast_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            ibtn("✅ Yuborish", callback_data="broadcast_confirm"),
            ibtn("❌ Bekor", callback_data="admin_cancel_fsm"),
        ]
    ])


GUIDE_SECTIONS = {
    "guide_start":      "🚀 Boshlash (1/8)",
    "guide_channel":    "📡 Kanal ulash (2/8)",
    "guide_movie_add":  "🎬 Kino qo'shish (3/8)",
    "guide_movie_del":  "🗑 Kino o'chirish (4/8)",
    "guide_sub":        "🔐 Majburiy obuna (5/8)",
    "guide_broadcast":  "📢 Broadcast (6/8)",
    "guide_settings":   "⚙️ Sozlamalar (7/8)",
    "guide_tips":       "💡 Maslahatlar (8/8)",
}

GUIDE_ORDER = list(GUIDE_SECTIONS.keys())


def guide_main_kb() -> InlineKeyboardMarkup:
    buttons = [[ibtn(label, callback_data=cb)] for cb, label in GUIDE_SECTIONS.items()]
    buttons.append([ibtn("◀️ Admin panelga", callback_data="admin_back")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def guide_nav_kb(current: str) -> InlineKeyboardMarkup:
    idx = GUIDE_ORDER.index(current)
    nav_row = []
    if idx > 0:
        nav_row.append(ibtn("⬅️ Oldingi", callback_data=GUIDE_ORDER[idx - 1]))
    nav_row.append(ibtn("📋 Ro'yxat", callback_data="guide_main"))
    if idx < len(GUIDE_ORDER) - 1:
        nav_row.append(ibtn("Keyingi ➡️", callback_data=GUIDE_ORDER[idx + 1]))
    return InlineKeyboardMarkup(inline_keyboard=[
        nav_row,
        [ibtn("🏠 Admin panelga", callback_data="admin_back")],
    ])
