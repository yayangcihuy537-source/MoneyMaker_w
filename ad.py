#!/usr/bin/env python3
"""
VOLT PTC FARMING - UI KEREN
Dengan username, balance, status, warna, emoji
"""

import requests
import re
import time
import json
import sys
import os
from bs4 import BeautifulSoup

# ======== KONFIGURASI ========
CONFIG_FILE = "config.json"

# ======== WARNA ========
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RED = "\033[91m"
CYAN = "\033[96m"
PURPLE = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"
WHITE = "\033[97m"
MAGENTA = "\033[95m"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(email, api_key):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"email": email, "api_key": api_key}, f, indent=2)

# ======== AMBIL KONFIGURASI ========
config = load_config()
if not config.get("email") or not config.get("api_key"):
    print(f"{YELLOW}[!] Konfigurasi belum diisi.{RESET}")
    email = input(f"{CYAN}Masukkan email FaucetPay: {RESET}").strip()
    api_key = input(f"{CYAN}Masukkan API Key bypassallshortlinks.space: {RESET}").strip()
    save_config(email, api_key)
    config = {"email": email, "api_key": api_key}

EMAIL = config["email"]
API_KEY = config["api_key"]
BASE_URL = "https://adcoins.cc"
API_SOLVER = "https://bypassallshortlinks.space"

# ======== SESSION ========
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": BASE_URL + "/"
})

def login():
    print(f"{BLUE}[*] Login ke AdCoins.cc...{RESET}")
    resp = session.get(BASE_URL + "/")
    if resp.status_code != 200:
        print(f"{RED}[!] Gagal load halaman utama{RESET}")
        return False

    soup = BeautifulSoup(resp.text, "html.parser")
    csrf = soup.find("meta", {"name": "csrf"})
    csrf = csrf.get("content") if csrf else ""

    payload = {"action": "login", "email": EMAIL, "csrf_token": csrf}
    r = session.post(BASE_URL + "/api.php", data=payload)
    try:
        data = r.json()
        if data.get("success"):
            print(f"{GREEN}[+] Login berhasil!{RESET}")
            return True
        else:
            print(f"{RED}[!] Login gagal: {data.get('message', 'Unknown')}{RESET}")
            return False
    except:
        print(f"{RED}[!] Login gagal, status: {r.status_code}{RESET}")
        return False

def get_user_info():
    """Ambil username, balance, status dari dashboard"""
    resp = session.get(BASE_URL + "/dashboard")
    if resp.status_code != 200:
        return None, None, None, None

    soup = BeautifulSoup(resp.text, "html.parser")
    username = None
    balance = None
    total_earned = None
    status = "ACTIVE"

    # Cari username - dari email
    email_tag = soup.find("a", class_="__cf_email__")
    if email_tag:
        username = email_tag.get_text(strip=True)
    else:
        # Alternatif: cari di div dengan class text-white truncate
        for p in soup.find_all("p", class_="text-sm font-medium text-white truncate"):
            text = p.get_text(strip=True)
            if "@" in text:
                username = text
                break

    # Cari balance
    for p in soup.find_all("p", class_=re.compile(r"text-2xl font-bold")):
        text = p.get_text(strip=True)
        if "coins" in text or "coin" in text:
            balance = text.replace("coins", "").strip()
            break

    # Cari total earned
    for p in soup.find_all("p", class_=re.compile(r"text-2xl font-bold text-teal-400")):
        text = p.get_text(strip=True)
        if "coins" in text or "coin" in text:
            total_earned = text.replace("coins", "").strip()
            break

    return username, balance, total_earned, status

def show_menu():
    username, balance, total_earned, status = get_user_info()
    
    # Header
    print(f"\n{WHITE}{'='*62}{RESET}")
    print(f"{BOLD}{CYAN}                    A D S C O I N S{RESET}")
    print(f"{WHITE}{'='*62}{RESET}")
    
    # Info user
    if username:
        print(f"  {GREEN}👤 USER{RESET}      : {YELLOW}{username}{RESET}")
    else:
        print(f"  {GREEN}👤 USER{RESET}      : {YELLOW}Not Logged In{RESET}")
    
    if balance:
        print(f"  {GREEN}💰 BALANCE{RESET}   : {CYAN}{balance}{RESET} Coins")
    else:
        print(f"  {GREEN}💰 BALANCE{RESET}   : {CYAN}0{RESET} Coins")
    
    if total_earned:
        print(f"  {GREEN}🏆 TOTAL{RESET}     : {MAGENTA}{total_earned}{RESET} Coins")
    
    print(f"  {GREEN}⚡ STATUS{RESET}    : {GREEN}{status}{RESET}")
    print(f"{WHITE}{'='*62}{RESET}")
    
    # Menu
    print(f"  {GREEN}[1]{RESET} ▶ START AUTO EARN")
    print(f"  {BLUE}[2]{RESET} ▶ ACCOUNT & APIKEY")
    print(f"  {RED}[0]{RESET} ▶ EXIT")
    print(f"{WHITE}{'='*62}{RESET}")
    print(f"  {BOLD}AdCoins > Select :{RESET} ", end="")
    return input().strip()

