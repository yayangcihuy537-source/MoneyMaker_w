#!/usr/bin/env python3
"""
MULTI-BOT: PepeFlow + Coinszon (Smart Dual Mode) - FIXED v2
"""

import os, sys, time, json, random, re, requests
from datetime import datetime
from collections import deque

R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'; C = '\033[96m'; W = '\033[97m'
GOLD = '\033[38;5;220m'; PURPLE = '\033[38;5;141m'; PINK = '\033[38;5;206m'
DIM = '\033[2m'; RESET = '\033[0m'

PEPE_CONFIG = "pepeflow_config.json"
COIN_CONFIG = "coinszon_config.json"
PEPE_URL = "https://pepeflow.com"
COIN_URL = "https://coinszon.com"
UA = "Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.7871.47 Mobile Safari/537.36 Telegram-Android/12.6.4"

PEPE_GAMES = ["lucky_wheel", "slots", "mystery_box"]
PEPE_GAME_MAP = {
    "lucky_wheel": {"display": "SPIN", "icon": "🎡"},
    "slots":       {"display": "TAP",  "icon": "🎰"},
    "mystery_box": {"display": "NEON", "icon": "🎁"},
}
COIN_GAMES = ["lucky_wheel", "slots", "mystery_box"]
COIN_GAME_MAP = {
    "lucky_wheel": {"display": "SPIN", "icon": "🎡"},
    "slots":       {"display": "TAP",  "icon": "🎰"},
    "mystery_box": {"display": "NEON", "icon": "🎁"},
}

class BaseConfig:
    def __init__(self, file):
        self.file = file
        self.phpsessid = None
        self.init_data = None
    def load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file) as f:
                    d = json.load(f)
                    self.phpsessid = d.get('phpsessid')
                    self.init_data = d.get('init_data')
                    return True
            except:
                return False
        return False
    def save(self):
        with open(self.file, 'w') as f:
            json.dump({'phpsessid': self.phpsessid, 'init_data': self.init_data}, f, indent=2)

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

def safe_float(val, default=0.0):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            cleaned = val.replace(',', '').strip()
            return float(cleaned)
        except:
            return default
    return default

def safe_int(val, default=0):
    return int(safe_float(val, default))

class MiniAppBot:
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
            self.session.cookies.set("PHPSESSID", cfg.phpsessid)
        self.balance = 0.0
        self.loop_counter = 0
        self.cooldowns = {g: 0 for g in game_list}
        self.play_counts = {g: 0 for g in game_list}
        self.doubled_available = {g: False for g in game_list}
        self.status = {g: "Ready" for g in game_list}
        self.rewards = {g: 0 for g in game_list}
        self.logs = deque(maxlen=10)
        self.running = True
        self.retry_doubled = {g: True for g in game_list}  # track retry for doubled

    def fmt(self, sec):
        if sec <= 0: return "Ready"
        m, s = divmod(int(sec), 60)
        return f"{m}m{s}s" if m else f"{s}s"

    def log(self, msg):
        t = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{t}] {msg}")

    def reauth(self):
        if not self.cfg.init_data:
            print(f"{R}❌ Tidak ada initData {self.name}!{RESET}")
            return False
        import urllib.parse
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
        }
        try:
            resp = self.session.post(f"{self.url}/actions/tg_auth.php", files=files)
            if resp.status_code == 200:
                for c in self.session.cookies:
                    if c.name == "PHPSESSID":
                        self.cfg.phpsessid = c.value
                        self.cfg.save()
                        print(f"{G}✅ {self.name} reauth OK{RESET}")
                        return True
                set_cookie = resp.headers.get('Set-Cookie','')
                if 'PHPSESSID' in set_cookie:
                    self.cfg.phpsessid = set_cookie.split('=')[1].split(';')[0]
                    self.cfg.save()
                    print(f"{G}✅ {self.name} reauth OK{RESET}")
                    return True
            print(f"{R}❌ {self.name} reauth gagal: {resp.status_code}{RESET}")
            return False
        except Exception as e:
            print(f"{R}❌ {self.name} reauth error: {e}{RESET}")
            return False

    def _get(self, endpoint):
        url = f"{self.url}{endpoint}"
        try:
            resp = self.session.get(url)
            if resp.status_code in [401,403] or (resp.status_code==200 and "Not logged in" in resp.text):
                if self.reauth():
                    resp = self.session.get(url)
                else:
                    self.running = False
            return resp
        except Exception as e:
            print(f"{R}❌ {self.name} GET error: {e}{RESET}")
            return None

    def _post(self, endpoint, files=None):
        url = f"{self.url}{endpoint}"
        try:
            resp = self.session.post(url, files=files)
            if resp.status_code in [401,403] or (resp.status_code==200 and "Not logged in" in resp.text):
                if self.reauth():
                    resp = self.session.post(url, files=files)
                else:
                    self.running = False
            return resp
        except Exception as e:
            print(f"{R}❌ {self.name} POST error: {e}{RESET}")
            return None

    def get_dashboard(self):
        resp = self._get("/pages/load_dashboard.php")
        if resp and resp.status_code == 200:
            if "pepeflow" in self.url:
                try:
                    data = resp.json()
                    self.balance = safe_float(data.get('balance', 0))
                    return data
                except: pass
            else:
                # Coinszon: balance di HTML
                html = resp.text
                patterns = [
                    r'id="dash-balance-pepe">\s*([\d.,]+)\s*<',
                    r'balance-pepe["\']?\s*[:>]\s*([\d.,]+)',
                    r'Balance:\s*([\d.,]+)',
                    r'class="balance"[^>]*>([\d.,]+)<',
                    r'(\d+\.\d+)\s*<span',  # fallback
                ]
                for p in patterns:
                    match = re.search(p, html, re.IGNORECASE)
                    if match:
                        self.balance = safe_float(match.group(1))
                        return html
                # fallback: cari angka di elemen dengan id dash-balance-pepe
                match = re.search(r'dash-balance-pepe[^>]*>([^<]+)</', html)
                if match:
                    self.balance = safe_float(match.group(1))
                return html
        return None

    def get_games_status(self):
        resp = self._get("/pages/load_games.php")
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
            # fallback: cari cooldown dari HTML
            for g in self.game_list:
                pattern = rf'{g}.*?cooldown.*?(\d+)'
                match = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
                if match:
                    self.cooldowns[g] = int(match.group(1))
                    self.status[g] = self.fmt(self.cooldowns[g]) if self.cooldowns[g] > 0 else "Ready"
        return None

    def play_game(self, game, doubled=False, base_reward=None, pick=None):
        files = {"action": (None, "play"), "game": (None, game),
                 "doubled": (None, "1" if doubled else "0")}
        if doubled and base_reward is not None:
            files["base_reward"] = (None, str(base_reward))
        if pick is not None:
            files["pick"] = (None, str(pick))
        resp = self._post("/actions/mini_games.php", files=files)
        if resp and resp.status_code == 200:
            try: return resp.json()
            except: pass
        return None

    def play_single(self, game):
        # Jika 2x tersedia dan belum pernah retry, coba doubled
        if self.doubled_available.get(game, False) and self.retry_doubled.get(game, True):
            # Coba dengan doubled
            doubled = True
            base = random.randint(10, 30)
            result = self.play_game(game, doubled=True, base_reward=base)
            if result and result.get('status') == 'success':
                # sukses
                return result
            elif result and result.get('status') == 'error':
                err = result.get('message', '')
                if '2x bonus window has expired' in err:
                    # Gagal karena 2x expired, tandai agar tidak coba doubled lagi
                    self.retry_doubled[game] = False
                    self.log(f"{Y}⚠️ 2x expired untuk {game}, fallback ke normal{RESET}")
                    # Lanjut ke normal claim
                else:
                    # error lain, return
                    return result
            else:
                # gagal total
                return result
        # Normal claim (tanpa doubled)
        if game == "lucky_wheel":
            return self.play_game(game, doubled=False)
        elif game == "slots":
            return self.play_game("slots")
        elif game == "mystery_box":
            pick = random.randint(0,7)
            return self.play_game("mystery_box", pick=pick)
        return None

    def display_dashboard(self):
        os.system('clear')
        self.get_games_status()
        print(f"{GOLD}╔══════════════════════════════════════════════════════════╗{RESET}")
        print(f"{GOLD}║{RESET}  {C}{self.name.upper()} AUTO-BOT{RESET}                              {GOLD}║{RESET}")
        print(f"{GOLD}╠══════════════════════════════════════════════════════════╣{RESET}")
        print(f"{GOLD}║{RESET}  Run/Loop : {C}{self.loop_counter}{RESET}      Balance : {G}{self.balance:.8f}{RESET}   {GOLD}║{RESET}")
        print(f"{GOLD}╠══════════════════════════════════════════════════════════╣{RESET}")
        for g in self.game_list:
            d = self.game_map[g]
            icon = d['icon']; disp = d['display']
            st = self.status[g]
            twox = "2X" if self.doubled_available[g] and self.retry_doubled.get(g, True) else "-"
            ply = self.play_counts[g]
            rwd = self.rewards[g]
            cd = self.fmt(self.cooldowns[g])
            sc = G if st == "Ready" else Y
            reward_str = f"{rwd:.8f}" if rwd < 0.001 else f"{rwd:.2f}"
            print(f"{GOLD}║{RESET}  {icon} {disp:<6} {sc}{st:<8}{RESET}  {twox:<5} {ply:<5} {reward_str:<12} {cd:<6}{GOLD}║{RESET}")
        print(f"{GOLD}╠══════════════════════════════════════════════════════════╣{RESET}")
        for log in list(self.logs)[-6:]:
            log_clean = log[:48] if len(log) > 48 else log
            print(f"{GOLD}║{RESET}  {log_clean}{' '*(50-len(log_clean))} {GOLD}║{RESET}")
        print(f"{GOLD}╚══════════════════════════════════════════════════════════╝{RESET}")

    def process_ready_games(self):
        try:
            self.get_games_status()
            ready = [g for g in self.game_list if self.cooldowns.get(g, 0) <= 0]
            if not ready:
                return False
            for g in ready:
                if not self.running: break
                self.display_dashboard()
                print(f"{C}🎮 {self.name} {self.game_map[g]['display']}...{RESET}")
                result = self.play_single(g)
                if result and result.get('status') == 'success':
                    rwd = safe_float(result.get('reward', 0))
                    self.balance = safe_float(result.get('new_balance', self.balance))
                    self.rewards[g] = rwd
                    self.play_counts[g] += 1
                    self.log(f"{G}✔ {self.game_map[g]['display']} +{rwd:.8f} (Bal: {self.balance:.8f})")
                elif result and result.get('status') == 'error':
                    err = result.get('message', '')
                    if 'not logged in' in err.lower():
                        self.log(f"{Y}⚠️ Not logged in, reauth...{RESET}")
                        self.reauth()
                        time.sleep(2)
                        result2 = self.play_single(g)
                        if result2 and result2.get('status') == 'success':
                            rwd = safe_float(result2.get('reward', 0))
                            self.balance = safe_float(result2.get('new_balance', self.balance))
                            self.rewards[g] = rwd
                            self.play_counts[g] += 1
                            self.log(f"{G}✔ {self.game_map[g]['display']} +{rwd:.8f} (Bal: {self.balance:.8f}) [retry OK]")
                        else:
                            err2 = result2.get('message','No resp') if result2 else 'No resp'
                            self.log(f"{R}✖ {self.game_map[g]['display']} FAIL: {err2} [retry failed]")
                    else:
                        self.log(f"{R}✖ {self.game_map[g]['display']} FAIL: {err}")
                else:
                    err = result.get('message','No resp') if result else 'No resp'
                    self.log(f"{R}✖ {self.game_map[g]['display']} FAIL: {err}")
                time.sleep(random.uniform(2, 5))

            self.get_dashboard()
            self.display_dashboard()
            return True
        except Exception as e:
            self.log(f"{R}✖ Process error: {e}{RESET}")
            return False

