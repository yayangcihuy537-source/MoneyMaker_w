#!/usr/bin/env python3
"""
CoinFree Auto Bot - All Modes + Auto Watch + Auto Claim + Captcha Solver
By: Kyriel (for Bos)
Dengan Auto-Recovery (tanpa Telethon)
"""

import os
import sys
import json
import time
import uuid
import requests
import threading
from typing import Dict, Optional
from datetime import datetime
from collections import deque

# ==================== COLOR ====================
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
RED = "\033[1;31m"
CYAN = "\033[1;36m"
BLUE = "\033[1;34m"
PURPLE = "\033[38;5;141m"
PINK = "\033[38;5;206m"
LIME = "\033[38;5;154m"
GOLD = "\033[38;5;220m"
DIM = "\033[2;37m"
WHITE = "\033[1;37m"
RESET = "\033[0m"
BOLD = "\033[1m"

# ==================== CONFIG ====================
BASE_URL = "https://coinfree.app/api.php"
CONFIG_FILE = "coinfree_config.json"
USER_AGENT = "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.6.4 (Samsung SM-A556E; Android 16; SDK 36; HIGH)"
COOKIE_FILE = "coinfree_cookies.json"

CAPTCHA_SITEKEY = "0x4AAAAAAB6mAUIH75NUE5fq"
CAPTCHA_PAGEURL = "https://coinfree.app"

# ==================== LOG QUEUE ====================
log_queue = deque(maxlen=3)
log_lock = threading.Lock()

def push_log(msg, color=WHITE):
    with log_lock:
        timestamp_str = datetime.now().strftime("%H:%M:%S")
        clean_msg = msg.replace(GREEN, '').replace(YELLOW, '').replace(RED, '').replace(CYAN, '').replace(BLUE, '').replace(PURPLE, '').replace(PINK, '').replace(LIME, '').replace(GOLD, '').replace(DIM, '').replace(WHITE, '').replace(RESET, '').replace(BOLD, '')
        log_queue.append(f"[{timestamp_str}] {clean_msg}")

def get_logs():
    with log_lock:
        return list(log_queue)

