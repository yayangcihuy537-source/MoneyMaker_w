#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════╗
║  ██╗  ██╗███████╗██╗     ██╗██╗  ██╗                    ║
║  ██║  ██║██╔════╝██║     ██║╚██╗██╔╝                    ║
║  ███████║█████╗  ██║     ██║ ╚███╔╝                     ║
║  ██╔══██║██╔══╝  ██║     ██║ ██╔██╗                     ║
║  ██║  ██║███████╗███████╗██║██╔╝╚██╗                    ║
║  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚═╝  ╚═╝                    ║
║                                                        ║
║                    🤖 HELIX BOT 🤖                    ║
║              AUTO FARM • AUTO CLAIM • ADS • GAME      ║
╚══════════════════════════════════════════════════════════╝
"""

import requests
import time
import random
import json
import os
import sys
import urllib.parse
from datetime import datetime

# ============================================================
# WARNA
# ============================================================
R, G, Y, B, M, C, W, X = '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[97m', '\033[0m'
GOLD = '\033[38;5;220m'
CYAN = '\033[1;96m'
PINK = '\033[38;5;206m'
DIM = '\033[2;37m'
P = PINK  # alias untuk pink
RS = X

# ============================================================
# BANNER
# ============================================================
BANNER = f"""
{CYAN}╔══════════════════════════════════════════════════════════╗
║  ██╗  ██╗███████╗██╗     ██╗██╗  ██╗                    ║
║  ██║  ██║██╔════╝██║     ██║╚██╗██╔╝                    ║
║  ███████║█████╗  ██║     ██║ ╚███╔╝                     ║
║  ██╔══██║██╔══╝  ██║     ██║ ██╔██╗                     ║
║  ██║  ██║███████╗███████╗██║██╔╝╚██╗                    ║
║  ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚═╝  ╚═╝                    ║
║                                                        ║
║                    {Y}🤖 HELIX BOT 🤖{X}{CYAN}                    ║
║  {G}Developer : ScriptyXSou  Tg : t.me/ScriptyXSouu{X}{CYAN}   ║
╚══════════════════════════════════════════════════════════╝{X}
"""

ADS_BANNER = f"""
{CYAN}╔══════════════════════════════════════════════╗
║              {Y}⚡ HELIX BOT CORE ⚡{X}{CYAN}            ║
║              {C}ADS EXECUTION MODE{X}{CYAN}             ║
╚══════════════════════════════════════════════╝{X}
"""

GAME_BANNER = f"""
{CYAN}╔══════════════════════════════════════════════╗
║              {Y}🎮 HELIX GAME MODE 🎮{X}{CYAN}          ║
║              {C}AUTO PLAY & CLAIM{X}{CYAN}              ║
╚══════════════════════════════════════════════╝{X}
"""

MENU = f"""
{CYAN}╔══════════════════════════════════════════════╗
║              {Y}☁️ HELIX VERSE ☁️{X}{CYAN}             ║
║          {CYAN}AUTO FARM • GAME • ADS{CYAN}           ║
╠══════════════════════════════════════════════╣
║  {G}[1] 🚀 Start Auto Watch Ads{X}{CYAN}              ║
║  {C}[2] 🎮 Auto Play Game{X}{CYAN}                    ║
║  {Y}[3] 🎡 Spin Wheel + Check-in{X}{CYAN}             ║
║  {B}[4] 💰 Check Balance{X}{CYAN}                     ║
║  {M}[5] 🔑 Set Init_Data{X}{CYAN}                     ║
║  {P}[6] 🔧 Toggle Anti Detection{X}{CYAN}             ║
║                                              ║
║  {R}[0] ❌ Exit{X}{CYAN}                                ║
╚══════════════════════════════════════════════╝{X}
"""

# ============================================================
# KONFIGURASI
# ============================================================
CONFIG_FILE = "helix_config.json"
BASE_URL = "https://app.helixverse.site"
ANTI_DETECTION = True

# ============================================================
# USER-AGENT LIST
# ============================================================
USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.6.4 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
    "Mozilla/5.0 (Linux; Android 15; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.7871.200 Mobile Safari/537.36 Telegram-Android/12.5.3",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.7871.190 Mobile Safari/537.36 Telegram-Android/12.4.5",
    "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.123 Mobile Safari/537.36 Telegram-Android/12.6.4 (Xiaomi 14; Android 16; SDK 36; HIGH)",
    "Mozilla/5.0 (Linux; Android 13; SM-A536E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.7871.160 Mobile Safari/537.36 Telegram-Android/12.3.1",
    "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 15; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.7871.200 Mobile Safari/537.36",
]

GAME_IDS = ["g1", "g2", "g3", "g4", "g5"]

# ============================================================
# FUNGSI UTILITY
# ============================================================
def random_delay(min_sec=0.5, max_sec=3.0):
    time.sleep(random.uniform(min_sec, max_sec))

def random_user_agent():
    return random.choice(USER_AGENTS)

def random_fingerprint():
    return f"fp_{''.join(random.choices('0123456789abcdef', k=8))}"

def random_gesture():
    return {
        "tr": True,
        "pt": random.choice(["touch", "click"]),
        "dur": random.randint(60, 250),
        "mv": random.randint(0, 10),
        "rx": round(random.uniform(0.3, 0.9), 3),
        "ry": round(random.uniform(0.3, 0.9), 3),
        "ts": int(time.time() * 1000) + random.randint(-2000, 2000)
    }

def random_ip():
    return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"

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

def progress_bar(current, total, bar_len=20, fill='█', empty='░'):
    if total == 0:
        return f"[{fill * bar_len}] 100%"
    pct = current / total
    filled_len = int(bar_len * pct)
    bar = fill * filled_len + empty * (bar_len - filled_len)
    return f"[{bar}] {int(pct*100)}%"

# ============================================================
# CLASS HelixBot
# ============================================================
class HelixBot:
    def __init__(self, init_data=None, device_fp=None, anti_detection=True, proxy=None):
        self.init_data = init_data
        self.device_fp = device_fp or random_fingerprint()
        self.anti_detection = anti_detection
        self.proxy = proxy
        self.session = requests.Session()
        if self.proxy:
            self.session.proxies = {"http": self.proxy, "https": self.proxy}
        self.headers = {}
        self.last_balance = None

    def _build_headers(self, extra=None):
        ua = random_user_agent() if self.anti_detection else USER_AGENTS[0]
        fp = random_fingerprint() if self.anti_detection else self.device_fp
        headers = {
            "Host": "app.helixverse.site",
            "sec-ch-ua-platform": '"Android"',
            "user-agent": ua,
            "x-device-fp": fp,
            "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
            "content-type": "application/json",
            "sec-ch-ua-mobile": "?1",
            "x-telegram-init-data": self.init_data,
            "accept": "*/*",
            "x-requested-with": "org.telegram.messenger.web",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://app.helixverse.site/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i",
        }
        if self.anti_detection:
            headers["X-Forwarded-For"] = random_ip()
            headers["X-Real-IP"] = random_ip()
        if extra:
            headers.update(extra)
        return headers

    def request(self, method, endpoint, data=None, json=None, headers_extra=None, retries=3):
        url = f"{BASE_URL}{endpoint}"
        headers = self._build_headers(headers_extra)
        for attempt in range(retries):
            try:
                if method.upper() == "GET":
                    resp = self.session.get(url, headers=headers, timeout=15)
                else:
                    resp = self.session.post(url, headers=headers, data=data, json=json, timeout=15)
                if resp.status_code == 200:
                    return resp
                if resp.status_code in [401, 403]:
                    print(f"{R}❌ Auth error (status {resp.status_code}). Skip.{X}")
                    return None
                if resp.status_code in [429, 500, 502, 503, 504]:
                    time.sleep(random.uniform(3, 7))
                    continue
                time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"{Y}⚠️ Request error: {e}, retry {attempt+1}/{retries}{X}")
                time.sleep(random.uniform(2, 5))
        return None

    def get_me(self):
        resp = self.request("GET", "/api/me")
        if resp:
            return resp.json()
        return None

    def get_ads(self):
        resp = self.request("GET", "/api/ads")
        if resp:
            return resp.json()
        return None

    def ads_shown(self, provider):
        payload = {"provider": provider, "gesture": random_gesture()}
        resp = self.request("POST", "/api/ads/shown", json=payload)
        if resp and resp.status_code == 200:
            try:
                data = resp.json()
                token = data.get('token') or data.get('ad_token') or data.get('data', {}).get('token')
                if token:
                    return True, token
                return True, None
            except:
                return True, None
        return False, None

    def ads_watched(self, provider, token):
        payload = {"provider": provider, "token": token}
        resp = self.request("POST", "/api/ads/watched", json=payload)
        if resp and resp.status_code == 200:
            return True
        return False

    # ============================================================
    # FITUR GAME
    # ============================================================
    def spin_wheel(self):
        """Spin roda keberuntungan"""
        resp = self.request("POST", "/api/wheel/spin")
        if resp:
            try:
                return resp.json()
            except:
                return {"status": "ok"}
        return None

    def checkin(self):
        """Daily check-in"""
        resp = self.request("POST", "/api/checkin/claim")
        if resp:
            try:
                return resp.json()
            except:
                return {"status": "ok"}
        return None

    def start_game(self, game_id):
        """Mulai game dengan game_id tertentu"""
        payload = {"game_id": game_id}
        resp = self.request("POST", "/api/games/start", json=payload)
        if resp and resp.status_code == 200:
            try:
                return resp.json()
            except:
                return {"status": "ok", "game_id": game_id}
        return None

    def play_game(self, max_games=5):
        """Mainkan game otomatis"""
        print(f"{C}🎮 Memulai Auto Game...{X}")
        if not self.init_data:
            print(f"{R}❌ Init_Data belum diset!{X}")
            return

        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        print(GAME_BANNER)
        print(f"\n{CYAN}[ HELIX ] Initializing Game Protocol...{X}")
        print(f"{G}[ ✓ ] Connection Established{X}\n")

        # Cek user
        user = self.get_me()
        if user:
            energy = user.get('energy', 0)
            print(f"{Y}⚡ Energy tersisa: {energy}{X}")
            if energy < 5:
                print(f"{Y}⚠️ Energy kurang dari 5, skip game.{X}")
                return

        played = 0
        for game_id in GAME_IDS[:max_games]:
            if played >= max_games:
                break
            print(f"\n{CYAN}>>> PLAYING GAME: {game_id}{X}")
            
            # Start game
            result = self.start_game(game_id)
            if result:
                print(f"{G}[ ✓ ] Game {game_id} started{X}")
                # Simulasi durasi game (5-10 detik)
                game_duration = random.randint(5, 10)
                for sec in range(game_duration):
                    time.sleep(1)
                    bar = progress_bar(sec+1, game_duration)
                    sys.stdout.write(f"\r{CYAN}{bar}{X} Playing... {sec+1}s/{game_duration}s")
                    sys.stdout.flush()
                print()
                print(f"{G}[ ✓ ] Game {game_id} completed!{X}")
                played += 1
                random_delay(1, 3)
            else:
                print(f"{R}❌ Gagal start game {game_id}{X}")
                if "401" in str(result) or "403" in str(result):
                    print(f"{Y}⚠️ Auth error, skip remaining games.{X}")
                    break

            # Refresh user untuk cek energy
            if played % 2 == 0:
                user = self.get_me()
                if user:
                    energy = user.get('energy', 0)
                    print(f"{DIM}⚡ Energy tersisa: {energy}{X}")

        print(f"\n{G}✅ Selesai {played} game.{X}")

    def claim_all(self):
        """Claim spin wheel + check-in"""
        print(f"{C}🎡 Auto Claim Spin + Check-in...{X}")
        if not self.init_data:
            print(f"{R}❌ Init_Data belum diset!{X}")
            return

        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        print(GAME_BANNER)
        print(f"\n{CYAN}[ HELIX ] Claiming Rewards...{X}")

        # 1. Spin Wheel
        print(f"\n{Y}🎡 Spinning Wheel...{X}")
        spin_result = self.spin_wheel()
        if spin_result:
            print(f"{G}[ ✓ ] Spin berhasil!{X}")
            try:
                print(f"{C}   {json.dumps(spin_result, indent=2)}{X}")
            except:
                pass
        else:
            print(f"{Y}⚠️ Spin skip/error (mungkin sudah di-claim){X}")

        random_delay(1, 2)

        # 2. Check-in
        print(f"\n{Y}📅 Daily Check-in...{X}")
        checkin_result = self.checkin()
        if checkin_result:
            print(f"{G}[ ✓ ] Check-in berhasil!{X}")
            try:
                print(f"{C}   {json.dumps(checkin_result, indent=2)}{X}")
            except:
                pass
        else:
            print(f"{Y}⚠️ Check-in skip/error (mungkin sudah di-claim){X}")

        # 3. Cek balance akhir
        print(f"\n{C}📊 Balance setelah claim:{X}")
        user = self.get_me()
        if user:
            print(f"{G}   Claimable: {user.get('claimable_reward', 0)} HLX{X}")
            print(f"{G}   Energy: {user.get('energy', 0)}/{user.get('energy_max', 100)}{X}")
        
        print(f"\n{G}✅ Claim selesai!{X}")

    # ============================================================
    # WATCH ADS
    # ============================================================
    def watch_ads_loop(self, max_rounds=50):
        print(f"{G}🚀 Memulai auto watch...{X}")
        if not self.init_data:
            print(f"{R}❌ Init_Data belum diset! Gunakan menu 5.{X}")
            return

        user_data = self.get_me()
        if user_data:
            self.last_balance = user_data.get('claimable_reward', 0)
            print(f"{DIM}Balance awal: {self.last_balance} HLX{X}\n")

        round_count = 0
        while round_count < max_rounds:
            round_count += 1
            os.system('cls' if os.name == 'nt' else 'clear')
            print(BANNER)
            print(ADS_BANNER)
            print(f"\n{CYAN}[ HELIX ] Initializing Ads Protocol...{X}")
            print(f"{G}[ ✓ ] Connection Established{X}")
            print(f"{G}[ ✓ ] Token Verified{X}\n")

            ads_data = self.get_ads()
            if not ads_data:
                print(f"{R}❌ Gagal get ads status.{X}")
                time.sleep(10)
                continue

            providers = []
            if ads_data.get("adsgram", {}).get("available"):
                max_ = ads_data["adsgram"]["max"]
                watched = ads_data["adsgram"]["watched"]
                if watched < max_:
                    providers.append({
                        "provider": "adsgram",
                        "max": max_,
                        "watched": watched,
                        "reward": ads_data.get("reward", 0),
                        "energy": ads_data.get("energy", 0)
                    })
            if ads_data.get("adsgram_reward", {}).get("available"):
                max_ = ads_data["adsgram_reward"]["max"]
                watched = ads_data["adsgram_reward"]["watched"]
                if watched < max_:
                    providers.append({
                        "provider": "adsgram_reward",
                        "max": max_,
                        "watched": watched,
                        "reward": ads_data.get("adsgram_reward_reward", 0),
                        "energy": ads_data.get("adsgram_reward_energy", 0)
                    })
            if ads_data.get("giga", {}).get("available"):
                max_ = ads_data["giga"]["max"]
                watched = ads_data["giga"]["watched"]
                if watched < max_:
                    providers.append({
                        "provider": "giga",
                        "max": max_,
                        "watched": watched,
                        "reward": ads_data.get("giga_reward", 0),
                        "energy": ads_data.get("giga_energy", 0)
                    })
            if ads_data.get("monetag", {}).get("available"):
                max_ = ads_data["monetag"]["max"]
                watched = ads_data["monetag"]["watched"]
                if watched < max_:
                    providers.append({
                        "provider": "monetag",
                        "max": max_,
                        "watched": watched,
                        "reward": ads_data.get("monetag_reward", 0),
                        "energy": ads_data.get("monetag_energy", 0)
                    })

            if not providers:
                print(f"{G}✅ Semua iklan selesai.{X}")
                break

            print(f"{Y}📺 Available Providers:{X}")
            for p in providers:
                print(f"  {C}{p['provider']}{X}: {p['watched']}/{p['max']} (reward: {p.get('reward',0)} HLX)")

            for p in providers:
                provider = p["provider"]
                max_watch = p["max"] - p["watched"]
                print(f"\n{CYAN}>>> {provider.upper()} REQUEST #{max_watch}{X}")

                for i in range(max_watch):
                    success, token = self.ads_shown(provider)
                    if not success:
                        print(f"{R}❌ Gagal shown {provider}{X}")
                        random_delay(2, 5)
                        continue

                    watch_duration = random.randint(14, 19)
                    print(f"{DIM}[ STATUS ] Watching Advertisement...{X}")
                    for sec in range(watch_duration):
                        time.sleep(1)
                        bar = progress_bar(sec+1, watch_duration)
                        sys.stdout.write(f"\r{CYAN}{bar}{X} {sec+1}s/{watch_duration}s")
                        sys.stdout.flush()
                    print()

                    if token:
                        if self.ads_watched(provider, token):
                            print(f"{G}[ ✓ ] Ads Completed{X}")
                            print(f"{G}[ ✓ ] Token Consumed Successfully{X}")
                            user_data = self.get_me()
                            if user_data:
                                current_balance = user_data.get('claimable_reward', 0)
                                diff = current_balance - self.last_balance
                                if diff > 0:
                                    print(f"{G}[ ✓ ] Reward Received: +{diff} HLX{X}")
                                    print(f"{G}[ ✓ ] Session Updated{X}")
                                    self.last_balance = current_balance
                                else:
                                    print(f"{Y}[ ! ] No reward change detected{X}")
                        else:
                            print(f"{R}❌ Gagal watched {provider}{X}")
                    else:
                        print(f"{Y}⚠️ Token tidak tersedia, lewati watched.{X}")
                    
                    random_delay(1, 3)

                ads_data = self.get_ads()
                if not ads_data:
                    break

            print(f"\n{CYAN}[ HELIX ] Waiting Next Task...{X}")
            time.sleep(2)

        print(f"\n{G}✅ Selesai {round_count} round.{X}")

# ============================================================
# FUNGSI MENU
# ============================================================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def set_credentials():
    global bot, ANTI_DETECTION
    clear_screen()
    print(BANNER)
    print(f"\n{Y}🔑 SET CREDENTIALS{X}")
    print(f"{C}{'='*50}{X}")
    init_data = input(f"{G}Masukkan init_data (panjang): {X}").strip()
    if not init_data:
        print(f"{R}❌ init_data tidak boleh kosong!{X}")
        time.sleep(2)
        return

    config = {"init_data": init_data, "anti_detection": ANTI_DETECTION}
    save_config(config)
    bot = HelixBot(init_data=init_data, anti_detection=ANTI_DETECTION)
    print(f"{G}✅ Credentials disimpan!{X}")
    time.sleep(1.5)

def check_balance():
    global bot
    clear_screen()
    print(BANNER)
    if not bot or not bot.init_data:
        print(f"{R}❌ Credentials belum diset! Gunakan menu 5.{X}")
        time.sleep(2)
        return

    print(f"{B}💰 Mengecek Balance...{X}\n")
    user = bot.get_me()
    if user:
        print(f"{G}👤 User: {user.get('username', 'N/A')} (ID: {user.get('telegram_id', 'N/A')}){X}")
        print(f"{G}💰 Balance TON: {user.get('ton_balance', 0)}{X}")
        print(f"{G}💰 Balance USDT: {user.get('usdt_balance', 0)}{X}")
        print(f"{G}⛏️ Claimable HLX: {user.get('claimable_reward', 0)}{X}")
        print(f"{G}📈 Total Mined: {user.get('total_mined', 0)}{X}")
        print(f"{G}⚡ Energy: {user.get('energy', 0)}/{user.get('energy_max', 100)}{X}")
        print(f"{G}📊 Rank: {user.get('rank', 'N/A')}{X}")
        print(f"{G}📅 Days Active: {user.get('days_active', 0)}{X}")
        print(f"{G}🎮 Games Won: {user.get('games_won', 0)}{X}")
    else:
        print(f"{R}❌ Gagal mengambil data.{X}")
    input(f"\n{C}Tekan Enter untuk kembali...{X}")

def toggle_anti_detection():
    global ANTI_DETECTION, bot
    clear_screen()
    print(BANNER)
    ANTI_DETECTION = not ANTI_DETECTION
    print(f"{G}✅ Anti Detection sekarang: {'AKTIF' if ANTI_DETECTION else 'NONAKTIF'}{X}")
    if bot:
        bot.anti_detection = ANTI_DETECTION
    config = load_config()
    if config:
        config["anti_detection"] = ANTI_DETECTION
        save_config(config)
    time.sleep(1.5)

def start_farming():
    global bot
    clear_screen()
    print(BANNER)
    if not bot or not bot.init_data:
        print(f"{R}❌ Credentials belum diset! Gunakan menu 5.{X}")
        time.sleep(2)
        return

    print(f"{G}🚀 Memulai Auto Watch dengan Anti Detection{' AKTIF' if ANTI_DETECTION else ' NONAKTIF'}{X}")
    print(f"{Y}⏹ Tekan Ctrl+C untuk berhenti.{X}\n")
    bot.watch_ads_loop(max_rounds=50)

def start_game():
    global bot
    clear_screen()
    print(BANNER)
    if not bot or not bot.init_data:
        print(f"{R}❌ Credentials belum diset! Gunakan menu 5.{X}")
        time.sleep(2)
        return

    print(f"{C}🎮 Memulai Auto Game...{X}")
    bot.play_game(max_games=5)

def claim_spin_checkin():
    global bot
    clear_screen()
    print(BANNER)
    if not bot or not bot.init_data:
        print(f"{R}❌ Credentials belum diset! Gunakan menu 5.{X}")
        time.sleep(2)
        return

    bot.claim_all()
    input(f"\n{C}Tekan Enter untuk kembali...{X}")

# ============================================================
# MAIN
# ============================================================
def main():
    global bot, ANTI_DETECTION

    config = load_config()
    if config:
        init_data = config.get("init_data")
        ANTI_DETECTION = config.get("anti_detection", True)
        if init_data:
            bot = HelixBot(init_data=init_data, anti_detection=ANTI_DETECTION)
            print(f"{G}🔑 Config ditemukan, auto-load credentials.{X}")
            time.sleep(1)
    else:
        bot = None

    while True:
        clear_screen()
        print(BANNER)
        print(MENU)
        print(f"{DIM}Status: {'🟢 Bot siap' if bot and bot.init_data else '🔴 Belum set credentials'}")
        print(f"{DIM}Anti Detection: {'🟢 AKTIF' if ANTI_DETECTION else '🔴 NONAKTIF'}{X}")

        choice = input(f"\n{CYAN}Select Menu » {X}").strip()

        if choice == "1":
            start_farming()
        elif choice == "2":
            start_game()
        elif choice == "3":
            claim_spin_checkin()
        elif choice == "4":
            check_balance()
        elif choice == "5":
            set_credentials()
        elif choice == "6":
            toggle_anti_detection()
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
