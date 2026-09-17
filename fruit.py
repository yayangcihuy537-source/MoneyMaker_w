#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import urllib.parse
import time
import sys
import os
import random

# ============================================================
# WARNA + ANIMASI
# ============================================================
CLEAR = '\033[K'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'
DIM = '\033[2m'
RESET = '\033[0m'
NEON_G = '\033[38;5;46m'
NEON_C = '\033[38;5;51m'
NEON_Y = '\033[38;5;226m'
NEON_P = '\033[38;5;201m'
NEON_R = '\033[38;5;196m'

# =============================================================
#                  🌙 SLEEPY MINE 🌙
#                     ⛏️ SLEEPY MINE
#                  💎 AUTO MINING BOT 💎
# 🤖 BOT   : @MineSLPYBot
# 🔗 REF   : ref6894031790
# 🚀 START : t.me/MineSLPYBot?startapp=ref6894031790
# ScriptMaker : @MoneyMaker_w
# TG          : https://t.me/ScriptyXSouu
# =============================================================

API_URL = "https://sleepymine.xyz/api/db.php"

# Config
MAX_REGULAR_ADS = 100    # adjust sesuai limit server
MAX_TADDY_ADS   = 250    # limit Taddy (dari script awal)
DELAY_REGULAR   = 5      # jeda antar regular ads
DELAY_TADDY     = 7      # jeda antar taddy ads

# ============================================================
# ANIMATIONS
# ============================================================
class Anim:
    @staticmethod
    def spinner(text, duration=2):
        frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        end = time.time() + duration
        i = 0
        while time.time() < end:
            row = f" {NEON_C}{frames[i % 10]}{RESET} {WHITE}{text}{RESET}"
            sys.stdout.write('\r' + CLEAR + row); sys.stdout.flush()
            time.sleep(0.08); i += 1
        sys.stdout.write('\r' + CLEAR)
        sys.stdout.write(f" {NEON_G}✓{RESET} {WHITE}{text}{RESET}\n"); sys.stdout.flush()

    @staticmethod
    def dots(text, duration=2):
        end = time.time() + duration
        n = 0
        while time.time() < end:
            d = "." * ((n % 3) + 1)
            row = f" {NEON_C}•{RESET} {WHITE}{text}{NEON_C}{d:<4}{RESET}"
            sys.stdout.write('\r' + CLEAR + row); sys.stdout.flush()
            time.sleep(0.3); n += 1
        sys.stdout.write('\r' + CLEAR)
        sys.stdout.write(f" {NEON_G}✓{RESET} {WHITE}{text}{RESET}\n"); sys.stdout.flush()

    @staticmethod
    def progress(text, duration=2, width=28):
        end = time.time() + duration
        total = duration
        while time.time() < end:
            elapsed = duration - (end - time.time())
            pct = min(1.0, elapsed / total)
            filled = int(pct * width)
            bar = f"{NEON_G}{'█' * filled}{DIM}{'░' * (width - filled)}{RESET}"
            row = f" {NEON_C}▶{RESET} {WHITE}{text:<28}{RESET} [{bar}] {NEON_Y}{int(pct*100):>3}%{RESET}"
            sys.stdout.write('\r' + CLEAR + row); sys.stdout.flush()
            time.sleep(0.05)
        sys.stdout.write('\r' + CLEAR)
        sys.stdout.write(f" {NEON_G}✓{RESET} {WHITE}{text}{RESET}\n"); sys.stdout.flush()

    @staticmethod
    def ad_watch(label, provider, duration):
        """Countdown animasi pas nonton ads"""
        spinner = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
        bar_len = 18
        start = time.time(); i = 0
        while True:
            elapsed = time.time() - start
            if elapsed >= duration: break
            pct = elapsed / duration
            filled = int(bar_len * pct)
            bar = '█' * filled + '░' * (bar_len - filled)
            remaining = duration - elapsed
            row = (f"  {NEON_P}{spinner[i % 10]}{RESET} "
                   f"{NEON_C}{label:<10}{RESET} "
                   f"{DIM}{provider:<12}{RESET} "
                   f"{NEON_G}[{bar}]{RESET} "
                   f"{NEON_Y}{int(pct*100):3d}%{RESET} "
                   f"{NEON_Y}{remaining:4.1f}s{RESET}")
            sys.stdout.write('\r' + CLEAR + row); sys.stdout.flush()
            time.sleep(0.1); i += 1
        sys.stdout.write('\r' + CLEAR); sys.stdout.flush()

    @staticmethod
    def glitch(text, duration=0.5):
        gc = "░▒▓█▄▀■□▪▫@#$%&*"
        end = time.time() + duration
        while time.time() < end:
            out = ''.join(random.choice(gc) if (random.randint(0,10)<2 and ch!=' ') else ch for ch in text)
            sys.stdout.write('\r' + CLEAR + f"  {NEON_P}{out}{RESET}"); sys.stdout.flush()
            time.sleep(0.06)
        sys.stdout.write('\r' + CLEAR)
        sys.stdout.write(f"  {NEON_C}{text}{RESET}\n"); sys.stdout.flush()

    @staticmethod
    def typewriter(text, delay=0.015, color=None):
        c = color or WHITE
        for ch in text:
            sys.stdout.write(f"{c}{ch}{RESET}"); sys.stdout.flush()
            time.sleep(delay)
        print()

