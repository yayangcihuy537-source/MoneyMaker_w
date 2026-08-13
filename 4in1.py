#!/usr/bin/env python3
"""
MULTI-APP AUTO WATCH ADS — 4 Mode + Coming Soon
Gamerlee • MiniappFaucetsbot • VipcoinFaucet • MiniappCrypto
"""

import os
import sys
import time
import json
import re
import random
import string
import asyncio
from urllib.parse import parse_qs, urlparse

import requests
from colorama import init, Fore, Style

from telethon import TelegramClient
from telethon.tl.functions.messages import RequestWebViewRequest
from telethon.errors import SessionPasswordNeededError

init(autoreset=True)

# ========== COLORS ==========
GREEN = Fore.LIGHTGREEN_EX
YELLOW = Fore.LIGHTYELLOW_EX
RED = Fore.LIGHTRED_EX
CYAN = Fore.LIGHTCYAN_EX
BLUE = Fore.LIGHTBLUE_EX
MAGENTA = Fore.LIGHTMAGENTA_EX
WHITE = Fore.WHITE
RESET = Style.RESET_ALL
DIM = Fore.LIGHTBLACK_EX

# ========== CONFIG ==========
CONFIG_FILE = "multiapp_config.json"
USER_AGENT = "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.1 (Samsung SM-A556E; Android 16; SDK 36; HIGH)"
WATCH_DURATION = 30
CLAIM_COOLDOWN = 12
MAX_ADS = 25

MODES = {
    "Gamerlee": {
        "base_url": "https://gamerlee.com",
        "bot_username": "gamerleebot",
        "login_endpoint": "/app/auth/telegram_login",
        "confirm_endpoint": "/app/links/confirm_ad",
        "watch_base": "/links/currency/",
        "home": "/"
    },
    "MiniappFaucetsbot": {
        "base_url": "https://mrappswala.com",
        "bot_username": "MiniappFaucetsbot",
        "login_endpoint": "/app/auth/telegram_login",
        "confirm_endpoint": "/app/links/confirm_ad",
        "watch_base": "/links/currency/",
        "home": "/"
    },
    "VipcoinFaucet": {
        "base_url": "https://vipcoinfaucet.com",
        "bot_username": "VipcoinFaucet_bot",
        "login_endpoint": "/app/auth/telegram_login",
        "confirm_endpoint": "/app/links/confirm_ad",
        "watch_base": "/links/currency/",
        "home": "/"
    },
    "MiniappCrypto": {
        "base_url": "https://linksfly.link",
        "bot_username": "Miniappcrypto_bot",
        "login_endpoint": "/app/auth/telegram_login",
        "confirm_endpoint": "/app/links/confirm_ad",
        "watch_base": "/links/currency/",
        "home": "/"
    }
}

# ========== BANNER ==========
def banner():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════════╗
║   {YELLOW}MULTI-APP AUTO WATCH ADS (Telethon)                {CYAN}║
║   {GREEN}⚡ 4 Mode • Coming Soon • 12s cooldown             {CYAN}║
║   {YELLOW}⏭️  Session persistent • Auto re-login            {CYAN}║
║   {CYAN}👑 Owner: ScriptyXSouu                             ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

# ========== CONFIG HANDLER ==========
class Config:
    def __init__(self):
        self.api_id = 0
        self.api_hash = ""
        self.coin = "LTC"
        self.mode = "Gamerlee"
        self.session_name = "gamerlee_session"

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.api_id = data.get('api_id', 0)
                    self.api_hash = data.get('api_hash', '')
                    self.coin = data.get('coin', 'LTC')
                    self.mode = data.get('mode', 'Gamerlee')
                    self.session_name = data.get('session_name', 'gamerlee_session')
                    return True
            except:
                pass
        return False

    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'api_id': self.api_id,
                'api_hash': self.api_hash,
                'coin': self.coin,
                'mode': self.mode,
                'session_name': self.session_name
            }, f, indent=4)

