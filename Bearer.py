#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  🔥 AUTO GET BEARER TOKEN CLOUDEARNBOT v1.0                       ║
║  DEVELOPED BY SCRIPTYXSOUU                                         ║
║  Ambil Bearer Token saja (init_data di belakang layar)            ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import urllib.parse
import json
import os
import sys
import sqlite3
import requests
from telethon import TelegramClient, functions, types

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
SUPABASE_URL = "https://supabase.cloudearn.org"

# Bearer Token default (anon key)
DEFAULT_AUTH_TOKEN = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc4NTgzNTU2MCwiZXhwIjo0OTQxNTA5MTYwLCJyb2xlIjoiYW5vbiJ9.zBqsny9LpLfI5TKgl2tdH5lj5KDcRQpYswNgvQ3mIiM"
DEFAULT_APIKEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzdXBhYmFzZSIsImlhdCI6MTc4NTgzNTU2MCwiZXhwIjo0OTQxNTA5MTYwLCJyb2xlIjoiYW5vbiJ9.zBqsny9LpLfI5TKgl2tdH5lj5KDcRQpYswNgvQ3mIiM"

# ==================== BANNER ====================
def show_banner():
    print(f"""
{GOLD}╔══════════════════════════════════════════════════════════════════════╗
║  {CYAN}🔥 AUTO GET BEARER TOKEN CLOUDEARNBOT v1.0{GOLD}                  ║
║  {PINK}DEVELOPED BY SCRIPTYXSOUU{GOLD}                                   ║
║  Ambil Bearer Token saja (init_data di belakang layar)                 ║
╚══════════════════════════════════════════════════════════════════════╝{X}
""")

# ==================== FUNGSI PENDUKUNG ====================
def save_phone(phone):
    try:
        with open(PHONE_FILE, 'w') as f:
            f.write(phone.strip())
        return True
    except:
        return False

def load_phone():
    try:
        if os.path.exists(PHONE_FILE):
            with open(PHONE_FILE, 'r') as f:
                return f.read().strip()
    except:
        pass
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
                try:
                    os.remove(session_path)
                    print(f"{Y}🗑️ Session file terkunci, dihapus.{X}")
                    return True
                except:
                    pass
    return False

