#!/usr/bin/env python3
"""
DOGEMINING AUTO CLAIM V2 - BANNER EDITION
- Menu interaktif dengan ASCII art
- Auto login + claim
- Live countdown 60 menit
- Dev: ScriptyXSou | Admin: MoneyMaker
"""

import requests
import re
import json
import time
import hashlib
import sys
import os
from bs4 import BeautifulSoup
from datetime import datetime

BASE_URL = "https://app.dogenetwork.online"
CONFIG_FILE = "config_doge.json"
FINGERPRINT_FILE = "fingerprint.txt"

# ===================== WARNA TERANG =====================
class Colors:
    merah = "\033[91m"
    hijau = "\033[92m"
    kuning = "\033[93m"
    biru = "\033[94m"
    ungu = "\033[95m"
    cyan = "\033[96m"
    putih = "\033[97m"
    bold = "\033[1m"
    reset = "\033[0m"
C = Colors()

# ===================== BANNER MENU =====================
def banner_menu():
    os.system('clear' if os.name != 'nt' else 'cls')
    print(f"""{C.cyan}╔════════════════════════════════════════════════════════════╗{C.reset}
{C.cyan}║                                                            ║{C.reset}
{C.cyan}║   {C.putih}██████╗  ██████╗  ██████╗ ███████╗███╗   ███╗██╗███╗   ██╗ {C.reset}{C.cyan}║{C.reset}
{C.cyan}║   {C.putih}██╔═══██╗██╔════╝ ██╔════╝ ██╔════╝████╗ ████║██║████╗  ██║ {C.reset}{C.cyan}║{C.reset}
{C.cyan}║   {C.putih}██║   ██║██║  ███╗██║  ███╗█████╗  ██╔████╔██║██║██╔██╗ ██║ {C.reset}{C.cyan}║{C.reset}
{C.cyan}║   {C.putih}██║   ██║██║   ██║██║   ██║██╔══╝  ██║╚██╔╝██║██║██║╚██╗██║ {C.reset}{C.cyan}║{C.reset}
{C.cyan}║   {C.putih}╚██████╔╝╚██████╔╝╚██████╔╝███████╗██║ ╚═╝ ██║██║██║ ╚████║ {C.reset}{C.cyan}║{C.reset}
{C.cyan}║   {C.putih} ╚═════╝  ╚═════╝  ╚═════╝ ╚══════╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝ {C.reset}{C.cyan}║{C.reset}
{C.cyan}║                                                            ║{C.reset}
{C.cyan}║              {C.bold}{C.kuning}⚡  A U T O   C L A I M  ⚡{C.reset}{C.cyan}                   ║{C.reset}
{C.cyan}║              {C.putih}LOGIN • CLAIM • BALANCE{C.reset}{C.cyan}                      ║{C.reset}
{C.cyan}╠════════════════════════════════════════════════════════════╣{C.reset}
{C.cyan}║                                                            ║{C.reset}
{C.cyan}║   {C.hijau}[ 1 ] 🚀  START AUTO CLAIM{C.reset}{C.cyan}                               ║{C.reset}
{C.cyan}║   {C.biru}[ 2 ] 💰  CHECK BALANCE{C.reset}{C.cyan}                                  ║{C.reset}
{C.cyan}║   {C.kuning}[ 3 ] ⚙️   SET EMAIL FAUCETPAY{C.reset}{C.cyan}                         ║{C.reset}
{C.cyan}║   {C.merah}[ 0 ] ❌  EXIT{C.reset}{C.cyan}                                           ║{C.reset}
{C.cyan}║                                                            ║{C.reset}
{C.cyan}╠════════════════════════════════════════════════════════════╣{C.reset}
{C.cyan}║   {C.putih}Dev           : {C.kuning}ScriptyXSou{C.reset}{C.cyan}                              ║{C.reset}
{C.cyan}║   {C.putih}AdminSupport  : {C.kuning}MoneyMaker{C.reset}{C.cyan}                               ║{C.reset}
{C.cyan}╚════════════════════════════════════════════════════════════╝{C.reset}
""")

