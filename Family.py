#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  ⚡ PICK FAMILY BOT v5.9 - RETRY CAPTCHA 3X              ║
║  🔥 If captcha solver fails, retry 3 times, then skip                   ║
║  🔐 All sitekeys hardcoded (PolPick, SuiPick, etc)                      ║
║  🎲 Shows coin in logs, live cooldown countdown                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import random
import base64
import re
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ========== WARNA ==========
R = '\033[91m'
G = '\033[92m'
Y = '\033[93m'
B = '\033[94m'
C = '\033[96m'
W = '\033[97m'
M = '\033[95m'
RESET = '\033[0m'

# ========== KONFIGURASI ==========
CONFIG_FILE = "pick_family_config.json"

# ========== HARDCORE SITEKEY ==========
SITEKEY_MAP = {
    "TronPick": "0x4AAAAAAAW74HiAaujGhyeV",
    "LitePick": "0x4AAAAAAA0-UWDHOKP0OrgS",
    "DogePick": "0x4AAAAAABbyeJO9QkW9czUo",
    "BnbPick":  "0x4AAAAAAA0_O3uScCqtpqXl",
    "PolPick":  "0x4AAAAAAA8_cZ-8EiewkNNb",
    "SuiPick":  "0x4AAAAAABgtwLBJbn9NePjw",
}

PICK_SITES = [
    {"name": "TronPick", "url": "https://tronpick.io", "currency": "TRX", "faucet_page": "/faucet.php"},
    {"name": "LitePick", "url": "https://litepick.io", "currency": "LTC", "faucet_page": "/faucet.php"},
    {"name": "DogePick", "url": "https://dogepick.io", "currency": "DOGE", "faucet_page": "/faucet.php"},
    {"name": "BnbPick", "url": "https://bnbpick.io", "currency": "BNB", "faucet_page": "/faucet.php"},
    {"name": "PolPick", "url": "https://polpick.io", "currency": "POL", "faucet_page": "/faucet.php"},
    {"name": "SuiPick", "url": "https://suipick.io", "currency": "SUI", "faucet_page": "/faucet.php"},
]

# ========== DATA CLASS ==========
@dataclass
class SiteStats:
    name: str
    currency: str
    balance: float = 0.0
    last_claim: float = 0.0
    total_earned: float = 0.0
    claim_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    cooldown: int = 0
    cooldown_until: Optional[datetime] = None
    status: str = "Idle"
    last_error: str = ""

@dataclass
class BotStats:
    total_earned: float = 0.0
    total_claims: int = 0
    total_success: int = 0
    total_fail: int = 0
    total_cooldown: int = 0
    start_time: datetime = field(default_factory=datetime.now)
    run_time: str = "00:00:00"
    logs: List[str] = field(default_factory=list)

