#!/usr/bin/env python3
"""
PrizeDrop Auto Bot — SOUU ENGINE EDITION
- Manual InitData via menu config
- Lucky Spin → Task → Ad watch
- Visual: ANSI 256 gradient, box banner, spinner timer, log buffer 6-line
"""
import os
import sys
import re
import json
import time
import uuid
import random
import signal
from datetime import datetime
from urllib.parse import parse_qsl, unquote

import requests


# ============================================================
#   KONFIG
# ============================================================
BASE_URL = "https://pricedropes.lovable.app/api/public"
APP_URL  = "https://pricedropes.lovable.app/"
CONFIG_FILE = "pricedropes_config.json"

MAX_CONSECUTIVE_FAIL = 3
SPIN_DELAY = 2.5
TASK_DELAY = 2
AD_DELAY = (16.0, 19.0)


# ============================================================
#   ANSI 256 HELPERS
# ============================================================
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
        "AUTH":     fg(46)  + bold("AUTH"),
        "STATUS":   fg(51)  + bold("STATUS"),
        "SPIN":     fg(213) + bold("SPIN"),
        "TASK":     fg(81)  + bold("TASK"),
        "AD":       fg(226) + bold("AD"),
        "CLAIM":    fg(46)  + bold("CLAIM"),
        "WAIT":     fg(208) + bold("WAIT"),
        "BLOCK":    fg(196) + bold("BLOCK"),
        "SYSTEM":   fg(135) + bold("SYSTEM"),
        "ERROR":    fg(196) + bold("ERROR"),
        "INIT":     fg(213) + bold("INIT"),
    }
    return m.get(tag.strip(), fg(250) + bold(tag))

def tag_icon(tag):
    m = {
        "AUTH":     "●",
        "STATUS":   "●",
        "SPIN":     "◉",
        "TASK":     "◈",
        "AD":       "▶",
        "CLAIM":    "✔",
        "WAIT":     "◷",
        "BLOCK":    "✖",
        "SYSTEM":   "⚙",
        "ERROR":    "✖",
        "INIT":     "⚡",
    }
    return m.get(tag.strip(), "•")

def ansi_len(s):
    return len(re.sub(r'\033\[[0-9;]*m', '', s))

def ansi_pad(s, length):
    pad = length - ansi_len(s)
    return s + (" " * pad if pad > 0 else "")

def human_delay(min_ms=150, max_ms=700):
    time.sleep(random.randint(min_ms, max_ms) / 1000.0)

def human_pause(min_ms=400, max_ms=1200):
    time.sleep(random.randint(min_ms, max_ms) / 1000.0)


# ============================================================
#   GLOBAL STATE
# ============================================================
STATS = {
    "ads":       0,
    "spins":     0,
    "tasks":     0,
    "rewards":   0.0,
    "start":     time.time(),
    "log":       [],
}
ACC = {
    "user":    "?",
    "ticket":  "0",
    "cash":    "0.00",
    "status":  "idle",
}
G = {"STOP": False}


def add_log(tag, msg):
    STATS["log"].append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "tag":  tag,
        "msg":  msg,
    })
    if len(STATS["log"]) > 6:
        STATS["log"].pop(0)


# ============================================================
#   BOX / BANNER
# ============================================================
def box_line(content):
    return fg(51) + "║  " + RESET + ansi_pad(content, 60) + fg(51) + "║" + RESET + "\n"

def box_divider():
    return fg(51) + "╠══════════════════════════════════════════════════════════════╣" + RESET + "\n"