# ========== HELPER FUNGSI ==========
def extract_csrf_from_html(html):
    match = re.search(r'<input[^>]*name="csrf_test_name"[^>]*value="([^"]+)"', html)
    return match.group(1) if match else None

def extract_reg_nonce(html):
    match = re.search(r'<input[^>]*name="reg_nonce"[^>]*value="([^"]+)"', html)
    return match.group(1) if match else None

def extract_uid_from_html(html):
    match = re.search(r'<input[^>]*name="uid"[^>]*value="([^"]+)"', html)
    return match.group(1) if match else None

def extract_ad_token(html):
    match = re.search(r'<input[^>]*name="ad_token"[^>]*value="([^"]+)"', html)
    return match.group(1) if match else None

def extract_claim_url(html):
    match = re.search(r'data-claim-url="([^"]+)"', html)
    return match.group(1) if match else None

def generate_uid():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=32))

def progress_bar(seconds):
    for i in range(seconds, 0, -1):
        bar_len = 20
        filled = int((seconds - i) / seconds * bar_len)
        bar = '█' * filled + '░' * (bar_len - filled)
        sys.stdout.write(f"\r{GREEN}⏳ [{bar}] {i}s left{RESET}")
        sys.stdout.flush()
        time.sleep(1)
    print()

def extract_init_data_from_url(url):
    parsed = urlparse(url)
    if parsed.fragment:
        fragment_params = parse_qs(parsed.fragment)
        init_data = fragment_params.get('tgWebAppData', [None])[0]
        if init_data:
            return init_data
    if parsed.query:
        query_params = parse_qs(parsed.query)
        init_data = query_params.get('tgWebAppData', [None])[0]
        if init_data:
            return init_data
    return None

def normalize_url(url, base):
    if not url:
        return None
    url = url.strip()
    if url.startswith('http://') or url.startswith('https://'):
        return url
    if url.startswith('//'):
        return 'https:' + url
    if url.startswith('/'):
        return base + url
    return base + '/' + url

def clear_csrf_cookies(session):
    to_remove = []
    for cookie in session.cookies:
        if cookie.name == 'csrf_cookie_name':
            to_remove.append(cookie)
    for cookie in to_remove:
        session.cookies.clear(domain=cookie.domain, path=cookie.path, name=cookie.name)

def set_csrf_cookie(session, value):
    clear_csrf_cookies(session)
    session.cookies.set('csrf_cookie_name', value, path='/')
    return value

def get_csrf_from_session(session):
    return session.cookies.get('csrf_cookie_name')

