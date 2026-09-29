#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║   FAUCETPAYZ AUTO CLAIM — SOUU ENGINE Edition v7.1          ║
║   Modes  : Faucet / YT Videos (aviso) / PTC (ajax/surf)     ║
║   Login  : username + password (no cookie file)             ║
╚══════════════════════════════════════════════════════════════╝
"""

import requests, re, json, time, sys, os, random, urllib.parse, secrets, signal
from datetime import datetime
from collections import deque
from colorama import init, Fore, Style
init(autoreset=True)

VERSION = "7.1"
HOST = "https://faucetpayz.com"
CONFIG_FILE = "config_faucetpayz.json"

WARYONO_IN  = "https://api.waryono.my.id/in.php"
WARYONO_RES = "https://api.waryono.my.id/res.php"

AVISO_API = "https://aviso.bz/api/v1"
AVISO_API_KEY_DEFAULT = "ak_744a2dca34fa1f0eea83f272ca72783d9e599bbb"

R, G, Y, B, C, W, M = Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.CYAN, Fore.WHITE, Fore.MAGENTA
RESET = Style.RESET_ALL

BOX_WIDTH = 62
LOG_LINES = 7
SUPPORTED_TASK_TYPES = ['ads', 'like']
ANSI_RE = re.compile(r'\033\[[0-9;]*m')

DEFAULT_UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36")
DEFAULT_TURNSTILE = "0x4AAAAAAAB-TZt_lwYtViEL"


# ═════════════════════════════════════════════════════════════
#  PANEL UI
# ═════════════════════════════════════════════════════════════
class UI:
    state = {
        "title": "FAUCETPAYZ AUTO CLAIM", "subtitle": "─────── SOUU ENGINE ───────",
        "running": False, "cycle": 0, "host": HOST, "user": "-",
        "balance": "-", "purchase": "-", "points": "-",
        "state": "INIT", "phase": "-", "cooldown": 0,
        "solver": "WARYONO", "mode": "-", "start_ts": int(time.time()),
    }
    logs = deque(maxlen=200)

    @staticmethod
    def fg(c, s): return f"\033[38;5;{c}m{s}\033[0m"
    @staticmethod
    def bold(s): return f"\033[1m{s}\033[22m"
    @staticmethod
    def dim(s): return f"\033[2m{s}\033[22m"
    @staticmethod
    def strip_ansi(s): return ANSI_RE.sub('', s)
    @staticmethod
    def vlen(s): return len(UI.strip_ansi(s))
    @staticmethod
    def pad(s, w):
        vl = UI.vlen(s)
        return s + (" " * (w - vl)) if vl < w else s

    @staticmethod
    def trunc_ansi(s, max_visible):
        if UI.vlen(s) <= max_visible:
            return s
        out, visible, i, n = [], 0, 0, len(s)
        target = max_visible - 1
        while i < n and visible < target:
            if s[i] == '\033':
                j = i + 1
                while j < n and s[j] != 'm': j += 1
                if j < n: out.append(s[i:j + 1]); i = j + 1
                else: i += 1
            else:
                out.append(s[i]); visible += 1; i += 1
        return "".join(out) + "…" + "\033[0m"

    @staticmethod
    def trunc(s, n): return UI.trunc_ansi(s, n)

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
        buf = "\033[2J\033[H"
        buf += UI.top() + "\n"
        buf += UI.row(UI.bold(UI.gradient(s["title"], 51, 213))) + "\n"
        buf += UI.row(UI.dim(s["subtitle"])) + "\n"
        buf += UI.mid() + "\n"

        buf += UI.row(UI.bold("SESSION")) + "\n"
        buf += UI.row("├─ " + UI.pad("Host", 11) + ": " + UI.trunc(UI.fg(226, s["host"]), 30)) + "\n"
        buf += UI.row("├─ " + UI.pad("Mode", 11) + ": " + UI.fg(213, str(s["mode"]).upper())) + "\n"
        buf += UI.row("├─ " + UI.pad("Cycle", 11) + ": " + UI.fg(226, str(s["cycle"]))) + "\n"
        buf += UI.row("└─ " + UI.pad("Solver", 11) + ": " + UI.fg(226, s["solver"])) + "\n"
        buf += UI.mid() + "\n"

        buf += UI.row(UI.bold("ACCOUNT")) + "\n"
        buf += UI.row("├─ " + UI.pad("User", 11) + ": " + UI.trunc(UI.fg(226, str(s["user"])), 30)) + "\n"
        buf += UI.row("├─ " + UI.pad("Balance", 11) + ": " + UI.trunc(UI.fg(46, str(s["balance"])), 30)) + "\n"
        buf += UI.row("├─ " + UI.pad("Purchase", 11) + ": " + UI.trunc(UI.fg(226, str(s["purchase"])), 30)) + "\n"
        buf += UI.row("└─ " + UI.pad("Points", 11) + ": " + UI.trunc(UI.fg(226, str(s["points"])), 30)) + "\n"
        buf += UI.mid() + "\n"

        phase = str(s["phase"])
        if int(s["cooldown"]) > 0: phase += f" · {int(s['cooldown'])}s"
        state_color = {"RUNNING": 46, "WAITING": 208, "ERROR": 196,
                       "INIT": 240, "DONE": 46, "LOGIN": 226}.get(s["state"], 226)
        buf += UI.row(UI.bold("STATUS")) + "\n"
        buf += UI.row("├─ " + UI.pad("State", 11) + ": " + UI.fg(state_color, str(s["state"]))) + "\n"
        buf += UI.row("└─ " + UI.pad("Phase", 11) + ": " + UI.trunc(UI.fg(208, phase), 30)) + "\n"
        buf += UI.mid() + "\n"

        logs = list(UI.logs)[-LOG_LINES:]
        for i in range(LOG_LINES):
            if i < len(logs): buf += UI.row(UI.fmt_log(logs[i])) + "\n"
            else: buf += UI.blank() + "\n"

        buf += UI.bot() + "\n"
        buf += "\n   " + UI.bold(UI.fg(46, "BOT RUNNING")) + " " + UI.dim("•") + " " + UI.fg(51, datetime.now().strftime("%H:%M:%S")) + "\n"
        buf += "   " + UI.dim("By Power ") + UI.fg(213, "@SouuXso") + UI.dim(" • ") + UI.fg(46, "FaucetPayz Edition") + "\n\n"
        sys.stdout.write(buf); sys.stdout.flush()

    @staticmethod
    def fmt_log(l):
        cmap = {"info": 51, "ok": 46, "warn": 208, "err": 196, "step": 213}
        c = cmap.get(l["kind"], 250)
        ts = UI.dim("[" + l["ts"] + "]")
        icon = UI.fg(c, l["icon"])
        tag = UI.fg(c, UI.pad(l["tag"], 7))
        avail = BOX_WIDTH - 1 - 10 - 1 - 1 - 1 - 7
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
        UI.state["start_ts"] = int(time.time())
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
        print()
        print(UI.fg(51, "╔" + "═" * W_ + "╗"))
        print(line(UI.bold(UI.gradient("FAUCETPAYZ AUTO CLAIM", 51, 213))))
        print(line(UI.dim("─────── SOUU ENGINE ───────")))
        print(UI.fg(51, "╠" + "═" * W_ + "╣"))
        print(line(UI.bold("ABOUT")))
        print(line("├─ " + UI.pad("Host", 11) + ": " + HOST))
        print(line("├─ " + UI.pad("Solver", 11) + ": WARYONO"))
        print(line("├─ " + UI.pad("Modes", 11) + ": faucet / ytvideos / ptc"))
        print(line("└─ " + UI.pad("Version", 11) + ": v" + VERSION))
        print(UI.fg(51, "╠" + "═" * W_ + "╣"))
        print(line(UI.bold("AUTHOR")))
        print(line("└─ " + UI.pad("By", 11) + ": " + UI.fg(213, "@SouuXso")))
        print(UI.fg(51, "╚" + "═" * W_ + "╝"))
        print()


def show_menu():
    W_ = BOX_WIDTH
    def line(c): return UI.fg(51, "║") + UI.pad(" " + c, W_) + UI.fg(51, "║")
    print()
    print(UI.fg(51, "╔" + "═" * W_ + "╗"))
    print(line(UI.bold(UI.gradient("SELECT MODE", 51, 213))))
    print(UI.fg(51, "╠" + "═" * W_ + "╣"))
    print(line(UI.fg(46, "  1") + ". " + UI.fg(15, "Faucet") + UI.dim(" — claim every 5 min")))
    print(line(UI.fg(46, "  2") + ". " + UI.fg(15, "YT Videos") + UI.dim(" — aviso API")))
    print(line(UI.fg(46, "  3") + ". " + UI.fg(15, "PTC Ads") + UI.dim(" — paid to click")))
    print(UI.fg(51, "╠" + "═" * W_ + "╣"))
    print(line(UI.fg(196, "  0") + ". " + UI.fg(15, "Exit")))
    print(UI.fg(51, "╚" + "═" * W_ + "╝"))
    print()
    try:
        return input(UI.c("  › ", "br_green") + "Choose [0-3]: ").strip()
    except (EOFError, KeyboardInterrupt):
        return "0"


# ═════════════════════════════════════════════════════════════
#  BOT
# ═════════════════════════════════════════════════════════════
class FaucetPayzBot:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': DEFAULT_UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        })
        self.username = ""
        self.password = ""
        self.api_key = ""
        self.aviso_endpoint = AVISO_API
        self.aviso_key = AVISO_API_KEY_DEFAULT
        self.user_hash = ""

    def get_config(self):
        if not os.path.exists(CONFIG_FILE):
            print(UI.c("\n  ⚙  SETUP WIZARD", "br_cyan"))
            print(UI.c("  " + "─" * 50, "br_cyan") + "\n")
            print(UI.c("  Username        : ", "white"), end="")
            u = input().strip()
            print(UI.c("  Password        : ", "white"), end="")
            p = input().strip()
            print(UI.c("  Waryono API Key : ", "white"), end="")
            k = input().strip()
            with open(CONFIG_FILE, 'w') as f:
                json.dump({"username": u, "password": p, "api_key": k}, f, indent=2)
            print(UI.c(f"\n  ✓ Config saved to {CONFIG_FILE}\n", "br_green"))
            time.sleep(1)
            return {"username": u, "password": p, "api_key": k}
        with open(CONFIG_FILE) as f:
            return json.load(f)

    def _headers(self, method='GET', referer=None, ajax=False):
        h = {
            'User-Agent': DEFAULT_UA,
            'Accept': '*/*' if ajax else 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
        }
        h['Referer'] = referer if referer else f'{HOST}/'
        if method.upper() == 'POST':
            h['Content-Type'] = 'application/x-www-form-urlencoded'
            h['Origin'] = HOST
        if ajax:
            h['x-requested-with'] = 'XMLHttpRequest'
            h['sec-fetch-site'] = 'same-origin'
            h['sec-fetch-mode'] = 'cors'
            h['sec-fetch-dest'] = 'empty'
        return h

    def _req(self, url, method='GET', data=None, referer=None, allow_redirects=True, ajax=False):
        try:
            hdr = self._headers(method, referer, ajax=ajax)
            if method.upper() == 'GET':
                r = self.session.get(url, headers=hdr, allow_redirects=allow_redirects, timeout=30)
            else:
                r = self.session.post(url, headers=hdr, data=data, allow_redirects=allow_redirects, timeout=30)
            return r.text
        except Exception as e:
            UI.err("HTTP", f"{type(e).__name__}: {str(e)[:40]}")
            return ""

    def is_logged_in(self):
        html = self._req(f"{HOST}/account")
        if not html: return False
        if 'name="username"' in html and 'name="password"' in html: return False
        return any(kw in html for kw in ['/logout', 'Main Balance'])

    def extract_csrf(self, html):
        for p in [r'<input[^>]+name=["\']csrf_token["\'][^>]+value=["\']([^"\']+)["\']',
                  r'<meta\s+name=["\']csrf-token["\']\s+content=["\']([^"\']+)["\']']:
            m = re.search(p, html)
            if m: return m.group(1)
        return None

    def extract_sitekey(self, html):
        m = re.search(r'class=["\']cf-turnstile["\'][^>]*data-sitekey=["\']([^"\']+)["\']', html)
        if m: return m.group(1)
        m = re.search(r'data-sitekey=["\']([^"\']+)["\']', html)
        return m.group(1) if m else None

    def solve_turnstile(self, sitekey, pageurl):
        UI.step("SOLVE", f"Turnstile {sitekey[:16]}…")
        payload = {"apikey": self.api_key, "methods": "turnstile",
                   "sitekey": sitekey, "domain": pageurl, "json": 1}
        try:
            j = requests.post(WARYONO_IN, json=payload, timeout=30).json()
        except Exception as e:
            UI.err("SOLVE", f"TS: {str(e)[:30]}")
            return None
        if not isinstance(j, dict) or j.get("status") != 1:
            UI.err("SOLVE", f"TS: {str(j.get('request', 'bad'))[:40]}")
            return None
        tid = j["request"]
        for i in range(60):
            time.sleep(2)
            try:
                j2 = requests.get(WARYONO_RES,
                    params={"apikey": self.api_key, "id": tid, "action": "get", "json": 1},
                    timeout=30).json()
            except Exception:
                continue
            if not isinstance(j2, dict): continue
            if j2.get("status") == 1:
                token = j2.get("request", "")
                UI.ok("SOLVE", f"Turnstile OK ({len(token)}c)")
                return token
            req = str(j2.get("request", ""))
            if "CAPCHA_NOT_READY" in req:
                if (i + 1) % 5 == 0: UI.info("SOLVE", f"TS poll {i+1}/60")
                continue
            UI.err("SOLVE", f"TS: {req[:40]}")
            return None
        UI.err("SOLVE", "TS timeout")
        return None

    def solve_antibot(self, main_b64, opt_ids, opt_b64s):
        if not main_b64 or not opt_ids: return None
        UI.step("SOLVE", f"Antibot ({len(opt_ids)} opts)")
        payload = {"apikey": self.api_key, "methods": "antibot", "main": main_b64, "json": 1}
        for rel, b64 in zip(opt_ids, opt_b64s):
            payload[str(rel)] = b64
        try:
            j = requests.post(WARYONO_IN, json=payload, timeout=30).json()
        except Exception as e:
            UI.err("SOLVE", f"AB: {str(e)[:30]}")
            return None
        if not isinstance(j, dict) or j.get("status") != 1:
            UI.err("SOLVE", f"AB: {str(j.get('request', 'bad'))[:40]}")
            return None
        tid = j["request"]
        for i in range(80):
            time.sleep(3)
            try:
                raw = requests.get(WARYONO_RES,
                    params={"apikey": self.api_key, "id": tid, "action": "get", "json": 1},
                    timeout=30).text.strip()
                if raw.startswith("OK|"):
                    return raw[3:]
                j2 = json.loads(raw)
            except Exception:
                continue
            if not isinstance(j2, dict): continue
            if j2.get("status") == 1: return str(j2.get("request", ""))
            req = str(j2.get("request", ""))
            if "CAPCHA_NOT_READY" in req:
                if (i + 1) % 5 == 0: UI.info("SOLVE", f"AB poll {i+1}/80")
                continue
            UI.err("SOLVE", f"AB: {req[:40]}")
            return None
        return None

    def login(self):
        UI.step("LOGIN", f"Login as {self.username}")
        self.session.cookies.clear()
        html = self._req(f"{HOST}/login")
        if not html:
            UI.err("LOGIN", "empty page"); return False
        csrf = self.extract_csrf(html)
        sitekey = self.extract_sitekey(html) or DEFAULT_TURNSTILE
        if not csrf:
            UI.err("LOGIN", "CSRF not found"); return False
        token = self.solve_turnstile(sitekey, f"{HOST}/login")
        if not token:
            UI.err("LOGIN", "turnstile fail"); return False

        html2 = self._req(f"{HOST}/login")
        csrf2 = self.extract_csrf(html2) if html2 else None
        if csrf2: csrf = csrf2

        data = {'csrf_token': csrf, 'username': self.username, 'password': self.password,
                '2fa': '', 'remember': '1', 'cf-turnstile-response': token}
        self._req(f"{HOST}/login", 'POST', data=data, referer=f'{HOST}/login')

        if self.is_logged_in():
            UI.ok("LOGIN", "Login OK"); return True
        UI.err("LOGIN", "login failed")
        return False

    def get_dashboard(self):
        html = self._req(f"{HOST}/account")
        if not html or ('name="username"' in html and 'name="password"' in html):
            return None
        info = {'balance': '?', 'purchase_balance': '?', 'points': '?'}
        for pat, key in [
            (r'id=["\']balance["\'][^>]*>([^<]+)', 'balance'),
            (r'id=["\']purchase_balance["\'][^>]*>([^<]+)', 'purchase_balance'),
            (r'id=["\']points["\'][^>]*>([^<]+)', 'points'),
        ]:
            m = re.search(pat, html, re.IGNORECASE)
            if m: info[key] = m.group(1).strip()
        return info

    def parse_balance(self):
        html = self._req(f"{HOST}/account")
        if not html: return None
        m = re.search(r'id=["\']balance["\'][^>]*>([^<]+)', html, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            num = re.search(r'([\d,]+)', raw)
            if num:
                try: return int(num.group(1).replace(',', ''))
                except: return None
        return None

    # ═════════════════════════════════════════════════════════
    #  MODE 1: FAUCET
    # ═════════════════════════════════════════════════════════
    def mode_faucet(self):
        UI.step("HEALTH", "GET /faucet")
        html = self._req(f"{HOST}/faucet", referer=f'{HOST}/account')
        if not html: return 'error'
        if 'name="username"' in html and 'name="password"' in html:
            return 'not_logged_in'

        for tp in [r'id="minute"[^>]*>(\d+)</b>[^:]*:\s*<b[^>]*id="second"[^>]*>(\d+)</b>',
                   r'id="clock"[^>]*>(\d+):(\d+)</span>']:
            m = re.search(tp, html, re.IGNORECASE | re.DOTALL)
            if m:
                mins, secs = int(m.group(1)), int(m.group(2))
                total = mins * 60 + secs
                if total > 0:
                    UI.warn("WAIT", f"timer {mins}m {secs}s")
                    UI.countdown(total, "next claim")
                    return 'waited'

        if 'Claim again' in html or 'claimleft' in html:
            UI.warn("WAIT", "timer active")
            UI.countdown(240, "next claim")
            return 'waited'

        csrf = self.extract_csrf(html)
        sitekey = self.extract_sitekey(html) or DEFAULT_TURNSTILE
        if not csrf:
            UI.err("CLAIM", "CSRF not found"); return False

        main_img = None
        for p in [r'order\s*<img\s+src="data:image/png;base64,([^"]+)"',
                  r'<img[^>]*src="data:image/png;base64,([^"]+)"[^>]*width="276"']:
            m = re.search(p, html, re.DOTALL | re.IGNORECASE)
            if m: main_img = m.group(1); break
        options = []
        for rel, b64 in re.findall(
            r'rel=["\'](\d+)["\'][^>]*>.*?src=["\']data:image/png;base64,([^"\']+)["\']',
            html, re.DOTALL):
            if rel not in [r for r, _ in options]:
                options.append((rel, b64))

        antibot_solution = None
        if options and len(options) >= 3 and main_img:
            UI.info("CLAIM", f"antibot {len(options)} opts")
            antibot_solution = self.solve_antibot(main_img,
                                                  [r for r, _ in options],
                                                  [b for _, b in options])
            if not antibot_solution:
                UI.err("CLAIM", "antibot fail"); return False
        else:
            UI.info("CLAIM", "no antibot")

        token = self.solve_turnstile(sitekey, f"{HOST}/faucet")
        if not token: return False

        data = {'csrf_token': csrf, 'cf-turnstile-response': token}
        if antibot_solution: data['antibotlinks'] = antibot_solution

        UI.step("CLAIM", "submit faucet")
        resp = self._req(f"{HOST}/faucet", 'POST', data=data, referer=f"{HOST}/faucet")

        if 'Tokens has been added' in resp or 'Token has been added' in resp or 'successfully' in resp.lower():
            am = re.search(r'(\d[\d,.]*)\s*Tokens?', resp, re.IGNORECASE)
            UI.ok("CLAIM", f"+{am.group(1)} Tokens!" if am else "claimed!")
            return True
        err_m = re.search(r'alert-danger[^>]*>(.*?)</div>', resp, re.DOTALL)
        if err_m:
            err_text = re.sub(r'<[^>]+>', '', err_m.group(1)).strip()
            UI.err("CLAIM", err_text[:40])
        else:
            UI.err("CLAIM", "failed")
        return False

    # ═════════════════════════════════════════════════════════
    #  MODE 2: YT VIDEOS
    # ═════════════════════════════════════════════════════════
    def extract_aviso(self, html):
        m = re.search(r'<div[^>]+id=["\']aviso-widget["\'][^>]*>', html, re.IGNORECASE)
        if not m: return None, None, None
        tag = m.group(0)
        def _a(name):
            x = re.search(rf'{name}\s*=\s*["\']([^"\']+)["\']', tag, re.IGNORECASE)
            return x.group(1) if x else None
        return _a('data-api-endpoint'), _a('data-api-key'), _a('data-user-hash')

    def aviso_headers(self):
        return {
            'Accept': '*/*', 'Accept-Language': 'en',
            'Content-Type': 'application/json',
            'Origin': HOST, 'Referer': HOST,
            'User-Agent': DEFAULT_UA,
            'X-Api-Key': self.aviso_key,
            'X-Requested-With': 'mark.via.gp',
        }

    def aviso(self, path, body=None, method='POST'):
        url = self.aviso_endpoint.rstrip('/') + path
        try:
            if method == 'GET':
                r = self.session.get(url, headers=self.aviso_headers(), timeout=20)
            else:
                r = self.session.post(url, headers=self.aviso_headers(),
                                      data=json.dumps(body) if body else None, timeout=20)
            try: return r.status_code, r.json()
            except Exception: return r.status_code, None
        except Exception:
            return 0, None

    def mode_ytvideos(self):
        UI.step("LOAD", "GET /ytvideos")
        html = self._req(f"{HOST}/ytvideos", referer=f'{HOST}/account')
        if not html: return 'error'
        if 'name="username"' in html and 'name="password"' in html:
            return 'not_logged_in'

        api_end, api_key, user_hash = self.extract_aviso(html)
        if not (api_end and api_key and user_hash):
            UI.err("AVISO", "widget not found")
            return 'no_task'

        self.aviso_endpoint = api_end
        self.aviso_key = api_key
        self.user_hash = user_hash
        UI.ok("AVISO", f"hash={user_hash[:12]}…")

        UI.step("AVISO", "identify")
        code, j = self.aviso('/youtube/tasks/identify', {
            "hash": user_hash, "ip": None, "userAgent": DEFAULT_UA,
            "fingerprint": {
                "fp": "8661a494702c33f967373004765326f5",
                "hashFont": "2f48d5374924fd0ce9bb54863fb00708",
                "langs": "en-PH, en-US", "timezone": "Asia/Manila",
                "platform": "Linux aarch64",
                "gpu": "Qualcomm~Adreno (TM) 619",
                "screen": "360x804", "memory": 8, "cpuCores": 8,
            },
        })
        if code != 200 or not isinstance(j, dict) or not j.get('id'):
            UI.err("AVISO", f"identify fail: {str(j)[:40]}")
            return 'error'
        UI.ok("AVISO", f"id={j['id']}")

        q = f"?hash={user_hash}&platform=Linux aarch64&offset=0&limit=100"
        code, ja = self.aviso('/youtube/tasks/available' + q, None, 'GET')
        if code != 200 or not isinstance(ja, dict):
            UI.err("AVISO", f"available: HTTP {code}")
            return 'error'

        batch = []
        for t in ('ads', 'like'):
            for task in ja.get(t, []):
                if task.get('inProgress'): continue
                task['_type'] = t
                batch.append(task)

        if not batch:
            UI.warn("AVISO", "no tasks")
            return 'no_task'

        UI.info("AVISO", f"{len(batch)} tasks")
        done = 0

        for task in batch[:8]:
            tid = task.get('id')
            ttype = task.get('_type', 'ads')
            title = str(task.get('title', ''))[:28]
            if not tid: continue

            UI.step("START", f"#{tid} [{ttype}] {title}")

            code, js = self.aviso('/youtube/tasks/start', {
                'taskId': tid, 'hash': user_hash, 'type': ttype, 'platform': 'Linux aarch64',
            })
            if code != 200 or not isinstance(js, dict):
                UI.err("START", f"#{tid} start fail")
                continue
            aid = js.get('attemptId')
            if not aid:
                UI.err("START", f"#{tid} no attemptId")
                continue

            url = js.get('url', '') or ''
            duration = int(js.get('duration', 0) or 0)
            if ttype == 'ads' and duration <= 0: duration = 10
            if ttype == 'like': duration = max(3, duration or 3)

            if url:
                try: self.session.get(url, headers={'user-agent': DEFAULT_UA}, timeout=10)
                except Exception: pass

            code, ts = self.aviso('/youtube/tasks/timer-status',
                                  {'attemptId': aid, 'action': 'start'})
            if not isinstance(ts, dict):
                UI.warn("YT", f"#{tid} timer start fail")
                continue

            status = ts.get('status', '')
            if status == 'need_check':
                UI.info("WATCH", f"#{tid} {duration}s")
                UI.countdown(duration, f"YT #{tid}")

                code, comp = self.aviso('/youtube/tasks/timer-status',
                                        {'attemptId': aid, 'action': 'complete', 'watchedTime': duration})
                if not isinstance(comp, dict) or not comp.get('verified'):
                    UI.warn("YT", f"#{tid} not verified")
                    continue

                code, chk = self.aviso('/youtube/tasks/timer-status',
                                       {'attemptId': aid, 'action': 'check'})
                if not isinstance(chk, dict) or not chk.get('viewExists'):
                    UI.warn("YT", f"#{tid} view not exists")
                    continue

            code, fin = self.aviso('/youtube/tasks/complete', {'attemptId': aid})
            if isinstance(fin, dict):
                if fin.get('code') == 'task_already_processed':
                    UI.ok("CLAIM", f"#{tid} already done"); done += 1
                elif fin.get('earned') or fin.get('amount'):
                    e = fin.get('earned') or fin.get('amount')
                    UI.ok("CLAIM", f"#{tid} +{e}"); done += 1
                else:
                    UI.warn("CLAIM", f"#{tid} resp: {str(fin)[:30]}")
            time.sleep(random.uniform(1.5, 3))

        return done > 0

    # ═════════════════════════════════════════════════════════
    #  MODE 3: PTC
    # ═════════════════════════════════════════════════════════
    def mode_ptc(self):
        UI.step("HEALTH", "GET /surf")
        html = self._req(f"{HOST}/surf", referer=f'{HOST}/account')
        if not html: return 'error'
        if 'name="username"' in html and 'name="password"' in html:
            return 'not_logged_in'

        ads = []
        for m in re.finditer(
            r'<a\s+href="/surf/([a-f0-9]{32})"\s+class="ptclinks[^"]*"[^>]*>(.*?)</a>',
            html, re.DOTALL):
            aid = m.group(1)
            body = m.group(2)
            coins_m = re.search(r'fa-coins[^<]*</i>\s*(\d+)\s*Tokens', body)
            dur_m = re.search(r'fa-clock[^<]*</i>\s*(\d+)\s*s', body)
            ads.append({
                'uid': aid,
                'coins': int(coins_m.group(1)) if coins_m else 18,
                'duration': int(dur_m.group(1)) if dur_m else 5,
            })

        if not ads:
            UI.warn("PTC", "no ads")
            return 'no_task'

        UI.info("PTC", f"{len(ads)} ads")
        done = 0

        for i, ad in enumerate(ads[:8], 1):
            aid = ad['uid']
            dur = ad['duration']
            UI.step("PTC", f"[{i}/{len(ads)}] {aid[:10]}… ({ad['coins']}c, {dur}s)")

            # 1. register view (302 redirect ke ad)
            self._req(f"{HOST}/surf/{aid}", referer=f"{HOST}/surf", allow_redirects=False)

            # 2. generate view token
            button_id = secrets.token_hex(32)
            c_param = button_id + str(random.randint(1000, 9999))

            # 3. fetch view page dengan token
            v = self._req(f"{HOST}/surf/{aid}/{c_param}",
                          referer=f"{HOST}/surf", allow_redirects=False)

            if not v or len(v) < 1000:
                UI.warn("PTC", f"#{aid[:8]} redirect, skip")
                time.sleep(2)
                continue

            m = re.search(r'id="surfCAPTCHA".*?name="csrf_token"\s+value="([^"]+)"', v, re.DOTALL)
            modal_csrf = m.group(1) if m else None
            m = re.search(r'id="surfCAPTCHA".*?id="uid"\s+value="([^"]*)"', v, re.DOTALL)
            modal_uid = m.group(1) if m else aid
            m = re.search(r'id="surfCAPTCHA".*?data-sitekey="([^"]+)"', v, re.DOTALL)
            modal_sitekey = m.group(1) if m else DEFAULT_TURNSTILE
            m = re.search(r'let count = (\d+);', v)
            count = int(m.group(1)) if m else dur

            if not modal_csrf:
                UI.warn("PTC", f"#{aid[:8]} no csrf")
                continue

            UI.info("PTC", f"view {count}s")
            UI.countdown(count, f"PTC {aid[:8]}")

            token = self.solve_turnstile(modal_sitekey, f"{HOST}/surf/{aid}")
            if not token: continue

            payload = {
                'csrf_token': modal_csrf,
                'cf-turnstile-response': token,
                'uid': modal_uid,
                'c': c_param,
            }
            UI.step("CLAIM", f"#{aid[:8]} submit")
            resp = self._req(f"{HOST}/ajax/surf", 'POST', data=payload,
                             referer=f"{HOST}/surf/{aid}", ajax=True)

            if resp and ('ptclinks' in resp or 'ptc-card' in resp or 'PTC -' in resp):
                UI.ok("PTC", f"#{aid[:8]} +{ad['coins']}c claimed")
                done += 1
            elif resp and 'Too early' in resp:
                UI.warn("PTC", f"#{aid[:8]} too early")
            else:
                UI.warn("PTC", f"#{aid[:8]} resp: {resp[:40] if resp else 'empty'}")

            time.sleep(random.uniform(2, 4))

        return done > 0

    # ═════════════════════════════════════════════════════════
    #  MAIN LOOP
    # ═════════════════════════════════════════════════════════
    def run(self, mode):
        os.system('cls' if os.name == 'nt' else 'clear')
        UI.banner()

        cfg = self.get_config()
        self.username = cfg.get('username', '').strip()
        self.password = cfg.get('password', '').strip()
        self.api_key = cfg.get('api_key', '').strip()

        if not self.username or not self.password:
            UI.err("CONFIG", "username/password kosong"); return
        if not self.api_key:
            print(UI.c("  Waryono API Key : ", "white"), end="")
            self.api_key = input().strip()
            cfg['api_key'] = self.api_key
            with open(CONFIG_FILE, 'w') as f:
                json.dump(cfg, f, indent=2)

        UI.set(user=self.username, solver="WARYONO", state="LOGIN", mode=mode)
        UI.start_panel()

        if not self.login():
            UI.err("AUTH", "login failed")
            UI.stop_panel(); return

        info = self.get_dashboard()
        if info:
            UI.set(balance=info.get('balance', '?'),
                   purchase=info.get('purchase_balance', '?'),
                   points=info.get('points', '?'))

        handlers = {"faucet": self.mode_faucet,
                    "ytvideos": self.mode_ytvideos,
                    "ptc": self.mode_ptc}
        handler = handlers.get(mode)
        if not handler:
            UI.err("MODE", f"unknown: {mode}")
            UI.stop_panel(); return

        cycle = 0
        while True:
            cycle += 1
            UI.set(cycle=cycle, state="RUNNING", phase="-")
            UI.info("CYCLE", f"Cycle #{cycle} [{mode}]")

            if not self.is_logged_in():
                UI.warn("AUTH", "session expired, re-login")
                if not self.login():
                    UI.err("AUTH", "re-login failed")
                    UI.countdown(60, "retry")
                    continue

            try:
                result = handler()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                UI.err("MODE", f"{type(e).__name__}: {str(e)[:40]}")
                result = 'error'

            if result == 'not_logged_in':
                UI.countdown(60, "retry"); continue
            if result in ('waited', 'already_claimed'):
                continue
            if result == 'no_task':
                delay = random.randint(60, 120)
                UI.warn("WAIT", f"no task, {delay}s")
                UI.countdown(delay, "idle")
                continue
            if result is True:
                info2 = self.get_dashboard()
                if info2:
                    UI.set(balance=info2.get('balance', '?'),
                           purchase=info2.get('purchase_balance', '?'),
                           points=info2.get('points', '?'))

            delay = random.randint(180, 300)
            UI.warn("WAIT", f"next cycle {delay}s")
            UI.countdown(delay, "next")


# ═════════════════════════════════════════════════════════════
#  ENTRY + SIGINT HANDLER
# ═════════════════════════════════════════════════════════════
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    UI.banner()
    while True:
        choice = show_menu()
        if choice == "0":
            print(UI.c("\n  bye boss 👋\n", "br_yellow")); return
        mode_map = {"1": "faucet", "2": "ytvideos", "3": "ptc"}
        mode = mode_map.get(choice)
        if not mode:
            print(UI.c("\n  ✖ invalid\n", "br_red"))
            time.sleep(1); os.system('cls' if os.name == 'nt' else 'clear'); UI.banner()
            continue
        try:
            FaucetPayzBot().run(mode)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            UI.stop_panel()
            print(f"\n{Fore.RED}  ✖ fatal: {e}{RESET}\n")
            import traceback; traceback.print_exc(); return


def _on_sigint(sig, frame):
    # restore default biar Ctrl+C kedua langsung kill
    try: signal.signal(signal.SIGINT, signal.SIG_DFL)
    except Exception: pass
    try: UI.stop_panel()
    except Exception: pass
    try:
        sys.stdout.write(f"\n{Fore.YELLOW}  ! CTRL+C — keluar dari script{RESET}\n")
        sys.stdout.write(f"{Fore.WHITE}  Re-run buat ganti mode: {Fore.CYAN}python bot.py{RESET}\n\n")
        sys.stdout.flush()
    except Exception: pass
    os._exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, _on_sigint)
    try:
        main()
    except KeyboardInterrupt:
        _on_sigint(signal.SIGINT, None)