# ===================== BANNER CLAIM =====================
def banner_claim(email, balance, delay_minutes=60):
    os.system('clear' if os.name != 'nt' else 'cls')
    status = f"{C.hijau}● RUNNING{C.reset}"
    print(f"""{C.cyan}╔════════════════════════════════════════════════════════════╗{C.reset}
{C.cyan}║             {C.bold}{C.kuning}🚀 AUTO CLAIM DOGE{C.reset}{C.cyan}                     ║{C.reset}
{C.cyan}╠════════════════════════════════════════════════════════════╣{C.reset}
{C.cyan}║  {C.putih}Account : {C.bold}{C.kuning}{email}{C.reset}{C.cyan}                         ║{C.reset}
{C.cyan}║  {C.putih}Balance : {C.bold}{C.hijau}{balance:.8f} DOGE{C.reset}{C.cyan}              ║{C.reset}
{C.cyan}║  {C.putih}Delay   : {C.bold}{C.cyan}{delay_minutes} minutes{C.reset}{C.cyan}                          ║{C.reset}
{C.cyan}║  {C.putih}Status  : {status}{C.cyan}                                   ║{C.reset}
{C.cyan}╚════════════════════════════════════════════════════════════╝{C.reset}
""")

# ===================== FUNGSI UTAMA =====================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_fingerprint():
    if os.path.exists(FINGERPRINT_FILE):
        with open(FINGERPRINT_FILE, 'r') as f:
            return f.read().strip()
    import platform
    data = f"{platform.node()}-{platform.processor()}-{time.time()}"
    fp = hashlib.sha256(data.encode()).hexdigest()
    with open(FINGERPRINT_FILE, 'w') as f:
        f.write(fp)
    return fp

def create_session():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
    })
    return s

def get_csrf_from_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    meta = soup.find('meta', {'name': 'csrf-token'})
    if meta:
        return meta.get('content')
    inp = soup.find('input', {'name': '_token'})
    if inp:
        return inp.get('value')
    match = re.search(r'X-CSRF-TOKEN["\']?\s*:\s*["\']([^"\']+)', html)
    if match:
        return match.group(1)
    return None

def login(session, email, fingerprint):
    print(f"{C.putih}[*] Login sebagai {email}...{C.reset}")
    resp = session.get(f"{BASE_URL}/register?ref=2953")
    if resp.status_code != 200:
        print(f"{C.merah}[!] Gagal akses halaman register.{C.reset}")
        return False
    csrf = get_csrf_from_page(resp.text)
    if not csrf:
        print(f"{C.merah}[!] CSRF tidak ditemukan.{C.reset}")
        return False
    headers = {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': csrf,
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': BASE_URL,
        'Referer': f"{BASE_URL}/register?ref=2953",
    }
    payload = {"email": email, "fingerprint": fingerprint}
    resp = session.post(f"{BASE_URL}/register", json=payload, headers=headers)
    if resp.status_code != 200:
        return False
    try:
        data = resp.json()
        if data.get('success') and data.get('redirect'):
            session.get(f"{BASE_URL}{data['redirect']}")
            return True
        return False
    except:
        return False

def get_balance(session):
    try:
        resp = session.get(f"{BASE_URL}/dashboard")
        if resp.status_code != 200:
            return None
        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')
        selectors = [
            ('span', {'id': 'account-balance-val'}),
            ('span', {'class': 'header-balance-amount'}),
            ('span', {'id': 'user-account-balance-display'}),
        ]
        for tag, attrs in selectors:
            el = soup.find(tag, attrs)
            if el:
                text = re.sub(r'[^\d.]+', '', el.get_text(strip=True))
                if text:
                    return float(text)
        match = re.search(r'([\d.]+)\s*DOGE', html)
        if match:
            return float(match.group(1))
        return 0.0
    except:
        return 0.0

