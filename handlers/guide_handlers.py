"""
Admin qo'llanmasi handlerlari (aiogram v3)
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery

from keyboards.admin_keyboards import guide_main_kb, guide_nav_kb, GUIDE_SECTIONS, GUIDE_ORDER

router = Router()

GUIDE_TEXTS: dict = {
    "guide_start": (
        "🚀 <b>BOSHLASH — Bot bilan tanishuv</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Bu bot foydalanuvchilarga kino kodi orqali kino yuboradi.\n\n"
        "<b>Qanday ishlaydi?</b>\n"
        "1️⃣ Admin kinoni botga yuklaydi va unga kod beradi\n"
        "2️⃣ Foydalanuvchi botga kodni yozadi\n"
        "3️⃣ Bot kinoni darhol yuboradi\n\n"
        "<b>Admin panelni ochish:</b>\n"
        "Botga <code>/admin</code> yuboring\n\n"
        "<b>Asosiy bo'limlar:</b>\n"
        "📡 <b>Kanal ulash</b> — Majburiy obuna kanalini qo'shish\n"
        "🎬 <b>Kino qo'shish</b> — Yangi kino yuklash\n"
        "🗑 <b>Kino o'chirish</b> — Mavjud kinoni o'chirish\n"
        "🔐 <b>Majburiy obuna</b> — Qanday ishlashini tushuntirish\n"
        "📢 <b>Broadcast</b> — Barcha foydalanuvchilarga xabar\n"
        "⚙️ <b>Sozlamalar</b> — Bot matnlarini tahrirlash\n\n"
        "👇 <b>Keyingi bo'limni o'qing yoki kerakli bo'limni tanlang</b>"
    ),
    "guide_channel": (
        "📡 <b>KANAL ULASH — Majburiy obuna kanali</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Foydalanuvchilar kanalingizga obuna bo'lmasa bot ularga javob bermaydi.\n\n"
        "<b>1-qadam: Botni kanalga admin qiling</b>\n"
        "• Kanalingizga kiring\n"
        "• <b>Kanal sozlamalari → Administratorlar</b>\n"
        "• <b>Administrator qo'shish</b> tugmasini bosing\n"
        "• Botingizni qidiring\n"
        "• Faqat <b>«A'zolarni ko'rish»</b> huquqi yetarli\n"
        "• <b>Saqlash</b> bosing ✅\n\n"
        "<b>2-qadam: Admin paneldan kanal qo'shing</b>\n"
        "• <code>/admin</code> → <b>📡 Kanal qo'shish</b>\n\n"
        "<b>Public kanal:</b> <code>@kanal_username</code>\n"
        "<b>Private kanal ID:</b> <code>-1001234567890</code>\n\n"
        "✅ <b>Muvaffaqiyatli bo'lsa:</b>\n"
        "<i>«Kanal muvaffaqiyatli qo'shildi!»</i> xabari keladi\n\n"
        "⚠️ <b>Xato bo'lsa:</b>\n"
        "• Bot kanalda admin emas — avval 1-qadamni bajaring\n"
        "• Username noto'g'ri — <code>@</code> bilan yozing"
    ),
    "guide_movie_add": (
        "🎬 <b>KINO QO'SHISH — To'liq jarayon</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Qadamlar:</b>\n"
        "<code>/admin</code> → <b>🎬 Kino qo'shish</b>\n\n"
        "<b>1-qadam — Kod kiriting</b>\n"
        "• Faqat <b>kichik harf va raqam</b> ishlating\n"
        "• Maksimal 50 belgi\n"
        "• Misol: <code>001</code>, <code>avatar2</code>\n\n"
        "<b>2-qadam — Fayl yuboring</b>\n"
        "💡 Sifat saqlanishi uchun:\n"
        "Paperclip 📎 → <b>File</b> (Hujjat) → kinoni tanlang\n\n"
        "<b>3-qadam — Nom kiriting</b>\n"
        "Misol: <code>Avatar: The Way of Water</code>\n\n"
        "<b>4-qadam — Tavsif (ixtiyoriy)</b>\n"
        "Kerak bo'lmasa <code>-</code> yuboring\n\n"
        "<b>5-qadam — Poster/Treyler (ixtiyoriy)</b>\n"
        "Kerak bo'lmasa <code>-</code> yuboring\n\n"
        "✅ Tayyor! Endi foydalanuvchi kodni yuborganda kino keladi."
    ),
    "guide_movie_del": (
        "🗑 <b>KINO O'CHIRISH</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Kinoni o'chirish:</b>\n"
        "<code>/admin</code> → <b>🗑 Kino o'chirish</b>\n"
        "• Kinoning kodini yuboring\n"
        "• Tasdiqlash so'raladi → <b>«Ha, o'chirish»</b>\n\n"
        "<b>Kinolar ro'yxatini ko'rish:</b>\n"
        "<code>/admin</code> → <b>📋 Kinolar ro'yxati</b>\n\n"
        "⚠️ <b>Eslatma:</b>\n"
        "O'chirilgan kinoni qaytarib bo'lmaydi."
    ),
    "guide_sub": (
        "🔐 <b>MAJBURIY OBUNA — Qanday ishlaydi?</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Foydalanuvchi botga yozganda — har bir xabar oldidan\n"
        "bot kanalingizga obuna bo'lganini <b>avtomatik tekshiradi.</b>\n\n"
        "<b>Obuna bo'lmagan foydalanuvchiga:</b>\n"
        "• Kanal havolalari bilan xabar keladi\n"
        "• «✅ Obuna bo'ldim, tekshir!» tugmasi ko'rinadi\n"
        "• Obuna bo'lgunga qadar hech narsa ishlamaydi\n\n"
        "<b>Bir nechta kanal:</b>\n"
        "Xohlagancha kanal qo'shing — foydalanuvchi\n"
        "<b>barchasiga</b> obuna bo'lishi kerak bo'ladi.\n\n"
        "⚠️ <b>Muhim:</b>\n"
        "Kanal o'chirib tashlansa yoki bot adminlikdan\n"
        "olib tashlansa — obuna tekshiruvi o'tkazib yuboriladi!"
    ),
    "guide_broadcast": (
        "📢 <b>BROADCAST — Barcha foydalanuvchilarga xabar</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>Qanday ishlatiladi:</b>\n"
        "<code>/admin</code> → <b>📢 Broadcast</b>\n"
        "• Yubormoqchi bo'lgan xabarni yuboring\n"
        "• Tasdiqlash so'raladi\n"
        "• <b>«✅ Yuborish»</b> bosing\n\n"
        "<b>Natija xabari:</b>\n"
        "✔️ Muvaffaqiyatli: <b>280</b>\n"
        "❌ Xato: <b>20</b>\n\n"
        "💡 <b>Xato bo'lishlari normal:</b>\n"
        "• Foydalanuvchi botni bloklagan\n"
        "• Foydalanuvchi Telegramni o'chgan\n\n"
        "⚠️ Broadcast yuborilgandan so'ng bekor qilib bo'lmaydi."
    ),
    "guide_settings": (
        "⚙️ <b>SOZLAMALAR — Bot matnlarini tahrirlash</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<code>/admin</code> → <b>⚙️ Sozlamalar</b>\n\n"
        "1️⃣ <b>Xush kelibsiz matni</b> — /start ga javob\n"
        "2️⃣ <b>Bot haqida matni</b> — «ℹ️ Bot haqida» tugmasi\n"
        "3️⃣ <b>Obuna eslatma matni</b> — Obuna bo'lmagan foydalanuvchiga\n"
        "4️⃣ <b>Avto-post kanali ID</b> — Yangi kino qo'shilganda kanal\n\n"
        "<b>HTML formatlash:</b>\n"
        "<code>&lt;b&gt;qalin&lt;/b&gt;</code> → <b>qalin</b>\n"
        "<code>&lt;i&gt;kursiv&lt;/i&gt;</code> → <i>kursiv</i>\n"
        "<code>&lt;code&gt;kod&lt;/code&gt;</code> → <code>kod</code>"
    ),
    "guide_tips": (
        "💡 <b>FOYDALI MASLAHATLAR</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "<b>📁 Kino fayl yuborish usuli:</b>\n"
        "📎 qo'shimcha → <b>Fayl</b> (File) sifatida yuboring\n\n"
        "<b>🔑 Kino kodlari:</b>\n"
        "• Qisqa kod ishlating: <code>001</code>, <code>002</code>\n"
        "• Kanalda e'lon qilayotganda kodni yozing\n\n"
        "<b>💾 Ma'lumotlar qayerda saqlanadi?</b>\n"
        "Railway Volume — <code>/app/data</code> papkasida:\n"
        "• <code>movies.json</code> — kinolar\n"
        "• <code>channels.json</code> — kanallar\n"
        "• <code>users.json</code> — foydalanuvchilar\n"
        "• <code>settings.json</code> — sozlamalar\n\n"
        "<b>🔄 Bot ishlamay qolsa:</b>\n"
        "• Railway → Logs bo'limini tekshiring\n"
        "• BOT_TOKEN to'g'riligini tekshiring\n"
        "• Redeploy qiling\n\n"
        "✅ <b>Qo'llanmani o'qib chiqdingiz!</b>\n"
        "Endi botni bemalol boshqara olasiz 🎉"
    ),
}


@router.callback_query(F.data == "guide_main")
async def cb_guide_main(callback: CallbackQuery):
    text = (
        "📖 <b>ADMIN QO'LLANMASI</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "O'qimoqchi bo'lgan bo'limni tanlang:\n\n"
        "🚀 <b>Boshlash</b> — Umumiy ma'lumot\n"
        "📡 <b>Kanal ulash</b> — Majburiy obuna\n"
        "🎬 <b>Kino qo'shish</b> — Yangi kino yuklash\n"
        "🗑 <b>Kino o'chirish</b> — Kino o'chirish\n"
        "🔐 <b>Majburiy obuna</b> — Qanday ishlashini bilish\n"
        "📢 <b>Broadcast</b> — Barcha foydalanuvchilarga xabar\n"
        "⚙️ <b>Sozlamalar</b> — Bot matnlarini tahrirlash\n"
        "💡 <b>Maslahatlar</b> — Foydali ko'rsatmalar\n"
    )
    try:
        await callback.message.edit_text(text, reply_markup=guide_main_kb())
    except Exception:
        await callback.message.answer(text, reply_markup=guide_main_kb())
    await callback.answer()


@router.callback_query(F.data.in_(set(GUIDE_TEXTS.keys())))
async def cb_guide_section(callback: CallbackQuery):
    section_key = callback.data
    text = GUIDE_TEXTS.get(section_key, "❌ Bu bo'lim topilmadi.")
    kb = guide_nav_kb(section_key)
    try:
        await callback.message.edit_text(text, reply_markup=kb)
    except Exception:
        await callback.message.answer(text, reply_markup=kb)
    await callback.answer()
