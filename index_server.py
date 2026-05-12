"""
Kino Bot 3.0 web server.

JSON bazadagi kinolarni o'qiydi. Telegram file_id lar getFile orqali
yechilib, /media/{file_id} proxy endpointidan webga chiqariladi.
"""
from __future__ import annotations

import json
import mimetypes
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PORT = int(os.getenv("PORT", "8080"))
DATA_DIR = Path(os.getenv("DATA_DIR", str(ROOT / "data")))
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
BOT_PROCESS: subprocess.Popen | None = None

MEDIA_CACHE_TTL = 45 * 60
MEDIA_CACHE: dict[str, dict] = {}
BOT_INFO_CACHE: dict = {"ts": 0, "data": None}


def read_json(filename: str, default):
    path = DATA_DIR / filename
    if not path.exists():
        path = ROOT / "data" / filename
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def write_json(handler: BaseHTTPRequestHandler, payload: dict, status: int = 200):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Cache-Control", "no-store")
    handler.end_headers()
    handler.wfile.write(body)


def public_media_id(movie: dict) -> tuple[str, str]:
    post_file_id = movie.get("post_file_id") or ""
    post_file_type = movie.get("post_file_type") or ""
    if post_file_id:
        return post_file_id, post_file_type or "photo"

    file_id = movie.get("file_id") or ""
    file_type = movie.get("file_type") or "document"
    if file_type in {"photo", "video"}:
        return file_id, file_type
    return "", "none"


def resolve_file_id(file_id: str) -> dict:
    now = time.time()
    cached = MEDIA_CACHE.get(file_id)
    if cached and now - cached.get("ts", 0) < MEDIA_CACHE_TTL:
        return cached

    if not BOT_TOKEN or not file_id:
        return {"ok": False, "url": "", "type": "none", "ts": now}


def telegram_json(method: str, params: dict | None = None) -> dict:
    if not BOT_TOKEN:
        return {}
    query = ""
    if params:
        query = "?" + urllib.parse.urlencode(params)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}{query}"
    with urllib.request.urlopen(url, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))

    query = urllib.parse.urlencode({"file_id": file_id})
    api_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getFile?{query}"
    try:
        with urllib.request.urlopen(api_url, timeout=12) as response:
            data = json.loads(response.read().decode("utf-8"))
        if not data.get("ok"):
            return {"ok": False, "url": "", "type": "none", "ts": now}

        file_path = data["result"]["file_path"]
        file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_path}"
        lower = file_path.lower()
        media_type = "video" if any(x in lower for x in ("video", ".mp4", ".mov", ".webm")) else "photo"
        result = {"ok": True, "url": file_url, "type": media_type, "path": file_path, "ts": now}
        MEDIA_CACHE[file_id] = result
        return result
    except Exception as exc:
        print(f"[web] getFile xatosi: {exc}")
        return {"ok": False, "url": "", "type": "none", "ts": now}


def movies_payload(query: str = "") -> dict:
    movies = read_json("movies.json", {})
    q = query.strip().casefold()
    rows = []
    for code, movie in movies.items():
        title = movie.get("title", "Kino")
        caption = movie.get("caption", "")
        haystack = f"{code} {title} {caption}".casefold()
        if q and q not in haystack:
            continue

        media_id, media_type = public_media_id(movie)
        safe_code = urllib.parse.quote(str(code), safe="")
        safe_media = urllib.parse.quote(media_id, safe="")
        rows.append({
            "code": code,
            "title": title,
            "caption": caption,
            "views": movie.get("views", 0),
            "file_type": movie.get("file_type", "document"),
            "media_type": media_type,
            "media_url": f"/media/{safe_media}" if media_id else "",
            "poster_url": f"/poster/{safe_code}" if media_id else "",
            "added_at": movie.get("added_at", ""),
        })

    rows.sort(key=lambda item: item.get("added_at") or "", reverse=True)
    return {"ok": True, "movies": rows, "total": len(rows)}


def start_bot() -> subprocess.Popen | None:
    if not BOT_TOKEN:
        print("[web] BOT_TOKEN topilmadi. Faqat web server ishga tushadi.")
        return None
    print("[web] bot.py ishga tushirilmoqda...")
    return subprocess.Popen([sys.executable, "bot.py"], cwd=str(ROOT))


