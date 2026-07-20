#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  💰 PAIDADZ BOT — Auto Watch Ads (ADAPTIF LIMIT)      ║
║  🔐 Login via InitData                                 ║
║  📺 Adsgram • Monetag • Gigapub (limit dinamis)       ║
║  🛑 Stop otomatis jika semua iklan habis             ║
║  ⏭️  429 atau limit = skip provider, lanjut yang lain ║
║  👑 Owner: @MoneyMaker_w                              ║
╚══════════════════════════════════════════════════════════╝
"""

import requests
import json
import os
import sys
import time
import random
import hashlib
from urllib.parse import parse_qs, unquote

# WARNA
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
BLUE = "\033[1;34m"
PURPLE = "\033[38;5;141m"
PINK = "\033[38;5;206m"
LIME = "\033[38;5;154m"
GOLD = "\033[38;5;220m"
DIM = "\033[2;37m"
RESET = "\033[0m"

# KONFIGURASI
CONFIG_FILE = "paidadz_config.json"
BASE_URL = "https://paidadz.xyz"
MIN_AD_DURATION = 11
MAX_AD_DURATION = 14
TIMER_CYCLE = 3

class Config:
    def __init__(self):
        self.init_data = None
        self.device_id = None
        self.session_cookie = None

    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.init_data = data.get('init_data')
                self.device_id = data.get('device_id')
                self.session_cookie = data.get('session_cookie')
                return True
        return False

    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'init_data': self.init_data,
                'device_id': self.device_id,
                'session_cookie': self.session_cookie
            }, f, indent=2)

    def clear(self):
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

def extract_user_id(init_data):
    parsed = parse_qs(init_data)
    user_str = parsed.get('user', [None])[0]
    if user_str:
        try:
            user_json = json.loads(unquote(user_str))
            return str(user_json.get('id'))
        except:
            pass
    return None

def show_banner():
    print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════╗
║   {GOLD}💰 PAIDADZ BOT — Limit Adaptif {PURPLE}                      ║
║   {LIME}📺 Adsgram • Monetag • Gigapub (limit dinamis)    {PURPLE}║
║   {LIME}⏭️  429 atau limit = skip provider, lanjut yang lain{PURPLE}║
║   {PINK}👑 Owner: @MoneyMaker_w                           {PURPLE}║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

class PaidAdzBot:
    def __init__(self, init_data, device_id=None, session_cookie=None):
        self.init_data = init_data
        self.device_id = device_id if device_id else self.generate_device_id()
        self.session = requests.Session()
        self.base_url = BASE_URL
        self.balance = 0
        self.total_watched_today = 0

        self.ag_count = 0
        self.mt_count = 0
        self.gp_count = 0

        self.ag_done = False
        self.mt_done = False
        self.gp_done = False

        self.cookie = session_cookie

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) Telegram-Android/12.6.4 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Origin": BASE_URL,
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://paidadz.xyz/",
            "Connection": "keep-alive",
            "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "x-tg-platform": "android",
            "x-device-id": self.device_id,
            "x-telegram-data": self.init_data,
        }
        if session_cookie:
            self.session.cookies.set("connect.sid", session_cookie)

    def generate_device_id(self):
        return hashlib.md5(f"{time.time()}{random.randint(1,999999)}".encode()).hexdigest()

    def generate_session_id(self):
        ts = int(time.time() * 1000)
        rand_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=7))
        hex_str = ''.join(random.choices('abcdef0123456789', k=12))
        return f"{ts}-{rand_str}-{hex_str}"

    def interaction_proof(self):
        now_ms = int(time.time() * 1000)
        return {
            "entropy": random.randint(0, 5),
            "timestamp": now_ms,
            "heartbeat": now_ms - random.randint(100, 5000),
            "visible": True
        }

    def device_fingerprint(self):
        return {
            "userAgent": "Mozilla/5.0 (Linux; Android 16; K) Telegram-Android/12.6.4 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
            "platform": "Linux aarch64",
            "language": "id-ID",
            "languages": "id-ID,en-US",
            "screenW": 384,
            "screenH": 832,
            "colorDepth": 24,
            "timezone": "Asia/Jakarta",
            "cookieEnabled": True,
            "doNotTrack": None,
            "hardwareConcurrency": 8,
            "deviceMemory": 8,
            "tgPlatform": "android",
            "tgVersion": "9.6",
            "tgColorScheme": "dark",
            "tgIsExpanded": True
        }

    def _request(self, method, endpoint, data=None, params=None, extra_headers=None):
        headers = self.headers.copy()
        if extra_headers:
            headers.update(extra_headers)
        if data is not None:
            headers["Content-Length"] = str(len(json.dumps(data)))
        headers["x-interaction-proof"] = json.dumps(self.interaction_proof())
        headers["x-device-fingerprint"] = json.dumps(self.device_fingerprint())
        headers["x-telegram-data"] = self.init_data
        if self.cookie:
            self.session.cookies.set("connect.sid", self.cookie)

        url = f"{self.base_url}{endpoint}"
        if method.lower() == "get":
            resp = self.session.get(url, headers=headers, params=params)
        else:
            resp = self.session.post(url, headers=headers, json=data)
        for cookie in self.session.cookies:
            if cookie.name == "connect.sid":
                self.cookie = cookie.value
        return resp

    def auth(self):
        print(f"{BLUE}┌─ 🔐 Auth via Telegram...{RESET}")
        payload = {"initData": self.init_data}
        resp = self._request("post", "/api/auth/telegram", data=payload)
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(f"{GREEN}└─ ✅ Auth berhasil! User: {data.get('username')}{RESET}")
                return True
            except:
                print(f"{GREEN}└─ ✅ Auth berhasil!{RESET}")
                return True
        else:
            print(f"{RED}└─ ❌ Auth gagal: {resp.status_code}{RESET}")
            return False

    def get_user(self):
        print(f"{BLUE}┌─ 📊 Get User Status...{RESET}")
        resp = self._request("get", "/api/auth/user")
        if resp.status_code == 200:
            try:
                data = resp.json()
                self.balance = float(data.get('balance', 0))
                self.total_watched_today = data.get('ads_watched_today', 0)
                print(f"{GREEN}└─ ✅ Balance: {self.balance} POW | Total hari ini: {self.total_watched_today}{RESET}")
                return data
            except:
                print(f"{GREEN}└─ ✅ Status loaded{RESET}")
                return {}
        else:
            print(f"{RED}└─ ❌ Gagal: {resp.status_code}{RESET}")
            return {}

    def watch_ad(self, ad_type, label):
        # Jika provider sudah ditandai done, skip
        if ad_type == "adsgram" and self.ag_done:
            print(f"{YELLOW}⏹️ {label} sudah limit/skip, lewati...{RESET}")
            return True
        if ad_type == "monetag" and self.mt_done:
            print(f"{YELLOW}⏹️ {label} sudah limit/skip, lewati...{RESET}")
            return True
        if ad_type == "gigapub" and self.gp_done:
            print(f"{YELLOW}⏹️ {label} sudah limit/skip, lewati...{RESET}")
            return True

        print(f"{BLUE}┌─ 🎬 Register {label} Session...{RESET}")
        session_id = self.generate_session_id()
        reg_payload = {
            "sessionId": session_id,
            "adType": ad_type,
            "context": "ads_watch"
        }
        resp_reg = self._request("post", "/api/ads/register-session", data=reg_payload)
        if resp_reg.status_code == 429:
            print(f"{YELLOW}└─ ⏳ {label} 429 (rate limit) — skip provider ini{RESET}")
            if ad_type == "adsgram":
                self.ag_done = True
            elif ad_type == "monetag":
                self.mt_done = True
            elif ad_type == "gigapub":
                self.gp_done = True
            return True
        if resp_reg.status_code != 200:
            print(f"{RED}└─ ❌ Register session gagal: {resp_reg.status_code}{RESET}")
            return False

        duration = random.randint(MIN_AD_DURATION, MAX_AD_DURATION)
        start_time = int(time.time() * 1000)

        print(f"{BLUE}┌─ 📺 Menonton iklan {duration} detik...{RESET}")
        for i in range(duration, 0, -1):
            sys.stdout.write(f"\r{YELLOW}⏳ Sisa waktu {i} detik{RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print()
        end_time = int(time.time() * 1000)
        actual_duration = end_time - start_time

        watch_payload = {
            "adType": ad_type,
            "sessionId": session_id,
            "backgroundDuration": actual_duration,
            "backgroundEntered": True,
            "sessionStart": start_time
        }
        print(f"{BLUE}┌─ 💰 Claim {label} Ad...{RESET}")
        resp_watch = self._request("post", "/api/ads/watch", data=watch_payload)
        if resp_watch.status_code == 429:
            print(f"{YELLOW}└─ ⏳ {label} 429 (rate limit) — skip provider ini{RESET}")
            if ad_type == "adsgram":
                self.ag_done = True
            elif ad_type == "monetag":
                self.mt_done = True
            elif ad_type == "gigapub":
                self.gp_done = True
            return True
        if resp_watch.status_code == 200:
            try:
                data = resp_watch.json()
                if data.get('success'):
                    reward = data.get('rewardPOW', 0)
                    self.balance = float(data.get('newBalance', self.balance))
                    if ad_type == "adsgram":
                        self.ag_count += 1
                    elif ad_type == "monetag":
                        self.mt_count += 1
                    elif ad_type == "gigapub":
                        self.gp_count += 1
                    print(f"{GREEN}└─ ✅ {label} +{reward} POW | Balance: {self.balance} POW (Watch {data.get('adsWatchedToday', 0)} today){RESET}")
                    return True
                else:
                    err = data.get('message', 'Unknown error')
                    if 'limit' in err.lower():
                        print(f"{YELLOW}└─ ⚠️ {label} limit: {err} — skip provider ini{RESET}")
                        if ad_type == "adsgram":
                            self.ag_done = True
                        elif ad_type == "monetag":
                            self.mt_done = True
                        elif ad_type == "gigapub":
                            self.gp_done = True
                        return True
                    else:
                        print(f"{RED}└─ ❌ Claim gagal: {err}{RESET}")
                        return False
            except:
                print(f"{GREEN}└─ ✅ {label} claimed!{RESET}")
                return True
        else:
            print(f"{RED}└─ ❌ Claim gagal: {resp_watch.status_code}{RESET}")
            return False

    def watch_adsgram(self):
        return self.watch_ad("adsgram", "AdsGram")

    def watch_monetag(self):
        return self.watch_ad("monetag", "MonetaG")

    def watch_gigapub(self):
        return self.watch_ad("gigapub", "Gigapub")

    def is_all_done(self):
        # Bot berhenti hanya jika semua provider sudah ditandai done (limit/429)
        return self.ag_done and self.mt_done and self.gp_done

    def countdown(self, seconds, msg="⏳ Menunggu"):
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r{YELLOW}{msg} {i} detik{RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print()

    def farming_loop(self):
        print(f"{CYAN}🚀 Starting farming ads...{RESET}")
        print(f"{YELLOW}📺 AdsGram: {self.ag_count} | MonetaG: {self.mt_count} | Gigapub: {self.gp_count}{RESET}")
        print(f"{YELLOW}⏱️ Durasi iklan acak 11-14 detik (anti-detection){RESET}")
        print(f"{YELLOW}🛑 Bot akan berhenti jika semua provider sudah limit/429{RESET}")
        print(f"{YELLOW}Press Ctrl+C to stop{RESET}\n")

        cycle = 0
        while True:
            cycle += 1
            print(f"\n{CYAN}🔄 Cycle #{cycle}{RESET}")

            self.get_user()

            if self.is_all_done():
                print(f"\n{GREEN}✅ Semua iklan sudah ditonton / limit hari ini!{RESET}")
                print(f"📊 Total iklan hari ini: {self.total_watched_today}")
                print(f"📊 AdsGram: {self.ag_count} | MonetaG: {self.mt_count} | Gigapub: {self.gp_count}")
                break

            # AdsGram
            print(f"\n{YELLOW}📺 AdsGram ({self.ag_count} watched)...{RESET}")
            if self.ag_done:
                print(f"{YELLOW}⏹️ AdsGram sudah limit/skip, lewati...{RESET}")
            else:
                self.watch_adsgram()
                self.countdown(TIMER_CYCLE, "⏳ Jeda")

            # MonetaG
            print(f"\n{YELLOW}📺 MonetaG ({self.mt_count} watched)...{RESET}")
            if self.mt_done:
                print(f"{YELLOW}⏹️ MonetaG sudah limit/skip, lewati...{RESET}")
            else:
                self.watch_monetag()
                self.countdown(TIMER_CYCLE, "⏳ Jeda")

            # Gigapub
            print(f"\n{YELLOW}📺 Gigapub ({self.gp_count} watched)...{RESET}")
            if self.gp_done:
                print(f"{YELLOW}⏹️ Gigapub sudah limit/skip, lewati...{RESET}")
            else:
                self.watch_gigapub()
                self.countdown(TIMER_CYCLE, "⏳ Jeda")

            print(f"{DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f"{YELLOW}⏰ Cycle #{cycle} selesai. Tunggu {TIMER_CYCLE} detik...{RESET}")
            self.countdown(TIMER_CYCLE, "⏳ Next cycle dalam")

# ==================== MENU ====================
def show_menu():
    print(f"\n{CYAN}╔════════════════════════════════════════════════════╗")
    print(f"║                    MAIN MENU                         ║")
    print(f"╠════════════════════════════════════════════════════╣")
    print(f"║  {GREEN}[1]{RESET} 🚀 Start Farming (All Ads)                ║")
    print(f"║  {YELLOW}[2]{RESET} 📝 Set InitData                         ║")
    print(f"║  {YELLOW}[3]{RESET} ⚙️  Reset Config                         ║")
    print(f"║  {BLUE}[4]{RESET} 💰 Check Balance                         ║")
    print(f"║  {RED}[0]{RESET} ❌ Exit                                  ║")
    print(f"╚════════════════════════════════════════════════════╝{RESET}")

def start_farming():
    config = Config()
    if not config.load():
        print(f"{RED}❌ InitData belum diset!{RESET}")
        print(f"{YELLOW}📝 Set dulu di menu 2.{RESET}")
        input("Tekan Enter untuk kembali...")
        return

    bot = PaidAdzBot(config.init_data, config.device_id, config.session_cookie)

    if not bot.auth():
        print(f"{RED}❌ Auth gagal. Cek InitData.{RESET}")
        input("Tekan Enter untuk kembali...")
        return

    if bot.cookie:
        config.session_cookie = bot.cookie
    if bot.device_id:
        config.device_id = bot.device_id
    config.save()

    bot.get_user()
    bot.farming_loop()
    input("Tekan Enter untuk kembali ke menu...")

def main():
    config = Config()
    config.load()

    while True:
        show_banner()
        show_menu()

        if config.init_data:
            print(f"{GREEN}✅ InitData tersimpan (panjang: {len(config.init_data)}){RESET}")
        else:
            print(f"{RED}❌ InitData belum diset!{RESET}")

        choice = input(f"\n{PURPLE}❯ Pilih: {RESET}").strip()

        if choice == '0':
            print(f"{YELLOW}👋 Bye!{RESET}")
            sys.exit(0)

        elif choice == '1':
            start_farming()

        elif choice == '2':
            print(f"{YELLOW}📝 Masukkan InitData dari Telegram:{RESET}")
            print(f"{DIM}Contoh: user=%7B%22id%22...&auth_date=...&hash=...{RESET}")
            qid = input("InitData: ").strip()
            if qid:
                config.init_data = qid
                config.session_cookie = None
                config.device_id = None
                config.save()
                print(f"{GREEN}✅ InitData disimpan!{RESET}")
            else:
                print(f"{RED}❌ InitData tidak boleh kosong!{RESET}")
            input("Tekan Enter untuk kembali...")

        elif choice == '3':
            print(f"{YELLOW}⚠️ Reset Config akan menghapus semua data login.{RESET}")
            confirm = input("Yakin? (y/n): ").strip().lower()
            if confirm == 'y':
                config.clear()
                print(f"{GREEN}✅ Config direset!{RESET}")
            else:
                print(f"{YELLOW}⏹️ Dibatalkan.{RESET}")
            input("Tekan Enter untuk kembali...")

        elif choice == '4':
            if not config.init_data:
                print(f"{RED}❌ InitData belum diset!{RESET}")
                input("Tekan Enter...")
                continue
            bot = PaidAdzBot(config.init_data, config.device_id, config.session_cookie)
            if bot.auth():
                bot.get_user()
            input("Tekan Enter untuk kembali...")

        else:
            print(f"{RED}❌ Pilihan salah!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}⚠️ Keluar...{RESET}")
        sys.exit(0)
