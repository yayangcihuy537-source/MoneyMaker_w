#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pitcoin Auto Claim & Boost Bot
- Auto Claim Mining setiap 10 menit
- Auto Boost (Watch Ads) setiap 10 menit
- Auto Claim Quests (Daily Check-in, Join Channel, dll.)
- Watch Ads 30 detik untuk speed boost +0.5 TH/s

============================================================
👨‍💻 ScriptMaker : @JoshuaXSupport
📢 TG          : https://t.me/+f3QBLkR5D8k4YzNl
============================================================
"""

import requests
import json
import time
import urllib.parse
from datetime import datetime
from typing import Dict, Optional

# ============================================================
# WARNA ANSI
# ============================================================
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GRAY = "\033[90m"

def pprint(msg, color=GREEN):
    print(f"{color}{msg}{RESET}")

def print_sep():
    print(f"{GRAY}{'='*60}{RESET}")

def print_info(msg):
    print(f"{BLUE}🚀 [INFO]{RESET} {msg}")

def print_ok(msg):
    print(f"{GREEN}✅ [ OK ]{RESET} {msg}")

def print_wait(msg):
    print(f"{YELLOW}⏳ [WAIT]{RESET} {msg}")

def print_error(msg):
    print(f"{RED}❌ [ERR ]{RESET} {msg}")

def print_success(msg):
    print(f"{GREEN}💰 [REWARD]{RESET} {msg}")

def countdown(seconds, msg="⏳ Menunggu"):
    while seconds > 0:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            time_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            time_str = f"{minutes:02d}:{secs:02d}"
        print(f"\r{msg} {time_str}   ", end="", flush=True)
        time.sleep(1)
        seconds -= 1
    print(f"\r{msg} selesai!     ")

# ============================================================
# CLASS PITCOIN
# ============================================================
class Pitcoin:
    BASE_URL = "https://pitcoin.onrender.com"

    def __init__(self, init_data: str):
        self.init_data = init_data
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 Mobile Safari/537.36 Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Origin": self.BASE_URL,
            "Referer": self.BASE_URL + "/app",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Sec-Ch-Ua": '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "X-Telegram-Init-Data": init_data,
            "Content-Type": "application/json",
        })

    def _request(self, method: str, endpoint: str, json_data: Optional[Dict] = None):
        url = self.BASE_URL + endpoint
        try:
            resp = self.session.request(method, url, json=json_data, timeout=30)
            if resp.status_code != 200:
                return {"error": resp.status_code, "text": resp.text[:200]}
            return resp.json()
        except Exception as e:
            return {"error": "exception", "text": str(e)}

    # ===== API ENDPOINTS =====
    def get_user(self) -> Dict:
        return self._request("GET", "/api/user")

    def claim_mine(self) -> Dict:
        return self._request("POST", "/api/mine/claim")

    def boost_overclock(self) -> Dict:
        return self._request("POST", "/api/boost/overclock")

    def complete_quest(self, quest_id: str) -> Dict:
        return self._request("POST", "/api/quests/complete", json_data={"questId": quest_id})

    def get_quests(self) -> Dict:
        return self._request("GET", "/api/quests")

# ============================================================
# FUNGSI BANTU
# ============================================================
def parse_init_data(init_data: str) -> Dict:
    parsed = urllib.parse.parse_qs(init_data)
    user_str = parsed.get("user", [""])[0]
    try:
        user_obj = json.loads(user_str)
    except:
        user_obj = {}
    return {
        "tg_id": str(user_obj.get("id", "")),
        "username": user_obj.get("username", ""),
        "full_name": f"{user_obj.get('first_name', '')} {user_obj.get('last_name', '')}".strip()
    }

def get_timestamp_ms() -> int:
    return int(time.time() * 1000)

def ms_to_seconds(ms: int) -> int:
    return ms // 1000

# ============================================================
# MAIN BOT
# ============================================================
class PitcoinBot:
    def __init__(self, init_data: str):
        self.init_data = init_data
        self.bot = Pitcoin(init_data)
        self.user_info = parse_init_data(init_data)
        self.tg_id = self.user_info["tg_id"]
        self.username = self.user_info["username"]
        self.full_name = self.user_info["full_name"] or self.username

        # State
        self.balance = 0.0
        self.last_claim_time = 0
        self.ad_boost_end_time = 0
        self.completed_quests = []
        self.is_ad_boost_active = False
        self.active_th_s = 0.2

    def update_user_data(self) -> bool:
        res = self.bot.get_user()
        if res.get("error"):
            print_error(f"Gagal ambil user: {res}")
            return False

        user = res.get("user", {})
        mining = res.get("miningState", {})

        self.balance = user.get("claimedPITBalance", 0.0)
        self.last_claim_time = user.get("lastClaimTime", 0)
        self.completed_quests = user.get("completedQuests", [])
        self.is_ad_boost_active = mining.get("isAdBoostActive", False)
        self.ad_boost_end_time = mining.get("adBoostTimeRemainingMs", 0)
        self.active_th_s = mining.get("activeTHs", 0.2)
        return True

    def get_claimable_amount(self) -> float:
        res = self.bot.get_user()
        if res.get("error"):
            return 0.0
        return res.get("user", {}).get("accumulatedPIT", 0.0)

    def claim_mining(self) -> bool:
        print_info("🔄 Claim mining...")
        res = self.bot.claim_mine()
        if res.get("error"):
            print_error(f"Gagal claim: {res}")
            return False

        if res.get("success"):
            amount = res.get("claimedAmount", 0)
            new_balance = res.get("newBalance", self.balance)
            self.balance = new_balance
            print_success(f"Claim mining berhasil! +{amount:.4f} PIT")
            print_ok(f"Balance: {self.balance:.4f} PIT")
            return True
        return False

    def boost_overclock(self) -> bool:
        print_info("📺 Watch Ads untuk Boost...")
        res = self.bot.boost_overclock()
        if res.get("error"):
            print_error(f"Gagal boost: {res}")
            return False

        if res.get("success"):
            message = res.get("message", "")
            mining = res.get("miningState", {})
            self.is_ad_boost_active = mining.get("isAdBoostActive", False)
            self.ad_boost_end_time = mining.get("adBoostTimeRemainingMs", 0)
            self.active_th_s = mining.get("activeTHs", 0.2)

            print_ok(f"Boost aktif! Speed: {self.active_th_s:.2f} TH/s")
            if self.ad_boost_end_time > 0:
                remaining_sec = ms_to_seconds(self.ad_boost_end_time)
                print_wait(f"Boost tersisa: {remaining_sec//60}m {remaining_sec%60}s")
            return True
        return False

    def check_and_claim_quests(self) -> bool:
        print_info("📋 Mengecek Quests...")
        res = self.bot.get_quests()
        if res.get("error"):
            print_wait("Tidak ada quest atau gagal ambil")
            return False

        quests = res.get("quests", []) if isinstance(res.get("quests"), list) else []
        if not quests:
            print_wait("Tidak ada quest tersedia")
            return False

        claimed_any = False
        for quest in quests:
            quest_id = quest.get("id")
            if not quest_id:
                continue
            if quest_id in self.completed_quests:
                continue

            title = quest.get("title", quest_id)
            reward = quest.get("reward", 0)
            print_info(f"🔄 Mencoba quest: {title} (reward: {reward})")

            res = self.bot.complete_quest(quest_id)
            if res.get("error"):
                print_error(f"Gagal complete quest: {res}")
                continue

            if res.get("success"):
                # Update balance dari response
                user = res.get("user", {})
                self.balance = user.get("claimedPITBalance", self.balance)
                self.completed_quests.append(quest_id)
                print_success(f"Quest completed! +{reward} PIT")
                claimed_any = True
            else:
                print_wait(f"Quest {title} belum bisa di-claim")

        return claimed_any

    def run_cycle(self) -> bool:
        print_sep()
        print_info(f"🔄 Siklus baru - {datetime.now().strftime('%H:%M:%S')}")

        if not self.update_user_data():
            print_error("Gagal update data user, lanjut...")

        print_info(f"💰 Balance: {self.balance:.4f} PIT")
        print_info(f"⚡ Speed: {self.active_th_s:.2f} TH/s")

        # 1. Quests
        self.check_and_claim_quests()

        # 2. Boost (Watch Ads) - jika belum aktif
        if not self.is_ad_boost_active:
            print_info("⚡ Boost tidak aktif, menonton iklan...")
            self.boost_overclock()
            print_wait("Jeda 5 detik setelah boost...")
            time.sleep(5)

        # 3. Claim Mining
        claimable = self.get_claimable_amount()
        if claimable > 0:
            self.claim_mining()
        else:
            print_wait("Belum ada PIT yang bisa di-claim, tunggu...")

        self.update_user_data()
        print_ok(f"💰 Balance akhir: {self.balance:.4f} PIT")
        print_sep()
        return True

    def run_loop(self):
        cycle_count = 0

        print_header()
        print_ok(f"Login sebagai: @{self.full_name} (ID: {self.tg_id})")
        print_sep()

        self.update_user_data()
        print_ok(f"💰 Balance awal: {self.balance:.4f} PIT")
        print_ok(f"⚡ Speed: {self.active_th_s:.2f} TH/s")
        print_sep()
        print_info("🚀 Bot siap berjalan!")
        print_info("📌 Claim setiap 10 menit, Boost otomatis")
        print_wait("Tekan Ctrl+C untuk berhenti")
        print_sep()

        while True:
            try:
                cycle_count += 1
                print_info(f"📊 Siklus #{cycle_count}")

                self.run_cycle()

                # Hitung waktu tunggu hingga 10 menit atau sampai boost habis
                wait_time = 600  # 10 menit default
                if self.ad_boost_end_time > 0:
                    remaining_ms = self.ad_boost_end_time
                    remaining_sec = ms_to_seconds(remaining_ms)
                    if remaining_sec > 0 and remaining_sec < wait_time:
                        wait_time = remaining_sec + 5

                print_wait(f"⏳ Jeda {wait_time//60}m {wait_time%60}s sebelum siklus berikutnya...")
                countdown(wait_time, "⏳ Menunggu")

            except KeyboardInterrupt:
                print("\n")
                print_wait("⏹️ Bot dihentikan oleh user")
                break
            except Exception as e:
                print_error(f"Error dalam loop: {e}")
                print_wait("Tunggu 30 detik sebelum coba lagi...")
                countdown(30, "⏳ Cooldown error")

        print_sep()
        print_ok("📊 BOT BERHENTI")
        print_ok(f"💰 Balance akhir: {self.balance:.4f} PIT")
        print_sep()

# ============================================================
# HEADER & MAIN
# ============================================================
def print_header():
    print(f"""
{BLUE}╔══════════════════════════════════════════════════════════════╗
║{WHITE}  Pitcoin Auto Claim & Boost Bot - {CYAN}Premium{WHITE}                    ║
║{WHITE}  Auto Claim Mining, Boost, Quests                        ║
╚══════════════════════════════════════════════════════════════╝{RESET}
{BLUE}============================================================{RESET}
{CYAN}👨‍💻 ScriptMaker : {WHITE}@JoshuaXSupport{RESET}
{CYAN}📢 TG          : {WHITE}https://t.me/+f3QBLkR5D8k4YzNl{RESET}
{BLUE}============================================================{RESET}
    """)

def get_init_data_from_user() -> str:
    print(f"\n{YELLOW}📌 Cara mendapatkan init_data:{RESET}")
    print(f"1. Buka {CYAN}https://pitcoin.onrender.com/app{RESET} di browser")
    print(f"2. Buka {CYAN}Developer Tools (F12) -> Network tab{RESET}")
    print(f"3. Cari request ke {CYAN}/api/user{RESET}")
    print(f"4. Lihat header {CYAN}'X-Telegram-Init-Data'{RESET}")
    print(f"5. Copy seluruh isinya (panjang bisa 200-500 karakter)")
    print_sep()
    init_data = input(f"\n📝 {BOLD}Paste X-Telegram-Init-Data di sini:{RESET} ").strip()
    if not init_data:
        print_error("Init data tidak boleh kosong!")
        return get_init_data_from_user()
    return init_data

def main():
    print_header()

    init_data = get_init_data_from_user()

    bot = PitcoinBot(init_data)
    bot.run_loop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n")
        print_wait("⏹️ Dibatalkan oleh user")
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
