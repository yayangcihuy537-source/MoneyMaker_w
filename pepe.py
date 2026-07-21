#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════╗
║  🐸 PEPEFLOW AUTO-BOT V3.5 (FIXED BALANCE & ERRORS)   ║
║  DEVELOPED BY MoneyMaker_w                             ║
║  📱 @PepeFlowOfficialBot                               ║
║  🔄 Auto-reauth via /actions/tg_auth.php               ║
║  🛡️ Handle "2x bonus window expired" & balance comma  ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import random
import re
import requests
from datetime import datetime
from collections import deque

# WARNA
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GOLD = "\033[38;5;220m"
LIME = "\033[38;5;154m"
PINK = "\033[38;5;206m"
PURPLE = "\033[38;5;141m"
ORANGE = "\033[38;5;214m"
TEAL = "\033[38;5;45m"
R, G, Y, B, M, C, W, X = RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, RESET

# ==================== KONFIGURASI ====================
CONFIG_FILE = "pepeflow_config.json"
BASE_URL = "https://pepeflow.com"
USER_AGENT = "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.47 Mobile Safari/537.36 Telegram-Android/12.6.4 (Samsung SM-A556E; Android 16; SDK 36; HIGH)"
GAME_INTERVAL = 3
LOOP_DELAY = 3

GAME_MAP = {
    "lucky_wheel": {"display": "SPIN",    "icon": "🎡"},
    "slots":       {"display": "TAP",     "icon": "🎰"},
    "card_flip":   {"display": "FLIP",    "icon": "🎴"},
    "mystery_box": {"display": "NEON",    "icon": "🎁"},
}
ALL_GAMES = ["lucky_wheel", "slots", "card_flip", "mystery_box"]

class Config:
    def __init__(self):
        self.phpsessid = None
        self.init_data = None
        self.username = "MoneyMaker"
        self.phone = "+62812***25"
    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.phpsessid = data.get('phpsessid')
                self.init_data = data.get('init_data')
                self.username = data.get('username', self.username)
                self.phone = data.get('phone', self.phone)
                return True
        return False
    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'phpsessid': self.phpsessid,
                'init_data': self.init_data,
                'username': self.username,
                'phone': self.phone
            }, f, indent=2)
    def clear(self):
        if os.path.exists(CONFIG_FILE): os.remove(CONFIG_FILE)

def parse_balance(balance_str):
    """Parse balance string yang mungkin pakai koma ribuan"""
    if isinstance(balance_str, (int, float)):
        return float(balance_str)
    if isinstance(balance_str, str):
        # hilangkan koma ribuan (1,023.65 -> 1023.65)
        clean = balance_str.replace(',', '')
        try:
            return float(clean)
        except:
            return 0.0
    return 0.0

