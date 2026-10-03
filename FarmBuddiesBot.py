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

# ═══════════ UI ═══════════

def display_banner():
    os.system("clear" if os.name == "posix" else "cls")
    print("\033[1;32m")
    print(r"""  ____  _   _ ____  ____ ___ _____ ____  
 | __ )| | | |  _ \|  _ \_ _| ____/ ___| 
 |  _ \| | | | | | | | | | ||  _| \___ \ 
 | |_) | |_| | |_| | |_| | || |___ ___) |
 |____/ \___/|____/|____/___|_____|____/ """)
    print("\033[1;31mScript by AHD1905 — Fixed by Kyriel v4\033[0m")
    print("\033[0;37m--------------------------------------------------\033[0m\n")

def custom_log(msg):
    lower = msg.lower()
    prefix = "✨ "
    if any(k in lower for k in ["water", "air", "siram", "💧"]): prefix = "💧 "
    elif any(k in lower for k in ["plant", "tanam", "bibit", "🌱"]): prefix = "🌱 "
    elif any(k in lower for k in ["harvest", "panen", "🌾"]): prefix = "🌾 "
    elif any(k in lower for k in ["ads", "iklan", "watch", "nonton", "📺"]): prefix = "📺 "
    elif any(k in lower for k in ["error", "gagal", "❌"]): prefix = "❌ "
    elif any(k in lower for k in ["auth", "token", "🔑"]): prefix = "🔑 "
    elif any(k in lower for k in ["coin", "koin", "💰"]): prefix = "💰 "
    elif any(k in lower for k in ["beli", "buy", "seed", "🛒"]): prefix = "🛒 "

    clean = msg
    for em in ["💧","🌱","🌿","✨","❌","🔑","🎉","💰","🛒","📺","🌾"]:
        clean = clean.replace(em, "")
    clean = clean.strip()
    final = f"{prefix}{clean}"
    if len(final) > 68:
        final = final[:65] + "..."

    print("\033[1;32m╔══════════════════════════════════════════════════════════════════════╗\033[0m")
    print(f"\033[1;32m║\033[0m \033[1;97m{final.ljust(68)}\033[0m \033[1;32m║\033[0m")
    print("\033[1;32m╚══════════════════════════════════════════════════════════════════════╝\033[0m")

def isi_data():
    display_banner()
    print("="*50)
    print("      SETUP AKUN FARM BUDDIES BOT")
    print("="*50)
    init_data = input("Telegram init_data / query_id: ").strip()
    device_id = input("deviceId (dev_...): ").strip()
    fingerprint = input("x-farm-fp / fingerprint: ").strip()

    data = {
        "init_data": init_data,
        "device_id": device_id,
        "fingerprint": fingerprint,
        "base_url": "https://farm-buddies-api.nhathaybip2000.workers.dev/api"
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)
    print("\n✅ Config disimpan!")
    time.sleep(2)

# ═══════════ HTTP ═══════════

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
        "Content-Type": "application/json",
        "Accept": "*/*",
        "Origin": "https://farm-buddies-4g5.pages.dev",
        "Referer": "https://farm-buddies-4g5.pages.dev/",
        "authorization": f"Bearer {CURRENT_TOKEN}",
        "x-farm-fp": FARM_FP
    }

def authenticate():
    global CURRENT_TOKEN
    try:
        custom_log("[AUTH] Minta token baru...")
        res = requests.post(
            f"{BASE_URL}/auth/telegram",
            headers={"Content-Type": "application/json"},
            json={"initData": INIT_DATA, "deviceId": DEVICE_ID, "fingerprint": FARM_FP},
            timeout=15
        )
        if res.status_code == 200:
            data = res.json()
            if data.get("ok"):
                CURRENT_TOKEN = data.get("token")
                custom_log("[AUTH] Bearer token didapat!")
                return True
        custom_log(f"[AUTH] Gagal. Status: {res.status_code}")
    except Exception as e:
        custom_log(f"[AUTH] Error: {e}")
    return False

