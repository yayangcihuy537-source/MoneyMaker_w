#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pitcoin Drop — Auto Farmer v7
Pure infinite cycle: BOOST → CLAIM → DOUBLE → repeat
Stop hanya kalau expired / error / user Ctrl+C
"""

import os
import sys
import time
import random
import shutil
import threading
from datetime import datetime

import requests


class C:
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    DIM     = "\033[2m"
    BOLD    = "\033[1m"
    RESET   = "\033[0m"
    HIDE    = "\033[?25l"
    SHOW    = "\033[?25h"
    CLEAR   = "\033[2J\033[H"


def tw(): return shutil.get_terminal_size((80, 20)).columns
def th(): return shutil.get_terminal_size((80, 20)).lines
def hide(): sys.stdout.write(C.HIDE); sys.stdout.flush()
def show(): sys.stdout.write(C.SHOW); sys.stdout.flush()
def clear(): sys.stdout.write(C.CLEAR); sys.stdout.flush()


# ============================================================
#  MATRIX
# ============================================================
MATRIX_CHARS = "01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン"
MATRIX_COLORS = [
    "\033[38;5;22m", "\033[38;5;28m", "\033[38;5;34m",
    "\033[38;5;40m", "\033[38;5;46m", "\033[38;5;82m",
]


class MatrixRain:
    def __init__(self):
        self.w = tw(); self.h = th()
        self.cols = [random.randint(-self.h, 0) for _ in range(self.w)]
        self.speeds = [random.choice([1, 1, 2]) for _ in range(self.w)]
        self.running = False
        self._tick = 0

    def _frame(self):
        self.w = tw(); self.h = th()
        if len(self.cols) < self.w:
            self.cols += [random.randint(-self.h, 0) for _ in range(self.w - len(self.cols))]
            self.speeds += [random.choice([1, 1, 2]) for _ in range(self.w - len(self.speeds))]
        buf = []
        for i in range(self.w):
            y = self.cols[i]
            if 1 <= y <= self.h:
                ch = random.choice(MATRIX_CHARS)
                col = random.choice(MATRIX_COLORS)
                buf.append(f"\033[{y};{i+1}H{col}{ch}{C.RESET}")
            if 2 <= y - 1 <= self.h:
                ch2 = random.choice(MATRIX_CHARS)
                buf.append(f"\033[{y-1};{i+1}H\033[38;5;22m{ch2}{C.RESET}")
            if self._tick % self.speeds[i] == 0:
                self.cols[i] += 2
            if self.cols[i] > self.h + 3:
                self.cols[i] = random.randint(-20, 0)
        sys.stdout.write("".join(buf))
        sys.stdout.flush()
        self._tick += 1

    def _loop(self):
        while self.running:
            self._frame()
            time.sleep(0.03)

    def start(self):
        if self.running: return
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False
        time.sleep(0.15)


matrix = MatrixRain()


def intro_animation():
    clear(); hide(); matrix.start()
    lines = [
        "",
        f"{C.GREEN}{C.BOLD}  ██████╗ ██╗████████╗ ██████╗ ██████╗ ██╗███╗   ██╗{C.RESET}",
        f"{C.GREEN}{C.BOLD}  ██╔══██╗██║╚══██╔══╝██╔════╝██╔═══██╗██║████╗  ██║{C.RESET}",
        f"{C.CYAN}{C.BOLD}  ██████╔╝██║   ██║   ██║     ██║   ██║██║██╔██╗ ██║{C.RESET}",
        f"{C.CYAN}{C.BOLD}  ██╔═══╝ ██║   ██║   ██║     ██║   ██║██║██║╚██╗██║{C.RESET}",
        f"{C.CYAN}{C.BOLD}  ██║     ██║   ██║   ╚██████╗╚██████╔╝██║██║ ╚████║{C.RESET}",
        f"{C.CYAN}{C.BOLD}  ╚═╝     ╚═╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝{C.RESET}",
        "",
        f"{C.DIM}           [ AUTO FARMER v7 — by Kyriel ]{C.RESET}",
        "",
    ]
    row = max(2, th() // 2 - len(lines) // 2)
    for i, ln in enumerate(lines):
        sys.stdout.write(f"\033[{row+i};1H{ln}")
    sys.stdout.flush()
    time.sleep(1.6)
    matrix.stop(); time.sleep(0.15)


def spin(text="Loading", dur=1.0):
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    start = time.time(); i = 0
    while time.time() - start < dur:
        sys.stdout.write(f"\r  {C.GREEN}{frames[i%len(frames)]}{C.RESET} {C.CYAN}{text}{C.RESET}...")
        sys.stdout.flush(); time.sleep(0.06); i += 1
    sys.stdout.write("\r" + " " * 70 + "\r"); sys.stdout.flush()


def countdown(seconds, label="WATCHING AD"):
    width = 30; total = max(seconds, 1)
    for s in range(total + 1):
        ratio = s / total
        filled = int(width * ratio)
        bar = "█" * filled + "░" * (width - filled)
        rem = total - s
        mm, ss = divmod(rem, 60)
        sys.stdout.write(
            f"\r  {C.MAGENTA}▶ {label}{C.RESET} "
            f"{C.GREEN}[{bar}]{C.RESET} {C.CYAN}{mm:02d}:{ss:02d}{C.RESET} left"
        )
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 80 + "\r"); sys.stdout.flush()


# ============================================================
#  CONFIG
# ============================================================
CFG = {
    "api_base":         "https://api.pitcoindrop.com",
    "origin":           "https://play.pitcoindrop.com",
    "user_agent":       ("Mozilla/5.0 (Linux; Android 16; K) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/152.0.7977.87 Mobile Safari/537.36 "
                         "Telegram-Android/12.9.2"),
    "boost_ad_sec":     30,     # durasi watch boost ad
    "double_ad_sec":    30,     # durasi watch double ad
    "cycle_delay":      1,      # jeda mini antar siklus (biar nggak spam)
    "user_refresh":     15,
}


def validate_init(s):
    return s and len(s) > 50 and "user=" in s and "hash=" in s


def ask_init_data():
    show(); clear()
    w = min(tw(), 62)
    print(f"\n{C.GREEN}{'═'*w}{C.RESET}")
    print(f"{C.GREEN}{C.BOLD}  🔑 MASUKIN INIT DATA TELEGRAM{C.RESET}")
    print(f"{C.GREEN}{'═'*w}{C.RESET}\n")
    print(f"  {C.DIM}DevTools → Network → copy header{C.RESET} "
          f"{C.YELLOW}x-telegram-init-data{C.RESET}\n")
    while True:
        val = input(f"  {C.BOLD}{C.GREEN}init_data > {C.RESET}").strip().strip('"').strip("'")
        if not val:
            print(f"  {C.RED}✗ kosong.{C.RESET}"); continue
        if not validate_init(val):
            print(f"  {C.RED}✗ format salah.{C.RESET}"); continue
        return val


# ============================================================
#  HTTP
# ============================================================
class FatalError(Exception):
    pass


class HTTP:
    def __init__(self, init):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "*/*",
            "content-type": "application/json",
            "origin": CFG["origin"],
            "referer": CFG["origin"] + "/",
            "x-requested-with": "org.telegram.messenger.web",
            "x-telegram-init-data": init,
            "user-agent": CFG["user_agent"],
        })

    def req(self, path, method="GET", body=None, retries=2):
        url = CFG["api_base"] + path
        for a in range(retries):
            try:
                r = self.session.request(method, url, json=body, timeout=15)

                if r.status_code in (401, 403):
                    raise FatalError(f"HTTP {r.status_code} pada {path}")

                if r.status_code == 200:
                    try: return r.json()
                    except: return {"raw": r.text}

                if r.status_code in (429, 502, 503, 504):
                    time.sleep(2 ** a); continue

                raise FatalError(f"HTTP {r.status_code} pada {path}")
            except requests.RequestException as e:
                if a >= retries - 1:
                    raise FatalError(f"Network error: {e}")
                time.sleep(2)
        return None


# ============================================================
#  BOT
# ============================================================
class PitcoinBot:
    def __init__(self, http):
        self.http = http
        self.user = {}
        self.balance = 0.0
        self.bucket = 0.0
        self.capacity = 0.0
        self.bucket_full = False
        self.boost_active = False
        self.boost_ms = 0

        self.claims = 0
        self.doubles = 0
        self.earned = 0.0
        self.boosts = 0
        self.fails = 0
        self.cycles = 0

        self.started = time.time()
        self.last_claim = "—"
        self.last_boost = "—"

        self.logs = []
        self.expired = False

    def log(self, msg, color=C.WHITE):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"{C.DIM}[{ts}]{C.RESET} {color}{msg}{C.RESET}")
        self.logs = self.logs[-7:]

    def get_user(self):
        d = self.http.req("/api/user")
        if not d: return False
        if not d.get("success"): return False
        u, m = d.get("user", {}), d.get("miningState", {})
        self.user = u
        self.balance = u.get("claimedPITBalance", 0.0)
        self.bucket = m.get("currentBucketValue", 0.0)
        self.capacity = m.get("bucketCapacity", 0.0)
        self.bucket_full = m.get("isBucketFull", False)
        self.boost_active = m.get("isAdBoostActive", False)
        self.boost_ms = m.get("adBoostTimeRemainingMs", 0)
        return True

    def claim(self, is_ad=False, mult=1.0):
        d = self.http.req("/api/mine/claim", "POST",
                          {"multiplier": mult, "isAdClaim": is_ad})
        if not d:
            self.fails += 1
            return False
        if d.get("success"):
            amt = d.get("claimedAmount", 0)
            bal = d.get("newBalance", self.balance)
            self.balance = bal
            self.claims += 1
            if is_ad:
                self.doubles += 1
            self.earned += amt
            self.last_claim = datetime.now().strftime("%H:%M:%S")
            tag = "DOUBLE" if is_ad else "CLAIM"
            self.log(f"✓ {tag} +{amt:.4f} PIT (x{mult})", C.GREEN)
            return True
        return False

    def overclock(self):
        d = self.http.req("/api/boost/overclock", "POST")
        if not d: return False
        if d.get("success"):
            self.boosts += 1
            self.last_boost = datetime.now().strftime("%H:%M:%S")
            rem = d.get("remainingMs", 0) // 1000
            hh, rr = divmod(rem, 3600); mm, ss = divmod(rr, 60)
            self.log(f"⚡ BOOST OK — stack {hh:02d}:{mm:02d}:{ss:02d}", C.MAGENTA)
            return True
        msg = d.get("message", "cooldown")
        self.log(f"⚠ boost: {msg}", C.YELLOW)
        return False

    def render(self):
        clear()
        w = min(tw(), 62)
        bar_w = min(46, w - 20)

        print(f"{C.GREEN}{'═' * w}{C.RESET}")
        print(f"{C.GREEN}{C.BOLD}  🪙 PITCOIN — LIVE DASHBOARD {C.DIM}[v7]{C.RESET}")
        print(f"{C.GREEN}{'═' * w}{C.RESET}")

        print(f"  {C.GREEN}👤 USER     {C.RESET}: {C.CYAN}{self.user.get('username','—')}{C.RESET}")
        print(f"  {C.GREEN}💰 BALANCE  {C.RESET}: {C.YELLOW}{self.balance:.4f} PIT{C.RESET}")

        pct = (self.bucket / self.capacity * 100) if self.capacity else 0
        filled = int(bar_w * min(self.bucket / self.capacity, 1.0)) if self.capacity else 0
        bbar = "█" * filled + "░" * (bar_w - filled)
        bcol = C.GREEN if pct > 60 else C.YELLOW if pct > 30 else C.RED
        print(f"  {C.GREEN}⛏️  BUCKET   {C.RESET}: {bcol}[{bbar}]{C.RESET} {pct:5.1f}%")

        full_txt = (f"{C.GREEN}✓ FULL{C.RESET}"
                    if self.bucket_full else f"{C.DIM}mining...{C.RESET}")
        print(f"  {C.GREEN}📦 STATUS   {C.RESET}: {full_txt}")

        if self.boost_active:
            bm = self.boost_ms // 1000
            mm, ss = divmod(bm, 60)
            boost_txt = f"{C.MAGENTA}⚡ ACTIVE — {mm:02d}:{ss:02d}{C.RESET}"
        else:
            boost_txt = f"{C.DIM}idle{C.RESET}"
        print(f"  {C.GREEN}🚀 BOOST    {C.RESET}: {boost_txt}")

        print(f"  {C.GREEN}🔁 CYCLES   {C.RESET}: {C.CYAN}{self.cycles}{C.RESET}")
        print(f"  {C.GREEN}📊 CLAIMS   {C.RESET}: {C.CYAN}{self.claims}{C.RESET}")
        print(f"  {C.GREEN}💎 EARNED   {C.RESET}: {C.GREEN}{self.earned:.4f} PIT{C.RESET}")
        print(f"  {C.GREEN}🔥 BOOSTS   {C.RESET}: {C.MAGENTA}{self.boosts}{C.RESET}")
        print(f"  {C.GREEN}⚠️  FAILS    {C.RESET}: {C.RED}{self.fails}{C.RESET}")

        rt = int(time.time() - self.started)
        h, rem = divmod(rt, 3600); m, s = divmod(rem, 60)
        print(f"  {C.GREEN}⏱️  RUNTIME  {C.RESET}: {h:02d}:{m:02d}:{s:02d}")
        print(f"  {C.GREEN}🕐 LAST CLAIM{C.RESET}: {self.last_claim}")
        print(f"  {C.GREEN}🕐 LAST BOOST{C.RESET}: {self.last_boost}")

        print(f"{C.DIM}{'─' * w}{C.RESET}")
        print(f"{C.BOLD}  📜 LIVE LOGS{C.RESET}")
        print(f"{C.DIM}{'─' * w}{C.RESET}")
        if self.logs:
            for e in self.logs: print("  " + e)
        else:
            print(f"  {C.DIM}(belum ada aktivitas){C.RESET}")
        print(f"{C.GREEN}{'═' * w}{C.RESET}")
        print(f"  {C.DIM}Ctrl+C untuk stop{C.RESET}")

    # ============================================================
    #  MAIN LOOP — PURE INFINITE CYCLE
    # ============================================================
    def run(self):
        hide()
        self.log("Auto-farm START — pure cycle", C.GREEN)

        try:
            while True:
                self.cycles += 1

                # ==========================================
                #  [1/3] BOOST
                # ==========================================
                self.render()
                print(f"\n  {C.MAGENTA}{C.BOLD}▶ [1/3] BOOST AD ({CFG['boost_ad_sec']}s){C.RESET}\n")
                countdown(CFG["boost_ad_sec"], "📺 BOOST AD")
                self.overclock()

                # ==========================================
                #  REFRESH
                # ==========================================
                if not self.get_user():
                    raise FatalError("Gagal refresh user")

                # ==========================================
                #  [2/3] CLAIM / [3/3] DOUBLE
                # ==========================================
                self.render()
                if self.bucket_full:
                    print(f"\n  {C.MAGENTA}{C.BOLD}▶ [3/3] DOUBLE AD ({CFG['double_ad_sec']}s){C.RESET}\n")
                    countdown(CFG["double_ad_sec"], "📺 DOUBLE AD")
                    self.claim(is_ad=True, mult=1.5)
                else:
                    print(f"\n  {C.YELLOW}{C.BOLD}▶ [2/3] CLAIM biasa{C.RESET}\n")
                    self.claim(is_ad=False, mult=1.0)

                self.render()
                time.sleep(CFG["cycle_delay"])

        except FatalError as e:
            self.expired = True
            self.log(f"✗ STOP: {e}", C.RED)
        except KeyboardInterrupt:
            pass
        finally:
            show()
            clear()
            self.render()


# ============================================================
#  MAIN
# ============================================================
def run_session(init_data):
    clear()
    spin("Booting", 0.6)
    spin("Validating", 0.6)

    http = HTTP(init_data)
    bot = PitcoinBot(http)

    try:
        if not bot.get_user():
            show(); clear()
            print(f"{C.RED}✗ init_data invalid / expired.{C.RESET}")
            return True
    except FatalError as e:
        show(); clear()
        print(f"{C.RED}✗ {e}{C.RESET}")
        return True

    print(f"{C.GREEN}✓ Login: {C.CYAN}{bot.user.get('username','—')}{C.RESET}")
    time.sleep(1)

    try:
        bot.run()
    except KeyboardInterrupt:
        return False

    return bot.expired


def main():
    intro_animation()

    init_data = ask_init_data()

    while True:
        expired = run_session(init_data)

        if not expired:
            show(); clear()
            print(f"\n{C.GREEN}✓ Selesai. Bye, Bos.{C.RESET}\n")
            sys.exit(0)

        show(); clear()
        print(f"\n{C.YELLOW}⚠ init_data EXPIRED. Paste yang baru buat lanjut.{C.RESET}\n")
        time.sleep(1)

        init_data = ask_init_data()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        show(); clear()
        print(f"\n{C.YELLOW}⚠ Dihentikan user.{C.RESET}\n")
