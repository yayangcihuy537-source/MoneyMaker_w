import time
import json
import os
import sys
import requests

CONFIG_FILE = "config.json"
CURRENT_TOKEN = None
CONFIG = {}
BASE_URL = ""
FARM_FP = ""
DEVICE_ID = ""
INIT_DATA = ""

def display_banner():
    os.system("clear" if os.name == "posix" else "cls")
    print("\033[1;32m")
    print(r"""  ____  _   _ ____  ____ ___ _____ ____  
 | __ )| | | |  _ \|  _ \_ _| ____/ ___| 
 |  _ \| | | | | | | | | | ||  _| \___ \ 
 | |_) | |_| | |_| | |_| | || |___ ___) |
 |____/ \___/|____/|____/___|_____|____/ """)
    print("\033[1;31mScript by AHD1905\033[0m")
    print("\033[0;37m--------------------------------------------------\033[0m\n")

def custom_log(msg):
    lower_msg = msg.lower()
    prefix = "✨ "
    if "water" in lower_msg or "air" in lower_msg or "menyiram" in lower_msg or "💧" in lower_msg:
        prefix = "💧 "
    elif "corn" in lower_msg or "tanaman" in lower_msg or "plant" in lower_msg or "tanam" in lower_msg or "jagung" in lower_msg or "🌱" in lower_msg:
        prefix = "🌽 "
    elif "harvest" in lower_msg or "panen" in lower_msg or "🌿" in lower_msg:
        prefix = "🌾 "
    elif "ads" in lower_msg or "iklan" in lower_msg or "reward" in lower_msg or "📺" in lower_msg:
        prefix = "📺 "
    elif "error" in lower_msg or "gagal" in lower_msg or "❌" in lower_msg:
        prefix = "❌ "
    elif "auth" in lower_msg or "token" in lower_msg or "🔑" in lower_msg:
        prefix = "🔑 "
        
    clean_msg = msg.replace("💧", "").replace("🌱", "").replace("🌿", "").replace("✨", "").replace("❌", "").replace("🔑", "").replace("🎉", "").strip()
    final_msg = f"{prefix}{clean_msg}"
    
    if len(final_msg) > 68:
        final_msg = final_msg[:65] + "..."
        
    print("\033[1;32m╔══════════════════════════════════════════════════════════════════════╗\033[0m")
    print(f"\033[1;32m║\033[0m \033[1;97m{final_msg.ljust(68)}\033[0m \033[1;32m║\033[0m")
    print("\033[1;32m╚══════════════════════════════════════════════════════════════════════╝\033[0m")

def isi_data():
    display_banner()
    print("="*50)
    print("      SETUP AKUN FARM BUDDIES BOT")
    print("="*50)
    init_data = input("Masukkan Telegram init_data / query_id: ").strip()
    device_id = input("Masukkan deviceId (contoh: dev_...): ").strip()
    fingerprint = input("Masukkan fingerprint/x-farm-fp: ").strip()

    config_data = {
        "init_data": init_data,
        "device_id": device_id,
        "fingerprint": fingerprint,
        "base_url": "https://farm-buddies-api.htmmo2025.workers.dev/api"
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config_data, f, indent=4)
    
    print("\n✅ Konfigurasi berhasil disimpan ke config.json!")
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

def authenticate():
    global CURRENT_TOKEN
    auth_url = f"{BASE_URL}/auth/telegram"
    payload = {
        "initData": INIT_DATA,
        "deviceId": DEVICE_ID,
        "fingerprint": FARM_FP
    }
    try:
        custom_log("[AUTH] Mengautentikasi ulang untuk mendapatkan Token baru...")
        res = requests.post(auth_url, headers={"Content-Type": "application/json"}, json=payload, timeout=15)
        if res.status_code == 200:
            data = res.json()
            if data.get("ok"):
                CURRENT_TOKEN = data.get("token")
                custom_log("[AUTH] Berhasil mendapatkan Bearer Token baru!")
                return True
        custom_log(f"[AUTH] Gagal autentikasi. Status: {res.status_code}")
    except Exception as e:
        custom_log(f"[AUTH] Error saat autentikasi: {e}")
    return False

def make_request(method, endpoint, json_payload=None):
    global CURRENT_TOKEN
    if not CURRENT_TOKEN:
        if not authenticate():
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
            custom_log("[AUTH] Token kedaluwarsa. Memperbarui token otomatis...")
            if authenticate():
                if method.lower() == "get":
                    res = requests.get(url, headers=get_headers(), timeout=15)
                elif method.lower() == "post":
                    res = requests.post(url, headers=get_headers(), json=json_payload, timeout=15)
            else:
                return None
        return res
    except Exception as e:
        custom_log(f"Request error ke {endpoint}: {e}")
        return None

