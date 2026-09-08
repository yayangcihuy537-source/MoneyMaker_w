#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                  ⚡ LITEPICK.IO AUTO BOT                                  ║
║  🔥 Auto claim faucet with Turnstile captcha                            ║
║  🔐 Sitekey: 0x4AAAAAAA0-UWDHOKP0OrgS                                  ║
║  🎲 Support: Waryono / BypassAll / Manual                              ║
║  💰 Auto balance display & cooldown countdown                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import random
import base64
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple

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
CONFIG_FILE = "litepick_config.json"

# Hardcode sitekey untuk LitePick
SITEKEY = "0x4AAAAAAA0-UWDHOKP0OrgS"

SITE_CONFIG = {
    "name": "LitePick",
    "url": "https://litepick.io",
    "currency": "LTC",
    "faucet_page": "/faucet.php"
}

# ========== DATA CLASS ==========
class LitePickStats:
    def __init__(self):
        self.name = "LitePick"
        self.currency = "LTC"
        self.balance = 0.0
        self.last_claim = 0.0
        self.total_earned = 0.0
        self.claim_count = 0
        self.success_count = 0
        self.fail_count = 0
        self.cooldown = 0
        self.cooldown_until = None
        self.status = "Idle"
        self.last_error = ""
        self.debug_info = ""  # untuk menyimpan debug terakhir

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

