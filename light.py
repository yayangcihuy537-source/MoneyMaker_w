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
BOLD = '\033[1m'

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

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except:
            pass
    return {"apikey": "", "email": "", "password": ""}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

# ========== NETWORK ==========
def http_request(url, payload=None, headers=None, method="POST", cookies=None):
    if headers is None:
        headers = {}
    try:
        if method.upper() == "POST":
            resp = requests.post(url, json=payload, headers=headers, cookies=cookies, timeout=30)
        else:
            resp = requests.get(url, headers=headers, cookies=cookies, timeout=30)

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

    result = http_request(SOLVER_IN, body, headers)
    response = result["body"]

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
        if not self.do_login():
            print(f"{PUTIH}{MERAH}Login gagal. Cek email/password{RESET}")
            return

        me = self.get_me()
        if me:
            print(f"{PUTIH}user: {CYAN}{self.username}{PUTIH} | level: {BIRU}{self.level}{RESET}")

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
            provider = (faucet.get('captchaProvider') or 'turnstile').lower()

            # ══════════ GUARD HCAPTCHA ══════════
            if captcha_required and provider != 'turnstile':
                print()
                print(f"{BOLD}{MERAH}╔══════════════════════════════════════════════════════════╗{RESET}")
                print(f"{BOLD}{MERAH}║          ⚠  HCAPTCHA TERDETEKSI — BOT STOP  ⚠            ║{RESET}")
                print(f"{BOLD}{MERAH}╚══════════════════════════════════════════════════════════╝{RESET}")
                print(f"{KUNING}Provider captcha sekarang : {MERAH}{provider}{RESET}")
                print(f"{KUNING}Bot ini cuma support      : {HIJAU}turnstile{RESET}")
                print()
                print(f"{PUTIH}Coba dulu lu main manual sampe {HIJAU}level 1-9{RESET}, baru naik {KUNING}level 10{RESET}.")
                print(f"{PUTIH}Baru balik lagi ke sini. Kocak kan level lu kelamaan. 🤡{RESET}")
                print()
                print(f"{MERAH}Bot berhenti otomatis. Tekan Ctrl+C buat exit.{RESET}")
                print()
                while True:
                    time.sleep(60)
                return

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

            ch = self.get_challenge()
            if not ch or not ch.get('claimToken'):
                print(f"{PUTIH}[CHALLENGE] {MERAH}{json.dumps(ch) if ch else 'No response'}{RESET}")
                timer(15, "  retry...")
                continue

            claim_token = ch['claimToken']
            min_wait = int(ch.get('minWaitSeconds', 0))
            if min_wait > 0:
                timer(min_wait, "  tunggu readyAt...")

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

            print(f"{PUTIH}[{BIRU}claim/faucet{PUTIH}]{RESET}")
            claim = self.claim_faucet(captcha_token, claim_token)

            if not claim or not claim.get('ok'):
                msg = claim.get('msg', claim.get('message', json.dumps(claim))) if claim else 'No response'
                print(f"{PUTIH}[CLAIM] {MERAH}{msg}{RESET}")
                timer(15, "  retry...")
                continue

            reward = claim.get('reward', {})
            coins = reward.get('coins', 0)
            xp = reward.get('xp', 0)

            print(f"{PUTIH}[CLAIM] {HIJAU}+{coins} coins, +{xp} xp{RESET}")

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

# ========== MENU ==========
def show_banner():
    clear()
    banner = f"""
{BOLD}{CYAN}================================================
              ⚡ LIGHTQUEST ⚡
               AUTO FARM BOT
================================================{RESET}
  {PUTIH}ScriptMaker : {KUNING}MoneyMaker_w
  {PUTIH}Only Level  : {KUNING}10+
  {PUTIH}APIKey      : {CYAN}@ski_control_api_Bot
  {PUTIH}Website     : {KUNING}LightQuest{RESET}
{BOLD}{CYAN}================================================{RESET}
       {HIJAU}💰 AUTO CLAIM  |  📈 XP FARM{RESET}
{BOLD}{CYAN}================================================{RESET}
"""
    print(banner)

