#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║  🔑 AMBIL INIT_DATA / QUERY_ID DARI BOT TELEGRAM v1.1      ║
║  DEVELOPED BY MoneyMaker_w                                 ║
║  Ambil tgWebAppData (init_data) dari bot via WebView      ║
║  📞 Nomor HP tersimpan otomatis (tidak perlu input ulang)  ║
╚══════════════════════════════════════════════════════════════╝
"""

import asyncio
import urllib.parse
import json
import os
import sys
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
SESSION_FILE = "telegram_session_initdata"
PHONE_FILE = "phone_number.txt"

# ==================== BANNER ====================
def show_banner():
    print(f"""
{GOLD}╔══════════════════════════════════════════════════════════════╗
║  {CYAN}🔑 AMBIL INIT_DATA / QUERY_ID DARI BOT TELEGRAM v1.1{GOLD}   ║
║  {PINK}DEVELOPED BY MoneyMaker_w{GOLD}                              ║
║  Ambil tgWebAppData (init_data) dari bot via WebView        ║
║  📞 Nomor HP tersimpan otomatis (tidak perlu input ulang){GOLD}║
╚══════════════════════════════════════════════════════════════╝{X}
""")

# ==================== FUNGSI ====================
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

async def get_webview_initdata(client, bot_username):
    """Buka WebView bot dan ambil initData dari URL"""
    try:
        bot = await client.get_input_entity(bot_username)
    except Exception as e:
        print(f"{R}❌ Gagal menemukan bot @{bot_username}: {e}{X}")
        return None

    try:
        full_user = await client(functions.users.GetFullUserRequest(id=bot))
        bot_info = full_user.full_user.bot_info
        target_url = f"https://t.me/{bot_username}"
        if bot_info and bot_info.menu_button and hasattr(bot_info.menu_button, 'url'):
            target_url = bot_info.menu_button.url
            print(f"{G}🔗 Auto-detected URL: {target_url}{X}")
        else:
            print(f"{Y}⚠️ Tidak dapat mendeteksi URL menu, menggunakan: {target_url}{X}")
    except Exception as e:
        print(f"{Y}⚠️ Gagal mengambil info bot: {e}{X}")
        target_url = f"https://t.me/{bot_username}"

    print(f"{C}📱 Meminta WebView untuk @{bot_username}...{X}")
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
        print(f"{G}✅ initData berhasil didapat.{X}")
        return init_data
    else:
        print(f"{R}❌ Tidak ditemukan tgWebAppData di URL WebView.{X}")
        print(f"{DIM}URL: {result.url}{X}")
        return None

async def login_telegram():
    """Login ke Telegram, gunakan nomor tersimpan jika ada"""
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        print(f"{G}✅ Session masih aktif! Login otomatis.{X}")
        return client, await client.get_me()

    saved_phone = load_phone()
    if saved_phone:
        print(f"{G}📞 Menggunakan nomor tersimpan: {saved_phone}{X}")
        phone = saved_phone
    else:
        print(f"\n{C}📱 Login ke Telegram diperlukan.{X}")
        phone = input(f"{G}📞 Masukkan nomor HP (dengan kode negara, +628...): {X}").strip()
        if not phone:
            print(f"{R}❌ Nomor HP tidak boleh kosong.{X}")
            return None, None

    try:
        await client.send_code_request(phone)
        code = input(f"{G}🔑 Masukkan kode OTP yang dikirim ke Telegram: {X}").strip()
        if not code:
            print(f"{R}❌ Kode OTP tidak boleh kosong.{X}")
            return None, None
        await client.sign_in(phone, code)
        save_phone(phone)
        print(f"{G}✅ Nomor HP tersimpan.{X}")
    except Exception as e:
        print(f"{R}❌ Login gagal: {e}{X}")
        return None, None

    print(f"{G}✅ Login sukses!{X}")
    return client, await client.get_me()

async def main():
    show_banner()
    print(f"{C}{'═' * 55}{X}")

    client, me = await login_telegram()
    if not client:
        print(f"{R}❌ Gagal login. Keluar.{X}")
        return
    print(f"{G}👤 Login sebagai: @{me.username if me.username else me.first_name}{X}")

    bot_name = input(f"\n{C}🤖 Masukkan username bot (tanpa @, contoh: PepeFlowOfficialBot): {X}").strip()
    if not bot_name:
        print(f"{R}❌ Nama bot tidak boleh kosong!{X}")
        await client.disconnect()
        return
    if not bot_name.startswith('@'):
        bot_name = '@' + bot_name

    print(f"\n{C}🔍 Mengambil initData dari bot {bot_name}...{X}")
    init_data = await get_webview_initdata(client, bot_name)

    await client.disconnect()

    if init_data:
        print(f"\n{GOLD}{'═' * 55}{X}")
        print(f"{G}🎯 INIT_DATA (tgWebAppData):{X}\n{init_data}")
        print(f"{GOLD}{'═' * 55}{X}")

        parsed = urllib.parse.parse_qs(init_data)
        query_id = parsed.get('query_id', [None])[0]
        if query_id:
            print(f"\n{C}📌 Query ID: {G}{query_id}{X}")

        save = input(f"\n{G}💾 Simpan ke file init_data.txt? (y/n): {X}").strip().lower()
        if save == 'y':
            with open("init_data.txt", "w") as f:
                f.write(init_data)
            print(f"{G}✅ init_data disimpan ke init_data.txt{X}")
    else:
        print(f"\n{R}❌ Gagal mendapatkan initData.{X}")
        print(f"{Y}💡 Coba manual: buka bot di Telegram, buka WebView, lalu ambil tgWebAppData dari URL.{X}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Y}⚠️ Dihentikan oleh user.{X}")
        sys.exit(0)
