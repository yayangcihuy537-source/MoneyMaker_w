#!/usr/bin/env python3
"""
BOSSDOG BOT – AUTO FARM + DAILY + TASKS (AUTO ADS TASK)
🐶 B O S S D O G  B O T 🐶
Login menggunakan init_data (seperti Fruit Cut)
"""

import os
import sys
import json
import time
import requests
from datetime import datetime

# ============================================================
# WARNA
# ============================================================
R, G, Y, B, M, C, W, X = '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[97m', '\033[0m'
CYAN = '\033[1;96m'
GOLD = '\033[38;5;220m'
PINK = '\033[38;5;206m'
DIM = '\033[2;37m'
BLD = '\033[1m'
RS = '\033[0m'

# ============================================================
# BANNER
# ============================================================
BANNER = f"""
{CYAN}╔══════════════════════════════════════════════════════╗
║                                                      ║
║  ██████╗  ██████╗ ███████╗██████╗  ██████╗  ██████╗ ║
║  ██╔══██╗██╔═══██╗██╔════╝██╔══██╗██╔════╝ ██╔═══██╗║
║  ██████╔╝██║   ██║███████╗██║  ██║██  ███╗ ██║   ██║║
║  ██╔══██╗██║   ██║╚════██║██║  ██║██║   ██║██║   ██║║
║  ██████╔╝╚██████╔╝███████║██████╔╝╚██████╔╝╚██████╔╝║
║  ╚═════╝  ╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝ ║
║                                                      ║
║             {GOLD}🐶 B O S S D O G  B O T 🐶{RS}{CYAN}              ║
║                                                      ║
║        {G}⚡ AUTO CLAIM • TASKS • ADS • REWARDS ⚡{RS}{CYAN}       ║
║                                                      ║
╠══════════════════════════════════════════════════════╣
║  📱 TG  : {PINK}t.me/ScriptyXSouu{RS}{CYAN}                          ║
║  👨‍💻 DEV : {PINK}ScriptyXSou{RS}{CYAN}                              ║
╚══════════════════════════════════════════════════════╝{RS}
"""

MENU = f"""
{CYAN}╔══════════════════════════════════════════════╗
║              {GOLD}🐶 BOSSDOG MENU 🐶{RS}{CYAN}             ║
╠══════════════════════════════════════════════╣
║  {G}[1] 🚀 Start Auto Claim (Task + Farm){RS}{CYAN}        ║
║  {B}[2] 💰 Check Balance & Info{RS}{CYAN}               ║
║  {Y}[3] 🔑 Set InitData (login){RS}{CYAN}               ║
║  {C}[4] 📋 Show Tasks{RS}{CYAN}                         ║
║                                              ║
║  {R}[0] ❌ Exit{RS}{CYAN}                                ║
╚══════════════════════════════════════════════╝{RS}
"""

CONFIG_FILE = "bossdog_config.json"

# ============================================================
# GLOBAL
# ============================================================
BASE_URL = "https://bossdogsearn.site/api"
INIT_DATA = ""
TOKEN = ""

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
# LOGIN DENGAN INIT_DATA
# ============================================================
def login_with_init_data(init_data):
    """Kirim initData ke /api/auth/verify, dapatkan token bearer"""
    url = f"{BASE_URL}/auth/verify"
    payload = {
        "initData": init_data,
        "fingerprint": "3fb8034",  # bisa diganti atau dinamis
        "startParam": "ref_C26EB750"  # bisa disesuaikan
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) Telegram-Android/12.9.1 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
        "Accept": "*/*",
        "X-Requested-With": "org.telegram.messenger.web",
        "Origin": "https://bossdogsearn.site",
        "Referer": "https://bossdogsearn.site/?tgWebAppStartParam=ref_C26EB750",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
    }
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get('token') or data.get('accessToken') or data.get('bearer')
            if token:
                return token
            else:
                print(f"{R}❌ Login gagal: response tidak mengandung token{RS}")
                return None
        else:
            print(f"{R}❌ Login error: {resp.status_code} - {resp.text[:200]}{RS}")
            return None
    except Exception as e:
        print(f"{R}❌ Login request error: {e}{RS}")
        return None

# ============================================================
# HEADERS DENGAN TOKEN
# ============================================================
def headers():
    return {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) Telegram-Android/12.9.1 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
        "Accept": "*/*",
        "X-Requested-With": "org.telegram.messenger.web",
        "Origin": "https://bossdogsearn.site",
        "Referer": "https://bossdogsearn.site/?tgWebAppStartParam=ref_C26EB750",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
    }

# ============================================================
# FUNGSI API
# ============================================================
def api_get(endpoint):
    url = f"{BASE_URL}/{endpoint}"
    try:
        resp = requests.get(url, headers=headers(), timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"{R}❌ API Error: {resp.status_code} - {resp.text[:200]}{RS}")
            return None
    except Exception as e:
        print(f"{R}❌ Request error: {e}{RS}")
        return None