def menu_config_email():
    clear()
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║      CONFIG EMAIL & PASSWORD         ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════╝{RESET}")
    cfg = load_config()
    cur_email = cfg.get('email', '')
    cur_pass  = cfg.get('password', '')

    print(f"{PUTIH}Email    [{KUNING}{cur_email or '-'}{PUTIH}] : {KUNING}", end="")
    email = input().strip() or cur_email
    print(f"{PUTIH}Password [{'*' * len(cur_pass) if cur_pass else '-'}] : {KUNING}", end="")
    password = input().strip() or cur_pass

    if not email or not password:
        print(f"{MERAH}Email/Password tidak boleh kosong!{RESET}")
        time.sleep(1.5)
        return

    cfg['email'] = email
    cfg['password'] = password
    save_config(cfg)
    print(f"{HIJAU}✔ Email & Password disimpan!{RESET}")
    time.sleep(1.2)

def menu_config_apikey():
    clear()
    print(f"{BOLD}{CYAN}╔══════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{CYAN}║           CONFIG API KEY             ║{RESET}")
    print(f"{BOLD}{CYAN}╚══════════════════════════════════════╝{RESET}")
    cfg = load_config()
    cur_key = cfg.get('apikey', '')
    masked = (cur_key[:6] + '...' + cur_key[-4:]) if len(cur_key) > 12 else (cur_key or '-')

    print(f"{PUTIH}API Key [{KUNING}{masked}{PUTIH}] : {KUNING}", end="")
    apikey = input().strip() or cur_key

    if not apikey:
        print(f"{MERAH}API Key tidak boleh kosong!{RESET}")
        time.sleep(1.5)
        return

    cfg['apikey'] = apikey
    save_config(cfg)
    print(f"{HIJAU}✔ API Key disimpan!{RESET}")
    time.sleep(1.2)

def menu_start():
    cfg = load_config()
    if not cfg.get('email') or not cfg.get('password'):
        print(f"{MERAH}Email/Password belum di-set! Pilih menu 2 dulu.{RESET}")
        time.sleep(2)
        return
    if not cfg.get('apikey'):
        print(f"{MERAH}API Key belum di-set! Pilih menu 3 dulu.{RESET}")
        time.sleep(2)
        return

    clear()
    bot = LightningBot(cfg)
    try:
        bot.run()
    except KeyboardInterrupt:
        print(f"\n{MERAH}Keluar dari farming.{RESET}")
        time.sleep(1.2)

def main_menu():
    while True:
        show_banner()
        cfg = load_config()
        email_ok = bool(cfg.get('email') and cfg.get('password'))
        key_ok   = bool(cfg.get('apikey'))

        print(f"  {PUTIH}Status Config:{RESET}")
        print(f"    {PUTIH}Email/Pass : {HIJAU + 'OK' if email_ok else MERAH + 'BELUM'}{RESET}")
        print(f"    {PUTIH}API Key    : {HIJAU + 'OK' if key_ok else MERAH + 'BELUM'}{RESET}")
        print()
        print(f"  {CYAN}[1]{RESET} {PUTIH}Start Farming{RESET}")
        print(f"  {CYAN}[2]{RESET} {PUTIH}Config Email & Password{RESET}")
        print(f"  {CYAN}[3]{RESET} {PUTIH}Config API Key{RESET}")
        print(f"  {CYAN}[0]{RESET} {PUTIH}Exit{RESET}")
        print()
        pilih = input(f"{KUNING}▸ Pilih menu : {RESET}").strip()

        if pilih == "1":
            menu_start()
        elif pilih == "2":
            menu_config_email()
        elif pilih == "3":
            menu_config_apikey()
        elif pilih == "0":
            print(f"\n{HIJAU}Sampai jumpa, bos!{RESET}\n")
            sys.exit(0)
        else:
            print(f"{MERAH}Pilihan tidak valid!{RESET}")
            time.sleep(1)

# ========== MAIN ==========
if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(f"\n{MERAH}Keluar.{RESET}")
        sys.exit(0)