def make_request(method, endpoint, json_payload=None):
    global CURRENT_TOKEN
    if not CURRENT_TOKEN and not authenticate():
        return None

    url = f"{BASE_URL}{endpoint}"
    try:
        if method.lower() == "get":
            res = requests.get(url, headers=get_headers(), timeout=15)
        else:
            res = requests.post(url, headers=get_headers(), json=json_payload, timeout=15)

        if res.status_code == 401:
            custom_log("[AUTH] Token expired, refresh...")
            if authenticate():
                if method.lower() == "get":
                    res = requests.get(url, headers=get_headers(), timeout=15)
                else:
                    res = requests.post(url, headers=get_headers(), json=json_payload, timeout=15)
            else:
                return None
        return res
    except Exception as e:
        custom_log(f"[REQ] Error {endpoint}: {e}")
        return None

# ═══════════ DATA FETCH ═══════════

def fetch_state():
    """Ambil farm + profile dari /user/bootstrap."""
    res = make_request("get", "/user/bootstrap")
    if res and res.status_code == 200:
        data = res.json()
        if data.get("ok"):
            profile = data.get("profile", {})
            farm = data.get("farm", {})
            return {
                "bootstrap": data,
                "username": profile.get("username", "Unknown"),
                "usdt": profile.get("usdt", 0),
                "coins": int(profile.get("coins", 0)),
                "level": profile.get("level", 1),
                "water": farm.get("water", 0),
                "waterMax": farm.get("waterMax", 10),
                "plots": farm.get("plots", []),
                "crops": farm.get("crops", []),
                "tasks": data.get("tasks", []),
            }
    return None

def print_header(s):
    display_banner()
    print("\033[1;36m" + "="*54 + "\033[0m")
    print(f" \033[1;33m👤 User       :\033[0m {s['username']} (Lv.{s['level']})")
    print(f" \033[1;32m💰 Saldo USDT :\033[0m {s['usdt']} USDT")
    print(f" \033[1;93m🪙 Coins      :\033[0m {s['coins']}")
    print(f" \033[1;34m💧 Air Kebun  :\033[0m {s['water']}/{s['waterMax']}")
    ready = sum(1 for p in s['plots'] if p.get('state') == 'ready')
    empty = sum(1 for p in s['plots'] if p.get('state') == 'empty')
    growing = sum(1 for p in s['plots'] if p.get('state') == 'growing')
    print(f" \033[1;35m🌾 Plot       :\033[0m ready={ready} | growing={growing} | empty={empty}")
    print("\033[1;36m" + "-"*54 + "\033[0m")
    print(" \033[1;93m📜 LIVE LOGS:\033[0m")
    print("\033[1;36m" + "-"*54 + "\033[0m")

# ═══════════ HELPERS ═══════════

def get_cheapest_crop(crops):
    unlocked = [c for c in crops if not c.get("locked", True)]
    if not unlocked:
        return 30, "wheat"
    cheapest = min(unlocked, key=lambda x: x.get("plantCost", 999999))
    return cheapest.get("plantCost", 30), cheapest.get("id", "wheat")

def get_best_affordable(crops, coins):
    """Crop terbaik yang bisa dibeli."""
    unlocked = [c for c in crops if not c.get("locked", True)]
    affordable = [c for c in unlocked if c.get("plantCost", 0) <= coins]
    if affordable:
        best = max(affordable, key=lambda x: x.get("payout", 0))
        return best.get("id", "wheat"), best.get("plantCost", 0)
    # Fallback: termurah
    if unlocked:
        cheapest = min(unlocked, key=lambda x: x.get("plantCost", 999999))
        return cheapest.get("id", "wheat"), cheapest.get("plantCost", 999999)
    return "wheat", 30

# ═══════════ ACTIONS ═══════════

def action_watch_ad_task(task_id, title, min_watch=8):
    """Nonton ad task, return: True / 'COOLDOWN' / False"""
    r = make_request("post", f"/ads/task/{task_id}/session", {"slotIndex": -1})
    if not r: return False
    if r.status_code == 409: return "COOLDOWN"
    if r.status_code != 200: return False

    d = r.json()
    if not d.get("ok"): return False

    sid = d.get("sessionId")
    mw = d.get("minWatchSec", min_watch)
    custom_log(f"[TASK ADS] Nonton [{title}] {mw}s...")
    time.sleep(mw + 2)

    payload = {
        "sessionId": sid,
        "slotIndex": d.get("slotIndex", 0),
        "provider": d.get("provider", "adsgram"),
        "clicked": True,
        "adsgramClicked": False
    }
    r2 = make_request("post", f"/ads/task/{task_id}/complete", payload)
    if r2 and r2.status_code == 200 and r2.json().get("ok"):
        custom_log(f"[TASK ADS] ✅ +reward dari [{title}]!")
        return True
    return False

