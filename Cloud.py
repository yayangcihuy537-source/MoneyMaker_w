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
║                                                          ║
║    ██████╗██╗      ██████╗ ██╗   ██╗██████╗             ║
║   ██╔════╝██║     ██╔═══██╗██║   ██║██╔══██╗            ║
║   ██║     ██║     ██║   ██║██║   ██║██║  ██║            ║
║   ██║     ██║     ██║   ██║██║   ██║██║  ██║            ║
║   ╚██████╗███████╗╚██████╔╝╚██████╔╝██████╔╝            ║
║    ╚═════╝╚══════╝ ╚═════╝  ╚═════╝ ╚═════╝             ║
║                                                          ║
║                 {Y}☁️  @CloudEarnBot ☁️{RS}{C}                    ║
║              {LC}Developed by SCRIPTYXSOUU{RS}{C}                 ║
║         {G}AUTO FARM • AUTO CLAIM • AUTO TASK{RS}{C}             ║
╚══════════════════════════════════════════════════════════╝{RS}
"""

WATCH_BANNER = f"""
{C}╔══════════════════════════════════════════════╗
║              {LC}📺 WATCH ADS MODE{RS}{C}              ║
╠══════════════════════════════════════════════╣
║  {Y}🤖 Bot        :{RS} ☁️ CloudEarn                ║
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
║  {Y}🤖 Bot        :{RS} ☁️ CloudEarn                ║
║  {Y}👆 Tap Rate   :{RS} {LC}100 taps/request{RS}         ║
║  {Y}🎯 Reward     :{RS} {G}5 credits/tap{RS}             ║
║  {Y}🔓 Unlock     :{RS} {G}Ticket Aging Mode{RS}         ║
╚══════════════════════════════════════════════╝{RS}
"""

MINING_BANNER = f"""
{C}╔══════════════════════════════════════════════╗
║              {LC}⛏️  MINING MODE{RS}{C}                ║
╠══════════════════════════════════════════════╣
║  {Y}🤖 Bot        :{RS} ☁️ CloudEarn                ║
║  {Y}⛏️  Status     :{RS} {LC}Auto Start & Maintain{RS}    ║
║  {Y}💎 Rate       :{RS} {G}40 cloud/hour{RS}             ║
╚══════════════════════════════════════════════╝{RS}
"""

CONFIG_FILE = "cloud.json"

INIT_DATA = ""
AUTH_TOKEN = ""
APIKEY = ""
START_PARAM = ""
SUPABASE_URL = "https://supabase.cloudearn.org"
ORIGIN_URL = "https://cloudearn.org"
WATCH_DURATION = 20

NETWORKS = [
    "adsgram", "monetag", "richads", "onclicka", "gigapup",
    "towerads", "adexium", "adloop", "monetix", "tads",
]

MAX_RETRY = 1
HEADERS = {}
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

def set_data(force=False):
    global INIT_DATA, AUTH_TOKEN, APIKEY, START_PARAM, HEADERS
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)

    old_config = load_config()
    old_auth_token = old_config.get("auth_token", "") if old_config else ""

    print(f"\n{Y}🔑 SET INIT_DATA — ☁️ CloudEarn{RS}")
    print(f"{C}{'='*50}{RS}")
    init_data = input(f"{LC}init_data (wajib): {RS}").strip()
    if not init_data:
        print(f"{R}❌ init_data tidak boleh kosong!{RS}")
        time.sleep(2)
        return False

    print(f"{Y}Bearer token (opsional, Enter untuk skip):{RS}")
    auth_token = input(f"{LC}Bearer token: {RS}").strip()
    if not auth_token and old_auth_token:
        auth_token = old_auth_token
    if auth_token and not auth_token.startswith("Bearer "):
        auth_token = "Bearer " + auth_token

    INIT_DATA = init_data
    AUTH_TOKEN = auth_token
    APIKEY = AUTH_TOKEN.replace("Bearer ", "") if AUTH_TOKEN else ""

    parsed = urllib.parse.parse_qs(INIT_DATA)
    sp = parsed.get("start_param", [None])[0]
    START_PARAM = sp if (sp and sp != "null") else None

    HEADERS = {
        "x-telegram-init-data": INIT_DATA,
        "user-agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.6.4",
        "content-type": "application/json",
        "accept": "*/*",
        "origin": "https://cloudearn.org",
        "referer": "https://cloudearn.org/",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "x-requested-with": "org.telegram.messenger.web",
    }
    if AUTH_TOKEN:
        HEADERS["authorization"] = AUTH_TOKEN
        HEADERS["apikey"] = APIKEY

    save_config({
        "platform": "cloudearn",
        "init_data": INIT_DATA,
        "auth_token": AUTH_TOKEN,
        "apikey": APIKEY,
        "start_param": START_PARAM,
        "supabase_url": SUPABASE_URL,
        "origin_url": ORIGIN_URL,
        "headers": HEADERS
    })
    print(f"{G}✅ Config disimpan!{RS}")
    time.sleep(1.5)
    return True

# ============================================================
# SUPABASE
# ============================================================
def supabase_request(action, payload=None):
    url = f"{SUPABASE_URL}/functions/v1/api"
    resp = requests.post(url, params={"action": action}, json=payload or {}, headers=HEADERS)
    if resp.status_code != 200:
        try: err = resp.json()
        except: err = resp.text
        raise Exception(f"{resp.status_code}: {err}")
    return resp.json()

def _init_payload():
    return {
        "start_param": START_PARAM if START_PARAM else None,
        "fp_hash": "88bba40c3cc06e4bc78f354c012a1d5b0f0307f72934bc902352886f2d03cc9b",
        "webgl_hash": "bfc8fbb0012f8c92b0f1f0e178d08ba95ec000335360ca22edcf270a098ddab2",
        "audio_hash": "05d0c5571616fb4731d584d3a16738cc81dcd566dcb2598bee29200a1eeb4a46",
        "tz": "Asia/Jakarta",
        "lang": "id-ID",
        "platform": "Linux aarch64"
    }

def init_session(debug=True):
    if not HEADERS or not HEADERS.get("x-telegram-init-data"):
        return False
    try:
        r = supabase_request("init", _init_payload())
        if debug:
            u = r.get("user", {})
            print(f"{G}  [DEBUG] session OK | user={u.get('username','?')} | bal={u.get('balance_cloud',0)}{RS}")
        return True
    except Exception as e:
        if debug: print(f"{R}  [DEBUG] init gagal: {e}{RS}")
        return False

def get_user_data(): return supabase_request("init", _init_payload())
def get_ad_stats(): return supabase_request("ad_stats", {})

def issue_ticket(network):
    data = supabase_request("ad_ticket_issue", {"purpose": "task_ads", "network": network})
    return data.get("ticket")

def record_ad_view(network, ticket):
    supabase_request("record_ad_view", {"network": network, "ad_ticket_id": ticket})

# TAPTAP
def taptap_status(): return supabase_request("taptap_status", {})
def taptap_tap(taps): return supabase_request("taptap_tap", {"taps": taps})
def taptap_unlock(tid): return supabase_request("taptap_unlock", {"ad_ticket_id": tid})
def issue_taptap_ticket(network="adsgram"):
    return supabase_request("ad_ticket_issue", {"purpose": "taptap", "network": network}).get("ticket")

# MINING
def mining_status(): return supabase_request("mining_status", {})
def mining_start(): return supabase_request("mining_start", {})

# ============================================================
# FARMING — LOOP SAMPAI SEMUA NETWORK ABIS (limit server)
# ============================================================
def start_farming():
    global HEADERS

    if not HEADERS or not HEADERS.get("x-telegram-init-data"):
        print(f"{R}❌ Init_Data belum diset!{RS}")
        time.sleep(2)
        return

    if not init_session(debug=True):
        print(f"{R}❌ Session gagal!{RS}")
        input(f"{Y}Tekan Enter...{RS}")
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(f"\n{G}🚀 Inisialisasi session...{RS}")
    print(f"{G}✅ Session OK. Auto watch dimulai.{RS}")
    print(f"{Y}⏹ Bot stop OTOMATIS saat SEMUA network abis (limit server).{RS}")
    print(f"{Y}⏹ Tekan Ctrl+C untuk berhenti manual.{RS}\n")
    time.sleep(2)

    grand_success = 0
    grand_failed = 0
    grand_exhausted = 0
    cycle_count = 0

    # Set yang persisten lintas cycle: network yang bener-bener ABIS dari server
    exhausted_networks = set()
    # Set network yang gagal (error), coba lagi di cycle berikutnya
    # success di 1 cycle belum tentu habis, jadi di cycle berikutnya bisa dicoba lagi

    while True:
        try:
            cycle_count += 1

            # Tiap cycle, reset status success/failed — biar dicoba ulang
            # Yang persisten cuma exhausted_networks
            cycle_success = set()
            cycle_failed = set()
            cycle_done = set()

            cycle_start_time = time.time()

            while True:
                os.system('cls' if os.name == 'nt' else 'clear')
                print(BANNER)
                print(WATCH_BANNER)
                print(f"\n{C}═══ CYCLE #{cycle_count} ═══{RS}")
                print(f"{DIM}  Cycle ini  : "
                      f"{G}✅ {len(cycle_success)}{RS}  "
                      f"{R}❌ {len(cycle_failed)}{RS}  "
                      f"{Y}⛔ {len(exhausted_networks)}{RS}  "
                      f"| Selesai: {len(cycle_done)}/{len(NETWORKS)}{RS}")
                print(f"{DIM}  All-time    : "
                      f"{G}✅ {grand_success}{RS}  "
                      f"{R}❌ {grand_failed}{RS}  "
                      f"{Y}⛔ {grand_exhausted}{RS}\n")

                stats = get_ad_stats()
                cooldowns = stats.get("cooldowns", {})

                ready_networks = []
                for net in NETWORKS:
                    cd = cooldowns.get(net, 0)
                    if net in exhausted_networks:
                        print(f"  {Y}⛔ {net} — ABIS (limit server){RS}")
                        continue
                    if net in cycle_success:
                        print(f"  {G}✅ {net} — BERHASIL cycle ini{RS}")
                        continue
                    if net in cycle_failed:
                        print(f"  {R}❌ {net} — GAGAL cycle ini{RS}")
                        continue
                    if cd == 0:
                        ready_networks.append(net)
                        print(f"  {LC}▶  {net} — READY{RS}")
                    else:
                        print(f"  {Y}⏳ {net} — COOLDOWN{RS}")

                # ═══ CEK: APAKAH SEMUA SUDAH ABIS? ═══
                # Stop HANYA kalau semua network masuk exhausted_networks
                if len(exhausted_networks) >= len(NETWORKS):
                    print(f"\n{G}✅ SEMUA network sudah ABIS (limit server)!{RS}")
                    print(f"{Y}🏁 Bot berhenti.{RS}")
                    break

                # ═══ Kalau gak ada yang ready, tunggu ═══
                if not ready_networks:
                    # Kalau ada network di cycle_success/cycle_failed tapi belum di-exhaust,
                    # berarti mesti di-reset cycle, tapi tunggu cooldown dulu
                    if (len(cycle_success) + len(cycle_failed) + len(exhausted_networks)) >= len(NETWORKS):
                        # Semua network udah dicoba di cycle ini, reset cycle
                        # Tapi HANYA kalau masih ada yang belum exhausted
                        still_available = len(exhausted_networks) < len(NETWORKS)
                        if still_available:
                            print(f"\n{Y}🔄 Cycle #{cycle_count} selesai, tapi masih ada network belum abis.{RS}")
                            print(f"{Y}🔄 Reset cycle, tunggu 60s biar cooldown server lewat...{RS}")
                            grand_success += len(cycle_success)
                            grand_failed += len(cycle_failed)

                            for i in range(60, 0, -1):
                                sys.stdout.write(f"\r  {Y}⌛ Restart cycle in {i}s...{RS}   ")
                                sys.stdout.flush()
                                time.sleep(1)
                            print()
                            break  # break inner while → mulai cycle baru
                        else:
                            break

                    print(f"\n{Y}Semua cooldown. Tunggu 30s...{RS}")
                    time.sleep(30)
                    continue

                # ═══ Proses network ready ═══
                for net in ready_networks:
                    print(f"\n{LC}>>> Nonton iklan: {net}{RS}")

                    for attempt in range(1, MAX_RETRY + 2):
                        print(f"  {Y}Percobaan {attempt}/{MAX_RETRY+1}{RS}")

                        try:
                            ticket = issue_ticket(net)
                            print(f"  {Y}Ticket: {ticket}{RS}")
                            print(f"  {C}Nonton {WATCH_DURATION} detik...{RS}")

                            for i in range(WATCH_DURATION):
                                time.sleep(1)
                                sys.stdout.write(f"\r  {G}[{'#' * (i+1)}{' ' * (WATCH_DURATION - i - 1)}] {i+1}/{WATCH_DURATION}s{RS}")
                                sys.stdout.flush()
                            print()

                            record_ad_view(net, ticket)
                            print(f"  {G}✅ {net} BERHASIL{RS}")
                            cycle_success.add(net)
                            cycle_done.add(net)
                            break

                        except Exception as e:
                            err_str = str(e)

                            # ─── LIMIT/HABIS → masuk exhausted, PERMANEN skip ───
                            if ("ad_required" in err_str or
                                "no ads" in err_str.lower() or
                                "limit" in err_str.lower() or
                                "not available" in err_str.lower() or
                                "quota" in err_str.lower()):
                                print(f"  {Y}⛔ {net}: ABIS / limit server → masuk EXHAUSTED{RS}")
                                exhausted_networks.add(net)
                                cycle_done.add(net)
                                grand_exhausted += 1
                                break

                            # ─── Cooldown sementara → bukan exhausted ───
                            if "cooldown" in err_str.lower() or "too_early" in err_str.lower():
                                print(f"  {Y}⏳ {net}: cooldown sementara → SKIP cycle ini{RS}")
                                cycle_failed.add(net)
                                cycle_done.add(net)
                                break

                            # ─── Error lain → retry ───
                            print(f"  {R}❌ Gagal: {e}{RS}")

                            if attempt <= MAX_RETRY:
                                print(f"  {Y}🔄 Retry 3s...{RS}")
                                time.sleep(3)
                                continue
                            else:
                                print(f"  {R}⚠️ {net} gagal {MAX_RETRY+1}x → SKIP cycle ini (dicoba lagi nanti){RS}")
                                cycle_failed.add(net)
                                cycle_done.add(net)

                # Cek lagi apakah semua abis
                if len(exhausted_networks) >= len(NETWORKS):
                    break

        except KeyboardInterrupt:
            print(f"\n{R}⏹ Dihentikan user.{RS}")
            break
        except Exception as e:
            print(f"{R}❌ Error: {e}{RS}")
            time.sleep(10)

    # ═══ SUMMARY ═══
    print(f"\n{C}═══════════════════════════════════════════════════════════{RS}")
    print(f"{G}              🏁 FARMING SUMMARY (ALL-TIME){RS}")
    print(f"{C}═══════════════════════════════════════════════════════════{RS}")
    print(f"  Total cycle    : {cycle_count}")
    print()
    print(f"  {G}✅ Berhasil    : {grand_success}{RS}")
    print(f"  {R}❌ Gagal       : {grand_failed}{RS}")
    print(f"  {Y}⛔ Abis (limit): {grand_exhausted}{RS}")
    print(f"{C}═══════════════════════════════════════════════════════════{RS}\n")
    input(f"{C}Tekan Enter untuk kembali ke menu...{RS}")

# ============================================================
# BALANCE
# ============================================================
def check_balance():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    if not HEADERS or not HEADERS.get("x-telegram-init-data"):
        print(f"{R}❌ Init_Data belum diset!{RS}")
        time.sleep(2)
        return
    if not init_session(debug=True):
        input(f"{Y}Enter...{RS}")
        return
    print(f"{B}💰 Mengecek Balance...{RS}\n")
    try:
        data = get_user_data()
        u = data.get("user", {})
        if not u:
            print(f"{R}❌ Gagal ambil data.{RS}")
        else:
            print(f"{G}👤 {u.get('username','N/A')} (ID: {u.get('tg_id','N/A')}){RS}")
            print(f"{C}   {u.get('first_name','')} {u.get('last_name','')} — {u.get('country_name','N/A')}{RS}")
            print(f"{Y}───────────────────────────{RS}")
            print(f"{G}☁️ Cloud: {u.get('balance_cloud',0)}{RS}")
            print(f"{G}💰 USDT : {u.get('balance_usdt',0)}{RS}")
            print(f"{G}📈 Total Cloud: {u.get('total_earned_cloud',0)}{RS}")
            print(f"{G}📈 Total USDT : {u.get('total_earned_usdt',0)}{RS}")
            print(f"{C}👥 Refs: {u.get('referral_count',0)} — Earnings: {u.get('ref_earnings_cloud',0)}{RS}")
            print(f"{B}📊 {'✅ Premium' if u.get('is_premium') else '⬜ Free'}{RS}")
    except Exception as e:
        print(f"{R}❌ Error: {e}{RS}")
    input(f"\n{C}Enter untuk kembali...{RS}")

# ============================================================
# TAPTAP
# ============================================================
def start_taptap():
    global HEADERS
    if not HEADERS or not HEADERS.get("x-telegram-init-data"):
        print(f"{R}❌ Init_Data belum diset!{RS}")
        time.sleep(2)
        return
    if not init_session(debug=True):
        input(f"{Y}Enter...{RS}")
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(TAPTAP_BANNER)
    print(f"{Y}⏹ Ctrl+C untuk stop.{RS}\n")

    def wait_cd(sec, label):
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

                print(f"{C}📊 earned={G}{earned}{C}/{limit} | locked={Y}{locked}{C} | next_lock={Y}{next_lock}{RS}")

                if earned >= limit:
                    print(f"\n{G}✅ Limit harian tercapai. Bot berhenti.{RS}")
                    break

                if locked:
                    print(f"\n{Y}🔒 Locked! Unlock...{RS}")
                    ticket = None
                    try:
                        ticket = issue_taptap_ticket("adsgram")
                        print(f"  {G}✓ Ticket: {ticket}{RS}")
                    except Exception as e:
                        print(f"  {R}❌ Issue gagal: {e}{RS}")
                        wait_cd(30, "Retry")
                        continue

                    unlocked = False
                    waited = 0
                    while waited < TICKET_AGING_MAX:
                        try:
                            taptap_unlock(ticket)
                            print(f"  {G}✅ Unlocked! ({waited}s){RS}")
                            unlocked = True
                            break
                        except Exception as e:
                            if "ticket_too_early" in str(e):
                                wait_cd(TICKET_AGING_INTERVAL, f"aging ({waited}s)")
                                waited += TICKET_AGING_INTERVAL
                                continue
                            else:
                                print(f"  {R}❌ {e}{RS}")
                                break
                    if not unlocked:
                        wait_cd(30, "Retry")
                    continue

                remaining_lock = next_lock - earned
                remaining_total = limit - earned
                taps = min(TAPS_PER_REQUEST,
                           max(1, remaining_lock // TAP_VALUE),
                           max(1, remaining_total // TAP_VALUE))
                if taps <= 0: taps = 1

                print(f"{LC}👆 Tap {taps}...{RS}")
                try:
                    res = taptap_tap(taps)
                    print(f"  {G}✓ +{res.get('credited',0)} | earned: {res.get('earned_today',earned)} | locked: {res.get('locked',False)}{RS}")
                except Exception as e:
                    if "max" in str(e).lower() or "too many" in str(e).lower():
                        try:
                            res = taptap_tap(10)
                            print(f"  {G}✓ +{res.get('credited',0)}{RS}")
                        except Exception as e2:
                            print(f"  {R}❌ {e2}{RS}")
                    else:
                        print(f"  {R}❌ {e}{RS}")
                time.sleep(2)
            except Exception as e:
                print(f"{R}❌ Loop: {e}{RS}")
                time.sleep(5)
    except KeyboardInterrupt:
        print(f"\n{R}⏹ Stop.{RS}")
        time.sleep(1.5)

# ============================================================
# MINING
# ============================================================
def start_mining():
    global HEADERS
    if not HEADERS or not HEADERS.get("x-telegram-init-data"):
        print(f"{R}❌ Init_Data belum diset!{RS}")
        time.sleep(2)
        return
    if not init_session(debug=True):
        input(f"{Y}Enter...{RS}")
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)
    print(MINING_BANNER)
    print(f"{Y}⏹ Ctrl+C untuk stop.{RS}\n")

    try:
        while True:
            try:
                st = mining_status()
                state = st.get("state", "unknown")
                session = st.get("session")
                rate = st.get("rate_per_hour", 40)

                print(f"{C}📊 state: {LC}{state}{RS}")
                if session:
                    print(f"  {Y}• Expires: {session.get('expires_at','-')}{RS}")
                    print(f"  {Y}• Hours  : {session.get('hours_total',1)}{RS}")
                    print(f"  {Y}• Reward : {session.get('reward',0)} cloud{RS}")
                    print(f"  {Y}• Rate   : {rate}/hour{RS}")

                if state == "running":
                    print(f"\n{G}✅ Mining jalan. Cek 60s lagi...{RS}")
                    for i in range(60, 0, -1):
                        sys.stdout.write(f"\r  {Y}⏳ {i}s...{RS}   ")
                        sys.stdout.flush()
                        time.sleep(1)
                    print()
                    continue

                if state in ("idle", "unknown"):
                    print(f"\n{LC}⛏️  Start mining...{RS}")
                    try:
                        print(f"  {G}✓ {mining_start()}{RS}")
                        time.sleep(5)
                    except Exception as e:
                        print(f"  {R}❌ {e}{RS}")
                        time.sleep(10)
                else:
                    print(f"\n{Y}⚠️ state={state}, tunggu 30s{RS}")
                    time.sleep(30)
            except Exception as e:
                print(f"{R}❌ Loop: {e}{RS}")
                time.sleep(10)
    except KeyboardInterrupt:
        print(f"\n{R}⏹ Stop.{RS}")
        time.sleep(1.5)

# ============================================================
# MAIN
# ============================================================
def main():
    global HEADERS, INIT_DATA, AUTH_TOKEN, APIKEY, START_PARAM, SUPABASE_URL, ORIGIN_URL
    config = load_config()
    if config:
        INIT_DATA = config.get("init_data", "")
        AUTH_TOKEN = config.get("auth_token", "")
        APIKEY = config.get("apikey", "")
        START_PARAM = config.get("start_param", None)
        if START_PARAM == "null": START_PARAM = None
        SUPABASE_URL = config.get("supabase_url", "https://supabase.cloudearn.org")
        ORIGIN_URL = config.get("origin_url", "https://cloudearn.org")
        HEADERS = config.get("headers", {})

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print(BANNER)
        print(MENU)

        if HEADERS and HEADERS.get("x-telegram-init-data"):
            print(f"{G}🔑 Config: Aktif ✅{RS}")
        else:
            print(f"{R}🔑 Config: Belum diset ❌{RS}")

        choice = input(f"\n{LC}Select » {RS}").strip()

        if choice == "1": start_farming()
        elif choice == "2": set_data(force=True)
        elif choice == "3": check_balance()
        elif choice == "4": start_taptap()
        elif choice == "5": start_mining()
        elif choice == "0":
            print(f"\n{R}❌ Exit...{RS}")
            sys.exit(0)
        else:
            print(f"{R}❌ Invalid!{RS}")
            time.sleep(1)

if __name__ == "__main__":
    main()
