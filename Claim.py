#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import time
import random
import re
import os
import sys
import json
from datetime import datetime
from colorama import init, Fore, Style
from pyfiglet import Figlet

# Init colorama
init(autoreset=True)

# ============================================================
# WARNA
# ============================================================
RED    = "\033[1;31m"
GREEN  = "\033[1;32m"
YELLOW = "\033[1;33m"
CYAN   = "\033[1;36m"
WHITE  = "\033[1;37m"
RESET  = "\033[0m"

# ============================================================
# BANNER
# ============================================================
def print_banner():
    f = Figlet(font="slant")
    print(CYAN + "╔════════════════════════════════════════════════════════════╗")
    print(WHITE + f.renderText("CLAIMCRYPTO"))
    print(CYAN + "╠════════════════════════════════════════════════════════════╣")
    print(GREEN + "  💰 AUTO CLAIM • AUTO FAUCET • AUTO LOGIN")
    print(YELLOW + "  ⚡ Fast • Faucet • Login")
    print(RED + "  👨‍💻 Developer : ScriptyXSouu")
    print(CYAN + "╚════════════════════════════════════════════════════════════╝" + RESET)

# ============================================================
# KONFIGURASI DEFAULT
# ============================================================
DEFAULT_CONFIG = {
    "base_url": "https://claimcrypto.in",
    "coins": ["ltc", "doge", "trx", "sol", "usdt", "dash", "bch", "dgb", "eth", "fey", "zec", "bnb"],
    "default_coin": "ltc",
    "min_delay": 6,
    "max_delay": 11,
    "max_claims_per_session": 10,
    "user_agents": [
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 11; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36"
    ]
}

CONFIG_FILE = 'config.json'
SETTINGS_FILE = 'settings.json'

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                user_config = json.load(f)
                merged = DEFAULT_CONFIG.copy()
                merged.update(user_config)
                return merged
        except:
            pass
    return DEFAULT_CONFIG

