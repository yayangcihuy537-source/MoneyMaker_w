#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time
import random
import re
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style
from pyfiglet import Figlet

init(autoreset=True)

# ============================================================
# KONSTANTA
# ============================================================
VERSION = "1.0"
SCRIPT_NAME = "CLAIMCRYPTO AUTO CLAIM"
BASE_URL = "https://claimcrypto.in"
CONFIG_FILE = "config.json"

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
    print(GREEN + "  💰 AUTO CLAIM • AUTO LOGIN • SMART DETECT")
    print(YELLOW + "  ⚡ Infinite Farm • Auto Switch Coin")
    print(RED + "  👨‍💻 Developer : @MoneyMaker_w")
    print(CYAN + "╚════════════════════════════════════════════════════════════╝" + RESET)

# ============================================================
# FUNGSI BANTUAN
# ============================================================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        default = {
            "email": "",
            "coin": "ltc",
            "user_agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36"
        }
        save_config(default)
        return default

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def random_delay(min_sec=6, max_sec=11):
    return random.uniform(min_sec, max_sec) + random.uniform(0, 1.5)

def log(message, color=Fore.WHITE, emoji=''):
    timestamp = datetime.now().strftime('%H:%M:%S')
    print(f"{color}[{timestamp}] {emoji} {message}{Style.RESET_ALL}")

def timer(seconds, prefix="⏳ Please wait"):
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"\r{prefix} {i}s  ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 30 + "\r")

def print_status(coin, total_claims, success, failed, bad_coins):
    print(f"\n{CYAN}📊 Status:{RESET}")
    print(f"   Coin: {YELLOW}{coin.upper()}{RESET}")
    print(f"   Total: {WHITE}{total_claims}{RESET}")
    print(f"   Success: {GREEN}{success}{RESET}")
    print(f"   Failed: {RED}{failed}{RESET}")
    print(f"   Bad Coins: {YELLOW}{', '.join(bad_coins) if bad_coins else 'None'}{RESET}")
    print("━"*50)

