#!/usr/bin/env python3
"""
PRISM AUTO BOT v8 — HACKER EDITION
Flow: Daily → Ads (auto block) → Claim → Wait 1h → Next block → ...

By ScriptMaker: MoneyMaker_w
"""

import requests
import time
import random
import json
import os
import sys
import threading
from datetime import datetime, date, timedelta
from urllib.parse import parse_qs, unquote

# ==================== WARNA + NEON ====================
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BLUE    = "\033[94m"
    # Neon 256
    NG      = "\033[38;5;46m"    # neon green
    NC      = "\033[38;5;51m"    # neon cyan
    NP      = "\033[38;5;201m"   # neon pink
    NY      = "\033[38;5;226m"   # neon yellow
    NO      = "\033[38;5;208m"   # neon orange
    NM      = "\033[38;5;135m"   # neon purple
    NR      = "\033[38;5;196m"   # neon red
    DIMC    = "\033[38;5;240m"

CLEAR_LINE = "\033[K"


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def ts():
    return datetime.now().strftime("%H:%M:%S")


# ==================== HACKER ANIMATIONS ====================
class Hack:
    @staticmethod
    def matrix_rain(lines=6, width=60, duration=3.0):
        """Matrix rain animation selama `duration` detik."""
        chars = list("01ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉPRISM")
        start = time.time()
        canvas = [[' '] * width for _ in range(lines)]
        for _ in range(lines):
            print()
        while time.time() - start < duration:
            for _ in range(4):
                col = random.randint(0, width - 1)
                canvas[0][col] = random.choice(chars)
            for i in range(lines - 1, 0, -1):
                canvas[i] = canvas[i - 1][:]
            canvas[0] = [' '] * width
            sys.stdout.write(f"\033[{lines}A")
            for i, row in enumerate(canvas):
                color = C.NG if i < 1 else (C.GREEN if i < 2 else C.DIM + C.GREEN)
                sys.stdout.write(color + ''.join(row) + C.RESET + "\n")
            sys.stdout.flush()
            time.sleep(0.08)

    @staticmethod
    def boot_sequence(duration=3.0):
        """Boot sequence hacker selama 3 detik."""
        steps = [
            "Initializing kernel module...",
            "Loading stealth headers...",
            "Rotating device fingerprint...",
            "Connecting to prism-worker...",
            "Bypassing protection layers...",
            "Session ready.",
        ]
        per_step = duration / len(steps)
        print()
        for s in steps:
            sys.stdout.write(f"  {C.NG}[✓]{C.RESET} {C.WHITE}{s}{C.RESET}\n")
            sys.stdout.flush()
            time.sleep(per_step)
        print(f"  {C.NY}[⚡]{C.RESET} {C.WHITE}Status: {C.NG}SECURE{C.RESET}")
        print(f"  {C.NP}[★]{C.RESET} {C.WHITE}Welcome, {C.NC}Operative{C.RESET}\n")
        time.sleep(0.4)

    @staticmethod
    def typewriter(text, delay=0.015, color=None):
        c = color or C.WHITE
        for ch in text:
            sys.stdout.write(f"{c}{ch}{C.RESET}")
            sys.stdout.flush()
            time.sleep(delay)
        print()

    @staticmethod
    def glitch(text, duration=0.6):
        gc = "░▒▓█▄▀■□▪▫@#$%&*"
        start = time.time()
        while time.time() - start < duration:
            out = ''.join(random.choice(gc) if (random.randint(0, 10) < 2 and ch != ' ') else ch for ch in text)
            sys.stdout.write('\r' + CLEAR_LINE + f"  {C.NP}{out}{C.RESET}")
            sys.stdout.flush()
            time.sleep(0.06)
        sys.stdout.write('\r' + CLEAR_LINE + f"  {C.NC}{text}{C.RESET}\n")
        sys.stdout.flush()

    @staticmethod
    def spinner(text, duration=1.5):
        frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        start = time.time()
        i = 0
        while time.time() - start < duration:
            sys.stdout.write('\r' + CLEAR_LINE + f" {C.NC}{frames[i % 10]}{C.RESET} {C.WHITE}{text}{C.RESET}")
            sys.stdout.flush()
            time.sleep(0.08)
            i += 1
        sys.stdout.write('\r' + CLEAR_LINE + f" {C.NG}✓{C.RESET} {C.WHITE}{text}{C.RESET}\n")
        sys.stdout.flush()

    @staticmethod
    def loading_bar(text, duration=2.0, width=30):
        """Loading bar dengan progress."""
        start = time.time()
        while True:
            elapsed = time.time() - start
            if elapsed >= duration:
                break
            pct = min(1.0, elapsed / duration)
            filled = int(pct * width)
            bar = f"{C.NG}{'█' * filled}{C.DIMC}{'░' * (width - filled)}{C.RESET}"
            sys.stdout.write(f"\r {C.NC}▶{C.RESET} {C.WHITE}{text:<26}{C.RESET} [{bar}] {C.NY}{int(pct*100):3d}%{C.RESET}")
            sys.stdout.flush()
            time.sleep(0.05)
        sys.stdout.write('\r' + CLEAR_LINE)
        sys.stdout.write(f" {C.NG}✓{C.RESET} {C.WHITE}{text}{C.RESET}\n")
        sys.stdout.flush()


