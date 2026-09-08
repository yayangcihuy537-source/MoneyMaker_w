#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import random
import re
import requests
from datetime import datetime

# ========== WARNA ==========
RESET = '\033[0m'
MERAH = '\033[91m'
HIJAU = '\033[92m'
KUNING = '\033[93m'
BIRU = '\033[94m'
CYAN = '\033[96m'
PUTIH = '\033[97m'

# ========== KONFIGURASI ==========
API_URL = "https://lightningquest.net"
CONFIG_FILE = "lightning_config.json"

SITEKEY_TURNSTILE = "0x4AAAAAADxePtT-Imsq_y0B"

# Waryono solver endpoints
SOLVER_IN = "https://api.waryono.my.id/in.php"
SOLVER_OUT = "https://api.waryono.my.id/res.php"

# ========== UTILITY ==========
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def timer(seconds, prefix="[!] please wait"):
    if seconds < 1:
        return
    frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    i = 0
    while seconds > 0:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        time_str = f"{h:02d}:{m:02d}:{s:02d}"
        spinner = frames[i % len(frames)]
        sys.stdout.write(f"\r{PUTIH}{prefix} {HIJAU}{time_str} {PUTIH}{spinner}\033[K")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
        i += 1
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()

def fmt_num(v):
    if v is None:
        return '?'
    if isinstance(v, dict):
        v = v.get('current', v.get('value', '?'))
    if isinstance(v, (int, float)):
        if v >= 1000:
            return f"{v:,.0f}"
        return f"{v:.2f}".rstrip('0').rstrip('.')
    return str(v)

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"apikey": "", "email": "", "password": ""}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_config():
    config = load_config()
    if config.get('apikey') and config.get('email') and config.get('password'):
        return config
    
    print(f"{PUTIH}API Key (captcha) : {KUNING}", end="")
    apikey = input().strip()
    print(f"{PUTIH}Email     : {KUNING}", end="")
    email = input().strip()
    print(f"{PUTIH}Password  : {KUNING}", end="")
    password = input().strip()
    
    config = {"apikey": apikey, "email": email, "password": password}
    save_config(config)
    print(f"{HIJAU}Konfigurasi disimpan ke {CONFIG_FILE}{RESET}")
    time.sleep(1)
    return config

# ========== NETWORK ==========
def http_request(url, payload=None, headers=None, method="POST", cookies=None):
    if headers is None:
        headers = {}
    try:
        if method.upper() == "POST":
            resp = requests.post(url, json=payload, headers=headers, cookies=cookies, timeout=30)
        else:
            resp = requests.get(url, headers=headers, cookies=cookies, timeout=30)
        
        # Update cookies from response
        if resp.cookies:
            if cookies is None:
                cookies = {}
            cookies.update(resp.cookies.get_dict())
        
        return {"body": resp.text, "code": resp.status_code, "cookies": cookies}
    except Exception as e:
        return {"body": str(e), "code": 0, "cookies": cookies}