def banner(status_text="RUNNING"):
    s = STATS
    a = ACC
    rt = int(time.time() - s["start"])
    rts = f"{rt//3600:02d}:{(rt%3600)//60:02d}:{rt%60:02d}"

    buf = ""
    buf += fg(51) + "╔══════════════════════════════════════════════════════════════╗" + RESET + "\n"
    buf += box_line(gradient("PRICEDROPES AUTO CLAIM", 51, 213))
    buf += box_line(dim("─────── SOUU ENGINE ───────"))
    buf += box_divider()

    # TASK LIST
    buf += box_line(fg(213) + bold("TASK LIST") + RESET)
    buf += box_line(fg(51) + "├─ Type     : " + RESET + fg(226) + "Lucky Spin + Tasks" + RESET)
    buf += box_line(fg(51) + "└─ Ads      : " + RESET + fg(226) + "Multi-Network" + RESET)
    buf += box_divider()

    # ACCOUNT
    buf += box_line(fg(213) + bold("ACCOUNT") + RESET)
    buf += box_line(fg(51) + "├─ User       : " + RESET + fg(226) + str(a["user"]) + RESET)
    buf += box_line(fg(51) + "├─ Tickets    : " + RESET + fg(226) + str(a["ticket"]) + RESET)
    buf += box_line(fg(51) + "├─ Cash       : " + RESET + fg(46) + "$" + str(a["cash"]) + RESET)
    buf += box_line(fg(51) + "└─ Status     : " + RESET + fg(226) + str(a["status"]) + RESET)
    buf += box_divider()

    # SYSTEM
    buf += box_line(fg(213) + bold("SYSTEM") + RESET)
    buf += box_line(fg(51) + "├─ Spins        : " + RESET + fg(226) + str(s["spins"]) + RESET)
    buf += box_line(fg(51) + "├─ Tasks        : " + RESET + fg(226) + str(s["tasks"]) + RESET)
    buf += box_line(fg(51) + "├─ Ads Done     : " + RESET + fg(226) + str(s["ads"]) + RESET)
    buf += box_line(fg(51) + "├─ Rewards      : " + RESET + fg(46) + "+" + f"{s['rewards']:.4f} tiket" + RESET)
    buf += box_line(fg(51) + "└─ Runtime      : " + RESET + fg(208) + rts + RESET)
    buf += box_divider()

    # LOGS
    for i in range(6):
        if i < len(s["log"]):
            l    = s["log"][i]
            icon = tag_icon(l["tag"])
            tag  = tag_color(l["tag"])
            line = dim(f"[{l['time']}]") + " " + fg(250) + icon + RESET + " " + tag + " " + fg(252) + l["msg"] + RESET
            buf += box_line(line)
        else:
            buf += fg(51) + "║" + (" " * 62) + "║" + RESET + "\n"

    buf += fg(51) + "╚══════════════════════════════════════════════════════════════╝" + RESET + "\n"
    buf += "\n   " + gradient(f"BOT {status_text}", 46, 226) + " " + fg(250) + "• " + datetime.now().strftime("%H:%M:%S") + RESET + "\n"
    buf += "   " + dim("By Power ") + fg(213) + "@SouuXso" + RESET + dim(" • ") + fg(46) + "PriceDrops Edition" + RESET + "\n\n"

    sys.stdout.write(buf)
    sys.stdout.flush()


# ============================================================
#   TIMER
# ============================================================
def timer(seconds, prefix="  wait.."):
    wait_time = int(seconds)
    if wait_time <= 0:
        wait_time = 1
    frames = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    fc = len(frames)
    cf = 0
    while wait_time > 0:
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


# ============================================================
#   HELPERS
# ============================================================
def safe_float(v, default=0.0):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except (ValueError, TypeError):
        return default

def safe_int(v, default=0):
    try:
        if v is None or v == "":
            return default
        return int(float(v))
    except (ValueError, TypeError):
        return default


