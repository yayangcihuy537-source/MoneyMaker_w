import requests
import json
import time
import sys
import os
import re
from colorama import Fore, Style, init
from pyfiglet import figlet_format

init(autoreset=True)

# ==================================================
# BANNER pyfiglet
# ==================================================
def print_banner():
    banner = figlet_format("CryptoFuture", font="slant")
    print(Fore.LIGHTRED_EX + banner + Style.RESET_ALL)
    print(Fore.WHITE + "           🚀 AUTO CRYPTO FUTURE 🚀")
    print(Fore.LIGHTRED_EX + "           👨‍💻 DEV: @ScriptyXSou")

# ==================================================
# KONFIGURASI
# ==================================================
DEFAULT_DELAY = 10
BASE_URL = "https://cryptofuture.co.in"
LOGIN_URL = f"{BASE_URL}/actions/auth.php"
CLAIM_URL = f"{BASE_URL}/api/claim_faucet.php"
FAUCET_PAGE = f"{BASE_URL}/pages/load_faucet.php"
CONFIG_FILE = "config.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "id-ID",
    "Sec-Ch-Ua": '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
    "Sec-Ch-Ua-Mobile": "?1",
    "Sec-Ch-Ua-Platform": '"Android"',
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Referer": f"{BASE_URL}/index.php",
}

# ==================================================
# CONFIG
# ==================================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def save_config(email, delay):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"email": email, "delay": delay}, f, indent=4)

def get_user_input():
    config = load_config()
    email = None
    delay = DEFAULT_DELAY

    if config:
        stored_email = config.get("email", "").strip()
        if stored_email:
            print(Fore.GREEN + "[✓] Konfigurasi ditemukan. Memakai data tersimpan.")
            return stored_email, config.get("delay", DEFAULT_DELAY)
        else:
            print(Fore.YELLOW + "[!] Konfigurasi tidak memiliki email yang valid. Masukkan ulang.")

    while not email or not email.strip():
        email = input(Fore.YELLOW + "[?] Masukkan email akun: ").strip()
        if not email:
            print(Fore.RED + "[!] Email tidak boleh kosong.")

    save_config(email, delay)
    print(Fore.CYAN + f"[*] Menggunakan delay default: {delay} detik.")
    return email, delay

# ==================================================
# FUNGSI AMBIL BALANCE DARI HALAMAN FAUCET
# ==================================================
def fetch_balance(session):
    try:
        resp = session.get(FAUCET_PAGE, headers=HEADERS)
        if resp.status_code == 200:
            # Cari data-balance="..." di HTML
            match = re.search(r'data-balance="([\d.]+)"', resp.text)
            if match:
                return float(match.group(1))
    except:
        pass
    return None

# ==================================================
# LOGIN
# ==================================================
def login(session, email):
    print(Fore.CYAN + "[*] Logging in as " + email + " ...")
    data = {"identifier": email, "remember_browser": "1"}
    try:
        resp = session.post(LOGIN_URL, data=data, headers=HEADERS, allow_redirects=False)
        if resp.status_code in [302, 303] and "index.php" in resp.headers.get("Location", ""):
            print(Fore.GREEN + "[✓] Login successful!")
            print(Fore.CYAN + "[*] Mengunjungi index.php untuk memantapkan session...")
            session.get(BASE_URL + "/index.php", headers=HEADERS)
            return True
        else:
            print(Fore.RED + "[!] Login gagal. Status:", resp.status_code)
            print(Fore.RED + resp.text[:200])
            return False
    except Exception as e:
        print(Fore.RED + "[!] Error saat login:", e)
        return False

# ==================================================
# FUNGSI CETAK HASIL CLAIM
# ==================================================
def print_result(attempt, reward, balance, claims_today, daily_limit, status, wait_time=None):
    print("=" * 46)
    print("             💰 CryptoFuture")
    print("=" * 46)

    if status == "success":
        print(f"🔄 Attempt : #{attempt}")
        print(f"🪙 Reward  : +{reward} Coins")
        print(f"💰 Balance : {balance:.2f} Coins")
        print(f"✅ Status  : SUCCESS")
        print(f"⏳ Cooldown: {wait_time or 10}s")
    elif status == "cooldown":
        print(f"🔄 Attempt : #{attempt}")
        print(f"⏳ Status  : COOLDOWN")
        print(f"⏱️  Wait    : {wait_time}s")
    elif status == "limit":
        print(f"🔄 Attempt : #{attempt}")
        print(f"🚫 Status  : DAILY LIMIT REACHED")
        print(f"📊 Today   : {claims_today} / {daily_limit}")
    else:  # error
        print(f"🔄 Attempt : #{attempt}")
        print(f"❌ Status  : ERROR")
        if wait_time:
            print(f"💬 Message : {wait_time}")

    print("=" * 46)
    print("👨‍💻 DEV : @ScriptyXSou")
    print("=" * 46)

