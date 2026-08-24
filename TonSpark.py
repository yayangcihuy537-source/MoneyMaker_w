#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import requests
from urllib.parse import parse_qs, unquote, urlencode
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "https://ton-spark-qu47.vercel.app"
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.169 Mobile Safari/537.36 Telegram-Android/12.9.1",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Origin": BASE_URL,
    "Referer": BASE_URL + "/?tgWebAppStartParam=TEP01059B51",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "x-requested-with": "org.telegram.messenger.web",
}

def banner():
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "⚡ Ton Spark Auto Bot - Fixed Edition ⚡")
    print(Fore.CYAN + "=" * 60)

def parse_init_data(init_data):
    """Parse initData string into dict and extract user info"""
    parsed = parse_qs(init_data)
    result = {k: v[0] if v else '' for k, v in parsed.items()}
    
    # Extract user
    user_str = result.get('user', '')
    if user_str:
        try:
            result['user_obj'] = json.loads(unquote(user_str))
        except:
            result['user_obj'] = {}
    else:
        result['user_obj'] = {}
    
    return result

def create_session():
    """Create a session with proper cookie handling"""
    session = requests.Session()
    session.headers.update(BASE_HEADERS)
    
    # Initial GET to set cookies
    try:
        session.get(BASE_URL + "/", timeout=10)
    except:
        pass
    
    return session

def safe_json_response(resp):
    """Safely parse JSON response with error handling"""
    try:
        return resp.json()
    except (json.JSONDecodeError, ValueError) as e:
        # If JSON fails, return raw text in error field
        return {
            'success': False,
            'error': f"JSON parse error: {str(e)}",
            'raw_response': resp.text[:500]  # first 500 chars for debugging
        }

def register(session, init_data):
    """Register user with proper error handling"""
    parsed = parse_init_data(init_data)
    user = parsed.get('user_obj', {})
    start_param = parsed.get('start_param', '') or parsed.get('startParam', '')
    
    payload = {
        "telegramId": user.get('id'),
        "username": user.get('username', ''),
        "firstName": user.get('first_name', ''),
        "referCode": start_param,
        "initData": init_data
    }
    
    # Remove None values
    payload = {k: v for k, v in payload.items() if v is not None}
    
    try:
        resp = session.post(BASE_URL + "/api/user", json=payload, timeout=30)
        return safe_json_response(resp)
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f"Request failed: {str(e)}"}

def get_user(session, telegram_id, init_data):
    """Get user data with proper error handling"""
    params = {"telegramId": str(telegram_id), "initData": init_data}
    try:
        resp = session.get(BASE_URL + "/api/user", params=params, timeout=30)
        return safe_json_response(resp)
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': f"Request failed: {str(e)}"}

def get_ad_status(session, telegram_id, init_data, network):
    params = {"telegramId": str(telegram_id), "network": network, "initData": init_data}
    try:
        resp = session.get(BASE_URL + "/api/adwatch", params=params, timeout=30)
        return safe_json_response(resp)
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}

def claim_ad(session, telegram_id, init_data, network):
    payload = {"telegramId": str(telegram_id), "network": network, "initData": init_data}
    try:
        resp = session.post(BASE_URL + "/api/adwatch", json=payload, timeout=30)
        return safe_json_response(resp)
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}

def claim_daily(session, telegram_id, init_data):
    payload = {"telegramId": str(telegram_id), "initData": init_data, "action": "daily"}
    try:
        resp = session.post(BASE_URL + "/api/daily", json=payload, timeout=30)
        return safe_json_response(resp)
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}

def get_lightning(session, telegram_id, init_data):
    params = {"telegramId": str(telegram_id), "initData": init_data}
    try:
        resp = session.get(BASE_URL + "/api/lightning", params=params, timeout=30)
        return safe_json_response(resp)
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}

def claim_lightning(session, telegram_id, init_data):
    payload = {"telegramId": str(telegram_id), "initData": init_data, "action": "blast"}
    try:
        resp = session.post(BASE_URL + "/api/lightning", json=payload, timeout=30)
        return safe_json_response(resp)
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}