# ============================================================
# BANNER
# ============================================================
def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"""{NEON_Y}{BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  ███████╗██╗     ███████╗███████╗██████╗ ██╗   ██╗             ║
║  ██╔════╝██║     ██╔════╝██╔════╝██╔══██╗╚██╗ ██╔╝             ║
║  ███████╗██║     █████╗  █████╗  ██████╔╝ ╚████╔╝              ║
║  ╚════██║██║     ██╔══╝  ██╔══╝  ██╔═══╝   ╚██╔╝               ║
║  ███████║███████╗███████╗███████╗██║        ██║                ║
║  ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝        ╚═╝                ║
║                                                                  ║
║            {NEON_Y}🌙 SLEEPY MINE  •  {NEON_P}⛏️ AUTO MINING BOT  •  {NEON_G}v2.0{NEON_Y}            ║
║                                                                  ║
║  {NEON_G}🤖 BOT     : {NEON_C}@MineSLPYBot{NEON_Y}                                  ║
║  {NEON_G}🔗 REF     : {NEON_C}ref6894031790{NEON_Y}                                ║
║  {NEON_G}🚀 START   : {NEON_C}t.me/MineSLPYBot?startapp=ref6894031790{NEON_Y}     ║
║                                                                  ║
║  {WHITE}ScriptMaker : {NEON_C}@MoneyMaker_w{NEON_Y}                              ║
║  {WHITE}TG          : {NEON_C}https://t.me/ScriptyXSouu{NEON_Y}                 ║
║                                                                  ║
║                       {NEON_G}HAPPY MINING 🚀{NEON_Y}                       ║
╚══════════════════════════════════════════════════════════════════╝{RESET}
""")

# ============================================================
# API HELPERS
# ============================================================
def parse_init_data(init_data: str):
    params = urllib.parse.parse_qs(init_data)
    user_json = params.get('user', [None])[0]
    if not user_json:
        raise ValueError("user parameter not found in init_data")
    user_data = json.loads(user_json)
    return str(user_data.get('id')), user_data

def db_request(payload, init_data):
    headers = {
        'Content-Type': 'application/json',
        'x-telegram-init-data': init_data,
        'origin': 'https://sleepymine.xyz',
        'referer': 'https://sleepymine.xyz/',
        'x-requested-with': 'org.telegram.messenger.web',
        'user-agent': 'Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)'
    }
    try:
        resp = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        if resp.status_code != 200:
            return {"error": f"HTTP {resp.status_code}", "raw": resp.text[:200]}
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def get_user(uid, init_data):
    payload = {
        "table": "airdrop_users",
        "action": "select",
        "select": "*",
        "filters": [{"col": "uid", "op": "eq", "val": uid}],
        "order": None, "limit": None, "single": True, "payload": None
    }
    result = db_request(payload, init_data)
    return result.get('data')

