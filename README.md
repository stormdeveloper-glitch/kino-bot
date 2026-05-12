# 🎬 Kino Bot — To'liq Qo'llanma

> Bu qo'llanma botni **noldan** o'rnatib, ishga tushirishga yordam beradi.  
> Dasturlash bilmagan odam ham o'qib tushuna oladi.

---

## 📋 Mundarija

1. [Bot nima qila oladi?](#1-bot-nima-qila-oladi)
2. [Tayyorgarlik](#2-tayyorgarlik)
3. [Telegram bot yaratish](#3-telegram-bot-yaratish)
4. [Admin ID ni topish](#4-admin-id-ni-topish)
5. [Loyihani yuklash](#5-loyihani-yuklash)
6. [Railwayga deploy qilish](#6-railwayga-deploy-qilish)
7. [Railway Volume sozlash](#7-railway-volume-sozlash)
8. [Muhit o'zgaruvchilarini sozlash](#8-muhit-ozgaruvchilarini-sozlash)
9. [Admin panel ishlatish](#9-admin-panel-ishlatish)
10. [Majburiy obuna kanali qo'shish](#10-majburiy-obuna-kanali-qoshish)
11. [Kino qo'shish](#11-kino-qoshish)
12. [Foydalanuvchi uchun ko'rsatmalar](#12-foydalanuvchi-uchun-korsatmalar)
13. [Ko'p so'raladigan savollar](#13-kop-soraladigan-savollar)

---

## 1. Bot nima qila oladi?

| Xususiyat | Tavsif |
|-----------|--------|
| 🎬 Kino yuborish | Foydalanuvchi kod yuborganda kino avtomatik keladi |
| 📡 Majburiy obuna | Foydalanuvchi ko'rsatilgan kanallarga obuna bo'lmasa bot ishlamaydi |
| 🛠 Admin panel | Kinolarni qo'shish, o'chirish, boshqarish |
| 📢 Broadcast | Barcha foydalanuvchilarga bir vaqtda xabar yuborish |
| 📊 Statistika | Foydalanuvchilar, kinolar, ko'rishlar soni |
| ⚙️ Sozlamalar | Xush kelibsiz matni va boshqa matnlarni tahrirlash |
| 💾 Volume saqlash | Ma'lumotlar Railway volumeda saqlanadi (o'chib ketmaydi) |

---

## 2. Tayyorgarlik

Sizga kerak bo'ladi:

- [ ] **Telegram** akkaunt
- [ ] **GitHub** akkaunt — [github.com](https://github.com) da ro'yxatdan o'ting
- [ ] **Railway** akkaunt — [railway.app](https://railway.app) da GitHub bilan kiring
- [ ] **BotFather** — @BotFather dan token olish

---

## 3. Telegram bot yaratish

**Qadamlar:**

1. Telegramda **@BotFather** ni oching
2. `/newbot` yuboring
3. Bot uchun **ism** kiriting (masalan: `Mening Kino Botim`)
4. Bot uchun **username** kiriting — oxiri `bot` bilan tugashi kerak  
   (masalan: `mening_kino_bot`)
5. BotFather sizga shunday token beradi:

```
Yaxshi! Bot yaratildi. Tokeningiz:
1234567890:ABCDefGhIJKlmNoPQRsTUVwxyZ
```

> ⚠️ **Bu tokenni hech kimga bermang!** U botingizni boshqarish kaliti.

---

## 4. Admin ID ni topish

Sizning Telegram ID ingizni bilish kerak:

1. **@userinfobot** ga `/start` yuboring
2. U sizga shunday xabar yuboradi:
   ```
   Your account ID: 123456789
   ```
3. Bu raqamni eslab qoling — bu sizning **Admin ID** ingiz.

---

## 5. Loyihani yuklash

### GitHub orqali (tavsiya etiladi):

1. [github.com](https://github.com) ga kiring
2. Yangi repository yarating:
   - `+` tugmasini bosing → **New repository**
   - Nom: `kino-bot`
   - **Private** tanlang
   - **Create repository** bosing
3. Barcha bot fayllarini shu repositoryga yuklang

### Fayl tuzilmasi to'g'ri bo'lishi kerak:

```
kino-bot/
├── bot.py
├── config.py
├── requirements.txt
├── Procfile
├── .env.example
├── handlers/
│   ├── __init__.py
│   ├── user_handlers.py
│   └── admin_handlers.py
├── keyboards/
│   ├── __init__.py
│   ├── user_keyboards.py
│   └── admin_keyboards.py
├── middlewares/
│   ├── __init__.py
│   └── subscription_middleware.py
└── utils/
    ├── __init__.py
    └── database.py
```

---

## 6. Railwayga deploy qilish

1. [railway.app](https://railway.app) ga kiring
2. **New Project** bosing
3. **Deploy from GitHub repo** tanlang
4. Yaratgan `kino-bot` repositoryingizni tanlang
5. Railway avtomatik deploy qila boshlaydi

> ⏳ Deploy 1-2 daqiqa oladi. Hozircha **Volume** va **Environment** ni sozlash kerak.

---

## 7. Railway Volume sozlash

> Ma'lumotlar (kinolar, foydalanuvchilar) `/app/data` papkasida saqlanadi.  
> Volume bo'lmasa, bot qayta ishga tushganda **barcha ma'lumotlar o'chadi!**

**Volume yaratish:**

1. Railway dashboard da loyihangizni oching
2. Chap panelda **+ New** bosing
3. **Volume** tanlang
4. Sozlamalar:
   - **Mount Path**: `/app/data`
5. **Create** bosing

✅ Endi ma'lumotlar o'chib ketmaydi!

---

## 8. Muhit o'zgaruvchilarini sozlash

1. Railway da xizmatni oching (Service)
2. **Variables** bo'limiga o'ting
3. Quyidagilarni qo'shing:

| O'zgaruvchi | Qiymat | Tavsif |
|-------------|--------|--------|
| `BOT_TOKEN` | `1234567890:ABCDef...` | BotFather dan olgan token |
| `ADMIN_IDS` | `123456789` | Sizning Telegram ID ingiz |
| `DEVELOPER_ID` | `123456789` | (Ixtiyoriy) Xatoliklar yuboriladigan ID |
| `ADMIN_USER` | `@admin` | (Ixtiyoriy) Yordam bo'limidagi admin username |
| `DATA_DIR` | `/app/data` | Volume mount path |

**Bir nechta admin qo'shish:**
```
ADMIN_IDS=123456789,987654321,111222333
```

4. **Deploy** bosing (o'zgaruvchilar saqlangandan keyin bot qayta ishga tushadi)

---

## 9. Admin panel ishlatish

Bot ishga tushgandan keyin:

1. Botga `/admin` yuboring
2. Quyidagi menyu ochiladi:

```
🛠 Admin Panel

[ 🎬 Kino qo'shish ]  [ 🗑 Kino o'chirish ]
[ 📋 Kinolar ro'yxati ] [ 📊 Statistika    ]
[ 📡 Kanal qo'shish ]  [ ❌ Kanal o'chirish ]
[ 📋 Kanallar ro'yxati ] [ 📢 Broadcast    ]
[ ⚙️ Sozlamalar                            ]
```

---

## 10. Majburiy obuna kanali qo'shish

> Bu **eng muhim qadam** — foydalanuvchilar kanalingizga obuna bo'lmaguncha bot ishlamaydi.

### Botni kanalga admin qilish (OLDIN BAJARING!):

1. Kanalingizni oching
2. **Kanal sozlamalari** → **Administratorlar**
3. **Administrator qo'shish** → Botingizni qidiring
4. **Faqat quyidagi huquqni qoldiring:**
   - ✅ Xabarlarni o'qish (Foydalanuvchilarni tekshirish uchun)
5. **Saqlash** bosing

### Kanal qo'shish (Admin paneldan):

1. `/admin` → **📡 Kanal qo'shish** bosing
2. Bot so'raydi: "Kanal username yoki ID sini yuboring"
3. Yuboring:
   - Public kanal uchun: `@mening_kanalim`
   - Private kanal uchun ID: `-1001234567890`

**Private kanal ID sini topish:**

1. @username_to_id_bot ga kanalingizni forward qiling
2. Yoki: Kanal linkidan `t.me/c/XXXXXXXXXX/1` — bu XXXXXXXXXX raqam, oldiga `-100` qo'shing

✅ **Muvaffaqiyatli bo'lsa:** `Kanal muvaffaqiyatli qo'shildi!` xabari keladi.

### Natija:

Endi foydalanuvchi boting'ga yozsa:
```
⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:

[ 📢 Mening Kanalim ]

[ ✅ Obuna bo'ldim, tekshir! ]
```

---

## 11. Kino qo'shish

### Qadam 1: `/admin` → **🎬 Kino qo'shish**

### Qadam 2: Kod kiriting
```
Bot: Kino kodini yuboring (masalan: 001, avatar2, spiderman)
Siz: 001
```

> 📌 Foydalanuvchilar shu kodni yuborsa kinoni oladi!

### Qadam 3: Faylni yuboring
```
Bot: Kino faylini yuboring (Video yoki Hujjat)
Siz: [Video yoki Dokument fayl yuborasiz]
```

> ⚠️ **Katta fayllar uchun:** Telegramda kompressiyasiz yuborish uchun  
> "File" sifatida yuboring (video sifatida emas) → shunda sifat yo'qolmaydi.

### Qadam 4: Nom kiriting
```
Bot: Kino nomini yuboring
Siz: Avatar: The Way of Water
```

### Qadam 5: Tavsif (ixtiyoriy)
```
Bot: Qo'shimcha matn yuboring (yoki - yuboring)
Siz: 🎬 Janr: Fantastika | Yil: 2022 | Til: O'zbekcha dublyaj
```

### Qadam 6: Avto-post Rasm/Video (ixtiyoriy)
```
Bot: Avto-post va ro'yxat uchun rasm (poster) yoki qisqa video (treyler) yuboring.
Siz: [Kinoning poster rasmini yuborasiz] (yoki kerak bo'lmasa - yuborasiz)
```
> Agar avto-post kanali sozlangan bo'lsa, bot avtomat shu kanallarga shu rasmni (yoki videoni) kino tayyor silkasi bilan post qiladi.

### ✅ Tayyor!

Endi foydalanuvchi `001` yuborganda:
```
🎬 Avatar: The Way of Water
🎬 Janr: Fantastika | Yil: 2022 | Til: O'zbekcha dublyaj
🔖 Kod: 001
[Video fayl]
```

---

## 12. Foydalanuvchi uchun ko'rsatmalar

Foydalanuvchilar uchun kanalda e'lon qiling:

```
🎬 Kino botimizdan foydalaning!

1. @sizning_bot_username ga o'ting
2. /start bosing
3. Kanallarga obuna bo'ling
4. Kino kodini yuboring va kinoni oling!

📌 Misol: 001 → Avatar 2
```

---

## 13. Ko'p so'raladigan savollar

### ❓ Bot ishlamayapti, nima qilishim kerak?

1. Railway da **Logs** bo'limini tekshiring — xato xabar bormi?
2. `BOT_TOKEN` to'g'ri kiritilganmi?
3. `ADMIN_IDS` to'g'ri kiritilganmi? (vergul bilan)

---

### ❓ Kanal qo'shdim lekin obuna tekshirilmayapti?

- Bot kanalda **admin** bo'lishi shart!
- Kanal **public** mi yoki **private** mi tekshiring
- Private kanallar uchun to'g'ri ID dan foydalaning

---

### ❓ Ma'lumotlar o'chib ketdi

- Railway **Volume** sozlanganmi? `/app/data` mount path to'g'riligini tekshiring
- `DATA_DIR=/app/data` o'zgaruvchisi qo'shilganmi?

---

### ❓ Kino kodini foydalanuvchi topib ola olmayapti

- Kod **kichik harflar** bilan saqlanadi. `001` va `001` bir xil, lekin `001` va `ABC` boshqa.
- **📋 Kinolar ro'yxati** dan mavjud kodlarni ko'ring

---

### ❓ Broadcast ishlamayapti

- Foydalanuvchi botni bloklagan bo'lsa yubora olmaysiz — bu normal holat
- Ko'p foydalanuvchiga yuborish biroz vaqt oladi

---

### ❓ Bot xatosi: "Unauthorized"

- Token noto'g'ri. BotFather dan yangi token oling yoki mavjudini to'g'irlang.

---

### ❓ Bir nechta admin qo'shish

`.env` yoki Railway variables da:
```
ADMIN_IDS=123456789,987654321,555666777
```

---

## 🔧 Tez-tez ishlatiladigan komandalar

| Komanda | Tavsif |
|---------|--------|
| `/start` | Botni ishga tushirish |
| `/admin` | Admin panel (faqat adminlar) |
| `/help` | Yordam xabari |

---

## 📞 Muammo bo'lsa

- Railway Logs ni tekshiring
- Bot tokenini tekshiring  
- Volume mount pathini tekshiring (`/app/data`)
- Kanal adminligini tekshiring

---

*Kino Bot v1.0 — aiogram 3.x + Railway + JSON Volume*
