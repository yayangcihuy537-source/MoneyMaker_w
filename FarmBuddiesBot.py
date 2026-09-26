import time
import json
import os
import sys
import requests
from datetime import datetime

CONFIG_FILE = "config.json"
CURRENT_TOKEN = None
CONFIG = {}
BASE_URL = ""
FARM_FP = ""
DEVICE_ID = ""
INIT_DATA = ""

# --- COLOR PALETTE ---
C_RESET = "\033[0m"
C_BOLD = "\033[1m"
C_GREEN = "\033[1;32m"
C_CYAN = "\033[1;36m"
C_YELLOW = "\033[1;33m"
C_RED = "\033[1;31m"
C_PURPLE = "\033[1;35m"
C_WHITE = "\033[1;97m"
C_DIM = "\033[2m"

def slow_print(text, delay=0.03):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def get_network_info():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=5)
        if res.status_code == 200:
            data = res.json()
            ip = data.get("ip", "Unknown")
            isp = data.get("org", "Unknown ISP")
            city = data.get("city", "Unknown City")
            region = data.get("region", "Unknown Region")
            lokasi = f"{city}, {region}"
            return ip, isp, lokasi
    except Exception:
        pass
    return "127.0.0.1", "Local Network", "Indonesia"

def display_banner():
    ip, isp, lokasi = get_network_info()
    current_time = datetime.now().strftime("%d %B %Y | %H:%M:%S WIB")

    print(f"{C_CYAN}╔════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_CYAN}{C_BOLD} ____  _   _ ____  ____ ___ _____ ____  {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_CYAN}{C_BOLD}| __ )| | | |  _ \\|  _ \\_ _| ____/ ___| {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_CYAN}{C_BOLD}|  _ \\| | | | | | | | | | ||  _| \\___ \\ {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_CYAN}{C_BOLD}| |_) | |_| | |_| | |_| | || |___ ___) |{C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_CYAN}{C_BOLD}|____/ \\___/|____/|____/___|_____|____/  {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╠════════════════════════════════════════╣{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_YELLOW}AHD1905 ● SCRIPTYXSOUU ● MONEYMAKER    {C_RESET}{C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_WHITE}IP  : {ip[:30].ljust(30)}{C_RESET} {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_WHITE}ISP : {isp[:30].ljust(30)}{C_RESET} {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_WHITE}Lokasi: {lokasi[:28].ljust(28)}{C_RESET} {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_WHITE}Waktu : {current_time[:28].ljust(28)}{C_RESET} {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╚════════════════════════════════════════╝{C_RESET}\n")

def print_header(username, usdt, water):
    print(f"{C_CYAN}╔════════════════════════════════════════╗{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_YELLOW}👤 User     :{C_RESET} {username.ljust(24)} {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_GREEN}💰 Saldo    :{C_RESET} {f'{usdt} USDT'.ljust(24)} {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}║{C_RESET} {C_CYAN}💧 Air Kebun:{C_RESET} {water.ljust(24)} {C_CYAN}║{C_RESET}")
    print(f"{C_CYAN}╚════════════════════════════════════════╝{C_RESET}")
    print(f" {C_YELLOW}📜 LIVE PROCESS LOGS:{C_RESET}")
    print(f"{C_DIM}──────────────────────────────────────────{C_RESET}")

