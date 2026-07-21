#!/usr/bin/env python3
"""
🔑 AUTO GET PHPSESSID DARI BOT TELEGRAM (FIXED ENDPOINT)
Cukup masukkan nomor HP + OTP, script akan:
1. Login ke Telegram via Telethon
2. Buka WebView bot yang diinginkan
3. Ambil initData dari URL WebView
4. Kirim ke /actions/tg_auth.php (multipart/form-data)
5. Dapatkan PHPSESSID dari cookie
"""

import asyncio
import urllib.parse
import requests
import json
import os
import sys
from telethon import TelegramClient, functions, types

# ==================== KONFIGURASI ====================
API_ID = 21578873
API_HASH = "b7562db4c393baff2f415d14a14d1f76"
DEFAULT_BOT = "PepeFlowOfficialBot"
SESSION_FILE = "telegram_session_phpsessid"
BASE_URL = "https://pepeflow.com"

# ==================== FUNGSI ====================
async def get_webview_initdata(client, bot_username):
    """Buka WebView bot dan ambil initData dari URL"""
    try:
        bot = await client.get_input_entity(bot_username)
    except Exception as e:
        print(f"❌ Gagal menemukan bot @{bot_username}: {e}")
        return None

    # Ambil info bot untuk mendapatkan URL menu
    try:
        full_user = await client(functions.users.GetFullUserRequest(id=bot))
        bot_info = full_user.full_user.bot_info
        target_url = "https://pepeflow.com/miniapp.php"
        if bot_info and bot_info.menu_button and hasattr(bot_info.menu_button, 'url'):
            target_url = bot_info.menu_button.url
            print(f"🔗 Auto-detected URL: {target_url}")
        else:
            print(f"⚠️ Tidak dapat mendeteksi URL menu, menggunakan default: {target_url}")
    except Exception as e:
        print(f"⚠️ Gagal mengambil info bot: {e}, menggunakan URL default")
        target_url = "https://pepeflow.com/miniapp.php"

    print(f"📱 Meminta WebView untuk @{bot_username}...")
    try:
        result = await client(functions.messages.RequestWebViewRequest(
            peer=bot,
            bot=bot,
            platform='android',
            from_bot_menu=True,
            url=target_url
        ))
    except Exception as e:
        print(f"❌ Gagal meminta WebView: {e}")
        return None

    parsed = urllib.parse.urlparse(result.url)
    init_data = None

    # Cari tgWebAppData di fragment atau query
    if parsed.fragment:
        params = urllib.parse.parse_qs(parsed.fragment)
        init_data = params.get('tgWebAppData', [None])[0]
    if not init_data and parsed.query:
        params = urllib.parse.parse_qs(parsed.query)
        init_data = params.get('tgWebAppData', [None])[0]

    if init_data:
        print("✅ initData berhasil didapat.")
        return init_data
    else:
        print("❌ Tidak ditemukan tgWebAppData di URL WebView.")
        return None

