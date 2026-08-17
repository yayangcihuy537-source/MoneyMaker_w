#!/usr/bin/env python3
"""
GRAM DROP - AUTO ADS + GAMES (REAL)
- Auto watch ads (earn + monetag) sampai limit harian
- Auto main game (whack, flappy, catch, merge) sampai habis
- Delay 17 detik sebelum claim (real play)
- Clean progress bar
- Auto detect daily limit & cooldown
"""

import os
import sys
import time
import json
import random
import uuid
import hashlib
import requests
from datetime import datetime

# ============================================================
# WARNA
# ============================================================
C = '\033[96m'
LC = '\033[1;96m'
Y = '\033[93m'
G = '\033[92m'
R = '\033[91m'
B = '\033[94m'
W = '\033[97m'
BLD = '\033[1m'
RS = '\033[0m'
DIM = '\033[2m'

# ============================================================
# BANNER
# ============================================================
BANNER = f"""
{C}╔══════════════════════════════════════════════════════════╗
║   ██████╗ ██████╗  █████╗ ███╗   ███╗██████╗ ██████╗   ║
║  ██╔════╝ ██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔══██╗  ║
║  ██║  ███╗██████╔╝███████║██╔████╔██║██████╔╝██████╔╝  ║
║  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║██╔═══╝ ██╔══██╗  ║
║  ╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║██║     ██║  ██║  ║
║   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝  ║
╠══════════════════════════════════════════════════════════╣
║                 {Y}☁️  GRAM DROP ☁️{RS}{C}                    ║
║            {LC}AUTO ADS + GAMES (REAL){RS}{C}              ║
╚══════════════════════════════════════════════════════════╝{RS}
"""

MENU = f"""
{C}╔══════════════════════════════════════════════╗
║              {Y}☁️ GRAM DROP ☁️{RS}{C}               ║
║          {LC}AUTO EARNER (REAL){RS}{C}             ║
╠══════════════════════════════════════════════╣
║  {G}[1] 📺 Watch Ads (auto){RS}{C}                 ║
║  {B}[2] 🎮 Play Games (auto){RS}{C}               ║
║  {Y}[3] 🔑 Set Init Data{RS}{C}                   ║
║  {B}[4] 💰 Check Balance{RS}{C}                   ║
║                                              ║
║  {R}[0] ❌ Exit{RS}{C}                                ║
╚══════════════════════════════════════════════╝{RS}
"""

CONFIG_FILE = "gramdrop_config.json"
BASE_URL = "https://modapkam.shop"