# ============================================================
# KELAS BOT
# ============================================================
class ClaimBot:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": config.get("user_agent", "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36"),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Cache-Control": "max-age=0",
        })
        self.logged_in = False
        self.csrf_token = None
        self.email = config.get("email", "")
        self.bad_coins = set()
        self.total_claims = 0
        self.success_claims = 0
        self.failed_claims = 0

    def get_csrf_from_home(self):
        try:
            resp = self.session.get(BASE_URL, timeout=30)
            if resp.status_code != 200:
                log("Failed to get homepage", Fore.RED, "❌")
                return None
            csrf = self.session.cookies.get('csrf_cookie_name')
            if csrf:
                return csrf
            match = re.search(r'name="csrf_token_name"\s*value="([^"]+)"', resp.text)
            if match:
                return match.group(1)
            match = re.search(r'csrf_cookie_name\s*=\s*"([^"]+)"', resp.text)
            if match:
                return match.group(1)
            return None
        except Exception as e:
            log(f"Error: {str(e)}", Fore.RED, "❌")
            return None

    def login(self, email):
        log(f"Logging in with email: {email}", Fore.CYAN, "🔑")
        csrf = self.get_csrf_from_home()
        if not csrf:
            log("Failed to get CSRF token", Fore.RED, "❌")
            return False
        self.csrf_token = csrf

        data = {
            "wallet": email,
            "csrf_token_name": csrf
        }
        headers = {
            "Origin": BASE_URL,
            "Referer": BASE_URL + "/",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        try:
            resp = self.session.post(f"{BASE_URL}/auth/login", data=data, headers=headers, timeout=30)
            if resp.status_code == 200 and ("Dashboard" in resp.text or "Earn Free" in resp.text):
                self.logged_in = True
                self.email = email
                self.config["email"] = email
                save_config(self.config)
                log("Login successful!", Fore.GREEN, "✅")
                return True
            else:
                log("Login failed - check email", Fore.RED, "❌")
                return False
        except Exception as e:
            log(f"Login error: {str(e)}", Fore.RED, "❌")
            return False

    def get_faucet_page(self, coin):
        """Get faucet page and extract token. Returns dict with status and token."""
        coin = coin.lower()
        url = f"{BASE_URL}/faucet/currency/{coin}"
        headers = {"Referer": f"{BASE_URL}/"}

        for attempt in range(3):  # retry 3 times
            try:
                resp = self.session.get(url, headers=headers, timeout=30)
                if resp.status_code != 200:
                    log(f"Failed to get faucet page: {resp.status_code}", Fore.RED, "❌")
                    continue

                html = resp.text

                # Check for captcha or limit on page
                if "captcha" in html.lower() or "i'm not a robot" in html.lower():
                    return {"status": "captcha"}
                if "daily claim limit" in html.lower() or "comeback again tomorrow" in html.lower():
                    return {"status": "limit"}

                # Extract token with multiple patterns
                token = None
                patterns = [
                    r'<input type="hidden" name="token" value="([^"]+)"',
                    r'token\s*=\s*"([^"]+)"',
                    r"token\s*=\s*'([^']+)'",
                    r'data-token="([^"]+)"',
                    r'name="token"\s*value="([^"]+)"',
                    r'var token\s*=\s*"([^"]+)"',
                ]
                for pat in patterns:
                    match = re.search(pat, html, re.IGNORECASE)
                    if match:
                        token = match.group(1)
                        break

                if token:
                    # Get CSRF
                    csrf = self.session.cookies.get('csrf_cookie_name')
                    if not csrf:
                        match = re.search(r'name="csrf_token_name"\s*value="([^"]+)"', html)
                        if match:
                            csrf = match.group(1)
                    if not csrf:
                        return {"status": "error", "msg": "CSRF not found"}
                    return {"status": "success", "token": token, "csrf": csrf}

                # If no token, maybe page is loading or showing something else
                if "please wait" in html.lower():
                    return {"status": "wait"}
                if "invalid" in html.lower():
                    return {"status": "invalid"}

                # If nothing matched, treat as unknown
                return {"status": "error", "msg": "Token not found"}

            except Exception as e:
                log(f"Error fetching page: {str(e)}", Fore.RED, "❌")
                time.sleep(2)
                continue

        return {"status": "error", "msg": "Max retries exceeded"}

    def claim_faucet(self, coin):
        coin = coin.lower()
        log(f"Claiming {coin.upper()}...", Fore.YELLOW, "💧")

        page_result = self.get_faucet_page(coin)
        status = page_result.get("status")

        if status == "captcha":
            log("Captcha detected, marking as bad", Fore.RED, "🤖")
            self.bad_coins.add(coin)
            return "captcha"
        elif status == "limit":
            log("Daily limit detected, marking as bad", Fore.YELLOW, "⛔")
            self.bad_coins.add(coin)
            return "limit"
        elif status == "wait":
            log("Page says 'please wait', retrying later", Fore.YELLOW, "⏳")
            return "wait"
        elif status == "invalid":
            log("Invalid page state, retrying", Fore.YELLOW, "⚠️")
            return "error"
        elif status == "error":
            log(f"Failed to get token: {page_result.get('msg', 'Unknown')}", Fore.RED, "❌")
            # If token not found after retries, maybe the coin is blocked temporarily
            # We'll mark it as bad after 3 consecutive errors? We'll handle in auto_farm
            return "error"
        elif status != "success":
            log(f"Unknown status: {status}", Fore.RED, "❌")
            return "error"

        token = page_result["token"]
        csrf = page_result["csrf"]

        data = {
            "csrf_token_name": csrf,
            "token": token,
            "wallet": self.email
        }
        url = f"{BASE_URL}/faucet/verify/{coin}"
        headers = {
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/faucet/currency/{coin.upper()}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        try:
            resp = self.session.post(url, data=data, headers=headers, timeout=30)
            if resp.status_code == 200:
                html = resp.text.lower()
                if "has been sent" in html or "good job" in html or "success" in html:
                    self.success_claims += 1
                    self.total_claims += 1
                    reward_match = re.search(r'([\d.]+)\s*' + coin.upper(), resp.text, re.IGNORECASE)
                    reward = reward_match.group(1) + " " + coin.upper() if reward_match else "unknown"
                    log(f"Claim successful! Reward: {reward}", Fore.GREEN, "🎉")
                    return True
                elif "daily claim limit" in html or "comeback again tomorrow" in html:
                    log("Daily limit reached for this coin", Fore.YELLOW, "⛔")
                    self.bad_coins.add(coin)
                    return "limit"
                elif "captcha" in html or "verify" in html or "robot" in html:
                    log("Captcha detected on this coin", Fore.RED, "🤖")
                    self.bad_coins.add(coin)
                    return "captcha"
                elif "sufficient funds" in html or "balance" in html:
                    log("Faucet out of funds", Fore.RED, "💰")
                    self.bad_coins.add(coin)
                    return "empty"
                elif "invalid" in html:
                    log("Invalid token or CSRF", Fore.RED, "❌")
                    return "invalid"
                elif "already" in html or "wait" in html:
                    log("Need to wait before next claim", Fore.YELLOW, "⏳")
                    return "wait"
                else:
                    self.failed_claims += 1
                    self.total_claims += 1
                    log("Claim failed - unknown response", Fore.RED, "❌")
                    return False
            else:
                self.failed_claims += 1
                self.total_claims += 1
                log(f"HTTP {resp.status_code}", Fore.RED, "❌")
                return False
        except Exception as e:
            self.failed_claims += 1
            self.total_claims += 1
            log(f"Error: {str(e)}", Fore.RED, "❌")
            return "error"

    def auto_farm(self):
        """Infinite auto claim loop until all coins blocked."""
        if not self.logged_in:
            if not self.login(self.email):
                log("Login failed. Please check email.", Fore.RED, "❌")
                return

        coin = self.config.get("coin", "ltc")
        coins = ["ltc", "doge", "dgb", "sol", "trx", "bnb", "bch", "dash", "eth", "fey", "zec", "usdt"]
        self.bad_coins = set()
        self.total_claims = 0
        self.success_claims = 0
        self.failed_claims = 0
        error_count = 0  # consecutive errors for current coin

        log(f"🚀 Starting infinite farming...", Fore.CYAN)
        log(f"📌 Starting coin: {coin.upper()}", Fore.CYAN, "🪙")
        print("\n" + "━"*50 + "\n")

        while True:
            # Check if all coins blocked
            if len(self.bad_coins) >= len(coins):
                log("❌ All coins are blocked (limit/captcha/empty). Stopping.", Fore.RED, "🛑")
                break

            # Skip bad coins
            if coin in self.bad_coins:
                start_idx = coins.index(coin) if coin in coins else 0
                found = False
                for i in range(len(coins)):
                    idx = (start_idx + i) % len(coins)
                    if coins[idx] not in self.bad_coins:
                        coin = coins[idx]
                        found = True
                        break
                if not found:
                    log("❌ No good coins left!", Fore.RED, "🛑")
                    break

            result = self.claim_faucet(coin)

            if result in ["limit", "captcha", "empty", "invalid"]:
                log(f"⚠️ {coin.upper()} blocked — switching...", Fore.RED, "🔄")
                self.bad_coins.add(coin)
                error_count = 0
                # Switch to next good coin
                try:
                    idx = coins.index(coin)
                    for i in range(1, len(coins)):
                        next_idx = (idx + i) % len(coins)
                        if coins[next_idx] not in self.bad_coins:
                            coin = coins[next_idx]
                            break
                    else:
                        log("❌ All coins blocked!", Fore.RED, "🛑")
                        break
                    log(f"Switching to {coin.upper()}", Fore.CYAN, "🔄")
                except ValueError:
                    coin = "ltc"
                continue
            elif result == "wait":
                delay = random_delay(10, 15)
                timer(int(delay), "⏳ Wait before retry")
                continue
            elif result == "error":
                error_count += 1
                # If too many errors on same coin, mark it as bad and switch
                if error_count >= 3:
                    log(f"❌ Too many errors on {coin.upper()}, switching...", Fore.RED, "🔄")
                    self.bad_coins.add(coin)
                    error_count = 0
                    # switch coin
                    try:
                        idx = coins.index(coin)
                        for i in range(1, len(coins)):
                            next_idx = (idx + i) % len(coins)
                            if coins[next_idx] not in self.bad_coins:
                                coin = coins[next_idx]
                                break
                        else:
                            log("❌ All coins blocked!", Fore.RED, "🛑")
                            break
                        log(f"Switching to {coin.upper()}", Fore.CYAN, "🔄")
                    except ValueError:
                        coin = "ltc"
                    continue
                else:
                    delay = random_delay(5, 8)
                    timer(int(delay), "⏳ Retry after")
                    continue
            elif result is True:
                error_count = 0  # reset error count on success
            else:
                # failed but not blocked, increment error count
                error_count += 1
                if error_count >= 3:
                    log(f"❌ Too many failures on {coin.upper()}, switching...", Fore.RED, "🔄")
                    self.bad_coins.add(coin)
                    error_count = 0
                    # switch coin
                    try:
                        idx = coins.index(coin)
                        for i in range(1, len(coins)):
                            next_idx = (idx + i) % len(coins)
                            if coins[next_idx] not in self.bad_coins:
                                coin = coins[next_idx]
                                break
                        else:
                            log("❌ All coins blocked!", Fore.RED, "🛑")
                            break
                        log(f"Switching to {coin.upper()}", Fore.CYAN, "🔄")
                    except ValueError:
                        coin = "ltc"
                    continue

            # Print status every 5 successful claims or total claims
            if self.total_claims % 5 == 0 and self.total_claims > 0:
                print_status(coin, self.total_claims, self.success_claims, self.failed_claims, self.bad_coins)

            delay = random_delay(6, 11)
            timer(int(delay), "⏳ Next claim in")

        # Final summary
        print("\n" + "━"*50)
        log("📊 FARMING COMPLETE", Fore.CYAN)
        print(f"   Total Claims : {self.total_claims}")
        print(f"   Successful   : {Fore.GREEN}{self.success_claims}{RESET}")
        print(f"   Failed       : {Fore.RED}{self.failed_claims}{RESET}")
        print(f"   Bad Coins    : {Fore.YELLOW}{', '.join(self.bad_coins) if self.bad_coins else 'None'}{RESET}")
        print("━"*50 + "\n")

# ============================================================
# MENU
# ============================================================
def menu_set_email(config):
    clear_screen()
    print_banner()
    current = config.get("email", "Not Set")
    print(f"{CYAN}Current Email: {YELLOW}{current}{RESET}\n")
    email = input(f"{YELLOW}Masukkan email FaucetPay: {RESET}").strip()
    if email:
        config["email"] = email
        save_config(config)
        print(f"{GREEN}✅ Email saved!{RESET}")
    else:
        print(f"{RED}Email tidak boleh kosong.{RESET}")
    input(f"\n{CYAN}Press Enter to continue...{RESET}")

def menu_select_coin(config):
    clear_screen()
    print_banner()
    coins = ["ltc", "doge", "dgb", "sol", "trx", "bnb", "bch", "dash", "eth", "fey", "zec", "usdt"]
    current = config.get("coin", "ltc")
    print(f"{CYAN}Current Coin: {YELLOW}{current.upper()}{RESET}\n")
    print(f"{CYAN}Available coins:{RESET}")
    for i, c in enumerate(coins, 1):
        print(f"  {i}. {c.upper()}")
    try:
        choice = int(input(f"\n{YELLOW}Pilih coin (1-{len(coins)}): {RESET}"))
        if 1 <= choice <= len(coins):
            selected = coins[choice-1]
            config["coin"] = selected
            save_config(config)
            print(f"{GREEN}✅ Coin set to {selected.upper()}{RESET}")
        else:
            print(f"{RED}Pilihan tidak valid.{RESET}")
    except ValueError:
        print(f"{RED}Masukkan angka.{RESET}")
    input(f"\n{CYAN}Press Enter to continue...{RESET}")

def menu_start_farming(config):
    clear_screen()
    print_banner()
    if not config.get("email"):
        print(f"{RED}❌ Email belum di set. Menu 2 dulu.{RESET}")
        input(f"\n{CYAN}Press Enter to continue...{RESET}")
        return

    bot = ClaimBot(config)
    bot.auto_farm()
    input(f"\n{CYAN}Press Enter to continue...{RESET}")

def main():
    config = load_config()
    while True:
        clear_screen()
        print_banner()
        print(f"""
{CYAN}[ 1 ] Start Farming (Infinite)
[ 2 ] Set Email (FaucetPay)
[ 3 ] Select Coin
[ 0 ] Exit{RESET}
        """)
        choice = input(f"{YELLOW}➤ Pilih Menu : {RESET}").strip()
        if choice == "1":
            menu_start_farming(config)
        elif choice == "2":
            menu_set_email(config)
        elif choice == "3":
            menu_select_coin(config)
        elif choice == "0":
            print(f"{GREEN}Keluar... Sampai jumpa sayang!{RESET}")
            break
        else:
            print(f"{RED}Pilihan tidak valid.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()
