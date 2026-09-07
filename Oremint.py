import asyncio
import sys
import os
import sqlite3
import requests
import json
import time
import random
import platform
import hashlib
import subprocess
import logging

# --- SILENCE PYROGRAM LOGS ---
logging.getLogger("pyrogram").setLevel(logging.ERROR)

# --- HELLFIRE & SYSTEM COLORS ---
RED    = "\033[31m"
ORANGE = "\033[38;5;208m"
YELLOW = "\033[93m"
GREEN  = "\033[92m"
CYAN   = "\033[96m"
WHITE  = "\033[97m"
BOLD   = "\033[1m"
GRAY   = "\033[90m"
END    = "\033[0m"

# --- UNIVERSAL ASYNCIO LOOP FIX ---
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Pyrogram Imports
try:
    from pyrogram import Client
    from pyrogram.raw.functions.messages import RequestWebView
    from pyrogram.errors import (
        SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid, 
        AuthKeyUnregistered, Unauthorized
    )
except ImportError:
    print(f"{RED}❌ Missing dependencies! Run: pip install pyrogram tgcrypto requests{END}")
    sys.exit()

# ==================== CONFIGURATION ====================
API_ID = 31810886  
API_HASH = "8cfcea6500abce782ec0596b3fbc89b2"
BOT_USERNAME = "OreMintbot"
APP_URL = "https://app.miniempire.app/miniapp/index.html?tid=541"
BASE_URL = "https://app.miniempire.app/miniapp"
TID = 541
SESS_NAME = "oreminter_541"

# --- SESSION DIRECTORY (pakai folder lokal script) ---
SESS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
if not os.path.exists(SESS_DIR):
    os.makedirs(SESS_DIR, exist_ok=True)

# --- SYSTEM UTILS ---
def get_hwid():
    id_str = platform.node() + platform.machine() + platform.processor()
    return hashlib.sha256(id_str.encode()).hexdigest()[:16].upper()

def get_sys_info():
    model, version = "Unknown", "N/A"
    try:
        model = subprocess.check_output(['getprop', 'ro.product.model']).decode().strip()
        version = subprocess.check_output(['getprop', 'ro.build.version.release']).decode().strip()
    except:
        model = platform.node()
        version = platform.release()
    return model, version

def banner():
    os.system('clear' if os.name == 'posix' else 'cls')
    print(f"{CYAN}{BOLD}")
    print("===============================================================")
    print("=====                 MINI EMPIRE BOT                    =====")
    print("=====       👑 BUILD YOUR EMPIRE • 💰 FARM • ⚡ EARN      =====")
    print("=====                                                     =====")
    print("=====       [✓] AUTO FARM  [✓] AUTO CLAIM  [✓] REWARD    =====")
    print("=====                                                     =====")
    print("=====              👨‍💻 ScriptMaker : @SouuXso             =====")
    print("===============================================================")
    print(f"{END}")
    model, android = get_sys_info()
    hwid = get_hwid()
    print(f"{WHITE}   📱 {BOLD}DEVICE:{END} {ORANGE}{model} (Android {android})")
    print(f"{WHITE}   🔑 {BOLD}HWID:  {END} {ORANGE}{hwid}")
    print(f"{RED}  " + "━"*53 + f"{END}")

# ==================== CUSTOM LOGIN SYSTEM ====================
async def nexor_login(app):
    print(f"   {RED}[AUTH]{END} {YELLOW}Initializing fresh Login...{END}")
    while True:
        try:
            phone = input(f"   {RED}[AUTH]{END} {WHITE}Enter Number (+): {END}").strip()
            sent_code = await app.send_code(phone)
            break
        except Exception:
            print(f"   {RED}[ERR]{END} {WHITE}Invalid Number Format!{END}")

    while True:
        try:
            code = input(f"   {RED}[AUTH]{END} {WHITE}Enter OTP Code: {END}").strip()
            await app.sign_in(phone, sent_code.phone_code_hash, code)
            break
        except SessionPasswordNeeded:
            while True:
                try:
                    pw = input(f"   {RED}[AUTH]{END} {WHITE}Enter 2FA Password: {END}").strip()
                    await app.check_password(pw)
                    break
                except PasswordHashInvalid:
                    print(f"   {RED}[ERR]{END} {WHITE}Wrong 2FA Password!{END}")
            break
        except PhoneCodeInvalid:
            print(f"   {RED}[ERR]{END} {WHITE}Wrong OTP Code!{END}")

