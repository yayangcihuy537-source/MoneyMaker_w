#!/usr/bin/env python3

import os
import sys
import json
import time
import random
import re
from datetime import datetime
from typing import Optional, Dict, List, Tuple

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


CONFIG_FILE  = "Btcadspace.json"
SESSION_FILE = "Btcadspace_session.json"

BASE_URL          = "https://btcadspace.com"
AVISO_API         = "https://aviso.bz/api/v1"
AVISO_API_KEY     = "ak_87e52f3d03d99fbb11505fc3ec24b881dddfb42e"
TURNSTILE_SITEKEY = "0x4AAAAAAAB-TZt_lwYtViEL"

BUXADS_ENDPOINT   = "http://37.60.224.60:7860/api"
SKIPCHA_ENDPOINT  = "https://skipcha.online"
SKIBIDIXXX_IN     = "https://api.waryono.my.id/in.php"
SKIBIDIXXX_RES    = "https://api.waryono.my.id/res.php"

TOOL_NAME = "BTCADSPACE"
DEVELOPER = "@MoneyMaker_w"
VERSION   = "v1.2.0"
TELEGRAM  = "t.me/ScriptyXSouu"
BOX_W     = 46


class C:
    X   = '\033[0m'
    B   = '\033[1m'
    D   = '\033[2m'
    G   = '\033[92m'
    DG  = '\033[32m'
    Y   = '\033[93m'
    R   = '\033[91m'
    C   = '\033[96m'
    W   = '\033[97m'
    O   = '\033[38;5;214m'
    GRY = '\033[90m'
    M   = '\033[95m'


# ═══════════════════════════════════════════════════════════
#  WIDE-CHAR + ANSI safe width
# ═══════════════════════════════════════════════════════════
_ANSI = re.compile(r'\x1b\[[0-9;]*m')


def _is_wide(cp: int) -> bool:
    return (
        0x1100 <= cp <= 0x115F or
        0x2329 <= cp <= 0x232A or
        0x2E80 <= cp <= 0x303E or
        0x3041 <= cp <= 0x33FF or
        0x3400 <= cp <= 0x4DBF or
        0x4E00 <= cp <= 0x9FFF or
        0xA000 <= cp <= 0xA4CF or
        0xAC00 <= cp <= 0xD7A3 or
        0xF900 <= cp <= 0xFAFF or
        0xFE30 <= cp <= 0xFE4F or
        0xFF00 <= cp <= 0xFF60 or
        0xFFE0 <= cp <= 0xFFE6 or
        0x1F300 <= cp <= 0x1F64F or
        0x1F680 <= cp <= 0x1F6FF or
        0x1F900 <= cp <= 0x1F9FF or
        0x1FA00 <= cp <= 0x1FAFF or
        0x2600  <= cp <= 0x27BF or
        0x2B00  <= cp <= 0x2BFF or
        0x1F000 <= cp <= 0x1F02F
    )


def vlen(s: str) -> int:
    s = _ANSI.sub('', s)
    w = 0
    for ch in s:
        w += 2 if _is_wide(ord(ch)) else 1
    return w


def pad(s, w, align='left'):
    vl = vlen(s)
    if vl > w:
        plain = _ANSI.sub('', s)
        acc = 0
        out = []
        for ch in plain:
            cw = 2 if _is_wide(ord(ch)) else 1
            if acc + cw > w - 3:
                break
            out.append(ch)
            acc += cw
        s = ''.join(out) + '...'
        vl = vlen(s)
    p = max(0, w - vl)
    if align == 'right':
        return ' ' * p + s
    if align == 'center':
        l = p // 2
        r = p - l
        return ' ' * l + s + ' ' * r
    return s + ' ' * p


# ═══════════════════════════════════════════════════════════
#  BOX RENDERERS
# ═══════════════════════════════════════════════════════════
def rbox_top(title='', w=BOX_W):
    if not title:
        return f"{C.C}╭{'─' * w}╮{C.X}"
    t = f" {C.C}{C.B}{title}{C.X} "
    rest = w - 1 - vlen(t)
    return f"{C.C}╭─{C.X}{t}{C.C}{'─' * max(0, rest)}╮{C.X}"


def rbox_mid(w=BOX_W):
    return f"{C.C}├{'─' * w}┤{C.X}"


def rbox_bot(w=BOX_W):
    return f"{C.C}╰{'─' * w}╯{C.X}"


def rbox_row(content, w=BOX_W):
    return f"{C.C}│{C.X}{pad('  ' + content, w)}{C.C}│{C.X}"


def rbox_row_center(content, w=BOX_W):
    return f"{C.C}│{C.X}{pad(content, w, 'center')}{C.C}│{C.X}"


def dbox_top(w=BOX_W):
    return f"{C.DG}╔{'═' * w}╗{C.X}"


def dbox_mid(w=BOX_W):
    return f"{C.DG}╠{'═' * w}╣{C.X}"


def dbox_bot(w=BOX_W):
    return f"{C.DG}╚{'═' * w}╝{C.X}"


def dbox_row(content, w=BOX_W):
    return f"{C.DG}║{C.X}{pad('  ' + content, w)}{C.DG}║{C.X}"


def dbox_row_center(content, w=BOX_W):
    return f"{C.DG}║{C.X}{pad(content, w, 'center')}{C.DG}║{C.X}"


# ═══════════════════════════════════════════════════════════
#  OUTPUT HELPERS
# ═══════════════════════════════════════════════════════════
def ok(msg):   print(f"  {C.G}✓{C.X} {msg}")
def err(msg):  print(f"  {C.R}✗{C.X} {msg}")
def info(msg): print(f"  {C.C}›{C.X} {msg}")
def dim(msg):  print(f"    {C.GRY}{msg}{C.X}")


def cooldown_display(sec):
    for i in range(sec, 0, -1):
        if not _RUNNING[0]:
            break
        h, rem = divmod(i, 3600)
        m, s = divmod(rem, 60)
        sys.stdout.write(
            f"\r  {C.Y}⏳ cooldown...{C.X}  "
            f"{C.B}{C.G}{h:02d}:{m:02d}:{s:02d}{C.X}     "
        )
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()


