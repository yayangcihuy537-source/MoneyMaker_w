import requests
import time
import urllib.parse
import sys
import os
import json

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

# ============================================================
# BANNER
# ============================================================
BANNER = f"""
{C}╔══════════════════════════════════════════════════════════╗
║   ██████╗██╗      ██████╗ ██╗   ██╗██████╗              ║
║  ██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗             ║
║  ██║     ██║     ██║   ██║██║   ██║██║  ██║             ║
║  ██║     ██║     ██║   ██║██║   ██║██║  ██║             ║
║  ╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝             ║
║   ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝              ║
║                                                        ║
║      ███████╗ █████╗ ██████╗ ███╗   ██╗                ║
║      ██╔════╝██╔══██╗██╔══██╗████╗  ██║                ║
║      █████╗  ███████║██████╔╝██╔██╗ ██║                ║
║      ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║                ║
║      ███████╗██║  ██║██║  ██║██║ ╚████║                ║
║      ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝                ║
╠══════════════════════════════════════════════════════════╣
║                 {Y}☁️  @CloudEarnBot ☁️{RS}{C}                    ║
║              {LC}Developed by SCRIPTYXSOUU{RS}{C}                 ║
║         {G}AUTO FARM • AUTO CLAIM • AUTO TASK{RS}{C}             ║
╚══════════════════════════════════════════════════════════╝{RS}
"""

WATCH_BANNER = f"""
{C}╔══════════════════════════════════════════════╗
║              {LC}📺 WATCH ADS MODE{RS}{C}              ║
╠══════════════════════════════════════════════╣
║  {Y}🤖 Bot        :{RS} @CloudEarnBot              ║
║  {Y}⏳ Status     :{RS} {LC}Watching Advertisement...{RS}  ║
║  {Y}🎯 Reward     :{RS} {G}Waiting...{RS}                 ║
║  {R}⚡ Please Wait, Don't Close Script{RS}         ║
╚══════════════════════════════════════════════╝{RS}
"""

MENU = f"""
{C}╔══════════════════════════════════════════════╗
║              {Y}☁️ @CloudEarnBot ☁️{RS}{C}            ║
║          {LC}AUTO FARMING & WATCH ADS{RS}{C}           ║
╠══════════════════════════════════════════════╣
║  {G}[1] 🚀 Start Farming{RS}{C}                       ║
║  {Y}[2] 🔑 Set Init_Data & Bearer Token{RS}{C}        ║
║  {B}[3] 💰 Check Balance{RS}{C}                       ║
║                                              ║
║  {R}[0] ❌ Exit{RS}{C}                                ║
╚══════════════════════════════════════════════╝{RS}
"""

CONFIG_FILE = "config.json"

# ============================================================
# GLOBAL VARIABLES
# ============================================================
INIT_DATA = ""
AUTH_TOKEN = ""
APIKEY = ""
START_PARAM = ""
SUPABASE_URL = "https://supabase.cloudearn.org"
WATCH_DURATION = 20
NETWORKS = ["adsgram", "monetag", "richads", "onclicka", "gigapup", "towerads"]
HEADERS = {}

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

def get_input_data():
    print(f"\n{Y}MASUKKAN DATA DARI CLOUDEARNBOT (WebApp):{RS}")
    print(f"{C}{'='*50}{RS}")
    init_data = input(f"{LC}init_data (panjang): {RS}").strip()
    auth_token = input(f"{LC}Authorization (Bearer ...): {RS}").strip()
    
    if not init_data or not auth_token:
        print(f"{R}❌ Kedua data wajib diisi!{RS}")
        return None, None
    
    if not auth_token.startswith("Bearer "):
        auth_token = "Bearer " + auth_token
    
    return init_data, auth_token

# ============================================================
# FUNGSI SET DATA
# ============================================================
def set_data(force=False):
    global INIT_DATA, AUTH_TOKEN, APIKEY, START_PARAM, SUPABASE_URL, HEADERS
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    
    if not force:
        # Coba load dari config
        config = load_config()
        if config:
            print(f"{G}✅ Config ditemukan, mencoba validasi...{RS}")
            INIT_DATA = config.get("init_data", "")
            AUTH_TOKEN = config.get("auth_token", "")
            APIKEY = config.get("apikey", "")
            START_PARAM = config.get("start_param", "")
            SUPABASE_URL = config.get("supabase_url", "https://supabase.cloudearn.org")
            HEADERS = config.get("headers", {})
            
            # Coba validasi dengan init_session
            if init_session():
                print(f"{G}✅ Config valid!{RS}")
                time.sleep(1.5)
                return True
            else:
                print(f"{R}❌ Config kadaluarsa / tidak valid. Masukkan data baru.{RS}")
                time.sleep(2)
    
    # Input baru
    init_data, auth_token = get_input_data()
    if not init_data or not auth_token:
        return False
    
    INIT_DATA = init_data
    AUTH_TOKEN = auth_token
    APIKEY = AUTH_TOKEN.replace("Bearer ", "")
    
    parsed = urllib.parse.parse_qs(INIT_DATA)
    START_PARAM = parsed.get("start_param", [None])[0]
    if START_PARAM:
        print(f"{G}✅ Start param ditemukan: {START_PARAM}{RS}")
    else:
        print(f"{Y}⚠️ Start param tidak ada, akan dikosongkan{RS}")
        START_PARAM = ""
    
    HEADERS = {
        "authorization": AUTH_TOKEN,
        "apikey": APIKEY,
        "x-telegram-init-data": INIT_DATA,
        "user-agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.6.4",
        "content-type": "application/json",
        "accept": "*/*",
        "origin": "https://cloudearn.vercel.app/",
        "referer": "https://cloudearn.vercel.app/",
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "x-requested-with": "org.telegram.messenger.web",
    }
    
    # Simpan config
    config = {
        "init_data": INIT_DATA,
        "auth_token": AUTH_TOKEN,
        "apikey": APIKEY,
        "start_param": START_PARAM,
        "supabase_url": SUPABASE_URL,
        "headers": HEADERS
    }
    save_config(config)
    print(f"{G}✅ Config disimpan!{RS}")
    time.sleep(1.5)
    return True

