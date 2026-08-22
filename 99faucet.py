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

# ========== HEADER SIMPLE ==========
def print_header():
    print()
    print(f"{C['cyan']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C['reset']}")
    print(f"{C['bold']}{C['kuning']}              🚀 99FAUCET AUTO BOT{C['reset']}")
    print(f"{C['cyan']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C['reset']}")
    print()

# ========== KONFIGURASI ==========
BASE_URL = "https://99faucet.com"
SOLVER_BASE = "https://bypassallshortlinks.space"
CONFIG_FILE = "config_99.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "id-ID",
    "Accept-Encoding": "gzip, deflate, br",
    "Sec-Ch-Ua": '"Chromium";v="127", "Not)A;Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?1",
    "Sec-Ch-Ua-Platform": "Android",
}

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

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        print(f"{C['putih']}API Key bypassallshortlinks: {C['kuning']}", end="")
        api_key = input().strip()
        print(f"{C['putih']}Cookie (opsional, kosongkan jika belum login): {C['kuning']}", end="")
        cookie = input().strip()
        config = {"apikey": api_key, "cookie": cookie}
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"{C['hijau']}Config disimpan ke {CONFIG_FILE}{C['reset']}")
        time.sleep(1)
        return config

def solve_hcaptcha(sitekey, pageurl, apikey, show_progress=False):
    submit = requests.get(f"{SOLVER_BASE}/in.php", params={
        "key": apikey,
        "method": "hcaptcha",
        "sitekey": sitekey,
        "pageurl": pageurl
    }, timeout=30)
    if not submit.text.startswith("OK|"):
        print(f"{C['merah']}[!] Gagal submit hCaptcha: {submit.text}{C['reset']}")
        return None
    task_id = submit.text.split("|")[-1]
    if show_progress:
        print(f"{C['kuning']}[+] Task ID    : {task_id}{C['reset']}")
        print(f"{C['cyan']}[*] hCaptcha    : WAITING...{C['reset']}")
    for i in range(45):
        time.sleep(2)
        poll = requests.get(f"{SOLVER_BASE}/res.php", params={"id": task_id, "key": apikey}, timeout=30)
        if poll.text.startswith("OK|"):
            token = poll.text.split("|")[-1]
            if show_progress:
                print(f"{C['hijau']}[+] hCaptcha   : SOLVED ✓{C['reset']}")
            return token
        if show_progress and i % 5 == 0:
            print(f"{C['dim']}[*] Polling     : {i+1}/45...{C['reset']}")
    print(f"{C['merah']}[!] hCaptcha timeout.{C['reset']}")
    return None

def get_sitekey(session, url, captcha_type="hcaptcha"):
    resp = session.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    if captcha_type == "hcaptcha":
        elem = soup.find("div", {"class": "h-captcha"})
        if elem:
            return elem.get("data-sitekey")
        elem = soup.find("div", {"data-sitekey": True})
        if elem:
            return elem.get("data-sitekey")
        match = re.search(r'data-sitekey="([^"]+)"', resp.text)
        if match:
            return match.group(1)
    return None

def login(session, email, password, apikey):
    print(f"{C['cyan']}[*] Login...{C['reset']}")
    sitekey = get_sitekey(session, BASE_URL, "hcaptcha")
    if not sitekey:
        print(f"{C['merah']}[!] Gagal ambil sitekey hCaptcha.{C['reset']}")
        return False
    print(f"{C['kuning']}[+] Sitekey    : {sitekey}{C['reset']}")
    captcha_token = solve_hcaptcha(sitekey, BASE_URL, apikey, show_progress=True)
    if not captcha_token:
        return False

    data = {
        "email": email,
        "captcha": "hcaptcha",
        "g-recaptcha-response": "",
        "h-captcha-response": captcha_token,
        "captcha_choosen": "",
        "uf": "13abf0b009dd510c96d7b75d8f3a8dd0",
        "utt": "Asia/Jakarta",
        "ls": "id-ID"
    }
    resp = session.post(f"{BASE_URL}/auth/login", data=data, headers={
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": BASE_URL,
        "Referer": BASE_URL+"/",
    }, timeout=30, allow_redirects=False)

    if resp.status_code == 302 or "dashboard" in resp.headers.get('Location', ''):
        print(f"{C['hijau']}[+] Login      : SUCCESS ✓{C['reset']}")
        return True
    else:
        print(f"{C['merah']}[!] Login gagal. Cek kredensial.{C['reset']}")
        return False