# ==================== HELPER ====================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log(msg, color=WHITE):
    push_log(msg, color)
    print(f"{DIM}[{timestamp()}]{RESET} {color}{msg}{RESET}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_cookies():
    if os.path.exists(COOKIE_FILE):
        with open(COOKIE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cookies(cookies):
    with open(COOKIE_FILE, 'w') as f:
        json.dump(cookies, f, indent=2)

def is_auth_error(response: Dict) -> bool:
    """Cek apakah error disebabkan oleh initData kadaluarsa atau tidak valid"""
    if not isinstance(response, dict):
        return False
    msg = str(response.get('message', '')).lower()
    return any(key in msg for key in ['initdata', 'invalid', 'expired', 'auth', 'unauthorized'])

# ==================== CAPTCHA SOLVER ====================
class CaptchaSolver:
    def __init__(self, service: str, api_key: str):
        self.service = service
        self.api_key = api_key
        if service == 'waryono':
            self.base = "https://api.waryono.my.id"
        else:
            self.base = "https://bypassallshortlinks.space"

    def solve_turnstile(self, sitekey: str, pageurl: str, timeout: int = 90) -> Optional[str]:
        if self.service == 'waryono':
            return self._solve_waryono(sitekey, pageurl, timeout)
        else:
            return self._solve_bypassall(sitekey, pageurl, timeout)

    def _solve_waryono(self, sitekey: str, pageurl: str, timeout: int) -> Optional[str]:
        payload = {
            "apikey": self.api_key,
            "methods": "turnstile",
            "domain": pageurl,
            "sitekey": sitekey,
            "action": "login",
            "cdata": f"session_{uuid.uuid4().hex[:8]}"
        }
        try:
            r = requests.post(f"{self.base}/in.php", json=payload, timeout=30)
            if r.status_code != 200:
                log(f"❌ Waryono submit failed: HTTP {r.status_code}", RED)
                return None
            data = r.json()
            if data.get("status") != 1:
                log(f"❌ Waryono error: {data.get('request', 'Unknown')}", RED)
                return None
            task_id = data.get("request")
            if not task_id or task_id.startswith("ERROR"):
                log(f"❌ Waryono task ID error: {task_id}", RED)
                return None
            log(f"📝 Waryono task created: {task_id}", DIM)
        except Exception as e:
            log(f"❌ Waryono submit exception: {e}", RED)
            return None

        start = time.time()
        while time.time() - start < timeout:
            time.sleep(3)
            try:
                params = {"apikey": self.api_key, "id": task_id, "action": "get", "json": 1}
                r = requests.get(f"{self.base}/res.php", params=params, timeout=10)
                if r.status_code != 200:
                    continue
                data = r.json()
                if data.get("status") == 1:
                    token = data.get("request")
                    if token and not token.startswith("ERROR"):
                        log(f"✅ Waryono solved: {token[:20]}...", GREEN)
                        return token
                    else:
                        log(f"❌ Waryono response invalid: {token}", RED)
                        return None
                elif data.get("request") == "CAPCHA_NOT_READY":
                    continue
                else:
                    log(f"❌ Waryono error: {data.get('request', 'Unknown')}", RED)
                    return None
            except Exception as e:
                log(f"⚠️ Waryono poll error: {e}", YELLOW)
                continue
        log("⏰ Waryono timeout", YELLOW)
        return None

    def _solve_bypassall(self, sitekey: str, pageurl: str, timeout: int) -> Optional[str]:
        params = {"key": self.api_key, "method": "turnstile", "sitekey": sitekey, "pageurl": pageurl}
        try:
            r = requests.get(f"{self.base}/in.php", params=params, timeout=30)
            if r.status_code != 200:
                log(f"❌ BypassAll submit failed: HTTP {r.status_code}", RED)
                return None
            resp = r.text.strip()
            if not resp.startswith("OK|"):
                log(f"❌ BypassAll submit error: {resp}", RED)
                return None
            task_id = resp.split("|")[-1]
            log(f"📝 BypassAll task created: {task_id}", DIM)
        except Exception as e:
            log(f"❌ BypassAll submit exception: {e}", RED)
            return None

        start = time.time()
        while time.time() - start < timeout:
            time.sleep(3)
            try:
                params = {"id": task_id, "key": self.api_key}
                r = requests.get(f"{self.base}/res.php", params=params, timeout=10)
                if r.status_code != 200:
                    continue
                resp = r.text.strip()
                if resp.startswith("OK|"):
                    token = resp.split("|")[-1]
                    log(f"✅ BypassAll solved: {token[:20]}...", GREEN)
                    return token
                elif "ERROR" in resp:
                    log(f"❌ BypassAll error: {resp}", RED)
                    return None
            except Exception as e:
                log(f"⚠️ BypassAll poll error: {e}", YELLOW)
                continue
        log("⏰ BypassAll timeout", YELLOW)
        return None

# ==================== DASHBOARD ====================
class Dashboard:
    def __init__(self, bot):
        self.bot = bot
        self.lock = threading.Lock()
        self.mode_status = {}
        for mode in bot.modes:
            self.mode_status[mode] = {
                "status": "⏳",
                "reward": "-",
                "cooldown": "-",
                "double": "Done",
                "play": "0/25",
                "play_count": 0
            }
        self.account_info = {
            "balance": "0.00000000",
            "coin": "PEPE",
            "run_loop": 0,
            "username": "User",
            "total_claim": 0,
            "status": "ONLINE"
        }
        self.stop_render = False

    def update_mode_status(self, mode, status=None, reward=None, cooldown=None, double=None, play_inc=None):
        with self.lock:
            if status is not None:
                self.mode_status[mode]["status"] = status
            if reward is not None:
                self.mode_status[mode]["reward"] = reward
            if cooldown is not None:
                self.mode_status[mode]["cooldown"] = cooldown
            if double is not None:
                self.mode_status[mode]["double"] = double
            if play_inc is not None:
                self.mode_status[mode]["play_count"] += play_inc
                current = self.mode_status[mode]["play_count"]
                self.mode_status[mode]["play"] = f"{current}/25"

    def update_account_info(self, balance, username, run_loop=0, total_claim=None, coin="PEPE", status="ONLINE"):
        with self.lock:
            self.account_info["balance"] = f"{balance:.8f}"
            self.account_info["coin"] = coin
            self.account_info["run_loop"] = run_loop
            self.account_info["username"] = username
            if total_claim is not None:
                self.account_info["total_claim"] = total_claim
            self.account_info["status"] = status

    def refresh_all_cooldowns(self):
        now = time.time()
        for mode in self.bot.modes:
            cooldown_end = self.bot.cooldowns.get(mode, 0)
            status = self.mode_status[mode]["status"]
            if cooldown_end > now:
                remaining = int(cooldown_end - now)
                with self.lock:
                    if status not in ["✅", "Finished"]:
                        self.mode_status[mode]["status"] = f"⏳{remaining}s"
                        self.mode_status[mode]["cooldown"] = remaining
            else:
                with self.lock:
                    if status in ["⏳", "⏳0s", "❌"] and self.mode_status[mode]["reward"] == "-":
                        self.mode_status[mode]["status"] = "Ready"
                        self.mode_status[mode]["cooldown"] = "-"

    def render(self):
        with self.lock:
            clear()
            # ====== CUSTOM HEADER ======
            print(f"""
{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {GOLD}⚡ SCRIPTYXSOUU{RESET}
  {CYAN}TG  : t.me/ScriptyXSouu{RESET}
  {PINK}DEV : ScriptyXSou{RESET}
{WHITE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}
""")
            # Account Info Box
            balance = self.account_info["balance"]
            coin = self.account_info["coin"]
            username = self.account_info["username"][:15]
            run_loop = self.account_info["run_loop"]
            total_claim = self.account_info["total_claim"]
            status = self.account_info["status"]
            status_icon = "🟢" if status == "ONLINE" else "🔴"

            print(f"""
{CYAN}╭──────────────────── ACCOUNT INFO ────────────────────╮
│ {WHITE}Run / Loop   : {BOLD}{run_loop}{RESET}                                   │
│ {WHITE}Username     : {GREEN}{username}{RESET}                                 │
│ {WHITE}Balance      : {GOLD}{balance} {coin}{RESET}                  │
│ {WHITE}Total Claim  : {LIME}{total_claim}{RESET}                                  │
│ {WHITE}Status       : {status_icon} {status}{RESET}                            │
{CYAN}╰─────────────────────────────────────────────────────╯{RESET}
""")

            # Table
            print(f"{CYAN}┌────────┬──────────────┬──────┬───────┬──────────────┐")
            print(f"│ {WHITE}MODE   │ STATUS       │ 2X   │ PLAY  │ REWARD       │{RESET}")
            print(f"{CYAN}├────────┼──────────────┼──────┼───────┼──────────────┤")

            for mode in self.bot.modes:
                status = self.mode_status[mode]
                status_text = status["status"]
                if len(status_text) > 12:
                    status_text = status_text[:12]
                double_text = status["double"][:6]
                play_text = status["play"][:7]
                reward_text = status["reward"]
                if len(reward_text) > 12:
                    reward_text = reward_text[:12]
                if "✅" in status_text or "Finished" in status_text:
                    status_color = GREEN
                elif "Ready" in status_text:
                    status_color = LIME
                elif "⏳" in status_text:
                    status_color = YELLOW
                elif "❌" in status_text or "Error" in status_text:
                    status_color = RED
                else:
                    status_color = WHITE
                print(f"│ {mode:6} │ {status_color}{status_text:12}{RESET} │ {double_text:4} │ {play_text:5} │ {reward_text:12} │")
            print(f"{CYAN}└────────┴──────────────┴──────┴───────┴──────────────┘{RESET}")

            # Live Logs
            print(f"\n{CYAN}┌──────────────────── LIVE LOGS ─────────────────────┐{RESET}")
            logs = get_logs()
            if logs:
                for log_line in logs[-3:]:
                    clean = log_line.replace(GREEN, '').replace(YELLOW, '').replace(RED, '').replace(CYAN, '').replace(BLUE, '').replace(PURPLE, '').replace(PINK, '').replace(LIME, '').replace(GOLD, '').replace(DIM, '').replace(WHITE, '').replace(RESET, '').replace(BOLD, '')
                    if len(clean) > 46:
                        clean = clean[:43] + "..."
                    print(f"│ {clean:<46} │")
            else:
                print(f"│ {DIM}Menunggu aktivitas...{' ' * 27}{RESET} │")
            print(f"{CYAN}└──────────────────────────────────────────────────────┘{RESET}")

            print(f"\n{DIM}⏳ Auto-run aktif. Tekan Ctrl+C untuk berhenti.{RESET}")

    def render_loop(self, interval=2):
        while not self.stop_render and self.bot.running:
            self.refresh_all_cooldowns()
            self.render()
            time.sleep(interval)

    def stop(self):
        self.stop_render = True

# ==================== COINFREE BOT ====================
class CoinFreeBot:
    def __init__(self, init_data: str, device_id: str, captcha_solver: CaptchaSolver):
        self.init_data = init_data
        self.device_id = device_id
        self.captcha_solver = captcha_solver
        self.session = requests.Session()
        self.session.headers.update({
            'Host': 'coinfree.app',
            'sec-ch-ua-platform': '"Android"',
            'User-Agent': USER_AGENT,
            'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
            'content-type': 'application/json',
            'sec-ch-ua-mobile': '?1',
            'accept': '*/*',
            'origin': 'https://coinfree.app',
            'x-requested-with': 'org.telegram.messenger.web',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://coinfree.app/',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i'
        })
        self.cookies = load_cookies()
        self.session.cookies.update(self.cookies)
        self.user_data = {}
        self.double_reward_multiplier = 4
        self.modes = ['plinko', 'target', 'box', 'card', 'wheel', 'roll']
        self.cooldowns = {}
        self.global_cooldown = 0
        self.running = True
        self.run_loop_count = 0
        self.total_claim_count = 0
        self.username = "User"
        self.dashboard = Dashboard(self)
        self.dashboard_thread = None
        self.needs_new_init_data = False

    def _request(self, payload: Dict) -> Dict:
        try:
            resp = self.session.post(BASE_URL, json=payload)
            if resp.cookies:
                self.session.cookies.update(resp.cookies)
                save_cookies(dict(resp.cookies))
            return resp.json()
        except Exception as e:
            log(f"Request error: {e}", RED)
            return {"status": "error", "message": str(e)}

    def get_user_data(self) -> Dict:
        payload = {
            "action": "get_user_data",
            "initData": self.init_data,
            "deviceId": self.device_id
        }
        result = self._request(payload)
        if result.get("status") == "success":
            self.user_data = result.get("data", {})
            self.double_reward_multiplier = self.user_data.get("double_reward_multiplier", 4)
            for mode in self.modes:
                key = f"faucet_cooldown_remaining_{mode}"
                if key in self.user_data:
                    rem = self.user_data.get(key, 0)
                    self.cooldowns[mode] = time.time() + rem if rem > 0 else 0
            if self.user_data.get("faucet_global_cooldown_remaining", 0) > 0:
                self.global_cooldown = time.time() + self.user_data["faucet_global_cooldown_remaining"]
            else:
                self.global_cooldown = 0
            balance = float(self.user_data.get("balance", 0))
            coin = self.user_data.get("preferred_coin", "PEPE")
            self.username = self.user_data.get("first_name", "User")
            self.dashboard.update_account_info(
                balance=balance,
                username=self.username,
                run_loop=self.run_loop_count,
                total_claim=self.total_claim_count,
                coin=coin
            )
        else:
            # Cek apakah error karena auth
            if is_auth_error(result):
                log("⚠️ InitData expired or invalid!", RED)
                self.needs_new_init_data = True
        return result

    def get_faucet_spin_reward(self, mode: str) -> Dict:
        payload = {
            "action": "get_faucet_spin_reward",
            "initData": self.init_data,
            "deviceId": self.device_id,
            "mode": mode
        }
        return self._request(payload)

    def complete_double_reward_ad(self, mode: str) -> Dict:
        payload = {
            "action": "complete_double_reward_ad",
            "initData": self.init_data,
            "deviceId": self.device_id,
            "mode": mode
        }
        return self._request(payload)

    def claim_faucet(self, mode: str, captcha_token: str) -> Dict:
        payload = {
            "action": "claim_faucet",
            "initData": self.init_data,
            "deviceId": self.device_id,
            "captchaToken": captcha_token,
            "mode": mode
        }
        return self._request(payload)

    def is_cooldown_ready(self, mode: str) -> bool:
        now = time.time()
        if self.global_cooldown > now:
            return False
        if self.cooldowns.get(mode, 0) > now:
            return False
        return True

    def wait_for_cooldown(self, mode: str):
        now = time.time()
        wait_time = 0
        if self.global_cooldown > now:
            wait_time = max(wait_time, self.global_cooldown - now)
        if self.cooldowns.get(mode, 0) > now:
            wait_time = max(wait_time, self.cooldowns[mode] - now)
        if wait_time > 0:
            self.dashboard.update_mode_status(mode, status=f"⏳{int(wait_time)}s", cooldown=wait_time)
            log(f"⏳ Cooldown {wait_time:.0f}s for mode {mode}", YELLOW)
            while wait_time > 0 and self.running:
                time.sleep(min(1, wait_time))
                wait_time -= 1
                if wait_time % 5 == 0 or wait_time < 5:
                    self.dashboard.update_mode_status(mode, status=f"⏳{int(wait_time)}s", cooldown=wait_time)
                    self.dashboard.refresh_all_cooldowns()

    def solve_captcha(self, mode: str) -> Optional[str]:
        if not self.captcha_solver:
            log("❌ No captcha solver configured", RED)
            return None
        self.dashboard.update_mode_status(mode, status="Solving")
        log("🔐 Solving Turnstile captcha...", CYAN)
        token = self.captcha_solver.solve_turnstile(CAPTCHA_SITEKEY, CAPTCHA_PAGEURL)
        if token:
            self.dashboard.update_mode_status(mode, status="Ready")
        return token

    def play_mode(self, mode: str) -> bool:
        self.dashboard.update_mode_status(mode, status="Running", reward="...", double="Done")
        log(f"🎮 Playing mode: {mode}", CYAN)

        if not self.is_cooldown_ready(mode):
            self.wait_for_cooldown(mode)
            if not self.is_cooldown_ready(mode):
                log(f"⏳ Still cooldown for {mode}, skipping", YELLOW)
                self.dashboard.update_mode_status(mode, status="Waiting", cooldown="-")
                return False

        # 1. Get spin reward
        log(f"📡 Getting spin reward for {mode}...", DIM)
        self.dashboard.update_mode_status(mode, status="Getting reward")
        spin_result = self.get_faucet_spin_reward(mode)
        if spin_result.get("status") != "success":
            # Cek auth error
            if is_auth_error(spin_result):
                log("⚠️ Auth error detected, need new initData", RED)
                self.needs_new_init_data = True
                return False
            log(f"❌ Failed to get spin reward: {spin_result.get('message')}", RED)
            self.dashboard.update_mode_status(mode, status="Error", reward="err")
            return False

        base_amount = spin_result.get("baseRewardAmount", 0)
        final_amount = spin_result.get("finalRewardAmount", base_amount)
        reward_index = spin_result.get("rewardIndex", 0)
        log(f"🎯 Base: {base_amount:.2f} | Final: {final_amount:.2f} | Index: {reward_index}", GOLD)

        # 2. Watch ad for double reward
        multiplier = self.double_reward_multiplier
        double_status = "Done"
        if multiplier > 1:
            log(f"📺 Watching ad for {multiplier}x reward...", CYAN)
            self.dashboard.update_mode_status(mode, status="Watching Ad")
            ad_result = self.complete_double_reward_ad(mode)
            if ad_result.get("status") == "success":
                log(f"✅ Double reward activated! Multiplier: {multiplier}", GREEN)
                if "double_reward_multiplier" in ad_result:
                    self.double_reward_multiplier = ad_result["double_reward_multiplier"]
                final_amount = final_amount * multiplier
                double_status = "Done"
            else:
                # Cek auth error
                if is_auth_error(ad_result):
                    log("⚠️ Auth error detected, need new initData", RED)
                    self.needs_new_init_data = True
                    return False
                log(f"⚠️ Ad failed: {ad_result.get('message')}, proceeding with normal reward", YELLOW)
                double_status = "Skip"

        # 3. Solve captcha
        token = self.solve_captcha(mode)
        if not token:
            log("❌ Failed to solve captcha", RED)
            self.dashboard.update_mode_status(mode, status="Captcha Fail", reward="fail")
            return False

        # 4. Claim
        log(f"⛏️ Claiming reward for {mode}...", DIM)
        self.dashboard.update_mode_status(mode, status="Claiming")
        claim_result = self.claim_faucet(mode, token)
        if claim_result.get("status") == "success":
            claimed = claim_result.get("claimed_amount", final_amount)
            coin = claim_result.get("coin", "PEPE")
            log(f"🎉 Claimed {claimed} {coin} from {mode}!", GREEN)
            try:
                reward_num = float(claimed)
                reward_display = f"{reward_num:.8f}"
            except (ValueError, TypeError):
                reward_display = str(claimed)
            self.total_claim_count += 1
            self.dashboard.update_mode_status(
                mode,
                status="✅",
                reward=reward_display,
                double=double_status,
                play_inc=1
            )
            if "faucet_global_cooldown_remaining" in claim_result:
                self.global_cooldown = time.time() + claim_result["faucet_global_cooldown_remaining"]
            mode_key = f"faucet_cooldown_remaining_{mode}"
            if mode_key in claim_result:
                self.cooldowns[mode] = time.time() + claim_result[mode_key]
            return True
        else:
            # Cek auth error
            if is_auth_error(claim_result):
                log("⚠️ Auth error detected, need new initData", RED)
                self.needs_new_init_data = True
                return False
            log(f"❌ Claim failed: {claim_result.get('message')}", RED)
            self.dashboard.update_mode_status(mode, status="Claim Fail", reward="fail")
            return False

    def run_loop(self):
        self.dashboard_thread = threading.Thread(target=self.dashboard.render_loop, daemon=True)
        self.dashboard_thread.start()

        log("🚀 Starting CoinFree Auto Bot...", PURPLE)
        log(f"📋 Modes: {', '.join(self.modes)}", DIM)

        while self.running:
            # Cek auth dulu
            if self.needs_new_init_data:
                log("🔄 InitData expired. Please update.", YELLOW)
                break  # keluar dari loop, akan di-handle di main

            self.get_user_data()
            if self.needs_new_init_data:
                continue

            log(f"👤 Balance: {self.user_data.get('balance', 0)}", LIME)

            self.run_loop_count += 1
            balance = float(self.user_data.get("balance", 0))
            coin = self.user_data.get("preferred_coin", "PEPE")
            self.dashboard.update_account_info(
                balance=balance,
                username=self.username,
                run_loop=self.run_loop_count,
                total_claim=self.total_claim_count,
                coin=coin
            )
            for mode in self.modes:
                if not self.running or self.needs_new_init_data:
                    break
                self.play_mode(mode)
                if self.needs_new_init_data:
                    break
                self.get_user_data()
                self.dashboard.refresh_all_cooldowns()
                time.sleep(2)
            if self.needs_new_init_data:
                continue
            log("🔄 Cycle complete. Waiting 10s before next round...", DIM)
            for _ in range(10):
                if not self.running or self.needs_new_init_data:
                    break
                time.sleep(1)

    def stop(self):
        self.running = False
        if self.dashboard:
            self.dashboard.stop()
        if self.dashboard_thread and self.dashboard_thread.is_alive():
            self.dashboard_thread.join(timeout=2)

# ==================== MAIN MENU ====================
def show_banner():
    clear()
    print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════════╗
║   {GOLD}⚡  COINFREE AUTO BOT — ALL MODES                     {PURPLE}║
║   {LIME}🎮 Auto Play • 📺 Auto Ad • 💰 Auto Claim            {PURPLE}║
║   {PINK}👑 Made ScriptyXSouu                          {PURPLE}║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

def get_captcha_service():
    print(f"""
{CYAN}Pilih solver Captcha:{RESET}
  {GREEN}[1]{RESET} Skibidixxx (waryono.my.id)
  {GREEN}[2]{RESET} BypassAllShortlinks.space
""")
    choice = input(f"{PURPLE}❯ Pilih (1/2): {RESET}").strip()
    if choice == "1":
        return "waryono"
    elif choice == "2":
        return "bypassall"
    else:
        log("Pilihan tidak valid, default ke bypassall", YELLOW)
        return "bypassall"

def refresh_init_data() -> str:
    """Minta user input init_data baru dan simpan ke config"""
    show_banner()
    print(f"{YELLOW}📝 InitData expired or invalid. Please paste new initData:{RESET}")
    new_init_data = input("initData: ").strip()
    while not new_init_data:
        log("InitData cannot be empty!", RED)
        new_init_data = input("initData: ").strip()
    # Simpan ke config
    config = load_config()
    config["init_data"] = new_init_data
    save_config(config)
    log("✅ InitData updated!", GREEN)
    return new_init_data

def main():
    config = load_config()
    init_data = config.get("init_data")
    device_id = config.get("device_id")

    # Jika device_id belum ada, buat baru
    if not device_id:
        device_id = uuid.uuid4().hex
        config["device_id"] = device_id
        save_config(config)

    # Captcha solver
    service = config.get("captcha_service")
    api_key = config.get(f"{service}_apikey") if service else None
    if not service or not api_key:
        show_banner()
        service = get_captcha_service()
        api_key = input(f"Masukkan API Key untuk {service}: ").strip()
        if not api_key:
            log("API Key required!", RED)
            sys.exit(1)
        config["captcha_service"] = service
        config[f"{service}_apikey"] = api_key
        save_config(config)

    captcha_solver = CaptchaSolver(service, api_key)

    # Loop utama dengan auto-recovery
    while True:
        if not init_data:
            show_banner()
            print(f"{RED}❌ No InitData found!{RESET}")
            print(f"{YELLOW}📝 Paste your initData from Telegram:{RESET}")
            init_data = input("initData: ").strip()
            if not init_data:
                log("InitData cannot be empty!", RED)
                time.sleep(1)
                continue
            config["init_data"] = init_data
            save_config(config)

        # Buat bot dengan init_data saat ini
        bot = CoinFreeBot(init_data, device_id, captcha_solver)
        try:
            bot.run_loop()
        except KeyboardInterrupt:
            log("\n👋 Stopping...", YELLOW)
            bot.stop()
            sys.exit(0)
        except Exception as e:
            log(f"⚠️ Unexpected error: {e}", RED)
            bot.stop()
            time.sleep(2)

        # Jika bot berhenti karena needs_new_init_data atau error, minta refresh
        if bot.needs_new_init_data:
            log("🔁 InitData expired. Please provide new initData.", YELLOW)
            init_data = refresh_init_data()
            # Loop akan restart dengan init_data baru
            continue
        else:
            # Bot berhenti normal (misal user stop), keluar
            break

if __name__ == "__main__":
    main()