# ========== BOT CLASS ==========
class MultiAppBot:
    def __init__(self, config):
        self.config = config
        self.mode = config.mode
        self.mode_info = MODES.get(self.mode)
        if not self.mode_info:
            raise ValueError(f"Mode {self.mode} not supported")
        self.base_url = self.mode_info["base_url"]
        self.bot_username = self.mode_info["bot_username"]
        self.login_endpoint = self.mode_info["login_endpoint"]
        self.confirm_endpoint = self.mode_info["confirm_endpoint"]
        self.watch_base = self.mode_info["watch_base"]
        self.home = self.mode_info["home"]

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Dest": "document",
            "Connection": "keep-alive",
        })
        self.csrf_token = None
        self.init_data = None
        self.ad_token = None
        self.claim_url = None
        self.available_ads = 0
        self.total_earned = 0.0
        self.watch_count = 0

    def log(self, msg, color=WHITE):
        print(f"{color}{msg}{RESET}")

    # ─── LOGIN VIA TELEGRAM ──────────────────────────
    async def get_init_data_from_telegram(self):
        session_file = self.config.session_name + ".session"
        client = TelegramClient(session_file, self.config.api_id, self.config.api_hash)

        if os.path.exists(session_file):
            self.log(f"{DIM}📁 Session file ditemukan: {session_file}")
            try:
                await client.start()
                if await client.is_user_authorized():
                    self.log(f"{GREEN}✅ Session valid!{RESET}")
                else:
                    self.log(f"{YELLOW}⚠️ Session tidak valid, login ulang...{RESET}")
                    phone = input(f"{GREEN}Masukkan nomor telepon (dengan kode negara, ex: +62812): {RESET}")
                    await client.start(phone=phone)
            except SessionPasswordNeededError:
                pwd = input(f"{YELLOW}Masukkan password 2FA Anda: {RESET}")
                await client.start(password=pwd)
            except Exception as e:
                self.log(f"{RED}❌ Error saat start session: {e}{RESET}")
                phone = input(f"{GREEN}Masukkan nomor telepon (dengan kode negara, ex: +62812): {RESET}")
                await client.start(phone=phone)
        else:
            self.log(f"{YELLOW}⚠️ Session file tidak ditemukan, login baru...{RESET}")
            phone = input(f"{GREEN}Masukkan nomor telepon (dengan kode negara, ex: +62812): {RESET}")
            try:
                await client.start(phone=phone)
            except SessionPasswordNeededError:
                pwd = input(f"{YELLOW}Masukkan password 2FA Anda: {RESET}")
                await client.start(password=pwd)

        self.log(f"{CYAN}🔐 Login Telegram berhasil! Mengambil init_data dari bot @{self.bot_username}...")

        try:
            result = await client(RequestWebViewRequest(
                peer=self.bot_username,
                bot=self.bot_username,
                platform='android',
                url=self.base_url
            ))
            web_url = result.url
            self.log(f"{DIM}📎 URL: {web_url[:100]}...")

            init_data = extract_init_data_from_url(web_url)
            if init_data:
                self.log(f"{GREEN}✅ init_data berhasil diambil! Panjang: {len(init_data)}")
                self.init_data = init_data
                await client.disconnect()
                return init_data
            else:
                self.log(f"{RED}❌ Tidak ada tgWebAppData di URL: {web_url}")
                await client.disconnect()
                return None
        except Exception as e:
            self.log(f"{RED}❌ Gagal request WebView: {e}")
            await client.disconnect()
            return None

    # ─── LOGIN KE WEBSITE ──────────────────────────
    def login_site(self, init_data):
        self.log(f"{CYAN}🔐 Logging in to {self.base_url}...")

        clear_csrf_cookies(self.session)

        resp = self.session.get(self.base_url + self.home)
        if resp.status_code != 200:
            self.log(f"❌ Failed to get home page: {resp.status_code}", RED)
            return False

        html = resp.text
        csrf = extract_csrf_from_html(html)
        reg_nonce = extract_reg_nonce(html)
        if not csrf or not reg_nonce:
            self.log("❌ Could not extract CSRF or reg_nonce", RED)
            return False

        uid = extract_uid_from_html(html) or generate_uid()

        login_url = self.base_url + self.login_endpoint
        payload = {
            "csrf_test_name": csrf,
            "tg_init_data": init_data,
            "reg_nonce": reg_nonce,
            "uid": uid,
            "website_url": ""
        }
        self.session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.base_url,
            "Referer": self.base_url + self.home,
        })
        resp = self.session.post(login_url, data=payload)
        if resp.status_code in [302, 303, 200]:
            if 'ci_session' in self.session.cookies:
                csrf_cookie = get_csrf_from_session(self.session)
                if csrf_cookie:
                    self.csrf_token = set_csrf_cookie(self.session, csrf_cookie)
                self.log(f"{GREEN}✅ Login {self.mode} successful!")
                return True
            else:
                self.log(f"❌ Login failed: no session cookie. Response: {resp.text[:200]}", RED)
                return False
        else:
            self.log(f"❌ Login HTTP error: {resp.status_code} - {resp.text[:200]}", RED)
            return False

    # ─── FETCH ADS PAGE ──────────────────────────────
    def fetch_ads_page(self):
        clear_csrf_cookies(self.session)

        url = self.base_url + self.watch_base + self.config.coin.lower()
        resp = self.session.get(url)
        if resp.status_code != 200:
            self.log(f"❌ Failed to get ads page: {resp.status_code}", RED)
            return None

        html = resp.text
        csrf = get_csrf_from_session(self.session)
        if not csrf:
            csrf = extract_csrf_from_html(html)
        if csrf:
            self.csrf_token = set_csrf_cookie(self.session, csrf)
        else:
            self.log("❌ No CSRF token found", RED)
            return None

        self.ad_token = extract_ad_token(html)
        if not self.ad_token:
            self.log("❌ No ad_token found", RED)
            return None

        raw_url = extract_claim_url(html)
        if not raw_url:
            self.log("❌ No claim URL found", RED)
            return None
        self.claim_url = normalize_url(raw_url, self.base_url)
        self.log(f"{DIM}🔗 Claim URL: {self.claim_url}")

        match = re.search(r'<h3 class="mb-1">(\d+)</h3>\s*<p class="text-muted mb-0">Available Ads</p>', html, re.DOTALL)
        if match:
            self.available_ads = int(match.group(1))
        else:
            match2 = re.search(r'Claim <span[^>]*>(\d+)/(\d+)</span>', html)
            if match2:
                used = int(match2.group(1))
                limit = int(match2.group(2))
                self.available_ads = limit - used
            else:
                self.available_ads = 25

        self.log(f"{DIM}📊 Available ads: {self.available_ads}, coin: {self.config.coin}")
        return html

    # ─── CONFIRM AD ────────────────────────────────────
    def confirm_ad(self):
        csrf = get_csrf_from_session(self.session)
        if csrf:
            self.csrf_token = set_csrf_cookie(self.session, csrf)

        url = self.base_url + self.confirm_endpoint
        payload = {
            "csrf_test_name": self.csrf_token,
            "ad_token": self.ad_token
        }
        resp = self.session.post(url, data=payload)
        if resp.status_code == 200:
            try:
                data = resp.json()
                if data.get('status') == 'ok':
                    new_csrf = data.get('csrf_hash')
                    if new_csrf:
                        self.csrf_token = set_csrf_cookie(self.session, new_csrf)
                    self.log(f"{GREEN}✅ Ad confirmed!")
                    return True
                else:
                    self.log(f"❌ Confirm failed: {data}", RED)
                    return False
            except:
                self.log(f"❌ Confirm response not JSON: {resp.text[:200]}", RED)
                return False
        else:
            self.log(f"❌ Confirm HTTP error: {resp.status_code}", RED)
            return False

    # ─── CLAIM REWARD ──────────────────────────────────
    def claim_reward(self):
        if not self.claim_url:
            self.log("❌ No claim_url", RED)
            return False

        csrf = get_csrf_from_session(self.session)
        if csrf:
            self.csrf_token = set_csrf_cookie(self.session, csrf)

        url = self.claim_url
        payload = {
            "csrf_test_name": self.csrf_token,
            "ad_token": self.ad_token
        }
        self.log(f"{DIM}📤 Claim POST to: {url}")
        resp = self.session.post(url, data=payload)
        if resp.status_code in [200, 302, 303]:
            html = resp.text
            if 'Great!' in html or 'has been send' in html:
                match = re.search(r'([0-9.]+)\s+' + self.config.coin, html)
                if match:
                    earned = float(match.group(1))
                    self.total_earned += earned
                    self.log(f"{GREEN}✅ Claimed! +{earned} {self.config.coin} (total: {self.total_earned:.8f})")
                else:
                    self.log(f"{GREEN}✅ Claimed successfully!")
                self.watch_count += 1
                return True
            else:
                self.log(f"{GREEN}✅ Claimed (redirect) {resp.status_code}")
                self.watch_count += 1
                return True
        else:
            self.log(f"❌ Claim HTTP error: {resp.status_code} - {resp.text[:200]}", RED)
            return False

    # ─── DO ONE CYCLE ──────────────────────────────────
    def do_cycle(self):
        if not self.fetch_ads_page():
            return False

        if self.available_ads <= 0:
            self.log(f"{YELLOW}⏹️ No ads left. Stopping.")
            return False

        self.log(f"{CYAN}🎬 Cycle #{self.watch_count+1} — {self.available_ads} ads remaining")

        self.log(f"{YELLOW}⏳ Watching ad {WATCH_DURATION}s...")
        progress_bar(WATCH_DURATION)

        if not self.confirm_ad():
            self.log(f"{RED}❌ Confirm failed, stopping.")
            return False

        if not self.claim_reward():
            self.log(f"{RED}❌ Claim failed, stopping.")
            return False

        self.log(f"{DIM}⏳ Cooldown {CLAIM_COOLDOWN}s...")
        for i in range(CLAIM_COOLDOWN, 0, -1):
            sys.stdout.write(f"\r   {DIM}⏳ {i}s{RESET}")
            sys.stdout.flush()
            time.sleep(1)
        print()

        return True

    # ─── MAIN FARMING ─────────────────────────────────
    async def run(self):
        init_data = await self.get_init_data_from_telegram()
        if not init_data:
            self.log(f"{RED}❌ Gagal mendapatkan init_data dari Telegram. Cek api_id/api_hash.")
            return

        if not self.login_site(init_data):
            self.log(f"{RED}❌ Login ke {self.mode} gagal.")
            return

        cycle = 0
        while True:
            if cycle >= MAX_ADS:
                self.log(f"{YELLOW}⏹️ Mencapai batas {MAX_ADS} iklan, berhenti.")
                break

            success = self.do_cycle()
            if not success:
                break
            cycle += 1

        self.log(f"\n{GREEN}📊 FINAL SUMMARY{RESET}")
        self.log(f"  🎯 Total iklan: {self.watch_count}")
        self.log(f"  💰 Total {self.config.coin}: {self.total_earned:.8f}")
        self.log(f"{YELLOW}🛑 Bot berhenti.")


