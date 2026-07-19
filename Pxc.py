#!/usr/bin/env python3
import requests, json, os, sys, time
from urllib.parse import parse_qs, unquote

GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
BLUE = "\033[1;34m"
PURPLE = "\033[1;35m"
DIM = "\033[2;37m"
RESET = "\033[0m"

def show_banner():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════════╗
║   {YELLOW}ARCADEPXC — AUTO CLAIM + 3 ADS (SKIP 429)         {CYAN}║
║   {GREEN}⚡ Daily • Claim • Interstitial • Gigapub • Monetag {CYAN}║
║   {YELLOW}⏭️  429 = Skip lanjut iklan lain                 {CYAN}║
║   {CYAN}👑 Owner: @MoneyMaker_w                             ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

CONFIG_FILE = "arcadepxc_config.json"
BASE_URL = "https://app.arcadepxc.xyz"
INTERVAL_ACTION = 5
INTERVAL_AD = 15
INTERVAL_CYCLE = 15   # <--- DIUBAH DARI 60 JADI 15
DAILY_BLOCK_ID = "int-34589"
MAX_INTERSTITIAL = 8
MAX_GIGAPUB = 20
MAX_MONETAG = 15

class Config:
    def __init__(self):
        self.init_data = None
        self.user_id = None
        self.session_cookie = None
    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.init_data = data.get('init_data')
                self.user_id = data.get('user_id')
                self.session_cookie = data.get('session_cookie')
                return True
        return False
    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'init_data':self.init_data,'user_id':self.user_id,'session_cookie':self.session_cookie}, f, indent=2)
    def clear(self):
        if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)

def extract_user_id(init_data):
    parsed = parse_qs(init_data)
    user_str = parsed.get('user', [None])[0]
    if user_str:
        try:
            user_json = json.loads(unquote(user_str))
            return str(user_json.get('id'))
        except: pass
    return None