# ======== PTC FUNCTIONS ========
def get_internal_ads():
    print(f"{BLUE}[*] Mengambil daftar iklan internal...{RESET}")
    resp = session.get(BASE_URL + "/ptc")
    if resp.status_code != 200:
        print(f"{RED}[!] Gagal mengambil halaman PTC{RESET}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    ads = []
    for btn in soup.find_all("button", attrs={"data-title": True, "data-url": True}):
        parent = btn.find_parent("div", class_="flex items-center justify-between")
        if parent and "opacity-50" in parent.get("class", []):
            continue
        title = btn.get("data-title")
        duration = int(btn.get("data-duration", 0))
        onclick = btn.get("@click") or btn.get("onclick")
        ad_id = None
        if onclick:
            match = re.search(r'viewWindowAd\((\d+)\)', onclick)
            if match:
                ad_id = int(match.group(1))
        if not ad_id:
            ad_id = btn.get("data-ad-id")
        if not ad_id and parent:
            class_attr = parent.get(":class", "")
            match = re.search(r'activeWindowAdId === (\d+)', class_attr)
            if match:
                ad_id = int(match.group(1))
        if ad_id:
            ads.append({"id": ad_id, "title": title, "duration": duration})
    print(f"{GREEN}[+] Ditemukan {len(ads)} iklan internal aktif{RESET}")
    return ads

def create_ptc_view(ad_id):
    payload = {"action": "create_ptc_view", "ad_id": ad_id}
    r = session.post(BASE_URL + "/api.php", data=payload)
    try:
        data = r.json()
        if data.get("success"):
            return data.get("view_id"), data.get("ad_url")
        else:
            return None, None
    except:
        return None, None

def solve_turnstile(sitekey, pageurl):
    submit_url = f"{API_SOLVER}/in.php"
    params = {"key": API_KEY, "method": "turnstile", "sitekey": sitekey, "pageurl": pageurl, "json": 1}
    try:
        r = requests.get(submit_url, params=params, timeout=30)
        if r.status_code != 200:
            return None
        try:
            data = r.json()
            if data.get("status") == 1:
                task_id = data.get("request")
            else:
                return None
        except:
            text = r.text.strip()
            if text.startswith("OK|"):
                task_id = text.split("|")[1]
            else:
                return None
    except:
        return None

    poll_url = f"{API_SOLVER}/res.php"
    for _ in range(40):
        params = {"id": task_id, "key": API_KEY, "json": 1}
        try:
            r = requests.get(poll_url, params=params, timeout=10)
            if r.status_code != 200:
                time.sleep(3)
                continue
            try:
                data = r.json()
                if data.get("status") == 1:
                    return data.get("request")
                elif data.get("status") == 0 and "CAPCHA_NOT_READY" in data.get("request", ""):
                    time.sleep(3)
                    continue
                else:
                    return None
            except:
                text = r.text.strip()
                if text.startswith("OK|"):
                    return text.split("|")[1]
                elif "CAPCHA_NOT_READY" in text:
                    time.sleep(3)
                    continue
                else:
                    return None
        except:
            time.sleep(3)
    return None

def claim_ptc_view(view_id, turnstile_token):
    payload = {"action": "claim_ptc_view", "view_id": view_id, "turnstile_token": turnstile_token}
    r = session.post(BASE_URL + "/api.php", data=payload)
    try:
        data = r.json()
        return data.get("success", False)
    except:
        return False

def start_farming():
    print(f"\n{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}{GREEN}🚀 START AUTO EARN{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    
    if not login():
        return
    ads = get_internal_ads()
    if not ads:
        print(f"{YELLOW}⚠️  Tidak ada iklan internal yang tersedia{RESET}")
        return
    success = 0
    for idx, ad in enumerate(ads, 1):
        print(f"\n{YELLOW}─── {idx}/{len(ads)} ───{RESET}")
        print(f"{BOLD}📌 Memproses:{RESET} {ad['title']}")
        print(f"   ⏱️  Durasi: {ad['duration']}s")
        view_id, _ = create_ptc_view(ad['id'])
        if not view_id:
            print(f"{RED}❌ Gagal create view{RESET}")
            continue
        print(f"{BLUE}⏳ Menunggu {ad['duration']} detik...{RESET}")
        time.sleep(ad['duration'])
        print(f"{BLUE}🔐 Menyelesaikan Turnstile...{RESET}")
        token = solve_turnstile("0x4AAAAAACyaNDdvQo-05xXY", BASE_URL + "/ptc")
        if not token:
            print(f"{RED}❌ Gagal mendapatkan token{RESET}")
            continue
        if claim_ptc_view(view_id, token):
            print(f"{GREEN}✅ Reward diklaim! 🎉{RESET}")
            success += 1
        else:
            print(f"{RED}❌ Claim gagal{RESET}")
        time.sleep(2)
    
    print(f"\n{GREEN}{'='*62}{RESET}")
    print(f"{GREEN}✅ Selesai! Berhasil mengklaim {success} dari {len(ads)} iklan.{RESET}")
    print(f"{GREEN}{'='*62}{RESET}")

def set_account():
    global EMAIL, API_KEY, config
    print(f"\n{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}{BLUE}⚙️  ACCOUNT & APIKEY{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BLUE}📧 Email saat ini: {YELLOW}{EMAIL}{RESET}")
    new_email = input(f"{CYAN}📧 Email baru (kosongkan jika tidak diubah): {RESET}").strip()
    new_api = input(f"{CYAN}🔑 API Key baru (kosongkan jika tidak diubah): {RESET}").strip()
    if new_email:
        EMAIL = new_email
        config["email"] = new_email
    if new_api:
        API_KEY = new_api
        config["api_key"] = new_api
    save_config(EMAIL, API_KEY)
    print(f"{GREEN}✅ Konfigurasi disimpan!{RESET}")

def main():
    while True:
        choice = show_menu()
        if choice == "1":
            start_farming()
        elif choice == "2":
            set_account()
        elif choice == "0":
            print(f"\n{GREEN}👋 Goodbye!{RESET}")
            break
        else:
            print(f"{RED}❌ Pilihan tidak valid{RESET}")
        input(f"\n{CYAN}⌨️  Press Enter untuk kembali ke menu...{RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}⚠️  Dihentikan oleh user.{RESET}")
        sys.exit(0)