# ========== MENU FUNCTIONS ==========
def menu_set_telethon(config):
    print(f"{CYAN}╔═══════════════════════════════════════════════╗")
    print(f"║              SET TELE THON                       ║")
    print(f"╚═══════════════════════════════════════════════╝{RESET}")
    try:
        api_id = int(input(f"{GREEN}Masukkan API ID: {RESET}").strip())
    except:
        print(f"{RED}❌ API ID harus angka!{RESET}")
        return
    api_hash = input(f"{GREEN}Masukkan API HASH: {RESET}").strip()
    if not api_hash:
        print(f"{RED}❌ API HASH tidak boleh kosong!{RESET}")
        return
    config.api_id = api_id
    config.api_hash = api_hash
    config.save()
    print(f"{GREEN}✅ Telethon credentials disimpan!{RESET}")

def menu_select_coin(config):
    coins = ['LTC', 'DOGE', 'ETH', 'TON', 'ZEC', 'TRX', 'USDT', 'BNB', 'SOL', 'PEPE', 'DASH', 'BCH']
    print(f"{CYAN}╔═══════════════════════════════════════════════╗")
    print(f"║              SELECT COIN                         ║")
    print(f"╚═══════════════════════════════════════════════╝{RESET}")
    for i, c in enumerate(coins, 1):
        print(f"  {GREEN}[{i}]{RESET} {c}")
    try:
        choice = int(input(f"{YELLOW}Pilih nomor: {RESET}").strip())
        if 1 <= choice <= len(coins):
            config.coin = coins[choice-1]
            config.save()
            print(f"{GREEN}✅ Coin diubah ke {config.coin}{RESET}")
        else:
            print(f"{RED}❌ Pilihan tidak valid!{RESET}")
    except:
        print(f"{RED}❌ Masukkan angka!{RESET}")