# ============================================================
# FUNGSI SUPABASE
# ============================================================
def supabase_request(action: str, payload: dict = None) -> dict:
    url = f"{SUPABASE_URL}/functions/v1/api"
    params = {"action": action}
    resp = requests.post(url, params=params, json=payload or {}, headers=HEADERS)
    if resp.status_code != 200:
        try:
            err = resp.json()
        except:
            err = resp.text
        raise Exception(f"{resp.status_code}: {err}")
    return resp.json()

def init_session():
    if not HEADERS:
        return False
    payload = {
        "fp_hash": "88bba40c3cc06e4bc78f354c012a1d5b0f0307f72934bc902352886f2d03cc9b",
        "webgl_hash": "bfc8fbb0012f8c92b0f1f0e178d08ba95ec000335360ca22edcf270a098ddab2",
        "audio_hash": "05d0c5571616fb4731d584d3a16738cc81dcd566dcb2598bee29200a1eeb4a46",
        "tz": "Asia/Jakarta",
        "lang": "id-ID",
        "platform": "Linux aarch64"
    }
    if START_PARAM:
        payload["start_param"] = START_PARAM
    try:
        supabase_request("init", payload)
        return True
    except:
        return False

def get_user_data():
    payload = {
        "fp_hash": "88bba40c3cc06e4bc78f354c012a1d5b0f0307f72934bc902352886f2d03cc9b",
        "webgl_hash": "bfc8fbb0012f8c92b0f1f0e178d08ba95ec000335360ca22edcf270a098ddab2",
        "audio_hash": "05d0c5571616fb4731d584d3a16738cc81dcd566dcb2598bee29200a1eeb4a46",
        "tz": "Asia/Jakarta",
        "lang": "id-ID",
        "platform": "Linux aarch64"
    }
    if START_PARAM:
        payload["start_param"] = START_PARAM
    return supabase_request("init", payload)

def get_ad_stats():
    return supabase_request("ad_stats", {})

def issue_ticket(network: str) -> str:
    data = supabase_request("ad_ticket_issue", {"purpose": "task_ads", "network": network})
    return data.get("ticket")

def record_ad_view(network: str, ticket: str):
    supabase_request("record_ad_view", {"network": network, "ad_ticket_id": ticket})

# ============================================================
# FUNGSI FARMING
# ============================================================
def start_farming():
    global HEADERS, INIT_DATA, AUTH_TOKEN
    
    if not HEADERS or not INIT_DATA:
        print(f"{R}❌ Data belum diset! Silakan pilih menu 2 dulu.{RS}")
        time.sleep(2)
        return
    
    # Cek validasi config
    if not init_session():
        print(f"{R}❌ Config kadaluarsa! Silakan set ulang di menu 2.{RS}")
        time.sleep(2)
        return
    
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(f"\n{G}🚀 Inisialisasi session...{RS}")
    
    if not init_session():
        print(f"{R}❌ Gagal init session, cek data.{RS}")
        time.sleep(2)
        return
    
    print(f"{G}✅ Session OK. Memulai auto watch...{RS}")
    print(f"{Y}⏹ Tekan Ctrl+C untuk berhenti.{RS}\n")
    
    cycle_count = 0
    while True:
        try:
            cycle_count += 1
            os.system('cls' if os.name == 'nt' else 'clear')
            print(BANNER)
            print(WATCH_BANNER)
            print(f"\n{C}--- Siklus {cycle_count} ---{RS}")
            
            stats = get_ad_stats()
            cooldowns = stats.get("cooldowns", {})
            for net, cd in cooldowns.items():
                if cd == 0:
                    print(f"  {G}{net}: {cd}s cooldown ✅{RS}")
                else:
                    print(f"  {Y}{net}: {cd}s cooldown ⏳{RS}")
            
            ready = [n for n in NETWORKS if cooldowns.get(n, 0) == 0]
            if not ready:
                print(f"\n{Y}Semua network cooldown. Tunggu 30 detik...{RS}")
                time.sleep(30)
                continue
            
            for net in ready:
                print(f"\n{LC}>>> Menonton iklan {net}{RS}")
                try:
                    ticket = issue_ticket(net)
                    print(f"  {Y}Ticket: {ticket}{RS}")
                    print(f"  {C}Menonton selama {WATCH_DURATION} detik...{RS}")
                    for i in range(WATCH_DURATION):
                        time.sleep(1)
                        sys.stdout.write(f"\r  {G}[{'#' * (i+1)}{' ' * (WATCH_DURATION - i - 1)}] {i+1}/{WATCH_DURATION}s{RS}")
                        sys.stdout.flush()
                    print()
                    record_ad_view(net, ticket)
                    print(f"  {G}✅ {net} selesai{RS}")
                except Exception as e:
                    print(f"  {R}❌ {net} gagal: {e}{RS}")
            
            stats = get_ad_stats()
            cooldowns = stats.get("cooldowns", {})
            if all(cd > 0 for cd in cooldowns.values()):
                print(f"\n{Y}Semua network cooldown. Tunggu 30 detik...{RS}")
                time.sleep(30)
            
        except KeyboardInterrupt:
            print(f"\n{R}⏹ Dihentikan oleh user.{RS}")
            break
        except Exception as e:
            print(f"{R}❌ Error: {e}{RS}")
            print(f"{Y}Tunggu 10 detik lalu lanjut...{RS}")
            time.sleep(10)