def print_header(username, usdt, water):
    display_banner()
    print("\033[1;36m" + "="*54 + "\033[0m")
    print(f" \033[1;33m👤 User      :\033[0m {username}")
    print(f" \033[1;32m💰 Saldo USDT :\033[0m {usdt} USDT")
    print(f" \033[1;34m💧 Air Kebun  :\033[0m {water}")
    print("\033[1;36m" + "-"*54 + "\033[0m")
    print(" \033[1;93m📜 LIVE PROCESS LOGS:\033[0m")
    print("\033[1;36m" + "-"*54 + "\033[0m")

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

def process_plant_action(plot_idx, bootstrap_data):
    best_crop = get_best_crop(bootstrap_data)
    payload = {"idx": plot_idx, "crop": best_crop}
    res = make_request("post", "/farm/plant", payload)
    if res and res.status_code == 200 and res.json().get("ok"):
        custom_log(f"[PLANT] Berhasil menanam {best_crop.upper()} di Plot [{plot_idx}]!")
        time.sleep(2)
        return True
    return False

def process_water_action(bootstrap_data):
    farm_info = bootstrap_data.get("farm", {})
    plots = farm_info.get("plots", [])
    water = farm_info.get("water", 0)

    if water <= 0:
        return False

    for plot in plots:
        idx = plot.get("idx")
        state = plot.get("state")
        watered = plot.get("watered", False)
        name = plot.get("name", "Tanaman")

        if state in ["growing", "ready"] and not watered:
            custom_log(f"[WATER] Plot [{idx}] {name} belum disiram. Menyiram...")
            res = make_request("post", "/farm/water", {"idx": idx})
            if res and res.status_code == 200 and res.json().get("ok"):
                custom_log(f"[WATER] Berhasil menyiram Plot [{idx}] {name}!")
                time.sleep(2)
                return True
    return False

def process_farm_ads_flow():
    res_session = make_request("post", "/ads/farm/session", {"ref": "water"})
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
    custom_log(f"[REFILL WATER] Menonton iklan isi ulang air ({min_watch} dtk)...")
    time.sleep(min_watch + 2)

    complete_payload = {"sessionId": session_id, "ref": "water", "provider": "adsgram", "clicked": True, "adsgramClicked": False}
    res_complete = make_request("post", "/ads/farm/complete", complete_payload)
    if res_complete and res_complete.status_code == 200 and res_complete.json().get("ok"):
        custom_log("[REFILL WATER] Air kebun berhasil diisi ulang penuh!")
        return True
    return False

def process_harvest_flow(plot_idx):
    res_session = make_request("post", "/ads/harvest/session", {"idx": plot_idx})
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
    custom_log(f"[HARVEST] Menonton iklan panen Plot [{plot_idx}] ({min_watch} dtk)...")
    time.sleep(min_watch + 2)

    complete_payload = {"sessionId": session_id, "provider": "adsgram", "clicked": True, "adsgramClicked": False}
    res_complete = make_request("post", "/ads/harvest/complete", complete_payload)
    if res_complete and res_complete.status_code == 200 and res_complete.json().get("ok"):
        custom_log(f"[HARVEST] Berhasil Panen & Klaim Reward Plot [{plot_idx}]!")
        return True
    return False

def process_ad_flow(task_id, task_title):
    res_session = make_request("post", f"/ads/task/{task_id}/session", {"slotIndex": -1})
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
    custom_log(f"[TASK ADS] Menonton [{task_title}] ({min_watch} dtk)...")
    time.sleep(min_watch + 2)

    complete_payload = {
        "sessionId": session_id,
        "slotIndex": data_session.get("slotIndex", 0),
        "provider": data_session.get("provider", "adsgram"),
        "clicked": True,
        "adsgramClicked": False
    }
    res_complete = make_request("post", f"/ads/task/{task_id}/complete", complete_payload)
    if res_complete and res_complete.status_code == 200 and res_complete.json().get("ok"):
        custom_log(f"[TASK ADS] Sukses Klaim Reward [{task_title}]!")
        return True
    return False

