#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TON SPARK AUTO FARM - FULL SCRIPT
No prompts, runs until all ads exhausted.
Features: Giga Ads, Monetag Ads, Lightning, Spin, Chest.
"""

import os
import sys
import time
import json
import urllib.parse
import requests
from colorama import init, Fore, Style

# ============================================================
# COLOR SETUP
# ============================================================

init(autoreset=True)

G = Fore.GREEN + Style.BRIGHT
Y = Fore.YELLOW + Style.BRIGHT
R = Fore.RED + Style.BRIGHT
C = Fore.CYAN + Style.BRIGHT
M = Fore.MAGENTA + Style.BRIGHT
W = Fore.WHITE + Style.BRIGHT
D = Fore.BLACK + Style.BRIGHT
RESET = Style.RESET_ALL


# ============================================================
# UI FUNCTIONS
# ============================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    clear_screen()
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                    :: TON SPARK ::{RESET}")
    print(f"{C}                   AUTO FARM BOT{RESET}")
    print(f"{G}========================================================{RESET}")
    print()
    print(f"{C}  [+] Mode      : {W}Auto Farm (Unlimited)")
    print(f"{C}  [+] Features  : {G}Ads • Lightning • Spin • Chest")
    print(f"{C}  [+] Website   : {W}ton-spark-qu47.vercel.app")
    print()
    print(f"{G}--------------------------------------------------------{RESET}")
    print()


def print_setup():
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                       :: SETUP ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print()
    print(f"{C}  [01] {W}Buka Telegram bot @TonSparks_bot")
    print(f"{C}  [02] {W}Buka DevTools / Network")
    print(f"{C}  [03] {W}Cari request dengan parameter 'initData'")
    print(f"{C}  [04] {W}Copy seluruh initData string (panjang).")
    print()
    print(f"{G}--------------------------------------------------------{RESET}")
    print()


def print_session(user_data):
    print()
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                    :: SESSION ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print(f"{C}  Status    : {G}✓ VALID")
    print(f"{C}  Username  : {W}{user_data.get('username', 'N/A')}")
    print(f"{C}  Gold      : {G}{user_data.get('goldBalance', 0)}")
    print(f"{C}  SP        : {C}{user_data.get('spBalance', 0)}")
    print(f"{C}  Referrals : {Y}{user_data.get('totalReferred', 0)}")
    print(f"{G}========================================================{RESET}")
    print()


def print_finished(gold, sp, videos, earned_gold, earned_sp):
    print()
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                :: EXECUTION FINISHED ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print()
    print(f"{C}  Videos Done   : {G}{videos}")
    print(f"{C}  Gold Earned   : {G}+{earned_gold}")
    print(f"{C}  SP Earned     : {C}+{earned_sp}")
    print(f"{C}  Final Gold    : {W}{gold}")
    print(f"{C}  Final SP      : {W}{sp}")
    print()
    print(f"{G}========================================================{RESET}")
    print()


def show_progress(total):
    for rem in range(total, -1, -1):
        pct = int(((total - rem) / total) * 100) if total > 0 else 100
        filled = int(20 * pct / 100)
        empty = 20 - filled
        bar = f"{G}━" * filled + f"{D}─" * empty
        sys.stdout.write(f"\r  {C}[{bar}{C}] {W}{pct:3d}% {Y}⏱ {rem:02d}s{RESET}")
        sys.stdout.flush()
        if rem > 0:
            time.sleep(1)
    print()


# ============================================================
# BOT CLASS
# ============================================================

class TonSparkBot:
    BASE_URL = "https://ton-spark-qu47.vercel.app"
    USER_API = f"{BASE_URL}/api/user"
    ADWATCH_API = f"{BASE_URL}/api/adwatch"
    LIGHTNING_API = f"{BASE_URL}/api/lightning"
    TASKS_API = f"{BASE_URL}/api/tasks"
    MINIAPP_API = f"{BASE_URL}/api/miniapp"

    def __init__(self):
        self.session = requests.Session()
        self.init_data = ""
        self.telegram_id = None
        self.user_data = {}
        self.gold = 0
        self.sp = 0
        self.ads_watched = 0
        self.video_count = 0
        self.earned_gold = 0
        self.earned_sp = 0
        self.giga_count = 0
        self.monetag_count = 0
        self.giga_max = 20
        self.monetag_max = 20

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.169 Mobile Safari/537.36 Telegram-Android/12.9.2",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Origin": self.BASE_URL,
            "Referer": self.BASE_URL + "/?tgWebAppStartParam=TEP31790QP1",
            "Sec-Ch-Ua": '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "org.telegram.messenger.web"
        })

    def _get(self, endpoint, params=None):
        try:
            resp = self.session.get(endpoint, params=params, timeout=15)
            return resp.json()
        except Exception as e:
            print(f"{R}✗ GET error: {e}{RESET}")
            return {}

    def _post(self, endpoint, data=None):
        try:
            resp = self.session.post(endpoint, json=data, timeout=15)
            return resp.json()
        except Exception as e:
            print(f"{R}✗ POST error: {e}{RESET}")
            return {}

    def parse_init_data(self, raw):
        """Extract telegramId from initData robustly."""
        try:
            parsed = urllib.parse.parse_qs(raw)
            user_str = parsed.get('user', [''])[0]
            if not user_str:
                import re
                match = re.search(r'user=([^&]+)', raw)
                if match:
                    user_str = match.group(1)
            if user_str:
                user_str = urllib.parse.unquote(user_str)
                user_obj = json.loads(user_str)
                return user_obj.get('id')
        except Exception as e:
            print(f"{R}✗ Parse error: {e}{RESET}")
        return None

    def get_init_data(self):
        print_banner()
        print_setup()
        print(f"{Y}[!] Masukkan initData (copy dari URL / Network tab).{RESET}")
        print(f"{D}  Contoh: user=%7B%22id%22%3A123...{RESET}\n")
        while True:
            raw = input(f"{C}  • initData: {W}").strip()
            if raw:
                self.init_data = raw
                self.telegram_id = self.parse_init_data(raw)
                if self.telegram_id:
                    print(f"{G}✅ Telegram ID: {self.telegram_id}{RESET}")
                    break
                else:
                    print(f"{R}❌ Gagal ekstrak ID. Pastikan initData valid.{RESET}")
            else:
                print(f"{R}❌ Tidak boleh kosong.{RESET}")

    def register(self):
        print(f"{Y}⚡ Register / Login...{RESET}")
        payload = {
            "telegramId": self.telegram_id,
            "username": "User",
            "firstName": "User",
            "referCode": "",
            "initData": self.init_data
        }
        resp = self._post(self.USER_API, payload)
        if resp.get("success"):
            print(f"{G}✓ Register/Login sukses{RESET}")
            return True
        else:
            print(f"{R}✗ Gagal: {resp.get('message', resp)}{RESET}")
            return False

    def fetch_user(self):
        params = {
            "telegramId": self.telegram_id,
            "initData": self.init_data
        }
        resp = self._get(self.USER_API, params)
        if resp.get("success"):
            self.user_data = resp.get("user", {})
            self.gold = self.user_data.get("goldBalance", 0)
            self.sp = self.user_data.get("spBalance", 0)
            self.ads_watched = self.user_data.get("totalAdsWatched", 0)
            # Update ad counts from user data
            giga = self.user_data.get("gigaAds", {})
            monetag = self.user_data.get("monetagAds", {})
            import datetime
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            if giga.get("date") == today:
                self.giga_count = giga.get("count", 0)
            else:
                self.giga_count = 0
            if monetag.get("date") == today:
                self.monetag_count = monetag.get("count", 0)
            else:
                self.monetag_count = 0
            print_session(self.user_data)
            return True
        else:
            print(f"{R}✗ Gagal fetch user{RESET}")
            return False

    def watch_ad(self, network):
        params = {
            "telegramId": self.telegram_id,
            "network": network,
            "initData": self.init_data
        }
        status = self._get(self.ADWATCH_API, params)
        if not status.get("success"):
            print(f"{R}✗ Gagal cek status {network}{RESET}")
            return False, 0

        count = status.get("count", 0)
        max_count = status.get("max", 20)
        reward = status.get("reward", 500)

        if count >= max_count:
            print(f"{Y}⚠️ {network.upper()} habis ({count}/{max_count}){RESET}")
            return False, 0

        print(f"{M}▶ {network.upper()} Ad {count+1}/{max_count} | Reward: {reward}")
        show_progress(5)

        payload = {
            "telegramId": self.telegram_id,
            "network": network,
            "initData": self.init_data
        }
        claim = self._post(self.ADWATCH_API, payload)
        if claim.get("success"):
            earned = claim.get("reward", reward)
            return True, earned
        else:
            print(f"{R}✗ Gagal claim {network}{RESET}")
            return False, 0

    def do_lightning(self):
        params = {
            "telegramId": self.telegram_id,
            "initData": self.init_data
        }
        status = self._get(self.LIGHTNING_API, params)
        if not status.get("success"):
            return False, 0
        if not status.get("canBlast"):
            next_ms = status.get("nextMs", 0)
            if next_ms > 0:
                mins = next_ms // 60000
                print(f"{Y}⚡ Lightning cooldown: {mins}m remaining{RESET}")
            return False, 0

        print(f"{C}⚡ Lightning siap! Meledakkan...{RESET}")
        payload = {
            "telegramId": self.telegram_id,
            "initData": self.init_data,
            "action": "blast"
        }
        resp = self._post(self.LIGHTNING_API, payload)
        if resp.get("success"):
            reward = resp.get("reward", 0)
            return True, reward
        return False, 0

    def do_minigame(self, game):
        params = {
            "telegramId": self.telegram_id,
            "initData": self.init_data,
            "game": game
        }
        status = self._get(self.MINIAPP_API, params)
        if not status.get("success"):
            return False, 0
        if not status.get("canPlay"):
            return False, 0

        label = status.get("label", game)
        print(f"{M}🎮 {label} available! Playing...{RESET}")
        payload = {
            "telegramId": self.telegram_id,
            "initData": self.init_data,
            "action": "play",
            "game": game
        }
        resp = self._post(self.MINIAPP_API, payload)
        if resp.get("success"):
            reward = resp.get("reward", 0)
            return True, reward
        return False, 0

    def show_tasks(self):
        params = {
            "telegramId": self.telegram_id,
            "initData": self.init_data,
            "category": "daily"
        }
        resp = self._get(self.TASKS_API, params)
        if resp.get("success"):
            tasks = resp.get("tasks", [])
            if tasks:
                print(f"{C}📋 Daily Tasks:{RESET}")
                for t in tasks[:5]:
                    status = "✅" if t.get("completed") else "⬜"
                    print(f"  {status} {t.get('title')} - {G}{t.get('reward')} Gold{RESET}")
        else:
            print(f"{R}✗ Gagal fetch tasks{RESET}")

    def run(self):
        self.get_init_data()

        if not self.register():
            return

        if not self.fetch_user():
            return

        print(f"\n{Y}[!] Starting farm... will stop when all ads exhausted.{RESET}")

        while True:
            # Refresh user data to get latest counts
            self.fetch_user()

            # Check daily limit (hardcoded 560 from logs, but we trust server)
            if self.ads_watched >= 560:
                print(f"\n{G}✓ Daily limit reached ({self.ads_watched}/560). Done!{RESET}")
                break

            # Check if all activities are exhausted
            giga_done = self.giga_count >= self.giga_max
            monetag_done = self.monetag_count >= self.monetag_max

            # If both ads exhausted, try lightning and minigames, but if nothing works, break
            if giga_done and monetag_done:
                # Still try lightning and minigames
                lightning_success = False
                spin_success = False
                chest_success = False

                # Try lightning
                success, earned = self.do_lightning()
                if success:
                    self.sp += earned
                    self.earned_sp += earned
                    print(f"  {C}✅ +{earned} SP (Lightning) | SP: {self.sp}{RESET}")
                    lightning_success = True

                # Try spin
                success, earned = self.do_minigame("spin")
                if success:
                    self.gold += earned
                    self.earned_gold += earned
                    print(f"  {G}✅ +{earned} Gold (Spin) | Balance: {self.gold}{RESET}")
                    spin_success = True

                # Try chest
                success, earned = self.do_minigame("chest")
                if success:
                    self.gold += earned
                    self.earned_gold += earned
                    print(f"  {G}✅ +{earned} Gold (Chest) | Balance: {self.gold}{RESET}")
                    chest_success = True

                # If nothing succeeded, break
                if not (lightning_success or spin_success or chest_success):
                    print(f"\n{Y}⚠️ All activities exhausted. Stopping.{RESET}")
                    break

                # If some succeeded, continue loop to re-check ads (maybe time passed)
                time.sleep(2)
                continue

            # ---- Giga Ads ----
            if not giga_done:
                success, earned = self.watch_ad("giga")
                if success:
                    self.gold += earned
                    self.earned_gold += earned
                    self.ads_watched += 1
                    self.video_count += 1
                    self.giga_count += 1
                    print(f"  {G}✅ +{earned} Gold (Giga) | Balance: {self.gold}{RESET}")

            # ---- Monetag Ads ----
            if not monetag_done:
                success, earned = self.watch_ad("monetag")
                if success:
                    self.gold += earned
                    self.earned_gold += earned
                    self.ads_watched += 1
                    self.video_count += 1
                    self.monetag_count += 1
                    print(f"  {G}✅ +{earned} Gold (Monetag) | Balance: {self.gold}{RESET}")

            # ---- Lightning ----
            success, earned = self.do_lightning()
            if success:
                self.sp += earned
                self.earned_sp += earned
                print(f"  {C}✅ +{earned} SP (Lightning) | SP: {self.sp}{RESET}")

            # ---- Spin ----
            success, earned = self.do_minigame("spin")
            if success:
                self.gold += earned
                self.earned_gold += earned
                print(f"  {G}✅ +{earned} Gold (Spin) | Balance: {self.gold}{RESET}")

            # ---- Chest ----
            success, earned = self.do_minigame("chest")
            if success:
                self.gold += earned
                self.earned_gold += earned
                print(f"  {G}✅ +{earned} Gold (Chest) | Balance: {self.gold}{RESET}")

            # Show tasks occasionally
            if self.video_count % 5 == 0:
                self.show_tasks()

            print(f"\n{D}[{Y}Status{D}] Videos: {self.video_count} | Gold: {self.gold} | SP: {self.sp}{RESET}")
            time.sleep(2)

        # Finished
        print_finished(self.gold, self.sp, self.video_count, self.earned_gold, self.earned_sp)
        input(f"{C}Press Enter to exit...{RESET}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    try:
        bot = TonSparkBot()
        bot.run()
    except KeyboardInterrupt:
        print(f"\n\n{Y}[!] Bot stopped by user. Goodbye!{RESET}\n")
        sys.exit(0)
