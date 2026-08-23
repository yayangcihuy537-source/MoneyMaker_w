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

# Konfigurasi
BASE_URL = "https://doge-drop-daily.base44.app"
APP_ID = "6a13f1a4804d249d12145f41"
FAUCETPAY_EMAIL = "tg6894031790@dogefaucet.app"  # ganti sesuai akun
INIT_DATA = ""

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.169 Mobile Safari/537.36 Telegram-Android/12.9.1",
    "Accept": "application/json",
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
    "x-base44-anonymous-id": "ct53qsrr7d78bfamovd3ji",
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
    print(Fore.GREEN + "🐕 Auto Watch Ads - ScriptyXSou 🐕")
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

def authenticate(init_data):
    url = f"{BASE_URL}/api/apps/{APP_ID}/functions/faucetAccount"
    payload = {
        "action": "tg_auth",
        "init_data": init_data,
        "landing_lang": "en"
    }
    try:
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("user"):
                return True
            else:
                print(Fore.RED + "Autentikasi gagal: respon tidak mengandung user")
                return False
        else:
            print(Fore.RED + f"Autentikasi gagal (HTTP {resp.status_code})")
            return False
    except Exception as e:
        print(Fore.RED + f"Error saat autentikasi: {e}")
        return False

def watch_ad(ad_type="short", duration=27):
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
        resp = requests.post(url, headers=HEADERS, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok"):
                reward = data.get("reward", 0.0)
                print(Fore.GREEN + f"✅ +{reward} DOGE")
                return reward
            else:
                # Jika ok false, biasanya karena limit habis
                err_msg = data.get("message", "unknown error")
                print(Fore.YELLOW + f"⚠️  Iklan {ad_type} tidak tersedia: {err_msg}")
                return 0.0
        else:
            print(Fore.RED + f"❌ HTTP {resp.status_code}")
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

    print(Fore.YELLOW + "\n🔐 Autentikasi...")
    if not authenticate(INIT_DATA):
        print(Fore.RED + "Gagal auth, cek init data.")
        input("Tekan Enter...")
        return

    total_reward = 0.0
    ad_types = ["short", "long", "tower"]  # urutan bebas
    round_count = 0

    print(Fore.CYAN + "\n🔄 Memulai auto-watch semua iklan...\n")

    while True:
        round_count += 1
        success_in_round = False

        for ad_type in ad_types:
            reward = watch_ad(ad_type, duration=27)
            if reward > 0:
                total_reward += reward
                success_in_round = True
                # jeda kecil agar tidak kena rate limit
                time.sleep(2)
            else:
                # kalau satu tipe gagal, tetap coba tipe lain
                pass

        # Jika dalam satu putaran tidak ada satupun iklan yang berhasil,
        # berarti semua kuota habis → berhenti
        if not success_in_round:
            print(Fore.RED + "\n🚫 Semua iklan sudah habis (limit harian/cooldown).")
            break

        # Opsional: batasi perulangan agar tidak endless (misal max 5 putaran)
        if round_count >= 10:
            print(Fore.YELLOW + "\n⏹️  Batas putaran tercapai, berhenti.")
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
