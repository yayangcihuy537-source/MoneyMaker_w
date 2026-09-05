import requests
import time
import json
import os
import sys
from datetime import datetime
from colorama import init, Fore, Style, Back

init(autoreset=True)

BASE_URL = "https://tz.tamimdev.dev/api"
HEADERS = {
    "host": "tz.tamimdev.dev",
    "sec-ch-ua-platform": "Android",
    "user-agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 Mobile Safari/537.36 Telegram-Android/12.10.1",
    "sec-ch-ua": '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
    "content-type": "application/json",
    "sec-ch-ua-mobile": "?1",
    "accept": "*/*",
    "origin": "https://tz.tamimdev.dev",
    "x-requested-with": "org.telegram.messenger",
    "sec-fetch-site": "same-origin",
    "sec-fetch-mode": "cors",
    "sec-fetch-dest": "empty",
    "referer": "https://tz.tamimdev.dev/",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "priority": "u=1, i"
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def spinner_loading(text, duration=1.5):
    spinner = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(f'\r{Fore.CYAN}{spinner[i % len(spinner)]} {text}{Fore.RESET}')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write(f'\r{Fore.GREEN}✔ {text}{Fore.RESET}\n')
    sys.stdout.flush()

def print_banner():
    banner = f"""
{Fore.CYAN}{'='*40}
{Fore.YELLOW}{Style.BRIGHT}              🚀 DATAMINER 🚀
{Fore.CYAN}{'='*40}
{Fore.GREEN}TG          : {Fore.LIGHTWHITE_EX}https://t.me/+f3QBLkR5D8k4YzNl
{Fore.GREEN}SCRIPTMAKER : {Fore.LIGHTWHITE_EX}MoneyMaker_w
{Fore.CYAN}{'='*40}{Style.RESET_ALL}
"""
    print(banner)

def get_init_data():
    print(f"{Fore.YELLOW}📝 Masukkan Telegram Init Data :")
    print(f"{Fore.LIGHTBLACK_EX}Contoh : query_id=AAFfrZMo...&hash=99f99cc...{Fore.RESET}")
    print(f"{Fore.LIGHTBLACK_EX}(Copy dari header x-telegram-init-data di DevTools){Fore.RESET}")
    print("-" * 60)
    init_data = input(f"{Fore.GREEN}➜ {Fore.RESET}").strip()
    if not init_data:
        print(f"{Fore.RED}❌ Init data tidak boleh kosong !{Fore.RESET}")
        return None
    return init_data

def get_user_info(headers):
    url = f"{BASE_URL}/auth"
    spinner_loading("⏳ Mengambil data user ...", 2.0)
    try:
        response = requests.post(url, headers=headers, json={}, timeout=10)
        data = response.json()
        if data.get('success'):
            user = data.get('user', {})
            settings = data.get('settings', {})
            print(f"\n{Fore.GREEN}{'='*60}")
            print(f"{Fore.CYAN}👤 Nama      : {Fore.WHITE}{user.get('displayName', 'N/A')}")
            print(f"{Fore.CYAN}📛 Username  : {Fore.WHITE}@{user.get('username', 'N/A')}")
            print(f"{Fore.CYAN}🆔 ID        : {Fore.WHITE}{user.get('telegramId', 'N/A')}")
            print(f"{Fore.CYAN}💰 Balance   : {Fore.GREEN}{user.get('miningBalance', 0):.4f} {settings.get('coinSymbol', 'DATA')}")
            print(f"{Fore.CYAN}⚡ Hashrate  : {Fore.WHITE}{user.get('hashrate', 0)} H/s")
            print(f"{Fore.CYAN}📊 Level     : {Fore.YELLOW}{user.get('level', 1)}")
            print(f"{Fore.CYAN}🎯 Referral  : {Fore.WHITE}{user.get('referralCode', 'N/A')}")
            status = "Active" if user.get('isMiningActive') else "Inactive"
            status_color = Fore.GREEN if user.get('isMiningActive') else Fore.RED
            print(f"{Fore.CYAN}🏷️  Status    : {status_color}{status}{Fore.RESET}")
            print(f"{Fore.GREEN}{'='*60}\n")
            return user
        else:
            print(f"{Fore.RED}❌ Gagal mengambil data user !{Fore.RESET}")
            return None
    except Exception as e:
        print(f"{Fore.RED}❌ Error : {e}{Fore.RESET}")
        return None

def claim_mining(headers, amount=0.02289):
    url = f"{BASE_URL}/user/claim-mining"
    payload = {"claimedAmount": amount}
    spinner_loading("⏳ Proses claim ...", 1.0)
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        data = response.json()
        if data.get('success'):
            balance = data.get('miningBalance', 0)
            message = data.get('message', '')
            unclaimed = data.get('unclaimedMined', 0)
            print(f"{Fore.GREEN}✅ {message}")
            print(f"{Fore.CYAN}💰 Balance : {Fore.GREEN}{balance:.4f} DATA")
            if unclaimed > 0:
                print(f"{Fore.YELLOW}⏳ Unclaimed : {unclaimed:.4f} DATA")
            return True, balance
        else:
            print(f"{Fore.RED}❌ Claim gagal : {data}")
            return False, 0
    except Exception as e:
        print(f"{Fore.RED}❌ Error claim : {e}")
        return False, 0

def watch_ad(headers):
    """Nonton iklan otomatis, return (success, data)"""
    url = f"{BASE_URL}/user/watch-ad-task"
    spinner_loading("⏳ Nonton iklan ...", 0.8)
    try:
        response = requests.post(url, headers=headers, json={}, timeout=10)
        data = response.json()
        if data.get('success'):
            reward = data.get('reward', 0)
            balance = data.get('miningBalance', 0)
            watched = data.get('adsTaskWatched', 0)
            limit = data.get('adsTaskLimit', 10)
            remaining = data.get('remaining', 0)
            print(f"{Fore.GREEN}✅ Berhasil nonton iklan ! Reward : +{reward} DATA")
            print(f"{Fore.CYAN}💰 Balance : {Fore.GREEN}{balance:.4f} DATA")
            print(f"{Fore.YELLOW}📺 Iklan : {watched}/{limit} (sisa {remaining})")
            return True, data
        else:
            # Jika gagal, mungkin karena limit atau error
            error_msg = data.get('message', 'Unknown error')
            if 'limit' in error_msg.lower() or 'remaining' in error_msg.lower():
                print(f"{Fore.YELLOW}⚠️ Iklan habis atau sedang dalam periode tunggu")
            else:
                print(f"{Fore.RED}❌ Gagal nonton iklan : {error_msg}")
            return False, None
    except Exception as e:
        print(f"{Fore.RED}❌ Error watch ad : {e}")
        return False, None

def countdown_timer(seconds):
    print(f"{Fore.YELLOW}⏳ Menunggu claim berikutnya ...{Fore.RESET}")
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
    HEADERS["x-telegram-init-data"] = init_data
    clear_screen()
    print_banner()
    user = get_user_info(HEADERS)
    if not user:
        print(f"\n{Fore.RED}❌ Gagal memulai bot. Cek init data Anda !{Fore.RESET}")
        return
    INTERVAL = 300  # 5 menit
    claim_count = 0
    total_claimed = 0
    print(f"\n{Fore.GREEN}✅ Bot berjalan ! Claim setiap {INTERVAL//60} menit")
    print(f"{Fore.YELLOW}💡 Tekan Ctrl+C untuk berhenti{Fore.RESET}\n")
    while True:
        try:
            claim_count += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"{Fore.CYAN}{'='*60}")
            print(f"{Fore.WHITE}[{current_time}] {Fore.YELLOW}🔄 Claim #{claim_count}")
            print(f"{Fore.CYAN}{'='*60}")
            # Claim mining
            success, balance = claim_mining(HEADERS)
            if success:
                total_claimed += 0.02289
                print(f"{Fore.MAGENTA}📊 Total Claim : {total_claimed:.4f} DATA")
            # Watch ads loop sampai habis
            print(f"\n{Fore.CYAN}📺 Memulai Watch Ads ...{Fore.RESET}")
            ads_remaining = None
            while True:
                ad_success, ad_data = watch_ad(HEADERS)
                if ad_success and ad_data:
                    ads_remaining = ad_data.get('remaining', 0)
                    if ads_remaining <= 0:
                        print(f"{Fore.GREEN}✅ Semua iklan selesai!{Fore.RESET}")
                        break
                    else:
                        print(f"{Fore.YELLOW}⏳ Sisa iklan: {ads_remaining}, tunggu 5 detik...{Fore.RESET}")
                        time.sleep(5)
                else:
                    # Gagal, mungkin karena limit atau error
                    print(f"{Fore.YELLOW}⏳ Iklan habis atau error, lanjut ke countdown...{Fore.RESET}")
                    break
            print()
            countdown_timer(INTERVAL)
        except KeyboardInterrupt:
            print(f"\n\n{Fore.RED}🛑 Bot dihentikan oleh user{Fore.RESET}")
            print(f"{Fore.CYAN}📊 Total claim : {claim_count} kali")
            print(f"{Fore.CYAN}💰 Total DATA : {total_claimed:.4f} DATA")
            print(f"\n{Fore.GREEN}Terima kasih ! 👋{Fore.RESET}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}❌ Error : {e}")
            print(f"{Fore.YELLOW}⏳ Coba lagi dalam 60 detik ...{Fore.RESET}")
            time.sleep(60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}🛑 Bot dihentikan{Fore.RESET}")