def get_csrf_cookie(session):
    for cookie in session.cookies:
        if cookie.name == 'XSRF-TOKEN':
            return cookie.value
    return None

def fetch_captcha(session):
    csrf = get_csrf_cookie(session)
    if not csrf:
        return None
    headers = {
        "Accept": "application/json",
        "X-CSRF-TOKEN": csrf,
        "X-Requested-With": "XMLHttpRequest",
        "Referer": f"{BASE_URL}/dashboard",
        "Origin": BASE_URL,
    }
    resp = session.get(f"{BASE_URL}/captcha", headers=headers)
    if resp.status_code == 200:
        try:
            data = resp.json()
            if data.get('success') and 'svg' in data:
                return data['svg']
        except:
            pass
    return None

def parse_svg_captcha(svg):
    soup = BeautifulSoup(svg, 'html.parser')
    digits = []
    for text in soup.find_all('text'):
        content = text.get_text(strip=True)
        if content.isdigit():
            digits.append(content)
    return ''.join(digits)

def do_claim(session, captcha_code):
    csrf = get_csrf_cookie(session)
    if not csrf:
        return None
    payload = {"captcha": captcha_code}
    headers = {
        "Content-Type": "application/json",
        "X-CSRF-TOKEN": csrf,
        "X-Requested-With": "XMLHttpRequest",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/dashboard",
    }
    resp = session.post(f"{BASE_URL}/claim", json=payload, headers=headers)
    if resp.status_code == 200:
        try:
            return resp.json()
        except:
            pass
    return None

def check_session(session):
    resp = session.get(f"{BASE_URL}/dashboard")
    if resp.status_code == 200 and "login" not in resp.url.lower():
        return True
    return False

