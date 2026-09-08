#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import urllib.parse
import requests
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# ===== COLOR =====
class Colors:
    HEADER = '\033[95m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PINK = '\033[38;5;206m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

BANNER = f"""
{Colors.CYAN}================================================{Colors.END}
{Colors.PINK}             █████╗ ████████╗███████╗{Colors.END}
{Colors.PINK}            ██╔══██╗╚══██╔══╝██╔════╝{Colors.END}
{Colors.PINK}            ███████║   ██║   █████╗{Colors.END}
{Colors.PINK}            ██╔══██║   ██║   ██╔══╝{Colors.END}
{Colors.PINK}            ██║  ██║   ██║   ███████╗{Colors.END}
{Colors.PINK}            ╚═╝  ╚═╝   ╚═╝   ╚══════╝{Colors.END}
{Colors.CYAN}================================================{Colors.END}
{Colors.BOLD}{Colors.WHITE}              ⚡ ATF MINER ⚡{Colors.END}
{Colors.BOLD}{Colors.WHITE}              AUTO FARM BOT{Colors.END}
{Colors.CYAN}================================================{Colors.END}
{Colors.GREEN}        ScriptMaker : MoneyMaker_w{Colors.END}
{Colors.CYAN}================================================{Colors.END}
{Colors.GREEN}   [✓] MINING     [✓] CLAIM{Colors.END}
{Colors.GREEN}   [✓] REWARD     [✓] AUTO RUN{Colors.END}
{Colors.CYAN}================================================{Colors.END}
"""

ACCOUNTS_FILE = "accounts.txt"
LOCK = threading.Lock()

def print_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)

# ============================================================
# SINGLE ACCOUNT ENGINE (dengan debug & validasi)
# ============================================================

