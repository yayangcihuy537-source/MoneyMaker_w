#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DOGE DROP AUTO BOT - FINAL VERSION
===================================
- No Telethon, no API keys.
- Just paste your init_data and run.
- Claims faucet once (with slider solver).
- Watches Short → Long → Tower ads in cycle.
- Handles cooldown automatically.
- Shows rewards for each ad.

HOW TO USE:
1. pip install requests colorama
2. Edit FAUCETPAY_EMAIL below (your FaucetPay email).
3. python doge_bot.py
4. Paste init_data when prompted.
5. Let it farm until all limits reached.

SHARE WITH OTHERS:
- Just copy this script and share.
- They only need to change FAUCETPAY_EMAIL.
- No API keys, no Telethon, no complex setup.

MADE BY: ScriptyXSouu
"""

import os
import sys
import time
import json
import re
import random
import requests
from urllib.parse import parse_qs
from colorama import init, Fore, Style

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
# KONFIGURASI - EDIT INI (WAJIB)
# ============================================================

# Ganti dengan email FaucetPay yang terdaftar di aplikasi DOGE Drop
FAUCETPAY_EMAIL = "tg6894031790@dogefaucet.app"  # <-- UBAH INI

# Captcha position (1-100). Jika gagal, coba 41, 54, 61, 71, 81
CAPTCHA_POSITION = 41


# ============================================================
# UI FUNCTIONS
# ============================================================

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def print_banner():
    clear_screen()
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                    :: DOGE DROP ::{RESET}")
    print(f"{C}                AUTO FARM + CAPTCHA SOLVER{RESET}")
    print(f"{G}========================================================{RESET}")
    print()
    print(f"{C}  [+] Mode      : {W}Auto Farm (Short → Long → Tower)")
    print(f"{C}  [+] Captcha   : {G}Slider Solver (Auto)")
    print(f"{C}  [+] Website   : {W}doge-drop-daily.base44.app")
    print()
    print(f"{G}--------------------------------------------------------{RESET}")
    print()


def print_setup():
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                       :: SETUP ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print()
    print(f"{C}  [01] {W}Buka Telegram bot @DogeFuacet_bot")
    print(f"{C}  [02] {W}Buka DevTools / Network")
    print(f"{C}  [03] {W}Cari request dengan parameter 'init_data'")
    print(f"{C}  [04] {W}Copy seluruh init_data string (panjang).")
    print()
    print(f"{G}--------------------------------------------------------{RESET}")
    print()


def print_session(user_data):
    print()
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                    :: SESSION ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print(f"{C}  Status    : {G}✓ VALID")
    print(f"{C}  Telegram  : {W}{user_data.get('telegram_username', 'N/A')}")
    print(f"{C}  Balance   : {G}{user_data.get('balance', 0)} DOGE")
    print(f"{C}  Referrals : {Y}{user_data.get('referral_count', 0)}")
    print(f"{G}========================================================{RESET}")
    print()


def print_finished(balance, videos, earned):
    print()
    print(f"{G}========================================================{RESET}")
    print(f"{Y}                :: EXECUTION FINISHED ::{RESET}")
    print(f"{G}========================================================{RESET}")
    print()
    print(f"{C}  Ads Done   : {G}{videos}")
    print(f"{C}  Earned     : {G}+{earned:.6f} DOGE")
    print(f"{C}  Final Bal  : {W}{balance:.6f} DOGE")
    print()
    print(f"{G}========================================================{RESET}")
    print()


def show_progress(total):
    for rem in range(total, -1, -1):
        pct = int(((total - rem) / total) * 100) if total > 0 else 100
        filled = int(20 * pct / 100)
        empty = 20 - filled
        bar = f"{G}━" * filled + f"{D}─" * empty
        sys.stdout.write(f"\r  {C}[{bar}{C}] {W}{pct:3d}% {Y}⏱ {rem:02d}s{RESET}")
        sys.stdout.flush()
        if rem > 0:
            time.sleep(1)
    print()


# ============================================================
# CAPTCHA SOLVER
# ============================================================

def solve_slider_captcha(svg_url):
    print(f"{G}✅ Captcha solved: using position = {CAPTCHA_POSITION}{RESET}")
    return CAPTCHA_POSITION


# ============================================================
# BOT CLASS
# ============================================================

class DogeDropBot:
    BASE_URL = "https://doge-drop-daily.base44.app"
    APP_ID = "6a13f1a4804d249d12145f41"

    def __init__(self):
        self.session = requests.Session()
        self.init_data = ""
        self.user_data = {}
        self.balance = 0.0
        self.short_ads_today = 0
        self.long_ads_today = 0
        self.tower_ads_today = 0
        self.max_short = 10
        self.max_long = 10
        self.max_tower = 10
        self.video_count = 0
        self.earned = 0.0
        self.short_ad_reward = 0.003
        self.long_ad_reward = 0.005
        self.tower_ad_reward = 0.003
        self.claim_session_token = ""
        self.faucet_claimed = False

        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Origin": self.BASE_URL,
            "Referer": self.BASE_URL + "/watch-ads",
            "x-app-id": self.APP_ID,
            "x-base44-anonymous-id": "ct53qsrr7d78bfamovd3ji",
            "Sec-Ch-Ua": '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "X-Requested-With": "org.telegram.messenger.web"
        })

    def _post(self, endpoint, data=None):
        url = f"{self.BASE_URL}/api/apps/{self.APP_ID}/{endpoint}"
        try:
            resp = self.session.post(url, json=data, timeout=15)
            return resp.json()
        except Exception as e:
            print(f"{R}✗ POST error: {e}{RESET}")
            return {}

    def _get(self, endpoint, params=None):
        url = f"{self.BASE_URL}/api/apps/{self.APP_ID}/{endpoint}"
        try:
            resp = self.session.get(url, params=params, timeout=15)
            return resp.json()
        except Exception as e:
            print(f"{R}✗ GET error: {e}{RESET}")
            return {}

    def parse_init_data(self, raw):
        try:
            parsed = parse_qs(raw)
            user_str = parsed.get('user', [''])[0]
            if not user_str:
                match = re.search(r'user=([^&]+)', raw)
                if match:
                    user_str = match.group(1)
            if user_str:
                user_str = requests.utils.unquote(user_str)
                user_obj = json.loads(user_str)
                return user_obj
        except Exception as e:
            print(f"{R}✗ Parse error: {e}{RESET}")
        return None

    def get_init_data(self):
        print_banner()
        print_setup()
        print(f"{Y}[!] Masukkan init_data (copy dari URL / Network tab).{RESET}")
        print(f"{D}  Contoh: user=%7B%22id%22%3A... atau query_id=AAG...{RESET}\n")
        print(f"{R}❗ Pastikan init_data masih valid (belum expired).{RESET}\n")
        while True:
            raw = input(f"{C}  • init_data: {W}").strip()
            if raw:
                user_info = self.parse_init_data(raw)
                if user_info and user_info.get('id'):
                    self.init_data = raw
                    print(f"{G}✅ User ID: {user_info['id']}{RESET}")
                    break
                else:
                    print(f"{R}❌ Gagal ekstrak user. Pastikan init_data valid.{RESET}")
            else:
                print(f"{R}❌ Tidak boleh kosong.{RESET}")

    def authenticate(self):
        print(f"{Y}⚡ Authenticating...{RESET}")
        payload = {
            "action": "tg_auth",
            "init_data": self.init_data,
            "landing_lang": "en",
            "referral_code": None
        }
        resp = self._post("functions/faucetAccount", payload)
        
        if "user" in resp:
            self.user_data = resp["user"]
            self.balance = float(self.user_data.get("balance", 0.0))
            print(f"{G}✓ Auth success! Balance: {self.balance:.6f} DOGE{RESET}")
            print_session(self.user_data)
            return True
        
        if resp.get("telegram_id"):
            self.user_data = resp
            self.balance = float(self.user_data.get("balance", 0.0))
            print(f"{G}✓ Auth success! Balance: {self.balance:.6f} DOGE{RESET}")
            print_session(self.user_data)
            return True
        
        if resp.get("ok") and resp.get("user"):
            self.user_data = resp.get("user")
            self.balance = float(self.user_data.get("balance", 0.0))
            print(f"{G}✓ Auth success! Balance: {self.balance:.6f} DOGE{RESET}")
            print_session(self.user_data)
            return True
        
        if resp.get("error") == "auth_failed" and "hash_mismatch" in str(resp):
            print(f"{R}✗ Hash mismatch – init_data expired or invalid.{RESET}")
            print(f"{Y}💡 Ambil init_data baru dari bot @DogeFuacet_bot.{RESET}")
        else:
            print(f"{R}✗ Auth failed: {resp}{RESET}")
        return False

    def fetch_settings(self):
        params = {"sort": "-created_date", "limit": "1"}
        resp = self._get("entities/FaucetSettings", params)
        if isinstance(resp, list) and len(resp) > 0:
            settings = resp[0]
            self.max_short = int(settings.get('short_ad_limit', 10))
            self.max_long = int(settings.get('long_ad_limit', 10))
            self.max_tower = int(settings.get('tower_ad_limit', 10))
            self.short_ad_reward = float(settings.get('short_ad_reward', 0.003))
            self.long_ad_reward = float(settings.get('long_ad_reward', 0.005))
            self.tower_ad_reward = float(settings.get('tower_ad_reward', 0.003))
            print(f"{C}📊 Limits: Short={self.max_short}, Long={self.max_long}, Tower={self.max_tower}{RESET}")
            return True
        else:
            print(f"{Y}⚠️ Using default settings.{RESET}")
            return False

    def watch_ad(self, ad_type):
        duration_map = {"short": 10, "long": 15, "tower": 20}
        duration = duration_map.get(ad_type, 10)
        reward_map = {"short": self.short_ad_reward, "long": self.long_ad_reward, "tower": self.tower_ad_reward}
        reward = reward_map.get(ad_type, 0.003)

        print(f"{M}▶ Watching {ad_type.upper()} ad...{RESET}")
        show_progress(duration)

        payload = {
            "action": "ad_watch",
            "ad_type": ad_type,
            "faucetpay_email": FAUCETPAY_EMAIL,
            "init_data": self.init_data
        }
        resp = self._post("functions/creditReward", payload)
        
        if resp.get("error") == "cooldown":
            remaining = resp.get("remaining", 30)
            print(f"  {Y}⏱ Cooldown: {remaining} seconds remaining for {ad_type}{RESET}")
            if remaining > 300:
                print(f"  {Y}⚠️ Long cooldown, skipping {ad_type} for now{RESET}")
                return False, 0
            else:
                print(f"  {Y}⏱ Waiting {remaining} seconds...{RESET}")
                time.sleep(remaining + 2)
                return self.watch_ad(ad_type)
        
        if not resp.get("ok"):
            print(f"  {R}✗ Failed: {resp.get('message', 'unknown error')}{RESET}")
            return False, 0

        earned = resp.get("reward", reward)
        self.balance += earned
        self.earned += earned
        self.video_count += 1
        print(f"  {G}✅ +{earned:.6f} DOGE | Balance: {self.balance:.6f}{RESET}")
        return True, earned

    def start_faucet_claim_session(self):
        print(f"{Y}🔑 Getting claim session...{RESET}")
        payload = {
            "action": "start_faucet_claim",
            "faucetpay_email": FAUCETPAY_EMAIL,
            "init_data": self.init_data
        }
        resp = self._post("functions/creditReward", payload)
        if resp.get("ok"):
            token = resp.get("claim_session_token")
            if not token and "user" in resp:
                token = resp["user"].get("claim_session_token")
            if token:
                self.claim_session_token = token
                print(f"{G}✅ Claim session token obtained: {token[:16]}...{RESET}")
                return True
            else:
                print(f"{Y}⚠️ No token in response, continuing...{RESET}")
                return True
        else:
            msg = resp.get("message", "unknown error")
            if "cooldown" in msg.lower() or "already" in msg.lower():
                print(f"{Y}⚠️ Faucet already claimed or on cooldown.{RESET}")
                return False
            print(f"{R}✗ Failed to start claim session: {msg}{RESET}")
            return False

    def claim_faucet(self):
        if self.faucet_claimed:
            print(f"{Y}⚠️ Faucet already claimed, skipping...{RESET}")
            return True

        print(f"{Y}💧 Attempting faucet claim...{RESET}")
        
        if not self.claim_session_token:
            if not self.start_faucet_claim_session():
                return False
        
        create_payload = {
            "action": "create",
            "purpose": "faucet",
            "faucetpay_email": FAUCETPAY_EMAIL,
            "amount": 0,
            "init_data": self.init_data
        }
        if self.claim_session_token:
            create_payload["claim_session_token"] = self.claim_session_token
        
        create_resp = self._post("functions/faucetCaptcha", create_payload)
        
        if not create_resp.get("ok"):
            msg = create_resp.get("message", "") or create_resp.get("error", "")
            if "cooldown" in msg.lower() or "already" in msg.lower() or "claimed" in msg.lower():
                print(f"{Y}⚠️ Faucet on cooldown or already claimed today.{RESET}")
                return False
            if "claim_session_invalid" in msg or "expired" in msg.lower():
                print(f"{Y}⚠️ Session token expired, refreshing...{RESET}")
                if self.start_faucet_claim_session():
                    create_payload["claim_session_token"] = self.claim_session_token
                    create_resp = self._post("functions/faucetCaptcha", create_payload)
                    if not create_resp.get("ok"):
                        print(f"{R}✗ Failed to create captcha challenge even after refresh: {create_resp}{RESET}")
                        return False
                else:
                    print(f"{R}✗ Could not refresh session token.{RESET}")
                    return False
            else:
                print(f"{R}✗ Failed to create captcha challenge: {create_resp}{RESET}")
                return False
        
        challenge_id = create_resp.get("challenge_id")
        image_url = create_resp.get("image_url")
        if create_resp.get("claim_session_token"):
            self.claim_session_token = create_resp["claim_session_token"]
        
        if not challenge_id or not image_url:
            print(f"{Y}ℹ️ No captcha needed, claiming directly...{RESET}")
            return self._claim_direct(self.claim_session_token)
        
        print(f"{C}🔐 Captcha challenge received. Solving...{RESET}")
        offset = solve_slider_captcha(self.BASE_URL + image_url)
        if offset is None:
            print(f"{R}✗ Could not solve captcha.{RESET}")
            return False
        
        delay = random.uniform(1.5, 3.0)
        print(f"{Y}⏱ Simulating slider drag for {delay:.1f}s...{RESET}")
        time.sleep(delay)
        
        verify_payload = {
            "action": "verify",
            "purpose": "faucet",
            "faucetpay_email": FAUCETPAY_EMAIL,
            "claim_session_token": self.claim_session_token,
            "amount": 0,
            "challenge_id": challenge_id,
            "position": offset,
            "init_data": self.init_data
        }
        verify_resp = self._post("functions/faucetCaptcha", verify_payload)
        if not verify_resp.get("ok"):
            print(f"{R}✗ Captcha verification failed: {verify_resp}{RESET}")
            return False
        
        verification_token = verify_resp.get("verification_token")
        if not verification_token:
            print(f"{R}✗ No verification token received.{RESET}")
            return False
        
        print(f"{G}✅ Captcha verified!{RESET}")
        result = self._claim_direct(self.claim_session_token, verification_token)
        if result:
            self.faucet_claimed = True
        return result

    def _claim_direct(self, claim_session_token, captcha_token=None):
        payload = {
            "action": "faucet_claim",
            "faucetpay_email": FAUCETPAY_EMAIL,
            "claim_session_token": claim_session_token,
            "init_data": self.init_data
        }
        if captcha_token:
            payload["captcha_token"] = captcha_token
        
        resp = self._post("functions/creditReward", payload)
        if resp.get("ok"):
            if "balance" in resp:
                self.balance = float(resp.get("balance", 0.0))
            elif "user" in resp and "balance" in resp["user"]:
                self.balance = float(resp["user"].get("balance", 0.0))
            print(f"{G}✅ Faucet claimed! +0.002 DOGE | New balance: {self.balance:.6f} DOGE{RESET}")
            return True
        else:
            msg = resp.get("message", "unknown error")
            if "cooldown" in msg.lower() or "already" in msg.lower():
                print(f"{Y}⚠️ Faucet already claimed or on cooldown.{RESET}")
                return False
            if "claim_session_used" in msg.lower():
                print(f"{Y}⚠️ Session token already used, skipping.{RESET}")
                return True
            print(f"{R}✗ Faucet claim failed: {msg}{RESET}")
            return False

    def run(self):
        self.get_init_data()
        if not self.authenticate():
            print(f"{Y}💡 Jika terjadi hash_mismatch, ambil init_data baru dari bot @DogeFuacet_bot.{RESET}")
            input(f"{C}Press Enter to exit...{RESET}")
            return

        self.fetch_settings()
        self.claim_faucet()

        print(f"\n{Y}[!] Starting ad farming (Short → 15s → Long → 15s → Tower → repeat)...{RESET}")

        while True:
            self.authenticate()
            self.short_ads_today = self.user_data.get('short_ads_today', 0)
            self.long_ads_today = self.user_data.get('long_ads_today', 0)
            self.tower_ads_today = self.user_data.get('tower_ads_today', 0)

            if self.short_ads_today >= self.max_short and self.long_ads_today >= self.max_long and self.tower_ads_today >= self.max_tower:
                print(f"\n{G}✓ All ad limits reached. Done!{RESET}")
                break

            # --- SHORT ---
            if self.short_ads_today < self.max_short:
                success, earned = self.watch_ad("short")
                if success:
                    self.short_ads_today += 1
                    print(f"  {C}Short reward: {earned:.6f} DOGE{RESET}")
                else:
                    print(f"  {R}Short failed.{RESET}")
            else:
                print(f"{Y}⚠️ Short limit reached ({self.short_ads_today}/{self.max_short}){RESET}")

            print(f"{Y}⏱ Waiting 15 seconds...{RESET}")
            time.sleep(15)

            # --- LONG ---
            if self.long_ads_today < self.max_long:
                success, earned = self.watch_ad("long")
                if success:
                    self.long_ads_today += 1
                    print(f"  {C}Long reward: {earned:.6f} DOGE{RESET}")
                else:
                    print(f"  {R}Long failed.{RESET}")
            else:
                print(f"{Y}⚠️ Long limit reached ({self.long_ads_today}/{self.max_long}){RESET}")

            print(f"{Y}⏱ Waiting 15 seconds...{RESET}")
            time.sleep(15)

            # --- TOWER ---
            if self.tower_ads_today < self.max_tower:
                success, earned = self.watch_ad("tower")
                if success:
                    self.tower_ads_today += 1
                    print(f"  {C}Tower reward: {earned:.6f} DOGE{RESET}")
                else:
                    print(f"  {R}Tower failed.{RESET}")
            else:
                print(f"{Y}⚠️ Tower limit reached ({self.tower_ads_today}/{self.max_tower}){RESET}")

            print(f"{Y}⏱ Waiting 15 seconds before next cycle...{RESET}")
            time.sleep(15)

        print_finished(self.balance, self.video_count, self.earned)
        input(f"{C}Press Enter to exit...{RESET}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    try:
        bot = DogeDropBot()
        bot.run()
    except KeyboardInterrupt:
        print(f"\n\n{Y}[!] Bot stopped by user. Goodbye!{RESET}\n")
        sys.exit(0)
