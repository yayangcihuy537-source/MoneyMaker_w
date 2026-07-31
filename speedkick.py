#!/usr/bin/env python3
"""
SpeedKick 24/7 Automation — Ads + Mining + Withdraw + Menu
Developer: ScriptyXSouu (Fixed by Kyriel)
"""

import os
import sys
import requests
import json
import time
import uuid
import hmac
import hashlib
import urllib.parse
from typing import Dict, Optional
from datetime import datetime

# ==================== CLEAR ====================
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================== CONFIG ====================
HMAC_KEY = b"f47b8274bff456e5a19b9f1351a73829a831849c994b98f1e3f3fd4c38a55c81"
BASE_URL = "https://api.speedkick.space"
CONFIG_FILE = "speedkick_config.json"

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

# ==================== BANNER ====================
def banner():
    clear()
    print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════════╗
║   {GOLD}⚡  SPEEDKICK AUTO BOT v3.2 — MENU MODE                {PURPLE}║
║   {LIME}🌾 Auto Farming • 💸 Withdraw • 📊 Balance            {PURPLE}║
║   {PINK}👑 Developer : ScriptyXSouu                          {PURPLE}║
║   {CYAN}🤖 BOT : SPEEDKICKBOT                                {PURPLE}║
╚══════════════════════════════════════════════════════════════╝{RESET}
""")

# ==================== SPEEDKICK CLASS ====================
class SpeedKick:
    def __init__(self, init_data: str):
        self.base_url = BASE_URL
        self.init_data = init_data
        self.session = requests.Session()
        self.user_data = None
        self.hmac_key = HMAC_KEY
        self.user_id = self._get_user_id()
        self.headers = {
            'Host': 'api.speedkick.space',
            'Connection': 'keep-alive',
            'sec-ch-ua-platform': '"Android"',
            'x-init-data': init_data,
            'User-Agent': 'Mozilla/5.0 (Linux; Android 16; K) Telegram-Android/12.6.4 (Samsung SM-A556E; Android 16; SDK 36; HIGH)',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Origin': 'https://speedkick.space',
            'X-Requested-With': 'org.telegram.messenger.web',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://speedkick.space/',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'en-IN,en-US;q=0.9,en;q=0.8',
            'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
            'sec-ch-ua-mobile': '?1',
        }

    def _get_user_id(self) -> str:
        parsed = urllib.parse.parse_qs(self.init_data)
        user_str = parsed.get('user', [''])[0]
        if user_str:
            try:
                user_str = urllib.parse.unquote(user_str)
                user = json.loads(user_str)
                return str(user.get('id', ''))
            except:
                pass
        return ''

    def _generate_nonce(self) -> str:
        return str(uuid.uuid4())

    def _generate_timestamp(self) -> str:
        return str(int(time.time() * 1000))

    def _sign_hmac(self, data: str) -> str:
        return hmac.new(self.hmac_key, data.encode(), hashlib.sha256).hexdigest()

    def _generate_signature(self, method: str, path: str, timestamp: str, nonce: str, body: str = "") -> str:
        sign_string = f"{method.upper()}\n{path}\n{timestamp}\n{nonce}\n{body}"
        return self._sign_hmac(sign_string)

    def _generate_xsrf_sign(self, nonce: str) -> str:
        data = f"{self.user_id}:{nonce}" if self.user_id else nonce
        return self._sign_hmac(data)

    def _request(self, method: str, path: str, data: Optional[Dict] = None) -> Dict:
        url = f"{self.base_url}{path}"
        body = json.dumps(data, separators=(',', ':')) if data else ""

        headers = self.headers.copy()
        nonce = self._generate_nonce()
        timestamp = self._generate_timestamp()
        signature = self._generate_signature(method, path, timestamp, nonce, body)
        xsrf_sign = self._generate_xsrf_sign(nonce)

        headers.update({
            'x-nonce': nonce,
            'x-timestamp': timestamp,
            'x-signature': signature,
            'x-xsrf-sign': xsrf_sign,
            'Content-Length': str(len(body))
        })

        try:
            if method.upper() == "GET":
                resp = self.session.get(url, headers=headers)
            else:
                resp = self.session.post(url, headers=headers, data=body)
            if resp.status_code != 200:
                return {"ok": False, "error": f"HTTP {resp.status_code}", "detail": resp.text}
            return resp.json()
        except Exception as e:
            return {"ok": False, "error": str(e)}

    def _parse_timestamp(self, ts) -> int:
        if ts is None: return 0
        if isinstance(ts, int): return ts
        if isinstance(ts, str):
            try:
                if 'T' in ts:
                    dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    return int(dt.timestamp() * 1000)
                return int(ts)
            except:
                return 0
        return 0

    # --- API Methods ---
    def auth_telegram(self) -> Dict:
        payload = {"initData": self.init_data, "referralCode": None}
        result = self._request("POST", "/api/auth/telegram", payload)
        if result.get("ok"):
            self.user_data = result.get("user", {})
        return result

    def verify_task(self, task_id: str) -> Dict:
        return self._request("POST", "/api/user/task/verify", {"taskId": task_id})

    def get_mining_status(self) -> Dict:
        return self._request("GET", "/api/user/mining/status")

    def complete_ad(self, purpose: str) -> Dict:
        return self._request("POST", "/api/user/ad/complete", {"purpose": purpose})

    def claim_mining(self) -> Dict:
        ad_result = self.complete_ad("game_claim")
        if not ad_result.get("ok"):
            return {"ok": False, "error": f"Ad failed: {ad_result.get('error')}"}
        token = ad_result.get("token")
        if not token:
            return {"ok": False, "error": "No token from ad completion"}
        return self._request("POST", "/api/user/mining/claim", {"token": token})

    def get_ad_views(self) -> int:
        # Selalu refresh dari server
        status = self.get_mining_status()
        if status.get("ok"):
            return status.get("adZone", {}).get("views", 0)
        return 0

    def get_ad_cooldown(self) -> int:
        status = self.get_mining_status()
        if status.get("ok"):
            return status.get("adZone", {}).get("cooldownUntil", 0)
        return 0

    def get_balance(self) -> float:
        status = self.get_mining_status()
        return status.get("balance", 0) if status.get("ok") else 0

    # --- FIXED: Ads loop with proper refresh ---
    def run_ads(self) -> bool:
        total = 20
        while True:
            # Ambil fresh views setiap iterasi
            views = self.get_ad_views()
            if views >= total:
                print(f"{GREEN}✅ All {total} ads done today{RESET}")
                return True

            cooldown_until = self.get_ad_cooldown()
            if cooldown_until and cooldown_until > 0:
                now = int(time.time() * 1000)
                if cooldown_until > now:
                    wait_seconds = (cooldown_until - now) / 1000
                    if wait_seconds > 0:
                        print(f"{YELLOW}⏳ Ads cooldown, waiting {wait_seconds:.0f}s...{RESET}")
                        time.sleep(wait_seconds)
                        continue

            next_ad = views + 1
            task_id = f"ad_zone_{next_ad}"
            print(f"\n{WHITE}🎯 {task_id}{RESET}")
            result = self.verify_task(task_id)

            if result.get("ok"):
                reward = result.get("reward", 0)
                print(f"{GOLD}💰 Reward : +{reward}{RESET}")
                print(f"{GREEN}✅ Claimed Successfully{RESET}")
                # Loop lagi, ambil views terbaru di awal loop
                continue
            else:
                error = result.get("error", "").lower()
                if "cooldown" in error or "throttle" in error or "too many" in error:
                    next_ad_at = self._parse_timestamp(result.get("nextAdAt"))
                    if next_ad_at:
                        wait_seconds = max(0, (next_ad_at - int(time.time()*1000)) / 1000)
                    else:
                        wait_seconds = 30
                    print(f"{YELLOW}⏳ Cooldown, waiting {wait_seconds:.0f}s...{RESET}")
                    time.sleep(wait_seconds)
                    continue
                elif "already" in error or "done" in error:
                    print(f"{GREEN}✅ Already done, refreshing views...{RESET}")
                    # Refresh views dan lanjut
                    continue
                else:
                    print(f"{RED}❌ Error: {error[:50]}{RESET}")
                    time.sleep(5)
                    continue

    # --- Mining (same) ---
    def run_mining(self) -> Dict:
        status = self.get_mining_status()
        if not status.get("ok"):
            print(f"{RED}❌ Mining status failed: {status.get('error')}{RESET}")
            return {"ok": False}
        mining = status.get("mining", {})
        can_claim = mining.get("canClaim", False)
        if can_claim:
            print(f"{CYAN}⛏️ Claiming mining...{RESET}")
            result = self.claim_mining()
            if result.get("ok"):
                reward = result.get("reward", 0)
                new_balance = result.get("newBalance", status.get("balance", 0))
                mining_data = result.get("mining", {})
                next_claim = mining_data.get("nextClaimAt")
                next_claim_ts = self._parse_timestamp(next_claim)
                if next_claim_ts:
                    wait = max(0, (next_claim_ts - int(time.time()*1000)) / 1000)
                    print(f"{GREEN}🎉 +{reward} | Balance: {new_balance} | Next mining: {wait/60:.1f}m{RESET}")
                else:
                    print(f"{GREEN}🎉 +{reward} | Balance: {new_balance}{RESET}")
                return {"ok": True, "nextClaimAt": next_claim_ts}
            else:
                print(f"{RED}❌ Claim failed: {result.get('error')}{RESET}")
                return {"ok": False}
        else:
            next_claim = mining.get("nextClaimAt")
            next_claim_ts = self._parse_timestamp(next_claim)
            if next_claim_ts:
                wait = max(0, (next_claim_ts - int(time.time()*1000)) / 1000)
                print(f"{YELLOW}⏳ Next mining in {wait/60:.1f}m{RESET}")
                return {"ok": False, "nextClaimAt": next_claim_ts}
            else:
                print(f"{YELLOW}⏳ Mining not ready{RESET}")
                return {"ok": False}

    # --- Withdraw (same) ---
    def withdraw_check(self) -> Dict:
        return self._request("GET", "/api/withdraw/check")

    def withdraw_submit(self, amount: int, network: str, address: str, ad_token: str) -> Dict:
        payload = {
            "amount": amount,
            "network": network,
            "address": address,
            "adToken": ad_token
        }
        return self._request("POST", "/api/withdraw/submit", payload)

    def withdraw(self, amount: int, network: str, address: str) -> Dict:
        print(f"{CYAN}💸 Bypass Withdraw SpeedKick{RESET}")
        print(f"   Amount: {amount} | Network: {network}")
        print(f"   Address: {address[:10]}...{address[-6:]}")

        check = self.withdraw_check()
        if not check.get("ok"):
            print(f"{RED}❌ Check failed: {check.get('error')}{RESET}")
            return check
        if not check.get("eligible"):
            print(f"{RED}❌ Not eligible (min: {check.get('min')}){RESET}")
            return check
        print(f"{GREEN}✅ Eligible | Min: {check['min']} | Fee: {check.get('fee', 0)}{RESET}")

        ad = self.complete_ad("withdraw")
        if not ad.get("ok"):
            print(f"{RED}❌ Ad failed: {ad.get('error')}{RESET}")
            return ad
        token = ad.get("token")
        if not token:
            print(f"{RED}❌ No token returned from ad{RESET}")
            return {"ok": False, "error": "No token"}
        print(f"{GREEN}✅ Ad token: {token[:20]}...{RESET}")

        result = self.withdraw_submit(amount, network, address, token)
        if result.get("ok"):
            print(f"{GREEN}🎉 Withdraw submitted!{RESET}")
            print(f"   Request ID: {result.get('requestId')}")
            print(f"   Net Amount: {result.get('netAmount')}")
            print(f"   New Balance: {result.get('newBalance')}")
            print(f"   Processing: {result.get('processingTime')}")
        else:
            print(f"{RED}❌ Withdraw failed: {result.get('error')}{RESET}")
        return result

    # --- Smart Loop (FIXED: uses run_ads that now works) ---
    def smart_loop(self):
        print(f"\n{GREEN}🌾 Starting Ads Farming...{RESET}")
        print(f"{YELLOW}Press Ctrl+C to return to menu{RESET}\n")
        self.run_ads()  # runs until 20 ads done
        print(f"\n{GREEN}🎉 All ads completed! Returning to menu...{RESET}")

# ==================== CONFIG FILE ====================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f).get('init_data')
    return None

def save_config(init_data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"init_data": init_data}, f)

# ==================== MAIN MENU ====================
def main():
    init_data = load_config()
    
    while not init_data:
        banner()
        print(f"{RED}❌ No InitData found!{RESET}")
        print(f"{YELLOW}📝 Please paste your InitData from Telegram:{RESET}")
        init_data = input("initData: ").strip()
        if init_data:
            save_config(init_data)
            print(f"{GREEN}✅ InitData saved!{RESET}\n")
            input("Tekan Enter untuk lanjut...")
            clear()
            break
        else:
            print(f"{RED}❌ InitData cannot be empty!{RESET}")
            time.sleep(1)
            clear()

    while True:
        banner()
        
        bot = SpeedKick(init_data)
        auth = bot.auth_telegram()
        if not auth.get("ok"):
            print(f"{RED}❌ InitData expired or invalid!{RESET}")
            print(f"{YELLOW}📝 Please update your InitData.{RESET}")
            init_data = input("New initData: ").strip()
            if init_data:
                save_config(init_data)
                clear()
                continue
            else:
                print(f"{RED}❌ InitData required!{RESET}")
                time.sleep(1)
                clear()
                continue
        
        balance = bot.get_balance()
        user = auth.get("user", {})
        print(f"{GREEN}👤 {user.get('firstName', 'User')} | 💰 Balance: {balance} V{RESET}")
        
        print(f"""
{CYAN}╔════════════════════════════════════════════════════╗
║                    MAIN MENU                         ║
╠════════════════════════════════════════════════════╣
║  {GREEN}[1]{RESET} 🌾 Start Farming (Ads only)                 ║
║  {PINK}[2]{RESET} 💸 Withdraw                               ║
║  {BLUE}[3]{RESET} 📊 Check Balance                         ║
║  {YELLOW}[4]{RESET} 📝 Update InitData                      ║
║  {RED}[0]{RESET} ❌ Exit                                  ║
╚════════════════════════════════════════════════════╝{RESET}
""")
        choice = input(f"{PURPLE}❯ Pilih: {RESET}").strip()

        if choice == '0':
            print(f"{YELLOW}👋 Bye!{RESET}")
            sys.exit(0)
        elif choice == '1':
            bot.smart_loop()
            clear()
        elif choice == '2':
            try:
                amount = int(input("Amount (min 500): ").strip())
                network = input("Network (USDT_BEP20/USDT_TRC20): ").strip().upper()
                address = input("Address: ").strip()
                if not network or not address:
                    print(f"{RED}❌ Network/Address required{RESET}")
                else:
                    bot.withdraw(amount, network, address)
            except ValueError:
                print(f"{RED}❌ Amount must be number{RESET}")
            input("Tekan Enter untuk kembali...")
            clear()
        elif choice == '3':
            print(f"{GREEN}💰 Balance: {balance} V{RESET}")
            input("Tekan Enter untuk kembali...")
            clear()
        elif choice == '4':
            print(f"{YELLOW}📝 Paste new InitData:{RESET}")
            new_data = input("initData: ").strip()
            if new_data:
                init_data = new_data
                save_config(init_data)
                print(f"{GREEN}✅ InitData updated!{RESET}")
                time.sleep(1)
                clear()
            else:
                print(f"{RED}❌ Cannot be empty!{RESET}")
                time.sleep(1)
                clear()
        else:
            time.sleep(1)
            clear()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}👋 Bye!{RESET}")
        sys.exit(0)
