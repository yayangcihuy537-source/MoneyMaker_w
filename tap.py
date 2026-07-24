#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║  🐶 BABYDOGE TAP BOT v2.9                                     ║
║  🔐 Login via InitData                                         ║
║  👆 Auto Tap (batch mode - tap banyak sekaligus)              ║
║  🎯 Auto Claim (Streak + Spin + Tasks)                       ║
║  ⏳ Task submit auto tunggu & retry sampai berhasil          ║
║  🔄 Auto re-init jika token kosong/expired                   ║
║  🔑 Auto update tapToken setiap tap                          ║
║  📊 Set Tap Limit & Batch Size                              ║
║  💸 Withdraw dengan input nominal & set address            ║
║  👑 Owner: @MoneyMaker_w                                      ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import requests
import json
import os
import sys
import time
import random
import re
import uuid
from datetime import datetime

# ==================== WARNA ====================
RED = "\033[38;5;196m"
GOLD = "\033[38;5;220m"
YELLOW = "\033[1;93m"
GREEN = "\033[1;92m"
CYAN = "\033[1;96m"
BLUE = "\033[38;5;39m"
PURPLE = "\033[38;5;141m"
PINK = "\033[38;5;206m"
LIME = "\033[38;5;154m"
DIM = "\033[90m"
WHITE = "\033[1;97m"
RESET = "\033[0m"

# ==================== BANNER ====================
BANNER = rf"""{CYAN}

██████╗  █████╗ ██████╗ ██╗   ██╗
██╔══██╗██╔══██╗██╔══██╗╚██╗ ██╔╝
██████╔╝███████║██████╔╝ ╚████╔╝
██╔══██╗██╔══██║██╔══██╗  ╚██╔╝
██████╔╝██║  ██║██████╔╝   ██║
╚═════╝ ╚═╝  ╚═╝╚═════╝    ╚═╝

██████╗  ██████╗  ██████╗ ███████╗
██╔══██╗██╔═══██╗██╔════╝ ██╔════╝
██║  ██║██║   ██║██║  ███╗█████╗
██║  ██║██║   ██║██║   ██║██╔══╝
██████╔╝╚██████╔╝╚██████╔╝███████╗
╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝

{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{GREEN} 🤖 BOT        : @BabyDOGETapbot
{YELLOW} 👨‍💻 DEVELOPER : @MoneyMaker_w
{CYAN} ⚡ SCRIPT     : AUTO TAP • AUTO TASK • AUTO CLAIM
{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}
"""

# ==================== KONFIGURASI ====================
CONFIG_FILE = "babydoge_config.json"
BASE_URL = "https://panel-api.bleon.net"
BOT_NAME = "BabyDOGETapbot"

