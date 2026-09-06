#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║              ⚡ A D C O I N S   A U T O   B O T ⚡              ║
║   🔥 FAUCET • PTC • AUTO EARN • MODERN DASHBOARD               ║
║   📊 LIVE STATUS • COLORFUL UI • EMOJI SUPPORT                 ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os, re, json, sys, time, base64, platform, subprocess, logging, requests
from bs4 import BeautifulSoup

# --- Windows Compatibility Fix ---
if platform.system() == 'Windows':
    sys.stdout.reconfigure(encoding='utf-8') if hasattr(sys.stdout, 'reconfigure') else None
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except: pass

# --- Warna (256-Color Codes) ---
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

RED = "\033[38;5;196m"
GREEN = "\033[38;5;46m"
YELLOW = "\033[38;5;226m"
CYAN = "\033[38;5;51m"
MAGENTA = "\033[38;5;201m"
BLUE = "\033[38;5;39m"
WHITE = "\033[38;5;15m"
GRAY = "\033[38;5;245m"
ORANGE = "\033[38;5;208m"
PINK = "\033[38;5;205m"

# --- Konstanta ---
CONFIG_FILE = "BAS_config.json"
API_KEY_FILE = "BASkey.txt"
BASE_URL = 'https://adcoins.cc'
SITE_URL = 'https://bypassallshortlinks.space'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WEBSITE_NAME = "AdCoins.cc"
TURNSTILE_SITEKEY = '0x4AAAAAACyaNDdvQo-05xXY'

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')
def ansi_len(text): return len(ANSI_RE.sub('', text))
def clear_screen(): os.system('cls' if platform.system() == 'Windows' else 'clear')
def safe_print(text):
    try: print(text)
    except UnicodeEncodeError: print(re.sub(r'[^\x00-\x7F]+', '', text))

# ==========================================
#  DASHBOARD v3.0 (Modern Cyberpunk UI)
# ==========================================
class Dashboard:
    def __init__(self):
        self.logs = []
        self.max_logs = 6
        self.status_mode = "Idle"
        self.claim_count = 0
        self.total_earned = 0.0
        self.balance = 0.0
        self.last_action = ""
        self.next_action = ""

    def redraw(self):
        print('\033[H\033[2J', end='')
        print('\033[?25l', end='')
        w = 50

        # --- HEADER ---
        print(f"{CYAN}╭{'─' * w}╮{RESET}")
        print(f"{CYAN}│{RESET}{MAGENTA}{BOLD}     ⚡  A D C O I N S   A U T O   B O T  ⚡{RESET}{' ' * (w - 48)}{CYAN}│{RESET}")
        print(f"{CYAN}╰{'─' * w}╯{RESET}")
        
        # --- INFO BOX ---
        print(f"{BLUE}┌{'─' * w}┐{RESET}")
        print(f"{BLUE}│{RESET}{BOLD}{CYAN}  🌐 WEBSITE & FUNCTIONS{RESET}{' ' * (w - 26)}{BLUE}│{RESET}")
        print(f"{BLUE}├{'─' * w}┤{RESET}")
        def info_line(label, value):
            text = f"  {label} : {value}"
            print(f"{BLUE}│{RESET} {text}{' ' * (w - ansi_len(text) - 2)}{BLUE}│{RESET}")
        info_line("Website", WHITE + WEBSITE_NAME)
        info_line("Functions", WHITE + "FAUCET | PTC")
        print(f"{BLUE}└{'─' * w}┘{RESET}")

        # --- DASHBOARD STATUS BOX ---
        print(f"\n{MAGENTA}┌{'─' * w}┐{RESET}")
        print(f"{MAGENTA}│{RESET}{BOLD}{YELLOW}  📊  L I V E   D A S H B O A R D{RESET}{' ' * (w - 32)}{MAGENTA}│{RESET}")
        print(f"{MAGENTA}├{'─' * w}┤{RESET}")
        def status_line(label, value, color=WHITE):
            text = f"  {label} : {color}{BOLD}{value}{RESET}"
            print(f"{MAGENTA}│{RESET} {text}{' ' * (w - ansi_len(text) - 2)}{MAGENTA}│{RESET}")
        
        status_line("🚀 Mode", self.status_mode, CYAN)
        status_line("🎮 Claim #", self.claim_count, BLUE)
        status_line("💰 Earned", f"{self.total_earned:.2f} Coins", GREEN)
        status_line("💎 Balance", f"{self.balance:.2f} Coins", GREEN)
        status_line("⚡ Status", self.last_action, ORANGE)
        status_line("⏳ Next In", self.next_action, YELLOW)
        print(f"{MAGENTA}└{'─' * w}┘{RESET}")

        # --- LOGS BOX ---
        print(f"\n{CYAN}┌{'─' * w}┐{RESET}")
        print(f"{CYAN}│{RESET}{BOLD}{PINK}  📜  S Y S T E M   L O G S{RESET}{' ' * (w - 27)}{CYAN}│{RESET}")
        print(f"{CYAN}├{'─' * w}┤{RESET}")
        for i in range(self.max_logs):
            if i < len(self.logs):
                raw_log = self.logs[i]
                if "[+]" in raw_log: color = GREEN
                elif "[-]" in raw_log: color = RED
                elif "[*]" in raw_log: color = BLUE
                else: color = WHITE
                log_text = ANSI_RE.sub('', raw_log)
                if len(log_text) > w - 4: log_text = log_text[:w-5] + "..."
                print(f"{CYAN}│{RESET} {color}{log_text:<{w-2}}{RESET}{CYAN}│{RESET}")
            else:
                print(f"{CYAN}│{RESET} {' ' * (w-2)}{CYAN}│{RESET}")
        print(f"{CYAN}└{'─' * w}┘{RESET}")
        print('\033[?25h', end='')

    def update_status(self, mode=None, claim_count=None, total_earned=None, balance=None, last_action=None, next_action=None):
        if mode is not None: self.status_mode = mode
        if claim_count is not None: self.claim_count = claim_count
        if total_earned is not None: self.total_earned = total_earned
        if balance is not None: self.balance = balance
        if last_action is not None: self.last_action = last_action
        if next_action is not None: self.next_action = next_action
        self.redraw()

    def add_log(self, message):
        self.logs.append(message)
        if len(self.logs) > self.max_logs: self.logs.pop(0)
        self.redraw()

