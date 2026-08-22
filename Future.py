#!/usr/bin/env python3
"""
CryptoFuture Auto Claim Bot v13 - Final Fix (Retry + Cooldown)
Dev: ScriptyXSou
"""

import requests
import time
import re
import json
import base64
import hashlib
import random
import string
import sys

# ======================== ANSI COLORS ========================
GREEN = '\033[92m'
YELLOW = '\033[93m'
ORANGE = '\033[38;5;214m'
ORANGE2 = '\033[38;5;208m'
CYAN = '\033[96m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

# ======================== BANNER ========================
def print_banner():
    try:
        import pyfiglet
        ascii_banner = pyfiglet.figlet_format("CryptoFuture", font="slant")
        print(ORANGE + BOLD + ascii_banner + RESET)
    except ImportError:
        print(ORANGE + BOLD + """
   ______               __  __ _             _             
  / ____/___  _________/ /_/ /(_)___  ____ _(_)___ ___   __
 / /   / __ \\/ ___/ __  __/ // / __ \\/ __ `/ / __ `__ \\ / /
/ /___/ /_/ / /  / /_/ / / // / / / / /_/ / / / / / / /_/ 
\\____/\\____/_/   \\__,_/ /_/_/_/ /_/\\__, /_/_/ /_/ /_/\\__, /  
                                  /____/             /____/   
        """ + RESET)
    
    print(ORANGE2 + "       dev: ScriptyXSou" + RESET)
    print()
    print(ORANGE + "~" * 50 + RESET)
    print()

# ======================== BOT ========================

