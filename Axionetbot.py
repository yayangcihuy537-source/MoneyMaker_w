#!/usr/bin/env python3
"""
Axionet Auto Bot — SOUU ENGINE EDITION
- Manual InitData via menu config
- Watch ads (register-session → watch)
- Visual: ANSI 256 gradient, box banner, spinner timer, log buffer 6-line
"""
import os
import sys
import re
import json
import time
import random
import signal
import uuid
from datetime import datetime, timezone
from urllib.parse import parse_qsl, unquote

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# ============================================================
#   KONFIG
# ============================================================
BASE_URL = "https://axionet.duckdns.org"
API_BASE = f"{BASE_URL}/api"

START_PARAM = "90bba4dd4313"
CONFIG_FILE = "axionet_config.json"
STATE_FILE  = "axionet_state.json"

AD_TYPES = ["adsgram", "monetag", "gigapub"]
WATCH_DURATION_MIN = 15
WATCH_DURATION_MAX = 20
BETWEEN_ADS_DELAY = (3, 7)
MAX_ADS_PER_TYPE = 100
MAX_CONSECUTIVE_FAIL = 3


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
        "AD":       fg(226) + bold("AD"),
        "WATCH":    fg(213) + bold("WATCH"),
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
        "AD":       "▶",
        "WATCH":    "◉",
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
    "rewards":   0,
    "start":     time.time(),
    "log":       [],
}
ACC = {
    "user":    "?",
    "balance": "0",
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
    s  = STATS
    a  = ACC
    rt = int(time.time() - s["start"])
    rts = f"{rt//3600:02d}:{(rt%3600)//60:02d}:{rt%60:02d}"

    buf = ""
    buf += fg(51) + "╔══════════════════════════════════════════════════════════════╗" + RESET + "\n"
    buf += box_line(gradient("AXIONET AUTO WATCH", 51, 213))
    buf += box_line(dim("─────── SOUU ENGINE ───────"))
    buf += box_divider()

    # AD NETWORK
    buf += box_line(fg(213) + bold("AD NETWORK") + RESET)
    buf += box_line(fg(51) + "├─ Adsgram  : " + RESET + fg(226) + "gems per watch" + RESET)
    buf += box_line(fg(51) + "├─ Monetag  : " + RESET + fg(226) + "gems per watch" + RESET)
    buf += box_line(fg(51) + "└─ Gigapub  : " + RESET + fg(226) + "gems per watch" + RESET)
    buf += box_divider()

    # ACCOUNT
    buf += box_line(fg(213) + bold("ACCOUNT") + RESET)
    buf += box_line(fg(51) + "├─ User       : " + RESET + fg(226) + str(a["user"]) + RESET)
    buf += box_line(fg(51) + "├─ Balance    : " + RESET + fg(46) + str(a["balance"]) + " gems" + RESET)
    buf += box_line(fg(51) + "└─ Status     : " + RESET + fg(226) + str(a["status"]) + RESET)
    buf += box_divider()

    # SYSTEM
    buf += box_line(fg(213) + bold("SYSTEM") + RESET)
    buf += box_line(fg(51) + "├─ Ads Done     : " + RESET + fg(226) + str(s["ads"]) + RESET)
    buf += box_line(fg(51) + "├─ Rewards      : " + RESET + fg(46) + "+" + str(s["rewards"]) + " gems" + RESET)
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
    buf += "   " + dim("By Power ") + fg(213) + "@SouuXso" + RESET + dim(" • ") + fg(46) + "Axionet Edition" + RESET + "\n\n"

    sys.stdout.write(buf)
    sys.stdout.flush()


# ============================================================
#   TIMER (spinner)
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
    os.system('cls' if os.name == 'nt' else 'clear')


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


def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "device_id": str(uuid.uuid4()),
        "created_at": int(time.time()),
    }


def save_state(s):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(s, f, indent=2)
    except Exception as e:
        add_log("ERROR", f"state save: {e}")