# ==================================================
# FUNGSI CLAIM
# ==================================================
def claim(session, attempt_number):
    try:
        api_headers = {
            **HEADERS,
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/index.php",
            "X-Requested-With": "XMLHttpRequest",
        }
        resp = session.post(CLAIM_URL, data="", headers=api_headers)

        if resp.status_code == 200:
            try:
                data = resp.json()
            except:
                text = resp.content.decode('utf-8', errors='replace')
                data = json.loads(text)

            status = data.get("status")
            reward = data.get("reward", "0")
            new_balance = data.get("new_balance", "0")  # dari JSON, tapi tidak akurat
            claims_today = data.get("claims_today", 0)
            daily_limit = data.get("daily_limit", 250)
            cooldown = data.get("cooldown", 10)

            if status == 200:
                # Ambil balance real dari halaman faucet
                real_balance = fetch_balance(session)
                if real_balance is None:
                    real_balance = float(new_balance)  # fallback

                return {
                    "status": "success",
                    "reward": reward,
                    "balance": real_balance,
                    "claims_today": claims_today,
                    "daily_limit": daily_limit,
                    "cooldown": cooldown
                }
            elif status == 429:
                wait = data.get("wait", cooldown)
                return {
                    "status": "cooldown",
                    "wait": wait,
                    "claims_today": claims_today,
                    "daily_limit": daily_limit
                }
            elif status == 403 and data.get("daily_limit_reached"):
                return {
                    "status": "limit",
                    "claims_today": claims_today,
                    "daily_limit": daily_limit
                }
            else:
                return {
                    "status": "error",
                    "message": data.get("message", "Unknown error")
                }
        else:
            return {
                "status": "error",
                "message": f"HTTP {resp.status_code}"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# ==================================================
# MAIN
# ==================================================
def main():
    print_banner()

    email, delay = get_user_input()

    session = requests.Session()
    session.headers.update(HEADERS)

    if not login(session, email):
        print(Fore.RED + "[!] Proses berhenti karena login gagal.")
        sys.exit(1)

    # Ambil balance awal
    initial_balance = fetch_balance(session)
    if initial_balance is not None:
        print(Fore.CYAN + f"[*] Saldo awal: {initial_balance:.2f} Coins")
    else:
        print(Fore.YELLOW + "[!] Gagal mengambil saldo awal.")

    attempt = 1
    success_count = 0

    while True:
        result = claim(session, attempt)

        if result["status"] == "success":
            print_result(
                attempt=attempt,
                reward=result["reward"],
                balance=result["balance"],
                claims_today=result["claims_today"],
                daily_limit=result["daily_limit"],
                status="success",
                wait_time=delay
            )
            success_count += 1
            attempt += 1

            print(Fore.YELLOW + f"[*] Menunggu {delay} detik...")
            time.sleep(delay)

        elif result["status"] == "cooldown":
            wait = result["wait"]
            # ambil balance saat ini (tidak berubah)
            current_balance = fetch_balance(session)
            if current_balance is None:
                current_balance = 0.0
            print_result(
                attempt=attempt,
                reward="?",
                balance=current_balance,
                claims_today=result["claims_today"],
                daily_limit=result["daily_limit"],
                status="cooldown",
                wait_time=wait
            )
            print(Fore.YELLOW + f"[*] Cooldown {wait} detik, akan mencoba lagi...")
            time.sleep(wait)
            # tidak menambah attempt, loop lagi

        elif result["status"] == "limit":
            # ambil balance terakhir
            current_balance = fetch_balance(session)
            if current_balance is None:
                current_balance = 0.0
            print_result(
                attempt=attempt,
                reward="?",
                balance=current_balance,
                claims_today=result["claims_today"],
                daily_limit=result["daily_limit"],
                status="limit"
            )
            break

        else:  # error
            print_result(
                attempt=attempt,
                reward="?",
                balance="?",
                claims_today="?",
                daily_limit="?",
                status="error",
                wait_time=result.get("message", "Unknown error")
            )
            break

    print(Fore.GREEN + f"\n[✓] Selesai! Total claim berhasil: {success_count} kali.")
    print(Fore.YELLOW + "[*] Tekan Ctrl+C untuk keluar, atau jalankan ulang untuk melanjutkan di hari berikutnya.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n[!] Dihentikan oleh user.")