class CryptoFutureBot:
    def __init__(self, email, max_claims=100):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-Ch-Ua': '"Chromium";v="127", "Not)A;Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://cryptofuture.co.in/',
            'Origin': 'https://cryptofuture.co.in',
        })
        self.base_url = 'https://cryptofuture.co.in'
        self.email = email
        self.device_token = None
        self.csrf_token = None
        self.fp_hash = None
        self.smart_token = None
        self.earn_ticket = None
        self.token = None
        self.balance = 0
        self.success_count = 0
        self.max_claims = max_claims
        self.last_reward = 0
        self.retry_count = 0
        
    # ---------- Extraction Helpers ----------
    def _extract_csrf(self, html):
        match = re.search(r'name="csrf_token_name"[^>]*value="([a-f0-9]+)"', html)
        if match:
            return match.group(1)
        match = re.search(r"name=['\"]csrf_token_name['\"][^>]*value=['\"]([a-f0-9]+)['\"]", html)
        if match:
            return match.group(1)
        match = re.search(r'csrf_token_name=([a-f0-9]+)', html)
        if match:
            return match.group(1)
        return None
    
    def _extract_token(self, html):
        match = re.search(r'name="token"[^>]*value="([A-Za-z0-9]+)"', html)
        if match:
            return match.group(1)
        return None
    
    def _extract_earn_ticket(self, html):
        match = re.search(r'name="earn_ticket"[^>]*value="([a-f0-9]+)"', html)
        if match:
            return match.group(1)
        return None
    
    def _extract_wallet(self, html):
        match = re.search(r'name="wallet"[^>]*value="([^"]+)"', html)
        if match:
            return match.group(1)
        return None
    
    def _extract_balance(self, html):
        patterns = [
            r'balance-amount[^>]*>\s*(\d+)\s*<span',
            r'balance-amount[^>]*>.*?(\d+)\s*<span',
            r'TOTAL BALANCE.*?(\d+)\s*Coins',
            r'balance-amount">\s*([\d,]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.DOTALL)
            if match:
                return int(match.group(1).replace(',', ''))
        return None
    
    def _extract_reward(self, html):
        match = re.search(r'(\d+)\s*Coins\s*has been added', html)
        if match:
            return int(match.group(1))
        match = re.search(r'\+\s*(\d+)\s*Coins', html)
        if match:
            return int(match.group(1))
        return None
    
    def _extract_timer(self, html):
        match = re.search(r'Next claim available in:\s*<span[^>]*>(\d+)</span>m\s*<span[^>]*>(\d+)</span>s', html)
        if match:
            return int(match.group(1)) * 60 + int(match.group(2))
        match = re.search(r'Next claim available in:\s*<span[^>]*>(\d+)</span>s', html)
        if match:
            return int(match.group(1))
        return 0
    
    # ---------- Token Generation ----------
    def _generate_device_token(self):
        if not self.device_token:
            self.device_token = 'dev_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=14)) + str(int(time.time() * 1000))
        return self.device_token
    
    def _generate_fp_hash(self):
        raw = f'fp-{self.session.headers["User-Agent"]}'
        raw += '384x832'
        return hashlib.sha256(raw.encode()).hexdigest()
    
    def _generate_smart_token(self):
        moves = random.randint(3, 15)
        data = {
            'ts': int(time.time() * 1000),
            'cpu': 8,
            'mem': 8,
            'w': 384,
            'h': 832,
            'touch': 5,
            'moves': moves
        }
        encoded = base64.b64encode(json.dumps(data).encode()).decode()
        return encoded
    
    # ---------- Balance Fetch ----------
    def get_balance(self):
        resp = self.session.get(self.base_url + '/dashboard')
        if resp.status_code != 200:
            resp = self.session.get(self.base_url + '/earn')
        if resp.status_code != 200:
            return None
        return self._extract_balance(resp.text)
    
    # ---------- Login ----------
    def login(self):
        print(f'[+] Logging in as: {self.email}')
        
        resp = self.session.get(self.base_url + '/')
        if resp.status_code != 200:
            print(RED + '[-] Failed to get homepage, status:' + RESET, resp.status_code)
            return False
        
        csrf = self._extract_csrf(resp.text)
        if not csrf:
            print(RED + '[-] CSRF not found in homepage' + RESET)
            print('[DEBUG] HTML snippet (first 1000 chars):')
            print(resp.text[:1000])
            return False
        
        self.csrf_token = csrf
        self.device_token = self._generate_device_token()
        
        login_data = {
            'wallet': self.email,
            'csrf_token_name': self.csrf_token,
            'device_token': self.device_token
        }
        
        resp = self.session.post(self.base_url + '/auth/login', data=login_data)
        if resp.status_code != 200:
            print(RED + '[-] Login failed, status:' + RESET, resp.status_code)
            return False
        
        if 'Login Success' in resp.text or '/dashboard' in resp.text or 'Dashboard' in resp.text:
            print(GREEN + '[✓] Login success!' + RESET)
            balance = self.get_balance()
            if balance is not None:
                self.balance = balance
                print(f'[+] Current balance: {self.balance} Coins')
            else:
                print(YELLOW + '[!] Could not fetch balance' + RESET)
            return True
        else:
            print(RED + '[-] Login failed - no success message' + RESET)
            return False
    
    # ---------- Get Fresh Form ----------
    def get_fresh_form(self):
        resp = self.session.get(self.base_url + '/earn')
        if resp.status_code != 200:
            return None, None, None, None, None
        
        html = resp.text
        csrf = self._extract_csrf(html)
        token = self._extract_token(html)
        earn_ticket = self._extract_earn_ticket(html)
        wallet = self._extract_wallet(html)
        
        return html, csrf, token, earn_ticket, wallet
    
    # ---------- Claim ----------
    def claim(self):
        # Get fresh form
        html, csrf, token, earn_ticket, wallet = self.get_fresh_form()
        if not all([csrf, token, earn_ticket, wallet]):
            print(RED + '[-] Missing required fields' + RESET)
            print(f'    csrf: {csrf}, token: {token}, earn_ticket: {earn_ticket}, wallet: {wallet}')
            return False
        
        # Check cooldown
        timer = self._extract_timer(html)
        if timer > 0:
            print(YELLOW + f'[⏳] Cooldown active: {timer} seconds remaining' + RESET)
            return timer
        
        self.csrf_token = csrf
        self.token = token
        self.earn_ticket = earn_ticket
        self.fp_hash = self._generate_fp_hash()
        self.smart_token = self._generate_smart_token()
        
        claim_data = {
            'csrf_token_name': self.csrf_token,
            'token': self.token,
            'earn_ticket': self.earn_ticket,
            'fp_hash': self.fp_hash,
            'confirm_wallet': '',
            'wallet': wallet,
            'smart_token': self.smart_token,
            'captcha': 'smartcaptcha'
        }
        
        resp = self.session.post(self.base_url + '/faucet/earn', data=claim_data, allow_redirects=False)
        
        if resp.status_code == 303:
            location = resp.headers.get('Location')
            if location:
                resp = self.session.get(location)
            else:
                resp = self.session.get(self.base_url + '/faucet/earn')
        
        html = resp.text
        
        # ===== DETEKSI SUKSES =====
        is_success = any(kw in html.lower() for kw in ['success', 'coins has been added'])
        if is_success or 'Success!' in html:
            reward = self._extract_reward(html)
            if reward is None:
                reward = 10
            self.last_reward = reward
            self.success_count += 1
            balance = self._extract_balance(html)
            if balance is not None:
                self.balance = balance
            else:
                bal = self.get_balance()
                if bal is not None:
                    self.balance = bal
            return True
        
        # ===== DETEKSI FAILED! =====
        if 'Failed!' in html or 'Please try again' in html:
            print(YELLOW + '[!] Got "Failed!" response, refreshing form and retrying...' + RESET)
            # Ambil form baru
            html2, csrf2, token2, earn_ticket2, wallet2 = self.get_fresh_form()
            if all([csrf2, token2, earn_ticket2, wallet2]):
                self.csrf_token = csrf2
                self.token = token2
                self.earn_ticket = earn_ticket2
                self.fp_hash = self._generate_fp_hash()
                self.smart_token = self._generate_smart_token()
                
                claim_data2 = {
                    'csrf_token_name': self.csrf_token,
                    'token': self.token,
                    'earn_ticket': self.earn_ticket,
                    'fp_hash': self.fp_hash,
                    'confirm_wallet': '',
                    'wallet': wallet2,
                    'smart_token': self.smart_token,
                    'captcha': 'smartcaptcha'
                }
                
                resp2 = self.session.post(self.base_url + '/faucet/earn', data=claim_data2, allow_redirects=False)
                if resp2.status_code == 303:
                    loc = resp2.headers.get('Location')
                    if loc:
                        resp2 = self.session.get(loc)
                    else:
                        resp2 = self.session.get(self.base_url + '/faucet/earn')
                
                html2 = resp2.text
                if any(kw in html2.lower() for kw in ['success', 'coins has been added']) or 'Success!' in html2:
                    reward2 = self._extract_reward(html2)
                    if reward2 is None:
                        reward2 = 10
                    self.last_reward = reward2
                    self.success_count += 1
                    bal2 = self._extract_balance(html2)
                    if bal2 is not None:
                        self.balance = bal2
                    return True
                else:
                    # Retry gagal, kemungkinan cooldown / rate limit
                    print(YELLOW + '[!] Retry failed, assuming cooldown (30s)...' + RESET)
                    return 30
            else:
                print(YELLOW + '[!] Could not refresh form, assuming cooldown (30s)...' + RESET)
                return 30
        
        # ===== COOLDOWN =====
        if 'Please Wait' in html:
            timer = self._extract_timer(html)
            if timer > 0:
                print(YELLOW + f'[⏳] Cooldown active: {timer} seconds remaining' + RESET)
                return timer
            else:
                print(YELLOW + '[!] "Please Wait" but no timer found, assuming 30s cooldown' + RESET)
                return 30
        
        if 'already claimed' in html.lower():
            print(YELLOW + '[!] Already claimed, checking timer...' + RESET)
            timer = self._extract_timer(html)
            if timer > 0:
                return timer
            else:
                print(YELLOW + '[!] No timer found, waiting 60s' + RESET)
                return 60
        
        # ===== UNKNOWN =====
        print(RED + '[-] Claim failed, unexpected response' + RESET)
        with open('claim_response.html', 'w', encoding='utf-8') as f:
            f.write(html)
        return False
    
    # ---------- Run Loop ----------
    def run(self, interval=12):
        print('='*50)
        print(' CryptoFuture Auto Claim Bot v13 (Retry Fix)')
        print(f' Email: {self.email}')
        print(f' Interval: {interval} seconds')
        print(f' Max claims: {self.max_claims}')
        print('='*50)
        
        if not self.login():
            print(RED + '[-] Login failed, exit' + RESET)
            return
        
        print(GREEN + '[✓] Login successful, starting claim loop...' + RESET)
        print('-'*50)
        
        claim_count = 0
        while self.success_count < self.max_claims:
            try:
                claim_count += 1
                time_str = time.strftime("%H:%M:%S")
                print(f'\n{CYAN}[{claim_count:02d}] 🕐 Claim attempt at {time_str}{RESET}')
                print(f'[+] 💰 Current balance : {self.balance} Coins')
                print(f'[+] 📊 Successful      : {self.success_count}/{self.max_claims}')
                print(f'[>] ⚡ Attempting to claim...')
                
                result = self.claim()
                
                if result is True:
                    print(GREEN + f'[✓] 🎉 Claim success!' + RESET)
                    print(f'[+] 🎁 Reward         : +{self.last_reward} Coins')
                    print(f'[+] 💰 New balance    : {self.balance} Coins')
                    print(GREEN + '[✓] Claim completed successfully' + RESET)
                elif isinstance(result, int) and result > 0:
                    print(YELLOW + f'[⏳] Waiting {result} seconds before next attempt' + RESET)
                    time.sleep(result + 2)
                    continue
                elif result is False:
                    print(RED + '[-] Claim failed, will retry after interval' + RESET)
                
                if self.success_count >= self.max_claims:
                    print(f'\n{GREEN}[✓] Reached maximum claims ({self.max_claims}). Stopping bot.{RESET}')
                    break
                
                print(f'{ORANGE}[⏳] Waiting {interval} seconds...{RESET}')
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print('\n[!] Stopped by user')
                break
            except Exception as e:
                print(RED + f'[-] Error: {e}' + RESET)
                time.sleep(interval)
        
        print(f'\n{GREEN}[✓] Bot finished. Total successful claims: {self.success_count}{RESET}')


# ======================== MAIN ========================
if __name__ == '__main__':
    print_banner()
    
    # Interactive input
    print(ORANGE + "Masukkan email FaucetPay Anda:" + RESET)
    email = input("Email: ").strip()
    if not email:
        print("[-] Email tidak boleh kosong. Keluar.")
        sys.exit(1)
    
    try:
        interval = int(input("Interval claim (detik, default 12): ").strip() or "12")
    except ValueError:
        interval = 12
    
    try:
        max_claims = int(input("Maksimum claim (default 100): ").strip() or "100")
    except ValueError:
        max_claims = 100
    
    print(ORANGE + f"\n[+] Email: {email}" + RESET)
    print(ORANGE + f"[+] Interval: {interval} detik" + RESET)
    print(ORANGE + f"[+] Max claims: {max_claims}" + RESET)
    print()
    
    bot = CryptoFutureBot(email, max_claims)
    bot.run(interval)