# ========== LITEPICK FAUCET ==========
class LitePickFaucet:
    def __init__(self, email: str, password: str, captcha_config: dict):
        self.email = email
        self.password = password
        self.captcha_service = captcha_config.get("service", "manual")
        self.waryono_key = captcha_config.get("waryono_api_key", "")
        self.bypassall_key = captcha_config.get("bypassall_api_key", "")
        
        self.solver = CaptchaSolver()
        self.sitekey = SITEKEY
        self.base_url = SITE_CONFIG["url"]
        self.currency = SITE_CONFIG["currency"]
        self.faucet_page = SITE_CONFIG["faucet_page"]
        
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
        
        self.stats = LitePickStats()
        self.logged_in = False
        self.csrf_token = None
        self.fingerprint = None
        self.decimals = 8
        self.units_per_coin = 100000000
        self.logs = []
        
        # Cache halaman faucet
        self._faucet_page_html = None
        self._faucet_page_fetched_at = None
    
    def _get_csrf_token(self) -> Optional[str]:
        for cookie in self.session.cookies:
            if cookie.name == "csrf_cookie_name":
                return cookie.value
        return None
    
    def _generate_fingerprint(self) -> str:
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
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
    
    def _solve_captcha(self, sitekey: str, action: str = "login") -> Optional[str]:
        """Solve captcha with retry, skip if all fail."""
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
            
            if attempt < max_retries and self.captcha_service != "manual":
                print(f"{Y}⚠️ Solver attempt {attempt} failed, retrying in 3s...{RESET}")
                time.sleep(3)
            elif attempt == max_retries and self.captcha_service != "manual":
                print(f"{Y}⚠️ All {max_retries} solver attempts failed, falling back to manual{RESET}")
            else:
                break
        
        # Fallback to manual input
        if self.captcha_service == "manual" or attempt >= max_retries:
            print(f"{C}🔑 Masukkan token Turnstile untuk LitePick ({action}){RESET}")
            print(f"{Y}Kosongkan untuk skip claim ini{RESET}")
            token = input(f"Token: {W}").strip()
            return token if token else None
        
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
        
        # Debug login response (tapi tidak dicetak ke user)
        try:
            result = resp.json()
            if result.get("ret") == 1:
                self.logged_in = True
                self.stats.status = "Logged In"
                return True
            else:
                self.stats.status = f"Login Failed: {result.get('mes', 'unknown')}"
                return False
        except json.JSONDecodeError:
            preview = re.sub(r"\s+", " ", resp.text[:300])
            self.stats.status = f"Invalid JSON login response: {preview}"
            return False
    
    def _fetch_faucet_page(self) -> bool:
        """Ambil halaman faucet sekali dan cache"""
        resp = self.session.get(f"{self.base_url}{self.faucet_page}")
        if resp.status_code != 200:
            self._faucet_page_html = None
            self._faucet_page_fetched_at = None
            return False
        self._faucet_page_html = resp.text
        self._faucet_page_fetched_at = time.time()
        return True
    
    def get_cooldown_from_html(self, html: str) -> int:
        """Ekstrak cooldown dari HTML tanpa request tambahan"""
        patterns = [
            r'cooldown_remaining["\']?\s*:\s*(\d+)',
            r'data-cooldown["\']?\s*=\s*["\'](\d+)["\']',
            r'next_claim["\']?\s*:\s*(\d+)',
            r'countdown["\']?\s*:\s*(\d+)',
            r'class="cooldown"[^>]*>(\d+)',
            r'id="cooldown"[^>]*>(\d+)',
            r'Wait\s*(\d+)\s*seconds?',
        ]
        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return int(match.group(1))
        return 0
    
    def get_balance_from_html(self, html: str) -> float:
        """Ekstrak balance dari HTML"""
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
        return self.stats.balance
    
    def get_cooldown(self) -> int:
        """Dapatkan cooldown, usahakan dari cache jika masih fresh"""
        # Coba dari cache halaman (valid 5 detik)
        if self._faucet_page_html and self._faucet_page_fetched_at and (time.time() - self._faucet_page_fetched_at) < 5:
            cd = self.get_cooldown_from_html(self._faucet_page_html)
            if cd > 0:
                self.stats.cooldown = cd
                self.stats.cooldown_until = datetime.now() + timedelta(seconds=cd)
                return cd
        
        # Jika cache tidak valid, fetch ulang
        if self._fetch_faucet_page():
            cd = self.get_cooldown_from_html(self._faucet_page_html)
            self.stats.cooldown = cd
            if cd > 0:
                self.stats.cooldown_until = datetime.now() + timedelta(seconds=cd)
            else:
                self.stats.cooldown_until = None
            return cd
        
        # Jika gagal fetch, kembalikan nilai terakhir
        return self.stats.cooldown
    
    def get_balance(self) -> float:
        if self._faucet_page_html:
            bal = self.get_balance_from_html(self._faucet_page_html)
            self.stats.balance = bal
            return bal
        
        if self._fetch_faucet_page():
            bal = self.get_balance_from_html(self._faucet_page_html)
            self.stats.balance = bal
            return bal
        return self.stats.balance
    
    def claim(self) -> Tuple[bool, float, str]:
        if not self.logged_in:
            if not self.login():
                return False, 0.0, "Not logged in"
        
        # Fetch halaman faucet sekali (digunakan untuk cooldown & balance)
        if not self._fetch_faucet_page():
            return False, 0.0, "Failed to load faucet page"
        
        html = self._faucet_page_html
        
        # Ambil CSRF dari cookie
        self.csrf_token = self._get_csrf_token()
        if not self.csrf_token:
            return False, 0.0, "No CSRF token"
        
        # Cek cooldown dari HTML yang sudah di-fetch
        cd = self.get_cooldown_from_html(html)
        if cd > 0:
            self.stats.cooldown = cd
            self.stats.cooldown_until = datetime.now() + timedelta(seconds=cd)
            return False, 0.0, f"Cooldown {cd}s"
        
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
        
        # ========== DEBUG RESPONSE YANG AMAN ==========
        content_type = resp.headers.get("Content-Type", "")
        body = resp.text.strip()
        
        debug_info = (
            f"Status: {resp.status_code} | "
            f"Content-Type: {content_type} | "
            f"Length: {len(body)}"
        )
        self.stats.debug_info = debug_info
        self.logs.append(f"🔍 {debug_info}")
        
        # Jika response kosong
        if not body:
            self.stats.fail_count += 1
            self.stats.status = "Empty Response"
            return False, 0.0, "Server returned empty response"
        
        # Coba parsing JSON
        try:
            result = resp.json()
        except json.JSONDecodeError:
            # Server mengirim HTML atau text bukan JSON
            preview = re.sub(r"\s+", " ", body[:300])
            self.stats.fail_count += 1
            self.stats.status = "Invalid JSON"
            self.logs.append(f"❌ Invalid JSON: {preview}")
            return False, 0.0, (
                f"Invalid JSON | HTTP {resp.status_code} | "
                f"Content-Type: {content_type} | Preview: {preview}"
            )
        
        if not isinstance(result, dict):
            self.stats.fail_count += 1
            self.stats.status = "Invalid JSON Object"
            return False, 0.0, "Server JSON bukan object"
        
        # Proses result JSON
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
            # Update cooldown dari response (jika ada)
            cd_from_resp = result.get('cooldown') or result.get('cooldown_remaining')
            if cd_from_resp is not None:
                try:
                    cd_int = int(cd_from_resp)
                    if cd_int > 0:
                        self.stats.cooldown = cd_int
                        self.stats.cooldown_until = datetime.now() + timedelta(seconds=cd_int)
                except:
                    pass
            return True, reward, result.get("mes", "Success")
        else:
            self.stats.fail_count += 1
            self.stats.status = "Failed"
            msg = result.get("mes", "Unknown error")
            
            # Ekstrak cooldown dari pesan error
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
                else:
                    cd_match = re.search(r'(\d+)\s*seconds?', msg, re.IGNORECASE)
                    if cd_match:
                        cd = int(cd_match.group(1))
                        self.stats.cooldown = cd
                        self.stats.cooldown_until = datetime.now() + timedelta(seconds=cd)
            
            return False, 0.0, msg
    
    def run_cycle(self) -> Dict:
        result = {
            "claimed": False,
            "reward": 0.0,
            "balance": self.stats.balance,
            "message": "",
            "cooldown": 0
        }
        
        if not self.logged_in:
            self.logs.append(f"🔐 Logging in...")
            if not self.login():
                result["message"] = "Login failed"
                return result
            self.logs.append(f"✅ Login successful")
        
        # Get cooldown (gunakan cache jika memungkinkan)
        cooldown = self.get_cooldown()
        if cooldown > 0:
            result["message"] = f"Cooldown {cooldown}s"
            result["cooldown"] = cooldown
            return result
        
        self.logs.append(f"🎯 Claiming reward...")
        success, reward, msg = self.claim()
        result["claimed"] = success
        result["reward"] = reward
        result["balance"] = self.stats.balance
        result["message"] = msg
        result["cooldown"] = self.stats.cooldown
        
        if success:
            dec = self.decimals
            reward_str = f"{reward:.{dec}f}"
            self.logs.append(f"💰 Claimed +{reward_str} LTC")
        else:
            self.logs.append(f"❌ Claim failed: {msg}")
        
        return result