# ==================== BANNER ====================
BANNER = f"""{C.NC}{C.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██████╗ ██████╗ ██╗███████╗███╗   ███╗                        ║
║   ██╔══██╗██╔══██╗██║██╔════╝████╗ ████║                        ║
║   ██████╔╝██████╔╝██║███████╗██╔████╔██║                        ║
║   ██╔═══╝ ██╔══██╗██║╚════██║██║╚██╔╝██║                        ║
║   ██║     ██║  ██║██║███████║██║ ╚═╝ ██║                        ║
║   ╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚═╝                        ║
║                                                                  ║
║  {C.NP}🔥 PRISM AUTO BOT  {C.NC}│ {C.NG}v8.0 {C.NC}│ {C.NY}HACKER EDITION{C.NC}              ║
║                                                                  ║
║  {C.NG}▸ ScriptMaker : {C.NC}MoneyMaker_w{C.NC}                              ║
║  {C.NG}▸ Channel     : {C.NC}https://t.me/ScriptyXSouu{C.NC}                 ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝{C.RESET}
"""


def show_banner():
    print(BANNER)


# ==================== LOG ====================
def log(msg, level="INFO"):
    icons = {
        "INFO":  (C.NC,  "i"),
        "OK":    (C.NG,  "+"),
        "ERR":   (C.NR,  "x"),
        "WARN":  (C.NY,  "!"),
        "MONEY": (C.NG,  "$"),
        "WAIT":  (C.NY,  "~"),
        "AD":    (C.NC,  "A"),
        "DAILY": (C.NY,  "D"),
        "CLAIM": (C.NP,  "C"),
        "SKIP":  (C.DIM, "-"),
        "DONE":  (C.NG,  "#"),
        "CHECK": (C.NC,  "?"),
        "BLOCK": (C.NC,  "B"),
        "HACK":  (C.NG,  ">"),
    }
    color, icon = icons.get(level, (C.WHITE, "*"))
    print(f"{C.DIM}[{ts()}]{C.RESET} {color}[{icon}]{C.RESET} {msg}", flush=True)


def line(char="─", width=60, color=C.DIMC):
    print(f"{color}{char * width}{C.RESET}")


def header(title, icon=">", color=C.NC):
    print()
    print(f"{color}{'═' * 60}{C.RESET}")
    print(f"{color}  {icon}  {C.BOLD}{title}{C.RESET}")
    print(f"{color}{'═' * 60}{C.RESET}")