def menu_select_mode(config):
    print(f"{CYAN}╔═══════════════════════════════════════════════╗")
    print(f"║              SELECT MODE (Miniapp)               ║")
    print(f"╚═══════════════════════════════════════════════╝{RESET}")
    print(f"  {GREEN}[1]{RESET} Gamerlee")
    print(f"  {YELLOW}[2]{RESET} MiniappFaucetsbot")
    print(f"  {BLUE}[3]{RESET} VipcoinFaucet")
    print(f"  {MAGENTA}[4]{RESET} MiniappCrypto")
    print(f"  {DIM}[5]{RESET} Coming Soon (placeholder)")
    try:
        choice = int(input(f"{YELLOW}Pilih: {RESET}").strip())
        if choice == 1:
            config.mode = "Gamerlee"
            config.save()
            print(f"{GREEN}✅ Mode: Gamerlee{RESET}")
        elif choice == 2:
            config.mode = "MiniappFaucetsbot"
            config.save()
            print(f"{GREEN}✅ Mode: MiniappFaucetsbot{RESET}")
        elif choice == 3:
            config.mode = "VipcoinFaucet"
            config.save()
            print(f"{GREEN}✅ Mode: VipcoinFaucet{RESET}")
        elif choice == 4:
            config.mode = "MiniappCrypto"
            config.save()
            print(f"{GREEN}✅ Mode: MiniappCrypto{RESET}")
        elif choice == 5:
            config.mode = "Coming Soon"
            config.save()
            print(f"{YELLOW}⏳ Mode Coming Soon (belum implementasi){RESET}")
        else:
            print(f"{RED}❌ Pilihan tidak valid!{RESET}")
    except:
        print(f"{RED}❌ Masukkan angka!{RESET}")

