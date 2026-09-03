#!/usr/bin/env python3
"""
GainLTC Auto Claim Bot - Full Color & Format
Support: count, pattern, sequence, emoji-slider, tap-target, drag-order, connect-pairs
"""

import requests
import time
import json
import sys
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# ========== WARNA ANSI ==========
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GRAY = "\033[90m"

# ========== KONFIGURASI ==========
BASE_URL = "https://gainltc.com"
RUN_HOURS = 8
MAX_CONSECUTIVE_FAILS = 5

# ========== SESSION ==========
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "id-ID,en;q=0.9",
    "Origin": BASE_URL,
    "Referer": f"{BASE_URL}/",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
})

# ========== PRINT FUNCTIONS ==========
def print_header():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}Website : {WHITE}GainLTC.com{RESET}")
    print(f"{BOLD}{CYAN}👨‍💻 ScriptMaker : {WHITE}@JoshuaXSupport{RESET}")
    print(f"{BOLD}{CYAN}📢 TG          : {WHITE}https://t.me/+f3QBLkR5D8k4YzNl{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_info(msg):
    print(f"{BLUE}🚀 [{datetime.now().strftime('%H:%M:%S')}] {BOLD}[INFO]{RESET} {msg}")

def print_ok(msg):
    print(f"{GREEN}✅ [{datetime.now().strftime('%H:%M:%S')}] {BOLD}[ OK ]{RESET} {msg}")

def print_wait(msg):
    print(f"{YELLOW}⏳ [{datetime.now().strftime('%H:%M:%S')}] {BOLD}[WAIT]{RESET} {msg}")

def print_error(msg):
    print(f"{RED}❌ [{datetime.now().strftime('%H:%M:%S')}] {BOLD}[ERR ]{RESET} {msg}")

def print_sep():
    print(f"{GRAY}{'='*60}{RESET}")

# ========== FUNGSI BANTU ==========
def wait_until(target_ts: int):
    now = int(time.time() * 1000)
    if target_ts > now:
        wait_sec = (target_ts - now) / 1000.0
        print_wait(f"Cooldown {wait_sec:.1f} detik")
        time.sleep(wait_sec + 1)

def get_csrf_token() -> Optional[str]:
    try:
        resp = session.get(f"{BASE_URL}/api/csrf-token")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                csrf_cookie = session.cookies.get("csrf_token")
                if csrf_cookie:
                    return csrf_cookie.split(":")[0]
                else:
                    print_error("CSRF token tidak ditemukan di cookie")
                    return None
            else:
                print_error(f"Gagal get CSRF: {data}")
                return None
        else:
            print_error(f"HTTP {resp.status_code} saat get CSRF")
            return None
    except Exception as e:
        print_error(f"Error get CSRF: {e}")
        return None

def generate_captcha() -> Optional[Dict[str, Any]]:
    try:
        resp = session.post(f"{BASE_URL}/api/captcha/generate", json={})
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return data
            else:
                print_error(f"Generate captcha gagal: {data}")
                return None
        else:
            print_error(f"HTTP {resp.status_code} generate captcha")
            return None
    except Exception as e:
        print_error(f"Error generate captcha: {e}")
        return None

def solve_captcha(challenge: Dict[str, Any]) -> List[str]:
    ctype = challenge.get("type")
    if ctype == "count":
        winner = challenge.get("winner")
        if winner:
            return [winner]
        else:
            print_error("Tidak ada winner pada count captcha")
            return []
    
    elif ctype in ("pattern", "sequence"):
        seq = challenge.get("sequence", [])
        null_idx = next((i for i, v in enumerate(seq) if v is None), -1)
        if null_idx == -1:
            print_error("Tidak ada null pada pattern/sequence")
            return []
        non_null = [v for v in seq if v is not None]
        if not non_null:
            return []
        # Cari siklus terkecil
        cycle_len = 1
        found = False
        for cl in range(1, len(non_null) + 1):
            pattern = non_null[:cl]
            ok = True
            for i in range(cl, len(non_null)):
                if non_null[i] != pattern[i % cl]:
                    ok = False
                    break
            if ok:
                cycle_len = cl
                found = True
                break
        if not found:
            cycle_len = len(non_null)
            pattern = non_null
        else:
            pattern = non_null[:cycle_len]
        missing = pattern[null_idx % cycle_len]
        return [missing]
    
    elif ctype == "emoji-slider":
        active = challenge.get("activeEmoji")
        ghosts = challenge.get("ghosts", [])
        for g in ghosts:
            if g.get("emoji") == active:
                return [str(g.get("position"))]
        print_error("Tidak menemukan activeEmoji di ghosts")
        return []
    
    elif ctype == "tap-target":
        target = challenge.get("target")
        taps = challenge.get("tapsRequired", 1)
        if target:
            return [target] * taps
        else:
            print_error("Tidak ada target pada tap-target")
            return []
    
    elif ctype == "drag-order":
        correct = challenge.get("correctOrder")
        if correct:
            return correct
        else:
            print_error("Tidak ada correctOrder pada drag-order")
            return []
    
    elif ctype == "connect-pairs":
        left = challenge.get("leftOrder")
        if left:
            return left
        else:
            print_error("Tidak ada leftOrder pada connect-pairs")
            return []
    
    else:
        print_error(f"Tipe captcha tidak dikenal: {ctype}")
        print_error(f"Challenge structure: {json.dumps(challenge, indent=2)}")
        return []

def verify_captcha(token: str, answer: List[str], ctype: str) -> Optional[str]:
    payload = {
        "token": token,
        "answer": answer,
        "type": ctype
    }
    try:
        resp = session.post(f"{BASE_URL}/api/captcha/verify", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return data.get("verifiedToken")
            else:
                print_error(f"Verify captcha gagal: {data}")
                return None
        else:
            print_error(f"HTTP {resp.status_code} verify captcha")
            return None
    except Exception as e:
        print_error(f"Error verify captcha: {e}")
        return None

def login(email: str, password: str) -> bool:
    print_info("Login...")
    csrf = get_csrf_token()
    if not csrf:
        print_error("Gagal mendapatkan CSRF token")
        return False
    session.headers.update({"X-CSRF-Token": csrf})

    captcha_data = generate_captcha()
    if not captcha_data:
        print_error("Gagal generate captcha")
        return False
    token = captcha_data.get("token")
    challenge = captcha_data.get("challenge")
    if not token or not challenge:
        print_error("Captcha data tidak lengkap")
        return False
    ctype = challenge.get("type", "count")

    answer = solve_captcha(challenge)
    if not answer:
        print_error("Gagal memecahkan captcha")
        return False

    verified = verify_captcha(token, answer, ctype)
    if not verified:
        print_error("Gagal verify captcha")
        return False

    login_payload = {
        "email": email,
        "password": password,
        "captchaToken": verified,
        "rememberMe": True
    }
    try:
        resp = session.post(f"{BASE_URL}/api/auth/login", json=login_payload)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                print_ok("Login berhasil")
                return True
            else:
                print_error(f"Login gagal: {data}")
                return False
        else:
            print_error(f"HTTP {resp.status_code} saat login")
            return False
    except Exception as e:
        print_error(f"Error login: {e}")
        return False

def get_faucet_status() -> Optional[Dict[str, Any]]:
    try:
        resp = session.get(f"{BASE_URL}/api/faucet/status")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("canClaim") is not None:
                return data
            else:
                print_error(f"Status faucet tidak valid: {data}")
                return None
        else:
            print_error(f"HTTP {resp.status_code} get faucet status")
            return None
    except Exception as e:
        print_error(f"Error get faucet status: {e}")
        return None

def claim_faucet() -> Optional[Dict[str, Any]]:
    captcha_data = generate_captcha()
    if not captcha_data:
        print_error("Gagal generate captcha untuk claim")
        return None
    token = captcha_data.get("token")
    challenge = captcha_data.get("challenge")
    if not token or not challenge:
        print_error("Captcha data tidak lengkap untuk claim")
        return None
    ctype = challenge.get("type", "count")

    answer = solve_captcha(challenge)
    if not answer:
        print_error("Gagal memecahkan captcha untuk claim")
        return None

    verified = verify_captcha(token, answer, ctype)
    if not verified:
        print_error("Gagal verify captcha untuk claim")
        return None

    payload = {"captchaToken": verified}
    try:
        resp = session.post(f"{BASE_URL}/api/faucet/claim", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            if "roll" in data and "reward" in data:
                return data
            else:
                print_error(f"Claim response tidak lengkap: {data}")
                return None
        else:
            print_error(f"HTTP {resp.status_code} saat claim")
            return None
    except Exception as e:
        print_error(f"Error claim: {e}")
        return None

# ========== MAIN ==========
def main():
    print_header()

    print_info(f"Target  : {RUN_HOURS} Jam")

    email = input(f"{CYAN}📧 Masukkan email GainLTC Anda: {RESET}").strip()
    if not email:
        print_error("Email tidak boleh kosong. Keluar.")
        sys.exit(1)
    password = input(f"{CYAN}🔑 Masukkan password GainLTC Anda: {RESET}").strip()
    if not password:
        print_error("Password tidak boleh kosong. Keluar.")
        sys.exit(1)

    print_sep()

    if not login(email, password):
        print_error("Login gagal, keluar")
        sys.exit(1)

    print_sep()

    start_time = datetime.now()
    end_time = start_time + timedelta(hours=RUN_HOURS)
    claim_count = 0
    consecutive_fails = 0

    while datetime.now() < end_time:
        status = get_faucet_status()
        if not status:
            print_wait("Gagal mendapatkan status, coba lagi 5 detik")
            time.sleep(5)
            continue

        can_claim = status.get("canClaim", False)
        next_claim_at = status.get("nextClaimAt")

        if not can_claim and next_claim_at:
            wait_until(next_claim_at)
            continue
        elif not can_claim:
            print_wait("Tidak bisa claim dan tidak ada nextClaimAt, tunggu 30 detik")
            time.sleep(30)
            continue

        claim_count += 1
        print_info(f"Claim #{claim_count} dimulai")
        result = claim_faucet()
        if result:
            reward = result.get("reward", 0)
            new_balance = result.get("newBalance", 0)
            next_claim = result.get("nextClaimAt")
            consecutive_fails = 0
            print_ok(f"Reward +{reward}⭐️ | 💳 Balance {new_balance}⭐️")
            if next_claim:
                wait_until(next_claim)
            else:
                print_wait("Tidak ada nextClaimAt, tunggu 10 detik")
                time.sleep(10)
        else:
            consecutive_fails += 1
            print_wait(f"Claim gagal ({consecutive_fails}/{MAX_CONSECUTIVE_FAILS})")
            if consecutive_fails >= MAX_CONSECUTIVE_FAILS:
                print_wait("Terlalu banyak gagal, mencoba re-login...")
                if not login(email, password):
                    print_error("Re-login gagal, keluar")
                    break
                consecutive_fails = 0
            else:
                time.sleep(10)

        # Cek session
        check = get_faucet_status()
        if check is None:
            print_wait("Session mungkin expired, login ulang...")
            if not login(email, password):
                print_error("Login ulang gagal, keluar")
                break

        print_sep()

    print_info(f"Bot selesai setelah {RUN_HOURS} jam. Total claim: {claim_count}")

if __name__ == "__main__":
    main()