def progress_bar(seconds, label="Wait", color=C.NY, width=28):
    start = time.time()
    while True:
        elapsed = time.time() - start
        if elapsed >= seconds:
            break
        pct = elapsed / seconds
        filled = int(pct * width)
        bar = "█" * filled + "░" * (width - filled)
        rem = int(seconds - elapsed)

        hours, rem2 = divmod(rem, 3600)
        mins, secs = divmod(rem2, 60)
        if hours > 0:
            ts_str = f"{hours}h{mins:02d}m{secs:02d}s"
        elif mins > 0:
            ts_str = f"{mins}m{secs:02d}s"
        else:
            ts_str = f"{secs}s"

        sys.stdout.write(f"\r  {C.NC}[{C.NG}{bar}{C.RESET}{C.NC}]{C.RESET} {C.DIM}{label} | {ts_str}{C.RESET}   ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write(f"\r  {C.NG}[{'█' * width}]{C.RESET} {C.NG}{label} done{C.RESET}                    \n")
    sys.stdout.flush()


# ==================== KONFIG ====================
BASE_URL = "https://prism-worker.alokkumarsaw312.workers.dev"
ORIGIN = "https://prism-app-alok.pages.dev"
CONFIG_FILE = "prism_config.txt"

GENERIC_UA = (
    "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
)

AD_PER_CYCLE = 15
AD_DELAY = (3, 5)
AD_LOADING_RETRY = 5
AD_LOADING_WAIT = 8

MAX_BLOCKS = 3
BLOCK_COOLDOWN = 3600
DAILY_RESET_WAIT = 24 * 3600

AUTO_CLAIM = True
CLAIM_DELAY = 3

CYCLE_DELAY = 60


# ==================== INIT DATA ====================
def parse_init_data(init_data):
    try:
        parsed = parse_qs(init_data)
        return {k: (unquote(v[0]) if v else "") for k, v in parsed.items()}
    except Exception:
        return {}


def extract_user_from_init(init_data):
    parsed = parse_init_data(init_data)
    if "user" not in parsed:
        return None
    try:
        user = json.loads(parsed["user"])
        return {
            "userId": user.get("id"),
            "firstName": user.get("first_name", "User"),
            "username": user.get("username", ""),
        }
    except Exception:
        return None


def validate_init_data(init_data):
    if not init_data or len(init_data) < 50:
        return False, "terlalu pendek"
    parsed = parse_init_data(init_data)
    required = ["query_id", "user", "auth_date", "hash"]
    missing = [k for k in required if k not in parsed]
    if missing:
        return False, "field hilang: " + ", ".join(missing)
    user_info = extract_user_from_init(init_data)
    if not user_info or not user_info.get("userId"):
        return False, "user id tidak ada"
    return True, "OK"


# ==================== CONFIG ====================
def load_config():
    cfg = {"init_data": "", "token": ""}
    if not os.path.exists(CONFIG_FILE):
        return cfg
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    k, _, v = line.partition("=")
                    cfg[k.strip()] = v.strip()
    except Exception as e:
        log("config read error: " + str(e), "WARN")
    return cfg


def save_config(cfg):
    try:
        lines = ["# Prism Config", "# " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ""]
        for k, v in cfg.items():
            lines.append(k + "=" + str(v))
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        log("Config saved", "OK")
    except Exception as e:
        log("save error: " + str(e), "WARN")


def ask(prompt):
    while True:
        v = input(f"{C.NP}? {C.RESET}{prompt}\n{C.DIMC}  > {C.RESET}").strip()
        if v:
            return v
        log("Tidak boleh kosong", "WARN")


def get_init_data(cfg):
    if cfg.get("init_data"):
        try:
            use_saved = input(f"{C.NP}? Pakai initData tersimpan? [Y/n]: {C.RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return None
        if not use_saved or use_saved in ("y", "ya", "yes"):
            ok, msg = validate_init_data(cfg["init_data"])
            if ok:
                Hack.spinner("InitData OK", 1.2)
                return cfg["init_data"]

    print(f"{C.NY}CARA MENDAPATKAN INIT DATA:{C.RESET}")
    print(f"{C.DIMC}  1. Buka Prism di Telegram{C.RESET}")
    print(f"{C.DIMC}  2. DevTools -> Network -> cari request{C.RESET}")
    print(f"{C.DIMC}  3. Copy field 'initData'{C.RESET}")
    print()

    while True:
        init_data = ask("Paste initData:")
        ok, msg = validate_init_data(init_data)
        if ok:
            Hack.spinner("InitData OK", 1.2)
            return init_data
        log("Invalid: " + msg, "ERR")


# ==================== API ====================
class PrismAPI:
    def __init__(self, token=None):
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "*/*",
            "user-agent": GENERIC_UA,
            "origin": ORIGIN,
            "referer": ORIGIN + "/",
            "x-requested-with": "org.telegram.messenger",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
        })
        if token:
            self.session.headers["authorization"] = "Bearer " + token

    def get(self, path):
        try:
            r = self.session.get(BASE_URL + path, timeout=30)
            try:
                return r.status_code, r.json()
            except Exception:
                return r.status_code, {"raw": r.text[:200]}
        except Exception as e:
            return None, {"error": str(e)}

    def post(self, path, payload):
        try:
            r = self.session.post(BASE_URL + path, json=payload, timeout=30)
            try:
                return r.status_code, r.json()
            except Exception:
                return r.status_code, {"raw": r.text[:200]}
        except Exception as e:
            return None, {"error": str(e)}


