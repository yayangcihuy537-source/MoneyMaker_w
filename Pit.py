#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PITCoinDrop Auto Bot
- Daily quest claim
- Boost overclock setiap 10 menit
- Claim mining setiap 10 menit
- Watch ad boost (hanya jika boost belum aktif)
- Portable untuk Termux/Windows/Linux
"""

import sys
import os
import time
import json
from datetime import datetime

# ============ DEPENDENCY CHECK ============
try:
    import requests
except ImportError:
    print("❌ Module 'requests' belum terinstall.")
    print("   Install: pip install requests")
    sys.exit(1)

try:
    from colorama import init, Fore, Style
    init(autoreset=True)
except ImportError:
    class DummyFore:
        BLACK = RED = GREEN = YELLOW = BLUE = MAGENTA = CYAN = WHITE = RESET = ''
        LIGHTBLACK_EX = LIGHTRED_EX = LIGHTGREEN_EX = LIGHTYELLOW_EX = ''
        LIGHTBLUE_EX = LIGHTMAGENTA_EX = LIGHTCYAN_EX = LIGHTWHITE_EX = ''
    Fore = DummyFore()
    Style = type('Style', (), {'BRIGHT': '', 'RESET_ALL': ''})()

# ============ KONFIGURASI ============
BASE_URL = "https://api.pitcoindrop.com"
INTERVAL_BOOST = 600          # 10 menit
DELAY_AFTER_AD = 30           # jeda 30 detik setelah watch ad
REQUEST_TIMEOUT = 15

BASE_HEADERS = {
    "host": "api.pitcoindrop.com",
    "sec-ch-ua-platform": "Android",
    "user-agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 Mobile Safari/537.36",
    "sec-ch-ua": '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?1",
    "accept": "*/*",
    "origin": "https://play.pitcoindrop.com",
    "x-requested-with": "org.telegram.messenger.web",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://play.pitcoindrop.com/",
    "accept-language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7"
}
# ======================================

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = f"""
{Fore.CYAN}{'='*40}
{Fore.YELLOW}{Style.BRIGHT}         🚀 PITCOINDROP BOT 🚀
{Fore.CYAN}{'='*40}
{Fore.GREEN}TG          : {Fore.LIGHTWHITE_EX}https://t.me/pitcoin_official
{Fore.GREEN}SCRIPTMAKER : {Fore.LIGHTWHITE_EX}MoneyMaker_w
{Fore.CYAN}{'='*40}{Style.RESET_ALL}
"""
    print(banner)

def get_init_data():
    print(f"{Fore.YELLOW}📝 Masukkan Telegram Init Data :")
    print(f"{Fore.LIGHTBLACK_EX}Contoh : user=%7B%22id%22%3A...&auth_date=...&hash=...{Fore.RESET}")
    print(f"{Fore.LIGHTBLACK_EX}(Copy dari header x-telegram-init-data di DevTools){Fore.RESET}")
    print("-" * 60)
    init_data = input(f"{Fore.GREEN}➜ {Fore.RESET}").strip()
    if not init_data:
        print(f"{Fore.RED}❌ Init data tidak boleh kosong !{Fore.RESET}")
        return None
    return init_data

def build_headers(init_data):
    headers = BASE_HEADERS.copy()
    headers["x-telegram-init-data"] = init_data
    return headers

def safe_json(response):
    try:
        return response.json()
    except ValueError:
        print(f"{Fore.RED}❌ Response bukan JSON: {response.text[:300]}{Fore.RESET}")
        return None

def api_request(method, endpoint, headers, data=None, params=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        resp = requests.request(method, url, headers=headers, json=data, params=params, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            return safe_json(resp)
        else:
            print(f"{Fore.RED}❌ HTTP {resp.status_code} - {resp.text[:100]}{Fore.RESET}")
            return None
    except requests.exceptions.Timeout:
        print(f"{Fore.RED}❌ Timeout ({REQUEST_TIMEOUT}s){Fore.RESET}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"{Fore.RED}❌ Gagal terhubung ke server{Fore.RESET}")
        return None
    except Exception as e:
        print(f"{Fore.RED}❌ Error request: {e}{Fore.RESET}")
        return None

def get_user_info(headers):
    data = api_request("GET", "/api/user", headers)
    if data and data.get("success"):
        user = data.get("user", {})
        mining = data.get("miningState", {})
        return user, mining
    return None, None

def get_mining_state(headers):
    """Ambil mining state terbaru tanpa print berlebihan"""
    data = api_request("GET", "/api/user", headers)
    if data and data.get("success"):
        return data.get("miningState", {})
    return None

def get_quests(headers):
    data = api_request("GET", "/api/quests", headers)
    if data and data.get("success"):
        return data.get("quests", [])
    return []

def claim_quest(headers, quest_id):
    payload = {"questId": quest_id}
    data = api_request("POST", "/api/quests/claim", headers, data=payload)
    if data and data.get("success"):
        print(f"{Fore.GREEN}✅ Quest {quest_id} berhasil diklaim! Reward: {data.get('reward', 0)}{Fore.RESET}")
        return True
    else:
        data2 = api_request("POST", "/api/quests/complete", headers, data=payload)
        if data2 and data2.get("success"):
            print(f"{Fore.GREEN}✅ Quest {quest_id} berhasil diklaim!{Fore.RESET}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️ Gagal klaim quest {quest_id} (mungkin sudah diklaim){Fore.RESET}")
            return False

def claim_mining(headers):
    print(f"{Fore.CYAN}⛏️  Claim mining ...{Fore.RESET}", end="", flush=True)
    data = api_request("POST", "/api/mine/claim", headers)
    if data and data.get("success"):
        claimed = data.get("claimedAmount", 0)
        new_balance = data.get("newBalance", 0)
        print(f"\r{Fore.GREEN}✅ Claimed {claimed:.4f} PIT  |  Balance: {new_balance:.4f} PIT{Fore.RESET}")
        return True, claimed, new_balance
    else:
        print(f"\r{Fore.YELLOW}⚠️ Claim mining gagal (mungkin bucket belum penuh){Fore.RESET}")
        return False, 0, 0

def boost_overclock(headers):
    print(f"{Fore.CYAN}⚡ Boost overclock ...{Fore.RESET}", end="", flush=True)
    data = api_request("POST", "/api/boost/overclock", headers)
    if data and data.get("success"):
        mining = data.get("miningState", {})
        ths = mining.get("activeTHs", 0)
        print(f"\r{Fore.GREEN}✅ Overclock aktif! Hashrate: {ths} TH/s{Fore.RESET}")
        return True
    else:
        print(f"\r{Fore.YELLOW}⚠️ Overclock gagal (mungkin cooldown){Fore.RESET}")
        return False

def is_ad_boost_active(headers):
    """Cek apakah ad boost masih aktif dari mining state"""
    mining = get_mining_state(headers)
    if mining:
        is_active = mining.get("isAdBoostActive", False)
        remaining_ms = mining.get("adBoostTimeRemainingMs", 0)
        if is_active and remaining_ms > 5000:  # lebih dari 5 detik
            print(f"{Fore.YELLOW}📺 Iklan masih aktif, sisa {remaining_ms//1000} detik, lewati watch ad{Fore.RESET}")
            return True
    return False

def watch_ad_boost(headers):
    """Coba watch ad boost, cek status dulu"""
    # Cek apakah boost sudah aktif
    if is_ad_boost_active(headers):
        return False  # skip, tidak perlu tonton iklan

    print(f"{Fore.CYAN}📺 Menonton iklan boost ...{Fore.RESET}", end="", flush=True)
    # Daftar endpoint yang mungkin
    endpoints = [
        "/api/boost/adsgram",      # Dari pesan response: Adsgram Rewarded Video
        "/api/boost/watch-ads",
        "/api/boost/ad",
        "/api/boost/watch",
        "/api/mine/boost",
        "/api/boost/ads"
    ]
    for ep in endpoints:
        data = api_request("POST", ep, headers)
        if data and data.get("success"):
            msg = data.get("message", "")
            mining = data.get("miningState", {})
            ths = mining.get("activeTHs", 0)
            print(f"\r{Fore.GREEN}✅ Iklan berhasil! {msg}  |  Hashrate: {ths} TH/s{Fore.RESET}")
            return True
    print(f"\r{Fore.YELLOW}⚠️ Gagal menonton iklan (limit atau tidak tersedia){Fore.RESET}")
    return False

def daily_checkin(headers):
    quests = get_quests(headers)
    daily_quest = None
    for q in quests:
        if "Daily Check-in" in q.get("title", ""):
            daily_quest = q
            break
    if not daily_quest:
        print(f"{Fore.YELLOW}⚠️ Quest Daily Check-in tidak ditemukan{Fore.RESET}")
        return False

    qid = daily_quest.get("id")
    user, _ = get_user_info(headers)
    if user:
        completed = [cq.get("id") for cq in user.get("completedQuests", [])]
        if qid in completed:
            print(f"{Fore.YELLOW}✅ Daily Check-in sudah diklaim hari ini{Fore.RESET}")
            return True
    print(f"{Fore.CYAN}📅 Claim Daily Check-in ...{Fore.RESET}")
    return claim_quest(headers, qid)

def countdown_timer(seconds, label="Menunggu"):
    print(f"{Fore.YELLOW}⏳ {label} {seconds//60} menit ...{Fore.RESET}")
    bar_length = 10
    for i in range(seconds, 0, -1):
        progress = (seconds - i) / seconds
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        mins = i // 60
        secs = i % 60
        text = f"⏱️ {mins:02d}:{secs:02d} [{bar}] {int(progress*100):3d}%"
        sys.stdout.write("\r" + text + " " * 10)
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()

def main():
    clear_screen()
    print_banner()
    init_data = get_init_data()
    if not init_data:
        return

    headers = build_headers(init_data)

    clear_screen()
    print_banner()

    user, mining = get_user_info(headers)
    if not user:
        print(f"{Fore.RED}❌ Gagal memulai bot. Cek init data Anda !{Fore.RESET}")
        return

    # Daily check-in
    print(f"\n{Fore.CYAN}📅 Menjalankan Daily Check-in ...{Fore.RESET}")
    daily_checkin(headers)

    print(f"\n{Fore.GREEN}✅ Bot berjalan! Boost & Claim setiap {INTERVAL_BOOST//60} menit")
    print(f"{Fore.YELLOW}💡 Tekan Ctrl+C untuk berhenti{Fore.RESET}\n")

    cycle_count = 0
    total_claimed = 0

    while True:
        try:
            cycle_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.WHITE}[{current_time}] {Fore.YELLOW}🔄 Siklus #{cycle_count}")
            print(f"{Fore.CYAN}{'='*60}")

            # 1. Boost overclock
            boost_overclock(headers)

            # 2. Claim mining
            success, claimed, new_bal = claim_mining(headers)
            if success:
                total_claimed += claimed

            # 3. Watch ad boost (hanya jika belum aktif)
            watch_ad_boost(headers)

            # 4. Jeda 30 detik setelah iklan (jika berhasil ditonton)
            #    Untuk efisiensi, kita tunda hanya jika iklan berhasil, tapi di sini kita tunda selalu
            print(f"{Fore.YELLOW}⏳ Jeda 30 detik setelah iklan ...{Fore.RESET}")
            time.sleep(DELAY_AFTER_AD)

            # 5. Countdown sampai siklus berikutnya
            countdown_timer(INTERVAL_BOOST, "Menunggu siklus berikutnya")

        except KeyboardInterrupt:
            print(f"\n\n{Fore.RED}🛑 Bot dihentikan oleh user{Fore.RESET}")
            print(f"{Fore.CYAN}📊 Total siklus: {cycle_count}")
            print(f"{Fore.CYAN}💰 Total PIT terkumpul: {total_claimed:.4f} PIT")
            print(f"\n{Fore.GREEN}Terima kasih ! 👋{Fore.RESET}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error: {e}")
            print(f"{Fore.YELLOW}⏳ Tunggu 60 detik lalu coba lagi ...{Fore.RESET}")
            time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}🛑 Bot dihentikan{Fore.RESET}")
