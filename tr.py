#!/usr/bin/env python3
"""
TRewards Auto Watch Ads Bot - Infinite Loop Until Limit
✨ With cool emojis & precise limit detection ✨
"""

import os
import sys
import time
import json
import requests
from datetime import datetime
from colorama import init, Fore, Back, Style

init(autoreset=True)

# ============= COLOR =============
GREEN = Fore.LIGHTGREEN_EX
YELLOW = Fore.LIGHTYELLOW_EX
RED = Fore.LIGHTRED_EX
CYAN = Fore.LIGHTCYAN_EX
WHITE = Fore.WHITE
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT
DIM = Fore.LIGHTBLACK_EX
MAGENTA = Fore.LIGHTMAGENTA_EX
BLUE = Fore.LIGHTBLUE_EX

# ============= CONFIG =============
BASE_URL = "https://trewards.duckdns.org"
AD_WATCH_DURATION = 25  # detik
AD_LIST = ['ad_b1', 'ad_b2', 'ad_b3', 'ad_b4']

# ============= SCRIPT BANNER =============
def print_banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"""
{GREEN}╔══════════════════════════════════════════════════════════════╗
║  {BOLD}████████╗██████╗ ███████╗██╗    ██╗ █████╗ ██████╗ ███████╗{RESET}{GREEN}║
║  {BOLD}╚══██╔══╝██╔══██╗██╔════╝██║    ██║██╔══██╗██╔══██╗██╔════╝{RESET}{GREEN}║
║  {BOLD}   ██║   ██████╔╝█████╗  ██║ █╗ ██║███████║██████╔╝███████╗{RESET}{GREEN}║
║  {BOLD}   ██║   ██╔══██╗██╔══╝  ██║███╗██║██╔══██║██╔══██╗╚════██║{RESET}{GREEN}║
║  {BOLD}   ██║   ██║  ██║███████╗╚███╔███╔╝██║  ██║██║  ██║███████║{RESET}{GREEN}║
║  {BOLD}   ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝{RESET}{GREEN}║
║                                                          ║
║              {MAGENTA}✨ AUTO WATCH ADS BOT ✨{RESET}{GREEN}             ║
║           {YELLOW}♻️ INFINITE LOOP UNTIL LIMIT ♻️{RESET}{GREEN}        ║
║                                                          ║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")


class TrewadsBot:
    def __init__(self, init_data: str):
        self.init_data = init_data
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.1',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Origin': 'https://trewards-frontend.onrender.com',
            'Referer': 'https://trewards-frontend.onrender.com/',
            'X-Requested-With': 'org.telegram.messenger.web',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
        })
        self.coins = 0
        self.ton_balance = 0.0
        self.streak = 0
        self.total_ads = 0
        self.cycle_count = 0
        self.limit_reached = False
        self.ad_stats = {ad: {'coins': 0, 'ton': 0, 'total': 0} for ad in AD_LIST}

    def log(self, msg, color=GREEN):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"{GREEN}[{ts}]{RESET} {color}{msg}{RESET}")

    def _request(self, method, endpoint, data=None):
        url = f"{BASE_URL}{endpoint}"
        try:
            if method.upper() == 'POST':
                resp = self.session.post(url, json=data)
            else:
                resp = self.session.get(url, params=data)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 403:
                return {"status": "limit", "code": 403}
            elif resp.status_code == 400:
                detail = resp.json().get('detail', '')
                if 'limit' in detail.lower():
                    return {"status": "limit", "code": 400, "detail": detail}
                return {"status": "already", "code": 400, "detail": detail}
            else:
                self.log(f"⚠️ HTTP {resp.status_code}: {resp.text[:100]}", RED)
                return {"status": "error", "code": resp.status_code}
        except Exception as e:
            self.log(f"❌ Request error: {e}", RED)
            return {"status": "error", "code": 0}

    def user_init(self):
        payload = {
            "init_data": self.init_data,
            "referrer_id": None,
            "language": "id"
        }
        res = self._request('POST', '/api/user', payload)
        if res and res.get('status') != 'error':
            self.coins = res.get('coins', 0)
            self.ton_balance = res.get('ton_balance', 0.0)
            self.streak = res.get('streak', 0)
            self.log(f"👤 User: {res.get('username', 'N/A')} | 💰 Coins: {self.coins} | 💎 TON: {self.ton_balance} | 🔥 Streak: {self.streak}")
            return True
        self.log("❌ Failed to initialize user", RED)
        return False

    def claim_streak(self):
        payload = {"init_data": self.init_data}
        res = self._request('POST', '/api/claim-streak', payload)
        if res and res.get('success'):
            coins_earned = res.get('coins_earned', 0)
            self.coins += coins_earned
            self.streak = res.get('streak', 1)
            self.log(f"🎯 Streak claimed! +{coins_earned} coins (streak {self.streak})")
            return True
        elif res and res.get('status') == 'already':
            self.log("ℹ️ Streak already claimed today", YELLOW)
        else:
            self.log("ℹ️ Streak claim error", YELLOW)
        return False

    def watch_ad(self, ad_id: str, ad_type='coins'):
        endpoint = '/api/watch-ad' if ad_type == 'coins' else '/api/watch-ad-ton'
        payload = {
            "init_data": self.init_data,
            "ad_id": ad_id
        }
        label = "🪙" if ad_type == 'coins' else "💎"
        self.log(f"📺 Watching {label} ad: {ad_id} ({AD_WATCH_DURATION}s)", CYAN)

        # Progress bar 25 detik
        for i in range(AD_WATCH_DURATION, 0, -1):
            bar_len = 20
            filled = int((AD_WATCH_DURATION - i) / AD_WATCH_DURATION * bar_len)
            bar = '█' * filled + '░' * (bar_len - filled)
            print(f"\r{GREEN}⏳ [{bar}] {i}s left{RESET}", end='')
            time.sleep(1)
        print()

        res = self._request('POST', endpoint, payload)
        if res and res.get('success'):
            if ad_type == 'coins':
                earned = res.get('coins_earned', 0)
                self.coins = res.get('new_balance', self.coins)
                self.ad_stats[ad_id]['coins'] += 1
                self.ad_stats[ad_id]['total'] += 1
                self.log(f"✅ +{earned} coins (total: {self.coins})", GREEN)
            else:
                earned = res.get('ton_earned', 0)
                self.ton_balance = res.get('new_ton_balance', self.ton_balance)
                self.ad_stats[ad_id]['ton'] += 1
                self.ad_stats[ad_id]['total'] += 1
                self.log(f"✅ +{earned} TON (total: {self.ton_balance})", GREEN)
            self.total_ads += 1
            return True
        elif res and res.get('status') == 'limit':
            self.log(f"🚫 {ad_id} limit reached (403)", RED)
            self.limit_reached = True
            return False
        else:
            self.log(f"❌ {ad_id} failed", RED)
            return False

    def print_stats(self):
        self.log(f"\n📊 STATS SO FAR", CYAN)
        for ad, stats in self.ad_stats.items():
            total = stats['total']
            if total > 0:
                self.log(f"  {ad}: 🪙{stats['coins']} | 💎{stats['ton']} | 🎯{total} total", DIM)
        self.log(f"  🏆 Total all ads: {self.total_ads}", YELLOW)

    def run(self):
        if not self.user_init():
            return
        self.claim_streak()

        self.log(f"🔄 Starting infinite loop until limit...", CYAN)
        self.log(f"📋 Ads list: {', '.join(AD_LIST)}", DIM)

        cycle = 0
        while not self.limit_reached:
            cycle += 1
            self.log(f"\n{'='*50}", DIM)
            self.log(f"🔄 Cycle #{cycle}", CYAN)

            # Process each ad in order
            for ad_id in AD_LIST:
                if self.limit_reached:
                    break
                self.log(f"🎯 Processing {ad_id}", CYAN)

                # Try coins first
                success = self.watch_ad(ad_id, 'coins')
                if success:
                    continue

                # If failed (not limit), try TON
                if not self.limit_reached:
                    self.log(f"🔄 Retry {ad_id} with TON...", YELLOW)
                    success = self.watch_ad(ad_id, 'ton')
                    if success:
                        continue

                # If still failed and not limit, skip
                if not self.limit_reached:
                    self.log(f"⏭️ {ad_id} skipped (error)", YELLOW)
                else:
                    # limit reached, break outer loop
                    break

                time.sleep(1)

            # Show stats every cycle
            self.print_stats()

            # If limit reached, break out of while
            if self.limit_reached:
                break

            # Small delay between cycles
            self.log(f"⏳ Cycle #{cycle} completed. Waiting 3s...", DIM)
            time.sleep(3)

        # Final summary
        self.log(f"\n{'='*50}", DIM)
        self.log("📊 FINAL SUMMARY", CYAN)
        self.log(f"  🎯 Total ads watched: {self.total_ads}")
        self.log(f"  💰 Final Coins: {self.coins}")
        self.log(f"  💎 Final TON: {self.ton_balance}")
        self.log(f"  🔥 Final Streak: {self.streak}")
        self.log(f"  📋 Per ad stats:")
        for ad, stats in self.ad_stats.items():
            total = stats['total']
            if total > 0:
                self.log(f"    {ad}: 🪙{stats['coins']} | 💎{stats['ton']} | 🎯{total} total", DIM)
        self.log("🛑 Bot stopped (limit reached or error)", RED)

# ============= FUNGSI INPUT INIT DATA (FIX) =============
def get_init_data():
    print(f"{GREEN}🔑 Masukkan init_data dari Telegram WebApp:{RESET}")
    print(f"{DIM}   (Paste di sini, lalu ENTER. Jika panjang, bisa tekan ENTER 2x untuk selesai){RESET}")
    lines = []
    while True:
        line = sys.stdin.readline()
        if line == "\n" and lines:
            break
        if line == "\n":
            continue
        lines.append(line.rstrip('\n'))
    data = ''.join(lines).strip()
    if not data:
        print(f"{RED}❌ init_data kosong!{RESET}")
        return None
    return data

# ============= MAIN =============
def main():
    print_banner()
    init_data = get_init_data()
    if not init_data:
        print(f"{RED}❌ Gagal mendapatkan init_data.{RESET}")
        sys.exit(1)

    # Preview singkat
    print(f"{DIM}✅ InitData diterima (panjang: {len(init_data)} karakter){RESET}")
    confirm = input(f"{YELLOW}Lanjutkan? (y/n): {RESET}").strip().lower()
    if confirm not in ['y', 'yes', '']:
        print(f"{RED}❌ Dibatalkan.{RESET}")
        sys.exit(0)

    bot = TrewadsBot(init_data)
    try:
        bot.run()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}⏹ Bot dihentikan oleh user.{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
