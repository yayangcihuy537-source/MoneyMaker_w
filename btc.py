#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import random
import hashlib
import re
import urllib.parse
import requests
from datetime import datetime, timezone

# ========== WARNA ==========
class Col:
    R    = '\033[0m'
    WHT  = '\033[97m'
    YEL  = '\033[93m'
    RED  = '\033[91m'
    GRN  = '\033[92m'
    BLU  = '\033[94m'
    CYA  = '\033[96m'
    MAG  = '\033[95m'
    DIM  = '\033[2m'
    B    = '\033[1m'
    NEON_G  = '\033[38;5;46m'
    NEON_C  = '\033[38;5;51m'
    NEON_P  = '\033[38;5;201m'
    NEON_Y  = '\033[38;5;226m'
    NEON_O  = '\033[38;5;208m'
    NEON_R  = '\033[38;5;196m'
    DIM_C   = '\033[38;5;240m'

RESET = Col.R
MERAH = Col.RED
HIJAU = Col.GRN
KUNING = Col.YEL
BIRU = Col.BLU
CYAN = Col.CYA
PUTIH = Col.WHT

# ========== KONFIGURASI ==========
BASE_URL = "https://btc.tonrevenue.space"
GIGA_URL = "https://ad.gigapub.tech/v1/ad"
GIGA_PROJ = "5736"
GIGA_TOKEN = "CEEUHXgZVL184wyaDp6laEchjHQ7RNN3"
CONFIG_FILE = "btcton_config.json"

DEFAULT_UA = "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)"

init_data = ""
SESSION_FINGERPRINT = ""

