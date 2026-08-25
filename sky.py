#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import time
import random
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore, Style

# ============================================================
# COLOR & INIT
# ============================================================
init(autoreset=True)

G = Fore.GREEN + Style.BRIGHT
Y = Fore.YELLOW + Style.BRIGHT
R = Fore.RED + Style.BRIGHT
C = Fore.CYAN + Style.BRIGHT
M = Fore.MAGENTA + Style.BRIGHT
W = Fore.WHITE + Style.BRIGHT
D = Fore.BLACK + Style.BRIGHT
RESET = Style.RESET_ALL


# ============================================================
# UI FUNCTIONS
# ============================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def line(char="=", width=56, color=G):
    print(f"{color}{char * width}{RESET}")

def title(text, width=56):
    line("=")
    print(f"{Y}{text.center(width)}{RESET}")
    line("=")

def print_banner():
    clear_screen()
    line("=")
    print(f"{Y}{':: SKYFREECOINS AUTO CLAIM ::'.center(56)}{RESET}")
    print(f"{C}{'AUTO FAUCET BOT'.center(56)}{RESET}")
    line("=")
    print()
    print(f"{C}  [+] Mode      : {W}Auto Faucet Claim{RESET}")
    print(f"{C}  [+] Captcha   : {G}Math Solver (Auto){RESET}")
    print(f"{C}  [+] Website   : {W}skyfreecoins.top{RESET}")
    print()
    line("-", 56, G)
    print()

def print_setup():
    title(":: SETUP ::")
    print()
    print(f"{C}  [01] {W}Login ke skyfreecoins.top via browser{RESET}")
    print(f"{C}  [02] {W}Buka DevTools → Application → Cookies{RESET}")
    print(f"{C}  [03] {W}Copy semua cookie (format: key1=value1; key2=value2){RESET}")
    print(f"{C}  [04] {W}Tempelkan di sini{RESET}")
    print()
    line("-", 56, G)
    print()

def setup_input():
    return input(f"{C}  >> Cookie : {W}").strip()

def continue_input():
    return input(f"{C}  >> Press Enter to continue... {W}")

def print_session_valid(username=None, balance=None):
    print()
    title(":: SESSION ::")
    print()
    print(f"{C}  Status  : {G}✓ VALID{RESET}")
    if username:
        print(f"{C}  User    : {W}{username}{RESET}")
    if balance is not None:
        print(f"{C}  Balance : {G}${balance:.7f}{RESET}")
    print()
    line()

def print_session_invalid():
    print()
    title(":: SESSION ::")
    print()
    print(f"{R}  [✗] Session tidak valid.{RESET}")
    print(f"{Y}      Cek kembali cookie.{RESET}")
    print()
    line()

def print_limits(claims_left, total_claims, reward_per_claim):
    print()
    title(":: LIMITS ::")
    print()
    print(f"{C}  Claims Left : {Y}{claims_left} / {total_claims}{RESET}")
    print(f"{C}  Reward      : {G}{reward_per_claim} USD{RESET}")
    print()
    line()

def print_task(captcha_question):
    print()
    title(":: CAPTCHA ::")
    print()
    print(f"{C}  Question : {W}{captcha_question}{RESET}")
    print()
    line("-", 56, G)

def show_progress(total, width=20):
    if total <= 0:
        return
    for rem in range(total, -1, -1):
        pct = int(((total - rem) / total) * 100) if total > 0 else 100
        filled = int(width * pct / 100)
        empty = width - filled
        bar = f"{G}━" * filled + f"{D}─" * empty
        sys.stdout.write(f"\r  {C}[{bar}{C}] {W}{pct:3d}% {Y}⏱ {rem:02d}s{RESET}")
        sys.stdout.flush()
        if rem > 0:
            time.sleep(1)
    print()

def print_success(reward, balance, claims_left):
    print()
    print(f"{G}  [✓] CLAIM SUCCESSFUL{RESET}")
    print(f"{C}      Reward  : {G}+{reward:.5f} USD{RESET}")
    if balance is not None:
        print(f"{C}      Balance : {W}${balance:.7f}{RESET}")
    print(f"{C}      Left    : {Y}{claims_left} claims{RESET}")
    print()
    line("-", 56, G)

def print_error(message):
    print()
    print(f"{R}  [✗] {message}{RESET}")
    print()

def print_warning(message):
    print()
    print(f"{Y}  [!] {message}{RESET}")
    print()

def show_cooldown(seconds):
    for rem in range(seconds, 0, -1):
        mins, secs = divmod(rem, 60)
        sys.stdout.write(f"\r  {Y}[!] Cooldown : {W}{mins:02d}:{secs:02d}{RESET}   ")
        sys.stdout.flush()
        time.sleep(1)
    print()

def print_finished(completed, earned, balance):
    print()
    title(":: EXECUTION FINISHED ::")
    print()
    print(f"{C}  Claims Completed : {G}{completed}{RESET}")
    print(f"{C}  Total Earned     : {G}+${earned:.5f} USD{RESET}")
    if balance is not None:
        print(f"{C}  Current Balance  : {W}${balance:.7f} USD{RESET}")
    print()
    line()

