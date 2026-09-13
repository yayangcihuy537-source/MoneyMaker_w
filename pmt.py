#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║     💜 PMT GRAM • AUTOFARM — HACKED EDITION 💜                  ║
║                                                                   ║
║   🎯 Smart Captcha Detection · Turnstile · hCaptcha · reCaptcha  ║
║   👑 ScriptMaker: MoneyMaker_w                                    ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import random
import requests
import hashlib
import re
import threading
from urllib.parse import unquote, parse_qs
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
#  WARNA
# ═══════════════════════════════════════════════════════════════
class C:
    RED      = "\033[91m"
    GREEN    = "\033[92m"
    YELLOW   = "\033[93m"
    BLUE     = "\033[94m"
    MAGENTA  = "\033[95m"
    CYAN     = "\033[96m"
    WHITE    = "\033[97m"
    BOLD     = "\033[1m"
    DIM      = "\033[2m"
    RESET    = "\033[0m"
    PURPLE   = "\033[38;5;135m"
    PURPLE_B = "\033[38;5;141m"
    PURPLE_L = "\033[38;5;177m"
    PURPLE_D = "\033[38;5;93m"
    LAVENDER = "\033[38;5;183m"
    VIOLET   = "\033[38;5;99m"
    ORCHID   = "\033[38;5;170m"
    SUCCESS  = "\033[38;5;118m"
    ERROR    = "\033[38;5;196m"
    WARN     = "\033[38;5;220m"
    INFO     = "\033[38;5;51m"
    MATRIX   = "\033[38;5;46m"
    GOLD     = "\033[38;5;220m"


PRINT_LOCK = threading.Lock()


def cprint(msg="", color=None, bold=False):
    c = color or ""
    b = C.BOLD if bold else ""
    with PRINT_LOCK:
        print(f"{b}{c}{msg}{C.RESET}", flush=True)


# ═══════════════════════════════════════════════════════════════
#  LOGO & LINES
# ═══════════════════════════════════════════════════════════════
def print_logo():
    purple = C.PURPLE_L
    print()
    cprint(" ██▓███   ███▄ ▄███▓▄▄▄█████▓", purple)
    cprint("▓██░  ██▒▓██▒▀█▀ ██▒▓  ██▒ ▓▒", purple)
    cprint("▓██░ ██▓▒▓██    ▓██░▒ ▓██░ ▒░", purple)
    cprint("▒██▄█▓▒ ▒▒██    ▒██ ░ ▓██▓ ░ ", C.PURPLE_B)
    cprint("▒██▒ ░  ░▒██▒   ░██▒  ▒██▒ ░ ", C.PURPLE_B)
    cprint("▒▓▒░ ░  ░░ ▒░   ░  ░  ▒ ░░   ", C.PURPLE)
    cprint("░▒ ░     ░  ░      ░    ░    ", C.PURPLE)
    cprint("░░       ░      ░     ░      ", C.PURPLE)
    cprint("                ░            ", C.PURPLE_D)
    print()


def line_eq(width=60):
    cprint("=" * width, C.PURPLE_L)


def line_dash(width=60):
    cprint("─" * width, C.PURPLE_B)


def line_eq_med(width=60):
    cprint("=" * width, C.PURPLE_L)


# ═══════════════════════════════════════════════════════════════
#  HACKER ANIMATIONS
# ═══════════════════════════════════════════════════════════════
def hacking_boot():
    os.system("cls" if os.name == "nt" else "clear")
    print_logo()
    line_eq()
    print()
    cprint(f"  {C.BOLD}{C.PURPLE_L}⚡ SYSTEM BOOT SEQUENCE{C.RESET}", C.PURPLE_L)
    print()

    boot_lines = [
        (f"{C.SUCCESS}[✓]{C.RESET} Initializing kernel module...", 0.15),
        (f"{C.SUCCESS}[✓]{C.RESET} Loading smart captcha engine...", 0.12),
        (f"{C.SUCCESS}[✓]{C.RESET} Connecting to Waryono solver API...", 0.18),
        (f"{C.SUCCESS}[✓]{C.RESET} Bypassing anti-bot detection...", 0.15),
        (f"{C.SUCCESS}[✓]{C.RESET} Generating device fingerprint...", 0.12),
        (f"{C.SUCCESS}[✓]{C.RESET} Injecting stealth headers...", 0.12),
        (f"{C.SUCCESS}[✓]{C.RESET} Multi-captcha resolver: ONLINE", 0.15),
        (f"{C.GOLD}[⚡]{C.RESET}   Node status: SECURE", 0.12),
        (f"{C.PURPLE_L}[★]{C.RESET}   System ready. Welcome, Operative.", 0.18),
    ]
    for line, delay in boot_lines:
        print(f"  {line}")
        time.sleep(delay)
    print()
    line_eq()
    time.sleep(0.4)


