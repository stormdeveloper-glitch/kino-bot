"""
Admin klaviaturalari (aiogram v3)
"""
from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def admin_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎬 Kino qo'shish", callback_data="admin_add_movie", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text="🗑 Kino o'chirish", callback_data="admin_del_movie", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton(text="📋 Kinolar ro'yxati", callback_data="admin_movie_list", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats", style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton(text="📡 Kanal qo'shish", callback_data="admin_add_channel", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text="❌ Kanal o'chirish", callback_data="admin_del_channel", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton(text="📋 Kanallar ro'yxati", callback_data="admin_channel_list", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast", style=ButtonStyle.SUCCESS),
        ],
        [InlineKeyboardButton(text="⚙️ Sozlamalar va avto-post", callback_data="admin_settings", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="📖 Pro qo'llanma", callback_data="guide_main", style=ButtonStyle.PRIMARY)],
    ])


def admin_settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Xush kelibsiz matni", callback_data="settings_welcome", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="✏️ Bot haqida matni", callback_data="settings_about", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="✏️ Obuna eslatma matni", callback_data="settings_not_sub", style=ButtonStyle.PRIMARY)],
        [InlineKeyboardButton(text="📢 Avto-post kanalini ulash", callback_data="settings_post_channel", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton(text="🧪 Avto-postni tekshirish", callback_data="settings_test_post", style=ButtonStyle.SUCCESS)],
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_back", style=ButtonStyle.DANGER)],
    ])


def confirm_kb(action: str, item_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"confirm_{action}_{item_id}", style=ButtonStyle.DANGER),
            InlineKeyboardButton(text="❌ Yo'q", callback_data="admin_back", style=ButtonStyle.PRIMARY),
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
            buttons.append([InlineKeyboardButton(text=f"🗑 {label}", callback_data=f"del_channel_{ch_id}", style=ButtonStyle.DANGER)])
        else:
            buttons.append([InlineKeyboardButton(text=label, callback_data="noop", style=ButtonStyle.PRIMARY)])
    buttons.append([InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_back", style=ButtonStyle.DANGER)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Orqaga", callback_data="admin_back", style=ButtonStyle.DANGER)]
    ])


def cancel_admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel_fsm", style=ButtonStyle.DANGER)]
    ])


def broadcast_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Yuborish", callback_data="broadcast_confirm", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton(text="❌ Bekor", callback_data="admin_cancel_fsm", style=ButtonStyle.DANGER),
        ]
    ])


# ════════════════ QO'LLANMA KLAVIATURALARI ════════════════

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
    buttons = [[InlineKeyboardButton(text=label, callback_data=cb)]
               for cb, label in GUIDE_SECTIONS.items()]
    buttons.append([InlineKeyboardButton(text="◀️ Admin panelga", callback_data="admin_back", style=ButtonStyle.PRIMARY)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def guide_nav_kb(current: str) -> InlineKeyboardMarkup:
    idx = GUIDE_ORDER.index(current)
    nav_row = []
    if idx > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Oldingi", callback_data=GUIDE_ORDER[idx - 1], style=ButtonStyle.PRIMARY))
    nav_row.append(InlineKeyboardButton(text="📋 Ro'yxat", callback_data="guide_main", style=ButtonStyle.PRIMARY))
    if idx < len(GUIDE_ORDER) - 1:
        nav_row.append(InlineKeyboardButton(text="Keyingi ➡️", callback_data=GUIDE_ORDER[idx + 1], style=ButtonStyle.PRIMARY))
    return InlineKeyboardMarkup(inline_keyboard=[
        nav_row,
        [InlineKeyboardButton(text="🏠 Admin panelga", callback_data="admin_back", style=ButtonStyle.PRIMARY)],
    ])
