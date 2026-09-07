#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import urllib.parse
import time
import sys

# Warna ANSI
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'

# =============================================================
#                  🌙 SLEEPY MINE 🌙
# =============================================================
#                     ⛏️ SLEEPY MINE
#                  💎 AUTO MINING BOT 💎
# =============================================================
# 🤖 BOT   : @MineSLPYBot
# 🔗 REF   : ref743382203
# 🚀 START : t.me/MineSLPYBot?startapp=ref743382203
# =============================================================
#                     HAPPY MINING 🚀
# =============================================================
# ScriptMaker : @MoneyMaker_w
# TG          : https://t.me/ScriptyXSouu
# =============================================================

API_URL = "https://sleepymine.xyz/api/db.php"

# Konfigurasi
MAX_REGULAR_ADS = 500      # Iklan biasa
MAX_TADDY_ADS = 250        # Iklan Taddy (0.25 SLPY each)
AD_DELAY = 3               # Jeda antar iklan (detik)

def parse_init_data(init_data: str):
    params = urllib.parse.parse_qs(init_data)
    user_json = params.get('user', [None])[0]
    if not user_json:
        raise ValueError("user parameter not found in init_data")
    user_data = json.loads(user_json)
    uid = str(user_data.get('id'))
    return uid

def db_request(payload, init_data):
    headers = {
        'Content-Type': 'application/json',
        'x-telegram-init-data': init_data
    }
    resp = requests.post(API_URL, json=payload, headers=headers)
    if resp.status_code != 200:
        print(f"{RED}Error {resp.status_code}: {resp.text}{RESET}")
    resp.raise_for_status()
    return resp.json()

def get_user(uid, init_data):
    payload = {
        "table": "airdrop_users",
        "action": "select",
        "select": "*",
        "filters": [{"col": "uid", "op": "eq", "val": uid}],
        "order": None,
        "limit": None,
        "single": True,
        "payload": None
    }
    result = db_request(payload, init_data)
    return result.get('data')

def claim_mined(uid, init_data):
    for fn in ['claim_mined', 'claim', 'claim_reward']:
        payload = {
            "action": "rpc",
            "fn": fn,
            "args": {"uid": uid}
        }
        try:
            result = db_request(payload, init_data)
            if result and result.get('data') and result['data'].get('success'):
                return result['data']
        except Exception:
            continue
    return None

def watch_regular_ad(uid, init_data):
    # Iklan biasa
    fn_list = ['credit_ad_reward', 'credit_ad', 'watch_ad']
    for fn in fn_list:
        payload = {
            "action": "rpc",
            "fn": fn,
            "args": {"uid": uid}
        }
        try:
            result = db_request(payload, init_data)
            if result and result.get('data') and result['data'].get('success'):
                return result['data']
        except Exception:
            continue
    return None

def watch_taddy_ad(uid, init_data):
    # Iklan Taddy (0.25 SLPY)
    fn_list = ['credit_taddy_reward', 'taddy_ad_reward', 'credit_taddy_ad', 'watch_taddy_ad']
    for fn in fn_list:
        payload = {
            "action": "rpc",
            "fn": fn,
            "args": {"uid": uid}
        }
        try:
            result = db_request(payload, init_data)
            if result and result.get('data') and result['data'].get('success'):
                return result['data']
        except Exception:
            continue
    return None

def print_banner():
    print(f"{CYAN}=" * 60)
    print(f"{CYAN}                 🌙 SLEEPY MINE 🌙")
    print(f"{CYAN}=" * 60)
    print()
    print(f"{YELLOW}                    ⛏️ SLEEPY MINE")
    print(f"{YELLOW}                 💎 AUTO MINING BOT 💎")
    print()
    print(f"{CYAN}=" * 60)
    print(f"{GREEN}🤖 BOT   : @MineSLPYBot")
    print(f"{GREEN}🔗 REF   : ref6894031790")
    print(f"{GREEN}🚀 START : t.me/MineSLPYBot?startapp=ref6894031790")
    print(f"{CYAN}=" * 60)
    print(f"{BOLD}                    HAPPY MINING 🚀{RESET}")
    print(f"{CYAN}=" * 60)
    print(f"{GREEN}ScriptMaker : @MoneyMaker_w")
    print(f"{GREEN}TG          : https://t.me/ScriptyXSouu{RESET}")
    print(f"{CYAN}=" * 60)