# ========== CAPTCHA SOLVER ==========
class CaptchaSolver:
    @staticmethod
    def check_waryono_balance(api_key: str) -> Optional[float]:
        try:
            resp = requests.get(
                "https://api.waryono.my.id/balance.php",
                params={"apikey": api_key},
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == 1:
                    return float(data.get("balance", 0))
        except:
            pass
        return None
    
    @staticmethod
    def solve_waryono(api_key: str, sitekey: str, domain: str) -> Optional[str]:
        try:
            submit_url = "https://api.waryono.my.id/in.php"
            payload = {
                "apikey": api_key,
                "methods": "turnstile",
                "domain": domain,
                "sitekey": sitekey,
                "action": "login",
                "cdata": f"session_{random.randint(100000, 999999)}"
            }
            resp = requests.post(submit_url, json=payload, timeout=30)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if data.get("status") != 1:
                return None
            task_id = data.get("task_id") or data.get("id") or data.get("request")
            if not task_id or task_id == "ERROR":
                return None
            poll_url = "https://api.waryono.my.id/res.php"
            for _ in range(30):
                time.sleep(2)
                poll_resp = requests.get(
                    poll_url,
                    params={
                        "apikey": api_key,
                        "id": task_id,
                        "action": "get",
                        "json": 1
                    },
                    timeout=30
                )
                if poll_resp.status_code != 200:
                    continue
                try:
                    result = poll_resp.json()
                except:
                    continue
                if result.get("status") == 1:
                    token = result.get("response") or result.get("request")
                    if token and not token.startswith("ERROR"):
                        return token
                elif result.get("status") == 0:
                    msg = result.get("request", "")
                    if "ERROR" in msg:
                        return None
                    continue
                else:
                    return None
            return None
        except:
            return None
    
    @staticmethod
    def solve_bypassall(api_key: str, sitekey: str, pageurl: str) -> Optional[str]:
        try:
            submit_url = "https://bypassallshortlinks.space/in.php"
            params = {
                "key": api_key,
                "method": "turnstile",
                "sitekey": sitekey,
                "pageurl": pageurl
            }
            resp = requests.get(submit_url, params=params, timeout=30)
            if resp.status_code != 200:
                return None
            text = resp.text.strip()
            if text.startswith("OK|"):
                task_id = text.split("|")[1]
            else:
                return None
            poll_url = "https://bypassallshortlinks.space/res.php"
            for _ in range(30):
                time.sleep(3)
                poll_resp = requests.get(
                    poll_url,
                    params={"id": task_id, "key": api_key},
                    timeout=30
                )
                if poll_resp.status_code != 200:
                    continue
                text = poll_resp.text.strip()
                if text.startswith("OK|"):
                    return text.split("|")[1]
                elif "ERROR" in text:
                    return None
            return None
        except:
            return None

# ========== BASE FAUCET CLASS ==========
class PickFaucet:
    def __init__(self, site_config: dict, credentials: dict, captcha_config: dict):
        self.name = site_config["name"]
        self.base_url = site_config["url"]
        self.currency = site_config["currency"]
        self.faucet_page = site_config["faucet_page"]
        self.email = credentials.get("email", "")
        self.password = credentials.get("password", "")
        self.captcha_service = captcha_config.get("service", "manual")
        self.waryono_key = captcha_config.get("waryono_api_key", "")
        self.bypassall_key = captcha_config.get("bypassall_api_key", "")
        self.solver = CaptchaSolver()
        
        self.sitekey = SITEKEY_MAP.get(self.name)
        if not self.sitekey:
            self.sitekey = self._get_sitekey_from_html()
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "id-ID",
            "Accept-Encoding": "gzip, deflate, br",
            "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "navigate",
        })
        
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
        
        self.stats = SiteStats(name=self.name, currency=self.currency)
        self.logged_in = False
        self.csrf_token = None
        self.fingerprint = None
        self.decimals = 6
        self.units_per_coin = 1000000
        self._get_coin_info()
    
    def _get_sitekey_from_html(self) -> Optional[str]:
        resp = self.session.get(f"{self.base_url}/login.php")
        if resp.status_code != 200:
            return None
        match = re.search(r'CF_KEY\s*=\s*"([^"]+)"', resp.text)
        if match:
            return match.group(1)
        match = re.search(r'0x[0-9a-fA-F]{32,}', resp.text)
        if match:
            return match.group(0)
        return None
    
    def _get_coin_info(self):
        try:
            resp = self.session.get(f"{self.base_url}{self.faucet_page}")
            if resp.status_code != 200:
                return
            html = resp.text
            match = re.search(r'window\.COIN\s*=\s*({.*?});', html, re.DOTALL)
            if match:
                coin_data = json.loads(match.group(1))
                self.decimals = coin_data.get('decimals', 6)
                self.units_per_coin = coin_data.get('unitsPerCoin', 1000000)
        except Exception:
            pass
    
    def _get_csrf_token(self) -> Optional[str]:
        for cookie in self.session.cookies:
            if cookie.name == "csrf_cookie_name":
                return cookie.value
        return None
    
    def _generate_fingerprint(self) -> str:
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    def _solve_captcha(self, sitekey: str, action: str = "login") -> Optional[str]:
        """Solve captcha with 3 retries, skip if all fail."""
        max_retries = 3
        attempt = 0
        
        while attempt < max_retries:
            attempt += 1
            token = None
            
            if self.captcha_service == "waryono" and self.waryono_key:
                balance = self.solver.check_waryono_balance(self.waryono_key)
                if balance is not None and balance >= 1:
                    token = self.solver.solve_waryono(self.waryono_key, sitekey, self.base_url)
            elif self.captcha_service == "bypassall" and self.bypassall_key:
                token = self.solver.solve_bypassall(self.bypassall_key, sitekey, f"{self.base_url}/login.php")
            
            if token:
                return token
            
            # If solver failed and still have retries
            if attempt < max_retries and self.captcha_service != "manual":
                print(f"{Y}⚠️ Solver attempt {attempt} failed for {self.name}, retrying in 3s...{RESET}")
                time.sleep(3)
            elif attempt == max_retries and self.captcha_service != "manual":
                print(f"{Y}⚠️ All {max_retries} solver attempts failed for {self.name}, falling back to manual{RESET}")
            else:
                # Manual mode - just ask once
                break
        
        # Fallback to manual input (or skip if user cancels)
        if self.captcha_service == "manual" or attempt >= max_retries:
            print(f"{C}🔑 Masukkan token Turnstile untuk {self.name} ({action}){RESET}")
            print(f"{Y}Kosongkan untuk skip claim ini{RESET}")
            token = input(f"Token: {W}").strip()
            return token if token else None
        
        return None
    
    def _generate_claim_hash(self) -> str:
        clientX = random.randint(0, 500)
        clientY = random.randint(0, 500)
        ts = int(time.time())
        key = "1a324a7cf36279b7e8d6642963fdd9cadf77ffd22f8b9e753ccf0d317a81c2f9"
        data = f"{clientX}:{clientY}:{ts}"
        chars = []
        for i, c in enumerate(data):
            xor_val = ord(c) ^ ord(key[i % len(key)])
            chars.append(chr(xor_val))
        return base64.b64encode(''.join(chars).encode()).decode()
    
    def _parse_balance(self, html: str) -> Optional[float]:
        patterns = [
            r'id="dd_main_balance"[^>]*>([\d.,]+)',
            r'class="user_balance"[^>]*>([\d.,]+)',
            r'id="header-user-balance"[^>]*>([\d.,]+)',
            r'Balance:\s*([\d.,]+)',
            r'"balance":\s*([\d.]+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                raw = match.group(1).replace(',', '').strip()
                try:
                    return float(raw)
                except:
                    continue
        return None
    
    def login(self) -> bool:
        if not self.sitekey:
            self.stats.status = "No Sitekey"
            return False
        
        resp = self.session.get(f"{self.base_url}/login.php")
        if resp.status_code != 200:
            self.stats.status = "Login Failed"
            return False
        
        self.csrf_token = self._get_csrf_token()
        if not self.csrf_token:
            self.stats.status = "No CSRF"
            return False
        
        self.fingerprint = self.session.cookies.get("fp")
        if not self.fingerprint:
            self.fingerprint = self._generate_fingerprint()
            self.session.cookies.set("fp", self.fingerprint)
        
        token = self._solve_captcha(self.sitekey, "login")
        if not token:
            self.stats.status = "Captcha Failed"
            return False
        
        data = {
            "action": "login",
            "email": self.email,
            "password": self.password,
            "captcha_type": "3",
            "g-recaptcha-response": "",
            "_iconcaptcha-token": "",
            "ic-rq": "",
            "ic-wid": "",
            "ic-cid": "",
            "ic-hp": "",
            "h-captcha-response": "",
            "c_captcha_response": token,
            "pcaptcha_token": "",
            "twofa": "",
            "csrf_test_name": self.csrf_token,
        }
        
        resp = self.session.post(
            f"{self.base_url}/process.php",
            data=data,
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": self.base_url,
                "Referer": f"{self.base_url}/login.php",
            }
        )
        
        if resp.status_code != 200:
            self.stats.status = "Login Request Failed"
            return False
        
        try:
            result = resp.json()
            if result.get("ret") == 1:
                self.logged_in = True
                self.stats.status = "Logged In"
                return True
            else:
                self.stats.status = f"Login Failed: {result.get('mes', 'unknown')}"
                return False
        except:
            self.stats.status = "Invalid Response"
            return False
    
    def get_balance(self) -> float:
        resp = self.session.get(f"{self.base_url}{self.faucet_page}")
        if resp.status_code != 200:
            return self.stats.balance
        
        bal = self._parse_balance(resp.text)
        if bal is not None:
            self.stats.balance = bal
        return self.stats.balance
    
    def get_cooldown(self) -> int:
        try:
            resp = self.session.get(f"{self.base_url}{self.faucet_page}")
            if resp.status_code != 200:
                return 0
            patterns = [
                r'cooldown_remaining["\']?\s*:\s*(\d+)',
                r'data-cooldown["\']?\s*=\s*["\'](\d+)["\']',
                r'next_claim["\']?\s*:\s*(\d+)',
                r'countdown["\']?\s*:\s*(\d+)',
            ]
            for pattern in patterns:
                match = re.search(pattern, resp.text)
                if match:
                    cd = int(match.group(1))
                    self.stats.cooldown = cd
                    if cd > 0:
                        self.stats.cooldown_until = datetime.now() + timedelta(seconds=cd)
                    else:
                        self.stats.cooldown_until = None
                    return cd
            self.stats.cooldown = 0
            self.stats.cooldown_until = None
            return 0
        except:
            return 0
    
    def claim(self) -> Tuple[bool, float, str]:
        if not self.logged_in:
            if not self.login():
                return False, 0.0, "Not logged in"
        
        resp = self.session.get(f"{self.base_url}{self.faucet_page}")
        if resp.status_code != 200:
            return False, 0.0, "Failed to load faucet page"
        
        self.csrf_token = self._get_csrf_token()
        if not self.csrf_token:
            return False, 0.0, "No CSRF token"
        
        cooldown = self.get_cooldown()
        if cooldown > 0:
            self.stats.cooldown = cooldown
            self.stats.cooldown_until = datetime.now() + timedelta(seconds=cooldown)
            return False, 0.0, f"Cooldown {cooldown}s"
        
        if not self.sitekey:
            return False, 0.0, "No sitekey"
        
        token = self._solve_captcha(self.sitekey, "faucet")
        if not token:
            return False, 0.0, "Captcha failed (skipped)"
        
        claim_hash = self._generate_claim_hash()
        
        data = {
            "action": "claim_hourly_faucet",
            "hash": claim_hash,
            "captcha_type": "3",
            "g-recaptcha-response": "",
            "_iconcaptcha-token": "",
            "ic-rq": "",
            "ic-wid": "",
            "ic-cid": "",
            "ic-hp": "",
            "h-captcha-response": "",
            "c_captcha_response": token,
            "pcaptcha_token": "",
            "ft": self.session.cookies.get("_ft", ""),
            "csrf_test_name": self.csrf_token,
        }
        
        resp = self.session.post(
            f"{self.base_url}/process.php",
            data=data,
            headers={
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                "Origin": self.base_url,
                "Referer": f"{self.base_url}{self.faucet_page}",
            }
        )
        
        if resp.status_code != 200:
            return False, 0.0, f"Request failed: {resp.status_code}"
        
        try:
            result = resp.json()
            if result.get("ret") == 1:
                raw_reward = float(result.get('reward', 0))
                reward = raw_reward
                if raw_reward > 0 and raw_reward == int(raw_reward) and self.units_per_coin:
                    reward = raw_reward / self.units_per_coin
                
                new_balance = result.get('new_balance')
                if new_balance is not None:
                    try:
                        nb = float(new_balance)
                        if nb > 0 and nb == int(nb) and self.units_per_coin:
                            nb = nb / self.units_per_coin
                        self.stats.balance = nb
                    except:
                        pass
                else:
                    self.get_balance()
                
                self.stats.last_claim = reward
                self.stats.total_earned += reward
                self.stats.claim_count += 1
                self.stats.success_count += 1
                self.stats.status = "Success"
                self.get_cooldown()
                return True, reward, result.get("mes", "Success")
            else:
                self.stats.fail_count += 1
                self.stats.status = "Failed"
                msg = result.get("mes", "Unknown error")
                
                cd_match = re.search(r'(\d+)\s*minutes?,\s*(\d+)\s*seconds?', msg, re.IGNORECASE)
                if cd_match:
                    mins = int(cd_match.group(1))
                    secs = int(cd_match.group(2))
                    cd = mins * 60 + secs
                    self.stats.cooldown = cd
                    self.stats.cooldown_until = datetime.now() + timedelta(seconds=cd)
                else:
                    cd_match = re.search(r'(\d+)\s*minutes?\s+(\d+)\s*seconds?', msg, re.IGNORECASE)
                    if cd_match:
                        mins = int(cd_match.group(1))
                        secs = int(cd_match.group(2))
                        cd = mins * 60 + secs
                        self.stats.cooldown = cd
                        self.stats.cooldown_until = datetime.now() + timedelta(seconds=cd)
                
                return False, 0.0, msg
        except Exception as e:
            self.stats.fail_count += 1
            self.stats.status = "Error"
            return False, 0.0, f"Exception: {e}"
    
    def run_cycle(self, logs: List[str]) -> Dict:
        result = {
            "name": self.name,
            "currency": self.currency,
            "claimed": False,
            "reward": 0.0,
            "balance": self.stats.balance,
            "message": "",
            "cooldown": 0
        }
        
        if not self.logged_in:
            logs.append(f"🔐 {self.currency} Logging in...")
            if not self.login():
                result["message"] = "Login failed"
                return result
            logs.append(f"✅ {self.currency} Login successful")
        
        self.get_cooldown()
        cooldown = self.stats.cooldown
        if cooldown > 0:
            result["message"] = f"Cooldown {cooldown}s"
            result["cooldown"] = cooldown
            return result
        
        logs.append(f"🎯 {self.currency} Claiming reward...")
        success, reward, msg = self.claim()
        result["claimed"] = success
        result["reward"] = reward
        result["balance"] = self.stats.balance
        result["message"] = msg
        result["cooldown"] = self.stats.cooldown
        
        if success:
            dec = self.decimals
            reward_str = f"{reward:.{dec}f}"
            logs.append(f"💰 {self.currency} Claimed +{reward_str} {self.currency}")
        else:
            logs.append(f"❌ {self.currency} Claim failed: {msg}")
        
        return result

