"""
Ma'lumotlar bazasi - JSON fayllari orqali
Barcha fayllar /app/data/ papkasida saqlanadi (Railway Volume)

Fayllar:
  movies.json   - Kinolar
  channels.json - Majburiy obuna kanallari
  users.json    - Foydalanuvchilar
  settings.json - Bot sozlamalari
"""
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Optional


class Database:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self._lock = asyncio.Lock()

    # ─────────────────── INIT ───────────────────
    async def init(self):
        """Papka va boshlang'ich fayllarni yaratish"""
        self.data_dir.mkdir(parents=True, exist_ok=True)

        defaults = {
            "movies.json": {},
            "channels.json": [],
            "users.json": {},
            "settings.json": {
                "welcome_text": (
                    "🍿 <b>Kino Bot Pro</b>\n\n"
                    "🟡 Kino olish uchun <b>kino kodini</b> yuboring.\n"
                    "🔎 Masalan: <code>001</code> yoki <code>avatar2</code>\n\n"
                    "🟢 Kod to'g'ri bo'lsa, fayl darhol yuboriladi."
                ),
                "about_text": (
                    "🍿 <b>Kino Bot Pro</b>\n\n"
                    "🟢 Tezkor kino qidirish\n"
                    "🟡 Kod orqali avtomatik yuborish\n"
                    "🔵 Majburiy obuna va kanal avto-posti\n\n"
                    "📞 Admin bilan bog'lanish: @admin"
                ),
                "not_subscribed_text": (
                    "⚠️ <b>Davom etish uchun quyidagi kanallarga obuna bo'ling.</b>\n\n"
                    "🟢 Obuna bo'lgach, <b>Obunani tekshirish</b> tugmasini bosing."
                ),
                "post_channel_id": "",
            },
        }

        for filename, default_data in defaults.items():
            filepath = self.data_dir / filename
            if not filepath.exists():
                self._write_sync(filename, default_data)

    # ─────────────────── INTERNAL IO ───────────────────
    def _read_sync(self, filename: str):
        filepath = self.data_dir / filename
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return [] if filename == "channels.json" else {}

    def _write_sync(self, filename: str, data):
        filepath = self.data_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def _read(self, filename: str):
        return self._read_sync(filename)

    async def _write(self, filename: str, data):
        self._write_sync(filename, data)

    # ─────────────────── MOVIES ───────────────────
    async def add_movie(
        self,
        code: str,
        title: str,
        file_id: str,
        file_type: str,
        added_by: int,
        caption: str = "",
    ) -> bool:
        """Kino qo'shish. False qaytarsa - kod allaqachon mavjud."""
        async with self._lock:
            movies = await self._read("movies.json")
            if code in movies:
                return False
            movies[code] = {
                "title": title,
                "file_id": file_id,
                "file_type": file_type,  # video | document | photo
                "caption": caption,
                "added_by": added_by,
                "added_at": datetime.now().isoformat(),
                "views": 0,
            }
            await self._write("movies.json", movies)
        return True

    async def get_movie(self, code: str) -> Optional[dict]:
        """Kino olish (ko'rishlar sonini +1 qiladi)"""
        async with self._lock:
            movies = await self._read("movies.json")
            movie = movies.get(code.strip().lower())
            if movie:
                movies[code.strip().lower()]["views"] = movie.get("views", 0) + 1
                await self._write("movies.json", movies)
            return movie

    async def delete_movie(self, code: str) -> bool:
        """Kinoni o'chirish"""
        async with self._lock:
            movies = await self._read("movies.json")
            code = code.strip().lower()
            if code not in movies:
                return False
            del movies[code]
            await self._write("movies.json", movies)
        return True

    async def get_all_movies(self) -> dict:
        return await self._read("movies.json")

    async def movie_exists(self, code: str) -> bool:
        movies = await self._read("movies.json")
        return code.strip().lower() in movies

    async def update_movie_code(self, old_code: str, new_code: str) -> bool:
        """Kino kodini o'zgartirish"""
        async with self._lock:
            movies = await self._read("movies.json")
            if old_code not in movies or new_code in movies:
                return False
            movies[new_code] = movies.pop(old_code)
            await self._write("movies.json", movies)
        return True

    # ─────────────────── CHANNELS ───────────────────
    async def add_channel(
        self, channel_id: int, username: str, title: str
    ) -> bool:
        """Majburiy obuna kanalini qo'shish"""
        async with self._lock:
            channels = await self._read("channels.json")
            for ch in channels:
                if ch["id"] == channel_id:
                    return False  # Allaqachon mavjud
            channels.append(
                {
                    "id": channel_id,
                    "username": username,
                    "title": title,
                    "added_at": datetime.now().isoformat(),
                }
            )
            await self._write("channels.json", channels)
        return True

    async def remove_channel(self, channel_id: int) -> bool:
        """Kanalni o'chirish"""
        async with self._lock:
            channels = await self._read("channels.json")
            new_list = [ch for ch in channels if ch["id"] != channel_id]
            if len(new_list) == len(channels):
                return False
            await self._write("channels.json", new_list)
        return True

    async def get_channels(self) -> list:
        return await self._read("channels.json")

    # ─────────────────── USERS ───────────────────
    async def upsert_user(
        self, user_id: int, name: str, username: Optional[str]
    ) -> bool:
        """Foydalanuvchini qo'shish yoki yangilash. True = yangi foydalanuvchi."""
        async with self._lock:
            users = await self._read("users.json")
            key = str(user_id)
            is_new = key not in users
            existing = users.get(key, {})
            users[key] = {
                "name": name,
                "username": username or "",
                "joined_at": existing.get("joined_at", datetime.now().isoformat()),
                "last_active": datetime.now().isoformat(),
                "searches": existing.get("searches", 0),
            }
            await self._write("users.json", users)
        return is_new

    async def increment_searches(self, user_id: int):
        async with self._lock:
            users = await self._read("users.json")
            key = str(user_id)
            if key in users:
                users[key]["searches"] = users[key].get("searches", 0) + 1
                await self._write("users.json", users)

    async def get_all_users(self) -> dict:
        return await self._read("users.json")

    async def get_user_ids(self) -> list[int]:
        users = await self._read("users.json")
        return [int(uid) for uid in users.keys()]

    # ─────────────────── SETTINGS ───────────────────
    async def get_settings(self) -> dict:
        return await self._read("settings.json")

    async def get_setting(self, key: str, default: str = "") -> str:
        settings = await self._read("settings.json")
        return settings.get(key, default)

    async def update_setting(self, key: str, value: str):
        async with self._lock:
            settings = await self._read("settings.json")
            settings[key] = value
            await self._write("settings.json", settings)

    # ─────────────────── STATS ───────────────────
    async def get_stats(self) -> dict:
        users = await self._read("users.json")
        movies = await self._read("movies.json")
        channels = await self._read("channels.json")
        total_views = sum(m.get("views", 0) for m in movies.values())
        return {
            "total_users": len(users),
            "total_movies": len(movies),
            "total_channels": len(channels),
            "total_views": total_views,
        }