class GramDropBot:
    def __init__(self, init_data: str = None):
        self.init_data = init_data
        self.base_url = BASE_URL
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.device_id = self._gen_device_id()
        self.user_data = None
        self.balance = 0
        self.pending_claim = None
        self.daily_bonus_claimed = False
        self.stats = {'total_earned': 0, 'start_balance': 0}
        self.GAME_IDS = ['whack', 'flappy', 'catch', 'merge']
        self.FIXED_SCORE = 600
        self._update_headers()

    def _gen_device_id(self) -> str:
        fp = "1920x1080|24|8|5|Linux|Asia/Kolkata|en-US"
        return hashlib.sha256(f"{fp}|{uuid.uuid4()}".encode()).hexdigest()[:40]

    def _update_headers(self):
        self.session.headers.update({
            'Host': 'modapkam.shop',
            'sec-ch-ua-platform': '"Android"',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Safari/537.36 Telegram-Android/12.6.4',
            'Content-Type': 'application/json',
            'X-Telegram-Initdata': self.init_data or '',
            'X-Device-Id': self.device_id,
            'Accept': '*/*',
            'X-Requested-With': 'org.telegram.messenger.web',
            'Referer': 'https://modapkam.shop/',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': 'https://modapkam.shop',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Connection': 'keep-alive',
        })

    def _request(self, method: str, endpoint: str, data: dict = None):
        url = f"{self.api_url}{endpoint}"
        try:
            if method.upper() == 'POST':
                resp = self.session.post(url, json=data or {})
            else:
                resp = self.session.get(url)
            if resp.status_code != 200:
                print(f"{R}⚠️ HTTP {resp.status_code}{RS}")
                return None
            return resp.json()
        except Exception as e:
            print(f"{R}❌ Request gagal: {e}{RS}")
            return None

    def get_user(self):
        resp = self._request('GET', '/me')
        if not resp:
            return None
        if 'error' in resp:
            print(f"{R}❌ API error: {resp}{RS}")
            return None
        self.user_data = resp.get('user', {})
        if not self.user_data:
            return None
        self.balance = self.user_data.get('balance', 0)
        self.pending_claim = self.user_data.get('pendingClaim')
        self.daily_bonus_claimed = self.user_data.get('dailyBonusClaimed', False)
        if self.stats['start_balance'] == 0:
            self.stats['start_balance'] = self.balance
        return resp

    def _watch_ad(self, purpose: str) -> tuple:
        start = self._request('POST', '/ads/start', {'purpose': purpose})
        if not start or 'error' in start:
            return False, None
        nonce = start.get('nonce')
        if not nonce:
            return False, None
        wait = start.get('minWatch', 30) + random.randint(1, 3)
        print(f"{C}⏳ Watching ad ({wait}s)...{RS}")
        for i in range(wait, 0, -1):
            print(f"\r   {G}[{'#' * (wait - i + 1)}{' ' * (i - 1)}] {i:2d}s{RS}", end='', flush=True)
            time.sleep(1)
        print()
        time.sleep(random.uniform(0.5, 1.5))
        complete = self._request('POST', '/ads/complete', {'nonce': nonce})
        if not complete or 'error' in complete:
            return False, None
        reward = complete.get('reward', 0)
        if reward:
            self.balance = complete.get('balance', self.balance)
            self.stats['total_earned'] += reward
            print(f"{G}✅ Ad completed: +{reward} GD (Bal: {self.balance}){RS}")
        else:
            print(f"{Y}⚠️ Ad completed, no reward{RS}")
        return True, nonce

    def play_game_delayed(self, game_id: str) -> int:
        if self.pending_claim:
            self.claim_pending()
            self.get_user()
            if self.pending_claim:
                return 0

        game_info = self.user_data.get('playsLeft', {})
        if game_info.get(game_id, 0) <= 0:
            return 0

        print(f"{LC}▶️  Playing {game_id}...{RS}")
        start = self._request('POST', '/games/start', {'game': game_id})
        if not start or 'error' in start:
            return 0
        nonce = start.get('nonce')
        if not nonce:
            return 0

        # Simulasi main game
        play_time = random.randint(10, 25)
        for i in range(play_time, 0, -1):
            print(f"\r   {C}🎮 Playing {i:2d}s{RS}", end='', flush=True)
            time.sleep(1)
        print()

        # Finish game
        finish = self._request('POST', '/games/finish', {'nonce': nonce, 'score': self.FIXED_SCORE})
        if not finish or 'error' in finish:
            return 0
        sid = finish.get('sessionId')
        if not sid:
            return 0

        # Start ad
        success, ad_nonce = self._watch_ad('game')
        if not success or not ad_nonce:
            self.pending_claim = {'sessionId': sid, 'game': game_id, 'reward': finish.get('reward', 0)}
            print(f"{Y}⚠️ Ad failed, pending claim saved.{RS}")
            return 0

        # Delay 17 detik sebelum claim
        print(f"{LC}⏳ Waiting 17 seconds before claim...{RS}")
        for i in range(17, 0, -1):
            print(f"\r   {C}🕒 {i:2d}s remaining{RS}", end='', flush=True)
            time.sleep(1)
        print()

        # Claim
        claim_resp = self._request('POST', '/games/claim', {'sessionId': sid, 'adNonce': ad_nonce})
        if not claim_resp or 'error' in claim_resp:
            return 0
        reward = claim_resp.get('reward', 0)
        if reward:
            self.balance = claim_resp.get('balance', self.balance)
            self.stats['total_earned'] += reward
            self.user_data['playsLeft'] = claim_resp.get('playsLeft', {})
            print(f"{G}✅ Claimed! +{reward} GD (Bal: {self.balance}){RS}")
        else:
            print(f"{R}❌ Claim failed{RS}")
        return reward

    def claim_pending(self) -> int:
        if not self.pending_claim:
            return 0
        sid = self.pending_claim.get('sessionId')
        reward = self.pending_claim.get('reward', 0)
        print(f"{Y}📌 Claiming pending {reward} GD...{RS}")
        success, nonce = self._watch_ad('game')
        if not success:
            return 0
        resp = self._request('POST', '/games/claim', {'sessionId': sid, 'adNonce': nonce})
        if resp and 'error' not in resp:
            self.pending_claim = None
            self.balance = resp.get('balance', self.balance)
            self.stats['total_earned'] += resp.get('reward', 0)
            return resp.get('reward', 0)
        return 0

    def get_ads_info(self):
        if not self.user_data:
            self.get_user()
        counters = self.user_data.get('adCounters', {})
        adsgram = counters.get('adsgram', {'used': 0, 'cap': 8})
        monetag = counters.get('monetag', {'used': 0, 'cap': 6})
        return {
            'adsgram': {
                'used': adsgram.get('used', 0),
                'cap': adsgram.get('cap', 8),
                'remaining': max(0, adsgram.get('cap', 8) - adsgram.get('used', 0))
            },
            'monetag': {
                'used': monetag.get('used', 0),
                'cap': monetag.get('cap', 6),
                'remaining': max(0, monetag.get('cap', 6) - monetag.get('used', 0))
            }
        }

    def watch_ads_loop(self):
        print(f"\n{LC}📺 Starting Ads Auto...{RS}")
        round_num = 0
        while True:
            round_num += 1
            info = self.get_ads_info()
            if info['adsgram']['remaining'] <= 0 and info['monetag']['remaining'] <= 0:
                print(f"{G}✅ All ad limits reached!{RS}")
                break

            if round_num % 2 == 1 and info['adsgram']['remaining'] > 0:
                print(f"{Y}📊 Adsgram: {info['adsgram']['remaining']} left{RS}")
                success, _ = self._watch_ad('earn')
                if success:
                    print(f"{G}✅ Adsgram done{RS}")
            elif info['monetag']['remaining'] > 0:
                print(f"{Y}📊 Monetag: {info['monetag']['remaining']} left{RS}")
                success, _ = self._watch_ad('monetag')
                if success:
                    print(f"{G}✅ Monetag done{RS}")
            self.get_user()
            time.sleep(random.randint(3, 6))

    def play_games_loop(self):
        print(f"\n{LC}🎮 Starting Games Auto...{RS}")
        if self.pending_claim:
            self.claim_pending()
            self.get_user()

        total_earned = 0
        for game in self.GAME_IDS:
            if self.user_data.get('playsLeft', {}).get(game, 0) > 0:
                reward = self.play_game_delayed(game)
                if reward:
                    total_earned += reward
                time.sleep(random.randint(3, 6))

        print(f"{G}✅ Games finished! Total earned: +{total_earned} GD{RS}")

    def show_balance(self):
        self.get_user()
        print(f"\n{B}💰 Balance: {self.balance} GD{RS}")
        print(f"{B}📊 Total earned today: {self.stats['total_earned']} GD{RS}")
        if self.pending_claim:
            print(f"{Y}⚠️ Pending claim: {self.pending_claim.get('reward', 0)} GD{RS}")
        plays = self.user_data.get('playsLeft', {})
        print(f"{B}🎮 Remaining plays:{RS}")
        for g, s in plays.items():
            print(f"   {C}{g}: {s} x{RS}")

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

