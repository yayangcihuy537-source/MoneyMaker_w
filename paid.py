#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  💰 PAIDADZ BOT — Human-like Auto Watch              ║
║  🔐 Login via InitData + Auto Retry                   ║
║  📺 Adsgram (225x) • Monetag (30x) • Gigapub (30x)   ║
║  🛑 Stop otomatis jika semua iklan habis             ║
║  ⏭️  429 = skip provider, lanjut yang lain           ║
║  🕒 Human-like delays (random & unpredictable)       ║
║  👑 Developer: ScriptyXSouu                          ║
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
# === HUMAN-LIKE RANDOM TIMERS ===
MIN_AD_DURATION = 10
MAX_AD_DURATION = 25          # lebih variatif
MIN_PAUSE_BETWEEN_ADS = 5
MAX_PAUSE_BETWEEN_ADS = 15    # jeda antar iklan
MIN_PAUSE_BETWEEN_CYCLES = 3
MAX_PAUSE_BETWEEN_CYCLES = 8  # jeda antar cycle
REQUEST_DELAY_MIN = 0.5
REQUEST_DELAY_MAX = 3.0       # delay sebelum request

RETRY_DELAY = 5
MAX_RETRIES = 3

MAX_ADSGRAM = 225
MAX_MONETAG = 30
MAX_GIGAPUB = 30
TOTAL_LIMIT = MAX_ADSGRAM + MAX_MONETAG + MAX_GIGAPUB

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

def show_banner():
    print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════╗
║   {GOLD}💰 PAIDADZ BOT — Human-like Auto Watch           {PURPLE}║
║   {LIME}📺 Adsgram (225x) • Monetag (30x) • Gigapub (30x){PURPLE}║
║   {LIME}⏭️  429 otomatis skip provider, lanjut yang lain   {PURPLE}║
║   {LIME}🕒 Human delays: random & unpredictable         {PURPLE}║
║   {PINK}👑 Developer: ScriptyXSouu                           {PURPLE}║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