def action_harvest(plot_idx):
    """Panen plot ready via ads session, return: True / 'COOLDOWN' / False"""
    r = make_request("post", "/ads/harvest/session", {"idx": plot_idx})
    if not r: return False
    if r.status_code == 409: return "COOLDOWN"
    if r.status_code != 200: return False

    d = r.json()
    if not d.get("ok"): return False

    sid = d.get("sessionId")
    mw = d.get("minWatchSec", 8)
    custom_log(f"[HARVEST] Nonton ad panen Plot [{plot_idx}] {mw}s...")
    time.sleep(mw + 2)

    payload = {"sessionId": sid, "provider": "adsgram", "clicked": True, "adsgramClicked": False}
    r2 = make_request("post", "/ads/harvest/complete", payload)
    if r2 and r2.status_code == 200 and r2.json().get("ok"):
        custom_log(f"[HARVEST] ✅ Panen Plot [{plot_idx}] sukses!")
        return True
    return False

def action_refill_water():
    """Refill air via ads, return: True / 'COOLDOWN' / False"""
    r = make_request("post", "/ads/farm/session", {"ref": "water"})
    if not r: return False
    if r.status_code == 409: return "COOLDOWN"
    if r.status_code != 200: return False

    d = r.json()
    if not d.get("ok"): return False

    sid = d.get("sessionId")
    mw = d.get("minWatchSec", 6)
    custom_log(f"[REFILL] Nonton ad refill air {mw}s...")
    time.sleep(mw + 2)

    payload = {"sessionId": sid, "ref": "water", "provider": "adsgram", "clicked": True, "adsgramClicked": False}
    r2 = make_request("post", "/ads/farm/complete", payload)
    if r2 and r2.status_code == 200 and r2.json().get("ok"):
        custom_log("[REFILL] ✅ Air diisi penuh!")
        return True
    return False

def action_plant(plot_idx, crop_id):
    r = make_request("post", "/farm/plant", {"idx": plot_idx, "crop": crop_id})
    if r and r.status_code == 200 and r.json().get("ok"):
        custom_log(f"[PLANT] ✅ {crop_id.upper()} di Plot [{plot_idx}]!")
        return True
    if r and r.status_code == 400:
        body = r.text.lower()
        if any(k in body for k in ["coin", "insufficient", "balance", "funds"]):
            custom_log(f"[PLANT] Coins tidak cukup")
            return "NO_COINS"
    return False

def action_water(plot_idx):
    r = make_request("post", "/farm/water", {"idx": plot_idx})
    if r and r.status_code == 200 and r.json().get("ok"):
        custom_log(f"[WATER] ✅ Siram Plot [{plot_idx}]!")
        return True
    return False

# ═══════════ SMART SCANNER ═══════════