def solve_captcha(apikey, method, sitekey, action=""):
    """Solve turnstile captcha via Waryono API"""
    headers = {"Content-Type": "application/json"}
    body = {
        "apikey": apikey,
        "methods": method,
        "domain": "https://lightningquest.net",
        "sitekey": sitekey,
        "json": 1
    }
    if action:
        body["action"] = action
        body["cdata"] = ""
    
    # Submit captcha
    result = http_request(SOLVER_IN, body, headers)
    response = result["body"]
    
    # Check errors
    errors = ["ERROR_WRONG_METHOD", "ERROR_KEY_DOES_NOT_EXIST", "ERROR_METHOD_NOT_SPECIFIED",
              "ERROR_NO_SUCH_METHOD", "ERROR_DATABASE_CONNECTION_FAILED", "ERROR_WRONG_USER_KEY",
              "ERROR_ZERO_BALANCE", "ERROR_BAD_PARAMETERS", "ERROR_EMPTY_IMAGE", "ERROR_UNKNOWN"]
    for err in errors:
        if err in response:
            print(f"{PUTIH}Error: {MERAH}{err}{RESET}")
            return None
    
    if "ERROR_TOO_MANY_REQUESTS" in response:
        print(f"{PUTIH}Error: {MERAH}ERROR_TOO_MANY_REQUESTS{RESET}")
        time.sleep(2)
        return solve_captcha(apikey, method, sitekey, action)
    
    try:
        data = json.loads(response)
        task_id = data.get("request")
        if not task_id:
            print(f"{PUTIH}Error: {MERAH}No task id{RESET}")
            return None
    except:
        print(f"{PUTIH}Error: {MERAH}Invalid response{RESET}")
        return None
    
    # Polling result
    max_attempts = 30
    for attempt in range(max_attempts):
        timer(3, f"  {method}... ({attempt+1}/{max_attempts})")
        
        res = http_request(
            f"{SOLVER_OUT}?apikey={apikey}&action=get&id={task_id}&json=1",
            method="GET"
        )
        result = res["body"]
        
        errors_poll = ["ERROR_BAD_PARAMETERS", "Database connection failed"]
        for err in errors_poll:
            if err in result:
                print(f"{PUTIH}Error: {MERAH}{err}{RESET}")
                return None
        
        if "WRONG_CAPTCHA_ID" in result or "ERROR_SOLVE_PENDING" in result:
            print(f"{PUTIH}Error: {MERAH}WRONG_CAPTCHA_ID / PENDING{RESET}")
            time.sleep(1.5)
            return solve_captcha(apikey, method, sitekey, action)
        
        if "CAPCHA_NOT_READY" in result or "CAPTCHA_NOT_READY" in result:
            continue
        
        if "ERROR_CAPTCHA_UNSOLVABLE" in result:
            print(f"{PUTIH}Error: {MERAH}ERROR_CAPTCHA_UNSOLVABLE{RESET}")
            time.sleep(1.5)
            return solve_captcha(apikey, method, sitekey, action)
        
        if "ERROR_BAD_REQUEST" in result or "INTENAL_SERVER_ERROR" in result:
            print(f"{PUTIH}Error: {MERAH}solver error{RESET}")
            time.sleep(1.5)
            return solve_captcha(apikey, method, sitekey, action)
        
        try:
            data = json.loads(result)
            if data.get("status") == 1:
                token = data.get("request")
                if token:
                    return token
        except:
            pass
    
    print(f"{PUTIH}Error: {MERAH}Timeout solving captcha{RESET}")
    return None