def print_footer():
    print()
    line("-", 56, G)
    print(f"{D}{'SKYFREECOINS • AUTO CLAIM'.center(56)}{RESET}")
    line("=")


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def parse_cookie_string(cookie_str):
    cookies = {}
    if not cookie_str:
        return cookies
    for item in cookie_str.split(';'):
        if '=' in item:
            key, val = item.strip().split('=', 1)
            cookies[key] = val
    return cookies

def random_delay(min_sec=1.0, max_sec=4.0):
    delay = random.uniform(min_sec, max_sec)
    print(f"{D}⏳ Pause {delay:.1f}s{RESET}")
    time.sleep(delay)

def fetch_dashboard(session, headers):
    """Get dashboard to extract balance and username."""
    try:
        resp = session.get("https://skyfreecoins.top/dashboard", headers=headers, timeout=30)
        if resp.status_code != 200:
            return None, None
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Find username from navbar: <span key="t-henry">Garapan</span>
        user_span = soup.find('span', {'key': 't-henry'})
        username = user_span.get_text(strip=True) if user_span else "Unknown"
        # Find balance: in the "stat-card" inside "dashboard-box"
        # The balance appears in a card: <h5>0</h5> but that might be zero if not loaded? Actually the dashboard shows "Balance" with a number.
        # The page shows: <p>Balance</p><h5>0</h5> but that seems to be the balance. However in the log, the balance is 0.01241 USD in the "Total Earned" but not the main balance.
        # Let's search for "Total Earned" or "Balance" followed by a number.
        balance = None
        # Try to find the balance from the stat cards
        stat_cards = soup.find_all('div', class_='stat-card')
        for card in stat_cards:
            label = card.find('p')
            if label and 'Balance' in label.get_text():
                val = card.find('h5')
                if val:
                    bal_text = val.get_text(strip=True)
                    # might be "0" or "0.01241"
                    try:
                        balance = float(bal_text)
                    except:
                        pass
                break
        # If not found, try to find "Total Earned"
        if balance is None:
            for card in stat_cards:
                label = card.find('p')
                if label and 'Total Earned' in label.get_text():
                    val = card.find('h5')
                    if val:
                        bal_text = val.get_text(strip=True).replace(' USD', '')
                        try:
                            balance = float(bal_text)
                        except:
                            pass
                    break
        return username, balance
    except Exception as e:
        print_error(f"Gagal mengambil dashboard: {e}")
        return None, None


# ============================================================
# MAIN WORKER
# ============================================================