dashboard = Dashboard()

# ==========================================
#  FUNGSI INPUT & KONFIGURASI
# ==========================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}

def save_config(config_data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f: json.dump(config_data, f, indent=4)

def get_email():
    config = load_config()
    if 'email' in config:
        safe_print(f"{GREEN}[+] Menggunakan email tersimpan{RESET}")
        return config['email']
    safe_print(f"{YELLOW}[!] Masukkan email Anda:{RESET}")
    email = input(f"{CYAN}📧 Email: {RESET}").strip()
    if email:
        config['email'] = email
        save_config(config)
    return email

def get_bas_api_key():
    if os.path.exists(API_KEY_FILE):
        try:
            with open(API_KEY_FILE, 'r', encoding='utf-8') as f:
                key = f.read().strip()
                if key: return key
        except: pass
    safe_print(f"{YELLOW}[!] Masukkan BAS API key:{RESET}")
    api_key = input(f"{CYAN}🔑 BAS API Key: {RESET}").strip()
    if api_key:
        with open(API_KEY_FILE, 'w', encoding='utf-8') as f: f.write(api_key)
        safe_print(f"{GREEN}[+] API key disimpan{RESET}")
    return api_key

def config_menu():
    clear_screen()
    print(f"\n{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    print(f"{BOLD}{BLUE}⚙️  KONFIGURASI AKUN & API KEY{RESET}")
    print(f"{CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
    
    email = get_email()
    api_key = get_bas_api_key()
    
    print(f"\n{BLUE}📧 Email saat ini: {YELLOW}{email}{RESET}")
    print(f"{BLUE}🔑 API Key saat ini: {YELLOW}{api_key[:8]}...{api_key[-4:] if len(api_key)>12 else ''}{RESET}")
    
    print(f"\n{CYAN}[1] {WHITE}Ubah Email{RESET}")
    print(f"{CYAN}[2] {WHITE}Ubah API Key{RESET}")
    print(f"{CYAN}[0] {WHITE}Kembali{RESET}")
    choice = input(f"\n{CYAN}Pilih: {RESET}").strip()
    
    if choice == '1':
        new_email = input(f"{CYAN}📧 Email baru: {RESET}").strip()
        if new_email:
            config = load_config()
            config['email'] = new_email
            save_config(config)
            print(f"{GREEN}✅ Email berhasil diupdate!{RESET}")
        else:
            print(f"{RED}❌ Email tidak boleh kosong!{RESET}")
        time.sleep(1.5)
        config_menu()
    elif choice == '2':
        new_api = input(f"{CYAN}🔑 API Key baru: {RESET}").strip()
        if new_api:
            with open(API_KEY_FILE, 'w', encoding='utf-8') as f:
                f.write(new_api)
            print(f"{GREEN}✅ API Key berhasil diupdate!{RESET}")
        else:
            print(f"{RED}❌ API Key tidak boleh kosong!{RESET}")
        time.sleep(1.5)
        config_menu()
    elif choice == '0':
        return
    else:
        print(f"{RED}❌ Pilihan tidak valid{RESET}")
        time.sleep(1)
        config_menu()

# ==========================================
#  FUNGSI SOLVING CAPTCHA
# ==========================================
def bas_submit(api_key, method, **kwargs):
    payload = {'api_key': api_key, 'method': method}
    payload.update(kwargs)
    for _ in range(3):
        try:
            resp = requests.post(f"{SITE_URL}/in.php", json=payload, timeout=30)
            text = resp.text.strip()
            if text.startswith('OK|'): return text[3:].strip()
            if 'RATE_LIMIT' in text:
                safe_print(f"{YELLOW}[*] Rate limited, tunggu...{RESET}")
                time.sleep(10); continue
        except: time.sleep(2)
    return None

def bas_poll(api_key, task_id, max_wait=120):
    for _ in range(max_wait // 3):
        time.sleep(3)
        try:
            resp = requests.get(f"{SITE_URL}/res.php", params={'key': api_key, 'action': 'get', 'id': task_id}, timeout=30)
            text = resp.text.strip()
            if text.startswith('OK|'): return text[3:].strip()
            if 'CAPCHA_NOT_READY' in text: continue
            return None
        except: continue
    return None

def solve_adcoins_captcha(api_key, image_b64):
    task_id = bas_submit(api_key, 'adcoins', image=image_b64)
    if not task_id: return None, None
    result = bas_poll(api_key, task_id)
    if result and ',' in result:
        parts = result.split(',')
        try: return int(parts[0]), int(parts[1])
        except: return None, None
    return None, None

def solve_turnstile(api_key, page_url=BASE_URL):
    for attempt in range(3):
        try:
            resp = requests.get(f"{SITE_URL}/in.php", params={'key': api_key, 'method': 'turnstile', 'sitekey': TURNSTILE_SITEKEY, 'pageurl': page_url, 'json': 1}, timeout=30)
            data = resp.json()
            if data.get('status') == 1:
                task_id = data['request']; break
        except:
            if attempt < 2: time.sleep(2)
            continue
    else: return None
    for _ in range(40):
        time.sleep(3)
        try:
            resp = requests.get(f"{SITE_URL}/res.php", params={'key': api_key, 'action': 'get', 'id': task_id, 'json': 1}, timeout=30)
            data = resp.json()
            if data.get('status') == 1: return data['request']
            if data.get('request', '') == 'CAPCHA_NOT_READY': continue
            return None
        except: continue
    return None

# ==========================================
#  FUNGSI WEBSITE
# ==========================================
def create_session():
    session = requests.Session()
    session.headers.update({
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8'})
    return session

def login(session, email):
    resp = session.post(f"{BASE_URL}/api.php", data={'action': 'login', 'email': email, 'csrf_token': ''}, headers={'origin': BASE_URL, 'referer': f"{BASE_URL}/faucet", 'content-type': 'application/x-www-form-urlencoded'})
    try: return resp.json()
    except: return {'success': False}

def get_balance(session):
    try:
        resp = session.get(f"{BASE_URL}/faucet", timeout=30)
        html = resp.text
        match = re.search(r'new_balance"?\s*:\s*([0-9.]+)', html)
        if match: return float(match.group(1))
        match = re.search(r'>([0-9.]+)\s*Coins<', html)
        if match: return float(match.group(1))
        match = re.search(r'Balance\s*:\s*([0-9.]+)', html)
        if match: return float(match.group(1))
        
        resp = session.get(f"{BASE_URL}/dashboard", timeout=30)
        html = resp.text
        match = re.search(r'new_balance"?\s*:\s*([0-9.]+)', html)
        if match: return float(match.group(1))
        match = re.search(r'>([0-9.]+)\s*Coins<', html)
        if match: return float(match.group(1))
    except Exception: pass
    return None

def get_slider_info(session):
    resp = session.get(f"{BASE_URL}/faucet")
    html = resp.text
    token_match = re.search(r"sliderToken:\s*'([^']+)'", html)
    target_match = re.search(r"sliderTarget:\s*(\d+)", html)
    return (token_match.group(1) if token_match else '', int(target_match.group(1)) if target_match else 50)

def generate_captcha(session):
    resp = session.post(f"{BASE_URL}/captcha/generate.php", headers={'origin': BASE_URL, 'referer': f"{BASE_URL}/faucet"})
    if resp.status_code != 200: return None, None, None
    token = resp.headers.get('x-n1-token', '')
    img_b64 = base64.b64encode(resp.content).decode()
    return img_b64, token, resp.content

def verify_captcha(session, token, cx, cy):
    resp = session.post(f"{BASE_URL}/captcha/verify.php", json={'token': token, 'answer': 'click', 'click_x': cx, 'click_y': cy}, headers={'origin': BASE_URL, 'referer': f"{BASE_URL}/faucet"})
    return resp.json()

def claim_faucet(session, captcha_token, slider_pos, n1_token=''):
    resp = session.post(f"{BASE_URL}/api.php", data={'action': 'claim', 'captcha_token': captcha_token, 'slider_position': str(slider_pos), 'hcaptcha_token': '', 'turnstile_token': '', 'n1_token': n1_token, 'n1_answer': 'verified'}, headers={'origin': BASE_URL, 'referer': f"{BASE_URL}/faucet"})
    return resp.json()

def parse_ptc_ads(html):
    ads = []
    for m in re.finditer(r'viewWindowAd\((\d+)\)"\s+data-title="([^"]+)"\s+data-url="([^"]+)"\s+data-duration="(\d+)"', html):
        ads.append({'id': int(m.group(1)), 'title': m.group(2), 'url': m.group(3), 'duration': int(m.group(4))})
    return ads

def create_ptc_view(session, ad_id):
    resp = session.post(f"{BASE_URL}/api.php", data={'action': 'create_ptc_view', 'ad_id': str(ad_id)}, headers={'origin': BASE_URL, 'referer': f"{BASE_URL}/ptc"})
    try: return resp.json()
    except: return {'success': False}

def claim_ptc_view(session, view_id, turnstile_token):
    resp = session.post(f"{BASE_URL}/api.php", data={'action': 'claim_ptc_view', 'view_id': str(view_id), 'turnstile_token': turnstile_token}, headers={'origin': BASE_URL, 'referer': f"{BASE_URL}/ptc"})
    try: return resp.json()
    except: return {'success': False}

def countdown_timer(seconds):
    while seconds > 0:
        m, s = divmod(seconds, 60)
        dashboard.update_status(next_action=f"{m:02d}:{s:02d}")
        time.sleep(1)
        seconds -= 1

# ==========================================
#  LOGIKA UTAMA
# ==========================================
def run_faucet(email, api_key):
    session = create_session()
    session.get(f"{BASE_URL}/faucet")
    result = login(session, email)
    if not result.get('success'):
        dashboard.add_log(f"{RED}[-] Login gagal{RESET}"); return

    dashboard.add_log(f"{GREEN}[+] Login berhasil{RESET}")
    
    initial_balance = get_balance(session)
    if initial_balance is not None:
        dashboard.update_status(balance=initial_balance)
        dashboard.add_log(f"{BLUE}[+] Balance awal: {initial_balance:.2f} Coins{RESET}")

    claim_count = 0; total_earned = 0.0
    while True:
        claim_count += 1
        dashboard.update_status(mode="🔥 Faucet Claim", claim_count=claim_count, total_earned=total_earned, last_action="Memulai...", next_action="")
        slider_token, slider_target = get_slider_info(session)
        slider_pos = max(0, min(100, slider_target))
        while True:
            dashboard.update_status(last_action="Generate Captcha...")
            img_b64, n1_token, _ = generate_captcha(session)
            if not img_b64:
                dashboard.add_log(f"{RED}[-] Gagal generate, coba lagi...{RESET}")
                time.sleep(2); continue
            dashboard.update_status(last_action="🧩 Solve Captcha (BAS)...")
            cx, cy = solve_adcoins_captcha(api_key, img_b64)
            if cx is None:
                dashboard.add_log(f"{RED}[-] Solve captcha gagal, coba lagi...{RESET}")
                time.sleep(1); continue
            dashboard.update_status(last_action="🔍 Verifikasi Captcha...")
            result = verify_captcha(session, n1_token, cx, cy)
            if not result.get('success'):
                dashboard.add_log(f"{RED}[-] Verifikasi gagal, coba lagi...{RESET}")
                time.sleep(1); continue
            dashboard.add_log(f"{GREEN}[+] Captcha berhasil{RESET}")
            break
        dashboard.update_status(last_action="💰 Klaim Faucet...")
        claim_result = claim_faucet(session, slider_token, slider_pos, n1_token)
        if claim_result.get('success'):
            reward = claim_result.get('reward', 10.0)
            try: reward = float(reward)
            except: reward = 10.0
            total_earned += reward
            
            current_balance = get_balance(session)
            if current_balance is not None:
                dashboard.update_status(balance=current_balance)
                dashboard.add_log(f"{BLUE}[+] Balance: {current_balance:.2f} Coins{RESET}")
            
            dashboard.add_log(f"{GREEN}[+] Earned {reward:.2f} coins{RESET}")
            dashboard.update_status(total_earned=total_earned, last_action="✅ Klaim Sukses")
            countdown_timer(60)
        else:
            msg = claim_result.get('message', '')
            if 'wait' in msg.lower():
                wait_match = re.search(r'(\d+):(\d+)', msg)
                wait_time = 60
                if wait_match: wait_time = int(wait_match.group(1)) * 60 + int(wait_match.group(2)) + 5
                dashboard.add_log(f"{YELLOW}[-] Cooldown: Menunggu {wait_time}s...{RESET}")
                countdown_timer(wait_time)
            else:
                dashboard.add_log(f"{RED}[-] Klaim gagal: {msg}{RESET}")
                time.sleep(5)

def run_ptc(email, api_key):
    session = create_session()
    result = login(session, email)
    if not result.get('success'):
        dashboard.add_log(f"{RED}[-] Login gagal{RESET}"); return
    dashboard.add_log(f"{GREEN}[+] Login berhasil{RESET}")
    initial_balance = get_balance(session)
    if initial_balance is not None: dashboard.update_status(balance=initial_balance)

    dashboard.add_log(f"{BLUE}[*] Mengambil daftar iklan PTC...{RESET}")
    resp = session.get(f"{BASE_URL}/ptc")
    ads = parse_ptc_ads(resp.text)
    dashboard.add_log(f"{GREEN}[+] Ditemukan {len(ads)} iklan{RESET}")
    if not ads: return
    success = 0
    for i, ad in enumerate(ads, 1):
        dashboard.update_status(mode="📢 Internal PTC Ads", claim_count=i, total_earned=success * 10.0, last_action=f"Memproses: {ad['title'][:20]}...", next_action=f"{ad['duration']}s")
        view_result = create_ptc_view(session, ad['id'])
        if not view_result.get('success'):
            msg = view_result.get('message', '')
            if msg: dashboard.add_log(f"{RED}[-] {msg}{RESET}")
            continue
        view_id = view_result.get('view_id')
        dashboard.update_status(last_action=f"⏳ Menunggu {ad['duration']} detik...")
        time.sleep(ad['duration'] + 1)
        dashboard.update_status(last_action="🔐 Menyelesaikan Turnstile...")
        token = solve_turnstile(api_key)
        if not token:
            dashboard.add_log(f"{RED}[-] Turnstile gagal{RESET}")
            continue
        claim_result = claim_ptc_view(session, view_id, token)
        if claim_result.get('success'):
            success += 1
            dashboard.add_log(f"{GREEN}[+] Iklan {ad['title'][:20]} berhasil!{RESET}")
            current_balance = get_balance(session)
            if current_balance is not None: dashboard.update_status(balance=current_balance)
            dashboard.update_status(total_earned=success * 10.0, last_action="✅ Iklan Sukses")
        else:
            msg = claim_result.get('message', 'Gagal')
            dashboard.add_log(f"{RED}[-] {msg}{RESET}")
        time.sleep(2)
    dashboard.add_log(f"{GREEN}[+] PTC Selesai: {success}/{len(ads)} diklaim{RESET}")

# ==========================================
#  MENU UTAMA
# ==========================================
def main_menu():
    clear_screen()
    w = 50
    print(f"{CYAN}╭{'─' * w}╮{RESET}")
    print(f"{CYAN}│{RESET}{MAGENTA}{BOLD}     ⚡  A D C O I N S   A U T O   B O T  ⚡{RESET}{' ' * (w - 48)}{CYAN}│{RESET}")
    print(f"{CYAN}╰{'─' * w}╯{RESET}\n")
    
    print(f"{BLUE}┌{'─' * w}┐{RESET}")
    print(f"{BLUE}│{RESET}{BOLD}{CYAN}  🌐 WEBSITE & FUNCTIONS{RESET}{' ' * (w - 26)}{BLUE}│{RESET}")
    print(f"{BLUE}├{'─' * w}┤{RESET}")
    def info_line(label, value):
        text = f"  {label} : {value}"
        print(f"{BLUE}│{RESET} {text}{' ' * (w - ansi_len(text) - 2)}{BLUE}│{RESET}")
    info_line("Website", WHITE + WEBSITE_NAME)
    info_line("Functions", WHITE + "🔥 FAUCET | 📢 PTC")
    print(f"{BLUE}└{'─' * w}┘{RESET}\n")
    
    print(f"{GREEN}  1️⃣  {WHITE}🔥 Start Faucet Farming")
    print(f"{GREEN}  2️⃣  {WHITE}📢 Claim PTC Ads")
    print(f"{GREEN}  3️⃣  {WHITE}⚙️  Config Email & API Key")
    print(f"{RED}  0️⃣  {WHITE}🚪 Exit")
    print()
    
    email = get_email()
    api_key = get_bas_api_key()
    choice = input(f"{CYAN}👉 Pilih opsi (0-3): {RESET}").strip()
    return choice, email, api_key

# ==========================================
#  MAIN
# ==========================================
def main():
    while True:
        choice, email, api_key = main_menu()
        if choice == '0':
            print(f"\n{GREEN}👋 Sampai jumpa!{RESET}")
            sys.exit(0)
        elif choice == '1':
            clear_screen()
            dashboard.update_status(mode="🔥 Starting Faucet...")
            try:
                run_faucet(email, api_key)
            except KeyboardInterrupt:
                print('\033[?25h', end='')
                safe_print(f"\n{YELLOW}[!] Dihentikan oleh pengguna.{RESET}")
                sys.exit()
            except Exception as e:
                dashboard.add_log(f"{RED}[-] Error: {e}{RESET}")
            input(f"\n{CYAN}⌨️  Press Enter untuk kembali ke menu...{RESET}")
        elif choice == '2':
            clear_screen()
            dashboard.update_status(mode="📢 Starting PTC...")
            try:
                run_ptc(email, api_key)
            except KeyboardInterrupt:
                print('\033[?25h', end='')
                safe_print(f"\n{YELLOW}[!] Dihentikan oleh pengguna.{RESET}")
                sys.exit()
            except Exception as e:
                dashboard.add_log(f"{RED}[-] Error: {e}{RESET}")
            input(f"\n{CYAN}⌨️  Press Enter untuk kembali ke menu...{RESET}")
        elif choice == '3':
            config_menu()
        else:
            print(f"{RED}❌ Pilihan tidak valid!{RESET}")
            time.sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\033[?25h', end='')
        safe_print(f"\n{YELLOW}[!] Bot dihentikan oleh pengguna.{RESET}")
        sys.exit()

