import requests
import json
import time
import os
import sys
import random

# ================================
# IMPORT COLORAMA (WAJIB UNTUK WARNA)
# ================================
try:
    from colorama import init, Fore, Back, Style
    init(autoreset=True)
    COLOR_ENABLED = True
except ImportError:
    print("[!] Warna tidak aktif. Install 'colorama' dengan: pip install colorama")
    class Fore: RED=''; GREEN=''; YELLOW=''; BLUE=''; RESET=''
    class Style: RESET_ALL=''
    COLOR_ENABLED = False

def color_text(text, color):
    if COLOR_ENABLED:
        return f"{color}{text}{Style.RESET_ALL}"
    return text

# ================================
# BANNER & MENU
# ================================
BANNER = r"""
╔══════════════════════════════════════════════╗
║   ██████╗ ██████╗  █████╗ ███╗   ███╗        ║
║  ██╔════╝ ██╔══██╗██╔══██╗████╗ ████║        ║
║  ██║  ███╗██████╔╝███████║██╔████╔██║        ║
║  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║        ║
║  ╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║        ║
║   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝        ║
║                                              ║
║  ███████╗██╗   ██╗██████╗ ███████╗          ║
║  ██╔════╝██║   ██║██╔══██╗██╔════╝          ║
║  ███████╗██║   ██║██████╔╝█████╗            ║
║  ╚════██║██║   ██║██╔══██╗██╔══╝            ║
║  ███████║╚██████╔╝██║  ██║██║               ║
║  ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝               ║
╠══════════════════════════════════════════════╣
║          ⚡ AUTO FARMING BOT ⚡             ║
║         Developer : ScriptyXSouu            ║
╚══════════════════════════════════════════════╝
"""

MENU = f"""
{color_text("╔══════════════════════════════════════════════╗", Fore.GREEN)}
{color_text("║  [1] ▶  START FARMING (Auto Ads + Task)     ║", Fore.GREEN)}
{color_text("║  [2] 🔑  SET InitData & Cookie              ║", Fore.GREEN)}
{color_text("║  [3] 💰  CHECK BALANCE                      ║", Fore.GREEN)}
{color_text("║  [4] 📅  DAILY BONUS (Check & Claim)        ║", Fore.GREEN)}
{color_text("║  [0] ❌  EXIT                               ║", Fore.GREEN)}
{color_text("╚══════════════════════════════════════════════╝", Fore.GREEN)}
"""

# ================================
# KONFIGURASI
# ================================
BASE_URL = "https://gram.surf"
CONFIG_FILE = "config.json"

PHPSESSID = ""
INIT_DATA = ""

HEADERS = {
    "Host": "gram.surf",
    "Content-Type": "application/json",
    "X-TG-Auth": "",
    "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.6.4 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
    "Accept": "*/*",
    "Origin": "https://gram.surf",
    "X-Requested-With": "org.telegram.messenger.web",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://gram.surf/",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Cookie": ""
}

def load_config():
    global PHPSESSID, INIT_DATA
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                PHPSESSID = data.get('phpsessid', '')
                INIT_DATA = data.get('init_data', '')
                update_headers()
                print(color_text("[✓] Konfigurasi dimuat dari file.", Fore.GREEN))
                return True
        except:
            print(color_text("[!] Gagal baca config, gunakan default.", Fore.RED))
            return False
    else:
        print(color_text("[!] File config tidak ditemukan. Gunakan menu 2 untuk setting.", Fore.YELLOW))
        return False

def save_config():
    data = {'phpsessid': PHPSESSID, 'init_data': INIT_DATA}
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(color_text("[✓] Konfigurasi disimpan.", Fore.GREEN))
    except:
        print(color_text("[!] Gagal simpan config.", Fore.RED))

def update_headers():
    HEADERS["X-TG-Auth"] = INIT_DATA
    HEADERS["Cookie"] = f"PHPSESSID={PHPSESSID}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear_screen()
    print(BANNER)
    print(MENU)

def ajax_request(action, data=None):
    url = f"{BASE_URL}/ajax.php?action={action}"
    payload = json.dumps(data) if data else "{}"
    try:
        resp = requests.post(url, headers=HEADERS, data=payload, timeout=15)
        return resp.json()
    except Exception as e:
        print(color_text(f"[!] Error request: {e}", Fore.RED))
        return None

