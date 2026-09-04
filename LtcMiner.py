#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import random
import urllib.parse
import requests
from datetime import datetime
from collections import deque

# ============================================================
# COLOR
# ============================================================

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[35m'
    MAGENTA = '\033[35m'
    ORANGE = '\033[38;5;208m'
    PINK = '\033[38;5;206m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

BANNER = f"""
{Colors.PINK}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════╗
║                                                                          ║
║  {Colors.HEADER}██╗     ████████╗ ██████╗██╗   ██╗██╗  ██╗███████╗██╗   ██╗║
║  {Colors.HEADER}██║     ╚══██╔══╝██╔════╝╚██╗ ██╔╝██║  ██║██╔════╝╚██╗ ██╔╝║
║  {Colors.HEADER}██║        ██║   ██║      ╚████╔╝ ███████║█████╗   ╚████╔╝ ║
║  {Colors.HEADER}██║        ██║   ██║       ╚██╔╝  ██╔══██║██╔══╝    ╚██╔╝  ║
║  {Colors.HEADER}███████╗   ██║   ╚██████╗   ██║   ██║  ██║███████╗   ██║   ║
║  {Colors.HEADER}╚══════╝   ╚═╝    ╚═════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝   ╚═╝   ║
║                                                                          ║
║  {Colors.PINK}🔥 LTC MINER BOT   {Colors.CYAN}│ {Colors.GREEN}v3.4 {Colors.CYAN}│ {Colors.YELLOW}Auto Cycle {Colors.PINK}5S→3P→2M{Colors.END} ║
║                                                                          ║
╚════════════════════════════════════════════════════════════════════════════╝{Colors.END}
"""

INIT_FILE = "init_ltcminer.txt"
TOKEN_FILE = "token_ltcminer.txt"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(BANNER)

def print_box(title, lines, color=Colors.CYAN):
    print(f"{color}╭{'─' * 52}╮{Colors.END}")
    print(f"{color}│{Colors.END} {Colors.BOLD}{color}{title:^50}{Colors.END} {color}│{Colors.END}")
    print(f"{color}├{'─' * 52}┤{Colors.END}")
    for line in lines:
        print(f"{color}│{Colors.END} {line:<50} {color}│{Colors.END}")
    print(f"{color}╰{'─' * 52}╯{Colors.END}")

def ad_progress(seconds=30, label="📺 Watching ad"):
    for i in range(seconds, 0, -1):
        bar_len = 20
        filled = int((seconds - i) / seconds * bar_len)
        bar = '█' * filled + '░' * (bar_len - filled)
        sys.stdout.write(f"\r{Colors.GREEN}{label} [{bar}] {i}s left{Colors.END}")
        sys.stdout.flush()
        time.sleep(1)
    print()

# ============================================================
# MAIN BOT
# ============================================================

class LTCMinerBot:
    def __init__(self):
        self.init_data = ""
        self.telegram_id = None
        self.username = None
        self.balance = 0.0
        self.xp = 0
        self.level = 1
        self.total_earned = 0.0
        self.daily_ad_count = 0
        self.daily_ad_limit = 10
        self.boost_active = False
        self.mining_active = False
        self.boost_expires = None

        self.logs = deque(maxlen=8)
        self.total_gain_session = 0.0
        self.cycle_count = 0

        self.base_url = "https://supabase.ltcminer.xyz"
        self.api_url = f"{self.base_url}/functions/v1"
        self.token = self.load_token()
        self.session = requests.Session()
        self.session.headers.update(self.build_headers())

        self.load_init_data()
        self.menu()

    def load_token(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                return f.read().strip()
        return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc4NjcxNzIwMCwiZXhwIjo0OTQyMzkwODAwLCJyb2xlIjoiYW5vbiJ9.sUtI3lKmtdBpXDW4StLp_wtdYzUPOZuGEZuMt2tnWZM"

    def build_headers(self):
        return {
            "authorization": f"Bearer {self.token}",
            "apikey": self.token,
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.2",
            "origin": "https://tgltcminer.vercel.app",
            "referer": "https://tgltcminer.vercel.app/",
            "x-requested-with": "org.telegram.messenger",
            "accept": "*/*"
        }

    # ========== INIT DATA ==========
    def load_init_data(self):
        if os.path.exists(INIT_FILE):
            with open(INIT_FILE, 'r') as f:
                self.init_data = f.read().strip()
            self._parse_user_info()
        else:
            self.init_data = ""

    def save_init_data(self, data):
        with open(INIT_FILE, 'w') as f:
            f.write(data.strip())
        self.init_data = data.strip()
        self._parse_user_info()

    def _parse_user_info(self):
        try:
            parsed = urllib.parse.parse_qs(self.init_data)
            if 'user' in parsed:
                user = json.loads(parsed['user'][0])
                self.telegram_id = user.get('id')
                self.username = user.get('username') or user.get('first_name', 'Unknown')
        except:
            pass

    # ========== LOG & DASHBOARD ==========
    def add_log(self, icon, message, color=Colors.WHITE):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"{Colors.DIM}[{timestamp}]{Colors.END} {icon} {color}{message}{Colors.END}")
        if len(self.logs) > 8:
            self.logs.popleft()

    def show_status(self):
        clear_screen()
        print_banner()
        mining_status = "🟢 ON" if self.mining_active else "🔴 OFF"
        boost_status = "🟢 ON" if self.boost_active else "🔴 OFF"
        lines = [
            f"{Colors.GREEN}● SYSTEM{Colors.END}                 {Colors.GREEN}ONLINE{Colors.END}",
            f"{Colors.CYAN}◈ ENGINE{Colors.END}                 {Colors.GREEN}READY{Colors.END}",
            f"{Colors.PINK}◉ NETWORK{Colors.END}                {Colors.GREEN}ACTIVE{Colors.END}",
            f"{Colors.GREEN}💰 BALANCE{Colors.END}              {Colors.YELLOW}{self.balance:.8f} LTC{Colors.END}",
            f"{Colors.PURPLE}📈 LEVEL{Colors.END}               {Colors.GREEN}{self.level}{Colors.END} (XP: {self.xp})",
            f"{Colors.CYAN}📺 ADS TODAY{Colors.END}             {Colors.YELLOW}{self.daily_ad_count}/{self.daily_ad_limit}{Colors.END}",
            f"{Colors.MAGENTA}⛏️ MINING{Colors.END}              {Colors.GREEN}{mining_status}{Colors.END}",
            f"{Colors.PINK}🚀 BOOST{Colors.END}                 {Colors.GREEN}{boost_status}{Colors.END}",
            f"{Colors.ORANGE}🔄 SIKLUS{Colors.END}               {Colors.WHITE}{self.cycle_count}{Colors.END}",
        ]
        if self.init_data:
            lines.append(f"{Colors.GREEN}◈ INIT DATA{Colors.END}            {Colors.GREEN}LOADED{Colors.END}")
            lines.append(f"{Colors.CYAN}👤 USER{Colors.END}                {Colors.WHITE}{self.username}{Colors.END}")
        else:
            lines.append(f"{Colors.RED}◈ INIT DATA{Colors.END}            {Colors.RED}EMPTY{Colors.END}")

        print_box("LTC MINER BOT", lines, Colors.PINK)
        print()

        print(f"{Colors.CYAN}╭{'─' * 52}╮{Colors.END}")
        print(f"{Colors.CYAN}│{Colors.END} {Colors.BOLD}{Colors.WHITE}{'L I V E   L O G':^50}{Colors.END} {Colors.CYAN}│{Colors.END}")
        print(f"{Colors.CYAN}├{'─' * 52}┤{Colors.END}")
        for log in list(self.logs)[-8:]:
            print(f"{Colors.CYAN}│{Colors.END} {log:<50} {Colors.CYAN}│{Colors.END}")
        print(f"{Colors.CYAN}╰{'─' * 52}╯{Colors.END}")

    # ========== API CALLS ==========
    def _post(self, endpoint, data):
        url = f"{self.base_url}{endpoint}"
        try:
            resp = self.session.post(url, json=data, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            return None
        except:
            return None

    def _get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        try:
            resp = self.session.get(url, params=params, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            return None
        except:
            return None

    # ========== AUTH & USER ==========
    def login(self):
        if not self.init_data:
            return False
        payload = {
            "action": "register_or_login",
            "telegram_id": self.telegram_id,
            "username": self.username or "",
            "first_name": self.username or "",
            "last_name": "",
            "language_code": "id",
            "ip_address": "36.71.173.183",
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        result = self._post("/functions/v1/user-operations", payload)
        if result and result.get('success'):
            user = result.get('user', {})
            self.balance = user.get('balance', 0.0)
            self.xp = user.get('xp', 0)
            self.level = user.get('level', 1)
            self.total_earned = user.get('total_earned', 0.0)
            self.daily_ad_count = user.get('daily_ad_count', 0)
            self.mining_active = user.get('mining_active', False)
            self.boost_active = user.get('boost_active', False)
            self.boost_expires = user.get('boost_expires_at')
            self.add_log("✅", "Login berhasil", Colors.GREEN)
            return True
        else:
            self.add_log("❌", "Login gagal", Colors.RED)
            return False

    def start_mining(self):
        if self.mining_active:
            return True
        payload = {
            "action": "start_mining",
            "telegram_id": self.telegram_id,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        result = self._post("/functions/v1/user-operations", payload)
        if result and result.get('success'):
            self.mining_active = True
            self.add_log("⛏️", "Mining diaktifkan", Colors.GREEN)
            return True
        else:
            self.add_log("❌", "Gagal start mining", Colors.RED)
            return False

    def activate_boost(self):
        if self.boost_active:
            return True
        payload = {
            "action": "activate_boost",
            "telegram_id": self.telegram_id,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        result = self._post("/functions/v1/user-operations", payload)
        if result and result.get('success'):
            self.boost_active = True
            self.add_log("🚀", "Boost diaktifkan", Colors.GREEN)
            return True
        else:
            self.add_log("❌", "Gagal activate boost", Colors.RED)
            return False

    # ========== SHORT AD ==========
    def watch_short_ad(self):
        if self.daily_ad_count >= self.daily_ad_limit:
            return False

        # Progress 30 detik
        ad_progress(30, "📺 Short ad")

        payload = {
            "action": "ad_watch_reward",
            "telegram_id": self.telegram_id,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        result = self._post("/functions/v1/user-operations", payload)
        if result and result.get('success'):
            reward = result.get('reward', 0.0)
            if reward > 0:
                self.balance += reward
                self.total_gain_session += reward
                self.daily_ad_count += 1
                print(f"\n{Colors.GREEN}💰 +{reward:.8f} LTC (Short){Colors.END}")
                self.add_log(f"💰 +{reward:.8f} LTC", Colors.GREEN)
                # Jeda 20 detik setelah nonton
                self._cooldown(20, "⏳ Cooldown 20s")
                return True
        self.add_log("❌", "Short ad gagal", Colors.RED)
        return False

    # ========== POP AD ==========
    def pop_ad_start(self):
        payload = {
            "telegram_id": self.telegram_id,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        result = self._post("/functions/v1/pop-ad-start", payload)
        if result and result.get('ok'):
            return result.get('session_id')
        return None

    def pop_ad_claim(self, session_id):
        payload = {
            "telegram_id": self.telegram_id,
            "session_id": session_id,
            "blur_total_ms": random.randint(2000, 8000),
            "elapsed_ms": random.randint(25000, 35000),
            "ad_done": True,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        result = self._post("/functions/v1/pop-ad-claim", payload)
        if result and result.get('ok'):
            reward = result.get('reward', 0.0)
            if reward > 0:
                self.balance += reward
                self.total_gain_session += reward
                self.daily_ad_count += 1
                return reward
        return 0

    def watch_pop_ad(self):
        if self.daily_ad_count >= self.daily_ad_limit:
            return False
        session_id = self.pop_ad_start()
        if not session_id:
            return False
        ad_progress(30, "📺 Pop ad")
        reward = self.pop_ad_claim(session_id)
        if reward > 0:
            print(f"\n{Colors.PURPLE}💰 +{reward:.8f} LTC (Pop){Colors.END}")
            self.add_log(f"💰 +{reward:.8f} LTC", Colors.GREEN)
            self._cooldown(20, "⏳ Cooldown 20s")
            return True
        else:
            self.add_log("❌", "Pop claim gagal", Colors.RED)
            return False

    # ========== MEGA POP AD ==========
    def mega_pop_ad_start(self):
        payload = {
            "telegram_id": self.telegram_id,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        result = self._post("/functions/v1/mega-pop-ad-start", payload)
        if result and result.get('ok'):
            return result.get('session_id')
        return None

    def mega_pop_ad_claim(self, session_id):
        payload = {
            "telegram_id": self.telegram_id,
            "session_id": session_id,
            "blur_total_ms": random.randint(3000, 10000),
            "elapsed_ms": random.randint(25000, 40000),
            "ad_done": True,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        result = self._post("/functions/v1/mega-pop-ad-claim", payload)
        if result and result.get('ok'):
            reward = result.get('reward', 0.0)
            if reward > 0:
                self.balance += reward
                self.total_gain_session += reward
                self.daily_ad_count += 1
                return reward
        return 0

    def watch_mega_pop_ad(self):
        if self.daily_ad_count >= self.daily_ad_limit:
            return False
        session_id = self.mega_pop_ad_start()
        if not session_id:
            return False
        ad_progress(30, "📺 Mega Pop")
        reward = self.mega_pop_ad_claim(session_id)
        if reward > 0:
            print(f"\n{Colors.PINK}💰 +{reward:.8f} LTC (Mega){Colors.END}")
            self.add_log(f"💰 +{reward:.8f} LTC", Colors.GREEN)
            self._cooldown(20, "⏳ Cooldown 20s")
            return True
        else:
            self.add_log("❌", "Mega claim gagal", Colors.RED)
            return False

    # ========== COOLDOWN HELPER ==========
    def _cooldown(self, seconds, label="⏳ Cooldown"):
        for i in range(seconds, 0, -1):
            sys.stdout.write(f"\r{Colors.YELLOW}{label} {i}s left{Colors.END}")
            sys.stdout.flush()
            time.sleep(1)
        print()  # newline

    # ========== DAILY TASK ==========
    def claim_daily_task(self):
        payload = {
            "action": "claim_daily_ad_task",
            "telegram_id": self.telegram_id,
            "task_type": "watch_3",
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        result = self._post("/functions/v1/user-operations", payload)
        if result and result.get('success'):
            self.add_log("✅", "Daily task claimed", Colors.GREEN)
            return True
        return False

    # ========== CYCLE ==========
    def run_cycle(self):
        self.cycle_count += 1
        print(f"\n{Colors.CYAN}{'═' * 50}{Colors.END}")
        print(f"{Colors.CYAN}🔄 SIKLUS #{self.cycle_count}{Colors.END}")
        print(f"{Colors.CYAN}{'─' * 50}{Colors.END}")

        # Short 5x
        for i in range(5):
            if self.daily_ad_count >= self.daily_ad_limit:
                print(f"\n{Colors.YELLOW}⏹️ Kuota harian habis (limit {self.daily_ad_limit}){Colors.END}")
                return False
            print(f"\n{Colors.CYAN}📺 Short #{i+1}/5{Colors.END}")
            if not self.watch_short_ad():
                time.sleep(2)
            # jeda sudah di dalam watch_short_ad

        # Pop 3x
        for i in range(3):
            if self.daily_ad_count >= self.daily_ad_limit:
                print(f"\n{Colors.YELLOW}⏹️ Kuota harian habis{Colors.END}")
                return False
            print(f"\n{Colors.PURPLE}📺 Pop #{i+1}/3{Colors.END}")
            if not self.watch_pop_ad():
                time.sleep(2)

        # Mega 2x
        for i in range(2):
            if self.daily_ad_count >= self.daily_ad_limit:
                print(f"\n{Colors.YELLOW}⏹️ Kuota harian habis{Colors.END}")
                return False
            print(f"\n{Colors.PINK}📺 Mega #{i+1}/2{Colors.END}")
            if not self.watch_mega_pop_ad():
                time.sleep(2)

        # Claim daily task (opsional)
        self.claim_daily_task()

        print(f"\n{Colors.GREEN}✅ Siklus #{self.cycle_count} selesai!{Colors.END}")
        print(f"{Colors.CYAN}💰 Gain siklus ini: {self.total_gain_session:.8f} LTC{Colors.END}")
        print(f"{Colors.CYAN}💰 Balance: {self.balance:.8f} LTC{Colors.END}")
        return True

    def main_loop(self):
        if not self.init_data:
            self.add_log("❌", "InitData kosong! Set dulu.", Colors.RED)
            return

        self.add_log("🚀", "Memulai LTC Miner Auto Cycle", Colors.CYAN)
        if not self.login():
            return

        if not self.mining_active:
            self.start_mining()
        else:
            self.add_log("⛏️", "Mining sudah aktif", Colors.CYAN)

        if not self.boost_active:
            self.activate_boost()
        else:
            self.add_log("🚀", "Boost sudah aktif", Colors.CYAN)

        while True:
            if self.daily_ad_count >= self.daily_ad_limit:
                print(f"\n{Colors.YELLOW}⏹️ Kuota harian habis! ({self.daily_ad_count}/{self.daily_ad_limit}){Colors.END}")
                print(f"{Colors.CYAN}⏳ Menunggu 10 menit untuk reset...{Colors.END}")
                for _ in range(10 * 60):
                    time.sleep(1)
                    if _ % 30 == 0:
                        rem = 10 * 60 - _
                        print(f"\r   {Colors.CYAN}⏱️ {rem//60}m {rem%60}s tersisa{Colors.END}", end="")
                print()
                self.daily_ad_count = 0
                self.login()
                continue

            if not self.run_cycle():
                time.sleep(10)
                continue

            # Tunggu 10 menit sebelum siklus berikutnya
            print(f"\n{Colors.YELLOW}⏳ Menunggu 10 menit...{Colors.END}")
            for _ in range(10 * 60):
                time.sleep(1)
                if _ % 30 == 0:
                    rem = 10 * 60 - _
                    print(f"\r   {Colors.CYAN}⏱️ {rem//60}m {rem%60}s tersisa{Colors.END}", end="")
            print()

    def start_all(self):
        self.main_loop()
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")

    # ========== SET INIT DATA ==========
    def set_init_data(self):
        print(f"\n{Colors.CYAN}{Colors.BOLD}📝 MASUKKAN TELEGRAM INIT DATA{Colors.END}")
        print(f"{Colors.YELLOW}(copy dari network log atau WebView){Colors.END}")
        print(f"{Colors.DIM}{'─' * 50}{Colors.END}")
        new_data = input(f"{Colors.CYAN}➜ {Colors.END}").strip()
        if not new_data:
            print(f"{Colors.RED}❌ InitData tidak boleh kosong!{Colors.END}")
            return
        self.save_init_data(new_data)
        print(f"{Colors.GREEN}✅ InitData saved!{Colors.END}")

    # ========== MENU ==========
    def menu(self):
        while True:
            self.show_status()
            print(f"\n{Colors.CYAN}╭{'─' * 52}╮{Colors.END}")
            print(f"{Colors.CYAN}│{Colors.END} {Colors.BOLD}{Colors.GREEN}[1]{Colors.END} {Colors.WHITE}Start Auto Cycle (5S→3P→2M){Colors.END}     {Colors.CYAN}│{Colors.END}")
            print(f"{Colors.CYAN}│{Colors.END} {Colors.BOLD}{Colors.YELLOW}[2]{Colors.END} {Colors.WHITE}Set InitData{Colors.END}                             {Colors.CYAN}│{Colors.END}")
            print(f"{Colors.CYAN}│{Colors.END} {Colors.BOLD}{Colors.RED}[0]{Colors.END} {Colors.WHITE}Exit{Colors.END}                                      {Colors.CYAN}│{Colors.END}")
            print(f"{Colors.CYAN}╰{'─' * 52}╯{Colors.END}")
            print()
            choice = input(f"{Colors.CYAN}  Select option → {Colors.END}").strip()
            if choice == "0":
                print(f"\n{Colors.GREEN}👋 Goodbye!{Colors.END}")
                sys.exit(0)
            elif choice == "1":
                self.start_all()
            elif choice == "2":
                self.set_init_data()
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
            else:
                print(f"{Colors.RED}❌ Invalid option!{Colors.END}")
                time.sleep(1)

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    try:
        bot = LTCMinerBot()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}🛑 Bot dihentikan oleh user!{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        sys.exit(1)
