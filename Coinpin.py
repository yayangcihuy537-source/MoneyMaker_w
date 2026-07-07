#!/usr/bin/env python3

import requests
import re
import time
import json
import os
from datetime import datetime
from colorama import Fore, Style, init

# ======================= INIT COLORAMA =======================
init(autoreset=True)

# ======================= BANNER =======================
def banner():
    os.system('clear')
    print(f"""{Fore.CYAN}
 ██████╗ ██████╗ ██╗███╗   ██╗██████╗ ██╗███╗   ██╗
██╔════╝██╔═══██╗██║████╗  ██║██╔══██╗██║████╗  ██║
██║     ██║   ██║██║██╔██╗ ██║██████╔╝██║██╔██╗ ██║
██║     ██║   ██║██║██║╚██╗██║██╔═══╝ ██║██║╚██╗██║
╚██████╗╚██████╔╝██║██║ ╚████║██║     ██║██║ ╚████║
 ╚═════╝ ╚═════╝ ╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═══╝
{Style.RESET_ALL}

{Fore.YELLOW}╔══════════════════════════════════════════════════════════════╗
║                 COINPIN.TOP AUTO CLAIM BOT                 ║
╠══════════════════════════════════════════════════════════════╣
║  👨‍💻 Developer : {Fore.MAGENTA}Moneymaker_w{Fore.YELLOW}
║  🌐 Website   : {Fore.CYAN}coinpin.top{Fore.YELLOW}
║  🤖 Language  : {Fore.GREEN}Python{Fore.YELLOW}
║  ⚡ Mode      : {Fore.GREEN}Auto Claim{Fore.YELLOW}
╚══════════════════════════════════════════════════════════════╝
{Style.RESET_ALL}
""")
    print()

# ======================= COLORS =======================
MONEY_GOLD = Fore.YELLOW
MONEY_BRONZE = Fore.LIGHTYELLOW_EX
MONEY_BROWN = Fore.LIGHTYELLOW_EX
MONEY_DARK_BROWN = Fore.LIGHTYELLOW_EX
MONEY_CHOCOLATE = Fore.LIGHTYELLOW_EX
MONEY_LIGHT_GOLD = Fore.LIGHTYELLOW_EX
MONEY_SUCCESS = Fore.GREEN
MONEY_ERROR = Fore.RED
WHITE = Fore.WHITE
RESET = Style.RESET_ALL
BOLD = Style.BRIGHT

LINE = f"{MONEY_GOLD}{'━'*60}{RESET}"

def center_text(text, width=60):
    clean = re.sub(r'\033\[[0-9;]*m', '', text)
    spaces = max(0, (width - len(clean)) // 2)
    return " " * spaces + text

def log_claim(amount):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{MONEY_LIGHT_GOLD}[{now}] {MONEY_SUCCESS}✅ Claimed: {amount} coins!{RESET}")

def log_error(msg):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"{MONEY_LIGHT_GOLD}[{now}] {MONEY_ERROR}❌ {msg}{RESET}")

# ======================= CONFIG =======================
BASE_URL = "https://coinpin.top"
CONFIG_FILE = "coinpin_config.json"
OCR_SERVER = "https://ocr-server-82fr.onrender.com/antibot"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return None

def save_config(email, user_agent):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"email": email, "user_agent": user_agent}, f, indent=4)

def get_csrf(session):
    resp = session.get(f"{BASE_URL}/login")
    match = re.search(r'name="csrf_token_name"\s*value="([^"]+)"', resp.text)
    return match.group(1) if match else None

def login(session, email, password):
    csrf = get_csrf(session)
    if not csrf:
        return False
    
    data = {"email": email, "password": password, "csrf_token_name": csrf}
    resp = session.post(f"{BASE_URL}/auth/login", data=data, allow_redirects=False)
    
    return resp.status_code == 303

def get_claims_left(html):
    match = re.search(r'(\d+)/(\d+)\s*claims left', html, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))
    return None, None

def extract_antibot_images(html):
    all_images = re.findall(r'data:image/png;base64,([A-Za-z0-9+/=]+)', html)
    if len(all_images) < 4:
        return None
    
    question_img = all_images[0]
    answer_imgs = all_images[1:4]
    
    rels = re.findall(r'rel=\\\"(\d+)\\\"', html)
    if not rels:
        rels = re.findall(r'rel="(\d+)"', html)
    
    if len(rels) < 3:
        return None
    
    return {
        'question': question_img,
        'answers': answer_imgs[:3],
        'rels': rels[:3]
    }

