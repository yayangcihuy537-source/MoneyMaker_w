#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import re
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
    print(f"{Y}                    :: FOMO EARN ::{RESET}")
    print(f"{C}                  AUTO WATCH BOT{RESET}")
    print(f"{G}========================================================{RESET}")
    print()
    print(f"{C}  [+] Mode      : {W}Auto Watch")
    print(f"{C}  [+] Captcha   : {G}No Captcha")
    print(f"{C}  [+] Website   : {W}fomoearn.com")
    print()
    print(f"{G}--------------------------------------------------------{RESET}")
    print()


def print_setup():
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                       :: SETUP ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print()
    print(f"{C}  [01] {W}Login ke fomoearn.com")
    print(f"{C}  [02] {W}Buka Cookies / Application")
    print(f"{C}  [03] {W}Siapkan konfigurasi akun")
    print(f"{C}  [04] {W}Masukkan konfigurasi")
    print()
    print(f"{G}--------------------------------------------------------{RESET}")
    print()


def print_session_valid(user_id, balance):
    print()
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                    :: SESSION ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print(f"{C}  Status  : {G}✓ VALID")
    print(f"{C}  User ID : {W}{user_id}")
    print(f"{C}  Balance : {G}${balance:.7f}")
    print(f"{G}========================================================{RESET}")
    print()


def print_limits(daily_limit, hourly_limit, duration):
    print()
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                    :: LIMITS ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print(f"{C}  Daily Limit  : {Y}{daily_limit} videos")
    print(f"{C}  Hourly Limit : {Y}{hourly_limit} videos")
    print(f"{C}  Duration     : {W}{duration}s")
    print(f"{G}========================================================{RESET}")
    print()


def print_task(task_id, target, duration, reward):
    print()
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                     :: TASK ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print(f"{C}  ID       : {W}#{task_id}")
    print(f"{C}  Target   : {W}{target[:45]}")
    print(f"{C}  Duration : {Y}{duration}s")
    print(f"{C}  Reward   : {G}${reward:.6f} USD")
    print(f"{G}--------------------------------------------------------{RESET}")


def show_progress(total):
    for rem in range(total, -1, -1):
        pct = int(((total - rem) / total) * 100)
        filled = int(20 * pct / 100)
        empty = 20 - filled
        bar = f"{G}━" * filled + f"{D}─" * empty
        sys.stdout.write(f"\r  {C}[{bar}{C}] {W}{pct:3d}% {Y}⏱ {rem:02d}s{RESET}")
        sys.stdout.flush()
        if rem > 0:
            time.sleep(1)
    print()


def print_success(reward, balance, hour, hour_limit, today, day_limit):
    print()
    print(f"{G}  [✓] TASK COMPLETED{RESET}")
    print(f"{C}      Reward  : {G}+${reward:.5f} USD")
    print(f"{C}      Balance : {W}${balance:.7f}")
    print(f"{C}      Hour    : {Y}{hour}/{hour_limit}")
    print(f"{C}      Today   : {Y}{today}/{day_limit}")
    print(f"{G}--------------------------------------------------------{RESET}")


def print_finished(completed, earned, balance, reason="FINISHED"):
    print()
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                :: {reason} ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print()
    print(f"{C}  Videos Completed : {G}{completed}")
    print(f"{C}  Total Earned     : {G}+${earned:.5f} USD")
    print(f"{C}  Current Balance  : {W}${balance:.7f} USD")
    print()
    print(f"{G}========================================================{RESET}")
    print()


# ============================================================
# COOKIE PARSER
# ============================================================

def parse_cookie_header(header):
    cookies = {}
    parts = []
    current = ""
    in_quotes = False
    for ch in header:
        if ch == '"':
            in_quotes = not in_quotes
            current += ch
        elif ch == ';' and not in_quotes:
            parts.append(current.strip())
            current = ""
        else:
            current += ch
    if current.strip():
        parts.append(current.strip())
    for part in parts:
        if '=' in part:
            k, v = part.split('=', 1)
            k = k.strip()
            v = v.strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1]
            if k and v:
                cookies[k] = v
    return cookies