def check_init_data_valid():
    res = ajax_request("ad_manager&mode=balance")
    if res is None:
        return False
    if res.get("success") == True:
        return True
    return False

def get_balance():
    res = ajax_request("ad_manager&mode=balance")
    if res and res.get("success"):
        user = res.get("user", {})
        bal = user.get("balance", 0)
        gram = user.get("balance_gram", "0.00")
        print(color_text(f"\n💰 Balance: {bal} coins", Fore.GREEN))
        print(color_text(f"💎 GRAM: {gram}", Fore.YELLOW))
        return bal
    else:
        print(color_text("[!] Gagal ambil balance. Mungkin init_data kadaluarsa.", Fore.RED))
        return None

# ================================
# FARMING FUNCTIONS
# ================================
def farm_regular_provider(provider):
    """Untuk adsgram, monetag, onclicka (butuh start_ad dan view_token)"""
    print(color_text(f"\n[+] Farming {provider.upper()}...", Fore.BLUE))
    start_res = ajax_request("ad_manager&mode=start_ad", {"type": provider})
    if not start_res or not start_res.get("success"):
        msg = start_res.get('message', 'Unknown error') if start_res else 'No response'
        print(color_text(f"[!] Gagal start ad {provider}: {msg}", Fore.RED))
        if "too many requests" in msg.lower():
            return "too_many_requests"
        return False
    view_token = start_res.get("view_token")
    if not view_token:
        print(color_text(f"[!] No view_token for {provider}", Fore.RED))
        return False
    print(color_text(f"[+] View token: {view_token[:20]}...", Fore.YELLOW))
    
    watch_time = random.randint(17, 21)
    print(color_text(f"[+] Menonton iklan selama {watch_time} detik...", Fore.YELLOW))
    time.sleep(watch_time)
    
    success_res = ajax_request("ad_manager&mode=success", {
        "type": provider,
        "view_token": view_token
    })
    if success_res and success_res.get("success"):
        reward = success_res.get("new_reward", 0)
        current = success_res.get("current_count", 0)
        max_ads = success_res.get("max_ads", 25)
        print(color_text(f"[✓] +{reward} coins ({current}/{max_ads})", Fore.GREEN))
        return True
    else:
        msg = success_res.get('message', 'Unknown error') if success_res else 'No response'
        print(color_text(f"[!] Gagal claim: {msg}", Fore.RED))
        return False

def farm_adsgram_task():
    """Khusus adsgram_task: langsung claim tanpa start_ad"""
    print(color_text(f"\n[+] Farming ADSGRAM_TASK...", Fore.BLUE))
    watch_time = random.randint(17, 21)
    print(color_text(f"[+] Menonton iklan task selama {watch_time} detik...", Fore.YELLOW))
    time.sleep(watch_time)
    
    success_res = ajax_request("ad_manager&mode=success", {"type": "adsgram_task"})
    if success_res and success_res.get("success"):
        reward = success_res.get("new_reward", 0)
        current = success_res.get("current_count", 0)
        max_ads = success_res.get("max_ads", 20)
        print(color_text(f"[✓] +{reward} coins ({current}/{max_ads})", Fore.GREEN))
        return True
    else:
        msg = success_res.get('message', 'Unknown error') if success_res else 'No response'
        print(color_text(f"[!] Gagal claim task: {msg}", Fore.RED))
        return False