# ============================================================
# SETTINGS
# ============================================================
DEFAULT_SETTINGS = {
    "email": "",
    "coin": "ltc",
    "target": 10,
    "user_agent_index": 0
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    else:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(DEFAULT_SETTINGS, f, indent=4)
        return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ============================================================
# BOT
# ============================================================
class ClaimCryptoBot:
    def __init__(self):
        self.config = load_config()
        self.settings = load_settings()
        self.base_url = self.config['base_url']
        self.all_coins = self.config.get('coins', [])
        self.current_coin_index = 0
        self.bad_coins = set()  # koin yang udah limit atau kena captcha
        self.session = requests.Session()
        self.logged_in = False
        self.csrf_token = None
        self.ci_session = None
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'limit_reached': False,
            'captcha_detected': False,
            'coins_used': [],
            'start_time': None
        }
        self._setup_session()
        self._apply_user_agent()

    def _setup_session(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Cache-Control': 'max-age=0',
            'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
        }
        self.session.headers.update(headers)

    def _apply_user_agent(self):
        ua_list = self.config.get('user_agents', [])
        idx = self.settings.get('user_agent_index', 0)
        ua = ua_list[idx] if 0 <= idx < len(ua_list) else ua_list[0]
        self.session.headers.update({'User-Agent': ua})

    def set_user_agent_by_index(self, idx):
        self.settings['user_agent_index'] = idx
        save_settings(self.settings)
        self._apply_user_agent()

    def set_email(self, email):
        self.settings['email'] = email
        save_settings(self.settings)

    def set_coin(self, coin):
        self.settings['coin'] = coin
        save_settings(self.settings)
        if coin.lower() in [c.lower() for c in self.all_coins]:
            self.current_coin_index = [c.lower() for c in self.all_coins].index(coin.lower())

    def set_target(self, target):
        self.settings['target'] = target
        save_settings(self.settings)

    def _random_delay(self, min_sec=None, max_sec=None):
        min_delay = min_sec or self.config.get('min_delay', 6)
        max_delay = max_sec or self.config.get('max_delay', 11)
        jitter = random.uniform(0, 1.5)
        return random.uniform(min_delay, max_delay) + jitter

    def _log(self, message, color=Fore.WHITE, emoji='', end='\n'):
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"{color}[{timestamp}] {emoji} {message}{Style.RESET_ALL}", end=end)

    def _extract_csrf(self, html):
        patterns = [
            r'csrf_token_name\s*=\s*"([^"]+)"',
            r'name="csrf_token_name"\s*value="([^"]+)"',
            r'csrf_cookie_name\s*=\s*"([^"]+)"',
            r'<input[^>]*name="csrf_token_name"[^>]*value="([^"]+)"',
        ]
        for p in patterns:
            m = re.search(p, html)
            if m:
                return m.group(1)
        return self.session.cookies.get('csrf_cookie_name')

    def _extract_token(self, html):
        patterns = [
            r'name="token"\s*value="([^"]+)"',
            r'token\s*=\s*"([^"]+)"',
            r'<input[^>]*name="token"[^>]*value="([^"]+)"',
            r'var\s+token\s*=\s*"([^"]+)"',
            r'token\s*=\s*\'([^\']+)\'',
            r'token=([a-zA-Z0-9]+)',
            r'"token":"([^"]+)"',
            r'token":"([^"]+)"',
            r'["\']token["\']\s*:\s*["\']([^"\']+)["\']',
            r'<script[^>]*>.*?token\s*=\s*["\']([^"\']+)["\']',
            r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
        ]
        for p in patterns:
            m = re.search(p, html, re.IGNORECASE | re.DOTALL)
            if m:
                return m.group(1)
        
        hidden_inputs = re.findall(
            r'<input[^>]*type="hidden"[^>]*name="([^"]+)"[^>]*value="([^"]+)"',
            html,
            re.IGNORECASE
        )
        for name, value in hidden_inputs:
            if 'token' in name.lower():
                return value
        
        if 'csrf_cookie_name' in self.session.cookies:
            return self.session.cookies.get('csrf_cookie_name')
        
        return None

    def login(self, email):
        self._log(f"Logging in with email: {email}", Fore.CYAN, '🔑')
        try:
            resp = self.session.get(f'{self.base_url}/')
            time.sleep(self._random_delay(2, 4))
            csrf = self._extract_csrf(resp.text)
            if not csrf:
                self._log("Failed to get CSRF token", Fore.RED, '❌')
                return False
            self.csrf_token = csrf
            data = {
                'fingerprint': '13abf0b009dd510c96d7b75d8f3a8dd0',
                'wallet': email,
                'csrf_token_name': csrf
            }
            login_resp = self.session.post(
                f'{self.base_url}/auth/login',
                data=data,
                headers={'Origin': self.base_url, 'Referer': f'{self.base_url}/', 'Content-Type': 'application/x-www-form-urlencoded'}
            )
            time.sleep(self._random_delay(3, 6))
            if 'dashboard' in login_resp.url or '/dashboard' in login_resp.text:
                self.logged_in = True
                self._log("Login successful!", Fore.GREEN, '✅')
                new_csrf = self._extract_csrf(login_resp.text)
                if new_csrf:
                    self.csrf_token = new_csrf
                return True
            else:
                self._log("Login failed", Fore.RED, '❌')
                return False
        except Exception as e:
            self._log(f"Login error: {str(e)}", Fore.RED, '❌')
            return False

    def get_faucet_page(self, coin):
        """Get faucet page - NO CAPTCHA DETECTION here! Only extract token."""
        coin = coin.lower()
        url = f'{self.base_url}/faucet/currency/{coin}'
        
        for attempt in range(3):
            try:
                headers = {
                    'Referer': f'{self.base_url}/',
                    'Sec-Fetch-Site': 'same-origin',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Dest': 'document',
                }
                self.session.headers.update(headers)
                resp = self.session.get(url)
                
                time.sleep(self._random_delay(4, 7))
                
                if resp.status_code != 200:
                    self._log(f"Failed to get faucet page: {resp.status_code}", Fore.RED, '❌')
                    continue
                
                html = resp.text
                
                csrf = self._extract_csrf(html)
                if csrf:
                    self.csrf_token = csrf
                
                token = self._extract_token(html)
                
                if not token:
                    self._log("Token not found, refreshing session...", Fore.YELLOW, '🔄')
                    resp2 = self.session.get(f'{self.base_url}/')
                    time.sleep(self._random_delay(2, 4))
                    csrf2 = self._extract_csrf(resp2.text)
                    if csrf2:
                        self.csrf_token = csrf2
                    token = self._extract_token(resp2.text)
                
                if token:
                    return {
                        'html': html,
                        'csrf': self.csrf_token,
                        'token': token,
                        'cookies': self.session.cookies.get_dict()
                    }
                
                self._log(f"Attempt {attempt+1}/3 failed to get token", Fore.YELLOW, '⏳')
                time.sleep(self._random_delay(3, 5))
                
            except Exception as e:
                self._log(f"Error: {str(e)}", Fore.RED, '❌')
                time.sleep(self._random_delay(3, 5))
        
        return None

    def _check_captcha_in_response(self, html):
        """Check if response contains ACTIVE captcha (only from POST response)"""
        captcha_patterns = [
            'shape captcha', 'shapecaptcha', 'ccap-card', 'shapeCaptchaBox',
            'captcha is required', 'please complete the captcha',
            'verify your identity', 'click shapes by size'
        ]
        return any(p in html.lower() for p in captcha_patterns)

    def _check_limit_in_response(self, html):
        """Check if response contains daily limit message"""
        limit_patterns = [
            'daily claim limit', 'comeback again tomorrow',
            'limit reached', 'max claims reached'
        ]
        return any(p in html.lower() for p in limit_patterns)

    def claim_faucet(self, coin, wallet):
        coin = coin.lower()
        self._log(f"Claiming {coin.upper()}...", Fore.YELLOW, '💧')
        
        for attempt in range(2):
            page = self.get_faucet_page(coin)
            if not page:
                if attempt == 0:
                    self._log("Retrying to get faucet page...", Fore.YELLOW, '🔄')
                    time.sleep(self._random_delay(3, 5))
                    continue
                return False, None, False, False
            
            csrf = page.get('csrf') or self.csrf_token
            token = page.get('token')
            
            if token:
                break
            else:
                self._log(f"Token not found, attempt {attempt+1}/2", Fore.YELLOW, '⏳')
                time.sleep(self._random_delay(3, 5))
        else:
            self._log("Token not found after retries", Fore.RED, '❌')
            return False, None, False, False
        
        data = {
            'csrf_token_name': csrf,
            'token': token,
            'wallet': wallet
        }
        url = f'{self.base_url}/faucet/verify/{coin}'
        
        try:
            headers = {
                'Origin': self.base_url,
                'Referer': f'{self.base_url}/faucet/currency/{coin.upper()}',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Dest': 'document',
                'Cache-Control': 'max-age=0',
                'Upgrade-Insecure-Requests': '1',
            }
            self.session.headers.update(headers)
            if self.ci_session:
                self.session.cookies.set('ci_session', self.ci_session)
            
            resp = self.session.post(url, data=data)
            time.sleep(self._random_delay(4, 7))
            
            self.stats['total'] += 1
            reward = None
            html = resp.text
            
            # ✅ CEK CAPTCHA dari RESPONSE POST (bukan dari halaman GET)
            if self._check_captcha_in_response(html):
                self._log(f"🚫 CAPTCHA triggered on {coin.upper()}!", Fore.RED, '🤖')
                return False, None, True, False
            
            # CEK DAILY LIMIT
            if self._check_limit_in_response(html):
                self._log(f"🚫 Daily limit reached for {coin.upper()}!", Fore.RED, '⛔')
                return False, None, False, True
            
            if resp.status_code == 200:
                success_patterns = [
                    'success', 'claim', 'reward', 'received', 
                    'added', 'credited', 'completed', 'berhasil',
                    'diterima', '✔', '✅', 'you have claimed',
                    'claim successful', 'reward claimed'
                ]
                
                is_success = any(p in html.lower() for p in success_patterns)
                has_reward = re.search(r'([\d.]+)\s*' + coin.upper(), html, re.IGNORECASE)
                has_balance = 'balance' in html.lower() or 'wallet' in html.lower()
                
                if resp.url and 'success' in resp.url.lower():
                    is_success = True
                
                if is_success or has_reward or has_balance:
                    self.stats['success'] += 1
                    if has_reward:
                        reward = f"{has_reward.group(1)} {coin.upper()}"
                    else:
                        reward = f"0.00000000 {coin.upper()}"
                    return True, reward, False, False
                    
                elif 'already' in html.lower() or 'wait' in html.lower():
                    self._log("Need to wait", Fore.YELLOW, '⏳')
                    return False, None, False, False
                else:
                    self.stats['failed'] += 1
                    self._log("Claim failed - unknown response", Fore.RED, '❌')
                    return False, None, False, False
            else:
                self.stats['failed'] += 1
                self._log(f"HTTP {resp.status_code}", Fore.RED, '❌')
                return False, None, False, False
                
        except Exception as e:
            self.stats['failed'] += 1
            self._log(f"Error: {str(e)}", Fore.RED, '❌')
            return False, None, False, False

    def get_next_coin(self):
        """Get next available coin, skip bad ones"""
        if len(self.bad_coins) >= len(self.all_coins):
            return None
        
        start_index = self.current_coin_index
        for i in range(len(self.all_coins)):
            idx = (start_index + i) % len(self.all_coins)
            coin = self.all_coins[idx]
            if coin not in self.bad_coins:
                self.current_coin_index = idx
                return coin
        
        return None

    def run_auto_claim(self, email, target):
        if not self.logged_in:
            if not self.login(email):
                self._log("Cannot start", Fore.RED, '❌')
                return
        
        print("\n" + "━"*50)
        self._log("🚀 Memulai Auto Claim...", Fore.CYAN)
        print("━"*50 + "\n")
        
        count = 0
        self.stats['start_time'] = datetime.now()
        self.bad_coins = set()
        
        # Ambil coin pertama
        current_coin = self.settings.get('coin', 'ltc').lower()
        if current_coin in self.all_coins:
            self.current_coin_index = self.all_coins.index(current_coin)
        else:
            self.current_coin_index = 0
        
        while count < target:
            coin = self.get_next_coin()
            if not coin:
                self._log("❌ All coins are blocked (limit/captcha). Stopping.", Fore.RED, '🛑')
                break
            
            self._log(f"📌 Using coin: {coin.upper()}", Fore.CYAN, '🪙')
            
            try:
                success, reward, captcha, limit = self.claim_faucet(coin, email)
                count += 1
                
                if captcha:
                    self.bad_coins.add(coin)
                    self._log(f"⚠️ {coin.upper()} blocked by CAPTCHA — switching...", Fore.RED, '🔄')
                    # Jangan hitung sebagai attempt
                    count -= 1
                    continue
                
                if limit:
                    self.bad_coins.add(coin)
                    self._log(f"⛔ {coin.upper()} daily limit reached — switching...", Fore.RED, '🔄')
                    count -= 1
                    continue
                
                if success:
                    print(f"           {Fore.GREEN}✅ Success{Style.RESET_ALL}")
                    if reward:
                        print(f"           {Fore.GREEN}💰 Reward : {reward}{Style.RESET_ALL}")
                    print(f"           {Fore.CYAN}📈 Progress : {count}/{target}{Style.RESET_ALL}")
                else:
                    print(f"           {Fore.RED}❌ Failed{Style.RESET_ALL}")
                    print(f"           {Fore.YELLOW}🔄 Retry {count}/{target}{Style.RESET_ALL}")
                
                if count < target:
                    delay = self._random_delay(6, 11)
                    print(f"\n{Fore.CYAN}⏳ Next claim : {delay:.2f}s{Style.RESET_ALL}")
                    print("━"*50 + "\n")
                    time.sleep(delay)
                    
            except KeyboardInterrupt:
                self._log("Stopped by user", Fore.YELLOW, '⏹️')
                break
            except Exception as e:
                self._log(f"Error: {str(e)}", Fore.RED, '❌')
                time.sleep(self._random_delay(8, 12))
        
        self._show_summary()

    def _show_summary(self):
        dur = datetime.now() - self.stats['start_time']
        h, rem = divmod(dur.total_seconds(), 3600)
        m, s = divmod(rem, 60)
        print("\n" + "━"*50)
        self._log("📊 Summary", Fore.CYAN)
        print(f"   Total Claims : {self.stats['total']}")
        print(f"   Successful   : {Fore.GREEN}{self.stats['success']}{Style.RESET_ALL}")
        print(f"   Failed       : {Fore.RED}{self.stats['failed']}{Style.RESET_ALL}")
        print(f"   Bad Coins    : {Fore.YELLOW}{', '.join(self.bad_coins) if self.bad_coins else 'None'}{Style.RESET_ALL}")
        print(f"   Duration     : {int(h)}h {int(m)}m {int(s)}s")
        print("━"*50 + "\n")