def main():
    print_banner()
    
    init_data = input(f"\n{YELLOW}Masukkan init_data (dari Telegram WebApp): {RESET}").strip()
    if not init_data:
        print(f"{RED}Init_data tidak boleh kosong!{RESET}")
        sys.exit(1)
    
    try:
        uid = parse_init_data(init_data)
        print(f"{GREEN}UID terdeteksi: {uid}{RESET}")
    except Exception as e:
        print(f"{RED}Gagal parse init_data: {e}{RESET}")
        sys.exit(1)
    
    print(f"\n{CYAN}[1] Mengambil data user...{RESET}")
    user = get_user(uid, init_data)
    if not user:
        print(f"{RED}Gagal mendapatkan data user.{RESET}")
        sys.exit(1)
    print(f"Nama: {user.get('name')}")
    print(f"Points: {user.get('points')}")
    print(f"Unclaimed Mined: {user.get('unclaimed_mined')}")
    print(f"Ads watched (regular): {user.get('ads_watched_count')}")
    print(f"Taddy ads watched: {user.get('taddy_watched_count')}")
    
    # Claim mined jika ada
    if user.get('unclaimed_mined', 0) > 0:
        print(f"\n{CYAN}[2] Melakukan claim mined...{RESET}")
        claim_result = claim_mined(uid, init_data)
        if claim_result and claim_result.get('success'):
            print(f"{GREEN}Claim berhasil!{RESET}")
            user = get_user(uid, init_data)
            print(f"Points sekarang: {user.get('points')}")
        else:
            print(f"{RED}Claim gagal atau tidak ada yang bisa di-claim.{RESET}")
    else:
        print(f"\n{YELLOW}[2] Tidak ada unclaimed mined, lewati claim.{RESET}")
    
    # ---- TADDY ADS ----
    print(f"\n{CYAN}[3a] Mulai menonton TADDY ADS (0.25 SLPY each, max {MAX_TADDY_ADS}/hari)...{RESET}")
    taddy_count = 0
    while taddy_count < MAX_TADDY_ADS:
        ad_result = watch_taddy_ad(uid, init_data)
        if not ad_result or not ad_result.get('success'):
            print(f"{YELLOW}Taddy ads habis atau error, lanjut ke iklan biasa.{RESET}")
            break
        
        taddy_count = ad_result.get('count', 0)
        reward = ad_result.get('reward', 0)
        points = ad_result.get('points', 0)
        print(f"{GREEN}Taddy ke-{taddy_count}: +{reward} SLPY, total points: {points}{RESET}")
        
        if taddy_count >= MAX_TADDY_ADS:
            print(f"{YELLOW}Sudah mencapai batas {MAX_TADDY_ADS} Taddy ads hari ini.{RESET}")
            break
        
        time.sleep(AD_DELAY)  # jeda 3 detik
    
    # ---- REGULAR ADS ----
    print(f"\n{CYAN}[3b] Mulai menonton REGULAR ADS (max {MAX_REGULAR_ADS}/hari)...{RESET}")
    regular_count = 0
    while regular_count < MAX_REGULAR_ADS:
        ad_result = watch_regular_ad(uid, init_data)
        if not ad_result or not ad_result.get('success'):
            print(f"{YELLOW}Regular ads habis atau error, berhenti.{RESET}")
            break
        
        regular_count = ad_result.get('count', 0)
        reward = ad_result.get('reward', 0)
        points = ad_result.get('points', 0)
        print(f"{GREEN}Regular ke-{regular_count}: +{reward} SLPY, total points: {points}{RESET}")
        
        if regular_count >= MAX_REGULAR_ADS:
            print(f"{YELLOW}Sudah mencapai batas {MAX_REGULAR_ADS} regular ads hari ini.{RESET}")
            break
        
        time.sleep(AD_DELAY)  # jeda 3 detik
    
    print(f"\n{GREEN}Selesai! Bot selesai menjalankan perintah.{RESET}")
    print_banner()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Bot dihentikan oleh user.{RESET}")
        sys.exit(0)