# ==================== AUTH ====================
def authenticate(api, init_data):
    log("Authenticating...", "INFO")
    user_info = extract_user_from_init(init_data)
    if not user_info:
        log("Gagal extract user", "ERR")
        return None

    endpoints = [
        ("/api/auth/telegram", {"initData": init_data}),
        ("/api/auth", {"initData": init_data}),
        ("/api/login", {"initData": init_data}),
    ]

    for path, payload in endpoints:
        status, data = api.post(path, payload)
        if status == 200 and (data.get("token") or data.get("accessToken")):
            token = data.get("token") or data.get("accessToken")
            Hack.spinner("Login OK", 1.2)
            return {"token": token, "user": user_info}

    log("Auth gagal", "ERR")
    return None


# ==================== PROFILE ====================
def get_profile(api):
    status, data = api.get("/api/profile")
    if status == 200 and data.get("profile"):
        return data["profile"]
    return None


# ==================== PARSE BLOCK ====================
def parse_block_status(profile):
    b1 = profile.get("block1_watched", 0) or profile.get("block1Watched", 0)
    b2 = profile.get("block2_watched", 0) or profile.get("block2Watched", 0)
    b3 = profile.get("block3_watched", 0) or profile.get("block3Watched", 0)

    blocks = [
        {"id": 0, "name": "Block 1", "watched": b1, "done": b1 >= AD_PER_CYCLE},
        {"id": 1, "name": "Block 2", "watched": b2, "done": b2 >= AD_PER_CYCLE},
        {"id": 2, "name": "Block 3", "watched": b3, "done": b3 >= AD_PER_CYCLE},
    ]

    active_block = None
    for b in blocks:
        if not b["done"]:
            active_block = b
            break

    all_done = all(b["done"] for b in blocks)
    last_claim = profile.get("last_ads_claim") or profile.get("lastAdsClaim") or profile.get("last_ads_claim_at")

    return {
        "blocks": blocks,
        "active_block": active_block,
        "all_done": all_done,
        "last_claim": last_claim,
    }


def format_block_display(blocks):
    parts = []
    for b in blocks:
        status_icon = "✅" if b["done"] else ("🟡" if b["watched"] > 0 else "⭕")
        parts.append(f"{status_icon} {b['name']} {b['watched']}/15")
    return " | ".join(parts)


# ==================== DAILY ====================
def daily_claim(api):
    status, data = api.post("/api/daily/claim", {})

    if status == 200 and data.get("reward") is not None:
        return {
            "ok": True,
            "reward": data.get("reward", 0),
            "streak": data.get("streak", 0),
            "balance": data.get("balance", 0),
        }

    msg = str(data.get("error") or data.get("message") or data)
    if "already" in msg.lower() or "claimed" in msg.lower():
        return {"ok": False, "error": "Sudah claim"}
    return {"ok": False, "error": msg[:100]}


# ==================== WATCH AD ====================
def watch_ad(api, block=0):
    status, data = api.post("/api/ads/watch", {"block": block})

    if status == 200:
        return {
            "ok": True,
            "reward": data.get("reward", 0),
            "watched": data.get("watched", 0),
            "block_completed": data.get("blockCompleted", False),
            "balance": data.get("balance", 0),
        }

    err_msg = ""
    if isinstance(data, dict):
        err_msg = data.get("error") or data.get("message") or json.dumps(data)
    else:
        err_msg = str(data)
    return {"ok": False, "error": err_msg[:200], "status": status, "raw": data}


def is_loading_error(err_msg):
    err = str(err_msg).lower()
    return ("still loading" in err or "try again" in err or "few seconds" in err)


def is_no_ads_error(err_msg):
    err = str(err_msg).lower()
    return (
        "limit reached" in err or "no ads" in err or "not available" in err
        or "no more ads" in err or "block limit" in err or "ads limit" in err
        or "quota" in err or "cooldown" in err
    )


