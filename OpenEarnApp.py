#!/usr/bin/env python3
"""
OpenEarnApp — ADS ONLY MODE (Hacker UI v4)
- Live real-time clock
- Visible countdown on wait
- Show ALL network status (remaining/cooldown/blocked)
- By Dev MoneyMaker_w
"""

import os
import sys
import requests
import time
import json
import random
import urllib.parse
import threading
from datetime import datetime, timedelta

# ============================================================
# ANSI
# ============================================================
R  = '\033[91m'
G  = '\033[92m'
Y  = '\033[93m'
C  = '\033[96m'
W  = '\033[97m'
BOLD = '\033[1m'
DIM  = '\033[2m'
RESET = '\033[0m'

N_GREEN  = '\033[38;5;46m'
N_CYAN   = '\033[38;5;51m'
N_PINK   = '\033[38;5;201m'
N_YELLOW = '\033[38;5;226m'
N_ORANGE = '\033[38;5;208m'
N_PURPLE = '\033[38;5;135m'
N_RED    = '\033[38;5;196m'
N_BLUE   = '\033[38;5;39m'

CLEAR_LINE = '\033[K'

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def cls_line():
    sys.stdout.write('\r' + CLEAR_LINE)
    sys.stdout.flush()

def matrix_rain(lines=5, width=60, duration=1.2):
    chars = list("01ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉ")
    start = time.time()
    canvas = [[' '] * width for _ in range(lines)]
    for _ in range(lines): print()
    while time.time() - start < duration:
        for _ in range(3):
            col = random.randint(0, width - 1)
            canvas[0][col] = random.choice(chars)
        for i in range(lines - 1, 0, -1):
            canvas[i] = canvas[i - 1][:]
        canvas[0] = [' '] * width
        sys.stdout.write(f"\033[{lines}A")
        for i, row in enumerate(canvas):
            color = N_GREEN if i < 1 else (G if i < 2 else DIM + G)
            sys.stdout.write(color + ''.join(row) + RESET + "\n")
        sys.stdout.flush()
        time.sleep(0.08)

