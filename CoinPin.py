#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
# COINPIN.TOP BOT - FAUCET + PTC (FIXED)
# Moneymaker_w Edition
# ============================================================

import requests
import re
import time
import json
import os
import sys
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# ======================= WARNA =======================
GOLD = Fore.YELLOW
LIGHT_GOLD = Fore.LIGHTYELLOW_EX
GREEN = Fore.GREEN
RED = Fore.RED
CYAN = Fore.CYAN
MAGENTA = Fore.MAGENTA
WHITE = Fore.WHITE
YELLOW = Fore.YELLOW
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT

# ======================= KONFIGURASI =======================
BASE_URL = "https://coinpin.top"
CONFIG_FILE = "coinpin_config.json"
OCR_SERVER = "https://ocr-server-82fr.onrender.com/antibot"

# ======================= BANNER =======================
def banner():
    os.system('clear')
    print(f"""{CYAN}
 ██████╗ ██████╗ ██╗███╗   ██╗██████╗ ██╗███╗   ██╗
██╔════╝██╔═══██╗██║████╗  ██║██╔══██╗██║████╗  ██║
██║     ██║   ██║██║██╔██╗ ██║██████╔╝██║██╔██╗ ██║
██║     ██║   ██║██║██║╚██╗██║██╔═══╝ ██║██║╚██╗██║
╚██████╗╚██████╔╝██║██║ ╚████║██║     ██║██║ ╚████║
 ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═══╝
{RESET}

{Fore.YELLOW}╔══════════════════════════════════════════════════════════════╗
║            COINPIN.TOP - FAUCET + PTC BOT                        ║
╠══════════════════════════════════════════════════════════════╣
║  👨‍💻 Developer : {Fore.MAGENTA}Moneymaker_w{Fore.YELLOW}
║  🌐 Website   : {Fore.CYAN}coinpin.top{Fore.YELLOW}
║  🤖 Language  : {Fore.GREEN}Python{Fore.YELLOW}
║  ⚡ Mode      : {Fore.GREEN}Auto Claim + Auto PTC{Fore.YELLOW}
╚══════════════════════════════════════════════════════════════╝
{RESET}
""")
    print()

# ======================= UTILITY =======================
def log_claim(amount, mode="Faucet"):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{LIGHT_GOLD}[{now}] {GREEN}✅ [{mode}] Claimed: {amount} coins!{RESET}")

def log_error(msg, mode="Faucet"):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{LIGHT_GOLD}[{now}] {RED}❌ [{mode}] {msg}{RESET}")