def get_minigame(session, telegram_id, init_data, game):
    params = {"telegramId": str(telegram_id), "initData": init_data, "game": game}
    try:
        resp = session.get(BASE_URL + "/api/miniapp", params=params, timeout=30)
        return safe_json_response(resp)
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}

def play_minigame(session, telegram_id, init_data, game):
    payload = {"telegramId": str(telegram_id), "initData": init_data, "action": "play", "game": game}
    try:
        resp = session.post(BASE_URL + "/api/miniapp", json=payload, timeout=30)
        return safe_json_response(resp)
    except requests.exceptions.RequestException as e:
        return {'success': False, 'error': str(e)}

def watch_ads_until_max(session, telegram_id, init_data, network, ad_sleep=5, max_attempts=20):
    total_reward = 0
    print(Fore.CYAN + f"\n▶️  Menonton iklan {network.upper()}...")
    
    for attempt in range(max_attempts):
        status = get_ad_status(session, telegram_id, init_data, network)
        if not status.get('success'):
            print(Fore.RED + f"❌ Gagal dapat status {network}: {status.get('error', status)}")
            break
        
        count = status.get('count', 0)
        max_count = status.get('max', 20)
        reward = status.get('reward', 500)
        
        if count >= max_count:
            print(Fore.YELLOW + f"⚠️  {network.upper()} sudah habis ({count}/{max_count})")
            break
        
        print(Fore.WHITE + f"  Iklan ke-{count+1}...")
        time.sleep(ad_sleep)
        
        claim = claim_ad(session, telegram_id, init_data, network)
        if claim.get('success'):
            total_reward += reward
            print(Fore.GREEN + f"    ✅ +{reward} Gold (total: {total_reward})")
        else:
            err = claim.get('error', claim)
            if 'already' in str(err).lower():
                print(Fore.YELLOW + f"    ⚠️  Iklan sudah diklaim, lanjut...")
                continue
            else:
                print(Fore.RED + f"    ❌ Gagal claim: {err}")
                break
    
    return total_reward