class ATFMinerBot:
    def __init__(self, init_data, account_id=0):
        self.init_data = init_data.strip()
        self.account_id = account_id
        self.device_id = f"dev-{uuid.uuid4()}"
        self.base_url = "https://atfminers.asloni.online"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.1",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": self.base_url,
            "Referer": f"{self.base_url}/miner/index.html"
        })
        self.session_token = None
        self.is_logged_in = False
        self.balance = 0.0
        self.total_boost = 0
        self.mining_freeze_at = 0
        self.username = "Unknown"
        self._parse_user()
        # Coba login, jika gagal minta input ulang
        if not self.login():
            self._log("❌ Login gagal, coba masukkan initData baru", Colors.RED)
            new_data = input(f"[Acc{self.account_id}] Masukkan initData ulang: ").strip()
            if new_data:
                self.init_data = new_data
                self._parse_user()
                self.login()

    def _parse_user(self):
        try:
            parsed = urllib.parse.parse_qs(self.init_data)
            if 'user' in parsed:
                user = json.loads(parsed['user'][0])
                self.username = user.get('username') or user.get('first_name', 'Unknown')
            else:
                self._log("⚠️ InitData tidak mengandung 'user'", Colors.YELLOW)
        except Exception as e:
            self._log(f"⚠️ Parse user error: {e}", Colors.YELLOW)

    def _log(self, msg, color=Colors.WHITE):
        prefix = f"[Acc{self.account_id}]" if self.account_id > 0 else ""
        with LOCK:
            print(f"{color}{prefix} {msg}{Colors.END}")

    def _call_api(self, action, extra=None):
        url = f"{self.base_url}/miner/index.php"
        params = {"action": action, "t": str(int(time.time()*1000))}
        payload = {
            "initData": self.init_data,
            "request_id": str(uuid.uuid4()),
            "device_id": self.device_id
        }
        if extra:
            payload.update(extra)
        headers = self.session.headers.copy()
        if self.session_token:
            headers["X-ATF-TMA-Session"] = self.session_token
            headers["Cookie"] = f"atf_tma_session={self.session_token}"
        try:
            resp = self.session.post(url, params=params, json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            else:
                self._log(f"HTTP {resp.status_code} - {resp.text[:200]}", Colors.RED)
        except Exception as e:
            self._log(f"Request exception: {e}", Colors.RED)
        return None

    def login(self):
        if not self.init_data:
            self._log("InitData kosong", Colors.RED)
            return False
        
        self._log("🔄 Login...", Colors.CYAN)
        result = self._call_api("login")
        if result:
            self._log(f"Response login: {json.dumps(result, indent=2)[:300]}", Colors.GRAY)
        
        if result and result.get('status') == 'success':
            user = result.get('user', {})
            self.session_token = result.get('tma_session_token')
            self.is_logged_in = True
            self.balance = float(user.get('mined_balance', 0))
            self.total_boost = int(user.get('total_boost_count', 0))
            self.mining_freeze_at = int(user.get('mining_freezes_at', 0))
            self._log(f"✅ Login OK | {self.username} | Balance: {self.balance:.4f} ATF", Colors.GREEN)
            return True
        else:
            self._log(f"❌ Login GAGAL - status: {result.get('status') if result else 'No response'}", Colors.RED)
            if result and result.get('message'):
                self._log(f"   Pesan: {result.get('message')}", Colors.RED)
            return False

    def countdown(self, sec, msg="⏳ Menunggu"):
        for i in range(sec, 0, -1):
            with LOCK:
                print(f"\r{Colors.YELLOW}[Acc{self.account_id}] {msg} {i} detik...{Colors.END}", end="")
            time.sleep(1)
        with LOCK:
            print(f"\r{Colors.GREEN}[Acc{self.account_id}] {msg} selesai!{Colors.END}          ")

    def claim(self):
        self._log("🔄 Claiming...", Colors.CYAN)
        result = self._call_api("claim")
        if not result:
            self._log("❌ Claim gagal (no response)", Colors.RED)
            return False
        status = result.get('status')
        if status == 'success':
            self.balance = float(result.get('user', {}).get('mined_balance', self.balance))
            self.mining_freeze_at = int(result.get('user', {}).get('mining_freezes_at', 0))
            self._log(f"✅ Claim success! Balance: {self.balance:.4f} ATF", Colors.GREEN)
            return True
        elif status in ('busy', 'cooldown'):
            wait = result.get('mining_freezes_at', 0) - int(time.time())
            if wait > 0:
                self._log(f"⏳ Claim cooldown {wait}s", Colors.YELLOW)
                self.countdown(wait, "Claim cooldown")
                return self.claim()
        else:
            self._log(f"❌ Claim status: {status}", Colors.RED)
        return False

    def do_boost(self):
        if self.mining_freeze_at > 0 and int(time.time()) >= self.mining_freeze_at:
            self._log("⛔ Mining frozen! Claim dulu...", Colors.YELLOW)
            if not self.claim():
                self._log("❌ Claim gagal, skip boost", Colors.RED)
                return False

        result = self._call_api("activate_boost", {"display_preview": round(0.15 + 0.1 * (time.time() % 1), 4)})
        if not result:
            self._log("❌ Boost no response", Colors.RED)
            return False

        status = result.get('status')
        if status == 'success':
            reward = result.get('pending_reward', 0)
            self.balance = float(result.get('user', {}).get('mined_balance', self.balance))
            self.total_boost = int(result.get('user', {}).get('total_boost_count', self.total_boost))
            self.mining_freeze_at = int(result.get('user', {}).get('mining_freezes_at', 0))
            self._log(f"✅ BOOST #{self.total_boost} | +{reward:.4f} ATF | Balance: {self.balance:.4f}", Colors.GREEN)
            return True

        elif status == 'frozen':
            self._log("⛔ Frozen response, claim...", Colors.YELLOW)
            if self.claim():
                return self.do_boost()
            return False

        elif status in ('busy', 'cooldown'):
            wait = result.get('boost_ready_at', 0) - int(time.time())
            if wait > 0:
                self._log(f"⏳ Cooldown {wait}s", Colors.YELLOW)
                self.countdown(wait, "Cooldown")
                return self.do_boost()
            time.sleep(1)
            return self.do_boost()

        elif status == 'rate_limited':
            wait = min(30, 5 * max(1, self.account_id))
            self._log(f"⚠️ Rate limited, tunggu {wait}s", Colors.YELLOW)
            self.countdown(wait, "Rate limit")
            return self.do_boost()

        else:
            self._log(f"⚠️ Status tidak dikenal: {status}", Colors.RED)
            return False

    def run_loop(self, max_boost=0):
        if not self.is_logged_in:
            self._log("Tidak login, skip", Colors.RED)
            return
        self._log("🚀 Memulai auto‑boost loop", Colors.CYAN)
        count = 0
        while max_boost == 0 or count < max_boost:
            try:
                if self.do_boost():
                    count += 1
                else:
                    time.sleep(5)
                self.countdown(15, "Cooling down")
            except KeyboardInterrupt:
                break
        self._log(f"⏹️ Loop berhenti, total boost: {count}", Colors.YELLOW)

# ============================================================
# MULTI‑ACCOUNT MANAGER
# ============================================================

def load_accounts():
    if not os.path.exists(ACCOUNTS_FILE):
        return []
    with open(ACCOUNTS_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def run_single(init_data, idx):
    bot = ATFMinerBot(init_data, idx)
    bot.run_loop()

def main():
    print_banner()
    accounts = load_accounts()
    if not accounts:
        print(f"{Colors.YELLOW}⚠️ Tidak ada accounts.txt, masukkan initData manual:{Colors.END}")
        manual = input("➜ ").strip()
        if manual:
            bot = ATFMinerBot(manual, 0)
            bot.run_loop()
        else:
            print(f"{Colors.RED}❌ Tidak ada data, keluar.{Colors.END}")
        return

    print(f"{Colors.GREEN}✅ Memuat {len(accounts)} akun.{Colors.END}")
    max_workers = min(len(accounts), 5)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_single, acc, i+1) for i, acc in enumerate(accounts)]
        for f in as_completed(futures):
            try:
                f.result()
            except Exception as e:
                print(f"{Colors.RED}❌ Error akun: {e}{Colors.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}🛑 Dihentikan user.{Colors.END}")
        sys.exit(0)