def custom_log(msg, username, usdt, water, duration=3):
    lower_msg = msg.lower()
    prefix = "✨ "
    color = C_WHITE
    
    if "water" in lower_msg or "air" in lower_msg or "menyiram" in lower_msg or "💧" in lower_msg:
        prefix = "💧 "
        color = C_CYAN
    elif "corn" in lower_msg or "tanaman" in lower_msg or "plant" in lower_msg or "tanam" in lower_msg or "jagung" in lower_msg or "🌱" in lower_msg:
        prefix = "🌽 "
        color = C_YELLOW
    elif "harvest" in lower_msg or "panen" in lower_msg or "🌿" in lower_msg:
        prefix = "🌾 "
        color = C_GREEN
    elif "ads" in lower_msg or "iklan" in lower_msg or "reward" in lower_msg or "📺" in lower_msg:
        prefix = "📺 "
        color = C_PURPLE
    elif "error" in lower_msg or "gagal" in lower_msg or "❌" in lower_msg:
        prefix = "❌ "
        color = C_RED
    elif "auth" in lower_msg or "token" in lower_msg or "🔑" in lower_msg:
        prefix = "🔑 "
        color = C_YELLOW
        
    clean_msg = msg.replace("💧", "").replace("🌱", "").replace("🌿", "").replace("✨", "").replace("❌", "").replace("🔑", "").replace("🎉", "").strip()
    final_msg = f"{prefix}{clean_msg}"
    
    if len(final_msg) > 40:
        final_msg = final_msg[:37] + "..."
        
    print(f"{C_GREEN}╔════════════════════════════════════════╗{C_RESET}")
    print(f"{C_GREEN}║{C_RESET} {color}{final_msg.ljust(38)}{C_RESET} {C_GREEN}║{C_RESET}")
    print(f"{C_GREEN}╚════════════════════════════════════════╝{C_RESET}")
    
    time.sleep(duration)
    
    # Hapus persis 3 baris log task di bawah
    sys.stdout.write("\033[3A\033[J")

def idle_countdown(seconds, username, usdt, water):
    clock_emojis = ["🕛", "🕐", "🕑", "🕒", "肆", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]
    
    # Cetak kerangka frame idle sekali di awal
    print(f"{C_GREEN}╔════════════════════════════════════════╗{C_RESET}")
    print(f"{C_GREEN}║{C_RESET} \033[38;5;255m⏳ [IDLE] Istirahat... Sisa: 05:00     {C_RESET} {C_GREEN}║{C_RESET}")
    print(f"{C_GREEN}╚════════════════════════════════════════╝{C_RESET}")
    
    for remaining in range(seconds, 0, -1):
        mins, secs = divmod(remaining, 60)
        time_format = f"{mins:02d}:{secs:02d}"
        clock_icon = clock_emojis[remaining % len(clock_emojis)]
        
        # Geser kursor ke atas tepat 3 baris untuk menimpa teks sisa waktu tanpa berkedip
        sys.stdout.write("\033[3A")
        print(f"{C_GREEN}╔════════════════════════════════════════╗{C_RESET}")
        print(f"{C_GREEN}║{C_RESET} {C_WHITE}{clock_icon} [IDLE] Istirahat... Sisa: {time_format}     {C_RESET} {C_GREEN}║{C_RESET}")
        print(f"{C_GREEN}╚════════════════════════════════════════╝{C_RESET}")
        time.sleep(1)
        
    # Bersihkan frame idle setelah selesai
    sys.stdout.write("\033[3A\033[J")

def isi_data():
    os.system("clear" if os.name == "posix" else "cls")
    display_banner()
    print(f"{C_CYAN}┌────────────────────────────────────────┐{C_RESET}")
    print(f"{C_CYAN}│{C_RESET} {C_YELLOW}      SETUP AKUN FARM BUDDIES BOT       {C_RESET}{C_CYAN}│{C_RESET}")
    print(f"{C_CYAN}└────────────────────────────────────────┘{C_RESET}\n")
    
    init_data = input(f"{C_WHITE}➜ Masukkan Telegram init_data: {C_RESET}").strip()
    device_id = input(f"{C_WHITE}➜ Masukkan deviceId: {C_RESET}").strip()
    fingerprint = input(f"{C_WHITE}➜ Masukkan fingerprint: {C_RESET}").strip()

    config_data = {
        "init_data": init_data,
        "device_id": device_id,
        "fingerprint": fingerprint,
        "base_url": "https://farm-buddies-api.htmmo2025.workers.dev/api"
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)
    
    print(f"\n{C_GREEN}✅ Konfigurasi berhasil disimpan!{C_RESET}")
    time.sleep(2)

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://farm-buddies.pages.dev",
        "Referer": "https://farm-buddies.pages.dev/",
        "authorization": f"Bearer {CURRENT_TOKEN}",
        "x-farm-fp": FARM_FP
    }

