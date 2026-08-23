#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import json
import requests
from urllib.parse import parse_qs, unquote
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "https://ton-spark-qu47.vercel.app"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.169 Mobile Safari/537.36 Telegram-Android/12.9.1",
    "Content-Type": "application/json",
    "Accept": "*/*",
    "Origin": BASE_URL,
    "x-requested-with": "org.telegram.messenger.web",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": BASE_URL + "/?tgWebAppStartParam=TEP01059B51",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7"
}

def banner():
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "⚡ Ton Spark Auto Bot - ScriptyXSou ⚡")
    print(Fore.CYAN + "=" * 60)

def get_telegram_id(init_data):
    parsed = parse_qs(init_data)
    user_str = parsed.get('user', [''])[0]
    if not user_str:
        return None
    try:
        user = json.loads(unquote(user_str))
        return user.get('id')
    except:
        return None

def register(session, init_data):
    parsed = parse_qs(init_data)
    user_str = parsed.get('user', [''])[0]
    user = json.loads(unquote(user_str))
    start_param = parsed.get('start_param', [''])[0]
    payload = {
        "telegramId": user['id'],
        "username": user.get('username', ''),
        "firstName": user.get('first_name', ''),
        "referCode": start_param,
        "initData": init_data
    }
    resp = session.post(BASE_URL + "/api/user", json=payload, headers=HEADERS)
    return resp.json()

def get_user(session, telegram_id, init_data):
    params = {"telegramId": telegram_id, "initData": init_data}
    resp = session.get(BASE_URL + "/api/user", params=params, headers=HEADERS)
    return resp.json()

def get_ad_status(session, telegram_id, init_data, network):
    params = {"telegramId": telegram_id, "network": network, "initData": init_data}
    resp = session.get(BASE_URL + "/api/adwatch", params=params, headers=HEADERS)
    return resp.json()

def claim_ad(session, telegram_id, init_data, network):
    payload = {"telegramId": telegram_id, "network": network, "initData": init_data}
    resp = session.post(BASE_URL + "/api/adwatch", json=payload, headers=HEADERS)
    return resp.json()

def claim_daily(session, telegram_id, init_data):
    payload = {"telegramId": telegram_id, "initData": init_data, "action": "daily"}
    resp = session.post(BASE_URL + "/api/daily", json=payload, headers=HEADERS)
    return resp.json()

def get_lightning(session, telegram_id, init_data):
    params = {"telegramId": telegram_id, "initData": init_data}
    resp = session.get(BASE_URL + "/api/lightning", params=params, headers=HEADERS)
    return resp.json()

def claim_lightning(session, telegram_id, init_data):
    payload = {"telegramId": telegram_id, "initData": init_data, "action": "blast"}
    resp = session.post(BASE_URL + "/api/lightning", json=payload, headers=HEADERS)
    return resp.json()

def get_minigame(session, telegram_id, init_data, game):
    params = {"telegramId": telegram_id, "initData": init_data, "game": game}
    resp = session.get(BASE_URL + "/api/miniapp", params=params, headers=HEADERS)
    return resp.json()

def play_minigame(session, telegram_id, init_data, game):
    payload = {"telegramId": telegram_id, "initData": init_data, "action": "play", "game": game}
    resp = session.post(BASE_URL + "/api/miniapp", json=payload, headers=HEADERS)
    return resp.json()

def watch_ads_until_max(session, telegram_id, init_data, network, ad_sleep=5):
    total_reward = 0
    print(Fore.CYAN + f"\n▶️  Menonton iklan {network.upper()}...")
    while True:
        status = get_ad_status(session, telegram_id, init_data, network)
        if not status.get('success'):
            print(Fore.RED + f"❌ Gagal dapat status {network}: {status}")
            break
        count = status.get('count', 0)
        max_count = status.get('max', 20)
        reward = status.get('reward', 500)
        if count >= max_count:
            print(Fore.YELLOW + f"⚠️  {network.upper()} sudah habis ({count}/{max_count})")
            break
        print(Fore.WHITE + f"  Iklan ke-{count+1}...")
        time.sleep(ad_sleep)  # simulasi nonton iklan
        claim = claim_ad(session, telegram_id, init_data, network)
        if claim.get('success'):
            total_reward += reward
            print(Fore.GREEN + f"    ✅ +{reward} Gold (total: {total_reward})")
        else:
            print(Fore.RED + f"    ❌ Gagal claim: {claim.get('error', claim)}")
            break
    return total_reward

def main():
    banner()
    print("Masukkan initData (copy dari URL Telegram):")
    init_data = input("initData: ").strip()
    if not init_data:
        print(Fore.RED + "initData tidak boleh kosong!")
        return

    session = requests.Session()
    # Ambil cookie awal
    try:
        session.get(BASE_URL + "/", headers={"User-Agent": HEADERS["User-Agent"]}, timeout=10)
    except:
        pass

    telegram_id = get_telegram_id(init_data)
    if not telegram_id:
        print(Fore.RED + "Gagal ekstrak telegramId dari initData")
        return

    print(Fore.CYAN + "🔐 Register akun...")
    reg = register(session, init_data)
    if not reg.get('success'):
        print(Fore.RED + f"Register gagal: {reg}")
        return
    print(Fore.GREEN + "✅ Register berhasil")

    print(Fore.CYAN + "📊 Mendapatkan data user...")
    user_data = get_user(session, telegram_id, init_data)
    if not user_data.get('success'):
        print(Fore.RED + f"Gagal get user: {user_data}")
        return
    user = user_data.get('user', {})
    gold_awal = user.get('goldBalance', 0)
    print(Fore.GREEN + f"Gold awal: {gold_awal}")

    total_gold = 0

    # 1. Watch ads Giga
    total_gold += watch_ads_until_max(session, telegram_id, init_data, "giga", ad_sleep=5)

    # 2. Watch ads Monetag
    total_gold += watch_ads_until_max(session, telegram_id, init_data, "monetag", ad_sleep=5)

    # 3. Daily Claim
    print(Fore.CYAN + "\n📅 Claim daily reward...")
    daily = claim_daily(session, telegram_id, init_data)
    if daily.get('success'):
        reward = daily.get('reward', 0)
        total_gold += reward
        print(Fore.GREEN + f"✅ +{reward} Gold (daily)")
    else:
        err = daily.get('error', '')
        if 'already' in err.lower() or 'claimed' in err.lower():
            print(Fore.YELLOW + "⚠️  Daily sudah di-claim hari ini")
        else:
            print(Fore.RED + f"❌ Gagal daily: {err}")

    # 4. Lightning
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
        print(Fore.YELLOW + "⚠️  Lightning belum siap (cooldown)")

    # 5. Spin
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
        print(Fore.YELLOW + "⚠️  Spin sedang cooldown, skip")

    # 6. Chest
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
        print(Fore.YELLOW + "⚠️  Chest sedang cooldown, skip")

    # Tampilkan total
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.GREEN + f"🏆 TOTAL GOLD YANG DIDAPAT: {total_gold} Gold")
    print(Fore.GREEN + f"💰 Saldo akhir: {gold_awal + total_gold} Gold")
    print(Fore.CYAN + "=" * 60)
    print(Fore.WHITE + "Selesai. Bot berhenti.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\nProgram dihentikan oleh user.")