# ============================================================
# MENU
# ============================================================
def print_menu():
    print(f"""
{CYAN}[ 1 ] Login & Start
[ 2 ] Set Email FaucetPay
[ 3 ] Ganti User-Agent
[ 4 ] Pilih Koin Awal
[ 5 ] Keluar{RESET}
    """)

def print_claim_status(coin, target, current, delay_min, delay_max, status):
    status_color = Fore.GREEN if status == "Running" else Fore.YELLOW
    print(f"""
{CYAN}╔════════════════════════════════════════════╗
║              💰 CLAIM MODE 💰              ║
╠════════════════════════════════════════════╣
║ Coin     : {coin.upper():<30} ║
║ Target   : {current}/{target:<27} ║
║ Delay    : {delay_min} - {delay_max} Detik{ ' ' * (24 - len(str(delay_min)+str(delay_max))) }║
║ Status   : {status_color}{status:<30}{Style.RESET_ALL}{Fore.CYAN}║
╚════════════════════════════════════════════╝{RESET}
    """)

def menu_set_email(bot):
    clear_screen()
    print_banner()
    current = bot.settings.get('email', 'Not Set')
    print(f"{CYAN}Current Email: {YELLOW}{current}{RESET}\n")
    email = input(f"{YELLOW}Masukkan email FaucetPay: {RESET}").strip()
    if email:
        bot.set_email(email)
        print(f"{GREEN}✅ Email saved!{RESET}")
    else:
        print(f"{RED}Email cannot be empty.{RESET}")
    input(f"\n{CYAN}Press Enter to continue...{RESET}")

