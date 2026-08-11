#!/usr/bin/env python3
"""
Bearer Token Extractor v6 - Khusus Bossdogearnbot & CloudEarnBot
"""

import asyncio
import urllib.parse
import requests
import json
import os
import sys
import sqlite3
from telethon import TelegramClient, functions

# ==================== WARNA ====================
R, G, Y, B, M, C, W, X = '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[97m', '\033[0m'
GOLD = '\033[38;5;220m'
CYAN = '\033[1;96m'
PINK = '\033[38;5;206m'
DIM = '\033[2;37m'

# ==================== KONFIGURASI ====================
API_ID = 21578873
API_HASH = "b7562db4c393baff2f415d14a14d1f76"
SESSION_FILE = "telegram_session_bearer"
PHONE_FILE = "phone_number.txt"
CONFIG_FILE = "config.json"

# Token default untuk CloudEarnBot
CLOUDEARN_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc4NTgzNTU2MCwiZXhwIjo0OTQxNTA5MTYwLCJyb2xlIjoiYW5vbiJ9.zBqsny9LpLfI5TKgl2tdH5lj5KDcRQpYswNgvQ3mIiM"
CLOUDEARN_APIKEY = CLOUDEARN_TOKEN.replace("Bearer ", "")

# ==================== BANNER ====================
def banner():
    print(f"""
{GOLD}╔══════════════════════════════════════════════════════════════════════╗
║  {CYAN}🔑 BEARER TOKEN EXTRACTOR v6 (Bossdog + CloudEarn){GOLD}          ║
║  {PINK}BY SCRIPTYXSOU{GOLD}                                              ║
╚══════════════════════════════════════════════════════════════════════╝{X}
""")

# ==================== FUNGSI ====================
def save_phone(phone):
    with open(PHONE_FILE, 'w') as f:
        f.write(phone.strip())

def load_phone():
    if os.path.exists(PHONE_FILE):
        with open(PHONE_FILE, 'r') as f:
            return f.read().strip()
    return None

def clear_session_if_locked():
    session_path = SESSION_FILE + ".session"
    if os.path.exists(session_path):
        try:
            conn = sqlite3.connect(session_path, timeout=0.1)
            conn.close()
            return False
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                os.remove(session_path)
                return True
    return False

async def get_webview_initdata(client, bot_username):
    try:
        bot = await client.get_input_entity(bot_username)
    except Exception as e:
        print(f"{R}❌ Bot tidak ditemukan: {e}{X}")
        return None, None

    target_url = None
    try:
        full_user = await client(functions.users.GetFullUserRequest(id=bot))
        bot_info = full_user.full_user.bot_info
        if bot_info and bot_info.menu_button and hasattr(bot_info.menu_button, 'url'):
            target_url = bot_info.menu_button.url
            print(f"{G}✅ Detected menu URL: {target_url}{X}")
    except:
        pass

    if not target_url:
        name = bot_username.replace('@', '')
        target_url = f"https://t.me/{name}/play"
        print(f"{Y}⚠️ Fallback URL: {target_url}{X}")

    print(f"{C}📱 Membuka WebView: {target_url}{X}")
    try:
        result = await client(functions.messages.RequestWebViewRequest(
            peer=bot,
            bot=bot,
            platform='android',
            from_bot_menu=True,
            url=target_url
        ))
    except Exception as e:
        print(f"{R}❌ Gagal buka WebView: {e}{X}")
        return None, None

    parsed = urllib.parse.urlparse(result.url)
    init_data = None
    if parsed.fragment:
        params = urllib.parse.parse_qs(parsed.fragment)
        init_data = params.get('tgWebAppData', [None])[0]
    if not init_data and parsed.query:
        params = urllib.parse.parse_qs(parsed.query)
        init_data = params.get('tgWebAppData', [None])[0]
    return init_data, result.url

async def login_telegram():
    clear_session_if_locked()
    session_path = SESSION_FILE + ".session"
    if os.path.exists(session_path):
        try:
            client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
            await client.connect()
            if await client.is_user_authorized():
                return client, await client.get_me()
        except:
            pass

    phone = load_phone()
    if not phone:
        phone = input(f"{G}📞 Nomor HP (dengan kode negara, +62...): {X}").strip()
        if not phone:
            return None, None
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()
    try:
        await client.send_code_request(phone)
        code = input(f"{G}🔑 Kode OTP: {X}").strip()
        if not code:
            return None, None
        await client.sign_in(phone, code)
        save_phone(phone)
        return client, await client.get_me()
    except Exception as e:
        print(f"{R}❌ Login gagal: {e}{X}")
        return None, None

