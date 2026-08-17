#!/usr/bin/env python3
"""
RENDERCOINS USDT FAUCET BOT
AUTO FARM • AUTO LOGIN • AUTO CLAIM
"""

import os
import sys
import time
import json
import re
import requests

# Warna ANSI
class Colors:
    GREEN = '\033[92m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

CONFIG_FILE = "rendercoins_config.json"
BASE_URL = "https://rendercoins.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class RenderCoinsBot:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'id,en-US;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': BASE_URL,
            'Referer': BASE_URL + '/'
        }
        self.email = None
        self.logged_in = False
        self.total_earned = 0.0
        self.last_amount = 0.0
        self.claim_count = 0
        self.success_count = 0
        self.start_time = None
        self.load_config()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self.email = data.get('email', '')
            except:
                pass

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({'email': self.email}, f, indent=2)

    def set_email(self):
        print(f"\n{Colors.CYAN}📧 Masukkan email FaucetPay:{Colors.RESET}")
        email = input("➜ ").strip()
        if email and '@' in email and '.' in email:
            self.email = email
            self.save_config()
            print(f"{Colors.GREEN}✅ Email tersimpan: {email}{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ Email tidak valid!{Colors.RESET}")

    def login(self):
        if not self.email:
            print(f"{Colors.RED}❌ Email belum diatur. Gunakan menu 2 dulu.{Colors.RESET}")
            return False

        print(f"{Colors.CYAN}🔐 Logging in as {self.email}...{Colors.RESET}", end=" ")
        try:
            self.session = requests.Session()
            self.session.headers.update(self.headers)

            response = self.session.get(f"{BASE_URL}/", headers=self.headers)
            csrf = response.cookies.get('csrf_cookie_name')
            if not csrf:
                print(f"{Colors.RED}❌ No CSRF token{Colors.RESET}")
                return False

            login_url = f"{BASE_URL}/auth/login"
            data = {'wallet': self.email, 'csrf_token_name': csrf}
            response = self.session.post(login_url, data=data, headers=self.headers, allow_redirects=False)

            if response.status_code in [303, 302]:
                redirect = response.headers.get('location')
                if redirect:
                    self.session.get(redirect, headers=self.headers)
                    self.logged_in = True
                    print(f"{Colors.GREEN}✅ SUCCESS{Colors.RESET}")
                    return True

            print(f"{Colors.RED}❌ FAILED (Status: {response.status_code}){Colors.RESET}")
            return False

        except Exception as e:
            print(f"{Colors.RED}❌ ERROR: {e}{Colors.RESET}")
            return False

    def extract_tokens(self, html):
        tokens = {}

        form_pattern = r'<form[^>]*id="verify"[^>]*>(.*?)</form>'
        form_match = re.search(form_pattern, html, re.DOTALL | re.IGNORECASE)

        if not form_match:
            form_pattern = r'<form[^>]*action="[^"]*faucet/verify[^"]*"[^>]*>(.*?)</form>'
            form_match = re.search(form_pattern, html, re.DOTALL | re.IGNORECASE)

        if form_match:
            form_html = form_match.group(1)
            input_pattern = r'<input[^>]*name="([^"]+)"[^>]*value="([^"]+)"[^>]*>'
            inputs = re.findall(input_pattern, form_html, re.IGNORECASE)
            for name, value in inputs:
                if name in ['auto_faucet_token', 'csrf_token_name', 'token']:
                    tokens[name] = value

        if not tokens.get('auto_faucet_token'):
            patterns = {
                'auto_faucet_token': [
                    r'name="auto_faucet_token"\s+value="([^"]+)"',
                    r'auto_faucet_token.*?value=["\']([^"\']+)',
                    r'auto_faucet_token["\']?\s*[:=]\s*["\']([^"\']+)'
                ],
                'csrf_token_name': [
                    r'name="csrf_token_name"\s+value="([^"]+)"',
                    r'csrf_token_name.*?value=["\']([^"\']+)',
                    r'csrf_token_name["\']?\s*[:=]\s*["\']([^"\']+)'
                ],
                'token': [
                    r'name="token"\s+value="([^"]+)"',
                    r'token.*?value=["\']([^"\']+)',
                    r'token["\']?\s*[:=]\s*["\']([^"\']+)'
                ]
            }
            for key, pattern_list in patterns.items():
                for pattern in pattern_list:
                    match = re.search(pattern, html, re.IGNORECASE)
                    if match:
                        tokens[key] = match.group(1)
                        break

        timer_match = re.search(r'let timer = (\d+)', html)
        tokens['timer'] = int(timer_match.group(1)) if timer_match else 30

        amount_patterns = [
            r'get\s+([\d.]+)\s*USDT',
            r'([\d.]+)\s*USDT\s*</div>',
            r'class="[^"]*text-info[^"]*">([\d.]+)'
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                tokens['amount'] = float(match.group(1))
                break
        if 'amount' not in tokens:
            tokens['amount'] = 0.00001101

        return tokens

    def claim_faucet(self):
        try:
            faucet_url = f"{BASE_URL}/faucet/currency/usdt"
            response = self.session.get(faucet_url, headers=self.headers)
            if response.status_code != 200:
                return False

            tokens = self.extract_tokens(response.text)
            if not tokens.get('auto_faucet_token'):
                with open("debug_faucet.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                return False

            claim_amount = tokens.get('amount', 0.00001101)
            wait_time = tokens.get('timer', 30)

            spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
            for i in range(wait_time, 0, -1):
                for s in spinner:
                    sys.stdout.write(f"\r{Colors.YELLOW}⏳ {s} Waiting {i}s{Colors.RESET}")
                    sys.stdout.flush()
                    time.sleep(0.05)
            sys.stdout.write("\r" + " " * 30 + "\r")
            sys.stdout.flush()

            verify_url = f"{BASE_URL}/faucet/verify/usdt"
            data = {
                'auto_faucet_token': tokens['auto_faucet_token'],
                'csrf_token_name': tokens['csrf_token_name'],
                'token': tokens['token']
            }
            response = self.session.post(verify_url, data=data, headers=self.headers, allow_redirects=True)

            if response.status_code in [200, 303, 302]:
                if "success" in response.text.lower() or "claimed" in response.text.lower():
                    self.last_amount = claim_amount
                    self.total_earned += claim_amount
                    return True
                elif response.status_code in [303, 302]:
                    self.last_amount = claim_amount
                    self.total_earned += claim_amount
                    return True
            return False

        except Exception as e:
            return False

    def run_farm(self):
        if not self.logged_in:
            if not self.login():
                print(f"{Colors.RED}❌ Gagal login. Periksa email dan koneksi.{Colors.RESET}")
                return

        print(f"{Colors.GREEN}🚀 Starting auto claim{Colors.RESET}")
        print("=" * 55)
        self.start_time = time.time()
        consecutive_fails = 0

        while True:
            try:
                self.claim_count += 1
                success = self.claim_faucet()

                if success:
                    consecutive_fails = 0
                    self.success_count += 1
                    elapsed = time.time() - self.start_time
                    hours = elapsed / 3600
                    rate = self.total_earned / hours if hours > 0 else 0
                    rate_str = f"{rate:.8f}" if rate < 1 else f"{rate:.4f}"
                    print(f"{Colors.GREEN}✅{Colors.RESET} #{self.claim_count:3d} | "
                          f"+{self.last_amount:.8f} | "
                          f"Total: {self.total_earned:.8f} | "
                          f"Rate: {rate_str}/h")
                else:
                    consecutive_fails += 1
                    print(f"{Colors.RED}❌{Colors.RESET} #{self.claim_count:3d} | Failed (attempt {consecutive_fails})")
                    if consecutive_fails >= 3:
                        print(f"{Colors.YELLOW}  🔄 Re-login...{Colors.RESET}")
                        self.logged_in = False
                        time.sleep(2)
                        self.login()
                        consecutive_fails = 0
                        continue
                    time.sleep(5)
                    continue

                # Countdown 30 detik
                for i in range(30, 0, -1):
                    sys.stdout.write(f"\r{Colors.CYAN}⏳ Next claim in {i:2d}s{Colors.RESET}")
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write("\r" + " " * 25 + "\r")
                sys.stdout.flush()

            except KeyboardInterrupt:
                self.print_summary()
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")
                time.sleep(10)

    def print_summary(self):
        print("\n" + "=" * 55)
        print(f"{Colors.BOLD}{Colors.PURPLE}📊 FINAL STATISTICS{Colors.RESET}")
        print("=" * 55)
        print(f"{Colors.CYAN}📧 Email       : {Colors.WHITE}{self.email}{Colors.RESET}")
        print(f"{Colors.CYAN}📌 Claims      : {Colors.WHITE}{self.claim_count}{Colors.RESET}")
        print(f"{Colors.CYAN}✅ Success     : {Colors.GREEN}{self.success_count}{Colors.RESET}")
        print(f"{Colors.CYAN}❌ Failed      : {Colors.RED}{self.claim_count - self.success_count}{Colors.RESET}")

        if self.claim_count > 0:
            rate = self.success_count / self.claim_count * 100
            print(f"{Colors.CYAN}📈 Success rate: {Colors.WHITE}{rate:.1f}%{Colors.RESET}")

        print(f"{Colors.CYAN}💰 Total earned: {Colors.GREEN}{self.total_earned:.8f} USDT{Colors.RESET}")

        if self.success_count > 0:
            avg = self.total_earned / self.success_count
            print(f"{Colors.CYAN}📊 Average     : {Colors.WHITE}{avg:.8f} USDT/claim{Colors.RESET}")
            elapsed = time.time() - self.start_time
            hours = elapsed / 3600
            if hours > 0:
                per_hour = self.total_earned / hours
                per_day = per_hour * 24
                per_month = per_day * 30
                print(f"\n{Colors.PURPLE}📈 ESTIMASI PENDAPATAN{Colors.RESET}")
                print(f"   {Colors.CYAN}Per jam  : {Colors.GREEN}{per_hour:.8f} USDT{Colors.RESET}")
                print(f"   {Colors.CYAN}Per hari : {Colors.GREEN}{per_day:.6f} USDT{Colors.RESET}")
                print(f"   {Colors.CYAN}Per bulan: {Colors.GREEN}{per_month:.6f} USDT{Colors.RESET}")
                usd_to_idr = 15500
                print(f"\n{Colors.PURPLE}💰 ESTIMASI RUPIAH (kurs Rp{usd_to_idr}){Colors.RESET}")
                print(f"   {Colors.CYAN}Per jam  : {Colors.GREEN}Rp{per_hour * usd_to_idr:,.2f}{Colors.RESET}")
                print(f"   {Colors.CYAN}Per hari : {Colors.GREEN}Rp{per_day * usd_to_idr:,.2f}{Colors.RESET}")
                print(f"   {Colors.CYAN}Per bulan: {Colors.GREEN}Rp{per_month * usd_to_idr:,.2f}{Colors.RESET}")
        print("=" * 55)

    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""{Colors.PURPLE}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   ██████╗ ███████╗███╗   ██╗██████╗ ███████╗██████╗        ║
║   ██╔══██╗██╔════╝████╗  ██║██╔══██╗██╔════╝██╔══██╗       ║
║   ██████╔╝█████╗  ██╔██╗ ██║██║  ██║█████╗  ██████╔╝       ║
║   ██╔══██╗██╔══╝  ██║╚██╗██║██║  ██║██╔══╝  ██╔══██╗       ║
║   ██║  ██║███████╗██║ ╚████║██████╔╝███████╗██║  ██║       ║
║   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝ ╚══════╝╚═╝  ╚═╝       ║
║                                                              ║
║           ⚡ RENDERCOINS AUTO CLAIM BOT ⚡                  ║
║              USDT FAUCET - AUTO CLAIM 30S                  ║
║                                                              ║
║                  {Colors.YELLOW}by @japarkiding{Colors.PURPLE}                          ║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
        """)

    def main_menu(self):
        while True:
            self.banner()
            if self.email:
                print(f"\n{Colors.GREEN}📧 Email saat ini: {self.email}{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}📧 Email belum diatur!{Colors.RESET}")
            print(f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════╗
║   {Colors.WHITE}[{Colors.GREEN}1{Colors.WHITE}] {Colors.GREEN}Start Farming USDT                         {Colors.CYAN}║
║   {Colors.WHITE}[{Colors.YELLOW}2{Colors.WHITE}] {Colors.YELLOW}Set Email FaucetPay                        {Colors.CYAN}║
║   {Colors.WHITE}[{Colors.RED}0{Colors.WHITE}] {Colors.RED}Exit                                        {Colors.CYAN}║
╚══════════════════════════════════════════════════════════════╝{Colors.RESET}
""")
            choice = input(f"{Colors.CYAN}❯ Pilih menu: {Colors.RESET}").strip()

            if choice == '1':
                self.run_farm()
                input(f"\n{Colors.DIM}Tekan Enter untuk kembali ke menu...{Colors.RESET}")
            elif choice == '2':
                self.set_email()
                input(f"\n{Colors.DIM}Tekan Enter untuk kembali ke menu...{Colors.RESET}")
            elif choice == '0':
                print(f"{Colors.RED}👋 Keluar.{Colors.RESET}")
                sys.exit(0)
            else:
                print(f"{Colors.RED}❌ Pilihan tidak valid{Colors.RESET}")
                time.sleep(1)

if __name__ == "__main__":
    try:
        bot = RenderCoinsBot()
        bot.main_menu()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}👋 Keluar.{Colors.RESET}")
        sys.exit(0)