def api_post(endpoint, data=None):
    url = f"{BASE_URL}/{endpoint}"
    try:
        resp = requests.post(url, json=data or {}, headers=headers(), timeout=15)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"{R}❌ API Error: {resp.status_code} - {resp.text[:200]}{RS}")
            return None
    except Exception as e:
        print(f"{R}❌ Request error: {e}{RS}")
        return None

# ============================================================
# FITUR API
# ============================================================
def get_me():
    return api_get("me")

def get_farm():
    return api_get("farm")

def claim_dog(dog_key):
    return api_post(f"farm/dogs/{dog_key}/claim", {"clicked": True})

def get_daily():
    return api_get("daily")

def start_daily(provider="adsgram"):
    return api_post("daily/start", {"provider": provider})

def claim_daily(token):
    return api_post("daily/claim", {"token": token, "clicked": True})

def get_tasks():
    return api_get("tasks")

def start_task(task_key, provider="adsgram"):
    return api_post(f"tasks/{task_key}/start", {"provider": provider})

def claim_task(task_key, token):
    return api_post(f"tasks/{task_key}/claim", {"token": token, "clicked": True})

# ============================================================
# PROGRESS BAR
# ============================================================
def progress_bar(current, total, length=20, fill='█', empty='░'):
    pct = current / total
    filled = int(length * pct)
    bar = fill * filled + empty * (length - filled)
    return f"[{bar}] {int(pct*100)}%"

