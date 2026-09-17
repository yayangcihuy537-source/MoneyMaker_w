#!/usr/bin/env python3
"""
NEWTUBE TON AUTO WATCH - FIXED v4
- No proxy
- Handles: daily_limit_reached, invalid_network, ip_in_use (409), timeout
- Per-network watch durations (adsgramSpecial = 30s+ to satisfy server)
- Auto-retry on watch_time_too_short (bumps duration by +10s, one retry)
- Random fingerprint & user-agent
- Reads new claimAdReward response shape ({ok:true, user:{...}})
- Tolerates both old & new adStart response shapes
- Fixed undefined RESET constant bug in 409 handler
- Network list synced to what the live JS actually calls
"""

import requests
import time
import random
import json
import os
import sys
import hashlib
from datetime import datetime

# ============================================================
# ANSI COLORS
# ============================================================
R, G, Y, B, M, C, W, X = (
    '\033[91m', '\033[92m', '\033[93m', '\033[94m',
    '\033[95m', '\033[96m', '\033[97m', '\033[0m',
)
CYAN = '\033[1;96m'
DIM  = '\033[2;37m'

BANNER = f"""
{CYAN}╔══════════════════════════════════════════════════════════════════════╗
║  ███╗   ██╗███████╗██╗    ██╗████████╗██╗   ██╗██████╗ ███████╗    ║
║  ████╗  ██║██╔════╝██║    ██║╚══██╔══╝██║   ██║██╔══██╗██╔════╝    ║
║  ██╔██╗ ██║█████╗  ██║ █╗ ██║   ██║   ██║   ██║██████╔╝█████╗      ║
║  ██║╚██╗██║██╔══╝  ██║███╗██║   ██║   ██║   ██║██╔══██╗██╔══╝      ║
║  ██║ ╚████║███████╗╚███╔███╔╝   ██║   ╚██████╔╝██████╔╝███████╗    ║
║  ╚═╝  ╚═══╝╚══════╝ ╚══╝╚══╝    ╚═╝    ╚═════╝ ╚═════╝ ╚══════╝    ║
║                                                                    ║
║           {Y}🤖 NEWTUBE TON AUTO WATCH (FIXED v4) 🤖{X}{CYAN}            ║
║        {G}RANDOM FINGERPRINT • NO PROXY • PER-NET TIMING{X}{CYAN}         ║
╚══════════════════════════════════════════════════════════════════════╝{X}
"""

MENU = f"""
{CYAN}╔══════════════════════════════════════════════╗
║              {Y}☁️ NEWTUBE TON ☁️{X}{CYAN}             ║
║          {CYAN}AUTO WATCH ADS + CLAIM{CYAN}           ║
╠══════════════════════════════════════════════╣
║  {G}[1] 🚀 Start Auto Watch{X}{CYAN}                  ║
║  {Y}[2] 🔑 Set Init Data{X}{CYAN}                    ║
║  {B}[3] 💰 Check Balance{X}{CYAN}                    ║
║  {R}[0] ❌ Exit{X}{CYAN}                                ║
╚══════════════════════════════════════════════╝{X}
"""

# ============================================================
# CONFIG
# ============================================================
CONFIG_FILE  = "newtube_config.json"
BASE_URL     = "https://newtube-ton.vercel.app"
API_USER     = f"{BASE_URL}/api/user"
API_EARN     = f"{BASE_URL}/api/earn"

# Mirrors AD_SHOW_FUNCTIONS in the live JS + AD_NETWORKS_UI ids.
VALID_NETWORKS = [
    "adsgramDaily",
    "adsgramSpecial",
    "monetag",
    "giga",
    "usl",
    "monetagPopup",
]

# Per-network daily limits mirrored from AD_NETWORKS_UI in the live JS.
NETWORK_LIMITS = {
    "adsgramDaily":   10,
    "adsgramSpecial": 10,
    "monetag":        10,
    "giga":           15,
    "usl":            10,
    "monetagPopup":    5,
}

# Counter field names in the user object (per network).
NETWORK_COUNTER_FIELDS = {
    "adsgramDaily":   "adsgramDailyCountToday",
    "adsgramSpecial": "adsgramSpecialCountToday",
    "monetag":        "monetagCountToday",
    "giga":           "gigaCountToday",
    "usl":            "uslCountToday",
    "monetagPopup":   "monetagPopupCountToday",
}

# Global default watch duration range.
MIN_DURATION = 18
MAX_DURATION = 21

# Per-network duration overrides (server rejects short watches on some).
# adsgramSpecial enforces watch_time_too_short below ~30s.
NETWORK_DURATIONS = {
    "adsgramSpecial": (30, 35),
    "adsgramDaily":   (18, 21),
    "monetag":        (18, 21),
    "giga":           (18, 21),
    "usl":            (18, 21),
    "monetagPopup":   (18, 21),
}