# ========== ANIMATIONS ==========
class Anim:
    @staticmethod
    def spinner(text, duration=2):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        end = time.time() + duration
        i = 0
        while time.time() < end:
            frame = frames[i % len(frames)]
            sys.stdout.write(f"\r {Col.NEON_C}{frame}{Col.R} {Col.WHT}{text}{Col.R}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        pad = " " * (len(text) + 6)
        sys.stdout.write(f"\r{pad}\r")
        print(f" {Col.NEON_G}✓{Col.R} {Col.WHT}{text}{Col.R}")

    @staticmethod
    def dots(text, duration=2):
        end = time.time() + duration
        n = 0
        while time.time() < end:
            d = "." * ((n % 3) + 1)
            sys.stdout.write(f"\r {Col.NEON_C}•{Col.R} {Col.WHT}{text}{Col.NEON_C}{d:<4}{Col.R}")
            sys.stdout.flush()
            time.sleep(0.3)
            n += 1
        pad = " " * (len(text) + 8)
        sys.stdout.write(f"\r{pad}\r")
        print(f" {Col.NEON_G}✓{Col.R} {Col.WHT}{text}{Col.R}")

    @staticmethod
    def progress(text, duration=2, width=30):
        end = time.time() + duration
        total = duration
        while time.time() < end:
            elapsed = duration - (end - time.time())
            pct = min(1.0, elapsed / total)
            filled = int(pct * width)
            empty = width - filled
            bar = f"{Col.NEON_G}{'█' * filled}{Col.DIM_C}{'░' * empty}{Col.R}"
            sys.stdout.write(
                f"\r {Col.NEON_C}▶{Col.R} "
                f"{Col.WHT}{text:<30}{Col.R} "
                f"[{bar}] "
                f"{Col.NEON_Y}{int(pct * 100):>3}%{Col.R}"
            )
            sys.stdout.flush()
            time.sleep(0.05)
        pad = " " * (len(text) + 60)
        sys.stdout.write(f"\r{pad}\r")
        print(f" {Col.NEON_G}✓{Col.R} {Col.WHT}{text}{Col.R}")

    @staticmethod
    def scan(text, duration=2):
        end = time.time() + duration
        i = 0
        bar_w = 30
        while time.time() < end:
            pos = i % (bar_w * 2)
            if pos >= bar_w:
                pos = bar_w * 2 - pos
            bar = ""
            for j in range(bar_w):
                if abs(j - pos) < 3:
                    bar += f"{Col.NEON_G}█{Col.R}"
                else:
                    bar += f"{Col.DIM_C}·{Col.R}"
            sys.stdout.write(f"\r {Col.NEON_C}[SCAN]{Col.R} {Col.WHT}{text:<25}{Col.R} [{bar}]")
            sys.stdout.flush()
            time.sleep(0.06)
            i += 1
        pad = " " * (len(text) + 50)
        sys.stdout.write(f"\r{pad}\r")
        print(f" {Col.NEON_G}✓{Col.R} {Col.WHT}{text}{Col.R}")

    @staticmethod
    def typewriter(text, delay=0.02, color=None):
        c = color or Col.WHT
        for ch in text:
            sys.stdout.write(f"{c}{ch}{Col.R}")
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def glitch(text, duration=0.6):
        gc = "░▒▓█▄▀■□▪▫@#$%&*"
        end = time.time() + duration
        while time.time() < end:
            out = ''.join(random.choice(gc) if (random.randint(0,10)<2 and ch!=' ') else ch for ch in text)
            sys.stdout.write(f"\r {Col.NEON_P}{out}{Col.R}")
            sys.stdout.flush()
            time.sleep(0.06)
        sys.stdout.write(f"\r {Col.NEON_C}{text}{Col.R}\n")
        sys.stdout.flush()

    @staticmethod
    def matrix_line(width=62, duration=1.5):
        chars = "0123456789ABCDEF"
        end = time.time() + duration
        while time.time() < end:
            line = "".join(random.choice(chars) if random.random() < 0.3 else " " for _ in range(width))
            sys.stdout.write(f"\r{Col.NEON_G}{line}{Col.R}")
            sys.stdout.flush()
            time.sleep(0.04)
        for _ in range(3):
            line = "".join(random.choice(chars) if random.random() < 0.1 else "─" for _ in range(width))
            sys.stdout.write(f"\r{Col.NEON_C}{line}{Col.R}")
            sys.stdout.flush()
            time.sleep(0.08)
        sys.stdout.write(f"\r{Col.NEON_C}{'─' * width}{Col.R}\n")

    @staticmethod
    def banner_animation():
        steps = [
            "Initializing kernel module...",
            "Loading stealth headers...",
            "Rotating device fingerprint...",
            "Connecting to remote server...",
            "Bypassing protection layers...",
            "Session ready.",
        ]
        print()
        for s in steps:
            sys.stdout.write(f"  {Col.NEON_G}[✓]{Col.R} {Col.WHT}{s}{Col.R}\n")
            sys.stdout.flush()
            time.sleep(random.uniform(0.06, 0.12))
        print(f"  {Col.NEON_Y}[⚡]{Col.R} {Col.WHT}Status: {Col.NEON_G}SECURE{Col.R}")
        print(f"  {Col.NEON_P}[★]{Col.R} {Col.WHT}Welcome, {Col.NEON_C}Operative{Col.R}\n")
        time.sleep(0.5)

# ========== BANNER ==========
BANNER = f"""
{Col.NEON_G}{Col.B}  ████████╗ ██████╗ ███╗   ██╗██████╗ ███████╗██╗   ██╗
  ╚══██╔══╝██╔═══██╗████╗  ██║██╔══██╗██╔════╝██║   ██║
     ██║   ██║   ██║██╔██╗ ██║██████╔╝█████╗  ██║   ██║
     ██║   ██║   ██║██║╚██╗██║██╔══██╗██╔══╝  ╚██╗ ██╔╝
     ██║   ╚██████╔╝██║ ╚████║██║  ██║███████╗ ╚████╔╝
     ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝  ╚═══╝{Col.R}

{Col.NEON_C}  ╔════════════════════════════════════════════════════════╗
  ║  {Col.NEON_Y}💰  TONREVENUE ADS FARM  •  {Col.NEON_P}BYPASS MODE{Col.NEON_C}  ║
  ╚════════════════════════════════════════════════════════╝{Col.R}

  {Col.NEON_G}▸ Dev     : {Col.NEON_C}MoneyMaker_w{Col.R}
  {Col.NEON_G}▸ Channel : {Col.NEON_C}t.me/ScriptyXSouu{Col.R}
  {Col.DIM}  ────────────────────────────────────────────{Col.R}
"""

# ========== UTILITY ==========
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def timer(seconds, prefix="[!] please wait"):
    if seconds < 1:
        return
    frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    i = 0
    while seconds > 0:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        time_str = f"{h:02d}:{m:02d}:{s:02d}"
        spinner = frames[i % len(frames)]
        sys.stdout.write(f"\r{Col.NEON_C}{prefix} {Col.NEON_G}{time_str} {Col.NEON_Y}{spinner}\033[K{Col.R}")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
        i += 1
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()

def fmt(n):
    if n is None:
        return "0"
    try:
        return f"{float(n):.8f}".rstrip('0').rstrip('.')
    except:
        return str(n)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"initData": ""}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# ========== PARSE INIT DATA ==========
