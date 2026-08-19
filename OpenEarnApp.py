#!/usr/bin/env python3

import os
import sys
import requests
import time
import json
import random
import urllib.parse
from datetime import datetime

# ============================================================
# COLOR
# ============================================================

class Colors:
    GREEN = '\033[92m'
    LIGHTGREEN = '\033[92m'
    CYAN = '\033[96m'
    LIGHTCYAN = '\033[96m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    PURPLE = '\033[35m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    DIM = '\033[2m'

# ============================================================
# BANNER
# ============================================================

BANNER = f"""
{Colors.LIGHTGREEN}   ____                   ______                 ___
  / __ \\____  ___  ____  / ____/___ __________  /   |  ____  ____
 / / / / __ \\/ _ \\/ __ \\/ __/ / __ `/ ___/ __ \\/ /| | / __ \\/ __ \\
/ /_/ / /_/ /  __/ / / / /___/ /_/ / /  / / / / ___ |/ /_/ / /_/ /
\\____/ .___/\\___/_/ /_/_____/\\__,_/_/  /_/ /_/_/  |_/ .___/ .___/
    /_/                                            /_/   /_/

{Colors.LIGHTCYAN}────────────────────────────────────────────────────────────{Colors.RESET}
{Colors.LIGHTGREEN}              AUTO TAP • ADS • MINES • WHEEL{Colors.RESET}
{Colors.LIGHTCYAN}────────────────────────────────────────────────────────────{Colors.RESET}
{Colors.RESET}
{Colors.LIGHTCYAN}┃ {Colors.YELLOW}By Dev ScriptyXSou{Colors.RESET}
{Colors.LIGHTCYAN}┃ {Colors.YELLOW}Channel : t.me/ScriptyXSouu{Colors.RESET}
"""

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(BANNER)

# ============================================================
# BOX FUNCTIONS
# ============================================================

def box_top(title, time_str=""):
    title_part = f" {title} " if title else ""
    if time_str:
        return f"{Colors.LIGHTCYAN}╭──────────────────────────────────────────────────────────╮{Colors.RESET}\n{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.LIGHTGREEN}{title_part}{Colors.RESET}{' ' * (40 - len(title_part))}{Colors.LIGHTCYAN}{time_str}{Colors.RESET}        {Colors.LIGHTCYAN}│{Colors.RESET}"
    return f"{Colors.LIGHTCYAN}╭──────────────────────────────────────────────────────────╮{Colors.RESET}\n{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.LIGHTGREEN}{title_part}{Colors.RESET}{' ' * (54 - len(title_part))}{Colors.LIGHTCYAN}│{Colors.RESET}"

def box_mid():
    return f"{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.DIM}──────────────────────────────────────────────────────{Colors.RESET}  {Colors.LIGHTCYAN}│{Colors.RESET}"

def box_line(text, indent=0):
    pad = " " * indent
    return f"{Colors.LIGHTCYAN}│{Colors.RESET}  {pad}{text}{' ' * (52 - len(pad) - len(text))}{Colors.LIGHTCYAN}│{Colors.RESET}"

def box_bottom():
    return f"{Colors.LIGHTCYAN}╰──────────────────────────────────────────────────────────╯{Colors.RESET}"

def box_double():
    return f"{Colors.LIGHTCYAN}├──────────────────────────────────────────────────────────┤{Colors.RESET}"

def box_status_line(icon, label, value, color=Colors.WHITE):
    return f"{Colors.LIGHTCYAN}│{Colors.RESET}  {icon} {Colors.LIGHTGREEN}{label}{Colors.RESET}{' ' * (20 - len(label))}{color}{value}{Colors.RESET}{' ' * (30 - len(str(value)))}{Colors.LIGHTCYAN}│{Colors.RESET}"

# ============================================================
# KONFIGURASI
# ============================================================

BASE_URL = "https://app.theopenearn.info/api"
TAPS_PER_CYCLE = 100
COOLDOWN_SECONDS = 300
AD_WATCH_DURATION = 30

PROVIDER_CONFIG = {
    'adsgram': {'ad_type': 'video', 'fallback': True},
    'monetag': {'ad_type': 'impression', 'fallback': True},
    'telega': {'ad_type': 'video', 'fallback': True},
    'richads': {'ad_type': 'video', 'fallback': True},
    'onclicka': {'ad_type': 'video', 'fallback': True},
    'taddy': {'ad_type': 'video', 'fallback': True},
    'gigapub': {'ad_type': 'video', 'fallback': True},
    'adsgram_task': {'ad_type': 'task', 'fallback': True},
}

# ============================================================
# BOT CLASS
# ============================================================

class FurrBot:
    def __init__(self, init_data, username=None):
        self.init_data = init_data
        self.username = username or self._extract_username(init_data)
        
        self.headers = {
            "authorization": f"tma {init_data}",
            "user-agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.2",
            "content-type": "application/json",
            "x-requested-with": "org.telegram.messenger",
            "accept": "*/*",
            "origin": "https://app.theopenearn.info",
            "referer": "https://app.theopenearn.info/"
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        self.running = True
        self.balance = "0"
        self.tot_balance = "0"
        self.total_taps = 0
        self.total_earned = 0
        self.total_ads = 0
        self.total_ads_earned = 0
        self.total_ads_tot = 0
        self.total_mines_won = 0
        self.total_mines_busted = 0
        self.total_wheel = 0
        self.cycles = 0
        self.last_tx_id = None
        self.providers_status = {}
        self.success_ads = []
        self.failed_ads = []
        self.ads_results = []
        self.mines_results = []
    
    def _extract_username(self, init_data):
        try:
            parsed = dict(urllib.parse.parse_qsl(init_data))
            if 'user' in parsed:
                user = json.loads(urllib.parse.unquote(parsed['user']))
                return user.get('username') or user.get('first_name', 'Unknown')
            return "Unknown"
        except:
            return "Unknown"
    
    def _print_status(self, icon, msg, color=Colors.WHITE):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{Colors.CYAN}[{timestamp}]{Colors.RESET} {icon} {msg}")
    
    def get_user_info(self):
        try:
            resp = self.session.get(f"{BASE_URL}/user")
            if resp.status_code == 200:
                data = resp.json()
                self.balance = str(data.get('balance', '0'))
                self.tot_balance = str(data.get('tot_balance', '0'))
                return data
            return None
        except:
            return None
    
    # ============================================================
    # TAP
    # ============================================================
    
    def do_tap(self, taps=100):
        try:
            resp = self.session.post(f"{BASE_URL}/earn", json={"taps": taps})
            if resp.status_code == 200:
                data = resp.json()
                self.total_taps += taps
                self.total_earned += data.get('score', 0)
                self.balance = str(data.get('tot_balance', 0))
                return data
            return None
        except:
            return None
    
    def wait_for_cooldown(self, cooldown_until):
        if cooldown_until:
            try:
                cooldown_time = datetime.fromisoformat(cooldown_until.replace('Z', '+00:00'))
                now = datetime.now().astimezone()
                wait_seconds = (cooldown_time - now).total_seconds()
                
                if wait_seconds > 0:
                    remaining = int(wait_seconds)
                    menit = remaining // 60
                    detik = remaining % 60
                    print(f"{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.YELLOW}⏳ Sisa {menit}m {detik}s...{Colors.RESET}                   {Colors.LIGHTCYAN}│{Colors.RESET}")
                    while remaining > 0 and self.running:
                        time.sleep(min(10, remaining))
                        remaining -= 10
                        if remaining > 0:
                            menit = remaining // 60
                            detik = remaining % 60
                            print(f"\r{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.YELLOW}⏳ Sisa {menit}m {detik}s...{Colors.RESET}                   {Colors.LIGHTCYAN}│{Colors.RESET}", end="", flush=True)
                    print(f"\r{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.LIGHTGREEN}✅ Cooldown selesai!{Colors.RESET}                         {Colors.LIGHTCYAN}│{Colors.RESET}")
                    return
            except:
                pass
        
        print(f"{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.YELLOW}⏳ Cooldown 5 menit...{Colors.RESET}                     {Colors.LIGHTCYAN}│{Colors.RESET}")
        for i in range(5, 0, -1):
            if not self.running:
                break
            print(f"\r{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.YELLOW}⏳ Sisa {i} menit...   {Colors.RESET}                     {Colors.LIGHTCYAN}│{Colors.RESET}", end="", flush=True)
            time.sleep(60)
        print(f"\r{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.LIGHTGREEN}✅ Cooldown selesai!{Colors.RESET}                         {Colors.LIGHTCYAN}│{Colors.RESET}")
    
    # ============================================================
    # ADS
    # ============================================================
    
    def get_daily_ad_status(self):
        try:
            resp = self.session.get(f"{BASE_URL}/ads/daily-status")
            if resp.status_code == 200:
                data = resp.json()
                providers = data.get('providers', {})
                self.providers_status = {}
                available = []
                
                for name, info in providers.items():
                    remaining = info.get('remaining', 0)
                    blocked = info.get('blocked', False)
                    cooldown = info.get('cooldown_remaining', 0)
                    
                    self.providers_status[name] = {
                        'remaining': remaining,
                        'blocked': blocked,
                        'cooldown': cooldown
                    }
                    
                    if remaining > 0 and not blocked and cooldown == 0:
                        available.append(name)
                
                return available, self.providers_status
            return None, None
        except:
            return None, None
    
    def watch_ad_simulation(self, provider):
        print(f"{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.YELLOW}├─ Watch        : {AD_WATCH_DURATION}s{Colors.RESET}                   {Colors.LIGHTCYAN}│{Colors.RESET}")
        for remaining in range(AD_WATCH_DURATION, 0, -1):
            if not self.running:
                return False
            if remaining % 5 == 0 or remaining <= 3:
                print(f"\r{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.YELLOW}├─ Watch        : {remaining}s remaining{Colors.RESET}              {Colors.LIGHTCYAN}│{Colors.RESET}", end="", flush=True)
            time.sleep(1)
        print(f"\r{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.LIGHTGREEN}├─ Status       : ✓ SUCCESS{Colors.RESET}                       {Colors.LIGHTCYAN}│{Colors.RESET}")
        return True
    
    def complete_ad(self, provider):
        try:
            if not self.watch_ad_simulation(provider):
                return None
            
            config = PROVIDER_CONFIG.get(provider, {'ad_type': 'video', 'fallback': True})
            
            payload = {
                "ad_type": config.get('ad_type', 'video'),
                "provider": provider,
                "watched": True,
                "fallback": config.get('fallback', True)
            }
            
            resp = self.session.post(f"{BASE_URL}/ads/complete", json=payload)
            
            if resp.status_code == 200:
                data = resp.json()
                
                reward = data.get('reward', 0)
                base_reward = data.get('base_reward', 0)
                bonus_reward = data.get('bonus_reward', 0)
                tot_reward = data.get('tot_reward', 0)
                new_balance = data.get('new_balance')
                tx_id = data.get('tx_id')
                is_bonus = data.get('is_bonus', False)
                is_tot_only = data.get('is_tot_only', False)
                
                ton_reward = reward if reward > 0 else (base_reward + bonus_reward)
                
                if new_balance:
                    self.balance = str(new_balance)
                if tot_reward:
                    self.tot_balance = str(float(self.tot_balance) + tot_reward)
                
                self.total_ads += 1
                self.total_ads_earned += ton_reward
                self.total_ads_tot += tot_reward
                
                # Tampilkan reward
                if ton_reward > 0:
                    print(f"{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.LIGHTGREEN}├─ TON Reward   : +{ton_reward} TON{Colors.RESET}                   {Colors.LIGHTCYAN}│{Colors.RESET}")
                else:
                    print(f"{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.YELLOW}├─ TON Reward   : +0 TON{Colors.RESET}                     {Colors.LIGHTCYAN}│{Colors.RESET}")
                
                if tot_reward > 0:
                    print(f"{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.CYAN}├─ TOT Reward   : +{tot_reward} TOT{Colors.RESET}                    {Colors.LIGHTCYAN}│{Colors.RESET}")
                
                if is_tot_only:
                    print(f"{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.YELLOW}└─ Type         : TOT-only{Colors.RESET}                      {Colors.LIGHTCYAN}│{Colors.RESET}")
                elif is_bonus:
                    print(f"{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.MAGENTA}└─ Type         : BONUS!{Colors.RESET}                        {Colors.LIGHTCYAN}│{Colors.RESET}")
                else:
                    print(f"{Colors.LIGHTCYAN}│{Colors.RESET}  {Colors.LIGHTGREEN}└─ Type         : STANDARD{Colors.RESET}                      {Colors.LIGHTCYAN}│{Colors.RESET}")
                
                self.success_ads.append(provider)
                
                # Main Mines
                if tx_id and tx_id != self.last_tx_id:
                    self.last_tx_id = tx_id
                    mines_result = self.play_mines(tx_id, provider)
                    if mines_result:
                        self.mines_results.append(mines_result)
                    else:
                        self.mines_results.append({'status': 'busted', 'reward': 0})
                else:
                    self.mines_results.append({'status': 'skipped', 'reward': 0})
                
                self.spin_wheel()
                
                return data
            else:
                self.failed_ads.append(provider)
                return None
                
        except Exception as e:
            self.failed_ads.append(provider)
            return None
    
    # ============================================================
    # MINES
    # ============================================================
    
    def play_mines(self, tx_id, provider, difficulty=3):
        mines_headers = self.headers.copy()
        mines_headers['Referer'] = 'https://app.theopenearn.info/mines'
        
        try:
            start = requests.post(
                f"{BASE_URL}/mines/start",
                json={"ad_reward_tx_id": tx_id, "ad_provider": provider, "mines_count": difficulty},
                headers=mines_headers,
                timeout=15
            )
            
            if start.status_code != 200:
                return None
            
            game_data = start.json()
            game_id = game_data.get('game_id')
            if not game_id:
                return None
            
            used = []
            clicks = random.randint(2, 3)
            busted = False
            
            for i in range(clicks):
                tile = random.randint(0, 24)
                while tile in used:
                    tile = random.randint(0, 24)
                used.append(tile)
                
                click = requests.post(
                    f"{BASE_URL}/mines/{game_id}/click",
                    json={"cell_index": tile},
                    headers=mines_headers,
                    timeout=10
                )
                
                if click.status_code == 200:
                    result = click.json()
                    if result.get('status') in ['busted', 'hit_mine']:
                        busted = True
                        self.total_mines_busted += 1
                        return {'status': 'busted', 'reward': 0}
                time.sleep(0.5)
            
            # Cashout
            cash = requests.post(
                f"{BASE_URL}/mines/{game_id}/cashout",
                json={},
                headers=mines_headers,
                timeout=10
            )
            
            if cash.status_code == 200:
                cash_data = cash.json()
                new_bal = cash_data.get('new_balance')
                if new_bal:
                    self.balance = str(new_bal)
                reward = cash_data.get('reward', 0)
                if reward > 0:
                    self.total_mines_won += reward
                    return {'status': 'won', 'reward': reward}
            
            return None
            
        except Exception as e:
            return None
    
    # ============================================================
    # WHEEL
    # ============================================================
    
    def spin_wheel(self):
        try:
            stat = self.session.get(f"{BASE_URL}/wheel/status")
            if stat.status_code != 200:
                return 0
            
            data = stat.json()
            free_spins = data.get('free_spins_available', 0)
            
            if free_spins > 0:
                spin = self.session.post(
                    f"{BASE_URL}/wheel/spin",
                    json={"is_paid": False}
                )
                
                if spin.status_code == 200:
                    result = spin.json()
                    reward = result.get('reward', 0)
                    if reward > 0:
                        self.total_wheel += reward
                        return reward
            return 0
        except:
            return 0
    
    # ============================================================
    # MAIN LOOP
    # ============================================================
    
    def run(self):
        self.running = True
        while self.running:
            self.cycles += 1
            cycle_start = datetime.now()
            self.success_ads = []
            self.ads_results = []
            self.mines_results = []
            cycle_ton = 0
            cycle_tot = 0
            ads_count = 0
            mines_won = 0
            mines_busted = 0
            wheel_reward = 0
            
            # ===== CYCLE HEADER =====
            print()
            print(box_top(f"🔄 CYCLE #{self.cycles}", cycle_start.strftime("%H:%M:%S")))
            print(box_line(f"{Colors.LIGHTGREEN}⚡ AUTO FARMING SESSION{Colors.RESET}"))
            print(box_bottom())
            print()
            
            # ===== 1. TAP =====
            print(box_top(f"⚡ TAP PROCESS"))
            print(box_line(f"{Colors.YELLOW}├─ Requested      : {TAPS_PER_CYCLE} taps{Colors.RESET}"))
            
            result = self.do_tap(TAPS_PER_CYCLE)
            
            if result:
                score = result.get('score', 0)
                balance = result.get('tot_balance', 0)
                cooldown_until = result.get('cooldown_until')
                self.balance = str(balance)
                
                print(box_line(f"{Colors.LIGHTGREEN}├─ Status         : ✓ SUCCESS{Colors.RESET}"))
                print(box_line(f"{Colors.YELLOW}├─ Earned         : +{score}{Colors.RESET}"))
                print(box_line(f"{Colors.CYAN}├─ Current Score  : {score}{Colors.RESET}"))
                print(box_line(f"{Colors.LIGHTGREEN}└─ Balance        : {balance}{Colors.RESET}"))
                print(box_bottom())
                print()
                
                # ===== 2. COOLDOWN =====
                print(box_top("⏳ COOLDOWN"))
                print(box_line(f"{Colors.YELLOW}├─ Duration       : 5 minutes{Colors.RESET}"))
                self.wait_for_cooldown(cooldown_until)
                print(box_line(f"{Colors.LIGHTGREEN}└─ Next Action    : Checking advertisements{Colors.RESET}"))
                print(box_bottom())
                print()
                
                # ===== 3. ADS =====
                print(box_top("📺 ADVERTISEMENTS"))
                
                available, status = self.get_daily_ad_status()
                
                if available:
                    print(box_line(f"{Colors.YELLOW}├─ Providers Found : {len(available)}{Colors.RESET}"))
                    print(box_line(f"{Colors.CYAN}├─ Available       : {', '.join(available)}{Colors.RESET}"))
                    print(box_mid())
                    
                    for provider in available:
                        if not self.running:
                            break
                        print(box_line(f"{Colors.LIGHTGREEN}├─ ✓ {provider.upper()}{Colors.RESET}"))
                        result_ad = self.complete_ad(provider)
                        if result_ad:
                            ads_count += 1
                        time.sleep(1)
                    
                    print(box_bottom())
                    print()
                else:
                    print(box_line(f"{Colors.YELLOW}├─ No ads available{Colors.RESET}"))
                    print(box_bottom())
                    print()
                
                # ===== 4. MINES SUMMARY =====
                mines_won = self.total_mines_won
                mines_busted = self.total_mines_busted
                
                print(box_top("🎮 MINES"))
                print(box_line(f"{Colors.YELLOW}├─ Games Started   : {len(self.mines_results)}{Colors.RESET}"))
                won_count = sum(1 for r in self.mines_results if r and r.get('status') == 'won')
                busted_count = sum(1 for r in self.mines_results if r and r.get('status') == 'busted')
                print(box_line(f"{Colors.LIGHTGREEN}├─ Successful      : {won_count}{Colors.RESET}"))
                print(box_line(f"{Colors.RED}├─ Busted          : {busted_count}{Colors.RESET}"))
                print(box_line(f"{Colors.YELLOW}└─ Reward          : +{self.total_mines_won} TON{Colors.RESET}"))
                print(box_bottom())
                print()
                
                # ===== 5. WHEEL =====
                wheel_reward = self.spin_wheel()
                print(box_top("🎰 WHEEL"))
                print(box_line(f"{Colors.YELLOW}├─ Free Spins      : {1 if wheel_reward > 0 else 0}{Colors.RESET}"))
                print(box_line(f"{Colors.LIGHTGREEN}└─ Reward          : +{wheel_reward} TON{Colors.RESET}"))
                print(box_bottom())
                print()
                
                # ===== 6. CYCLE SUMMARY =====
                duration = (datetime.now() - cycle_start).total_seconds()
                cycle_ton = self.total_ads_earned + self.total_mines_won + wheel_reward
                cycle_tot = self.total_ads_tot
                
                print(box_top(f"✓ CYCLE #{self.cycles} COMPLETED", f"{int(duration)} seconds"))
                print(box_line(f"{Colors.LIGHTGREEN}📊 CYCLE SUMMARY{Colors.RESET}"))
                print(box_mid())
                print(box_line(f"{Colors.YELLOW}⚡ Taps Earned      : +{self.total_earned}{Colors.RESET}"))
                print(box_line(f"{Colors.LIGHTGREEN}💰 TON Earned      : +{cycle_ton:.8f} TON{Colors.RESET}"))
                print(box_line(f"{Colors.CYAN}💎 TOT Earned      : +{cycle_tot} TOT{Colors.RESET}"))
                print(box_line(f"{Colors.MAGENTA}📺 Ads Completed   : {ads_count}{Colors.RESET}"))
                print(box_line(f"{Colors.YELLOW}🎮 Mines Won       : {won_count}{Colors.RESET}"))
                print(box_line(f"{Colors.YELLOW}🎰 Wheel Reward    : +{wheel_reward} TON{Colors.RESET}"))
                print(box_mid())
                print(box_line(f"{Colors.LIGHTGREEN}💰 CURRENT BALANCE{Colors.RESET}"))
                print(box_line(f"{Colors.YELLOW}├─ TON              : {self.balance} TON{Colors.RESET}"))
                print(box_line(f"{Colors.CYAN}└─ TOT              : {self.tot_balance}{Colors.RESET}"))
                print(box_bottom())
                print()
                
            else:
                print(box_line(f"{Colors.RED}├─ Status         : ✗ FAILED{Colors.RESET}"))
                print(box_line(f"{Colors.YELLOW}└─ Retrying in 30s...{Colors.RESET}"))
                print(box_bottom())
                print()
                time.sleep(30)

# ============================================================
# MENU
# ============================================================

def menu(bot):
    while True:
        print_banner()
        
        # Account info
        print(f"{Colors.LIGHTCYAN}┌─ ACCOUNT ────────────────────────────────────────────────┐{Colors.RESET}")
        print(f"{Colors.LIGHTCYAN}│{Colors.RESET} {Colors.LIGHTGREEN}👤 Username :{Colors.RESET} {bot.username}")
        print(f"{Colors.LIGHTCYAN}│{Colors.RESET} {Colors.LIGHTGREEN}💰 Balance  :{Colors.RESET} {Colors.YELLOW}{bot.balance} TON{Colors.RESET}")
        print(f"{Colors.LIGHTCYAN}│{Colors.RESET} {Colors.LIGHTGREEN}💎 TOT      :{Colors.RESET} {Colors.CYAN}{bot.tot_balance}{Colors.RESET}")
        print(f"{Colors.LIGHTCYAN}└─────────────────────────────────────────────────────────┘{Colors.RESET}")
        
        print()
        print(f"{Colors.LIGHTGREEN}    {Colors.LIGHTGREEN}1 › {Colors.WHITE}🚀 Start Farming{Colors.RESET}")
        print(f"{Colors.LIGHTGREEN}    {Colors.LIGHTGREEN}2 › {Colors.WHITE}💰 Check Balance{Colors.RESET}")
        print(f"{Colors.LIGHTGREEN}    {Colors.LIGHTGREEN}3 › {Colors.WHITE}📺 Available Ads{Colors.RESET}")
        print(f"{Colors.LIGHTGREEN}    {Colors.LIGHTGREEN}4 › {Colors.WHITE}🎰 Spin Wheel{Colors.RESET}")
        print(f"{Colors.LIGHTGREEN}    {Colors.LIGHTGREEN}5 › {Colors.WHITE}📊 Statistics{Colors.RESET}")
        print()
        print(f"{Colors.RED}    {Colors.RED}0 › {Colors.WHITE}❌ Exit{Colors.RESET}")
        
        print(f"\n{Colors.LIGHTCYAN}────────────────────────────────────────────────────────────{Colors.RESET}")
        
        choice = input(f"{Colors.LIGHTGREEN}    OpenEarnApp › {Colors.WHITE}").strip()
        
        if choice in ["1"]:
            bot.running = True
            bot.run()
            input(f"\n{Colors.CYAN}Press Enter to return to menu...{Colors.RESET}")
            
        elif choice in ["2"]:
            bot.get_user_info()
            print(f"\n💰 Balance : {bot.balance} TON")
            print(f"💎 TOT     : {bot.tot_balance}")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.RESET}")
            
        elif choice in ["3"]:
            available, _ = bot.get_daily_ad_status()
            print()
            if available:
                for ad in available:
                    print(f"{Colors.LIGHTGREEN}● {ad.upper()}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}Tidak ada ads tersedia.{Colors.RESET}")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.RESET}")
            
        elif choice in ["4"]:
            reward = bot.spin_wheel()
            print(f"\n🎰 Wheel reward: +{reward} TON")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.RESET}")
            
        elif choice in ["5"]:
            print(f"\n{Colors.LIGHTGREEN}📊 STATISTICS{Colors.RESET}")
            print(f"Cycles        : {bot.cycles}")
            print(f"Total Taps    : {bot.total_taps}")
            print(f"Total Earned  : {bot.total_earned}")
            print(f"Total Ads     : {bot.total_ads}")
            print(f"TON Earned    : {bot.total_ads_earned:.8f} TON")
            print(f"TOT Earned    : {bot.total_ads_tot} TOT")
            print(f"Mines Won     : {bot.total_mines_won} TON")
            print(f"Mines Busted  : {bot.total_mines_busted}")
            print(f"Wheel Reward  : {bot.total_wheel} TON")
            input(f"\n{Colors.CYAN}Press Enter...{Colors.RESET}")
            
        elif choice in ["0"]:
            bot.running = False
            print(f"\n{Colors.LIGHTGREEN}👋 OpenEarnApp stopped.{Colors.RESET}")
            break
            
        else:
            print(f"{Colors.RED}❌ Menu tidak tersedia!{Colors.RESET}")
            time.sleep(1)