def start_farming_loop():
    if not check_init_data_valid():
        print(color_text("[!] InitData tidak valid atau kadaluarsa! Silakan set ulang di menu 2.", Fore.RED))
        return
    
    # Daftar provider: regular + task
    # Format: (nama, fungsi, limit default)
    providers = [
        ("adsgram", farm_regular_provider, 25),
        ("monetag", farm_regular_provider, 25),
        ("onclicka", farm_regular_provider, 25),
        ("adsgram_task", farm_adsgram_task, 20)
    ]
    
    total_earned = 0
    cycle_count = 0
    print(color_text("\n[+] Auto Farming started... (CTRL+C to stop)", Fore.GREEN))
    try:
        while True:
            cycle_count += 1
            print(color_text(f"\n--- CYCLE {cycle_count} ---", Fore.BLUE))
            success_any = False
            
            for name, func, default_limit in providers:
                # Cek status provider
                check_res = ajax_request("ad_manager&mode=check", {"type": name})
                if check_res and check_res.get("disabled") == True:
                    print(color_text(f"[!] {name.upper()} disabled", Fore.YELLOW))
                    delay = random.randint(7, 14)
                    print(color_text(f"[+] Jeda {delay} detik sebelum provider berikutnya...", Fore.YELLOW))
                    time.sleep(delay)
                    continue
                
                current = check_res.get("current_count", 0) if check_res else 0
                max_ads = check_res.get("max_ads", default_limit) if check_res else default_limit
                if current >= max_ads:
                    print(color_text(f"[!] {name.upper()} sudah mencapai limit ({current}/{max_ads})", Fore.YELLOW))
                    delay = random.randint(7, 14)
                    print(color_text(f"[+] Jeda {delay} detik sebelum provider berikutnya...", Fore.YELLOW))
                    time.sleep(delay)
                    continue
                
                # Eksekusi farming
                success = False
                retry_count = 0
                max_retry = 3
                while not success and retry_count < max_retry:
                    if name == "adsgram_task":
                        result = func()  # langsung claim
                    else:
                        result = func(name)
                    
                    if result == True:
                        success = True
                        reward = check_res.get("reward", 0) if check_res else 0
                        total_earned += reward
                        success_any = True
                        break
                    elif result == "too_many_requests" and name != "adsgram_task":
                        retry_count += 1
                        if retry_count < max_retry:
                            delay = random.randint(45, 60)
                            print(color_text(f"[!] Too many requests, menunggu {delay} detik lalu retry ({retry_count}/{max_retry})...", Fore.RED))
                            time.sleep(delay)
                        else:
                            print(color_text(f"[!] Gagal setelah {max_retry} kali percobaan, skip {name}.", Fore.RED))
                    else:
                        # gagal selain too many requests, tidak retry
                        break
                
                # Jeda antar provider 7-14 detik
                delay = random.randint(7, 14)
                print(color_text(f"[+] Jeda {delay} detik sebelum provider berikutnya...", Fore.YELLOW))
                time.sleep(delay)
            
            # Tampilkan progress
            total_ads = 0
            for name, _, default_limit in providers:
                check_res = ajax_request("ad_manager&mode=check", {"type": name})
                if check_res:
                    cur = check_res.get("current_count", 0)
                    max_ = check_res.get("max_ads", default_limit)
                    total_ads += cur
            print(color_text(f"\n📊 Progress: {total_ads}/95 total ads completed", Fore.CYAN))
            get_balance()
            
            if not success_any:
                print(color_text("[!] Tidak ada iklan yang tersisa. Cek limit atau tunggu reset.", Fore.YELLOW))
                break
            
            # Jeda antar cycle 7-14 detik
            cycle_delay = random.randint(7, 14)
            print(color_text(f"[+] Jeda antar cycle {cycle_delay} detik...", Fore.YELLOW))
            time.sleep(cycle_delay)
            
    except KeyboardInterrupt:
        print(color_text("\n[!] Farming dihentikan oleh user.", Fore.RED))
    finally:
        print(color_text(f"[+] Total earned di sesi ini: {total_earned} coins", Fore.GREEN))

# ================================
# DAILY BONUS
# ================================
def check_daily_bonus():
    res = ajax_request("bonus_manager&mode=check_daily")
    if res and res.get("success"):
        return res
    else:
        print(color_text("[!] Gagal cek daily bonus.", Fore.RED))
        return None