def solve_antibot(question, answers, rels):
    try:
        payload = {"question": question, "answers": answers, "rels": rels}
        resp = requests.post(OCR_SERVER, json=payload, timeout=60)
        
        if resp.status_code == 200:
            result = resp.text.strip()
            indexes = [int(x) for x in result.split()]
            ordered = [rels[i-1] for i in indexes if 1 <= i <= len(rels)]
            if ordered:
                return '+' + '+'.join(ordered)
        return None
    except:
        return None

def claim_faucet(session):
    resp = session.get(f"{BASE_URL}/faucet", timeout=30)
    html = resp.text
    
    if "Daily limit reached" in html:
        log_error("Daily limit reached! Script stopped.")
        return "LIMIT"
    
    left, total = get_claims_left(html)
    if left is not None and left <= 0:
        log_error("Daily limit reached! Script stopped.")
        return "LIMIT"
    
    csrf_match = re.search(r'name="csrf_token_name"\s+id="token"\s+value="([^"]+)"', html)
    token_match = re.search(r'name="token"\s+value="([^"]+)"', html)
    
    if not csrf_match or not token_match:
        return None
    
    csrf = csrf_match.group(1)
    token = token_match.group(1)
    
    antibot = extract_antibot_images(html)
    if not antibot:
        return None
    
    antibot_value = solve_antibot(antibot['question'], antibot['answers'], antibot['rels'])
    if not antibot_value:
        return None
    
    post_data = f"antibotlinks={antibot_value}&csrf_token_name={csrf}&token={token}"
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Origin": BASE_URL, "Referer": f"{BASE_URL}/faucet"}
    
    resp2 = session.post(f"{BASE_URL}/faucet/verify", data=post_data, headers=headers, allow_redirects=False, timeout=30)
    
    if resp2.status_code == 303:
        location = resp2.headers.get('Location', '')
        resp3 = session.get(location, timeout=30)
        
        if 'Good job' in resp3.text and 'has been added' in resp3.text:
            reward = re.search(r'(\d+)\s+coins\s+has been added', resp3.text, re.IGNORECASE)
            if reward:
                return reward.group(1)
            return "success"
    
    return None

def main():
    banner()
    
    # Load saved config
    config = load_config()
    
    if config and config.get('email') and config.get('user_agent'):
        email = config['email']
        user_agent = config['user_agent']
        print(f"{MONEY_LIGHT_GOLD}📧 Using saved email: {WHITE}{email}{RESET}")
        print(f"{MONEY_LIGHT_GOLD}🌐 Using saved User-Agent: {WHITE}{user_agent[:50]}...{RESET}")
        use_saved = input(f"{MONEY_LIGHT_GOLD}Use saved? (y/n): {RESET}").lower()
        if use_saved != 'y':
            email = input(f"{MONEY_LIGHT_GOLD}📧 Email: {RESET}").strip()
            user_agent = input(f"{MONEY_LIGHT_GOLD}🌐 User-Agent: {RESET}").strip()
            save_config(email, user_agent)
    else:
        email = input(f"{MONEY_LIGHT_GOLD}📧 Email: {RESET}").strip()
        user_agent = input(f"{MONEY_LIGHT_GOLD}🌐 User-Agent: {RESET}").strip()
        save_config(email, user_agent)
    
    password = input(f"{MONEY_LIGHT_GOLD}🔑 Password: {RESET}").strip()
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9",
        "X-Requested-With": "mark.via.gp",
    })
    
    if not login(session, email, password):
        log_error("Login failed!")
        return
    
    banner()
    print(center_text(f"{MONEY_LIGHT_GOLD}{BOLD}➤ STARTING FAUCET CLAIM{RESET}"))
    print(LINE)
    
    while True:
        result = claim_faucet(session)
        
        if result == "LIMIT":
            break
        elif result:
            log_claim(result)
            time.sleep(15)
        else:
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{MONEY_LIGHT_GOLD}👋 Exited{RESET}")