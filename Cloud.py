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
DIM = '\033[2m'

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
║  {Y}[2] 🔑 Set Init_Data (Bearer opsional){RS}{C}     ║
║  {B}[3] 💰 Check Balance{RS}{C}                       ║
║  {LC}[4] 👆 Taptap Auto (100/tap){RS}{C}              ║
║  {LC}[5] ⛏️  Start Mining (Auto Re-Start){RS}{C}       ║
║                                              ║
║  {R}[0] ❌ Exit{RS}{C}                                ║
╚══════════════════════════════════════════════╝{RS}
"""

TAPTAP_BANNER = f"""
{C}╔══════════════════════════════════════════════╗
║              {LC}👆 TAPTAP AUTO MODE{RS}{C}           ║
╠══════════════════════════════════════════════╣
║  {Y}🤖 Bot        :{RS} @CloudEarnBot              ║
║  {Y}👆 Tap Rate   :{RS} {LC}100 taps/request{RS}         ║
║  {Y}🎯 Reward     :{RS} {G}5 credits/tap{RS}             ║
║  {Y}🔓 Unlock     :{RS} {G}Ticket Aging Mode{RS}         ║
║  {R}⚡ Auto Unlock saat Locked{RS}                  ║
╚══════════════════════════════════════════════╝{RS}
"""

MINING_BANNER = f"""
{C}╔══════════════════════════════════════════════╗
║              {LC}⛏️  MINING MODE{RS}{C}                ║
╠══════════════════════════════════════════════╣
║  {Y}🤖 Bot        :{RS} @CloudEarnBot              ║
║  {Y}⛏️  Status     :{RS} {LC}Auto Start & Maintain{RS}    ║
║  {Y}💎 Rate       :{RS} {G}40 cloud/hour{RS}             ║
║  {R}⚡ Max 6 jam per sesi{RS}                        ║
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

# ═══════════════════════════════════════════════════════════════
# NETWORK LIST (UPDATED - monetix + tads ditambah)
# ═══════════════════════════════════════════════════════════════
NETWORKS = [
    "adsgram",
    "monetag",
    "richads",
    "onclicka",
    "gigapup",
    "towerads",
    "adsgalaxy",
    "adexium",
    "adloop",
    "monetix",
    "tads",
]

# Retry config
MAX_RETRY = 2   # 2x retry → total 3 percobaan, kalau gagal semua → skip

HEADERS = {}