def set_init_data():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(f"\n{Y}🔑 SET INIT DATA{RS}")
    print(f"{C}{'='*50}{RS}")
    print(f"{Y}⚠️  Pastikan init_data masih VALID dan belum expired!{RS}")
    print(f"{Y}⚠️  Copy dari WebApp Telegram (bisa dari DevTools){RS}")
    init_data = input(f"{LC}X-Telegram-Initdata (wajib): {RS}").strip()
    if not init_data:
        print(f"{R}❌ Init data tidak boleh kosong!{RS}")
        time.sleep(2)
        return False

    old_config = load_config() or {}
    config = {
        "init_data": init_data,
        "device_id": old_config.get("device_id", hashlib.sha256(f"{uuid.uuid4()}".encode()).hexdigest()[:40])
    }
    save_config(config)
    print(f"{G}✅ Config disimpan!{RS}")
    time.sleep(1.5)
    return True

def main():
    config = load_config()
    init_data = config.get("init_data", "") if config else ""

    bot = None
    if init_data:
        bot = GramDropBot(init_data)
        if not bot.get_user():
            print(f"{R}❌ Init_data tidak valid atau expired. Silakan set ulang.{RS}")
            bot = None
            time.sleep(2)

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        print(MENU)
        if bot and bot.init_data:
            print(f"{G}🔑 Config: Aktif ✅ (Init_Data tersimpan){RS}")
            print(f"{B}💰 Balance: {bot.balance} GD{RS}")
        else:
            print(f"{R}🔑 Config: Belum diset ❌{RS}")

        choice = input(f"\n{LC}Pilih Menu » {RS}").strip()

        if choice == "1":
            if not bot:
                print(f"{R}❌ Set Init_Data dulu (menu 3){RS}")
                time.sleep(2)
                continue
            bot.watch_ads_loop()
            input(f"\n{C}Tekan Enter untuk kembali...{RS}")
        elif choice == "2":
            if not bot:
                print(f"{R}❌ Set Init_Data dulu (menu 3){RS}")
                time.sleep(2)
                continue
            bot.play_games_loop()
            input(f"\n{C}Tekan Enter untuk kembali...{RS}")
        elif choice == "3":
            if set_init_data():
                config = load_config()
                init_data = config.get("init_data", "")
                bot = GramDropBot(init_data)
                if not bot.get_user():
                    print(f"{R}❌ Init_data tidak valid. Coba lagi.{RS}")
                    bot = None
                    time.sleep(2)
        elif choice == "4":
            if not bot:
                print(f"{R}❌ Set Init_Data dulu (menu 3){RS}")
                time.sleep(2)
                continue
            bot.show_balance()
            input(f"\n{C}Tekan Enter untuk kembali...{RS}")
        elif choice == "0":
            print(f"\n{R}❌ Exit...{RS}")
            sys.exit(0)
        else:
            print(f"{R}❌ Pilihan tidak valid!{RS}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Y}⏹ Dihentikan oleh user.{RS}")
        sys.exit(0)
