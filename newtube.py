#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  ███╗   ██╗███████╗██╗    ██╗████████╗██╗   ██╗██████╗ ███████╗    ║
║  ████╗  ██║██╔════╝██║    ██║╚══██╔══╝██║   ██║██╔══██╗██╔════╝    ║
║  ██╔██╗ ██║█████╗  ██║ █╗ ██║   ██║   ██║   ██║██████╔╝█████╗      ║
║  ██║╚██╗██║██╔══╝  ██║███╗██║   ██║   ██║   ██║██╔══██╗██╔══╝      ║
║  ██║ ╚████║███████╗╚███╔███╔╝   ██║   ╚██████╔╝██████╔╝███████╗    ║
║  ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝    ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝    ║
║                                                                    ║
║           🤖 NEWTUBE TON AUTO WATCH ADS 🤖                      ║
║              AUTO WATCH • AUTO CLAIM • AUTO REWARD             ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import requests
import time
import random
import json
import os
import sys
from datetime import datetime

# ============================================================
# WARNA
# ============================================================
R, G, Y, B, M, C, W, X = '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[97m', '\033[0m'
CYAN = '\033[1;96m'
DIM = '\033[2;37m'

BANNER = f"""
{CYAN}╔══════════════════════════════════════════════════════════════════════╗
║  ███╗   ██╗███████╗██╗    ██╗████████╗██╗   ██╗██████╗ ███████╗    ║
║  ████╗  ██║██╔════╝██║    ██║╚══██╔══╝██║   ██║██╔══██╗██╔════╝    ║
║  ██╔██╗ ██║█████╗  ██║ █╗ ██║   ██║   ██║   ██║██████╔╝█████╗      ║
║  ██║╚██╗██║██╔══╝  ██║███╗██║   ██║   ██║   ██║██╔══██╗██╔══╝      ║
║  ██║ ╚████║███████╗╚███╔███╔╝   ██║   ╚██████╔╝██████╔╝███████╗    ║
║  ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝    ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝    ║
║                                                                    ║
║           {Y}🤖 NEWTUBE TON AUTO WATCH ADS 🤖{X}{CYAN}                      ║
║              {G}AUTO WATCH • AUTO CLAIM • AUTO REWARD{X}{CYAN}             ║
╚══════════════════════════════════════════════════════════════════════╝{X}
"""

MENU = f"""
{CYAN}╔══════════════════════════════════════════════╗
║              {Y}☁️ NEWTUBE TON ☁️{X}{CYAN}             ║
║          {CYAN}AUTO WATCH ADS + CLAIM{CYAN}           ║
╠══════════════════════════════════════════════╣
║  {G}[1] 🚀 Start Auto Watch{X}{CYAN}                  ║
║  {Y}[2] 🔑 Set Init Data{X}{CYAN}                    ║
║  {B}[3] 💰 Check Balance{X}{CYAN}                    ║
║                                              ║
║  {R}[0] ❌ Exit{X}{CYAN}                                ║
╚══════════════════════════════════════════════╝{X}
"""

# ============================================================
# KONFIGURASI
# ============================================================
CONFIG_FILE = "newtube_config.json"
BASE_URL = "https://newtube-ton.vercel.app"
NETWORKS = ["adsgramDaily", "adsgramSpecial", "monetag", "giga"]
MIN_DURATION = 18
MAX_DURATION = 21
FINGERPRINT = "6b988b3392f1bf292427f2dd31a5bf182e2d506792c36a6cd5fec011135fd8ee"

# Daftar User-Agent untuk rotasi
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/119.0",
]

# ============================================================
# FUNGSI UTILITY
# ============================================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print(BANNER)

def progress_bar(current, total, bar_len=20, fill='█', empty='░'):
    pct = current / total
    filled_len = int(bar_len * pct)
    bar = fill * filled_len + empty * (bar_len - filled_len)
    return f"[{bar}] {int(pct*100)}%"

def random_delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

def random_ua():
    return random.choice(USER_AGENTS)

def safe_json_response(resp):
    try:
        return resp.json()
    except:
        text = resp.text
        if text.startswith('\ufeff'):
            text = text[1:]
        return json.loads(text)