# ========== BOT MANAGER ==========
class PickBotManager:
    def __init__(self, credentials_map: Dict[str, Dict], captcha_config: Dict):
        self.credentials_map = credentials_map
        self.captcha_config = captcha_config
        self.faucets: Dict[str, PickFaucet] = {}
        self.stats = BotStats()
        self.running = True
        self.lock = threading.Lock()
        self.running_sites: List[str] = []
        self._dashboard_lock = threading.Lock()
        
        for site in PICK_SITES:
            creds = credentials_map.get(site["name"], {"email": "", "password": ""})
            if creds.get("email"):
                faucet = PickFaucet(site, creds, captcha_config)
                self.faucets[site["name"]] = faucet
    
    def get_available_sites(self) -> List[str]:
        return list(self.faucets.keys())
    
    def _format_time(self, seconds: int) -> str:
        if seconds <= 0:
            return "READY"
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
    
    def _get_remaining_cooldown(self, faucet: PickFaucet) -> int:
        if faucet.stats.cooldown_until is None:
            return 0
        remaining = (faucet.stats.cooldown_until - datetime.now()).total_seconds()
        return max(0, int(remaining))
    
    def _display_dashboard(self, faucets: List[PickFaucet], wait_seconds: Optional[int] = None):
        with self._dashboard_lock:
            print(f"\n{C}{'='*60}{RESET}")
            print(f"{C}                 ⚡ PICK FAMILY BOT v1.0{RESET}")
            print(f"{C}{'='*60}{RESET}\n")
            
            elapsed = datetime.now() - self.stats.start_time
            hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            run_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            
            for faucet in faucets:
                name_display = faucet.name.replace("Pick", "Pick.io") if "Pick" in faucet.name else faucet.name
                status = "🟢" if faucet.logged_in else "🔴"
                dec = faucet.decimals
                balance = f"{faucet.stats.balance:,.{dec}f}"
                
                print(f"{M}|| 📋 SITE       : {G}{name_display}{RESET}")
                print(f"{M}|| 🔄 STATUS     : {G}{status} {'RUNNING' if self.running else 'STOPPED'}{RESET}")
                print(f"{M}|| ⏱️ RUNTIME    : {G}{run_time}{RESET}")
                print(f"{M}|| 💰 BALANCE    : {G}{balance} {faucet.currency}{RESET}")
                if faucet.stats.last_claim > 0:
                    last = f"{faucet.stats.last_claim:,.{dec}f}"
                    print(f"{M}|| 📈 EARNED     : {G}+{last} {faucet.currency}{RESET}")
                
                cd_remaining = self._get_remaining_cooldown(faucet)
                if cd_remaining > 0:
                    cd_str = self._format_time(cd_remaining)
                    print(f"{M}|| ⏳ COOLDOWN   : {Y}{cd_str}{RESET}")
                else:
                    print(f"{M}|| ⏳ COOLDOWN   : {G}✅ READY{RESET}")
                print()
            
            print(f"{C}{'='*60}{RESET}")
            print(f"{C}                     💎 NETWORK{RESET}")
            print(f"{C}{'='*60}{RESET}\n")
            
            for faucet in faucets:
                status = "🟢" if faucet.logged_in else "🔴"
                name_display = faucet.name.replace("Pick", "Pick.io") if "Pick" in faucet.name else faucet.name
                dec = faucet.decimals
                balance = f"{faucet.stats.balance:,.{dec}f}"
                print(f"{M}|| {status} {name_display}{RESET}")
                print(f"{M}|| 💎 Coin       : {G}{faucet.currency}{RESET}")
                print(f"{M}|| 💰 Balance    : {G}{balance}{RESET}")
                if faucet.stats.last_claim > 0:
                    last = f"{faucet.stats.last_claim:,.{dec}f}"
                    print(f"{M}|| 🎯 Last Claim : {G}+{last}{RESET}")
                cd_remaining = self._get_remaining_cooldown(faucet)
                if cd_remaining > 0:
                    cd_str = self._format_time(cd_remaining)
                    print(f"{M}|| ⏳ Cooldown   : {Y}{cd_str}{RESET}")
                else:
                    print(f"{M}|| ⏳ Cooldown   : {G}READY{RESET}")
                print(f"{M}|| 📊 Claims     : {G}{faucet.stats.claim_count}{RESET}")
                print()
            
            print(f"{C}{'='*60}{RESET}")
            print(f"{C}                     📡 LIVE LOGS{RESET}")
            print(f"{C}{'='*60}{RESET}\n")
            
            logs = self.stats.logs[-6:] if self.stats.logs else ["⏳ Waiting for first claim..."]
            for log in logs:
                print(f"{M}|| {log}{RESET}")
            
            print(f"\n{C}{'='*60}{RESET}")
            print(f"{C}                       📊 STATS{RESET}")
            print(f"{C}{'='*60}{RESET}\n")
            
            success_rate = (self.stats.total_success / max(1, self.stats.total_claims)) * 100
            print(f"{M}|| ✅ Success : {G}{self.stats.total_success}{RESET}")
            print(f"{M}|| ❌ Failed  : {R}{self.stats.total_fail}{RESET}")
            print(f"{M}|| 🎯 Claims  : {G}{self.stats.total_claims}{RESET}")
            print(f"{M}|| ⚡ Rate    : {G}{success_rate:.1f}%{RESET}")
            
            min_cd = min([self._get_remaining_cooldown(f) for f in faucets], default=0)
            if wait_seconds is not None and wait_seconds > 0:
                min_cd = wait_seconds
            
            if min_cd > 0:
                cd_str = self._format_time(min_cd)
                print(f"\n{C}{'='*60}{RESET}")
                print(f"{C}              ⏳ NEXT CLAIM IN {cd_str}{RESET}")
            else:
                print(f"\n{C}{'='*60}{RESET}")
                print(f"{C}              ⏳ NEXT CLAIM IN 00:00 (READY){RESET}")
            print(f"{C}{'='*60}{RESET}")
    
    def _wait_with_dashboard(self, faucets: List[PickFaucet], seconds: int):
        if seconds <= 0:
            return
        
        for f in faucets:
            f.get_cooldown()
        
        start_time = datetime.now()
        while seconds > 0 and self.running:
            elapsed = (datetime.now() - start_time).total_seconds()
            remaining = max(0, int(seconds - elapsed))
            
            for f in faucets:
                if f.stats.cooldown_until is not None:
                    cd_left = (f.stats.cooldown_until - datetime.now()).total_seconds()
                    if cd_left <= 0:
                        f.stats.cooldown_until = None
                        f.stats.cooldown = 0
            
            os.system('clear' if os.name == 'posix' else 'cls')
            self._display_dashboard(faucets, remaining)
            
            if remaining <= 0:
                break
            
            cd_str = self._format_time(remaining)
            sys.stdout.write(f"\r{Y}⏳ Waiting {cd_str} before next cycle...  {RESET}")
            sys.stdout.flush()
            time.sleep(1)
            seconds -= 1
        
        sys.stdout.write("\r" + " " * 60 + "\r")
        sys.stdout.flush()
    
    def run_selected(self, selected: List[str]):
        if not selected:
            print(f"{R}❌ Tidak ada situs dipilih{RESET}")
            return
        
        self.running_sites = selected
        self.stats.start_time = datetime.now()
        
        selected_faucets = []
        for name in selected:
            if name in self.faucets:
                selected_faucets.append(self.faucets[name])
        
        if not selected_faucets:
            print(f"{R}❌ Tidak ada situs valid{RESET}")
            return
        
        print(f"\n{G}🚀 Starting bot for: {', '.join(selected)}{RESET}\n")
        
        for f in selected_faucets:
            f.get_cooldown()
        
        while self.running:
            os.system('clear' if os.name == 'posix' else 'cls')
            self._display_dashboard(selected_faucets)
            
            for faucet in selected_faucets:
                if not self.running:
                    break
                
                logs = []
                result = faucet.run_cycle(logs)
                
                with self.lock:
                    if result["claimed"]:
                        self.stats.total_earned += result["reward"]
                        self.stats.total_claims += 1
                        self.stats.total_success += 1
                    elif result["cooldown"] > 0:
                        self.stats.total_cooldown += 1
                    else:
                        self.stats.total_fail += 1
                    
                    for log in logs:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        self.stats.logs.append(f"{timestamp} {log}")
                        if len(self.stats.logs) > 50:
                            self.stats.logs.pop(0)
                
                os.system('clear' if os.name == 'posix' else 'cls')
                self._display_dashboard(selected_faucets)
                time.sleep(random.uniform(1, 3))
            
            min_cd = min([self._get_remaining_cooldown(f) for f in selected_faucets if self._get_remaining_cooldown(f) > 0], default=0)
            
            if min_cd > 0:
                self._wait_with_dashboard(selected_faucets, min_cd)
            else:
                self._wait_with_dashboard(selected_faucets, 10)
            
            for faucet in selected_faucets:
                faucet.get_cooldown()

