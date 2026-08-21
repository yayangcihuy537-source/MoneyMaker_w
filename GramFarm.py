#!/usr/bin/env python3
"""
FarmVerse Auto Bot - Daily, Farm, Ads
ScriptMaker : ScriptyXSou
Channel : t.me/ScriptyXSouu
"""

import requests
import json
import time
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

# ============================================================
# WARNA GLOBAL (LENGKAP)
# ============================================================
R = '\033[91m'      # RED
G = '\033[92m'      # GREEN
Y = '\033[93m'      # YELLOW
B = '\033[94m'      # BLUE
M = '\033[95m'      # MAGENTA
C = '\033[96m'      # CYAN
W = '\033[97m'      # WHITE
X = '\033[0m'       # RESET (sama dengan RESET)

# Tambahan alias untuk kemudahan
RED = R
GREEN = G
YELLOW = Y
CYAN = C
PINK = '\033[38;5;206m'
GOLD = '\033[38;5;220m'
DIM = '\033[2;37m'
BLD = '\033[1m'
RS = X
RESET = X
WHITE = W   # <-- ini yang tadi kurang

class FarmverseBot:
    def __init__(self, init_data: str = ""):
        self.base_url = "https://farmverse.fun"
        self.init_data = init_data
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.1',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'Origin': self.base_url,
            'Referer': self.base_url + '/?tgWebAppStartParam=ref_88BF9D35',
            'X-Requested-With': 'org.telegram.messenger.web',
        })
        self.device_id = "aca602fa2fe04868a371af0d3d3667c6"
        self.fingerprint = "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.1 (Samsung SM-A556E; Android 16; SDK 36; HIGH)|Android|id-ID|8|8|384x832x24|-420|5"
        self.token = None
        self.user = None
        self.config = None
        self.coins = 0
        self.total_earned = 0
        self.daily_status = {}
        self.farm_status = {}
        self.ads_status = {}
        self.logs: List[str] = []
        self.running = False
        self.total_gain = 0

    def _log(self, msg: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "SUCCESS": GREEN,
            "ERROR": RED,
            "WARNING": YELLOW,
            "INFO": CYAN,
            "ACTION": PINK,
        }
        color = color_map.get(level, WHITE)  # WHITE sekarang sudah defined
        entry = f"{color}[{timestamp}] {msg}{RESET}"
        self.logs.append(entry)
        if len(self.logs) > 6:
            self.logs.pop(0)

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Optional[Dict]:
        url = self.base_url + endpoint
        req_headers = self.session.headers.copy()
        if self.token:
            req_headers['Authorization'] = f'Bearer {self.token}'
        if headers:
            req_headers.update(headers)
        try:
            resp = self.session.request(method, url, json=data, params=params, headers=req_headers)
            if resp.status_code in [200, 304]:
                if resp.headers.get('content-type', '').startswith('application/json'):
                    return resp.json()
                return {"raw": resp.text}
            else:
                self._log(f"Request {method} {endpoint} failed: {resp.status_code} - {resp.text[:100]}", "ERROR")
                return None
        except Exception as e:
            self._log(f"Request error: {e}", "ERROR")
            return None

    def auth(self) -> bool:
        if not self.init_data:
            self._log("InitData kosong!", "ERROR")
            return False

        payload = {
            "deviceId": self.device_id,
            "fingerprint": self.fingerprint,
            "startParam": "ref_88BF9D35",
            "initData": self.init_data
        }
        self._log("Autentikasi...", "INFO")
        result = self._request("POST", "/api/auth/verify", data=payload)
        if result and "token" in result:
            self.token = result["token"]
            self._log("Auth berhasil!", "SUCCESS")
            self.get_me()
            return True
        self._log("Auth gagal!", "ERROR")
        return False

    def get_me(self) -> bool:
        result = self._request("GET", "/api/me")
        if result and "user" in result:
            self.user = result["user"]
            self.config = result.get("config")
            self.coins = self.user.get("coins", 0)
            self.total_earned = self.user.get("totalEarned", 0)
            self._log(f"Coins: {self.coins} | Total Earned: {self.total_earned}", "INFO")
            return True
        return False

    def get_daily_status(self) -> bool:
        result = self._request("GET", "/api/daily")
        if result:
            self.daily_status = result
            return True
        return False

    def get_farm_status(self) -> bool:
        result = self._request("GET", "/api/farm")
        if result:
            self.farm_status = result
            return True
        return False

    def get_ads_status(self) -> bool:
        result = self._request("GET", "/api/ads/status")
        if result:
            self.ads_status = result
            return True
        return False

    def _watch_ad(self, duration: int = 25) -> bool:
        """Progress bar untuk nonton iklan, return True selalu"""
        for i in range(1, duration+1):
            bar = f"[{'█'*i}{'░'*(duration-i)}] {int(i/duration*100)}%"
            sys.stdout.write(f"\r{DIM}{bar} {i}s/{duration}s{RS}")
            sys.stdout.flush()
            time.sleep(1)
        print()
        return True

    def start_daily_ad(self) -> Optional[str]:
        result = self._request("POST", "/api/daily/start", data={"provider": "adsgram"})
        if result and "token" in result:
            return result["token"]
        return None

    def click_ad(self, token: str) -> bool:
        result = self._request("POST", "/api/ads/click", data={"token": token})
        if result and result.get("ok"):
            return True
        return False

    def claim_daily_reward(self, token: str) -> bool:
        result = self._request("POST", "/api/daily/claim", data={"token": token, "clicked": True})
        if result and result.get("ok"):
            reward = result.get("reward", 0)
            coins = result.get("coins", 0)
            self.coins = coins
            self.total_gain += reward
            self._log(f"Daily claimed! +{reward} coins (streak {result.get('streak', 0)})", "SUCCESS")
            return True
        return False

    def start_farm_ad(self, phase: str = "claim") -> Optional[str]:
        payload = {"provider": "adsgram", "phase": phase}
        result = self._request("POST", "/api/farm/ad/start", data=payload)
        if result and "token" in result:
            return result["token"]
        return None

    def claim_farm(self, token: str) -> bool:
        result = self._request("POST", "/api/farm/claim", data={"tokens": [token], "clicked": True})
        if result and result.get("ok"):
            reward = result.get("reward", 0)
            coins = result.get("coins", 0)
            self.coins = coins
            self.total_gain += reward
            self._log(f"Farm claimed! +{reward} coins (total: {coins})", "SUCCESS")
            return True
        return False

    def claim_daily(self) -> bool:
        self.get_daily_status()
        if self.daily_status.get("cooldownLeft", 0) > 0:
            self._log(f"Daily cooldown {self.daily_status['cooldownLeft']}s, skip", "WARNING")
            return False

        watched = self.daily_status.get("watchedToday", 0)
        limit = self.daily_status.get("dailyLimit", 30)
        if watched >= limit:
            self._log(f"Daily limit reached ({watched}/{limit})", "WARNING")
            return False

        self._log("Starting daily claim...", "ACTION")
        token = self.start_daily_ad()
        if not token:
            self._log("Failed to start daily ad", "ERROR")
            return False

        self._watch_ad(25)

        if not self.click_ad(token):
            self._log("Failed to click ad", "ERROR")
            return False

        if not self.claim_daily_reward(token):
            self._log("Failed to claim daily reward", "ERROR")
            return False

        self.get_me()
        return True

    def process_farm_claim(self) -> bool:
        self.get_farm_status()
        status = self.farm_status.get("status", "idle")
        seconds_left = self.farm_status.get("secondsLeft", 0)

        if status == "farming":
            if seconds_left > 0:
                self._log(f"Farming in progress, {seconds_left}s left", "INFO")
                return False
            else:
                self._log("Farming ready to claim, watching ad...", "ACTION")
                token = self.start_farm_ad("claim")
                if not token:
                    self._log("Failed to start claim ad", "ERROR")
                    return False
                self._watch_ad(25)
                if not self.click_ad(token):
                    self._log("Failed to click", "ERROR")
                    return False
                if not self.claim_farm(token):
                    self._log("Failed to claim farm", "ERROR")
                    return False
                self.get_me()
                return True
        elif status == "idle":
            self._log("Farming idle, need to start farming first...", "ACTION")
            token = self.start_farm_ad("start")
            if not token:
                self._log("Failed to start farm ad", "ERROR")
                return False
            self._watch_ad(25)
            if not self.click_ad(token):
                self._log("Failed to click", "ERROR")
                return False
            self.get_farm_status()
            if self.farm_status.get("status") == "farming":
                self._log("Farming started! Waiting for 60 minutes.", "SUCCESS")
                return True
            else:
                self._log("Farming status not changed, maybe need additional step", "WARNING")
                return False
        else:
            self._log(f"Unknown farm status: {status}", "WARNING")
            return False

    def watch_ads(self, count: int = 10) -> bool:
        """Watch ads count times (each ad: start -> watch 25s -> click -> claim)"""
        self.get_ads_status()
        watched = self.ads_status.get("watchedToday", 0)
        limit = self.ads_status.get("dailyLimit", 30)
        if watched >= limit:
            self._log(f"ADS limit reached ({watched}/{limit})", "WARNING")
            return False

        available = limit - watched
        to_watch = min(count, available)
        if to_watch <= 0:
            self._log("No ads available to watch", "WARNING")
            return False

        self._log(f"Watching {to_watch} ads...", "ACTION")
        success = 0
        for i in range(1, to_watch+1):
            self._log(f"Ad {i}/{to_watch}", "INFO")
            # Start ad
            token = self._request("POST", "/api/ads/start", data={"provider": "adsgram"})
            if not token or not token.get("token"):
                self._log(f"Failed to start ad {i}", "ERROR")
                continue
            token = token["token"]
            self._watch_ad(25)
            if not self.click_ad(token):
                self._log(f"Failed to click ad {i}", "ERROR")
                continue
            # Claim reward
            claim_res = self._request("POST", "/api/ads/claim", data={"clicked": True})
            if claim_res and claim_res.get("ok"):
                reward = claim_res.get("reward", 0)
                coins = claim_res.get("coins", 0)
                self.coins = coins
                self.total_gain += reward
                self._log(f"Ad {i} claimed! +{reward} coins", "SUCCESS")
                success += 1
            else:
                self._log(f"Failed to claim ad {i}", "ERROR")
            # Tunggu 30 detik setelah setiap ad (kecuali terakhir)
            if i < to_watch:
                self._log(f"Waiting 30s before next ad...", "INFO")
                for j in range(30, 0, -1):
                    sys.stdout.write(f"\r{DIM}⏳ {j}s{RS}")
                    sys.stdout.flush()
                    time.sleep(1)
                print()

        self._log(f"Watched {success}/{to_watch} ads successfully", "INFO")
        self.get_me()
        return success > 0

    def _render_box(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        width = 58
        border = "═" * width
        print(f"{PINK}╔{border}╗{RESET}")
        print(f"{PINK}║{RESET}  {BLD}FARMVERSE BOT{RESET}  {PINK}⚡{RESET}  {YELLOW}(FARM){RESET}  {PINK}║{RESET}".ljust(width+3))
        print(f"{PINK}╠{border}╣{RESET}")
        bal_line = f"  Coins : {self.coins}  |  Total Earned : {self.total_earned}"
        print(f"{PINK}║{RESET} {bal_line:<{width-2}} {PINK}║{RESET}")
        print(f"{PINK}╠{border}╣{RESET}")

        daily_watched = self.daily_status.get("watchedToday", 0)
        daily_limit = self.daily_status.get("dailyLimit", 30)
        daily_cd = self.daily_status.get("cooldownLeft", 0)
        daily_line = f"  📅 Daily  {daily_watched}/{daily_limit}  cooldown: {daily_cd}s"
        print(f"{PINK}║{RESET} {daily_line:<{width-2}} {PINK}║{RESET}")

        farm_status = self.farm_status.get("status", "idle")
        farm_seconds = self.farm_status.get("secondsLeft", 0)
        farm_pending = self.farm_status.get("pending", 0)
        farm_line = f"  🌾 Farm   {farm_status}  {farm_seconds}s left  pending:{farm_pending}"
        print(f"{PINK}║{RESET} {farm_line:<{width-2}} {PINK}║{RESET}")

        ads_watched = self.ads_status.get("watchedToday", 0)
        ads_limit = self.ads_status.get("dailyLimit", 30)
        ads_cd = self.ads_status.get("cooldownLeft", 0)
        ads_line = f"  📺 ADS    {ads_watched}/{ads_limit}  cooldown: {ads_cd}s"
        print(f"{PINK}║{RESET} {ads_line:<{width-2}} {PINK}║{RESET}")

        print(f"{PINK}╠{border}╣{RESET}")

        log_lines = self.logs[-6:]
        for line in log_lines:
            print(f"{PINK}║{RESET} {line:<{width-2}} {PINK}║{RESET}")

        print(f"{PINK}╚{border}╝{RESET}")
        print(f"{PINK}  {YELLOW}Total gain this session: +{self.total_gain} coins{RESET}")

    def run_all(self):
        if not self.auth():
            self._log("Auth gagal, cek initData!", "ERROR")
            self._render_box()
            return

        self.running = True
        self.total_gain = 0
        self.logs.clear()
        self._log("Mulai eksekusi...", "ACTION")
        self._render_box()

        # Update status awal
        self.get_daily_status()
        self.get_farm_status()
        self.get_ads_status()
        self._render_box()

        # ALUR:
        # 1. Claim daily 1x (jika belum)
        # 2. Tunggu 30 detik
        # 3. Claim farm 1x (jika siap)
        # 4. Tunggu 30 detik
        # 5. Watch ads 10x (masing-masing dengan jeda 30 detik)
        # 6. Ulangi dari awal (cek daily & farm lagi, watch ads lagi jika masih ada limit)

        while self.running:
            # --- DAILY ---
            self.get_daily_status()
            if not self.daily_status.get("claimedToday", False):
                self._log("Claim daily (1x)...", "ACTION")
                self.claim_daily()
                self._render_box()
                # Tunggu 30 detik
                self._log("Waiting 30s after daily...", "INFO")
                for i in range(30, 0, -1):
                    sys.stdout.write(f"\r{DIM}⏳ {i}s{RS}")
                    sys.stdout.flush()
                    time.sleep(1)
                print()
            else:
                self._log("Daily already claimed today", "INFO")

            # --- FARM ---
            self.get_farm_status()
            if self.farm_status.get("status") == "idle" or self.farm_status.get("secondsLeft", 0) <= 0:
                self._log("Claim farm (1x)...", "ACTION")
                self.process_farm_claim()
                self._render_box()
                # Tunggu 30 detik
                self._log("Waiting 30s after farm...", "INFO")
                for i in range(30, 0, -1):
                    sys.stdout.write(f"\r{DIM}⏳ {i}s{RS}")
                    sys.stdout.flush()
                    time.sleep(1)
                print()
            else:
                self._log("Farming still in progress, skip claim", "INFO")

            # --- ADS ---
            self.get_ads_status()
            watched = self.ads_status.get("watchedToday", 0)
            limit = self.ads_status.get("dailyLimit", 30)
            if watched < limit:
                self._log("Watch ads 10x...", "ACTION")
                self.watch_ads(10)
                self._render_box()
                # Tunggu 30 detik setelah watch ads (opsional)
                self._log("Waiting 30s after ads...", "INFO")
                for i in range(30, 0, -1):
                    sys.stdout.write(f"\r{DIM}⏳ {i}s{RS}")
                    sys.stdout.flush()
                    time.sleep(1)
                print()
            else:
                self._log("ADS limit reached, no more ads today", "WARNING")
                # Jika daily sudah claim dan farm idle/tidak bisa claim, dan ads habis, kita stop
                if self.daily_status.get("claimedToday", False) and (self.farm_status.get("status") == "idle" or self.farm_status.get("secondsLeft", 0) <= 0):
                    self._log("All tasks done for now. Exiting...", "SUCCESS")
                    self.running = False
                    break

            # Cek jika semua limit habis, stop
            self.get_ads_status()
            if self.ads_status.get("watchedToday", 0) >= self.ads_status.get("dailyLimit", 30):
                if self.daily_status.get("claimedToday", False):
                    self._log("Daily claimed, ads limit reached. Bot will stop.", "INFO")
                    self.running = False
                    break

            # Tunggu sebentar sebelum loop lagi (opsional)
            self._log("Menunggu 5 detik sebelum siklus berikutnya...", "INFO")
            time.sleep(5)
            self._render_box()

        self._log("Bot berhenti.", "INFO")
        self._render_box()

    def set_init_data(self):
        print(f"{CYAN}Masukkan initData (dari Telegram WebApp):{RESET}")
        new_data = input("> ").strip()
        if new_data:
            self.init_data = new_data
            print(f"{GREEN}InitData diperbarui.{RESET}")
        else:
            print(f"{YELLOW}InitData tidak berubah.{RESET}")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    banner = r"""
   ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄ 
  ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
  ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀▀▀▀█░▌
  ▐░▌          ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌       ▐░▌
  ▐░█▄▄▄▄▄▄▄▄▄ ▐░▌       ▐░▌▐░▌       ▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░▌       ▐░▌
  ▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░▌       ▐░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌
   ▀▀▀▀▀▀▀▀▀█░▌▐░▌       ▐░▌▐░▌       ▐░▌ ▀▀▀▀▀▀▀▀▀█░▌▐░▌       ▐░▌
            ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌          ▐░▌▐░▌       ▐░▌
   ▄▄▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌ ▄▄▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌
  ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌
   ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀ 
    """
    print(f"{PINK}{banner}{RESET}")
    print(f"{PINK}{BLD}        FarmVerse Auto Bot - Daily + Farm + Ads{RESET}")
    print(f"{PINK}{BLD}        ScriptMaker : ScriptyXSou{RESET}")
    print(f"{PINK}{BLD}        Channel : t.me/ScriptyXSouu{RESET}\n")

def main():
    bot = FarmverseBot()
    while True:
        clear_screen()
        print_banner()
        print(f"{CYAN}1. Start All Live Log{RESET}")
        print(f"{CYAN}2. Set InitData (wajib diisi sebelum start){RESET}")
        print(f"{CYAN}0. Exit{RESET}")
        choice = input(f"{YELLOW}Pilih menu: {RESET}").strip()

        if choice == "1":
            if not bot.init_data:
                print(f"{RED}InitData belum diset! Silakan pilih menu 2.{RESET}")
                input(f"{YELLOW}\nTekan Enter untuk kembali...{RESET}")
                continue
            bot.run_all()
            input(f"{YELLOW}\nTekan Enter untuk kembali ke menu...{RESET}")
        elif choice == "2":
            bot.set_init_data()
            input(f"{YELLOW}\nTekan Enter untuk kembali...{RESET}")
        elif choice == "0":
            print(f"{PINK}Terima kasih, sampai jumpa!{RESET}")
            break
        else:
            print(f"{RED}Pilihan tidak valid!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{PINK}Program dihentikan oleh pengguna.{RESET}")
        sys.exit(0)
