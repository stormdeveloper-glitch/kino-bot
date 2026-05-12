"""
Kino Bot 3.0 web entrypoint.

Railway bitta service start command ishlatgani uchun bu fayl:
1. bot.py ni subprocess sifatida ishga tushiradi;
2. PORT orqali index.html ni web sahifa sifatida serve qiladi.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PORT = int(os.getenv("PORT", "8080"))
BOT_PROCESS: subprocess.Popen | None = None


class AppHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        if self.path in {"/", "/index", "/index.html"}:
            self.path = "/index.html"
        elif self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            bot_alive = BOT_PROCESS is not None and BOT_PROCESS.poll() is None
            self.wfile.write(
                f'{{"status":"ok","version":"3.0","bot_alive":{str(bot_alive).lower()}}}'.encode()
            )
            return
        return super().do_GET()

    def log_message(self, format, *args):
        print(f"[web] {self.address_string()} - {format % args}")


def start_bot() -> subprocess.Popen | None:
    if not os.getenv("BOT_TOKEN"):
        print("[web] BOT_TOKEN topilmadi. Web sahifa ishga tushadi, bot subprocess boshlanmaydi.")
        return None
    print("[web] bot.py ishga tushirilmoqda...")
    return subprocess.Popen([sys.executable, "bot.py"], cwd=str(ROOT))


def stop_bot(*_):
    if BOT_PROCESS and BOT_PROCESS.poll() is None:
        print("[web] bot.py to'xtatilmoqda...")
        BOT_PROCESS.terminate()
        try:
            BOT_PROCESS.wait(timeout=10)
        except subprocess.TimeoutExpired:
            BOT_PROCESS.kill()
    raise SystemExit


def main():
    global BOT_PROCESS
    BOT_PROCESS = start_bot()

    signal.signal(signal.SIGTERM, stop_bot)
    signal.signal(signal.SIGINT, stop_bot)

    server = ThreadingHTTPServer(("0.0.0.0", PORT), AppHandler)
    print(f"[web] Kino Bot 3.0 web server: http://0.0.0.0:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