def auto_all_banner(cycle_no, mark="✅"):
    """Box banner khusus CLAIM ALL mode."""
    title    = "🚀 CLAIM ALL — AUTO EARN ENGINE"
    subtitle = "FAUCET • SURF • VIDEOS"
    task     = f"⚡ ALL TASK {cycle_no}"

    print()
    print(dbox_top())
    print(dbox_row_center(f"{C.G}{C.B}{title}{C.X}"))
    print(dbox_row_center(f"{C.GRY}{subtitle}{C.X}"))
    print(dbox_mid())
    # baris task: kiri "⚡ ALL TASK n", kanan "ALL TASK ✅"
    left  = f"{C.G}{C.B}{task}{C.X}"
    right = f"{C.G}ALL TASK {mark}{C.X}"
    gap = BOX_W - 2 - vlen(left) - vlen(right) - 4
    if gap < 2:
        gap = 2
    row = f"  {left}{' ' * gap}{C.W}➜{C.X}{' ' * 4}{right}"
    print(f"{C.DG}║{C.X}{pad(row, BOX_W)}{C.DG}║{C.X}")
    print(dbox_bot())
    print()


_RUNNING = [True]


# ═══════════════════════════════════════════════════════════
#  BANNER HEADER (untuk menu utama)
# ═══════════════════════════════════════════════════════════
def print_banner(status_active=False):
    status = (f"{C.G}{C.B}● ACTIVE{C.X}" if status_active
              else f"{C.Y}{C.B}○ IDLE{C.X}")

    print()
    print(dbox_top())
    print(dbox_row_center(f"{C.O}{C.B}⚡ AUTO CLAIM ENGINE ⚡{C.X}"))
    print(dbox_mid())
    print(dbox_row(f"{C.C}◆{C.X} Tool       : {C.O}{C.B}{TOOL_NAME}{C.X}"))
    print(dbox_row(f"{C.C}◆{C.X} Developer  : {C.M}{C.B}{DEVELOPER}{C.X}"))
    print(dbox_row(f"{C.C}◆{C.X} Version    : {C.W}{VERSION}{C.X}"))
    print(dbox_row(f"{C.C}◆{C.X} Status     : {status}"))
    print(dbox_row(f"{C.C}◆{C.X} Telegram   : {C.C}{TELEGRAM}{C.X}"))
    print(dbox_bot())
    print()
    print(f"  {C.G}{C.B}✓ Souu Engine Ready!{C.X}")
    print(f"  {C.DG}{'─' * BOX_W}{C.X}")
    print()


# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════
class Config:
    def __init__(self):
        self.data = {
            "username": "", "password": "",
            "captcha_provider": "", "captcha_api_key": "",
            "antibot_provider": "", "antibot_api_key": "",
        }
        self._load()

    def _load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE) as f:
                    self.data.update(json.load(f))
            except Exception:
                pass

    def save(self):
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception:
            pass

    def get(self, k, d=None): return self.data.get(k, d)
    def set(self, k, v): self.data[k] = v; self.save()


# ═══════════════════════════════════════════════════════════
#  TURNSTILE SOLVER
# ═══════════════════════════════════════════════════════════
class TurnstileSolver:
    def __init__(self, provider, api_key):
        self.provider = (provider or "").lower().strip()
        self.api_key  = api_key
        self.endpoint = {
            "buxads":     BUXADS_ENDPOINT,
            "skipcha":    SKIPCHA_ENDPOINT,
            "skibidixxx": SKIBIDIXXX_IN,
        }.get(self.provider, "")

    def solve(self, sitekey, pageurl):
        try:
            fn = {
                "buxads":     self._buxads,
                "skipcha":    self._skipcha,
                "skibidixxx": self._skibidixxx,
            }.get(self.provider)
            return fn(sitekey, pageurl) if fn else None
        except Exception:
            return None

    @staticmethod
    def _post(url, **kw):
        try:    return requests.post(url, timeout=kw.pop("timeout", 30),
                                    verify=False, **kw)
        except: return None

    @staticmethod
    def _get(url, **kw):
        try:    return requests.get(url, timeout=kw.pop("timeout", 30),
                                   verify=False, **kw)
        except: return None

    def _buxads(self, sitekey, pageurl):
        ep = self.endpoint
        dim(f"BuxAds endpoint: {ep}")
        headers = {"Content-Type": "application/json",
                   "Accept": "application/json"}

        create_variants = [
            {"apikey": self.api_key, "mode": "turnstile",
             "domain": pageurl, "siteKey": sitekey},
            {"apikey": self.api_key, "mode": "turnstile",
             "domain": pageurl, "sitekey": sitekey},
            {"key": self.api_key, "method": "turnstile",
             "domain": pageurl, "siteKey": sitekey, "json": "1"},
            {"clientKey": self.api_key, "task": {
                "type": "TurnstileTaskProxyless",
                "websiteURL": pageurl,
                "websiteKey": sitekey,
            }},
            {"apikey": self.api_key, "mode": "turnstile",
             "pageurl": pageurl, "sitekey": sitekey},
        ]

        job = None
        for idx, payload in enumerate(create_variants):
            try:
                r = self._post(ep, json=payload, headers=headers)
            except Exception as e:
                dim(f"variant {idx} exception: {e}")
                continue
            if not r:
                dim(f"variant {idx}: no response")
                continue
            try:
                body = r.json()
            except Exception:
                dim(f"variant {idx}: HTTP {r.status_code} non-JSON: {r.text[:120]}")
                continue

            dim(f"variant {idx}: HTTP {r.status_code} -> {str(body)[:150]}")

            job = (body.get("jobId") or body.get("taskId")
                   or body.get("id") or body.get("request"))
            if job:
                dim(f"BuxAds job: {job}")
                break

            errmsg = (body.get("errorDescription")
                      or body.get("error") or body.get("message"))
            if errmsg:
                dim(f"variant {idx} error: {errmsg}")
                continue

        if not job:
            err("BuxAds create failed — no jobId from any payload variant")
            return None

        poll_variants = [
            {"apikey": self.api_key, "action": "get", "id": job},
            {"key": self.api_key, "action": "get", "id": job, "json": "1"},
            {"clientKey": self.api_key, "taskId": job},
        ]

        for _ in range(30):
            time.sleep(3)
            d = None
            for payload in poll_variants:
                try:
                    r = self._post(ep, json=payload, headers=headers)
                except Exception:
                    continue
                if not r or r.status_code != 200:
                    continue
                try:
                    d = r.json()
                except Exception:
                    continue
                if d:
                    break

            if not d:
                sys.stdout.write(f"{C.D}.{C.X}"); sys.stdout.flush()
                continue

            status = d.get("status")
            if status is True or status == 1 or status == "ready":
                sol = d.get("solution") or {}
                token = (sol.get("token") or sol.get("gRecaptchaResponse")
                         or d.get("request"))
                if token and len(str(token)) > 20:
                    ok("Turnstile solved (BuxAds)")
                    return str(token)
                continue

            if d.get("errorId") not in (0, None) or d.get("error"):
                msg = d.get("errorDescription") or d.get("error")
                if msg and "not ready" in str(msg).lower():
                    sys.stdout.write(f"{C.D}.{C.X}"); sys.stdout.flush()
                    continue
                err(f"BuxAds: {msg}")
                return None

            sys.stdout.write(f"{C.D}.{C.X}"); sys.stdout.flush()

        err("BuxAds timeout")
        return None

    def _skipcha(self, sitekey, pageurl):
        r = self._get(f"{self.endpoint}/in.php",
                      params={"key": self.api_key, "method": "turnstile",
                              "sitekey": sitekey, "pageurl": pageurl, "json": 1})
        if not r: return None
        try: d = r.json()
        except: return None
        if d.get("status") != 1: return None
        tid = str(d["request"])
        for _ in range(30):
            time.sleep(5)
            r = self._get(f"{self.endpoint}/res.php",
                          params={"key": self.api_key, "action": "get",
                                  "id": tid, "json": 1})
            if not r: continue
            try: d = r.json()
            except: continue
            if d.get("status") == 1 and len(d.get("request", "")) > 20:
                return d["request"]
        return None

    def _skibidixxx(self, sitekey, pageurl):
        dim(f"Skibidixxx (waryono) submit...")
        try:
            r = self._post(SKIBIDIXXX_IN, json={
                "apikey":  self.api_key,
                "methods": "turnstile",
                "domain":  pageurl,
                "sitekey": sitekey,
                "json":    1,
            }, headers={"Content-Type": "application/json"})
        except Exception as e:
            err(f"Skibidixxx submit error: {e}")
            return None
        if not r: return None
        try:
            d = r.json()
        except Exception:
            err(f"Skibidixxx non-JSON: {r.text[:120]}")
            return None

        if d.get("status") != 1 or not d.get("request"):
            err(f"Skibidixxx submit rejected: {d}")
            return None

        tid = str(d["request"])
        dim(f"Skibidixxx task: {tid}")

        for _ in range(40):
            time.sleep(3)
            try:
                r = self._get(SKIBIDIXXX_RES,
                              params={"apikey": self.api_key,
                                      "id": tid, "action": "get", "json": 1})
            except Exception:
                continue
            if not r: continue
            body = r.text.strip()

            if body.startswith("OK|"):
                tok = body.split("|", 1)[1].strip()
                if tok and len(tok) > 20:
                    ok("Turnstile solved (Skibidixxx)")
                    return tok
                continue

            try:
                d = r.json()
            except Exception:
                continue

            status = d.get("status")
            req = str(d.get("request", ""))

            if status == 1 and req and len(req) > 20:
                ok("Turnstile solved (Skibidixxx)")
                return req

            if "CAPCHA_NOT_READY" in req or "NOT_READY" in req:
                sys.stdout.write(f"{C.D}.{C.X}"); sys.stdout.flush()
                continue

            if "ERROR" in req:
                err(f"Skibidixxx: {req}")
                return None

            sys.stdout.write(f"{C.D}.{C.X}"); sys.stdout.flush()

        err("Skibidixxx timeout")
        return None