# ============================================================
# BOT CLASS
# ============================================================

class FomoEarnBot:
    BASE_URL = "https://fomoearn.com"
    USER_API = f"{BASE_URL}/api/user/"
    TASKS_API = f"{BASE_URL}/api/user/tasks/"
    START_API = f"{BASE_URL}/api/user/tasks/start/"

    def __init__(self):
        self.session = requests.Session()
        self.hash = ""
        self.user_agent = "Mozilla/5.0 (Linux; Android 14; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.127 Mobile Safari/537.36"
        self.balance = 0.0
        self.cur_day = 0
        self.cur_hour = 0
        self.daily_limit = 50
        self.hourly_limit = 62
        self.duration_default = 15
        self.completed_today = 0
        self.total_earned = 0.0
        self.extra_cookies = {}
        self.max_videos = 0          # 0 = unlimited
        self.videos_done = 0         # counter for max limit
        self.failures = 0            # counter for consecutive failures

    def _set_cookies(self, cookies_dict):
        for k, v in cookies_dict.items():
            self.session.cookies.set(k, v, domain='.fomoearn.com', path='/')
            self.session.cookies.set(k, v, domain='fomoearn.com', path='/')

    def _parse_and_set_cookies(self, raw_input):
        raw_input = raw_input.strip()
        if '=' in raw_input and (';' in raw_input or '"' in raw_input):
            cookies = parse_cookie_header(raw_input)
        else:
            cookies = {'hash': raw_input}
        if 'hash' in cookies:
            self.hash = cookies['hash']
        elif len(raw_input) == 64 and all(c in '0123456789abcdef' for c in raw_input.lower()):
            self.hash = raw_input
            cookies['hash'] = raw_input
        if not self.hash:
            return False
        self._set_cookies(cookies)
        self.extra_cookies = {k: v for k, v in cookies.items() if k not in ['hash', 'signed']}
        return True

    def load_config(self):
        print_banner()
        cfg_file = "fomo_config.json"
        config = {}
        if os.path.exists(cfg_file):
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            except Exception as e:
                print(f"{R}✗ Error reading config: {e}{RESET}")

        self.hash = config.get("hash", "")
        self.user_agent = config.get("user_agent", self.user_agent)
        self.balance = float(config.get("last_balance", 0.0))
        self.extra_cookies = config.get("extra_cookies", {})
        self.max_videos = config.get("max_videos", 0)

        self.session.headers.update({
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.BASE_URL,
            "Referer": f"{self.BASE_URL}/watch",
            "Sec-Ch-Ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Android WebView";v="128"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "XMLHttpRequest"
        })

        # If no hash, run setup
        if not self.hash:
            print_setup()
            print(f"{Y}[!] Silakan masukkan cookie atau hash.{RESET}")
            while not self.hash:
                raw_in = input(f"{C}  • Masukkan Cookie / Hash: {W}").strip()
                if self._parse_and_set_cookies(raw_in):
                    print(f"    {G}Hash ditemukan: {self.hash[:16]}...{RESET}")
                else:
                    print(f"    {R}Hash tidak ditemukan! Coba lagi.{RESET}")

        # Set cookies from config
        if self.hash:
            self._set_cookies({'hash': self.hash, 'signed': '1'})
            for k, v in self.extra_cookies.items():
                self._set_cookies({k: v})

        # Ask for max videos limit
        if self.max_videos == 0:
            print(f"\n{Y}[?] Berapa banyak video maksimal yang ingin ditonton? (0 = tanpa batas){RESET}")
            while True:
                try:
                    val = int(input(f"{C}  • Max videos: {W}").strip())
                    if val >= 0:
                        self.max_videos = val
                        break
                    else:
                        print(f"{R}Masukkan angka >= 0.{RESET}")
                except ValueError:
                    print(f"{R}Masukkan angka.{RESET}")

        self.save_state()
        return True

    def save_state(self):
        try:
            cfg_file = "fomo_config.json"
            config = {}
            if os.path.exists(cfg_file):
                with open(cfg_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
            config["hash"] = self.hash
            config["user_agent"] = self.user_agent
            config["extra_cookies"] = self.extra_cookies
            config["last_balance"] = self.balance
            config["max_videos"] = self.max_videos
            with open(cfg_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            print(f"{Y}⚠️ Failed to save config: {e}{RESET}")

    def _post(self, url, data, timeout=15):
        try:
            resp = self.session.post(url, data=data, timeout=timeout)
            if resp.status_code != 200:
                print(f"{Y}Response preview: {resp.text[:200]}{RESET}")
            return resp.json()
        except Exception as e:
            print(f"{R}✗ Request error: {e}{RESET}")
            return {"status": "error", "message": str(e)}

    def login(self):
        print(f"{Y}⚡ Verifikasi sesi akun...{RESET}")
        # Try getCurrentUser
        resp = self._post(self.USER_API, {"method": "getCurrentUser"})
        if resp.get("status") == "ok":
            data = resp.get("data", {})
            if data.get("userid"):
                user_id = data["userid"]
                self.balance = float(data.get("balance", 0.0))
                print_session_valid(user_id, self.balance)
                return True

        # Fallback to dashboard
        resp = self._post(self.USER_API, {"method": "dashboard"})
        if resp.get("status") == "ok":
            data = resp.get("data", {})
            if data.get("user"):
                user = data["user"]
                self.balance = float(user.get("balance", 0.0))
                user_id = "N/A"
                resp2 = self._post(self.USER_API, {"method": "getCurrentUser"})
                if resp2.get("status") == "ok" and resp2.get("data", {}).get("userid"):
                    user_id = resp2["data"]["userid"]
                print_session_valid(user_id, self.balance)
                return True
            elif data.get("id"):
                user_id = data["id"]
                self.balance = float(data.get("balance", 0.0))
                print_session_valid(user_id, self.balance)
                return True

        print(f"{R}✗ Sesi tidak valid. Cek cookie hash.{RESET}")
        return False

    def fetch_limits(self):
        resp = self._post(self.TASKS_API, {"method": "getLimits"})
        if resp.get("status") == "ok":
            data = resp.get("data", {})
            self.daily_limit = int(data.get("limDay", 50))
            self.hourly_limit = int(data.get("limHour", 62))
            self.duration_default = int(data.get("duration", 15))
            print_limits(self.daily_limit, self.hourly_limit, self.duration_default)
        else:
            print(f"{R}✗ Gagal fetch limits: {resp.get('message')}{RESET}")

    def get_task(self):
        resp = self._post(self.TASKS_API, {"method": "get"})
        if resp.get("status") == "ok":
            return resp.get("data", {})
        else:
            # Jika respon mengandung limitDay, kita anggap daily limit tercapai
            msg = resp.get("message", "")
            if "limitDay" in msg or "daily" in msg.lower():
                self.cur_day = self.daily_limit  # force stop
            return None

    def claim_task(self, task_id):
        data = {"TaskId": str(task_id), "fin": "1"}
        resp = self._post(self.START_API, data)
        if resp.get("status") == "ok":
            return True, resp.get("data", {})
        else:
            return False, resp.get("message", "")

    def get_current_user(self):
        resp = self._post(self.USER_API, {"method": "getCurrentUser"})
        if resp.get("status") == "ok":
            data = resp.get("data", {})
            user = data.get("user", {})
            self.balance = float(user.get("balance", 0.0))
            self.cur_day = int(user.get("viewCurDay", 0))
            return True
        return False

    def _cooldown(self, seconds):
        for rem in range(seconds, 0, -1):
            mins, secs = divmod(rem, 60)
            sys.stdout.write(f"\r  {Y}⏱ Cooldown: {W}{mins:02d}m {secs:02d}s remaining...{RESET}  ")
            sys.stdout.flush()
            time.sleep(1)
        print()

    def run(self):
        if not self.load_config():
            return
        if not self.login():
            return

        self.fetch_limits()

        print(f"{C}  Max Videos  : {W}{'Unlimited' if self.max_videos == 0 else self.max_videos}{RESET}")
        print(f"{C}  Stop after  : {W}2 consecutive failures{RESET}")

        while True:
            # Refresh limits periodically
            self.fetch_limits()

            # Check limits
            if self.cur_hour >= self.hourly_limit:
                print(f"\n{Y}☕ Hourly limit reached ({self.cur_hour}/{self.hourly_limit}). Stopping.{RESET}")
                break

            if self.cur_day >= self.daily_limit:
                print(f"\n{G}✓ Daily limit reached ({self.cur_day}/{self.daily_limit}). Done!{RESET}")
                break

            if self.max_videos > 0 and self.videos_done >= self.max_videos:
                print(f"\n{G}✓ Max videos limit reached ({self.videos_done}/{self.max_videos}). Done!{RESET}")
                break

            print(f"\n{M}▶ Fetching video task...{RESET}")
            task = self.get_task()
            if not task:
                # Jika get_task gagal karena limitDay, cur_day sudah di-set = daily_limit, loop berikutnya akan break
                if self.cur_day >= self.daily_limit:
                    continue  # akan break di awal loop berikutnya
                print(f"{Y}! No task available, waiting 5s...{RESET}")
                time.sleep(5)
                continue

            task_id = task.get("id")
            yt_url = task.get("href", "")
            duration = int(task.get("duration", 15))
            price = float(task.get("price", 0.0005))
            self.balance = float(task.get("balance", self.balance))

            watch_time = max(16, duration + 3)
            self.cur_hour += 1
            self.cur_day += 1

            print_task(task_id, yt_url, watch_time, price)

            # Progress bar
            show_progress(watch_time)

            success, result = self.claim_task(task_id)
            if success:
                self.failures = 0  # reset failure counter on success
                self.videos_done += 1
                self.completed_today += 1
                self.total_earned += price
                self.balance += price
                self.save_state()
                print_success(
                    price,
                    self.balance,
                    self.cur_hour,
                    self.hourly_limit,
                    self.cur_day,
                    self.daily_limit
                )
            else:
                self.failures += 1
                print(f"  {R}✗ Claim failed: {result}{RESET} (failure {self.failures}/2)")
                if self.failures >= 2:
                    print(f"{R}✗ Too many consecutive failures. Stopping.{RESET}")
                    break
                # Jika failure karena limit, kita break juga? tapi lebih baik biarkan counter gagal
                if "limit" in str(result).lower():
                    print(f"{Y}☕ Server limit detected. Cooldown 3 min...{RESET}")
                    self._cooldown(180)

            time.sleep(2)

        # Finish
        reason = "STOPPED (failures)" if self.failures >= 2 else "FINISHED"
        if self.cur_day >= self.daily_limit:
            reason = "DAILY LIMIT REACHED"
        elif self.cur_hour >= self.hourly_limit:
            reason = "HOURLY LIMIT REACHED"
        elif self.max_videos > 0 and self.videos_done >= self.max_videos:
            reason = "MAX VIDEOS REACHED"

        print_finished(self.completed_today, self.total_earned, self.balance, reason)
        input(f"{C}Press Enter to exit...{RESET}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    try:
        bot = FomoEarnBot()
        bot.run()
    except KeyboardInterrupt:
        print(f"\n\n{Y}[!] Bot stopped by user. Goodbye!{RESET}\n")
        sys.exit(0)