# ============================================================
# FUNGSI CEK BALANCE
# ============================================================
def check_balance():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    if not HEADERS:
        print(f"{R}❌ Data belum diset! Silakan pilih menu 2 dulu.{RS}")
        time.sleep(2)
        return
    
    # Cek validasi config
    if not init_session():
        print(f"{R}❌ Config kadaluarsa! Silakan set ulang di menu 2.{RS}")
        time.sleep(2)
        return
    
    print(f"{B}💰 Mengecek Balance...{RS}\n")
    try:
        data = get_user_data()
        user = data.get("user", {})
        if not user:
            print(f"{R}❌ Gagal mengambil data user.{RS}")
        else:
            print(f"{G}👤 User: {user.get('username', 'N/A')}{RS}")
            print(f"{C}   ID: {user.get('tg_id', 'N/A')}{RS}")
            print(f"{C}   Nama: {user.get('first_name', '')} {user.get('last_name', '')}{RS}")
            print(f"{C}   Negara: {user.get('country_name', 'N/A')}{RS}")
            print(f"{Y}───────────────────────────{RS}")
            print(f"{G}💰 Balance Cloud: {user.get('balance_cloud', 0)}{RS}")
            print(f"{G}💰 Balance USDT: {user.get('balance_usdt', 0)}{RS}")
            print(f"{G}📈 Total Earned Cloud: {user.get('total_earned_cloud', 0)}{RS}")
            print(f"{G}📈 Total Earned USDT: {user.get('total_earned_usdt', 0)}{RS}")
            print(f"{C}👥 Referral Count: {user.get('referral_count', 0)}{RS}")
            print(f"{C}🎁 Referral Earnings: {user.get('ref_earnings_cloud', 0)}{RS}")
            print(f"{Y}───────────────────────────{RS}")
            print(f"{B}📊 Status: {'✅ Premium' if user.get('is_premium') else '⬜ Free'}{RS}")
            print(f"{B}📊 Bio Verified: {'✅ Ya' if user.get('bio_verified') else '❌ Tidak'}{RS}")
            print(f"{B}📊 Channels Verified: {'✅ Ya' if user.get('channels_verified') else '❌ Tidak'}{RS}")
    except Exception as e:
        print(f"{R}❌ Error: {e}{RS}")
    input(f"\n{C}Tekan Enter untuk kembali...{RS}")

# ============================================================
# MAIN
# ============================================================
def main():
    global HEADERS, INIT_DATA, AUTH_TOKEN, APIKEY, START_PARAM, SUPABASE_URL
    # Coba load config di awal
    config = load_config()
    if config:
        INIT_DATA = config.get("init_data", "")
        AUTH_TOKEN = config.get("auth_token", "")
        APIKEY = config.get("apikey", "")
        START_PARAM = config.get("start_param", "")
        SUPABASE_URL = config.get("supabase_url", "https://supabase.cloudearn.org")
        HEADERS = config.get("headers", {})
    
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        print(MENU)
        
        # Tampilkan status config
        if HEADERS and INIT_DATA:
            print(f"{G}🔑 Config: Aktif ✅{RS}")
        else:
            print(f"{R}🔑 Config: Belum diset ❌{RS}")
        
        choice = input(f"\n{LC}Select Menu » {RS}").strip()
        
        if choice == "1":
            start_farming()
        elif choice == "2":
            set_data(force=True)  # Force input ulang
        elif choice == "3":
            check_balance()
        elif choice == "0":
            print(f"\n{R}❌ Exit...{RS}")
            sys.exit(0)
        else:
            print(f"{R}❌ Pilihan tidak valid!{RS}")
            time.sleep(1)

if __name__ == "__main__":
    main()
