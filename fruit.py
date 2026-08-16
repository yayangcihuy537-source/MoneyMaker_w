#!/usr/bin/env python3
"""
GRAM DROP - AUTO ADS ONLY
- Auto watch ads (earn + monetag) sampai limit harian
- Clean progress bar
- Auto detect daily limit & cooldown
- Kembali ke menu setelah semua iklan selesai
"""

import os, sys, time, json, random, uuid, requests, urllib.parse
from datetime import datetime

# ============================================================
# WARNA
# ============================================================
C = '\033[96m'
LC = '\033[1;96m'
Y = '\033[93m'
G = '\033[92m'
R = '\033[91m'
B = '\033[94m'
W = '\033[97m'
BLD = '\033[1m'
RS = '\033[0m'
DIM = '\033[2m'

# ============================================================
# BANNER
# ============================================================
BANNER = f"""
{C}╔══════════════════════════════════════════════════════════╗
║   ██████╗ ██████╗  █████╗ ███╗   ███╗██████╗ ██████╗   ║
║  ██╔════╝ ██╔══██╗██╔══██╗████╗ ████║██╔══██╗██╔══██╗  ║
║  ██║  ███╗██████╔╝███████║██╔████╔██║██████╔╝██████╔╝  ║
║  ██║   ██║██╔══██╗██╔══██║██║╚██╔╝██║██╔═══╝ ██╔══██╗  ║
║  ╚██████╔╝██║  ██║██║  ██║██║ ╚═╝ ██║██║     ██║  ██║  ║
║   ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝  ╚═╝  ║
╠══════════════════════════════════════════════════════════╣
║                 {Y}☁️  GRAM DROP ☁️{RS}{C}                    ║
║              {LC}AUTO ADS (NO GAMES){RS}{C}                 ║
╚══════════════════════════════════════════════════════════╝{RS}
"""

MENU = f"""
{C}╔══════════════════════════════════════════════╗
║              {Y}☁️ GRAM DROP ☁️{RS}{C}               ║
║          {LC}AUTO WATCH ADS{RS}{C}                 ║
╠══════════════════════════════════════════════╣
║  {G}[1] 📺 Watch Ads (auto detect){RS}{C}           ║
║  {Y}[2] 🔑 Set Init Data{RS}{C}                   ║
║  {B}[3] 💰 Check Balance{RS}{C}                   ║
║                                              ║
║  {R}[0] ❌ Exit{RS}{C}                                ║
╚══════════════════════════════════════════════╝{RS}
"""

CONFIG_FILE = "gramdrop_config.json"
BASE_URL = "https://modapkam.shop"

ADS_NETWORKS = ["earn", "monetag"]

# ============================================================
# FUNGSI CONFIG
# ============================================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            return None
    return None

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# ============================================================
# FUNGSI SET DATA
# ============================================================
def set_init_data():
    global INIT_DATA, DEVICE_ID, HEADERS
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(f"\n{Y}🔑 SET INIT DATA{RS}")
    print(f"{C}{'='*50}{RS}")
    init_data = input(f"{LC}X-Telegram-Initdata (wajib): {RS}").strip()
    if not init_data:
        print(f"{R}❌ Init data tidak boleh kosong!{RS}")
        time.sleep(2)
        return False

    old_config = load_config() or {}
    device_id = old_config.get("device_id")
    if not device_id:
        device_id = str(uuid.uuid4())[:22].replace('-', '')
    
    config = {
        "init_data": init_data,
        "device_id": device_id
    }
    save_config(config)
    INIT_DATA = init_data
    DEVICE_ID = device_id
    HEADERS = build_headers(init_data, device_id)
    print(f"{G}✅ Config disimpan!{RS}")
    time.sleep(1.5)
    return True

def build_headers(init_data, device_id):
    return {
        "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.1 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
        "Accept": "*/*",
        "Accept-Language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "X-Requested-With": "org.telegram.messenger.web",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Origin": "https://modapkam.shop",
        "Referer": "https://modapkam.shop/",
        "Content-Type": "application/json",
        "Sec-Ch-Ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": '"Android"',
        "X-Device-Id": device_id,
        "X-Telegram-Initdata": init_data,
    }