# ========== LIGHTNING QUEST BOT ==========
class LightningBot:
    def __init__(self, config):
        self.apikey = config['apikey']
        self.email = config['email']
        self.password = config['password']
        self.access_token = None
        self.cookies = {}
        self.username = None
        self.balance = 0
        self.xp = 0
        self.level = 0
        
    def auth_headers(self):
        headers = {
            'sec-ch-ua': '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
            'sec-ch-ua-platform': '"Android"',
            'sec-ch-ua-mobile': '?1',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36',
            'content-type': 'application/json',
            'accept': '*/*',
            'origin': 'https://lightningquest.net',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://lightningquest.net/faucet',
            'accept-language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
            'priority': 'u=1, i'
        }
        if self.access_token:
            headers['authorization'] = f'Bearer {self.access_token}'
        return headers
    
    def do_login(self):
        print(f"{PUTIH}[LOGIN] {KUNING}Melakukan login...{RESET}")
        body = {
            "email": self.email,
            "password": self.password,
            "trafficExchangeBonus": False
        }
        result = http_request(
            f"{API_URL}/api/auth/login",
            body,
            self.auth_headers(),
            cookies=self.cookies
        )
        
        if result["code"] == 0:
            print(f"{PUTIH}[LOGIN] {MERAH}Connection failed{RESET}")
            return False
        
        try:
            data = json.loads(result["body"])
        except:
            print(f"{PUTIH}[LOGIN] {MERAH}Invalid response{RESET}")
            return False
        
        if data.get('access_token'):
            self.access_token = data['access_token']
            self.username = data.get('user', {}).get('username', self.email)
            print(f"{PUTIH}[LOGIN] {HIJAU}Success! User: {CYAN}{self.username}{RESET}")
            return True
        
        msg = data.get('msg', data.get('message', result["body"]))
        print(f"{PUTIH}[LOGIN] {MERAH}{msg}{RESET}")
        return False
    
    def api_get(self, path):
        result = http_request(
            f"{API_URL}{path}",
            method="GET",
            headers=self.auth_headers(),
            cookies=self.cookies
        )
        
        if result["code"] == 401:
            print(f"{PUTIH}[AUTH] {KUNING}Token expired, login ulang...{RESET}")
            if self.do_login():
                return self.api_get(path)
            return None
        
        try:
            return json.loads(result["body"])
        except:
            return None
    
    def api_post(self, path, payload):
        result = http_request(
            f"{API_URL}{path}",
            payload,
            self.auth_headers(),
            cookies=self.cookies
        )
        
        if result["code"] == 401:
            print(f"{PUTIH}[AUTH] {KUNING}Token expired, login ulang...{RESET}")
            if self.do_login():
                return self.api_post(path, payload)
            return None
        
        try:
            return json.loads(result["body"])
        except:
            return None
    
    def get_me(self):
        data = self.api_get("/api/me")
        if data:
            self.username = data.get('username', self.username)
            self.balance = data.get('balance', self.balance)
            self.xp = data.get('xp', self.xp)
            self.level = data.get('level', self.level)
        return data
    
    def claim_daily(self):
        result = self.api_post("/api/claim/daily", {})
        if result and result.get('ok'):
            reward = result.get('reward', {})
            coins = reward.get('coins', 0)
            xp = reward.get('xp', 0)
            print(f"{PUTIH}[DAILY] {HIJAU}+{coins} coins, +{xp} xp{RESET}")
            return True
        else:
            msg = result.get('msg', result.get('message', 'gagal')) if result else 'no response'
            print(f"{PUTIH}[DAILY] {MERAH}{msg}{RESET}")
            return False
    
    def get_claim_status(self):
        return self.api_get("/api/claim-status")
    
    def get_challenge(self):
        return self.api_get("/api/faucet/challenge")
    
    def claim_faucet(self, captcha_token, claim_token):
        payload = {
            "captchaToken": captcha_token,
            "claimToken": claim_token
        }
        return self.api_post("/api/claim/faucet", payload)
    
    def run(self):
        # Header lama dihapus, sekarang hanya menampilkan user info setelah login
        if not self.do_login():
            print(f"{PUTIH}{MERAH}Login gagal. Cek email/password{RESET}")
            return
        
        # Get user info
        me = self.get_me()
        if me:
            balance = fmt_num(me.get('balance', 0))
            xp = fmt_num(me.get('xp', 0))
            level = fmt_num(me.get('level', 0))
            print(f"{PUTIH}user: {CYAN}{self.username}{PUTIH} | balance: {BIRU}{balance}{PUTIH} | xp: {BIRU}{xp}{PUTIH} | level: {BIRU}{level}{RESET}")
        
        while True:
            print()
            
            status = self.get_claim_status()
            if not status or 'faucet' not in status:
                print(f"{PUTIH}[STATUS] {MERAH}{json.dumps(status) if status else 'No response'}{RESET}")
                timer(30, "  retry...")
                continue
            
            faucet = status['faucet']
            ready = faucet.get('ready', False)
            captcha_required = faucet.get('captchaRequired', False)
            provider = faucet.get('captchaProvider', 'turnstile')
            
            # Daily claim
            daily = status.get('daily', {})
            if daily.get('ready') and daily.get('firstClaim'):
                print(f"{PUTIH}[DAILY] {KUNING}first claim tersedia, claim...{RESET}")
                self.claim_daily()
            
            if not ready:
                next_at = faucet.get('nextAt')
                if next_at:
                    try:
                        dt = datetime.fromisoformat(next_at.replace('Z', '+00:00'))
                        wait = int((dt - datetime.now().astimezone()).total_seconds())
                    except:
                        wait = int(faucet.get('cooldownSeconds', 300))
                else:
                    wait = int(faucet.get('cooldownSeconds', 300))
                if wait < 5:
                    wait = 5
                timer(wait, "  waiting..")
                continue
            
            print(f"{PUTIH}[STATUS] READY | captcha: {BIRU}{'yes(' + provider + ')' if captcha_required else 'no'}{RESET}")
            
            # Get challenge
            ch = self.get_challenge()
            if not ch or not ch.get('claimToken'):
                print(f"{PUTIH}[CHALLENGE] {MERAH}{json.dumps(ch) if ch else 'No response'}{RESET}")
                timer(15, "  retry...")
                continue
            
            claim_token = ch['claimToken']
            min_wait = int(ch.get('minWaitSeconds', 0))
            if min_wait > 0:
                timer(min_wait, "  tunggu readyAt...")
            
            # Solve captcha if required
            captcha_token = ""
            if captcha_required:
                print(f"{PUTIH}[CAPTCHA] {KUNING}Solving turnstile...{RESET}")
                captcha_token = solve_captcha(
                    self.apikey,
                    "turnstile",
                    SITEKEY_TURNSTILE,
                    "faucet-cadence-v1"
                )
                if not captcha_token:
                    print(f"{PUTIH}[CAPTCHA] {MERAH}Failed to solve captcha{RESET}")
                    timer(15, "  retry...")
                    continue
                print(f"{PUTIH}[CAPTCHA] {HIJAU}Solved!{RESET}")
            
            # Claim faucet
            print(f"{PUTIH}[{BIRU}claim/faucet{PUTIH}]{RESET}")
            claim = self.claim_faucet(captcha_token, claim_token)
            
            if not claim or not claim.get('ok'):
                msg = claim.get('msg', claim.get('message', json.dumps(claim))) if claim else 'No response'
                print(f"{PUTIH}[CLAIM] {MERAH}{msg}{RESET}")
                timer(15, "  retry...")
                continue
            
            reward = claim.get('reward', {})
            snapshot = reward.get('snapshot', claim.get('snapshot', {}))
            coins = reward.get('coins', 0)
            xp = reward.get('xp', 0)
            balance = fmt_num(snapshot.get('balance', 0))
            xp_total = fmt_num(snapshot.get('xp', 0))
            level = fmt_num(snapshot.get('level', 0))
            
            print(f"{PUTIH}[CLAIM] {HIJAU}+{coins} coins, +{xp} xp{RESET}")
            print(f"{PUTIH}        balance: {BIRU}{balance}{PUTIH} | xp: {BIRU}{xp_total}{PUTIH} | level: {BIRU}{level}{RESET}")
            
            # Cooldown
            next_at = claim.get('nextAt')
            if next_at:
                try:
                    dt = datetime.fromisoformat(next_at.replace('Z', '+00:00'))
                    cooldown = int((dt - datetime.now().astimezone()).total_seconds())
                except:
                    cooldown = 300
            else:
                cooldown = 300
            
            if cooldown < 5:
                cooldown = 300
            
            timer(cooldown + random.randint(2, 5), "  waiting next claim...")

# ========== MAIN ==========
def main():
    clear()
    banner = """
================================================
              ⚡ LIGHTQUEST ⚡
               AUTO FARM BOT
================================================
  ScriptMaker : MoneyMaker_w
  Only Level  : 10+
  APIKey      : @ski_control_api_Bot
  Website     : LightQuest
================================================
       💰 AUTO CLAIM  |  📈 XP FARM
================================================
"""
    print(banner)
    config = get_config()
    bot = LightningBot(config)
    
    try:
        bot.run()
    except KeyboardInterrupt:
        print(f"\n{MERAH}Keluar.{RESET}")
        sys.exit(0)

if __name__ == "__main__":
    main()
