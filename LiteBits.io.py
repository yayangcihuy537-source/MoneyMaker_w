#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LiteBits.io Auto Claim Autopilot Bot
Real-Time Server Synchronization (Balance & Cooldown)
Dynamic Captcha Detection & Real-Time Card UI (Waryono API)
"""

import time
import json
import re
import os
import sys
import webbrowser
from datetime import datetime, timezone, timedelta

# Fix Windows stdout encoding for UTF-8 terminals
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# ANSI Terminal Colors
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    G   = Fore.GREEN   + Style.BRIGHT
    Y   = Fore.YELLOW  + Style.BRIGHT
    R   = Fore.RED     + Style.BRIGHT
    C   = Fore.CYAN    + Style.BRIGHT
    M   = Fore.MAGENTA + Style.BRIGHT
    W   = Fore.WHITE   + Style.BRIGHT
    B   = Fore.BLUE    + Style.BRIGHT
    DIM = Style.DIM
    RESET = Style.RESET_ALL
except ImportError:
    G = Y = R = C = M = W = B = DIM = RESET = ""

CONFIG_FILE = "config.json"
API_BASE    = "https://api.litebits.io"
SITE_BASE   = "https://litebits.io"
BAS_BASE    = "https://api.waryono.my.id" 
REF_URL     = "https://litebits.io/ref/3AU5MQ1X"

TURNSTILE_SITEKEY = "0x4AAAAAAAzzCfGXT_ftSwS2"
RECAPTCHA_SITEKEY = "6LeXpoArAAAAAGUUu0WVKiCb_yHUXSFqC0TUqDQE"

ADS_WAIT = 15    # 15 seconds ad viewing duration

# Animasi jam analog
CLOCK_FRAMES = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    now_utc = datetime.now(timezone.utc)
    wib_time = now_utc + timedelta(hours=7)
    wib_str = wib_time.strftime("%d-%m-%Y | %H:%M:%S WIB")

    print(f"\n{C}  _    _ _       _     _ _{RESET}")
    print(f"{C} | |  (_) |_ ___| |__ (_) |_ ___{RESET}")
    print(f"{C} | |__| | __/ _ \ '_ \| | __/ __|{RESET}")
    print(f"{C} |____|_|\__\___/_.__/|_|\__\___| {G}v2.0{RESET}")
    print(f"\n{Y}  ⚡ {W}AHD1905 {C}•{W} SCRIPTIXSOU {C}•{W} WARYONO {Y}⚡{RESET}")
    print(f"         {DIM}{wib_str}{RESET}")
    print(f"{M}  {'━'*40}{RESET}\n")

def print_dashboard_card(user_info, session_earned):
    email = str(user_info.get('email', 'Unknown'))
    if len(email) > 23:
        email = email[:20] + "..."
        
    balance = str(user_info.get('balance', '0.0000'))
    bal_str = f"{balance} Coins"
    earn_str = f"+{session_earned:.4f} Coins"

    # Frame diubah menjadi warna HIJAU ({G})
    print(f"{G}╭{'─'*40}╮")
    print(f"{G}│ {W}👤 Akun    : {C}{email:<25}{G}│")
    print(f"{G}├{'─'*40}┤")
    print(f"{G}│ {W}💰 Saldo   : {Y}{bal_str:<25}{G}│")
    print(f"{G}│ {W}📈 Didapat : {G}{earn_str:<25}{G}│")
    print(f"{G}╰{'─'*40}╯{RESET}\n")


class LiteBitsBot:

    def __init__(self):
        self.session          = None
        self.bas_key          = "1RPl20njseu1VbjdqdaWxR2nZTFvvwCU"
        self.auth_token       = ""
        self.cookie_str       = ""
        self.user_agent       = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        self.session_earned   = 0.0
        self.cycles           = 0
        self.user_info        = {}
        self.cooldown_seconds = 297   # default 5 minutes
        self.running          = True
        self.cycle_logs       = []

    def render_view(self, live_line=None):
        clear()
        print_banner()
        print_dashboard_card(self.user_info, self.session_earned)
        for entry in self.cycle_logs:
            print(entry)
        if live_line:
            print(f"\n {B}❯{RESET} {live_line}")

    def add_log(self, level, msg):
        now_wib = (datetime.now(timezone.utc) + timedelta(hours=7)).strftime("%H:%M:%S")
        icons = {
            'ok':   f"{G}[✓]{RESET}",
            'err':  f"{R}[✗]{RESET}",
            'info': f"{C}[i]{RESET}",
            'wait': f"{Y}[~]{RESET}",
            'warn': f"{Y}[!]{RESET}",
            'star': f"{M}[★]{RESET}",
        }
        icon = icons.get(level, f"{C}[·]{RESET}")
        self.cycle_logs.append(f" {DIM}[{now_wib}]{RESET} {icon} {W}{msg}{RESET}")
        self.render_view()

    def get_clock(self, tick):
        """Mengambil frame jam analog berdasarkan tick"""
        return CLOCK_FRAMES[tick % 12]

    def init_session(self):
        try:
            from curl_cffi import requests as c_requests
            self.session = c_requests.Session(impersonate="chrome120")
        except ImportError:
            try:
                import cloudscraper
                self.session = cloudscraper.create_scraper(
                    browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
                )
            except ImportError:
                import requests
                self.session = requests.Session()

        self.apply_headers()

    def apply_headers(self):
        headers = {
            'User-Agent': self.user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Origin': SITE_BASE,
            'Referer': f"{SITE_BASE}/dashboard",
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
        }
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        if self.cookie_str:
            headers['Cookie'] = self.cookie_str

        if hasattr(self.session, 'headers'):
            self.session.headers.update(headers)

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            return False
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
            self.bas_key    = cfg.get('bas_key', self.bas_key)
            self.auth_token = cfg.get('auth_token', '')
            self.cookie_str = cfg.get('cookie', '')
            self.user_agent = cfg.get('user_agent', self.user_agent)
            return True
        except Exception:
            return False

    def save_config(self):
        cfg = {
            'bas_key': self.bas_key,
            'auth_token': self.auth_token,
            'cookie': self.cookie_str,
            'user_agent': self.user_agent
        }
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    def check_bas_api(self):
        try:
            import requests
            r = requests.get(f"{BAS_BASE}/res.php", params={'apikey': self.bas_key, 'action': 'getbalance'}, timeout=10)
            return True 
        except Exception:
            return False

    def silent_init(self):
        try:
            webbrowser.open(REF_URL)
        except Exception:
            pass
        try:
            self.session.get(REF_URL, timeout=10, allow_redirects=True)
        except Exception:
            pass

    def fetch_app_settings(self):
        url = f"{API_BASE}/api/app-settings"
        try:
            r = self.session.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                interval_hrs = float(data.get('claimInterval', 0.0825))
                self.cooldown_seconds = max(60, int(interval_hrs * 3600))
                return True
        except Exception:
            pass
        return False

    def fetch_user_profile(self):
        url = f"{API_BASE}/api/user/profile"
        try:
            headers = {
                'Authorization': f"Bearer {self.auth_token}",
                'Origin': SITE_BASE,
                'Referer': f"{SITE_BASE}/dashboard",
                'Accept': 'application/json'
            }
            if self.cookie_str:
                headers['Cookie'] = self.cookie_str

            r = self.session.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                data = r.json()
                if data.get('success') and data.get('user'):
                    self.user_info = data['user']
                    return True
                elif 'balance' in data or 'email' in data:
                    self.user_info = data
                    return True
            return False
        except Exception:
            return False

    def get_server_cooldown_left(self):
        last_claim_str = self.user_info.get('lastClaim')
        if not last_claim_str:
            return 0

        try:
            last_dt = datetime.fromisoformat(last_claim_str.replace('Z', '+00:00'))
            now_dt = datetime.now(timezone.utc)
            passed = int((now_dt - last_dt).total_seconds())
            remaining = max(0, self.cooldown_seconds - passed)
            return remaining
        except Exception:
            return 0

    def extract_token_from_input(self, raw_input):
        raw_input = raw_input.strip()
        if "auth-storage" in raw_input or '"token"' in raw_input or '"state"' in raw_input:
            try:
                clean_json = raw_input
                if "auth-storage:" in raw_input:
                    clean_json = raw_input.split("auth-storage:", 1)[1].strip()
                data = json.loads(clean_json)
                token = data.get('state', {}).get('token') or data.get('token')
                if token:
                    return token
            except Exception:
                m = re.search(r'"token"\s*:\s*"([^"]+)"', raw_input)
                if m:
                    return m.group(1)

        if raw_input.startswith("Bearer "):
            return raw_input.replace("Bearer ", "").strip()
        if raw_input.startswith("eyJ"):
            return raw_input
        return raw_input

    def setup_interactive(self):
        clear()
        print_banner()
        self.load_config()
        self.check_bas_api()
        self.fetch_app_settings()

        valid_auth = False
        if self.auth_token:
            if self.fetch_user_profile():
                valid_auth = True
                user_label = self.user_info.get('email') or self.user_info.get('username') or 'User'
                print(f" {G}[✓]{RESET} {W}Session active for {G}{user_label}{RESET}")

        if valid_auth:
            print(f"\n {C}❖{RESET} {W}Main Menu:{RESET}")
            print(f"   {C}1.{RESET} Start Auto Claim (Default)")
            print(f"   {C}2.{RESET} Update Auth Token")
            print(f"   {C}3.{RESET} Update API Key")
            choice = input(f"\n {C}❯{RESET} {W}Pilih opsi (default 1): {G}").strip()
            print(RESET, end='')
        else:
            self.silent_init()
            choice = '2'

        if choice == '2':
            print(f"\n{Y}Cara ambil Auth Token dari browser:{RESET}")
            print(f"  1. Login di: {W}{REF_URL}{RESET}")
            print(f"  2. DevTools (F12) -> Tab {W}Application{RESET} -> {W}Local Storage{RESET}.")
            print(f"  3. Copy isi dari {G}auth-storage{RESET}.\n")

            user_in = input(f"{W}Paste auth-storage / Token: {G}").strip()
            print(RESET, end='')
            if user_in:
                token = self.extract_token_from_input(user_in)
                self.auth_token = token
                self.apply_headers()

                if self.fetch_user_profile():
                    self.save_config()
                else:
                    print(f"\n {R}[✗]{RESET} {W}Token invalid/expired.{RESET}")
                    time.sleep(2)
                    return False

        elif choice == '3':
            key_in = input(f"\n{W}Masukkan Waryono API Key: {G}").strip()
            print(RESET, end='')
            if key_in:
                self.bas_key = key_in
                self.save_config()
                self.check_bas_api()

        return True

    # ── Dynamic Captcha Solver ───────────────────────────────────────────────
    def solve_captcha(self, provider="turnstile"):
        sitekey = TURNSTILE_SITEKEY if provider == "turnstile" else RECAPTCHA_SITEKEY
        method = "turnstile" if provider == "turnstile" else "userrecaptcha"
        label = "Turnstile" if provider == "turnstile" else "reCAPTCHA v2"

        self.add_log('info', f"Challenge: {C}{label}{RESET} — Solving...")
        start_t = time.time()

        try:
            import requests
            
            payload = {
                'apikey': self.bas_key,
                'methods': method,
                'domain': f"{SITE_BASE}/dashboard",
                'sitekey': sitekey,
                'json': 1 
            }
            
            if provider == "recaptcha":
                payload['version'] = "2" 

            r = requests.post(f"{BAS_BASE}/in.php", json=payload, timeout=25)
            
            task_id = None
            try:
                res_json = r.json()
                if res_json.get("status") == 1:
                    task_id = str(res_json.get("request"))
                else:
                    self.add_log('err', f"Submit error: {res_json.get('request')}")
            except Exception:
                raw_text = r.text.strip()
                if 'OK|' in raw_text:
                    task_id = raw_text.replace('OK|', '').strip()
                else:
                    self.add_log('err', f"Submit error: {raw_text}")
                
            if not task_id:
                return None

            for poll in range(35):
                time.sleep(3)
                res = requests.get(
                    f"{BAS_BASE}/res.php",
                    params={'apikey': self.bas_key, 'action': 'get', 'id': task_id},
                    timeout=15
                )

                try:
                    poll_json = res.json()
                    status = poll_json.get("status")
                    request_msg = poll_json.get("request")

                    if status == 1:
                        elapsed = int(time.time() - start_t)
                        self.add_log('ok', f"{label} Solved! {DIM}({elapsed}s){RESET}")
                        return str(request_msg)
                    elif status == 0:
                        if request_msg == "CAPCHA_NOT_READY":
                            self.render_view(f"{self.get_clock(poll)} Solving {label} ({poll+1}/35)")
                            continue
                        else:
                            self.add_log('err', f"Solver error: {request_msg}")
                            return None
                except Exception:
                    solution = res.text.strip()
                    if 'OK|' in solution:
                        solution_token = solution.replace('OK|', '').strip()
                        elapsed = int(time.time() - start_t)
                        self.add_log('ok', f"{label} Solved! {DIM}({elapsed}s){RESET}")
                        return solution_token
                    elif 'CAPCHA_NOT_READY' in solution:
                        self.render_view(f"{self.get_clock(poll)} Solving {label} ({poll+1}/35)")
                        continue
                    else:
                        self.add_log('err', f"Solver error: {solution}")
                        return None
                    
                self.render_view(f"{self.get_clock(poll)} Solving {label} ({poll+1}/35)")

            self.add_log('err', f"{label} timeout.")
            return None

        except Exception as e:
            self.add_log('err', f"Exception: {e}")
            return None

    # ── Claim Execution ──────────────────────────────────────────────────────
    def do_claim(self):
        self.fetch_user_profile()

        time_left = self.get_server_cooldown_left()
        if time_left > 0:
            return True, "Cooldown"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {self.auth_token}",
            'Origin': SITE_BASE,
            'Referer': f"{SITE_BASE}/dashboard",
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': self.user_agent
        }

        provider = "turnstile"
        token = self.solve_captcha(provider="turnstile")

        if not token:
            self.add_log('warn', "Mencoba fallback reCAPTCHA v2...")
            provider = "recaptcha"
            token = self.solve_captcha(provider="recaptcha")

        if not token:
            return False, "Captcha Failed"

        self.add_log('info', f"Verifikasi claim ({provider})...")
        start_payload = {
            "cf-turnstile-response" if provider == "turnstile" else "g-recaptcha-response": token,
            "captchaProvider": provider
        }

        start_url = f"{API_BASE}/api/claim/start"
        try:
            r = self.session.post(start_url, json=start_payload, headers=headers, timeout=20)
            resp_data = r.json()
        except Exception as e:
            self.add_log('err', f"Dispatch error: {e}")
            return False, str(e)

        if not resp_data.get('success') and resp_data.get('requiresV2'):
            self.add_log('warn', "Server butuh reCAPTCHA v2...")
            provider = "recaptcha"
            v2_token = self.solve_captcha(provider="recaptcha")
            if not v2_token:
                return False, "reCAPTCHA v2 failed"

            start_payload = {
                "g-recaptcha-response": v2_token,
                "captchaProvider": "recaptcha"
            }
            r = self.session.post(start_url, json=start_payload, headers=headers, timeout=20)
            resp_data = r.json()

        if not resp_data.get('success') or not resp_data.get('claimId'):
            err_msg = resp_data.get('message', 'Ditolak server')
            self.add_log('err', f"Server: {err_msg}")
            return False, err_msg

        claim_id = resp_data.get('claimId')
        self.add_log('ok', f"Claim Init! {DIM}({claim_id[:8]}...){RESET}")

        ads_url_ep = f"{API_BASE}/api/claim/{claim_id}/ads"
        try:
            r_ads = self.session.get(ads_url_ep, headers=headers, timeout=15)
            if r_ads.status_code == 200:
                ads_json = r_ads.json()
                if ads_json.get('success') and ads_json.get('adsUrl'):
                    ads_target = ads_json['adsUrl'].get('url', '')
                    self.add_log('info', f"Ad: {DIM}{ads_target[:30]}...{RESET}")
        except Exception:
            pass

        self.add_log('info', f"Menunggu Ad ({ADS_WAIT}s)...")
        tick = 0
        for sec in range(ADS_WAIT, 0, -1):
            self.render_view(f"{self.get_clock(tick)} Ad view: {sec:>2}s tersisa")
            time.sleep(1)
            tick += 1

        complete_url = f"{API_BASE}/api/claim/{claim_id}/complete"
        self.add_log('info', "Konfirmasi claim...")
        amount_awarded = 0.6
        try:
            r_comp = self.session.post(complete_url, json={}, headers=headers, timeout=20)
            comp_data = r_comp.json()
            if comp_data.get('success'):
                amount_awarded = comp_data.get('reward', 0.6)
            else:
                self.add_log('warn', f"Note: {comp_data.get('message')}")
        except Exception as e:
            self.add_log('err', f"Konfirmasi error: {e}")

        time.sleep(1)
        self.fetch_user_profile()
        try:
            self.session_earned += float(str(amount_awarded))
        except Exception:
            pass
        self.cycles += 1

        self.add_log('star', f"{G}Sukses! Reward: +{amount_awarded} Coins{RESET}")
        return True, amount_awarded

    def live_cooldown(self):
        tick = 0
        while self.running:
            time_left = self.get_server_cooldown_left()
            if time_left <= 0:
                self.render_view(f"{G}⚡{RESET} Cooldown selesai!")
                time.sleep(1)
                break

            m, s = divmod(time_left, 60)
            self.render_view(f"{self.get_clock(tick)} Cooldown: {Y}{m:02d}:{s:02d}{RESET}")
            time.sleep(1)
            tick += 1

    def run(self):
        self.init_session()

        if not self.setup_interactive():
            sys.exit(1)

        while self.running:
            try:
                self.fetch_user_profile()
                self.fetch_app_settings()
                time_left = self.get_server_cooldown_left()

                self.cycle_logs.clear()
                self.render_view()

                if time_left > 0:
                    self.live_cooldown()
                    self.fetch_user_profile()
                    self.cycle_logs.clear()
                    self.render_view()

                ok, res = self.do_claim()

                if not ok:
                    self.add_log('warn', "Gagal. Retrying (30s)...")
                    time.sleep(30)
                    continue

                # ----- Fitur Bertahan 2 Detik Lalu Clear -----
                # Setelah tugas selesai (cycle komplit), tahan layar 2 detik
                time.sleep(2)
                
                # Kosongkan log print agar bersih untuk tugas selanjutnya
                self.cycle_logs.clear()
                self.render_view()
                # -----------------------------------------------

                self.live_cooldown()

            except KeyboardInterrupt:
                clear()
                print(f"\n {Y}Bot dihentikan user.{RESET}\n")
                self.save_config()
                break
            except Exception as e:
                self.add_log('err', f"Loop exception: {e}")
                time.sleep(15)


if __name__ == '__main__':
    bot = LiteBitsBot()
    bot.run()


#Created by AHD1905
