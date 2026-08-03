#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🍓 Fruit Cut Bot — Full Menu
- 1. Auto Game (loop sampai token habis)
- 2. Auto Watch Ads (loop semua network sampai limit)
- 3. Check Balance
- 4. Set InitData
- 0. Exit
"""

import requests
import time
import json
import sys
import os
from datetime import datetime

# ─── COLOR ─────────────────────────────────────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    C = Fore
    S = Style
except ImportError:
    class C:
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        CYAN = '\033[96m'
        MAGENTA = '\033[95m'
        WHITE = '\033[97m'
        BLUE = '\033[94m'
        RESET = '\033[0m'
    class S:
        BRIGHT = '\033[1m'
        RESET = '\033[0m'

BASE_URL = "https://fruit-cut-eight.vercel.app"
INIT_DATA = ""
INIT_FILE = "init_data.txt"

# ─── BANNER ────────────────────────────────────────────────
BANNER = f"""
{C.YELLOW}╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║ ███████╗██████╗ ██╗   ██╗██╗████████╗██╗   ██╗██╗  ██╗███████╗║
║ ██╔════╝██╔══██╗██║   ██║██║╚══██╔══╝╚██╗ ██╔╝╚██╗██╔╝██╔════╝║
║ ███████╗██████╔╝██║   ██║██║   ██║    ╚████╔╝  ╚███╔╝ ███████╗║
║ ╚════██║██╔══██╗██║   ██║██║   ██║     ╚██╔╝   ██╔██╗ ╚════██║║
║ ███████║██║  ██║╚██████╔╝██║   ██║      ██║   ██╔╝ ██╗███████║║
║ ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚══════╝║
║                                                              ║
║                 🍓  F R U I T   G A M E   B O T             ║
║                                                              ║
║              👨‍💻 Dev : ScriptyXSou                           ║
║              📢 TG  : t.me/ScriptyXSouu                      ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝{C.RESET}
"""

# ─── HELPERS ──────────────────────────────────────────────
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
        self.user = None
        self.gold = 0
        self.fruit_coin = 0
        self.stage = 1
        self.game_tokens = 0
        self.lottery_tokens = 0
        self.max_tokens = 10

    def log(self, msg, color=C.WHITE, end="\n"):
        print(f"{color}{msg}{C.RESET}", end=end)

    def api(self, endpoint, data=None):
        url = f"{BASE_URL}{endpoint}"
        try:
            resp = self.session.post(url, json=data or {}, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            self.log(f"❌ API Error: {e}", C.RED)
            return None

    def login(self):
        self.log("🔐 Login...", C.CYAN)
        payload = {"deviceId": f"dev_{int(time.time())}", "referredBy": None}
        res = self.api("/api/auth", payload)
        if res and res.get("success"):
            u = res.get("user", {})
            self.gold = u.get("gold", 0)
            self.fruit_coin = u.get("fruitCoin", 0)
            self.game_tokens = u.get("gameTokens", 0)
            self.lottery_tokens = u.get("lotteryTokens", 0)
            self.stage = u.get("stage", 1)
            self.max_tokens = u.get("maxTokens", 10)
            return True
        return False

    def sync(self):
        res = self.api("/api/init", {"syncOnly": True})
        if res and res.get("success"):
            u = res.get("user", {})
            self.gold = u.get("gold", self.gold)
            self.fruit_coin = u.get("fruitCoin", self.fruit_coin)
            self.game_tokens = u.get("gameTokens", self.game_tokens)
            self.lottery_tokens = u.get("lotteryTokens", self.lottery_tokens)
            self.stage = u.get("stage", self.stage)
            return True
        return False

    def start_game(self):
        res = self.api("/api/game_claim", {"action": "start_game"})
        if res and res.get("success"):
            self.game_tokens = res.get("tokens", self.game_tokens)
            self.stage = res.get("stage", self.stage)
            return res.get("sessionId")
        return None

    def claim_reward(self, session_id, watch_ad=False):
        res = self.api("/api/game_claim", {
            "isAdWatched": watch_ad,
            "sessionId": session_id
        })
        if res and res.get("success"):
            reward = res.get("reward", 0)
            self.gold = res.get("user", {}).get("gold", self.gold)
            self.fruit_coin = res.get("user", {}).get("fruitCoin", self.fruit_coin)
            return reward
        return None

    def watch_ad(self, ad_type="adsgram"):
        session_res = self.api("/api/ads", {
            "action": "request_session",
            "network": ad_type
        })
        if not session_res or not session_res.get("success"):
            self.log(f"❌ Gagal request session {ad_type}", C.RED)
            return False
        session_id = session_res.get("sessionId")

        self.log(f"⏳ Menonton {ad_type} 17 detik...", C.CYAN)
        for i in range(17, 0, -1):
            print(f"\r   {progress_bar(i, 17, '📺', 20)}", end="")
            time.sleep(1)
        print("\r   ✅ Iklan selesai!        ")

        claim_res = self.api("/api/ads", {
            "action": ad_type,
            "sessionId": session_id
        })
        if claim_res and claim_res.get("success"):
            self.sync()
            return True
        self.log(f"❌ Gagal claim reward {ad_type}", C.RED)
        return False

# ─── MENU FUNCTIONS ────────────────────────────────────────

def get_init_data():
    clear()
    print(BANNER)
    box("🔐 SET INIT DATA", 54)
    print(f"{C.WHITE}║{C.RESET}")
    print(f"{C.WHITE}║  Paste init_data (panjang, dari header x-telegram-init-data){C.RESET}")
    print(f"{C.WHITE}║  Tekan Enter dua kali setelah selesai paste{C.RESET}")
    print(f"{C.WHITE}║{C.RESET}")
    box_end(54)
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    data = "".join(lines).strip()
    if data:
        with open(INIT_FILE, "w") as f:
            f.write(data)
        print(f"{C.GREEN}✅ Disimpan ke {INIT_FILE}{C.RESET}")
        return data
    return None

def load_init_data():
    if os.path.exists(INIT_FILE):
        with open(INIT_FILE, "r") as f:
            data = f.read().strip()
        if data:
            return data
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
    box("🍓 FRUIT GAME BOT", 54)
    print(f"{C.WHITE}║{C.RESET}")
    print(f"{C.WHITE}║  {C.GREEN}[1]{C.WHITE} 🎮 Auto Game (loop sampai token habis){C.RESET}")
    print(f"{C.WHITE}║  {C.YELLOW}[2]{C.WHITE} 📺 Auto Watch Ads (semua network){C.RESET}")
    print(f"{C.WHITE}║  {C.CYAN}[3]{C.WHITE} 💰 Check Balance{C.RESET}")
    print(f"{C.WHITE}║  {C.MAGENTA}[4]{C.WHITE} 🔐 Set InitData (ganti){C.RESET}")
    print(f"{C.WHITE}║{C.RESET}")
    print(f"{C.WHITE}║  {C.RED}[0]{C.WHITE} ❌ Exit{C.RESET}")
    box_end(54)
    return input(f"{C.CYAN}➜ Select Menu : {C.RESET}").strip()

def check_balance(bot):
    if not bot.login():
        print(f"{C.RED}❌ Gagal login, mungkin init_data salah.{C.RESET}")
        if input("Ingin set ulang init_data? (y/n): ").lower() == 'y':
            if ensure_init_data():
                bot = FruitCutBot(INIT_DATA)
                check_balance(bot)
                return
        input("Tekan Enter...")
        return
    print(f"""
{C.WHITE}💰 Gold        : {C.YELLOW}{bot.gold}{C.RESET}
{C.WHITE}🍎 Fruit Coin : {C.YELLOW}{bot.fruit_coin}{C.RESET}
{C.WHITE}🎮 Game Tokens: {C.YELLOW}{bot.game_tokens} / {bot.max_tokens}{C.RESET}
{C.WHITE}🎫 Lottery Tok: {C.YELLOW}{bot.lottery_tokens}{C.RESET}
{C.WHITE}🏆 Stage      : {C.YELLOW}{bot.stage}{C.RESET}
    """)
    input("Tekan Enter untuk kembali...")

def auto_game(bot, max_rounds=999):
    if not bot.login():
        print(f"{C.RED}❌ Gagal login, mungkin init_data salah.{C.RESET}")
        if input("Ingin set ulang init_data? (y/n): ").lower() == 'y':
            if ensure_init_data():
                bot = FruitCutBot(INIT_DATA)
                auto_game(bot, max_rounds)
                return
        input("Tekan Enter...")
        return

    round_count = 0
    while bot.game_tokens > 0 and round_count < max_rounds:
        round_count += 1
        clear()
        print(BANNER)
        box(f"🚀 AUTO GAME — Round {round_count}", 54)
        print(f"{C.WHITE}║  🎟 Tokens  : {bot.game_tokens} → {bot.game_tokens-1}{C.RESET}")
        
        session_id = bot.start_game()
        if not session_id:
            print(f"{C.RED}║  ❌ Start game gagal!{C.RESET}")
            box_end(54)
            input("Tekan Enter...")
            break
        print(f"{C.WHITE}║  🆔 Session : {session_id[:8]}...{C.RESET}")
        
        print(f"{C.WHITE}║  ⏳ Playing :{C.RESET}", end="")
        for i in range(15, 0, -1):
            print(f"\r║  ⏳ Playing : {progress_bar(i, 15, '', 20)}", end="")
            time.sleep(1)
        print(f"\r║  ✅ Finished : {C.GREEN}15s{C.RESET}")
        
        print(f"{C.WHITE}║  🎁 Claim reward...{C.RESET}")
        reward = bot.claim_reward(session_id, watch_ad=False)
        if reward is None:
            print(f"{C.RED}║  ❌ Claim gagal!{C.RESET}")
        else:
            print(f"{C.WHITE}║  💰 Reward  : +{C.GREEN}{reward}{C.WHITE} Gold{C.RESET}")
            print(f"{C.WHITE}║  🪙 Total   : {C.YELLOW}{bot.gold}{C.WHITE} Gold{C.RESET}")
        
        bot.sync()
        print(f"{C.WHITE}💰 Gold sekarang: {C.YELLOW}{bot.gold}{C.RESET}")
        time.sleep(1)

    if bot.game_tokens <= 0:
        print(f"\n{C.YELLOW}⚠️ Token habis! Bot berhenti. Tunggu refill atau beli token.{C.RESET}")
    else:
        print(f"\n{C.GREEN}✅ Selesai {round_count} round!{C.RESET}")
    input("Tekan Enter untuk kembali...")

def auto_watch_ads(bot, max_loops=10):
    if not bot.login():
        print(f"{C.RED}❌ Gagal login, mungkin init_data salah.{C.RESET}")
        if input("Ingin set ulang init_data? (y/n): ").lower() == 'y':
            if ensure_init_data():
                bot = FruitCutBot(INIT_DATA)
                auto_watch_ads(bot, max_loops)
                return
        input("Tekan Enter...")
        return

    # Daftar network & limit harian
    ad_networks = [
        ("adsgram", 5),
        ("adsgramDaily", 5),
        ("monetag", 10),
        ("gigapub", 10)
    ]

    total_success = 0
    total_failed = 0

    clear()
    print(BANNER)
    box("📺 AUTO WATCH ADS", 54)
    print(f"{C.WHITE}║  Target: {max_loops} iklan (akan coba semua network){C.RESET}")
    print(f"{C.WHITE}║{C.RESET}")
    box_end(54)

    for network, limit in ad_networks:
        if total_success >= max_loops:
            break
        # Coba network ini sampai limit atau sampai gagal
        for i in range(min(max_loops - total_success, limit)):
            print(f"\n{C.YELLOW}[{total_success+1}/{max_loops}] Menonton {network}...{C.RESET}")
            ok = bot.watch_ad(network)
            if ok:
                total_success += 1
                print(f"{C.GREEN}✅ Iklan {network} selesai, +Gold!{C.RESET}")
                bot.sync()
                print(f"{C.WHITE}💰 Gold sekarang: {C.YELLOW}{bot.gold}{C.RESET}")
            else:
                total_failed += 1
                print(f"{C.RED}❌ Gagal menonton {network}, skip ke network berikutnya.{C.RESET}")
                # Langsung keluar dari loop network ini, lanjut ke network berikutnya
                break
            time.sleep(1)
        # Jika sukses sudah mencapai target, keluar dari loop network
        if total_success >= max_loops:
            break

    print(f"\n{C.GREEN}✅ Selesai menonton {total_success} iklan (gagal: {total_failed}){C.RESET}")
    if total_success == 0:
        print(f"{C.RED}⚠️ Tidak ada iklan yang berhasil. Cek koneksi atau coba lagi nanti.{C.RESET}")
    input("Tekan Enter untuk kembali...")

# ─── MAIN ──────────────────────────────────────────────────
def main():
    global INIT_DATA
    INIT_DATA = load_init_data() or ""

    bot = None
    if INIT_DATA:
        bot = FruitCutBot(INIT_DATA)

    while True:
        choice = show_menu()
        if choice == "1":
            if not ensure_init_data():
                print(f"{C.RED}❌ Gagal mendapatkan init_data.{C.RESET}")
                input("Tekan Enter...")
                continue
            if bot is None or bot.init_data != INIT_DATA:
                bot = FruitCutBot(INIT_DATA)
            auto_game(bot, max_rounds=999)
        elif choice == "2":
            if not ensure_init_data():
                print(f"{C.RED}❌ Gagal mendapatkan init_data.{C.RESET}")
                input("Tekan Enter...")
                continue
            if bot is None or bot.init_data != INIT_DATA:
                bot = FruitCutBot(INIT_DATA)
            auto_watch_ads(bot, max_loops=10)  # bisa diubah
        elif choice == "3":
            if not ensure_init_data():
                print(f"{C.RED}❌ Gagal mendapatkan init_data.{C.RESET}")
                input("Tekan Enter...")
                continue
            if bot is None or bot.init_data != INIT_DATA:
                bot = FruitCutBot(INIT_DATA)
            check_balance(bot)
        elif choice == "4":
            new_data = get_init_data()
            if new_data:
                INIT_DATA = new_data
                bot = FruitCutBot(INIT_DATA)
                print(f"{C.GREEN}✅ InitData diperbarui!{C.RESET}")
            else:
                print(f"{C.RED}❌ Gagal memperbarui.{C.RESET}")
            input("Tekan Enter...")
        elif choice == "0":
            print(f"{C.YELLOW}👋 Sampai jumpa!{C.RESET}")
            sys.exit(0)
        else:
            print(f"{C.RED}❌ Pilihan tidak valid!{C.RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}👋 Dihentikan oleh user.{C.RESET}")
        sys.exit(0)