# ===================== AUTO CLAIM LOOP =====================
def auto_claim_loop(email, fingerprint):
    session = create_session()
    
    # Login
    if not login(session, email, fingerprint):
        print(f"{C.merah}[!] Login gagal.{C.reset}")
        return
    
    if not check_session(session):
        print(f"{C.merah}[!] Session tidak valid.{C.reset}")
        return
    
    # Ambil balance awal
    balance = get_balance(session)
    if balance is None:
        balance = 0.0
    
    claim_count = 0
    delay_seconds = 3600  # 60 menit
    
    while True:
        # Tampilkan banner claim
        banner_claim(email, balance, delay_seconds//60)
        
        # Tampilkan log claim
        print(f"\n{C.cyan}[{datetime.now().strftime('%H:%M:%S')}] {C.bold}{C.kuning}Claim #{claim_count+1}{C.reset}")
        
        # Ambil captcha
        svg = fetch_captcha(session)
        if not svg:
            print(f"{C.merah}[!] Gagal ambil captcha, coba login ulang...{C.reset}")
            if login(session, email, fingerprint):
                svg = fetch_captcha(session)
            if not svg:
                print(f"{C.merah}[!] Tetap gagal, tunggu 30 detik...{C.reset}")
                time.sleep(30)
                continue
        
        # Parse captcha
        captcha = parse_svg_captcha(svg)
        if not captcha or len(captcha) != 4:
            print(f"{C.merah}[!] Captcha tidak valid: {captcha}{C.reset}")
            time.sleep(10)
            continue
        
        print(f"{C.hijau}[+] Captcha solved: {C.bold}{captcha}{C.reset}")
        
        # Claim
        result = do_claim(session, captcha)
        if result and result.get('success'):
            claimed = float(result.get('amount', 0))
            balance = float(result.get('balance', 0))
            print(f"{C.hijau}[✓] Claimed : {C.bold}+{claimed:.8f} DOGE{C.reset}")
            print(f"{C.hijau}[✓] Balance : {C.bold}{balance:.8f} DOGE{C.reset}")
            claim_count += 1
        else:
            msg = result.get('message', 'unknown') if result else 'unknown'
            print(f"{C.merah}[✗] Claim gagal: {msg}{C.reset}")
        
        print(f"\n{C.cyan}──────────────────────────────────────────────────────────────────{C.reset}")
        
        # Countdown 60 menit
        for remaining in range(delay_seconds, 0, -1):
            mins = remaining // 60
            secs = remaining % 60
            sys.stdout.write(f"\r{C.kuning}[⏳] Next claim in {mins:02d}:{secs:02d}...{C.reset}")
            sys.stdout.flush()
            time.sleep(1)
            # Update balance setiap 5 menit
            if remaining % 300 == 0:
                balance = get_balance(session)
                if balance is None:
                    balance = 0.0
                sys.stdout.write(f"\r{C.putih}[🔄] Balance update: {balance:.8f} DOGE     {C.reset}")
                time.sleep(1)
        print()

# ===================== MENU =====================
def main():
    config = load_config()
    email = config.get('email', '')
    fingerprint = get_fingerprint()
    
    while True:
        banner_menu()
        print()
        # Tampilkan email saat ini
        if email:
            print(f"{C.putih}╭─[ {C.bold}{C.kuning}Current Account{C.reset}{C.putih} ]─────────────────────────────────╮{C.reset}")
            print(f"{C.putih}│  {C.kuning}{email}{C.reset}{C.putih}                                      │{C.reset}")
            print(f"{C.putih}╰────────────────────────────────────────────────────────────╯{C.reset}")
        else:
            print(f"{C.putih}╭─[ {C.bold}{C.merah}No Email Set{C.reset}{C.putih} ]─────────────────────────────────╮{C.reset}")
            print(f"{C.putih}│  {C.merah}Please set email via option 3{C.reset}{C.putih}                          │{C.reset}")
            print(f"{C.putih}╰────────────────────────────────────────────────────────────╯{C.reset}")
        print()
        pilihan = input(f"{C.putih}╭─[ {C.bold}{C.cyan}SELECT OPTION{C.reset}{C.putih} ]────────────────────────────────╮{C.reset}\n{C.putih}│  ➜ {C.reset}")
        pilihan = pilihan.strip()
        
        if pilihan == "1":
            if not email:
                print(f"\n{C.merah}[!] Email belum diatur!{C.reset}")
                input(f"{C.putih}Tekan Enter untuk kembali...{C.reset}")
                continue
            auto_claim_loop(email, fingerprint)
            
        elif pilihan == "2":
            print(f"\n{C.putih}[*] Mengecek balance...{C.reset}")
            session = create_session()
            if email:
                if not login(session, email, fingerprint):
                    print(f"{C.merah}[!] Login gagal.{C.reset}")
                    input(f"{C.putih}Tekan Enter untuk kembali...{C.reset}")
                    continue
                balance = get_balance(session)
                if balance is not None:
                    print(f"{C.hijau}[✓] Balance: {C.bold}{balance:.8f} DOGE{C.reset}")
                else:
                    print(f"{C.merah}[!] Gagal ambil balance.{C.reset}")
            else:
                print(f"{C.merah}[!] Email belum diatur.{C.reset}")
            input(f"{C.putih}Tekan Enter untuk kembali...{C.reset}")
            
        elif pilihan == "3":
            print(f"{C.putih}[*] Masukkan email Faucetpay:{C.reset}")
            new_email = input(f"{C.kuning}Email: {C.reset}").strip()
            if new_email:
                config['email'] = new_email
                save_config(config)
                email = new_email
                print(f"{C.hijau}[✓] Email disimpan: {email}{C.reset}")
            else:
                print(f"{C.merah}[!] Email kosong.{C.reset}")
            input(f"{C.putih}Tekan Enter untuk kembali...{C.reset}")
            
        elif pilihan == "0":
            print(f"{C.kuning}[!] Keluar...{C.reset}")
            sys.exit(0)
        else:
            print(f"{C.merah}[!] Pilihan tidak valid.{C.reset}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.kuning}[!] Dihentikan user.{C.reset}")
        sys.exit(0)
    except Exception as e:
        print(f"{C.merah}[!] Error: {e}{C.reset}")
        sys.exit(1)