# ==================== CLAIM ====================
def claim_ads_reward(api, block=0):
    try:
        status, data = api.post("/api/ads/claim", {"block": block})
    except Exception as e:
        return {"ok": False, "error": str(e)}

    if status == 200:
        reward = data.get("reward", 0)
        balance = data.get("balance", 0)
        if reward > 0 or balance > 0:
            return {"ok": True, "reward": reward, "balance": balance}
        return {"ok": False, "error": "Response kosong"}

    err_msg = ""
    if isinstance(data, dict):
        err_msg = data.get("error") or data.get("message") or json.dumps(data)
    else:
        err_msg = str(data)
    return {"ok": False, "error": err_msg[:200], "status": status}


# ==================== FARM BLOCK ====================
def farm_block(api, block_id, block_name, stats):
    log(f"Mulai farming {block_name}...", "BLOCK")

    ads_done = 0
    ads_earned = 0
    consecutive_fail = 0
    block_completed = False
    no_ads = False

    for i in range(1, AD_PER_CYCLE + 1):
        result = None
        for retry in range(AD_LOADING_RETRY):
            result = watch_ad(api, block_id)
            if result["ok"]:
                break
            err = result.get("error", "")
            if is_loading_error(err):
                time.sleep(AD_LOADING_WAIT)
                continue
            break

        if not result or not result["ok"]:
            err = result.get("error", "?") if result else "no result"
            if is_no_ads_error(err):
                log(f"Ad #{i} limit reached: {err}", "WARN")
                no_ads = True
                break
            consecutive_fail += 1
            log(f"Ad #{i} gagal: {err}", "WARN")
            if consecutive_fail >= 3:
                log("3x gagal berturut — stop", "WARN")
                break
            time.sleep(random.uniform(*AD_DELAY))
            continue

        consecutive_fail = 0
        ads_done += 1
        reward = result["reward"]
        ads_earned += reward
        stats["ads_watched"] += 1
        if reward > 0:
            stats["earned"] += reward

        log(f"[{i:2}/{AD_PER_CYCLE}] +{reward:3} | bal: {result['balance']}", "MONEY")

        if result["block_completed"]:
            block_completed = True
            break

        if i < AD_PER_CYCLE:
            time.sleep(random.uniform(*AD_DELAY))

    return {
        "success": ads_done > 0,
        "ads_done": ads_done,
        "earned": ads_earned,
        "block_completed": block_completed,
        "no_ads": no_ads,
    }


# ==================== RUN CYCLE ====================
def run_cycle(api, stats, cycle_num):
    header(f"CYCLE #{cycle_num}", "▶", C.NP)

    profile = get_profile(api)
    if not profile:
        log("Gagal ambil profile", "ERR")
        return {"action": "error"}

    block_info = parse_block_status(profile)
    balance = profile.get("balance", 0)
    last_daily = profile.get("last_daily_claim", "") or profile.get("lastDailyClaim", "")

    log(f"Balance: {C.NG}{balance}{C.RESET}", "INFO")
    log(f"Blocks : {format_block_display(block_info['blocks'])}", "INFO")

    if block_info["all_done"]:
        log("Semua block sudah selesai hari ini", "DONE")
        return {"action": "all_done"}

    today = date.today().isoformat()
    last_daily_date = str(last_daily)[:10] if last_daily else ""

    if last_daily_date == today:
        log("Daily sudah diklaim", "SKIP")
    else:
        daily_result = daily_claim(api)
        if daily_result["ok"]:
            stats["daily_claims"] += 1
            stats["earned"] += daily_result["reward"]
            log(f"Daily +{daily_result['reward']} | Streak: {daily_result['streak']}", "MONEY")
        else:
            log(f"Daily: {daily_result['error']}", "WARN")

    active_block = block_info["active_block"]
    if not active_block:
        log("Tidak ada block aktif", "WARN")
        return {"action": "no_block"}

    block_id = active_block["id"]
    block_name = active_block["name"]
    block_watched = active_block["watched"]

    log(f"Block aktif: {C.NC}{block_name}{C.RESET} ({block_watched}/{AD_PER_CYCLE})", "BLOCK")

    if block_watched >= AD_PER_CYCLE:
        log(f"{block_name} sudah 15/15 — langsung claim", "CLAIM")
        if CLAIM_DELAY > 0:
            time.sleep(CLAIM_DELAY)
        claim_result = claim_ads_reward(api, block_id)
        if claim_result["ok"]:
            stats["claims"] += 1
            stats["earned"] += claim_result["reward"]
            log(f"CLAIM +{claim_result['reward']} | bal: {claim_result['balance']}", "MONEY")
            return {"action": "claimed", "block_id": block_id}
        else:
            err = claim_result.get("error", "")
            if "already" in str(err).lower():
                log("Sudah pernah claim", "SKIP")
                return {"action": "already_claimed"}
            log(f"Claim gagal: {err}", "WARN")
            return {"action": "claim_failed"}

    farm_result = farm_block(api, block_id, block_name, stats)
    total_watched = block_watched + farm_result["ads_done"]

    if farm_result["no_ads"] and total_watched < AD_PER_CYCLE:
        log(f"Iklan habis ({total_watched}/15) — belum bisa claim", "WARN")
        return {"action": "no_ads_partial"}

    if total_watched >= AD_PER_CYCLE:
        log(f"Block {block_name} selesai ({total_watched}/15) — CLAIM", "CLAIM")
        if CLAIM_DELAY > 0:
            time.sleep(CLAIM_DELAY)
        claim_result = claim_ads_reward(api, block_id)
        if claim_result["ok"]:
            stats["claims"] += 1
            stats["earned"] += claim_result["reward"]
            log(f"CLAIM +{claim_result['reward']} | bal: {claim_result['balance']}", "MONEY")
            return {"action": "claimed", "block_id": block_id, "next_wait": BLOCK_COOLDOWN}
        else:
            err = claim_result.get("error", "")
            log(f"Claim gagal: {err}", "WARN")
            return {"action": "claim_failed"}

    return {"action": "partial", "watched": total_watched}


