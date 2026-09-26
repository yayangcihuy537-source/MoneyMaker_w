#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║         🌾 C R Y P T O C R O P S   A U T O M A T I O N 🌾        ║
║   🔥 SOUU ENGINE • NO FAUCET MODE (FARM ONLY)                  ║
╚═══════════════════════════════════════════════════════════════════╝

Fitur:
  - Auto plant, harvest, mission, harvest pass, fulfill orders
  - Faucet mode DIHAPUS (turnstile skip)
  - UI: SOUU ENGINE (box banner, ANSI 256, spinner, log buffer)
"""

import os
import re
import sys
import time
import uuid
import json
import random
import signal
import requests
from datetime import datetime


# ═══════════════════════════════════════════════════════════════════════════
#  KONFIG
# ═══════════════════════════════════════════════════════════════════════════
BASE_URL   = "https://cryptocrops.net"
CONFIG_FILE = "cryptocrops_config.json"

PRIORITY_SEEDS = ("lettuce", "carrot", "radish", "wheat", "green-peas", "strawberry")

SEED_NAMES_ID = {
    "wheat":      "gandum",
    "lettuce":    "selada",
    "radish":     "lobak",
    "carrot":     "wortel",
    "green-peas": "kacang polong",
    "green_peas": "kacang polong",
    "strawberry": "stroberi",
    "tomato":     "tomat",
    "corn":       "jagung",
    "potato":     "kentang",
}

UA = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/153.0.0.0 Mobile Safari/537.36"


# ═══════════════════════════════════════════════════════════════════════════
#  ANSI 256 HELPERS
# ═══════════════════════════════════════════════════════════════════════════
RESET = "\033[0m"

def fg(c):    return f"\033[38;5;{c}m"
def bold(s):  return f"\033[1m{s}\033[22m"
def dim(s):   return f"\033[2m{s}\033[22m"

def gradient(text, start=51, end=196):
    n = len(text)
    if n <= 1:
        return fg(start) + text + RESET
    out = ""
    for i, ch in enumerate(text):
        t = i / (n - 1)
        c = int(round(start + (end - start) * t))
        out += fg(c) + ch
    return out + RESET

def tag_color(tag):
    m = {
        "AUTH":    fg(46)  + bold("AUTH"),
        "STATUS":  fg(51)  + bold("STATUS"),
        "CAPTCHA": fg(213) + bold("CAPTCHA"),
        "CLAIM":   fg(226) + bold("CLAIM"),
        "FARM":    fg(81)  + bold("FARM"),
        "PLANT":   fg(46)  + bold("PLANT"),
        "HARVEST": fg(226) + bold("HARVEST"),
        "MISSION": fg(135) + bold("MISSION"),
        "PASS":    fg(141) + bold("PASS"),
        "ORDER":   fg(208) + bold("ORDER"),
        "WAIT":    fg(208) + bold("WAIT"),
        "BLOCK":   fg(196) + bold("BLOCK"),
        "SYSTEM":  fg(135) + bold("SYSTEM"),
        "ERROR":   fg(196) + bold("ERROR"),
        "INIT":    fg(213) + bold("INIT"),
        "SOLVER":  fg(141) + bold("SOLVER"),
        "COIN":    fg(226) + bold("COIN"),
        "DEBUG":   fg(250) + bold("DEBUG"),
    }
    return m.get(tag.strip(), fg(250) + bold(tag))

def tag_icon(tag):
    m = {
        "AUTH":    "●", "STATUS":  "●", "CAPTCHA": "◉", "CLAIM":   "✔",
        "FARM":    "⚙", "PLANT":   "🌱", "HARVEST": "🌾", "MISSION": "🎯",
        "PASS":    "🎟", "ORDER":   "🚚", "WAIT":    "◷", "BLOCK":   "✖",
        "SYSTEM":  "⚙", "ERROR":   "✖", "INIT":    "⚡", "SOLVER":  "🧩",
        "COIN":    "🪙", "DEBUG":   "·",
    }
    return m.get(tag.strip(), "•")

def ansi_len(s):
    return len(re.sub(r'\033\[[0-9;]*m', '', s))

def ansi_pad(s, length):
    pad = length - ansi_len(s)
    return s + (" " * pad if pad > 0 else "")

def human_pause(min_ms=400, max_ms=1200):
    time.sleep(random.randint(min_ms, max_ms) / 1000.0)


def safe_int(v, default=0):
    if v is None:
        return default
    try:
        return int(v)
    except (ValueError, TypeError):
        try:
            return int(float(v))
        except (ValueError, TypeError):
            return default


# ═══════════════════════════════════════════════════════════════════════════
#  GLOBAL STATE
# ═══════════════════════════════════════════════════════════════════════════
STATS = {
    "plants":    0, "harvests":  0,
    "missions":  0, "pass":      0, "orders":    0,
    "start":     time.time(), "log": [],
}
ACC = {
    "name":    "?", "level":   0, "coins":   0,
    "points":  0,   "status":  "idle",
}
G = {"STOP": False}


def add_log(tag, msg):
    STATS["log"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "tag":  tag,
        "msg":  str(msg),
    })
    if len(STATS["log"]) > 6:
        STATS["log"].pop(0)


def seed_id(name):
    if not name:
        return "?"
    key = str(name).lower().strip()
    return SEED_NAMES_ID.get(key, name)


# ═══════════════════════════════════════════════════════════════════════════
#  BOX / BANNER
# ═══════════════════════════════════════════════════════════════════════════
def box_line(content):
    return fg(51) + "║  " + RESET + ansi_pad(content, 60) + fg(51) + "║" + RESET + "\n"

def box_divider():
    return fg(51) + "╠══════════════════════════════════════════════════════════════╣" + RESET + "\n"


def banner(status_text="RUNNING", extra_info=None):
    s = STATS
    a = ACC
    rt = int(time.time() - s["start"])
    rts = f"{rt//3600:02d}:{(rt%3600)//60:02d}:{rt%60:02d}"

    buf = ""
    buf += fg(51) + "╔══════════════════════════════════════════════════════════════╗" + RESET + "\n"
    buf += box_line(gradient("CRYPTOCROPS AUTO FARM", 51, 213))
    buf += box_line(dim("─────── SOUU ENGINE ───────"))
    buf += box_divider()

    buf += box_line(fg(213) + bold("AKUN") + RESET)
    buf += box_line(fg(51) + "├─ Nama       : " + RESET + fg(226) + str(a["name"])[:30] + RESET)
    buf += box_line(fg(51) + "├─ Level      : " + RESET + fg(226) + str(a["level"]) + RESET)
    buf += box_line(fg(51) + "├─ Koin       : " + RESET + fg(46) + str(a["coins"]) + RESET)
    buf += box_line(fg(51) + "└─ Status     : " + RESET + fg(226) + str(a["status"]) + RESET)
    buf += box_divider()

    if extra_info:
        buf += box_line(fg(213) + bold("INFO") + RESET)
        for line in extra_info:
            buf += box_line(fg(51) + "• " + RESET + fg(250) + str(line)[:55] + RESET)
        buf += box_divider()

    buf += box_line(fg(213) + bold("SISTEM") + RESET)
    buf += box_line(fg(51) + "├─ Tanam     : " + RESET + fg(46) + str(s["plants"]) + RESET)
    buf += box_line(fg(51) + "├─ Panen     : " + RESET + fg(46) + str(s["harvests"]) + RESET)
    buf += box_line(fg(51) + "├─ Misi      : " + RESET + fg(226) + str(s["missions"]) + RESET)
    buf += box_line(fg(51) + "├─ Pass      : " + RESET + fg(226) + str(s["pass"]) + RESET)
    buf += box_line(fg(51) + "└─ Runtime   : " + RESET + fg(208) + rts + RESET)
    buf += box_divider()

    for i in range(6):
        if i < len(s["log"]):
            l    = s["log"][i]
            icon = tag_icon(l["tag"])
            tag  = tag_color(l["tag"])
            line = dim(f"[{l['time']}]") + " " + fg(250) + icon + RESET + " " + tag + " " + fg(252) + l["msg"][:45] + RESET
            buf += box_line(line)
        else:
            buf += fg(51) + "║" + (" " * 62) + "║" + RESET + "\n"

    buf += fg(51) + "╚══════════════════════════════════════════════════════════════╝" + RESET + "\n"
    buf += "\n   " + gradient(f"BOT {status_text}", 46, 226) + " " + fg(250) + "• " + datetime.now().strftime("%H:%M:%S") + RESET + "\n"
    buf += "   " + dim("By Power ") + fg(213) + "@SouuXso" + RESET + dim(" • ") + fg(46) + "CryptoCrops Edition" + RESET + "\n\n"

    sys.stdout.write(buf)
    sys.stdout.flush()


def timer(seconds, prefix="  tunggu.."):
    wait_time = int(seconds)
    if wait_time <= 0:
        wait_time = 1
    frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    fc = len(frames)
    cf = 0
    while wait_time > 0 and not G["STOP"]:
        start = time.time()
        while (time.time() - start) < 1:
            h = wait_time // 3600
            m = (wait_time % 3600) // 60
            s = wait_time % 60
            tf = f"{h:02d}:{m:02d}:{s:02d}"
            sp = frames[cf]
            sys.stdout.write(fg(250) + prefix + fg(46) + f" {tf} " + fg(226) + sp + "\r")
            sys.stdout.flush()
            time.sleep(0.1)
            cf = (cf + 1) % fc
            if (time.time() - start) >= 1:
                break
        wait_time -= 1
    sys.stdout.write("\r" + (" " * 60) + "\r")
    sys.stdout.flush()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


# ═══════════════════════════════════════════════════════════════════════════
#  CONFIG IO
# ═══════════════════════════════════════════════════════════════════════════
def get_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ═══════════════════════════════════════════════════════════════════════════
#  API CLIENT (NO TURNSTILE)
# ═══════════════════════════════════════════════════════════════════════════
class CryptoCrops:
    def __init__(self, cookie):
        self.cookie = cookie
        self.headers = {
            "Host": "cryptocrops.net",
            "User-Agent": UA,
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/farm/",
            "Accept-Language": "id,en-US;q=0.9,en;q=0.8",
            "Cookie": cookie,
        }

    def _api(self, method, endpoint, payload=None):
        url = BASE_URL + endpoint
        try:
            if method == "POST":
                body = dict(payload) if payload else {}
                if "idempotency_key" not in body:
                    body["idempotency_key"] = str(uuid.uuid4())
                r = requests.post(url, headers=self.headers, json=body, timeout=45)
            else:
                r = requests.get(url, headers=self.headers, timeout=45)
            return r
        except Exception as e:
            add_log("ERROR", f"api: {str(e)[:40]}")
            return None

    def bootstrap(self):
        return self._api("GET", "/api/bootstrap")

    def plant(self, seed, plot_idx):
        r = self._api("POST", "/api/farm/plant", {"seed_id": seed, "plot_index": plot_idx})
        if r and r.status_code in (200, 201):
            return True
        body = (r.text or "").lower() if r else ""
        if "no_available_seed" in body or "already planted" in body:
            return "no_seed"
        if "invalid_plot" in body or "not available" in body:
            return "invalid_plot"
        return False

    def harvest(self, crop_id, plot_idx):
        if not crop_id:
            return False
        r = self._api("POST", "/api/farm/harvest", {"crop_id": crop_id})
        if r and r.status_code in (200, 201):
            return True
        body = (r.text or "").lower() if r else ""
        if "crop_not_ready" in body or "still growing" in body:
            return "not_ready"
        return False

    def claim_mission(self, mission_id, title):
        r = self._api("POST", "/api/missions/claim", {"mission_id": mission_id})
        if r and r.status_code in (200, 201):
            try:
                d = r.json()
                xp = d.get("pass_xp_earned", 0)
                add_log("MISSION", f"'{str(title)[:20]}' +{xp} XP")
            except Exception:
                add_log("MISSION", f"'{str(title)[:20]}' ok")
            STATS["missions"] += 1
            return True
        return False

    def claim_pass(self, tier, track):
        r = self._api("POST", "/api/pass/claim", {"tier": tier, "track": track})
        if r and r.status_code in (200, 201):
            try:
                d = r.json()
                label = d.get("reward_label") or d.get("reward") or "reward"
            except Exception:
                label = "reward"
            add_log("PASS", f"tier {tier} ({track}) → {str(label)[:20]}")
            STATS["pass"] += 1
            return True
        return False

    def fulfill_order(self, order_id):
        r = self._api("POST", "/api/orders/fulfill", {"order_id": order_id})
        if r and r.status_code in (200, 201):
            add_log("ORDER", f"order {order_id} ok")
            STATS["orders"] += 1
            return True
        return False


# ═══════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def find_val(sources, *keys, default=0):
    for src in sources:
        if not isinstance(src, dict):
            continue
        for k in keys:
            if k in src and src[k] is not None:
                return src[k]
        lower_map = {str(kk).lower(): vv for kk, vv in src.items()}
        for k in keys:
            if k.lower() in lower_map and lower_map[k.lower()] is not None:
                return lower_map[k.lower()]
    return default


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════════════════════
def run_bot():
    cfg = get_config() or {}
    cookie = cfg.get("cookie", "")

    if not cookie:
        clear()
        sys.stdout.write(fg(196) + "\n  ✖ Cookie belum diset. Isi menu [2].\n" + RESET)
        sys.stdout.write(fg(250) + "  Tekan Enter..." + RESET)
        sys.stdout.flush()
        input()
        return

    STATS["plants"]   = 0
    STATS["harvests"] = 0
    STATS["missions"] = 0
    STATS["pass"]     = 0
    STATS["orders"]   = 0
    STATS["start"]    = time.time()
    STATS["log"]      = []
    ACC["status"]     = "running"

    bot = CryptoCrops(cookie)

    add_log("INIT", "CryptoCrops engine boot (farm only)")
    clear()
    banner("INIT")

    add_log("AUTH", "testing cookie...")
    clear()
    banner("INIT")
    resp = bot.bootstrap()
    if resp is None:
        add_log("ERROR", "tidak bisa connect")
        clear()
        banner("ERROR")
        sys.stdout.write(fg(196) + "\n  ✖ Gagal connect. Cek cookie & koneksi. Enter...\n" + RESET)
        sys.stdout.flush()
        input()
        return
    if resp.status_code == 401:
        add_log("ERROR", "cookie expired/invalid")
        clear()
        banner("ERROR")
        sys.stdout.write(fg(196) + "\n  ✖ Cookie invalid. Ambil ulang dari browser. Enter...\n" + RESET)
        sys.stdout.flush()
        input()
        return
    if resp.status_code not in (200, 201):
        add_log("ERROR", f"bootstrap HTTP {resp.status_code}")
        clear()
        banner("ERROR")
        sys.stdout.write(fg(196) + f"\n  ✖ HTTP {resp.status_code}. Enter...\n" + RESET)
        sys.stdout.flush()
        input()
        return

    add_log("AUTH", "cookie OK")
    clear()
    banner("RUNNING")

    failed_seeds = set()

    while not G["STOP"]:
        try:
            resp = bot.bootstrap()
            if resp is None or resp.status_code not in (200, 201):
                add_log("ERROR", "bootstrap failed, retry 15s")
                clear()
                banner("WAITING")
                timer(15, "  retry..")
                continue

            data = resp.json()
            auth_info    = data.get("auth") or {}
            farm_data    = data.get("farm") or {}
            profile      = data.get("profile") or farm_data.get("profile") or {}
            pool_info    = data.get("pool") or {}
            orders       = data.get("orders") or farm_data.get("orders") or []
            missions     = data.get("missions") or farm_data.get("missions") or []
            harvest_pass = data.get("harvest_pass") or farm_data.get("harvest_pass") or {}

            server_now = safe_int(
                farm_data.get("server_now") or int(time.time() * 1000),
                default=int(time.time() * 1000),
            )

            sources = [profile, auth_info, farm_data, pool_info]
            if isinstance(auth_info.get("user"), dict):
                sources.append(auth_info["user"])

            ACC["name"]   = find_val(sources, "display_name", "name", default="Unknown")
            ACC["level"]  = find_val(sources, "farm_level", "level", "farmLevel", default=0)
            ACC["coins"]  = find_val(sources, "farm_coins", "coins", "farmCoins", default=0)
            ACC["points"] = find_val(sources, "total_points", "points", default=0)

            crops          = farm_data.get("crops") or []
            seeds_list     = farm_data.get("seeds") or []
            inventory      = farm_data.get("inventory") or {}
            total_capacity = farm_data.get("total_capacity") or farm_data.get("capacity") or 8

            # ===== MISSION =====
            for mission in (missions or []):
                if not isinstance(mission, dict):
                    continue
                if mission.get("complete") and not mission.get("claimed"):
                    m_id = mission.get("mission_id") or mission.get("id")
                    m_title = mission.get("title", "")
                    if m_id:
                        add_log("MISSION", f"claim '{str(m_title)[:20]}'")
                        clear()
                        banner("RUNNING")
                        bot.claim_mission(m_id, m_title)

            # ===== PASS =====
            if isinstance(harvest_pass, dict):
                tiers      = harvest_pass.get("tiers") or []
                is_premium = bool(harvest_pass.get("premium_track_active"))
            else:
                tiers      = harvest_pass if isinstance(harvest_pass, list) else []
                is_premium = False

            free_to_claim    = []
            premium_to_claim = []
            for t in tiers:
                if not isinstance(t, dict):
                    continue
                if not t.get("unlocked"):
                    continue
                if not t.get("free_claimed"):
                    free_to_claim.append(t)
                if is_premium and not t.get("premium_claimed"):
                    premium_to_claim.append(t)

            for t in free_to_claim:
                tier = t.get("tier")
                add_log("PASS", f"free tier {tier}")
                clear()
                banner("RUNNING")
                bot.claim_pass(tier, "free")

            for t in premium_to_claim:
                tier = t.get("tier")
                add_log("PASS", f"premium tier {tier}")
                clear()
                banner("RUNNING")
                bot.claim_pass(tier, "premium")

            # ===== HARVEST =====
            active_plots    = {}
            planted_count   = {}
            harvested_any   = False
            next_harvest_at = None

            for crop in (crops or []):
                if not isinstance(crop, dict):
                    continue
                plot_idx = crop.get("plot_index", crop.get("plotIndex"))
                ready_at = crop.get("ready_at") or crop.get("readyAt")
                crop_id  = crop.get("crop_id") or crop.get("cropId") or crop.get("id")
                seed_name = str(crop.get("seed_name") or crop.get("seedName") or "?").lower()

                active_plots[plot_idx] = crop
                planted_count[seed_name] = planted_count.get(seed_name, 0) + 1

                ready_at_int = safe_int(ready_at, default=None) if ready_at is not None else None
                is_ready = False

                if ready_at_int is not None:
                    diff_ms = server_now - ready_at_int
                    is_ready = diff_ms >= 2000

                if is_ready:
                    add_log("HARVEST", f"plot {plot_idx} ({seed_id(seed_name)})")
                    clear()
                    banner("RUNNING")
                    res = bot.harvest(crop_id, plot_idx)
                    if res is True:
                        STATS["harvests"] += 1
                        harvested_any = True
                    elif res == "not_ready":
                        retry_at = server_now + 15000
                        if next_harvest_at is None or retry_at < next_harvest_at:
                            next_harvest_at = retry_at
                else:
                    if ready_at_int is not None:
                        if next_harvest_at is None or ready_at_int < next_harvest_at:
                            next_harvest_at = ready_at_int

            if harvested_any:
                clear()
                banner("RUNNING")
                continue

            # ===== PLANT =====
            used_plots = set()
            for p in active_plots.keys():
                if p is not None:
                    pi = safe_int(p, default=None)
                    if pi is not None:
                        used_plots.add(pi)

            api_cap = safe_int(total_capacity, default=0)
            capacity = max(api_cap, max(used_plots) if used_plots else 0, 8)

            available_seeds = []
            for s in (seeds_list or []):
                if not isinstance(s, dict):
                    continue
                sid = s.get("seed_id") or s.get("id") or s.get("seedId")
                if sid:
                    sid = str(sid).lower()
                qty = safe_int(s.get("quantity") or s.get("qty") or s.get("available"), default=0)
                already = planted_count.get(sid, 0)
                free_qty = max(0, qty - already)
                if sid and free_qty > 0 and sid not in failed_seeds:
                    available_seeds.append((sid, free_qty))

            if not available_seeds and isinstance(inventory, dict):
                for sid, val in inventory.items():
                    sid = str(sid).lower()
                    qty = 0
                    if isinstance(val, (int, float)):
                        qty = int(val)
                    elif isinstance(val, list):
                        for item in val:
                            if isinstance(item, dict):
                                qty += safe_int(item.get("quantity") or item.get("qty"), default=0)
                    already = planted_count.get(sid, 0)
                    free_qty = max(0, qty - already)
                    if free_qty > 0 and sid not in failed_seeds:
                        available_seeds.append((sid, free_qty))

            seeds_to_try = []
            for p_seed in PRIORITY_SEEDS:
                for sid, qty in available_seeds:
                    if sid == p_seed and sid not in seeds_to_try:
                        seeds_to_try.append(sid)
            for sid, qty in available_seeds:
                if sid not in seeds_to_try:
                    seeds_to_try.append(sid)

            free_plots = [i for i in range(1, capacity + 1) if i not in used_plots]

            if seeds_to_try and free_plots:
                seed_idx = 0
                just_planted = 0

                for plot_idx in free_plots:
                    if G["STOP"]:
                        break
                    while seed_idx < len(seeds_to_try):
                        seed_to_plant = seeds_to_try[seed_idx]
                        remaining = 0
                        for sid, qty in available_seeds:
                            if sid == seed_to_plant:
                                remaining = qty - just_planted
                                break
                        if remaining > 0:
                            break
                        seed_idx += 1
                        just_planted = 0
                    else:
                        break

                    add_log("PLANT", f"plot {plot_idx} → {seed_id(seed_to_plant)[:15]}")
                    clear()
                    banner("RUNNING")

                    result = bot.plant(seed_to_plant, plot_idx)
                    if result is True:
                        used_plots.add(plot_idx)
                        just_planted += 1
                        STATS["plants"] += 1
                        time.sleep(0.5)
                    elif result == "no_seed":
                        failed_seeds.add(seed_to_plant)
                        seed_idx += 1
                        just_planted = 0
                        if seed_idx >= len(seeds_to_try):
                            break
                    elif result == "invalid_plot":
                        break
                    else:
                        seed_idx += 1
                        just_planted = 0
                        if seed_idx >= len(seeds_to_try):
                            break

            # ===== ORDER =====
            for order in (orders or []):
                if not isinstance(order, dict):
                    continue
                if order.get("status") != "active":
                    continue
                order_id = order.get("order_id") or order.get("id")
                if not order_id:
                    continue
                add_log("ORDER", f"try order {order_id}")
                clear()
                banner("RUNNING")
                bot.fulfill_order(order_id)

            # ===== WAIT =====
            candidates = []
            try:
                now_local = int(time.time() * 1000)
                if next_harvest_at:
                    nha = safe_int(next_harvest_at, default=None)
                    if nha:
                        diff = (nha - now_local) // 1000
                        if diff > 0:
                            candidates.append(max(5, diff))
            except Exception:
                pass
            sleep_time = min(min(candidates) if candidates else 60, 300)

            add_log("WAIT", f"next cycle {sleep_time}s")
            clear()
            banner("WAITING")
            timer(sleep_time, "  cycle..")

        except KeyboardInterrupt:
            break
        except Exception as e:
            add_log("ERROR", f"loop exc: {str(e)[:50]}")
            clear()
            banner("ERROR")
            timer(30, "  retry..")

    ACC["status"] = "done"
    add_log("SYSTEM", "dihentikan")
    clear()
    banner("DONE")
    sys.stdout.write(fg(226) + "\n  ⏱  Bot stopped. Enter balik menu...\n" + RESET)
    sys.stdout.flush()
    input()
    ACC["status"] = "idle"


# ═══════════════════════════════════════════════════════════════════════════
#  SIGNAL
# ═══════════════════════════════════════════════════════════════════════════
def signal_handler(sig, frame):
    sys.stdout.write("\n" + fg(208) + "  ⚠ Ctrl+C — stopping...\n" + RESET)
    sys.stdout.flush()
    G["STOP"] = True


# ═══════════════════════════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════════════════════════
def menu():
    cfg = get_config() or {}
    cookie = cfg.get("cookie", "")

    cookie_disp = cookie[:20] + "..." if len(cookie) > 20 else (cookie or "belum diset")

    buf = ""
    buf += fg(51) + "╔══════════════════════════════════════════════════════════════╗" + RESET + "\n"
    buf += box_line(gradient("CRYPTOCROPS — SOUU ENGINE", 51, 213))
    buf += box_line(dim("─────── AUTO FARM (NO FAUCET) ───────"))
    buf += box_divider()
    buf += box_line(fg(51) + "  Cookie  : " + RESET + fg(226) + cookie_disp + RESET)
    buf += box_line(fg(51) + "  Mode    : " + RESET + fg(226) + "Farm only (plant/harvest/mission/pass/order)" + RESET)
    buf += box_divider()
    buf += box_line(fg(46)  + "  [1] " + RESET + fg(252) + "Mulai Bot" + RESET)
    buf += box_line(fg(213) + "  [2] " + RESET + fg(252) + "Config Cookie (cc_session_v1)" + RESET)
    buf += box_line(fg(196) + "  [0] " + RESET + fg(252) + "Exit" + RESET)
    buf += fg(51) + "╚══════════════════════════════════════════════════════════════╝" + RESET + "\n\n"
    buf += fg(51) + "  Pilih >> " + RESET

    sys.stdout.write(buf)
    sys.stdout.flush()


def action_config_cookie():
    cfg = get_config()
    sys.stdout.write("\n" + fg(213) + "  Paste cookie (cc_session_v1=xxx) :\n" + fg(51) + "  > " + RESET)
    sys.stdout.flush()
    try:
        raw = sys.stdin.readline().strip()
    except (EOFError, KeyboardInterrupt):
        return

    if not raw:
        sys.stdout.write(fg(196) + "  ✖ kosong, skip\n" + RESET)
        sys.stdout.flush()
        human_pause(500, 900)
        return

    if "cc_session_v1=" in raw:
        for part in raw.split(";"):
            part = part.strip()
            if part.startswith("cc_session_v1="):
                cookie_value = part
                break
        else:
            cookie_value = "cc_session_v1=" + raw.split("cc_session_v1=")[-1].split(";")[0].strip()
    else:
        cookie_value = "cc_session_v1=" + raw.replace('"', '').replace("'", "")

    cfg["cookie"] = cookie_value
    save_config(cfg)
    sys.stdout.write(fg(46) + f"  ✓ cookie disimpan ({len(cookie_value)} char)\n" + RESET)
    sys.stdout.flush()
    human_pause(500, 900)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    signal.signal(signal.SIGINT, signal_handler)

    first = True
    while True:
        clear()
        if first:
            sys.stdout.write("\n")
            first = False
        menu()

        try:
            opt = sys.stdin.readline().strip()
        except (EOFError, KeyboardInterrupt):
            opt = "0"

        if opt == "1":
            run_bot()

        elif opt == "2":
            action_config_cookie()

        elif opt == "0":
            clear()
            sys.stdout.write(fg(213) + "\n  bye boss 👋\n\n" + RESET)
            sys.stdout.flush()
            sys.exit(0)

        else:
            sys.stdout.write(fg(196) + "\n  ✖ Pilihan gak valid.\n" + RESET)
            sys.stdout.flush()
            human_pause(600, 1000)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write(fg(196) + "\n\n  ✖ Dihentikan\n" + RESET)
        sys.exit(0)
    except Exception as e:
        sys.stdout.write(fg(196) + f"\n  ✖ Fatal: {e}\n" + RESET)
        import traceback
        traceback.print_exc()
        sys.exit(1)
