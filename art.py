#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
⛏️  ART MINING BOT v1.0
- Auto start mining
- Auto watch ads (10/day, 10 ATF each)
- Auto stop kalau abis
- Animation + summary
- ScriptMaker: @MoneyMaker_w
"""

import os
import sys
import time
import json
import random
import urllib.parse
import requests
from datetime import datetime

# ============================================================
# COLORS + ANIM
# ============================================================
CLEAR = '\033[K'
G = '\033[92m'
Y = '\033[93m'
R = '\033[91m'
C = '\033[96m'
M = '\033[95m'
W = '\033[97m'
BOLD = '\033[1m'
DIM = '\033[2m'
RST = '\033[0m'
NG = '\033[38;5;46m'
NC = '\033[38;5;51m'
NY = '\033[38;5;226m'
NP = '\033[38;5;201m'
NO = '\033[38;5;208m'

BANNER = f"""{NY}{BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║      █████╗ ██████╗ ████████╗    ███╗   ███╗██╗███╗   ██╗      ║
║     ██╔══██╗██╔══██╗╚══██╔══╝    ████╗ ████║██║████╗  ██║      ║
║     ███████║██████╔╝   ██║       ██╔████╔██║██║██╔██╗ ██║      ║
║     ██╔══██║██╔══██╗   ██║       ██║╚██╔╝██║██║██║╚██╗██║      ║
║     ██║  ██║██║  ██║   ██║       ██║ ╚═╝ ██║██║██║ ╚████║      ║
║     ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝       ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝      ║
║                                                                  ║
║  {NY}⛏️  ART MINING BOT  {NC}│ {NG}v1.0 {NC}│ {NP}Auto Mining + Ads{RST}{NY}            ║
║                                                                  ║
║  {NG}▸ Bot     : {NC}@ART_AIRDROP_BOT{RST}{NY}                            ║
║  {NG}▸ Script  : {NC}@MoneyMaker_w{RST}{NY}                               ║
║  {NG}▸ Channel : {NC}https://t.me/ScriptyXSouu{RST}{NY}                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{RST}
"""

INIT_FILE = "art_init.txt"
BASE = "https://art.tamimdev.dev/api"

# ============================================================
# ANIMATIONS
# ============================================================
class Anim:
    @staticmethod
    def spinner(text, duration=1.5):
        frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        end = time.time() + duration
        i = 0
        while time.time() < end:
            sys.stdout.write('\r' + CLEAR + f" {NC}{frames[i%10]}{RST} {W}{text}{RST}")
            sys.stdout.flush()
            time.sleep(0.08); i += 1
        sys.stdout.write('\r' + CLEAR + f" {NG}✓{RST} {W}{text}{RST}\n")
        sys.stdout.flush()

    @staticmethod
    def dots(text, duration=1.5):
        end = time.time() + duration
        n = 0
        while time.time() < end:
            d = "." * ((n % 3) + 1)
            sys.stdout.write('\r' + CLEAR + f" {NC}•{RST} {W}{text}{NC}{d:<4}{RST}")
            sys.stdout.flush()
            time.sleep(0.3); n += 1
        sys.stdout.write('\r' + CLEAR + f" {NG}✓{RST} {W}{text}{RST}\n")
        sys.stdout.flush()

    @staticmethod
    def watch_bar(label, provider, duration):
        spinner = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
        bar_len = 18
        start = time.time(); i = 0
        while True:
            elapsed = time.time() - start
            if elapsed >= duration: break
            pct = elapsed / duration
            filled = int(bar_len * pct)
            bar = '█' * filled + '░' * (bar_len - filled)
            rem = duration - elapsed
            row = (f"  {NP}{spinner[i%10]}{RST} {NC}{label:<9}{RST} "
                   f"{DIM}{provider:<10}{RST} "
                   f"{NG}[{bar}]{RST} {NY}{int(pct*100):3d}%{RST} {NY}{rem:4.1f}s{RST}")
            sys.stdout.write('\r' + CLEAR + row); sys.stdout.flush()
            time.sleep(0.1); i += 1
        sys.stdout.write('\r' + CLEAR); sys.stdout.flush()

    @staticmethod
    def glitch(text, duration=0.5):
        gc = "░▒▓█▄▀■□▪▫@#$%&*"
        end = time.time() + duration
        while time.time() < end:
            out = ''.join(random.choice(gc) if (random.randint(0,10)<2 and ch!=' ') else ch for ch in text)
            sys.stdout.write('\r' + CLEAR + f"  {NP}{out}{RST}")
            sys.stdout.flush(); time.sleep(0.06)
        sys.stdout.write('\r' + CLEAR + f"  {NC}{text}{RST}\n"); sys.stdout.flush()

    @staticmethod
    def typewriter(text, delay=0.015, color=None):
        c = color or W
        for ch in text:
            sys.stdout.write(f"{c}{ch}{RST}"); sys.stdout.flush()
            time.sleep(delay)
        print()

# ============================================================
# BOT
# ============================================================
class ArtMiningBot:
    def __init__(self):
        self.init_data = ""
        self.user_id = None
        self.username = None
        self.profile = {}
        self.settings = {}
        self.mining = {}
        self.stats = {
            "ads_watched": 0,
            "ads_earned": 0,
            "ads_failed": 0,
            "start_time": datetime.now()
        }
        self.session = requests.Session()
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "*/*",
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
            "Origin": "https://art.tamimdev.dev",
            "Referer": "https://art.tamimdev.dev/",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.session.headers.update(self.headers)
        self.load_init()

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def load_init(self):
        if os.path.exists(INIT_FILE):
            with open(INIT_FILE, 'r') as f:
                self.init_data = f.read().strip()
            self._parse()

    def save_init(self, data):
        with open(INIT_FILE, 'w') as f:
            f.write(data.strip())
        self.init_data = data.strip()
        self._parse()

    def _parse(self):
        try:
            p = urllib.parse.parse_qs(self.init_data)
            if 'user' in p:
                u = json.loads(p['user'][0])
                self.user_id = str(u.get('id'))
                self.username = u.get('username') or u.get('first_name', 'Unknown')
        except:
            pass

    # ============ API ============
    def _req(self, method, path, json_data=None, timeout=30):
        url = f"{BASE}{path}"
        headers = self.session.headers.copy()
        headers["x-telegram-init-data"] = self.init_data
        for attempt in range(3):
            try:
                if method.upper() == 'GET':
                    r = self.session.get(url, headers=headers, timeout=timeout)
                else:
                    r = self.session.post(url, headers=headers, json=json_data, timeout=timeout)
                if r.status_code == 429:
                    wait = int(r.headers.get('Retry-After', 5))
                    print(f"{Y}  ⚠️  Rate limit, tunggu {wait}s...{RST}")
                    time.sleep(wait); continue
                return r
            except requests.exceptions.Timeout:
                if attempt < 2: time.sleep(2); continue
                return None
            except Exception as e:
                print(f"{R}  ❌ {e}{RST}")
                return None
        return None

    # ============ USER ============
    def get_user(self):
        r = self._req('GET', f"/user/{self.user_id}")
        if not r or r.status_code != 200:
            return False
        try:
            j = r.json()
            self.profile = j.get('user', {})
            self.settings = j.get('settings', {})
            self.mining = j.get('miningState', {})
            return True
        except:
            return False

    def start_mining(self):
        r = self._req('POST', "/user/start-mining", {"userId": self.user_id})
        if not r or r.status_code != 200:
            return False
        try:
            j = r.json()
            if j.get('success'):
                self.profile = j.get('user', {})
                self.mining = j.get('miningState', {})
                return True
        except:
            pass
        return False

    # ============ ADS ============
    def ads_status(self):
        r = self._req('GET', f"/ads/status/{self.user_id}")
        if not r or r.status_code != 200:
            return None
        try:
            return r.json()
        except:
            return None

    def ads_claim(self):
        r = self._req('POST', "/ads/claim", {"userId": self.user_id})
        if not r or r.status_code != 200:
            return None
        try:
            j = r.json()
            if j.get('success'):
                self.profile = j.get('user', self.profile)
                return j
        except:
            pass
        return None

    # ============ MAIN FLOW ============
    def run(self):
        # Step 1: Fetch user
        Anim.dots("fetch user data", 1.5)
        if not self.get_user():
            print(f"{R}❌ Gagal fetch user data{RST}")
            return

        # Step 2: Check mining
        is_mining = self.mining.get('isMining', False)
        if is_mining:
            print(f"{NG}⛏️  Mining sudah aktif{RST}")
            print(f"{NC}   Elapsed  : {NY}{self.mining.get('elapsedSeconds', 0)}s{RST}")
            print(f"{NC}   Acc ATF  : {NY}{self.mining.get('accumulatedAtf', 0):.4f}{RST}")
            print(f"{NC}   Remaining: {NY}{self.mining.get('remainingSeconds', 0)}s{RST}")
        else:
            Anim.spinner("start mining", 1.5)
            if self.start_mining():
                print(f"{NG}⛏️  Mining aktivasi!{RST}")
                print(f"{NC}   Duration : {NY}8 jam{RST}")
                print(f"{NC}   Rate     : {NY}{self.mining.get('hourlyRate', 0)} ATF/jam{RST}")
            else:
                print(f"{Y}⚠️  Mining gagal diaktifkan (mungkin udah jalan){RST}")

        # Step 3: Show profile
        self._show_profile()

        # Step 4: Check ads status
        print()
        Anim.dots("check ads status", 1.0)
        ads = self.ads_status()
        if not ads:
            print(f"{R}❌ Gagal cek status ads{RST}")
            return

        if not ads.get('enabled'):
            print(f"{R}❌ Ads disabled{RST}")
            return

        remaining = ads.get('remaining', 0)
        limit = ads.get('limit', 10)
        reward = ads.get('rewardAtf', 10)

        print(f"\n{NC}╭─────────────────────────────────────────╮{RST}")
        print(f"{NC}│{RST} {NG}📺 Ads Available{RST}")
        print(f"{NC}│{RST} {NC}Watch count : {NG}{ads.get('watched', 0)}/{limit}{RST}")
        print(f"{NC}│{RST} {NC}Remaining   : {NG}{remaining}{RST}")
        print(f"{NC}│{RST} {NC}Reward each : {NY}{reward} ATF{RST}")
        print(f"{NC}╰─────────────────────────────────────────╯{RST}")

        if remaining <= 0:
            print(f"\n{Y}⏹ Semua ads sudah ditonton hari ini.{RST}")
            print(f"{NC}   Reset dalam: {NY}{ads.get('resetsInSeconds', 0) // 3600} jam{RST}")
            self._print_summary()
            return

        # Step 5: Watch ads
        print(f"\n{NY}🎬 MULAI WATCH ADS ({remaining}x tersisa){RST}")

        consecutive_fail = 0
        for i in range(1, remaining + 1):
            print(f"\n{NC}  ┌─ [{i:02d}/{remaining:02d}] Watch Ads{RST}")
            Anim.watch_bar("ADS", "gigapub", 5)

            res = self.ads_claim()
            if res:
                consecutive_fail = 0
                rew = res.get('reward', 0)
                watched = res.get('watched', 0)
                lim = res.get('limit', 10)
                rem_after = res.get('remaining', 0)
                self.stats['ads_watched'] += 1
                self.stats['ads_earned'] += rew

                print(f"{NG}  ✅ #{i:02d}: +{rew} ATF | today: {watched}/{lim} | remaining: {rem_after}{RST}")
                time.sleep(3)
            else:
                consecutive_fail += 1
                self.stats['ads_failed'] += 1
                print(f"{Y}  ⚠️  Ads claim gagal (attempt {consecutive_fail}/3){RST}")

                if consecutive_fail >= 3:
                    print(f"{R}  ❌ Ads limit/error 3x → STOP ads loop{RST}")
                    break
                time.sleep(5)

        # Step 6: Refresh
        print()
        Anim.dots("refresh profile", 1.5)
        self.get_user()
        self._print_summary()

    def _show_profile(self):
        p = self.profile
        s = self.settings
        print(f"\n{NC}╭─────────────────────────────────────────╮{RST}")
        print(f"{NC}│{RST} {NG}👤 Profile{RST}")
        print(f"{NC}│{RST} {NC}Username    : {W}@{p.get('username', 'N/A')}{RST}")
        print(f"{NC}│{RST} {NC}Level       : {W}{p.get('level', 1)}{RST}")
        print(f"{NC}│{RST} {NC}Holding     : {NY}{p.get('holdingWallet', 0):.4f} {s.get('tokenSymbol', 'ART')}{RST}")
        print(f"{NC}│{RST} {NC}Pool Wallet : {NY}{p.get('poolWallet', 0):.4f}{RST}")
        print(f"{NC}│{RST} {NC}Today PNL   : {NY}{p.get('todayPnl', 0):.4f}{RST}")
        print(f"{NC}│{RST} {NC}All-Time    : {NY}{p.get('allTimeMined', 0):.4f}{RST}")
        print(f"{NC}│{RST} {NC}Ads Watched : {W}{p.get('adsWatchedCount', 0)}/10{RST}")
        print(f"{NC}│{RST} {NC}ATF Price   : {NY}${s.get('atfPriceUsd', 0)}{RST}")
        print(f"{NC}╰─────────────────────────────────────────╯{RST}")

    def _print_summary(self):
        duration = (datetime.now() - self.stats['start_time']).total_seconds()
        print(f"\n{NC}{'═' * 55}{RST}")
        print(f"{NG}🏁 SESSION SUMMARY{RST}")
        print(f"{NC}{'═' * 55}{RST}")
        print(f"  {NG}📺 Ads watched  : {W}{self.stats['ads_watched']}{RST}")
        print(f"  {NY}💰 ATF earned   : {NG}{self.stats['ads_earned']}{RST}")
        print(f"  {R}❌ Ads failed   : {W}{self.stats['ads_failed']}{RST}")
        print(f"  {NC}⏱️  Duration     : {W}{int(duration//60)}m {int(duration%60)}s{RST}")
        p = self.profile
        if p:
            print(f"  {NG}💰 Holding      : {NY}{p.get('holdingWallet', 0):.4f} ART{RST}")
            print(f"  {NC}📈 All-time    : {NY}{p.get('allTimeMined', 0):.4f} ART{RST}")
        print(f"{NC}{'═' * 55}{RST}")

    # ============ MENU ============
    def menu(self):
        while True:
            self.clear()
            print(BANNER)
            if self.init_data:
                print(f"{NG}🔑 Status : {NG}SET ({self.init_data[:30]}...){RST}")
                if self.username:
                    print(f"{NC}👤 User   : {W}@{self.username}{RST}")
            else:
                print(f"{R}🔑 Status : {R}EMPTY{RST}")

            print(f"\n{NC}  [1] 🚀 Start (Auto Mining + Watch Ads)")
            print(f"  [2] 🔑 Set InitData")
            print(f"  [3] 👤 Check Profile")
            print(f"  {R}[0] 🚪 Exit{RST}")
            print(f"\n{NC}{'═' * 55}{RST}")

            c = input(f"  {NG}➜ {RST}").strip()

            if c == "1":
                if not self.init_data:
                    print(f"{R}❌ Set InitData dulu!{RST}")
                    time.sleep(2); continue
                print()
                Anim.glitch("ART MINING STARTED", 0.5)
                self.run()
                input(f"\n{NC}Enter untuk kembali...{RST}")

            elif c == "2":
                print(f"\n{Y}🔑 Masukkan initData (Enter untuk batal):{RST}")
                d = input(f"  {NG}➜ {RST}").strip()
                if d:
                    self.save_init(d)
                    print(f"{NG}✓ Saved! User: @{self.username}{RST}")
                time.sleep(1.5)

            elif c == "3":
                if not self.init_data:
                    continue
                Anim.dots("fetch profile", 1.5)
                if self.get_user():
                    self._show_profile()
                input(f"\n{NC}Enter...{RST}")

            elif c == "0":
                print(f"\n{NG}👋 Bye, bos.{RST}")
                break

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    try:
        os.system('cls' if os.name == 'nt' else 'clear')
        Anim.glitch("ART MINING BOT v1.0", 0.5)
        time.sleep(0.3)
        bot = ArtMiningBot()
        bot.menu()
    except KeyboardInterrupt:
        print(f"\n{R}⏹️  Stopped.{RST}")
    except Exception as e:
        print(f"\n{R}❌ Error: {e}{RST}")
        import traceback; traceback.print_exc()
        input(f"\n{NC}Enter...{RST}")