def claim_mined(uid, init_data):
    for fn in ['claim_mined', 'claim', 'claim_reward']:
        result = db_request({"action": "rpc", "fn": fn, "args": {"uid": uid}}, init_data)
        if result and result.get('data') and result['data'].get('success'):
            return result['data']
    return None

# ========== ADS ENDPOINTS ==========
def watch_regular_ad(uid, init_data):
    """credit_ad_reward — regular ads (0.25 SLPY each)"""
    result = db_request({"action": "rpc", "fn": "credit_ad_reward", "args": {"uid": uid}}, init_data)
    if result and result.get('data') and result['data'].get('success'):
        return result['data']
    return None

def watch_taddy_ad(uid, init_data):
    """credit_taddy_ad_reward — Taddy ads (0.25 SLPY each, max 250/day)"""
    result = db_request({"action": "rpc", "fn": "credit_taddy_ad_reward", "args": {"uid": uid}}, init_data)
    if result and result.get('data') and result['data'].get('success'):
        return result['data']
    return None

# ============================================================
# MAIN LOGIC
# ============================================================
def run_regular_ads(uid, init_data):
    """Loop regular ads. Kalau limit/error, skip & return."""
    print(f"\n{NEON_C}🎞️  REGULAR ADS{NEON_Y}")
    print(f"{DIM}   Provider: adsgram_reward • reward 0.25 SLPY/ad{NEON_Y}")

    count = 0
    consecutive_errors = 0
    while count < MAX_REGULAR_ADS:
        # Animasi nonton
        Anim.ad_watch("REGULAR", "adsgram", 5)

        result = watch_regular_ad(uid, init_data)

        if not result or not result.get('success'):
            consecutive_errors += 1
            print(f"{YELLOW}  ⚠️  Regular ads limit/error (attempt {consecutive_errors}/3), skip...{RESET}")

            if consecutive_errors >= 3:
                print(f"{RED}  ❌ Regular ads HABIS / LIMIT. Lanjut ke Taddy.{RESET}")
                return count
            time.sleep(3)
            continue

        consecutive_errors = 0
        reward = result.get('reward', 0)
        points = result.get('points', 0)
        count = result.get('count', count + 1)
        print(f"{NEON_G}  ✅ #{count}: +{reward} SLPY | points: {points:.4f}{RESET}")

        if count >= MAX_REGULAR_ADS:
            print(f"{YELLOW}  ⏹  Cap {MAX_REGULAR_ADS} tercapai.{RESET}")
            break

        time.sleep(DELAY_REGULAR)

    return count

def run_taddy_ads(uid, init_data):
    """Loop Taddy ads. Kalau limit/error, skip & return."""
    print(f"\n{NEON_P}🎞️  TADDY ADS{NEON_Y}")
    print(f"{DIM}   Provider: taddy_reward • reward 0.25 SLPY/ad • max {MAX_TADDY_ADS}/hari{NEON_Y}")

    count = 0
    consecutive_errors = 0
    while count < MAX_TADDY_ADS:
        # Animasi nonton
        Anim.ad_watch("TADDY", "taddy", 5)

        result = watch_taddy_ad(uid, init_data)

        if not result or not result.get('success'):
            consecutive_errors += 1
            print(f"{YELLOW}  ⚠️  Taddy limit/error (attempt {consecutive_errors}/3), skip...{RESET}")

            if consecutive_errors >= 3:
                print(f"{RED}  ❌ Taddy HABIS / LIMIT. Stop ads loop.{RESET}")
                return count
            time.sleep(3)
            continue

        consecutive_errors = 0
        reward = result.get('reward', 0)
        points = result.get('points', 0)
        count = result.get('count', count + 1)
        print(f"{NEON_G}  ✅ Taddy #{count}: +{reward} SLPY | points: {points:.4f}{RESET}")

        if count >= MAX_TADDY_ADS:
            print(f"{YELLOW}  ⏹  Cap Taddy {MAX_TADDY_ADS} tercapai.{RESET}")
            break

        time.sleep(DELAY_TADDY)

    return count