def menu_set_coin(bot):
    clear_screen()
    print_banner()
    coins = bot.config.get('coins', [])
    current = bot.settings.get('coin', 'ltc')
    print(f"{CYAN}Current Coin: {YELLOW}{current.upper()}{RESET}\n")
    print(f"{CYAN}Available coins:{RESET}")
    for i, c in enumerate(coins, 1):
        print(f"  {i}. {c.upper()}")
    try:
        choice = int(input(f"\n{YELLOW}Pilih coin awal (1-{len(coins)}): {RESET}"))
        if 1 <= choice <= len(coins):
            selected = coins[choice-1]
            bot.set_coin(selected)
            print(f"{GREEN}✅ Coin set to {selected.upper()}{RESET}")
        else:
            print(f"{RED}Invalid.{RESET}")
    except ValueError:
        print(f"{RED}Masukkan angka.{RESET}")
    input(f"\n{CYAN}Press Enter to continue...{RESET}")

def menu_set_user_agent(bot):
    clear_screen()
    print_banner()
    ua_list = bot.config.get('user_agents', [])
    current_idx = bot.settings.get('user_agent_index', 0)
    print(f"{CYAN}Current User-Agent:{RESET}")
    if 0 <= current_idx < len(ua_list):
        print(f"{YELLOW}{ua_list[current_idx]}{RESET}\n")
    else:
        print(f"{YELLOW}Default{RESET}\n")
    print(f"{CYAN}Available:{RESET}")
    for i, ua in enumerate(ua_list, 1):
        short = ua[:60] + "..." if len(ua) > 60 else ua
        print(f"  {i}. {short}")
    print(f"  0. Custom")
    try:
        choice = input(f"\n{YELLOW}Pilih (0-{len(ua_list)}): {RESET}")
        if choice == "0":
            custom = input(f"{YELLOW}Masukkan User-Agent: {RESET}").strip()
            if custom:
                ua_list.append(custom)
                bot.settings['user_agent_index'] = len(ua_list)-1
                save_settings(bot.settings)
                bot._apply_user_agent()
                print(f"{GREEN}✅ Custom applied!{RESET}")
            else:
                print(f"{RED}Invalid.{RESET}")
        else:
            idx = int(choice) - 1
            if 0 <= idx < len(ua_list):
                bot.set_user_agent_by_index(idx)
                print(f"{GREEN}✅ User-Agent changed.{RESET}")
            else:
                print(f"{RED}Invalid.{RESET}")
    except ValueError:
        print(f"{RED}Masukkan angka.{RESET}")
    input(f"\n{CYAN}Press Enter to continue...{RESET}")