def get_duration(network, extra=0):
    lo, hi = NETWORK_DURATIONS.get(network, (MIN_DURATION, MAX_DURATION))
    return random.randint(lo + extra, hi + extra)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:109.0) Gecko/20100101 Firefox/119.0",
]

# ============================================================
# UTILS
# ============================================================
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print(BANNER)

def progress_bar(current, total, bar_len=20, fill='█', empty='░'):
    pct = current / total
    filled_len = int(bar_len * pct)
    bar = fill * filled_len + empty * (bar_len - filled_len)
    return f"[{bar}] {int(pct*100)}%"

def random_delay(min_sec=1, max_sec=3):
    time.sleep(random.uniform(min_sec, max_sec))

def random_ua():
    return random.choice(USER_AGENTS)

def generate_fingerprint():
    """Random fingerprint — new one each launch, per session."""
    raw = f"{time.time()}{random.randint(100000, 999999)}"
    return hashlib.sha256(raw.encode()).hexdigest()

def safe_json_response(resp):
    """Handles JSON with/without BOM, non-JSON bodies, and HTML fallbacks."""
    text = resp.text or ""
    if text.startswith('\ufeff'):
        text = text[1:]
    try:
        return json.loads(text)
    except Exception:
        snippet = text.strip().replace("\n", " ")[:180]
        raise Exception(f"Non-JSON response (HTTP {resp.status_code}): {snippet}")