def claim_daily_bonus():
    print(color_text("\n[📅] Claiming Daily Bonus...", Fore.BLUE))
    watch_time = random.randint(17, 21)
    print(color_text(f"[+] Menonton video daily selama {watch_time} detik...", Fore.YELLOW))
    time.sleep(watch_time)
    
    res = ajax_request("bonus_manager&mode=claim_daily")
    if res and res.get("success"):
        reward = res.get("reward", 0)
        new_streak = res.get("new_streak", 0)
        seconds_to_next = res.get("seconds_to_next", 0)
        print(color_text(f"[✓] Daily bonus claimed! +{reward} coins", Fore.GREEN))
        print(color_text(f"   Streak sekarang: {new_streak}", Fore.YELLOW))
        if seconds_to_next > 0:
            h = seconds_to_next // 3600
            m = (seconds_to_next % 3600) // 60
            s = seconds_to_next % 60
            print(color_text(f"   Waktu hingga daily berikutnya: {h:02d}:{m:02d}:{s:02d}", Fore.YELLOW))
        return True
    else:
        msg = res.get('message', 'Unknown error') if res else 'No response'
        print(color_text(f"[!] Gagal claim daily: {msg}", Fore.RED))
        return False

def daily_bonus_menu():
    print(color_text("\n[📅] DAILY BONUS", Fore.BLUE))
    status = check_daily_bonus()
    if not status:
        return
    
    streak = status.get("streak", 0)
    can_claim = status.get("can_claim", False)
    rewards_list = status.get("rewards_list", [])
    seconds_to_next = status.get("seconds_to_next", 0)
    
    print(color_text(f"   Streak saat ini: {streak}", Fore.YELLOW))
    if rewards_list:
        next_reward = rewards_list[streak] if streak < len(rewards_list) else rewards_list[-1]
        print(color_text(f"   Reward hari berikutnya: +{next_reward} coins", Fore.CYAN))
        reward_str = " → ".join([str(r) for r in rewards_list])
        print(color_text(f"   Reward list: {reward_str}", Fore.CYAN))
    
    if can_claim:
        print(color_text("\n[✓] Daily bonus siap di-claim!", Fore.GREEN))
        confirm = input(color_text("Claim sekarang? (y/n): ", Fore.YELLOW)).strip().lower()
        if confirm == 'y':
            claim_daily_bonus()
            get_balance()
        else:
            print(color_text("[!] Dibatalkan.", Fore.RED))
    else:
        if seconds_to_next > 0:
            h = seconds_to_next // 3600
            m = (seconds_to_next % 3600) // 60
            s = seconds_to_next % 60
            print(color_text(f"\n[⏳] Daily berikutnya tersedia dalam: {h:02d}:{m:02d}:{s:02d}", Fore.YELLOW))
        else:
            print(color_text("\n[!] Daily tidak tersedia saat ini.", Fore.RED))

# ================================
# SET INITDATA
# ================================
def set_initdata():
    global INIT_DATA, PHPSESSID
    print(color_text("\n[🔑] SET InitData & Cookie", Fore.BLUE))
    new_init = input(color_text("InitData (kosong = tetap): ", Fore.YELLOW)).strip()
    if new_init:
        INIT_DATA = new_init
    new_cookie = input(color_text("PHPSESSID (kosong = tetap): ", Fore.YELLOW)).strip()
    if new_cookie:
        PHPSESSID = new_cookie
    update_headers()
    save_config()
    if check_init_data_valid():
        print(color_text("[✓] InitData valid!", Fore.GREEN))
    else:
        print(color_text("[!] InitData tidak valid! Periksa kembali.", Fore.RED))

# ================================
# MAIN
# ================================
def main():
    load_config()
    if not PHPSESSID or not INIT_DATA:
        print(color_text("[!] Belum ada konfigurasi. Silakan set di menu 2.", Fore.YELLOW))
    
    while True:
        print_banner()
        choice = input(color_text("Pilih menu: ", Fore.BLUE)).strip()
        if choice == "1":
            start_farming_loop()
            input(color_text("\nTekan Enter untuk kembali...", Fore.YELLOW))
        elif choice == "2":
            set_initdata()
            input(color_text("\nTekan Enter untuk kembali...", Fore.YELLOW))
        elif choice == "3":
            get_balance()
            input(color_text("\nTekan Enter untuk kembali...", Fore.YELLOW))
        elif choice == "4":
            daily_bonus_menu()
            input(color_text("\nTekan Enter untuk kembali...", Fore.YELLOW))
        elif choice == "0":
            print(color_text("\n[+] Goodbye!", Fore.GREEN))
            sys.exit(0)
        else:
            print(color_text("[!] Pilihan tidak valid.", Fore.RED))
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(color_text("\n[+] Exiting.", Fore.GREEN))
        sys.exit(0)
