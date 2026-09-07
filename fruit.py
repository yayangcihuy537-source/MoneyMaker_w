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
# 🔗 REF   : ref6894031790
# 🚀 START : t.me/MineSLPYBot?startapp=ref6894031790
# =============================================================
#                     HAPPY MINING 🚀
# =============================================================
# ScriptMaker : @MoneyMaker_w
# TG          : https://t.me/ScriptyXSouu
# =============================================================

API_URL = "https://sleepymine.xyz/api/db.php"
MAX_TADDY_ADS = 250      # Batas Taddy ads per hari (0.25 SLPY each)
TADDY_DELAY = 7          # Jeda Taddy ads (detik)

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

def watch_taddy_ad(uid, init_data):
    """Taddy Ads - 0.25 SLPY per ad, max 250/hari"""
    payload = {
        "action": "rpc",
        "fn": "credit_taddy_ad_reward",
        "args": {"uid": uid}
    }
    try:
        result = db_request(payload, init_data)
        if result and result.get('data') and result['data'].get('success'):
            return result['data']
    except Exception:
        pass
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
    print(f"Taddy watched: {user.get('taddy_watched_count', 0)}")
    
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
    print(f"\n{CYAN}[3] Mulai menonton TADDY ADS (0.25 SLPY each, max {MAX_TADDY_ADS}/hari) dengan jeda {TADDY_DELAY} detik...{RESET}")
    count = 0
    while count < MAX_TADDY_ADS:
        ad_result = watch_taddy_ad(uid, init_data)
        if not ad_result or not ad_result.get('success'):
            print(f"{YELLOW}Taddy ads habis atau error, berhenti.{RESET}")
            break
        
        count = ad_result.get('count', 0)
        reward = ad_result.get('reward', 0)
        points = ad_result.get('points', 0)
        print(f"{GREEN}Taddy ke-{count}: +{reward} SLPY, total points: {points}{RESET}")
        
        if count >= MAX_TADDY_ADS:
            print(f"{YELLOW}Sudah mencapai batas {MAX_TADDY_ADS} Taddy ads hari ini.{RESET}")
            break
        
        time.sleep(TADDY_DELAY)
    
    print(f"\n{GREEN}Selesai! Bot selesai menjalankan perintah.{RESET}")
    print_banner()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Bot dihentikan oleh user.{RESET}")
        sys.exit(0)