# ========== MAIN MENU ==========
def main_menu():
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"\n{C}{'='*60}{RESET}")
        print(f"{C}                 ⚡ PICK FAMILY BOT v1.0{RESET}")
        print(f"{C}{'='*60}{RESET}\n")
        print(f"{M}|| [1] 🚀 RUN PICK BOT{RESET}")
        print(f"{M}|| [2] ⚙️  CONFIGURATION{RESET}")
        print(f"{M}|| [0] ❌ Exit{RESET}")
        print(f"\n{C}{'='*60}{RESET}")
        
        choice = input(f"\n{C}❯ Pilih: {W}").strip()
        if choice == '0':
            print(f"\n{G}👋 Bye!{RESET}")
            sys.exit(0)
        elif choice == '1':
            run_menu()
        elif choice == '2':
            config_menu()
        else:
            print(f"{R}❌ Invalid choice{RESET}")
            time.sleep(1)

def config_menu():
    config = load_or_create_config()
    credentials = config.get("credentials", {})
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"\n{C}{'='*60}{RESET}")
        print(f"{C}                 ⚡ PICK FAMILY BOT{RESET}")
        print(f"{C}{'='*60}{RESET}\n")
        print(f"{C}📋 CONFIGURATION{RESET}\n")
        
        for i, site in enumerate(PICK_SITES, 1):
            cred = credentials.get(site["name"], {})
            email = cred.get("email", "NOT SET")
            status = "✅" if email != "NOT SET" and email else "❌"
            print(f"{M}|| [{i}] {status} {site['name']}: {G}{email}{RESET}")
        
        print(f"{M}|| [8] ▶️ Run selected{RESET}")
        print(f"{M}|| [9] 🔑 Config Apikey{RESET}")
        print(f"{M}|| [0] ↩️ Back{RESET}")
        print(f"\n{C}{'='*60}{RESET}")
        
        choice = input(f"\n{C}❯ Pilih: {W}").strip()
        if choice == '0':
            break
        elif choice == '8':
            run_menu()
            break
        elif choice == '9':
            api_key_menu(config)
        elif choice.isdigit() and 1 <= int(choice) <= 7:
            idx = int(choice) - 1
            site = PICK_SITES[idx]
            edit_credentials(config, site)
        else:
            print(f"{R}❌ Invalid choice{RESET}")
            time.sleep(1)

