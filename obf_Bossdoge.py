#!/usr/bin/env python3
"""
🐕 BOSSDOGSEARN — AUTO DAILY + TASKS + ADS (FIXED LOOP)
👑 Owner: @MoneyMaker_w
🔧 Deteksi limit Adsgram & Monetag otomatis dari API
🛑 Berhenti jika semua iklan habis
"""

import requests
import json
import os
import sys
import time

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

CONFIG_FILE = "bossdog_config.json"
BASE_URL = "https://bossdogsearn.site"
TIMER_ADS = 17
MAX_MONETAG = 5  # default, nanti di-override dari API

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
            json.dump({'init_data': self.init_data, 'token': self.token}, f, indent=2)

    def clear(self):
        if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)

def show_banner():
    print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════╗
║   {GOLD}🐕 BOSSDOGSEARN — AUTO CLAIM BOT {PURPLE}                 ║
║   {LIME}📅 Daily • Social Tasks • Adsgram (auto) • Monetag (auto){PURPLE}║
║   {LIME}⏱️ Timer 17 detik • Stop if all ads done              {PURPLE}║
║   {PINK}👑 Owner: @MoneyMaker_w                           {PURPLE}║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

class BossDogsBot:
    def __init__(self, init_data, token=None):
        self.init_data = init_data
        self.token = token
        self.session = requests.Session()
        self.base_url = BASE_URL
        self.balance = 0
        self.tasks = {}  # menyimpan info task d1 & d2
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Origin": "https://bossdogsearn.site",
            "X-Requested-With": "org.telegram.messenger.web",
            "Connection": "keep-alive",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    def auth(self):
        print(f"{BLUE}┌─ 🔐 Auth...{RESET}")
        payload = {"initData": self.init_data, "fingerprint": "3fb8034", "startParam": "ref_C26EB750"}
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

    def get_me(self):
        print(f"{BLUE}┌─ 👤 Get Profile...{RESET}")
        resp = self.session.get(f"{self.base_url}/api/me", headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                self.balance = data.get('coins', 0)
                print(f"{GREEN}└─ ✅ Balance: {self.balance}{RESET}")
                return data
            except:
                print(f"{GREEN}└─ ✅ Profile loaded{RESET}")
                return {}
        else:
            print(f"{RED}└─ ❌ Gagal: {resp.status_code}{RESET}")
            return {}

    def get_tasks(self):
        """Ambil daftar task dari /api/tasks dan simpan limit d1 & d2"""
        print(f"{BLUE}┌─ 📡 Get Tasks...{RESET}")
        resp = self.session.get(f"{self.base_url}/api/tasks", headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                for task in data:
                    if task.get('key') == 'd1':
                        self.tasks['d1'] = {
                            'limit': task.get('limit', 10),
                            'watchedToday': task.get('watchedToday', 0),
                            'provider': task.get('provider', 'adsgram'),
                            'reward': task.get('reward', 25),
                            'label': 'Adsgram'
                        }
                    elif task.get('key') == 'd2':
                        self.tasks['d2'] = {
                            'limit': task.get('limit', 5),
                            'watchedToday': task.get('watchedToday', 0),
                            'provider': task.get('provider', 'monetag'),
                            'reward': task.get('reward', 10),
                            'label': 'Monetag'
                        }
                print(f"{GREEN}└─ ✅ Tasks loaded: Adsgram {self.tasks.get('d1', {}).get('limit', 0)}x, Monetag {self.tasks.get('d2', {}).get('limit', 0)}x{RESET}")
                return True
            except:
                pass
        print(f"{YELLOW}└─ ⚠️ Gagal ambil tasks, pakai default{RESET}")
        # fallback default
        self.tasks['d1'] = {'limit': 10, 'watchedToday': 0, 'provider': 'adsgram', 'label': 'Adsgram'}
        self.tasks['d2'] = {'limit': 5, 'watchedToday': 0, 'provider': 'monetag', 'label': 'Monetag'}
        return False

    def claim_daily(self):
        print(f"{BLUE}┌─ 📅 Claim Daily...{RESET}")
        try:
            resp = self.session.post(f"{self.base_url}/api/daily/start", json={"provider": "adsgram"}, headers=self.headers)
            if resp.status_code != 200:
                print(f"{YELLOW}└─ ⚠️ Daily start gagal, skip...{RESET}")
                return False
            token = resp.json().get('token')
            if not token:
                print(f"{YELLOW}└─ ⚠️ Token kosong, skip...{RESET}")
                return False
            resp = self.session.post(f"{self.base_url}/api/daily/claim", json={"token": token, "clicked": True}, headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                if 'coins' in data: self.balance = data['coins']
                print(f"{GREEN}└─ ✅ Daily claimed! Balance: {self.balance}{RESET}")
                return True
            else:
                print(f"{YELLOW}└─ ⚠️ Daily claim gagal, skip...{RESET}")
                return False
        except:
            print(f"{YELLOW}└─ ⚠️ Daily error, skip...{RESET}")
            return False

    def claim_task(self, task_endpoint):
        print(f"{BLUE}┌─ 📋 Claim task: {task_endpoint}{RESET}")
        try:
            resp = self.session.post(f"{self.base_url}/api/tasks/{task_endpoint}/claim", json={"clicked": True}, headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                if 'coins' in data: self.balance = data['coins']
                print(f"{GREEN}└─ ✅ Task claimed! Balance: {self.balance}{RESET}")
                return True
            else:
                print(f"{YELLOW}└─ ⚠️ Task gagal, skip...{RESET}")
                return False
        except:
            print(f"{YELLOW}└─ ⚠️ Task error, skip...{RESET}")
            return False

    def watch_ad(self, task_key, label):
        """Nonton iklan untuk task key (d1 = Adsgram, d2 = Monetag)"""
        print(f"{BLUE}┌─ 📺 Watch {label}...{RESET}")
        try:
            # START
            resp = self.session.post(f"{self.base_url}/api/tasks/{task_key}/start", json={"provider": self.tasks.get(task_key, {}).get('provider', 'adsgram')}, headers=self.headers)
            if resp.status_code != 200:
                print(f"{YELLOW}└─ ⚠️ Start {label} gagal, skip...{RESET}")
                return False
            token = resp.json().get('token')
            if not token:
                print(f"{YELLOW}└─ ⚠️ Token kosong, skip...{RESET}")
                return False

            # Tunggu 17 detik
            for i in range(TIMER_ADS, 0, -1):
                sys.stdout.write(f"\r{YELLOW}⏳ {label} {i} detik{RESET}")
                sys.stdout.flush()
                time.sleep(1)
            print()

            # CLAIM
            resp = self.session.post(f"{self.base_url}/api/tasks/{task_key}/claim", json={"token": token, "clicked": True}, headers=self.headers)
            if resp.status_code == 200:
                data = resp.json()
                if 'coins' in data: self.balance = data['coins']
                print(f"{GREEN}└─ ✅ {label} watched! Balance: {self.balance}{RESET}")
                return True
            else:
                print(f"{RED}└─ ❌ Claim {label} gagal, skip...{RESET}")
                return False
        except:
            print(f"{RED}└─ ❌ {label} error, skip...{RESET}")
            return False

    def farming_loop(self):
        print(f"{CYAN}🚀 Starting bot...{RESET}\n")

        # Ambil task limit
        self.get_tasks()

        # Daily
        print(f"{GOLD}📅 Claiming Daily...{RESET}")
        self.claim_daily()
        self.countdown(2, "⏳ Jeda")

        # Social Tasks
        print(f"{GOLD}📋 Claiming Social Tasks...{RESET}")
        self.claim_task("join_telegram_group")
        self.claim_task("join_announcement_channel")
        self.countdown(2, "⏳ Jeda")

        # Adsgram (loop sampai limit)
        d1 = self.tasks.get('d1', {})
        d1_limit = d1.get('limit', 10)
        d1_watched = d1.get('watchedToday', 0)
        d1_provider = d1.get('provider', 'adsgram')
        print(f"{GOLD}📺 Watching Adsgram ({d1_watched}/{d1_limit})...{RESET}")

        for i in range(d1_watched, d1_limit):
            ok = self.watch_ad('d1', 'Adsgram')
            if not ok:
                print(f"{YELLOW}⏭️ Adsgram gagal, lanjut ke Monetag...{RESET}")
                break
            self.countdown(2, "⏳ Jeda")

        # Monetag (loop sampai limit)
        d2 = self.tasks.get('d2', {})
        d2_limit = d2.get('limit', 5)
        d2_watched = d2.get('watchedToday', 0)
        d2_provider = d2.get('provider', 'monetag')
        print(f"{GOLD}📺 Watching Monetag ({d2_watched}/{d2_limit})...{RESET}")

        for i in range(d2_watched, d2_limit):
            ok = self.watch_ad('d2', 'Monetag')
            if not ok:
                print(f"{YELLOW}⏭️ Monetag gagal, lanjut ke tahap akhir...{RESET}")
                break
            self.countdown(2, "⏳ Jeda")

        print(f"\n{GREEN}✅ Selesai! Semua iklan selesai.{RESET}")
        self.get_me()

    def countdown(self, seconds, msg="⏳ Menunggu"):
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r{YELLOW}{msg} {i} detik{RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print()

def show_menu():
    print(f"\n{CYAN}╔════════════════════════════════════════════════════╗")
    print(f"║              🐕 BOSSDOGSEARN BOT                    ║")
    print(f"╠════════════════════════════════════════════════════╣")
    print(f"║  {GREEN}[1]{RESET} 🚀 Start Farming                         ║")
    print(f"║  {YELLOW}[2]{RESET} 📝 Set InitData                         ║")
    print(f"║  {YELLOW}[3]{RESET} ⚙️  Reset Config                         ║")
    print(f"║  {BLUE}[4]{RESET} 💰 Check Balance                         ║")
    print(f"║  {RED}[0]{RESET} ❌ Exit                                  ║")
    print(f"╚════════════════════════════════════════════════════╝{RESET}")

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

        if config.token:
            print(f"{GREEN}✅ Token tersimpan{RESET}")
        else:
            print(f"{RED}❌ Token belum diset (login otomatis){RESET}")

        choice = input(f"\n{PURPLE}❯ Pilih: {RESET}").strip()

        if choice == '0':
            print(f"{YELLOW}👋 Bye!{RESET}")
            sys.exit(0)

        elif choice == '1':
            if not config.init_data:
                print(f"{RED}❌ InitData belum diset!{RESET}")
                input("Tekan Enter...")
                continue

            bot = BossDogsBot(config.init_data, config.token)
            if not bot.auth():
                print(f"{RED}❌ Auth gagal. Cek InitData.{RESET}")
                input("Tekan Enter...")
                continue

            if bot.token:
                config.token = bot.token
                config.save()

            bot.get_me()
            bot.farming_loop()
            input("Tekan Enter untuk kembali ke menu...")

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
            confirm = input("Yakin reset? (y/n): ").strip().lower()
            if confirm == 'y':
                config.clear()
                print(f"{GREEN}✅ Config direset!{RESET}")
            input("Tekan Enter untuk kembali...")

        elif choice == '4':
            if not config.init_data:
                print(f"{RED}❌ InitData belum diset!{RESET}")
                input("Tekan Enter...")
                continue
            bot = BossDogsBot(config.init_data, config.token)
            if bot.auth():
                bot.get_me()
            input("Tekan Enter untuk kembali...")

        else:
            print(f"{RED}❌ Pilihan salah!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()