async def menu_start_farming(config):
    if config.api_id == 0 or not config.api_hash:
        print(f"{RED}❌ Telethon credentials belum diset! Silakan menu 2 dulu.{RESET}")
        input("Tekan Enter untuk kembali...")
        return

    if config.mode == "Coming Soon":
        print(f"{YELLOW}⏳ Mode Coming Soon belum tersedia. Silakan pilih mode lain.{RESET}")
        input("Tekan Enter untuk kembali...")
        return

    bot = MultiAppBot(config)
    try:
        await bot.run()
    except Exception as e:
        print(f"{RED}❌ Error: {e}{RESET}")
    input("Tekan Enter untuk kembali ke menu...")

# ========== MAIN ==========
def main():
    config = Config()
    config.load()

    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        banner()
        print(f"{CYAN}╔═══════════════════════════════════════════════╗")
        print(f"║                    MAIN MENU                     ║")
        print(f"╠═══════════════════════════════════════════════╣")
        print(f"║  {GREEN}[1]{RESET} 🚀 Start Farming                         ║")
        print(f"║  {YELLOW}[2]{RESET} 🔑 Set Telethon                        ║")
        print(f"║  {BLUE}[3]{RESET} 💰 Select Coin                         ║")
        print(f"║  {MAGENTA}[4]{RESET} 📱 Select Mode (Miniapp)              ║")
        print(f"║  {RED}[0]{RESET} ❌ Exit                                  ║")
        print(f"╚═══════════════════════════════════════════════╝{RESET}")

        if config.api_id:
            print(f"{DIM}🔑 API ID: {config.api_id}  |  Coin: {config.coin}  |  Mode: {config.mode}{RESET}")
        else:
            print(f"{RED}⚠️  Telethon belum diset!{RESET}")

        choice = input(f"\n{CYAN}❯ Pilih: {RESET}").strip()

        if choice == '0':
            print(f"{YELLOW}👋 Bye!{RESET}")
            sys.exit(0)
        elif choice == '1':
            asyncio.run(menu_start_farming(config))
        elif choice == '2':
            menu_set_telethon(config)
        elif choice == '3':
            menu_select_coin(config)
        elif choice == '4':
            menu_select_mode(config)
        else:
            print(f"{RED}❌ Pilihan tidak valid!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}👋 Bye!{RESET}")
        sys.exit(0)