# ========== BOT ==========
class LitePickBot:
    def __init__(self, email: str, password: str, captcha_config: dict):
        self.faucet = LitePickFaucet(email, password, captcha_config)
        self.running = True
    
    def _format_time(self, seconds: int) -> str:
        if seconds <= 0:
            return "READY"
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"
    
    def _display_dashboard(self):
        stats = self.faucet.stats
        dec = self.faucet.decimals
        balance = f"{stats.balance:,.{dec}f}"
        
        cd_remaining = 0
        if stats.cooldown_until:
            cd_remaining = max(0, int((stats.cooldown_until - datetime.now()).total_seconds()))
        
        print(f"\n{C}{'='*60}{RESET}")
        print(f"{C}              ⚡ LITEPICK.IO AUTO BOT{RESET}")
        print(f"{C}{'='*60}{RESET}\n")
        print(f"{M}|| 📋 SITE       : {G}LitePick.io{RESET}")
        print(f"{M}|| 💰 BALANCE    : {G}{balance} LTC{RESET}")
        if stats.last_claim > 0:
            last = f"{stats.last_claim:,.{dec}f}"
            print(f"{M}|| 📈 EARNED     : {G}+{last} LTC{RESET}")
        print(f"{M}|| 🎯 CLAIMS     : {G}{stats.claim_count}{RESET}")
        print(f"{M}|| ✅ SUCCESS    : {G}{stats.success_count}{RESET}")
        print(f"{M}|| ❌ FAILED     : {R}{stats.fail_count}{RESET}")
        if cd_remaining > 0:
            cd_str = self._format_time(cd_remaining)
            print(f"{M}|| ⏳ COOLDOWN   : {Y}{cd_str}{RESET}")
        else:
            print(f"{M}|| ⏳ COOLDOWN   : {G}✅ READY{RESET}")
        
        if stats.debug_info:
            print(f"{M}|| 🐞 DEBUG      : {Y}{stats.debug_info}{RESET}")
        
        if self.faucet.logs:
            print(f"\n{C}{'='*60}{RESET}")
            print(f"{C}                     📡 LIVE LOGS{RESET}")
            print(f"{C}{'='*60}{RESET}\n")
            logs = self.faucet.logs[-5:]
            for log in logs:
                print(f"{M}|| {log}{RESET}")
        
        print(f"\n{C}{'='*60}{RESET}")
        if cd_remaining > 0:
            cd_str = self._format_time(cd_remaining)
            print(f"{C}              ⏳ NEXT CLAIM IN {cd_str}{RESET}")
        else:
            print(f"{C}              ⏳ NEXT CLAIM IN 00:00 (READY){RESET}")
        print(f"{C}{'='*60}{RESET}")
    
    def run(self):
        print(f"\n{G}🚀 Starting LitePick.io Bot...{RESET}\n")
        
        while self.running:
            os.system('clear' if os.name == 'posix' else 'cls')
            self._display_dashboard()
            
            result = self.faucet.run_cycle()
            
            if result["claimed"]:
                dec = self.faucet.decimals
                reward_str = f"{result['reward']:.{dec}f}"
                print(f"\n{G}✅ Claimed +{reward_str} LTC!{RESET}")
            elif result["cooldown"] > 0:
                cd_str = self._format_time(result["cooldown"])
                print(f"\n{Y}⏳ Cooldown {cd_str}{RESET}")
            else:
                print(f"\n{R}❌ {result['message']}{RESET}")
            
            # Refresh display
            time.sleep(2)
            
            # Check cooldown
            cd_remaining = 0
            if self.faucet.stats.cooldown_until:
                cd_remaining = max(0, int((self.faucet.stats.cooldown_until - datetime.now()).total_seconds()))
            
            if cd_remaining > 0:
                for i in range(cd_remaining, 0, -1):
                    if not self.running:
                        break
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self._display_dashboard()
                    cd_str = self._format_time(i)
                    sys.stdout.write(f"\r{Y}⏳ Waiting {cd_str} before next claim...  {RESET}")
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write("\r" + " " * 60 + "\r")
                sys.stdout.flush()
            else:
                time.sleep(5)