# ============================================================
# FUNGSI REQUEST
# ============================================================
def make_request(method, endpoint, payload=None):
    url = f"{BASE_URL}{endpoint}"
    try:
        if method.upper() == "GET":
            resp = requests.get(url, headers=HEADERS, timeout=15)
        else:
            resp = requests.post(url, json=payload, headers=HEADERS, timeout=15)
        if resp.status_code == 429:
            try:
                err = resp.json()
                wait = err.get('waitSecs', 5)
                print(f"{Y}⏳ Cooldown {wait}s, waiting...{RS}")
                time.sleep(wait)
                # Retry once
                if method.upper() == "GET":
                    resp = requests.get(url, headers=HEADERS, timeout=15)
                else:
                    resp = requests.post(url, json=payload, headers=HEADERS, timeout=15)
            except:
                pass
        if resp.status_code != 200:
            # Check if it's daily limit error
            try:
                err = resp.json()
                if "daily_limit" in str(err).lower() or "limit reached" in str(err).lower():
                    print(f"{Y}⚠️ Daily limit reached{RS}")
                    return None
            except:
                pass
            print(f"{R}❌ HTTP {resp.status_code}: {resp.text[:200]}{RS}")
            return None
        return resp.json()
    except Exception as e:
        print(f"{R}❌ Request error: {e}{RS}")
        return None

def get_profile():
    return make_request("GET", "/api/me")

# ============================================================
# FUNGSI ADS
# ============================================================
def watch_ad(purpose):
    """Watch single ad with progress bar and return success"""
    print(f"{LC}📺 Watching {purpose} ad...{RS}")
    start_resp = make_request("POST", "/api/ads/start", {"purpose": purpose})
    if not start_resp:
        print(f"{R}❌ Failed to start ad{RS}")
        return False
    nonce = start_resp.get("nonce")
    if not nonce:
        print(f"{R}❌ No nonce{RS}")
        return False

    # Durasi iklan 12-18 detik
    duration = random.randint(12, 18)
    print(f"{C}⏳ Watching for {duration}s...{RS}")
    for i in range(duration):
        time.sleep(1)
        progress = "#" * (i+1) + " " * (duration - i - 1)
        sys.stdout.write(f"\r  {G}[{progress}] {i+1}/{duration}s{RS}")
        sys.stdout.flush()
    print()

    complete_resp = make_request("POST", "/api/ads/complete", {"nonce": nonce})
    if not complete_resp:
        print(f"{R}❌ Failed to complete ad{RS}")
        return False

    if complete_resp.get("ok") or complete_resp.get("reward") is not None:
        reward = complete_resp.get("reward", 0)
        balance = complete_resp.get("balance", 0)
        if reward:
            print(f"{G}✅ {purpose} ad completed! +{reward} GD (Bal: {balance}){RS}")
        else:
            print(f"{G}✅ {purpose} ad completed! (no reward){RS}")
        return True
    else:
        print(f"{R}❌ Ad completion failed{RS}")
        return False

def is_ad_limited(network):
    """Check if ad network is already daily limited"""
    profile = get_profile()
    if not profile:
        return False
    user = profile.get("user", {})
    ad_counters = user.get("adCounters", {})
    for key, val in ad_counters.items():
        if network in key:
            used = val.get("used", 0)
            cap = val.get("cap", 999)
            if used >= cap:
                return True
    return False