def main():
    banner()
    print(Fore.WHITE + "Masukkan initData (copy dari URL Telegram):")
    init_data = input("initData: ").strip()
    
    if not init_data:
        print(Fore.RED + "initData tidak boleh kosong!")
        return
    
    # Parse init data first to validate
    parsed = parse_init_data(init_data)
    user = parsed.get('user_obj', {})
    telegram_id = user.get('id')
    
    if not telegram_id:
        print(Fore.RED + "Gagal ekstrak telegramId dari initData")
        print(Fore.YELLOW + "Pastikan initData lengkap dan valid")
        return
    
    print(Fore.CYAN + f"📱 Telegram ID: {telegram_id}")
    print(Fore.CYAN + f"👤 Username: @{user.get('username', 'N/A')}")
    
    session = create_session()
    
    # Try register with better error handling
    print(Fore.CYAN + "\n🔐 Register akun...")
    reg = register(session, init_data)
    
    if not reg.get('success'):
        print(Fore.RED + f"❌ Register gagal: {reg.get('error', reg)}")
        if 'raw_response' in reg:
            print(Fore.YELLOW + f"📄 Server response: {reg['raw_response'][:200]}")
        return
    
    print(Fore.GREEN + "✅ Register berhasil")
    
    print(Fore.CYAN + "\n📊 Mendapatkan data user...")
    user_data = get_user(session, telegram_id, init_data)
    
    if not user_data.get('success'):
        print(Fore.RED + f"❌ Gagal get user: {user_data.get('error', user_data)}")
        return
    
    user_info = user_data.get('user', {})
    gold_awal = user_info.get('goldBalance', 0)
    print(Fore.GREEN + f"💰 Gold awal: {gold_awal}")
    
    total_gold = 0
    
    # 1. Watch ads
    total_gold += watch_ads_until_max(session, telegram_id, init_data, "giga", ad_sleep=5)
    total_gold += watch_ads_until_max(session, telegram_id, init_data, "monetag", ad_sleep=5)
    
    # 2. Daily Claim
    print(Fore.CYAN + "\n📅 Claim daily reward...")
    daily = claim_daily(session, telegram_id, init_data)
    if daily.get('success'):
        reward = daily.get('reward', 0)
        total_gold += reward
        print(Fore.GREEN + f"✅ +{reward} Gold (daily)")
    else:
        err = daily.get('error', '')
        if 'already' in str(err).lower() or 'claimed' in str(err).lower():
            print(Fore.YELLOW + "⚠️  Daily sudah di-claim hari ini")
        else:
            print(Fore.RED + f"❌ Gagal daily: {err}")
    
    # 3. Lightning
    print(Fore.CYAN + "\n⚡ Cek Lightning...")
    light = get_lightning(session, telegram_id, init_data)
    if light.get('success') and light.get('canBlast'):
        print(Fore.WHITE + "  Meledakkan Lightning...")
        blast = claim_lightning(session, telegram_id, init_data)
        if blast.get('success'):
            reward = blast.get('reward', 0)
            total_gold += reward
            print(Fore.GREEN + f"    ✅ +{reward} Gold (Lightning)")
        else:
            print(Fore.RED + f"    ❌ Gagal blast: {blast.get('error', blast)}")
    else:
        err = light.get('error', '')
        if 'cooldown' in str(err).lower() or 'wait' in str(err).lower():
            print(Fore.YELLOW + "⚠️  Lightning cooldown, skip")
        else:
            print(Fore.YELLOW + f"⚠️  Lightning tidak tersedia: {err}")
    
    # 4. Spin
    print(Fore.CYAN + "\n🎡 Cek Spin...")
    spin_status = get_minigame(session, telegram_id, init_data, "spin")
    if spin_status.get('success') and spin_status.get('canPlay'):
        print(Fore.WHITE + "  Memutar Spin...")
        spin_play = play_minigame(session, telegram_id, init_data, "spin")
        if spin_play.get('success'):
            reward = spin_play.get('reward', 0)
            total_gold += reward
            print(Fore.GREEN + f"    ✅ +{reward} Gold (Spin)")
        else:
            print(Fore.RED + f"    ❌ Gagal spin: {spin_play.get('error', spin_play)}")
    else:
        err = spin_status.get('error', '')
        if 'cooldown' in str(err).lower():
            print(Fore.YELLOW + "⚠️  Spin cooldown, skip")
        else:
            print(Fore.YELLOW + f"⚠️  Spin tidak tersedia: {err}")
    
    # 5. Chest
    print(Fore.CYAN + "\n🎁 Cek Chest...")
    chest_status = get_minigame(session, telegram_id, init_data, "chest")
    if chest_status.get('success') and chest_status.get('canPlay'):
        print(Fore.WHITE + "  Membuka Chest...")
        chest_play = play_minigame(session, telegram_id, init_data, "chest")
        if chest_play.get('success'):
            reward = chest_play.get('reward', 0)
            total_gold += reward
            tier = chest_play.get('tier', '')
            print(Fore.GREEN + f"    ✅ +{reward} Gold (Chest {tier})")
        else:
            print(Fore.RED + f"    ❌ Gagal chest: {chest_play.get('error', chest_play)}")
    else:
        err = chest_status.get('error', '')
        if 'cooldown' in str(err).lower():
            print(Fore.YELLOW + "⚠️  Chest cooldown, skip")
        else:
            print(Fore.YELLOW + f"⚠️  Chest tidak tersedia: {err}")
    
    # Summary
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.GREEN + f"🏆 TOTAL GOLD DAPAT: {total_gold} Gold")
    print(Fore.GREEN + f"💰 Saldo akhir: {gold_awal + total_gold} Gold")
    print(Fore.CYAN + "=" * 60)
    print(Fore.WHITE + "\nSelesai, bot berhenti.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n⏹️  Program dihentikan user.")
    except Exception as e:
        print(Fore.RED + f"\n💥 Error tak terduga: {e}")
        sys.exit(1)
