#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  🔥 QUERY GRABBER v2 — Ambil tgWebAppData dari Bot Manapun       ║
║  👑 Author: MoneyMaker_w | Fix: VoltXSou                          ║
║  ✅ Support semua bot • Auto fallback URL • Parse query        ║
║  ✅ Tampilkan user ID, query_id, auth_date, hash, dll.         ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import urllib.parse
import json
import os
import sys
import sqlite3
import requests
from telethon import TelegramClient, functions

# ==================== WARNA ====================
R, G, Y, B, M, C, W, X = '\033[91m','\033[92m','\033[93m','\033[94m','\033[95m','\033[96m','\033[97m','\033[0m'
GOLD, CYAN, PINK, DIM = '\033[38;5;220m','\033[1;96m','\033[38;5;206m','\033[2;37m'

# ==================== KONFIG ====================
API_ID = 21578873
API_HASH = "b7562db4c393baff2f415d14a14d1f76"
SESSION_FILE = "telegram_session"

# ==================== BANNER ====================
def show_banner():
    print(f"""
{GOLD}╔══════════════════════════════════════════════════════════════════════╗
║  {CYAN}🔥 QUERY GRABBER v2 — Ambil tgWebAppData dari Bot Manapun{GOLD}   ║
║  {PINK}👑 Author: MoneyMaker_w | Fix: VoltXSou{GOLD}                       ║
║  {C}✅ Support semua bot • Auto fallback URL • Parse query{GOLD}        ║
║  {C}✅ Tampilkan user ID, query_id, auth_date, hash, dll.{GOLD}         ║
╚══════════════════════════════════════════════════════════════════════╝{X}
""")

# ==================== FUNGSI ====================
def force_clear_session():
    session_path = SESSION_FILE + ".session"
    if os.path.exists(session_path):
        try:
            os.remove(session_path)
            print(f"{Y}🗑️ Session file terkunci dihapus.{X}")
        except:
            pass

def parse_initdata(init_data):
    """Parse tgWebAppData menjadi dictionary"""
    parsed = urllib.parse.parse_qs(init_data)
    result = {}
    for k, v in parsed.items():
        if k == 'user':
            try:
                result[k] = json.loads(v[0])
            except:
                result[k] = v[0]
        else:
            result[k] = v[0] if len(v) == 1 else v
    return result

def print_parsed(data):
    print(f"\n{CYAN}{'═' * 60}{X}")
    print(f"{GOLD}📊 PARSED tgWebAppData:{X}")
    for k, v in data.items():
        if k == 'user':
            print(f"  {G}👤 user:{X} {json.dumps(v, indent=2, ensure_ascii=False)}")
        else:
            print(f"  {G}{k}:{X} {v}")
    print(f"{CYAN}{'═' * 60}{X}")

def save_initdata(init_data, filename="query_data.txt"):
    with open(filename, 'w') as f:
        f.write(init_data)
    print(f"{G}💾 Data disimpan ke {filename}{X}")

def send_to_api(init_data, api_url=None):
    if not api_url:
        return
    headers = {"Content-Type": "application/json"}
    payload = {"initData": init_data}
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=10)
        print(f"{G}📦 Status API: {resp.status_code}{X}")
        try:
            print(f"{G}📨 Response:{X}\n{json.dumps(resp.json(), indent=2, ensure_ascii=False)}")
        except:
            print(f"{Y}⚠️ Response bukan JSON:{X}\n{resp.text[:300]}")
    except Exception as e:
        print(f"{R}❌ Gagal kirim API: {e}{X}")

# ==================== AMBIL INITDATA ====================
async def get_initdata_from_bot(bot_username, custom_url=None):
    force_clear_session()
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        print(f"{C}📱 Login Telegram diperlukan.{X}")
        phone = input(f"{G}📞 Nomor HP (+628...): {X}").strip()
        if not phone:
            print(f"{R}❌ Nomor kosong.{X}")
            await client.disconnect()
            return None
        try:
            await client.send_code_request(phone)
            code = input(f"{G}🔑 Kode OTP: {X}").strip()
            await client.sign_in(phone, code)
            print(f"{G}✅ Login sukses.{X}")
        except Exception as e:
            print(f"{R}❌ Login gagal: {e}{X}")
            await client.disconnect()
            return None

    try:
        bot = await client.get_input_entity(bot_username)
    except:
        print(f"{R}❌ Bot @{bot_username} tidak ditemukan.{X}")
        await client.disconnect()
        return None

    # Daftar URL yang dicoba
    urls = []
    if custom_url:
        urls.append(custom_url)
    name = bot_username.replace('@', '').strip()
    urls += [
        f"https://{name}.xyz",
        f"https://{name}.vercel.app",
        f"https://{name}.t.me",
        f"https://t.me/{name}/app"
    ]
    # Hapus duplikat
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)

    init_data = None
    for url in unique:
        print(f"{C}🔗 Mencoba: {url}{X}")
        try:
            result = await client(functions.messages.RequestWebViewRequest(
                peer=bot,
                bot=bot,
                platform='android',
                from_bot_menu=True,
                url=url
            ))
            parsed = urllib.parse.urlparse(result.url)
            if parsed.fragment:
                params = urllib.parse.parse_qs(parsed.fragment)
                init_data = params.get('tgWebAppData', [None])[0]
            if not init_data and parsed.query:
                params = urllib.parse.parse_qs(parsed.query)
                init_data = params.get('tgWebAppData', [None])[0]
            if init_data:
                print(f"{G}✅ Berhasil dari {url}{X}")
                break
        except Exception as e:
            print(f"{Y}⚠️ Gagal: {str(e)[:60]}{X}")

    await client.disconnect()
    return init_data

# ==================== MAIN ====================
async def main():
    show_banner()
    print(f"{C}{'═' * 60}{X}")

    bot = input(f"{G}🤖 Masukkan username bot (tanpa @, contoh: MyBot): {X}").strip()
    if not bot:
        print(f"{R}❌ Bot username tidak boleh kosong.{X}")
        return
    if not bot.startswith('@'):
        bot = '@' + bot

    custom = input(f"{G}🔗 URL khusus (opsional, Enter untuk auto): {X}").strip()
    custom = custom if custom else None

    print(f"\n{C}🔍 Mengambil tgWebAppData dari {bot}...{X}")
    init_data = await get_initdata_from_bot(bot, custom)

    if not init_data:
        print(f"{Y}⚠️ Gagal otomatis. Masukkan manual.{X}")
        init_data = input(f"{G}📝 Paste tgWebAppData lengkap: {X}").strip()
        if not init_data:
            print(f"{R}❌ Data kosong. Keluar.{X}")
            return

    # Parse dan tampilkan
    parsed = parse_initdata(init_data)
    print_parsed(parsed)

    # Simpan
    save_initdata(init_data, "query_data.txt")

    # Opsi kirim ke API (jika ada)
    api_url = input(f"\n{G}🚀 Kirim ke API? (masukkan URL atau Enter skip): {X}").strip()
    if api_url:
        send_to_api(init_data, api_url)

    print(f"\n{GOLD}{'═' * 60}{X}")
    print(f"{G}✅ Selesai! Data tersimpan di query_data.txt{X}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Y}⚠️ Dibatalkan.{X}")
        sys.exit(0)
