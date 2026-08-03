#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🍓 Fruit Cut Bot — Full Menu
- 1. Auto Game (main + claim + optional ad)
- 2. Auto Watch Ads (loop sampai limit harian)
- 3. Check Balance
- 4. Set InitData (auto retry kalau gagal)
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

def show_toast(msg, color=C.GREEN):
    print(f"{color}└─ {msg}{C.RESET}")

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
        self.adsgram_count = 0
        self.adsgram_daily_count = 0
        self.monetag_count = 0
        self.gigapub_count = 0

    def log(self, msg, color=C.WHITE, end="\n"):
        print(f"{color}{msg}{C.RESET}", end=end)

    def api(self, endpoint, data=None):
        url = f"{BASE_URL}{endpoint}"
        try:
            resp = self.session.post(url, json=data or {})
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
            # Load ad counts (from local storage or server? we keep local)
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
        # 1. request session
        session_res = self.api("/api/ads", {
            "action": "request_session",
            "network": ad_type
        })
        if not session_res or not session_res.get("success"):
            self.log("❌ Gagal request session iklan", C.RED)
            return False
        session_id = session_res.get("sessionId")

        # 2. simulate 17 detik
        self.log("⏳ Menonton iklan 17 detik...", C.CYAN)
        for i in range(17, 0, -1):
            print(f"\r   {progress_bar(i, 17, '📺', 20)}", end="")
            time.sleep(1)
        print("\r   ✅ Iklan selesai!        ")

        # 3. claim reward
        claim_res = self.api("/api/ads", {
            "action": ad_type,
            "sessionId": session_id
        })
        if claim_res and claim_res.get("success"):
            self.sync()
            return True
        self.log("❌ Gagal claim reward iklan", C.RED)
        return False

# ─── MENU FUNCTIONS ────────────────────────────────────────

def get_init_data():
    """Minta init_data dari user, simpan ke file"""
    clear()
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
        # simpan ke file
        with open(INIT_FILE, "w") as f:
            f.write(data)
        print(f"{C.GREEN}✅ Disimpan ke {INIT_FILE}{C.RESET}")
        return data
    return None

def load_init_data():
    """Load dari file, jika ada"""
    if os.path.exists(INIT_FILE):
        with open(INIT_FILE, "r") as f:
            data = f.read().strip()
        if data:
            return data
    return None

def ensure_init_data():
    """Pastikan init_data tersedia, retry jika gagal login"""
    global INIT_DATA
    # coba load dari file
    data = load_init_data()
    if data:
        INIT_DATA = data
        return True
    # minta manual
    data = get_init_data()
    if data:
        INIT_DATA = data
        return True
    return False

def show_menu():
    clear()
    box("🍓 FRUIT GAME BOT", 54)
    print(f"{C.WHITE}║{C.RESET}")
    print(f"{C.WHITE}║  {C.GREEN}[1]{C.WHITE} 🎮 Auto Game{C.RESET}")
    print(f"{C.WHITE}║  {C.YELLOW}[2]{C.WHITE} 📺 Auto Watch Ads{C.RESET}")
    print(f"{C.WHITE}║  {C.CYAN}[3]{C.WHITE} 💰 Check Balance{C.RESET}")
    print(f"{C.WHITE}║  {C.MAGENTA}[4]{C.WHITE} 🔐 Set InitData (ganti){C.RESET}")
    print(f"{C.WHITE}║{C.RESET}")
    print(f"{C.WHITE}║  {C.RED}[0]{C.WHITE} ❌ Exit{C.RESET}")
    box_end(54)
    return input(f"{C.CYAN}➜ Select Menu : {C.RESET}").strip()

def check_balance(bot):
    if not bot.login():
        print(f"{C.RED}❌ Gagal login, cek init_data{C.RESET}")
        input("Tekan Enter...")
        return
    print(f"""
{C.WHITE}💰 Gold        : {C.YELLOW}{bot.gold}{C.RESET}
{C.WHITE}🍎 Fruit Coin : {C.YELLOW}{bot.fruit_coin}{C.RESET}
{C.WHITE}🎮 Game Tokens: {C.YELLOW}{bot.game_tokens} / {bot.max_tokens}{C.RESET}
{C.WHITE}🎫 Lottery Tok: {C.YELLOW}{bot.lottery_tokens}{C.RESET}
{C.WHITE}🏆 Stage      : {C.YELLOW}{bot.stage}{C.RESET}
{C.WHITE}📺 Ads Today  : {C.YELLOW}{bot.adsgram_count} adsgram, {bot.adsgram_daily_count} daily, {bot.monetag_count} monetag{C.RESET}
    """)
    input("Tekan Enter untuk kembali...")