def loading_bar(label="INITIALIZING", duration=1.5):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start = time.time()
    i = 0
    while time.time() - start < duration:
        progress = (time.time() - start) / duration
        bar_len = 30
        filled = int(bar_len * progress)
        bar = "█" * filled + "░" * (bar_len - filled)
        frame = frames[i % len(frames)]
        hex_noise = "".join(random.choices("0123456789ABCDEF", k=8))
        line = (f"\r{C.PURPLE_L}┃{C.RESET} {C.ORCHID}{frame}{C.RESET} "
                f"{C.LAVENDER}{label:<24}{C.RESET} {C.PURPLE_L}[{bar}]{C.RESET} "
                f"{C.PURPLE_B}{int(progress*100):>3}%{C.RESET} {C.DIM}0x{hex_noise}{C.RESET}")
        sys.stdout.write(line)
        sys.stdout.flush()
        time.sleep(0.06)
        i += 1
    sys.stdout.write("\r" + " " * 110 + "\r")
    sys.stdout.flush()


def glitch_text(text, duration=0.8):
    glitch_chars = "!@#$%^&*()_+{}|:<>?~`"
    start = time.time()
    while time.time() - start < duration:
        result = "".join(random.choice(glitch_chars) if random.random() < 0.3 else ch for ch in text)
        sys.stdout.write(f"\r{C.PURPLE_L}{result}{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write(f"\r{C.PURPLE_L}{text}{C.RESET}\n")


def scan_animation(label="Scanning target"):
    bar_len = 45
    for i in range(bar_len + 1):
        bar = f"{C.PURPLE_L}{'█' * i}{C.DIM}{'░' * (bar_len - i)}{C.RESET}"
        noise = "".join(random.choices("01", k=16))
        sys.stdout.write(f"\r{C.PURPLE_B}┃{C.RESET} {C.LAVENDER}{label}{C.RESET} {bar} {C.PURPLE_L}[{noise}]{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.035)
    sys.stdout.write("\n")


def matrix_rain(width=60, height=5, duration=1.0):
    chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉ0123456789"
    start = time.time()
    lines = [[' ' for _ in range(width)] for _ in range(height)]
    while time.time() - start < duration:
        for _ in range(3):
            col = random.randint(0, width - 1)
            lines[0][col] = random.choice(chars)
        for y in range(height - 1, 0, -1):
            lines[y] = lines[y-1].copy()
            lines[0] = [' ' for _ in range(width)]
        output = ""
        for y, row in enumerate(lines):
            line = "".join(row)
            intensity = C.PURPLE_L if y < 2 else (C.PURPLE_B if y < 3 else C.DIM)
            output += f"{intensity}{line}{C.RESET}\n"
        sys.stdout.write(f"\033[{height}A")
        sys.stdout.write(output)
        sys.stdout.flush()
        time.sleep(0.08)


# ═══════════════════════════════════════════════════════════════
#  AUTHENTICATION SETUP UI  —  BARU
# ═══════════════════════════════════════════════════════════════
def print_auth_header():
    """Header AUTHENTICATION SETUP."""
    print()
    line_eq()
    title = "⚡ AUTHENTICATION SETUP"
    pad = (60 - len(title) - 2) // 2
    cprint(f"{' ' * pad}{C.BOLD}{C.PURPLE_L}{title}{C.RESET}")
    line_eq()
    print()


def print_waryono_section(status="WAITING", api_key=""):
    """Section [01] WARYONO SOLVER."""
    if status == "READY":
        status_color = C.SUCCESS
        status_icon = "● READY"
    else:
        status_color = C.WARN
        status_icon = "● WAITING"

    key_display = "********" if api_key else "(belum diisi)"

    cprint(f"  {C.PURPLE_L}[01]{C.RESET} {C.BOLD}{C.LAVENDER}WARYONO SOLVER{C.RESET}")
    cprint(f"       {C.PURPLE_D}├─{C.RESET} Status    : {status_color}{status_icon}{C.RESET}")
    cprint(f"       {C.PURPLE_D}├─{C.RESET} Support   : {C.LAVENDER}Turnstile / hCaptcha / reCAPTCHA{C.RESET}")
    cprint(f"       {C.PURPLE_D}└─{C.RESET} API Key   : {C.LAVENDER}{key_display}{C.RESET}")
    print()


def print_initdata_section(status="WAITING"):
    """Section [02] TELEGRAM MINI APP."""
    if status == "READY":
        status_color = C.SUCCESS
        status_icon = "● READY"
    else:
        status_color = C.WARN
        status_icon = "● WAITING"

    cprint(f"  {C.PURPLE_L}[02]{C.RESET} {C.BOLD}{C.LAVENDER}TELEGRAM MINI APP{C.RESET}")
    cprint(f"       {C.PURPLE_D}├─{C.RESET} Method    : {C.LAVENDER}Telegram WebApp{C.RESET}")
    cprint(f"       {C.PURPLE_D}├─{C.RESET} Format    : {C.LAVENDER}authorization: tma ...{C.RESET}")
    cprint(f"       {C.PURPLE_D}└─{C.RESET} Status    : {status_color}{status_icon}{C.RESET}")
    print()


def print_system_init_header():
    """Header SYSTEM INITIALIZING."""
    line_eq()
    title = "SYSTEM INITIALIZING..."
    pad = (60 - len(title) - 2) // 2
    cprint(f"{' ' * pad}{C.BOLD}{C.PURPLE_L}{title}{C.RESET}")
    line_eq()


# ═══════════════════════════════════════════════════════════════
#  INPUT PROMPT
# ═══════════════════════════════════════════════════════════════
def input_prompt(prompt, color=None, required=True, default=None, prefix="▸"):
    color = color or C.PURPLE_L
    while True:
        try:
            val = input(f"     {color}{C.BOLD}{prefix} {prompt}{C.RESET}\n       {C.PURPLE_L}❯ {C.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            cprint(f"\n  {C.ERROR}[!] Dibatalkan.{C.RESET}")
            sys.exit(0)
        if not val and default is not None:
            return default
        if not val and required:
            cprint(f"  {C.ERROR}[!] Tidak boleh kosong. Coba lagi.{C.RESET}")
            continue
        return val


# ═══════════════════════════════════════════════════════════════
#  KONFIG
# ═══════════════════════════════════════════════════════════════
BASE_URL      = "https://captivating-gentleness-production-3932.up.railway.app"
WEBAPP_ORIGIN = "https://pmtgram.vercel.app"

TURNSTILE_SITEKEY = "0x4AAAAAACOf6mYyukJx5XVy"
HCAPTCHA_SITEKEY  = ""
RECAPTCHA_SITEKEY = ""

WARYONO_IN  = "https://api.waryono.my.id/in.php"
WARYONO_RES = "https://api.waryono.my.id/res.php"
WARYONO_POLL_INTERVAL = 3
WARYONO_MAX_WAIT      = 120

COMPANY_ORDER = ["adsgram", "monetag", "gigapub"]

DELAY_MIN = 12
DELAY_MAX = 22


CONFIG = {
    "init_data": None,
    "waryono_key": None,
    "device_fingerprint": None,
    "device_id": None,
    "signals": None,
    "user_info": None,
    "captcha_cache": {},
}


# ═══════════════════════════════════════════════════════════════
#  HEADERS & PAYLOAD
# ═══════════════════════════════════════════════════════════════
def build_headers():
    return {
        "authorization": f"tma {CONFIG['init_data']}",
        "content-type": "application/json",
        "origin": WEBAPP_ORIGIN,
        "referer": WEBAPP_ORIGIN + "/",
        "user-agent": (
            "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 "
            "Telegram-Android/12.10.1 (Infinix Infinix X6817; Android 12; SDK 31; AVERAGE)"
        ),
        "x-requested-with": "org.telegram.messenger",
        "accept": "*/*",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Android WebView";v="152"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-site": "cross-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
    }


def common_payload():
    return {
        "_deviceFingerprint": CONFIG["device_fingerprint"],
        "_deviceId": CONFIG["device_id"],
        "_suspiciousFlags": {"headless": False, "emulator": False, "devtools": False},
        "_signals": CONFIG["signals"],
    }


# ═══════════════════════════════════════════════════════════════
#  INIT DATA
# ═══════════════════════════════════════════════════════════════
def parse_init_data(init_data):
    try:
        qs = parse_qs(init_data)
        user_raw = qs.get("user", [None])[0]
        if not user_raw:
            return None
        user = json.loads(unquote(user_raw))
        return {
            "id": user.get("id"),
            "first_name": user.get("first_name", ""),
            "username": user.get("username", ""),
        }
    except Exception:
        return None


def generate_device_info():
    seed = f"{time.time()}{random.random()}"
    h = lambda x: hashlib.sha256(f"{seed}{x}".encode()).hexdigest()
    fp = h("fp")
    dev = f"{h('d1')[:8]}-{h('d2')[:4]}-{h('d3')[:4]}-{h('d4')[:4]}-{h('d5')[:12]}"
    signals = {
        "canvasHash":   h("canvas"),
        "webglHash":    h("webgl"),
        "hardwareHash": h("hardware"),
        "fontsHash":    h("fonts"),
        "audioHash":    h("audio"),
    }
    return fp, dev, signals


# ═══════════════════════════════════════════════════════════════
#  SMART CAPTCHA DETECTION
# ═══════════════════════════════════════════════════════════════
CAPTCHA_PATTERNS = {
    "turnstile": [
        r"0x4AAAAAA[A-Za-z0-9_-]{10,}",
        r"turnstile",
        r"cf-turnstile",
    ],
    "hcaptcha": [
        r"hcaptcha\.com",
        r"h-captcha",
        r"hcaptcha",
        r"[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}",
    ],
    "recaptcha": [
        r"6L[a-zA-Z0-9_-]{38}",
        r"recaptcha",
        r"g-recaptcha",
        r"grecaptcha",
    ],
}


def detect_captcha_type(response_data):
    if not response_data:
        return None, None

    raw = json.dumps(response_data) if isinstance(response_data, (dict, list)) else str(response_data)
    detected_type = None
    detected_sitekey = None

    if isinstance(response_data, dict):
        for field in ["captchaType", "captcha_type", "captcha", "type", "provider"]:
            val = response_data.get(field, "")
            if val:
                val_l = str(val).lower()
                if "turnstile" in val_l:
                    detected_type = "turnstile"
                    break
                elif "hcaptcha" in val_l or "h-captcha" in val_l:
                    detected_type = "hcaptcha"
                    break
                elif "recaptcha" in val_l or "re-captcha" in val_l:
                    detected_type = "recaptcha"
                    break

        for field in ["sitekey", "siteKey", "site_key", "captchaSitekey"]:
            if field in response_data:
                detected_sitekey = response_data[field]
                break

        data = response_data.get("data", {})
        if isinstance(data, dict):
            for field in ["captchaType", "captcha", "sitekey", "siteKey"]:
                if field in data and not detected_sitekey:
                    detected_sitekey = data[field]

    if not detected_type:
        for cap_type, patterns in CAPTCHA_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, raw, re.IGNORECASE)
                if match:
                    detected_type = cap_type
                    if not detected_sitekey:
                        if pattern.startswith(("0x4", "6L", "[a-f0-9]{8}")):
                            detected_sitekey = match.group(0)
                    break
            if detected_type:
                break

    if not detected_type:
        detected_type = "turnstile"
        detected_sitekey = TURNSTILE_SITEKEY

    if not detected_sitekey:
        detected_sitekey = {
            "turnstile": TURNSTILE_SITEKEY,
            "hcaptcha": HCAPTCHA_SITEKEY,
            "recaptcha": RECAPTCHA_SITEKEY,
        }.get(detected_type, TURNSTILE_SITEKEY)

    return detected_type, detected_sitekey


# ═══════════════════════════════════════════════════════════════
#  WARYONO SOLVER
# ═══════════════════════════════════════════════════════════════
def waryono_balance():
    try:
        r = requests.get(
            f"{WARYONO_RES}?apikey={CONFIG['waryono_key']}&action=balance&json=1",
            timeout=15
        )
        return r.text.strip()
    except Exception:
        return "error"


def solve_captcha(cap_type="turnstile", sitekey=None):
    sitekey = sitekey or TURNSTILE_SITEKEY
    method_map = {
        "turnstile": "turnstile",
        "hcaptcha": "hcaptcha",
        "recaptcha": "userrecaptcha",
    }
    method = method_map.get(cap_type, "turnstile")

    body = {
        "apikey": CONFIG["waryono_key"],
        "methods": method,
        "domain": WEBAPP_ORIGIN,
        "sitekey": sitekey,
    }
    if cap_type == "recaptcha":
        body["action"] = "verify"

    try:
        r = requests.post(WARYONO_IN, json=body, timeout=30)
        text = r.text.strip()
        if r.status_code != 200:
            return None, f"HTTP {r.status_code}"
        try:
            j = r.json()
            if j.get("status") == 1:
                return j.get("request"), None
            return None, j.get("request", "unknown")
        except ValueError:
            if text.startswith("OK|"):
                return text.split("|", 1)[1], None
            return None, text
    except Exception as e:
        return None, str(e)


def poll_token(task_id):
    params = {"apikey": CONFIG["waryono_key"], "id": task_id, "action": "get", "json": 1}
    start = time.time()
    last_status = ""

    while time.time() - start < WARYONO_MAX_WAIT:
        try:
            r = requests.get(WARYONO_RES, params=params, timeout=20)
            try:
                j = r.json()
                status = j.get("status")
                req = str(j.get("request", ""))
                if status == 1 and req:
                    return req, None
                if status == 0:
                    req_upper = req.upper()
                    if "NOT_READY" in req_upper:
                        last_status = "waiting"
                        sys.stdout.write(f"\r{C.DIM}     [solver] ⏳ waiting... ({int(time.time()-start)}s){C.RESET}   ")
                        sys.stdout.flush()
                        time.sleep(WARYONO_POLL_INTERVAL)
                        continue
                    if "ERROR" in req_upper:
                        return None, req
                    last_status = req
            except ValueError:
                t = r.text.strip()
                if t.startswith("OK|"):
                    return t.split("|", 1)[1], None
                if "NOT_READY" in t.upper():
                    last_status = "waiting"
                    time.sleep(WARYONO_POLL_INTERVAL)
                    continue
                if t.startswith("ERROR"):
                    return None, t
        except Exception:
            pass
        time.sleep(WARYONO_POLL_INTERVAL)

    sys.stdout.write("\r" + " " * 60 + "\r")
    return None, f"TIMEOUT ({last_status})"


# ═══════════════════════════════════════════════════════════════
#  PMT API
# ═══════════════════════════════════════════════════════════════
def safe_request(session, method, url, **kwargs):
    try:
        if method == "post":
            r = session.post(url, timeout=30, **kwargs)
        else:
            r = session.get(url, timeout=30, **kwargs)

        ctype = r.headers.get("content-type", "")
        if "json" not in ctype.lower() and r.text and not r.text.strip().startswith(("{", "[")):
            return {"success": False, "error": f"Non-JSON response: {r.text[:100]}"}

        try:
            return r.json()
        except ValueError:
            return {"success": False, "error": f"Invalid JSON: {r.text[:100]}"}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timeout"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Connection error"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_state(session):
    payload = common_payload()
    payload["_initData"] = CONFIG["init_data"]
    payload["_startParam"] = ""
    return safe_request(session, "post", f"{BASE_URL}/getState",
                        headers=build_headers(), json=payload)


def heartbeat(session):
    return safe_request(session, "post", f"{BASE_URL}/heartbeat",
                        headers=build_headers(), json=common_payload())


def claim_reward(session, company):
    payload = common_payload()
    payload["company"] = company

    resp = safe_request(session, "post", f"{BASE_URL}/claimAdReward",
                        headers=build_headers(), json=payload)

    if resp.get("success"):
        return resp

    err_msg = (resp.get("error") or resp.get("message") or "").lower()
    needs_captcha = (
        "captcha" in err_msg or "turnstile" in err_msg
        or "token" in err_msg or "verification" in err_msg
        or "challenge" in err_msg
    )
    if not needs_captcha:
        return resp

    cache_key = company
    if cache_key in CONFIG["captcha_cache"]:
        cap_type, sitekey = CONFIG["captcha_cache"][cache_key]
    else:
        cap_type, sitekey = detect_captcha_type(resp)
        CONFIG["captcha_cache"][cache_key] = (cap_type, sitekey)
        cprint(f"     {C.PURPLE_L}[smart]{C.RESET} {C.LAVENDER}Detected: {cap_type}{C.RESET}")

    cprint(f"     {C.PURPLE_B}[solver]{C.RESET} {C.LAVENDER}Requesting {cap_type}...{C.RESET}")
    task_id, err = solve_captcha(cap_type, sitekey)
    if not task_id:
        cprint(f"     {C.WARN}[solver] {cap_type} failed: {err}{C.RESET}")
        cprint(f"     {C.WARN}[solver] Fallback to turnstile...{C.RESET}")
        cap_type = "turnstile"
        sitekey = TURNSTILE_SITEKEY
        task_id, err = solve_captcha(cap_type, sitekey)
        if not task_id:
            return {"success": False, "error": f"solver submit ({cap_type}): {err}"}

    tok, err = poll_token(task_id)
    sys.stdout.write("\r" + " " * 60 + "\r")
    if not tok:
        return {"success": False, "error": f"solver poll ({cap_type}): {err}"}
    cprint(f"     {C.SUCCESS}[solver]{C.RESET} {C.LAVENDER}✓ Token OK{C.RESET}")

    payload["turnstileToken"] = tok
    payload["captchaToken"] = tok
    payload["hcaptchaToken"] = tok
    payload["recaptchaToken"] = tok

    resp = safe_request(session, "post", f"{BASE_URL}/claimAdReward",
                        headers=build_headers(), json=payload)
    return resp


# ═══════════════════════════════════════════════════════════════
#  COMPANY LOGIC
# ═══════════════════════════════════════════════════════════════
def parse_server_config(stats):
    return (
        stats.get("adCompanies", {}),
        stats.get("adsWatchedByCompany", {}),
        stats.get("adDailyTotalLimit", 70),
        stats.get("adsWatchedToday", 0),
    )


def pick_company(companies, watched, total_today, total_limit):
    sisa_total = total_limit - total_today
    if sisa_total <= 0:
        return None, 0, 0
    for comp in COMPANY_ORDER:
        if comp not in companies:
            continue
        conf = companies[comp]
        limit = conf.get("dailyLimit", 0)
        reward = conf.get("reward", 0)
        done = watched.get(comp, 0)
        if limit <= 0 or done >= limit:
            continue
        sisa = min(limit - done, sisa_total)
        if sisa > 0:
            return comp, sisa, reward
    return None, 0, 0


# ═══════════════════════════════════════════════════════════════
#  COLLECT INPUT — UI BARU
# ═══════════════════════════════════════════════════════════════
def collect_input():
    os.system("cls" if os.name == "nt" else "clear")
    print_logo()
    print_auth_header()

    # ══ [01] Waryono Solver ══
    print_waryono_section(status="WAITING", api_key="")
    line_dash()

    print(f"\n     {C.PURPLE_L}▸{C.RESET} {C.BOLD}{C.LAVENDER}Masukkan Waryono API Key:{C.RESET}")
    while True:
        key = input(f"       {C.PURPLE_L}❯ {C.RESET}").strip()
        if not key:
            cprint(f"  {C.ERROR}[!] Tidak boleh kosong.{C.RESET}")
            continue
        if len(key) < 16:
            cprint(f"  {C.ERROR}[!] Key terlalu pendek (min 16).{C.RESET}")
            continue
        CONFIG["waryono_key"] = key
        break

    # Animasi verify key
    print()
    loading_bar("Verifying API key", 0.8)
    cprint(f"  {C.SUCCESS}✓{C.RESET} API Key tersimpan: {C.LAVENDER}{key[:8]}...{key[-4:]}{C.RESET}")
    time.sleep(0.4)

    # ══ [02] Telegram Mini App ══
    os.system("cls" if os.name == "nt" else "clear")
    print_logo()
    print_auth_header()

    print_waryono_section(status="READY", api_key=key)
    line_dash()
    print()
    print_initdata_section(status="WAITING")
    line_dash()

    print(f"\n     {C.PURPLE_L}▸{C.RESET} {C.BOLD}{C.LAVENDER}Masukkan Init Data:{C.RESET}")
    cprint(f"       {C.DIM}Format: authorization: tma <query_id=...&user=...>{C.RESET}")
    while True:
        init = input(f"       {C.PURPLE_L}❯ {C.RESET}").strip()
        if not init:
            cprint(f"  {C.ERROR}[!] Tidak boleh kosong.{C.RESET}")
            continue
        if "query_id=" not in init:
            cprint(f"  {C.ERROR}[!] Harus mengandung 'query_id='.{C.RESET}")
            continue
        # strip kalau user paste full "authorization: tma ..."
        if "tma " in init.lower():
            init = init.split("tma ", 1)[1].strip()
        CONFIG["init_data"] = init
        info = parse_init_data(init)
        if info:
            cprint(f"  {C.SUCCESS}✓{C.RESET} User: {C.LAVENDER}{info['first_name']} (@{info['username']}){C.RESET}")
        break

    # Generate device info
    fp, dev, signals = generate_device_info()
    CONFIG["device_fingerprint"] = fp
    CONFIG["device_id"] = dev
    CONFIG["signals"] = signals

    # ══ SYSTEM INITIALIZING ══
    print()
    time.sleep(0.4)
    os.system("cls" if os.name == "nt" else "clear")
    print_logo()
    print_auth_header()

    print_waryono_section(status="READY", api_key=key)
    line_dash()
    print()
    print_initdata_section(status="READY")
    line_dash()

    print()
    print_system_init_header()
    print()

    # Animasi inisialisasi keren
    init_steps = [
        (f"{C.PURPLE_L}[01]{C.RESET} {C.LAVENDER}Generating device fingerprint...{C.RESET}", 0.9),
        (f"{C.PURPLE_L}[02]{C.RESET} {C.LAVENDER}Signing request headers...{C.RESET}", 0.7),
        (f"{C.PURPLE_L}[03]{C.RESET} {C.LAVENDER}Initializing smart captcha engine...{C.RESET}", 0.8),
        (f"{C.PURPLE_L}[04]{C.RESET} {C.LAVENDER}Warming up Waryono solver...{C.RESET}", 0.6),
        (f"{C.PURPLE_L}[05]{C.RESET} {C.LAVENDER}Establishing secure channel...{C.RESET}", 0.7),
    ]
    for step, dur in init_steps:
        print(f"  {step}")
        loading_bar("", dur)
        cprint(f"    {C.SUCCESS}✓ Done{C.RESET}", C.SUCCESS)
        print()

    # Matrix rain sebelum lanjut
    matrix_rain(width=60, height=4, duration=0.8)
    scan_animation("Handshake with PMT Gram server")
    time.sleep(0.3)

    cprint(f"  {C.SUCCESS}✓{C.RESET} {C.LAVENDER}Device ID: {C.DIM}{dev}{C.RESET}")
    cprint(f"  {C.SUCCESS}✓{C.RESET} {C.LAVENDER}Authentication ready{C.RESET}")
    print()
    line_eq()
    time.sleep(0.5)


# ═══════════════════════════════════════════════════════════════
#  FARMER
# ═══════════════════════════════════════════════════════════════
def print_main_banner():
    os.system("cls" if os.name == "nt" else "clear")
    print_logo()
    line_eq()
    title = "PMT GRAM • AUTOFARM"
    pad = (60 - len(title) - 2) // 2
    cprint(f"{' ' * pad}{C.BOLD}{C.PURPLE_L}{title}{C.RESET}")
    line_eq()
    cprint(f"  {C.PURPLE_B}ScriptMaker {C.RESET}: {C.LAVENDER}MoneyMaker_w{C.RESET}")
    cprint(f"  {C.PURPLE_B}Engine      {C.RESET}: {C.LAVENDER}Smart Captcha Detection{C.RESET}")
    cprint(f"  {C.PURPLE_B}Mode        {C.RESET}: {C.LAVENDER}Auto Farmer{C.RESET}")
    cprint(f"  {C.PURPLE_B}Status      {C.RESET}: {C.SUCCESS}● CONNECTED{C.RESET}")
    print()


def print_account_section(user, balance, ads_today, total_limit, waryono_bal):
    line_eq()
    cprint(f"  {C.BOLD}{C.PURPLE_L}ACCOUNT{C.RESET}")
    line_eq()
    cprint(f"  {C.PURPLE_B}User        {C.RESET}: {C.LAVENDER}{user}{C.RESET}")
    cprint(f"  {C.PURPLE_B}Balance     {C.RESET}: {C.GOLD}{balance:,} PMT{C.RESET}")
    cprint(f"  {C.PURPLE_B}Ads Today   {C.RESET}: {C.LAVENDER}{ads_today}/{total_limit}{C.RESET}")
    cprint(f"  {C.PURPLE_B}Solver      {C.RESET}: {C.LAVENDER}Waryono {C.PURPLE_D}•{C.RESET} {C.CYAN}{waryono_bal}{C.RESET}")
    print()


def progress_bar(done, limit, width=10):
    if limit <= 0:
        return "░" * width
    ratio = min(1.0, done / limit)
    filled = int(ratio * width)
    return "█" * filled + "░" * (width - filled)


def print_company_section(companies, watched):
    line_eq()
    cprint(f"  {C.BOLD}{C.PURPLE_L}COMPANY STATUS{C.RESET}")
    line_eq()
    for comp in COMPANY_ORDER:
        if comp not in companies:
            continue
        conf = companies[comp]
        limit = conf.get("dailyLimit", 0)
        reward = conf.get("reward", 0)
        done = watched.get(comp, 0)
        bar = progress_bar(done, limit)

        if done >= limit:
            bar_color = C.DIM
            status_color = C.YELLOW
        elif done >= limit * 0.7:
            bar_color = C.SUCCESS
            status_color = C.SUCCESS
        else:
            bar_color = C.PURPLE_B
            status_color = C.LAVENDER

        comp_upper = comp.upper()
        line = (
            f"  {C.PURPLE_L}{comp_upper:<11}{C.RESET} "
            f"{bar_color}[{bar}]{C.RESET}  "
            f"{status_color}{done:>2}/{limit:<3}{C.RESET}  "
            f"{C.GOLD}+{reward} PMT{C.RESET}"
        )
        cprint(line)
    print()


def print_live_log_claim(idx, added, balance, ads_done, ads_total):
    now = datetime.now().strftime("%H:%M:%S")
    cprint(f"  {C.PURPLE_D}{now}{C.RESET}  {C.SUCCESS}●{C.RESET} {C.BOLD}{C.LAVENDER}Claim #{idx:02d}{C.RESET}")
    cprint(f"            {C.GOLD}+{added} PMT{C.RESET}")
    cprint(f"            {C.PURPLE_B}Balance {C.RESET}: {C.CYAN}{balance:,} PMT{C.RESET}")
    cprint(f"            {C.PURPLE_B}Ads     {C.RESET}: {C.CYAN}{ads_done}/{ads_total}{C.RESET}")
    print()


def print_live_log_heartbeat():
    now = datetime.now().strftime("%H:%M:%S")
    cprint(f"  {C.PURPLE_D}{now}{C.RESET}  {C.INFO}◉{C.RESET} {C.LAVENDER}Heartbeat OK{C.RESET}")


def print_live_log_waiting(delay):
    now = datetime.now().strftime("%H:%M:%S")
    cprint(f"  {C.PURPLE_D}{now}{C.RESET}  {C.WARN}⏳{C.RESET} {C.LAVENDER}Waiting {delay:.1f}s...{C.RESET}")
    print()


def print_live_log_fail(idx, msg):
    now = datetime.now().strftime("%H:%M:%S")
    cprint(f"  {C.PURPLE_D}{now}{C.RESET}  {C.ERROR}✗{C.RESET} {C.ERROR}Claim #{idx:02d} GAGAL{C.RESET}")
    cprint(f"            {C.DIM}{msg[:60]}{C.RESET}")
    print()


def print_session_section(sukses, gagal, runtime_str, status="FARMING"):
    line_eq()
    cprint(f"  {C.BOLD}{C.PURPLE_L}SESSION{C.RESET}")
    line_eq()
    cprint(f"  {C.SUCCESS}SUCCESS     {C.RESET}: {C.BOLD}{C.SUCCESS}{sukses}{C.RESET}")
    cprint(f"  {C.ERROR}FAILED      {C.RESET}: {C.BOLD}{C.ERROR}{gagal}{C.RESET}")
    cprint(f"  {C.PURPLE_B}CLAIMS      {C.RESET}: {C.BOLD}{C.LAVENDER}{sukses + gagal}{C.RESET}")
    cprint(f"  {C.PURPLE_B}RUNTIME     {C.RESET}: {C.BOLD}{C.LAVENDER}{runtime_str}{C.RESET}")
    status_color = C.SUCCESS if status == "FARMING" else C.WARN
    cprint(f"  {C.PURPLE_B}STATUS      {C.RESET}: {status_color}● {status}{C.RESET}")
    line_eq()


def run_farmer():
    session = requests.Session()

    scan_animation("Fetching account state")
    st = get_state(session)

    if not st.get("success"):
        cprint(f"  {C.ERROR}✗ getState gagal: {st.get('error', 'unknown')}{C.RESET}")
        return

    data = st["data"]
    user = data["user"]
    stats = data["stats"]

    companies, watched, total_limit, total_today = parse_server_config(stats)

    user_name = user.get('firstName') or user.get('username') or "Unknown"
    waryono_bal = waryono_balance()

    os.system("cls" if os.name == "nt" else "clear")
    print_main_banner()
    print_account_section(user_name, data.get('balance', 0), total_today, total_limit, waryono_bal)
    print_company_section(companies, watched)

    # Plan section
    line_eq()
    cprint(f"  {C.BOLD}{C.PURPLE_L}PLAN{C.RESET}")
    line_eq()
    preview_total = 0
    preview_reward = 0
    tmp_today = total_today
    for comp in COMPANY_ORDER:
        if comp not in companies:
            continue
        conf = companies[comp]
        limit = conf.get("dailyLimit", 0)
        reward = conf.get("reward", 0)
        done = watched.get(comp, 0)
        sisa = min(limit - done, total_limit - tmp_today)
        if sisa > 0:
            cprint(f"  {C.PURPLE_L}{comp.upper():<11}{C.RESET} : {C.LAVENDER}{sisa:>2} ads × {reward} PMT{C.RESET} = {C.GOLD}{sisa*reward} PMT{C.RESET}")
            preview_total += sisa
            preview_reward += sisa * reward
            tmp_today += sisa
        else:
            cprint(f"  {C.PURPLE_L}{comp.upper():<11}{C.RESET} : {C.DIM}(skip){C.RESET}")

    if preview_total <= 0:
        cprint(f"\n  {C.SUCCESS}✓ Semua company sudah penuh.{C.RESET}")
        return

    print()
    line_eq()
    cprint(f"  {C.BOLD}{C.GOLD}Total: {preview_total} ads ≈ {preview_reward} PMT{C.RESET}")
    line_eq()

    print()
    input(f"     {C.PURPLE_L}▸ {C.LAVENDER}Tekan ENTER untuk mulai{C.RESET}")

    os.system("cls" if os.name == "nt" else "clear")
    print_main_banner()
    line_eq()
    cprint(f"  {C.BOLD}{C.PURPLE_L}LIVE FARMING{C.RESET}")
    line_eq()
    print()

    sukses, gagal = 0, 0
    current_company = None
    start_time = time.time()
    counter = 0
    consecutive_fails = 0
    MAX_CONSECUTIVE_FAILS = 5

    while True:
        st = get_state(session)
        if not st.get("success"):
            consecutive_fails += 1
            if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                break
            time.sleep(5)
            continue

        try:
            stats = st["data"]["stats"]
            companies, watched, total_limit, total_today = parse_server_config(stats)
        except (KeyError, TypeError):
            break

        next_comp, sisa, reward = pick_company(companies, watched, total_today, total_limit)

        if not next_comp or sisa <= 0:
            cprint(f"  {C.SUCCESS}✓ Semua company penuh. Stop.{C.RESET}")
            break

        if current_company != next_comp:
            current_company = next_comp

        counter += 1
        i = counter

        if i > 1 and (i - 1) % 5 == 0:
            hb = heartbeat(session)
            if hb.get("success"):
                print_live_log_heartbeat()

        resp = claim_reward(session, current_company)

        if resp.get("success"):
            consecutive_fails = 0
            d = resp.get("data", {})
            sukses += 1
            print_live_log_claim(
                i,
                d.get('shibaAdded', 0),
                int(float(d.get('shibaBalance', 0))),
                d.get('adsWatchedToday', 0),
                d.get('adDailyTotalLimit', total_limit)
            )
        else:
            consecutive_fails += 1
            gagal += 1
            msg = resp.get("error") or resp.get("message") or json.dumps(resp)[:80]
            print_live_log_fail(i, msg)
            low = str(msg).lower()

            if "limit" in low or "quota" in low or "penuh" in low:
                time.sleep(2)
                continue
            if "rate" in low or "429" in low:
                wait = random.randint(30, 60)
                time.sleep(wait)
                continue
            if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                break

        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        print_live_log_waiting(delay)
        time.sleep(delay)

    elapsed = int(time.time() - start_time)
    runtime_str = f"{elapsed // 3600:02d}:{(elapsed % 3600) // 60:02d}:{elapsed % 60:02d}"

    print()
    print_session_section(sukses, gagal, runtime_str, "DONE")

    print()
    fs = get_state(session)
    if fs.get("success"):
        fd = fs["data"]
        fst = fd["stats"]
        companies, watched, total_limit, total_today = parse_server_config(fst)

        print_account_section(
            fd.get('user', {}).get('firstName') or user_name,
            fd.get('balance', 0),
            total_today,
            total_limit,
            waryono_balance()
        )
        print_company_section(companies, watched)

    cprint(f"\n  {C.PURPLE_L}👑 ScriptMaker: {C.LAVENDER}MoneyMaker_w{C.RESET}", C.PURPLE_L)
    print()


# ═══════════════════════════════════════════════════════════════
#  ENTRY
# ═══════════════════════════════════════════════════════════════
def main():
    try:
        hacking_boot()
        loading_bar("Loading core modules", 1.2)
        collect_input()
        run_farmer()
    except KeyboardInterrupt:
        print()
        glitch_text("SYSTEM SHUTDOWN...", 0.6)
        cprint(f"\n  {C.WARN}[!] Dihentikan oleh user.{C.RESET}")
        sys.exit(0)
    except Exception as e:
        print()
        cprint(f"\n  {C.ERROR}[!] Error fatal: {e}{C.RESET}")
        import traceback
        cprint(traceback.format_exc(), C.DIM)
        sys.exit(1)


if __name__ == "__main__":
    main()