# ============================================================
#   CONFIG IO
# ============================================================
def get_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r") as f:
            c = json.load(f)
        if "initData" not in c:
            return None
        return c
    except Exception:
        return None


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ============================================================
#   BOT CLASS
# ============================================================
class PrizeDropBot:
    def __init__(self, init_data):
        self.init_data = init_data
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": ("Mozilla/5.0 (Linux; Android 15; SM-S928B) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/146.0.7680.153 Mobile Safari/537.36 "
                           "Telegram-Android/12.1.1"),
            "Content-Type": "application/json",
            "origin": "https://pricedropes.lovable.app",
            "referer": "https://pricedropes.lovable.app/",
            "accept": "*/*",
            "sec-ch-ua-platform": '"Android"',
            "sec-ch-ua-mobile": "?1",
            "x-telegram-init-data": init_data,
        })

        self.username = "Unknown"
        self.ticket_balance = 0.0
        self.cash_balance = 0.0
        self.ads_watched = 0
        self.daily_ad_limit = 50

    def init_session(self):
        try:
            self.session.get(APP_URL, timeout=12)
            if "session-id" not in self.session.cookies.get_dict():
                self.session.cookies.set("session-id", str(uuid.uuid4()))
            return True
        except Exception:
            return False

    def get_account(self):
        try:
            r = self.session.get(f"{BASE_URL}/account", timeout=12)
            if r.status_code == 200:
                d = r.json()
                self.ticket_balance = safe_float(d.get("ticketBalance"), 0.0)
                self.cash_balance   = safe_float(d.get("cashBalance"), 0.0)
                self.ads_watched    = safe_int(d.get("adsWatched"), 0)

                ACC["user"]   = self.username if self.username != "Unknown" else (
                    d.get("firstName") or d.get("username") or "User"
                )
                ACC["ticket"] = str(self.ticket_balance)
                ACC["cash"]   = f"{self.cash_balance:.2f}"
                return d
            else:
                add_log("ERROR", f"account HTTP {r.status_code}")
        except Exception as e:
            add_log("ERROR", f"account: {str(e)[:50]}")
        return None

    def get_config_api(self):
        try:
            r = self.session.get(f"{BASE_URL}/app-config", timeout=12)
            if r.status_code == 200:
                return r.json()
            else:
                add_log("ERROR", f"config HTTP {r.status_code}")
        except Exception as e:
            add_log("ERROR", f"config: {str(e)[:50]}")
        return None

    def spin(self):
        try:
            r = self.session.post(f"{BASE_URL}/rewards",
                                  json={"action": "spin"}, timeout=12)
            if r.status_code == 200:
                d = r.json()
                if d.get("ok"):
                    rew = safe_float(d.get("reward"), 0.0)
                    self.ticket_balance = safe_float(
                        d.get("ticketBalance"), self.ticket_balance)
                    STATS["spins"] += 1
                    STATS["rewards"] += rew
                    ACC["ticket"] = str(self.ticket_balance)
                    return True
        except Exception:
            pass
        return False

    def claim_task(self, task_id, title):
        try:
            r = self.session.post(f"{BASE_URL}/rewards",
                                  json={"action": "task", "taskId": task_id},
                                  timeout=12)
            if r.status_code == 200:
                d = r.json()
                if d.get("ok"):
                    rew = safe_float(d.get("reward"), 0.0)
                    self.ticket_balance = safe_float(
                        d.get("ticketBalance"), self.ticket_balance)
                    STATS["tasks"] += 1
                    STATS["rewards"] += rew
                    ACC["ticket"] = str(self.ticket_balance)
                    return True
        except Exception:
            pass
        return False

    def claim_ad(self, network_id, net_name):
        try:
            payload = {
                "action": "ad",
                "networkId": network_id,
                "eventId": str(uuid.uuid4()),
            }
            r = self.session.post(f"{BASE_URL}/rewards", json=payload, timeout=12)

            if r.status_code == 200:
                d = r.json()
                if d.get("ok"):
                    rew = safe_float(d.get("reward"), 0.0)
                    self.ticket_balance = safe_float(
                        d.get("ticketBalance"), self.ticket_balance)
                    self.ads_watched = safe_int(
                        d.get("adsWatched"), self.ads_watched + 1)
                    STATS["ads"] += 1
                    STATS["rewards"] += rew
                    ACC["ticket"] = str(self.ticket_balance)
                    return True, False, rew
                err = (d.get("error") or "").lower()
                if "limit" in err:
                    return False, True, 0
            elif r.status_code == 400:
                return False, True, 0
        except Exception:
            pass
        return False, False, 0

    # ---------- RUN ----------
    def run(self):
        # reset stats
        STATS["ads"] = 0
        STATS["spins"] = 0
        STATS["tasks"] = 0
        STATS["rewards"] = 0.0
        STATS["start"] = time.time()
        STATS["log"] = []
        ACC["status"] = "running"

        add_log("INIT", "PriceDrops engine boot")
        clear()
        banner("INIT")

        self.init_session()

        human_delay(200, 500)
        acc = self.get_account()
        if not acc:
            add_log("ERROR", "Account load failed")
            clear()
            banner("ERROR")
            sys.stdout.write(fg(196) + "\n  ✖ InitData expired/salah. Enter...\n" + RESET)
            sys.stdout.flush()
            input()
            return

        self.username = (acc.get("firstName")
                         or acc.get("username")
                         or acc.get("name")
                         or "User")
        ACC["user"] = self.username

        add_log("AUTH", f"Login as {self.username}")
        clear()
        banner("RUNNING")

        cfg = self.get_config_api()
        if not cfg:
            add_log("ERROR", "Config load failed")
            clear()
            banner("ERROR")
            sys.stdout.write(fg(196) + "\n  ✖ Config gagal. Enter...\n" + RESET)
            sys.stdout.flush()
            input()
            return

        settings = cfg.get("settings", {})
        self.daily_ad_limit = safe_int(settings.get("ads_daily_limit"), 50)

        # ===== SPIN =====
        add_log("SPIN", "Lucky Spin start")
        clear()
        banner("RUNNING")

        spin_count = 0
        spin_consec_fail = 0
        while not G["STOP"]:
            if not self.spin():
                spin_consec_fail += 1
                if spin_consec_fail >= MAX_CONSECUTIVE_FAIL:
                    break
                break
            spin_count += 1
            spin_consec_fail = 0
            add_log("CLAIM", f"Spin #{spin_count} (tiket {self.ticket_balance})")
            clear()
            banner("RUNNING")
            time.sleep(SPIN_DELAY)

        add_log("SPIN", f"Spin done ({spin_count}x)")
        clear()
        banner("RUNNING")

        # ===== TASK =====
        tasks = cfg.get("tasks", [])
        if tasks and not G["STOP"]:
            add_log("TASK", f"Klaim {len(tasks)} task")
            clear()
            banner("RUNNING")

            for t in tasks:
                if G["STOP"]:
                    break
                t_id = t.get("id")
                t_title = (t.get("title") or "Task").strip()[:40]

                ok = self.claim_task(t_id, t_title)
                if ok:
                    add_log("CLAIM", f"Task '{t_title}' ok")
                else:
                    add_log("TASK", f"Task '{t_title}' skip")
                clear()
                banner("RUNNING")
                time.sleep(TASK_DELAY)

            add_log("TASK", f"All tasks checked")
            clear()
            banner("RUNNING")

        # ===== ADS =====
        networks = cfg.get("networks", [])
        if networks and not G["STOP"]:
            add_log("AD", f"Ads target {self.daily_ad_limit}")
            clear()
            banner("RUNNING")

            net_idx = 0
            ad_fail = 0
            while self.ads_watched < self.daily_ad_limit and not G["STOP"]:
                net = networks[net_idx % len(networks)]
                net_name = net.get("name", "Ad")

                add_log("AD", f"{net_name} #{self.ads_watched+1}")
                clear()
                banner("RUNNING")

                ok, limit_hit, rew = self.claim_ad(net.get("id"), net_name)

                if limit_hit:
                    add_log("BLOCK", "Limit reached")
                    clear()
                    banner("RUNNING")
                    break

                if ok:
                    add_log("CLAIM", f"+{rew} tiket (total {self.ads_watched}/{self.daily_ad_limit})")
                    clear()
                    banner("RUNNING")
                    ad_fail = 0

                    wait = random.uniform(*AD_DELAY)
                    add_log("WAIT", f"next ad {wait:.1f}s")
                    clear()
                    banner("RUNNING")
                    time.sleep(wait)
                else:
                    ad_fail += 1
                    add_log("ERROR", f"{net_name} fail ({ad_fail}/{MAX_CONSECUTIVE_FAIL})")
                    clear()
                    banner("RUNNING")
                    if ad_fail >= MAX_CONSECUTIVE_FAIL:
                        add_log("BLOCK", "Ads stop")
                        clear()
                        banner("RUNNING")
                        break
                    time.sleep(3)

                net_idx += 1

        # ===== FINAL =====
        self.get_account()
        ACC["status"] = "done"
        add_log("SYSTEM", f"Done — {STATS['spins']} spin, {STATS['tasks']} task, {STATS['ads']} ads")
        clear()
        banner("DONE")

        sys.stdout.write(
            fg(46) + f"\n  ✅ Selesai! Tiket: {self.ticket_balance} | Cash: ${self.cash_balance:.2f}\n" + RESET
        )
        sys.stdout.write(fg(226) + "  Enter balik ke menu...\n" + RESET)
        sys.stdout.flush()
        input()
        ACC["status"] = "idle"