# ═══════════════════════════════════════════════════════════
#  ANTIBOT SOLVER
# ═══════════════════════════════════════════════════════════
class AntiBotSolver:
    def __init__(self, provider, api_key):
        self.provider = (provider or "").lower().strip()
        self.api_key  = api_key
        self.endpoint = {
            "buxads":     BUXADS_ENDPOINT,
            "skipcha":    SKIPCHA_ENDPOINT,
            "skibidixxx": SKIBIDIXXX_IN,
        }.get(self.provider, "")

    def solve(self, main_b64, options, labels=None):
        try:
            fn = {
                "buxads":     self._buxads,
                "skipcha":    self._skipcha,
                "skibidixxx": self._skibidixxx,
            }.get(self.provider)
            return fn(main_b64, options, labels) if fn else None
        except Exception:
            return None

    @staticmethod
    def _post(url, **kw):
        try:    return requests.post(url, timeout=kw.pop("timeout", 60),
                                    verify=False, **kw)
        except: return None

    @staticmethod
    def _get(url, **kw):
        try:    return requests.get(url, timeout=kw.pop("timeout", 60),
                                   verify=False, **kw)
        except: return None

    def _buxads(self, main_b64, options, labels):
        ep = self.endpoint
        dim(f"BuxAds AB endpoint: {ep}")

        sub = {}
        for i, b64 in enumerate(options):
            k = labels[i] if labels and i < len(labels) else str(i + 1)
            sub[str(k)] = b64

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 VernuablePHP/1.0",
        }

        try:
            r = self._post(ep,
                           json={"key": self.api_key, "method": "antibot",
                                 "main": main_b64, "sub": sub, "json": "1"},
                           headers=headers)
        except Exception as e:
            err(f"BuxAds AB create error: {e}")
            return None

        if not r:
            err(f"BuxAds AB unreachable at {ep}")
            return None
        if r.status_code != 200:
            err(f"BuxAds AB create HTTP {r.status_code}: {r.text[:150]}")
            return None

        try:
            d = r.json()
        except Exception:
            err(f"BuxAds AB non-JSON: {r.text[:150]}")
            return None

        if d.get("status") != 1 and not (d.get("jobId") or d.get("taskId")):
            err(f"BuxAds AB submit rejected: {d}")
            return None

        tid = d.get("request") or d.get("jobId") or d.get("taskId")
        dim(f"BuxAds AB task: {tid}")

        for _ in range(40):
            time.sleep(2)
            try:
                r = self._post(ep,
                               json={"key": self.api_key, "action": "get",
                                     "id": tid, "json": "1"},
                               headers=headers)
            except Exception:
                continue
            if not r or r.status_code != 200:
                continue
            try:
                d = r.json()
            except Exception:
                continue

            if d.get("status") == 1:
                ans = str(d.get("request", "")).strip()
                if ans:
                    ok(f"AntiBot answer: {ans}")
                    return ans

            req = str(d.get("request", ""))
            if "NOT_READY" in req or "PROCESSING" in req:
                sys.stdout.write(f"{C.D}.{C.X}"); sys.stdout.flush()
                continue

            if d.get("status") == 0 and req and req != "CAPCHA_NOT_READY":
                err(f"BuxAds AB: {req}")
                return None

            sys.stdout.write(f"{C.D}.{C.X}"); sys.stdout.flush()

        err("BuxAds AB timeout")
        return None

    def _skipcha(self, main_b64, options, labels=None):
        r = self._post(f"{self.endpoint}/in.php",
                       params={"key": self.api_key, "method": "antibot", "json": 1},
                       json={"main": main_b64, "options": options})
        if not r: return None
        try: d = r.json()
        except: return None
        tid = d.get("request")
        if not tid: return None
        for _ in range(30):
            time.sleep(3)
            r = self._get(f"{self.endpoint}/res.php",
                          params={"key": self.api_key, "action": "get",
                                  "id": tid, "json": 1})
            if not r: continue
            try: d = r.json()
            except: continue
            if d.get("status") == 1 and d.get("request"):
                return str(d["request"]).strip()
        return None

    def _skibidixxx(self, main_b64, options, labels=None):
        dim(f"Skibidixxx (waryono) AB submit...")
        try:
            r = self._post(SKIBIDIXXX_IN, json={
                "apikey":  self.api_key,
                "methods": "antibot",
                "main":    main_b64,
                "json":    1,
            }, headers={"Content-Type": "application/json"})
        except Exception as e:
            err(f"Skibidixxx AB error: {e}")
            return None
        if not r: return None
        try:
            d = r.json()
        except Exception:
            err(f"Skibidixxx AB non-JSON: {r.text[:120]}")
            return None

        if d.get("status") != 1 or not d.get("request"):
            err(f"Skibidixxx AB rejected: {d}")
            return None

        tid = str(d["request"])
        dim(f"Skibidixxx AB task: {tid}")

        for _ in range(40):
            time.sleep(3)
            try:
                r = self._get(SKIBIDIXXX_RES,
                              params={"apikey": self.api_key,
                                      "id": tid, "action": "get", "json": 1})
            except Exception:
                continue
            if not r: continue
            body = r.text.strip()

            if body.startswith("OK|"):
                ans = body.split("|", 1)[1].strip()
                if ans:
                    ok(f"AntiBot answer: {ans}")
                    return ans
                continue

            try:
                d = r.json()
            except Exception:
                continue

            status = d.get("status")
            req = str(d.get("request", ""))

            if status == 1 and req:
                ok(f"AntiBot answer: {req}")
                return req

            if "CAPCHA_NOT_READY" in req or "NOT_READY" in req:
                sys.stdout.write(f"{C.D}.{C.X}"); sys.stdout.flush()
                continue

            if "ERROR" in req:
                err(f"Skibidixxx AB: {req}")
                return None

            sys.stdout.write(f"{C.D}.{C.X}"); sys.stdout.flush()

        err("Skibidixxx AB timeout")
        return None