# ============================================================
# MAIN
# ============================================================
def main():
    print_banner()

    init_data = input(f"\n{NEON_Y}Masukkan init_data (dari Telegram WebApp): {RESET}").strip()
    if not init_data:
        print(f"{RED}Init_data tidak boleh kosong!{RESET}")
        sys.exit(1)

    # Parse
    try:
        uid, user_info = parse_init_data(init_data)
        Anim.spinner(f"UID detected: {uid}", 1)
    except Exception as e:
        print(f"{RED}Gagal parse init_data: {e}{RESET}")
        sys.exit(1)

    # Get user
    Anim.dots("fetch user data", 1.5)
    user = get_user(uid, init_data)
    if not user:
        print(f"{RED}Gagal mendapatkan data user.{RESET}")
        sys.exit(1)

    # Display user info
    print(f"\n{NEON_C}╭{'─' * 60}╮{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}👤 Nama            :{RESET} {WHITE}{user.get('name', 'N/A')}{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}💰 Points          :{RESET} {NEON_Y}{user.get('points', 0):.4f} SLPY{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}⛏️  Mined Points   :{RESET} {WHITE}{user.get('mined_points', 0):.4f}{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}📊 Unclaimed       :{RESET} {WHITE}{user.get('unclaimed_mined', 0):.4f}{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}📺 Regular watCh   :{RESET} {WHITE}{user.get('ads_watched_count', 0)}{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}🎯 Taddy watched   :{RESET} {WHITE}{user.get('taddy_watched_count', 0)}{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}🚫 Banned          :{RESET} {WHITE}{user.get('banned', False)}{RESET}")
    print(f"{NEON_C}╰{'─' * 60}╯{RESET}")

    # Claim mined kalau ada
    if user.get('unclaimed_mined', 0) > 0:
        print()
        Anim.dots("claim mined", 1.5)
        cr = claim_mined(uid, init_data)
        if cr and cr.get('success'):
            print(f"{NEON_G}✓ Claim berhasil!{RESET}")
            user = get_user(uid, init_data) or user
            print(f"{NEON_C}  Points now: {NEON_Y}{user.get('points', 0):.4f} SLPY{RESET}")
        else:
            print(f"{YELLOW}⚠️  Claim gagal / tidak ada.{RESET}")
    else:
        print(f"\n{DIM}   Tidak ada unclaimed mined, skip.{RESET}")

    # Session start
    print(f"\n{NEON_Y}🚀 MULAI SESI ADS-WATCH{RESET}")
    saldo_awal = user.get('points', 0)

    # === Regular ads ===
    reg_count = run_regular_ads(uid, init_data)

    # === Taddy ads ===
    taddy_count = run_taddy_ads(uid, init_data)

    # === Refresh & summary ===
    Anim.dots("refresh user", 1.5)
    user_after = get_user(uid, init_data) or user
    gain = user_after.get('points', 0) - saldo_awal

    print(f"\n{NEON_G}✅ SESI SELESAI{RESET}")
    print(f"{NEON_C}╭{'─' * 60}╮{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}📺 Regular ads   :{RESET} {WHITE}{reg_count}{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}🎯 Taddy ads     :{RESET} {WHITE}{taddy_count}{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}💰 Gain sesi      :{RESET} {NEON_Y}+{gain:.4f} SLPY{RESET}")
    print(f"{NEON_C}│{RESET} {NEON_G}💰 Saldo akhir    :{RESET} {NEON_Y}{user_after.get('points', 0):.4f} SLPY{RESET}")
    print(f"{NEON_C}╰{'─' * 60}╯{RESET}")

    print(f"\n{NEON_P}🏁 Selesai! Bot selesai menjalankan perintah.{RESET}")
    print_banner()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}🛑 Bot dihentikan oleh user.{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{RED}❌ Error: {e}{RESET}")
        sys.exit(1)