class PepeFlowBot:
    def __init__(self, phpsessid, init_data=None, username="MoneyMaker", phone="+62812***25"):
        self.phpsessid = phpsessid
        self.init_data = init_data
        self.username = username
        self.phone = phone
        self.session = requests.Session()
        self.base_url = BASE_URL
        self.balance = 0.0
        self.total_earned = 0.0
        self.games_played = 0
        self.games_won = 0
        self.logs = deque(maxlen=8)
        self.running = True
        self.cooldowns = {g: 0 for g in ALL_GAMES}
        self.play_counts = {g: 0 for g in ALL_GAMES}
        self.doubled_available = {g: False for g in ALL_GAMES}
        self.status = {g: "Ready" for g in ALL_GAMES}
        self.rewards = {g: 0 for g in ALL_GAMES}
        self.loop_counter = 0
        self.headers = {
            "User-Agent": USER_AGENT,
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/miniapp.php",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Connection": "keep-alive",
            "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
        }
        if phpsessid:
            self.session.cookies.set("PHPSESSID", phpsessid)

    def reauth(self):
        if not self.init_data:
            print(f"{RED}❌ Tidak ada initData untuk reauth!{RESET}")
            return False
        print(f"{YELLOW}🔄 Mencoba reauth dengan initData...{RESET}")
        import urllib.parse
        parsed = urllib.parse.parse_qs(self.init_data)
        user_str = parsed.get('user', [None])[0]
        telegram_id = "0"
        telegram_username = ""
        if user_str:
            try:
                user_json = json.loads(urllib.parse.unquote(user_str))
                telegram_id = str(user_json.get('id', '0'))
                telegram_username = user_json.get('username', '')
            except: pass
        files = {
            "init_data": (None, self.init_data),
            "telegram_id": (None, telegram_id),
            "telegram_username": (None, telegram_username),
            "auto_login": (None, "1"),
        }
        try:
            resp = self.session.post(f"{self.base_url}/actions/tg_auth.php", files=files, headers=self.headers)
            if resp.status_code == 200:
                for cookie in self.session.cookies:
                    if cookie.name == "PHPSESSID":
                        self.phpsessid = cookie.value
                        print(f"{GREEN}✅ Reauth sukses! PHPSESSID baru: {self.phpsessid}{RESET}")
                        config = Config()
                        config.load()
                        config.phpsessid = self.phpsessid
                        config.save()
                        return True
                set_cookie = resp.headers.get('Set-Cookie', '')
                if 'PHPSESSID' in set_cookie:
                    phpsessid = set_cookie.split('=')[1].split(';')[0]
                    self.phpsessid = phpsessid
                    print(f"{GREEN}✅ Reauth sukses! PHPSESSID baru: {self.phpsessid}{RESET}")
                    config = Config()
                    config.load()
                    config.phpsessid = self.phpsessid
                    config.save()
                    return True
            else:
                print(f"{RED}❌ Reauth gagal: {resp.status_code}{RESET}")
            return False
        except Exception as e:
            print(f"{RED}❌ Reauth error: {e}{RESET}")
            return False

    def _request(self, endpoint, files=None):
        url = f"{self.base_url}{endpoint}"
        try:
            if files:
                resp = self.session.post(url, headers=self.headers, files=files)
            else:
                resp = self.session.get(url, headers=self.headers)
            if resp.status_code in [401, 403] or (resp.status_code == 200 and "Not logged in" in resp.text):
                print(f"{YELLOW}⚠️ Session invalid. Mencoba reauth...{RESET}")
                if self.reauth():
                    if files:
                        resp = self.session.post(url, headers=self.headers, files=files)
                    else:
                        resp = self.session.get(url, headers=self.headers)
                else:
                    print(f"{RED}❌ Gagal reauth, stop.{RESET}")
                    self.running = False
            return resp
        except Exception as e:
            print(f"{RED}❌ Request error: {e}{RESET}")
            return None

    def get_dashboard(self):
        resp = self._request("/pages/load_dashboard.php")
        if resp and resp.status_code == 200:
            try:
                data = resp.json()
                self.balance = parse_balance(data.get('balance', 0))
                self.total_earned = parse_balance(data.get('total_earned', 0))
                return data
            except: pass
        return None

    def get_games_status(self):
        resp = self._request("/pages/load_games.php")
        if resp and resp.status_code == 200:
            html = resp.text
            match = re.search(r'var gameConfigs\s*=\s*({.*?});', html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    for internal, info in data.items():
                        for g in ALL_GAMES:
                            if g == internal:
                                cd = info.get('cooldown_remaining', info.get('cooldown', 0))
                                self.cooldowns[g] = cd
                                self.status[g] = self.format_time(cd) if cd > 0 else "Ready"
                                self.doubled_available[g] = bool(info.get('doubled', False))
                    return data
                except: pass
        return None

    def format_time(self, seconds):
        if seconds <= 0: return "Ready"
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        if mins > 0:
            return f"{mins}m{secs}s"
        return f"{secs}s"

    def play_game(self, game, doubled=False, base_reward=None, pick=None):
        if game not in ALL_GAMES:
            game = "lucky_wheel"
        files = {
            "action": (None, "play"),
            "game": (None, game),
            "doubled": (None, "1" if doubled else "0")
        }
        if doubled and base_reward is not None:
            files["base_reward"] = (None, str(base_reward))
        if pick is not None:
            files["pick"] = (None, str(pick))
        resp = self._request("/actions/mini_games.php", files=files)
        if resp and resp.status_code == 200:
            try: return resp.json()
            except: pass
        return None

    def play_lucky_wheel(self):
        # Coba doubled, jika gagal karena "2x bonus window" maka kita skip
        doubled = random.choice([True, False])
        base_reward = random.randint(10, 30)
        result = self.play_game("lucky_wheel", doubled=doubled, base_reward=base_reward if doubled else None)
        # Jika result error karena "2x bonus window", kita tandai game ini skip
        if result and result.get('status') == 'error' and '2x bonus window' in result.get('message', ''):
            self.cooldowns["lucky_wheel"] = 120  # set cooldown 2 menit agar tidak langsung dicoba lagi
            self.status["lucky_wheel"] = "Skip (2x expired)"
            return result
        return result

    def play_slots(self):
        return self.play_game("slots")
    def play_card_flip(self):
        doubled = random.choice([True, False])
        pick = random.randint(0, 7)
        base_reward = random.randint(10, 35)
        return self.play_game("card_flip", doubled=doubled, base_reward=base_reward if doubled else None, pick=pick)
    def play_mystery_box(self):
        pick = random.randint(0, 7)
        return self.play_game("mystery_box", pick=pick)

    def log(self, msg):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {msg}")
        if len(self.logs) > 8:
            self.logs.popleft()

    def update_balance(self, data):
        if data and 'new_balance' in data:
            self.balance = parse_balance(data['new_balance'])
            return True
        return False

    def display_dashboard(self):
        os.system('clear')
        self.get_games_status()
        print(f"{GOLD}╔══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{GOLD}║{RESET}  {CYAN}PEPEFLOW AUTO-BOT V3.5 (FIXED){RESET}                     {GOLD}║{RESET}")
        print(f"{GOLD}║{RESET}  {PINK}DEVELOPED BY MoneyMaker_w{RESET}                             {GOLD}║{RESET}")
        print(f"{GOLD}║{RESET}  📱 @PepeFlowOfficialBot                                 {GOLD}║{RESET}")
        print(f"{GOLD}╠══════════════════════════════════════════════════════════╣{RESET}")
        print(f"{GOLD}║{RESET}  {BOLD}ACCOUNT INFO{RESET}                                      {GOLD}║{RESET}")
        print(f"{GOLD}║{RESET}  Run / Loop : {CYAN}{self.loop_counter}{RESET}                                      {GOLD}║{RESET}")
        print(f"{GOLD}║{RESET}  Akun Aktif : {GREEN}{self.username}{RESET}                                 {GOLD}║{RESET}")
        print(f"{GOLD}║{RESET}  Total Saldo : {GREEN}{self.balance:.8f} PEPE{RESET}                        {GOLD}║{RESET}")
        print(f"{GOLD}╠══════════════════════════════════════════════════════════╣{RESET}")
        print(f"{GOLD}║{RESET}  {BOLD}MODE    STATUS    2X    PLY    REWARD  CD{RESET}        {GOLD}║{RESET}")
        print(f"{GOLD}║{RESET}  {DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}        {GOLD}║{RESET}")
        for g in ALL_GAMES:
            display = GAME_MAP[g]["display"]
            icon = GAME_MAP[g]["icon"]
            status = self.status[g]
            twox = "2X" if self.doubled_available[g] else "-"
            ply = self.play_counts[g]
            reward = self.rewards[g]
            cd = self.format_time(self.cooldowns[g])
            cd_display = cd if cd != "Ready" else "Ready"
            if status == "Ready":
                status_color = GREEN
            elif "m" in status or "s" in status or "Skip" in status:
                status_color = YELLOW
            else:
                status_color = RED
            print(f"{GOLD}║{RESET}  {icon} {display:<6} {status_color}{status:<8}{RESET}  {twox:<5} {ply:<5} {reward:<7} {cd_display:<6}{GOLD}║{RESET}")
        print(f"{GOLD}╠══════════════════════════════════════════════════════════╣{RESET}")
        print(f"{GOLD}║{RESET}  {BOLD}LIVE LOGS (last {len(self.logs)}){RESET}                                  {GOLD}║{RESET}")
        for log in list(self.logs)[-6:]:
            print(f"{GOLD}║{RESET}  {log}{' ' * (50 - len(log))} {GOLD}║{RESET}")
        print(f"{GOLD}╚══════════════════════════════════════════════════════════╝{RESET}")

    def farming_loop(self):
        print(f"{CYAN}🚀 Starting PepeFlow bot...{RESET}")
        self.get_dashboard()
        print(f"{GREEN}💰 Balance: {self.balance:.8f} PEPE{RESET}")
        print(f"{YELLOW}Press Ctrl+C to stop{RESET}\n")
        time.sleep(2)

        game_methods = {
            "lucky_wheel": self.play_lucky_wheel,
            "slots": self.play_slots,
            "card_flip": self.play_card_flip,
            "mystery_box": self.play_mystery_box,
        }

        self.display_dashboard()

        while self.running:
            self.loop_counter += 1
            self.get_games_status()
            ready_games = [g for g in ALL_GAMES if self.cooldowns.get(g, 0) <= 0]

            if not ready_games:
                min_cd = min([self.cooldowns.get(g, 0) for g in ALL_GAMES])
                if min_cd > 0:
                    print(f"{YELLOW}⏳ All games on cooldown. Next ready in {self.format_time(min_cd)}. Waiting...{RESET}")
                    time.sleep(min_cd + 1)
                self.display_dashboard()
                continue

            for game in ready_games:
                if not self.running: break
                self.display_dashboard()
                display = GAME_MAP[game]["display"]
                print(f"\n{CYAN}🎮 Playing {display}...{RESET}")
                result = game_methods[game]()
                if result and result.get('status') == 'success':
                    won = result.get('won', False)
                    reward = result.get('reward', 0)
                    self.games_played += 1
                    if won:
                        self.games_won += 1
                        self.total_earned += reward
                        self.update_balance(result)
                        self.rewards[game] = reward
                        self.play_counts[game] += 1
                        self.log(f"{GREEN}✔ {display} +{reward:.2f} PEPE (Balance: {self.balance:.8f}){RESET}")
                    else:
                        self.log(f"{RED}✖ {display} LOST (no reward){RESET}")
                else:
                    err = result.get('message', 'unknown error') if result else 'No response'
                    if 'cooldown' in err.lower():
                        self.get_games_status()
                        self.log(f"{YELLOW}⏳ {display} {err}{RESET}")
                    elif '2x bonus' in err.lower():
                        # Skip game ini untuk sementara
                        self.cooldowns[game] = 120
                        self.status[game] = "Skip (2x expired)"
                        self.log(f"{YELLOW}⏳ {display} {err} — skipped 2m{RESET}")
                    else:
                        self.log(f"{RED}✖ {display} FAILED: {err}{RESET}")
                time.sleep(GAME_INTERVAL)

            self.get_dashboard()
            self.display_dashboard()
            print(f"\n{DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
            print(f"{YELLOW}⏰ Loop {self.loop_counter} selesai. Checking cooldowns...{RESET}")
            time.sleep(LOOP_DELAY)

        print(f"\n{GREEN}✅ Bot stopped. Total games: {self.games_played}, Won: {self.games_won}, Earned: {self.total_earned:.2f} PEPE{RESET}")

# ==================== MENU ====================
def show_banner():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════════╗
║   {GOLD}🐸 PEPEFLOW AUTO-BOT V3.5 (FIXED){CYAN}                       ║
║   {PINK}DEVELOPED BY MoneyMaker_w                            {CYAN}║
║   📱 @PepeFlowOfficialBot                                   {CYAN}║
║   🛡️ Handle "2x bonus window expired" & balance comma     {CYAN}║
╚══════════════════════════════════════════════════════════╝{RESET}
""")

def show_menu():
    print(f"\n{CYAN}╔════════════════════════════════════════════════════╗")
    print(f"║                    MAIN MENU                         ║")
    print(f"╠════════════════════════════════════════════════════╣")
    print(f"║  {GREEN}[1]{RESET} 🚀 Start Farming (Mini Games)              ║")
    print(f"║  {YELLOW}[2]{RESET} 📝 Set PHPSESSID & InitData               ║")
    print(f"║  {YELLOW}[3]{RESET} ⚙️  Reset Config                         ║")
    print(f"║  {BLUE}[4]{RESET} 💰 Check Balance                         ║")
    print(f"║  {RED}[0]{RESET} ❌ Exit                                  ║")
    print(f"╚════════════════════════════════════════════════════╝{RESET}")

def start_farming():
    config = Config()
    if not config.load() or not config.phpsessid:
        print(f"{RED}❌ PHPSESSID belum diset!{RESET}")
        print(f"{YELLOW}📝 Set dulu di menu 2.{RESET}")
        input("Tekan Enter untuk kembali...")
        return

    bot = PepeFlowBot(config.phpsessid, config.init_data, config.username, config.phone)
    try:
        bot.farming_loop()
    except KeyboardInterrupt:
        bot.running = False
        print(f"\n{YELLOW}⏹️ Stopped by user{RESET}")
    input("Tekan Enter untuk kembali ke menu...")

def main():
    config = Config()
    config.load()

    while True:
        show_banner()
        show_menu()

        if config.phpsessid:
            print(f"{GREEN}✅ PHPSESSID tersimpan: {config.phpsessid[:10]}...{RESET}")
        else:
            print(f"{RED}❌ PHPSESSID belum diset!{RESET}")

        choice = input(f"\n{PURPLE}❯ Pilih: {RESET}").strip()

        if choice == '0':
            print(f"{YELLOW}👋 Bye!{RESET}")
            sys.exit(0)

        elif choice == '1':
            start_farming()

        elif choice == '2':
            print(f"{YELLOW}📝 Masukkan PHPSESSID dan InitData:{RESET}")
            phpsessid = input("PHPSESSID: ").strip()
            if phpsessid:
                config.phpsessid = phpsessid
            init_data = input("InitData (opsional, kosongkan jika tidak ada): ").strip()
            if init_data:
                config.init_data = init_data
            config.save()
            print(f"{GREEN}✅ Data disimpan!{RESET}")
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
            if not config.phpsessid:
                print(f"{RED}❌ PHPSESSID belum diset!{RESET}")
                input("Tekan Enter...")
                continue
            bot = PepeFlowBot(config.phpsessid, config.init_data, config.username, config.phone)
            data = bot.get_dashboard()
            if data:
                balance = data.get('balance', 0)
                print(f"{GREEN}💰 Balance: {parse_balance(balance):.8f} PEPE{RESET}")
            else:
                print(f"{RED}❌ Gagal mengambil balance. Cek PHPSESSID.{RESET}")
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