def typing_text(text, color=N_CYAN, delay=0.015):
    sys.stdout.write('  ')
    for ch in text:
        sys.stdout.write(color + ch + RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def glitch_text(text, duration=0.5):
    gc = "░▒▓█▄▀■□▪▫@#$%&*"
    start = time.time()
    while time.time() - start < duration:
        out = ''.join(random.choice(gc) if (random.randint(0,10)<2 and ch!=' ') else ch for ch in text)
        cls_line()
        sys.stdout.write('  ' + N_PINK + out + RESET)
        sys.stdout.flush()
        time.sleep(0.06)
    cls_line()
    sys.stdout.write('  ' + N_CYAN + text + RESET + '\n')
    sys.stdout.flush()

def boot_sequence():
    steps = [
        "Initializing kernel module...",
        "Loading stealth headers...",
        "Rotating device fingerprint...",
        "Connecting to remote server...",
        "Session ready.",
    ]
    print()
    for s in steps:
        sys.stdout.write(f"  {N_GREEN}[✓]{RESET} {W}{s}{RESET}\n")
        sys.stdout.flush()
        time.sleep(random.uniform(0.06, 0.12))
    print(f"  {N_YELLOW}[⚡]{RESET} {W}Status: {N_GREEN}SECURE{RESET}")
    print(f"  {N_PINK}[★]{RESET} {W}Welcome, {N_CYAN}Operative{RESET}\n")
    time.sleep(0.6)

# ============================================================
# LIVE CLOCK
# ============================================================
class LiveClock:
    """Update clock di terminal setiap detik — background thread"""
    def __init__(self, y_offset=0):
        self.running = False
        self.thread = None
        self.y_offset = y_offset

    def _loop(self):
        while self.running:
            now = datetime.now().strftime("%H:%M:%S")
            sys.stdout.write(f"\033[s")  # save cursor
            sys.stdout.write(f"\033[{self.y_offset};52H")  # move to position
            sys.stdout.write(f"{N_YELLOW}{now}{RESET}")
            sys.stdout.write(f"\033[u")  # restore cursor
            sys.stdout.flush()
            time.sleep(1)

    def start(self):
        if self.running: return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

# ============================================================
# BANNER
# ============================================================
BANNER = f"""
{N_GREEN}{BOLD}  ███████╗ █████╗ ██████╗ ███╗   ██╗
  ██╔════╝██╔══██╗██╔══██╗████╗  ██║
  █████╗  ███████║██████╔╝██╔██╗ ██║
  ██╔══╝  ██╔══██║██╔══██╗██║╚██╗██║
  ███████╗██║  ██║██║  ██║██║ ╚████║
  ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝{RESET}

{N_CYAN}  ╔════════════════════════════════════════════╗
  ║ {N_YELLOW}📺  ADS ONLY  •  {N_PINK}8H MAX  •  {N_GREEN}HACKER MODE{N_CYAN} ║
  ╚════════════════════════════════════════════╝{RESET}

  {N_GREEN}▸ Dev     : {N_CYAN}MoneyMaker_w{RESET}
  {N_GREEN}▸ Channel : {N_CYAN}t.me/ScriptyXSouu{RESET}
  {DIM}  ────────────────────────────────────────────{RESET}
"""

# ============================================================
# KONFIG
# ============================================================
BASE_URL = "https://app.theopenearn.info/api"
AD_WATCH_DURATION = 30
MAX_RUNTIME_HOURS = 8
MAX_RUNTIME_SECONDS = MAX_RUNTIME_HOURS * 3600
COOLDOWN_BETWEEN_ADS = 3
COOLDOWN_WHEN_EMPTY = 120
COOLDOWN_BEFORE_CYCLE = 15    # jeda antar cycle walau masih ada ads

PROVIDER_CONFIG = {
    'adsgram':      {'ad_type': 'video',      'fallback': True},
    'monetag':      {'ad_type': 'impression', 'fallback': True},
    'telega':       {'ad_type': 'video',      'fallback': True},
    'richads':      {'ad_type': 'video',      'fallback': True},
    'onclicka':     {'ad_type': 'video',      'fallback': True},
    'taddy':        {'ad_type': 'video',      'fallback': True},
    'gigapub':      {'ad_type': 'video',      'fallback': True},
    'adsgram_task': {'ad_type': 'task',       'fallback': True},
}

# ============================================================
# BOT
# ============================================================
class OpenEarnAdsBot:
    def __init__(self, init_data, username=None):
        self.init_data = init_data
        self.username = username or self._extract_username(init_data)
        self.headers = {
            "authorization": f"tma {init_data}",
            "user-agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.2",
            "content-type": "application/json",
            "x-requested-with": "org.telegram.messenger",
            "accept": "*/*",
            "origin": "https://app.theopenearn.info",
            "referer": "https://app.theopenearn.info/"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        self.running = True
        self.balance = "0"
        self.tot_balance = "0"
        self.total_ads = 0
        self.total_ads_earned = 0.0
        self.total_ads_tot = 0.0
        self.success_ads_count = 0
        self.failed_ads_count = 0
        self.cycles = 0
        self.start_time = None
        self.providers_full = {}   # {name: {remaining, blocked, cooldown}}

    def _extract_username(self, init_data):
        try:
            parsed = dict(urllib.parse.parse_qsl(init_data))
            if 'user' in parsed:
                user = json.loads(urllib.parse.unquote(parsed['user']))
                return user.get('username') or user.get('first_name', 'Unknown')
            return "Unknown"
        except:
            return "Unknown"

    def elapsed_str(self):
        if not self.start_time: return "00:00:00"
        e = int((datetime.now() - self.start_time).total_seconds())
        return f"{e//3600:02d}:{(e%3600)//60:02d}:{e%60:02d}"

    def remaining_str(self):
        if not self.start_time: return f"{MAX_RUNTIME_HOURS:02d}:00:00"
        e = int((datetime.now() - self.start_time).total_seconds())
        r = max(0, MAX_RUNTIME_SECONDS - e)
        return f"{r//3600:02d}:{(r%3600)//60:02d}:{r%60:02d}"

    def get_user_info(self):
        try:
            resp = self.session.get(f"{BASE_URL}/user")
            if resp.status_code == 200:
                data = resp.json()
                self.balance = str(data.get('balance', '0'))
                self.tot_balance = str(data.get('tot_balance', '0'))
                return data
        except: pass
        return None

    def fetch_ads_status(self):
        """Ambil status lengkap semua network + return list ready"""
        try:
            resp = self.session.get(f"{BASE_URL}/ads/daily-status")
            if resp.status_code == 200:
                providers = resp.json().get('providers', {})
                self.providers_full = {}
                available = []
                for name, info in providers.items():
                    remaining = info.get('remaining', 0)
                    blocked = info.get('blocked', False)
                    cooldown = info.get('cooldown_remaining', 0)
                    self.providers_full[name] = {
                        'remaining': remaining,
                        'blocked': blocked,
                        'cooldown': cooldown
                    }
                    if remaining > 0 and not blocked and cooldown == 0:
                        available.append(name)
                return available
        except Exception as e:
            print(f"  {N_RED}⚠ fetch ads status error: {e}{RESET}")
        return None

    def _watch_animation(self, provider, duration):
        spinner = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
        bar_len = 20
        start = time.time()
        i = 0
        while True:
            elapsed = time.time() - start
            if elapsed >= duration or not self.running:
                break
            pct = elapsed / duration
            filled = int(bar_len * pct)
            bar = '█' * filled + '░' * (bar_len - filled)
            remaining = duration - elapsed
            row = (f"  {N_PINK}{spinner[i % len(spinner)]}{RESET} "
                   f"{N_CYAN}WATCH {provider.upper():<14}{RESET} "
                   f"{N_GREEN}[{bar}]{RESET} "
                   f"{N_YELLOW}{int(pct*100):3d}%{RESET} "
                   f"{N_ORANGE}{remaining:4.1f}s{RESET}")
            cls_line()
            sys.stdout.write(row)
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        cls_line()
        return True

    def complete_ad(self, provider):
        try:
            print(f"  {N_CYAN}┌─ {N_GREEN}▶ {provider.upper()}{RESET}")
            self._watch_animation(provider, AD_WATCH_DURATION)

            config = PROVIDER_CONFIG.get(provider, {'ad_type': 'video', 'fallback': True})
            payload = {
                "ad_type": config.get('ad_type', 'video'),
                "provider": provider,
                "watched": True,
                "fallback": config.get('fallback', True)
            }
            resp = self.session.post(f"{BASE_URL}/ads/complete", json=payload)

            if resp.status_code == 200:
                data = resp.json()
                reward = data.get('reward', 0)
                base_reward = data.get('base_reward', 0)
                bonus_reward = data.get('bonus_reward', 0)
                tot_reward = data.get('tot_reward', 0)
                new_balance = data.get('new_balance')
                is_bonus = data.get('is_bonus', False)
                ton_reward = reward if reward > 0 else (base_reward + bonus_reward)

                if new_balance: self.balance = str(new_balance)
                if tot_reward:  self.tot_balance = str(float(self.tot_balance) + tot_reward)

                self.total_ads += 1
                self.total_ads_earned += ton_reward
                self.total_ads_tot += tot_reward
                self.success_ads_count += 1

                if ton_reward > 0:
                    print(f"  {N_CYAN}│{RESET}  {N_GREEN}✓ {N_YELLOW}+{ton_reward} TON{RESET}  {N_CYAN}+{tot_reward} TOT{RESET}"
                          + (f"  {N_PINK}★ BONUS!{RESET}" if is_bonus else ""))
                else:
                    print(f"  {N_CYAN}│{RESET}  {N_GREEN}✓ TOT-only{RESET}  {N_CYAN}+{tot_reward} TOT{RESET}")
                print(f"  {N_CYAN}└{'─' * 55}{RESET}")
                return data
            else:
                self.failed_ads_count += 1
                print(f"  {N_CYAN}│{RESET}  {N_RED}✗ HTTP {resp.status_code}{RESET}")
                print(f"  {N_CYAN}└{'─' * 55}{RESET}")
                return None
        except Exception as e:
            self.failed_ads_count += 1
            print(f"  {N_CYAN}│{RESET}  {N_RED}✗ ERROR: {str(e)[:45]}{RESET}")
            print(f"  {N_CYAN}└{'─' * 55}{RESET}")
            return None

    def _visible_sleep(self, seconds, label="WAITING"):
        """Countdown live biar keliatan bot gak stuck"""
        spinner = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
        i = 0
        start = time.time()
        while time.time() - start < seconds and self.running:
            elapsed = time.time() - start
            remaining = seconds - elapsed
            bar_len = 20
            pct = elapsed / seconds
            filled = int(bar_len * pct)
            bar = '█' * filled + '░' * (bar_len - filled)
            row = (f"  {N_PURPLE}{spinner[i % len(spinner)]}{RESET} "
                   f"{N_CYAN}{label:<12}{RESET} "
                   f"{N_GREEN}[{bar}]{RESET} "
                   f"{N_YELLOW}{int(pct*100):3d}%{RESET} "
                   f"{N_ORANGE}{remaining:5.1f}s{RESET}")
            cls_line()
            sys.stdout.write(row)
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        cls_line()

    def _status_network_panel(self):
        """Tampilkan status semua network — kenapa cuma N yang ready"""
        print(f"  {N_CYAN}┌─ {N_GREEN}📡 NETWORK STATUS{N_CYAN} ───────────────────────────┐{RESET}")
        for name in sorted(self.providers_full.keys()):
            info = self.providers_full[name]
            remaining = info['remaining']
            blocked = info['blocked']
            cooldown = info['cooldown']

            if blocked:
                icon = f"{N_RED}⛔ BLOCKED{RESET}"
                detail = ""
            elif remaining <= 0:
                icon = f"{N_ORANGE}✗ HABIS{RESET}"
                detail = f"{DIM}(0 left){RESET}"
            elif cooldown > 0:
                icon = f"{N_YELLOW}⏳ CD {int(cooldown)}s{RESET}"
                detail = f"{N_CYAN}{remaining} left{RESET}"
            else:
                icon = f"{N_GREEN}✓ READY{RESET}"
                detail = f"{N_CYAN}{remaining} left{RESET}"

            line = f"  {N_CYAN}│{RESET}  {name:<15} {icon:<20} {detail}"
            print(line)
        print(f"  {N_CYAN}└{'─' * 55}{RESET}")

    def run(self):
        self.running = True
        self.start_time = datetime.now()
        deadline = self.start_time + timedelta(seconds=MAX_RUNTIME_SECONDS)

        print(f"  {N_GREEN}🚀 {BOLD}ADS-ONLY LOOP STARTED{RESET}")
        print(f"  {DIM}Auto-stop after {MAX_RUNTIME_HOURS}h ({deadline.strftime('%H:%M:%S')}){RESET}")
        print(f"  {DIM}Ctrl+C to stop manually{RESET}\n")
        time.sleep(1.5)

        while self.running:
            if datetime.now() >= deadline:
                print(f"\n  {N_YELLOW}⏰ 8 HOURS REACHED — AUTO-STOP{RESET}")
                self.running = False
                break

            self.cycles += 1
            cycle_start = datetime.now()
            cycle_ads = 0
            cycle_ton = 0.0
            cycle_tot = 0.0

            clear_screen()
            print(BANNER)

            # ── CYCLE HEADER dengan live clock di kanan ──
            clock = LiveClock(y_offset=20)  # baris 20 (setelah banner)
            print(f"  {N_CYAN}╔════════════════════════════════════════════╗{RESET}")
            print(f"  {N_CYAN}║{RESET} {N_GREEN}🔄 CYCLE #{self.cycles}{RESET}"
                  f"{' ' * (22 - len(str(self.cycles)))}"
                  f"{N_YELLOW}{cycle_start.strftime('%H:%M:%S')}{N_CYAN} ║{RESET}")
            print(f"  {N_CYAN}╠════════════════════════════════════════════╣{RESET}")
            print(f"  {N_CYAN}║{RESET}  {N_CYAN}⏱  Elapsed  : {N_GREEN}{self.elapsed_str()}{RESET}"
                  f"{' ' * (18)}{N_CYAN}║{RESET}")
            print(f"  {N_CYAN}║{RESET}  {N_ORANGE}⏳ Remaining: {N_YELLOW}{self.remaining_str()}{RESET}"
                  f"{' ' * (18)}{N_CYAN}║{RESET}")
            print(f"  {N_CYAN}║{RESET}  {N_PURPLE}💰 Balance  : {N_YELLOW}{self.balance} TON{RESET}"
                  f"{' ' * max(0, 24 - len(str(self.balance)))}{N_CYAN}║{RESET}")
            print(f"  {N_CYAN}╚════════════════════════════════════════════╝{RESET}\n")

            # ── FETCH ADS ──
            print(f"  {N_CYAN}┌─ {N_GREEN}📺 AVAILABLE ADS{N_CYAN} ──────────────────────────┐{RESET}")
            available = self.fetch_ads_status()

            if not available:
                print(f"  {N_CYAN}│{RESET}  {N_YELLOW}⚠ Semua network HABIS / cooldown{RESET}")
                print(f"  {N_CYAN}└{'─' * 55}{RESET}\n")

                # Tampilkan status lengkap
                self._status_network_panel()
                print()

                # Visible countdown wait
                print(f"  {N_CYAN}⏳ Menunggu {COOLDOWN_WHEN_EMPTY}s sebelum cek ulang...{RESET}")
                self._visible_sleep(COOLDOWN_WHEN_EMPTY, "WAIT")
                continue

            print(f"  {N_CYAN}│{RESET}  {N_YELLOW}▶ Found    : {N_GREEN}{len(available)}{RESET}")
            print(f"  {N_CYAN}│{RESET}  {N_YELLOW}▶ Ready    : {N_CYAN}{', '.join(available)}{RESET}")
            print(f"  {N_CYAN}└{'─' * 55}{RESET}\n")

            # ── STATUS PANEL (kenapa cuma N yang ready) ──
            self._status_network_panel()
            print()

            # ── PROCESS ADS ──
            for provider in available:
                if not self.running or datetime.now() >= deadline:
                    break
                result = self.complete_ad(provider)
                if result:
                    cycle_ads += 1
                    r = result.get('reward', 0)
                    t = result.get('tot_reward', 0)
                    cycle_ton += r if r > 0 else (result.get('base_reward', 0) + result.get('bonus_reward', 0))
                    cycle_tot += t
                time.sleep(COOLDOWN_BETWEEN_ADS)

            # ── CYCLE SUMMARY ──
            dur = int((datetime.now() - cycle_start).total_seconds())
            print(f"\n  {N_CYAN}┌─ {N_GREEN}✓ CYCLE #{self.cycles} DONE{RESET}  {DIM}({dur}s){RESET}")
            print(f"  {N_CYAN}│{RESET}  {N_GREEN}📺 Ads Success : {N_GREEN}{cycle_ads}{RESET}")
            print(f"  {N_CYAN}│{RESET}  {N_YELLOW}💰 TON Earned  : {N_GREEN}+{cycle_ton:.8f} TON{RESET}")
            print(f"  {N_CYAN}│{RESET}  {N_CYAN}💎 TOT Earned  : {N_CYAN}+{cycle_tot} TOT{RESET}")
            print(f"  {N_CYAN}│{RESET}  {N_ORANGE}⏳ Time Left   : {N_YELLOW}{self.remaining_str()}{RESET}")
            print(f"  {N_CYAN}└{'─' * 55}{RESET}\n")

            print(f"  {N_PURPLE}💰 Current Balance : {N_GREEN}{self.balance} TON{RESET}")
            print(f"  {N_PURPLE}💎 Current TOT     : {N_CYAN}{self.tot_balance}{RESET}\n")

            # Refresh balance dari server
            self.get_user_info()

            # Visible wait sebelum cycle berikutnya
            print(f"  {N_CYAN}⏳ Cooldown sebelum cycle berikutnya...{RESET}")
            self._visible_sleep(COOLDOWN_BEFORE_CYCLE, "NEXT CYCLE")

        self._print_final_summary()

    def _print_final_summary(self):
        print(f"\n  {N_CYAN}╔════════════════════════════════════════════╗{RESET}")
        print(f"  {N_CYAN}║{RESET}  {N_GREEN}{BOLD}🏁 FINAL SUMMARY{RESET}{' ' * 28}{N_CYAN}║{RESET}")
        print(f"  {N_CYAN}╠════════════════════════════════════════════╣{RESET}")
        print(f"  {N_CYAN}║{RESET}  {N_YELLOW}Total Cycles   : {N_GREEN}{self.cycles}{RESET}")
        print(f"  {N_CYAN}║{RESET}  {N_YELLOW}Runtime        : {N_GREEN}{self.elapsed_str()}{RESET}")
        print(f"  {N_CYAN}║{RESET}  {N_YELLOW}Total Ads      : {N_GREEN}{self.total_ads}{RESET}")
        print(f"  {N_CYAN}║{RESET}  {N_YELLOW}Ads Success    : {N_GREEN}{self.success_ads_count}{RESET}")
        print(f"  {N_CYAN}║{RESET}  {N_YELLOW}Ads Failed     : {N_RED}{self.failed_ads_count}{RESET}")
        print(f"  {N_CYAN}║{RESET}  {N_YELLOW}TON Earned     : {N_GREEN}{self.total_ads_earned:.8f} TON{RESET}")
        print(f"  {N_CYAN}║{RESET}  {N_YELLOW}TOT Earned     : {N_CYAN}{self.total_ads_tot} TOT{RESET}")
        print(f"  {N_CYAN}║{RESET}  {N_YELLOW}Final Balance  : {N_GREEN}{self.balance} TON{RESET}")
        print(f"  {N_CYAN}╚════════════════════════════════════════════╝{RESET}\n")

# ============================================================
# MENU
# ============================================================
def menu(bot):
    while True:
        clear_screen()
        print(BANNER)
        print(f"  {N_CYAN}┌─ {N_GREEN}ACCOUNT{N_CYAN} ───────────────────────────────────┐{RESET}")
        print(f"  {N_CYAN}│{RESET}  {N_GREEN}👤 Username : {N_CYAN}{bot.username}{RESET}")
        print(f"  {N_CYAN}│{RESET}  {N_GREEN}💰 Balance  : {N_YELLOW}{bot.balance} TON{RESET}")
        print(f"  {N_CYAN}│{RESET}  {N_GREEN}💎 TOT      : {N_CYAN}{bot.tot_balance}{RESET}")
        print(f"  {N_CYAN}└{'─' * 44}{RESET}")
        print()
        print(f"  {N_GREEN}[{N_YELLOW}1{N_GREEN}]{RESET}  {N_CYAN}🚀 Start ADS-ONLY Loop {DIM}(8h max){RESET}")
        print(f"  {N_GREEN}[{N_YELLOW}2{N_GREEN}]{RESET}  {N_CYAN}💰 Check Balance{RESET}")
        print(f"  {N_GREEN}[{N_YELLOW}3{N_GREEN}]{RESET}  {N_CYAN}📺 Available Ads + Status{RESET}")
        print(f"  {N_GREEN}[{N_YELLOW}4{N_GREEN}]{RESET}  {N_CYAN}📊 Statistics{RESET}")
        print(f"  {N_RED}[{N_YELLOW}0{N_RED}]{RESET}  {N_RED}❌ Exit{RESET}")
        print()
        print(f"  {DIM}────────────────────────────────────────────{RESET}")

        choice = input(f"  {N_GREEN}OpenEarn › {RESET}").strip()

        if choice == "1":
            bot.running = True
            bot.run()
            input(f"\n  {N_CYAN}Press Enter to return...{RESET}")
        elif choice == "2":
            bot.get_user_info()
            print(f"\n  {N_GREEN}💰 Balance : {N_YELLOW}{bot.balance} TON{RESET}")
            print(f"  {N_GREEN}💎 TOT     : {N_CYAN}{bot.tot_balance}{RESET}")
            input(f"\n  {N_CYAN}Press Enter...{RESET}")
        elif choice == "3":
            available = bot.fetch_ads_status()
            print()
            if available:
                print(f"  {N_GREEN}✓ Ready ({len(available)}):{RESET}")
                for ad in available:
                    print(f"    {N_CYAN}● {ad.upper()}{RESET}")
            else:
                print(f"  {N_YELLOW}Tidak ada ads tersedia.{RESET}")
            print()
            bot._status_network_panel()
            input(f"\n  {N_CYAN}Press Enter...{RESET}")
        elif choice == "4":
            print(f"\n  {N_GREEN}{BOLD}📊 STATISTICS{RESET}")
            print(f"  {N_YELLOW}Cycles        : {N_GREEN}{bot.cycles}{RESET}")
            print(f"  {N_YELLOW}Runtime       : {N_GREEN}{bot.elapsed_str()}{RESET}")
            print(f"  {N_YELLOW}Total Ads     : {N_GREEN}{bot.total_ads}{RESET}")
            print(f"  {N_YELLOW}Success       : {N_GREEN}{bot.success_ads_count}{RESET}")
            print(f"  {N_YELLOW}Failed        : {N_RED}{bot.failed_ads_count}{RESET}")
            print(f"  {N_YELLOW}TON Earned    : {N_GREEN}{bot.total_ads_earned:.8f}{RESET}")
            print(f"  {N_YELLOW}TOT Earned    : {N_CYAN}{bot.total_ads_tot}{RESET}")
            input(f"\n  {N_CYAN}Press Enter...{RESET}")
        elif choice == "0":
            bot.running = False
            print(f"\n  {N_GREEN}👋 Bye, boss.{RESET}")
            break
        else:
            print(f"  {N_RED}❌ Invalid!{RESET}")
            time.sleep(1)

# ============================================================
# MAIN
# ============================================================
def main():
    clear_screen()
    matrix_rain(lines=5, width=60, duration=1.2)
    print()
    typing_text(">>> OpenEarnApp ADS-ONLY v4.0", N_CYAN, 0.015)
    glitch_text("HACKER EDITION", 0.5)
    print()
    boot_sequence()
    time.sleep(0.5)

    clear_screen()
    print(BANNER)

    print(f"  {N_CYAN}┌─ {N_GREEN}📌 CARA MENDAPATKAN INIT DATA{N_CYAN} ────────────────┐{RESET}")
    print(f"  {N_CYAN}│{RESET}  {W}1. Buka bot The Open Earn di Telegram{RESET}")
    print(f"  {N_CYAN}│{RESET}  {W}2. DevTools (F12) → Tab Network{RESET}")
    print(f"  {N_CYAN}│{RESET}  {W}3. Cari request ke '/api/user'{RESET}")
    print(f"  {N_CYAN}│{RESET}  {W}4. Copy header 'authorization' (tanpa 'tma '){RESET}")
    print(f"  {N_CYAN}└{'─' * 44}{RESET}")

    init_data = input(f"\n  {N_GREEN}🔑 Init data: {RESET}").strip()
    if not init_data:
        print(f"  {N_RED}❌ Init data kosong!{RESET}")
        return
    if init_data.startswith('tma '):
        init_data = init_data[4:]

    username = input(f"  {N_GREEN}📛 Nama (enter auto): {RESET}").strip() or None
    bot = OpenEarnAdsBot(init_data, username)
    menu(bot)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {N_RED}⏹️  Stopped by user.{RESET}")
    except Exception as e:
        print(f"\n  {N_RED}❌ Error: {e}{RESET}")
