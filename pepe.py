#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║   ███████╗███████╗██████╗ ███████╗███████╗██╗      ██████╗  ║
║   ██╔════╝██╔════╝██╔══██╗██╔════╝██╔════╝██║     ██╔═══██╗ ║
║   █████╗  █████╗  ██████╔╝█████╗  █████╗  ██║     ██║   ██║ ║
║   ██╔══╝  ██╔══╝  ██╔═══╝ ██╔══╝  ██╔══╝  ██║     ██║   ██║ ║
║   ██║     ███████╗██║     ███████╗██║     ███████╗╚██████╔╝ ║
║   ╚═╝     ╚══════╝╚═╝     ╚══════╝╚═╝     ╚══════╝ ╚═════╝  ║
║                                                             ║
║   🚀 MULTI-BOT: PEPEFLOW + COINSZON + MINIGRAMX + LITOSHI  ║
║   AUTO CLAIM • AUTO GAMES • AUTO DOUBLE • AUTO SKIP LIMIT  ║
║   🔐 AUTH via init_data (NO PHPSESSID)                     ║
║   🎲 FINGERPRINT RANDOM (acak tiap reauth)                 ║
║   📋 MENU: 1) PEPE+COINS  2) MINI+LITOSHI                 ║
╚═══════════════════════════════════════════════════════════════╝
"""

import os, sys, time, json, random, re, requests, urllib.parse
from datetime import datetime
from collections import deque

# ========== WARNA ==========
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'; C = '\033[96m'; W = '\033[97m'
GOLD = '\033[38;5;220m'; PURPLE = '\033[38;5;141m'; PINK = '\033[38;5;206m'
RESET = '\033[0m'

# ========== KONFIGURASI ==========
PEPE_CONFIG = "pepeflow_config.json"
COIN_CONFIG  = "coinszon_config.json"
MINI_CONFIG  = "minigramx_config.json"
LITOSHI_CONFIG = "litoshipay_config.json"

PEPE_URL = "https://pepeflow.com"
COIN_URL  = "https://coinszon.com"
MINI_URL  = "https://minigramx.top"
LITOSHI_URL = "https://litoshipay.com"

UA = "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.47 Mobile Safari/537.36 Telegram-Android/12.6.4"

# ---------- Game config ----------
PEPE_GAMES = ["lucky_wheel", "slots", "scratch", "treasure_dig"]
PEPE_GAME_MAP = {
    "lucky_wheel": {"display": "SPIN", "icon": "🎡"},
    "slots": {"display": "SLOTS", "icon": "🎰"},
    "scratch": {"display": "SCRATCH", "icon": "🎫"},
    "treasure_dig": {"display": "DIG", "icon": "⛏️"},
}

COIN_GAMES = ["lucky_wheel", "slots"]
COIN_GAME_MAP = {
    "lucky_wheel": {"display": "SPIN", "icon": "🎡"},
    "slots": {"display": "SLOTS", "icon": "🎰"},
}

MINI_GAMES = ["lucky_wheel", "slots", "scratch", "treasure_dig"]
MINI_GAME_MAP = {
    "lucky_wheel": {"display": "SPIN", "icon": "🎡"},
    "slots": {"display": "SLOTS", "icon": "🎰"},
    "scratch": {"display": "SCRATCH", "icon": "🎫"},
    "treasure_dig": {"display": "DIG", "icon": "⛏️"},
}

LITOSHI_GAMES = ["lucky_wheel", "treasure_dig", "coin_catch", "flappy_coin"]
LITOSHI_GAME_MAP = {
    "lucky_wheel": {"display": "SPIN", "icon": "🎡"},
    "treasure_dig": {"display": "DIG", "icon": "⛏️"},
    "coin_catch": {"display": "CATCH", "icon": "🪙"},
    "flappy_coin": {"display": "FLAPPY", "icon": "🐦"},
}

# ========== Config (only init_data) ==========
class BaseConfig:
    def __init__(self, file):
        self.file = file
        self.init_data = None
        self.telegram_id = None
        self.telegram_username = None
    def load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file) as f:
                    d = json.load(f)
                    self.init_data = d.get('init_data')
                    self.telegram_id = d.get('telegram_id')
                    self.telegram_username = d.get('telegram_username')
                    return True
            except:
                return False
        return False
    def save(self):
        with open(self.file, 'w') as f:
            json.dump({
                'init_data': self.init_data,
                'telegram_id': self.telegram_id,
                'telegram_username': self.telegram_username
            }, f, indent=2)

# ========== Utility ==========
def safe_float(val, default=0.0):
    if val is None: return default
    if isinstance(val, (int, float)): return float(val)
    if isinstance(val, str):
        try:
            return float(val.replace(',', '').strip())
        except:
            return default
    return default

def safe_int(val, default=0):
    return int(safe_float(val, default))

def live_timer(seconds, msg="⏳ Menunggu"):
    if seconds < 1:
        return
    while seconds > 0:
        m, s = divmod(seconds, 60)
        sys.stdout.write(f"\r{Y}{msg} {m:02d}:{s:02d} {RESET}  ")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()

def ad_progress(seconds=30, label="📺 Watching ad"):
    for i in range(seconds, 0, -1):
        bar_len = 20
        filled = int((seconds - i) / seconds * bar_len)
        bar = '█' * filled + '░' * (bar_len - filled)
        sys.stdout.write(f"\r{G}{label} [{bar}] {i}s left{RESET}")
        sys.stdout.flush()
        time.sleep(1)
    print()

# ========== Base Bot ==========
class BaseBot:
    def __init__(self, url, cfg, game_list, game_map, name, currency="PEPE"):
        self.url = url
        self.cfg = cfg
        self.game_list = game_list
        self.game_map = game_map
        self.name = name
        self.currency = currency
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": UA,
            "Accept": "*/*",
            "Origin": url,
            "Referer": f"{url}/miniapp.php",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Connection": "keep-alive",
            "sec-ch-ua": '"Not;A=Brand";v="8","Chromium";v="150","Android WebView";v="150"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
        })
        self.balance = 0.0
        self.cooldowns = {g: 0 for g in game_list}
        self.play_counts = {g: 0 for g in game_list}
        self.doubled_available = {g: False for g in game_list}
        self.status = {g: "Ready" for g in game_list}
        self.rewards = {g: 0 for g in game_list}
        self.logs = deque(maxlen=8)
        self.running = True
        self.retry_doubled = {g: True for g in game_list}
        self.daily_claimed = False
        self.game_index = 0
        self.treasure_token = None
        self.limited = False
        self.limited_games = set()
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        self._initial_auth()

    def fmt(self, sec):
        if sec <= 0: return "Ready"
        m, s = divmod(int(sec), 60)
        return f"{m}m{s}s" if m else f"{s}s"

    def log(self, msg):
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    # ---------- AUTH (only init_data) ----------
    def _initial_auth(self):
        if not self.cfg.init_data:
            self.log(f"{R}❌ init_data kosong! Bot tidak bisa jalan{RESET}")
            self.running = False
            return False
        return self.reauth()

    def reauth(self):
        if not self.cfg.init_data:
            self.log(f"{R}❌ init_data tidak ada{RESET}")
            return False
        parsed = urllib.parse.parse_qs(self.cfg.init_data)
        user_str = parsed.get('user', [None])[0]
        tid, tuname = "0", ""
        if user_str:
            try:
                u = json.loads(urllib.parse.unquote(user_str))
                tid = str(u.get('id','0'))
                tuname = u.get('username','')
            except: pass
        self.cfg.telegram_id = tid
        self.cfg.telegram_username = tuname
        self.cfg.save()

        # 🔥 FINGERPRINT RANDOM tiap kali reauth
        fingerprint = os.urandom(16).hex()

        files = {
            "init_data": (None, self.cfg.init_data),
            "telegram_id": (None, tid),
            "telegram_username": (None, tuname),
            "auto_login": (None, "1"),
            "fingerprint": (None, fingerprint),
        }
        try:
            resp = self.session.post(f"{self.url}/actions/tg_auth.php", files=files)
            if resp.status_code == 200:
                self.log(f"{G}✅ {self.name} auth OK (fingerprint: {fingerprint[:8]}...){RESET}")
                return True
            else:
                self.log(f"{R}❌ Auth gagal, status {resp.status_code}{RESET}")
                return False
        except Exception as e:
            self.log(f"{R}❌ Auth error: {e}{RESET}")
            return False

    # ---------- HTTP ----------
    def _request(self, method, endpoint, **kwargs):
        if not self.running:
            return None
        url = f"{self.url}{endpoint}"
        try:
            resp = self.session.request(method, url, **kwargs)
            
            if resp.status_code == 429:
                self.consecutive_errors += 1
                self.log(f"{R}🚫 429 Too Many Requests! ({self.consecutive_errors}/{self.max_consecutive_errors}){RESET}")
                if self.consecutive_errors >= self.max_consecutive_errors:
                    self.log(f"{R}🛑 {self.name} terlalu banyak 429! Bot di-stop{RESET}")
                    self.running = False
                return None
            else:
                self.consecutive_errors = 0
            
            if resp.status_code in [401,403] or (resp.status_code==200 and "Not logged" in resp.text):
                self.log(f"{Y}⚠️ Session expired, reauth...{RESET}")
                if self.reauth():
                    resp = self.session.request(method, url, **kwargs)
                    if "Not logged" in resp.text:
                        self.log(f"{R}❌ Session masih invalid{RESET}")
                        return None
                else:
                    self.log(f"{R}❌ Reauth gagal, lanjut tanpa session{RESET}")
                    return None
            return resp
        except Exception as e:
            self.log(f"{R}❌ Request error: {e}{RESET}")
            self.consecutive_errors += 1
            if self.consecutive_errors >= self.max_consecutive_errors:
                self.log(f"{R}🛑 {self.name} terlalu banyak error! Bot di-stop{RESET}")
                self.running = False
            return None

    def get(self, endpoint):
        return self._request('GET', endpoint)

    def post(self, endpoint, files=None, data=None):
        return self._request('POST', endpoint, files=files, data=data)

    # ---------- Dashboard ----------
    def get_dashboard(self):
        resp = self.get("/pages/load_dashboard.php")
        if resp and resp.status_code == 200:
            html = resp.text
            patterns = [
                r'id="header-user-balance"[^>]*>([\d.,]+)\s*(PEPE|GRAM|COIN|LTC)',
                r'id="dash-balance-coin">([\d.,]+)',
                r'Balance:\s*([\d.,]+)',
                r'"balance":\s*([\d.]+)',
            ]
            for p in patterns:
                match = re.search(p, html, re.IGNORECASE)
                if match:
                    self.balance = safe_float(match.group(1))
                    return html
            return html
        return None

    # ---------- Game status ----------
    def get_games_status(self):
        if not self.game_list:
            return None
        resp = self.get("/pages/load_games.php")
        if resp and resp.status_code == 200:
            html = resp.text
            match = re.search(r'var gameConfigs\s*=\s*({.*?});', html, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group(1))
                    for g in self.game_list:
                        if g in data:
                            info = data[g]
                            cd = info.get('cooldown_remaining', 0)
                            self.cooldowns[g] = cd
                            self.status[g] = self.fmt(cd) if cd > 0 else "Ready"
                            self.doubled_available[g] = bool(info.get('doubled', False))
                            # Perbaikan limit: cek daily_limit, kalo 0 => unlimited
                            daily_limit = info.get('daily_limit', None)
                            limit_reached = info.get('limit_reached', False)
                            daily_remaining = info.get('daily_remaining', 999)
                            # Hanya mark limited kalo daily_limit > 0 dan (limit_reached atau daily_remaining <= 0)
                            if daily_limit is not None and daily_limit > 0:
                                if limit_reached or daily_remaining <= 0:
                                    self.limited_games.add(g)
                                else:
                                    self.limited_games.discard(g)
                            else:
                                # daily_limit 0 atau None => unlimited, jangan mark
                                self.limited_games.discard(g)
                    return data
                except: pass
            # Fallback: scan HTML
            for g in self.game_list:
                pattern = rf'{g}.*?cooldown.*?(\d+)'
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    self.cooldowns[g] = int(match.group(1))
                    self.status[g] = self.fmt(self.cooldowns[g]) if self.cooldowns[g] > 0 else "Ready"
        return None

    def has_ready_games(self):
        if not self.game_list:
            return False
        try:
            self.get_games_status()
            ready = [g for g in self.game_list if g not in self.limited_games and self.cooldowns.get(g, 0) <= 0]
            return len(ready) > 0
        except:
            return False

    def get_ready_games(self):
        if not self.game_list:
            return []
        try:
            self.get_games_status()
            return [g for g in self.game_list if g not in self.limited_games and self.cooldowns.get(g, 0) <= 0]
        except:
            return []

    def is_all_limited(self):
        if not self.game_list:
            return False
        return all(g in self.limited_games for g in self.game_list)

    # ---------- Play game ----------
    def play_game(self, game, doubled=False, base_reward=None, pick=None, quiz_token=None, answer_index=None, double_token=None, score=None, bombed=None, diamonds=None, survived=None):
        if not self.game_list:
            return None
        if game in self.limited_games:
            self.log(f"{Y}⏭️ {game} sudah limit, skip{RESET}")
            return None
        files = {"action": (None, "play"), "game": (None, game),
                 "doubled": (None, "1" if doubled else "0")}
        if doubled and base_reward is not None:
            files["base_reward"] = (None, str(base_reward))
        if doubled and double_token:
            files["double_token"] = (None, str(double_token))
        if pick is not None:
            files["pick"] = (None, str(pick))
        if quiz_token is not None:
            files["quiz_token"] = (None, str(quiz_token))
        if answer_index is not None:
            files["answer_index"] = (None, str(answer_index))
        if score is not None:
            files["score"] = (None, str(score))
        if bombed is not None:
            files["bombed"] = (None, "1" if bombed else "0")
        if diamonds is not None:
            files["diamonds"] = (None, str(diamonds))
        if survived is not None:
            files["survived"] = (None, "1" if survived else "0")
        resp = self.post("/actions/mini_games.php", files=files)
        if resp and resp.status_code == 200:
            try: return resp.json()
            except: pass
        return None

    def start_treasure_dig(self):
        if not self.game_list:
            return None
        resp = self.post("/actions/mini_games.php", data={"action": "quiz_start", "game": "treasure_dig"})
        if resp and resp.status_code == 200:
            try:
                data = resp.json()
                if data.get('status') == 'success':
                    self.treasure_token = data.get('quiz_token')
                    return self.treasure_token
            except: pass
        return None

    def play_single(self, game):
        if not self.game_list:
            return None
        if game in self.limited_games:
            self.log(f"{Y}⏭️ {game} sudah limit, skip{RESET}")
            return None
            
        if self.doubled_available.get(game, False) and self.retry_doubled.get(game, True):
            ad_progress(30, f"📺 {self.game_map[game]['display']} double ad")
            base = random.uniform(1e-7, 5e-6)
            result = self.play_game(game, doubled=True, base_reward=base)
            if result and result.get('status') == 'success':
                return result
            elif result and result.get('status') == 'error':
                if '2x bonus window has expired' in result.get('message', ''):
                    self.retry_doubled[game] = False
            else:
                return result

        if game == "lucky_wheel":
            return self.play_game(game, doubled=False)
        elif game == "slots":
            return self.play_game("slots", doubled=False)
        elif game == "scratch":
            return self.play_game("scratch", doubled=False)
        elif game == "treasure_dig":
            token = self.start_treasure_dig()
            if token:
                pick = random.randint(0, 8)
                return self.play_game("treasure_dig", pick=pick, quiz_token=token, answer_index=pick)
            else:
                self.log(f"{R}❌ Gagal ambil token treasure_dig{RESET}")
                self.cooldowns["treasure_dig"] = 30
                return None
        elif game == "coin_catch":
            score = random.randint(0, 5)
            bombed = False
            if random.random() < 0.2:
                bombed = True
                score = 0
            diamonds = random.randint(0, 1) if not bombed else 0
            return self.play_game(game, score=score, bombed=bombed, diamonds=diamonds)
        elif game == "flappy_coin":
            score = random.randint(0, 8)
            survived = score >= 3
            bombed = False
            if random.random() < 0.3:
                bombed = True
                score = 0
                survived = False
            return self.play_game(game, score=score, bombed=bombed, survived=survived)
        return None

    # ---------- Claim Daily ----------
    def claim_daily(self):
        if self.daily_claimed:
            return True
        if not self.cfg.init_data:
            self.log(f"{R}❌ init_data kosong{RESET}")
            return False
        self.log(f"📅 Claim daily {self.name}...")
        resp = self.post("/actions/daily_bonus_ajax.php", data={"action": "claim_daily"})
        if resp and resp.status_code == 200:
            try:
                result = resp.json()
                if result.get('success') or result.get('status') == 'success':
                    self.balance = safe_float(result.get('new_balance', self.balance))
                    self.daily_claimed = True
                    self.log(f"{G}✅ Daily claimed! Bal: {self.balance:.8f} {self.currency}{RESET}")
                    return True
                else:
                    msg = result.get('message', '')
                    if 'already claimed' in msg.lower():
                        self.daily_claimed = True
                        return True
                    self.log(f"{R}❌ Daily gagal: {msg}{RESET}")
                    return False
            except:
                if 'already' in str(resp.text).lower():
                    self.daily_claimed = True
                    return True
                return False
        return False

    # ---------- Display ----------
    def display_dashboard(self):
        try:
            self.get_games_status()
            lines = []
            lines.append(f"{GOLD}╔══════════════════════════════════════════════════════════╗")
            lines.append(f"{GOLD}║{RESET}  {C}{self.name.upper()}{RESET}  ({self.currency})                            {GOLD}║")
            lines.append(f"{GOLD}╠══════════════════════════════════════════════════════════╣")
            lines.append(f"{GOLD}║{RESET}  Balance : {G}{self.balance:.8f}{RESET}   {GOLD}║")
            if self.game_list:
                lines.append(f"{GOLD}╠══════════════════════════════════════════════════════════╣")
                for g in self.game_list:
                    icon = self.game_map[g]['icon']; disp = self.game_map[g]['display']
                    if g in self.limited_games:
                        st = "LIMIT 🚫"
                        sc = R
                    else:
                        st = self.status[g]
                        sc = G if st == "Ready" else Y
                    
                    twox = "2X" if self.doubled_available.get(g, False) and self.retry_doubled.get(g, True) else "-"
                    ply = self.play_counts[g]
                    rwd = self.rewards[g]
                    cd = self.fmt(self.cooldowns[g])
                    
                    if rwd <= 0.00000001:
                        reward_str = f"{G}0.00000000{RESET}"
                    else:
                        reward_str = f"{G}{rwd:.8f}{RESET}" if rwd < 0.001 else f"{G}{rwd:.2f}{RESET}"
                    
                    line = f"{GOLD}║{RESET}  {icon} {disp:<6} {sc}{st:<10}{RESET}  {twox:<5} {ply:<5} {reward_str:<16} {cd:<6}{GOLD}║"
                    lines.append(line)
            lines.append(f"{GOLD}╠══════════════════════════════════════════════════════════╣")
            for log in list(self.logs)[-6:]:
                log_clean = log[:48] if len(log) > 48 else log
                lines.append(f"{GOLD}║{RESET}  {log_clean}{' '*(50-len(log_clean))} {GOLD}║")
            lines.append(f"{GOLD}╚══════════════════════════════════════════════════════════╝")
            return "\n".join(lines)
        except Exception as e:
            return f"{R}❌ Error display: {e}{RESET}"

    def process_one_game(self):
        if not self.game_list:
            return False
        try:
            ready = self.get_ready_games()
            if not ready:
                if self.is_all_limited():
                    self.log(f"{R}🛑 {self.name} SEMUA GAME LIMIT! Bot di-stop{RESET}")
                    self.running = False
                return False
            
            for i in range(len(self.game_list)):
                idx = (self.game_index + i) % len(self.game_list)
                g = self.game_list[idx]
                if g in ready:
                    self.game_index = (idx + 1) % len(self.game_list)
                    break
            else:
                return False

            print(f"{C}🎮 {self.name} {self.game_map[g]['display']}...{RESET}")
            result = self.play_single(g)
            if result and result.get('status') == 'success':
                rwd = safe_float(result.get('reward', 0))
                if rwd == 0:
                    rwd = safe_float(result.get('base_reward', 0))
                self.balance = safe_float(result.get('new_balance', self.balance))
                self.rewards[g] = rwd
                self.play_counts[g] += 1
                if rwd > 0:
                    self.log(f"{G}✔ {self.game_map[g]['display']} +{rwd:.8f} (Bal: {self.balance:.8f}){RESET}")
                else:
                    self.log(f"{G}✔ {self.game_map[g]['display']} +0.00000000 (Bal: {self.balance:.8f}){RESET}")

                # Cek daily limit dari response (hanya jika daily_limit > 0)
                daily_played = result.get('daily_played')
                daily_limit = result.get('daily_limit')
                if daily_played is not None and daily_limit is not None and daily_limit > 0 and daily_played >= daily_limit:
                    self.limited_games.add(g)
                    self.log(f"{Y}⏭️ {self.game_map[g]['display']} daily limit reached ({daily_played}/{daily_limit}){RESET}")

                # Cek global limit (hanya jika global_limit > 0)
                global_played = result.get('global_played')
                global_limit = result.get('global_limit')
                if global_played is not None and global_limit is not None and global_limit > 0 and global_played >= global_limit:
                    self.log(f"{Y}🌍 Global limit reached ({global_played}/{global_limit}) — all games stop{RESET}")
                    for game in self.game_list:
                        self.limited_games.add(game)

            elif result and result.get('status') == 'error':
                err = result.get('message', '')
                if 'not logged in' in err.lower():
                    self.log(f"{Y}⚠️ Not logged in, reauth...{RESET}")
                    if self.reauth():
                        time.sleep(2)
                        result2 = self.play_single(g)
                        if result2 and result2.get('status') == 'success':
                            rwd = safe_float(result2.get('reward', 0))
                            self.balance = safe_float(result2.get('new_balance', self.balance))
                            self.rewards[g] = rwd
                            self.play_counts[g] += 1
                            self.log(f"{G}✔ {self.game_map[g]['display']} +{rwd:.8f} [retry OK]{RESET}")
                        else:
                            self.log(f"{R}✖ {self.game_map[g]['display']} FAIL [retry]{RESET}")
                    else:
                        self.log(f"{R}✖ Reauth gagal, skip{RESET}")
                elif 'daily_limit' in err.lower() or 'limit reached' in err.lower():
                    self.limited_games.add(g)
                    self.log(f"{Y}⏭️ {self.game_map[g]['display']} LIMIT REACHED, skip{RESET}")
                else:
                    self.log(f"{R}✖ {self.game_map[g]['display']} FAIL: {err}{RESET}")
            else:
                err = result.get('message','No resp') if result else 'No resp'
                self.log(f"{R}✖ {self.game_map[g]['display']} FAIL: {err}{RESET}")
            time.sleep(random.uniform(1, 3))
            self.get_dashboard()
            return True
        except Exception as e:
            self.log(f"{R}✖ Process error: {e}{RESET}")
            return False

# ========== BOT CLASSES ==========
class PepeBot(BaseBot):
    def __init__(self, cfg):
        super().__init__(PEPE_URL, cfg, PEPE_GAMES, PEPE_GAME_MAP, "PepeFlow", "PEPE")

class CoinBot(BaseBot):
    def __init__(self, cfg):
        super().__init__(COIN_URL, cfg, COIN_GAMES, COIN_GAME_MAP, "Coinszon", "COIN")

class MiniBot(BaseBot):
    def __init__(self, cfg):
        super().__init__(MINI_URL, cfg, MINI_GAMES, MINI_GAME_MAP, "MiniGramX", "GRAM")

class LitoshiBot(BaseBot):
    def __init__(self, cfg):
        super().__init__(LITOSHI_URL, cfg, LITOSHI_GAMES, LITOSHI_GAME_MAP, "LitoshiPay", "LTC")

# ========== MODE PARALLEL (untuk 2 bot) ==========
def parallel_pair(bots):
    for bot in bots:
        if hasattr(bot, 'claim_daily'):
            bot.claim_daily()
    
    while any(b.running for b in bots):
        any_played = False
        for bot in bots:
            if not bot.running:
                continue
            if bot.has_ready_games():
                os.system('clear')
                for b in bots:
                    if b.running:
                        print(b.display_dashboard())
                        print()
                print(f"{C}▶️ {bot.name} ada game ready, mainkan...{RESET}")
                bot.process_one_game()
                any_played = True
                time.sleep(0.5)
        
        if not any_played:
            all_cds = []
            for bot in bots:
                if bot.running:
                    all_cds.extend([cd for cd in bot.cooldowns.values() if cd > 0])
            if all_cds:
                min_cd = min(all_cds)
                os.system('clear')
                for b in bots:
                    if b.running:
                        print(b.display_dashboard())
                        print()
                print(f"{Y}⏳ Semua bot cooldown. Menunggu {min_cd} detik...{RESET}")
                live_timer(min_cd, f"⏳ Menunggu cooldown {min_cd}s")
            else:
                time.sleep(1)

# ========== SETUP PAIR ==========
def setup_pair(label1, file1, label2, file2):
    print(f"{Y}📝 Setup {label1} dan {label2}{RESET}")
    init1 = input(f"Masukkan init_data untuk {label1}: ").strip()
    if init1:
        cfg1 = BaseConfig(file1)
        cfg1.init_data = init1
        try:
            parsed = urllib.parse.parse_qs(init1)
            user_str = parsed.get('user', [None])[0]
            if user_str:
                u = json.loads(urllib.parse.unquote(user_str))
                cfg1.telegram_id = str(u.get('id',''))
                cfg1.telegram_username = u.get('username','')
        except:
            pass
        cfg1.save()
        print(f"{G}✅ {label1} tersimpan{RESET}")
    else:
        print(f"{R}❌ {label1} kosong, dilewati{RESET}")
    
    init2 = input(f"Masukkan init_data untuk {label2}: ").strip()
    if init2:
        cfg2 = BaseConfig(file2)
        cfg2.init_data = init2
        try:
            parsed = urllib.parse.parse_qs(init2)
            user_str = parsed.get('user', [None])[0]
            if user_str:
                u = json.loads(urllib.parse.unquote(user_str))
                cfg2.telegram_id = str(u.get('id',''))
                cfg2.telegram_username = u.get('username','')
        except:
            pass
        cfg2.save()
        print(f"{G}✅ {label2} tersimpan{RESET}")
    else:
        print(f"{R}❌ {label2} kosong, dilewati{RESET}")

# ========== MAIN ==========
def main():
    while True:
        os.system('clear')
        print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════╗
║   {GOLD}🚀 MULTI-BOT (PEPE+COINS / MINI+LITOSHI)          {PURPLE}║
║   {PINK}🔐 AUTH via init_data (NO PHPSESSID)              {PURPLE}║
║   {PINK}🎲 FINGERPRINT RANDOM setiap reauth               {PURPLE}║
║   {PINK}🚫 AUTO SKIP LIMIT (daily + global)               {PURPLE}║
╠══════════════════════════════════════════════════════════╣
║   {G}[1]{RESET} 🔄 Start PepeFlow X CoinsZons (parallel)  ║
║   {G}[2]{RESET} 🔄 Start LitoshiPay X MiniGramX (parallel)║
║   {Y}[3]{RESET} Setup initdata PepeFlow X CoinsZon       ║
║   {Y}[4]{RESET} Setup initdata LitoshiPay X MiniGramX    ║
║   {R}[0]{RESET} Exit                                     ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")
        choice = input(f"{PURPLE}❯ Pilih: {RESET}").strip()
        if choice == '0':
            sys.exit(0)
        elif choice == '1':
            pcfg = BaseConfig(PEPE_CONFIG)
            ccfg = BaseConfig(COIN_CONFIG)
            if not pcfg.load() or not pcfg.init_data:
                print(f"{R}❌ PepeFlow init_data belum disetup (menu 3){RESET}")
                input("Enter...")
                continue
            if not ccfg.load() or not ccfg.init_data:
                print(f"{R}❌ Coinszon init_data belum disetup (menu 3){RESET}")
                input("Enter...")
                continue
            pbot = PepeBot(pcfg)
            cbot = CoinBot(ccfg)
            try:
                parallel_pair([pbot, cbot])
            except KeyboardInterrupt:
                pass
            input("Enter...")
        elif choice == '2':
            lcfg = BaseConfig(LITOSHI_CONFIG)
            mcfg = BaseConfig(MINI_CONFIG)
            if not lcfg.load() or not lcfg.init_data:
                print(f"{R}❌ LitoshiPay init_data belum disetup (menu 4){RESET}")
                input("Enter...")
                continue
            if not mcfg.load() or not mcfg.init_data:
                print(f"{R}❌ MiniGramX init_data belum disetup (menu 4){RESET}")
                input("Enter...")
                continue
            lbot = LitoshiBot(lcfg)
            mbot = MiniBot(mcfg)
            try:
                parallel_pair([lbot, mbot])
            except KeyboardInterrupt:
                pass
            input("Enter...")
        elif choice == '3':
            setup_pair("PepeFlow", PEPE_CONFIG, "Coinszon", COIN_CONFIG)
            input("Enter...")
        elif choice == '4':
            setup_pair("LitoshiPay", LITOSHI_CONFIG, "MiniGramX", MINI_CONFIG)
            input("Enter...")
        else:
            print(f"{R}❌ Invalid{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}👋 Keluar.{RESET}")
        sys.exit(0)
