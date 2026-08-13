#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🍓 Fruit Cut Bot — ONLY ADS (Forever, Stop on Error/403)
- Auto Watch Ads tanpa batas, loop bergantian network
- Stop jika request/claim gagal atau 403
- Log hijau jelas
"""

import requests
import time
import json
import sys
import os
import urllib.parse

# ─── COLOR ─────────────────────────────────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    C = Fore
    S = Style
except ImportError:
    class C:
        GREEN = '\033[92m'; YELLOW = '\033[93m'; RED = '\033[91m'
        CYAN = '\033[96m'; MAGENTA = '\033[95m'; WHITE = '\033[97m'
        BLUE = '\033[94m'; RESET = '\033[0m'
    class S:
        BRIGHT = '\033[1m'; RESET = '\033[0m'

BASE_URL = "https://fruit-cut-eight.vercel.app"
INIT_DATA = ""
INIT_FILE = "init_data.txt"

# ─── BANNER ────────────────────────────────────────────────
BANNER = f"""
{C.YELLOW}╔══════════════════════════════════════════════════════════════╗
║                 🍓  F R U I T   A D S   B O T              ║
║              🔥 Auto Ads Forever — Stop on Error           ║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
"""

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def box(title, width=54):
    print(f"{C.CYAN}╔{'═'*(width-2)}╗{C.RESET}")
    print(f"{C.CYAN}║{title.center(width-2)}║{C.RESET}")
    print(f"{C.CYAN}╠{'═'*(width-2)}╣{C.RESET}")

def box_end(width=54):
    print(f"{C.CYAN}╚{'═'*(width-2)}╝{C.RESET}")

def progress_bar(seconds, total, label="", width=20):
    filled = int(round(width * seconds / total))
    bar = '█' * filled + '░' * (width - filled)
    return f"{label} [{C.GREEN}{bar}{C.RESET}] {seconds}/{total}s"

def extract_telegram_id(init_data):
    if not init_data: return None
    parsed = urllib.parse.parse_qs(init_data)
    user_str = parsed.get('user', [None])[0]
    if user_str:
        try:
            user_json = json.loads(urllib.parse.unquote(user_str))
            return str(user_json.get('id'))
        except: pass
    return None

# ─── BOT CLASS ─────────────────────────────────────────────
class FruitCutBot:
    def __init__(self, init_data):
        self.init_data = init_data
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "x-telegram-init-data": init_data,
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36"
        })
        self.gold = 0
        self.fruit_coin = 0
        self.stage = 1
        self.telegram_id = extract_telegram_id(init_data) or "6894031790"

    def log(self, msg, color=C.WHITE, end="\n"):
        print(f"{color}{msg}{C.RESET}", end=end)

    def api(self, endpoint, data=None, retries=2):
        url = f"{BASE_URL}{endpoint}"
        for attempt in range(retries):
            try:
                resp = self.session.post(url, json=data or {}, timeout=10)
                if resp.status_code == 403:
                    self.log(f"🚫 403 Forbidden — Hentikan bot.", C.RED)
                    sys.exit(1)
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.HTTPError as e:
                if resp.status_code == 403:
                    self.log(f"🚫 403 Forbidden — Hentikan bot.", C.RED)
                    sys.exit(1)
                if attempt < retries - 1:
                    self.log(f"⚠️ HTTP error, coba ulang {attempt+1}/{retries}...", C.YELLOW)
                    time.sleep(2)
                else:
                    self.log(f"❌ HTTP Error: {e}", C.RED)
                    return None
            except Exception as e:
                if attempt < retries - 1:
                    time.sleep(2)
                else:
                    self.log(f"❌ API Error: {e}", C.RED)
                    return None
        return None

    def login(self):
        self.log("🔐 Login...", C.CYAN)
        if not self.init_data: return False
        res = self.api("/api/init", {"syncOnly": True})
        if res and res.get("success"):
            u = res.get("user", {})
            self.gold = u.get("gold", 0)
            self.fruit_coin = u.get("fruitCoin", 0)
            self.stage = u.get("stage", 1)
            if u.get("telegramId"):
                self.telegram_id = str(u["telegramId"])
            return True
        return False

    def sync(self):
        res = self.api("/api/init", {"syncOnly": True})
        if res and res.get("success"):
            u = res.get("user", {})
            self.gold = u.get("gold", self.gold)
            self.fruit_coin = u.get("fruitCoin", self.fruit_coin)
            self.stage = u.get("stage", self.stage)
            return True
        return False

# ─── MENU FUNCTIONS ────────────────────────────────────────

def get_init_data():
    clear()
    print(BANNER)
    box("🔐 SET INIT DATA", 54)
    print(f"{C.WHITE}║  Paste init_data, Enter 2x untuk selesai{C.RESET}")
    box_end(54)
    lines = []
    while True:
        line = input()
        if line == "": break
        lines.append(line)
    data = "".join(lines).strip()
    if data:
        with open(INIT_FILE, "w") as f: f.write(data)
        print(f"{C.GREEN}✅ Disimpan{C.RESET}")
        return data
    return None

def load_init_data():
    if os.path.exists(INIT_FILE):
        with open(INIT_FILE, "r") as f:
            data = f.read().strip()
        if data: return data
    return None

def ensure_init_data():
    global INIT_DATA
    data = load_init_data()
    if data:
        INIT_DATA = data
        return True
    data = get_init_data()
    if data:
        INIT_DATA = data
        return True
    return False

def show_menu():
    clear()
    print(BANNER)
    box("🍓 FRUIT ADS BOT", 54)
    print(f"{C.WHITE}║  {C.YELLOW}[1]{C.WHITE} 📺 Auto Watch Ads (Forever, stop on error){C.RESET}")
    print(f"{C.WHITE}║  {C.CYAN}[2]{C.WHITE} 💰 Check Balance{C.RESET}")
    print(f"{C.WHITE}║  {C.MAGENTA}[3]{C.WHITE} 🔐 Set InitData{C.RESET}")
    print(f"{C.WHITE}║  {C.RED}[0]{C.WHITE} ❌ Exit{C.RESET}")
    box_end(54)
    return input(f"{C.CYAN}➜ Pilih : {C.RESET}").strip()

def check_balance(bot):
    if not bot.login():
        print(f"{C.RED}❌ Gagal login.{C.RESET}")
        input("Enter...")
        return
    print(f"""
{C.WHITE}💰 Gold        : {C.YELLOW}{bot.gold}{C.RESET}
{C.WHITE}🍎 Fruit Coin : {C.YELLOW}{bot.fruit_coin}{C.RESET}
{C.WHITE}🏆 Stage      : {C.YELLOW}{bot.stage}{C.RESET}
    """)
    input("Enter...")

def auto_watch_ads_forever(bot):
    if not bot.login():
        print(f"{C.RED}❌ Gagal login.{C.RESET}")
        input("Enter...")
        return

    ad_count = 0
    success_count = 0
    networks = ["adsgram", "adsgramDaily", "monetag", "gigapub"]
    network_index = 0

    try:
        while True:
            network = networks[network_index % len(networks)]
            network_index += 1
            ad_count += 1

            print(f"\n{C.CYAN}[{ad_count}] Menonton {network}...{C.RESET}")

            # Request session
            session_res = bot.api("/api/ads", {
                "telegramId": bot.telegram_id,
                "action": "request_session",
                "network": network
            })
            if not session_res or not session_res.get("success"):
                print(f"{C.RED}❌ Gagal request session, stop.{C.RESET}")
                sys.exit(1)

            sid = session_res.get("sessionId")
            if not sid:
                print(f"{C.RED}❌ Tidak dapat sessionId, stop.{C.RESET}")
                sys.exit(1)

            # Tunggu iklan 17 detik dengan progress bar hijau
            print(f"   {C.GREEN}⏳ Menonton iklan{C.RESET}")
            for i in range(17, 0, -1):
                print(f"\r   {progress_bar(i, 17, '', 20)}", end="")
                time.sleep(1)
            print("\r   ✅ Iklan selesai!        ")

            # Claim
            claim_res = bot.api("/api/ads", {
                "telegramId": bot.telegram_id,
                "action": network,
                "sessionId": sid
            })
            if not claim_res or not claim_res.get("success"):
                print(f"{C.RED}❌ Gagal claim iklan, stop.{C.RESET}")
                sys.exit(1)

            # Update gold
            if "user" in claim_res:
                bot.gold = claim_res["user"].get("gold", bot.gold)
            success_count += 1
            print(f"{C.GREEN}✅ {network} selesai! Gold: {C.YELLOW}{bot.gold}{C.RESET}")
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}⏹️ Berhenti. Total iklan: {ad_count}, Berhasil: {success_count}{C.RESET}")
        input("Enter...")

# ─── MAIN ──────────────────────────────────────────────────
def main():
    global INIT_DATA
    INIT_DATA = load_init_data() or ""
    bot = FruitCutBot(INIT_DATA) if INIT_DATA else None

    while True:
        choice = show_menu()
        if choice == "1":
            if not ensure_init_data(): continue
            bot = FruitCutBot(INIT_DATA)
            auto_watch_ads_forever(bot)
        elif choice == "2":
            if not ensure_init_data(): continue
            bot = FruitCutBot(INIT_DATA)
            check_balance(bot)
        elif choice == "3":
            new = get_init_data()
            if new:
                INIT_DATA = new
                bot = FruitCutBot(INIT_DATA)
                print(f"{C.GREEN}✅ InitData diperbarui{C.RESET}")
            input("Enter...")
        elif choice == "0":
            print(f"{C.YELLOW}👋 Sampai jumpa{C.RESET}")
            sys.exit(0)
        else:
            print(f"{C.RED}❌ Pilihan salah{C.RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}👋 Bye{C.RESET}")
        sys.exit(0)