def authenticate(username="Unknown", usdt="0.00", water="0/10"):
    global CURRENT_TOKEN
    auth_url = f"{BASE_URL}/auth/telegram"
    payload = {
        "initData": INIT_DATA,
        "deviceId": DEVICE_ID,
        "fingerprint": FARM_FP
    }
    try:
        custom_log("[AUTH] Mengautentikasi ulang...", username, usdt, water, duration=2)
        res = requests.post(auth_url, headers={"Content-Type": "application/json"}, json=payload, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if data.get("ok"):
                CURRENT_TOKEN = data.get("token")
                custom_log("[AUTH] Berhasil dapat Token baru!", username, usdt, water, duration=2)
                return True
        custom_log(f"[AUTH] Gagal autentikasi. Status: {res.status_code}", username, usdt, water, duration=2)
    except Exception as e:
        custom_log(f"[AUTH] Error: {e}", username, usdt, water, duration=2)
    return False

def make_request(method, endpoint, json_payload=None, username="Unknown", usdt="0.00", water="0/10"):
    global CURRENT_TOKEN
    if not CURRENT_TOKEN:
        if not authenticate(username, usdt, water):
            return None

    url = f"{BASE_URL}{endpoint}"
    try:
        if method.lower() == "get":
            res = requests.get(url, headers=get_headers(), timeout=15)
        elif method.lower() == "post":
            res = requests.post(url, headers=get_headers(), json=json_payload, timeout=15)
        else:
            return None

        if res.status_code == 401:
            custom_log("[AUTH] Token kedaluwarsa. Memperbarui...", username, usdt, water, duration=2)
            if authenticate(username, usdt, water):
                if method.lower() == "get":
                    res = requests.get(url, headers=get_headers(), timeout=15)
                elif method.lower() == "post":
                    res = requests.post(url, headers=get_headers(), json=json_payload, timeout=15)
            else:
                return None
        return res
    except Exception as e:
        custom_log(f"Request error: {e}", username, usdt, water, duration=2)
        return None

def fetch_bootstrap():
    res = make_request("get", "/user/bootstrap")
    if res and res.status_code == 200:
        data = res.json()
        if data.get("ok"):
            profile = data.get("profile", {})
            farm = data.get("farm", {})
            username = profile.get("username", "Unknown")
            usdt = str(profile.get("usdt", "0.00"))
            water = f"{farm.get('water')}/{farm.get('waterMax')}"
            return data, username, usdt, water
    return None, "Unknown", "0.00", "0/10"

def get_best_crop(bootstrap_data):
    try:
        crops = bootstrap_data.get("farm", {}).get("crops", [])
        unlocked_crops = [c for c in crops if not c.get("locked", True)]
        if unlocked_crops:
            best_crop = max(unlocked_crops, key=lambda x: x.get("payout", 0))
            return best_crop.get("id", "corn")
    except Exception:
        pass
    return "corn"

def process_plant_action(plot_idx, bootstrap_data, username, usdt, water):
    best_crop = get_best_crop(bootstrap_data)
    payload = {"idx": plot_idx, "crop": best_crop}
    res = make_request("post", "/farm/plant", payload, username, usdt, water)
    if res and res.status_code == 200 and res.json().get("ok"):
        custom_log(f"[PLANT] Tanam {best_crop.upper()} di Plot [{plot_idx}]!", username, usdt, water, duration=3)
        return True
    return False

def process_water_action(bootstrap_data, username, usdt, water):
    farm_info = bootstrap_data.get("farm", {})
    plots = farm_info.get("plots", [])
    current_water = farm_info.get("water", 0)

    if current_water <= 0:
        return False

    for plot in plots:
        idx = plot.get("idx")
        state = plot.get("state")
        watered = plot.get("watered", False)

        if state in ["growing", "ready"] and not watered:
            custom_log(f"[WATER] Plot [{idx}] belum disiram...", username, usdt, water, duration=2)
            res = make_request("post", "/farm/water", {"idx": idx}, username, usdt, water)
            if res and res.status_code == 200 and res.json().get("ok"):
                custom_log(f"[WATER] Sukses siram Plot [{idx}]!", username, usdt, water, duration=3)
                return True
    return False

def process_farm_ads_flow(username, usdt, water):
    res_session = make_request("post", "/ads/farm/session", {"ref": "water"}, username, usdt, water)
    if not res_session:
        return False
    if res_session.status_code == 409:
        return "COOLDOWN"
    if res_session.status_code != 200:
        return False

    data_session = res_session.json()
    if not data_session.get("ok"):
        return False

    session_id = data_session.get("sessionId")
    min_watch = data_session.get("minWatchSec", 6)
    custom_log(f"[REFILL] Nonton iklan air ({min_watch} dtk)...", username, usdt, water, duration=min_watch)

    complete_payload = {"sessionId": session_id, "ref": "water", "provider": "adsgram", "clicked": True, "adsgramClicked": False}
    res_complete = make_request("post", "/ads/farm/complete", complete_payload, username, usdt, water)
    if res_complete and res_complete.status_code == 200 and res_complete.json().get("ok"):
        custom_log("[REFILL] Air kebun terisi penuh!", username, usdt, water, duration=3)
        return True
    return False

def process_harvest_flow(plot_idx, username, usdt, water):
    res_session = make_request("post", "/ads/harvest/session", {"idx": plot_idx}, username, usdt, water)
    if not res_session:
        return False
    if res_session.status_code == 409:
        return "COOLDOWN"
    if res_session.status_code != 200:
        return False

    data_session = res_session.json()
    if not data_session.get("ok"):
        return False

    session_id = data_session.get("sessionId")
    min_watch = data_session.get("minWatchSec", 8)
    custom_log(f"[HARVEST] Nonton iklan Plot [{plot_idx}] ({min_watch} dtk)...", username, usdt, water, duration=min_watch)

    complete_payload = {"sessionId": session_id, "provider": "adsgram", "clicked": True, "adsgramClicked": False}
    res_complete = make_request("post", "/ads/harvest/complete", complete_payload, username, usdt, water)
    if res_complete and res_complete.status_code == 200 and res_complete.json().get("ok"):
        custom_log(f"[HARVEST] Panen Plot [{plot_idx}] sukses!", username, usdt, water, duration=3)
        return True
    return False

def process_ad_flow(task_id, task_title, username, usdt, water):
    res_session = make_request("post", f"/ads/task/{task_id}/session", {"slotIndex": -1}, username, usdt, water)
    if not res_session:
        return False
    if res_session.status_code == 409:
        return "COOLDOWN"
    if res_session.status_code != 200:
        return False

    data_session = res_session.json()
    if not data_session.get("ok"):
        return False

    session_id = data_session.get("sessionId")
    min_watch = data_session.get("minWatchSec", 8)
    custom_log(f"[TASK] Nonton [{task_title}] ({min_watch} dtk)...", username, usdt, water, duration=min_watch)

    complete_payload = {
        "sessionId": session_id,
        "slotIndex": data_session.get("slotIndex", 0),
        "provider": data_session.get("provider", "adsgram"),
        "clicked": True,
        "adsgramClicked": False
    }
    res_complete = make_request("post", f"/ads/task/{task_id}/complete", complete_payload, username, usdt, water)
    if res_complete and res_complete.status_code == 200 and res_complete.json().get("ok"):
        custom_log(f"[TASK] Sukses klaim [{task_title}]!", username, usdt, water, duration=3)
        return True
    return False

def run_smart_scanner(bootstrap_data, username, usdt, water):
    if not bootstrap_data:
        return False

    farm_info = bootstrap_data.get("farm", {})
    plots = farm_info.get("plots", [])

    for plot in plots:
        idx = plot.get("idx")
        if plot.get("state") == "empty" and not plot.get("locked", False):
            if process_plant_action(idx, bootstrap_data, username, usdt, water):
                return True

    if process_water_action(bootstrap_data, username, usdt, water):
        return True

    if farm_info.get("water", 0) == 0:
        res = process_farm_ads_flow(username, usdt, water)
        if res is True:
            return True
        elif res == "COOLDOWN":
            time.sleep(2)

    for plot in plots:
        idx = plot.get("idx")
        if plot.get("state") == "ready" and plot.get("adsDone", 0) < plot.get("adsNeeded", 0):
            res = process_harvest_flow(idx, username, usdt, water)
            if res is True:
                return True
            elif res == "COOLDOWN":
                time.sleep(2)

    tasks_data = bootstrap_data.get("tasks", [])
    ad_tasks = [t for t in tasks_data if t.get("type") == "ad"] if isinstance(tasks_data, list) else []

    all_ads_limit_reached = all(t.get("progress", 0) >= t.get("target", 20) for t in ad_tasks) if ad_tasks else True

    if all_ads_limit_reached:
        return False

    for task in ad_tasks:
        task_id = task.get("id")
        title = task.get("title", "Ad Task")
        target = task.get("target", 20)
        progress = task.get("progress", 0)

        if progress >= target:
            continue

        result = process_ad_flow(task_id, title, username, usdt, water)
        if result is True:
            return True
        elif result == "COOLDOWN":
            time.sleep(2)
            continue

    return False

def run_bot():
    global BASE_URL, FARM_FP, DEVICE_ID, INIT_DATA
    BASE_URL = CONFIG.get("base_url", "https://farm-buddies-api.htmmo2025.workers.dev/api")
    FARM_FP = CONFIG.get("fingerprint", "")
    DEVICE_ID = CONFIG.get("device_id", "")
    INIT_DATA = CONFIG.get("init_data", "")

    bootstrap_data, username, usdt, water = fetch_bootstrap()
    if not authenticate(username, usdt, water):
        return

    # Clear layar SEKALI SAJA di awal agar banner tetap di atas secara permanen
    os.system("clear" if os.name == "posix" else "cls")
    display_banner()
    print_header(username, usdt, water)
    
    while True:
        try:
            bootstrap_data, username, usdt, water = fetch_bootstrap()
            
            if bootstrap_data:
                # Perbarui info header di tempatnya tanpa kedip
                sys.stdout.write("\033[6A")
                print_header(username, usdt, water)
                
                success_action = run_smart_scanner(bootstrap_data, username, usdt, water)
                
                if not success_action:
                    idle_countdown(300, username, usdt, water)
                else:
                    time.sleep(1)
            else:
                custom_log("[WARNING] Gagal sync server. Coba 10 dtk...", "Unknown", "0.00", "0/10", duration=10)
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            time.sleep(30)

def main():
    while True:
        os.system("clear" if os.name == "posix" else "cls")
        display_banner()
        
        slow_print(f"{C_WHITE}Sebelum menjalankan scriptnya mari kita berdoa kepada TUHAN YANG MAHA ESA agar di beri rezeki lebih untuk mencukupi kebutuhan sehari-hari dan beramal{C_RESET}", 0.015)
        slow_print(f"{C_YELLOW}#SAVEPALESTINE{C_RESET}\n", 0.02)
        
        print(f"{C_CYAN}Panel Menu :{C_RESET}")
        print(f"{C_CYAN}1.{C_RESET} Jalankan Bot 🚀")
        print(f"{C_CYAN}2.{C_RESET} Config 📋")
        print(f"{C_CYAN}3.{C_RESET} Hapus 🧹")
        print(f"{C_CYAN}0.{C_RESET} Exit 🚪\n")
        
        pilihan = input(f"{C_WHITE}Pilih menu ➜ {C_RESET}").strip()
        
        if pilihan == "1":
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    global CONFIG
                    CONFIG = json.load(f)
                run_bot()
            else:
                print(f"\n{C_RED}❌ Data belum diisi! Pilih menu 2 dulu.{C_RESET}")
                time.sleep(2)
        elif pilihan == "2":
            isi_data()
        elif pilihan == "3":
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
                print(f"\n{C_GREEN}✅ Data berhasil dihapus!{C_RESET}")
            else:
                print(f"\n{C_YELLOW}⚠️ Tidak ada data untuk dihapus.{C_RESET}")
            time.sleep(2)
        elif pilihan == "0":
            print(f"\n{C_CYAN}Terima kasih, selamat istirahat wak!{C_RESET}\n")
            sys.exit(0)
        else:
            print(f"\n{C_RED}❌ Pilihan tidak valid!{C_RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()


#Created by AHD1905 