# ==================== LOGIC ENGINE ====================
async def get_tg_init_data():
    app = Client(SESS_NAME, API_ID, API_HASH, workdir=SESS_DIR)
    try:
        await app.connect()
        if not await app.get_me():
            await nexor_login(app)
    except (AuthKeyUnregistered, Unauthorized):
        await app.disconnect()
        session_path = os.path.join(SESS_DIR, f"{SESS_NAME}.session")
        if os.path.exists(session_path): os.remove(session_path)
        app = Client(SESS_NAME, API_ID, API_HASH, workdir=SESS_DIR)
        await app.connect()
        await nexor_login(app)
    except Exception as e:
        print(f"   {RED}[ERR]{END} {WHITE}Connection issue: {e}{END}")
        return None

    try:
        web_view = await app.invoke(RequestWebView(
            peer=await app.resolve_peer(BOT_USERNAME),
            bot=await app.resolve_peer(BOT_USERNAME),
            platform="android", from_bot_menu=False, url=APP_URL
        ))
        import urllib.parse
        data = urllib.parse.unquote(web_view.url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0])
        await app.disconnect()
        return data
    except Exception as e:
        await app.disconnect()
        return None

class MiniEmpireBot:
    def __init__(self, init_data):
        self.init_data = init_data
        self.base_url = "https://app.miniempire.app/miniapp"
        self.headers = {
            'User-Agent': "Mozilla/5.0 (Linux; Android 15; SM-S928B) AppleWebKit/537.36",
            'Content-Type': "application/json",
            'origin': "https://app.miniempire.app",
            'x-requested-with': "org.telegram.messenger"
        }

    def log(self, tag, msg, color=WHITE):
        print(f"   {RED}[{tag}]{END} {color}{msg}{END}")

    def process(self):
        try:
            self.log("INIT", "Syncing with Satellite...", YELLOW)
            
            # Auth
            res = requests.post(
                f"{self.base_url}/auth?tid={TID}",
                json={"initData": self.init_data, "tid": TID, "fp": {"uid": get_hwid(), "sw": 400, "sh": 889}},
                headers=self.headers
            ).json()
            if not res.get('ok'):
                self.log("ERR", "Auth failed", RED)
                return False
            
            user = res.get('user', {})
            self.log("INFO", f"Diver: {WHITE}{user.get('username')}{END} | Power: {CYAN}{user.get('power')}{END}")
            self.log("INFO", f"Hashes: {GREEN}{round(user.get('hashes', 0), 4)}{END}")

            # Claim
            claim = requests.post(
                f"{self.base_url}/claim?tid={TID}",
                json={"initData": self.init_data, "tid": TID},
                headers=self.headers
            ).json()
            if claim.get('ok'):
                self.log("CLAIM", f"Hashes Collected! ✅", GREEN)

            # Spin
            spin = requests.post(
                f"{self.base_url}/tasks/slot-spin?tid={TID}",
                json={"initData": self.init_data, "tid": TID},
                headers=self.headers
            ).json()
            if spin.get('ok'):
                reels = "".join(spin.get('reels', []))
                self.log("SLOT", f"Spin: {reels} | Reward: {GREEN}+{spin.get('pips_awarded')}{END}")
            
            # Ads (hanya untuk keeping session active)
            for k in ["monetag", "gigapub"]:
                requests.post(
                    f"{self.base_url}/house/hit",
                    json={"tid": str(TID), "kind": k, "surface": "app", "moment": "action"},
                    headers=self.headers
                )
                self.log("ADS", f"Bypassed {k} Protocol 🔥", ORANGE)
            
            return True
        except Exception as e:
            self.log("ERR", f"Process exception: {e}", RED)
            return False

# ==================== MAIN ====================
async def main_engine():
    banner()
    while True:
        banner()
        print(f"   {CYAN}🛰️  FETCHING SATELLITE AUTH...{END}")
        
        init_data = await get_tg_init_data()
        
        if init_data:
            banner()
            bot = MiniEmpireBot(init_data)
            if bot.process():
                print(f"\n   {YELLOW}🔥 CYCLE FINISHED. NEXT IGNITION IN 10 MIN.{END}")
                for i in range(600, 0, -1):
                    sys.stdout.write(f"\r   ⏳ TIMER: {i}s ")
                    sys.stdout.flush()
                    await asyncio.sleep(1)
            else:
                print(f"   {RED}[ERR]{END} {WHITE}Process Failed. Retrying...{END}")
                await asyncio.sleep(10)
        else:
            print(f"   {RED}[ERR]{END} {WHITE}Auth Failed. Retrying...{END}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        loop.run_until_complete(main_engine())
    except KeyboardInterrupt:
        print(f"\n\n   {RED}🛑 [SHUTDOWN] {YELLOW}NEXOR Engine Safely Off.{END}")
        sys.exit(0)
