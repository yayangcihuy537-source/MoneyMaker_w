#!/usr/bin/env python3
import requests
import time
import re
import json
import sys
import os
from bs4 import BeautifulSoup

# ========== WARNA ANSI ==========
C = {
    "hitam": "\033[0;30m",
    "merah": "\033[0;31m",
    "hijau": "\033[0;32m",
    "kuning": "\033[0;33m",
    "biru": "\033[0;34m",
    "cyan": "\033[0;36m",
    "putih": "\033[0;37m",
    "bold": "\033[1m",
    "reset": "\033[0m",
    "dim": "\033[2m",
}

HEADER = f"""
{C['cyan']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C['reset']}
{C['bold']}{C['kuning']}              🚀 ALTCRYP AUTO BOT{C['reset']}
{C['cyan']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C['reset']}
"""

SEPARATOR = f"{C['cyan']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C['reset']}"

def print_box(title, lines, color=C['hijau']):
    print(f"{C['bold']}{color}╭─[ {title} ]{C['reset']}")
    for line in lines:
        print(f"{color}│{C['reset']} {line}")
    print(f"{color}╰────────────────────────────────────────────────────{C['reset']}")

def timer(seconds, prefix="[!] Please wait"):
    wait_time = int(seconds)
    frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    frame_count = len(frames)
    current_frame = 0
    while wait_time > 0:
        start = time.time()
        while (time.time() - start) < 1:
            hours = wait_time // 3600
            minutes = (wait_time % 3600) // 60
            secs = wait_time % 60
            time_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
            spinner = frames[current_frame]
            print(f"{C['putih']}{prefix} {C['hijau']}{time_str} {C['putih']}{spinner}\r", end="")
            time.sleep(0.1)
            current_frame = (current_frame + 1) % frame_count
            if (time.time() - start) >= 1:
                break
        wait_time -= 1
    print(" " * 50 + "\r", end="")

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

# ========== KONFIGURASI ==========
BASE_URL = "https://altcryp.com"
SOLVER_BASE = "https://bypassallshortlinks.space"
CONFIG_FILE = "config_altcryp.json"
CLAIM_INTERVAL = 14  # <-- diubah jadi 14 detik

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "id-ID",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Ch-Ua": '"Chromium";v="127", "Not)A;Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?1",
    "Sec-Ch-Ua-Platform": "Android",
}

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        print(f"{C['putih']}Cookie (dari browser): {C['kuning']}", end="")
        cookie = input().strip()
        print(f"{C['putih']}API Key bypassallshortlinks: {C['kuning']}", end="")
        api_key = input().strip()
        config = {"cookie": cookie, "apikey": api_key}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"{C['hijau']}Config disimpan ke {CONFIG_FILE}{C['reset']}")
        time.sleep(1)
        return config

def solve_turnstile(sitekey, pageurl, apikey, show_progress=False):
    submit = requests.get(f"{SOLVER_BASE}/in.php", params={
        "key": apikey,
        "method": "turnstile",
        "sitekey": sitekey,
        "pageurl": pageurl
    }, timeout=30)
    if not submit.text.startswith("OK|"):
        print(f"{C['merah']}[!] Gagal submit Turnstile: {submit.text}{C['reset']}")
        return None
    task_id = submit.text.split("|")[-1]
    if show_progress:
        print(f"{C['kuning']}[+] Task ID    : {task_id}{C['reset']}")
        print(f"{C['cyan']}[*] Menunggu Turnstile...{C['reset']}")
    for i in range(45):
        time.sleep(2)
        poll = requests.get(f"{SOLVER_BASE}/res.php", params={"id": task_id, "key": apikey}, timeout=30)
        if poll.text.startswith("OK|"):
            token = poll.text.split("|")[-1]
            if show_progress:
                print(f"{C['hijau']}[+] Turnstile  : SOLVED ✓{C['reset']}")
            return token
        if show_progress and i % 5 == 0:
            print(f"{C['dim']}[*] Polling ke-{i+1}/45...{C['reset']}")
    print(f"{C['merah']}[!] Turnstile timeout.{C['reset']}")
    return None