def menu_login_start(bot):
    clear_screen()
    print_banner()
    email = bot.settings.get('email', '')
    if not email:
        print(f"{RED}❌ Email not set. Please set email first (Menu 2).{RESET}")
        input(f"\n{CYAN}Press Enter to continue...{RESET}")
        return
    coin = bot.settings.get('coin', 'ltc')
    target = bot.settings.get('target', 10)
    try:
        new_target = input(f"{YELLOW}Target claims (default {target}): {RESET}").strip()
        if new_target:
            target = int(new_target)
            bot.set_target(target)
    except ValueError:
        print(f"{RED}Invalid, using default.{RESET}")
    clear_screen()
    print_banner()
    print_claim_status(coin, target, 0, bot.config.get('min_delay',6), bot.config.get('max_delay',11), "Starting...")
    print("\n" + "━"*50)
    bot.run_auto_claim(email, target)
    input(f"\n{CYAN}Press Enter to continue...{RESET}")

# ============================================================
# MAIN
# ============================================================
def main():
    bot = ClaimCryptoBot()
    while True:
        clear_screen()
        print_banner()
        print_menu()
        choice = input(f"{YELLOW}➤ Pilih Menu : {RESET}").strip()
        if choice == '1':
            menu_login_start(bot)
        elif choice == '2':
            menu_set_email(bot)
        elif choice == '3':
            menu_set_user_agent(bot)
        elif choice == '4':
            menu_set_coin(bot)
        elif choice == '5':
            print(f"{GREEN}Keluar... Sampai jumpa sayang!{RESET}")
            break
        else:
            print(f"{RED}Pilihan tidak valid.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()
