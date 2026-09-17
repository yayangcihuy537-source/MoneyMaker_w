#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌾 FARMING MATES BOT v2.0
- Auto-skip ads yang gagal/limit
- Animation pack (anti-spam clear-line)
- Loop sampai semua ads abis
- Handle rate limit 429
- ScriptMaker: @MoneyMaker_w
"""

import requests
import json
import time
import os
import random
import sys
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

BANNER = f"""{NY}{BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║  ███████╗ █████╗ ██████╗ ███╗   ███╗██╗███╗   ██╗ ██████╗      ║
║  ██╔════╝██╔══██╗██╔══██╗████╗ ████║██║████╗  ██║██╔════╝      ║
║  █████╗  ███████║██████╔╝██╔████╔██║██║██╔██╗ ██║██║  ███╗     ║
║  ██╔══╝  ██╔══██║██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██║   ██║     ║
║  ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║██║██║ ╚████║╚██████╔╝     ║
║  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ ╚═════╝      ║
║                                                                  ║
║  {NY}🌾 FARMING MATES BOT  {NC}│ {NG}v2.0 {NC}│ {NP}AUTO FARM + SKIP{RST}{NY}              ║
║                                                                  ║
║  {NG}▸ Bot     : {NC}@FarmingMatesBot{RST}{NY}                            ║
║  {NG}▸ Script  : {NC}@MoneyMaker_w{RST}{NY}                               ║
║  {NG}▸ Channel : {NC}https://t.me/ScriptyXSouu{RST}{NY}                  ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{RST}
"""

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
    def bar(label, provider, duration):
        """Live watch bar dengan clear-line"""
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
            sys.stdout.write('\r' + CLEAR + row)
            sys.stdout.flush()
            time.sleep(0.1); i += 1
        sys.stdout.write('\r' + CLEAR); sys.stdout.flush()

    @staticmethod
    def glitch(text, duration=0.5):
        gc = "░▒▓█▄▀■□▪▫@#$%&*"
        end = time.time() + duration
        while time.time() < end:
            out = ''.join(random.choice(gc) if (random.randint(0,10)<2 and ch!=' ') else ch for ch in text)
            sys.stdout.write('\r' + CLEAR + f"  {NP}{out}{RST}")
            sys.stdout.flush()
            time.sleep(0.06)
        sys.stdout.write('\r' + CLEAR + f"  {NC}{text}{RST}\n"); sys.stdout.flush()

# ============================================================
# BOT CLASS
# ============================================================
class FarmingMatesBot:
    BASE = "https://api.farmingmates.site/api"

    def __init__(self):
        self.init_data = ""
        self.device_id = "dev_" + ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=22))
        self.token = None
        self.profile = None
        self.session = requests.Session()
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
            "Accept": "*/*",
            "Origin": "https://farmingmates.site",
            "Referer": "https://farmingmates.site/",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        self.session.headers.update(self.headers)
        self.stats = {
            'watched': 0,
            'earned': 0,
            'failed': 0,
            'skipped': 0,
            'start': datetime.now()
        }
        self.load_init()

    def load_init(self):
        f = "farmingmates_init.txt"
        if os.path.exists(f):
            with open(f, 'r') as fp:
                self.init_data = fp.read().strip()

    def save_init(self, data):
        with open("farmingmates_init.txt", 'w') as fp:
            fp.write(data.strip())
        self.init_data = data.strip()

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    # ============ API ============
    def request(self, method, path, json_data=None, timeout=30):
        url = f"{self.BASE}{path}"
        for attempt in range(3):
            try:
                if method.upper() == 'GET':
                    r = self.session.get(url, timeout=timeout)
                else:
                    r = self.session.post(url, json=json_data, timeout=timeout)

                # rate limit
                if r.status_code == 429:
                    wait = int(r.headers.get('Retry-After', 5))
                    print(f"{Y}  ⚠️  Rate limited, tunggu {wait}s...{RST}")
                    time.sleep(wait)
                    continue
                return r
            except requests.exceptions.Timeout:
                if attempt < 2:
                    time.sleep(2); continue
                return None
            except Exception as e:
                print(f"{R}  ❌ {e}{RST}")
                return None
        return None

    # ============ AUTH ============
    def login(self):
        if not self.init_data:
            return False
        data = {"initData": self.init_data, "deviceId": self.device_id}
        r = self.request('POST', "/auth/telegram", data)
        if not r or r.status_code != 200:
            print(f"{R}❌ Login gagal (HTTP {r.status_code if r else 'timeout'}){RST}")
            return False
        try:
            j = r.json()
            if not j.get('ok'):
                print(f"{R}❌ Login gagal: {j.get('message')}{RST}")
                return False
            self.token = j.get('token')
            self.profile = j.get('profile', {})
            self.session.headers["Authorization"] = f"Bearer {self.token}"
            return True
        except:
            return False

    # ============ TASKS ============
    def get_tasks(self):
        r = self.request('GET', "/tasks")
        if r and r.status_code == 200:
            try:
                return r.json().get('tasks', [])
            except:
                return []
        return []

    def get_slots(self, task_id):
        r = self.request('GET', f"/tasks/{task_id}/slots")
        if r and r.status_code == 200:
            try:
                return r.json()
            except:
                return {"ok": False}
        return {"ok": False}

    # ============ WATCH ============
    def watch_slot(self, task_id, slot_index, provider, reward, task_name, idx, total):
        # 1) Session
        r = self.request('POST', f"/ads/task/{task_id}/session", {"slotIndex": slot_index})
        if not r or r.status_code != 200:
            return None
        try:
            sd = r.json()
            if not sd.get('ok'):
                return None
        except:
            return None

        session_id = sd.get('sessionId')
        if not session_id:
            return None

        provider = sd.get('provider', provider)
        min_watch = sd.get('minWatchSec', 1)
        watch_dur = max(3, min_watch + random.randint(2, 4))  # 3-5 detik

        print(f"\n{NC}  ┌─ [{idx:02d}/{total:02d}] {task_name}{RST}")
        Anim.bar(task_name[:9], provider, watch_dur)

        # 2) Complete
        payload = {
            "sessionId": session_id,
            "slotIndex": slot_index,
            "provider": provider,
            "clicked": True,
            "adsgramClicked": None
        }
        r2 = self.request('POST', f"/ads/task/{task_id}/complete", payload)
        if not r2 or r2.status_code != 200:
            return None
        try:
            d = r2.json()
            if not d.get('ok'):
                return None
            return d
        except:
            return None

    def watch_task(self, task):
        """Watch satu task (10 slot). Return (watched, earned, failed)."""
        task_id = task['id']
        name = task['title'].strip()
        total_slots = task.get('adSlots', 10) or 10

        # Skip task yang gak support ads
        if task.get('kind') != 'ad' and task.get('type') != 'ad':
            return 0, 0, 0

        slots_data = self.get_slots(task_id)
        if not slots_data.get('ok'):
            print(f"{Y}  ⚠️  Gagal cek slot: {name}{RST}")
            return 0, 0, 0

        ready = slots_data.get('ready', 0)
        per_slot = slots_data.get('perSlotReward', 0)

        if ready == 0:
            print(f"{Y}  ⏭  {name}: tidak ada slot ready{RST}")
            return 0, 0, 0

        print(f"\n{NC}  ╔══════════════════════════════════════════════════╗{RST}")
        print(f"{NC}  ║{RST}  {NG}📺 {name:<45}{NC}║{RST}")
        print(f"{NC}  ║{RST}  {NC}Slot ready : {NG}{ready}/{total_slots}{RST}")
        print(f"{NC}  ║{RST}  {NC}Per slot   : {NG}{per_slot} koin{RST}")
        print(f"{NC}  ╚══════════════════════════════════════════════════╝{RST}")

        watched = 0
        earned = 0
        failed = 0

        for idx, slot in enumerate(slots_data.get('slots', []), start=1):
            if slot.get('status') != 'ready':
                continue

            slot_index = slot['index']
            provider = slot.get('provider', 'unknown')
            reward = slot.get('reward', per_slot)

            res = self.watch_slot(task_id, slot_index, provider, reward, name, idx, ready)

            if res:
                got = res.get('reward', 0)
                profile = res.get('profile', {})
                if profile:
                    self.profile = profile
                coins = profile.get('coins', self.profile.get('coins', 0) if self.profile else 0)
                self.stats['watched'] += 1
                self.stats['earned'] += got
                watched += 1
                earned += got
                print(f"{NG}  ✅ #{idx:02d}: +{got} koin | balance: {coins:,}{RST}")
                time.sleep(2)
            else:
                failed += 1
                self.stats['failed'] += 1
                print(f"{Y}  ⏭  #{idx:02d}: gagal → skip{RST}")

                # Kalau 3x gagal berturut, stop task ini
                if failed >= 3 and watched == 0:
                    print(f"{R}  ❌ {name}: gagal 3x, skip task ini{RST}")
                    break

        return watched, earned, failed

    # ============ MAIN LOOP ============
    def run(self):
        print(f"\n{NC}{'═'*60}{RST}")
        print(f"{NY}🚜 AUTO FARMING STARTED{RST}")
        print(f"{NC}{'═'*60}{RST}")

        session_start = datetime.now()

        # Get tasks
        Anim.dots("fetch tasks", 1.5)
        tasks = self.get_tasks()
        if not tasks:
            print(f"{R}❌ Gagal fetch tasks{RST}")
            return

        # Filter hanya ads task
        ad_tasks = [t for t in tasks if t.get('kind') == 'ad' or t.get('type') == 'ad']
        print(f"{NG}✓ Found {len(ad_tasks)} ads task{RST}\n")

        total_watched = 0
        total_earned = 0
        total_failed = 0

        # Loop terus sampai semua task abis (gak ada ready)
        loop = 0
        while True:
            loop += 1
            if loop > 50:  # safety
                print(f"{Y}⚠️  50 loop tercapai, stop.{RST}")
                break

            any_ready = False
            for task in ad_tasks:
                w, e, f = self.watch_task(task)
                total_watched += w
                total_earned += e
                total_failed += f
                if w > 0:
                    any_ready = True
                time.sleep(1)

            if not any_ready:
                print(f"\n{NY}⏹ Semua ads task abis / limit. Bot berhenti.{RST}")
                break

            print(f"\n{NC}🔄 Refresh tasks...{RST}")
            tasks = self.get_tasks()
            ad_tasks = [t for t in tasks if t.get('kind') == 'ad' or t.get('type') == 'ad']
            time.sleep(5)

        # Summary
        duration = (datetime.now() - session_start).total_seconds()
        print(f"\n{NC}{'═'*60}{RST}")
        print(f"{NG}🏁 SESSION SUMMARY{RST}")
        print(f"{NC}{'═'*60}{RST}")
        print(f"  {NG}📺 Watched  : {W}{total_watched}{RST}")
        print(f"  {NG}💰 Earned   : {NY}{total_earned} koin{RST}")
        print(f"  {R}❌ Failed   : {W}{total_failed}{RST}")
        print(f"  {NG}💰 Balance  : {NY}{self.profile.get('coins', 0) if self.profile else 0:,} koin{RST}")
        print(f"  {NC}⏱️  Duration : {W}{int(duration//60)}m {int(duration%60)}s{RST}")
        print(f"{NC}{'═'*60}{RST}")

    # ============ MENU ============
    def menu(self):
        while True:
            self.clear()
            print(BANNER)

            if self.init_data:
                print(f"{NG}🔑 Status : {NG}InitData SET ({self.init_data[:30]}...){RST}")
            else:
                print(f"{R}🔑 Status : {R}InitData EMPTY{RST}")

            print(f"\n{NC}  [1] 🚜 Start Farming")
            print(f"  [2] 🔑 Set InitData")
            print(f"  [3] 👤 Refresh Profile")
            print(f"  {R}[0] 🚪 Exit{RST}")
            print(f"\n{NC}{'═'*60}{RST}")

            c = input(f"  {NG}➜ {RST}").strip()

            if c == "1":
                if not self.init_data:
                    print(f"{R}❌ Set InitData dulu!{RST}")
                    time.sleep(2); continue
                Anim.dots("login", 1.5)
                if not self.login():
                    input(f"\n{R}Enter...{RST}"); continue
                print(f"\n{NG}✓ Logged in as @{self.profile.get('username', 'N/A')}{RST}")
                print(f"{NG}💰 Balance: {NY}{self.profile.get('coins', 0):,}{RST}")
                self.run()
                input(f"\n{NC}Enter untuk kembali...{RST}")

            elif c == "2":
                print(f"\n{Y}🔑 Masukkan InitData (Enter untuk batal):{RST}")
                d = input(f"  {NG}➜ {RST}").strip()
                if d:
                    self.save_init(d)
                    print(f"{NG}✓ InitData saved!{RST}")
                time.sleep(1.5)

            elif c == "3":
                if not self.init_data:
                    continue
                Anim.dots("login", 1.5)
                if self.login():
                    p = self.profile
                    print(f"\n{NC}╭─────────────────────────────────────╮{RST}")
                    print(f"{NC}│{RST} {NG}👤 @{p.get('username', 'N/A'):<33}{NC}│{RST}")
                    print(f"{NC}│{RST} {NG}💰 Coins     : {NY}{p.get('coins', 0):<20,}{NC}│{RST}")
                    print(f"{NC}│{RST} {NG}⚡ Energy   : {NY}{p.get('energy', 0)}/{p.get('energyMax', 0):<19}{NC}│{RST}")
                    print(f"{NC}│{RST} {NG}📈 Level    : {NY}{p.get('level', 1):<20}{NC}│{RST}")
                    print(f"{NC}│{RST} {NG}📺 Ads Today: {NY}{p.get('adsToday', 0):<20}{NC}│{RST}")
                    print(f"{NC}│{RST} {NG}💎 Total Ads: {NY}{p.get('totalAds', 0):<20}{NC}│{RST}")
                    print(f"{NC}╰─────────────────────────────────────╯{RST}")
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
        Anim.glitch("FARMING MATES BOT v2.0", 0.6)
        time.sleep(0.3)
        bot = FarmingMatesBot()
        bot.menu()
    except KeyboardInterrupt:
        print(f"\n{R}⏹️  Stopped by user.{RST}")
    except Exception as e:
        print(f"\n{R}❌ Error: {e}{RST}")
        import traceback; traceback.print_exc()
        input(f"\n{NC}Enter untuk keluar...{RST}")