def get_coins(session):
    resp = session.get(BASE_URL, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    links = soup.find_all("a", href=True)
    coins = []
    for link in links:
        href = link.get("href")
        if href and "/faucet/currency/" in href:
            coin = href.split("/faucet/currency/")[-1]
            if coin and coin not in coins:
                coins.append(coin)
    return coins

def get_csrf_and_token(session, coin):
    url = f"{BASE_URL}/faucet/currency/{coin}"
    resp = session.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None, None
    soup = BeautifulSoup(resp.text, "html.parser")
    csrf_input = soup.find("input", {"name": "csrf_token_name"})
    csrf = csrf_input.get("value") if csrf_input else None
    token_input = soup.find("input", {"name": "token"})
    token = token_input.get("value") if token_input else None
    if not csrf:
        match = re.search(r'name="csrf_token_name"\s+value="([^"]+)"', resp.text)
        if match:
            csrf = match.group(1)
    if not token:
        match = re.search(r'name="token"\s+value="([^"]+)"', resp.text)
        if match:
            token = match.group(1)
    return csrf, token

def claim_faucet(session, coin, apikey):
    print(f"{C['cyan']}[*] Claim      : PROCESSING... (coin: {coin.upper()}){C['reset']}")
    csrf, token = get_csrf_and_token(session, coin)
    if not csrf or not token:
        print(f"{C['merah']}[!] Gagal ambil CSRF/Token.{C['reset']}")
        return False
    print(f"{C['kuning']}[+] CSRF Token : {csrf}{C['reset']}")
    print(f"{C['kuning']}[+] Token      : {token}{C['reset']}")

    sitekey = "0x4AAAAAAAHPLPJjjJUpAitl"
    pageurl = f"{BASE_URL}/faucet/currency/{coin}"
    turnstile_token = solve_turnstile(sitekey, pageurl, apikey, show_progress=True)
    if not turnstile_token:
        return False

    data = {
        "username_fake_field": "",
        "csrf_token_name": csrf,
        "token": token,
        "captcha": "turnstile",
        "cf-turnstile-response": turnstile_token
    }

    url_verify = f"{BASE_URL}/faucet/verify/{coin}"
    resp = session.post(url_verify, data=data, headers={
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/faucet/currency/{coin}",
    }, timeout=30)

    if "Good job" in resp.text or "success" in resp.text.lower():
        print(f"{C['hijau']}[+] Success sent to faucetpay ✓{C['reset']}")  # <-- ubah reward message
        return True
    elif "already claimed" in resp.text.lower() or "wait" in resp.text.lower():
        print(f"{C['kuning']}[!] Claim      : COOLDOWN ⏳{C['reset']}")
        return False
    else:
        print(f"{C['merah']}[?] Claim tidak jelas.{C['reset']}")
        with open("claim_debug_altcryp.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        return False

def main():
    clear()
    print(HEADER)
    print(SEPARATOR)
    print()

    config = get_config()
    cookie = config.get('cookie', '')
    apikey = config.get('apikey', '')

    if not cookie or not apikey:
        print(f"{C['merah']}[!] Cookie atau API Key kosong.{C['reset']}")
        return

    session = requests.Session()
    session.headers.update({"Cookie": cookie})

    coins = get_coins(session)
    if not coins:
        print(f"{C['merah']}[!] Gagal ambil daftar coin. Cek cookie.{C['reset']}")
        return

    print(f"{C['kuning']}💰 Daftar coin yang tersedia:{C['reset']}")
    for i, coin in enumerate(coins, 1):
        num = str(i).rjust(2)
        coin_upper = coin.upper().ljust(6)
        print(f"{C['putih']}({num}) {C['hijau']}{coin_upper}{C['reset']}", end=" ")
        if i % 4 == 0 or i == len(coins):
            print()
    print()
    choice = input(f"{C['cyan']}🎯 Pilih nomor coin: {C['reset']}").strip()
    try:
        idx = int(choice) - 1
        coin = coins[idx]
    except:
        print(f"{C['merah']}[!] Pilihan tidak valid. Default ke coin pertama.{C['reset']}")
        coin = coins[0]
    print(f"{C['hijau']}✅ Coin dipilih: {coin.upper()}{C['reset']}")

    count = 0
    while True:
        count += 1
        print()
        print_box(f"🎯 ROUND {count}", [
            f"{C['cyan']}🚀 Claim       : PROCESSING... (coin: {coin.upper()}){C['reset']}"
        ], C['cyan'])
        success = claim_faucet(session, coin, apikey)
        if success:
            print(f"{C['hijau']}⏳ Waiting for next claim...{C['reset']}")
            timer(CLAIM_INTERVAL, prefix="🔄 Next claim in")  # <-- pakai CLAIM_INTERVAL = 14 detik
        else:
            print(f"{C['kuning']}🔄 Retry in 60 seconds...{C['reset']}")
            timer(60, prefix="🔄 Retry in")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C['merah']}[!] Bot dihentikan oleh user.{C['reset']}")
        sys.exit(0)