def edit_credentials(config: Dict, site: Dict):
    name = site["name"]
    creds = config["credentials"].get(name, {})
    
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"\n{C}{'='*60}{RESET}")
    print(f"{C}🔧 Config {name}{RESET}")
    print(f"{C}{'='*60}{RESET}\n")
    print(f"{M}Current email: {G}{creds.get('email', '')}{RESET}")
    email = input(f"{C}Email (kosongkan untuk hapus): {W}").strip()
    if email:
        password = input(f"{C}Password: {W}").strip()
        config["credentials"][name] = {"email": email, "password": password}
        print(f"{G}✅ {name} configured{RESET}")
    else:
        config["credentials"][name] = {"email": "", "password": ""}
        print(f"{Y}⚠️ {name} removed{RESET}")
    save_config(config)
    time.sleep(1)

def api_key_menu(config: Dict):
    captcha = config.get("captcha", {})
    
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"\n{C}{'='*60}{RESET}")
    print(f"{C}🔑 API KEY CONFIG{RESET}")
    print(f"{C}{'='*60}{RESET}\n")
    print(f"{M}Current service: {G}{captcha.get('service', 'manual')}{RESET}")
    print(f"{M}Waryono API Key: {G}{captcha.get('waryono_api_key', '')[:20]}...{RESET}")
    print(f"{M}BypassAll API Key: {G}{captcha.get('bypassall_api_key', '')[:20]}...{RESET}\n")
    print(f"{M}[1] Waryono API Key{RESET}")
    print(f"{M}[2] BypassAll API Key{RESET}")
    print(f"{M}[3] Service: Manual{RESET}")
    print(f"{M}[0] Back{RESET}")
    
    choice = input(f"\n{C}❯ Pilih: {W}").strip()
    if choice == '1':
        key = input(f"{C}Waryono API Key: {W}").strip()
        captcha["waryono_api_key"] = key
        captcha["service"] = "waryono"
        config["captcha"] = captcha
        save_config(config)
        print(f"{G}✅ Updated{RESET}")
    elif choice == '2':
        key = input(f"{C}BypassAll API Key: {W}").strip()
        captcha["bypassall_api_key"] = key
        captcha["service"] = "bypassall"
        config["captcha"] = captcha
        save_config(config)
        print(f"{G}✅ Updated{RESET}")
    elif choice == '3':
        captcha["service"] = "manual"
        config["captcha"] = captcha
        save_config(config)
        print(f"{G}✅ Set to manual{RESET}")
    time.sleep(1)