# ============================================================
# BOT
# ============================================================
class NewTubeBot:
    def __init__(self, init_data=None):
        self.init_data = init_data
        self.session = requests.Session()
        self.fingerprint = generate_fingerprint()
        self._update_headers()

    def _update_headers(self):
        ua = random_ua()
        chrome_ver = random.randint(100, 125)
        self.session.headers.update({
            "User-Agent": ua,
            "Accept": "*/*",
            "Accept-Language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "X-Requested-With": "org.telegram.messenger.web",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
            "Content-Type": "application/json",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Sec-Ch-Ua": f'"Not?A_Brand";v="24", "Chromium";v="{chrome_ver}", "Android WebView";v="{chrome_ver}"',
            "Sec-Ch-Ua-Mobile": "?1",
            "Sec-Ch-Ua-Platform": '"Android"',
        })

    # --------------------------------------------------------
    # raw request helper
    # --------------------------------------------------------
    def _request(self, method, url, data=None, params=None):
        self._update_headers()
        try:
            if method.upper() == "GET":
                resp = self.session.get(url, params=params, timeout=20)
            else:
                resp = self.session.post(url, json=data, timeout=20)

            if resp.status_code == 409:
                try:
                    err = safe_json_response(resp)
                    if err.get("error") == "ip_in_use":
                        print(f"{Y}⚠️  IP/fingerprint already registered (owner exists). Continuing...{X}")
                        return {"ok": True, "alreadyExists": True, "owner": err.get("owner")}
                except Exception:
                    pass
                raise Exception(f"HTTP 409: {resp.text[:200]}")

            if resp.status_code != 200:
                raise Exception(f"HTTP {resp.status_code}: {resp.text[:200]}")

            return safe_json_response(resp)
        except requests.exceptions.Timeout:
            raise Exception("Request timed out")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    # --------------------------------------------------------
    # API calls
    # --------------------------------------------------------
    def init_user(self):
        payload = {
            "action": "init",
            "fingerprint": self.fingerprint,
            "initData": self.init_data,
        }
        return self._request("POST", API_USER, data=payload)

    def get_profile(self):
        params = {"action": "profile", "initData": self.init_data}
        return self._request("GET", API_USER, params=params)

    def ad_start(self, network):
        payload = {
            "action": "adStart",
            "network": network,
            "initData": self.init_data,
        }
        return self._request("POST", API_EARN, data=payload)

    def claim_ad_reward(self, network, start_time, signature):
        payload = {
            "action": "claimAdReward",
            "network": network,
            "startTime": start_time,
            "signature": signature,
            "initData": self.init_data,
        }
        return self._request("POST", API_EARN, data=payload)

    # --------------------------------------------------------
    # Main loop
    # --------------------------------------------------------
    def watch_all(self):
        print(f"{C}🔐 Fingerprint: {self.fingerprint[:16]}...{X}")

        # ── init ──
        try:
            init_resp = self.init_user()
            if init_resp.get("alreadyExists") or init_resp.get("ok"):
                if init_resp.get("alreadyExists"):
                    owner = init_resp.get("owner") or {}
                    print(f"{G}✅ Already registered as {owner.get('firstName','?')} (ID {owner.get('id','?')}){X}")
                else:
                    print(f"{G}✅ Init OK{X}")
        except Exception as e:
            print(f"{R}❌ Init failed: {e}{X}")
            return

        # ── profile ──
        try:
            profile = self.get_profile()
            user = profile.get("user", {}) or {}
            print(f"{G}👤 User: {user.get('telegramUsername', 'N/A')}{X}")
            print(f"{G}💰 WTC Balance: {user.get('wtcBalance', 0)}{X}")
            print(f"{G}📈 Lifetime Earned: {user.get('lifetimeWtcEarned', 0)}{X}")
            print(f"{G}📺 Ads Watched Today: {user.get('adsWatchedToday', 0)}{X}")
            print(f"{G}📊 Lifetime Ads: {user.get('lifetimeAdsWatched', 0)}{X}")
        except Exception as e:
            print(f"{Y}⚠️  Profile fetch failed: {e}{X}")
            user = {}

        # ── per-network loop ──
        for network in VALID_NETWORKS:
            limit = NETWORK_LIMITS.get(network, 10)
            counter_field = NETWORK_COUNTER_FIELDS.get(network, "")
            current_count = user.get(counter_field, 0) if counter_field else 0

            print(f"\n{CYAN}=== {network} ({current_count}/{limit} today) ==={X}")

            attempt = 0
            bump_extra = 0  # extra seconds added after a too-short rejection

            while True:
                attempt += 1
                if limit > 0 and current_count >= limit:
                    print(f"{Y}⚠️  Daily limit already reached for {network}{X}")
                    break

                # ── adStart ──
                try:
                    start_resp = self.ad_start(network)
                except Exception as e:
                    print(f"{R}❌ adStart error: {e}{X}")
                    break

                if not start_resp.get("ok"):
                    err = str(start_resp.get("error", ""))
                    msg = str(start_resp.get("message", ""))
                    if "daily_limit_reached" in err or "limit" in msg.lower():
                        print(f"{Y}⚠️  Daily limit reached for {network}{X}")
                        break
                    if "invalid_network" in err:
                        print(f"{Y}⚠️  Invalid network: {network} (skip){X}")
                        break
                    if err == "unauthorized":
                        print(f"{R}❌ Session expired — refresh initData.{X}")
                        return
                    print(f"{Y}⚠️  adStart failed: {start_resp}{X}")
                    break

                # Direct-credit payload (rare) — some backend builds return
                # a rewarded result straight from adStart.
                if "startTime" not in start_resp or "signature" not in start_resp:
                    if "reward" in start_resp:
                        reward = start_resp.get("reward", 0)
                        current_count = start_resp.get("countToday", current_count + 1)
                        print(f"{G}✅ (direct-credit) +{reward} WTC ({current_count}/{limit}){X}")
                        random_delay(1, 3)
                        continue
                    print(f"{R}❌ adStart missing startTime/signature: {start_resp}{X}")
                    break

                start_time = start_resp["startTime"]
                signature  = start_resp["signature"]

                # ── fake watch ──
                duration = get_duration(network, extra=bump_extra)
                print(f"\n{CYAN}╔══════════════════════════════════════════════╗")
                print(f"║              {Y}📺 WATCHING ADS 📺{X}{CYAN}              ║")
                print(f"║         {C}Network: {G}{network}{X}{CYAN}")
                print(f"║         {C}Attempt: {G}{attempt}{X}{CYAN}")
                print(f"╚══════════════════════════════════════════════╝{X}\n")
                print(f"{C}⏳ Watching for {duration}s...{X}")
                for sec in range(duration):
                    time.sleep(1)
                    bar = progress_bar(sec + 1, duration)
                    sys.stdout.write(f"\r  {G}{bar}{X} {sec+1}s/{duration}s")
                    sys.stdout.flush()
                print()

                # ── claim ──
                try:
                    claim_resp = self.claim_ad_reward(network, start_time, signature)
                except Exception as e:
                    print(f"{R}❌ Claim error: {e}{X}")
                    break

                if not claim_resp.get("ok"):
                    err = str(claim_resp.get("error", ""))
                    msg = str(claim_resp.get("message", ""))

                    if "daily_limit_reached" in err or "limit" in msg.lower():
                        print(f"{Y}⚠️  Daily limit reached for {network}{X}")
                        break
                    if "invalid_network" in err:
                        print(f"{Y}⚠️  Invalid network: {network} (skip){X}")
                        break
                    if "watch_time_too_short" in err:
                        # Server says our fake watch was too short. Bump by
                        # +10s and retry the SAME network once.
                        bump_extra += 10
                        print(f"{Y}⚠️  watch_time_too_short — retrying with +{bump_extra}s extra.{X}")
                        random_delay(2, 4)
                        continue
                    print(f"{R}❌ Claim failed: {claim_resp}{X}")
                    break

                # ── Success ──
                # New response shape: {ok:true, user:{...}}
                user_obj = claim_resp.get("user")
                if user_obj:
                    old_balance = user.get("wtcBalance", 0)
                    new_balance = user_obj.get("wtcBalance", old_balance)
                    gained = max(0, new_balance - old_balance)
                    current_count = user_obj.get(counter_field, current_count + 1)
                    user = user_obj
                    print(f"{G}✅ Claimed +{gained} WTC | Balance: {new_balance} | Today: {current_count}/{limit}{X}")
                else:
                    reward = claim_resp.get("reward", 0)
                    current_count = claim_resp.get("countToday", current_count + 1)
                    daily_limit = claim_resp.get("dailyLimit", limit)
                    print(f"{G}✅ Claimed +{reward} WTC ({current_count}/{daily_limit}){X}")

                if limit > 0 and current_count >= limit:
                    print(f"{Y}⚠️  Daily limit reached for {network}{X}")
                    break

                random_delay(2, 4)

        print(f"\n{G}✅ Done processing all networks.{X}")