def render_stats(stats, profile=None):
    print()
    print(f"{C.NP}  ╔{'═' * 56}╗{C.RESET}")
    print(f"{C.NP}  ║{C.RESET} {C.BOLD}{C.NC}  SESSION STATS{C.RESET}{' ' * 41}{C.NP}║{C.RESET}")
    print(f"{C.NP}  ╠{'═' * 56}╣{C.RESET}")

    if profile:
        balance = profile.get("balance", "?")
        block_info = parse_block_status(profile)
        print(f"{C.NP}  ║{C.RESET} {C.DIMC}Balance    :{C.RESET} {C.NG}{str(balance):<39}{C.NP}║{C.RESET}")
        print(f"{C.NP}  ║{C.RESET} {C.DIMC}Blocks     :{C.RESET} {format_block_display(block_info['blocks']):<39}{C.NP}║{C.RESET}")

    print(f"{C.NP}  ║{C.RESET} {C.DIMC}Daily      :{C.RESET} {C.NC}{str(stats['daily_claims']):<39}{C.NP}║{C.RESET}")
    print(f"{C.NP}  ║{C.RESET} {C.DIMC}Ads watched:{C.RESET} {C.NC}{str(stats['ads_watched']):<39}{C.NP}║{C.RESET}")
    print(f"{C.NP}  ║{C.RESET} {C.DIMC}Claims     :{C.RESET} {C.NP}{str(stats['claims']):<39}{C.NP}║{C.RESET}")
    print(f"{C.NP}  ║{C.RESET} {C.DIMC}Earned     :{C.RESET} {C.NG}+{str(int(stats['earned'])):<38}{C.NP}║{C.RESET}")
    print(f"{C.NP}  ╚{'═' * 56}╝{C.RESET}")


