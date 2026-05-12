"""
Konfiguratsiya fayli
Barcha sozlamalar .env faylidan o'qiladi
"""
import os
from dataclasses import dataclass


@dataclass
class Config:
    BOT_TOKEN: str
    ADMIN_IDS: list[int]
    ADMIN_USERNAME: str = "@admin"
    DEVELOPER_ID: int = 0
    DATA_DIR: str = "/app/data"


def load_config() -> Config:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise ValueError("❌ BOT_TOKEN topilmadi! .env faylini tekshiring.")

    admin_str = os.getenv("ADMIN_IDS", "")
    admin_ids: list[int] = []
    for item in admin_str.split(","):
        item = item.strip()
        if item.isdigit():
            admin_ids.append(int(item))

    if not admin_ids:
        raise ValueError("❌ ADMIN_IDS topilmadi! Kamida bitta admin ID kiriting.")

    developer_id = int(os.getenv("DEVELOPER_ID", "0"))
    if developer_id == 0 and admin_ids:
        developer_id = admin_ids[0]

    admin_username = os.getenv("ADMIN_USER", os.getenv("ADMIN_USERNAME", "@admin"))
    if not admin_username.startswith("@") and not admin_username.startswith("http"):
        admin_username = f"@{admin_username}"

    data_dir = os.getenv("DATA_DIR", "/app/data")

    return Config(
        BOT_TOKEN=token,
        ADMIN_IDS=admin_ids,
        ADMIN_USERNAME=admin_username,
        DEVELOPER_ID=developer_id,
        DATA_DIR=data_dir,
    )