def save_config(init_data, auth_token, apikey, start_param=""):
    config = {
        "init_data": init_data,
        "auth_token": auth_token,
        "apikey": apikey,
        "start_param": start_param,
        "supabase_url": SUPABASE_URL,
        "headers": {
            "authorization": auth_token,
            "apikey": apikey,
            "x-telegram-init-data": init_data,
            "user-agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.6.4",
            "content-type": "application/json",
            "accept": "*/*",
            "origin": "https://cloudearn.vercel.app/",
            "referer": "https://cloudearn.vercel.app/",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "x-requested-with": "org.telegram.messenger.web",
        }
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    print(f"{G}✅ Config disimpan ke {CONFIG_FILE}{X}")

# ==================== AMBIL INITDATA (SILENT) ====================
async def get_webview_initdata(client, bot_username):
    try:
        bot = await client.get_input_entity(bot_username)
    except Exception as e:
        print(f"{R}❌ Gagal menemukan bot @{bot_username}: {e}{X}")
        return None

    target_url = None
    try:
        full_user = await client(functions.users.GetFullUserRequest(id=bot))
        bot_info = full_user.full_user.bot_info
        if bot_info and bot_info.menu_button and hasattr(bot_info.menu_button, 'url'):
            target_url = bot_info.menu_button.url
            print(f"{DIM}✅ Auto-detected URL: {target_url}{X}")
    except Exception as e:
        print(f"{DIM}⚠️ Gagal ambil menu button, pakai default{X}")

    if not target_url:
        target_url = "https://cloudearn.vercel.app/"

    print(f"{C}📱 Meminta WebView...{X}")
    try:
        result = await client(functions.messages.RequestWebViewRequest(
            peer=bot,
            bot=bot,
            platform='android',
            from_bot_menu=True,
            url=target_url
        ))
    except Exception as e:
        print(f"{R}❌ Gagal meminta WebView: {e}{X}")
        return None

    parsed = urllib.parse.urlparse(result.url)
    init_data = None

    if parsed.fragment:
        params = urllib.parse.parse_qs(parsed.fragment)
        init_data = params.get('tgWebAppData', [None])[0]
    if not init_data and parsed.query:
        params = urllib.parse.parse_qs(parsed.query)
        init_data = params.get('tgWebAppData', [None])[0]

    if init_data:
        print(f"{G}✅ initData berhasil (tidak ditampilkan){X}")
        return init_data
    else:
        print(f"{R}❌ Tidak ditemukan tgWebAppData.{X}")
        return None

# ==================== LOGIN TELEGRAM ====================
async def login_telegram():
    clear_session_if_locked()
    session_path = SESSION_FILE + ".session"

    if os.path.exists(session_path):
        try:
            client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
            await client.connect()
            if await client.is_user_authorized():
                print(f"{G}✅ Session Telegram ditemukan! Login otomatis.{X}")
                return client, await client.get_me()
            else:
                print(f"{Y}⚠️ Session tidak valid, login ulang.{X}")
                os.remove(session_path)
        except Exception as e:
            print(f"{Y}⚠️ Session error: {e}{X}")
            if os.path.exists(session_path):
                try: os.remove(session_path)
                except: pass

    print(f"\n{C}📱 Login ke Telegram diperlukan.{X}")
    saved_phone = load_phone()
    if saved_phone:
        print(f"{G}📞 Menggunakan nomor tersimpan: {saved_phone}{X}")
        phone = saved_phone
    else:
        phone = input(f"{G}📞 Masukkan nomor HP (dengan kode negara, +628...): {X}").strip()
        if not phone:
            print(f"{R}❌ Nomor HP tidak boleh kosong.{X}")
            return None, None

    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()

    try:
        await client.send_code_request(phone)
        code = input(f"{G}🔑 Masukkan kode OTP: {X}").strip()
        if not code:
            print(f"{R}❌ Kode OTP tidak boleh kosong.{X}")
            return None, None
        await client.sign_in(phone, code)
        save_phone(phone)
        print(f"{G}✅ Login sukses!{X}")
        return client, await client.get_me()
    except Exception as e:
        print(f"{R}❌ Login gagal: {e}{X}")
        return None, None

# ==================== VALIDASI & TAMPIL TOKEN ====================
def validate_and_show_token(init_data, auth_token, apikey):
    url = f"{SUPABASE_URL}/functions/v1/api?action=init"
    headers = {
        "authorization": auth_token,
        "apikey": apikey,
        "x-telegram-init-data": init_data,
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.181 Mobile Safari/537.36",
        "origin": "https://cloudearn.vercel.app/",
        "referer": "https://cloudearn.vercel.app/",
    }
    payload = {
        "fp_hash": "88bba40c3cc06e4bc78f354c012a1d5b0f0307f72934bc902352886f2d03cc9b",
        "webgl_hash": "bfc8fbb0012f8c92b0f1f0e178d08ba95ec000335360ca22edcf270a098ddab2",
        "audio_hash": "05d0c5571616fb4731d584d3a16738cc81dcd566dcb2598bee29200a1eeb4a46",
        "tz": "Asia/Jakarta",
        "lang": "id-ID",
        "platform": "Linux aarch64"
    }
    parsed = urllib.parse.parse_qs(init_data)
    start_param = parsed.get('start_param', [None])[0]
    if start_param:
        payload["start_param"] = start_param

    try:
        resp = requests.post(url, json=payload, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            user = data.get('user', {})
            print(f"{G}✅ Validasi sukses!{X}")
            print(f"{C}👤 User: {user.get('username', 'N/A')} (ID: {user.get('tg_id', 'N/A')}){X}")
            return data, start_param
        else:
            print(f"{R}❌ Validasi gagal: {resp.status_code}{X}")
            return None, None
    except Exception as e:
        print(f"{R}❌ Error validasi: {e}{X}")
        return None, None

# ==================== MAIN ====================
async def main():
    show_banner()
    print(f"{C}{'═' * 60}{X}")

    client, me = await login_telegram()
    if not client:
        print(f"{R}❌ Gagal login. Keluar.{X}")
        return
    print(f"{G}👤 Login sebagai: @{me.username if me.username else me.first_name}{X}")

    bot_name = input(f"\n{C}🤖 Masukkan username bot (default: CloudEarnBot): {X}").strip()
    if not bot_name:
        bot_name = "CloudEarnBot"
    if not bot_name.startswith('@'):
        bot_name = '@' + bot_name

    print(f"\n{C}🔍 Mengambil initData...{X}")
    init_data = await get_webview_initdata(client, bot_name)

    await client.disconnect()

    if not init_data:
        print(f"\n{R}❌ Gagal mendapatkan initData.{X}")
        return

    # Validasi dan tampilkan user
    print(f"\n{C}🔄 Validasi ke Supabase...{X}")
    data, start_param = validate_and_show_token(init_data, DEFAULT_AUTH_TOKEN, DEFAULT_APIKEY)
    if not data:
        print(f"{R}❌ Token tidak valid.{X}")
        return

    # TAMPILKAN BEARER TOKEN SAJA (tanpa init_data)
    print(f"\n{GOLD}{'═' * 60}{X}")
    print(f"{G}🎯 BEARER TOKEN:{X}")
    print(f"{C}{DEFAULT_AUTH_TOKEN}{X}")
    print(f"{GOLD}{'═' * 60}{X}")

    # Simpan config?
    save_choice = input(f"\n{G}💾 Simpan ke config.json (termasuk init_data) untuk farming? (y/n): {X}").strip().lower()
    if save_choice == 'y':
        save_config(init_data, DEFAULT_AUTH_TOKEN, DEFAULT_APIKEY, start_param or "")
        print(f"{G}✅ Config siap digunakan!{X}")

    print(f"\n{G}✅ Selesai! Token di atas bisa langsung dipakai.{X}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Y}⚠️ Dihentikan oleh user.{X}")
        sys.exit(0)