def run_smart_scanner(bootstrap_data):
    if not bootstrap_data:
        return False

    farm_info = bootstrap_data.get("farm", {})
    plots = farm_info.get("plots", [])

    for plot in plots:
        idx = plot.get("idx")
        if plot.get("state") == "empty" and not plot.get("locked", False):
            best_crop_name = get_best_crop(bootstrap_data)
            custom_log(f"[INFO] Menemukan Plot Kosong [{idx}]. Menanam: {best_crop_name.upper()}...")
            if process_plant_action(idx, bootstrap_data):
                return True

    if process_water_action(bootstrap_data):
        return True

    if farm_info.get("water", 0) == 0:
        custom_log("[INFO] Air kebun habis (0/10). Mengisi ulang air...")
        res = process_farm_ads_flow()
        if res is True:
            return True
        elif res == "COOLDOWN":
            custom_log("[REFILL WATER] Cooldown, melewati...")
            time.sleep(2)

    for plot in plots:
        idx = plot.get("idx")
        if plot.get("state") == "ready" and plot.get("adsDone", 0) < plot.get("adsNeeded", 0):
            custom_log(f"[INFO] Plot [{idx}] READY. Memproses iklan panen...")
            res = process_harvest_flow(idx)
            if res is True:
                return True
            elif res == "COOLDOWN":
                custom_log(f"[HARVEST Plot {idx}] Cooldown, melewati...")
                time.sleep(2)

    tasks_data = bootstrap_data.get("tasks", [])
    ad_tasks = [t for t in tasks_data if t.get("type") == "ad"]

    all_ads_limit_reached = all(t.get("progress", 0) >= t.get("target", 20) for t in ad_tasks)

    if all_ads_limit_reached:
        custom_log("[SMART LOGIC] Semua task iklan harian sudah mencapai limit masing-masing.")
        return False

    for task in ad_tasks:
        task_id = task.get("id")
        title = task.get("title", "Ad Task")
        target = task.get("target", 20)
        progress = task.get("progress", 0)

        if progress >= target:
            continue

        result = process_ad_flow(task_id, title)
        if result is True:
            return True
        elif result == "COOLDOWN":
            custom_log(f"[{title}] Sedang Cooldown, melewati...")
            time.sleep(2)
            continue

    return False

def run_bot():
    global BASE_URL, FARM_FP, DEVICE_ID, INIT_DATA
    BASE_URL = CONFIG.get("base_url", "https://farm-buddies-api.htmmo2025.workers.dev/api")
    FARM_FP = CONFIG.get("fingerprint", "")
    DEVICE_ID = CONFIG.get("device_id", "")
    INIT_DATA = CONFIG.get("init_data", "")

    if not authenticate():
        custom_log("Gagal autentikasi awal. Pastikan initData valid.")
        time.sleep(3)
        return

    bootstrap_data, username, usdt, water = fetch_bootstrap()
    print_header(username, usdt, water)
    
    custom_log("Bot Smart Farm Buddies (JSON Config) Berjalan...")
    
    while True:
        try:
            bootstrap_data, username, usdt, water = fetch_bootstrap()
            
            if bootstrap_data:
                success_action = run_smart_scanner(bootstrap_data)
                
                if not success_action:
                    custom_log("[IDLE] Semua aktivitas selesai / cooldown. Istirahat 5 menit...")
                    time.sleep(300)
                else:
                    time.sleep(3)
            else:
                custom_log("[WARNING] Gagal sync data server. Coba lagi dalam 10 detik...")
                time.sleep(10)
                
        except KeyboardInterrupt:
            custom_log("Bot dihentikan manual oleh pengguna.")
            break
        except Exception as e:
            custom_log(f"Error pada loop utama: {e}")
            time.sleep(30)

def main():
    while True:
        display_banner()
        print("Sebelum menjalankan scriptnya mari kita berdoa kepada TUHAN YANG MAHA ESA agar di beri rezeki lebih untuk mencukupi kebutuhan sehari-hari dan beramal")
        print("#SAVEPALESTINE \n")
        print("1. Mainkan wak")
        print("2. Isi init_data")
        print("3. Hapus Data")
        print("0. Pulang wak Turu\n")
        
        pilihan = input("Pilih menu: ").strip()
        
        if pilihan == "1":
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    global CONFIG
                    CONFIG = json.load(f)
                run_bot()
            else:
                print("\n\033[1;31mData belum diisi! Silakan pilih menu 2 (Isi init_data) terlebih dahulu.\033[0m")
                time.sleep(2)
        elif pilihan == "2":
            isi_data()
        elif pilihan == "3":
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
                print("\n\033[1;32m✅ Data config.json berhasil dihapus!\033[0m")
            else:
                print("\n\033[1;33m⚠️ Tidak ada data (config.json) yang bisa dihapus.\033[0m")
            time.sleep(2)
        elif pilihan == "0":
            print("\n\033[1;36mTerima kasih, selamat beristirahat wak!\033[0m\n")
            sys.exit(0)
        else:
            print("\n\033[1;31mPilihan tidak valid!\033[0m")
            time.sleep(1)

if __name__ == "__main__":
    main()





#created by AHD1905
