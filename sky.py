#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
import time
import requests
from bs4 import BeautifulSoup

# ====================== Warna ======================
class Color:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def parse_cookie_string(cookie_str):
    cookies = {}
    if not cookie_str:
        return cookies
    for item in cookie_str.split(';'):
        if '=' in item:
            key, val = item.strip().split('=', 1)
            cookies[key] = val
    return cookies

# ====================== Main Worker ======================
def worker(cookie_raw, user_agent):
    acc_prefix = f"[{Color.BOLD}{Color.CYAN}AKUN{Color.RESET}]"
    
    session = requests.Session()
    session.cookies.update(parse_cookie_string(cookie_raw))

    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": '"Android"',
    }

    get_url = "https://skyfreecoins.top/app/faucet"
    post_url = "https://skyfreecoins.top/app/faucet/verify"

    print(f"{acc_prefix} {Color.CYAN}[*] Memulai auto claim...{Color.RESET}")

    while True:
        try:
            # 1. GET halaman faucet
            res_get = session.get(get_url, headers=headers, timeout=30)

            # Deteksi redirect ke login (cookie expired)
            if res_get.status_code in (302, 303) or "login" in res_get.url:
                print(f"{acc_prefix} {Color.RED}[-] Cookie expired / belum login. Ambil cookie baru.{Color.RESET}")
                break

            if res_get.status_code != 200:
                print(f"{acc_prefix} {Color.RED}[-] HTTP {res_get.status_code}{Color.RESET}")
                time.sleep(10)
                continue

            soup = BeautifulSoup(res_get.text, 'html.parser')

            # 2. Ambil token
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
                print(f"{acc_prefix} {Color.RED}[-] Token tidak ditemukan. Cek cookie atau login ulang.{Color.RESET}")
                break

            # 3. Claims left
            claims_left = None
            total_claims = None
            for p in soup.find_all('p', class_=re.compile(r'font-weight-bold')):
                text = p.get_text(strip=True)
                match = re.search(r'(\d+)/(\d+)', text)
                if match:
                    claims_left = int(match.group(1))
                    total_claims = match.group(2)
                    break

            if claims_left is None or claims_left <= 0:
                print(f"{acc_prefix} {Color.YELLOW}[!] Tidak ada sisa claim atau cookie tidak valid.{Color.RESET}")
                break

            # 4. Math captcha
            captcha_box = soup.find('div', class_='captcha-question')
            if not captcha_box:
                print(f"{acc_prefix} {Color.RED}[-] Captcha tidak ditemukan.{Color.RESET}")
                break

            raw_captcha = captcha_box.get_text(strip=True)
            clean = re.sub(r'=\s*\?', '', raw_captcha).strip()
            clean = clean.replace('×', '*').replace('÷', '/')
            match = re.search(r'([\d.]+)\s*([+\-*/])\s*([\d.]+)', clean)
            if not match:
                print(f"{acc_prefix} {Color.RED}[-] Format captcha salah: {clean}{Color.RESET}")
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

            print(f"{acc_prefix} {Color.CYAN}[*] Captcha: {raw_captcha} → {result}{Color.RESET}")

            # 5. Delay 5 detik sebelum POST
            time.sleep(5)

            # 6. POST claim
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

            # 7. Parse hasil claim
            msg = "Claim berhasil!"
            swal_match = re.search(r"Swal\.fire\s*\(\s*['\"][^'\"]*['\"]\s*,\s*['\"]([^'\"]+)['\"]", res_post.text)
            if swal_match:
                msg = swal_match.group(1)
            else:
                post_soup = BeautifulSoup(res_post.text, 'html.parser')
                alert = post_soup.find('div', class_=re.compile(r'alert'))
                if alert:
                    msg = alert.get_text(strip=True)

            rem_claims = claims_left - 1
            print(
                f"{acc_prefix} {Color.GREEN}[✓] {msg}{Color.RESET} "
                f"{Color.YELLOW}||{Color.RESET} {Color.CYAN}Sisa {rem_claims}/{total_claims}{Color.RESET}"
            )

            # 8. Tunggu 10 detik sebelum putaran berikutnya
            time.sleep(10)

        except KeyboardInterrupt:
            print(f"\n{Color.YELLOW}[!] Dihentikan oleh user.{Color.RESET}")
            break
        except Exception as e:
            print(f"{acc_prefix} {Color.RED}[-] Error: {e}{Color.RESET}")
            time.sleep(10)

# ====================== MAIN ======================
def main():
    clear_screen()
    print(f"{Color.BOLD}{Color.CYAN}===== AUTO CLAIM SKYFREECOINS ====={Color.RESET}\n")

    cookie = input(f"{Color.YELLOW}Masukkan Cookie (full): {Color.RESET}").strip()
    if not cookie:
        print(f"{Color.RED}Cookie tidak boleh kosong!{Color.RESET}")
        return

    ua = input(f"{Color.YELLOW}User-Agent (enter untuk default): {Color.RESET}").strip()
    if not ua:
        ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36"

    clear_screen()
    print(f"{Color.BOLD}{Color.CYAN}===== MENJALANKAN AUTO CLAIM ====={Color.RESET}\n")
    print(f"{Color.YELLOW}[!] Tekan Ctrl+C untuk berhenti{Color.RESET}\n")

    worker(cookie, ua)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Program dihentikan.{Color.RESET}")
        sys.exit(0)