def get_start_param(init_data):
    parsed = urllib.parse.parse_qs(init_data)
    return parsed.get('start_param', [None])[0]

def get_domain_from_url(url):
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc
    if host.startswith('www.'):
        host = host[4:]
    return host

async def get_bossdog_token(client, bot_username):
    """Ambil token dari Bossdogearnbot via /api/auth/verify"""
    init_data, webview_url = await get_webview_initdata(client, bot_username)
    if not init_data:
        return None

    domain = get_domain_from_url(webview_url)
    if not domain:
        print(f"{R}❌ Gagal ekstrak domain.{X}")
        return None

    print(f"{DIM}🏠 Domain: {domain}{X}")

    start_param = get_start_param(init_data) or ""
    base_url = f"https://{domain}"
    verify_url = f"{base_url}/api/auth/verify"
    fingerprint = "3fb8034"
    payload = {
        "initData": init_data,
        "fingerprint": fingerprint,
        "startParam": start_param
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 Chrome/150.0.7871.124 Mobile Safari/537.36",
        "Accept": "*/*",
        "Origin": base_url,
        "Referer": f"{base_url}/",
    }

    print(f"\n{C}🔐 Mengirim ke {verify_url}...{X}")
    try:
        resp = requests.post(verify_url, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            token = data.get('token') or data.get('access_token') or data.get('bearer') or data.get('auth_token')
            if token:
                if not token.startswith("Bearer "):
                    token = "Bearer " + token
                print(f"{G}✅ Token didapat!{X}")
                return token
        else:
            print(f"{Y}⚠️ Gagal (status {resp.status_code}){X}")
    except Exception as e:
        print(f"{R}❌ Error: {e}{X}")

    return None

def get_cloudearn_token():
    """Token CloudEarnBot sudah diketahui (anon key)"""
    print(f"{G}✅ Token CloudEarn sudah tersedia (anon key).{X}")
    return CLOUDEARN_TOKEN

async def main():
    banner()
    print(f"{C}{'═' * 60}{X}")

    client, me = await login_telegram()
    if not client:
        print(f"{R}❌ Gagal login.{X}")
        return
    print(f"{G}👤 Login sebagai: @{me.username if me.username else me.first_name}{X}")

    print(f"\n{C}🤖 Pilih bot:{X}")
    print(f"  {G}[1]{X} Bossdogearnbot (ambil via API)")
    print(f"  {G}[2]{X} CloudEarnBot (token default)")
    choice = input(f"{C}Pilih (1/2): {X}").strip()

    token = None
    if choice == "1":
        bot = "Bossdogearnbot"
        if not bot.startswith('@'):
            bot = '@' + bot
        print(f"\n{C}🔍 Mengambil Bearer Token dari {bot}...{X}")
        token = await get_bossdog_token(client, bot)
    elif choice == "2":
        token = get_cloudearn_token()
    else:
        print(f"{R}❌ Pilihan tidak valid.{X}")
        return

    await client.disconnect()

    if token:
        print(f"\n{GOLD}{'═' * 60}{X}")
        print(f"{G}🎯 BEARER TOKEN:{X}")
        print(f"{C}{token}{X}")
        print(f"{GOLD}{'═' * 60}{X}")
        save = input(f"\n{G}💾 Simpan ke config.json? (y/n): {X}").strip().lower()
        if save == 'y':
            apikey = token.replace("Bearer ", "")
            config = {
                "auth_token": token,
                "apikey": apikey,
                "headers": {
                    "Authorization": token,
                    "apikey": apikey,
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 Chrome/150.0.7871.124 Mobile Safari/537.36",
                }
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            print(f"{G}✅ Config disimpan.{X}")
    else:
        print(f"\n{R}❌ Gagal mendapatkan Bearer Token.{X}")
        print(f"{Y}💡 Coba manual: buka bot di browser, devtools, cari request ke /api/me, copy Authorization header.{X}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Y}⚠️ Dihentikan user.{X}")
        sys.exit(0)