STATE = load_state()


# ============================================================
#   USER-AGENT / FINGERPRINT
# ============================================================
USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 "
    "Telegram-Android/12.10.3 (Infinix Infinix X6817; Android 12; SDK 31; AVERAGE)"
)

DEVICE_FINGERPRINT = {
    "userAgent": USER_AGENT,
    "platform": "Linux aarch64",
    "language": "id-ID",
    "languages": "id-ID,en-US",
    "screenW": 360,
    "screenH": 820,
    "colorDepth": 24,
    "timezone": "Asia/Jakarta",
    "cookieEnabled": True,
    "doNotTrack": None,
    "hardwareConcurrency": 8,
    "deviceMemory": 4,
    "tgPlatform": "android",
    "tgVersion": "9.6",
    "tgColorScheme": "light",
    "tgIsExpanded": False,
}


# ============================================================
#   AXI CLIENT
# ============================================================
class Axionet:
    def __init__(self, init_data):
        self.session = requests.Session()
        self.init_data = init_data
        self.user = None

        self.session.headers.update({
            "host": "axionet.duckdns.org",
            "user-agent": USER_AGENT,
            "accept": "*/*",
            "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "content-type": "application/json",
            "origin": BASE_URL,
            "referer": f"{BASE_URL}/",
            "x-requested-with": "org.telegram.messenger",
            "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Android WebView";v="152"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "x-telegram-data": init_data,
            "x-device-id": STATE["device_id"],
            "x-tg-platform": "android",
        })

    def _interaction_proof(self):
        now = int(time.time() * 1000)
        return json.dumps({
            "entropy": random.randint(0, 5),
            "timestamp": now,
            "heartbeat": now - random.randint(300, 1500),
            "visible": True,
        }, separators=(",", ":"))

    def _fingerprint(self):
        return json.dumps(DEVICE_FINGERPRINT, separators=(",", ":"))

    def _common_headers(self, referer=None):
        return {
            "x-interaction-proof": self._interaction_proof(),
            "x-device-fingerprint": self._fingerprint(),
            "referer": referer or f"{BASE_URL}/",
        }

    def login(self):
        add_log("AUTH", "Login ke Axionet...")
        clear()
        banner("INIT")

        payload = {"initData": self.init_data, "startParam": START_PARAM}

        try:
            r = self.session.post(
                f"{API_BASE}/auth/telegram",
                json=payload,
                headers=self._common_headers(),
                timeout=30, verify=False,
            )
        except Exception as e:
            add_log("ERROR", f"Koneksi: {str(e)[:50]}")
            return False

        if not r.ok:
            add_log("ERROR", f"HTTP {r.status_code}: {r.text[:60]}")
            return False

        try:
            self.user = r.json()
        except Exception:
            add_log("ERROR", "Response bukan JSON")
            return False

        ACC["user"] = "@" + str(self.user.get("username", "?"))
        ACC["balance"] = str(self.user.get("balance", "0"))
        add_log("AUTH", f"Login OK — {ACC['user']}")
        clear()
        banner("RUNNING")
        return True

    def get_user(self):
        try:
            r = self.session.get(
                f"{API_BASE}/auth/user",
                headers=self._common_headers(),
                timeout=30, verify=False,
            )
            if r.ok:
                self.user = r.json()
                ACC["user"] = "@" + str(self.user.get("username", "?"))
                ACC["balance"] = str(self.user.get("balance", "0"))
                return self.user
        except Exception as e:
            add_log("ERROR", f"get_user: {str(e)[:50]}")
        return None

    def _generate_session_id(self):
        ts_ms = int(time.time() * 1000)
        rand_part = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=7))
        hex_part = os.urandom(6).hex()
        return f"{ts_ms}-{rand_part}-{hex_part}", ts_ms

    def register_session(self, session_id, ad_type="adsgram", context="ads_watch"):
        payload = {
            "sessionId": session_id,
            "adType": ad_type,
            "context": context,
        }
        try:
            r = self.session.post(
                f"{API_BASE}/ads/register-session",
                json=payload,
                headers=self._common_headers(referer=f"{BASE_URL}/mission"),
                timeout=30, verify=False,
            )
        except Exception as e:
            return {"ok": False, "msg": f"Koneksi: {str(e)[:60]}"}

        if not r.ok:
            return {"ok": False, "msg": f"HTTP {r.status_code}"}

        try:
            d = r.json()
        except Exception:
            return {"ok": False, "msg": "Bukan JSON"}

        if not d.get("success"):
            return {"ok": False, "msg": str(d.get("error", d.get("message", "register gagal")))[:60]}

        return {"ok": True, "data": d}

    def watch_ad(self, ad_type="adsgram"):
        # STEP 1: generate session
        session_id, session_start = self._generate_session_id()

        # STEP 2: register session
        add_log("AD", f"{ad_type} register...")
        clear()
        banner("RUNNING")
        human_delay(120, 300)

        reg = self.register_session(session_id, ad_type, "ads_watch")
        if not reg.get("ok"):
            return {"ok": False, "msg": f"register: {reg.get('msg')}"}

        # STEP 3: watch timer
        watch_sec = random.randint(WATCH_DURATION_MIN, WATCH_DURATION_MAX)
        add_log("WATCH", f"{ad_type} watching {watch_sec}s")
        clear()
        banner("RUNNING")
        timer(watch_sec, f"  {ad_type}..")

        # STEP 4: submit
        payload = {
            "adType": ad_type,
            "sessionId": session_id,
            "backgroundDuration": watch_sec * 1000,
            "backgroundEntered": True,
            "sessionStart": session_start,
        }

        try:
            r = self.session.post(
                f"{API_BASE}/ads/watch",
                json=payload,
                headers=self._common_headers(referer=f"{BASE_URL}/mission"),
                timeout=30, verify=False,
            )
        except Exception as e:
            return {"ok": False, "msg": f"Koneksi: {str(e)[:60]}"}

        if not r.ok:
            return {"ok": False, "msg": f"HTTP {r.status_code}"}

        try:
            d = r.json()
        except Exception:
            return {"ok": False, "msg": "Bukan JSON"}

        if not d.get("success"):
            return {"ok": False, "msg": str(d.get("error", d.get("message", "unknown")))[:60]}

        return {
            "ok": True,
            "reward": d.get("rewardGems", 0),
            "balance": d.get("newBalance", "0"),
            "adsToday": d.get("adsWatchedToday", 0),
            "adTypeWatched": d.get("adTypeWatchedToday", 0),
        }