# ========== MAIN MENU ==========
def load_or_create_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    
    config = {
        "email": "",
        "password": "",
        "captcha": {
            "service": "manual",
            "waryono_api_key": "",
            "bypassall_api_key": ""
        }
    }
    save_config(config)
    return config

def save_config(config: dict):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def main_menu():
    config = load_or_create_config()
    
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"\n{C}{'='*60}{RESET}")
        print(f"{C}              ⚡ LITEPICK.IO BOT v1.1{RESET}")
        print(f"{C}{'='*60}{RESET}\n")
        print(f"{M}|| [1] 🚀 START BOT{RESET}")
        print(f"{M}|| [2] ⚙️  CONFIGURATION{RESET}")
        print(f"{M}|| [0] ❌ Exit{RESET}")
        print(f"\n{C}{'='*60}{RESET}")
        
        choice = input(f"\n{C}❯ Pilih: {W}").strip()
        if choice == '0':
            print(f"\n{G}👋 Bye!{RESET}")
            sys.exit(0)
        elif choice == '1':
            run_bot(config)
        elif choice == '2':
            config_menu(config)
        else:
            print(f"{R}❌ Invalid choice{RESET}")
            time.sleep(1)

def config_menu(config: dict):
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print(f"\n{C}{'='*60}{RESET}")
        print(f"{C}              ⚙️  CONFIGURATION{RESET}")
        print(f"{C}{'='*60}{RESET}\n")
        print(f"{M}|| Email    : {G}{config.get('email', '')}{RESET}")
        print(f"{M}|| Password : {G}{'*' * len(config.get('password', ''))}{RESET}")
        print(f"{M}|| Captcha  : {G}{config.get('captcha', {}).get('service', 'manual')}{RESET}")
        print(f"\n{M}|| [1] Set Email & Password{RESET}")
        print(f"{M}|| [2] Set Captcha Service{RESET}")
        print(f"{M}|| [3] Set API Keys{RESET}")
        print(f"{M}|| [0] Back{RESET}")
        print(f"\n{C}{'='*60}{RESET}")
        
        choice = input(f"\n{C}❯ Pilih: {W}").strip()
        if choice == '0':
            break
        elif choice == '1':
            email = input(f"{C}Email: {W}").strip()
            password = input(f"{C}Password: {W}").strip()
            if email and password:
                config['email'] = email
                config['password'] = password
                save_config(config)
                print(f"{G}✅ Credentials saved!{RESET}")
            else:
                print(f"{R}❌ Email dan password tidak boleh kosong{RESET}")
            time.sleep(1)
        elif choice == '2':
            print(f"\n{M}[1] Manual{RESET}")
            print(f"{M}[2] Waryono{RESET}")
            print(f"{M}[3] BypassAll{RESET}")
            svc = input(f"{C}Pilih (1-3): {W}").strip()
            if svc == '1':
                config['captcha']['service'] = 'manual'
                print(f"{G}✅ Set to Manual{RESET}")
            elif svc == '2':
                config['captcha']['service'] = 'waryono'
                print(f"{G}✅ Set to Waryono{RESET}")
            elif svc == '3':
                config['captcha']['service'] = 'bypassall'
                print(f"{G}✅ Set to BypassAll{RESET}")
            save_config(config)
            time.sleep(1)
        elif choice == '3':
            print(f"\n{M}Waryono API Key: {G}{config['captcha'].get('waryono_api_key', '')}{RESET}")
            wary = input(f"{C}Waryono API Key: {W}").strip()
            if wary:
                config['captcha']['waryono_api_key'] = wary
            print(f"{M}BypassAll API Key: {G}{config['captcha'].get('bypassall_api_key', '')}{RESET}")
            byp = input(f"{C}BypassAll API Key: {W}").strip()
            if byp:
                config['captcha']['bypassall_api_key'] = byp
            save_config(config)
            print(f"{G}✅ API Keys saved!{RESET}")
            time.sleep(1)

def run_bot(config: dict):
    email = config.get('email', '')
    password = config.get('password', '')
    captcha_config = config.get('captcha', {"service": "manual"})
    
    if not email or not password:
        print(f"\n{R}❌ Email atau password belum di-set!{RESET}")
        print(f"{Y}⚠️ Setup dulu di menu Configuration{RESET}")
        input("Press Enter...")
        return
    
    bot = LitePickBot(email, password, captcha_config)
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.running = False
        print(f"\n{R}👋 Bot stopped{RESET}")
        input("Press Enter...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{R}👋 Keluar.{RESET}")
        sys.exit(0)
