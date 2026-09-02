#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScriptMaker : @SouuXso
TG Group   : https://t.me/+f3QBLkR5D8k4YzNl

Gram Bux - Auto Watch ALL BLOCKS (jeda 1 jam jika gagal)
"""

import requests
import json
import time
import urllib.parse
from typing import Dict, Optional

# Konfigurasi
WATCH_DELAY = 15          # detik antar watch dalam satu block
RETRY_DELAY = 3600        # 1 jam = 3600 detik jika gagal
CLAIM_DELAY = 5           # detik setelah claim
BLOCK_DELAY = 7           # detik antar block

# Warna
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

def pprint(msg, color=GREEN): print(f"{color}{msg}{RESET}")

def countdown(seconds, msg="⏳ Menunggu"):
    """Tampilkan countdown dengan format waktu"""
    while seconds > 0:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            time_str = f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            time_str = f"{minutes:02d}:{secs:02d}"
            
        print(f"\r{msg} {time_str}   ", end="", flush=True)
        time.sleep(1)
        seconds -= 1
    print(f"\r{msg} selesai!     ")

class GramBux:
    BASE_URL = "https://grambux-backend.ankisaw1003.workers.dev"
    FRONTEND = "https://grambux-frontend.onrender.com"

    def __init__(self, init_data: str):
        self.init_data = init_data
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 Mobile Safari/537.36 Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
            "Accept": "*/*",
            "Accept-Language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Origin": self.FRONTEND,
            "Referer": self.FRONTEND + "/",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Sec-Ch-Ua": '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
            "X-Telegram-Init-Data": init_data,
            "Content-Type": "application/json",
        })

    def _request(self, method: str, endpoint: str, json_data: Optional[Dict] = None, params: Optional[Dict] = None):
        url = self.BASE_URL + endpoint
        resp = self.session.request(method, url, json=json_data, params=params)
        resp.raise_for_status()
        return resp.json()

    def get_user(self, tg_id: str, username: str, telegram_username: str, referrer: str = "") -> Dict:
        params = {
            "tg_id": tg_id,
            "username": username,
            "telegram_username": telegram_username,
            "referrer": referrer,
            "_t": int(time.time() * 1000)
        }
        return self._request("GET", "/api/user", params=params)

    def verify_channels(self, tg_id: str) -> Dict:
        return self._request("POST", "/api/verify-channels", json_data={"tg_id": tg_id})

    def watch_ad(self, tg_id: str, block_id: int) -> Dict:
        return self._request("POST", "/api/watch-ad/watch", json_data={"tg_id": tg_id, "block_id": block_id})

    def claim_ad(self, tg_id: str, block_id: int) -> Dict:
        return self._request("POST", "/api/watch-ad/claim", json_data={"tg_id": tg_id, "block_id": block_id})

def parse_init_data(init_data: str) -> Dict:
    parsed = urllib.parse.parse_qs(init_data)
    user_str = parsed.get("user", [""])[0]
    try:
        user_obj = json.loads(user_str)
    except:
        user_obj = {}
    return {
        "tg_id": str(user_obj.get("id", "")),
        "username": user_obj.get("username", ""),
        "full_name": f"{user_obj.get('first_name', '')} {user_obj.get('last_name', '')}".strip()
    }

def print_progress(current, target=10):
    filled = min(current, target)
    empty = target - filled
    fire = "🔥" * filled
    lock = "🔏" * empty
    pprint(f"{fire}{lock} {filled}/{target}", YELLOW)

def check_block_status(bot, tg_id, block_id):
    """Cek status block dari watchProgress"""
    try:
        user_data = bot.get_user(tg_id, "MoneyMaker", "@MoneyMaker_w")
        watch_progress = user_data.get("watchProgress", {})
        block_data = watch_progress.get(str(block_id), {})
        watched_count = block_data.get("watched_count", 0)
        claimed_today = block_data.get("claimed_today", False)
        return watched_count, claimed_today
    except:
        return 0, False

def watch_block_with_retry(bot, tg_id, block_id):
    """Watch block dengan retry 1 jam jika gagal"""
    pprint(f"\n📺 [ BLOCK {block_id} ]", CYAN)
    pprint(f"🎯 Target: 10/10 ads", YELLOW)
    
    # Cek status awal
    watched_count, claimed_today = check_block_status(bot, tg_id, block_id)
    if watched_count >= 10 and claimed_today:
        pprint(f"ℹ️ Block {block_id} sudah selesai dan di-claim!", YELLOW)
        return {"status": "already_claimed", "watched": watched_count, "claimed": True, "earned": 0.0022}
    
    attempt = 0
    retry_count = 0
    
    while True:
        attempt += 1
        try:
            watch_res = bot.watch_ad(tg_id, block_id)
            watched_count = watch_res.get("watched_count", 0)
            claimed_today = watch_res.get("claimed_today", False)
            
            pprint(f"🔄 Watch ke-{attempt}:", YELLOW)
            print_progress(watched_count, 10)
            pprint(f"👁️ Watched Count : {watched_count}/10", GREEN)
            pprint(f"🎁 Claimed Today : {'✅ True' if claimed_today else '❌ False'}", GREEN)
            
            if watched_count >= 10:
                break
                
            countdown(WATCH_DELAY, "⏳ Menunggu sebelum watch berikutnya")
            
        except Exception as e:
            pprint(f"❌ Error watch block {block_id}: {e}", RED)
            if "400" in str(e):
                retry_count += 1
                pprint(f"⚠️ Block {block_id} masih terkunci! (Percobaan ke-{retry_count})", YELLOW)
                pprint(f"⏳ Jeda 1 JAM sebelum coba lagi...", YELLOW)
                countdown(RETRY_DELAY, "⏳ Jeda 1 jam")
                continue
            else:
                countdown(10, "⏳ Error, coba lagi dalam 10 detik")
                continue
    
    # Claim
    if watched_count >= 10:
        if not claimed_today:
            pprint("🎯 Target 10/10 tercapai! Claiming...", GREEN)
            try:
                claim_res = bot.claim_ad(tg_id, block_id)
                new_balance = claim_res.get("newBalance", 0)
                new_stars = claim_res.get("newStars", 0)
                pprint(f"💰 Claim berhasil! +{new_stars} TON", GREEN)
                pprint(f"💎 Balance baru: {new_balance} TON", GREEN)
                return {"status": "success", "watched": watched_count, "claimed": True, "earned": new_stars}
            except Exception as e:
                pprint(f"❌ Gagal claim: {e}", RED)
                return {"status": "claimed_failed", "watched": watched_count, "claimed": False, "earned": 0}
        else:
            pprint("ℹ️ Sudah di-claim hari ini.", YELLOW)
            return {"status": "already_claimed", "watched": watched_count, "claimed": True, "earned": 0.0022}
    else:
        return {"status": "failed", "watched": watched_count, "claimed": False, "earned": 0}

def main():
    pprint("==== 🚀 Gram Bux Auto Script ====", CYAN)
    pprint("👨‍💻 ScriptMaker : @SouuXso", CYAN)
    pprint("📢 TG          : https://t.me/+f3QBLkR5D8k4YzNl", CYAN)
    pprint("⚡ Status      : 🟢 ONLINE\n", CYAN)

    pprint("🔐 [ AUTHENTICATION ]\n", YELLOW)
    pprint("🔑 Masukkan X-Telegram-Init-Data:", YELLOW)
    init_data = input("👉 >>> ").strip()
    if not init_data:
        pprint("❌ Init data kosong, keluar.", RED)
        return

    user_info = parse_init_data(init_data)
    tg_id = user_info["tg_id"]
    username = user_info["username"]

    bot = GramBux(init_data)

    pprint("\n====\n👤 [ USER INFORMATION ]", YELLOW)
    try:
        verify = bot.verify_channels(tg_id)
        verified = verify.get("verified", False)
        status = "🟢 VERIFIED" if verified else "🔴 UNVERIFIED"
    except:
        status = "⚠️ ERROR"
    pprint(f"👋 Login sebagai : {user_info['full_name']}", GREEN)
    pprint(f"🆔 User ID      : {tg_id}", GREEN)
    pprint(f"📢 Channel      : {status}", GREEN)

    pprint("\n====\n💰 [ ACCOUNT ]", YELLOW)
    try:
        user_data = bot.get_user(tg_id, username, f"@{username}")
        user = user_data.get("user", {})
        balance = user.get("ton_balance", 0)
        streak = user.get("daily_streak", 0)
        banned = user.get("banned", False)
        status_acc = "🟢 ACTIVE" if not banned else "🔴 BANNED"
        pprint(f"💎 Balance      : {balance} TON", GREEN)
        pprint(f"🔥 Daily Streak : {streak}", GREEN)
        pprint(f"📊 Status       : {status_acc}", GREEN)
    except Exception as e:
        pprint(f"❌ Gagal ambil data: {e}", RED)

    pprint("\n====\n▶️ [ WATCH ADS ]", YELLOW)
    pprint("🚀 Memulai watch iklan block 1-5...", CYAN)
    pprint("📊 Total target: 50 ads (10 ads x 5 block)", CYAN)
    pprint("⚠️ Jika block error, akan jeda 1 jam lalu coba lagi\n", YELLOW)

    results = {}
    total_earned = 0
    total_ads = 0

    try:
        for block_id in range(1, 6):
            # Cek status awal
            watched_count, claimed_today = check_block_status(bot, tg_id, block_id)
            
            if watched_count >= 10 and claimed_today:
                pprint(f"ℹ️ Block {block_id} sudah selesai, lanjut ke block berikutnya.", YELLOW)
                results[block_id] = {"status": "already_claimed", "watched": watched_count, "claimed": True, "earned": 0.0022}
                total_earned += 0.0022
                total_ads += watched_count
                if block_id < 5:
                    countdown(BLOCK_DELAY, f"⏳ Jeda {BLOCK_DELAY} detik sebelum block {block_id+1}")
                continue
            
            # Proses block
            result = watch_block_with_retry(bot, tg_id, block_id)
            results[block_id] = result
            
            total_ads += result.get("watched", 0)
            
            if result["status"] == "success":
                total_earned += result.get("earned", 0.0022)
                pprint(f"✅ Block {block_id} SELESAI - Earned +{result.get('earned', 0.0022)} TON", GREEN)
            elif result["status"] == "already_claimed":
                total_earned += 0.0022
                pprint(f"ℹ️ Block {block_id} sudah di-claim hari ini", YELLOW)
            else:
                pprint(f"❌ Block {block_id} GAGAL", RED)
            
            # Jeda antar block
            if block_id < 5:
                countdown(CLAIM_DELAY, "⏳ Jeda 5 detik setelah claim")
                countdown(BLOCK_DELAY, f"⏳ Jeda {BLOCK_DELAY} detik sebelum block {block_id+1}")

    except KeyboardInterrupt:
        pprint("\n⚠️ Script dihentikan oleh pengguna.", RED)

    # Hasil Akhir
    pprint("\n" + "="*50, CYAN)
    pprint("📊 [ HASIL AKHIR ]", CYAN)
    pprint("="*50, CYAN)
    
    pprint(f"👁️ Total Ads Watched : {total_ads}/50", GREEN)
    pprint(f"💰 Total Earned     : {total_earned:.4f} TON", GREEN)
    
    sukses = sum(1 for r in results.values() if r["status"] in ["success", "already_claimed"])
    pprint(f"✅ Block Berhasil   : {sukses}/5 block", GREEN)
    pprint(f"❌ Block Gagal     : {5 - sukses}/5 block", RED)

    pprint("\n📋 [ DETAIL PER BLOCK ]", YELLOW)
    for block_id, result in results.items():
        status_icon = "✅" if result["status"] in ["success", "already_claimed"] else "❌"
        watched = result.get("watched", 0)
        claimed = "Ya" if result.get("claimed", False) else "Tidak"
        earned = result.get("earned", 0)
        pprint(f"Block {block_id}: {status_icon} Watched: {watched}/10, Claimed: {claimed}, Earned: {earned:.4f} TON", 
               GREEN if status_icon == "✅" else RED)

    pprint("\n" + "="*50, CYAN)
    pprint("💎 Gram Bux Auto Script Selesai!", CYAN)
    pprint("👨‍💻 @SouuXso", CYAN)
    pprint("="*50, CYAN)

if __name__ == "__main__":
    main()
