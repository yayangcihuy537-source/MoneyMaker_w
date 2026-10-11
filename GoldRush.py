#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║   GOLDRUSH AUTO WATCH — SOUU ENGINE Edition v1.4             ║
║   HOST : goldrush-api.king7star.workers.dev                  ║
║   FEAT : adsgram2 / adloop / monetag / gigapub               ║
║   FEAT : randomized device fingerprint                       ║
║   FEAT : live dashboard + auto-loop                          ║
╚══════════════════════════════════════════════════════════════╝
"""

import requests, json, time, sys, os, random, signal, string, base64
import urllib.parse, re as _re
from datetime import datetime
from collections import deque
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from colorama import init, Fore, Style
init(autoreset=True)

VERSION = "1.4"
API_BASE = "https://goldrush-api.king7star.workers.dev"
ORIGIN = "https://goldrush-4kwg.onrender.com"
CONFIG_FILE = "config_goldrush.json"

BOX_WIDTH = 62
LOG_LINES = 8

TELEGRAM_UA = ("Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 "
               "(KHTML, like Gecko) Chrome/153.0.8010.36 Mobile Safari/537.36 "
               "Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)")

HTTP_MAX_RETRY = 4
HTTP_BACKOFF_BASE = 3
REQUEST_TIMEOUT = 30

# ── Network list: adsgram (1) dihapus, adsgram2 + lain-lain tetep ──
NETWORKS = [
    {"id": "adsgram2", "slot": "morning_adsgram2", "label": "Adsgram 2"},
    {"id": "adloop",   "slot": "morning_adloop",   "label": "Adloop"},
    {"id": "monetag",  "slot": "morning_monetag",  "label": "Monetag"},
    {"id": "gigapub",  "slot": "morning_gigapub",  "label": "Gigapub"},
]

# ── Pool device profile buat randomize fingerprint ──
SCREENS = [
    "360x800@3", "360x780@3", "384x832@2.8125", "393x873@3", "412x915@2.625",
    "360x812@3", "412x892@2.625", "384x854@2.8125", "393x830@2.75",
    "412x919@2.625", "360x760@3", "428x926@2.625",
]

GPUS = [
    "ANGLE ((Samsung Xclipse 530) on Vulkan 1.3.279)",
    "ANGLE ((Samsung Xclipse 920) on Vulkan 1.3.279)",
    "ANGLE ((Adreno (TM) 730) on Vulkan 1.3.220)",
    "ANGLE ((Adreno (TM) 740) on Vulkan 1.3.250)",
    "ANGLE ((Mali-G78 MC14) on Vulkan 1.1.178)",
    "ANGLE ((Mali-G77 MC9) on Vulkan 1.1.176)",
    "ANGLE ((Mali-G68 MC4) on Vulkan 1.1.178)",
    "ANGLE ((PowerVR GM9446) on Vulkan 1.1.178)",
    "ANGLE ((Adreno (TM) 650) on Vulkan 1.1.194)",
    "ANGLE ((Mali-G715-Immortalis MC11) on Vulkan 1.3.0)",
    "ANGLE ((Adreno (TM) 710) on Vulkan 1.3.220)",
    "ANGLE ((Samsung Xclipse 940) on Vulkan 1.3.280)",
]

HARDWARE_CORES = [4, 6, 8, 10, 12]
DEVICE_MEMORY = [4, 6, 8, 12, 16]

BATTERY_LEVELS = [
    "25% (charging)", "44% (charging)", "55% (charging)", "67% (charging)",
    "78% (charging)", "89% (charging)", "32% (discharging)",
    "58% (discharging)", "74% (discharging)", "91% (discharging)",
]

HUMAN_PAUSE_MIN = 3
HUMAN_PAUSE_MAX = 6
MAX_EMPTY_CYCLES = 3

CLEAR = "\033[2J\033[3J\033[H"


class AuthError(Exception):
    pass


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def generate_random_device_id():
    return ''.join(random.choices(string.hexdigits.lower(), k=32))


def generate_random_canvas_fingerprint():
    return ''.join(random.choices(string.hexdigits.lower(), k=8))


def generate_random_device_profile():
    return {
        "screen_resolution": random.choice(SCREENS),
        "gpu_renderer": random.choice(GPUS),
        "canvas_fingerprint": generate_random_canvas_fingerprint(),
        "hardware_cores": random.choice(HARDWARE_CORES),
        "device_memory": random.choice(DEVICE_MEMORY),
        "is_touch_device": True,
        "battery_level": random.choice(BATTERY_LEVELS),
    }


def parse_tg_user(init_data):
    try:
        kv = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))
        return json.loads(kv.get("user", "{}"))
    except Exception:
        return {}


# ═══════════════════════════════════════════════════════════════
#  UI
# ═══════════════════════════════════════════════════════════════
class UI:
    state = {
        "title": "GOLDRUSH AUTO WATCH",
        "subtitle": "─────── SOUU ENGINE ───────",
        "running": False,
        "cycle": 0,
        "host": API_BASE,
        "user_id": "-",
        "device_id": "-",
        "screen": "-",
        "gpu": "-",
        "balance": 0,
        "start_balance": 0,
        "state": "INIT",
        "phase": "-",
        "cooldown": 0,
        "last_reward": "-",
        "session_reward": 0,
        "session_ads": 0,
        "net_retry": 0,
        "net_summary": [],
        "watching_name": "-",
        "watching_reward": "-",
        "watching_progress": 0.0,
        "watching_total": 0,
    }
    logs = deque(maxlen=300)

    @staticmethod
    def fg(c, s): return f"\033[38;5;{c}m{s}\033[0m"
    @staticmethod
    def bold(s): return f"\033[1m{s}\033[22m"
    @staticmethod
    def dim(s): return f"\033[2m{s}\033[22m"
    @staticmethod
    def _strip(s): return _re.sub(r'\033\[[0-9;]*m', '', s)
    @staticmethod
    def vlen(s): return len(UI._strip(s))
    @staticmethod
    def pad(s, w):
        vl = UI.vlen(s)
        return s + (" " * (w - vl)) if vl < w else s
    @staticmethod
    def trunc(s, n):
        if UI.vlen(s) <= n: return s
        out = s
        while UI.vlen(out) > n - 1 and len(out) > 0:
            out = out[:-1]
        return out + "…\033[0m"
    @staticmethod
    def gradient(text, start=51, end=213):
        if not text: return text
        n = len(text)
        if n <= 1: return UI.fg(start, text)
        return "".join(
            f"\033[38;5;{int(round(start + (end - start) * i / (n - 1)))}m{ch}"
            for i, ch in enumerate(text)
        ) + "\033[0m"

    @staticmethod
    def top(): return UI.fg(51, "╔" + "═" * BOX_WIDTH + "╗")
    @staticmethod
    def mid(): return UI.fg(51, "╠" + "═" * BOX_WIDTH + "╣")
    @staticmethod
    def bot(): return UI.fg(51, "╚" + "═" * BOX_WIDTH + "╝")
    @staticmethod
    def row(content):
        return UI.fg(51, "║") + UI.pad(" " + content, BOX_WIDTH) + UI.fg(51, "║")
    @staticmethod
    def blank():
        return UI.fg(51, "║") + (" " * BOX_WIDTH) + UI.fg(51, "║")

    @staticmethod
    def render():
        if not UI.state["running"]: return
        s = UI.state
        buf = CLEAR
        buf += UI.top() + "\n"
        buf += UI.row(UI.bold(UI.gradient(s["title"], 51, 213))) + "\n"
        buf += UI.row(UI.dim(s["subtitle"])) + "\n"
        buf += UI.mid() + "\n"

        # USER
        buf += UI.row(UI.bold("USER")) + "\n"
        buf += UI.row("├─ " + UI.pad("TG ID", 12) + ": " + UI.trunc(UI.fg(226, str(s["user_id"])), 29)) + "\n"
        buf += UI.row("├─ " + UI.pad("Balance", 12) + ": " + UI.fg(46, f"{int(s['balance']):,}")) + "\n"
        buf += UI.row("└─ " + UI.pad("Started", 12) + ": " + UI.fg(226, str(int(s['start_balance'])))) + "\n"
        buf += UI.mid() + "\n"

        # DEVICE
        buf += UI.row(UI.bold("DEVICE (randomized)")) + "\n"
        buf += UI.row("├─ " + UI.pad("Device ID", 12) + ": " + UI.trunc(UI.fg(213, str(s["device_id"])), 29)) + "\n"
        buf += UI.row("├─ " + UI.pad("Screen", 12) + ": " + UI.fg(226, str(s["screen"]))) + "\n"
        buf += UI.row("└─ " + UI.pad("GPU", 12) + ": " + UI.trunc(UI.fg(208, str(s["gpu"])), 29)) + "\n"
        buf += UI.mid() + "\n"

        # NETWORKS
        buf += UI.row(UI.bold("AD NETWORKS")) + "\n"
        nets = s.get("net_summary", [])
        if not nets:
            buf += UI.row("└─ " + UI.dim("(belum load)")) + "\n"
        else:
            for i, n in enumerate(nets):
                last = (i == len(nets) - 1)
                branch = "└─" if last else "├─"
                name = n["label"][:14]
                st = n["status"]
                rw = n.get("reward", 0)
                dur = n.get("min_dur", 0)
                hits = n.get("hits", 0)
                fails = n.get("fails", 0)

                if st == "ready":
                    color, tag = 46, "READY"
                elif st == "watching":
                    color, tag = 213, "WATCH"
                elif st == "success":
                    color, tag = 46, "OK"
                elif st == "failed":
                    color, tag = 196, "FAIL"
                elif st == "skip":
                    color, tag = 208, "SKIP"
                else:
                    color, tag = 226, st.upper()

                line = (branch + " " + UI.pad(name, 14) +
                        " " + UI.fg(46, f"+{rw}") +
                        " " + UI.fg(208, f"{dur}s") +
                        " " + UI.fg(51, f"ok{hits}/x{fails}") +
                        " " + UI.fg(color, tag))
                buf += UI.row(line) + "\n"
        buf += UI.mid() + "\n"

        # WATCHING
        buf += UI.row(UI.bold("WATCHING")) + "\n"
        wname = s.get("watching_name", "-")
        wrew = s.get("watching_reward", "-")
        wpct = float(s.get("watching_progress", 0.0))
        wtotal = int(s.get("watching_total", 0))
        bar_len = 34
        filled = int(wpct * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        if wname == "-":
            buf += UI.row("├─ " + UI.dim("idle — menunggu iklan…")) + "\n"
            buf += UI.row("├─ [" + UI.dim("░" * bar_len) + "]") + "\n"
        else:
            buf += UI.row("├─ " + UI.fg(226, UI.trunc(wname, 42))) + "\n"
            buf += UI.row("├─ [" + UI.fg(46, bar) + "] " + UI.fg(226, f"{int(wpct*100)}%")) + "\n"
        remain = wtotal - int(wpct * wtotal) if wtotal else 0
        buf += UI.row("└─ " + UI.pad("Reward", 9) + ": " + UI.fg(46, str(wrew)) +
                      "  " + UI.pad("Sisa", 5) + ": " + UI.fg(208, f"{remain}s")) + "\n"
        buf += UI.mid() + "\n"

        # SESSION
        buf += UI.row(UI.bold("SESSION")) + "\n"
        buf += UI.row("├─ " + UI.pad("Cycle", 12) + ": " + UI.fg(226, str(s["cycle"]))) + "\n"
        buf += UI.row("├─ " + UI.pad("Ads watched", 12) + ": " + UI.fg(226, str(s["session_ads"]))) + "\n"
        srew = s.get("session_reward", 0)
        buf += UI.row("├─ " + UI.pad("Reward", 12) + ": " + UI.fg(46, f"+{int(srew)}")) + "\n"
        buf += UI.row("├─ " + UI.pad("Last", 12) + ": " + UI.fg(226, str(s["last_reward"]))) + "\n"
        buf += UI.row("└─ " + UI.pad("Net retry", 12) + ": " + UI.fg(208, str(s.get("net_retry", 0)))) + "\n"
        buf += UI.mid() + "\n"

        # STATUS
        phase = str(s["phase"])
        if int(s["cooldown"]) > 0: phase += f" · {int(s['cooldown'])}s"
        state_color = {"RUNNING": 46, "WAITING": 208, "ERROR": 196,
                       "INIT": 240, "DONE": 46, "PAUSE": 213, "RETRY": 208,
                       "WATCHING": 213, "COOLDOWN": 208}.get(s["state"], 226)
        buf += UI.row(UI.bold("STATUS")) + "\n"
        buf += UI.row("├─ " + UI.pad("State", 12) + ": " + UI.fg(state_color, str(s["state"]))) + "\n"
        buf += UI.row("└─ " + UI.pad("Phase", 12) + ": " + UI.trunc(UI.fg(208, phase), 29)) + "\n"
        buf += UI.mid() + "\n"

        # LOGS
        logs = list(UI.logs)[-LOG_LINES:]
        for i in range(LOG_LINES):
            if i < len(logs): buf += UI.row(UI.fmt_log(logs[i])) + "\n"
            else: buf += UI.blank() + "\n"

        buf += UI.bot() + "\n"
        buf += "\n   " + UI.bold(UI.fg(46, "BOT RUNNING")) + " " + UI.dim("•") + " " + \
               UI.fg(51, datetime.now().strftime("%H:%M:%S")) + "\n"
        buf += "   " + UI.dim("By Power ") + UI.fg(213, "@SouuXso") + UI.dim(" • ") + \
               UI.fg(46, "GoldRush Edition") + "\n\n"
        sys.stdout.write(buf); sys.stdout.flush()

    @staticmethod
    def fmt_log(l):
        cmap = {"info": 51, "ok": 46, "warn": 208, "err": 196, "step": 213, "dbg": 240}
        c = cmap.get(l["kind"], 250)
        ts = UI.dim("[" + l["ts"] + "]")
        icon = UI.fg(c, l["icon"])
        tag = UI.fg(c, UI.pad(l["tag"], 8))
        avail = BOX_WIDTH - 1 - 10 - 1 - 1 - 1 - 8
        msg = UI.trunc(UI.fg(250, l["msg"]), avail)
        return f"{ts} {icon} {tag} {msg}"

    @staticmethod
    def push(tag, msg, kind="info", icon="◈"):
        UI.logs.append({"ts": datetime.now().strftime("%H:%M:%S"),
                        "icon": icon, "tag": tag.upper(), "msg": msg, "kind": kind})
        if UI.state["running"]: UI.render()

    @staticmethod
    def ok(tag, msg): UI.push(tag, msg, "ok", "✔")
    @staticmethod
    def err(tag, msg): UI.push(tag, msg, "err", "✖")
    @staticmethod
    def warn(tag, msg): UI.push(tag, msg, "warn", "◈")
    @staticmethod
    def info(tag, msg): UI.push(tag, msg, "info", "◈")
    @staticmethod
    def step(tag, msg): UI.push(tag, msg, "step", "⬢")

    @staticmethod
    def set(**kw): UI.state.update(kw)

    @staticmethod
    def start_panel():
        UI.state["running"] = True
        UI.render()

    @staticmethod
    def stop_panel(): UI.state["running"] = False

    @staticmethod
    def countdown(seconds, label):
        for i in range(int(seconds), 0, -1):
            UI.set(phase=label, cooldown=i)
            if UI.state["running"]: UI.render()
            time.sleep(1)
        UI.set(phase="-", cooldown=0)

    @staticmethod
    def watch_timer(duration, name, reward):
        UI.set(watching_name=name, watching_reward=reward,
               watching_total=duration, watching_progress=0.0,
               state="WATCHING")
        for i in range(1, duration + 1):
            if not UI.state["running"]: break
            UI.set(watching_progress=i / duration,
                   phase=f"watch {name} {i}/{duration}")
            UI.render()
            time.sleep(1)
        UI.set(watching_name="-", watching_reward="-",
               watching_progress=0.0, watching_total=0)

    @staticmethod
    def c(text, color):
        cmap = {"reset": 0, "bold": 1, "dim": 2,
                "red": 196, "green": 46, "yellow": 226, "blue": 51, "magenta": 201,
                "cyan": 51, "white": 15, "gray": 240, "orange": 208,
                "br_red": 196, "br_green": 46, "br_yellow": 226, "br_cyan": 51}
        return f"\033[{cmap.get(color, 0)}m{text}\033[0m"

    @staticmethod
    def banner():
        W_ = BOX_WIDTH
        def line(c): return UI.fg(51, "║") + UI.pad(" " + c, W_) + UI.fg(51, "║")
        print(CLEAR, end="")
        print(UI.fg(51, "╔" + "═" * W_ + "╗"))
        print(line(UI.bold(UI.gradient("GOLDRUSH AUTO WATCH", 51, 213))))
        print(line(UI.dim("─────── SOUU ENGINE ───────")))
        print(UI.fg(51, "╠" + "═" * W_ + "╣"))
        print(line(UI.bold("ABOUT")))
        print(line("├─ " + UI.pad("Host", 11) + ": goldrush-api"))
        print(line("├─ " + UI.pad("Networks", 11) + f": {len(NETWORKS)} types"))
        print(line("├─ " + UI.pad("Device", 11) + ": randomized"))
        print(line("└─ " + UI.pad("Version", 11) + ": v" + VERSION))
        print(UI.fg(51, "╠" + "═" * W_ + "╣"))
        print(line(UI.bold("AUTHOR")))
        print(line("└─ " + UI.pad("By", 11) + ": " + UI.fg(213, "@SouuXso")))
        print(UI.fg(51, "╚" + "═" * W_ + "╝"))
        print()


# ═══════════════════════════════════════════════════════════════
#  SESSION
# ═══════════════════════════════════════════════════════════════
def make_session():
    s = requests.Session()
    retry = Retry(total=0, connect=0, read=0, redirect=0, status=0, backoff_factor=0)
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


# ═══════════════════════════════════════════════════════════════
#  BOT
# ═══════════════════════════════════════════════════════════════
class GoldRushBot:
    def __init__(self, init_data, device_id=None, device_profile=None):
        self.session = make_session()
        self.init_data = init_data
        self.device_id = device_id or generate_random_device_id()
        self.device = device_profile if device_profile else generate_random_device_profile()

        tg = parse_tg_user(init_data)
        self.tg_id = int(tg.get("id", 0))
        self.username = tg.get("username") or tg.get("first_name") or "?"

        self.balance = 0
        self.start_balance = 0
        self.net_stats = {n["id"]: {"hits": 0, "fails": 0} for n in NETWORKS}

    def _headers(self):
        return {
            "authorization": f"tma {self.init_data}",
            "x-telegram-init-data": self.init_data,
            "x-device-id": self.device_id,
            "user-agent": TELEGRAM_UA,
            "accept": "*/*",
            "content-type": "application/json",
            "origin": ORIGIN,
            "referer": f"{ORIGIN}/",
            "x-requested-with": "org.telegram.messenger.web",
            "sec-ch-ua-platform": '"Android"',
            "sec-ch-ua": '"Android WebView";v="153", "Not_A Brand";v="8", "Chromium";v="153"',
            "sec-ch-ua-mobile": "?1",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        }

    def _is_transient(self, exc):
        msg = str(exc).lower()
        keys = ['connection aborted', 'connection reset', 'connection refused',
                'read timed out', 'timed out', 'timeout', 'ssl error', 'sslerror',
                'temporary failure', 'remote end closed', 'connection broken',
                'protocolerror', 'protocol error', 'badstatusline', 'bad gateway',
                'service unavailable', 'server disconnected', 'incompleteread']
        return any(k in msg for k in keys)

    def _request_with_retry(self, method, url, headers, body=None):
        last_exc = None
        for attempt in range(1, HTTP_MAX_RETRY + 1):
            try:
                if method == "GET":
                    r = self.session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
                else:
                    r = self.session.post(url, headers=headers, data=body, timeout=REQUEST_TIMEOUT)
                return r, None
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout,
                    requests.exceptions.SSLError, requests.exceptions.ChunkedEncodingError,
                    requests.exceptions.ContentDecodingError, requests.exceptions.ProxyError) as e:
                last_exc = e
                if not self._is_transient(e):
                    return None, e
                if attempt < HTTP_MAX_RETRY:
                    wait = HTTP_BACKOFF_BASE * (2 ** (attempt - 1)) + random.uniform(0, 2)
                    UI.warn("NET", f"{type(e).__name__} (try {attempt}/{HTTP_MAX_RETRY}) — retry {int(wait)}s")
                    UI.set(net_retry=int(UI.state.get("net_retry", 0)) + 1)
                    if attempt >= 2:
                        try: self.session.close()
                        except Exception: pass
                        self.session = make_session()
                    time.sleep(wait)
                else:
                    return None, e
        return None, last_exc

    def _post(self, path, body):
        url = f"{API_BASE}{path}"
        headers = self._headers()
        data = json.dumps(body) if body is not None else "{}"
        r, err = self._request_with_retry("POST", url, headers, data)
        if r is None:
            UI.err("HTTP", f"{type(err).__name__}: {str(err)[:40]}")
            return None
        if r.status_code in (401, 403):
            raise AuthError(f"HTTP {r.status_code}")
        try:
            return r.json()
        except Exception:
            return {"success": False, "error": "invalid json", "_raw": r.text[:200]}

    def get_config(self):
        if not os.path.exists(CONFIG_FILE):
            print(CLEAR, end="")
            print(UI.c("\n  ⚙  SETUP — GOLDRUSH", "br_cyan"))
            print(UI.c("  " + "─" * 50, "br_cyan") + "\n")
            print(UI.c("  Telegram Desktop → DevTools → Network", "white"))
            print(UI.c("  Cari request ke goldrush-api, copy 'x-telegram-init-data'", "white"))
            print(UI.c("  (query_id=...&user=...&auth_date=...&signature=...&hash=...)\n", "br_cyan"))
            print(UI.c("  init_data : ", "white"), end="")
            idata = input().strip()
            if not idata:
                print(UI.c("  ✖ kosong\n", "br_red")); sys.exit(1)
            cfg = {
                "init_data": idata,
                "device_id": generate_random_device_id(),
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(cfg, f, indent=2)
            print(UI.c(f"\n  ✓ Saved\n", "br_green"))
            time.sleep(1)
            return cfg
        with open(CONFIG_FILE) as f:
            return json.load(f)

    def user_sync(self):
        UI.step("SYNC", "POST /api/user/sync")
        payload = dict(self.device)
        payload.update({
            "telegram_id": self.tg_id,
            "username": self.username,
            "first_name": self.username,
            "photo_url": "",
            "language_code": "id",
        })
        res = self._post("/api/user/sync", payload)
        if not res or not res.get("success"):
            UI.err("SYNC", f"gagal: {str(res)[:60]}")
            return False
        UI.ok("SYNC", "user synced")
        return True

    def check_channel(self):
        UI.step("CHAN", "check-official-channel")
        res = self._post("/api/user/check-official-channel", {"telegram_id": self.tg_id})
        if not res:
            return False
        ok = bool(res.get("is_member", False))
        if ok:
            UI.ok("CHAN", "member ✓")
        else:
            UI.warn("CHAN", "not a member")
        return ok

    def start_session(self, network_id, slot_key):
        payload = dict(self.device)
        payload.update({
            "telegram_id": self.tg_id,
            "network_id": network_id,
            "slot_key": slot_key,
        })
        res = self._post("/api/ads/session/start", payload)
        if not res:
            return None
        if not res.get("success"):
            err = res.get("error") or res.get("code") or "unknown"
            return {"error": err}
        return {
            "session_token": res.get("session_token"),
            "min_dur": int(res.get("min_duration_sec", 5)),
            "reward": int(res.get("reward", 0)),
        }

    def complete_session(self, session_token):
        payload = dict(self.device)
        payload.update({
            "telegram_id": self.tg_id,
            "session_token": session_token,
        })
        res = self._post("/api/ads/session/complete", payload)
        if not res:
            return None
        return res

    def watch_network(self, net):
        nid = net["id"]
        label = net["label"]
        slot = net["slot"]

        UI.step("START", f"{label}: start session")
        sess = self.start_session(nid, slot)
        if sess is None:
            UI.err("START", f"{label}: no response")
            self.net_stats[nid]["fails"] += 1
            return "FAIL"

        if "error" in sess:
            UI.warn("START", f"{label}: {sess['error'][:40]}")
            self.net_stats[nid]["fails"] += 1
            return "SKIP"

        token = sess["session_token"]
        min_dur = sess["min_dur"]
        reward = sess["reward"]

        if not token:
            UI.err("START", f"{label}: no session_token")
            self.net_stats[nid]["fails"] += 1
            return "FAIL"

        # Update summary ke watching
        for item in UI.state.get("net_summary", []):
            if item["id"] == nid:
                item["status"] = "watching"
                item["reward"] = reward
                item["min_dur"] = min_dur
        UI.render()

        watch_dur = max(min_dur + random.randint(1, 3), min_dur + 1)
        UI.info("WATCH", f"{label}: {watch_dur}s (min {min_dur}s)")
        UI.watch_timer(watch_dur, label, f"+{reward}")

        UI.step("CLAIM", f"{label}: complete session")
        res = self.complete_session(token)

        if not res:
            UI.err("CLAIM", f"{label}: no response")
            self.net_stats[nid]["fails"] += 1
            return "FAIL"

        if not res.get("success"):
            err = res.get("error") or res.get("code") or "unknown"
            UI.err("CLAIM", f"{label}: {err[:50]}")
            self.net_stats[nid]["fails"] += 1
            return "FAIL"

        got = int(res.get("reward", reward))
        new_bal = int(res.get("new_balance", self.balance))
        self.balance = new_bal

        self.net_stats[nid]["hits"] += 1
        try:
            cur = int(UI.state.get("session_reward", 0))
            UI.set(
                balance=self.balance,
                session_reward=cur + got,
                session_ads=int(UI.state.get("session_ads", 0)) + 1,
                last_reward=f"+{got}",
            )
        except Exception:
            pass

        UI.ok("DONE", f"{label}: +{got} • bal {self.balance}")
        return got

    def refresh_summary(self):
        out = []
        for n in NETWORKS:
            st = self.net_stats[n["id"]]
            existing = next((x for x in UI.state.get("net_summary", []) if x["id"] == n["id"]), None)
            out.append({
                "id": n["id"],
                "label": n["label"],
                "slot": n["slot"],
                "reward": existing.get("reward", 0) if existing else 0,
                "min_dur": existing.get("min_dur", 0) if existing else 0,
                "hits": st["hits"],
                "fails": st["fails"],
                "status": "ready",
            })
        UI.set(net_summary=out)
        return out

    def run(self):
        UI.set(state="INIT", session_reward=0, session_ads=0,
               last_reward="-", net_retry=0,
               user_id=self.tg_id,
               device_id=self.device_id[:18] + "…",
               screen=self.device["screen_resolution"],
               gpu=self.device["gpu_renderer"][:40])
        UI.start_panel()

        UI.info("DEVICE", f"{self.device['screen_resolution']} • cores={self.device['hardware_cores']} • ram={self.device['device_memory']}GB")

        try:
            if not self.user_sync():
                UI.err("FATAL", "sync gagal")
                UI.stop_panel(); return
        except AuthError:
            UI.err("FATAL", "auth error — refresh init_data")
            UI.stop_panel(); return

        try:
            self.check_channel()
        except AuthError:
            pass

        self.refresh_summary()

        cycle = 0
        stop_reason = "finished"
        empty_cycles = 0

        while True:
            if not UI.state["running"]:
                stop_reason = "stopped"
                break

            cycle += 1
            UI.set(cycle=cycle, state="RUNNING", phase="-")
            UI.info("CYCLE", f"#{cycle}")

            self.refresh_summary()

            any_success_this_cycle = False

            for net in NETWORKS:
                if not UI.state["running"]: break

                try:
                    result = self.watch_network(net)
                except AuthError:
                    stop_reason = "auth_expired"
                    break

                for item in UI.state.get("net_summary", []):
                    if item["id"] == net["id"]:
                        if isinstance(result, int):
                            item["status"] = "success"
                        elif result == "FAIL":
                            item["status"] = "failed"
                        elif result == "SKIP":
                            item["status"] = "skip"
                        else:
                            item["status"] = "ready"
                UI.render()

                if isinstance(result, int):
                    any_success_this_cycle = True

                pause = random.randint(HUMAN_PAUSE_MIN, HUMAN_PAUSE_MAX)
                UI.set(state="PAUSE")
                UI.warn("PAUSE", f"{pause}s")
                UI.countdown(pause, "human pause")

            if stop_reason == "auth_expired":
                break

            if not any_success_this_cycle:
                empty_cycles += 1
                if empty_cycles >= MAX_EMPTY_CYCLES:
                    UI.ok("DONE", "semua network gagal / habis — bot stop")
                    UI.set(state="DONE", phase="all done")
                    stop_reason = "all_done"
                    break
                UI.warn("IDLE", f"kosong {empty_cycles}/{MAX_EMPTY_CYCLES} — tunggu 30s")
                UI.set(state="WAITING")
                UI.countdown(30, "idle wait")
            else:
                empty_cycles = 0

        UI.set(state="DONE", phase=stop_reason)
        UI.stop_panel()

        print()
        print(UI.c("═" * 64, "br_cyan"))
        print(UI.c("  ✓ BOT SELESAI", "br_green"))
        print(UI.c("═" * 64, "br_cyan"))
        print(UI.c(f"  Reason      : {stop_reason}", "white"))
        print(UI.c(f"  TG ID       : {UI.state['user_id']}", "white"))
        print(UI.c(f"  Balance     : {self.balance}", "br_yellow"))
        print(UI.c(f"  Session     : +{int(UI.state['session_reward'])} ({UI.state['session_ads']} ads)", "br_green"))
        print(UI.c(f"  Net retries : {UI.state['net_retry']}", "yellow"))
        for n in NETWORKS:
            s = self.net_stats[n["id"]]
            print(UI.c(f"  {n['label']:14}: ok={s['hits']} fail={s['fails']}", "white"))
        print(UI.c("═" * 64, "br_cyan"))
        print()


# ═══════════════════════════════════════════════════════════════
#  ENTRY
# ═══════════════════════════════════════════════════════════════
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    UI.banner()
    try:
        if not os.path.exists(CONFIG_FILE):
            bot_tmp = GoldRushBot("")
            bot_tmp.get_config()
        with open(CONFIG_FILE) as f:
            cfg = json.load(f)
        init_data = cfg.get("init_data", "").strip()
        device_id = cfg.get("device_id", "").strip() or None
        if not init_data:
            print(UI.c("  ✖ init_data kosong\n", "br_red")); return
        bot = GoldRushBot(init_data, device_id=device_id)
        bot.run()
    except KeyboardInterrupt:
        raise
    except AuthError:
        UI.stop_panel()
        print(f"\n{Fore.RED}  ✖ auth error — init_data expired{RESET}\n")
    except Exception as e:
        UI.stop_panel()
        print(f"\n{Fore.RED}  ✖ fatal: {e}{RESET}\n")
        import traceback
        traceback.print_exc()


def _on_sigint(sig, frame):
    try: signal.signal(signal.SIGINT, signal.SIG_DFL)
    except Exception: pass
    try: UI.stop_panel()
    except Exception: pass
    try:
        sys.stdout.write(f"\n{Fore.YELLOW}  ! CTRL+C — keluar{RESET}\n\n")
        sys.stdout.flush()
    except Exception: pass
    os._exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, _on_sigint)
    try:
        main()
    except KeyboardInterrupt:
        _on_sigint(signal.SIGINT, None)
