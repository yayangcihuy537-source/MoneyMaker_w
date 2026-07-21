#!/usr/bin/env python3
"""
🔑 AMBIL INIT_DATA / QUERY_ID DARI BOT TELEGRAM
Cukup masukkan username bot, script akan:
1. Login ke Telegram via Telethon
2. Buka WebView bot tersebut
3. Ambil tgWebAppData (init_data) dari URL
4. Tampilkan init_data lengkap
"""

import asyncio
import urllib.parse
import json
import os
import sys
from telethon import TelegramClient, functions, types

# ==================== KONFIGURASI ====================
API_ID = 21578873
API_HASH = "b7562db4c393baff2f415d14a14d1f76"
SESSION_FILE = "telegram_session_initdata"

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
        target_url = None
        if bot_info and bot_info.menu_button and hasattr(bot_info.menu_button, 'url'):
            target_url = bot_info.menu_button.url
            print(f"🔗 Auto-detected URL: {target_url}")
        else:
            # fallback: coba URL umum
            target_url = f"https://t.me/{bot_username}"
            print(f"⚠️ Tidak dapat mendeteksi URL menu, menggunakan: {target_url}")
    except Exception as e:
        print(f"⚠️ Gagal mengambil info bot: {e}")
        target_url = f"https://t.me/{bot_username}"

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
        print(f"URL: {result.url}")
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

async def main():
    print("\n🐸 🔑 AMBIL INIT_DATA DARI BOT TELEGRAM DEV : MoneyMaker_w")
    print("=" * 55)

    # Login ke Telegram
    client, me = await login_telegram()
    if not client:
        print("❌ Gagal login. Keluar.")
        return
    print(f"👤 Login sebagai: @{me.username if me.username else me.first_name}")

    # Minta nama bot
    bot_name = input("\n🤖 Masukkan username bot (tanpa @, contoh: PepeFlowOfficialBot): ").strip()
    if not bot_name:
        print("❌ Nama bot tidak boleh kosong!")
        await client.disconnect()
        return
    if not bot_name.startswith('@'):
        bot_name = '@' + bot_name

    print(f"\n🔍 Mengambil initData dari bot {bot_name}...")
    init_data = await get_webview_initdata(client, bot_name)

    await client.disconnect()

    if init_data:
        print("\n" + "=" * 55)
        print(f"🎯 INIT_DATA (tgWebAppData):\n{init_data}")
        print("=" * 55)

        # Parse query_id dari init_data
        parsed = urllib.parse.parse_qs(init_data)
        query_id = parsed.get('query_id', [None])[0]
        if query_id:
            print(f"\n📌 Query ID: {query_id}")

        # Tawarkan untuk menyimpan ke file
        save = input("\n💾 Simpan ke file init_data.txt? (y/n): ").strip().lower()
        if save == 'y':
            with open("init_data.txt", "w") as f:
                f.write(init_data)
            print("✅ init_data disimpan ke init_data.txt")
    else:
        print("\n❌ Gagal mendapatkan initData.")
        print("💡 Coba manual: buka bot di Telegram, buka WebView, lalu ambil tgWebAppData dari URL.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Dihentikan oleh user.")
        sys.exit(0)