# ═══════════════════════════════════════════════════════════
#  BOT
# ═══════════════════════════════════════════════════════════
class BTCadSpaceBot:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.session = requests.Session()
        self.session.verify = False
        self.session.timeout = 30

        self.username = cfg.get("username", "")
        self.password = cfg.get("password", "")
        self.logged_in = False
        self.csrf_token = None
        self.user_hash = None

        self.total_coins = 0
        self.faucet_claims = 0
        self.surf_claims = 0
        self.video_claims = 0
        self.running = True
        _RUNNING[0] = True

        self.turnstile_solver = None
        self.antibot_solver = None
        self._build_solvers()
        self._load_session()

    def _build_solvers(self):
        prov = self.cfg.get("captcha_provider", "")
        key  = self.cfg.get("captcha_api_key", "")
        self.turnstile_solver = TurnstileSolver(prov, key) if prov else None
        ab_prov = self.cfg.get("antibot_provider", "") or prov
        ab_key  = self.cfg.get("antibot_api_key", "") or key
        self.antibot_solver = AntiBotSolver(ab_prov, ab_key) if ab_prov else None

    def _load_session(self):
        if os.path.exists(SESSION_FILE):
            try:
                with open(SESSION_FILE) as f:
                    d = json.load(f)
                for n, v in d.get("cookies", {}).items():
                    self.session.cookies.set(n, v)
                self.username = d.get("username", self.username)
                self.password = d.get("password", self.password)
                self.user_hash = d.get("user_hash")
            except Exception:
                pass

    def _save_session(self):
        try:
            cookies = {c.name: c.value for c in self.session.cookies}
            with open(SESSION_FILE, "w") as f:
                json.dump({"username": self.username, "password": self.password,
                           "cookies": cookies, "user_hash": self.user_hash},
                          f, indent=2)
        except Exception:
            pass

    def _headers(self, referer=None, ajax=False):
        h = {
            'Accept': '*/*' if ajax else
                       'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-PH,en-US;q=0.9,en;q=0.8',
            'User-Agent': ('Mozilla/5.0 (Linux; Android 15; CPH2505 Build/UKQ1.230924.001) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 '
                           'Mobile Safari/537.36'),
            'X-Requested-With': 'XMLHttpRequest' if ajax else 'mark.via.gp',
            'Sec-Ch-Ua': '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors' if ajax else 'navigate',
            'Sec-Fetch-User': '?1',
            'Sec-Fetch-Dest': 'empty' if ajax else 'document',
            'Referer': referer or BASE_URL,
            'Origin':  BASE_URL,
        }
        if ajax:
            h['Content-Type'] = 'application/x-www-form-urlencoded'
        return h

    def _aviso_headers(self):
        return {
            'Accept': '*/*', 'Accept-Language': 'en',
            'Content-Type': 'application/json',
            'Origin': BASE_URL, 'Referer': BASE_URL,
            'User-Agent': ('Mozilla/5.0 (Linux; Android 15; CPH2505 Build/UKQ1.230924.001) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 '
                           'Mobile Safari/537.36'),
            'X-Api-Key': AVISO_API_KEY,
            'X-Requested-With': 'mark.via.gp',
            'Sec-Ch-Ua': '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
            'Sec-Ch-Ua-Mobile': '?1',
            'Sec-Ch-Ua-Platform': '"Android"',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
        }

    @staticmethod
    def _csrf(html):
        for pat in [r'name="csrf_token"\s+value="([^"]+)"',
                    r'<meta\s+name="csrf-token"\s+content="([^"]+)"']:
            m = re.search(pat, html)
            if m: return m.group(1)
        return None

    @staticmethod
    def _user_hash(html):
        for pat in [r'data-user-hash="([a-f0-9]{64})"',
                    r'user_hash["\']?\s*[:=]\s*["\']([a-f0-9]{64})',
                    r'ext_user_id["\']?\s*[:=]\s*["\']([a-f0-9]{32,64})']:
            m = re.search(pat, html)
            if m: return m.group(1)
        return None

    @staticmethod
    def _sitekey(html):
        for pat in [r'data-sitekey="([^"]+)"',
                    r'sitekey["\']?\s*[:=]\s*["\']([^"\']+)']:
            m = re.search(pat, html)
            if m: return m.group(1)
        return None

    def fetch_balance(self) -> int:
        try:
            r = self.session.get(f"{BASE_URL}/account",
                                 headers=self._headers(f"{BASE_URL}/login"),
                                 timeout=15)
            if r.status_code != 200:
                return -1
            html = r.text

            m = re.search(r'<span\s+id="balance"[^>]*>\s*([\d,]+)\s*Coins?\s*</span>',
                          html, re.IGNORECASE)
            if not m:
                m = re.search(r'id="balance"[^>]*>\s*([\d,]+)', html, re.IGNORECASE)
            if not m:
                m = re.search(r'Main Balance.*?([\d,]+)\s*Coins?',
                              html, re.DOTALL | re.IGNORECASE)

            if m:
                val = m.group(1).replace(",", "").strip()
                try:
                    return int(val)
                except ValueError:
                    return -1
            return -1
        except Exception:
            return -1

    def refresh_balance(self, quiet=False) -> int:
        b = self.fetch_balance()
        if b >= 0:
            old = self.total_coins
            self.total_coins = b
            if not quiet and old != b:
                dim(f"balance: {old} → {b}")
            return b
        return self.total_coins

    def login(self, username=None, password=None) -> bool:
        if username: self.username = username
        if password: self.password = password
        if not self.username or not self.password: return False

        try:
            url = f"{BASE_URL}/login"
            r = self.session.get(url, headers=self._headers(), timeout=15)
            if r.status_code != 200: return False

            html = r.text
            self.csrf_token = self._csrf(html)
            if not self.csrf_token: return False

            sitekey = self._sitekey(html) or TURNSTILE_SITEKEY
            token = (self.turnstile_solver.solve(sitekey, url)
                     if self.turnstile_solver else None)
            if not token:
                err("captcha fail")
                return False

            data = {"csrf_token": self.csrf_token, "username": self.username,
                    "password": self.password, "2fa": "", "remember": "1",
                    "cf-turnstile-response": token}
            r = self.session.post(url, data=data, headers=self._headers(url),
                                  timeout=20, allow_redirects=True)

            if "/account" in r.url or "logout" in r.text.lower():
                ok("login OK")
                self.logged_in = True
                self.user_hash = self._user_hash(r.text) or self.user_hash
                self._save_session()
                return True
            if r.status_code == 302 and "/account" in r.headers.get("Location", ""):
                ok("login OK")
                self.logged_in = True
                self._save_session()
                return True
            err("login fail")
            return False
        except Exception:
            return False

    def check_login(self):
        try:
            r = self.session.get(f"{BASE_URL}/account",
                                 headers=self._headers(f"{BASE_URL}/login"),
                                 timeout=15)
            if r.status_code == 200 and "/login" not in r.url:
                self.logged_in = True
                self.user_hash = self._user_hash(r.text) or self.user_hash
                return True
            return False
        except Exception:
            return False

    @staticmethod
    def _ablinks_from_js(html):
        main_b64 = None
        m = re.search(
            r'class="alert\s+alert-warning"[^>]*>.*?'
            r'<img\s+src="data:image/[^;]+;base64,([^"]+)"',
            html, re.DOTALL)
        if m: main_b64 = m.group(1)

        m = re.search(r'var\s+ablinks\s*=\s*(\[.*?\])\s*;', html, re.DOTALL)
        if not m: m = re.search(r'var\s+ablinks\s*=\s*(\[.*?\])', html, re.DOTALL)
        if not m: return main_b64, [], []

        js = m.group(1).replace('\\"', '"').replace('\\/', '/')
        entries = re.findall(
            r'rel="(\d+)"[^>]*>\s*<img\s+src="data:image/[^;]+;base64,([^"]+)"',
            js, re.DOTALL)
        if not entries:
            entries = re.findall(
                r'rel="(\d+)"[^>]*data:image/[^;]+;base64,([^"]+)',
                js, re.DOTALL)
        if not entries:
            rels = re.findall(r'rel="(\d+)"', js)
            b64s = re.findall(r'data:image/[^;]+;base64,([^"]+)', js)
            if rels and len(rels) == len(b64s):
                entries = list(zip(rels, b64s))
        return main_b64, [e[1] for e in entries], [e[0] for e in entries]

    def claim_faucet(self) -> bool:
        try:
            url = f"{BASE_URL}/faucet"
            r = self.session.get(url, headers=self._headers(f"{BASE_URL}/account"),
                                 timeout=15)
            if r.status_code != 200: return False

            html = r.text
            csrf = self._csrf(html)
            if not csrf: return False
            sitekey = self._sitekey(html) or TURNSTILE_SITEKEY

            main_b64, options, rel_ids = self._ablinks_from_js(html)
            if not options: return False
            if not main_b64: main_b64 = options[0]
            if len(options) > 4:
                options, rel_ids = options[:4], rel_ids[:4]

            ans = (self.antibot_solver.solve(main_b64, options, rel_ids)
                   if self.antibot_solver else None)
            if not ans:
                err("antibot fail")
                return False

            tokens = re.findall(r"\d+", ans)
            n = len(rel_ids)
            is_idx = all(0 <= int(t) <= n for t in tokens) and rel_ids

            if is_idx:
                zero_based = ("0" in tokens) or (max(int(t) for t in tokens) < n)
                ordered = []
                for t in tokens:
                    i = int(t)
                    if zero_based and 0 <= i < n: ordered.append(rel_ids[i])
                    elif not zero_based and 1 <= i <= n: ordered.append(rel_ids[i - 1])
                antibotlinks = " " + " ".join(ordered if len(ordered) == n else tokens)
            else:
                antibotlinks = " " + " ".join(tokens)

            token = (self.turnstile_solver.solve(sitekey, url)
                     if self.turnstile_solver else None)
            if not token:
                err("captcha fail")
                return False

            data = {"csrf_token": csrf, "antibotlinks": antibotlinks,
                    "cf-turnstile-response": token}
            r = self.session.post(url, data=data, headers=self._headers(url),
                                  timeout=20, allow_redirects=True)

            body = r.text.lower()
            if r.status_code in (200, 302):
                if ("has been added to your balance" in body
                        or "'success'" in r.text
                        or (r.status_code == 302 and "/faucet" in r.headers.get("location", ""))):
                    self.faucet_claims += 1
                    self.refresh_balance(quiet=True)
                    ok(f"[faucet] +5 coins  →  balance {self.total_coins}")
                    return True
                for kw in ("error", "invalid", "too early", "captcha failed", "wrong"):
                    if kw in body:
                        err(f"faucet: {kw}")
                        return False
            return False
        except Exception:
            return False

    def get_surf_ads(self):
        try:
            r = self.session.get(f"{BASE_URL}/surf",
                                 headers=self._headers(f"{BASE_URL}/account"),
                                 timeout=15)
            if r.status_code != 200:
                return []
            html = r.text
            self.csrf_token = self._csrf(html) or self.csrf_token

            ads = []

            card_pat = re.compile(
                r'<a\s+href="/surf/([a-f0-9]{32})"([^>]*)>\s*'
                r'.*?<span class="fw-bold">([^<]+)</span>\s*'
                r'.*?<span><i class="far fa-coins"></i>\s*(\d+)\s*Coins</span>\s*'
                r'.*?<span class="float-end"><i class="far fa-stopwatch"></i>\s*(\d+)\s*seconds</span>',
                re.DOTALL
            )
            for m in card_pat.finditer(html):
                uid, attrs, title, coins, dur = m.groups()
                if 'd-none' in attrs:
                    continue
                ads.append({
                    "uid": uid,
                    "title": title.strip(),
                    "coins": int(coins),
                    "duration": int(dur),
                })

            if not ads:
                alt_pat = re.compile(
                    r'href="/surf/([a-f0-9]{32})"[^>]*>\s*'
                    r'.*?<span class="fw-bold">([^<]+)</span>\s*'
                    r'.*?<span><i class="far fa-coins"></i>\s*(\d+)\s*Coins</span>\s*'
                    r'.*?<span class="float-end"><i class="far fa-stopwatch"></i>\s*(\d+)\s*seconds</span>',
                    re.DOTALL
                )
                for m in alt_pat.finditer(html):
                    uid, title, coins, dur = m.groups()
                    lookback = html[max(0, m.start() - 400):m.start() + 50]
                    a_match = re.search(
                        rf'<a\s+href="/surf/{uid}"([^>]*)>', lookback)
                    if a_match and 'd-none' in a_match.group(1):
                        continue
                    ads.append({
                        "uid": uid,
                        "title": title.strip(),
                        "coins": int(coins),
                        "duration": int(dur),
                    })

            return ads
        except Exception:
            return []

    def claim_surf_ad(self, ad) -> bool:
        try:
            uid, coins, duration = ad["uid"], ad["coins"], ad["duration"]

            try:
                r = self.session.get(f"{BASE_URL}/surf",
                                     headers=self._headers(f"{BASE_URL}/account"),
                                     timeout=10)
                if r.status_code == 200:
                    m_anchor = re.search(
                        rf'<a\s+href="/surf/{uid}"([^>]*)>', r.text)
                    if not m_anchor:
                        return False
                    if 'd-none' in m_anchor.group(1):
                        return False
            except Exception:
                pass

            url = f"{BASE_URL}/surf/{uid}"
            r = self.session.get(url, headers=self._headers(f"{BASE_URL}/surf"),
                                 timeout=15)
            if r.status_code != 200: return False
            html = r.text
            csrf = self._csrf(html) or self.csrf_token

            btn = (re.search(r'<button\s+id="([a-f0-9]+)"\s+class="btn btn-primary start-btn"', html)
                   or re.search(r'id="([a-f0-9]+)"[^>]*class="[^"]*start-btn', html))
            if not btn: return False
            start_token = btn.group(1)

            id_m = re.search(r"let id = '([a-f0-9]+)';", html)
            cnt_m = re.search(r"let count = (\d+);", html)
            ad_id = id_m.group(1) if id_m else start_token
            count = int(cnt_m.group(1)) if cnt_m else duration

            c_param = ad_id + str(random.randint(1, 9999))
            self.session.get(f"{BASE_URL}/surf/{uid}/{c_param}",
                             headers=self._headers(url),
                             timeout=15, allow_redirects=False)

            cooldown_display(count)

            r = self.session.get(url, headers=self._headers(f"{BASE_URL}/surf"),
                                 timeout=15)
            html = r.text
            csrf = self._csrf(html) or csrf
            sitekey = self._sitekey(html) or TURNSTILE_SITEKEY

            token = (self.turnstile_solver.solve(sitekey, url)
                     if self.turnstile_solver else None)
            if not token:
                err("captcha fail")
                return False

            payload = {"csrf_token": csrf, "uid": uid, "c": c_param,
                       "cf-turnstile-response": token}
            r = self.session.post(f"{BASE_URL}/ajax/surf", data=payload,
                                  headers=self._headers(url, ajax=True), timeout=20)
            if r.status_code == 200:
                try: d = r.json()
                except: return False
                if d.get("success"):
                    self.surf_claims += 1
                    self.refresh_balance(quiet=True)
                    ok(f"[surf] +{coins} coins  →  balance {self.total_coins}")
                    return True
            return False
        except Exception:
            return False

    def auto_surf(self):
        print()
        print(rbox_top("SURF ADS"))
        ads = self.get_surf_ads()
        if not ads:
            print(rbox_row(f"{C.Y}! no surf ads available — skipping{C.X}"))
            print(rbox_bot())
            return

        print(rbox_row(f"{C.C}›{C.X} found {C.B}{len(ads)}{C.X} available ads"))
        print(rbox_bot())

        wins = fails = 0
        for i, ad in enumerate(ads, 1):
            if not self.running:
                break
            print(f"\n{C.DG}┌─ {C.G}AD {i}/{len(ads)}{C.X} "
                  f"{C.GRY}—{C.X} {C.G}{ad['title']}{C.X} "
                  f"({C.O}{ad['coins']} coins{C.X} / {ad['duration']}s)"
                  f" {C.DG}─┐{C.X}")
            if self.claim_surf_ad(ad):
                wins += 1
            else:
                fails += 1
            if i < len(ads):
                time.sleep(2)
        print()
        print(f"  {C.G}✓ success: {wins}{C.X}   {C.R}✗ fail: {fails}{C.X}")

    def _aviso_identify(self):
        if not self.user_hash:
            try:
                r = self.session.get(f"{BASE_URL}/ytvideos",
                                     headers=self._headers(f"{BASE_URL}/surf"),
                                     timeout=15)
                self.user_hash = self._user_hash(r.text) or self.user_hash
            except Exception:
                pass
        if not self.user_hash: return None

        payload = {
            "hash": self.user_hash, "ip": None,
            "userAgent": ("Mozilla/5.0 (Linux; Android 15; CPH2505 Build/UKQ1.230924.001) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 "
                          "Mobile Safari/537.36"),
            "fingerprint": {
                "fp": "8661a494702c33f967373004765326f5",
                "hashFont": "2f48d5374924fd0ce9bb54863fb00708",
                "langs": "en-PH, en-US", "timezone": "Asia/Manila",
                "platform": "Linux aarch64", "gpu": "Qualcomm~Adreno (TM) 619",
                "screen": "360x804", "memory": 8, "cpuCores": 8,
            },
        }
        r = requests.post(f"{AVISO_API}/youtube/tasks/identify", json=payload,
                          headers=self._aviso_headers(), timeout=15, verify=False)
        try: return r.json().get("id") if r.status_code == 200 else None
        except: return None

    def _aviso_tasks_page(self, offset=0, limit=100):
        r = requests.get(f"{AVISO_API}/youtube/tasks/available",
                         params={"hash": self.user_hash, "platform": "Linux aarch64",
                                 "offset": offset, "limit": limit},
                         headers=self._aviso_headers(), timeout=20, verify=False)
        try: return r.json() if r.status_code == 200 else None
        except: return None

    def _aviso_start(self, task_id, task_type):
        r = requests.post(f"{AVISO_API}/youtube/tasks/start",
                          json={"taskId": task_id, "hash": self.user_hash,
                                "type": task_type, "platform": "Linux aarch64"},
                          headers=self._aviso_headers(), timeout=15, verify=False)
        try: return r.json() if r.status_code == 200 else None
        except: return None

    def _aviso_timer(self, attempt_id, action, watched=None):
        p = {"attemptId": attempt_id, "action": action}
        if watched is not None: p["watchedTime"] = watched
        r = requests.post(f"{AVISO_API}/youtube/tasks/timer-status", json=p,
                          headers=self._aviso_headers(), timeout=15, verify=False)
        try: return r.json() if r.status_code == 200 else None
        except: return None

    def _aviso_complete(self, attempt_id):
        r = requests.post(f"{AVISO_API}/youtube/tasks/complete",
                          json={"attemptId": attempt_id},
                          headers=self._aviso_headers(), timeout=15, verify=False)
        try: return r.json() if r.status_code == 200 else None
        except: return None

    def claim_video(self, task) -> bool:
        if task.get("inProgress"):
            return False

        tid = task["id"]; ttype = task["type"]
        duration = int(task.get("duration", 10)) if ttype == "ads" else 5

        start = self._aviso_start(tid, ttype)
        if not start: return False
        aid = start.get("attemptId")
        if not aid: return False
        if start.get("duration"): duration = int(start["duration"])

        url = start.get("url")
        if url:
            try: self.session.get(url, headers=self._headers(), timeout=15)
            except: pass

        t = self._aviso_timer(aid, "start")
        if not t: return False

        if t.get("status") == "need_check":
            cooldown_display(duration)
            comp = self._aviso_timer(aid, "complete", duration)
            if not comp or not comp.get("verified"): return False
            chk = self._aviso_timer(aid, "check")
            if not chk or not chk.get("viewExists"): return False
            fin = self._aviso_complete(aid)
            if fin:
                earned = fin.get("earned", 0)
                usdt = float(earned)
                self.video_claims += 1
                self.refresh_balance(quiet=True)
                ok(f"[{ttype}] +{usdt:.5f} USDT  →  balance {self.total_coins}")
                return True
            return False

        if ttype in ("like", "sub"):
            time.sleep(3)
            chk = self._aviso_timer(aid, "check")
            if chk and chk.get("viewExists"):
                fin = self._aviso_complete(aid)
                if fin:
                    earned = fin.get("earned", 0)
                    usdt = float(earned)
                    self.video_claims += 1
                    self.refresh_balance(quiet=True)
                    ok(f"[{ttype}] +{usdt:.5f} USDT  →  balance {self.total_coins}")
                    return True
        return False

    def auto_videos(self):
        print()
        print(rbox_top("YOUTUBE VIDEOS"))
        if not self._aviso_identify():
            print(rbox_row(f"{C.R}! aviso identify failed{C.X}"))
            print(rbox_bot())
            return
        print(rbox_bot())

        seen = set()
        wins = fails = 0
        batch_no = 0
        stale_rounds = 0
        MAX_STALE = 2

        while self.running:
            batch_no += 1
            data = self._aviso_tasks_page(offset=0, limit=100)
            if not data:
                break

            page_tasks = []
            for t in ("ads", "like", "sub"):
                for task in data.get(t, []):
                    tid = task.get("id")
                    if tid in seen:
                        continue
                    if task.get("inProgress", False):
                        seen.add(tid)
                        continue
                    task["type"] = t
                    page_tasks.append(task)

            if not page_tasks:
                stale_rounds += 1
                if stale_rounds >= MAX_STALE:
                    break
                time.sleep(3)
                continue

            stale_rounds = 0
            print(f"  {C.C}›{C.X} batch {C.B}{batch_no}{C.X}: "
                  f"{C.B}{len(page_tasks)}{C.X} available tasks")

            for i, task in enumerate(page_tasks, 1):
                if not self.running:
                    break
                seen.add(task["id"])
                print(f"\n{C.DG}┌─ {C.G}TASK {i}/{len(page_tasks)}{C.X} "
                      f"{C.GRY}[{task['type']}]{C.X} {C.DG}─┐{C.X}")
                if self.claim_video(task):
                    wins += 1
                else:
                    fails += 1
                if i < len(page_tasks):
                    time.sleep(2)

        if wins == 0 and fails == 0:
            err("no youtube tasks available")
        print()
        print(f"  {C.G}✓ success: {wins}{C.X}   {C.R}✗ fail: {fails}{C.X}")

    def auto_all(self):
        cycle_no = 0
        while self.running:
            try:
                cycle_no += 1
                auto_all_banner(cycle_no)

                if not self.check_login():
                    ok("session expired, re-login")
                    if not self.login(): break

                self.claim_faucet()
                self.auto_surf()
                self.auto_videos()

                self.refresh_balance(quiet=True)

                # summary box
                print()
                print(rbox_top("CYCLE SUMMARY"))
                print(rbox_row(f"{C.W}faucet{C.X} : {C.G}{self.faucet_claims}{C.X}"))
                print(rbox_row(f"{C.W}surf  {C.X} : {C.G}{self.surf_claims}{C.X}"))
                print(rbox_row(f"{C.W}video {C.X} : {C.G}{self.video_claims}{C.X}"))
                print(rbox_row(f"{C.W}coins {C.X} : {C.O}{C.B}{self.total_coins}{C.X}"))
                print(rbox_bot())

                cooldown_display(300)
            except KeyboardInterrupt:
                break
            except Exception:
                time.sleep(10)

    def header(self):
        print_banner(status_active=self.logged_in)
        if self.logged_in:
            self.refresh_balance(quiet=True)

        print(rbox_top("ACCOUNT"))
        print(rbox_row(f"{C.W}Accounts Loaded{C.X} : "
                       f"{C.C}{C.B}{1 if self.username else 0}{C.X}"))
        print(rbox_row(f"{C.W}Username        {C.X} : "
                       f"{C.C}{(self.username or '(belum login)')[:30]}{C.X}"))
        print(rbox_row(f"{C.W}Balance         {C.X} : "
                       f"{C.O}{C.B}{self.total_coins} COINS{C.X}"))
        print(rbox_row(f"{C.W}Solver          {C.X} : "
                       f"{C.Y}{self.cfg.get('captcha_provider') or '(belum diset)'}{C.X}"))
        print(rbox_bot())
        print()

    def menu(self):
        items = [
            ("1", "Start Farming"),
            ("2", "Config Email"),
            ("3", "Config Apikey"),
            ("4", "Exit"),
        ]
        print(rbox_top("MENU"))
        for k, label in items:
            print(rbox_row(f"{C.G}[{k}]{C.X} {label}"))
        print(rbox_bot())
        print()

    def config_email(self):
        print()
        print(rbox_top("CONFIG EMAIL"))
        cur_u = self.cfg.get("username", "")
        u = input(f"  {C.C}username{C.X} [{cur_u}]: ").strip()
        if u:
            self.cfg.set("username", u); self.username = u
        elif cur_u:
            self.username = cur_u

        cur_p = self.cfg.get("password", "")
        shown = '*' * len(cur_p) if cur_p else ''
        p = input(f"  {C.C}password{C.X} [{shown}]: ").strip()
        if p:
            self.cfg.set("password", p); self.password = p

        self.cfg.save()
        print(rbox_bot())
        ok("email saved")
        print()

    def config_apikey(self):
        print()
        print(rbox_top("CONFIG APIKEY"))
        print(rbox_row(f"{C.G}1){C.X} buxads   "
                       f"{C.G}2){C.X} skipcha   {C.G}3){C.X} skibidixxx"))
        cur = self.cfg.get("captcha_provider", "")
        print(rbox_row(f"{C.W}current{C.X} : {C.Y}{cur or '-'}{C.X}"))
        print(rbox_bot())
        ch = input(f"  {C.C}provider{C.X} [1-3, enter=keep]: ").strip()
        pmap = {"1": "buxads", "2": "skipcha", "3": "skibidixxx"}
        if ch in pmap:
            self.cfg.set("captcha_provider", pmap[ch])

        prov = self.cfg.get("captcha_provider")
        if prov:
            cur_key = self.cfg.get("captcha_api_key", "")
            shown = '*' * 8 if cur_key else 'empty'
            v = input(f"  {C.C}api key{C.X} [{shown}]: ").strip()
            if v:
                self.cfg.set("captcha_api_key", v)

        self.cfg.save()
        self._build_solvers()
        ok("apikey saved")
        print()

    def show_stats(self):
        print()
        print(rbox_top("STATS"))
        if self.logged_in:
            self.refresh_balance(quiet=True)
        print(rbox_row(f"{C.W}user     {C.X}: {self.username}"))
        print(rbox_row(f"{C.W}logged in{C.X}: "
                       f"{'yes' if self.logged_in else 'no'}"))
        print(rbox_row(f"{C.W}turnstile{C.X}: "
                       f"{self.cfg.get('captcha_provider') or '-'}"))
        print(rbox_row(f"{C.W}antibot  {C.X}: "
                       f"{self.cfg.get('antibot_provider') or self.cfg.get('captcha_provider') or '-'}"))
        print(rbox_row(f"{C.W}faucet   {C.X}: {self.faucet_claims}"))
        print(rbox_row(f"{C.W}surf     {C.X}: {self.surf_claims}"))
        print(rbox_row(f"{C.W}video    {C.X}: {self.video_claims}"))
        print(rbox_row(f"{C.W}coins    {C.X}: {C.O}{self.total_coins}{C.X}"))
        print(rbox_bot())
        print()

    def run(self):
        os.system('clear' if os.name != 'nt' else 'cls')
        self.header()

        if self.username and self.password:
            print(f"{C.D}[auto-login]{C.X}")
            if self.login():
                self.refresh_balance(quiet=True)
                os.system('clear' if os.name != 'nt' else 'cls')
                self.header()
            else:
                print(f"  {C.Y}auto-login failed{C.X}")

        if not self.cfg.get("captcha_provider"):
            print(f"  {C.Y}! solver belum diset — menu 3 untuk setup{C.X}")
            print()
        if not self.username:
            print(f"  {C.Y}! email belum diset — menu 2 untuk setup{C.X}")
            print()

        while self.running:
            self.menu()
            try:
                ch = input(f"{C.G}choose:{C.X} ").strip()

                if ch == "4" or ch == "0":
                    self.running = False
                    _RUNNING[0] = False
                    print(f"\n  {C.G}bye 👋{C.X}")
                    break
                elif ch == "1":
                    if not self.username or not self.cfg.get("captcha_provider"):
                        err("setup dulu — menu 2 (email) & menu 3 (apikey)")
                        continue
                    if not self.logged_in and not self.login():
                        continue
                    self.auto_all()
                    os.system('clear' if os.name != 'nt' else 'cls')
                    self.header()
                elif ch == "2":
                    self.config_email()
                    os.system('clear' if os.name != 'nt' else 'cls')
                    self.header()
                elif ch == "3":
                    self.config_apikey()
                    os.system('clear' if os.name != 'nt' else 'cls')
                    self.header()
                else:
                    print(f"  {C.R}invalid{C.X}")
            except KeyboardInterrupt:
                self.running = False
                _RUNNING[0] = False
                print(f"\n  {C.G}bye 👋{C.X}")
                break
            except Exception:
                time.sleep(1)


def main():
    cfg = Config()
    bot = BTCadSpaceBot(cfg)
    try:
        bot.run()
    except KeyboardInterrupt:
        print(f"\n  {C.G}stopped{C.X}")
    except Exception as e:
        print(f"{C.R}fatal: {e}{C.X}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