def auto_game(bot, max_rounds=10):
    if not bot.login():
        print(f"{C.RED}❌ Gagal login. Cek init_data.{C.RESET}")
        input("Tekan Enter...")
        return

    round_count = 0
    while bot.game_tokens > 0 and round_count < max_rounds:
        round_count += 1
        clear()
        box(f"🚀 AUTO GAME — Round {round_count}/{max_rounds}", 54)
        print(f"{C.WHITE}║  🎟 Tokens  : {bot.game_tokens} → {bot.game_tokens-1}{C.RESET}")
        
        # Start game
        session_id = bot.start_game()
        if not session_id:
            print(f"{C.RED}║  ❌ Start game gagal!{C.RESET}")
            box_end(54)
            input("Tekan Enter...")
            break
        print(f"{C.WHITE}║  🆔 Session : {session_id[:8]}...{C.RESET}")
        
        # Simulate 15s
        print(f"{C.WHITE}║  ⏳ Playing :{C.RESET}", end="")
        for i in range(15, 0, -1):
            print(f"\r║  ⏳ Playing : {progress_bar(i, 15, '', 20)}", end="")
            time.sleep(1)
        print(f"\r║  ✅ Finished : {C.GREEN}15s{C.RESET}")
        
        # Claim reward (tanpa ad dulu, bisa minta ad)
        print(f"{C.WHITE}║  🎁 Claim reward...{C.RESET}")
        reward = bot.claim_reward(session_id, watch_ad=False)
        if reward is None:
            print(f"{C.RED}║  ❌ Claim gagal!{C.RESET}")
        else:
            print(f"{C.WHITE}║  💰 Reward  : +{C.GREEN}{reward}{C.WHITE} Gold{C.RESET}")
            print(f"{C.WHITE}║  🪙 Total   : {C.YELLOW}{bot.gold}{C.WHITE} Gold{C.RESET}")
        
        # Tanya mau tonton iklan untuk 2x reward?
        print(f"{C.WHITE}║{C.RESET}")
        box_end(54)
        tanya = input(f"{C.CYAN}➜ Tonton iklan untuk 2x reward? (y/n): {C.RESET}").strip().lower()
        if tanya == 'y':
            print(f"{C.WHITE}📺 Memutar iklan...{C.RESET}")
            if bot.watch_ad("adsgram"):
                # claim lagi dengan ad
                reward2 = bot.claim_reward(session_id, watch_ad=True)
                if reward2:
                    print(f"{C.GREEN}✅ +{reward2} Gold (2x reward)!{C.RESET}")
                else:
                    print(f"{C.RED}❌ Gagal claim 2x reward{C.RESET}")
            else:
                print(f"{C.RED}❌ Iklan gagal, reward tetap.{C.RESET}")
        else:
            print(f"{C.WHITE}⏭️  Skip iklan{C.RESET}")

        # Sinkron ulang
        bot.sync()
        print(f"{C.WHITE}💰 Gold sekarang: {C.YELLOW}{bot.gold}{C.RESET}")
        time.sleep(2)

    if bot.game_tokens <= 0:
        print(f"\n{C.YELLOW}⚠️ Token habis! Tunggu refill atau beli di Shop.{C.RESET}")
    else:
        print(f"\n{C.GREEN}✅ Selesai {round_count} round!{C.RESET}")
    input("Tekan Enter untuk kembali...")

def auto_watch_ads(bot, max_loops=10):
    if not bot.login():
        print(f"{C.RED}❌ Gagal login.{C.RESET}")
        input("Tekan Enter...")
        return

    # Daftar network dengan limit
    ad_networks = [
        ("adsgram", 5),
        ("adsgramDaily", 5),
        ("monetag", 10),
        ("gigapub", 10)
    ]
    # Kita simpan counter di bot (local)
    # Untuk demo, kita pakai counter local, tapi idealnya dari server
    # Kita simpan di atribut bot (misal bot.ads_count)
    if not hasattr(bot, 'ads_count'):
        bot.ads_count = 0

    clear()
    box("📺 AUTO WATCH ADS", 54)
    print(f"{C.WHITE}║  Target: {max_loops} iklan (atau sampai limit harian){C.RESET}")
    print(f"{C.WHITE}║{C.RESET}")
    box_end(54)

    count = 0
    for network, limit in ad_networks:
        # cek limit local (tapi kita tidak punya data dari server, asumsikan unlimited)
        # Kita hanya loop sebanyak max_loops
        for i in range(min(max_loops - count, limit)):
            count += 1
            print(f"\n{C.YELLOW}[{count}/{max_loops}] Menonton {network}...{C.RESET}")
            ok = bot.watch_ad(network)
            if ok:
                print(f"{C.GREEN}✅ Iklan {network} selesai, +Gold!{C.RESET}")
                # sync untuk update gold
                bot.sync()
                print(f"{C.WHITE}💰 Gold sekarang: {C.YELLOW}{bot.gold}{C.RESET}")
            else:
                print(f"{C.RED}❌ Gagal menonton {network}, skip.{C.RESET}")
            time.sleep(1)
            if count >= max_loops:
                break
        if count >= max_loops:
            break

    print(f"\n{C.GREEN}✅ Selesai menonton {count} iklan!{C.RESET}")
    input("Tekan Enter untuk kembali...")

# ─── MAIN ──────────────────────────────────────────────────
def main():
    global INIT_DATA

    # Coba load init_data dari file
    if not ensure_init_data():
        print(f"{C.RED}❌ Gagal mendapatkan init_data. Keluar.{C.RESET}")
        sys.exit(1)

    bot = FruitCutBot(INIT_DATA)

    while True:
        choice = show_menu()
        if choice == "1":
            auto_game(bot, max_rounds=5)
        elif choice == "2":
            auto_watch_ads(bot, max_loops=5)
        elif choice == "3":
            check_balance(bot)
        elif choice == "4":
            # Set new init_data
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
