#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiteBits.io Telegram Mini App Auto Claim Bot (@litebits_faucet_bot)
- Telethon Auth + Referral A7F2K9
- Auto-stop 6 jam + Session Report
- Animated UI + Sparkline + Success Rate
"""

import time
import json
import re
import os
import sys
import random
import urllib.parse
import asyncio
from datetime import datetime, timezone
from collections import deque

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


# ==================== COLORS ====================
class Col:
    R = '\033[0m'
    B = '\033[1m'
    D = '\033[2m'
    RED = '\033[91m'
    GRN = '\033[92m'
    YEL = '\033[93m'
    BLU = '\033[94m'
    MAG = '\033[95m'
    CYN = '\033[96m'
    WHT = '\033[97m'
    GRY = '\033[90m'
    NEON_G = '\033[38;5;46m'
    NEON_C = '\033[38;5;51m'
    NEON_Y = '\033[38;5;226m'
    NEON_P = '\033[38;5;207m'
    NEON_O = '\033[38;5;208m'
    NEON_V = '\033[38;5;141m'
    NEON_R = '\033[38;5;196m'
    PURPLE = '\033[38;5;129m'
    DIM_C  = '\033[38;5;244m'


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# ==================== ANIMATIONS ====================
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
            sys.stdout.write(f"\r {Col.NEON_C}▶{Col.R} {Col.WHT}{text:<30}{Col.R} [{bar}] {Col.NEON_Y}{int(pct*100):>3}%{Col.R}")
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
    def matrix_line(width=62, duration=1.5):
        chars = "0123456789ABCDEF"
        end = time.time() + duration
        while time.time() < end:
            line = "".join(random.choice(chars) if random.random() < 0.3 else " " for _ in range(width))
            sys.stdout.write(f"\r{Col.NEON_G}{line}{Col.R}")
            sys.stdout.flush()
            time.sleep(0.04)
        for alpha in range(3):
            line = "".join(random.choice(chars) if random.random() < 0.1 else "─" for _ in range(width))
            sys.stdout.write(f"\r{Col.NEON_C}{line}{Col.R}")
            sys.stdout.flush()
            time.sleep(0.08)
        sys.stdout.write(f"\r{Col.NEON_C}{'─' * width}{Col.R}\n")

    @staticmethod
    def opening_sequence():
        clear()
        print()
        Anim.typewriter(f"{Col.NEON_C}Initializing boot sequence...", 0.02, Col.NEON_C)
        time.sleep(0.3)
        Anim.progress("Loading core modules", 1.0)
        Anim.progress("Establishing secure channel", 1.0)
        Anim.progress("Verifying signature chain", 0.8)
        print()
        Anim.matrix_line(62, 1.2)
        print()

        banner_lines = [
            f"{Col.NEON_C}=============================================================={Col.R}",
            f"{Col.NEON_Y}                    ⚡ {Col.NEON_G}LITEBITS{Col.NEON_Y} ⚡{Col.R}",
            f"{Col.NEON_C}                 {Col.WHT}AUTO CLAIM SYSTEM v2.5{Col.R}",
            f"{Col.NEON_C}=============================================================={Col.R}",
            f"{Col.NEON_V} ScriptMaker : {Col.WHT}MoneyMaker_w{Col.R}",
            f"{Col.NEON_V} Bot         : {Col.NEON_C}@litebits_faucet_bot{Col.R}",
            f"{Col.NEON_V} Referral    : {Col.NEON_Y}{REFERRAL_CODE}{Col.R}",
            f"{Col.NEON_V} Auto-stop   : {Col.NEON_O}{MAX_RUNTIME // 3600} hours{Col.R}",
            f"{Col.NEON_V} Status      : {Col.NEON_G}● READY{Col.R}",
            f"{Col.NEON_C}=============================================================={Col.R}",
        ]
        for line in banner_lines:
            print(line)
            time.sleep(0.05)
        print()
        time.sleep(0.5)


# ==================== BANNER ====================
def render_banner():
    return f"""
{Col.NEON_C}=============================================================={Col.R}
{Col.NEON_Y}                    ⚡ {Col.NEON_G}LITEBITS{Col.NEON_Y} ⚡{Col.R}
{Col.NEON_C}                 {Col.WHT}AUTO CLAIM SYSTEM v2.5{Col.R}
{Col.NEON_C}=============================================================={Col.R}
{Col.NEON_V} ScriptMaker : {Col.WHT}MoneyMaker_w{Col.R}
{Col.NEON_V} Bot         : {Col.NEON_C}@litebits_faucet_bot{Col.R}
{Col.NEON_V} Referral    : {Col.NEON_Y}{REFERRAL_CODE}{Col.R}
{Col.NEON_V} Auto-stop   : {Col.NEON_O}{MAX_RUNTIME // 3600} hours{Col.R}
{Col.NEON_V} Status      : {Col.NEON_G}● ONLINE{Col.R}
{Col.NEON_C}=============================================================={Col.R}
"""


# ==================== CONFIG ====================
API_HASH      = 'fb06985ea797ac51aaa1e6d1168ceaaa'
API_ID        = 35898257
DEFAULT_BOT   = 'litebits_faucet_bot'
REFERRAL_CODE = 'A7F2K9'
CONFIG_FILE   = 'litebits.json'
BASE_URL      = 'https://mini.litebits.io'

HOLD_DURATION    = 5
PREPARE_WAIT     = 8
AD_VIEW_WAIT     = 20
DEFAULT_COOLDOWN = 301

# ===== AUTO STOP =====
MAX_RUNTIME = 6 * 3600       # 6 jam
REPORT_FILE = 'litebits_report.txt'

try:
    from telethon import TelegramClient, functions, types
    HAS_TELETHON = True
except ImportError:
    HAS_TELETHON = False


# ==================== BOT ====================
class LiteBitsTeleBot:

    def __init__(self):
        self.session          = None
        self.init_data        = ""
        self.auth_token       = ""
        self.bot_username     = DEFAULT_BOT
        self.user_agent       = "Mozilla/5.0 (Linux; Android 14; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Mobile Safari/537.36 Telegram-Android"
        self.session_earned   = 0.0
        self.cycles           = 0
        self.cycles_failed    = 0
        self.user_info        = {}
        self.cooldown_seconds = DEFAULT_COOLDOWN
        self.running          = True
        self.cycle_logs       = []
        self.base_dir         = os.path.dirname(os.path.abspath(__file__))
        self.start_time       = time.time()

        self.balance_history  = deque(maxlen=30)
        self.earned_history   = deque(maxlen=30)
        self.last_claim_time  = None
        self.streak           = 0

    # ---------- SPARKLINE ----------
    def sparkline(self, values, width=30):
        if not values or len(values) < 2:
            return f"{Col.DIM_C}{'·' * width}{Col.R}"
        blocks = "▁▂▃▄▅▆▇█"
        vmin = min(values)
        vmax = max(values)
        span = vmax - vmin if vmax > vmin else 1
        vals = list(values)
        if len(vals) > width:
            step = len(vals) / width
            vals = [vals[int(i * step)] for i in range(width)]
        elif len(vals) < width:
            vals = [vmin] * (width - len(vals)) + vals
        out = ""
        for v in vals:
            idx = int((v - vmin) / span * 7)
            idx = max(0, min(7, idx))
            if idx >= 6:
                c = Col.NEON_G
            elif idx >= 4:
                c = Col.NEON_C
            elif idx >= 2:
                c = Col.NEON_Y
            else:
                c = Col.NEON_O
            out += f"{c}{blocks[idx]}{Col.R}"
        return out

    # ---------- TIMER BAR ----------
    def _bar(self, remaining, total, width=20):
        if total <= 0:
            total = 1
        filled = int((total - remaining) / total * width)
        filled = max(0, min(width, filled))
        empty = width - filled
        return f"{Col.NEON_G}{'█' * filled}{Col.DIM_C}{'░' * empty}{Col.R}"

    def _progress_wait(self, seconds, label="WAIT", total=None):
        total = total or seconds
        for left in range(seconds, 0, -1):
            if not self.running:
                break
            bar = self._bar(left, total)
            mm, ss = divmod(left, 60)
            hh, mm = divmod(mm, 60)
            tstr = f"{hh:02d}:{mm:02d}:{ss:02d}"
            line = f" {Col.NEON_Y}[⏳ {label}]{Col.R} {Col.WHT}{tstr}{Col.R} [{bar}]"
            self.render_view(live_line=line)
            time.sleep(1)

    # ---------- DASHBOARD ----------
    def render_dashboard(self):
        name = str(
            self.user_info.get('telegramUsername')
            or self.user_info.get('username')
            or self.user_info.get('first_name')
            or self.user_info.get('id')
            or 'User'
        )
        if not name.startswith('@') and (
            self.user_info.get('telegramUsername') or self.user_info.get('username')
        ):
            name = '@' + name

        try:
            bal = float(str(self.user_info.get('balance', '0')))
            bal_str = f"{bal:.2f} Coins"
        except Exception:
            bal_str = f"{self.user_info.get('balance', '0.00')} Coins"

        earned_str = f"+{self.session_earned:.2f} Coins"

        total_cyc = self.cycles + self.cycles_failed
        rate = (self.cycles / total_cyc * 100) if total_cyc > 0 else 100.0

        # Runtime & remaining
        elapsed = int(time.time() - self.start_time)
        remaining = max(0, MAX_RUNTIME - elapsed)
        eh, er = divmod(elapsed, 3600); em, es = divmod(er, 60)
        rh, rr = divmod(remaining, 3600); rm, rs = divmod(rr, 60)

        print(f"{Col.NEON_C}┌─ {Col.NEON_Y}ACCOUNT{Col.NEON_C} " + "─" * 49 + f"┐{Col.R}")
        print(f"{Col.NEON_C}│{Col.R} {Col.NEON_V}User{Col.R}      : {Col.NEON_C}{name:<46}{Col.NEON_C}│{Col.R}")
        print(f"{Col.NEON_C}│{Col.R} {Col.NEON_V}Balance{Col.R}   : {Col.NEON_Y}{bal_str:<46}{Col.NEON_C}│{Col.R}")
        print(f"{Col.NEON_C}│{Col.R} {Col.NEON_V}Earned{Col.R}    : {Col.NEON_G}{earned_str:<46}{Col.NEON_C}│{Col.R}")
        print(f"{Col.NEON_C}│{Col.R} {Col.NEON_V}Cycles{Col.R}    : {Col.WHT}{str(self.cycles):<46}{Col.NEON_C}│{Col.R}")
        print(f"{Col.NEON_C}│{Col.R} {Col.NEON_V}Success{Col.R}   : {Col.NEON_G if rate >= 90 else Col.NEON_Y}{f'{rate:.1f}%':<46}{Col.NEON_C}│{Col.R}")
        print(f"{Col.NEON_C}│{Col.R} {Col.NEON_V}Uptime{Col.R}    : {Col.NEON_C}{f'{eh:02d}:{em:02d}:{es:02d}':<46}{Col.NEON_C}│{Col.R}")
        print(f"{Col.NEON_C}│{Col.R} {Col.NEON_V}Remaining{Col.R} : {Col.NEON_O}{f'{rh:02d}:{rm:02d}:{rs:02d}':<46}{Col.NEON_C}│{Col.R}")
        print(f"{Col.NEON_C}└" + "─" * 60 + f"┘{Col.R}")

        if len(self.balance_history) >= 2:
            spark = self.sparkline(list(self.balance_history), 50)
            try:
                cur = float(self.balance_history[-1])
                prev = float(self.balance_history[0])
                delta = cur - prev
                delta_c = Col.NEON_G if delta >= 0 else Col.NEON_R
                delta_s = f"+{delta:.2f}" if delta >= 0 else f"{delta:.2f}"
            except Exception:
                delta_s = "?"
                delta_c = Col.WHT
            print(f"{Col.NEON_C}┌─ {Col.NEON_Y}BALANCE TREND{Col.NEON_C} " + "─" * 43 + f"┐{Col.R}")
            print(f"{Col.NEON_C}│{Col.R} {spark}  {delta_c}{delta_s:>8}{Col.R} {Col.NEON_C}│{Col.R}")
            print(f"{Col.NEON_C}└" + "─" * 60 + f"┘{Col.R}")
        print()

    # ---------- RENDER ----------
    def render_view(self, live_line=None):
        clear()
        print(render_banner())
        self.render_dashboard()

        print(f"{Col.NEON_C}========================= {Col.NEON_Y}LIVE LOGS{Col.NEON_C} ==========================={Col.R}")
        print()
        for entry in self.cycle_logs[-12:]:
            print(entry)
        print()

        if live_line:
            print(live_line)
            print()

        runtime = int(time.time() - self.start_time)
        h, r = divmod(runtime, 3600)
        m, s = divmod(r, 60)
        status = f"{Col.NEON_G}● RUNNING" if self.running else f"{Col.NEON_R}● STOPPED"
        print(f"{Col.NEON_C}=============================================================={Col.R}")
        print(
            f"{Col.NEON_V} STATUS : {status}{Col.R}   "
            f"{Col.DIM_C}| Uptime: {h:02d}:{m:02d}:{s:02d}{Col.R}   "
            f"{Col.DIM_C}| PID: {os.getpid()}{Col.R}"
        )
        print(f"{Col.NEON_C}=============================================================={Col.R}")

    # ---------- LOGGING ----------
    def add_log(self, level, msg):
        icons = {
            'ok':    f"{Col.NEON_G}✓{Col.R}",
            'err':   f"{Col.RED}✗{Col.R}",
            'info':  f"{Col.NEON_C}•{Col.R}",
            'wait':  f"{Col.NEON_Y}⏳{Col.R}",
            'warn':  f"{Col.NEON_O}!{Col.R}",
            'star':  f"{Col.NEON_P}★{Col.R}",
            'auth':  f"{Col.NEON_C}🔐{Col.R}",
            'bal':   f"{Col.NEON_Y}💰{Col.R}",
            'cycle': f"{Col.NEON_V}🔄{Col.R}",
            'net':   f"{Col.NEON_C}🌐{Col.R}",
            'fire':  f"{Col.NEON_O}🔥{Col.R}",
        }
        icon = icons.get(level, f"{Col.NEON_C}·{Col.R}")
        ts = datetime.now().strftime("%H:%M:%S")
        prefix = f"{Col.DIM_C}[{ts}]{Col.R}"
        self.cycle_logs.append(f"{prefix} {icon} {Col.WHT}{msg}{Col.R}")
        self.render_view()

    # ---------- HTTP ----------
    def init_http_session(self):
        try:
            from curl_cffi import requests as c_requests
            self.session = c_requests.Session(impersonate="chrome120")
        except ImportError:
            try:
                import cloudscraper
                self.session = cloudscraper.create_scraper()
            except ImportError:
                import requests
                self.session = requests.Session()
        self.apply_headers()

    def apply_headers(self):
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': BASE_URL,
            'Referer': f"{BASE_URL}/",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Content-Type': 'application/json'
        }
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        if self.init_data:
            headers['x-telegram-init-data'] = self.init_data
        if hasattr(self.session, 'headers'):
            self.session.headers.update(headers)

    # ---------- CONFIG ----------
    def load_config(self):
        cfg_path = os.path.join(self.base_dir, CONFIG_FILE)
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                self.init_data    = cfg.get('init_data', '')
                self.auth_token   = cfg.get('auth_token', '')
                self.bot_username = cfg.get('bot_username', DEFAULT_BOT)
                self.user_agent   = cfg.get('user_agent', self.user_agent)
                self.session_earned = float(cfg.get('total_earned', 0))
                self.cycles       = int(cfg.get('total_cycles', 0))
                return bool(self.init_data or self.auth_token)
            except Exception:
                pass
        return False

    def save_config(self):
        cfg_path = os.path.join(self.base_dir, CONFIG_FILE)
        cfg = {
            'init_data': self.init_data,
            'auth_token': self.auth_token,
            'bot_username': self.bot_username,
            'user_agent': self.user_agent,
            'total_earned': round(self.session_earned, 4),
            'total_cycles': self.cycles,
        }
        try:
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    # ---------- AUTH ----------
    def validate_telegram_auth(self):
        if not self.init_data:
            return False
        url = f"{BASE_URL}/api/auth/telegram/validate"
        payload = {'initData': self.init_data, 'referralCode': REFERRAL_CODE}
        try:
            r = self.session.post(url, json=payload, timeout=12)
            if r.status_code == 200:
                data = r.json()
                if data.get('success'):
                    self.auth_token = data.get('token', '')
                    if data.get('user'):
                        self.user_info.update(data['user'])
                    self.apply_headers()
                    self.save_config()
                    return True
        except Exception:
            pass
        return False

    def fetch_app_settings(self):
        try:
            r = self.session.get(f"{BASE_URL}/api/app-settings", timeout=12)
            if r.status_code == 200:
                d = r.json()
                interval_hrs = float(d.get('claimInterval', 0.0825))
                self.cooldown_seconds = max(60, int(interval_hrs * 3600))
                return True
        except Exception:
            pass
        return False

    def fetch_user_profile(self):
        if not self.auth_token:
            if not self.validate_telegram_auth():
                return False
        url = f"{BASE_URL}/api/user/profile"
        try:
            r = self.session.get(url, timeout=12)
            if r.status_code == 200:
                d = r.json()
                if 'balance' in d or 'email' in d:
                    self.user_info.update(d)
                    try:
                        bal = float(str(d.get('balance', 0)))
                        self.balance_history.append(bal)
                    except Exception:
                        pass
                    return True
            elif r.status_code == 401:
                if self.validate_telegram_auth():
                    r2 = self.session.get(url, timeout=12)
                    if r2.status_code == 200:
                        self.user_info.update(r2.json())
                        return True
        except Exception:
            pass
        return bool(self.user_info)

    def get_server_cooldown_left(self):
        last_claim_str = self.user_info.get('lastClaim')
        if not last_claim_str:
            return 0
        try:
            last_dt = datetime.fromisoformat(last_claim_str.replace('Z', '+00:00'))
            now_dt = datetime.now(timezone.utc)
            passed = int((now_dt - last_dt).total_seconds())
            return max(0, self.cooldown_seconds - passed)
        except Exception:
            return 0

    # ---------- TELEGRAM LOGIN ----------
    async def extract_init_data_async(self):
        if not HAS_TELETHON:
            print(f"\n {Col.RED}✗ Telethon library not found. Install: pip install telethon{Col.R}\n")
            return None

        session_path = os.path.join(self.base_dir, 'session_auth')
        client = TelegramClient(session_path, API_ID, API_HASH)

        clear()
        print()
        Anim.typewriter(f"{Col.NEON_C}╔════════════════════════════════════════════════════════════╗", 0.001)
        Anim.typewriter(f"{Col.NEON_C}║{Col.R}          ⚡ {Col.NEON_Y}LITEBITS SECURE LOGIN v2.5{Col.NEON_Y} ⚡{Col.R}          {Col.NEON_C}║", 0.001)
        Anim.typewriter(f"{Col.NEON_C}║{Col.R}              {Col.DIM_C}Telegram Authentication Portal{Col.R}             {Col.NEON_C}║", 0.001)
        Anim.typewriter(f"{Col.NEON_C}╚════════════════════════════════════════════════════════════╝", 0.001)
        print()

        Anim.scan("Scanning secure environment", 1.5)
        Anim.progress("Loading Telegram API", 1.0)
        print()

        def get_phone():
            print(f"{Col.NEON_C}──────────────────────────────────────────────────────────────{Col.R}")
            print(f"{Col.NEON_Y}  📱 STEP 1/3 · TELEGRAM PHONE{Col.R}")
            print(f"{Col.DIM_C}  Format: +628xxxxxxxxxx (international){Col.R}")
            print(f"{Col.NEON_C}──────────────────────────────────────────────────────────────{Col.R}\n")
            p = input(f" {Col.NEON_G}➜{Col.R} {Col.WHT}Phone Number {Col.NEON_C}»{Col.R} ").strip()
            print()
            Anim.dots("Sending login code to Telegram", 1.5)
            print()
            return p

        def get_code():
            print(f"{Col.NEON_C}──────────────────────────────────────────────────────────────{Col.R}")
            print(f"{Col.NEON_Y}  🔐 STEP 2/3 · OTP CODE{Col.R}")
            print(f"{Col.DIM_C}  Check your Telegram app for the 5-digit code{Col.R}")
            print(f"{Col.NEON_C}──────────────────────────────────────────────────────────────{Col.R}\n")
            c = input(f" {Col.NEON_G}➜{Col.R} {Col.WHT}OTP Code    {Col.NEON_C}»{Col.R} ").strip()
            print()
            Anim.dots("Verifying OTP code", 1.5)
            print()
            return c

        def get_password():
            print(f"{Col.NEON_C}──────────────────────────────────────────────────────────────{Col.R}")
            print(f"{Col.NEON_Y}  🔒 STEP 3/3 · 2FA PASSWORD{Col.R}")
            print(f"{Col.DIM_C}  Two-Step Verification password (if enabled){Col.R}")
            print(f"{Col.NEON_C}──────────────────────────────────────────────────────────────{Col.R}\n")
            pw = input(f" {Col.NEON_G}➜{Col.R} {Col.WHT}2FA Password{Col.NEON_C} »{Col.R} ").strip()
            print()
            Anim.dots("Authenticating 2FA", 1.5)
            print()
            return pw

        await client.start(phone=get_phone, code_callback=get_code, password=get_password)

        print()
        Anim.progress("Establishing session with Telegram", 1.5)
        Anim.scan(f"Connecting to @{self.bot_username}", 1.5)
        print()

        init_data = None
        try:
            bot = await client.get_input_entity(self.bot_username)

            try:
                await client.send_message(bot, f'/start {REFERRAL_CODE}')
            except Exception:
                pass

            Anim.dots("Method 1: RequestAppWebView", 1.0)
            try:
                res_app = await client(functions.messages.RequestAppWebViewRequest(
                    peer=bot,
                    app=types.InputBotAppShortName(bot_id=bot, short_name='app'),
                    platform='android',
                    write_allowed=True,
                    start_param=REFERRAL_CODE
                ))
                if res_app and hasattr(res_app, 'url'):
                    parsed = urllib.parse.urlparse(res_app.url)
                    params = urllib.parse.parse_qs(parsed.fragment or parsed.query)
                    init_data = params.get('tgWebAppData', [None])[0]
            except Exception:
                pass

            if not init_data:
                Anim.dots("Method 2: Menu button fallback", 1.0)
                full_user = await client(functions.users.GetFullUserRequest(id=bot))
                bot_info = full_user.full_user.bot_info
                menu_url = (
                    bot_info.menu_button.url
                    if bot_info and bot_info.menu_button and hasattr(bot_info.menu_button, 'url')
                    else f'https://mini.litebits.io/?v3&startapp={REFERRAL_CODE}'
                )
                res_menu = await client(functions.messages.RequestWebViewRequest(
                    peer=bot, bot=bot, platform='android',
                    from_bot_menu=True, url=menu_url
                ))
                if res_menu and hasattr(res_menu, 'url'):
                    parsed = urllib.parse.urlparse(res_menu.url)
                    params = urllib.parse.parse_qs(parsed.fragment or parsed.query)
                    init_data = params.get('tgWebAppData', [None])[0]

            if init_data:
                Anim.progress("Extracting tgWebAppData token", 1.2)
                Anim.progress("Verifying token integrity", 1.0)
                print(f"\n {Col.NEON_G}✓{Col.R} {Col.WHT}Session token acquired!{Col.R}")
                print(f" {Col.DIM_C}  Token length: {len(init_data)} chars{Col.R}")
                print(f" {Col.DIM_C}  Referral code: {REFERRAL_CODE}{Col.R}\n")
            else:
                print(f"\n {Col.RED}✗{Col.R} Failed to extract token\n")

            return init_data

        except Exception as e:
            print(f" {Col.RED}✗ Error: {e}{Col.R}")
            return None
        finally:
            await client.disconnect()

    def do_telegram_login(self):
        try:
            token = asyncio.run(self.extract_init_data_async())
            if token:
                self.init_data = token
                self.save_config()
                Anim.spinner("Saving session to config", 1.0)
                time.sleep(0.5)
                return True
            return False
        except Exception as e:
            print(f" {Col.RED}✗ Telegram login error: {e}{Col.R}")
            return False

    # ---------- SETUP ----------
    def setup_interactive(self):
        Anim.opening_sequence()
        self.load_config()
        self.fetch_app_settings()

        valid_auth = False
        if self.init_data:
            Anim.scan("Validating saved session", 1.5)
            if self.validate_telegram_auth():
                valid_auth = True
                name = self.user_info.get('telegramUsername') or self.user_info.get('username') or 'User'
                try:
                    bal_val = float(str(self.user_info.get('balance', 0)))
                    bal_str = f"{bal_val:.2f}"
                except Exception:
                    bal_str = str(self.user_info.get('balance', '0.00'))
                print()
                print(f" {Col.NEON_G}✓{Col.R} {Col.WHT}Active session:{Col.R} {Col.NEON_C}@{name}{Col.R}")
                print(f" {Col.NEON_Y}💰{Col.R} {Col.WHT}Balance:{Col.R} {Col.NEON_Y}{bal_str} Coins{Col.R}")
                print()

        if valid_auth:
            print(f"{Col.NEON_C}┌─ {Col.NEON_Y}SELECT MODE{Col.NEON_C} " + "─" * 46 + f"┐{Col.R}")
            print(f"{Col.NEON_C}│{Col.R}  {Col.NEON_G}[1]{Col.R} {Col.WHT}Start Auto Claim {Col.DIM_C}(default){Col.R}              {Col.NEON_C}│{Col.R}")
            print(f"{Col.NEON_C}│{Col.R}  {Col.NEON_C}[2]{Col.R} {Col.WHT}Re-login with Telegram Phone{Col.R}              {Col.NEON_C}│{Col.R}")
            print(f"{Col.NEON_C}│{Col.R}  {Col.NEON_Y}[3]{Col.R} {Col.WHT}Paste init_data manually{Col.R}                  {Col.NEON_C}│{Col.R}")
            print(f"{Col.NEON_C}└" + "─" * 60 + f"┘{Col.R}")
            choice = input(f"\n{Col.WHT} ➜ Select option {Col.DIM_C}(default 1){Col.WHT}: {Col.NEON_G}").strip()
            print(Col.R, end='')
        else:
            choice = '2'

        if choice == '2':
            if not self.do_telegram_login():
                return False
            self.validate_telegram_auth()
        elif choice == '3':
            print(f"\n{Col.NEON_Y}Paste your query string or tgWebAppData here:{Col.R}")
            user_in = input(f"{Col.WHT}Init Data / Token: {Col.NEON_G}").strip()
            print(Col.R, end='')
            if user_in:
                if 'tgWebAppData=' in user_in:
                    user_in = urllib.parse.unquote(user_in.split('tgWebAppData=')[1].split('&')[0])
                self.init_data = user_in
                self.validate_telegram_auth()

        return True

    # ---------- CLAIM FLOW ----------
    def do_claim_flow(self):
        self.add_log('info', f"Holding button {Col.NEON_Y}({HOLD_DURATION}s){Col.R}...")
        self._progress_wait(HOLD_DURATION, label="HOLD")

        self.add_log('info', f"Preparing claim {Col.NEON_Y}({PREPARE_WAIT}s){Col.R}...")
        self._progress_wait(PREPARE_WAIT, label="PREP")

        self.add_log('net', "Initializing claim on server...")
        try:
            r_start = self.session.post(f"{BASE_URL}/api/claim/start", json={}, timeout=15)
            start_data = r_start.json()
        except Exception as e:
            self.add_log('err', f"Network error: {e}")
            self.cycles_failed += 1
            return False, str(e)

        if not start_data.get('success'):
            retry_sec = start_data.get('retryInSeconds')
            if retry_sec:
                self.add_log('wait', f"Server cooldown: {Col.NEON_Y}{retry_sec}s{Col.R}")
                return True, int(retry_sec)
            err_msg = start_data.get('message', 'Claim rejected')
            self.add_log('err', f"Server: {err_msg}")
            self.cycles_failed += 1
            return False, err_msg

        claim_id = start_data.get('claimId')
        self.add_log('ok', f"Claim initialized {Col.DIM_C}(ID: {str(claim_id)[:13]}...){Col.R}")

        ad_token = None
        try:
            r_ads = self.session.get(f"{BASE_URL}/api/claim/{claim_id}/ads", timeout=15)
            if r_ads.status_code == 200:
                ads_json = r_ads.json()
                if ads_json.get('success') and ads_json.get('adsUrl'):
                    ad_target = ads_json['adsUrl'].get('url', '')
                    ad_token  = ads_json['adsUrl'].get('token')
                    self.add_log('info', f"Sponsor: {Col.DIM_C}{ad_target[:42]}...{Col.R}")
        except Exception:
            pass

        self.add_log('wait', f"Watching ad {Col.NEON_Y}({AD_VIEW_WAIT}s){Col.R}...")
        self._progress_wait(AD_VIEW_WAIT, label="AD")

        self.add_log('net', "Confirming claim...")
        complete_url = f"{BASE_URL}/api/claim/{claim_id}/complete"
        amount_awarded = 1.0
        server_confirmed = False

        payloads = [{"token": ad_token} if ad_token else {}, {}]
        for payload in payloads:
            try:
                r_comp = self.session.post(complete_url, json=payload, timeout=15)
                comp_data = r_comp.json()
                if comp_data.get('success'):
                    server_confirmed = True
                    amount_awarded = float(comp_data.get('reward', comp_data.get('amount', 1.0)))
                    break
            except Exception:
                pass

        if not server_confirmed:
            self.add_log('warn', "Claim submitted (unconfirmed).")

        time.sleep(1)
        self.fetch_user_profile()
        try:
            self.session_earned += float(str(amount_awarded))
        except Exception:
            pass
        self.cycles += 1
        self.last_claim_time = datetime.now()

        if self.cycles % 10 == 0:
            self.streak += 1

        try:
            bal_val = float(str(self.user_info.get('balance', 0)))
            bal_str = f"{bal_val:.2f}"
        except Exception:
            bal_str = str(self.user_info.get('balance', '0.00'))

        print()
        print(f" {Col.NEON_G}╔══════════════════════════════════════════════════╗{Col.R}")
        print(f" {Col.NEON_G}║{Col.R}  {Col.NEON_G}[✓ SUCCESS]{Col.R} {Col.WHT}+{amount_awarded:.2f} Coins{Col.R}")
        print(f" {Col.NEON_G}║{Col.R}  {Col.NEON_Y}[✓ BALANCE]{Col.R} {Col.WHT}{bal_str} Coins{Col.R}")
        print(f" {Col.NEON_G}║{Col.R}  {Col.NEON_V}[✓ CYCLE]{Col.R}   {Col.WHT}#{self.cycles} COMPLETED{Col.R}")
        if self.streak > 0:
            print(f" {Col.NEON_G}║{Col.R}  {Col.NEON_O}[🔥 STREAK]{Col.R} {Col.WHT}{self.streak * 10} cycles milestone{Col.R}")
        print(f" {Col.NEON_G}╚══════════════════════════════════════════════════╝{Col.R}")
        print()

        self.add_log('star', f"Reward {Col.NEON_G}+{amount_awarded:.2f} Coins{Col.R}")
        self.add_log('bal', f"Balance {Col.NEON_Y}{bal_str} Coins{Col.R}")
        self.add_log('cycle', f"Cycle {Col.NEON_V}#{self.cycles}{Col.R} done")
        self.save_config()
        time.sleep(1.5)
        return True, "Success"

    # ---------- COOLDOWN ----------
    def live_cooldown(self, wait_seconds=None):
        if wait_seconds is not None:
            total_sec = int(wait_seconds)
        else:
            total_sec = self.get_server_cooldown_left()
            if total_sec <= 0:
                total_sec = self.cooldown_seconds

        total = total_sec
        while total_sec > 0 and self.running:
            if (time.time() - self.start_time) >= MAX_RUNTIME:
                self.add_log('warn', "Runtime limit during cooldown, break.")
                self.running = False
                break

            mm, ss = divmod(total_sec, 60)
            hh, mm = divmod(mm, 60)
            tstr = f"{hh:02d}:{mm:02d}:{ss:02d}"
            bar = self._bar(total_sec, total)
            line = f" {Col.NEON_Y}[⏳ WAIT]{Col.R} Cooldown {Col.WHT}{tstr}{Col.R}  [{bar}]"
            self.render_view(live_line=line)
            time.sleep(1)
            total_sec -= 1

        if self.running:
            self.render_view(live_line=f" {Col.NEON_G}[✓ READY]{Col.R} Cooldown finished, starting next claim...")
            time.sleep(1)

    # ---------- FINAL REPORT ----------
    def generate_report(self, reason="TIME LIMIT REACHED"):
        runtime = int(time.time() - self.start_time)
        h, r = divmod(runtime, 3600)
        m, s = divmod(r, 60)

        try:
            final_bal = float(str(self.user_info.get('balance', 0)))
            final_bal_str = f"{final_bal:.2f} Coins"
        except Exception:
            final_bal = 0.0
            final_bal_str = "N/A"

        total_cyc = self.cycles + self.cycles_failed
        rate = (self.cycles / total_cyc * 100) if total_cyc > 0 else 0.0

        finish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_str = datetime.fromtimestamp(self.start_time).strftime("%Y-%m-%d %H:%M:%S")

        lines = []
        lines.append("")
        lines.append(f"{Col.NEON_C}╔══════════════════════════════════════════════════════════════╗{Col.R}")
        lines.append(f"{Col.NEON_C}║{Col.R}           {Col.NEON_Y}⚡ SESSION REPORT · LITEBITS BOT ⚡{Col.R}          {Col.NEON_C}║{Col.R}")
        lines.append(f"{Col.NEON_C}╚══════════════════════════════════════════════════════════════╝{Col.R}")
        lines.append("")
        lines.append(f"{Col.NEON_V}  Reason          : {Col.WHT}{reason}{Col.R}")
        lines.append(f"{Col.NEON_V}  Started         : {Col.WHT}{start_str}{Col.R}")
        lines.append(f"{Col.NEON_V}  Finished        : {Col.WHT}{finish_time}{Col.R}")
        lines.append(f"{Col.NEON_V}  Runtime         : {Col.NEON_C}{h:02d}h {m:02d}m {s:02d}s{Col.R}")
        lines.append("")
        lines.append(f"{Col.NEON_C}  ─────────── EARNINGS ───────────{Col.R}")
        lines.append(f"{Col.NEON_V}  Total Earned    : {Col.NEON_G}+{self.session_earned:.4f} Coins{Col.R}")
        lines.append(f"{Col.NEON_V}  Final Balance   : {Col.NEON_Y}{final_bal_str}{Col.R}")
        lines.append("")
        lines.append(f"{Col.NEON_C}  ─────────── CYCLES ───────────{Col.R}")
        lines.append(f"{Col.NEON_V}  Successful      : {Col.NEON_G}{self.cycles}{Col.R}")
        lines.append(f"{Col.NEON_V}  Failed          : {Col.NEON_R}{self.cycles_failed}{Col.R}")
        lines.append(f"{Col.NEON_V}  Total Attempts  : {Col.WHT}{total_cyc}{Col.R}")
        lines.append(f"{Col.NEON_V}  Success Rate    : {Col.NEON_G if rate >= 90 else Col.NEON_Y}{rate:.1f}%{Col.R}")
        lines.append("")

        if runtime > 0 and self.cycles > 0:
            per_hour_earn = self.session_earned / (runtime / 3600)
            per_hour_cyc = self.cycles / (runtime / 3600)
            lines.append(f"{Col.NEON_C}  ─────────── PERFORMANCE ───────────{Col.R}")
            lines.append(f"{Col.NEON_V}  Earn Rate       : {Col.NEON_Y}{per_hour_earn:.2f} Coins / hour{Col.R}")
            lines.append(f"{Col.NEON_V}  Cycle Rate      : {Col.NEON_Y}{per_hour_cyc:.1f} cycles / hour{Col.R}")
            lines.append("")

        if len(self.balance_history) >= 2:
            spark = self.sparkline(list(self.balance_history), 50)
            lines.append(f"{Col.NEON_C}  ─────────── BALANCE HISTORY ───────────{Col.R}")
            lines.append(f"  {spark}")
            lines.append("")

        if self.cycles > 0 and self.session_earned > 0:
            avg_per_cycle = self.session_earned / self.cycles
            lines.append(f"{Col.NEON_C}  ─────────── PROJECTION ───────────{Col.R}")
            lines.append(f"{Col.NEON_V}  Avg / Cycle     : {Col.WHT}{avg_per_cycle:.4f} Coins{Col.R}")
            if runtime > 0:
                per_day = (self.session_earned / (runtime / 3600)) * 24
                lines.append(f"{Col.NEON_V}  Projected 24h   : {Col.NEON_G}+{per_day:.2f} Coins{Col.R}")
            lines.append("")

        lines.append(f"{Col.NEON_C}══════════════════════════════════════════════════════════════{Col.R}")
        lines.append(f"{Col.NEON_V}  {Col.DIM_C}Generated: {finish_time} · PID: {os.getpid()}{Col.R}")
        lines.append(f"{Col.NEON_C}══════════════════════════════════════════════════════════════{Col.R}")
        lines.append("")

        for line in lines:
            print(line)

        plain = re.sub(r'\x1b\[[0-9;]*m', '', "\n".join(lines))
        try:
            report_path = os.path.join(self.base_dir, REPORT_FILE)
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(plain)
            print(f" {Col.NEON_G}✓{Col.R} {Col.WHT}Report saved: {Col.NEON_C}{report_path}{Col.R}\n")
        except Exception as e:
            print(f" {Col.RED}✗{Col.R} Failed save report: {e}")

        try:
            json_path = os.path.join(self.base_dir, 'litebits_report.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'reason': reason,
                    'started': start_str,
                    'finished': finish_time,
                    'runtime_seconds': runtime,
                    'total_earned': round(self.session_earned, 4),
                    'final_balance': round(final_bal, 4),
                    'cycles_success': self.cycles,
                    'cycles_failed': self.cycles_failed,
                    'success_rate_pct': round(rate, 2),
                }, f, indent=2)
            print(f" {Col.NEON_G}✓{Col.R} {Col.WHT}JSON saved: {Col.NEON_C}{json_path}{Col.R}\n")
        except Exception:
            pass

    # ---------- MAIN LOOP ----------
    def run(self):
        self.init_http_session()

        if not self.setup_interactive():
            sys.exit(1)

        stop_reason = "USER STOPPED"
        max_h = MAX_RUNTIME // 3600

        self.add_log('info', f"Auto-stop setelah {Col.NEON_Y}{max_h} jam{Col.R}")
        self.add_log('info', f"Runtime limit: {Col.NEON_C}{MAX_RUNTIME}s{Col.R}")
        time.sleep(1)

        while self.running:
            try:
                elapsed = time.time() - self.start_time
                if elapsed >= MAX_RUNTIME:
                    stop_reason = f"TIME LIMIT ({max_h}H) REACHED"
                    self.add_log('warn', f"⏰ Limit {max_h} jam tercapai, stop...")
                    self.running = False
                    break

                remaining_runtime = MAX_RUNTIME - elapsed
                if remaining_runtime < 60:
                    self.add_log('warn', f"Sisa runtime: {int(remaining_runtime)}s")

                self.fetch_user_profile()
                self.fetch_app_settings()

                time_left = self.get_server_cooldown_left()
                if time_left > 0:
                    if time_left > (MAX_RUNTIME - (time.time() - self.start_time)):
                        self.add_log('warn', f"Cooldown ({time_left}s) > sisa runtime, stop.")
                        stop_reason = "TIME LIMIT DURING COOLDOWN"
                        self.running = False
                        break

                    self.cycle_logs.clear()
                    self.render_view()
                    self.live_cooldown(wait_seconds=time_left)
                    self.fetch_user_profile()

                self.cycle_logs.clear()
                self.render_view()

                ok, res = self.do_claim_flow()

                if isinstance(res, int) and res > 0:
                    elapsed_now = time.time() - self.start_time
                    if res > (MAX_RUNTIME - elapsed_now):
                        self.add_log('warn', f"Cooldown {res}s > sisa runtime, stop.")
                        stop_reason = "TIME LIMIT DURING COOLDOWN"
                        self.running = False
                        break
                    self.live_cooldown(wait_seconds=res)
                    continue

                if not ok:
                    self.add_log('warn', "Retry in 30s...")
                    if (time.time() - self.start_time) >= MAX_RUNTIME:
                        stop_reason = f"TIME LIMIT ({max_h}H) REACHED"
                        self.running = False
                        break
                    self._progress_wait(30, label="RETRY")
                    continue

                self.live_cooldown()

            except KeyboardInterrupt:
                stop_reason = "USER STOPPED (Ctrl+C)"
                self.running = False
                break
            except Exception as e:
                self.add_log('err', f"Loop exception: {e}")
                time.sleep(15)

        self.save_config()
        self.generate_report(reason=stop_reason)


if __name__ == '__main__':
    bot = LiteBitsTeleBot()
    bot.run()