def worker(cookie_raw, user_agent):
    session = requests.Session()
    session.cookies.update(parse_cookie_string(cookie_raw))

    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Ch-Ua": '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": '"Android"',
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate, br, zstd",
    }

    get_url = "https://skyfreecoins.top/app/faucet"
    post_url = "https://skyfreecoins.top/app/faucet/verify"

    # --- Get initial dashboard data ---
    username, balance = fetch_dashboard(session, headers)
    if username is None:
        print_session_invalid()
        return
    if balance is None:
        balance = 0.0  # fallback

    # --- First fetch faucet page to get limits and reward ---
    try:
        resp = session.get(get_url, headers=headers, timeout=30)
        if resp.status_code != 200:
            print_error(f"HTTP {resp.status_code} saat mengambil halaman faucet.")
            return
        soup = BeautifulSoup(resp.text, 'html.parser')
        # Claims left
        claims_left = None
        total_claims = None
        for p in soup.find_all('p', class_=re.compile(r'font-weight-bold')):
            text = p.get_text(strip=True)
            match = re.search(r'(\d+)/(\d+)', text)
            if match:
                claims_left = int(match.group(1))
                total_claims = int(match.group(2))
                break
        if claims_left is None:
            claims_left = 0
            total_claims = 0
        # Reward per claim
        reward_match = re.search(r'([\d.]+)\s*<sup>', resp.text)
        reward_per_claim = float(reward_match.group(1)) if reward_match else 0.00005
    except Exception as e:
        print_error(f"Gagal memuat halaman faucet: {e}")
        return

    # Show session
    print_session_valid(username=username, balance=balance)
    print_limits(claims_left, total_claims, reward_per_claim)
    continue_input()

    total_claims_made = 0
    total_earned = 0.0

    # Main loop
    while True:
        try:
            # Human pause before cycle
            random_delay(8.0, 15.0)

            # 1. GET faucet page
            res_get = session.get(get_url, headers=headers, timeout=30)
            if res_get.status_code in (302, 303) or "login" in res_get.url:
                print_session_invalid()
                break
            if res_get.status_code != 200:
                print_error(f"HTTP {res_get.status_code}")
                continue

            random_delay(1.0, 3.0)

            soup = BeautifulSoup(res_get.text, 'html.parser')

            # 2. Tokens
            def get_input_value(name):
                inp = soup.find('input', {'name': name})
                if inp:
                    return inp.get('value')
                inp_css = soup.select_one(f'input[name="{name}"]')
                if inp_css:
                    return inp_css.get('value')
                return None

            csrf = get_input_value('csrf_token_name')
            token = get_input_value('token')
            secure = get_input_value('secure_token')

            if not csrf or not token or not secure:
                print_error("Token tidak ditemukan. Cookie mungkin expired.")
                break

            # 3. Claims left
            claims_left = None
            total_claims = None
            for p in soup.find_all('p', class_=re.compile(r'font-weight-bold')):
                text = p.get_text(strip=True)
                match = re.search(r'(\d+)/(\d+)', text)
                if match:
                    claims_left = int(match.group(1))
                    total_claims = int(match.group(2))
                    break

            if claims_left is None or claims_left <= 0:
                print_warning("Tidak ada sisa claim hari ini.")
                break

            # 4. Captcha
            captcha_box = soup.find('div', class_='captcha-question')
            if not captcha_box:
                print_error("Captcha tidak ditemukan.")
                break

            raw_captcha = captcha_box.get_text(strip=True)
            clean = re.sub(r'=\s*\?', '', raw_captcha).strip()
            clean = clean.replace('×', '*').replace('÷', '/')
            match = re.search(r'([\d.]+)\s*([+\-*/])\s*([\d.]+)', clean)
            if not match:
                print_error(f"Format captcha salah: {clean}")
                break

            a = float(match.group(1))
            op = match.group(2)
            b = float(match.group(3))

            if op == '+':
                result = a + b
            elif op == '-':
                result = a - b
            elif op == '*':
                result = a * b
            elif op == '/':
                result = a / b
            else:
                result = 0

            if result.is_integer():
                result = int(result)

            print_task(raw_captcha)

            # Pause before solving
            random_delay(2.0, 4.0)
            # Pause before POST
            random_delay(1.0, 2.5)

            # 5. POST claim
            payload = {
                'csrf_token_name': csrf,
                'token': token,
                'secure_token': secure,
                'js_enabled': '1',
                'email_confirm': '',
                'math_captcha': str(result)
            }

            post_headers = headers.copy()
            post_headers.update({
                'Content-Type': 'application/x-www-form-urlencoded',
                'Origin': 'https://skyfreecoins.top',
                'Referer': get_url
            })

            res_post = session.post(post_url, data=payload, headers=post_headers, timeout=30)

            # Pause after submission
            random_delay(2.0, 5.0)

            # 6. Parse result
            msg = "Claim berhasil!"
            swal_match = re.search(r"Swal\.fire\s*\(\s*['\"][^'\"]*['\"]\s*,\s*['\"]([^'\"]+)['\"]", res_post.text)
            if swal_match:
                msg = swal_match.group(1)
            else:
                post_soup = BeautifulSoup(res_post.text, 'html.parser')
                alert = post_soup.find('div', class_=re.compile(r'alert'))
                if alert:
                    msg = alert.get_text(strip=True)

            reward = 0.0
            reward_match = re.search(r'([\d.]+)\s*USD', res_post.text)
            if reward_match:
                reward = float(reward_match.group(1))
                total_earned += reward
                total_claims_made += 1

            # Refresh balance from dashboard after claim
            _, new_balance = fetch_dashboard(session, headers)
            if new_balance is not None:
                balance = new_balance

            # Update claims left from response
            post_soup = BeautifulSoup(res_post.text, 'html.parser')
            for p in post_soup.find_all('p', class_=re.compile(r'font-weight-bold')):
                text = p.get_text(strip=True)
                match = re.search(r'(\d+)/(\d+)', text)
                if match:
                    claims_left = int(match.group(1))
                    total_claims = int(match.group(2))
                    break

            print_success(reward, balance, claims_left)

            # 7. Cooldown timer
            minute_elem = post_soup.find('b', id='minute')
            second_elem = post_soup.find('b', id='second')
            if minute_elem and second_elem:
                try:
                    mins = int(minute_elem.text)
                    secs = int(second_elem.text)
                    cooldown = mins * 60 + secs
                    if cooldown > 0:
                        print(f"{Y}[!] Cooldown {cooldown} detik{RESET}")
                        show_cooldown(cooldown)
                except:
                    pass

        except KeyboardInterrupt:
            print_warning("Dihentikan oleh user.")
            break
        except Exception as e:
            print_error(f"Error: {e}")
            time.sleep(10)

    print_finished(total_claims_made, total_earned, balance)
    print_footer()


# ============================================================
# MAIN
# ============================================================

def main():
    print_banner()
    print_setup()
    cookie = setup_input()
    if not cookie:
        print_error("Cookie tidak boleh kosong!")
        return

    ua = input(f"{Y}User-Agent (enter untuk default): {W}").strip()
    if not ua:
        ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36"

    clear_screen()
    print_banner()
    print(f"{Y}[!] Human‑like delays added: reading, typing, waiting...{RESET}")
    print(f"{Y}[!] Tekan Ctrl+C untuk berhenti{RESET}\n")

    worker(cookie, ua)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Y}Program dihentikan.{RESET}")
        sys.exit(0)