# ============================================================
# MENU HANDLERS
# ============================================================
bot = None

def set_init_data():
    global bot
    clear_screen()
    print_header()
    print(f"\n{Y}🔑 SET INIT DATA{X}")
    print(f"{C}{'='*50}{X}")
    init_data = input(f"{G}Paste init_data (from WebApp): {X}").strip()
    if not init_data:
        print(f"{R}❌ init_data cannot be empty.{X}")
        time.sleep(2)
        return
    config = load_config() or {}
    config["init_data"] = init_data
    save_config(config)
    bot = NewTubeBot(init_data=init_data)
    print(f"{G}✅ Saved. New fingerprint: {bot.fingerprint[:16]}...{X}")
    time.sleep(1.5)

def start_auto_watch():
    global bot
    clear_screen()
    print_header()
    if not bot or not bot.init_data:
        print(f"{R}❌ No init_data yet. Use menu 2 first.{X}")
        time.sleep(2)
        return
    print(f"{G}🚀 Starting auto-watch...{X}")
    bot.watch_all()
    input(f"\n{C}Press Enter to return...{X}")

def check_balance():
    global bot
    clear_screen()
    print_header()
    if not bot or not bot.init_data:
        print(f"{R}❌ No init_data yet. Use menu 2 first.{X}")
        time.sleep(2)
        return
    try:
        profile = bot.get_profile()
        user = profile.get("user", {}) or {}
        print(f"{G}👤 User: {user.get('telegramUsername', 'N/A')}{X}")
        print(f"{G}💰 WTC Balance: {user.get('wtcBalance', 0)}{X}")
        print(f"{G}📈 Lifetime Earned: {user.get('lifetimeWtcEarned', 0)}{X}")
        print(f"{G}📺 Ads Watched Today: {user.get('adsWatchedToday', 0)}{X}")
        print(f"{G}📊 Lifetime Ads: {user.get('lifetimeAdsWatched', 0)}{X}")
        print(f"{G}🤝 Valid Referrals: {user.get('validReferralCount', 0)}{X}")
    except Exception as e:
        print(f"{R}❌ Failed to fetch: {e}{X}")
    input(f"\n{C}Press Enter to return...{X}")

# ============================================================
# MAIN
# ============================================================
def main():
    global bot
    config = load_config()
    if config and config.get("init_data"):
        bot = NewTubeBot(init_data=config["init_data"])
        print(f"{G}🔑 Config loaded. Fingerprint: {bot.fingerprint[:16]}...{X}")
        time.sleep(1)
    else:
        bot = None

    while True:
        clear_screen()
        print_header()
        print(MENU)
        status = "🟢 Ready" if bot and bot.init_data else "🔴 No init_data"
        print(f"{DIM}Status: {status}{X}")
        if bot:
            print(f"{DIM}Fingerprint: {bot.fingerprint[:16]}...{X}")

        choice = input(f"\n{CYAN}Pick menu » {X}").strip()

        if choice == "1":
            start_auto_watch()
        elif choice == "2":
            set_init_data()
        elif choice == "3":
            check_balance()
        elif choice == "0":
            print(f"\n{R}❌ Bye.{X}")
            sys.exit(0)
        else:
            print(f"{R}❌ Invalid choice.{X}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Y}⏹ Stopped by user.{X}")
        sys.exit(0)

