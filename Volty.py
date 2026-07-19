#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  ⚡ VOLTLY EARN BOT — ADS ONLY                         ║
║  🔐 Login via InitData                                 ║
║  📺 Adsgram (6x) • Monetag (6x)                      ║
║  🛑 Stop otomatis jika semua iklan habis             ║
║  👑 Owner: @MoneyMaker_w                              ║
╚══════════════════════════════════════════════════════════╝
"""

import requests
import json
import os
import sys
import time
from urllib.parse import parse_qs, unquote

# ==================== WARNA ====================
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

# ==================== KONFIGURASI ====================
CONFIG_FILE = "voltly_config.json"
BASE_URL = "https://voltly.site"
TIMER_ADS = 5
MAX_ADSGRAM = 6
MAX_MONETAG = 6   # <--- DIUBAH DARI 8 JADI 6

class Config:
    def __init__(self):
        self.init_data = None
        self.token = None

    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.init_data = data.get('init_data')
                self.token = data.get('token')
                return True
        return False

    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'init_data': self.init_data,
                'token': self.token
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

# ==================== BANNER ====================
def show_banner():
    print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════╗
║   {GOLD}⚡ VOLTLY EARN BOT — ADS ONLY {PURPLE}                    ║
║   {LIME}📺 Adsgram (6x) • Monetag (6x)                     {PURPLE}║
║   {LIME}🛑 Stop otomatis jika semua iklan habis          {PURPLE}║
║   {PINK}👑 Owner: @MoneyMaker_w                           {PURPLE}║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

# ==================== BOT ====================
class VoltlyBot:
    def __init__(self, init_data, token=None):
        self.init_data = init_data
        self.token = token
        self.session = requests.Session()
        self.base_url = BASE_URL
        self.balance = 0
        self.ag_count = 0
        self.mt_count = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.7827.164 Mobile Safari/537.36 Telegram-Android/12.6.4",
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Origin": "https://voltly.site",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Connection": "keep-alive",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def auth(self):
        print(f"{BLUE}┌─ 🔐 Auth...{RESET}")
        payload = {"initData": self.init_data, "deviceId": "e6a300e3-2a15-409b-8bd5-90589bfc6a19"}
        resp = self.session.post(f"{self.base_url}/api/auth/verify", json=payload, headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                token = data.get('token')
                if token:
                    self.token = token
                    self.headers["Authorization"] = f"Bearer {token}"
                    print(f"{GREEN}└─ ✅ Auth berhasil!{RESET}")
                    return True
            except:
                print(f"{GREEN}└─ ✅ Auth berhasil!{RESET}")
                return True
        else:
            print(f"{RED}└─ ❌ Auth gagal: {resp.status_code}{RESET}")
            return False

    def get_balance(self):
        print(f"{BLUE}┌─ 💰 Check Balance...{RESET}")
        resp = self.session.get(f"{self.base_url}/api/me", headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                user = data.get('user', {})
                self.balance = user.get('balanceUsdt', 0)
                print(f"{GREEN}└─ ✅ Balance: {self.balance} V{RESET}")
                return data
            except:
                print(f"{GREEN}└─ ✅ Balance loaded{RESET}")
                return {}
        else:
            print(f"{RED}└─ ❌ Gagal: {resp.status_code}{RESET}")
            return {}

    def start_ad(self, provider):
        print(f"{BLUE}┌─ 🎬 Start {provider} Ad...{RESET}")
        payload = {"provider": provider}
        resp = self.session.post(f"{self.base_url}/api/ads/start", json=payload, headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                token = data.get('token')
                print(f"{GREEN}└─ ✅ {provider} started!{RESET}")
                return token
            except:
                print(f"{GREEN}└─ ✅ {provider} started!{RESET}")
                return None
        else:
            print(f"{RED}└─ ❌ {provider} gagal: {resp.status_code}{RESET}")
            return None

    def claim_ad(self, token, provider):
        print(f"{BLUE}┌─ 💰 Claim {provider} Ad...{RESET}")
        payload = {"token": token, "clicked": True}
        resp = self.session.post(f"{self.base_url}/api/ads/claim", json=payload, headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                reward = data.get('reward', 0)
                if reward:
                    self.balance += reward
                    print(f"{GREEN}└─ ✅ Claimed {provider} +{reward} V{RESET}")
                else:
                    print(f"{GREEN}└─ ✅ Claimed {provider}{RESET}")
                return True
            except:
                print(f"{GREEN}└─ ✅ Claimed {provider}{RESET}")
                return True
        elif resp.status_code == 400:
            print(f"{YELLOW}└─ ⚠️ Claim {provider} gagal: 400, skip...{RESET}")
            return False
        else:
            print(f"{RED}└─ ❌ Claim {provider} gagal: {resp.status_code}{RESET}")
            return False

    def watch_adsgram(self):
        if self.ag_count >= MAX_ADSGRAM:
            print(f"{YELLOW}⏹️ AdsGram sudah limit ({self.ag_count}/{MAX_ADSGRAM}). Lewati.{RESET}")
            return True
        token = self.start_ad("adsgram")
        if not token:
            return False
        print(f"{BLUE}┌─ 📺 Menonton iklan 5 detik...{RESET}")
        for i in range(5, 0, -1):
            sys.stdout.write(f"\r{YELLOW}⏳ Sisa waktu {i} detik{RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print()
        success = self.claim_ad(token, "adsgram")
        if success:
            self.ag_count += 1
        return success

    def watch_monetag(self):
        if self.mt_count >= MAX_MONETAG:
            print(f"{YELLOW}⏹️ Monetag sudah limit ({self.mt_count}/{MAX_MONETAG}). Lewati.{RESET}")
            return True
        token = self.start_ad("monetag")
        if not token:
            return False
        print(f"{BLUE}┌─ 📺 Menonton iklan 5 detik...{RESET}")
        for i in range(5, 0, -1):
            sys.stdout.write(f"\r{YELLOW}⏳ Sisa waktu {i} detik{RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print()
        success = self.claim_ad(token, "monetag")
        if success:
            self.mt_count += 1
        return success

    def is_all_done(self):
        return self.ag_count >= MAX_ADSGRAM and self.mt_count >= MAX_MONETAG

    def countdown(self, seconds, msg="⏳ Menunggu"):
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r{YELLOW}{msg} {i} detik{RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print()

    def farming_loop(self):
        print(f"{CYAN}🚀 Starting farming ads...{RESET}")
        print(f"{YELLOW}📺 AdsGram: {self.ag_count}/{MAX_ADSGRAM} | Monetag: {self.mt_count}/{MAX_MONETAG}{RESET}")
        print(f"{YELLOW}⏱️ Timer antar iklan: {TIMER_ADS} detik{RESET}")
        print(f"{YELLOW}🛑 Bot akan berhenti jika semua iklan habis{RESET}")
        print(f"{YELLOW}Press Ctrl+C to stop{RESET}\n")

        cycle = 0
        try:
            while True:
                cycle += 1
                print(f"\n{CYAN}🔄 Cycle #{cycle}{RESET}")

                if self.is_all_done():
                    print(f"\n{GREEN}✅ Semua iklan sudah ditonton hari ini!{RESET}")
                    print(f"📊 AdsGram: {self.ag_count}/{MAX_ADSGRAM} | Monetag: {self.mt_count}/{MAX_MONETAG}")
                    self.get_balance()
                    break

                print(f"\n{YELLOW}📺 AdsGram ({self.ag_count}/{MAX_ADSGRAM})...{RESET}")
                self.watch_adsgram()
                self.countdown(TIMER_ADS, "⏳ Jeda sebelum iklan")

                print(f"\n{YELLOW}📺 Monetag ({self.mt_count}/{MAX_MONETAG})...{RESET}")
                self.watch_monetag()
                self.countdown(TIMER_ADS, "⏳ Jeda sebelum iklan")

                self.get_balance()
                print(f"{DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
                print(f"{YELLOW}⏰ Cycle #{cycle} selesai. Tunggu {TIMER_ADS} detik...{RESET}")
                self.countdown(TIMER_ADS, "⏳ Next cycle dalam")
        except KeyboardInterrupt:
            print(f"\n{YELLOW}⏹️ Farming stopped.{RESET}")
            input("Tekan Enter untuk kembali ke menu...")

# ==================== MENU ====================
def show_menu():
    print(f"\n{CYAN}╔════════════════════════════════════════════════════╗")
    print(f"║                    MAIN MENU                         ║")
    print(f"╠════════════════════════════════════════════════════╣")
    print(f"║  {GREEN}[1]{RESET} 🚀 Start Farming (Ads Only)                ║")
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

    bot = VoltlyBot(config.init_data, config.token)

    if not bot.auth():
        print(f"{RED}❌ Auth gagal. Cek InitData.{RESET}")
        input("Tekan Enter untuk kembali...")
        return

    if bot.token:
        config.token = bot.token
        config.save()

    bot.get_balance()
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
                config.token = None
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
                print(f"{GREEN}✅ Config & initData direset!{RESET}")
            else:
                print(f"{YELLOW}⏹️ Dibatalkan.{RESET}")
            input("Tekan Enter untuk kembali...")

        elif choice == '4':
            if not config.init_data:
                print(f"{RED}❌ InitData belum diset!{RESET}")
                input("Tekan Enter...")
                continue
            bot = VoltlyBot(config.init_data, config.token)
            if bot.auth():
                bot.get_balance()
            input("Tekan Enter untuk kembali...")

        else:
            print(f"{RED}❌ Pilihan salah!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()