# Taptap config
TAPS_PER_REQUEST = 100
TAP_VALUE = 5
TICKET_AGING_INTERVAL = 15
TICKET_AGING_MAX = 180

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
def set_data(force=False):
    global INIT_DATA, AUTH_TOKEN, APIKEY, START_PARAM, SUPABASE_URL, HEADERS
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)

    old_config = load_config()
    old_auth_token = old_config.get("auth_token", "") if old_config else ""

    print(f"\n{Y}🔑 SET INIT_DATA (Bearer token opsional){RS}")
    print(f"{C}{'='*50}{RS}")
    init_data = input(f"{LC}init_data (wajib): {RS}").strip()
    if not init_data:
        print(f"{R}❌ init_data tidak boleh kosong!{RS}")
        time.sleep(2)
        return False

    print(f"{Y}Masukkan Bearer token (opsional, Enter untuk skip):{RS}")
    auth_token = input(f"{LC}Bearer token: {RS}").strip()
    if not auth_token and old_auth_token:
        auth_token = old_auth_token
        print(f"{G}✅ Menggunakan Bearer token dari config sebelumnya.{RS}")
        time.sleep(1)
    if auth_token and not auth_token.startswith("Bearer "):
        auth_token = "Bearer " + auth_token

    INIT_DATA = init_data
    AUTH_TOKEN = auth_token
    APIKEY = AUTH_TOKEN.replace("Bearer ", "") if AUTH_TOKEN else ""

    parsed = urllib.parse.parse_qs(INIT_DATA)
    START_PARAM = parsed.get("start_param", [None])[0]
    if START_PARAM:
        print(f"{G}✅ Start param ditemukan: {START_PARAM}{RS}")
    else:
        print(f"{Y}⚠️ Start param tidak ada, akan dikosongkan{RS}")
        START_PARAM = ""

    HEADERS = {
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
    if AUTH_TOKEN:
        HEADERS["authorization"] = AUTH_TOKEN
        HEADERS["apikey"] = APIKEY

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
    if not HEADERS or not HEADERS.get("x-telegram-init-data"):
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

# ═══════════════════════════════════════════════════════════════
# FUNGSI TAPTAP
# ═══════════════════════════════════════════════════════════════
def taptap_status():
    return supabase_request("taptap_status", {})

def taptap_tap(taps: int):
    return supabase_request("taptap_tap", {"taps": taps})

def taptap_unlock(ad_ticket_id: str):
    return supabase_request("taptap_unlock", {"ad_ticket_id": ad_ticket_id})

def issue_taptap_ticket(network: str = "adsgram") -> str:
    data = supabase_request("ad_ticket_issue", {"purpose": "taptap", "network": network})
    return data.get("ticket")

# ═══════════════════════════════════════════════════════════════
# FUNGSI MINING
# ═══════════════════════════════════════════════════════════════
def mining_status():
    return supabase_request("mining_status", {})

def mining_start():
    return supabase_request("mining_start", {})

def xox_close_session():
    try:
        return supabase_request("xox_close_session", {})
    except:
        return None

# ============================================================
# FUNGSI FARMING (UPDATED - retry 2x, stop kalau semua abis/gagal)
# ============================================================
def start_farming():
    global HEADERS, INIT_DATA, AUTH_TOKEN

    if not HEADERS or not HEADERS.get("x-telegram-init-data"):
        print(f"{R}❌ Init_Data belum diset! Silakan pilih menu 2 dulu.{RS}")
        time.sleep(2)
        return

    if not init_session():
        print(f"{R}❌ Session gagal! Cek init_data atau koneksi.{RS}")
        time.sleep(2)
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(f"\n{G}🚀 Inisialisasi session...{RS}")
    print(f"{G}✅ Session OK. Memulai auto watch...{RS}")
    print(f"{Y}⏹ Tekan Ctrl+C untuk berhenti.{RS}\n")

    cycle_count = 0
    done_networks = set()    # network yang udah sukses ATAU gagal total

    while True:
        try:
            cycle_count += 1
            os.system('cls' if os.name == 'nt' else 'clear')
            print(BANNER)
            print(WATCH_BANNER)
            print(f"\n{C}--- Siklus {cycle_count} ---{RS}")
            print(f"{DIM}Progress: {len(done_networks)}/{len(NETWORKS)} network selesai{RS}\n")

            stats = get_ad_stats()
            cooldowns = stats.get("cooldowns", {})

            ready_networks = []
            for net in NETWORKS:
                cd = cooldowns.get(net, 0)
                if net in done_networks:
                    print(f"  {DIM}{net}: DONE (skipped){RS}")
                    continue
                if cd == 0:
                    ready_networks.append(net)
                    print(f"  {G}{net}: ready ✅{RS}")
                else:
                    print(f"  {Y}{net}: cooldown ⏳{RS}")

            # ═══ STOP kalau semua network udah done ═══
            if len(done_networks) >= len(NETWORKS):
                print(f"\n{G}✅ Semua iklan telah selesai / gagal! Bot berhenti.{RS}")
                print(f"{G}   Total: {len(done_networks)}/{len(NETWORKS)} network{RS}")
                break

            # ═══ Kalau gak ada yang ready, tunggu cooldown ═══
            if not ready_networks:
                print(f"\n{Y}Semua network cooldown. Tunggu 30 detik...{RS}")
                time.sleep(30)
                continue

            # ═══ Loop tiap network yang ready ═══
            for net in ready_networks:
                print(f"\n{LC}>>> Menonton iklan {net}{RS}")

                success = False
                for attempt in range(1, MAX_RETRY + 2):  # 1 initial + MAX_RETRY
                    print(f"  {Y}Percobaan {attempt}/{MAX_RETRY+1}{RS}")

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
                        success = True
                        done_networks.add(net)
                        break

                    except Exception as e:
                        err_str = str(e)

                        # Kalau network udah habis / limit → langsung skip (gak perlu retry)
                        if "ad_required" in err_str or "ticket_too_early" in err_str or "limit" in err_str.lower() or "cooldown" in err_str.lower():
                            print(f"  {Y}⚠️ {net}: habis / limit → skip{RS}")
                            done_networks.add(net)
                            break

                        # Kalau error lain → retry
                        print(f"  {R}❌ Gagal: {e}{RS}")

                        if attempt <= MAX_RETRY:
                            print(f"  {Y}🔄 Retry dalam 3 detik...{RS}")
                            time.sleep(3)
                            continue
                        else:
                            print(f"  {Y}⚠️ {net} gagal setelah {MAX_RETRY+1} percobaan → skip{RS}")
                            done_networks.add(net)

                # Cek lagi apakah semua udah kelar setelah network ini
                if len(done_networks) >= len(NETWORKS):
                    break

        except KeyboardInterrupt:
            print(f"\n{R}⏹ Dihentikan oleh user.{RS}")
            break
        except Exception as e:
            print(f"{R}❌ Error: {e}{RS}")
            print(f"{Y}Tunggu 10 detik lalu lanjut...{RS}")
            time.sleep(10)

    print(f"\n{C}═══════════════════════════════════════════════════════════{RS}")
    print(f"{G}🏁 Farming selesai. Bot berhenti.{RS}")
    print(f"{C}═══════════════════════════════════════════════════════════{RS}\n")
    input(f"{C}Tekan Enter untuk kembali ke menu...{RS}")

# ============================================================
# FUNGSI CEK BALANCE
# ============================================================
def check_balance():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    if not HEADERS or not HEADERS.get("x-telegram-init-data"):
        print(f"{R}❌ Init_Data belum diset! Silakan pilih menu 2 dulu.{RS}")
        time.sleep(2)
        return

    if not init_session():
        print(f"{R}❌ Session gagal! Cek init_data atau koneksi.{RS}")
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

# ═══════════════════════════════════════════════════════════════
# FUNGSI TAPTAP AUTO — Ticket Aging Mode
# ═══════════════════════════════════════════════════════════════
def start_taptap():
    global HEADERS

    if not HEADERS or not HEADERS.get("x-telegram-init-data"):
        print(f"{R}❌ Init_Data belum diset! Silakan pilih menu 2 dulu.{RS}")
        time.sleep(2)
        return

    if not init_session():
        print(f"{R}❌ Session gagal! Cek init_data atau koneksi.{RS}")
        time.sleep(2)
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(TAPTAP_BANNER)
    print(f"{Y}⏹ Tekan Ctrl+C untuk berhenti.{RS}\n")

    def wait_countdown(sec, label=""):
        for i in range(sec, 0, -1):
            sys.stdout.write(f"\r  {Y}⌛ {label} {i}s...{RS}   ")
            sys.stdout.flush()
            time.sleep(1)
        print()

    try:
        while True:
            try:
                st = taptap_status()
                earned = st.get("earned_today", 0)
                limit = st.get("limit", 500)
                locked = st.get("locked", False)
                next_lock = st.get("next_lock_at", 100)

                print(f"{C}📊 Status : earned={G}{earned}{C} / limit={G}{limit}{C} | locked={Y}{locked}{C} | next_lock={Y}{next_lock}{RS}")

                if earned >= limit:
                    print(f"\n{G}✅ Limit harian tercapai ({earned}/{limit}). Bot berhenti.{RS}")
                    break

                if locked:
                    print(f"\n{Y}🔒 Taptap locked! Proses unlock...{RS}")

                    ticket = None
                    try:
                        ticket = issue_taptap_ticket("adsgram")
                        print(f"  {G}✓ Ticket issued: {DIM}{ticket}{RS}")
                    except Exception as e:
                        err = str(e)
                        if "ticket_too_early" in err:
                            print(f"  {Y}⏳ Belum bisa issue ticket. Jeda 30s...{RS}")
                            wait_countdown(30, "Retry in")
                            continue
                        else:
                            print(f"  {R}❌ Issue gagal: {e}{RS}")
                            wait_countdown(30, "Retry in")
                            continue

                    unlocked = False
                    waited = 0

                    print(f"  {C}⏳ Menunggu tiket siap (aging)...{RS}")

                    while waited < TICKET_AGING_MAX:
                        try:
                            taptap_unlock(ticket)
                            print(f"  {G}✅ Unlocked! (setelah {waited}s){RS}")
                            unlocked = True
                            break
                        except Exception as e:
                            err = str(e)

                            if "ticket_too_early" in err:
                                wait_countdown(TICKET_AGING_INTERVAL, f"Ticket aging ({waited}s)")
                                waited += TICKET_AGING_INTERVAL
                                continue
                            elif "invalid_ticket" in err or "expired" in err or "not_found" in err:
                                print(f"  {R}❌ Tiket invalid/expired: {e}{RS}")
                                break
                            else:
                                print(f"  {R}❌ Unlock error: {e}{RS}")
                                break

                    if not unlocked:
                        print(f"  {Y}⚠️ Gagal unlock setelah {waited}s. Jeda 30s lalu coba ulang...{RS}")
                        wait_countdown(30, "Retry in")
                        continue

                    time.sleep(2)
                    continue

                remaining_to_lock = next_lock - earned
                remaining_total = limit - earned
                taps_to_lock = max(1, remaining_to_lock // TAP_VALUE)
                taps_to_limit = max(1, remaining_total // TAP_VALUE)
                taps = min(TAPS_PER_REQUEST, taps_to_lock, taps_to_limit)

                if taps <= 0:
                    taps = 1

                print(f"{LC}👆 Tapping {taps} (est. +{taps * TAP_VALUE} credits)...{RS}")

                try:
                    res = taptap_tap(taps)
                    credited = res.get("credited", 0)
                    new_earned = res.get("earned_today", earned)
                    is_locked = res.get("locked", False)
                    print(f"  {G}✓ +{credited} credits | earned: {new_earned} | locked: {is_locked}{RS}")
                except Exception as e:
                    err_str = str(e)
                    if "too many" in err_str.lower() or "max" in err_str.lower():
                        print(f"  {Y}⚠️ Reject {taps} taps, fallback 10...{RS}")
                        try:
                            res = taptap_tap(10)
                            print(f"  {G}✓ +{res.get('credited', 0)} credits{RS}")
                        except Exception as e2:
                            print(f"  {R}❌ Fallback gagal: {e2}{RS}")
                    else:
                        print(f"  {R}❌ Tap gagal: {e}{RS}")

                time.sleep(2)

            except Exception as e:
                print(f"{R}❌ Loop error: {e}{RS}")
                time.sleep(5)

    except KeyboardInterrupt:
        print(f"\n{R}⏹ Dihentikan oleh user.{RS}")
        time.sleep(1.5)

# ═══════════════════════════════════════════════════════════════
# FUNGSI MINING AUTO
# ═══════════════════════════════════════════════════════════════
def start_mining():
    global HEADERS

    if not HEADERS or not HEADERS.get("x-telegram-init-data"):
        print(f"{R}❌ Init_Data belum diset! Silakan pilih menu 2 dulu.{RS}")
        time.sleep(2)
        return

    if not init_session():
        print(f"{R}❌ Session gagal! Cek init_data atau koneksi.{RS}")
        time.sleep(2)
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(MINING_BANNER)
    print(f"{Y}⏹ Tekan Ctrl+C untuk berhenti.{RS}\n")

    try:
        while True:
            try:
                st = mining_status()
                state = st.get("state", "unknown")
                session = st.get("session")
                rate = st.get("rate_per_hour", 40)
                max_hours = st.get("max_hours", 6)
                can_boost = st.get("can_boost", False)

                print(f"{C}📊 Mining state : {LC}{state}{RS}")
                if session:
                    started = session.get("started_at", "-")
                    expires = session.get("expires_at", "-")
                    hours = session.get("hours_total", 1)
                    reward = session.get("reward", 0)
                    print(f"  {Y}• Started  : {started}{RS}")
                    print(f"  {Y}• Expires  : {expires}{RS}")
                    print(f"  {Y}• Hours    : {hours} / max {max_hours}{RS}")
                    print(f"  {Y}• Reward   : {reward} cloud{RS}")
                    print(f"  {Y}• Rate     : {rate}/hour{RS}")
                    print(f"  {Y}• Boost    : {'✅ available' if can_boost else '❌ no'}{RS}")

                if state == "running":
                    print(f"\n{G}✅ Mining sudah jalan. Cek lagi dalam 60 detik...{RS}")
                    for i in range(60, 0, -1):
                        sys.stdout.write(f"\r  {Y}⏳ Next check in {i}s...{RS}   ")
                        sys.stdout.flush()
                        time.sleep(1)
                    print()
                    continue

                if state == "idle" or state == "unknown":
                    print(f"\n{LC}⛏️  Mining idle, starting session...{RS}")
                    try:
                        res = mining_start()
                        print(f"  {G}✓ {res}{RS}")
                        print(f"  {C}Tunggu 5 detik...{RS}")
                        time.sleep(5)
                    except Exception as e:
                        print(f"  {R}❌ Start gagal: {e}{RS}")
                        time.sleep(10)
                else:
                    print(f"\n{Y}⚠️ Unknown state: {state}. Tunggu 30 detik...{RS}")
                    time.sleep(30)

            except Exception as e:
                print(f"{R}❌ Loop error: {e}{RS}")
                time.sleep(10)

    except KeyboardInterrupt:
        print(f"\n{R}⏹ Dihentikan oleh user.{RS}")
        time.sleep(1.5)

# ============================================================
# MAIN
# ============================================================
def main():
    global HEADERS, INIT_DATA, AUTH_TOKEN, APIKEY, START_PARAM, SUPABASE_URL
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

        if HEADERS and HEADERS.get("x-telegram-init-data"):
            print(f"{G}🔑 Config: Aktif ✅ (Init_Data tersimpan){RS}")
        else:
            print(f"{R}🔑 Config: Belum diset ❌{RS}")

        choice = input(f"\n{LC}Select Menu » {RS}").strip()

        if choice == "1":
            start_farming()
        elif choice == "2":
            set_data(force=True)
        elif choice == "3":
            check_balance()
        elif choice == "4":
            start_taptap()
        elif choice == "5":
            start_mining()
        elif choice == "0":
            print(f"\n{R}❌ Exit...{RS}")
            sys.exit(0)
        else:
            print(f"{R}❌ Pilihan tidak valid!{RS}")
            time.sleep(1)

if __name__ == "__main__":
    main()
