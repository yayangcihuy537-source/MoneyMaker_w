#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import requests
from datetime import datetime
from pyfiglet import Figlet
from colorama import init, Fore, Style, Back

init(autoreset=True)

# Konfigurasi - ubah sesuai kebutuhan
BASE_URL = "https://doge-drop-daily.base44.app"
APP_ID = "6a13f1a4804d249d12145f41"
FAUCETPAY_EMAIL = "tg6894031790@dogefaucet.app"  # ganti dengan email faucetpay kamu
INIT_DATA = ""  # akan diisi lewat menu

# Headers dasar (akan ditambah cookie/session nanti)
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.169 Mobile Safari/537.36 Telegram-Android/12.9.1",
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": BASE_URL,
    "X-Requested-With": "org.telegram.messenger.web",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": f"{BASE_URL}/watch-ads",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "x-app-id": APP_ID,
}

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def banner():
    f = Figlet(font='big')
    ascii_art = f.renderText('Doge')
    lines = ascii_art.split('\n')
    colored = []
    for line in lines:
        if line.strip():
            colored.append(Fore.YELLOW + line + Style.RESET_ALL)
        else:
            colored.append(line)
    print('\n'.join(colored))
    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + "🐕 Auto Watch Ads - ScriptyXSou (Fixed) 🐕")
    print(Fore.CYAN + "=" * 60)

def progress_bar(duration, label="Menonton iklan"):
    start = time.time()
    elapsed = 0
    while elapsed < duration:
        elapsed = time.time() - start
        percent = min(elapsed / duration, 1.0)
        filled = int(percent * 10)
        bar = "■" * filled + " " * (10 - filled)
        sys.stdout.write(f"\r{label} [{bar}] {int(percent*100)}%  ")
        sys.stdout.flush()
        time.sleep(0.5)
    sys.stdout.write(f"\r{label} [{Fore.GREEN}■■■■■■■■■■{Style.RESET_ALL}] 100%  \n")
    sys.stdout.flush()

def safe_json_response(resp):
    """Safe JSON parsing with debug output on failure."""
    try:
        return resp.json()
    except (json.JSONDecodeError, ValueError) as e:
        # Return raw text for debugging
        raw = resp.text[:500] if resp.text else "(empty response)"
        return {
            'ok': False,
            'error': f"JSON parse error: {str(e)}",
            'raw': raw,
            'status_code': resp.status_code
        }

def create_session(init_data):
    """Create a session with proper cookies and headers."""
    session = requests.Session()
    session.headers.update(BASE_HEADERS)
    
    # Add initData as a query param for initial page load? Maybe not needed.
    # But we can do a GET to set cookies
    try:
        session.get(BASE_URL + "/watch-ads", timeout=10)
    except:
        pass
    
    # Also set the anonymous-id header if needed (generate random or use static)
    # We'll keep it static for now
    session.headers.update({
        "x-base44-anonymous-id": "ct53qsrr7d78bfamovd3ji"
    })
    
    return session

