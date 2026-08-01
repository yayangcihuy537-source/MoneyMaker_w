#!/usr/bin/env python3
"""
Earnbitsun Auto Faucet Bot (Simple)
By: Kyriel (for Bos)
Auto Save Config + 2 Solver
"""

import os
import sys
import json
import time
import uuid
import requests
from typing import Dict, Optional
from datetime import datetime

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
BASE_URL = "https://earnbitsun.club"
CONFIG_FILE = "earnbitsun_config.json"
USER_AGENT = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"
CAPTCHA_SITEKEY = "0x4AAAAAADXP0YCJj-kEWRBh"
CAPTCHA_PAGEURL = "https://earnbitsun.club"

# ==================== HELPERS ====================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log(msg, color=WHITE):
    print(f"{DIM}[{timestamp()}]{RESET} {color}{msg}{RESET}")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ==================== CAPTCHA SOLVER ====================
class CaptchaSolver:
    def __init__(self, service: str, api_key: str):
        self.service = service
        self.api_key = api_key
        if service == 'waryono':
            self.base = "https://api.waryono.my.id"
        else:
            self.base = "https://bypassallshortlinks.space"

    def solve_turnstile(self, pageurl: str, timeout: int = 90) -> Optional[str]:
        if self.service == 'waryono':
            return self._solve_waryono(pageurl, timeout)
        else:
            return self._solve_bypassall(pageurl, timeout)

    def _solve_waryono(self, pageurl: str, timeout: int) -> Optional[str]:
        payload = {
            "apikey": self.api_key,
            "methods": "turnstile",
            "domain": pageurl,
            "sitekey": CAPTCHA_SITEKEY,
            "action": "login",
            "cdata": f"session_{uuid.uuid4().hex[:8]}",
            "json": 1
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
                status = data.get("status")
                request = data.get("request", "")
                
                if status == 1:
                    token = request
                    if token and not token.startswith("ERROR"):
                        log(f"✅ Waryono solved: {token[:20]}...", GREEN)
                        return token
                    else:
                        log(f"❌ Waryono response invalid: {token}", RED)
                        return None
                elif request == "CAPCHA_NOT_READY":
                    continue
                elif request == "ERROR_CAPTCHA_UNSOLVABLE":
                    log(f"❌ Waryono unsolvable, retrying...", YELLOW)
                    return None
                else:
                    log(f"❌ Waryono error: {request}", RED)
                    return None
            except Exception as e:
                log(f"⚠️ Waryono poll error: {e}", YELLOW)
                continue
        log("⏰ Waryono timeout", YELLOW)
        return None

    def _solve_bypassall(self, pageurl: str, timeout: int) -> Optional[str]:
        params = {"key": self.api_key, "method": "turnstile", "sitekey": CAPTCHA_SITEKEY, "pageurl": pageurl}
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

# ==================== EARNBITSUN BOT ====================
class EarnbitsunBot:
    def __init__(self, email: str, password: str, captcha_solver: CaptchaSolver):
        self.email = email
        self.password = password
        self.captcha_solver = captcha_solver
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': USER_AGENT,
            'accept': 'application/json, text/plain, */*',
            'content-type': 'application/json',
            'origin': BASE_URL,
            'referer': f'{BASE_URL}/faucet',
        })
        self.csrf_token = None
        self.balance = 0
        self.total_claims = 0
        self.running = True

    def get_csrf_token(self) -> bool:
        try:
            r = self.session.get(f"{BASE_URL}/api/auth/csrf")
            if r.status_code == 200:
                data = r.json()
                self.csrf_token = data.get("csrfToken")
                log(f"✅ CSRF token: {self.csrf_token[:20]}...", DIM)
                return True
            return False
        except:
            return False

    def login(self) -> bool:
        if not self.csrf_token:
            if not self.get_csrf_token():
                return False

        log("🔐 Solving captcha for login...", CYAN)
        captcha_token = self.captcha_solver.solve_turnstile(CAPTCHA_PAGEURL)
        if not captcha_token:
            log("❌ Failed to get captcha token for login", RED)
            return False

        payload = {
            "email": self.email,
            "password": self.password,
            "captcha_token": f"turnstile:{captcha_token}"
        }

        try:
            r = self.session.post(f"{BASE_URL}/api/auth/signin", json=payload)
            if r.status_code == 200:
                data = r.json()
                if data.get("data", {}).get("success"):
                    log(f"✅ Login successful!", GREEN)
                    return True
                else:
                    log(f"❌ Login failed: {data.get('error', 'Unknown')}", RED)
                    return False
            else:
                log(f"❌ Login HTTP error: {r.status_code}", RED)
                return False
        except Exception as e:
            log(f"❌ Login exception: {e}", RED)
            return False

    def get_faucet_status(self) -> Dict:
        try:
            r = self.session.get(f"{BASE_URL}/api/faucet")
            if r.status_code == 200:
                return r.json().get("data", {})
            return {}
        except:
            return {}

    def get_balance(self) -> float:
        try:
            r = self.session.get(f"{BASE_URL}/api/account/tokens/Coins")
            if r.status_code == 200:
                return float(r.json().get("data", {}).get("balance", 0))
            return 0
        except:
            return 0

    def get_username(self) -> str:
        try:
            r = self.session.get(f"{BASE_URL}/faucet")
            if r.status_code == 200:
                import re
                match = re.search(r'class="text-sm font-bold text-green-600">([^<]+)<', r.text)
                if match:
                    return match.group(1)
            return "Unknown"
        except:
            return "Unknown"

    def claim_faucet(self) -> bool:
        log("🎯 Claiming faucet...", CYAN)

        status = self.get_faucet_status()
        if status.get("cycle_ended_at"):
            try:
                from datetime import datetime as dt
                end_time = dt.fromisoformat(status["cycle_ended_at"].replace('Z', '+00:00')).timestamp()
                now = time.time()
                if now < end_time:
                    wait = int(end_time - now)
                    log(f"⏳ Cooldown: {wait}s", YELLOW)
                    return False
            except:
                pass

        log("🔐 Solving captcha for claim...", CYAN)
        captcha_token = self.captcha_solver.solve_turnstile(CAPTCHA_PAGEURL)
        if not captcha_token:
            log("❌ Failed to get captcha token", RED)
            return False

        payload = {"captcha_token": f"turnstile:{captcha_token}"}

        try:
            headers = {
                'User-Agent': USER_AGENT,
                'accept': 'application/json, text/plain, */*',
                'content-type': 'application/json',
                'x-version-request': '934d362',
                'origin': BASE_URL,
                'referer': f'{BASE_URL}/faucet',
            }
            r = self.session.post(f"{BASE_URL}/api/faucet", json=payload, headers=headers)
            if r.status_code == 200:
                data = r.json()
                if data.get("data"):
                    result = data.get("data")
                    claimed = result.get("claimed_amount", 0)
                    log(f"🎉 Claimed! +{claimed} Coins", GREEN)
                    self.total_claims += 1
                    return True
                else:
                    log(f"❌ Claim failed: {data.get('error', 'Unknown')}", RED)
                    return False
            else:
                log(f"❌ Claim HTTP error: {r.status_code}", RED)
                return False
        except Exception as e:
            log(f"❌ Claim exception: {e}", RED)
            return False

    def run(self):
        clear()
        print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════════╗