def human_pause(min_sec, max_sec, label="⏳"):
    """Jeda dengan durasi random antara min_sec dan max_sec"""
    duration = random.uniform(min_sec, max_sec)
    print(f"{YELLOW}{label} Jeda {duration:.1f} detik...{RESET}")
    time.sleep(duration)

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
        if self.cookie:
            self.session.cookies.set("connect.sid", self.cookie)

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

    def _request(self, method, endpoint, data=None, params=None, extra_headers=None, retry=True):
        # === HUMAN-LIKE DELAY SEBELUM REQUEST ===
        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        time.sleep(delay)

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
        for attempt in range(MAX_RETRIES):
            try:
                if method.lower() == "get":
                    resp = self.session.get(url, headers=headers, params=params)
                else:
                    resp = self.session.post(url, headers=headers, json=data)
                # Simpan cookie dari response
                for cookie in self.session.cookies:
                    if cookie.name == "connect.sid":
                        self.cookie = cookie.value
                # Jika status 429 atau 433, tunggu dan retry
                if resp.status_code in [429, 433] and retry:
                    print(f"{YELLOW}⚠️ Rate limit ({resp.status_code}), tunggu {RETRY_DELAY}s...{RESET}")
                    time.sleep(RETRY_DELAY)
                    continue
                return resp
            except Exception as e:
                print(f"{RED}❌ Request error: {e}{RESET}")
                if retry:
                    time.sleep(RETRY_DELAY)
                    continue
                return None
        # Jika semua retry gagal
        if resp.status_code in [429, 433]:
            print(f"{RED}❌ Rate limit persistent, coba lagi nanti.{RESET}")
        return resp

    def auth(self):
        print(f"{BLUE}┌─ 🔐 Auth via Telegram...{RESET}")
        payload = {"initData": self.init_data}
        resp = self._request("post", "/api/auth/telegram", data=payload, retry=True)
        if resp and resp.status_code == 200:
            try:
                data = resp.json()
                print(f"{GREEN}└─ ✅ Auth berhasil! User: {data.get('username')}{RESET}")
                return True
            except:
                print(f"{GREEN}└─ ✅ Auth berhasil!{RESET}")
                return True
        else:
            if resp:
                print(f"{RED}└─ ❌ Auth gagal: {resp.status_code} - {resp.text[:100]}{RESET}")
            else:
                print(f"{RED}└─ ❌ Auth gagal: no response{RESET}")
            return False

    def get_user(self):
        print(f"{BLUE}┌─ 📊 Get User Status...{RESET}")
        resp = self._request("get", "/api/auth/user", retry=True)
        if resp and resp.status_code == 200:
            try:
                data = resp.json()
                self.balance = float(data.get('balance', 0))
                self.total_watched_today = data.get('ads_watched_today', 0)
                print(f"{GREEN}└─ ✅ Balance: {self.balance} POW | Total hari ini: {self.total_watched_today}/{TOTAL_LIMIT}{RESET}")
                return data
            except:
                print(f"{GREEN}└─ ✅ Status loaded{RESET}")
                return {}
        else:
            print(f"{RED}└─ ❌ Gagal: {resp.status_code if resp else 'No response'}{RESET}")
            return {}

    def watch_ad(self, ad_type, label):
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
        resp_reg = self._request("post", "/api/ads/register-session", data=reg_payload, retry=True)
        if not resp_reg:
            print(f"{RED}└─ ❌ Register session gagal (no response){RESET}")
            return False
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

        # === DURASI NONTON RANDOM (HUMAN-LIKE) ===
        duration = random.randint(MIN_AD_DURATION, MAX_AD_DURATION)
        start_time = int(time.time() * 1000)

        print(f"{BLUE}┌─ 📺 Menonton iklan {duration} detik...{RESET}")
        # Tampilkan countdown hanya beberapa kali biar gak spam
        for i in range(duration, 0, -1):
            if i % 3 == 0 or i <= 5:  # tampilkan tiap 3 detik atau 5 detik terakhir
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
        resp_watch = self._request("post", "/api/ads/watch", data=watch_payload, retry=True)
        if not resp_watch:
            print(f"{RED}└─ ❌ Claim gagal (no response){RESET}")
            return False
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
        return (self.ag_done and self.mt_done and self.gp_done) or self.total_watched_today >= TOTAL_LIMIT

    def human_pause(self, min_sec, max_sec, label="⏳ Jeda"):
        duration = random.uniform(min_sec, max_sec)
        print(f"{YELLOW}{label} {duration:.1f} detik...{RESET}")
        time.sleep(duration)

    def farming_loop(self):
        print(f"{CYAN}🚀 Starting farming ads...{RESET}")
        print(f"{YELLOW}📺 AdsGram: {self.ag_count}/{MAX_ADSGRAM} | MonetaG: {self.mt_count}/{MAX_MONETAG} | Gigapub: {self.gp_count}/{MAX_GIGAPUB}{RESET}")
        print(f"{YELLOW}⏱️ Durasi iklan random {MIN_AD_DURATION}-{MAX_AD_DURATION} detik (anti-detection){RESET}")
        print(f"{YELLOW}🛑 Bot akan berhenti jika semua iklan habis (atau 429 semua){RESET}")
        print(f"{YELLOW}Press Ctrl+C to stop{RESET}\n")

        cycle = 0
        while True:
            cycle += 1
            print(f"\n{CYAN}🔄 Cycle #{cycle}{RESET}")

            if not self.get_user():
                print(f"{YELLOW}⚠️ Gagal get user, coba login ulang...{RESET}")
                if not self.auth():
                    print(f"{RED}❌ Auth ulang gagal, stop.{RESET}")
                    break
                continue

            if self.is_all_done():
                print(f"\n{GREEN}✅ Semua iklan sudah ditonton / limit hari ini!{RESET}")
                print(f"📊 Total iklan hari ini: {self.total_watched_today}/{TOTAL_LIMIT}")
                print(f"📊 AdsGram: {self.ag_count} | MonetaG: {self.mt_count} | Gigapub: {self.gp_count}")
                break

            # AdsGram
            print(f"\n{YELLOW}📺 AdsGram ({self.ag_count}/{MAX_ADSGRAM})...{RESET}")
            if self.ag_done:
                print(f"{YELLOW}⏹️ AdsGram sudah limit/skip, lewati...{RESET}")
            else:
                self.watch_adsgram()
                self.human_pause(MIN_PAUSE_BETWEEN_ADS, MAX_PAUSE_BETWEEN_ADS, "⏳ Jeda antar iklan")

            # MonetaG
            print(f"\n{YELLOW}📺 MonetaG ({self.mt_count}/{MAX_MONETAG})...{RESET}")
            if self.mt_done:
                print(f"{YELLOW}⏹️ MonetaG sudah limit/skip, lewati...{RESET}")
            else:
                self.watch_monetag()
                self.human_pause(MIN_PAUSE_BETWEEN_ADS, MAX_PAUSE_BETWEEN_ADS, "⏳ Jeda antar iklan")

            # Gigapub
            print(f"\n{YELLOW}📺 Gigapub ({self.gp_count}/{MAX_GIGAPUB})...{RESET}")
            if self.gp_done:
                print(f"{YELLOW}⏹️ Gigapub sudah limit/skip, lewati...{RESET}")
            else:
                self.watch_gigapub()
                self.human_pause(MIN_PAUSE_BETWEEN_ADS, MAX_PAUSE_BETWEEN_ADS, "⏳ Jeda antar iklan")

            print(f"{DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            # Jeda antar cycle (random)
            self.human_pause(MIN_PAUSE_BETWEEN_CYCLES, MAX_PAUSE_BETWEEN_CYCLES, "⏳ Jeda antar cycle")

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
        print(f"{RED}❌ Auth gagal. Coba update InitData di menu 2.{RESET}")
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