async def login_telegram():
    """Login ke Telegram dan ekstrak initData"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        print("\n📱 Login ke Telegram diperlukan.")
        phone = input("📞 Masukkan nomor HP (dengan kode negara, +628...): ").strip()
        if not phone:
            print("❌ Nomor HP tidak boleh kosong.")
            return None, None

        try:
            await client.send_code_request(phone)
            code = input("🔑 Masukkan kode OTP yang dikirim ke Telegram: ").strip()
            if not code:
                print("❌ Kode OTP tidak boleh kosong.")
                return None, None
            await client.sign_in(phone, code)
        except Exception as e:
            print(f"❌ Login gagal: {e}")
            return None, None

    print("✅ Login sukses!")
    return client, await client.get_me()

async def get_phpsessid_from_bot(client, bot_username):
    """Dapatkan initData dari bot, kirim ke /actions/tg_auth.php, ambil PHPSESSID"""
    init_data = await get_webview_initdata(client, bot_username)
    if not init_data:
        return None

    print("\n🔐 Mengirim initData ke /actions/tg_auth.php...")
    session = requests.Session()
    
    # Ekstrak telegram_id dan username dari initData
    import urllib.parse
    parsed_init = urllib.parse.parse_qs(init_data)
    user_str = parsed_init.get('user', [None])[0]
    telegram_id = None
    telegram_username = None
    if user_str:
        try:
            import json
            user_json = json.loads(urllib.parse.unquote(user_str))
            telegram_id = str(user_json.get('id', ''))
            telegram_username = user_json.get('username', '')
        except:
            pass

    # Headers sesuai capture
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.47 Mobile Safari/537.36 Telegram-Android/12.6.4 (Samsung SM-A556E; Android 16; SDK 36; HIGH)",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/miniapp.php",
        "X-Requested-With": "org.telegram.messenger.web",
        "sec-ch-ua": '"Not;A=Brand";v="8", "Chromium";v="150", "Android WebView";v="150"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Accept": "*/*",
        "Accept-Language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    # Multipart form data
    files = {
        "init_data": (None, init_data),
        "telegram_id": (None, telegram_id or "0"),
        "telegram_username": (None, telegram_username or ""),
        "auto_login": (None, "1"),
    }

    try:
        resp = session.post(f"{BASE_URL}/actions/tg_auth.php", headers=headers, files=files)
        if resp.status_code == 200:
            # Ambil PHPSESSID dari cookie
            for cookie in session.cookies:
                if cookie.name == "PHPSESSID":
                    print("✅ PHPSESSID ditemukan dari /actions/tg_auth.php")
                    return cookie.value
            # Kalau gak ada di cookie, coba dari response header
            if 'Set-Cookie' in resp.headers:
                for cookie in resp.headers.get('Set-Cookie', '').split(';'):
                    if 'PHPSESSID' in cookie:
                        phpsessid = cookie.split('=')[1].strip()
                        print("✅ PHPSESSID ditemukan dari Set-Cookie header")
                        return phpsessid
            print("⚠️ Response sukses tapi tidak ada PHPSESSID di cookie.")
            return None
        else:
            print(f"❌ Request ke /actions/tg_auth.php gagal: {resp.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

async def main():
    print("\n🐸 🔑 AUTO GET PHPSESSID DARI BOT TELEGRAM DEV : MoneyMaker_w")
    print("=" * 55)

    # Login ke Telegram
    client, me = await login_telegram()
    if not client:
        print("❌ Gagal login. Keluar.")
        return
    print(f"👤 Login sebagai: @{me.username if me.username else me.first_name}")

    # Minta nama bot
    bot_name = input(f"\n🤖 Masukkan username bot (default: {DEFAULT_BOT}): ").strip()
    if not bot_name:
        bot_name = DEFAULT_BOT
    if not bot_name.startswith('@'):
        bot_name = '@' + bot_name

    print(f"\n🔍 Mencari PHPSESSID dari bot {bot_name}...")
    phpsessid = await get_phpsessid_from_bot(client, bot_name)

    await client.disconnect()

    if phpsessid:
        print("\n" + "=" * 55)
        print(f"🎯 PHPSESSID: {phpsessid}")
        print("=" * 55)
        print("\n📌 Simpan nilai ini untuk digunakan di script PepeFlow.")
        save = input("\n💾 Simpan ke file config PepeFlow? (y/n): ").strip().lower()
        if save == 'y':
            config_file = "pepeflow_config.json"
            if os.path.exists(config_file):
                try:
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                except:
                    config = {}
            else:
                config = {}
            config['phpsessid'] = phpsessid
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            print(f"✅ PHPSESSID disimpan ke {config_file}")
    else:
        print("\n❌ Gagal mendapatkan PHPSESSID.")
        print("💡 Coba manual: buka bot di Telegram, buka WebView, lalu ambil cookie dari browser.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Dihentikan oleh user.")
        sys.exit(0)