def timer(seconds, prefix="⏳ Please wait"):
    for i in range(seconds, 0, -1):
        sys.stdout.write(f"\r{prefix} {i}s   ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write("\r" + " " * 40 + "\r")

# ============================================================
# FUNGSI LOGIN
# ============================================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def save_config(email, user_agent):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"email": email, "user_agent": user_agent}, f, indent=4)

def get_csrf(session):
    resp = session.get(f"{BASE_URL}/login")
    match = re.search(r'name="csrf_token_name"\s*value="([^"]+)"', resp.text)
    return match.group(1) if match else None

def login(session, email, password):
    csrf = get_csrf(session)
    if not csrf:
        return False
    data = {"email": email, "password": password, "csrf_token_name": csrf}
    resp = session.post(f"{BASE_URL}/auth/login", data=data, allow_redirects=False)
    return resp.status_code == 303

# ============================================================
# 1. FAUCET CLAIM
# ============================================================
def get_claims_left(html):
    match = re.search(r'(\d+)/(\d+)\s*claims left', html, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def extract_antibot_images(html):
    all_images = re.findall(r'data:image/png;base64,([A-Za-z0-9+/=]+)', html)
    if len(all_images) < 4:
        return None
    question_img = all_images[0]
    answer_imgs = all_images[1:4]
    rels = re.findall(r'rel=\\\"(\d+)\\\"', html)
    if not rels:
        rels = re.findall(r'rel="(\d+)"', html)
    if len(rels) < 3:
        return None
    return {
        'question': question_img,
        'answers': answer_imgs[:3],
        'rels': rels[:3]
    }

def solve_antibot(question, answers, rels):
    try:
        payload = {"question": question, "answers": answers, "rels": rels}
        resp = requests.post(OCR_SERVER, json=payload, timeout=60)
        if resp.status_code == 200:
            result = resp.text.strip()
            indexes = [int(x) for x in result.split()]
            ordered = [rels[i-1] for i in indexes if 1 <= i <= len(rels)]
            if ordered:
                return '+' + '+'.join(ordered)
        return None
    except:
        return None

def claim_faucet(session):
    resp = session.get(f"{BASE_URL}/faucet", timeout=30)
    html = resp.text
    if "Daily limit reached" in html:
        log_error("Daily limit reached!", "Faucet")
        return "LIMIT"
    left, total = get_claims_left(html)
    if left is not None and left <= 0:
        log_error("No claims left today!", "Faucet")
        return "LIMIT"
    csrf_match = re.search(r'name="csrf_token_name"\s+id="token"\s+value="([^"]+)"', html)
    token_match = re.search(r'name="token"\s+value="([^"]+)"', html)
    if not csrf_match or not token_match:
        return None
    csrf = csrf_match.group(1)
    token = token_match.group(1)
    antibot = extract_antibot_images(html)
    if not antibot:
        return None
    antibot_value = solve_antibot(antibot['question'], antibot['answers'], antibot['rels'])
    if not antibot_value:
        return None
    post_data = f"antibotlinks={antibot_value}&csrf_token_name={csrf}&token={token}"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/faucet"
    }
    resp2 = session.post(f"{BASE_URL}/faucet/verify", data=post_data, headers=headers, allow_redirects=False, timeout=30)
    if resp2.status_code == 303:
        location = resp2.headers.get('Location', '')
        resp3 = session.get(location, timeout=30)
        if 'Good job' in resp3.text and 'has been added' in resp3.text:
            reward = re.search(r'(\d+)\s+coins\s+has been added', resp3.text, re.IGNORECASE)
            if reward:
                return reward.group(1)
            return "success"
    return None

def run_faucet(session, max_claims=999):
    print(f"\n{GREEN}▶ STARTING FAUCET (until limit){RESET}")
    claimed = 0
    while claimed < max_claims:
        result = claim_faucet(session)
        if result == "LIMIT":
            log_error("Faucet limit reached, stopping.", "Faucet")
            break
        elif result:
            claimed += 1
            log_claim(result, "Faucet")
            time.sleep(15)
        else:
            log_error("Claim failed, retrying...", "Faucet")
            time.sleep(5)
    print(f"{GREEN}✅ Faucet finished. Total claims: {claimed}{RESET}")

# ============================================================
# 2. PTC CLAIM (FIXED - berdasarkan ptc_debug.html)
# ============================================================
def ptc_fetch_ads(session):
    url = f"{BASE_URL}/ptc"
    headers = {
        "User-Agent": session.headers.get('User-Agent', 'Mozilla/5.0'),
        "Referer": f"{BASE_URL}/dashboard"
    }
    resp = session.get(url, headers=headers, timeout=30)
    html = resp.text
    if not html or "Just a moment" in html:
        return []

    ads = []
    
    # Ekstrak ID dari onclick tombol "Go"
    link_matches = re.findall(r"window\.location\s*=\s*'https?://coinpin\.top/ptc/view/(\d+)'", html)
    if not link_matches:
        # fallback: cari href
        link_matches = re.findall(r'href="https?://coinpin\.top/ptc/view/(\d+)"', html)

    # Ekstrak judul dari <h5 class="card-title">
    title_matches = re.findall(r'<h5 class="card-title[^"]*">(.*?)</h5>', html, re.DOTALL)

    # Ekstrak koin dari <i class="fas fa-gift"></i>: 2100.000000 coins
    coin_matches = re.findall(r'<i class="fas fa-gift"[^>]*></i>:\s*([\d,.]+)\s+coins', html)

    # Ekstrak waktu dari <i class="fas fa-stopwatch"></i>: 10 seconds
    time_matches = re.findall(r'<i class="fas fa-stopwatch"[^>]*></i>:\s*(\d+)\s+seconds', html)

    for i in range(len(link_matches)):
        ads.append({
            'id': link_matches[i],
            'title': title_matches[i].strip() if i < len(title_matches) else f'Ad {i+1}',
            'coins': coin_matches[i].strip() if i < len(coin_matches) else '0',
            'time': int(time_matches[i]) if i < len(time_matches) else 10
        })

    return ads

def ptc_claim_ad(session, ad):
    view_url = f"{BASE_URL}/ptc/view/{ad['id']}"
    
    # STEP 1: Buka halaman view
    headers_get = {
        "User-Agent": session.headers.get('User-Agent', 'Mozilla/5.0'),
        "Referer": f"{BASE_URL}/ptc"
    }
    try:
        resp = session.get(view_url, headers=headers_get, timeout=30)
        html = resp.text
    except:
        return "FAILED"

    if not html:
        return "FAILED"
    if "Just a moment" in html:
        return "CLOUDFLARE"
    if "Already Claimed" in html or "already claimed" in html or "already viewed" in html:
        return "CLAIMED"
    if "view-ads" in html or "Complete the captcha" in html:
        return "SHORTLINK"

    # STEP 2: Ekstrak csrf & token
    csrf_match = re.search(r'name="csrf_token_name".*?value="([^"]+)"', html)
    token_match = re.search(r'name="token".*?value="([^"]+)"', html)
    if not csrf_match or not token_match:
        csrf_match = re.search(r'csrf_token_name" value="([^"]+)"', html)
        token_match = re.search(r'token" value="([^"]+)"', html)
    if not csrf_match or not token_match:
        return "NO_TOKEN"
    csrf = csrf_match.group(1)
    token = token_match.group(1)

    # STEP 3: Tunggu waktu
    wait_time = ad['time']
    print(f"{LIGHT_GOLD}⏳ Waiting {wait_time}s for PTC...{RESET}")
    timer(wait_time, "⏳ PTC wait")

    # STEP 4: POST verify
    verify_url = f"{BASE_URL}/ptc/verify/{ad['id']}"
    post_data = {
        'csrf_token_name': csrf,
        'token': token
    }
    headers_post = {
        "User-Agent": session.headers.get('User-Agent', 'Mozilla/5.0'),
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": BASE_URL,
        "Referer": view_url
    }
    try:
        result = session.post(verify_url, data=post_data, headers=headers_post, timeout=30).text
    except:
        return "FAILED"

    if not result:
        return "FAILED"
    if "Just a moment" in result:
        return "CLOUDFLARE"

    # STEP 5: Cek hasil
    if re.search(r"title:\s*'Good job!',\s*text:\s*'([^']+)'", result, re.IGNORECASE):
        match = re.search(r"Good job!',\s*'([^']+)'", result, re.IGNORECASE)
        if match:
            return {"success": match.group(1)}
    if re.search(r"Swal\.fire\('Good job!',\s*'([^']+)'", result, re.IGNORECASE):
        match = re.search(r"Swal\.fire\('Good job!',\s*'([^']+)'", result, re.IGNORECASE)
        if match:
            return {"success": match.group(1)}

    fail_match = re.search(r'alert-danger">.*?</i>\s*([^<]+)', result, re.IGNORECASE | re.DOTALL)
    if fail_match:
        return {"failed": fail_match.group(1).strip()}

    if "Successfully" in result or "successfully" in result:
        return {"success": "PTC claim berhasil!"}
    if "Invalid Click" in result:
        return "INVALID_CLICK"
    if "Good job" in result or "has been added" in result:
        return {"success": "PTC claim success!"}

    return None

def run_ptc(session, max_cycles=5):
    print(f"\n{GREEN}▶ STARTING PTC (max {max_cycles} cycles){RESET}")
    cycle = 0
    while cycle < max_cycles:
        cycle += 1
        print(f"\n{CYAN}━━━ PTC CYCLE #{cycle} ━━━{RESET}")
        ads = ptc_fetch_ads(session)
        if not ads:
            log_error("Tidak ada PTC ads tersedia!", "PTC")
            timer(30)
            continue
        print(f"{WHITE}Ditemukan {GREEN}{len(ads)}{WHITE} PTC ads")
        for ad in ads:
            print(f"\n[PTC] {CYAN}{ad['title']}{WHITE} ({GREEN}{ad['coins']} coins{WHITE})")
            result = ptc_claim_ad(session, ad)
            if result == "CLOUDFLARE":
                log_error("Cloudflare! Skip...", "PTC")
                time.sleep(3)
            elif result == "CLAIMED":
                print(f"{GOLD}⏳ Already claimed{RESET}")
            elif result == "SHORTLINK":
                print(f"{GOLD}🔗 Shortlink/captcha, skip...{RESET}")
            elif result == "NO_TOKEN":
                log_error("Failed to extract token!", "PTC")
            elif result == "INVALID_CLICK":
                log_error("Invalid Click, retry later...", "PTC")
            elif isinstance(result, dict):
                if "success" in result:
                    print(f"{GREEN}✅ {result['success']}{RESET}")
                elif "failed" in result:
                    log_error(result['failed'], "PTC")
            else:
                log_error("Unknown response", "PTC")
            time.sleep(2)
        if cycle < max_cycles:
            print(f"\n{WHITE}✅ Siklus {cycle} selesai. Menunggu 30s...{RESET}")
            timer(30)
    print(f"{GREEN}✅ PTC finished. Total cycles: {cycle}{RESET}")

# ============================================================
# MENU UTAMA
# ============================================================
def main():
    banner()
    config = load_config()
    if config and config.get('email') and config.get('user_agent'):
        email = config['email']
        user_agent = config['user_agent']
        print(f"{LIGHT_GOLD}📧 Using saved email: {WHITE}{email}{RESET}")
        print(f"{LIGHT_GOLD}🌐 Using saved User-Agent: {WHITE}{user_agent[:50]}...{RESET}")
        use_saved = input(f"{LIGHT_GOLD}Use saved? (y/n): {RESET}").lower()
        if use_saved != 'y':
            email = input(f"{LIGHT_GOLD}📧 Email: {RESET}").strip()
            user_agent = input(f"{LIGHT_GOLD}🌐 User-Agent: {RESET}").strip()
            save_config(email, user_agent)
    else:
        email = input(f"{LIGHT_GOLD}📧 Email: {RESET}").strip()
        user_agent = input(f"{LIGHT_GOLD}🌐 User-Agent: {RESET}").strip()
        save_config(email, user_agent)
    password = input(f"{LIGHT_GOLD}🔑 Password: {RESET}").strip()

    session = requests.Session()
    session.headers.update({
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "X-Requested-With": "mark.via.gp",
    })
    if not login(session, email, password):
        log_error("Login failed!", "System")
        return

    while True:
        banner()
        print(f"{WHITE}╔════════════════════════════════════════════╗")
        print(f"{WHITE}║  {GREEN}[1]{WHITE} Claim Faucet     ║")
        print(f"{WHITE}║  {CYAN}[2]{WHITE} Claim PTC         ║")
        print(f"{WHITE}║  {MAGENTA}[3]{WHITE} ALL            ║")
        print(f"{WHITE}║  {RED}[0]{WHITE} Exit                              ║")
        print(f"{WHITE}╚════════════════════════════════════════════╝{RESET}")
        choice = input(f"\n{GOLD}❯ Pilih: {RESET}").strip()

        if choice == '0':
            print(f"{RED}👋 Bye!{RESET}")
            sys.exit(0)
        elif choice == '1':
            run_faucet(session, max_claims=999)
        elif choice == '2':
            run_ptc(session, max_cycles=5)
        elif choice == '3':
            print(f"{GREEN}Mode ALL: Faucet → PTC → Faucet → PTC ...{RESET}")
            while True:
                run_faucet(session, max_claims=999)
                run_ptc(session, max_cycles=5)
                print(f"{GOLD}↻ Siklus ALL selesai, mulai ulang...{RESET}")
                time.sleep(10)
        else:
            print(f"{RED}❌ Invalid choice!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}👋 Exited by user{RESET}")
        sys.exit(0)