# ============================================================
#   VALIDASI
# ============================================================
def is_valid_init_data(s):
    if not s or len(s) < 50:
        return False, "Terlalu pendek"
    if "user=" not in s:
        return False, "Tidak ada 'user='"
    if "hash=" not in s:
        return False, "Tidak ada 'hash='"
    return True, "OK"


# ============================================================
#   SIGNAL
# ============================================================
def signal_handler(sig, frame):
    sys.stdout.write("\n" + fg(208) + "  ⚠ Ctrl+C — stopping...\n" + RESET)
    sys.stdout.flush()
    G["STOP"] = True


# ============================================================
#   MENU
# ============================================================
def menu():
    cfg = get_config()
    init_disp = "belum diset"
    user_disp = "?"
    if cfg and cfg.get("initData"):
        try:
            parsed = dict(parse_qsl(cfg["initData"]))
            user = json.loads(unquote(parsed.get("user", "{}")))
            user_disp = "@" + str(user.get("username", "?"))
            init_disp = cfg["initData"][:24] + "..."
        except Exception:
            init_disp = cfg["initData"][:24] + "..."

    buf = ""
    buf += fg(51) + "╔══════════════════════════════════════════════════════════════╗" + RESET + "\n"
    buf += box_line(gradient("PRICEDROPES MENU", 51, 213))
    buf += box_line(dim("─────── SOUU ENGINE ───────"))
    buf += box_divider()
    buf += box_line(fg(51) + "  initData : " + RESET + fg(226) + init_disp + RESET)
    buf += box_line(fg(51) + "  User     : " + RESET + fg(226) + user_disp + RESET)
    buf += box_divider()
    buf += box_line(fg(46)  + "  [1] " + RESET + fg(252) + "Start Farming (Spin+Task+Ads)" + RESET)
    buf += box_line(fg(208) + "  [2] " + RESET + fg(252) + "Config initData" + RESET)
    buf += box_line(fg(196) + "  [0] " + RESET + fg(252) + "Exit" + RESET)
    buf += fg(51) + "╚══════════════════════════════════════════════════════════════╝" + RESET + "\n\n"
    buf += fg(51) + "  Pilih >> " + RESET

    sys.stdout.write(buf)
    sys.stdout.flush()


