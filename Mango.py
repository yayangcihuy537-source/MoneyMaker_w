#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🥭 MANGO CASH AUTO WATCH BOT v2.0
- Reward + limit aware (sesuai app)
- Adsgram fix: cooldown ≤120s tunggu & retry (gak skip)
- Skip network kalau error/limit, jangan spam
- Jeda 7s antar network
- Auto-stop kalau semua limit harian kena
"""

import requests
import time
import urllib.parse
import sys
import os
import json
import random

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
M = '\033[95m'

# ============================================================
# BANNER — MANGO CASH 🥭
# ============================================================
BANNER = f"""
{C}╔══════════════════════════════════════════════════════════╗
║                                                          ║
║    ███╗   ███╗ █████╗ ███╗   ██╗ ██████╗  ██████╗       ║
║    ████╗ ████║██╔══██╗████╗  ██║██╔════╝ ██╔═══██╗      ║
║    ██╔████╔██║███████║██╔██╗ ██║██║  ███╗██║   ██║      ║
║    ██║╚██╔╝██║██╔══██║██║╚██╗██║██║   ██║██║   ██║      ║
║    ██║ ╚═╝ ██║██║  ██║██║ ╚████║╚██████╔╝╚██████╔╝      ║
║    ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝       ║
║                                                          ║
║                     {Y}🥭  MangoCash  🥭{RS}{C}                  ║
║                                                          ║
║              {LC}Developed by SCRIPTYXSOUU{RS}{C}                 ║
║         {G}AUTO FARM • AUTO CLAIM • AUTO TASK{RS}{C}             ║
╚══════════════════════════════════════════════════════════╝{RS}
"""

WATCH_BANNER = f"""
{C}╔══════════════════════════════════════════════╗
║              {LC}📺 WATCH ADS MODE{RS}{C}              ║
╠══════════════════════════════════════════════╣
║  {Y}🤖 Bot        :{RS} 🥭 MangoCash               ║
║  {Y}⏳ Status     :{RS} {LC}Watching Advertisement...{RS}  ║
║  {Y}🎯 Reward     :{RS} {G}Waiting...{RS}                 ║
║  {R}⚡ Please Wait, Don't Close Script{RS}         ║
╚══════════════════════════════════════════════╝{RS}
"""

MENU = f"""
{C}╔══════════════════════════════════════════════╗
║              {Y}🥭 MangoCash 🥭{RS}{C}                ║
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
║  {Y}🤖 Bot        :{RS} 🥭 MangoCash               ║
║  {Y}👆 Tap Rate   :{RS} {LC}100 taps/request{RS}         ║
║  {Y}🎯 Reward     :{RS} {G}5 credits/tap{RS}             ║
║  {Y}🔓 Unlock     :{RS} {G}Ticket Aging Mode{RS}         ║
╚══════════════════════════════════════════════╝{RS}
"""

MINING_BANNER = f"""
{C}╔══════════════════════════════════════════════╗
║              {LC}⛏️  MINING MODE{RS}{C}                ║
╠══════════════════════════════════════════════╣
║  {Y}🤖 Bot        :{RS} 🥭 MangoCash               ║
║  {Y}⛏️  Status     :{RS} {LC}Auto Start & Maintain{RS}    ║
║  {Y}💎 Rate       :{RS} {G}40 cloud/hour{RS}             ║
╚══════════════════════════════════════════════╝{RS}
"""

CONFIG_FILE = "config.json"

INIT_DATA = ""
AUTH_TOKEN = ""
APIKEY = ""
START_PARAM = ""
SUPABASE_URL = "https://supabase.mangocash.tech"
ORIGIN_URL = "https://mangocash.tech"

# ============================================================
# TUNING
# ============================================================
WATCH_DURATION         = 20
DELAY_BETWEEN_NETWORKS = 7      # jeda antar network
COOLDOWN_SHORT_MAX     = 120    # ≤ 120s → tunggu & retry
TICKET_MAX_RETRY       = 3
TICKET_RETRY_DELAY     = (3, 8)

# ============================================================
# NETWORK MAP — MangoCash
# { name: {reward, limit, label} }
# ============================================================
NETWORKS = {
    "adsgram":   {"reward": 30, "limit": 10, "label": "Adsgram"},
    "monetag":   {"reward": 10, "limit": 8,  "label": "Monetag"},
    "towerads":  {"reward": 10, "limit": 10, "label": "TowerAds"},
    "monetix":   {"reward": 5,  "limit": 15, "label": "Monetix"},
    "tads":      {"reward": 5,  "limit": 10, "label": "Tads"},
    "richads":   {"reward": 5,  "limit": 8,  "label": "RichAds"},
    "onclicka":  {"reward": 5,  "limit": 8,  "label": "OnClickA"},
    "gigapup":   {"reward": 5,  "limit": 3,  "label": "GigaPup"},
    "adexium":   {"reward": 5,  "limit": 10, "label": "Adexium"},
    "adloop":    {"reward": 5,  "limit": 30, "label": "Adloop"},
}

HEADERS = {}
TAPS_PER_REQUEST      = 100
TAP_VALUE             = 5
TICKET_AGING_INTERVAL = 15
TICKET_AGING_MAX      = 180

# Default bearer / apikey MangoCash (lu udah kasih)
DEFAULT_APIKEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc4NTc3MjY4MCwiZXhwIjo0OTQxNDQ2MjgwLCJyb2xlIjoiYW5vbiJ9.X3wvaxDhs_ObrxK1UOPk57lyBKIh4jVEDVxfo3P98UU"


# ============================================================
# HELPERS — cooldown / limit detection
# ============================================================
def now_ms():
    return int(time.time() * 1000)


def _norm_cooldown(cd_val):
    """
    Normalize cooldown dari server.
    Server bisa balikin:
      - epoch ms (1790578327802)
      - epoch s  (1790578327)
      - durasi s (90)
      - 0
    Return sisa detik (int >= 0).
    """
    try:
        v = int(cd_val or 0)
    except Exception:
        return 0
    if v <= 0:
        return 0
    if v > 10_000_000_000:        # epoch ms
        return max(0, (v - now_ms()) // 1000)
    if v > 10_000_000:            # epoch s
        return max(0, v - int(time.time()))
    return max(0, v)              # durasi detik


def is_limit_error(err_str):
    s = str(err_str).lower()
    keys = ("ad_required", "no ads", "not available", "quota",
            "limit reached", "daily limit", "exhausted",
            "unavailable", "no ad", "habis", "batas")
    return any(k in s for k in keys)


def is_cooldown_error(err_str):
    s = str(err_str).lower()
    return ("cooldown" in s) or ("too_early" in s) or ("too early" in s) \
           or ("try again" in s) or ("please wait" in s)


def _issue_ticket_retry(net, max_retry=TICKET_MAX_RETRY):
    """
    Issue ticket dengan retry + backoff.
    Return (ticket, err_type):
      err_type = None       → sukses
      err_type = 'limit'    → network abis, skip permanen
      err_type = 'short_cd' → cooldown, masuk waiting
      err_type = 'error'    → error lain, skip cycle ini
    """
    last_err = None
    for attempt in range(1, max_retry + 1):
        try:
            t = issue_ticket(net)
            if t:
                return t, None
            last_err = "empty ticket"
        except Exception as e:
            last_err = str(e)
            if is_limit_error(last_err):
                return None, "limit"
        if attempt < max_retry:
            d = random.uniform(*TICKET_RETRY_DELAY)
            sys.stdout.write(f"\r  {Y}↻ ticket retry {attempt}/{max_retry} dalam {d:.1f}s...{RS}")
            sys.stdout.flush()
            time.sleep(d)
            sys.stdout.write("\r" + " " * 55 + "\r")
            sys.stdout.flush()
    if last_err and is_limit_error(last_err):
        return None, "limit"
    if last_err and is_cooldown_error(last_err):
        return None, "short_cd"
    return None, "error"


# ============================================================
# CONFIG
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

    print(f"\n{Y}🔑 SET INIT_DATA — 🥭 MangoCash{RS}")
    print(f"{C}{'='*50}{RS}")
    init_data = input(f"{LC}init_data (wajib): {RS}").strip()
    if not init_data:
        print(f"{R}❌ init_data tidak boleh kosong!{RS}")
        time.sleep(2)
        return False

    print(f"{Y}Bearer token (opsional, Enter untuk pakai default):{RS}")
    auth_token = input(f"{LC}Bearer token: {RS}").strip()
    if not auth_token and old_auth_token:
        auth_token = old_auth_token
    if not auth_token:
        auth_token = "Bearer " + DEFAULT_APIKEY
    if auth_token and not auth_token.startswith("Bearer "):
        auth_token = "Bearer " + auth_token

    INIT_DATA = init_data
    AUTH_TOKEN = auth_token
    APIKEY = AUTH_TOKEN.replace("Bearer ", "") if AUTH_TOKEN else DEFAULT_APIKEY

    parsed = urllib.parse.parse_qs(INIT_DATA)
    sp = parsed.get("start_param", [None])[0]
    START_PARAM = sp if (sp and sp != "null") else None

    HEADERS = {
        "x-telegram-init-data": INIT_DATA,
        "user-agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
        "content-type": "application/json",
        "accept": "*/*",
        "origin": "https://mangocash.tech",
        "referer": "https://mangocash.tech/",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "x-requested-with": "org.telegram.messenger.web",
    }
    if AUTH_TOKEN:
        HEADERS["authorization"] = AUTH_TOKEN
        HEADERS["apikey"] = APIKEY

    save_config({
        "platform": "mangocash",
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
def supabase_request(action, payload=None, timeout=30):
    url = f"{SUPABASE_URL}/functions/v1/api"
    resp = requests.post(url, params={"action": action}, json=payload or {},
                         headers=HEADERS, timeout=timeout)
    if resp.status_code != 200:
        try: err = resp.json()
        except: err = resp.text
        raise Exception(f"{resp.status_code}: {err}")
    return resp.json()


def _init_payload():
    return {
        "start_param": START_PARAM if START_PARAM else None,
        "fp_hash": "25fe1a2a59b2722cc52416d6b5d5f280bd5dd2b126a7ae218d3e22963c8368c3",
        "webgl_hash": "bfc8fbb0012f8c92b0f1f0e178d08ba95ec000335360ca22edcf270a098ddab2",
        "audio_hash": "5d34e8dc021286e3222015f1b08b000fec5e67dd5beb3aae202a99c57c7f4ec6",
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
def get_ad_stats():  return supabase_request("ad_stats", {})


def issue_ticket(network):
    data = supabase_request("ad_ticket_issue", {"purpose": "task_ads", "network": network})
    return data.get("ticket")


def record_ad_view(network, ticket):
    return supabase_request("record_ad_view", {"network": network, "ad_ticket_id": ticket})


# TAPTAP
def taptap_status(): return supabase_request("taptap_status", {})
def taptap_tap(taps): return supabase_request("taptap_tap", {"taps": taps})
def taptap_unlock(tid): return supabase_request("taptap_unlock", {"ad_ticket_id": tid})
def issue_taptap_ticket(network="adsgram"):
    return supabase_request("ad_ticket_issue", {"purpose": "taptap", "network": network}).get("ticket")


# MINING
def mining_status(): return supabase_request("mining_status", {})
def mining_start():  return supabase_request("mining_start", {})


# ============================================================
# FARMING v2.0 — reward+limit aware, adsgram cooldown fix, jeda 7s
# ============================================================
def start_farming():
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
    print(f"\n{G}🚀 Session OK. Auto watch dimulai.{RS}")
    print(f"{Y}⏱  Jeda antar network    : {DELAY_BETWEEN_NETWORKS}s{RS}")
    print(f"{Y}⏳ Cooldown ≤ {COOLDOWN_SHORT_MAX}s   : tunggu & retry network itu{RS}")
    print(f"{Y}⏭  Cooldown > {COOLDOWN_SHORT_MAX}s   : skip, lanjut yang lain{RS}")
    print(f"{Y}⏹ Auto-stop saat SEMUA network limit harian tercapai.{RS}")
    print(f"{Y}⏹ Ctrl+C untuk berhenti manual.{RS}\n")
    time.sleep(2)

    grand_success = 0
    grand_failed = 0
    grand_exhausted = 0
    total_cloud_earned = 0
    cycle_count = 0

    done_networks = set()

    try:
        while True:
            cycle_count += 1

            # ===== AMBIL STATS =====
            try:
                stats = get_ad_stats()
            except Exception as e:
                print(f"{R}❌ Gagal ambil ad_stats: {e}{RS}")
                time.sleep(15)
                continue

            watched   = stats.get("data", {}) or {}
            cooldowns = stats.get("cooldowns", {}) or {}

            # ===== RENDER TABLE =====
            os.system('cls' if os.name == 'nt' else 'clear')
            print(BANNER)
            print(f"{C}═══ CYCLE #{cycle_count} ═══{RS}")
            print(f"{DIM}  All-time: {G}✅ {grand_success}{RS}  "
                  f"{R}❌ {grand_failed}{RS}  "
                  f"{Y}⛔ {grand_exhausted}{RS}  "
                  f"| {G}+{total_cloud_earned} cloud{RS}\n")

            print(f"  {W}{'Network':<12}{'Reward':<9}{'Sisa':<6}{'Limit':<7}{'Status'}{RS}")
            print(f"  {DIM}{'─'*58}{RS}")

            ready   = []
            waiting = []
            for net, cfg in NETWORKS.items():
                label  = cfg["label"]
                reward = cfg["reward"]
                limit  = cfg["limit"]
                cnt    = int(watched.get(net, 0) or 0)
                remaining = max(0, limit - cnt)
                cd_left_s = _norm_cooldown(cooldowns.get(net, 0))

                if remaining <= 0:
                    done_networks.add(net)
                    print(f"  {G}{label:<12}{'+'+str(reward)+' 🥭':<9}{'0':<6}{limit:<7}✅ DONE{RS}")
                    continue

                if cd_left_s > 0:
                    if cd_left_s <= COOLDOWN_SHORT_MAX:
                        waiting.append((net, cd_left_s))
                        print(f"  {Y}{label:<12}{'+'+str(reward)+' 🥭':<9}{remaining:<6}{limit:<7}⏳ CD {cd_left_s}s → WAIT{RS}")
                    else:
                        print(f"  {M}{label:<12}{'+'+str(reward)+' 🥭':<9}{remaining:<6}{limit:<7}⏭ CD {cd_left_s}s → SKIP{RS}")
                    continue

                ready.append(net)
                print(f"  {LC}{label:<12}{'+'+str(reward)+' 🥭':<9}{remaining:<6}{limit:<7}▶ READY{RS}")

            print(f"\n  {DIM}Ready: {len(ready)} | Waiting: {len(waiting)} | Done: {len(done_networks)}/{len(NETWORKS)}{RS}")

            # ===== CEK: SEMUA LIMIT? =====
            all_done = all(
                int(watched.get(n, 0) or 0) >= NETWORKS[n]["limit"]
                for n in NETWORKS
            )
            if all_done:
                print(f"\n{G}🏁 SEMUA network sudah limit harian! Bot stop.{RS}")
                break

            # ===== PROSES NETWORK READY =====
            for net in ready:
                if net in done_networks:
                    continue

                cfg    = NETWORKS[net]
                label  = cfg["label"]
                reward = cfg["reward"]
                limit  = cfg["limit"]

                # pre-check ulang
                try:
                    s2 = get_ad_stats()
                    w2 = s2.get("data", {}) or {}
                    c2 = s2.get("cooldowns", {}) or {}
                    if int(w2.get(net, 0) or 0) >= limit:
                        print(f"\n{G}  ✅ {label}: limit tercapai, skip.{RS}")
                        done_networks.add(net)
                        continue
                    cd2 = _norm_cooldown(c2.get(net, 0))
                    if cd2 > 0:
                        if cd2 <= COOLDOWN_SHORT_MAX:
                            waiting.append((net, cd2))
                            print(f"\n{Y}  ⏳ {label}: cooldown {cd2}s → wait.{RS}")
                        else:
                            print(f"\n{M}  ⏭ {label}: cooldown {cd2}s → skip.{RS}")
                        continue
                except Exception:
                    pass

                print(f"\n{LC}  ▶ Nonton iklan: {label} (+{reward} 🥭){RS}")

                # ===== ISSUE TICKET (retry) =====
                ticket, err_type = _issue_ticket_retry(net)
                print()

                if not ticket:
                    if err_type == "limit":
                        print(f"  {Y}⛔ {label}: LIMIT/ABIS → skip permanen.{RS}")
                        done_networks.add(net)
                        grand_exhausted += 1
                    elif err_type == "short_cd":
                        print(f"  {Y}⏳ {label}: cooldown → masuk waiting.{RS}")
                        waiting.append((net, 15))
                    else:
                        print(f"  {R}❌ {label}: ticket error → skip cycle ini.{RS}")
                        grand_failed += 1
                    time.sleep(DELAY_BETWEEN_NETWORKS)
                    continue

                print(f"  {Y}Ticket: {ticket}{RS}")

                # ===== NONTON AD =====
                print(f"  {C}Nonton {WATCH_DURATION}s...{RS}")
                for i in range(WATCH_DURATION):
                    time.sleep(1)
                    bar_len = 20
                    filled = int((i + 1) / WATCH_DURATION * bar_len)
                    bar = '█' * filled + '░' * (bar_len - filled)
                    sys.stdout.write(f"\r  {G}[{bar}] {i+1:2d}/{WATCH_DURATION}s{RS}")
                    sys.stdout.flush()
                print()

                # ===== RECORD =====
                try:
                    res = record_ad_view(net, ticket)
                    got = int(res.get("reward", reward) or reward)
                    total_cloud_earned += got
                    grand_success += 1
                    print(f"  {G}✅ {label}: +{got} 🥭{RS}")

                    # refresh limit / cooldown
                    try:
                        s3 = get_ad_stats()
                        w3 = s3.get("data", {}) or {}
                        c3 = s3.get("cooldowns", {}) or {}
                        cnt_now = int(w3.get(net, 0) or 0)
                        if cnt_now >= limit:
                            done_networks.add(net)
                            print(f"  {G}   {label} limit tercapai ({cnt_now}/{limit}).{RS}")
                        else:
                            cd3 = _norm_cooldown(c3.get(net, 0))
                            if cd3 > 0:
                                if cd3 <= COOLDOWN_SHORT_MAX:
                                    waiting.append((net, cd3))
                                print(f"  {Y}   {label} cooldown {cd3}s.{RS}")
                    except Exception:
                        pass

                except Exception as e:
                    err = str(e)
                    if is_limit_error(err):
                        print(f"  {Y}⛔ {label}: LIMIT saat record → skip permanen.{RS}")
                        done_networks.add(net)
                        grand_exhausted += 1
                    elif is_cooldown_error(err):
                        print(f"  {Y}⏳ {label}: cooldown saat record → tunggu.{RS}")
                        waiting.append((net, 15))
                        grand_failed += 1
                    else:
                        print(f"  {R}❌ {label}: record error → skip.{RS}")
                        print(f"  {DIM}   {err[:120]}{RS}")
                        grand_failed += 1

                # ===== JEDA 7 DETIK antar network =====
                print(f"  {DIM}   ⏱ jeda {DELAY_BETWEEN_NETWORKS}s...{RS}")
                time.sleep(DELAY_BETWEEN_NETWORKS)

            # ===== PROSES NETWORK WAITING (cooldown pendek) =====
            if waiting:
                waiting.sort(key=lambda x: x[1])
                min_wait = waiting[0][1]
                to_wait = min(min_wait + 2, COOLDOWN_SHORT_MAX + 5)

                print(f"\n{Y}⏳ Menunggu cooldown pendek: {len(waiting)} network...{RS}")
                for i in range(to_wait, 0, -1):
                    n_show = ", ".join(n for n, _ in waiting[:3])
                    if len(waiting) > 3:
                        n_show += f" +{len(waiting)-3}"
                    sys.stdout.write(f"\r  {Y}⌛ {i:3d}s — next: {n_show}{RS}   ")
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write("\r" + " " * 75 + "\r")
                sys.stdout.flush()

            # ===== Kalau gak ada ready & gak ada waiting =====
            if not ready and not waiting:
                still = [
                    n for n in NETWORKS
                    if int(watched.get(n, 0) or 0) < NETWORKS[n]["limit"]
                    and n not in done_networks
                ]
                if not still:
                    break
                print(f"\n{Y}⚠ Gak ada network ready/waiting. Cek ulang 60s...{RS}")
                for i in range(60, 0, -1):
                    sys.stdout.write(f"\r  {Y}⌛ recheck {i}s...{RS}   ")
                    sys.stdout.flush()
                    time.sleep(1)
                print()

            time.sleep(2)

    except KeyboardInterrupt:
        print(f"\n{R}⏹ Dihentikan user.{RS}")
    except Exception as e:
        print(f"{R}❌ Error: {e}{RS}")
        import traceback; traceback.print_exc()

    # ===== SUMMARY =====
    print(f"\n{C}═══════════════════════════════════════════════════════════{RS}")
    print(f"{G}              🏁 FARMING SUMMARY{RS}")
    print(f"{C}═══════════════════════════════════════════════════════════{RS}")
    print(f"  Cycles         : {cycle_count}")
    print(f"  {G}✅ Berhasil   : {grand_success}{RS}")
    print(f"  {R}❌ Gagal      : {grand_failed}{RS}")
    print(f"  {Y}⛔ Limit/Abis : {grand_exhausted}{RS}")
    print(f"  {G}🥭 Cloud      : +{total_cloud_earned}{RS}")
    print(f"  {LC}🎯 Done net  : {len(done_networks)}/{len(NETWORKS)}{RS}")
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
            print(f"{G}🥭 Cloud: {u.get('balance_cloud',0)}{RS}")
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
        SUPABASE_URL = config.get("supabase_url", "https://supabase.mangocash.tech")
        ORIGIN_URL = config.get("origin_url", "https://mangocash.tech")
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