def watch_ads_phase():
    """Auto watch ads until all networks done (limit reached)"""
    done_networks = set()
    cycle = 0

    while True:
        cycle += 1
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        print(f"\n{C}--- ADS CYCLE {cycle} ---{RS}")
        
        # Check limit for each network
        remaining = []
        for net in ADS_NETWORKS:
            if net in done_networks:
                continue
            if is_ad_limited(net):
                print(f"{Y}⚠️ {net} daily limit reached, skipping.{RS}")
                done_networks.add(net)
            else:
                remaining.append(net)
        
        if not remaining:
            print(f"{G}✅ All ads completed! Returning to menu.{RS}")
            time.sleep(2)
            return
        
        print(f"{Y}Networks remaining: {', '.join(remaining)}{RS}\n")
        
        # Try to watch each remaining network
        for net in remaining:
            if net in done_networks:
                continue
            print(f"{LC}>>> Processing {net}{RS}")
            success = False
            attempts = 0
            max_attempts = 2
            while attempts < max_attempts and not success:
                attempts += 1
                try:
                    if watch_ad(net):
                        success = True
                        # After success, check if limit reached
                        if is_ad_limited(net):
                            print(f"{Y}⚠️ {net} daily limit reached after watching.{RS}")
                            done_networks.add(net)
                    else:
                        print(f"{Y}⚠️ Retry {net} in 5s...{RS}")
                        time.sleep(5)
                except Exception as e:
                    print(f"{R}❌ Error: {e}{RS}")
                    time.sleep(3)
            if not success:
                print(f"{Y}⚠️ {net} failed after attempts, marking as done to avoid loop.{RS}")
                done_networks.add(net)
        
        # Check if all done
        if len(done_networks) >= len(ADS_NETWORKS):
            print(f"{G}✅ All ads completed! Returning to menu.{RS}")
            time.sleep(2)
            return
        
        # If there are remaining networks, wait a bit before next cycle
        remaining_after = [n for n in ADS_NETWORKS if n not in done_networks]
        if remaining_after:
            print(f"{Y}⏳ Waiting 10s before retry: {', '.join(remaining_after)}{RS}")
            time.sleep(10)

# ============================================================
# FUNGSI CEK BALANCE
# ============================================================
def check_balance():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    if not HEADERS or not HEADERS.get("X-Telegram-Initdata"):
        print(f"{R}❌ Init_Data belum diset! Silakan menu 2 dulu.{RS}")
        time.sleep(2)
        return

    print(f"{B}💰 Mengecek Balance...{RS}\n")
    profile = get_profile()
    if not profile:
        print(f"{R}❌ Gagal mengambil profil{RS}")
        input(f"\n{C}Tekan Enter untuk kembali...{RS}")
        return

    user = profile.get("user", {})
    print(f"{G}👤 User: {user.get('name', 'N/A')} (@{user.get('username', 'N/A')}){RS}")
    print(f"{G}💰 Balance: {user.get('balance', 0)} GD{RS}")
    print(f"{G}📺 Ads Today: {user.get('adsToday', 0)}/{user.get('adsTotal', 0)}{RS}")
    ad_counters = user.get("adCounters", {})
    for net, val in ad_counters.items():
        print(f"{G}📊 {net}: {val.get('used', 0)}/{val.get('cap', '∞')}{RS}")
    input(f"\n{C}Tekan Enter untuk kembali...{RS}")

# ============================================================
# MAIN
# ============================================================
def main():
    global INIT_DATA, DEVICE_ID, HEADERS
    config = load_config()
    if config:
        INIT_DATA = config.get("init_data", "")
        DEVICE_ID = config.get("device_id", "")
        if INIT_DATA and DEVICE_ID:
            HEADERS = build_headers(INIT_DATA, DEVICE_ID)
        else:
            HEADERS = {}
    else:
        HEADERS = {}

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        print(MENU)
        if HEADERS and HEADERS.get("X-Telegram-Initdata"):
            print(f"{G}🔑 Config: Aktif ✅ (Init_Data tersimpan){RS}")
        else:
            print(f"{R}🔑 Config: Belum diset ❌{RS}")

        choice = input(f"\n{LC}Pilih Menu » {RS}").strip()

        if choice == "1":
            if not HEADERS or not HEADERS.get("X-Telegram-Initdata"):
                print(f"{R}❌ Set Init_Data dulu (menu 2){RS}")
                time.sleep(2)
                continue
            watch_ads_phase()
        elif choice == "2":
            set_init_data()
        elif choice == "3":
            check_balance()
        elif choice == "0":
            print(f"\n{R}❌ Exit...{RS}")
            sys.exit(0)
        else:
            print(f"{R}❌ Pilihan tidak valid!{RS}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Y}⏹ Dihentikan oleh user.{RS}")
        sys.exit(0)