def action_config_initdata():
    cfg = get_config() or {"initData": ""}
    sys.stdout.write("\n" + fg(213) + "  Paste initData (query_id=...) :\n" + fg(51) + "  > " + RESET)
    sys.stdout.flush()

    try:
        val = sys.stdin.readline().strip()
    except (EOFError, KeyboardInterrupt):
        return

    if not val:
        sys.stdout.write(fg(196) + "  ✖ kosong, tidak disimpan\n" + RESET)
        sys.stdout.flush()
        human_pause(500, 900)
        return

    ok, reason = is_valid_init_data(val)
    if not ok:
        sys.stdout.write(fg(196) + f"  ✖ Format tidak valid: {reason}\n" + RESET)
        sys.stdout.flush()
        human_pause(800, 1400)
        return

    try:
        parsed = dict(parse_qsl(val))
        user = json.loads(unquote(parsed.get("user", "{}")))
        uname = "@" + str(user.get("username", "?"))
    except Exception:
        uname = "?"

    cfg["initData"] = val
    save_config(cfg)

    sys.stdout.write(fg(46) + f"  ✓ initData disimpan ({len(val)} char) — {uname}\n" + RESET)
    sys.stdout.flush()
    human_pause(500, 900)


# ============================================================
#   MAIN
# ============================================================
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
            cfg = get_config()
            if not cfg or not cfg.get("initData"):
                clear()
                sys.stdout.write(fg(196) + "\n  ✖ initData belum diset. Set dulu (menu 2).\n" + RESET)
                sys.stdout.write(fg(250) + "  Tekan Enter..." + RESET)
                sys.stdout.flush()
                input()
                continue

            bot = PrizeDropBot(cfg["initData"])
            bot.run()

        elif opt == "2":
            action_config_initdata()

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