def run_menu():
    config = load_or_create_config()
    credentials = config.get("credentials", {})
    
    available = []
    for site in PICK_SITES:
        cred = credentials.get(site["name"], {})
        if cred.get("email"):
            available.append(site["name"])
    
    if not available:
        print(f"\n{R}❌ Tidak ada situs dengan credentials. Setup dulu di menu Config.{RESET}")
        input("Press Enter...")
        return
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"\n{C}{'='*60}{RESET}")
        print(f"{C}                 🚀 RUN PICK BOT{RESET}")
        print(f"{C}{'='*60}{RESET}\n")
        
        for i, name in enumerate(available, 1):
            print(f"{M}|| [{i}] Run {name}{RESET}")
        print(f"{M}|| [{len(available)+1}] ALL RUN{RESET}")
        print(f"{M}|| [0] Back{RESET}")
        print(f"\n{C}{'='*60}{RESET}")
        
        choice = input(f"\n{C}❯ Pilih: {W}").strip()
        if choice == '0':
            break
        elif choice == str(len(available) + 1):
            selected = available
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(available):
                    selected = [available[idx]]
                else:
                    print(f"{R}❌ Invalid choice{RESET}")
                    time.sleep(1)
                    continue
            except:
                print(f"{R}❌ Invalid choice{RESET}")
                time.sleep(1)
                continue
        
        captcha_config = config.get("captcha", {"service": "manual"})
        bot = PickBotManager(credentials, captcha_config)
        
        valid_sites = []
        for name in selected:
            if name in bot.faucets:
                valid_sites.append(name)
        
        if not valid_sites:
            print(f"{R}❌ Tidak ada situs valid{RESET}")
            input("Press Enter...")
            continue
        
        try:
            bot.run_selected(valid_sites)
        except KeyboardInterrupt:
            bot.running = False
            print(f"\n{R}👋 Bot stopped{RESET}")
            input("Press Enter...")
            break

def load_or_create_config() -> Dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    config = {
        "captcha": {
            "service": "manual",
            "waryono_api_key": "",
            "bypassall_api_key": ""
        },
        "credentials": {}
    }
    save_config(config)
    return config

def save_config(config: Dict):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{R}👋 Keluar.{RESET}")
        sys.exit(0)