def get_coins(session):
    resp = session.get(f"{BASE_URL}/dashboard", headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    links = soup.find_all("a", href=True)
    coins = []
    for link in links:
        href = link.get("href")
        if href and "/faucet/" in href:
            coin = href.split("/faucet/")[-1]
            if coin and coin not in coins:
                coins.append(coin)
    coins.sort(key=len)
    return coins

def get_csrf_token(session, coin):
    url = f"{BASE_URL}/faucet/{coin}"
    resp = session.get(url, headers=HEADERS, timeout=30)
    if resp.status_code != 200:
        return None
    soup = BeautifulSoup(resp.text, "html.parser")
    token_input = soup.find("input", {"name": "token"})
    if token_input:
        return token_input.get("value")
    match = re.search(r'name="token"\s+value="([^"]+)"', resp.text)
    if match:
        return match.group(1)
    return None

def claim_faucet(session, coin, apikey):
    url = f"{BASE_URL}/faucet/{coin}"
    sitekey = get_sitekey(session, url, "hcaptcha")
    if not sitekey:
        print(f"{C['merah']}[!] Gagal ambil sitekey hCaptcha faucet.{C['reset']}")
        return False
    print(f"{C['kuning']}[+] Sitekey    : {sitekey[:16]}****{C['reset']}")
    captcha_token = solve_hcaptcha(sitekey, url, apikey, show_progress=True)
    if not captcha_token:
        return False

    csrf_token = get_csrf_token(session, coin)
    if not csrf_token:
        print(f"{C['merah']}[!] Gagal ambil CSRF token.{C['reset']}")
        return False
    print(f"{C['kuning']}[+] CSRF Token : ********{C['reset']}")

    data = {
        "ci_csrf_token": "",
        "token": csrf_token,
        "currency": coin,
        "captcha": "hcaptcha",
        "g-recaptcha-response": "",
        "h-captcha-response": captcha_token,
        "uf": "13abf0b009dd510c96d7b75d8f3a8dd0",
        "utt": "Asia/Jakarta",
        "ls": "id-ID"
    }
    resp = session.post(f"{BASE_URL}/faucet/verify", data=data, headers={
        **HEADERS,
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/faucet/{coin}",
    }, timeout=30)

    if "Good job" in resp.text or "success" in resp.text.lower():
        print(f"{C['hijau']}[+] Claim      : SUCCESS ✓{C['reset']}")
        reward_match = re.search(r'([\d.]+)\s+(\w+)', resp.text)
        if reward_match:
            print(f"{C['kuning']}[+] Reward     : {reward_match.group(1)} {reward_match.group(2)}{C['reset']}")
        print(f"{C['hijau']}[+] FaucetPay  : SUCCESSFUL{C['reset']}")
        print(f"{C['hijau']}[+] Status     : SENT TO FAUCETPAY ✓{C['reset']}")
        return True
    elif "already claimed" in resp.text.lower() or "wait" in resp.text.lower():
        print(f"{C['kuning']}[!] Claim      : COOLDOWN ⏳{C['reset']}")
        return False
    else:
        print(f"{C['merah']}[?] Claim tidak jelas.{C['reset']}")
        with open("claim_debug_99.html", "w", encoding="utf-8") as f:
            f.write(resp.text)
        return False

def main():
    clear()
    print_header()

    config = get_config()
    apikey = config.get('apikey')
    cookie = config.get('cookie', '')
    session = requests.Session()
    if cookie:
        session.headers.update({"Cookie": cookie})

    session.get(BASE_URL, headers=HEADERS, timeout=30)

    if not cookie or not session.cookies.get('ci_session'):
        email = input(f"{C['cyan']}Email: {C['reset']}").strip()
        password = input(f"{C['cyan']}Password: {C['reset']}").strip()
        if not all([email, password]):
            print(f"{C['merah']}[!] Email dan password harus diisi!{C['reset']}")
            return
        if not login(session, email, password, apikey):
            print(f"{C['merah']}[!] Login gagal, keluar.{C['reset']}")
            return
        cookie_str = "; ".join([f"{k}={v}" for k, v in session.cookies.items()])
        config['cookie'] = cookie_str
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        print(f"{C['hijau']}[+] Cookie disimpan ke config.{C['reset']}")
    else:
        print(f"{C['hijau']}🍪 [+] Menggunakan cookie dari config.{C['reset']}")

    coins = get_coins(session)
    if not coins:
        print(f"{C['merah']}[!] Gagal ambil daftar coin.{C['reset']}")
        return

    print(f"\n{C['kuning']}💰 Daftar coin yang tersedia:{C['reset']}")
    emoji_map = {
        "ltc": "🪙", "dgb": "💎", "trx": "🔥", "bch": "💵",
        "bnb": "🟡", "sol": "☀️", "xrp": "💧", "pol": "🟣",
        "ada": "🔵", "ton": "💎", "xlm": "🌟", "eth": "♦️",
        "usdt": "💵", "dash": "🟠", "doge": "🐕", "usdc": "💵",
        "pepe": "🐸", "trump": "🇺🇸"
    }
    for i, coin in enumerate(coins, 1):
        emoji = emoji_map.get(coin, "🪙")
        num = str(i).rjust(2)
        coin_upper = coin.upper().ljust(6)
        print(f"{C['putih']}({num}) {emoji} {C['hijau']}{coin_upper}{C['reset']}", end=" ")
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
            timer(300, prefix="🔄 Next claim in")
            print()
            print(f"{C['cyan']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C['reset']}")
            print(f"{C['bold']}{C['hijau']}                 🤖 BOT RUNNING{C['reset']}")
            print(f"{C['cyan']}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C['reset']}")
        else:
            print(f"{C['kuning']}🔄 Retry in 11 seconds...{C['reset']}")
            timer(11, prefix="🔄 Retry in")  # 11 detik sesuai request
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C['merah']}[!] Bot dihentikan oleh user.{C['reset']}")
        sys.exit(0)