class ArcadePXC:
    def __init__(self, init_data, user_id):
        self.init_data = init_data
        self.user_id = user_id
        self.session = requests.Session()
        self.base_url = BASE_URL
        self.session_cookie = None
        self.balance = 0
        self.daily_claimed = False
        self.inter_count = 0
        self.giga_count = 0
        self.monetag_count = 0
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36",
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9",
            "Content-Type": "application/json",
            "Origin": "https://app.arcadepxc.xyz",
            "Referer": f"https://app.arcadepxc.xyz/tasks?user_id={user_id}",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Connection": "keep-alive",
        }
    def set_cookie(self, cookie):
        self.session_cookie = cookie
        self.session.cookies.set("session", cookie)
    def auth_session(self):
        print(f"{BLUE}┌─ 🔐 Auth Session...{RESET}")
        payload = {"initData": self.init_data}
        resp = self.session.post(f"{self.base_url}/api/auth/session", json=payload, headers=self.headers)
        if resp.status_code == 200:
            for cookie in self.session.cookies:
                if cookie.name == "session":
                    self.session_cookie = cookie.value
            print(f"{GREEN}└─ ✅ Auth berhasil!{RESET}")
            return True
        else:
            print(f"{RED}└─ ❌ Auth gagal: {resp.status_code}{RESET}")
            return False
    def sync_data(self):
        print(f"{BLUE}┌─ 📡 Sync Telegram Data...{RESET}")
        payload = {"user_id": self.user_id, "username": "MoneyMaker_w", "first_name": "MoneyMaker", "last_name": None, "init_data": self.init_data}
        resp = self.session.post(f"{self.base_url}/api/sync-telegram-data", json=payload, headers=self.headers)
        if resp.status_code == 200:
            print(f"{GREEN}└─ ✅ Sync berhasil!{RESET}")
            return True
        else:
            print(f"{RED}└─ ❌ Sync gagal: {resp.status_code}{RESET}")
            return False
    def claim_daily(self):
        if self.daily_claimed:
            print(f"{YELLOW}⏹️ Daily sudah diklaim hari ini.{RESET}")
            return True
        print(f"{BLUE}┌─ 📅 Claim Daily Challenge...{RESET}")
        resp = self.session.get(f"{self.base_url}/api/daily-challenge?user_id={self.user_id}&lang=en", headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data.get('success'):
                    reward = data.get('reward', 0)
                    self.balance += reward
                    self.daily_claimed = True
                    print(f"{GREEN}└─ ✅ Daily claimed! +{reward} PXC{RESET}")
                    return True
                else:
                    print(f"{YELLOW}└─ ⚠️ Daily sudah diklaim.{RESET}")
                    self.daily_claimed = True
                    return True
            except:
                print(f"{GREEN}└─ ✅ Daily claimed!{RESET}")
                self.daily_claimed = True
                return True
        else:
            print(f"{RED}└─ ❌ Daily gagal: {resp.status_code}{RESET}")
            return False
    def claim_pxc(self):
        print(f"{BLUE}┌─ 💰 Claim PXC...{RESET}")
        resp = self.session.post(f"{self.base_url}/api/claim?user_id={self.user_id}", headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data.get('success') or data.get('claimed'):
                    print(f"{GREEN}└─ ✅ Claim PXC berhasil!{RESET}")
                    return True
            except:
                print(f"{GREEN}└─ ✅ Claim PXC berhasil!{RESET}")
                return True
        else:
            print(f"{RED}└─ ❌ Claim PXC gagal: {resp.status_code}{RESET}")
            return False

    # ---- ADS ----
    def watch_interstitial(self):
        if self.inter_count >= MAX_INTERSTITIAL:
            print(f"{YELLOW}⏹️ Interstitial limit ({self.inter_count}/{MAX_INTERSTITIAL}){RESET}")
            return True
        print(f"{BLUE}┌─ 📺 Watch Interstitial Ad...{RESET}")
        payload = {"user_id": self.user_id, "block_id": DAILY_BLOCK_ID}
        resp = self.session.post(f"{self.base_url}/api/adsgram/interstitial-reward", json=payload, headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data.get('success'):
                    reward = data.get('reward', 0)
                    self.balance += reward
                    self.inter_count += 1
                    print(f"{GREEN}└─ ✅ Interstitial +{reward} PXC ({self.inter_count}/{MAX_INTERSTITIAL}){RESET}")
                    return True
                else:
                    err = data.get('message', '')
                    if 'limit' in err.lower() or 'already' in err.lower():
                        print(f"{YELLOW}└─ ⚠️ Interstitial limit: {err}{RESET}")
                        self.inter_count = MAX_INTERSTITIAL
                        return True
                    else:
                        print(f"{RED}└─ ❌ Interstitial gagal: {err}{RESET}")
                        return False
            except:
                print(f"{GREEN}└─ ✅ Interstitial berhasil!{RESET}")
                self.inter_count += 1
                return True
        elif resp.status_code == 429:
            print(f"{YELLOW}└─ ⏳ Interstitial 429 (rate limit) — SKIP{RESET}")
            return True
        else:
            print(f"{RED}└─ ❌ Interstitial gagal: {resp.status_code}{RESET}")
            return False

    def watch_gigapub(self):
        if self.giga_count >= MAX_GIGAPUB:
            print(f"{YELLOW}⏹️ Gigapub limit ({self.giga_count}/{MAX_GIGAPUB}){RESET}")
            return True
        print(f"{BLUE}┌─ 📺 Watch Gigapub Ad...{RESET}")
        payload = {"user_id": self.user_id}
        resp = self.session.post(f"{self.base_url}/api/gigapub/reward", json=payload, headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data.get('success'):
                    reward = data.get('reward', 0)
                    self.balance += reward
                    self.giga_count += 1
                    print(f"{GREEN}└─ ✅ Gigapub +{reward} PXC ({self.giga_count}/{MAX_GIGAPUB}){RESET}")
                    return True
                else:
                    err = data.get('message', '')
                    if 'limit' in err.lower() or 'already' in err.lower():
                        print(f"{YELLOW}└─ ⚠️ Gigapub limit: {err}{RESET}")
                        self.giga_count = MAX_GIGAPUB
                        return True
                    else:
                        print(f"{RED}└─ ❌ Gigapub gagal: {err}{RESET}")
                        return False
            except:
                print(f"{GREEN}└─ ✅ Gigapub berhasil!{RESET}")
                self.giga_count += 1
                return True
        elif resp.status_code == 429:
            print(f"{YELLOW}└─ ⏳ Gigapub 429 (rate limit) — SKIP{RESET}")
            return True
        else:
            print(f"{RED}└─ ❌ Gigapub gagal: {resp.status_code}{RESET}")
            return False

    def watch_monetag(self):
        if self.monetag_count >= MAX_MONETAG:
            print(f"{YELLOW}⏹️ Monetag limit ({self.monetag_count}/{MAX_MONETAG}){RESET}")
            return True
        print(f"{BLUE}┌─ 📺 Watch Monetag Ad...{RESET}")
        payload = {"user_id": self.user_id}
        resp = self.session.post(f"{self.base_url}/api/monetag/reward", json=payload, headers=self.headers)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data.get('success'):
                    reward = data.get('reward', 0)
                    self.balance += reward
                    self.monetag_count += 1
                    print(f"{GREEN}└─ ✅ Monetag +{reward} PXC ({self.monetag_count}/{MAX_MONETAG}){RESET}")
                    return True
                else:
                    err = data.get('message', '')
                    if 'limit' in err.lower() or 'already' in err.lower():
                        print(f"{YELLOW}└─ ⚠️ Monetag limit: {err}{RESET}")
                        self.monetag_count = MAX_MONETAG
                        return True
                    else:
                        print(f"{RED}└─ ❌ Monetag gagal: {err}{RESET}")
                        return False
            except:
                print(f"{GREEN}└─ ✅ Monetag berhasil!{RESET}")
                self.monetag_count += 1
                return True
        elif resp.status_code == 429:
            print(f"{YELLOW}└─ ⏳ Monetag 429 (rate limit) — SKIP{RESET}")
            return True
        else:
            print(f"{RED}└─ ❌ Monetag gagal: {resp.status_code}{RESET}")
            return False

    def is_all_ads_limit_reached(self):
        return (self.inter_count >= MAX_INTERSTITIAL and
                self.giga_count >= MAX_GIGAPUB and
                self.monetag_count >= MAX_MONETAG)

    def countdown(self, seconds, msg="⏳ Menunggu"):
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r{YELLOW}{msg} {i} detik{RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print()

# ==================== FARMING ====================
def farming(bot):
    if not bot.claim_daily():
        print(f"{RED}❌ Daily gagal, stop.{RESET}")
        return
    bot.countdown(INTERVAL_ACTION, "⏳ Jeda setelah daily")
    cycle = 0
    while True:
        if bot.is_all_ads_limit_reached():
            print(f"\n{GREEN}✅ Semua iklan sudah habis hari ini.{RESET}")
            print(f"📊 Interstitial: {bot.inter_count}/{MAX_INTERSTITIAL}")
            print(f"📊 Gigapub: {bot.giga_count}/{MAX_GIGAPUB}")
            print(f"📊 Monetag: {bot.monetag_count}/{MAX_MONETAG}")
            print(f"{YELLOW}🛑 Bot berhenti. Kembali ke menu...{RESET}")
            time.sleep(2)
            return
        cycle += 1
        print(f"\n{CYAN}╔════════════════════════════════════════════════════╗")
        print(f"║                 🎮 CYCLE #{cycle}                        ║")
        print(f"╚════════════════════════════════════════════════════╝{RESET}")
        if not bot.claim_pxc():
            print(f"{RED}❌ Claim PXC gagal, stop.{RESET}")
            return
        bot.countdown(INTERVAL_ACTION, "⏳ Jeda sebelum iklan")
        if not bot.watch_interstitial():
            print(f"{RED}❌ Interstitial gagal (bukan 429/limit), stop.{RESET}")
            return
        bot.countdown(INTERVAL_AD, "⏳ Jeda iklan 15s")
        if not bot.watch_gigapub():
            print(f"{RED}❌ Gigapub gagal (bukan 429/limit), stop.{RESET}")
            return
        bot.countdown(INTERVAL_AD, "⏳ Jeda iklan 15s")
        if not bot.watch_monetag():
            print(f"{RED}❌ Monetag gagal (bukan 429/limit), stop.{RESET}")
            return
        bot.countdown(INTERVAL_AD, "⏳ Jeda iklan 15s")
        print(f"{DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        print(f"{YELLOW}⏰ Cycle #{cycle} selesai. Tunggu {INTERVAL_CYCLE} detik...{RESET}")
        bot.countdown(INTERVAL_CYCLE, "⏳ Next cycle dalam")

# ==================== MENU ====================
def main():
    config = Config()
    config.load()
    while True:
        show_banner()
        print(f"{CYAN}╔════════════════════════════════════════════════════╗")
        print(f"║                    MAIN MENU                         ║")
        print(f"╠════════════════════════════════════════════════════╣")
        print(f"║  {GREEN}[1]{RESET} 🚀 Start Farming                          ║")
        print(f"║  {YELLOW}[2]{RESET} 📝 Set InitData                         ║")
        print(f"║  {RED}[0]{RESET} ❌ Exit                                  ║")
        print(f"╚════════════════════════════════════════════════════╝{RESET}")
        if config.init_data:
            print(f"{GREEN}✅ InitData tersimpan (user_id: {config.user_id}){RESET}")
        else:
            print(f"{RED}❌ InitData belum diset!{RESET}")
        choice = input(f"\n{PURPLE}❯ Pilih: {RESET}").strip()
        if choice == '0':
            print(f"{YELLOW}👋 Bye!{RESET}")
            sys.exit(0)
        elif choice == '1':
            if not config.init_data:
                print(f"{RED}❌ InitData belum diset! Set dulu (menu 2).{RESET}")
                input("Tekan Enter untuk kembali...")
                continue
            bot = ArcadePXC(config.init_data, config.user_id)
            if config.session_cookie:
                bot.set_cookie(config.session_cookie)
            if not bot.auth_session():
                print(f"{RED}❌ Auth gagal.{RESET}")
                input("Tekan Enter...")
                continue
            if not bot.sync_data():
                print(f"{RED}❌ Sync gagal.{RESET}")
                input("Tekan Enter...")
                continue
            if bot.session_cookie:
                config.session_cookie = bot.session_cookie
                config.save()
            try:
                farming(bot)
            except KeyboardInterrupt:
                print(f"\n{YELLOW}⏹️ Farming dihentikan.{RESET}")
            input("Tekan Enter untuk kembali ke menu...")
        elif choice == '2':
            print(f"{YELLOW}📝 Masukkan InitData:{RESET}")
            qid = input("InitData: ").strip()
            if qid:
                config.init_data = qid
                user_id = extract_user_id(qid)
                if user_id:
                    config.user_id = user_id
                    print(f"{GREEN}✅ User ID: {user_id}{RESET}")
                else:
                    config.user_id = input("Masukkan User ID manual: ").strip()
                config.save()
                print(f"{GREEN}✅ InitData disimpan!{RESET}")
            else:
                print(f"{RED}❌ InitData kosong!{RESET}")
            input("Tekan Enter...")
        else:
            print(f"{RED}❌ Pilihan salah!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()
