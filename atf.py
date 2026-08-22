#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import re
import urllib.parse
import requests
from datetime import datetime
import uuid

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
    GRAY = '\033[90m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

BANNER = f"""
{Colors.PINK}{Colors.BOLD}╔══════════════════════════════════════════════════════════════════╗
║                                                                          ║
║  {Colors.HEADER} █████╗ ████████╗███████╗                                 ║
║  {Colors.HEADER}██╔══██╗╚══██╔══╝██╔════╝                                 ║
║  {Colors.HEADER}███████║   ██║   █████╗                                   ║
║  {Colors.HEADER}██╔══██║   ██║   ██╔══╝                                   ║
║  {Colors.HEADER}██║  ██║   ██║   ██║                                     ║
║  {Colors.HEADER}╚═╝  ╚═╝   ╚═╝   ╚═╝                                     ║
║                                                                          ║
║  {Colors.PINK}🔥 ATF MINER BOOST BOT   {Colors.CYAN}│ {Colors.GREEN}v2.0 {Colors.END} ║
║                                                                          ║
╚════════════════════════════════════════════════════════════════════════════╝{Colors.END}
"""

INIT_FILE = "init_atfminer.txt"

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

class ATFMinerBot:
    def __init__(self):
        self.init_data = ""
        self.telegram_id = None
        self.username = None
        self.device_id = f"dev-{uuid.uuid4()}"
        
        self.base_url = "https://atfminers.asloni.online"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.1 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://atfminers.asloni.online",
            "Referer": "https://atfminers.asloni.online/miner/index.html?v=1784385080&entry=bot_start",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"'
        })
        
        self.session_token = None
        self.is_logged_in = False
        self.boost_count = 0
        self.consecutive_fails = 0
        self.cooldown_seconds = 15
        self.balance = 0
        self.total_boost_count = 0
        
        self.load_init_data()
        self.menu()

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

    def _generate_request_id(self):
        return str(uuid.uuid4())

    def _get_timestamp(self):
        return str(int(time.time() * 1000))

    def _call_api(self, action, extra_data=None):
        url = f"{self.base_url}/miner/index.php"
        params = {"action": action, "t": self._get_timestamp()}
        
        payload = {
            "initData": self.init_data,
            "request_id": self._generate_request_id(),
            "device_id": self.device_id,
            "tg_id": self.telegram_id
        }
        if extra_data:
            payload.update(extra_data)
        
        headers = self.session.headers.copy()
        if self.session_token:
            headers["X-ATF-TMA-Session"] = self.session_token
            headers["Cookie"] = f"atf_tma_session={self.session_token}"
        
        try:
            response = self.session.post(url, params=params, json=payload, headers=headers, timeout=30)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"{Colors.RED}❌ HTTP Error: {response.status_code}{Colors.END}")
                return None
        except Exception as e:
            print(f"{Colors.RED}❌ Request failed: {e}{Colors.END}")
            return None

    def login(self):
        if not self.init_data:
            print(f"{Colors.RED}❌ InitData kosong!{Colors.END}")
            return False
        
        print(f"{Colors.CYAN}🔄 Melakukan login...{Colors.END}")
        result = self._call_api("login", {"username": self.username})
        
        if result and result.get('status') == 'success':
            user = result.get('user', {})
            self.session_token = result.get('tma_session_token')
            self.is_logged_in = True
            self.balance = float(user.get('mined_balance', 0))
            self.total_boost_count = int(user.get('total_boost_count', 0))
            
            print(f"{Colors.GREEN}✅ Login BERHASIL!{Colors.END}")
            print(f"   {Colors.CYAN}Username:{Colors.END} {Colors.WHITE}{user.get('username')}{Colors.END}")
            print(f"   {Colors.CYAN}Level:{Colors.END} {Colors.WHITE}{user.get('miner_level')}{Colors.END}")
            print(f"   {Colors.CYAN}Balance:{Colors.END} {Colors.WHITE}{self.balance:.4f} ATF{Colors.END}")
            return True
        else:
            print(f"{Colors.RED}❌ Login GAGAL{Colors.END}")
            return False

    def countdown(self, seconds, message="⏳ Menunggu"):
        for i in range(seconds, 0, -1):
            print(f"\r{Colors.YELLOW}{message} {i} detik...{Colors.END}", end="", flush=True)
            time.sleep(1)
        print(f"\r{Colors.GREEN}{message} selesai!{Colors.END}          ")

    def do_boost(self):
        if not self.is_logged_in or not self.session_token:
            print(f"{Colors.RED}❌ Belum login!{Colors.END}")
            return False
        
        result = self._call_api("activate_boost", {"display_preview": round(0.15 + (0.10 * (time.time() % 1)), 4)})
        if not result:
            self.consecutive_fails += 1
            return False
        
        status = result.get('status')
        
        if status == 'success':
            self.boost_count += 1
            self.consecutive_fails = 0
            reward = result.get('pending_reward', 0)
            self.balance = float(result.get('user', {}).get('mined_balance', self.balance))
            self.total_boost_count = int(result.get('user', {}).get('total_boost_count', self.total_boost_count))
            
            print(f"{Colors.GREEN}✅ BOOST #{self.boost_count}{Colors.END} | {Colors.YELLOW}+{reward:.4f} ATF{Colors.END} | {Colors.CYAN}{datetime.now().strftime('%H:%M:%S')}{Colors.END}")
            print(f"   {Colors.GREEN}💰 Balance: {self.balance:.4f} ATF{Colors.END}")
            print(f"   {Colors.CYAN}📊 Total boost: {self.total_boost_count}{Colors.END}")
            
            print(f"{Colors.CYAN}⏳ Cooldown {self.cooldown_seconds} detik...{Colors.END}")
            self.countdown(self.cooldown_seconds, "⏳ Cooldown")
            return True
            
        elif status == 'busy':
            ready_at = result.get('boost_ready_at', 0)
            wait = ready_at - int(time.time())
            if wait > 0:
                print(f"{Colors.YELLOW}⏳ Busy, menunggu {wait} detik...{Colors.END}")
                self.countdown(wait, "⏰ Busy")
                return self.do_boost()
            else:
                time.sleep(1)
                return self.do_boost()
                
        elif status == 'cooldown':
            ready_at = result.get('boost_ready_at', 0)
            wait = ready_at - int(time.time())
            if wait > 0:
                print(f"{Colors.YELLOW}⏳ Cooldown server {wait} detik...{Colors.END}")
                self.countdown(wait, "⏰ Cooldown server")
                return self.do_boost()
            else:
                time.sleep(1)
                return self.do_boost()
                
        elif status == 'rate_limited':
            self.consecutive_fails += 1
            wait = min(30 * self.consecutive_fails, 300)
            print(f"{Colors.YELLOW}⚠️ Rate limited ({self.consecutive_fails}x), menunggu {wait} detik...{Colors.END}")
            self.countdown(wait, "⚠️ Rate limited")
            return self.do_boost()
            
        else:
            self.consecutive_fails += 1
            print(f"{Colors.RED}❌ Boost GAGAL: {status} - {result}{Colors.END}")
            if self.consecutive_fails >= 5:
                print(f"{Colors.YELLOW}⚠️ Terlalu banyak gagal, menunggu 60 detik...{Colors.END}")
                self.countdown(60, "⏳ Waiting")
                self.consecutive_fails = 0
            return False

    def auto_boost_loop(self):
        if not self.login():
            return
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}🚀 START AUTO BOOST LOOP{Colors.END}")
        print(f"{Colors.CYAN}{'═' * 50}{Colors.END}")
        print(f"{Colors.GRAY}Cooldown: {self.cooldown_seconds} detik{Colors.END}")
        print(f"{Colors.GRAY}Press Ctrl+C to stop{Colors.END}\n")
        
        while True:
            try:
                self.do_boost()
            except KeyboardInterrupt:
                print(f"\n{Colors.GREEN}👋 Dihentikan oleh user{Colors.END}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {e}{Colors.END}")
                time.sleep(5)

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
            clear_screen()
            print_banner()
            
            lines = [
                f"{Colors.GREEN}● SYSTEM{Colors.END}                 {Colors.GREEN}ONLINE{Colors.END}",
                f"{Colors.CYAN}◈ ENGINE{Colors.END}                 {Colors.GREEN}READY{Colors.END}",
                f"{Colors.GREEN}💰 BALANCE{Colors.END}              {Colors.YELLOW}{self.balance:.4f} ATF{Colors.END}",
                f"{Colors.CYAN}📊 BOOST COUNT{Colors.END}           {Colors.YELLOW}{self.total_boost_count}{Colors.END}",
            ]
            if self.init_data:
                lines.append(f"{Colors.GREEN}◈ INIT DATA{Colors.END}            {Colors.GREEN}LOADED{Colors.END}")
                lines.append(f"{Colors.CYAN}👤 USER{Colors.END}                {Colors.WHITE}{self.username}{Colors.END}")
            else:
                lines.append(f"{Colors.RED}◈ INIT DATA{Colors.END}            {Colors.RED}EMPTY{Colors.END}")
            
            print_box("ATF MINER BOOST", lines, Colors.PINK)
            print()
            
            print(f"\n{Colors.CYAN}╭{'─' * 52}╮{Colors.END}")
            print(f"{Colors.CYAN}│{Colors.END} {Colors.BOLD}{Colors.GREEN}[1]{Colors.END} {Colors.WHITE}Start Auto Boost{Colors.END}                          {Colors.CYAN}│{Colors.END}")
            print(f"{Colors.CYAN}│{Colors.END} {Colors.BOLD}{Colors.YELLOW}[2]{Colors.END} {Colors.WHITE}Set InitData{Colors.END}                             {Colors.CYAN}│{Colors.END}")
            print(f"{Colors.CYAN}│{Colors.END} {Colors.BOLD}{Colors.RED}[0]{Colors.END} {Colors.WHITE}Exit{Colors.END}                                      {Colors.CYAN}│{Colors.END}")
            print(f"{Colors.CYAN}╰{'─' * 52}╯{Colors.END}")
            print()
            
            choice = input(f"{Colors.CYAN}  Select option → {Colors.END}").strip()
            
            if choice == "0":
                print(f"\n{Colors.GREEN}👋 Goodbye!{Colors.END}")
                sys.exit(0)
            elif choice == "1":
                self.auto_boost_loop()
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
        bot = ATFMinerBot()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}🛑 Bot dihentikan oleh user!{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.END}")
        sys.exit(1)