def authenticate(session, init_data):
    """Authenticate using initData with robust error handling."""
    url = f"{BASE_URL}/api/apps/{APP_ID}/functions/faucetAccount"
    payload = {
        "action": "tg_auth",
        "init_data": init_data,
        "landing_lang": "en"
    }
    try:
        resp = session.post(url, json=payload, timeout=15)
        if resp.status_code != 200:
            print(Fore.RED + f"HTTP {resp.status_code} – mungkin server error atau endpoint berubah.")
            # Tampilkan 200 karakter pertama
            print(Fore.YELLOW + f"Response preview: {resp.text[:200]}")
            return False
        
        data = safe_json_response(resp)
        if not data.get('ok', False) and 'error' in data:
            # Jika ada error dari JSON parse
            if 'raw' in data:
                print(Fore.RED + f"Server returned non-JSON: {data['raw']}")
                return False
            else:
                print(Fore.RED + f"Auth gagal: {data.get('error', 'unknown')}")
                return False
        
        # Jika response berisi user
        if data.get("user"):
            print(Fore.GREEN + "✅ Autentikasi berhasil.")
            return True
        else:
            print(Fore.RED + "Autentikasi gagal: respon tidak mengandung 'user'.")
            print(Fore.YELLOW + f"Response: {json.dumps(data, indent=2)}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"Request error: {e}")
        return False

def watch_ad(session, ad_type="short", duration=27):
    """Watch an ad and claim reward."""
    print(Fore.CYAN + f"\n▶ Menjalankan iklan tipe: {ad_type.upper()}")
    progress_bar(duration, f"Menonton {ad_type}")

    url = f"{BASE_URL}/api/apps/{APP_ID}/functions/creditReward"
    payload = {
        "action": "ad_watch",
        "ad_type": ad_type,
        "faucetpay_email": FAUCETPAY_EMAIL,
        "init_data": INIT_DATA
    }
    try:
        resp = session.post(url, json=payload, timeout=15)
        if resp.status_code != 200:
            print(Fore.RED + f"❌ HTTP {resp.status_code}")
            return 0.0

        data = safe_json_response(resp)
        if 'error' in data:
            print(Fore.RED + f"❌ JSON error: {data['error']}")
            if 'raw' in data:
                print(Fore.YELLOW + f"Raw: {data['raw']}")
            return 0.0

        if data.get("ok"):
            reward = data.get("reward", 0.0)
            print(Fore.GREEN + f"✅ +{reward} DOGE")
            return reward
        else:
            err_msg = data.get("message", "unknown error")
            # Jika limit habis biasanya 'ok' false
            print(Fore.YELLOW + f"⚠️  Iklan {ad_type} tidak tersedia: {err_msg}")
            return 0.0
    except Exception as e:
        print(Fore.RED + f"❌ Error: {e}")
        return 0.0

def start_farming():
    global INIT_DATA
    if not INIT_DATA:
        print(Fore.RED + "⚠️  Init data belum diatur! Menu 2 dulu.")
        input("Tekan Enter...")
        return

    session = create_session(INIT_DATA)

    print(Fore.YELLOW + "\n🔐 Autentikasi...")
    if not authenticate(session, INIT_DATA):
        print(Fore.RED + "Gagal auth, cek init data dan koneksi.")
        input("Tekan Enter...")
        return

    total_reward = 0.0
    ad_types = ["short", "long", "tower"]  # urutan bebas
    round_count = 0
    max_rounds = 10  # batas agar tidak endless

    print(Fore.CYAN + "\n🔄 Memulai auto-watch semua iklan...\n")

    while round_count < max_rounds:
        round_count += 1
        success_in_round = False

        for ad_type in ad_types:
            reward = watch_ad(session, ad_type, duration=27)
            if reward > 0:
                total_reward += reward
                success_in_round = True
                time.sleep(2)  # jeda agar tidak kena rate limit
            else:
                # Gagal, lanjut ke tipe berikutnya
                pass

        # Jika dalam satu putaran tidak ada yang berhasil → semua kuota habis
        if not success_in_round:
            print(Fore.RED + "\n🚫 Semua iklan sudah habis (limit harian/cooldown).")
            break

    print(Fore.CYAN + "=" * 60)
    print(Fore.GREEN + f"🏆 TOTAL REWARD : {total_reward:.6f} DOGE")
    print(Fore.CYAN + "=" * 60)
    input("Tekan Enter untuk kembali ke menu...")

def set_init_data():
    global INIT_DATA
    clear()
    banner()
    print(Fore.YELLOW + "\n📝 Masukkan init_data (copy dari tgWebAppData):")
    new_data = input("Init data: ").strip()
    if new_data:
        INIT_DATA = new_data
        print(Fore.GREEN + "✅ Init data disimpan.")
    else:
        print(Fore.RED + "❌ Tidak boleh kosong.")
    input("Tekan Enter...")

def main():
    while True:
        clear()
        banner()
        print(Fore.MAGENTA + "\n📋 MENU UTAMA")
        print(Fore.WHITE + "1. 🚀 Start Farming (semua iklan otomatis)")
        print("2. ⚙️  Set Init Data")
        print("0. ❌ Exit")
        print(Fore.CYAN + "-" * 40)
        if INIT_DATA:
            print(Fore.GREEN + f"Status Init Data: {Fore.YELLOW}Sudah diatur ✓")
        else:
            print(Fore.RED + "Status Init Data: Belum diatur ✗")
        choice = input(Fore.WHITE + "\nPilih menu: ").strip()

        if choice == "1":
            start_farming()
        elif choice == "2":
            set_init_data()
        elif choice == "0":
            print(Fore.RED + "Keluar... Sampai jumpa! 🐕")
            sys.exit(0)
        else:
            print(Fore.RED + "Pilihan tidak valid.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\nProgram dihentikan user. 🐕")
        sys.exit(0)
