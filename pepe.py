#!/usr/bin/env python3
"""
TRIPLE-BOT PARALLEL (Pepe + Coin + Mini) - FIXED v2
- Reauth tidak mematikan bot
- Error handling lebih baik
- Cek init_data sebelum claim daily
"""

import os, sys, time, json, random, re, requests, urllib.parse
from datetime import datetime
from collections import deque

# ========== Warna ==========
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'; C = '\033[96m'; W = '\033[97m'
GOLD = '\033[38;5;220m'; PURPLE = '\033[38;5;141m'; PINK = '\033[38;5;206m'
RESET = '\033[0m'

# ========== KONFIGURASI ==========
PEPE_CONFIG = "pepeflow_config.json"
COIN_CONFIG  = "coinszon_config.json"
MINI_CONFIG  = "minigramx_config.json"

PEPE_URL = "https://pepeflow.com"
COIN_URL  = "https://coinszon.com"
MINI_URL  = "https://minigramx.top"

UA = "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.47 Mobile Safari/537.36 Telegram-Android/12.6.4"

# ---------- Game config ----------
PEPE_GAMES = ["lucky_wheel", "mystery_box"]
PEPE_GAME_MAP = {
    "lucky_wheel": {"display": "SPIN", "icon": "🎡"},
    "mystery_box": {"display": "NEON", "icon": "🎁"},
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

# ========== Config ==========
class BaseConfig:
    def __init__(self, file):
        self.file = file
        self.phpsessid = None
        self.init_data = None
        self.telegram_id = None
        self.telegram_username = None
    def load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file) as f:
                    d = json.load(f)
                    self.phpsessid = d.get('phpsessid')
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
                'phpsessid': self.phpsessid,
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
    def __init__(self, url, cfg, game_list, game_map, name):
        self.url = url
        self.cfg = cfg
        self.game_list = game_list
        self.game_map = game_map
        self.name = name
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
        if cfg.phpsessid:
            domain = url.replace('https://', '').split('/')[0]
            self.session.cookies.set("PHPSESSID", cfg.phpsessid, domain=domain, path='/')

        self.balance = 0.0
        self.loop_counter = 0
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
        self.last_display = ""

    def fmt(self, sec):
        if sec <= 0: return "Ready"
        m, s = divmod(int(sec), 60)
        return f"{m}m{s}s" if m else f"{s}s"

    def log(self, msg):
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    # ---------- REAUTH (TIDAK MATIKAN BOT) ----------
    def reauth(self):
        if not self.cfg.init_data:
            self.log(f"{R}❌ Tidak ada init_data untuk {self.name}{RESET}")
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

        files = {
            "init_data": (None, self.cfg.init_data),
            "telegram_id": (None, tid),
            "telegram_username": (None, tuname),
            "auto_login": (None, "1"),
            "fingerprint": (None, "de79799dd411d00634a2959334a5fcc1"),
        }
        try:
            resp = self.session.post(f"{self.url}/actions/tg_auth.php", files=files)
            if resp.status_code == 200:
                new_sid = None
                for c in self.session.cookies:
                    if c.name == "PHPSESSID":
                        new_sid = c.value
                        break
                if not new_sid:
                    set_cookie = resp.headers.get('Set-Cookie', '')
                    if 'PHPSESSID' in set_cookie:
                        match = re.search(r'PHPSESSID=([^;]+)', set_cookie)
                        if match:
                            new_sid = match.group(1)
                if new_sid:
                    domain = self.url.replace('https://', '').split('/')[0]
                    self.session.cookies.set("PHPSESSID", new_sid, domain=domain, path='/')
                    self.cfg.phpsessid = new_sid
                    self.cfg.save()
                    self.log(f"{G}✅ {self.name} reauth OK{RESET}")
                    return True
            return False
        except Exception as e:
            self.log(f"{R}❌ Reauth error: {e}{RESET}")
            return False

    # ---------- HTTP (TIDAK MATIKAN BOT) ----------
    def _request(self, method, endpoint, **kwargs):
        if not self.running:
            return None
        url = f"{self.url}{endpoint}"
        try:
            resp = self.session.request(method, url, **kwargs)
            if resp.status_code in [401,403] or (resp.status_code==200 and "Not logged" in resp.text):
                self.log(f"{Y}⚠️ Session expired, reauth...{RESET}")
                if self.reauth():
                    resp = self.session.request(method, url, **kwargs)
                    if "Not logged" in resp.text:
                        self.log(f"{R}❌ Session masih invalid{RESET}")
                        # JANGAN matikan bot, biarkan loop lanjut
                        return None
                else:
                    self.log(f"{R}❌ Reauth gagal, lanjut tanpa session{RESET}")
                    return None
            return resp
        except Exception as e:
            self.log(f"{R}❌ Request error: {e}{RESET}")
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
                r'id="header-user-balance"[^>]*>([\d.,]+)\s*GRAM',
                r'id="dash-balance-coin">([\d.,]+)',
                r'id="dash-balance-pepe">\s*([\d.,]+)',
                r'Balance:\s*([\d.,]+)',
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
                    return data
                except: pass
            for g in self.game_list:
                pattern = rf'{g}.*?cooldown.*?(\d+)'
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    self.cooldowns[g] = int(match.group(1))
                    self.status[g] = self.fmt(self.cooldowns[g]) if self.cooldowns[g] > 0 else "Ready"
        return None

    def has_ready_games(self):
        try:
            self.get_games_status()
            return any(cd <= 0 for cd in self.cooldowns.values())
        except:
            return False

    # ---------- Play ----------
    def play_game(self, game, doubled=False, base_reward=None, pick=None, quiz_token=None, answer_index=None):
        files = {"action": (None, "play"), "game": (None, game),
                 "doubled": (None, "1" if doubled else "0")}
        if doubled and base_reward is not None:
            files["base_reward"] = (None, str(base_reward))
        if pick is not None:
            files["pick"] = (None, str(pick))
        if quiz_token is not None:
            files["quiz_token"] = (None, str(quiz_token))
        if answer_index is not None:
            files["answer_index"] = (None, str(answer_index))
        resp = self.post("/actions/mini_games.php", files=files)
        if resp and resp.status_code == 200:
            try: return resp.json()
            except: pass
        return None

    def play_single(self, game):
        raise NotImplementedError

    def claim_daily(self):
        if self.daily_claimed:
            return True
        # Cek init_data sebelum claim
        if not self.cfg.init_data:
            self.log(f"{R}❌ init_data kosong, tidak bisa claim daily{RESET}")
            return False
        self.log(f"📅 Claim daily {self.name}...")
        if "pepeflow" in self.url or "coinszon" in self.url:
            resp = self.post("/actions/daily_bonus_claim.php", data={"cf_response": "", "ad_watched": "0"})
        else:
            resp = self.post("/actions/daily_bonus_ajax.php", data={"action": "claim_daily"})
        if resp and resp.status_code == 200:
            try:
                result = resp.json()
                if result.get('success') or result.get('status') == 'success':
                    self.balance = safe_float(result.get('new_balance', self.balance))
                    self.daily_claimed = True
                    self.log(f"{G}✅ Daily claimed! Bal: {self.balance:.8f}{RESET}")
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
            lines.append(f"{GOLD}║{RESET}  {C}{self.name.upper()}{RESET}                                    {GOLD}║")
            lines.append(f"{GOLD}╠══════════════════════════════════════════════════════════╣")
            lines.append(f"{GOLD}║{RESET}  Loop : {C}{self.loop_counter}{RESET}        Balance : {G}{self.balance:.8f}{RESET}   {GOLD}║")
            lines.append(f"{GOLD}╠══════════════════════════════════════════════════════════╣")
            for g in self.game_list:
                icon = self.game_map[g]['icon']; disp = self.game_map[g]['display']
                st = self.status[g]
                twox = "2X" if self.doubled_available.get(g, False) and self.retry_doubled.get(g, True) else "-"
                ply = self.play_counts[g]
                rwd = self.rewards[g]
                cd = self.fmt(self.cooldowns[g])
                sc = G if st == "Ready" else Y
                reward_str = f"{rwd:.8f}" if rwd < 0.001 else f"{rwd:.2f}"
                line = f"{GOLD}║{RESET}  {icon} {disp:<6} {sc}{st:<8}{RESET}  {twox:<5} {ply:<5} {reward_str:<12} {cd:<6}{GOLD}║"
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
        """Mainkan satu game yang ready"""
        try:
            self.get_games_status()
            ready = [g for g in self.game_list if self.cooldowns.get(g, 0) <= 0]
            if not ready:
                return False
            # Round-robin
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
                self.balance = safe_float(result.get('new_balance', self.balance))
                self.rewards[g] = rwd
                self.play_counts[g] += 1
                self.log(f"{G}✔ {self.game_map[g]['display']} +{rwd:.8f} (Bal: {self.balance:.8f}){RESET}")
            elif result and result.get('status') == 'error':
                err = result.get('message', '')
                if 'not logged in' in err.lower():
                    self.log(f"{Y}⚠️ Not logged in, coba reauth...{RESET}")
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

# ========== PEPEFLOW ==========
class PepeBot(BaseBot):
    def __init__(self, cfg):
        super().__init__(PEPE_URL, cfg, PEPE_GAMES, PEPE_GAME_MAP, "PepeFlow")

    def play_single(self, game):
        if game == "lucky_wheel":
            return self.play_game(game, doubled=False)
        elif game == "mystery_box":
            pick = random.randint(0, 7)
            return self.play_game("mystery_box", pick=pick)
        return None

# ========== COINSZON ==========
class CoinBot(BaseBot):
    def __init__(self, cfg):
        super().__init__(COIN_URL, cfg, COIN_GAMES, COIN_GAME_MAP, "Coinszon")

    def play_single(self, game):
        if game == "lucky_wheel":
            return self.play_game(game, doubled=False)
        elif game == "slots":
            return self.play_game("slots", doubled=False)
        return None

# ========== MINIGRAMX ==========
class MiniBot(BaseBot):
    def __init__(self, cfg):
        super().__init__(MINI_URL, cfg, MINI_GAMES, MINI_GAME_MAP, "MiniGramX")
        self.treasure_token = None

    def start_treasure_dig(self):
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
        if self.doubled_available.get(game, False) and self.retry_doubled.get(game, True):
            ad_progress(30, f"📺 {self.game_map[game]['display']} double ad")
            base = random.randint(10, 30)
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
        return None

# ========== PARALLEL LOOP ==========
def parallel_loop(bots):
    # Cek init_data
    for bot in bots:
        if not bot.cfg.init_data:
            print(f"{Y}⚠️ {bot.name} tidak punya init_data. Masukkan sekarang:{RESET}")
            bot.cfg.init_data = input("init_data: ").strip()
            bot.cfg.save()
    
    # Claim daily untuk semua
    print(f"{C}📅 Claiming daily bonuses...{RESET}")
    for bot in bots:
        bot.claim_daily()
    
    last_display = ""
    while all(b.running for b in bots):
        any_played = False
        for bot in bots:
            try:
                if bot.has_ready_games() and bot.running:
                    current_display = "\n".join([b.display_dashboard() for b in bots])
                    if current_display != last_display:
                        os.system('clear')
                        print(current_display)
                        last_display = current_display
                    print(f"{C}▶️ {bot.name} ada game ready, mainkan...{RESET}")
                    bot.process_one_game()
                    any_played = True
                    time.sleep(0.5)
            except Exception as e:
                print(f"{R}❌ Error pada {bot.name}: {e}{RESET}")
                bot.running = False
        
        if not any_played:
            all_cds = []
            for bot in bots:
                all_cds.extend([cd for cd in bot.cooldowns.values() if cd > 0])
            if all_cds:
                min_cd = min(all_cds)
                current_display = "\n".join([b.display_dashboard() for b in bots])
                if current_display != last_display:
                    os.system('clear')
                    print(current_display)
                    last_display = current_display
                print(f"{Y}⏳ Semua bot cooldown. Menunggu {min_cd} detik...{RESET}")
                # Tunggu 5 detik lalu re-check
                time.sleep(5)
            else:
                time.sleep(1)

# ========== SETUP ==========
def setup_config(file, label):
    print(f"{Y}📝 Setup {label}{RESET}")
    sid = input("PHPSESSID: ").strip()
    init = input("init_data (boleh kosong): ").strip()
    if sid:
        cfg = BaseConfig(file)
        cfg.phpsessid = sid
        cfg.init_data = init if init else None
        cfg.save()
        print(f"{G}✅ {label} tersimpan{RESET}")

# ========== MAIN ==========
def main():
    while True:
        os.system('clear')
        print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════╗
║   {GOLD}🤖 TRIPLE-BOT PARALLEL (Pepe + Coin + Mini)        {PURPLE}║
╠══════════════════════════════════════════════════════════╣
║   {G}[1]{RESET} Jalankan Semua (parallel)                 ║
║   {G}[2]{RESET} PepeFlow only                           ║
║   {G}[3]{RESET} Coinszon only                           ║
║   {G}[4]{RESET} MiniGramX only                          ║
║   {Y}[5]{RESET} Setup PepeFlow                          ║
║   {Y}[6]{RESET} Setup Coinszon                          ║
║   {Y}[7]{RESET} Setup MiniGramX                         ║
║   {R}[0]{RESET} Exit                                   ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")
        choice = input(f"{PURPLE}❯ Pilih: {RESET}").strip()
        if choice == '0':
            sys.exit(0)
        elif choice == '1':
            pcfg = BaseConfig(PEPE_CONFIG); ccfg = BaseConfig(COIN_CONFIG); mcfg = BaseConfig(MINI_CONFIG)
            if not pcfg.load() or not pcfg.phpsessid:
                print(f"{R}❌ PepeFlow belum disetup{RESET}"); input("Enter..."); continue
            if not ccfg.load() or not ccfg.phpsessid:
                print(f"{R}❌ Coinszon belum disetup{RESET}"); input("Enter..."); continue
            if not mcfg.load() or not mcfg.phpsessid:
                print(f"{R}❌ MiniGramX belum disetup{RESET}"); input("Enter..."); continue
            pbot = PepeBot(pcfg); cbot = CoinBot(ccfg); mbot = MiniBot(mcfg)
            try:
                parallel_loop([pbot, cbot, mbot])
            except KeyboardInterrupt:
                print(f"\n{Y}⏹ Dihentikan user{RESET}")
            except Exception as e:
                print(f"{R}❌ Error: {e}{RESET}")
            input("Enter...")
        elif choice == '2':
            cfg = BaseConfig(PEPE_CONFIG)
            if not cfg.load() or not cfg.phpsessid:
                print(f"{R}❌ Setup dulu (menu 5){RESET}"); input("Enter..."); continue
            bot = PepeBot(cfg)
            bot.claim_daily()
            try:
                while bot.running:
                    if bot.has_ready_games():
                        os.system('clear')
                        print(bot.display_dashboard())
                        bot.process_one_game()
                    else:
                        cds = [cd for cd in bot.cooldowns.values() if cd > 0]
                        if cds:
                            os.system('clear')
                            print(bot.display_dashboard())
                            print(f"{Y}⏳ {bot.name} cooldown, tunggu {min(cds)} detik...{RESET}")
                            time.sleep(5)
                        else:
                            time.sleep(1)
            except KeyboardInterrupt:
                bot.running = False
            input("Enter...")
        elif choice == '3':
            cfg = BaseConfig(COIN_CONFIG)
            if not cfg.load() or not cfg.phpsessid:
                print(f"{R}❌ Setup dulu (menu 6){RESET}"); input("Enter..."); continue
            bot = CoinBot(cfg)
            bot.claim_daily()
            try:
                while bot.running:
                    if bot.has_ready_games():
                        os.system('clear')
                        print(bot.display_dashboard())
                        bot.process_one_game()
                    else:
                        cds = [cd for cd in bot.cooldowns.values() if cd > 0]
                        if cds:
                            os.system('clear')
                            print(bot.display_dashboard())
                            print(f"{Y}⏳ {bot.name} cooldown, tunggu {min(cds)} detik...{RESET}")
                            time.sleep(5)
                        else:
                            time.sleep(1)
            except KeyboardInterrupt:
                bot.running = False
            input("Enter...")
        elif choice == '4':
            cfg = BaseConfig(MINI_CONFIG)
            if not cfg.load() or not cfg.phpsessid:
                print(f"{R}❌ Setup dulu (menu 7){RESET}"); input("Enter..."); continue
            bot = MiniBot(cfg)
            bot.claim_daily()
            try:
                while bot.running:
                    if bot.has_ready_games():
                        os.system('clear')
                        print(bot.display_dashboard())
                        bot.process_one_game()
                    else:
                        cds = [cd for cd in bot.cooldowns.values() if cd > 0]
                        if cds:
                            os.system('clear')
                            print(bot.display_dashboard())
                            print(f"{Y}⏳ {bot.name} cooldown, tunggu {min(cds)} detik...{RESET}")
                            time.sleep(5)
                        else:
                            time.sleep(1)
            except KeyboardInterrupt:
                bot.running = False
            input("Enter...")
        elif choice == '5':
            setup_config(PEPE_CONFIG, "PepeFlow"); input("Enter...")
        elif choice == '6':
            setup_config(COIN_CONFIG, "Coinszon"); input("Enter...")
        elif choice == '7':
            setup_config(MINI_CONFIG, "MiniGramX"); input("Enter...")
        else:
            print(f"{R}❌ Invalid{RESET}"); time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}👋 Keluar.{RESET}")
        sys.exit(0)
