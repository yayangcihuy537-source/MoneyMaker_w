#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  ██████╗ ███████╗██████╗ ███████╗   ║
║  ██╔══██╗██╔════╝██╔══██╗██╔════╝   ║
║  ██████╔╝█████╗  ██║  ██║█████╗     ║
║  ██╔══██╗██╔══╝  ██║  ██║██╔══╝     ║
║  ██║  ██║███████╗██████╔╝███████╗   ║
║  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝   ║
║                                                                    ║
║           🔴 REDTUBE TON AUTO WATCH ADS 🔴                         ║
║              AUTO WATCH • AUTO SPIN • AUTO REWARD                  ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import requests
import time
import random
import json
import os
import sys

# ============================================================
# WARNA
# ============================================================
R, G, Y, B, M, C, W, X = '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[97m', '\033[0m'
CYAN = '\033[1;96m'
DIM = '\033[2;37m'

BANNER = f"""
{CYAN}╔══════════════════════════════════════════════════════════════════════╗
║  ██████╗ ███████╗██████╗ ███████╗   ║
║  ██╔══██╗██╔════╝██╔══██╗██╔════╝   ║
║  ██████╔╝█████╗  ██║  ██║█████╗     ║
║  ██╔══██╗██╔══╝  ██║  ██║██╔══╝     ║
║  ██║  ██║███████╗██████╔╝███████╗   ║
║  ╚═╝  ╚═╝╚══════╝╚═════╝ ╚══════╝   ║
║                                                                    ║
║           {R}🔴 REDTUBE TON AUTO WATCH ADS 🔴{X}{CYAN}                      ║
║              {G}AUTO WATCH • AUTO SPIN • AUTO REWARD{X}{CYAN}             ║
╚══════════════════════════════════════════════════════════════════════╝{X}
"""

MENU = f"""
{CYAN}╔══════════════════════════════════════════════╗
║              {Y}☁️ REDTUBE TON ☁️{X}{CYAN}             ║
║          {CYAN}AUTO WATCH ADS + SPIN + CLAIM{CYAN}       ║
╠══════════════════════════════════════════════╣
║  {G}[1] 🚀 Start Auto Watch & Spin{X}{CYAN}           ║
║  {Y}[2] 🔑 Set Init Data{X}{CYAN}                    ║
║  {B}[3] 💰 Check Balance{X}{CYAN}                    ║
║                                              ║
║  {R}[0] ❌ Exit{X}{CYAN}                                ║
╚══════════════════════════════════════════════╝{X}
"""

# ============================================================
# KONFIGURASI
# ============================================================
CONFIG_FILE = "redtube_config.json"
BASE_URL = "https://redtube-nine.vercel.app"
MIN_DURATION = 15
MAX_DURATION = 25

# Urutan prioritas network ads: Adsgram dulu -> Monetag -> Seterusnya
ADS_PRIORITY = ["adsgram", "adsgram_daily", "adsgram_special", "monetag", "gigapub", "giga"]

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

def jitter_delay(base=2, jitter=3):
    time.sleep(random.uniform(base, base + jitter))

def safe_json_response(resp):
    try:
        return resp.json()
    except:
        text = resp.text
        if text.startswith('\ufeff'):
            text = text[1:]
        return json.loads(text)