def run_smart_scanner(s):
    """
    Priority:
    1. HARVEST plot ready (butuh ads, dapet coins)
    2. WATER tanaman growing yang belum disiram
    3. PLANT plot empty (kalau coins cukup)
    4. WATCH ADS buat kumpulin coins
    5. REFILL air kalau habis
    """
    plots = s["plots"]
    coins = s["coins"]
    water = s["water"]
    crops = s["crops"]
    tasks = s["tasks"]

    # ─── 1. HARVEST ready plots ───
    for p in plots:
        if p.get("state") == "ready":
            idx = p.get("idx")
            name = p.get("name", "crop")
            payout = p.get("payout", 0)
            custom_log(f"[HARVEST] Plot [{idx}] {name} ready (+{payout} coins)")
            res = action_harvest(idx)
            if res is True:
                return True
            elif res == "COOLDOWN":
                custom_log(f"[HARVEST {idx}] Cooldown, skip")
                time.sleep(1)
                continue

    # ─── 2. WATER growing yang belum disiram ───
    if water > 0:
        for p in plots:
            if p.get("state") in ["growing", "ready"] and not p.get("watered", False):
                idx = p.get("idx")
                if action_water(idx):
                    return True

    # ─── 3. PLANT empty plots (kalau coins cukup) ───
    empty_plots = [p for p in plots if p.get("state") == "empty" and not p.get("locked", False)]
    cheapest_cost, cheapest_id = get_cheapest_crop(crops)

    if empty_plots and coins >= cheapest_cost:
        crop_id, cost = get_best_affordable(crops, coins)
        idx = empty_plots[0].get("idx")
        custom_log(f"[PLANT] Coba tanam {crop_id.upper()} (cost={cost}) di Plot [{idx}]")
        res = action_plant(idx, crop_id)
        if res is True:
            return True
        elif res == "NO_COINS":
            custom_log(f"[PLANT] Beralih ke ads...")
            # lanjut ke ads

    # ─── 4. WATCH ADS (buat farming coins) ───
    # Urut task by reward desc
    ad_tasks = [t for t in tasks if t.get("type") == "ad" and t.get("state") == "open"]
    ad_tasks.sort(key=lambda x: x.get("reward", 0), reverse=True)

    for t in ad_tasks:
        tid = t.get("id")
        title = t.get("title", "Ad")
        target = t.get("target", 10)
        progress = t.get("progress", 0)
        if progress >= target:
            continue
        res = action_watch_ad_task(tid, title)
        if res is True:
            return True
        elif res == "COOLDOWN":
            custom_log(f"[{title}] Cooldown, task lain...")
            time.sleep(1)
            continue

    # ─── 5. REFILL air ───
    if water == 0:
        custom_log("[INFO] Air habis, refill...")
        res = action_refill_water()
        if res is True:
            return True

    return False

# ═══════════ MAIN LOOP ═══════════

def run_bot():
    global BASE_URL, FARM_FP, DEVICE_ID, INIT_DATA
    BASE_URL = CONFIG.get("base_url", "https://farm-buddies-api.nhathaybip2000.workers.dev/api")
    FARM_FP = CONFIG.get("fingerprint", "")
    DEVICE_ID = CONFIG.get("device_id", "")
    INIT_DATA = CONFIG.get("init_data", "")

    if not authenticate():
        custom_log("Auth awal gagal!")
        time.sleep(3)
        return

    s = fetch_state()
    if s:
        print_header(s)

    custom_log("Bot Farm Buddies v4 jalan...")

    idle_count = 0
    while True:
        try:
            s = fetch_state()
            if not s:
                custom_log("[WARN] Gagal sync, retry 10s...")
                time.sleep(10)
                continue

            print_header(s)

            acted = run_smart_scanner(s)

            if acted:
                idle_count = 0
                time.sleep(2)
            else:
                idle_count += 1
                if idle_count >= 3:
                    custom_log("[IDLE] Semua cooldown. Tidur 5 menit...")
                    time.sleep(300)
                    idle_count = 0
                else:
                    custom_log(f"[IDLE] Gak ada aksi, tunggu 20s ({idle_count}/3)")
                    time.sleep(20)

        except KeyboardInterrupt:
            custom_log("Bot dimatiin manual.")
            break
        except Exception as e:
            custom_log(f"[ERR] Loop: {e}")
            time.sleep(30)

# ═══════════ MENU ═══════════

def main():
    while True:
        display_banner()
        print("Sebelum menjalankan scriptnya mari kita berdoa kepada TUHAN YANG MAHA ESA")
        print("#SAVEPALESTINE\n")
        print("1. Mainkan wak")
        print("2. Isi init_data")
        print("3. Hapus Data")
        print("0. Pulang wak Turu\n")

        pilih = input("Pilih menu: ").strip()

        if pilih == "1":
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, "r") as f:
                    global CONFIG
                    CONFIG = json.load(f)
                run_bot()
            else:
                print("\n\033[1;31mData belum diisi! Pilih menu 2 dulu.\033[0m")
                time.sleep(2)
        elif pilih == "2":
            isi_data()
        elif pilih == "3":
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
                print("\n\033[1;32m✅ config.json dihapus!\033[0m")
            else:
                print("\n\033[1;33m⚠️ Tidak ada config.json.\033[0m")
            time.sleep(2)
        elif pilih == "0":
            print("\n\033[1;36mSelamat istirahat wak!\033[0m\n")
            sys.exit(0)
        else:
            print("\n\033[1;31mPilihan tidak valid!\033[0m")
            time.sleep(1)

if __name__ == "__main__":
    main()

# created by AHD1905 — fixed by Kyriel