def parse_init_data(raw):
    try:
        if raw.startswith('user=') or '&hash=' in raw:
            parsed = dict(urllib.parse.parse_qsl(raw))
        else:
            parsed = dict(urllib.parse.parse_qsl(urllib.parse.unquote(raw)))

        user_str = parsed.get('user', '{}')
        try:
            user = json.loads(urllib.parse.unquote(user_str))
        except:
            user = json.loads(user_str) if user_str.startswith('{') else {}

        auth_date = parsed.get('auth_date')
        auth_ts = int(auth_date) if auth_date else 0

        return {
            'raw': raw,
            'user': user,
            'language_code': user.get('language_code', 'id'),
            'auth_date': auth_ts,
            'hash': parsed.get('hash', '')
        }
    except Exception as e:
        return {'raw': raw, 'user': {}, 'language_code': 'id', 'auth_date': 0, 'hash': '', 'error': str(e)}

def validate_init_data(parsed):
    if not parsed.get('auth_date'):
        return True, "no auth_date"
    age = time.time() - parsed['auth_date']
    if age > 86400:
        return False, f"auth_date expired ({int(age/3600)}h lalu, max 24h)"
    if age < 0:
        return False, "auth_date di masa depan (clock skew)"
    return True, f"valid ({int(age/60)}m ago)"

def gen_fingerprint(seed=None):
    if seed is None:
        seed = f"{time.time()}{random.random()}{random.randint(0, 999999)}"
    return hashlib.md5(seed.encode()).hexdigest()

def get_init_data():
    global init_data
    config = load_config()
    if config.get('initData'):
        return config['initData']
    print(f"{Col.WHT}initData (TG) : {Col.NEON_Y}", end="")
    init_data = input().strip()
    if init_data:
        config['initData'] = init_data
        save_config(config)
        print(f"{Col.NEON_G}Konfigurasi disimpan ke {CONFIG_FILE}{Col.R}")
        return init_data
    return None

def refresh_initdata():
    global init_data
    print(f"{Col.WHT}initData baru: {Col.NEON_Y}", end="")
    new = input().strip()
    if not new:
        return False
    config = load_config()
    config['initData'] = new
    save_config(config)
    init_data = new
    parsed = parse_init_data(new)
    ok, msg = validate_init_data(parsed)
    if ok:
        print(f"{Col.NEON_G}✓ InitData valid ({msg}){Col.R}")
    else:
        print(f"{Col.NEON_Y}⚠ {msg}{Col.R}")
    return True