# ============================================================
# AUTO CLAIM
# ============================================================
def auto_claim():
    global TOKEN
    # Login dulu
    if not INIT_DATA:
        print(f"{R}❌ InitData belum diset!{RS}")
        return
    TOKEN = login_with_init_data(INIT_DATA)
    if not TOKEN:
        print(f"{R}❌ Gagal login dengan init_data.{RS}")
        return

    print(f"{G}🚀 Memulai Auto Claim (Farm + Daily + Task)...{RS}")
    print(f"{Y}⏹ Tekan Ctrl+C untuk berhenti.{RS}\n")

    cycle = 0
    all_tasks_done = False
    all_ads_exhausted = False

    while not all_tasks_done and not all_ads_exhausted:
        cycle += 1
        print(f"{C}--- Siklus {cycle} ---{RS}")

        # ---------- FARM ----------
        farm = get_farm()
        if farm:
            coins = farm.get('coins', 0)
            print(f"{G}💰 Coins: {coins}{RS}")
            dogs = farm.get('dogs', [])
            for dog in dogs:
                key = dog.get('key')
                name = dog.get('name', key)
                ready = dog.get('ready', False)
                pending = dog.get('pending', 0)
                claims_used = dog.get('claims', {}).get('used', 0)
                claims_limit = dog.get('claims', {}).get('limit', 7)
                if ready and pending > 0:
                    print(f"{Y}🐶 {name} siap dipanen ({pending} coins){RS}")
                    result = claim_dog(key)
                    if result and result.get('ok'):
                        print(f"{G}✅ {name} claimed! +{result.get('reward', 0)} coins, total: {result.get('coins', coins)}{RS}")
                    else:
                        print(f"{R}❌ Gagal claim {name}{RS}")
                else:
                    print(f"{DIM}🐶 {name}: pending {pending}, claims {claims_used}/{claims_limit}{RS}")
        else:
            print(f"{R}❌ Gagal ambil data farm{RS}")

        # ---------- DAILY ----------
        daily = get_daily()
        if daily:
            claimed_today = daily.get('claimedToday')
            reward = daily.get('reward', 0)
            streak = daily.get('streak', 0)
            require_ad = daily.get('requireAd', True)
            if not claimed_today:
                print(f"{Y}📅 Daily reward belum di-claim (streak {streak}){RS}")
                if require_ad:
                    print(f"{Y}📺 Perlu nonton iklan dulu...{RS}")
                    start_res = start_daily("adsgram")
                    if start_res and start_res.get('token'):
                        token = start_res['token']
                        print(f"{G}✅ Iklan dimulai, token: {token}{RS}")
                        duration = 30
                        for i in range(1, duration+1):
                            bar = progress_bar(i, duration)
                            sys.stdout.write(f"\r{DIM}{bar} {i}s/{duration} detik{RS}")
                            sys.stdout.flush()
                            time.sleep(1)
                        print()
                        claim_res = claim_daily(token)
                        if claim_res and claim_res.get('ok'):
                            print(f"{G}✅ Daily reward claimed! +{claim_res.get('reward', 0)} coins (streak {claim_res.get('streak', 0)}){RS}")
                        else:
                            print(f"{R}❌ Gagal claim daily{RS}")
                    else:
                        print(f"{R}❌ Gagal start daily iklan{RS}")
                else:
                    print(f"{Y}📺 Tidak perlu iklan, langsung claim...{RS}")
                    claim_res = claim_daily("")
                    if claim_res and claim_res.get('ok'):
                        print(f"{G}✅ Daily reward claimed! +{claim_res.get('reward', 0)} coins{RS}")
                    else:
                        print(f"{R}❌ Gagal claim daily{RS}")
            else:
                print(f"{G}✅ Daily sudah di-claim hari ini (streak {streak}){RS}")
        else:
            print(f"{R}❌ Gagal ambil daily status{RS}")

        # ---------- TASKS (AUTO ADS) ----------
        tasks = get_tasks()
        if tasks and isinstance(tasks, list):
            pending_tasks = [t for t in tasks if not t.get('done', False)]
            if not pending_tasks:
                print(f"{G}✅ Semua tasks selesai! Bot akan berhenti.{RS}")
                all_tasks_done = True
                break

            ad_tasks = []
            for t in pending_tasks:
                if t.get('requireAd', False) and t.get('repeatable', False):
                    key = t.get('key')
                    if not key:
                        continue
                    watched = t.get('watchedToday', 0)
                    limit = t.get('limit', 0)
                    if limit > 0 and watched >= limit:
                        print(f"{DIM}⏭️ Task {t['title']} sudah mencapai limit ({limit}), skip{RS}")
                        continue
                    ad_tasks.append(t)
            if not ad_tasks:
                print(f"{Y}⚠️ Tidak ada task iklan yang tersisa (semua sudah limit atau non-repeatable). Bot akan berhenti.{RS}")
                all_ads_exhausted = True
                break

            for task in ad_tasks:
                key = task['key']
                title = task.get('title', key)
                reward = task.get('reward', 0)
                print(f"{Y}📺 Menonton iklan untuk task: {title} (reward {reward}){RS}")
                start_res = start_task(key, "adsgram")
                if start_res and start_res.get('token'):
                    token = start_res['token']
                    print(f"{G}✅ Token didapat: {token}{RS}")
                    duration = 30
                    for i in range(1, duration+1):
                        bar = progress_bar(i, duration)
                        sys.stdout.write(f"\r{DIM}{bar} {i}s/{duration} detik{RS}")
                        sys.stdout.flush()
                        time.sleep(1)
                    print()
                    claim_res = claim_task(key, token)
                    if claim_res and claim_res.get('ok'):
                        coins = claim_res.get('coins', 0)
                        reward_got = claim_res.get('reward', 0)
                        print(f"{G}✅ Task {title} selesai! +{reward_got} coins, total: {coins}{RS}")
                    else:
                        print(f"{R}❌ Gagal claim task {title}{RS}")
                else:
                    print(f"{R}❌ Gagal start task {title}{RS}")
                time.sleep(1)
        else:
            print(f"{R}❌ Gagal ambil tasks{RS}")

        # Cek lagi
        tasks_after = get_tasks()
        if tasks_after and isinstance(tasks_after, list):
            remaining = [t for t in tasks_after if not t.get('done', False) and t.get('requireAd', False) and t.get('repeatable', False)]
            if not remaining:
                print(f"{G}✅ Tidak ada task iklan yang tersisa. Bot akan berhenti.{RS}")
                break
            any_available = False
            for t in remaining:
                key = t.get('key')
                if not key:
                    continue
                watched = t.get('watchedToday', 0)
                limit = t.get('limit', 0)
                if limit == 0 or watched < limit:
                    any_available = True
                    break
            if not any_available:
                print(f"{Y}⚠️ Semua task iklan sudah mencapai limit. Bot berhenti.{RS}")
                break

        if not all_tasks_done and not all_ads_exhausted:
            wait = 10
            print(f"{Y}⏳ Tunggu {wait} detik sebelum siklus berikutnya...{RS}")
            for i in range(wait, 0, -1):
                sys.stdout.write(f"\r{DIM}⏳ {i}s{RS}")
                sys.stdout.flush()
                time.sleep(1)
            print()

    print(f"\n{G}✅ Bot berhenti. Semua task selesai atau iklan habis.{RS}")