class KinoHandler(BaseHTTPRequestHandler):
    server_version = "KinoBotWeb/3.0"

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = urllib.parse.unquote(parsed.path)
        params = urllib.parse.parse_qs(parsed.query)

        if path in {"/", "/index", "/index.html"}:
            return self.serve_file(ROOT / "index.html", "text/html; charset=utf-8")

        if path == "/api/movies":
            return write_json(self, movies_payload((params.get("q") or [""])[0]))

        if path.startswith("/api/movies/"):
            code = path.removeprefix("/api/movies/").strip().lower()
            movies = read_json("movies.json", {})
            movie = movies.get(code)
            if not movie:
                return write_json(self, {"ok": False, "error": "Kino topilmadi"}, 404)
            payload = movies_payload(code)
            match = next((item for item in payload["movies"] if item["code"] == code), None)
            return write_json(self, {"ok": True, "movie": match})

        if path == "/api/bot-info":
            return write_json(self, self.bot_info())

        if path.startswith("/poster/"):
            code = path.removeprefix("/poster/").strip().lower()
            movies = read_json("movies.json", {})
            movie = movies.get(code)
            if not movie:
                return self.not_found()
            media_id, _ = public_media_id(movie)
            if not media_id:
                return self.not_found()
            self.send_response(302)
            self.send_header("Location", f"/media/{urllib.parse.quote(media_id, safe='')}")
            self.end_headers()
            return

        if path.startswith("/media/"):
            file_id = path.removeprefix("/media/")
            return self.proxy_media(file_id)

        return self.not_found()

    def serve_file(self, path: Path, content_type: str | None = None):
        if not path.exists() or not path.is_file():
            return self.not_found()
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type or mimetypes.guess_type(str(path))[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "public, max-age=120")
        self.end_headers()
        self.wfile.write(body)

    def bot_info(self) -> dict:
        now = time.time()
        cached = BOT_INFO_CACHE.get("data")
        if cached and now - BOT_INFO_CACHE.get("ts", 0) < MEDIA_CACHE_TTL:
            return cached

        result = {"ok": True, "name": "Kino Bot 3.0", "username": "", "photo_url": ""}
        if not BOT_TOKEN:
            return result
        try:
            data = telegram_json("getMe")
            if data.get("ok"):
                me = data["result"]
                bot_id = me.get("id")
                result["name"] = me.get("first_name") or result["name"]
                result["username"] = me.get("username") or ""
                if bot_id:
                    photos = telegram_json("getUserProfilePhotos", {"user_id": bot_id, "limit": 1})
                    photo_sets = photos.get("result", {}).get("photos", []) if photos.get("ok") else []
                    if photo_sets and photo_sets[0]:
                        file_id = photo_sets[0][-1].get("file_id", "")
                        if file_id:
                            result["photo_url"] = f"/media/{urllib.parse.quote(file_id, safe='')}"
        except Exception:
            pass
        BOT_INFO_CACHE["ts"] = now
        BOT_INFO_CACHE["data"] = result
        return result

    def proxy_media(self, file_id: str):
        info = resolve_file_id(file_id)
        if not info.get("ok"):
            return self.not_found()

        headers = {}
        if self.headers.get("Range"):
            headers["Range"] = self.headers["Range"]

        request = urllib.request.Request(info["url"], headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                self.send_response(response.status)
                self.send_header("Content-Type", response.headers.get("Content-Type", "application/octet-stream"))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("Cache-Control", "public, max-age=1800")
                for header in ("Content-Length", "Content-Range"):
                    if response.headers.get(header):
                        self.send_header(header, response.headers[header])
                self.end_headers()
                while True:
                    chunk = response.read(64 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
        except urllib.error.HTTPError as exc:
            self.send_error(exc.code)
        except Exception as exc:
            print(f"[web] media proxy xatosi: {exc}")
            self.send_error(502)

    def not_found(self):
        self.send_response(404)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write("Not found".encode("utf-8"))

    def log_message(self, format, *args):
        print(f"[web] {self.address_string()} - {format % args}")


def main():
    global BOT_PROCESS
    BOT_PROCESS = start_bot()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), KinoHandler)
    print(f"[web] Kino Bot 3.0 web server: http://0.0.0.0:{PORT}")
    try:
        server.serve_forever()
    finally:
        if BOT_PROCESS and BOT_PROCESS.poll() is None:
            BOT_PROCESS.terminate()


if __name__ == "__main__":
    main()