class Config:
    def __init__(self):
        self.init_data = None
        self.tap_limit = 0
        self.withdraw_address = ""
        self.tap_batch_size = 50
        self.tap_batch_delay_min = 3
        self.tap_batch_delay_max = 7

    def load(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.init_data = data.get('init_data')
                self.tap_limit = data.get('tap_limit', 0)
                self.withdraw_address = data.get('withdraw_address', "")
                self.tap_batch_size = data.get('tap_batch_size', 50)
                self.tap_batch_delay_min = data.get('tap_batch_delay_min', 3)
                self.tap_batch_delay_max = data.get('tap_batch_delay_max', 7)
                return True
        return False

    def save(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({
                'init_data': self.init_data,
                'tap_limit': self.tap_limit,
                'withdraw_address': self.withdraw_address,
                'tap_batch_size': self.tap_batch_size,
                'tap_batch_delay_min': self.tap_batch_delay_min,
                'tap_batch_delay_max': self.tap_batch_delay_max
            }, f, indent=2)

    def clear(self):
        self.init_data = None
        self.tap_limit = 0
        self.withdraw_address = ""
        self.tap_batch_size = 50
        self.tap_batch_delay_min = 3
        self.tap_batch_delay_max = 7
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)

# ==================== UTILITY ====================
def uuid4():
    return str(uuid.uuid4())

def random_delay(min_sec=1, max_sec=15):
    return random.uniform(min_sec, max_sec)

def extract_wait_seconds(error_msg):
    match = re.search(r'(\d+)\s*seconds?\s*to\s*go', error_msg, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def countdown_timer(seconds, message="⏳ Waiting"):
    frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    frame_idx = 0
    while seconds > 0:
        mins = seconds // 60
        secs = seconds % 60
        sys.stdout.write(f"\r{YELLOW}{message}: {mins:02d}:{secs:02d}  {frames[frame_idx]}{RESET}")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
        frame_idx = (frame_idx + 1) % len(frames)
    print(f"\r{YELLOW}{message}: 00:00 ✅{RESET}")

# ==================== BABYDOGE BOT ====================
class BabyDogeBot:
    def __init__(self, init_data, tap_limit=0, withdraw_address="", batch_size=50, batch_delay_min=3, batch_delay_max=7):
        self.init_data = init_data
        self.tap_limit = tap_limit
        self.withdraw_address = withdraw_address
        self.batch_size = batch_size
        self.batch_delay_min = batch_delay_min
        self.batch_delay_max = batch_delay_max
        self.session = requests.Session()
        self.base_url = BASE_URL
        self.bot_name = BOT_NAME
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.124 Mobile Safari/537.36 Telegram-Android/12.6.4 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Origin": "https://tapgame.bleon.net",
            "Referer": "https://tapgame.bleon.net/",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Connection": "keep-alive",
        }
        self.token = ""
        self.tap_token = ""
        self.balance = 0
        self.energy = 0
        self.tap_count = 0
        self.streak_count = 0
        self.total_earned = 0
        self.completed_tasks = []
        self.withdraw_address_set = withdraw_address

    def log(self, msg: str, level: str = "INFO"):
        t = datetime.now().strftime("%H:%M:%S")
        prefix = {"INFO": CYAN, "SUCCESS": GREEN, "WARNING": YELLOW, "ERROR": RED}.get(level, WHITE)
        print(f"{prefix}[{t}] {msg}{RESET}")

    def _request(self, endpoint: str, data: dict = None, multipart: bool = False) -> dict:
        url = f"{self.base_url}{endpoint}"
        headers = self.headers.copy()

        try:
            if multipart:
                headers.pop("Content-Type", None)
                files = {}
                if data:
                    for key, value in data.items():
                        files[key] = (None, str(value))
                resp = self.session.post(url, files=files, headers=headers, timeout=30)
            else:
                resp = self.session.post(url, json=data, headers=headers, timeout=30)

            if resp.status_code == 200:
                try:
                    return resp.json()
                except:
                    return {"ok": False, "error": "Invalid JSON"}
            else:
                try:
                    err = resp.json()
                    return {"ok": False, "error": err.get('message', f"HTTP {resp.status_code}")}
                except:
                    return {"ok": False, "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _update_player(self, data: dict):
        player = data.get("player", {})
        if player:
            self.balance = player.get("balance", self.balance)
            self.energy = player.get("energy", self.energy)
            self.tap_count = player.get("tapsTotal", self.tap_count)
            self.streak_count = player.get("streakDay", self.streak_count)
            withdraw_to = player.get("withdrawTo", "")
            if withdraw_to:
                self.withdraw_address_set = withdraw_to
        else:
            self.balance = data.get("balance", self.balance)
            self.energy = data.get("energy", self.energy)

    def init(self) -> bool:
        self.log("🔐 Init game...", "INFO")
        payload = {
            "bot": self.bot_name,
            "initData": self.init_data
        }
        result = self._request("/v1/game/init", data=payload)
        if result and result.get("ok"):
            self.token = result.get("token") or result.get("data", {}).get("token", "")
            self.tap_token = result.get("tapToken") or result.get("data", {}).get("tapToken", "")
            self._update_player(result)
            token_preview = self.token[:20] if self.token else "(empty)"
            tap_preview = self.tap_token[:20] if self.tap_token else "(empty)"
            self.log(f"✅ Init OK | Balance: {self.balance} | Energy: {self.energy} | Token: {token_preview}... | TapToken: {tap_preview}...", "SUCCESS")
            return True
        else:
            error = result.get('error') if result else 'No response'
            self.log(f"❌ Init failed: {error}", "ERROR")
            return False

    def ensure_token(self) -> bool:
        if not self.token:
            self.log("⚠️ Token kosong, re-init...", "WARNING")
            return self.init()
        if not self.tap_token:
            self.log("⚠️ TapToken kosong, ambil dari init...", "WARNING")
            return self.init()
        return True

    def refresh_tap_token(self):
        self.log("🔄 Refresh tapToken...", "INFO")
        return self.init()

    def tap(self, taps: int = 10) -> bool:
        if not self.ensure_token():
            return False

        tap_token_to_use = self.tap_token if self.tap_token else self.token

        payload = {
            "bot": self.bot_name,
            "initData": self.init_data,
            "taps": taps,
            "token": tap_token_to_use
        }
        result = self._request("/v1/game/tap", data=payload)

        if result and result.get("ok"):
            self._update_player(result)
            earned = result.get("gained", 0) or result.get("earned", 0)
            self.total_earned += earned
            self.tap_count += taps

            new_tap_token = result.get("tapToken")
            if new_tap_token:
                self.tap_token = new_tap_token
                self.log(f"✅ Tap {taps}x | Earned: {earned} | Balance: {self.balance} | Energy: {self.energy} | TapToken updated", "SUCCESS")
            else:
                self.log(f"✅ Tap {taps}x | Earned: {earned} | Balance: {self.balance} | Energy: {self.energy}", "SUCCESS")
            return True
        else:
            error = result.get('error') if result else 'No response'
            if 'cooldown' in str(error).lower():
                self.log(f"⏳ Tap cooldown", "WARNING")
                time.sleep(random_delay(5, 15))
                return False
            elif 'stale' in str(error).lower() or 'tapToken' in str(error).lower():
                self.log(f"⚠️ Stale tap session, refresh tapToken...", "WARNING")
                self.refresh_tap_token()
                return self.tap(taps)
            elif 'token' in str(error).lower() or 'invalid' in str(error).lower():
                self.log(f"⚠️ Token error, re-init...", "WARNING")
                self.token = ""
                self.tap_token = ""
                return self.tap(taps)
            else:
                self.log(f"❌ Tap failed: {error}", "ERROR")
                return False

    def claim_streak(self) -> bool:
        if not self.ensure_token():
            return False

        self.log("🔥 Claim streak...", "INFO")
        payload = {
            "bot": self.bot_name,
            "initData": self.init_data
        }
        result = self._request("/v1/game/streak", data=payload)
        if result and result.get("ok"):
            reward = result.get("reward", 0)
            self._update_player(result)
            self.streak_count += 1
            self.total_earned += reward
            self.log(f"✅ Streak claimed! Reward: {reward} | Balance: {self.balance}", "SUCCESS")
            return True
        else:
            error = result.get('error') if result else 'No response'
            if 'cooldown' in str(error).lower() or 'already' in str(error).lower():
                self.log(f"⏳ Streak: {error}", "WARNING")
            else:
                self.log(f"❌ Streak failed: {error}", "ERROR")
            return False

    def spin(self) -> bool:
        if not self.ensure_token():
            return False

        self.log("🎰 Spin...", "INFO")
        payload = {
            "bot": self.bot_name,
            "initData": self.init_data
        }
        result = self._request("/v1/game/spin", data=payload)
        if result and result.get("ok"):
            reward = result.get("reward", 0)
            self._update_player(result)
            self.total_earned += reward
            self.log(f"✅ Spin OK | Reward: {reward} | Balance: {self.balance}", "SUCCESS")
            return True
        else:
            error = result.get('error') if result else 'No response'
            if 'cooldown' in str(error).lower():
                self.log(f"⏳ Spin cooldown", "WARNING")
            else:
                self.log(f"❌ Spin failed: {error}", "ERROR")
            return False

    def get_tasks(self) -> list:
        if not self.ensure_token():
            return []

        self.log("📋 Ambil tasks...", "INFO")
        payload = {
            "bot": self.bot_name,
            "initData": self.init_data
        }
        result = self._request("/v1/game/tasks", data=payload)
        if result and result.get("ok"):
            tasks = result.get("tasks", [])
            self.log(f"📋 {len(tasks)} tasks available", "INFO")
            return tasks
        return []

    def start_task(self, task_id: str) -> bool:
        if not self.ensure_token():
            return False

        self.log(f"▶️ Start task {task_id[:8]}...", "INFO")
        payload = {
            "bot": self.bot_name,
            "initData": self.init_data,
            "task_id": task_id
        }
        result = self._request("/v1/game/task/start", data=payload)
        if result and result.get("ok"):
            self.log(f"✅ Task {task_id[:8]} started", "SUCCESS")
            return True
        else:
            error = result.get('error') if result else 'No response'
            self.log(f"❌ Start task failed: {error}", "ERROR")
            return False

    def submit_task(self, task_id: str, max_retries: int = 5) -> bool:
        if not self.ensure_token():
            return False

        for attempt in range(max_retries):
            self.log(f"📤 Submit task {task_id[:8]} (attempt {attempt+1}/{max_retries})...", "INFO")
            data = {
                "bot": self.bot_name,
                "initData": self.init_data,
                "task_id": task_id
            }
            result = self._request("/v1/game/task/submit", data=data, multipart=True)

            if result and result.get("ok"):
                reward = result.get("reward", 0)
                self._update_player(result)
                self.total_earned += reward
                self.completed_tasks.append(task_id)
                self.log(f"✅ Task {task_id[:8]} submitted! Reward: {reward}", "SUCCESS")
                return True
            else:
                error = result.get('error') if result else 'No response'
                wait_sec = extract_wait_seconds(str(error))
                if wait_sec:
                    self.log(f"⏳ Server minta tunggu {wait_sec} detik...", "WARNING")
                    countdown_timer(wait_sec, "⏳ Waiting before retry")
                    continue
                elif 'already' in str(error).lower():
                    self.log(f"⏳ Task already submitted", "WARNING")
                    return True
                else:
                    self.log(f"❌ Submit task failed: {error}", "ERROR")
                    return False

        self.log(f"❌ Gagal submit task {task_id[:8]} setelah {max_retries} percobaan", "ERROR")
        return False

    def claim_tasks(self):
        self.log("📋 Claim tasks...", "INFO")
        tasks = self.get_tasks()
        if not tasks:
            self.log("✅ Tidak ada task", "SUCCESS")
            return

        for task in tasks:
            task_id = task.get("id")
            status = task.get("status", "pending")
            title = task.get("title", "Unknown")[:25]

            if status == "pending":
                self.log(f"📌 Task: {title}", "INFO")
                if self.start_task(task_id):
                    delay = random_delay(2, 5)
                    time.sleep(delay)
                    self.submit_task(task_id)
                    delay = random_delay(1, 3)
                    time.sleep(delay)
                else:
                    self.log(f"⚠️ Gagal start task {title}, skip", "WARNING")
            else:
                self.log(f"⏭️ Skip {title} (status: {status})", "DIM")

    def set_withdraw_address(self, address: str) -> bool:
        if not self.ensure_token():
            return False

        self.log(f"💳 Set withdraw address: {address[:10]}...", "INFO")
        payload = {
            "bot": self.bot_name,
            "initData": self.init_data,
            "address": address
        }
        result = self._request("/v1/game/withdraw-address", data=payload)
        if result and result.get("ok"):
            self.withdraw_address_set = address
            self._update_player(result)
            self.log(f"✅ Withdraw address set!", "SUCCESS")
            return True
        else:
            error = result.get('error') if result else 'No response'
            self.log(f"❌ Set address failed: {error}", "ERROR")
            return False

    def withdraw(self, amount: int) -> bool:
        if not self.ensure_token():
            return False

        if amount <= 0:
            self.log(f"⚠️ Nominal harus > 0", "WARNING")
            return False

        if not self.withdraw_address_set:
            self.log(f"⚠️ Belum ada withdraw address!", "WARNING")
            return False

        self.log(f"💸 Withdraw {amount}...", "INFO")
        payload = {
            "bot": self.bot_name,
            "initData": self.init_data,
            "amount": amount
        }
        result = self._request("/v1/game/withdraw", data=payload)
        if result and result.get("ok"):
            self._update_player(result)
            self.log(f"✅ Withdraw {amount} successful! Sisa balance: {self.balance}", "SUCCESS")
            return True
        else:
            error = result.get('error') if result else 'No response'
            self.log(f"❌ Withdraw failed: {error}", "ERROR")
            return False

    def withdraw_menu(self):
        self.log("💸 WITHDRAW MENU", "INFO")

        if not self.init():
            self.log("❌ Init failed", "ERROR")
            return

        print(f"\n{CYAN}📊 Current Balance: {GREEN}{self.balance}{RESET}")

        if not self.withdraw_address_set:
            self.log(f"⚠️ Belum ada withdraw address!", "WARNING")
            addr = input(f"{YELLOW}📝 Masukkan alamat wallet (BEP-20): {RESET}").strip()
            if not addr:
                self.log(f"❌ Address kosong, withdraw dibatalkan", "ERROR")
                return
            if self.set_withdraw_address(addr):
                config = Config()
                config.load()
                config.withdraw_address = addr
                config.save()
            else:
                return

        print(f"\n{CYAN}💰 Balance saat ini: {GREEN}{self.balance}{RESET}")
        nominal_input = input(f"{YELLOW}📝 Masukkan nominal withdraw (atau ketik 'all' untuk semua): {RESET}").strip()

        if nominal_input.lower() == 'all':
            amount = self.balance
        else:
            try:
                amount = int(nominal_input)
            except:
                self.log(f"❌ Nominal harus angka atau 'all'", "ERROR")
                return

        if amount <= 0:
            self.log(f"❌ Nominal harus > 0", "ERROR")
            return

        if amount > self.balance:
            self.log(f"❌ Nominal melebihi balance! Balance: {self.balance}", "ERROR")
            return

        print(f"\n{YELLOW}⚠️ Konfirmasi withdraw:{RESET}")
        print(f"  Address: {self.withdraw_address_set}")
        print(f"  Amount : {amount}")
        confirm = input(f"{PINK}Lanjutkan? (y/n): {RESET}").strip().lower()

        if confirm == 'y':
            self.withdraw(amount)
        else:
            self.log("❌ Withdraw dibatalkan", "WARNING")

        self.show_status()

    def check_balance(self) -> bool:
        self.log("📊 Check balance...", "INFO")
        if not self.init():
            return False
        self.show_status()
        return True

    def show_status(self):
        addr_preview = self.withdraw_address_set[:12] + "..." if self.withdraw_address_set else "(not set)"
        print(f"""
{GREEN}╔══════════════════════════════════════════════════════════╗
║  🐶 BABYDOGE STATUS                                     ║
╠══════════════════════════════════════════════════════════╣
║  {WHITE}Balance {GREEN}: {self.balance}
║  {WHITE}Energy  {GREEN}: {self.energy}
║  {WHITE}Taps   {GREEN}: {self.tap_count}
║  {WHITE}Streak {GREEN}: {self.streak_count}
║  {WHITE}Earned {GREEN}: {self.total_earned}
║  {WHITE}Tasks  {GREEN}: {len(self.completed_tasks)}
║  {WHITE}Address{GREEN}: {addr_preview}
╚══════════════════════════════════════════════════════════╝{RESET}
""")

    # ==================== TAP BATCH MODE ====================
    def tap_batch(self):
        """Lakukan tap dalam batch tanpa jeda antar request"""
        batch_size = self.batch_size
        if batch_size <= 0:
            batch_size = 50

        taps_done_in_batch = 0
        while taps_done_in_batch < batch_size:
            # Cek energy
            if self.energy <= 0:
                self.log(f"⏳ Energy habis ({self.energy}), tunggu 60 detik...", "WARNING")
                time.sleep(60)
                self.init()
                continue

            # Tentukan jumlah tap per request (5-15)
            t = random.randint(5, 15)
            if taps_done_in_batch + t > batch_size:
                t = batch_size - taps_done_in_batch

            self.tap(t)
            taps_done_in_batch += t

            # Jeda kecil 0.3-0.8 detik antar request dalam batch (agar tidak terlalu cepat)
            if taps_done_in_batch < batch_size:
                time.sleep(random.uniform(0.3, 0.8))

        # Selesai batch, update status
        self.log(f"✅ Batch {batch_size} taps selesai", "SUCCESS")

    def auto_tap_unlimited(self):
        tap_limit = self.tap_limit
        if tap_limit > 0:
            self.log(f"👆 AUTO TAP BATCH MODE START (limit: {tap_limit} taps, batch: {self.batch_size})", "SUCCESS")
        else:
            self.log(f"👆 AUTO TAP BATCH MODE START (unlimited, batch: {self.batch_size})", "SUCCESS")
        self.log("⏹️  Tekan Ctrl+C untuk berhenti", "WARNING")

        if not self.init():
            self.log("❌ Init failed", "ERROR")
            return

        total_taps_done = 0
        try:
            while True:
                # Cek limit
                if tap_limit > 0 and total_taps_done >= tap_limit:
                    self.log(f"✅ Tap limit ({tap_limit}) tercapai! Selesai.", "SUCCESS")
                    break

                # Cek energy
                if self.energy <= 0:
                    self.log(f"⏳ Energy habis ({self.energy}), tunggu 60 detik...", "WARNING")
                    time.sleep(60)
                    self.init()
                    continue

                # Jalankan batch
                self.tap_batch()
                total_taps_done += self.batch_size

                # Cek limit setelah batch
                if tap_limit > 0 and total_taps_done >= tap_limit:
                    self.log(f"✅ Tap limit ({tap_limit}) tercapai! Selesai.", "SUCCESS")
                    break

                # Jeda antar batch
                delay = random.uniform(self.batch_delay_min, self.batch_delay_max)
                self.log(f"⏳ Jeda batch {delay:.1f} detik... ({total_taps_done}/{tap_limit if tap_limit > 0 else '∞'})", "DIM")
                time.sleep(delay)

        except KeyboardInterrupt:
            self.log("🛑 Auto Tap dihentikan", "WARNING")
        finally:
            self.show_status()

    def auto_claim(self):
        self.log("🎯 AUTO CLAIM START", "SUCCESS")

        if not self.init():
            self.log("❌ Init failed", "ERROR")
            return

        self.claim_streak()
        time.sleep(random_delay(1, 3))

        self.spin()
        time.sleep(random_delay(1, 3))

        self.claim_tasks()
        time.sleep(random_delay(1, 3))

        self.show_status()
        self.log("✅ AUTO CLAIM DONE", "SUCCESS")

    def auto_all(self):
        self.log("🚀 ALL MODE START", "SUCCESS")
        self.log("⏹️  Tekan Ctrl+C untuk berhenti", "WARNING")

        if not self.init():
            self.log("❌ Init failed", "ERROR")
            return

        try:
            cycle = 0
            while True:
                cycle += 1
                self.log(f"🔄 CYCLE #{cycle}", "INFO")

                # Claim dulu
                self.claim_streak()
                time.sleep(random_delay(1, 3))

                self.spin()
                time.sleep(random_delay(1, 3))

                self.claim_tasks()
                time.sleep(random_delay(1, 3))

                # Tap pakai batch
                max_taps = self.tap_limit if self.tap_limit > 0 else 50
                self.log(f"👆 Tap {max_taps}x (batch mode)...", "INFO")
                total_done = 0
                while total_done < max_taps:
                    if self.energy <= 0:
                        self.log(f"⏳ Energy habis ({self.energy}), tunggu 60 detik...", "WARNING")
                        time.sleep(60)
                        self.init()
                        continue

                    # Berapa batch size yang bisa dipakai
                    batch_now = min(self.batch_size, max_taps - total_done)
                    # Set batch size sementara
                    original_batch = self.batch_size
                    self.batch_size = batch_now
                    self.tap_batch()
                    self.batch_size = original_batch
                    total_done += batch_now
                    if total_done < max_taps:
                        time.sleep(random.uniform(0.5, 2))

                self.show_status()

                wait = random.randint(5, 10)
                self.log(f"⏳ Tunggu {wait} menit...", "INFO")
                time.sleep(wait * 60)

        except KeyboardInterrupt:
            self.log("🛑 ALL MODE dihentikan", "WARNING")
            self.show_status()

# ==================== MENU ====================
def menu():
    config = Config()
    config.load()

    while True:
        print(BANNER)
        print(f"""
{CYAN}╔════════════════════════════════════════════════════════════╗
║                      MAIN MENU                               ║
╠════════════════════════════════════════════════════════════╣
║  {GREEN}[1]{RESET} 👆 Auto Tap (Batch Mode)                     ║
║  {YELLOW}[2]{RESET} 🎯 Auto Claim (Streak + Spin + Tasks)       ║
║  {PURPLE}[3]{RESET} 🚀 ALL (Tap Batch + Claim)                   ║
║  {CYAN}[4]{RESET} 📝 Set InitData                               ║
║  {BLUE}[5]{RESET} 📊 Check Balance                              ║
║  {LIME}[6]{RESET} 📊 Set Tap Limit                              ║
║  {GOLD}[7]{RESET} 💸 Withdraw (Set Address + Nominal)           ║
║  {PINK}[8]{RESET} ⚙️ Set Tap Batch (Size + Jeda)                ║
║  {RED}[0]{RESET} ❌ Exit                                        ║
╚════════════════════════════════════════════════════════════╝{RESET}
""")

        if config.init_data:
            print(f"{GREEN}✅ InitData tersimpan (panjang: {len(config.init_data)}){RESET}")
        else:
            print(f"{RED}❌ InitData belum diset!{RESET}")

        if config.tap_limit > 0:
            print(f"{LIME}📊 Tap Limit: {config.tap_limit}{RESET}")
        else:
            print(f"{DIM}📊 Tap Limit: Unlimited{RESET}")

        if config.withdraw_address:
            print(f"{GOLD}💳 Address: {config.withdraw_address[:12]}...{RESET}")
        else:
            print(f"{RED}💳 Address: Not set{RESET}")

        print(f"{PINK}⚙️ Batch: {config.tap_batch_size} taps, Jeda {config.tap_batch_delay_min}-{config.tap_batch_delay_max}s{RESET}")

        choice = input(f"\n{PINK}❯ Pilih: {RESET}").strip()

        if choice == '0':
            print(f"{YELLOW}👋 Bye!{RESET}")
            sys.exit(0)

        elif choice == '1':
            if not config.init_data:
                print(f"{RED}❌ InitData belum diset. Set dulu (menu 4).{RESET}")
                input("Tekan Enter untuk kembali...")
                continue
            bot = BabyDogeBot(config.init_data, config.tap_limit, config.withdraw_address,
                             config.tap_batch_size, config.tap_batch_delay_min, config.tap_batch_delay_max)
            bot.auto_tap_unlimited()
            input("Tekan Enter untuk kembali ke menu...")

        elif choice == '2':
            if not config.init_data:
                print(f"{RED}❌ InitData belum diset. Set dulu (menu 4).{RESET}")
                input("Tekan Enter untuk kembali...")
                continue
            bot = BabyDogeBot(config.init_data, config.tap_limit, config.withdraw_address,
                             config.tap_batch_size, config.tap_batch_delay_min, config.tap_batch_delay_max)
            bot.auto_claim()
            input("Tekan Enter untuk kembali ke menu...")

        elif choice == '3':
            if not config.init_data:
                print(f"{RED}❌ InitData belum diset. Set dulu (menu 4).{RESET}")
                input("Tekan Enter untuk kembali...")
                continue
            bot = BabyDogeBot(config.init_data, config.tap_limit, config.withdraw_address,
                             config.tap_batch_size, config.tap_batch_delay_min, config.tap_batch_delay_max)
            bot.auto_all()
            input("Tekan Enter untuk kembali ke menu...")

        elif choice == '4':
            print(f"{YELLOW}📝 Masukkan InitData dari Reqable:{RESET}")
            print(f"{DIM}Copy dari body request POST /v1/game/init{RESET}")
            qid = input("InitData: ").strip()
            if qid:
                config.init_data = qid
                config.save()
                print(f"{GREEN}✅ InitData disimpan!{RESET}")
            else:
                print(f"{RED}❌ InitData tidak boleh kosong!{RESET}")
            input("Tekan Enter untuk kembali...")

        elif choice == '5':
            if not config.init_data:
                print(f"{RED}❌ InitData belum diset.{RESET}")
            else:
                bot = BabyDogeBot(config.init_data, config.tap_limit, config.withdraw_address,
                                 config.tap_batch_size, config.tap_batch_delay_min, config.tap_batch_delay_max)
                bot.check_balance()
            input("Tekan Enter untuk kembali...")

        elif choice == '6':
            print(f"{LIME}📊 Set Tap Limit:{RESET}")
            print(f"{DIM}0 = Unlimited, 50 = 50 taps per sesi, dst{RESET}")
            limit = input(f"Masukkan limit: ").strip()
            if limit.isdigit():
                config.tap_limit = int(limit)
                config.save()
                print(f"{GREEN}✅ Tap Limit set ke: {config.tap_limit}{RESET}")
            else:
                print(f"{RED}❌ Masukkan angka!{RESET}")
            input("Tekan Enter untuk kembali...")

        elif choice == '7':
            if not config.init_data:
                print(f"{RED}❌ InitData belum diset.{RESET}")
            else:
                bot = BabyDogeBot(config.init_data, config.tap_limit, config.withdraw_address,
                                 config.tap_batch_size, config.tap_batch_delay_min, config.tap_batch_delay_max)
                bot.withdraw_menu()
            input("Tekan Enter untuk kembali...")

        elif choice == '8':
            print(f"{PINK}⚙️ Set Tap Batch:{RESET}")
            print(f"{DIM}Contoh: batch 50, jeda 3-7 detik{RESET}")

            batch = input(f"Jumlah tap per batch (default 50): ").strip()
            if batch.isdigit():
                config.tap_batch_size = int(batch)

            delay_min = input(f"Jeda minimal antar batch (detik, default 3): ").strip()
            if delay_min.replace('.', '').isdigit():
                config.tap_batch_delay_min = float(delay_min)

            delay_max = input(f"Jeda maksimal antar batch (detik, default 7): ").strip()
            if delay_max.replace('.', '').isdigit():
                config.tap_batch_delay_max = float(delay_max)

            if config.tap_batch_delay_min > config.tap_batch_delay_max:
                config.tap_batch_delay_min, config.tap_batch_delay_max = config.tap_batch_delay_max, config.tap_batch_delay_min

            config.save()
            print(f"{GREEN}✅ Batch set: {config.tap_batch_size} taps, Jeda {config.tap_batch_delay_min}-{config.tap_batch_delay_max}s{RESET}")
            input("Tekan Enter untuk kembali...")

        else:
            print(f"{RED}❌ Pilihan salah!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}👋 Bye!{RESET}")
        sys.exit(0)