# ============================================================
# CEK BALANCE
# ============================================================
def check_balance():
    global TOKEN
    if not INIT_DATA:
        print(f"{R}❌ InitData belum diset!{RS}")
        return
    TOKEN = login_with_init_data(INIT_DATA)
    if not TOKEN:
        print(f"{R}❌ Gagal login.{RS}")
        return

    print(f"{B}💰 Mengecek Balance & Info...{RS}\n")
    me = get_me()
    if me:
        user = me.get('user', {})
        config = me.get('config', {})
        coin_name = config.get('coin', {}).get('name', 'BossCoin')
        print(f"{G}👤 User: {user.get('firstName', 'N/A')} (@{user.get('username', 'N/A')}){RS}")
        print(f"{G}🆔 Telegram ID: {user.get('telegramId', 'N/A')}{RS}")
        print(f"{G}💰 Coins: {user.get('coins', 0)} {coin_name}{RS}")
        print(f"{G}📈 Referrals: {user.get('referrals', 0)}{RS}")
        print(f"{G}✅ Verified: {'Ya' if user.get('isVerified') else 'Tidak'}{RS}")
        print(f"{G}📊 Daily Streak: {user.get('dailyStreak', 0)}{RS}")
        print(f"{G}📺 Ads Watched: {user.get('adsWatchedTotal', 0)}{RS}")
        print(f"{Y}───────────────────────────{RS}")
        print(f"{C}💲 USDT Rate: {config.get('coin', {}).get('usdtRate', 'N/A')} coins per USDT{RS}")
        print(f"{C}💳 Withdraw Min: {config.get('withdraw', {}).get('minAmount', 'N/A')} coins{RS}")
    else:
        print(f"{R}❌ Gagal mengambil data user.{RS}")

# ============================================================
# TAMPILKAN TASKS
# ============================================================
def show_tasks():
    global TOKEN
    if not INIT_DATA:
        print(f"{R}❌ InitData belum diset!{RS}")
        return
    TOKEN = login_with_init_data(INIT_DATA)
    if not TOKEN:
        print(f"{R}❌ Gagal login.{RS}")
        return

    print(f"{C}📋 Daftar Tasks:{RS}\n")
    tasks = get_tasks()
    if tasks and isinstance(tasks, list):
        if not tasks:
            print(f"{G}✅ Tidak ada tasks.{RS}")
            return
        for t in tasks:
            done = "✅" if t.get('done') else "⬜"
            title = t.get('title', 'Unknown')
            reward = t.get('reward', 0)
            tab = t.get('tab', '')
            require_ad = "📺" if t.get('requireAd') else ""
            repeat = "🔄" if t.get('repeatable') else ""
            watched = t.get('watchedToday', 0)
            limit = t.get('limit', 0)
            lim = f" ({watched}/{limit})" if limit > 0 else ""
            print(f"{done} {title} (reward {reward}, {tab}) {require_ad} {repeat} {lim}")
    else:
        print(f"{R}❌ Gagal ambil tasks{RS}")

# ============================================================
# SET INIT DATA
# ============================================================
def set_init_data():
    global INIT_DATA
    print(f"{Y}🔑 Masukkan InitData (panjang):{RS}")
    print(f"{DIM}Paste di sini, lalu tekan Enter 2x untuk selesai{RS}")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    data = "".join(lines).strip()
    if data:
        INIT_DATA = data
        save_config({"init_data": INIT_DATA})
        print(f"{G}✅ InitData disimpan!{RS}")
    else:
        print(f"{R}❌ InitData kosong!{RS}")

# ============================================================
# MAIN
# ============================================================
def main():
    global INIT_DATA, TOKEN
    os.system('clear' if os.name == 'posix' else 'cls')
    print(BANNER)
    print(MENU)

    config = load_config()
    if config and config.get('init_data'):
        INIT_DATA = config['init_data']
        print(f"{G}🔑 InitData ditemukan di config.{RS}")
    else:
        print(f"{R}🔑 InitData belum diset. Silakan menu 3.{RS}")

    while True:
        choice = input(f"\n{CYAN}Select Menu » {RS}").strip()

        if choice == "1":
            if not INIT_DATA:
                print(f"{R}❌ InitData belum diset!{RS}")
                time.sleep(1)
                continue
            auto_claim()
            input(f"\n{C}Tekan Enter untuk kembali...{RS}")
        elif choice == "2":
            if not INIT_DATA:
                print(f"{R}❌ InitData belum diset!{RS}")
                time.sleep(1)
                continue
            check_balance()
            input(f"\n{C}Tekan Enter untuk kembali...{RS}")
        elif choice == "3":
            set_init_data()
            input(f"\n{C}Tekan Enter untuk kembali...{RS}")
        elif choice == "4":
            if not INIT_DATA:
                print(f"{R}❌ InitData belum diset!{RS}")
                time.sleep(1)
                continue
            show_tasks()
            input(f"\n{C}Tekan Enter untuk kembali...{RS}")
        elif choice == "0":
            print(f"\n{R}❌ Exit...{RS}")
            sys.exit(0)
        else:
            print(f"{R}❌ Pilihan tidak valid!{RS}")
            time.sleep(1)

        os.system('clear' if os.name == 'posix' else 'cls')
        print(BANNER)
        print(MENU)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}⏹ Dihentikan user.{RS}")
        sys.exit(0)