def smart_dual_loop(pbot, cbot):
    while pbot.running and cbot.running:
        try:
            played_p = pbot.process_ready_games()
            if not played_p:
                print(f"{Y}⏩ PepeFlow semua cooldown, switch ke Coinszon{RESET}")
            time.sleep(1)

            played_c = cbot.process_ready_games()
            if not played_c:
                print(f"{Y}⏩ Coinszon semua cooldown{RESET}")

            all_cds = list(pbot.cooldowns.values()) + list(cbot.cooldowns.values())
            all_cds = [cd for cd in all_cds if cd > 0]
            if all_cds:
                min_cd = min(all_cds)
                live_timer(min_cd, f"⏳ Menunggu game berikutnya")
        except KeyboardInterrupt:
            pbot.running = cbot.running = False
            break
        except Exception as e:
            print(f"{R}❌ Dual loop error: {e}{RESET}")
            time.sleep(5)

def set_phpsessid(file, label):
    print(f"{Y}📝 Masukkan PHPSESSID untuk {label}:{RESET}")
    sid = input("PHPSESSID: ").strip()
    print(f"{Y}📝 Masukkan InitData (boleh kosong):{RESET}")
    init = input("InitData: ").strip()
    if sid:
        cfg = BaseConfig(file)
        cfg.phpsessid = sid
        cfg.init_data = init
        cfg.save()
        print(f"{G}✅ {label} config saved.{RESET}")

