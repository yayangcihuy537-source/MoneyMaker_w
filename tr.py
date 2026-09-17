#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎁 TREWARDS AUTO WATCH BOT v1.1
- Auto watch 4 ad blocks (loop sampai abis)
- Auto-stop kalau semua block sudah watched
- Hacker theme + animation
- ScriptMaker: MoneyMaker_w
"""

import os, sys, time, json, random
import requests
from datetime import datetime

CLEAR = '\033[K'
R = '\033[0m'
B = '\033[1m'
D = '\033[2m'
NG = '\033[38;5;46m'
NC = '\033[38;5;51m'
NP = '\033[38;5;201m'
NY = '\033[38;5;226m'
NO = '\033[38;5;208m'
NR = '\033[38;5;196m'
NM = '\033[38;5;135m'
DW = '\033[38;5;15m'
DG = '\033[38;5;240m'

BASE = "https://trewards-backend.ankisaw1010.workers.dev"
ORIGIN = "https://trewards-frontend.onrender.com"
CONFIG_FILE = "trewards_config.json"

UA = "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)"

AD_BLOCKS = [
    {"id": "adCounter1", "reward": "5000 TR"},
    {"id": "adCounter2", "reward": "5000 TR"},
    {"id": "adCounter3", "reward": "0.0005 TON"},
    {"id": "adCounter4", "reward": "0.0005 TON"},
]

AD_DURATION = 20
DELAY_BETWEEN = 25
CYCLE_DELAY = 60            # jeda antar cycle kalau masih ada block ready
MAX_CYCLES = 999            # safety

BANNER = f"""{NC}{B}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  ████████╗██████╗ ███████╗██╗    ██╗ █████╗ ██████╗ ██████╗ ███████╗
║  ╚══██╔══╝██╔══██╗██╔════╝██║    ██║██╔══██╗██╔══██╗██╔══██╗██╔════╝
║     ██║   ██████╔╝█████╗  ██║ █╗ ██║███████║██████╔╝██║  ██║███████╗
║     ██║   ██╔══██╗██╔══╝  ██║███╗██║██╔══██║██╔══██╗██║  ██║╚════██║
║     ██║   ██║  ██║███████╗╚███╔███╔╝██║  ██║██║  ██║██████╔╝███████║
║     ╚═╝   ╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝
║                                                                  ║
║  {NY}🎁 TREWARDS AUTO WATCH  {NC}│ {NG}v1.1 {NC}│ {NP}Auto Loop{R}
║                                                                  ║
║  {NG}▸ ScriptMaker : {NC}MoneyMaker_w
║  {NG}▸ Channel     : {NC}https://t.me/ScriptyXSouu
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{R}
"""

class Anim:
    @staticmethod
    def matrix_rain(lines=5, width=60, duration=1.5):
        chars = list("01ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉTREWARDS")
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
                color = NG if i < 1 else (NG if i < 2 else D + NG)
                sys.stdout.write(color + ''.join(row) + R + "\n")
            sys.stdout.flush()
            time.sleep(0.08)

    @staticmethod
    def boot(duration=2.0):
        steps = [
            "Initializing kernel module...",
            "Loading stealth headers...",
            "Rotating device fingerprint...",
            "Connecting to trewards-backend...",
            "Session ready.",
        ]
        per = duration / len(steps)
        print()
        for s in steps:
            sys.stdout.write(f"  {NG}[✓]{R} {DW}{s}{R}\n")
            sys.stdout.flush()
            time.sleep(per)
        print(f"  {NY}[⚡]{R} {DW}Status: {NG}SECURE{R}")
        print(f"  {NP}[★]{R} {DW}Welcome, {NC}Operative{R}\n")
        time.sleep(0.3)

    @staticmethod
    def watch_bar(label, duration):
        spinner = ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏']
        bar_len = 22
        start = time.time(); i = 0
        while True:
            elapsed = time.time() - start
            if elapsed >= duration: break
            pct = elapsed / duration
            filled = int(bar_len * pct)
            bar = '█' * filled + '░' * (bar_len - filled)
            rem = duration - elapsed
            row = (f"  {NP}{spinner[i%10]}{R} {NC}{label:<12}{R} "
                   f"{NG}[{bar}]{R} {NY}{int(pct*100):3d}%{R} {NY}{rem:4.1f}s{R}")
            sys.stdout.write('\r' + CLEAR + row)
            sys.stdout.flush()
            time.sleep(0.1); i += 1
        sys.stdout.write('\r' + CLEAR); sys.stdout.flush()

    @staticmethod
    def dots(text, duration=1.5):
        end = time.time() + duration
        n = 0
        while time.time() < end:
            d = "." * ((n % 3) + 1)
            sys.stdout.write('\r' + CLEAR + f" {NC}•{R} {DW}{text}{NC}{d:<4}{R}")
            sys.stdout.flush()
            time.sleep(0.3); n += 1
        sys.stdout.write('\r' + CLEAR + f" {NG}✓{R} {DW}{text}{R}\n")
        sys.stdout.flush()

    @staticmethod
    def glitch(text, duration=0.5):
        gc = "░▒▓█▄▀■□▪▫@#$%&*"
        start = time.time()
        while time.time() - start < duration:
            out = ''.join(random.choice(gc) if (random.randint(0,10)<2 and ch!=' ') else ch for ch in text)
            sys.stdout.write('\r' + CLEAR + f"  {NP}{out}{R}")
            sys.stdout.flush()
            time.sleep(0.06)
        sys.stdout.write('\r' + CLEAR + f"  {NC}{text}{R}\n")
        sys.stdout.flush()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def strip_ansi(s):
    import re
    return re.sub(r'\033\[[0-9;]*m', '', s)

def print_box(title, lines, color=NC, w=62):
    print(f"{color}╭{'─' * w}╮{R}")
    print(f"{color}│{R} {B}{color}{title:^{w}}{R} {color}│{R}")
    print(f"{color}├{'─' * w}┤{R}")
    for line in lines:
        clean = strip_ansi(line)
        pad = w - len(clean)
        if pad < 0: pad = 0
        print(f"{color}│{R} {line}{' ' * pad} {color}│{R}")
    print(f"{color}╰{'─' * w}╯{R}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: pass
    return {}

def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)

def get_user_id():
    cfg = load_config()
    if cfg.get('user_id'):
        print(f"{NG}✓ {DW}User ID tersimpan: {NC}{cfg['user_id']}{R}")
        use = input(f"{NY}? Pakai user_id ini? [Y/n]: {R}").strip().lower()
        if not use or use in ('y', 'yes', 'ya'):
            return str(cfg['user_id'])
    print(f"\n{NY}CARA DAPAT USER ID:{R}")
    print(f"{DG}  Buka Trewards di Telegram → DevTools → Network → /api/user/sync")
    print(f"  Cari field 'telegram_id' di body atau URL.{R}\n")
    uid = input(f"{NC}📧 User ID: {R}").strip()
    if uid:
        cfg['user_id'] = uid
        save_config(cfg)
    return uid

class TRewardsBot:
    def __init__(self):
        self.user_id = None
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "*/*",
            "content-type": "application/json",
            "user-agent": UA,
            "origin": ORIGIN,
            "referer": ORIGIN + "/",
            "x-requested-with": "org.telegram.messenger.web",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "accept-language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7",
        })
        self.stats = {
            "ads_watched": 0,
            "tr_earned": 0,
            "ton_earned": 0.0,
            "failed": 0,
            "cycles": 0,
            "start_time": datetime.now(),
        }
        self.user_data = None

    def _req(self, method, path, json_data=None, timeout=30):
        url = f"{BASE}{path}"
        for attempt in range(3):
            try:
                if method.upper() == 'GET':
                    r = self.session.get(url, timeout=timeout)
                else:
                    r = self.session.post(url, json=json_data, timeout=timeout)
                if r.status_code == 429:
                    time.sleep(int(r.headers.get('Retry-After', 5)))
                    continue
                try:
                    return r.json()
                except:
                    return {"_raw": r.text[:200], "_code": r.status_code}
            except Exception as e:
                if attempt == 2:
                    return {"_error": str(e)}
                time.sleep(2)
        return None

    def sync_user(self):
        data = self._req('POST', f"/api/user/sync?_t={int(time.time()*1000)}", {
            "telegram_id": int(self.user_id),
            "username": "",
            "first_name": "",
            "last_name": "",
            "referrer_id": None
        })
        if data and data.get('success'):
            self.user_data = data.get('user', {})
            return True
        return False

    def get_user(self):
        return self.user_data or {}

    def verify_channels(self):
        return self._req('POST', f"/api/channels/verify?_t={int(time.time()*1000)}", {
            "user_id": int(self.user_id)
        })

    def watch_ad(self, block_id):
        payload = {
            "user_id": int(self.user_id),
            "ad_block_id": block_id,
            "duration_sec": AD_DURATION,
            "client_timestamp": int(time.time() * 1000)
        }
        return self._req('POST', f"/api/ad/watch?_t={int(time.time()*1000)}", payload)

    def _show_user_info(self):
        user = self.get_user()
        print()
        lines = [
            f"{NG}👤 Username      : {DW}@{user.get('username', 'N/A')}{R}",
            f"{NG}📛 Nama          : {DW}{user.get('first_name', 'N/A')}{R}",
            f"{NG}🆔 User ID       : {DW}{user.get('id', 'N/A')}{R}",
            f"{NG}💰 TR Balance    : {NY}{user.get('tr_balance', 0):,} TR{R}",
            f"{NG}💎 TON Balance   : {NY}{user.get('ton_balance', 0):.4f} TON{R}",
            f"{NG}🎯 Ads Watched   : {DW}{user.get('ads_watched_count', 0)}{R}",
            f"{NG}🎰 Spins         : {DW}{user.get('spins_available', 0)}{R}",
            f"{NG}🚫 Banned        : {DW}{user.get('is_banned', False)}{R}",
        ]
        print_box("✅ USER INFO", lines, NG)

    def _show_blocks(self):
        user = self.get_user()
        today = user.get('today_ads_watched', {}) if isinstance(user, dict) else {}
        print()
        lines = []
        for b in AD_BLOCKS:
            cnt = today.get(b['id'], 0)
            status = f"{NG}✅ DONE{R}" if cnt >= 1 else f"{NY}⭕ READY{R}"
            lines.append(f"{NC}{b['id']:<12}{R} : {status} {DG}({b['reward']}){R}")
        print_box("📺 AD BLOCKS", lines, NC)

    def _get_ready_blocks(self):
        user = self.get_user()
        today = user.get('today_ads_watched', {}) if isinstance(user, dict) else {}
        return [b for b in AD_BLOCKS if today.get(b['id'], 0) == 0]

    # ============ MAIN LOOP ============
    def auto_watch_loop(self):
        Anim.dots("sync user", 1.5)
        if not self.sync_user():
            print(f"{NR}❌ Sync user gagal!{R}")
            return

        Anim.dots("verify channels", 1.0)
        self.verify_channels()
        self.sync_user()

        self._show_user_info()
        self._show_blocks()

        # ==== LOOP CONTINUOUS ====
        while self.stats['cycles'] < MAX_CYCLES:
            self.stats['cycles'] += 1
            ready = self._get_ready_blocks()

            if not ready:
                print(f"\n{NG}✅ Semua block sudah selesai! Bot stop.{R}")
                break

            print(f"\n{NP}{'═' * 60}{R}")
            print(f"{NP}  🔄 CYCLE #{self.stats['cycles']}  |  {len(ready)} block ready{R}")
            print(f"{NP}{'═' * 60}{R}")

            total = len(ready)
            cycle_success = 0
            cycle_fail = 0

            for idx, block in enumerate(ready, 1):
                print(f"\n{NC}  ┌─ [{idx:02d}/{total:02d}] {block['id']} {DG}({block['reward']}){R}")

                Anim.watch_bar(block['id'], AD_DURATION)
                result = self.watch_ad(block['id'])

                if result and result.get('success'):
                    reward = result.get('reward_amount', 0)
                    currency = result.get('currency', '?')
                    user_new = result.get('user', {})

                    if currency == 'TR':
                        self.stats['tr_earned'] += reward
                    elif currency == 'TON':
                        self.stats['ton_earned'] += reward

                    self.stats['ads_watched'] += 1
                    cycle_success += 1
                    if user_new:
                        self.user_data = user_new

                    print(f"{NG}  ✅ {block['id']}: +{reward} {currency} | bal: {user_new.get('tr_balance',0):,} TR | {user_new.get('ton_balance',0):.4f} TON{R}")

                    if idx < total:
                        for i in range(DELAY_BETWEEN, 0, -1):
                            sys.stdout.write(f"\r  {NY}⏳ Next in {i:2d}s...{R}   ")
                            sys.stdout.flush()
                            time.sleep(1)
                        sys.stdout.write('\r' + ' ' * 40 + '\r')
                else:
                    err = (result or {}).get('error', (result or {}).get('message', 'unknown'))
                    print(f"{NR}  ❌ {block['id']}: {err}{R}")
                    self.stats['failed'] += 1
                    cycle_fail += 1
                    time.sleep(3)

            # refresh
            print()
            Anim.dots("refresh user", 1.0)
            self.sync_user()

            # cek lagi siap atau stop
            remaining = self._get_ready_blocks()
            if not remaining:
                print(f"\n{NG}🏁 Semua block sudah habis! Bot stop.{R}")
                break

            # kalau cycle_success == 0 dan cycle_fail > 0 → stop biar gak spam
            if cycle_success == 0:
                print(f"\n{NY}⚠️  Cycle gagal total, stop untuk hindari spam.{R}")
                break

            # kalau masih ada ready (mungkin reset) — tunggu cycle delay
            print(f"\n{NY}⏳ {len(remaining)} block masih ready — cycle berikutnya dalam {CYCLE_DELAY}s...{R}")
            for i in range(CYCLE_DELAY, 0, -1):
                sys.stdout.write(f"\r  {NC}⏳ Next cycle in {i:3}s...{R}   ")
                sys.stdout.flush()
                time.sleep(1)
            sys.stdout.write('\r' + ' ' * 45 + '\r')

        self._show_summary()

    def _show_summary(self):
        user = self.get_user()
        dur = (datetime.now() - self.stats['start_time']).total_seconds()
        print()
        lines = [
            f"{NC}🔄 Cycles        : {DW}{self.stats['cycles']}{R}",
            f"{NG}📺 Ads Watched   : {DW}{self.stats['ads_watched']}{R}",
            f"{NG}💰 TR Earned     : {NY}{self.stats['tr_earned']:,} TR{R}",
            f"{NG}💎 TON Earned    : {NY}{self.stats['ton_earned']:.4f} TON{R}",
            f"{NR}❌ Failed        : {DW}{self.stats['failed']}{R}",
            f"{NC}⏱  Duration      : {DW}{int(dur//60)}m {int(dur%60)}s{R}",
            f"{NM}💰 TR Balance    : {NY}{user.get('tr_balance', 0):,} TR{R}",
            f"{NM}💎 TON Balance   : {NY}{user.get('ton_balance', 0):.4f} TON{R}",
        ]
        print_box("🏁 FINAL SUMMARY", lines, NG)

def main():
    clear()
    Anim.matrix_rain(lines=5, width=60, duration=1.2)
    print()
    Anim.glitch("TREWARDS AUTO WATCH v1.1", 0.5)
    Anim.boot(1.5)
    clear()
    print(BANNER)

    user_id = get_user_id()
    if not user_id:
        print(f"{NR}❌ User ID wajib!{R}")
        sys.exit(1)

    bot = TRewardsBot()
    bot.user_id = user_id

    print()
    Anim.glitch("STARTING AUTO WATCH (LOOP)", 0.4)

    try:
        bot.auto_watch_loop()
    except KeyboardInterrupt:
        print(f"\n{NY}⏹️  Stopped by user.{R}")
        bot._show_summary()
    except Exception as e:
        print(f"\n{NR}❌ Error: {e}{R}")

    input(f"\n{NC}Press Enter to exit...{R}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{NY}Stopped.{R}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{NR}Fatal: {e}{R}")
        import traceback; traceback.print_exc()
        sys.exit(1)
