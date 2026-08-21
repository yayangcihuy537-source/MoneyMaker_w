#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import re
import random
import urllib.parse
import requests
from datetime import datetime, timedelta

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
║  {Colors.PINK}🔥 LTC MINER BOT   {Colors.CYAN}│ {Colors.GREEN}v2.0 {Colors.CYAN}│ {Colors.YELLOW}Telegram Mini App ║
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

# ============================================================
# MAIN BOT
# ============================================================

class LTCMinerBot:
    def __init__(self):
        self.init_data = ""
        self.telegram_id = None
        self.username = None
        self.balance = 0
        self.xp = 0
        self.level = 1
        self.total_earned = 0
        self.daily_ad_count = 0
        self.daily_ad_limit = 10
        self.boost_active = False
        self.running = False
        self.ads_watched = 0
        self.ads_claimed = 0
        
        self.logs = []
        
        self.base_url = "https://supabase.ltcminer.xyz"
        self.api_url = f"{self.base_url}/functions/v1"
        self.adsgram_base = "https://api.adsgram.ai"
        
        self.token = self.load_token()
        self.headers = self.build_headers()
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.ads_headers = {
            "cache-control": "max-age=0",
            "x-color-scheme": "light",
            "x-viewport-height": "680",
            "x-is-fullscreen": "false",
            "x-accelerometer": '{"x":-0.5359500050544739,"y":-6.933000564575195,"z":-7.120950222015381,"isStarted":false}',
            "x-gyroscope": '{"x":0.30717501044273376,"y":1.7766374349594116,"z":-1.0481624603271484,"isStarted":false}',
            "x-device-orientation": '{"absolute":false,"alpha":-2.1036267280578613,"beta":0.7557645440101624,"gamma":-0.0704130306839943,"isStarted":false}',
            "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "accept": "*/*",
            "origin": "https://tgltcminer.vercel.app",
            "x-requested-with": "org.telegram.messenger",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://tgltcminer.vercel.app/",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "priority": "u=1, i"
        }
        
        self.load_init_data()
        self.menu()

    def load_token(self):
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                return f.read().strip()
        return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc4NjcxNzIwMCwiZXhwIjo0OTQyMzkwODAwLCJyb2xlIjoiYW5vbiJ9.sUtI3lKmtdBpXDW4StLp_wtdYzUPOZuGEZuMt2tnWZM"

    def save_token(self, token):
        with open(TOKEN_FILE, 'w') as f:
            f.write(token)

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

    def add_log(self, icon, message, color=Colors.WHITE):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"{Colors.DIM}[{timestamp}]{Colors.END} {icon} {color}{message}{Colors.END}")
        if len(self.logs) > 6:
            self.logs.pop(0)

    def show_status(self):
        clear_screen()
        print_banner()
        lines = [
            f"{Colors.GREEN}● SYSTEM{Colors.END}                 {Colors.GREEN}ONLINE{Colors.END}",
            f"{Colors.CYAN}◈ ENGINE{Colors.END}                 {Colors.GREEN}READY{Colors.END}",
            f"{Colors.PINK}◉ NETWORK{Colors.END}                {Colors.GREEN}ACTIVE{Colors.END}",
            f"{Colors.GREEN}💰 BALANCE{Colors.END}              {Colors.YELLOW}{self.balance:.8f} LTC{Colors.END}",
            f"{Colors.PURPLE}📈 LEVEL{Colors.END}               {Colors.GREEN}{self.level}{Colors.END}",
            f"{Colors.CYAN}📺 ADS TODAY{Colors.END}             {Colors.YELLOW}{self.daily_ad_count}/{self.daily_ad_limit}{Colors.END}",
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
        for log in self.logs[-6:]:
            print(f"{Colors.CYAN}│{Colors.END} {log:<50} {Colors.CYAN}│{Colors.END}")
        print(f"{Colors.CYAN}╰{'─' * 52}╯{Colors.END}")

    # ==================== API CALLS ====================
    
    def call_api(self, action, data=None):
        url = f"{self.api_url}/{action}"
        try:
            response = self.session.post(url, json=data or {})
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def login(self):
        if not self.init_data:
            return False
        
        payload = {
            "action": "register_or_login",
            "telegram_id": self.telegram_id,
            "username": self.username,
            "first_name": self.username,
            "last_name": "",
            "language_code": "id",
            "ip_address": "36.71.173.183",
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        
        result = self.call_api("user-operations", payload)
        if result and result.get('success'):
            user = result.get('user', {})
            self.balance = user.get('balance', 0)
            self.xp = user.get('xp', 0)
            self.level = user.get('level', 1)
            self.total_earned = user.get('total_earned', 0)
            self.daily_ad_count = user.get('daily_ad_count', 0)
            self.boost_active = user.get('boost_active', False)
            return True
        return False

    def do_boost(self):
        if self.boost_active:
            return True
        
        payload = {
            "action": "activate_boost",
            "telegram_id": self.telegram_id,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        
        result = self.call_api("user-operations", payload)
        if result and result.get('success'):
            self.boost_active = True
            return True
        return False

    def _send_ad_reward_trigger(self):
        """Trigger reward setelah nonton short ad"""
        url = f"{self.api_url}/richads-bot-ad-trigger"
        payload = {
            "telegram_id": self.telegram_id,
            "event": "watch_ad_reward",
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get('skipped') == 'no_fill':
                    return False
                return True
        except:
            pass
        return False

    def watch_short_ad(self):
        """Nonton short ad + trigger reward"""
        if self.daily_ad_count >= self.daily_ad_limit:
            return False
        
        print(f"\n{Colors.PINK}📺 Iklan Pendek ({self.daily_ad_count+1}/{self.daily_ad_limit}){Colors.END}")
        
        # Countdown 15-25 detik
        duration = random.randint(15, 25)
        for i in range(duration, 0, -1):
            percent = int(((duration - i) / duration) * 100)
            bar = f"{Colors.GREEN}{'█' * int(percent/4)}{Colors.DIM}{'░' * (25 - int(percent/4))}{Colors.END}"
            print(f"\r   {Colors.CYAN}⏱️ {i:2d} detik tersisa {Colors.END}{bar} {percent}%", end="")
            time.sleep(1)
        print()
        
        # Trigger reward
        success = self._send_ad_reward_trigger()
        
        # Refresh balance
        self.login()
        
        if success or self.daily_ad_count < self.daily_ad_limit:
            self.daily_ad_count += 1
            self.ads_watched += 1
            print(f"   {Colors.GREEN}💰 Reward claimed! Balance: {self.balance:.8f} LTC{Colors.END}")
            return True
        else:
            print(f"   {Colors.RED}❌ Gagal claim reward{Colors.END}")
            return False

    # ==================== POP-UP AD ====================
    
    def start_pop_ad(self):
        url = f"{self.api_url}/pop-ad-start"
        payload = {
            "telegram_id": self.telegram_id,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data.get('session_id')
                elif data.get('reason') == 'cooldown':
                    wait = data.get('wait_seconds', 10)
                    print(f"   {Colors.YELLOW}⏳ Cooldown {wait}s{Colors.END}")
                    time.sleep(wait)
                    return self.start_pop_ad()
            return None
        except:
            return None

    def claim_pop_ad(self, session_id):
        url = f"{self.api_url}/pop-ad-claim"
        elapsed_ms = random.randint(15000, 25000)
        payload = {
            "telegram_id": self.telegram_id,
            "session_id": session_id,
            "blur_total_ms": 0,
            "elapsed_ms": elapsed_ms,
            "ad_done": True,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    reward = data.get('reward', 0)
                    self.balance += reward
                    return reward
            return 0
        except:
            return 0

    def watch_pop_ad(self):
        """Nonton Pop-up + claim"""
        if self.daily_ad_count >= self.daily_ad_limit:
            return False
        
        print(f"\n{Colors.PINK}📺 Pop-up ({self.daily_ad_count+1}/{self.daily_ad_limit}){Colors.END}")
        
        # Start session
        session_id = self.start_pop_ad()
        if not session_id:
            return False
        
        # Countdown 20-30 detik
        duration = random.randint(20, 30)
        for i in range(duration, 0, -1):
            percent = int(((duration - i) / duration) * 100)
            bar = f"{Colors.GREEN}{'█' * int(percent/4)}{Colors.DIM}{'░' * (25 - int(percent/4))}{Colors.END}"
            print(f"\r   {Colors.CYAN}⏱️ {i:2d} detik tersisa {Colors.END}{bar} {percent}%", end="")
            time.sleep(1)
        print()
        
        # Claim reward
        reward = self.claim_pop_ad(session_id)
        if reward > 0:
            self.daily_ad_count += 1
            self.ads_watched += 1
            print(f"   {Colors.GREEN}💰 +{reward:.8f} LTC (Balance: {self.balance:.8f}){Colors.END}")
            return True
        else:
            print(f"   {Colors.RED}❌ Gagal claim reward{Colors.END}")
            return False

    # ==================== MEGA POP-UP ====================
    
    def start_mega_pop_ad(self):
        url = f"{self.api_url}/mega-pop-ad-start"
        payload = {
            "telegram_id": self.telegram_id,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    return data.get('session_id')
                elif data.get('reason') == 'cooldown':
                    wait = data.get('wait_seconds', 10)
                    print(f"   {Colors.YELLOW}⏳ Cooldown {wait}s{Colors.END}")
                    time.sleep(wait)
                    return self.start_mega_pop_ad()
            return None
        except:
            return None

    def claim_mega_pop_ad(self, session_id):
        url = f"{self.api_url}/mega-pop-ad-claim"
        blur_ms = random.randint(20000, 35000)
        elapsed_ms = blur_ms + random.randint(1000, 5000)
        payload = {
            "telegram_id": self.telegram_id,
            "session_id": session_id,
            "blur_total_ms": blur_ms,
            "elapsed_ms": elapsed_ms,
            "ad_done": True,
            "_init_data": self.init_data,
            "_ts": int(time.time() * 1000)
        }
        try:
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    reward = data.get('reward', 0)
                    self.balance += reward
                    return reward
            return 0
        except:
            return 0

    def watch_mega_pop_ad(self):
        """Nonton Mega Pop-up + claim"""
        if self.daily_ad_count >= self.daily_ad_limit:
            return False
        
        print(f"\n{Colors.PURPLE}⭐ Mega Pop-up ({self.daily_ad_count+1}/{self.daily_ad_limit}){Colors.END}")
        
        # Start session
        session_id = self.start_mega_pop_ad()
        if not session_id:
            return False
        
        # Countdown 25-40 detik
        duration = random.randint(25, 40)
        for i in range(duration, 0, -1):
            percent = int(((duration - i) / duration) * 100)
            bar = f"{Colors.GREEN}{'█' * int(percent/4)}{Colors.DIM}{'░' * (25 - int(percent/4))}{Colors.END}"
            print(f"\r   {Colors.CYAN}⏱️ {i:2d} detik tersisa {Colors.END}{bar} {percent}%", end="")
            time.sleep(1)
        print()
        
        # Claim reward
        reward = self.claim_mega_pop_ad(session_id)
        if reward > 0:
            self.daily_ad_count += 1
            self.ads_watched += 1
            print(f"   {Colors.PURPLE}💰 +{reward:.8f} LTC (Balance: {self.balance:.8f}){Colors.END}")
            return True
        else:
            print(f"   {Colors.RED}❌ Gagal claim reward{Colors.END}")
            return False

    def run_cycle(self):
        """Satu siklus auto claim"""
        if not self.login():
            print(f"{Colors.RED}❌ Login gagal!{Colors.END}")
            return False
        
        self.do_boost()
        
        # Urutan iklan: short → pop → mega
        ads = [
            ("short", 5),
            ("pop", 3),
            ("mega", 2),
        ]
        
        total_success = 0
        for ad_type, count in ads:
            for i in range(count):
                if self.daily_ad_count >= self.daily_ad_limit:
                    break
                if ad_type == "short":
                    if self.watch_short_ad():
                        total_success += 1
                elif ad_type == "pop":
                    if self.watch_pop_ad():
                        total_success += 1
                elif ad_type == "mega":
                    if self.watch_mega_pop_ad():
                        total_success += 1
                time.sleep(2)
        
        return total_success > 0

    def start_all(self):
        """Main loop auto claim"""
        if not self.init_data:
            print(f"{Colors.RED}❌ InitData kosong! Set dulu menu [2]{Colors.END}")
            return
        
        self.ads_watched = 0
        cycle = 0
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}🚀 START AUTO CLAIM{Colors.END}")
        print(f"{Colors.CYAN}{'═' * 50}{Colors.END}")
        
        while True:
            cycle += 1
            print(f"\n{Colors.CYAN}🔄 SIKLUS #{cycle}{Colors.END}")
            print(f"{Colors.DIM}{'─' * 50}{Colors.END}")
            
            self.run_cycle()
            
            if self.daily_ad_count >= self.daily_ad_limit:
                print(f"\n{Colors.YELLOW}⏹️ Kuota iklan habis! ({self.daily_ad_count}/{self.daily_ad_limit}){Colors.END}")
                print(f"{Colors.CYAN}⏳ Lanjut besok...{Colors.END}")
                break
            
            wait = 10 * 60
            print(f"\n{Colors.YELLOW}⏳ Menunggu 10 menit...{Colors.END}")
            for _ in range(wait):
                time.sleep(1)
                if _ % 30 == 0:
                    rem = wait - _
                    print(f"\r   {Colors.CYAN}⏱️ {rem//60}m {rem%60}s tersisa{Colors.END}", end="")
            print()
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ SELESAI!{Colors.END}")
        print(f"{Colors.CYAN}📊 Total ads ditonton: {self.ads_watched}{Colors.END}")
        print(f"{Colors.YELLOW}💰 Balance akhir: {self.balance:.8f} LTC{Colors.END}")
        print(f"{Colors.CYAN}{'═' * 50}{Colors.END}")

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

    def menu(self):
        while True:
            self.show_status()
            
            print(f"\n{Colors.CYAN}╭{'─' * 52}╮{Colors.END}")
            print(f"{Colors.CYAN}│{Colors.END} {Colors.BOLD}{Colors.GREEN}[1]{Colors.END} {Colors.WHITE}Start Auto Claim{Colors.END}                        {Colors.CYAN}│{Colors.END}")
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
                input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")
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