# ==================== MAIN ====================
def main():
    # ==== BOOT ANIMATION ====
    clear()
    print()

    # 1) Matrix rain 1.5s
    Hack.matrix_rain(lines=6, width=60, duration=1.5)

    # 2) Typewriter title
    print()
    Hack.typewriter("  >>> PRISM AUTO BOT v8.0", delay=0.012, color=C.NC)

    # 3) Glitch "HACKER EDITION"
    Hack.glitch("HACKER EDITION", 0.5)
    print()

    # 4) Boot sequence 3s
    Hack.boot_sequence(duration=3.0)

    # 5) Loading bar "initializing"
    Hack.loading_bar("Loading modules", 1.5)
    Hack.loading_bar("Fetching config", 1.0)

    time.sleep(0.5)
    clear()
    show_banner()

    if not isinstance(AD_DELAY, (tuple, list)) or len(AD_DELAY) != 2:
        print(f"{C.NR}[!] ERROR: AD_DELAY harus tuple 2 elemen{C.RESET}")
        sys.exit(1)

    cfg = load_config()

    token = None
    if cfg.get("token"):
        log("Token tersimpan ditemukan", "OK")
        try:
            use_saved = input(f"{C.NP}? Pakai token tersimpan? [Y/n]: {C.RESET}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not use_saved or use_saved in ("y", "ya", "yes"):
            token = cfg["token"]

    if not token:
        init_data = get_init_data(cfg)
        if not init_data:
            return

        print()
        api = PrismAPI()
        res = authenticate(api, init_data)
        if not res:
            log("Login gagal — keluar", "ERR")
            sys.exit(1)

        token = res["token"]
        cfg["init_data"] = init_data
        cfg["token"] = token
        save_config(cfg)

    api = PrismAPI(token)

    Hack.spinner("Fetching profile", 1.2)
    profile = get_profile(api)
    if not profile:
        log("Token tidak valid", "ERR")
        log("Hapus prism_config.txt dan jalankan ulang", "INFO")
        sys.exit(1)

    log(f"User    : {C.BOLD}@{profile.get('username', '?')}{C.RESET}", "OK")
    log(f"Balance : {C.NG}{profile.get('balance', 0)}{C.RESET}", "OK")

    block_info = parse_block_status(profile)
    log(f"Blocks  : {format_block_display(block_info['blocks'])}", "INFO")
    log(f"Auto claim: {C.NG}ON{C.RESET}", "INFO")

    stats = {
        "daily_claims": 0,
        "ads_watched": 0,
        "claims": 0,
        "earned": 0,
    }

    log("Auto loop aktif — Ctrl+C untuk stop", "OK")

    cycle = 0
    try:
        while True:
            cycle += 1

            try:
                result = run_cycle(api, stats, cycle)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                log(f"Cycle error: {e}", "ERR")
                result = {"action": "error"}

            fresh = get_profile(api)
            if fresh:
                profile = fresh

            render_stats(stats, profile)

            action = result.get("action", "unknown")

            if action == "all_done":
                log("Semua block selesai — tunggu reset harian", "WAIT")
                wait = DAILY_RESET_WAIT
                print()
                try:
                    progress_bar(wait, label="Reset harian", color=C.NY)
                except KeyboardInterrupt:
                    raise

            elif action == "claimed":
                log("Block selesai & claim — tunggu 1 jam untuk block berikutnya", "WAIT")
                wait = BLOCK_COOLDOWN
                print()
                try:
                    progress_bar(wait, label="Next block", color=C.NY)
                except KeyboardInterrupt:
                    raise

            elif action == "no_ads_partial":
                log("Iklan habis — tunggu 1 jam untuk coba lagi", "WAIT")
                wait = BLOCK_COOLDOWN
                print()
                try:
                    progress_bar(wait, label="Next try", color=C.NY)
                except KeyboardInterrupt:
                    raise

            elif action == "already_claimed":
                log("Sudah claim — tunggu 1 jam", "WAIT")
                wait = BLOCK_COOLDOWN
                print()
                try:
                    progress_bar(wait, label="Next block", color=C.NY)
                except KeyboardInterrupt:
                    raise

            elif action == "no_block":
                log("Tidak ada block aktif — tunggu 5 menit", "WAIT")
                wait = 300
                print()
                try:
                    progress_bar(wait, label="Wait", color=C.NP)
                except KeyboardInterrupt:
                    raise

            else:
                log("Cooldown pendek...", "WAIT")
                wait = CYCLE_DELAY
                print()
                try:
                    progress_bar(wait, label=f"Cooldown {wait}s", color=C.NP)
                except KeyboardInterrupt:
                    raise

    except KeyboardInterrupt:
        print()
        print()
        log("Dihentikan oleh user", "WARN")
        render_stats(stats, profile)
        log("Sampai jumpa", "OK")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print(f"{C.NY}Stopped.{C.RESET}")
        sys.exit(0)
    except Exception as e:
        print()
        print(f"{C.NR}Fatal: {e}{C.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