def main():
    while True:
        os.system('clear')
        print(f"""
{PURPLE}╔══════════════════════════════════════════════════════════╗
║   {GOLD}🤖 MULTI-BOT (PepeFlow + Coinszon)                 {PURPLE}║
║   {PINK}Developer: @MoneyMaker_w                         {PURPLE}║
╠══════════════════════════════════════════════════════════╣
║   {G}[1]{RESET} 🐸 PepeFlow only                            ║
║   {C}[2]{RESET} 🪙 Coinszon only (No Withdraw)              ║
║   {Y}[3]{RESET} 🔄 Smart Dual Mode (PepeFlow ⇄ Coinszon)   ║
║   {W}[4]{RESET} 📝 Set PHPSESSID for PepeFlow              ║
║   {W}[5]{RESET} 📝 Set PHPSESSID + Init data for Coinszon  ║
║   {R}[0]{RESET} ❌ Exit                                   ║
╚══════════════════════════════════════════════════════════╝{RESET}
""")
        c = input(f"{PURPLE}❯ Pilih: {RESET}").strip()
        if c == '0':
            print(f"{Y}👋 Bye!{RESET}")
            sys.exit(0)
        elif c == '1':
            cfg = BaseConfig(PEPE_CONFIG)
            if not cfg.load() or not cfg.phpsessid:
                print(f"{R}❌ PepeFlow PHPSESSID belum diset!{RESET}")
                input("Enter..."); continue
            bot = MiniAppBot(PEPE_URL, cfg, PEPE_GAMES, PEPE_GAME_MAP, "PepeFlow")
            try:
                while bot.running:
                    bot.process_ready_games()
                    time.sleep(1)
            except KeyboardInterrupt:
                bot.running = False
            input("Enter...")
        elif c == '2':
            cfg = BaseConfig(COIN_CONFIG)
            if not cfg.load() or not cfg.phpsessid:
                print(f"{R}❌ Coinszon PHPSESSID belum diset!{RESET}")
                input("Enter..."); continue
            bot = MiniAppBot(COIN_URL, cfg, COIN_GAMES, COIN_GAME_MAP, "Coinszon")
            try:
                while bot.running:
                    bot.process_ready_games()
                    time.sleep(1)
            except KeyboardInterrupt:
                bot.running = False
            input("Enter...")
        elif c == '3':
            pcfg = BaseConfig(PEPE_CONFIG)
            ccfg = BaseConfig(COIN_CONFIG)
            if not pcfg.load() or not pcfg.phpsessid:
                print(f"{R}❌ PepeFlow PHPSESSID belum diset!{RESET}")
                input("Enter..."); continue
            if not ccfg.load() or not ccfg.phpsessid:
                print(f"{R}❌ Coinszon PHPSESSID belum diset!{RESET}")
                input("Enter..."); continue
            pbot = MiniAppBot(PEPE_URL, pcfg, PEPE_GAMES, PEPE_GAME_MAP, "PepeFlow")
            cbot = MiniAppBot(COIN_URL, ccfg, COIN_GAMES, COIN_GAME_MAP, "Coinszon")
            print(f"{Y}🔄 Smart Dual Mode started. Press Ctrl+C to stop.{RESET}")
            try:
                smart_dual_loop(pbot, cbot)
            except KeyboardInterrupt:
                pbot.running = cbot.running = False
            input("Enter...")
        elif c == '4':
            set_phpsessid(PEPE_CONFIG, "PepeFlow")
            input("Enter...")
        elif c == '5':
            set_phpsessid(COIN_CONFIG, "Coinszon")
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