# ============================================================
# MAIN
# ============================================================

def main():
    print_banner()
    
    print(f"\n{Colors.LIGHTCYAN}{'═' * 60}{Colors.RESET}")
    print(f"{Colors.YELLOW}📌 CARA MENDAPATKAN INIT DATA:{Colors.RESET}")
    print(f"1. {Colors.WHITE}Buka bot The Open Earn di Telegram{Colors.RESET}")
    print(f"2. {Colors.WHITE}Buka DevTools (F12) → Tab Network{Colors.RESET}")
    print(f"3. {Colors.WHITE}Cari request ke '/api/user'{Colors.RESET}")
    print(f"4. {Colors.WHITE}Copy header 'authorization' (tanpa 'tma ' di awal){Colors.RESET}")
    print(f"{Colors.LIGHTCYAN}{'═' * 60}{Colors.RESET}")
    
    init_data = input(f"\n{Colors.LIGHTGREEN}🔑 Init data: {Colors.RESET}").strip()
    
    if not init_data:
        print(f"{Colors.RED}❌ Init data kosong!{Colors.RESET}")
        return
    
    if init_data.startswith('tma '):
        init_data = init_data[4:]
    
    username = input(f"{Colors.LIGHTGREEN}📛 Nama (enter untuk auto): {Colors.RESET}").strip()
    if not username:
        username = None
    
    bot = FurrBot(init_data, username)
    menu(bot)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}⏹️ Bot stopped{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