# ============================================================
# CLASS RedTubeBot
# ============================================================
class RedTubeBot:
    def __init__(self, init_data=None):
        self.init_data = init_data
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.1 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
            "Accept": "application/json",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "X-Requested-With": "org.telegram.messenger.web",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
            "Content-Type": "application/json",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Sec-Ch-Ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "X-Telegram-Init-Data": self.init_data
        })
        # Menyimpan daftar network yang error/403 agar di-skip selamanya selama sesi ini
        self.blocked_networks = set()

    def update_headers(self):
        self.session.headers.update({
            "X-Telegram-Init-Data": self.init_data
        })

    def _request(self, method, endpoint, data=None, params=None, retries=3):
        url = f"{BASE_URL}{endpoint}"
        self.update_headers()
        for attempt in range(retries):
            try:
                if method.upper() == "GET":
                    resp = self.session.get(url, params=params, timeout=15)
                else:
                    resp = self.session.post(url, json=data, timeout=15)
                
                if resp.status_code == 429:
                    wait = random.randint(30, 60)
                    print(f"{Y}⚠️ Rate limit (429), tidur {wait} detik...{X}")
                    time.sleep(wait)
                    continue
                
                # Khusus handle 403 atau error akses pada earn post
                if resp.status_code == 403:
                    return {"success": False, "status_code": 403, "error": "Forbidden"}

                if resp.status_code != 200:
                    raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")
                return safe_json_response(resp)
            except Exception as e:
                if attempt == retries - 1:
                    return {"success": False, "error": str(e)}
                wait = random.randint(3, 6)
                time.sleep(wait)

    def get_user_profile(self):
        return self._request("GET", "/api/user")

    def get_earn_status(self):
        return self._request("GET", "/api/earn")

    def post_earn(self, payload):
        return self._request("POST", "/api/earn", data=payload)

    def get_spin_status(self):
        return self._request("GET", "/api/earn?type=spin")

    def watch_all(self):
        print(f"{C}🔐 Mengambil profil user...{X}")
        try:
            profile = self.get_user_profile()
            print(f"{G}👤 User: {profile.get('username', 'N/A')}{X}")
            print(f"{G}💰 Balance: {profile.get('balance', 0)}{X}")
            print(f"{G}💎 USDT Balance: {profile.get('usdtBalance', 0)}{X}")
            print(f"{G}📺 Ads Watched Today: {profile.get('adsWatchedToday', 0)}{X}")
        except Exception as e:
            print(f"{R}❌ Gagal ambil profil: {e}{X}")
            return

        jitter_delay(2, 3)

        # 1. AUTO WATCH ADS (Ads -> Monetag -> Seterusnya, skip jika kena 403/gagal)
        print(f"\n{CYAN}=== Memulai Auto Watch Ads (Ads => Monetag => Seterusnya) ==={X}")
        while True:
            try:
                status = self.get_earn_status()
                if not status:
                    print(f"{Y}⚠️ Gagal ambil status earn{X}")
                    break

                target_network = None
                
                # Cek berdasarkan urutan prioritas, pastikan tidak masuk daftar blocked_networks
                for p_net in ADS_PRIORITY:
                    if p_net in status and p_net not in self.blocked_networks:
                        data = status[p_net]
                        if data:
                            limit_reached = data.get("limitReached", False)
                            cooldown = data.get("cooldownSecondsLeft", 0)
                            watched = data.get("watchedToday", 0)
                            limit = data.get("limit", 0)
                            
                            if not limit_reached and (limit == 0 or watched < limit) and cooldown == 0:
                                target_network = p_net
                                break

                # Kalau di prioritas belum ketemu, cek network lain yang ada di response API
                if not target_network:
                    for network, data in status.items():
                        if network not in ADS_PRIORITY and network not in self.blocked_networks and data:
                            limit_reached = data.get("limitReached", False)
                            cooldown = data.get("cooldownSecondsLeft", 0)
                            watched = data.get("watchedToday", 0)
                            limit = data.get("limit", 0)
                            
                            if not limit_reached and (limit == 0 or watched < limit) and cooldown == 0:
                                target_network = network
                                break

                if not target_network:
                    print(f"{Y}🏁 Semua limit ads dari seluruh network sudah habis atau ter-block! Lanjut ke Spin...{X}")
                    break

                print(f"\n{CYAN}Network aktif: {G}{target_network}{X}")
                duration = random.randint(MIN_DURATION, MAX_DURATION)
                print(f"{C}⏳ Menonton iklan selama {duration}s...{X}")
                
                for sec in range(duration):
                    time.sleep(1)
                    bar = progress_bar(sec+1, duration)
                    sys.stdout.write(f"\r  {G}{bar}{X} {sec+1}s/{duration}s")
                    sys.stdout.flush()
                print()

                res = self.post_earn({"network": target_network})
                
                # Handle jika response gagal atau 403 (Detected)
                if res.get("status_code") == 403 or not res.get("success"):
                    print(f"{R}🚨 DETECTED / Gagal pada network {target_network}! Network di-skip selamanya.{X}")
                    self.blocked_networks.add(target_network)
                    time.sleep(2)
                    continue

                if res.get("success"):
                    reward = res.get("reward", 0)
                    watched = res.get("watchedToday", 0)
                    limit = res.get("limit", 0)
                    print(f"{G}✅ Reward +{reward}! (Watched: {watched}/{limit}){X}")
                else:
                    print(f"{Y}⚠️ Respon: {res}{X}")
                    time.sleep(2)
                
                jitter_delay(2, 3)

            except Exception as e:
                print(f"{R}❌ Error Watch: {e}{X}")
                break

        # 2. AUTO SPIN (Setelah semua ads habis, baru lanjut spin sampai habis)
        print(f"\n{CYAN}=== Memulai Auto Spin (Sampai Habis) ==={X}")
        while True:
            try:
                spin_status = self.get_spin_status()
                if not spin_status:
                    print(f"{Y}⚠️ Gagal ambil status spin{X}")
                    break

                spins_available = spin_status.get("spinsAvailable", 0)
                cooldown = spin_status.get("spinCooldownSecondsLeft", 0)
                next_network = spin_status.get("nextNetwork", "monetag")

                print(f"{C}🎡 Spins Tersedia: {G}{spins_available}{X} | {C}Cooldown: {Y}{cooldown}s{X}")

                if spins_available <= 0:
                    print(f"{Y}🏁 Spin sudah habis total!{X}")
                    break

                if cooldown > 0:
                    print(f"{Y}⏳ Spin kena cooldown, menunggu selama {cooldown} detik...{X}")
                    time.sleep(cooldown + 1)
                    continue

                print(f"{C}🔄 Melakukan spin pada network: {G}{next_network}{X}")
                res = self.post_earn({"action": "spin", "network": next_network})
                
                if res.get("status_code") == 403 or not res.get("success", True):
                    print(f"{R}🚨 DETECTED / Gagal saat spin! Menghentikan spin.{X}")
                    break

                print(f"{G}✅ Spin Result: {res}{X}")
                jitter_delay(3, 4)

            except Exception as e:
                print(f"{R}❌ Error Spin: {e}{X}")
                break

        print(f"\n{G}✅ Seluruh proses ads & spin sudah selesai total, bot berhenti! ><{X}")

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
        bot.update_headers()
    else:
        bot = RedTubeBot(init_data=init_data)
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

    print(f"{G}🚀 Memulai auto watch & spin...{X}")
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
        profile = bot.get_user_profile()
        print(f"{G}👤 User: {profile.get('username', 'N/A')}{X}")
        print(f"{G}📛 Nama: {profile.get('firstName', 'N/A')}{X}")
        print(f"{G}💰 Balance: {profile.get('balance', 0)}{X}")
        print(f"{G}💎 USDT Balance: {profile.get('usdtBalance', 0)}{X}")
        print(f"{G}📈 Lifetime Earned: {profile.get('lifetimeEarned', 0)}{X}")
        print(f"{G}📺 Ads Watched Today: {profile.get('adsWatchedToday', 0)}{X}")
        print(f"{G}📋 Tasks Done Today: {profile.get('tasksDoneToday', 0)}{X}")
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
            bot = RedTubeBot(init_data=init_data)
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