# ============================================================
# CLASS NewTubeBot
# ============================================================
class NewTubeBot:
    def __init__(self, init_data=None):
        self.init_data = init_data
        self.session = requests.Session()
        self._update_headers()

    def _update_headers(self):
        ua = random_ua()
        self.session.headers.update({
            "User-Agent": ua,
            "Accept": "application/json",
            "Accept-Language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "X-Requested-With": "org.telegram.messenger.web",
            "Origin": "https://newtube-ton.vercel.app",
            "Referer": "https://newtube-ton.vercel.app/",
            "Content-Type": "application/json",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Sec-Ch-Ua": f'"Not;A=Brand";v="8", "Chromium";v="{random.randint(100,120)}", "Android WebView";v="{random.randint(100,120)}"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            # X-Forwarded-For (hanya tipuan, tidak mengubah IP asli)
            "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        })

    def _request(self, method, endpoint, data=None, params=None):
        # Rotasi User-Agent setiap request
        self._update_headers()
        url = f"{BASE_URL}{endpoint}"
        if method.upper() == "GET":
            resp = self.session.get(url, params=params, timeout=15)
        else:
            resp = self.session.post(url, json=data, timeout=15)
        if resp.status_code != 200:
            raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")
        return safe_json_response(resp)

    def init_user(self):
        payload = {
            "action": "init",
            "fingerprint": FINGERPRINT,
            "initData": self.init_data
        }
        return self._request("POST", "/api/user", data=payload)

    def get_profile(self):
        params = {
            "action": "profile",
            "initData": self.init_data
        }
        return self._request("GET", "/api/user", params=params)

    def ad_start(self, network):
        payload = {
            "action": "adStart",
            "network": network,
            "initData": self.init_data
        }
        return self._request("POST", "/api/earn", data=payload)

    def claim_ad_reward(self, network, start_time, signature):
        payload = {
            "action": "claimAdReward",
            "network": network,
            "startTime": start_time,
            "signature": signature,
            "initData": self.init_data
        }
        return self._request("POST", "/api/earn", data=payload)

    def watch_all(self):
        print(f"{C}🔐 Initializing...{X}")
        try:
            init_resp = self.init_user()
            if init_resp.get("alreadyExists"):
                print(f"{G}✅ User already exists, lanjut...{X}")
            else:
                print(f"{G}✅ Init successful{X}")
        except Exception as e:
            print(f"{R}❌ Init failed: {e}{X}")
            return

        print(f"{C}👤 Getting profile...{X}")
        try:
            profile = self.get_profile()
            user = profile.get("user", {})
            print(f"{G}👤 User: {user.get('telegramUsername', 'N/A')}{X}")
            print(f"{G}💰 WTC Balance: {user.get('wtcBalance', 0)}{X}")
            print(f"{G}📈 Lifetime Earned: {user.get('lifetimeWtcEarned', 0)}{X}")
            print(f"{G}📺 Ads Watched Today: {user.get('adsWatchedToday', 0)}{X}")
            print(f"{G}📊 Lifetime Ads: {user.get('lifetimeAdsWatched', 0)}{X}")
        except Exception as e:
            print(f"{Y}⚠️ Failed to get profile: {e}{X}")

        for network in NETWORKS:
            print(f"\n{CYAN}=== Processing {network} ==={X}")
            attempts = 0
            while True:
                attempts += 1
                try:
                    start_resp = self.ad_start(network)
                    if not start_resp.get("ok"):
                        msg = start_resp.get("message", "")
                        if "limit" in msg.lower() or "daily" in msg.lower():
                            print(f"{Y}⚠️ Daily limit reached for {network}{X}")
                        else:
                            print(f"{Y}⚠️ Start failed: {start_resp}{X}")
                        break
                    start_time = start_resp.get("startTime")
                    signature = start_resp.get("signature")
                    if not start_time or not signature:
                        print(f"{R}❌ No startTime/signature in response{X}")
                        break

                    duration = random.randint(MIN_DURATION, MAX_DURATION)
                    print(f"\n{CYAN}╔══════════════════════════════════════════════╗")
                    print(f"║              {Y}📺 WATCHING ADS 📺{X}{CYAN}              ║")
                    print(f"║         {C}Network: {G}{network}{X}{CYAN}                 ║")
                    print(f"║         {C}Attempt: {G}{attempts}{X}{CYAN}                 ║")
                    print(f"╚══════════════════════════════════════════════╝{X}\n")
                    print(f"{C}⏳ Watching for {duration}s...{X}")
                    for sec in range(duration):
                        time.sleep(1)
                        bar = progress_bar(sec+1, duration)
                        sys.stdout.write(f"\r  {G}{bar}{X} {sec+1}s/{duration}s")
                        sys.stdout.flush()
                    print()

                    claim_resp = self.claim_ad_reward(network, start_time, signature)
                    if claim_resp.get("ok"):
                        reward = claim_resp.get("reward", 0)
                        count_today = claim_resp.get("countToday", 0)
                        daily_limit = claim_resp.get("dailyLimit", 0)
                        print(f"{G}✅ Claimed {reward} WTC! (Today: {count_today}/{daily_limit}){X}")
                        if daily_limit > 0 and count_today >= daily_limit:
                            print(f"{Y}⚠️ Daily limit reached for {network}{X}")
                            break
                    else:
                        print(f"{R}❌ Claim failed: {claim_resp}{X}")
                        break

                except Exception as e:
                    print(f"{R}❌ Error: {e}{X}")
                    break

                # Random delay antar request agar tidak terlalu cepat
                random_delay(2, 5)

        print(f"\n{G}✅ Selesai memproses semua network!{X}")

# ============================================================
# FUNGSI MENU
# ============================================================
def set_init_data():
    global bot
    clear_screen()
    print_header()
    print(f"\n{Y}🔑 SET INIT DATA{X}")
    print(f"{C}{'='*50}{X}")
    init_data = input(f"{G}Masukkan init_data (dari WebApp): {X}").strip()
    if not init_data:
        print(f"{R}❌ init_data tidak boleh kosong!{X}")
        time.sleep(2)
        return
    config = load_config() or {}
    config["init_data"] = init_data
    save_config(config)
    if bot:
        bot.init_data = init_data
    else:
        bot = NewTubeBot(init_data=init_data)
    print(f"{G}✅ Init data disimpan!{X}")
    time.sleep(1.5)

def start_auto_watch():
    global bot
    clear_screen()
    print_header()
    if not bot or not bot.init_data:
        print(f"{R}❌ Init data belum diset! Silakan menu 2 terlebih dahulu.{X}")
        time.sleep(2)
        return

    print(f"{G}🚀 Memulai auto watch...{X}")
    bot.watch_all()
    input(f"\n{C}Tekan Enter untuk kembali...{X}")

def check_balance():
    global bot
    clear_screen()
    print_header()
    if not bot or not bot.init_data:
        print(f"{R}❌ Init data belum diset! Silakan menu 2 terlebih dahulu.{X}")
        time.sleep(2)
        return

    try:
        profile = bot.get_profile()
        user = profile.get("user", {})
        print(f"{G}👤 User: {user.get('telegramUsername', 'N/A')}{X}")
        print(f"{G}💰 WTC Balance: {user.get('wtcBalance', 0)}{X}")
        print(f"{G}📈 Lifetime Earned: {user.get('lifetimeWtcEarned', 0)}{X}")
        print(f"{G}📺 Ads Watched Today: {user.get('adsWatchedToday', 0)}{X}")
        print(f"{G}📊 Lifetime Ads: {user.get('lifetimeAdsWatched', 0)}{X}")
    except Exception as e:
        print(f"{R}❌ Gagal mengambil data: {e}{X}")
    input(f"\n{C}Tekan Enter untuk kembali...{X}")

# ============================================================
# MAIN
# ============================================================
def main():
    global bot
    config = load_config()
    if config:
        init_data = config.get("init_data")
        if init_data:
            bot = NewTubeBot(init_data=init_data)
            print(f"{G}🔑 Config ditemukan, init_data siap.{X}")
            time.sleep(1)
        else:
            bot = None
    else:
        bot = None

    while True:
        clear_screen()
        print_header()
        print(MENU)
        status = "🟢 Siap" if bot and bot.init_data else "🔴 Belum set init_data"
        print(f"{DIM}Status: {status}{X}")

        choice = input(f"\n{CYAN}Pilih Menu » {X}").strip()

        if choice == "1":
            start_auto_watch()
        elif choice == "2":
            set_init_data()
        elif choice == "3":
            check_balance()
        elif choice == "0":
            print(f"\n{R}❌ Exit...{X}")
            sys.exit(0)
        else:
            print(f"{R}❌ Pilihan tidak valid!{X}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Y}⏹ Dihentikan oleh user.{X}")
        sys.exit(0)