# ============================================================
#   WATCH LOOP
# ============================================================
def watch_loop(api, ad_types=None, max_ads=None):
    if ad_types is None:
        ad_types = AD_TYPES

    STATS["ads"] = 0
    STATS["rewards"] = 0
    STATS["start"] = time.time()
    STATS["log"] = []
    ACC["status"] = "running"

    add_log("INIT", "Axionet engine boot")
    clear()
    banner("INIT")

    human_delay(200, 500)
    api.get_user()
    add_log("AUTH", f"Session OK — {ACC['user']}")
    clear()
    banner("RUNNING")

    grand_total = 0
    grand_ads = 0

    for ad_type in ad_types:
        if G["STOP"]:
            break

        add_log("SYSTEM", f"Type: {ad_type.upper()}")
        clear()
        banner("RUNNING")

        type_reward = 0
        type_fail = 0
        limit = max_ads or MAX_ADS_PER_TYPE

        for i in range(1, limit + 1):
            if G["STOP"]:
                break

            add_log("AD", f"{ad_type} #{i}")
            clear()
            banner("RUNNING")

            res = api.watch_ad(ad_type)

            if res.get("ok"):
                reward = res.get("reward", 0)
                type_reward += reward
                grand_total += reward
                grand_ads += 1
                STATS["ads"] += 1
                STATS["rewards"] += reward
                ACC["balance"] = str(res.get("balance", ACC["balance"]))
                type_fail = 0

                add_log("CLAIM", f"+{reward} gems (bal {res.get('balance')})")
                clear()
                banner("RUNNING")

                api.get_user()

                if i < limit:
                    wait = random.randint(*BETWEEN_ADS_DELAY)
                    add_log("WAIT", f"{wait}s...")
                    clear()
                    banner("RUNNING")
                    time.sleep(wait)
            else:
                type_fail += 1
                add_log("ERROR", f"{ad_type}: {res.get('msg')}")
                clear()
                banner("RUNNING")

                if type_fail >= MAX_CONSECUTIVE_FAIL:
                    add_log("BLOCK", f"{ad_type} stop ({MAX_CONSECUTIVE_FAIL}x fail)")
                    clear()
                    banner("RUNNING")
                    break

                time.sleep(5)

        if ad_type != ad_types[-1] and not G["STOP"]:
            wait = random.randint(5, 10)
            add_log("WAIT", f"jeda antar network {wait}s")
            clear()
            banner("RUNNING")
            time.sleep(wait)

    ACC["status"] = "done"
    add_log("SYSTEM", f"Selesai +{grand_total} gems ({grand_ads} ads)")
    clear()
    banner("DONE")

    sys.stdout.write(fg(226) + f"\n  ⏱  Selesai: {grand_ads} ads, +{grand_total} gems. Enter...\n" + RESET)
    sys.stdout.flush()
    input()
    ACC["status"] = "idle"


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
    buf += box_line(gradient("AXIONET MENU", 51, 213))
    buf += box_line(dim("─────── SOUU ENGINE ───────"))
    buf += box_divider()
    buf += box_line(fg(51) + "  initData : " + RESET + fg(226) + init_disp + RESET)
    buf += box_line(fg(51) + "  User     : " + RESET + fg(226) + user_disp + RESET)
    buf += box_divider()
    buf += box_line(fg(46)  + "  [1] " + RESET + fg(252) + "Watch ALL (adsgram+monetag+gigapub)" + RESET)
    buf += box_line(fg(213) + "  [2] " + RESET + fg(252) + "Watch Adsgram only" + RESET)
    buf += box_line(fg(213) + "  [3] " + RESET + fg(252) + "Watch Monetag only" + RESET)
    buf += box_line(fg(213) + "  [4] " + RESET + fg(252) + "Watch Gigapub only" + RESET)
    buf += box_line(fg(208) + "  [5] " + RESET + fg(252) + "Config initData" + RESET)
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

    # validasi format
    parsed = dict(parse_qsl(val))
    if not parsed or "user" not in parsed or "hash" not in parsed:
        sys.stdout.write(fg(196) + "  ✖ Format initData tidak valid (butuh user + hash)\n" + RESET)
        sys.stdout.flush()
        human_pause(800, 1400)
        return

    try:
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

        if opt in ("1", "2", "3", "4"):
            cfg = get_config()
            if not cfg or not cfg.get("initData"):
                clear()
                sys.stdout.write(fg(196) + "\n  ✖ initData belum diset. Set dulu (menu 5).\n" + RESET)
                sys.stdout.write(fg(250) + "  Tekan Enter..." + RESET)
                sys.stdout.flush()
                input()
                continue

            api = Axionet(cfg["initData"])

            # login dulu
            if not api.login():
                clear()
                banner("ERROR")
                sys.stdout.write(fg(196) + "\n  ✖ Login gagal. Enter...\n" + RESET)
                sys.stdout.flush()
                input()
                continue

            if opt == "1":
                watch_loop(api, ["adsgram", "monetag", "gigapub"])
            elif opt == "2":
                watch_loop(api, ["adsgram"])
            elif opt == "3":
                watch_loop(api, ["monetag"])
            elif opt == "4":
                watch_loop(api, ["gigapub"])

        elif opt == "5":
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