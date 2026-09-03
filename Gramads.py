#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GramBux Auto Claim + Watch Ads FULL
- Watch Ads Block 1-5 (10 watch per block, claim otomatis)
- Auto Claim BOT Tasks
- Auto Tap to Earn
- Auto Mystery Box, Miner, Vault
- Jeda 1 jam jika block error

============================================================
👨‍💻 ScriptMaker : @JoshuaXSupport
📢 TG          : https://t.me/+f3QBLkR5D8k4YzNl
============================================================
"""

import requests
import json
import time
import urllib.parse
from typing import Dict, Optional, List

# ============================================================
# WARNA ANSI
# ============================================================
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
GRAY = "\033[90m"

def pprint(msg, color=GREEN): 
    print(f"{color}{msg}{RESET}")

def print_sep():
    print(f"{GRAY}{'='*60}{RESET}")

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

def print_progress(current, target=10):
    filled = min(current, target)
    empty = target - filled
    fire = "🔥" * filled
    lock = "🔏" * empty
    pprint(f"{fire}{lock} {filled}/{target}", YELLOW)

# ============================================================
# CLASS GRAMBUX
# ============================================================
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
        try:
            resp = self.session.request(method, url, json=json_data, params=params, timeout=30)
            if resp.status_code != 200:
                return {"error": resp.status_code, "text": resp.text[:200]}
            return resp.json()
        except requests.exceptions.Timeout:
            return {"error": "timeout", "text": "Request timeout"}
        except requests.exceptions.ConnectionError:
            return {"error": "connection", "text": "Connection error"}
        except Exception as e:
            return {"error": "exception", "text": str(e)}

    # === USER ===
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

    def get_earn_status(self, tg_id: str) -> Dict:
        return self._request("GET", "/api/earn/status", params={"tg_id": tg_id})

    def get_tasks(self) -> Dict:
        return self._request("GET", "/api/tasks")

    # === WATCH ADS ===
    def watch_ad(self, tg_id: str, block_id: int) -> Dict:
        return self._request("POST", "/api/watch-ad/watch", json_data={"tg_id": tg_id, "block_id": block_id})

    def claim_ad(self, tg_id: str, block_id: int) -> Dict:
        return self._request("POST", "/api/watch-ad/claim", json_data={"tg_id": tg_id, "block_id": block_id})

    # === TASKS ===
    def initiate_task(self, tg_id: str, task_id: str) -> Dict:
        return self._request("POST", "/api/task/initiate", json_data={"tg_id": tg_id, "task_id": task_id})

    def claim_task(self, tg_id: str, task_id: str) -> Dict:
        return self._request("POST", "/api/task/claim", json_data={"tg_id": tg_id, "task_id": task_id})

    # === TAP TO EARN ===
    def claim_tap(self, tg_id: str) -> Dict:
        return self._request("POST", "/api/tap-to-earn/claim", json_data={"tg_id": tg_id})

    # === MYSTERY BOX ===
    def claim_mystery_box(self, tg_id: str) -> Dict:
        return self._request("POST", "/api/mystery-box/claim", json_data={"tg_id": tg_id})

    # === MINER ===
    def start_miner(self, tg_id: str) -> Dict:
        return self._request("POST", "/api/miner/start", json_data={"tg_id": tg_id})

    def claim_miner(self, tg_id: str) -> Dict:
        return self._request("POST", "/api/miner/claim", json_data={"tg_id": tg_id})

    # === VAULT ===
    def start_vault(self, tg_id: str) -> Dict:
        return self._request("POST", "/api/vault/start", json_data={"tg_id": tg_id})

    def claim_vault(self, tg_id: str) -> Dict:
        return self._request("POST", "/api/vault/claim", json_data={"tg_id": tg_id})

# ============================================================
# FUNGSI BANTU
# ============================================================
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

def check_block_status(bot, tg_id, block_id):
    """Cek status block dari watchProgress"""
    try:
        user_data = bot.get_user(tg_id, "MoneyMaker", "@MoneyMaker_w")
        if user_data.get("error"):
            return 0, False
        watch_progress = user_data.get("watchProgress", {})
        block_data = watch_progress.get(str(block_id), {})
        watched_count = block_data.get("watched_count", 0)
        claimed_today = block_data.get("claimed_today", False)
        return watched_count, claimed_today
    except:
        return 0, False

def watch_block(bot, tg_id, block_id, retry_delay=3600):
    """Watch block 10x lalu claim"""
    pprint(f"\n📺 [ BLOCK {block_id} ]", CYAN)
    pprint(f"🎯 Target: 10/10 ads", YELLOW)
    
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
            if watch_res.get("error"):
                error_text = str(watch_res.get("text", ""))
                if "400" in str(watch_res) or "block" in error_text.lower():
                    retry_count += 1
                    pprint(f"⚠️ Block {block_id} masih terkunci! (Percobaan ke-{retry_count})", YELLOW)
                    pprint(f"⏳ Jeda 1 JAM sebelum coba lagi...", YELLOW)
                    countdown(retry_delay, "⏳ Jeda 1 jam")
                    continue
                else:
                    pprint(f"❌ Error: {watch_res}", RED)
                    countdown(10, "⏳ Coba lagi dalam 10 detik")
                    continue
            
            watched_count = watch_res.get("watched_count", 0)
            
            pprint(f"🔄 Watch ke-{attempt}:", YELLOW)
            print_progress(watched_count, 10)
            pprint(f"👁️ Watched Count : {watched_count}/10", GREEN)
            
            if watched_count >= 10:
                break
                
            countdown(15, "⏳ Menunggu sebelum watch berikutnya")
            
        except Exception as e:
            pprint(f"❌ Error watch: {e}", RED)
            countdown(10, "⏳ Coba lagi dalam 10 detik")
            continue
    
    # Claim
    if watched_count >= 10:
        if not claimed_today:
            pprint("🎯 Target 10/10 tercapai! Claiming...", GREEN)
            try:
                claim_res = bot.claim_ad(tg_id, block_id)
                if claim_res.get("error"):
                    pprint(f"❌ Gagal claim: {claim_res}", RED)
                    return {"status": "claim_failed", "watched": watched_count, "claimed": False, "earned": 0}
                new_balance = claim_res.get("newBalance", 0)
                new_stars = claim_res.get("newStars", 0)
                pprint(f"💰 Claim berhasil! +{new_stars} TON", GREEN)
                pprint(f"💎 Balance baru: {new_balance} TON", GREEN)
                return {"status": "success", "watched": watched_count, "claimed": True, "earned": new_stars}
            except Exception as e:
                pprint(f"❌ Gagal claim: {e}", RED)
                return {"status": "claim_failed", "watched": watched_count, "claimed": False, "earned": 0}
        else:
            pprint("ℹ️ Sudah di-claim hari ini.", YELLOW)
            return {"status": "already_claimed", "watched": watched_count, "claimed": True, "earned": 0.0022}
    else:
        return {"status": "failed", "watched": watched_count, "claimed": False, "earned": 0}

# ============================================================
# FUNGSI AUTO CLAIM LAINNYA
# ============================================================
def claim_bot_tasks(bot, tg_id, completions):
    """Claim semua task type BOT yang belum diklaim"""
    pprint("\n📋 Mengecek Tasks type BOT...", CYAN)
    tasks_res = bot.get_tasks()
    if tasks_res.get("error") or not isinstance(tasks_res, list):
        pprint("❌ Gagal ambil tasks", RED)
        return 0, 0
    
    all_tasks = tasks_res
    bot_tasks = []
    
    for task in all_tasks:
        if not isinstance(task, dict):
            continue
        task_id = task.get('id')
        task_type = task.get('type', '')
        if task_id == 'daily1':
            continue
        if task_id in completions:
            continue
        if task_type == 'bot':
            bot_tasks.append(task)
    
    pprint(f"🤖 Bot tasks ditemukan: {len(bot_tasks)}", YELLOW)
    if not bot_tasks:
        pprint("✅ Semua bot tasks sudah diklaim!", GREEN)
        return 0, 0
    
    total_earned = 0
    claimed_count = 0
    
    for idx, task in enumerate(bot_tasks, 1):
        task_id = task.get('id')
        title = task.get('title', 'No title')[:30]
        reward = task.get('reward_ton', 0)
        
        pprint(f"\n[{idx}/{len(bot_tasks)}] ⏳ {title} (reward: {reward:.5f} TON)", YELLOW)
        
        # Initiate
        init_res = bot.initiate_task(tg_id, task_id)
        if init_res.get("error"):
            if "already completed" in str(init_res):
                pprint("   Task sudah diklaim", YELLOW)
                continue
            pprint(f"   ❌ Initiate gagal: {init_res}", RED)
            continue
        
        if init_res.get('success'):
            pprint("   ⏳ Menunggu 5 detik...", YELLOW)
            time.sleep(5)
            
            # Claim
            claim_res = bot.claim_task(tg_id, task_id)
            if claim_res.get("error"):
                if "already claimed" in str(claim_res):
                    pprint("   Task sudah diklaim", YELLOW)
                    continue
                if "timer not completed" in str(claim_res):
                    pprint("   ⏳ Timer belum selesai, tunggu 3 detik...", YELLOW)
                    time.sleep(3)
                    claim_res = bot.claim_task(tg_id, task_id)
            
            if claim_res and claim_res.get('success'):
                earned = claim_res.get('starsAwarded', 0)
                pprint(f"   💰 +{earned:.5f} TON", GREEN)
                total_earned += earned
                claimed_count += 1
            else:
                pprint(f"   ❌ Claim gagal: {claim_res}", RED)
        else:
            pprint(f"   ❌ Initiate gagal", RED)
        
        time.sleep(2)
    
    return claimed_count, total_earned

def claim_tap(bot, tg_id):
    """Claim tap to earn"""
    pprint("\n🖐️ Mengecek Tap to Earn...", CYAN)
    status = bot.get_earn_status(tg_id)
    if status.get("error"):
        pprint("❌ Gagal ambil status tap", RED)
        return 0, 0
    
    tap_info = status.get("tap_to_earn", {})
    remaining = tap_info.get("remaining_taps", 0)
    cooldown = tap_info.get("cooldown_remaining_sec", 0)
    
    pprint(f"Tap tersisa: {remaining}/10", YELLOW)
    if remaining == 0:
        pprint("Tap sudah habis hari ini ✅", GREEN)
        return 0, 0
    if cooldown > 60:
        pprint(f"⏳ Cooldown {cooldown//60}m {cooldown%60}s - SKIP", YELLOW)
        return 0, 0
    
    claimed = 0
    earned = 0
    for i in range(remaining):
        if cooldown > 60:
            break
        if cooldown > 0:
            pprint(f"⏳ Cooldown {cooldown}s, tunggu...", YELLOW)
            time.sleep(cooldown + 1)
            cooldown = 0
        
        res = bot.claim_tap(tg_id)
        if res.get("error"):
            pprint(f"❌ Tap gagal: {res}", RED)
            break
        if res.get("success"):
            earned += res.get("earned_ton", 0)
            claimed += 1
            pprint(f"💰 Tap #{i+1}: +{res.get('earned_ton', 0):.5f} TON", GREEN)
            cooldown = res.get("cooldown_sec", 0)
        else:
            pprint(f"❌ Tap gagal: {res}", RED)
            break
        time.sleep(1)
    
    return claimed, earned

def claim_mystery_box(bot, tg_id):
    """Claim mystery box"""
    pprint("\n📦 Mengecek Mystery Box...", CYAN)
    status = bot.get_earn_status(tg_id)
    if status.get("error"):
        pprint("❌ Gagal ambil status", RED)
        return 0
    
    mystery = status.get("mystery_box", {})
    if not mystery.get("available"):
        pprint("Mystery Box belum tersedia", YELLOW)
        return 0
    
    pprint("Mystery Box tersedia! Mengklaim...", GREEN)
    res = bot.claim_mystery_box(tg_id)
    if res.get("error"):
        pprint(f"❌ Gagal claim: {res}", RED)
        return 0
    if res.get("success"):
        earned = res.get("earned_ton", 0)
        pprint(f"💰 +{earned:.5f} TON", GREEN)
        return earned
    return 0

def handle_miner(bot, tg_id):
    """Start atau claim miner"""
    pprint("\n⛏️ Mengecek Miner...", CYAN)
    status = bot.get_earn_status(tg_id)
    if status.get("error"):
        pprint("❌ Gagal ambil status", RED)
        return 0
    
    miner = status.get("miner", {})
    if miner.get("ready"):
        pprint("Miner ready! Mengklaim...", GREEN)
        res = bot.claim_miner(tg_id)
        if res.get("success"):
            earned = res.get("earned_ton", 0)
            pprint(f"💰 +{earned:.5f} TON", GREEN)
            return earned
        return 0
    elif miner.get("can_start") and not miner.get("is_running"):
        pprint("Starting Miner...", YELLOW)
        res = bot.start_miner(tg_id)
        if res.get("success"):
            pprint("✅ Miner started!", GREEN)
        else:
            pprint(f"❌ Gagal start: {res}", RED)
    else:
        pprint("Miner sedang berjalan", YELLOW)
    return 0

def handle_vault(bot, tg_id):
    """Start atau claim vault"""
    pprint("\n🏦 Mengecek Vault...", CYAN)
    status = bot.get_earn_status(tg_id)
    if status.get("error"):
        pprint("❌ Gagal ambil status", RED)
        return 0
    
    vault = status.get("vault", {})
    if vault.get("ready"):
        pprint("Vault ready! Mengklaim...", GREEN)
        res = bot.claim_vault(tg_id)
        if res.get("success"):
            earned = res.get("earned_ton", 0)
            pprint(f"💰 +{earned:.5f} TON", GREEN)
            return earned
        return 0
    elif vault.get("can_start") and not vault.get("is_running"):
        pprint("Starting Vault...", YELLOW)
        res = bot.start_vault(tg_id)
        if res.get("success"):
            pprint("✅ Vault started!", GREEN)
        else:
            pprint(f"❌ Gagal start: {res}", RED)
    else:
        pprint("Vault sedang berjalan", YELLOW)
    return 0

# ============================================================
# MAIN
# ============================================================
def main():
    print_sep()
    pprint("🚀 Gram Bux Auto Script FULL", CYAN)
    pprint("👨‍💻 ScriptMaker : @JoshuaXSupport", CYAN)
    pprint("📢 TG          : https://t.me/+f3QBLkR5D8k4YzNl", CYAN)
    print_sep()
    
    pprint("\n🔐 Masukkan X-Telegram-Init-Data:", YELLOW)
    init_data = input("👉 ").strip()
    if not init_data:
        pprint("❌ Init data kosong, keluar.", RED)
        return

    user_info = parse_init_data(init_data)
    tg_id = user_info["tg_id"]
    username = user_info["username"]
    full_name = user_info["full_name"] or username

    bot = GramBux(init_data)

    # Cek user
    pprint("\n👤 USER INFORMATION", CYAN)
    try:
        user_data = bot.get_user(tg_id, username, f"@{username}")
        if user_data.get("error"):
            pprint(f"❌ Gagal ambil data user: {user_data}", RED)
            return
        user = user_data.get("user", {})
        balance = user.get("ton_balance", 0)
        completions = user_data.get("completions", {})
        watch_progress = user_data.get("watchProgress", {})
        pprint(f"👋 Login sebagai : {full_name}", GREEN)
        pprint(f"🆔 User ID      : {tg_id}", GREEN)
        pprint(f"💰 Balance      : {balance:.5f} TON", GREEN)
        pprint(f"📋 Tasks done   : {len(completions)}", GREEN)
        
        # Hitung total watch progress
        total_watch = 0
        for block in watch_progress.values():
            total_watch += block.get("watched_count", 0)
        pprint(f"👁️ Total watch  : {total_watch}", GREEN)
    except Exception as e:
        pprint(f"❌ Error: {e}", RED)
        return

    print_sep()
    total_earned = 0
    total_claim = 0

    # ============================================================
    # 1. WATCH ADS BLOCK 1-5
    # ============================================================
    pprint("\n▶️ [ WATCH ADS BLOCK 1-5 ]", CYAN)
    pprint("📊 Target: 10 ads x 5 block = 50 ads", YELLOW)
    pprint("⚠️ Jika error, akan jeda 1 jam lalu coba lagi\n", YELLOW)
    
    for block_id in range(1, 6):
        result = watch_block(bot, tg_id, block_id)
        if result["status"] in ["success", "already_claimed"]:
            total_earned += result.get("earned", 0)
            total_claim += 1
        if block_id < 5:
            countdown(7, f"⏳ Jeda 7 detik sebelum block {block_id+1}")
    
    print_sep()
    
    # ============================================================
    # 2. TAP TO EARN
    # ============================================================
    tap_claimed, tap_earned = claim_tap(bot, tg_id)
    total_earned += tap_earned
    total_claim += tap_claimed
    
    # ============================================================
    # 3. BOT TASKS
    # ============================================================
    task_claimed, task_earned = claim_bot_tasks(bot, tg_id, completions)
    total_earned += task_earned
    total_claim += task_claimed
    
    # ============================================================
    # 4. MYSTERY BOX
    # ============================================================
    total_earned += claim_mystery_box(bot, tg_id)
    
    # ============================================================
    # 5. MINER
    # ============================================================
    total_earned += handle_miner(bot, tg_id)
    
    # ============================================================
    # 6. VAULT
    # ============================================================
    total_earned += handle_vault(bot, tg_id)
    
    # ============================================================
    # FINAL
    # ============================================================
    print_sep()
    pprint("📊 RINGKASAN AKHIR", CYAN)
    pprint(f"💰 Total Earned Hari Ini : {total_earned:.5f} TON", GREEN)
    pprint(f"📋 Total Claim Berhasil  : {total_claim}", GREEN)
    
    # Ambil balance terbaru
    try:
        user_data = bot.get_user(tg_id, username, f"@{username}")
        if not user_data.get("error"):
            new_balance = user_data.get("user", {}).get("ton_balance", 0)
            pprint(f"💎 Balance Akhir        : {new_balance:.5f} TON", GREEN)
    except:
        pass
    
    print_sep()
    pprint("✅ Selesai! 🎉", GREEN)
    pprint(f"📢 Bergabung dengan TG: https://t.me/+f3QBLkR5D8k4YzNl", CYAN)
    print_sep()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pprint("\n⚠️ Dibatalkan oleh user.", RED)
    except Exception as e:
        pprint(f"❌ Error: {e}", RED)
        import traceback
        traceback.print_exc()