║   {GOLD}⚡  EARNBITSUN AUTO FAUCET BOT                      {PURPLE}║
║   {LIME}🎯 Auto Claim • 🤖 Auto Captcha • 💰 Auto Earn     {PURPLE}║
║   {PINK}👑 Made ScriptyXSou                         {PURPLE}║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")
        log("🚀 Starting Earnbitsun Bot...", PURPLE)
        log(f"📧 Email: {self.email}", DIM)

        if not self.login():
            log("❌ Login failed.", RED)
            return

        username = self.get_username()
        balance = self.get_balance()
        status = self.get_faucet_status()
        if status:
            self.total_claims = status.get("total_claims", 0)

        log(f"👤 Username: {username}", GREEN)
        log(f"💰 Balance: {balance} Coins", GOLD)

        loop = 0
        while self.running:
            loop += 1
            log(f"\n{'='*40}", DIM)
            log(f"🔄 Cycle #{loop}", CYAN)

            success = self.claim_faucet()
            if not success:
                status = self.get_faucet_status()
                if status and status.get("cycle_ended_at"):
                    try:
                        from datetime import datetime as dt
                        end_time = dt.fromisoformat(status["cycle_ended_at"].replace('Z', '+00:00')).timestamp()
                        now = time.time()
                        if now < end_time:
                            wait = int(end_time - now) + 2
                            log(f"⏳ Waiting {wait}s...", YELLOW)
                            time.sleep(wait)
                            continue
                    except:
                        pass
                log("⏳ Waiting 30s...", YELLOW)
                time.sleep(30)
            else:
                balance = self.get_balance()
                log(f"💰 Balance: {balance} Coins", GOLD)

            time.sleep(5)

    def stop(self):
        self.running = False

# ==================== MAIN ====================
def show_banner():
    clear()
    print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════════╗
║   {GOLD}⚡  EARNBITSUN AUTO FAUCET BOT                      {PURPLE}║
║   {LIME}🎯 Auto Claim • 🤖 Auto Captcha • 💰 Auto Earn     {PURPLE}║
║   {PINK}👑 Made ScriptyXSou                          {PURPLE}║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

def get_captcha_service():
    print(f"""
{CYAN}Pilih solver Captcha:{RESET}
  {GREEN}[1]{RESET} Skibidixxx (waryono.my.id)
  {GREEN}[2]{RESET} BypassAllShortlinks.space
""")
    choice = input(f"{PURPLE}❯ Pilih (1/2): {RESET}").strip()
    return "waryono" if choice == "1" else "bypassall"

def main():
    config = load_config()

    # Kalo config ada, pake langsung
    email = config.get("email")
    password = config.get("password")
    service = config.get("captcha_service")
    api_key = config.get(f"{service}_apikey") if service else None

    # Kalo ada yang kosong, minta input
    if not email or not password or not service or not api_key:
        show_banner()
        if not email:
            email = input("📧 Email: ").strip()
        if not password:
            password = input("🔑 Password: ").strip()
        if not service:
            service = get_captcha_service()
        if not api_key:
            api_key = input(f"🔑 API Key untuk {service}: ").strip()

        if not email or not password or not api_key:
            log("❌ Email, Password, dan API Key wajib!", RED)
            sys.exit(1)

        config["email"] = email
        config["password"] = password
        config["captcha_service"] = service
        config[f"{service}_apikey"] = api_key
        save_config(config)
        log(f"✅ Config saved to {CONFIG_FILE}", GREEN)

    captcha_solver = CaptchaSolver(service, api_key)
    bot = EarnbitsunBot(email, password, captcha_solver)

    try:
        bot.run()
    except KeyboardInterrupt:
        log("\n👋 Stopping...", YELLOW)
        bot.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