# ========== HEADERS ==========
def tg_headers(init_user_agent=None, extra=None):
    ua = init_user_agent or DEFAULT_UA
    headers = {
        'user-agent': ua,
        'content-type': 'application/json',
        'x-requested-with': 'org.telegram.messenger.web',
        'origin': BASE_URL,
        'referer': BASE_URL + '/',
        'sec-ch-ua': '"Chromium";v="152", "Not?A_Brand";v="24", "Android WebView";v="152"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept': '*/*',
        'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    if extra:
        headers.update(extra)
    return headers

def build_init_payload():
    parsed = parse_init_data(init_data)
    lang = parsed.get('language_code', 'id')
    return {
        "initData": init_data,
        "start_param": None,
        "fingerprint": SESSION_FINGERPRINT,
        "ua": DEFAULT_UA,
        "screen": "384x832",
        "lang": f"{lang}-{lang.upper()}" if lang else "id-ID",
        "tz": "Asia/Jakarta",
        "platform": "Linux aarch64",
        "tg_platform": "android",
        "viewport_width": 384,
        "viewport_height": 696,
        "max_touch_points": 5,
        "device_pixel_ratio": 2.8125
    }

def http_json(url, payload, headers, timeout=20):
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        try:
            data = resp.json()
            if isinstance(data, dict):
                data['_status_code'] = resp.status_code
            return data
        except:
            return {"error": "non_json", "_status_code": resp.status_code, "_text": resp.text[:200]}
    except requests.exceptions.Timeout:
        return {"error": "timeout"}
    except Exception as e:
        return {"error": "connection_failed", "_detail": str(e)}

def is_init_error(j):
    msg = str(j.get('detail', '')) + ' ' + str(j.get('message', '')) + ' ' + str(j.get('error', ''))
    return ('InitData' in msg
            or 'initdata' in msg.lower()
            or 'session expired' in msg.lower()
            or 'invalid' in msg.lower()
            or 'auth' in msg.lower())

def api(path, extra=None):
    global init_data
    for attempt in range(2):
        payload = {"initData": init_data}
        if extra:
            payload.update(extra)
        r = http_json(BASE_URL + path, payload, tg_headers())
        if attempt == 0 and is_init_error(r):
            if refresh_initdata():
                continue
        return r
    return r

def giga_call(body):
    headers = tg_headers(extra={
        'authorization': f'Bearer {GIGA_TOKEN}',
        'project-id': GIGA_PROJ
    })
    return http_json(GIGA_URL, body, headers)

def giga_user():
    parsed = parse_init_data(init_data)
    return {'user': parsed.get('user', {}), 'platform': 'android', 'version': '9.6', 'start_param': None}

def get_state():
    r = api("/api/tasks/ads/state")
    return r.get('tasks', [])

def get_init():
    global init_data
    for attempt in range(2):
        payload = build_init_payload()
        r = http_json(BASE_URL + "/api/init", payload, tg_headers())
        if attempt == 0 and is_init_error(r):
            if refresh_initdata():
                continue
        return r
    return r

def captcha_answer(ch):
    prompt = re.sub(r'[^a-zA-Z ]', '', ch.get('prompt', '')).strip().lower()
    want = None
    m = re.search(r'the (\w+)', prompt)
    if m:
        want = m.group(1)
    else:
        want = re.sub(r'tap ', '', prompt).strip()
    for opt in ch.get('options', []):
        if opt.get('id', '').lower() == want or opt.get('label', '').lower() == want:
            return opt['id']
    return ''

def ensure_captcha():
    for _ in range(3):
        j = get_init()
        ch = j.get('user', {}).get('captcha_challenge')
        if not ch:
            return True
        ans = captcha_answer(ch)
        if not ans:
            print(f"{Col.WHT}[CAPTCHA] {Col.RED}jawaban gak ketemu untuk '{ch.get('prompt', '?')}'{Col.R}")
            return False
        Anim.dots(f"solve captcha '{ch.get('prompt', '?')}'", 1.5)
        r = api("/api/captcha/verify", {"challenge_id": ch['challenge_id'], "answer": ans})
        if r.get('status') == 'success':
            print(f"{Col.WHT}[CAPTCHA] {Col.NEON_G}✓ OK{Col.R}")
            return True
        print(f"{Col.WHT}[CAPTCHA] {Col.RED}✗ {r.get('detail', r.get('message', 'gagal'))}{Col.R}")
        time.sleep(2)
    return False

# ========== FARM ==========
def do_farm():
    notified_limit = {}
    max_cycles = 100
    cycle = 0
    while cycle < max_cycles:
        cycle += 1
        tasks = get_state()
        if not tasks:
            print(f"{Col.WHT}[STATE] {Col.RED}kosong/gagal, coba captcha...{Col.R}")
            ensure_captcha()
            tasks = get_state()
            if not tasks:
                timer(60, "  retry...")
                continue

        busy = 0
        tried_any = False
        claimed = False

        for t in tasks:
            prov = t.get('provider', '')
            if prov not in ['adexium', 'gigapubs']:
                continue
            rem = int(t.get('remaining_today', 0))
            cdl = int(t.get('cooldown_left', 0))
            cds = int(t.get('cooldown_seconds', 300))
            if rem <= 0:
                if prov not in notified_limit:
                    print(f"{Col.WHT}[{Col.NEON_C}{prov}{Col.WHT}] {Col.NEON_Y}limit hari ini habis, skip{Col.R}")
                    notified_limit[prov] = True
                continue
            if cdl > 0:
                busy = max(busy, cdl)
                continue

            tried_any = True
            Anim.progress(f"start ad {prov}", 1.5)
            st = api("/api/tasks/ads/start", {"provider": prov, "interaction": None})
            sid = st.get('session_uid', '')
            if not sid:
                print(f"{Col.WHT}[{Col.NEON_C}{prov}{Col.WHT}] {Col.RED}{st.get('detail', st.get('message', 'start gagal'))}{Col.R}")
                continue

            if prov == 'gigapubs':
                Anim.scan("gigapubs simulation", 2)
                tg = giga_user()
                giga_call({'method': 'init', 'args': {'user': tg}, 'version': 'v85', 'seconds': 9.9})
                uniq = f"{random.randint(100000000, 999999999)}.{random.randint(100000, 999999)}"
                any_data = {
                    'showDone': True,
                    'fallPriorityList': ['rich','rD','t','d','monetag','m1','o1','rB'],
                    'fallRotationType': 'priority',
                    'showCounter': 0,
                    'showTryCounter': 0,
                    'uniqShowId': uniq,
                    'readyNetsCount': 4,
                    'showTag': None
                }
                base = {'user': tg, 'placementId': 'main', 'transactionId': None, 'version': 'v85'}
                giga_call({'method': 'adShowTryStart', 'args': {**base, 'network': 't', 'rotationType': 'priority', 'showCounter': 0, 'anyData': any_data}})
                time.sleep(4)
                any2 = dict(any_data); any2['showDone'] = False; any2['showTryCounter'] = 1
                giga_call({'method': 'adShowed', 'args': {**base, 'network': 't', 'rotationType': 'priority', 'showCounter': 0, 'seconds': 18.7, 'anyData': any2}})
                any3 = dict(any_data); any3['showCounter'] = 1; any3['showTryCounter'] = 2
                giga_call({'method': 'adShowTryStart', 'args': {**base, 'network': 'd', 'rotationType': 'priority', 'showCounter': 1, 'anyData': any3}})
                time.sleep(4)
                any4 = dict(any3); any4['showDone'] = True
                giga_call({'method': 'adShowedX', 'args': {**base, 'network': 'd', 'rotationType': 'priority', 'showCounter': 2, 'seconds': 32.8, 'anyData': any4}})

            Anim.progress("confirm reward", 1.5)
            cf = api("/api/tasks/ads/confirm", {"session_uid": sid})
            status = cf.get('status', '')
            if status in ['success', 'already_confirmed']:
                amt = cf.get('reward_sats', 0.2)
                nb = cf.get('new_balance', '?')
                used = int(cf.get('used_today', 0))
                rem2 = int(cf.get('remaining_today', rem))
                c = int(cf.get('cooldown', cds))
                print(f"{Col.WHT}[{Col.NEON_C}{prov}{Col.WHT}] {Col.NEON_G}+{fmt(amt)}{Col.WHT} sat — {Col.NEON_C}{used}/{used+rem2}{Col.WHT} — bal {Col.NEON_C}{fmt(nb)}{Col.WHT} sat{Col.R}")
                busy = max(busy, c)
                claimed = True
                timer(random.randint(8, 10), "  wait...")
            elif status == 'pending_postback':
                print(f"{Col.WHT}[{Col.NEON_C}{prov}{Col.WHT}] {Col.NEON_Y}pending postback{Col.R}")
                busy = max(busy, cds)
            else:
                print(f"{Col.WHT}[{Col.NEON_C}{prov}{Col.WHT}] {Col.RED}{cf.get('detail', cf.get('message', status or 'gagal'))}{Col.R}")

        if busy > 0:
            timer(busy, "  next...")
            continue
        if not tried_any:
            print(f"{Col.WHT}semua limit hari ini, exit...{Col.R}")
            return
        if claimed:
            timer(5, "  wait...")
            continue
        timer(20, "  retry...")
    print(f"{Col.WHT}Maksimal cycle tercapai, berhenti.{Col.R}")

# ========== MAIN ==========
def main():
    global init_data, SESSION_FINGERPRINT

    # Generate fingerprint awal
    SESSION_FINGERPRINT = gen_fingerprint()

    # BOOT ANIMATION
    clear()
    Anim.matrix_line(width=62, duration=1.0)
    Anim.typewriter("  >>> TONREVENUE ADS FARM v3.0", delay=0.012, color=Col.NEON_C)
    Anim.glitch("BYPASS EDITION", 0.5)
    print()
    Anim.banner_animation()
    time.sleep(0.3)

    clear()
    print(BANNER)
    print(f"  {Col.NEON_C}Fingerprint : {Col.WHT}{SESSION_FINGERPRINT[:24]}...{Col.R}\n")

    init_data = get_init_data()
    if not init_data:
        print(f"{Col.RED}init_data tidak boleh kosong!{Col.R}")
        sys.exit(1)

    parsed = parse_init_data(init_data)
    ok, msg = validate_init_data(parsed)
    if ok:
        print(f"{Col.NEON_G}✓ InitData valid ({msg}){Col.R}")
        print(f"{Col.WHT}  User: {Col.NEON_C}{parsed['user'].get('username', '?')}{Col.R}")
    else:
        print(f"{Col.RED}✗ {msg}{Col.R}")
        print(f"{Col.NEON_Y}  Login ulang di Telegram → ambil initData baru.{Col.R}")
        if not refresh_initdata():
            sys.exit(1)

    Anim.progress("initialize session", 1.5)
    print()

    while True:
        print(f"\n{Col.NEON_C}═══ {Col.NEON_G}TONREVENUE MENU{Col.NEON_C} ═══{Col.R}\n")

        ensure_captcha()
        Anim.spinner("fetch account info", 1)
        ib = get_init()
        if ib.get('user'):
            u = ib['user']
            acc = ib.get('access', {})
            print(f"{Col.WHT}balance    : {Col.NEON_C}{fmt(u.get('balance', 0))}{Col.WHT} sat{Col.R}")
            print(f"{Col.WHT}withdraw   : {Col.NEON_G}{fmt(ib.get('withdraw_available_sats', 0))}{Col.WHT} sat available{Col.R}")
            if acc.get('mobile_only_blocked'):
                print(f"{Col.WHT}status     : {Col.RED}MOBILE ONLY BLOCKED{Col.R}")
            elif u.get('is_blocked'):
                print(f"{Col.WHT}status     : {Col.RED}BLOCKED ({u.get('ban_reason', '?')}){Col.R}")
            else:
                print(f"{Col.WHT}status     : {Col.NEON_G}clean{Col.R}")
        else:
            err = ib.get('detail', ib.get('message', ib.get('error', '?')))
            print(f"{Col.WHT}balance    : {Col.RED}gagal fetch ({err}){Col.R}")

        Anim.dots("fetch tasks", 1)
        tasks = get_state()
        if tasks:
            for t in tasks:
                prov = t.get('provider', '')
                if prov not in ['adexium', 'gigapubs']:
                    continue
                used = int(t.get('daily_cap', 0)) - int(t.get('remaining_today', 0))
                print(f"{Col.WHT}{prov:<10}: {Col.NEON_C}{used}/{t.get('daily_cap', '?')}{Col.WHT} | reward {Col.NEON_Y}{t.get('reward_sats', '?')}{Col.WHT} sat | cooldown {Col.NEON_Y}{t.get('cooldown_left', '?')}s{Col.R}")
        else:
            print(f"{Col.WHT}tasks      : {Col.RED}gagal fetch state{Col.R}")

        print()
        print(f"{Col.NEON_G}  [1]{Col.WHT} 🚀 Start Farm {Col.DIM}(Adexium + GigaPubs){Col.R}")
        print(f"{Col.NEON_Y}  [2]{Col.WHT} 🔄 Refresh InitData{Col.R}")
        print(f"{Col.NEON_C}  [3]{Col.WHT} 🔑 Ganti Fingerprint{Col.R}")
        print(f"{Col.RED}  [0]{Col.WHT} ❌ Exit{Col.R}")
        print()
        print(f"{Col.WHT}pilih: {Col.NEON_Y}", end="")
        opt = input().strip()

        if opt == '1':
            do_farm()
            input(f"\n{Col.WHT}enter untuk kembali...{Col.R}")
        elif opt == '2':
            refresh_initdata()
            input(f"\n{Col.WHT}enter...{Col.R}")
        elif opt == '3':
            SESSION_FINGERPRINT = gen_fingerprint()
            Anim.spinner("rotate fingerprint", 1.5)
            print(f"{Col.NEON_G}  → {SESSION_FINGERPRINT}{Col.R}")
            input(f"\n{Col.WHT}enter...{Col.R}")
        elif opt == '0':
            Anim.dots("shutting down", 1)
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Col.RED}⏹️  Keluar.{Col.R}")
        sys.exit(0)
