#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════╗
║     🐸 PEPE TAP MINER • AUTO FARMER v1.1 💀                     ║
║        uiiiaaas                                                           ║
║   🎯 Auto tap 20x per request                                    ║
║   ⚡ Auto turbo boost (5x multiplier)                            ║
║   🔋 Auto refill energy via same endpoint (kind=refill)          ║
║   🎬 Hacker animation (boot, loading, matrix, scan)              ║
║   👑 ScriptMaker: MoneyMaker_w                                    ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import os
import sys
import time
import json
import random
import requests
import hashlib
import uuid
import threading
from datetime import datetime, timezone
from urllib.parse import unquote, parse_qs


# ═══════════════════════════════════════════════════════════════
#  WARNA
# ═══════════════════════════════════════════════════════════════
class C:
    RED      = "\033[91m"
    GREEN    = "\033[92m"
    YELLOW   = "\033[93m"
    BLUE     = "\033[94m"
    MAGENTA  = "\033[95m"
    CYAN     = "\033[96m"
    WHITE    = "\033[97m"
    BOLD     = "\033[1m"
    DIM      = "\033[2m"
    RESET    = "\033[0m"
    SUCCESS  = "\033[38;5;118m"
    ERROR    = "\033[38;5;196m"
    WARN     = "\033[38;5;220m"
    INFO     = "\033[38;5;51m"
    GOLD     = "\033[38;5;220m"
    GREEN_M  = "\033[38;5;46m"
    GREEN_B  = "\033[38;5;82m"
    GREEN_L  = "\033[38;5;118m"
    PURPLE   = "\033[38;5;141m"
    PURPLE_L = "\033[38;5;177m"
    LAVENDER = "\033[38;5;183m"
    RED_GLOW = "\033[38;5;196m"
    CYAN_GLOW= "\033[38;5;51m"


PRINT_LOCK = threading.Lock()


def cprint(msg="", color=None, bold=False):
    c = color or ""
    b = C.BOLD if bold else ""
    with PRINT_LOCK:
        print(f"{b}{c}{msg}{C.RESET}", flush=True)


# ═══════════════════════════════════════════════════════════════
#  LOGO & LINES
# ═══════════════════════════════════════════════════════════════
def print_logo():
    print()
    cprint("     ██████╗ ███████╗██████╗ ███████╗", C.GREEN_M)
    cprint("     ██╔══██╗██╔════╝██╔══██╗██╔════╝", C.GREEN_M)
    cprint("     ██████╔╝█████╗  ██████╔╝█████╗  ", C.GREEN_B)
    cprint("     ██╔═══╝ ██╔══╝  ██╔═══╝ ██╔══╝  ", C.GREEN_B)
    cprint("     ██║     ███████╗██║     ███████╗", C.GREEN_L)
    cprint("     ╚═╝     ╚══════╝╚═╝     ╚══════╝", C.GREEN_L)
    print()
    cprint("           🐸 PEPE TAP MINER — AUTO FARMER v1.1 🐸", C.BOLD + C.GREEN_M)
    cprint("              👑 ScriptMaker: MoneyMaker_w", C.PURPLE_L)
    print()
    cprint("  " + "═" * 60, C.GREEN_M)


def line_eq(width=60, color=None):
    cprint("=" * width, color or C.GREEN_M)


def line_dash(width=60, color=None):
    cprint("─" * width, color or C.GREEN_B)


# ═══════════════════════════════════════════════════════════════
#  ANIMATIONS
# ═══════════════════════════════════════════════════════════════
def hacking_boot():
    """Boot sequence ala hacker."""
    os.system("cls" if os.name == "nt" else "clear")
    print_logo()
    print()

    boot_lines = [
        (f"{C.GREEN_M}[✓]{C.RESET} {C.GREEN_L}Initializing kernel module...{C.RESET}", 0.20),
        (f"{C.GREEN_M}[✓]{C.RESET} {C.GREEN_L}Loading TSS serializer...{C.RESET}", 0.15),
        (f"{C.GREEN_M}[✓]{C.RESET} {C.GREEN_L}Connecting to Lovable server...{C.RESET}", 0.22),
        (f"{C.GREEN_M}[✓]{C.RESET} {C.GREEN_L}Bypassing anti-bot detection...{C.RESET}", 0.18),
        (f"{C.GREEN_M}[✓]{C.RESET} {C.GREEN_L}Generating session fingerprint...{C.RESET}", 0.15),
        (f"{C.GREEN_M}[✓]{C.RESET} {C.GREEN_L}Warming up tap engine (20x/batch)...{C.RESET}", 0.15),
        (f"{C.GREEN_M}[✓]{C.RESET} {C.GREEN_L}Boost + refill module: READY{C.RESET}", 0.18),
        (f"{C.GOLD}[⚡]{C.RESET}  {C.GREEN_L}Node status: SECURE{C.RESET}", 0.15),
        (f"{C.GREEN_B}[★]{C.RESET}  {C.GREEN_L}System ready. Welcome, Operative.{C.RESET}", 0.20),
    ]
    for line, delay in boot_lines:
        print(f"  {line}")
        time.sleep(delay)
    print()
    line_eq()
    time.sleep(0.4)


def loading_bar(label="INITIALIZING", duration=1.5, color=None):
    """Loading bar dengan hex noise ala hacking."""
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start = time.time()
    i = 0
    col = color or C.GREEN_M
    while time.time() - start < duration:
        progress = (time.time() - start) / duration
        bar_len = 28
        filled = int(bar_len * progress)
        bar = "█" * filled + "░" * (bar_len - filled)
        frame = frames[i % len(frames)]
        hex_noise = "".join(random.choices("0123456789ABCDEF", k=6))
        line = (f"\r{col}┃{C.RESET} {C.GREEN_B}{frame}{C.RESET} "
                f"{C.GREEN_L}{label:<24}{C.RESET} {col}[{bar}]{C.RESET} "
                f"{C.GREEN_B}{int(progress*100):>3}%{C.RESET} {C.DIM}0x{hex_noise}{C.RESET}")
        sys.stdout.write(line)
        sys.stdout.flush()
        time.sleep(0.05)
        i += 1
    sys.stdout.write("\r" + " " * 110 + "\r")
    sys.stdout.flush()


def scan_animation(label="Scanning", duration=1.5):
    """Scanning bar ala hacker."""
    bar_len = 40
    start = time.time()
    i = 0
    while time.time() - start < duration:
        i += 1
        pos = i % (bar_len * 2)
        if pos < bar_len:
            fill = pos
        else:
            fill = bar_len * 2 - pos
        bar = f"{C.GREEN_M}{'█' * fill}{C.DIM}{'░' * (bar_len - fill)}{C.RESET}"
        noise = "".join(random.choices("01", k=14))
        sys.stdout.write(f"\r{C.GREEN_B}┃{C.RESET} {C.GREEN_L}{label}{C.RESET} {bar} {C.GREEN_B}[{noise}]{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.04)
    sys.stdout.write("\n")


def matrix_rain(width=58, height=5, duration=1.0):
    """Matrix rain effect."""
    chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉ0123456789"
    start = time.time()
    lines = [[' ' for _ in range(width)] for _ in range(height)]
    while time.time() - start < duration:
        for _ in range(3):
            col = random.randint(0, width - 1)
            lines[0][col] = random.choice(chars)
        for y in range(height - 1, 0, -1):
            lines[y] = lines[y-1].copy()
            lines[0] = [' ' for _ in range(width)]
        output = ""
        for y, row in enumerate(lines):
            line = "".join(row)
            intensity = C.GREEN_M if y < 2 else (C.GREEN_B if y < 3 else C.DIM)
            output += f"{intensity}{line}{C.RESET}\n"
        sys.stdout.write(f"\033[{height}A")
        sys.stdout.write(output)
        sys.stdout.flush()
        time.sleep(0.08)
    print()


def glitch_text(text, duration=0.8):
    """Text glitch effect."""
    glitch_chars = "!@#$%^&*()_+{}|:<>?~`"
    start = time.time()
    while time.time() - start < duration:
        result = "".join(random.choice(glitch_chars) if random.random() < 0.3 else ch for ch in text)
        sys.stdout.write(f"\r{C.GREEN_M}{result}{C.RESET}")
        sys.stdout.flush()
        time.sleep(0.05)
    sys.stdout.write(f"\r{C.GREEN_M}{text}{C.RESET}\n")


def pulse_animation(text, duration=1.2):
    """Pulsing text animation."""
    colors = [C.GREEN_M, C.GREEN_B, C.GREEN_L, C.GREEN_B, C.GREEN_M]
    start = time.time()
    i = 0
    while time.time() - start < duration:
        col = colors[i % len(colors)]
        sys.stdout.write(f"\r{col}{C.BOLD}  {text}{C.RESET}   ")
        sys.stdout.flush()
        time.sleep(0.12)
        i += 1
    sys.stdout.write("\r" + " " * (len(text) + 10) + "\r")
    sys.stdout.flush()


# ═══════════════════════════════════════════════════════════════
#  TSS SERIALIZATION (TanStack Start)
# ═══════════════════════════════════════════════════════════════
def tss_encode(obj, counter=None):
    """Encode Python object ke format TSS."""
    if counter is None:
        counter = [0]

    def _enc(val):
        if val is None:
            return {"t": 2, "s": 0}
        if val is True:
            return {"t": 2, "s": 1}
        if val is False:
            return {"t": 2, "s": 2}
        if isinstance(val, (int, float)):
            return {"t": 0, "s": val}
        if isinstance(val, str):
            return {"t": 1, "s": val}
        if isinstance(val, list):
            return {
                "t": 9, "i": counter[0],
                "a": [_enc(x) for x in val], "o": 0
            }
        if isinstance(val, dict):
            counter[0] += 1
            keys = list(val.keys())
            vals = [_enc(val[k]) for k in keys]
            return {
                "t": 10, "i": counter[0] - 1,
                "p": {"k": keys, "v": vals}, "o": 0
            }
        return {"t": 1, "s": str(val)}

    return _enc(obj)


def build_server_fn_payload(data_dict):
    """Build payload TSS untuk /_serverFn/ call."""
    inner = tss_encode(data_dict, counter=[0])
    return {
        "t": {
            "t": 10, "i": 0,
            "p": {"k": ["data"], "v": [inner]}, "o": 0
        },
        "f": 63,
        "m": []
    }


def tss_decode(node, cache=None):
    """Decode TSS response ke Python object."""
    if cache is None:
        cache = {}

    if not isinstance(node, dict):
        return node

    t = node.get("t")

    if t == 0:
        return node.get("s")
    if t == 1:
        return node.get("s")
    if t == 2:
        s = node.get("s")
        return {0: None, 1: True, 2: False}.get(s, None)

    if t == 9:
        idx = node.get("i", -1)
        arr = [tss_decode(x, cache) for x in node.get("a", [])]
        if idx >= 0:
            cache[idx] = arr
        return arr

    if t == 10:
        idx = node.get("i", -1)
        p = node.get("p", {})
        keys = p.get("k", [])
        vals = p.get("v", [])
        obj = {keys[i]: tss_decode(vals[i], cache) for i in range(min(len(keys), len(vals)))}
        if idx >= 0:
            cache[idx] = obj
        return obj

    if t == 11:
        idx = node.get("i", -1)
        return cache.get(idx)

    return node


def parse_response(resp_text):
    """Parse response text (NDJSON atau JSON biasa)."""
    text = resp_text.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    results = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        try:
            results.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return results if results else None


# ═══════════════════════════════════════════════════════════════
#  KONFIG
# ═══════════════════════════════════════════════════════════════
BASE_URL = "https://pepeminertap.lovable.app"

FN_TAP   = "d6c34d4220c777cceb07dfc1cb576fc88f72e9825c48d9e89550cff0249a618e"
FN_STATE = "61b5ecda5620dcf6c89aa3f75cbd73a5b50d96e6f83c5f81c6701e35244e9cf1"
FN_BOOST = "e7511189ffe36241e50aa0fbb623585efa31d4fa1acba26871f611c182e2b32f"

UA = ("Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 "
      "Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)")

CONFIG_FILE = "pepe_tap_config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"init_data": "", "session_id": ""}


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


# ═══════════════════════════════════════════════════════════════
#  BOT
# ═══════════════════════════════════════════════════════════════
class PepeTapBot:
    def __init__(self, init_data, session_id=""):
        self.init_data = init_data
        self.session = requests.Session()
        self.session.headers.update({
            "Host": "pepeminertap.lovable.app",
            "sec-ch-ua-platform": '"Android"',
            "user-agent": UA,
            "accept": "application/x-tss-framed, application/x-ndjson, application/json",
            "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Android WebView";v="152"',
            "content-type": "application/json",
            "sec-ch-ua-mobile": "?1",
            "x-tsr-serverfn": "true",
            "origin": BASE_URL,
            "x-requested-with": "org.telegram.messenger.web",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": f"{BASE_URL}/app",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "id,id-ID;q=0.9,en-US;q=0.8,en;q=0.7",
        })

        if not session_id:
            session_id = str(uuid.uuid4())
        self.session_id = session_id
        self.session.cookies.set("session-id", session_id, domain="pepeminertap.lovable.app")

        # State
        self.balance = 0
        self.energy = 0
        self.energy_max = 1000
        self.tap_reward = 500
        self.energy_per_tap = 5
        self.ad_break_taps = 30
        self.taps_since_ad = 0
        self.boost_active = False
        self.boost_until = None
        self.boost_multiplier = 1
        self.wallet = ""
        self.name = ""
        self.ref_count = 0

        # Stats
        self.total_taps = 0
        self.total_earned = 0
        self.claims = 0
        self.start_time = datetime.now()

    # ---------- HTTP ----------
    def _call_fn(self, fn_hash, data):
        url = f"{BASE_URL}/_serverFn/{fn_hash}"
        payload = build_server_fn_payload(data)
        try:
            r = self.session.post(url, json=payload, timeout=30)
            return r
        except Exception as e:
            return None

    def _extract_result(self, resp):
        if resp is None:
            return None
        if resp.status_code != 200:
            return {"__http_error__": resp.status_code, "__text__": resp.text[:200]}

        parsed = parse_response(resp.text)
        if not parsed:
            return None

        if isinstance(parsed, list):
            for item in parsed:
                dec = tss_decode(item)
                if isinstance(dec, dict) and "result" in dec:
                    return dec["result"]
            return parsed[0] if parsed else None

        dec = tss_decode(parsed)
        if isinstance(dec, dict) and "result" in dec:
            return dec["result"]
        return dec

    # ---------- Actions ----------
    def get_state(self):
        resp = self._call_fn(FN_STATE, {"initData": self.init_data})
        result = self._extract_result(resp)
        if not result or not isinstance(result, dict):
            return False

        player = result.get("player", {})
        settings = result.get("settings", {})
        referrals = result.get("referrals", {})

        if player:
            self.balance = player.get("balance", 0) or 0
            self.energy = player.get("energy", 0) or 0
            self.energy_max = player.get("energyMax", 1000) or 1000
            self.taps_since_ad = player.get("tapsSinceAd", 0) or 0
            self.wallet = player.get("wallet", "") or ""
            self.boost_active = bool(player.get("boostActive", False))
            self.boost_multiplier = player.get("boostMultiplier", 1) or 1
            self.boost_until = player.get("boostUntil")
            self.name = player.get("name", "") or ""
            self.ref_count = player.get("referralCount", 0) or 0

        if settings:
            self.tap_reward = settings.get("tapReward", 500) or 500
            self.energy_per_tap = settings.get("energyPerTap", 5) or 5
            self.ad_break_taps = settings.get("adBreakTaps", 30) or 30

        return True

    def do_tap(self, taps=20):
        resp = self._call_fn(FN_TAP, {
            "initData": self.init_data,
            "taps": taps,
        })
        if resp is None:
            return False, "no response"

        if resp.status_code != 200:
            return False, f"HTTP {resp.status_code}"

        parsed = parse_response(resp.text)
        if not parsed:
            return False, "invalid JSON"

        result = None
        if isinstance(parsed, list):
            for item in parsed:
                dec = tss_decode(item)
                if isinstance(dec, dict) and "result" in dec:
                    result = dec["result"]
                    break
        else:
            dec = tss_decode(parsed)
            if isinstance(dec, dict) and "result" in dec:
                result = dec["result"]

        if not result or not isinstance(result, dict):
            return False, "no result"

        if "error" in result and result["error"]:
            return False, str(result["error"])[:80]

        self.balance = result.get("balance", self.balance)
        self.energy = result.get("energy", self.energy)
        self.taps_since_ad = result.get("tapsSinceAd", self.taps_since_ad)

        return True, result

    def _call_boost_kind(self, kind):
        """Call boost endpoint dengan kind tertentu (turbo/refill)."""
        resp = self._call_fn(FN_BOOST, {
            "initData": self.init_data,
            "kind": kind,
        })
        if resp is None:
            return False, "no response"

        if resp.status_code != 200:
            return False, f"HTTP {resp.status_code}"

        parsed = parse_response(resp.text)
        result = None
        if isinstance(parsed, list):
            for item in parsed:
                dec = tss_decode(item)
                if isinstance(dec, dict) and "result" in dec:
                    result = dec["result"]
                    break
        else:
            dec = tss_decode(parsed)
            if isinstance(dec, dict) and "result" in dec:
                result = dec["result"]

        if not result or not isinstance(result, dict):
            return False, "no result"

        if "error" in result and result["error"]:
            return False, str(result["error"])[:80]

        # Update state
        if "energy" in result:
            self.energy = result["energy"]
        if "boostUntil" in result:
            self.boost_until = result["boostUntil"]
            self.boost_active = True
        if "boostMultiplier" in result:
            self.boost_multiplier = result["boostMultiplier"]

        return True, result

    def activate_turbo(self):
        return self._call_boost_kind("turbo")

    def refill_energy(self):
        return self._call_boost_kind("refill")

    # ---------- Display ----------
    def show_status(self):
        boost_str = "OFF"
        boost_color = C.DIM
        if self.boost_active:
            boost_str = f"ACTIVE x{self.boost_multiplier}"
            boost_color = C.SUCCESS

        wallet_display = (self.wallet[:16] + "...") if self.wallet else "(not set)"
        runtime = datetime.now() - self.start_time
        h, r = divmod(int(runtime.total_seconds()), 3600)
        m, s = divmod(r, 60)

        # Energy bar
        e_bar_len = 20
        e_filled = int((self.energy / self.energy_max) * e_bar_len) if self.energy_max > 0 else 0
        e_bar = f"{C.GREEN_M}{'█' * e_filled}{C.DIM}{'░' * (e_bar_len - e_filled)}{C.RESET}"

        print()
        line_eq()
        cprint(f"  🐸 {C.BOLD}{C.GREEN_M}PEPE TAP MINER — STATUS{C.RESET}", C.GREEN_M)
        line_eq()
        if self.name:
            cprint(f"  {C.SUCCESS}User     {C.RESET}: {C.BOLD}{C.GREEN_L}{self.name}{C.RESET}")
        cprint(f"  {C.SUCCESS}Balance  {C.RESET}: {C.BOLD}{C.GOLD}{self.balance:,}{C.RESET} PEPE")
        cprint(f"  {C.SUCCESS}Energy   {C.RESET}: [{e_bar}] {C.LAVENDER}{self.energy}/{self.energy_max}{C.RESET}")
        cprint(f"  {C.SUCCESS}Total Tap{C.RESET}: {C.LAVENDER}{self.total_taps:,}{C.RESET}")
        cprint(f"  {C.SUCCESS}Earned   {C.RESET}: {C.GOLD}{self.total_earned:,}{C.RESET} PEPE")
        cprint(f"  {C.SUCCESS}Claims   {C.RESET}: {C.LAVENDER}{self.claims}{C.RESET}")
        cprint(f"  {C.SUCCESS}Boost    {C.RESET}: {boost_color}{boost_str}{C.RESET}")
        cprint(f"  {C.SUCCESS}Refs     {C.RESET}: {C.LAVENDER}{self.ref_count}{C.RESET}")
        cprint(f"  {C.SUCCESS}Wallet   {C.RESET}: {C.DIM}{wallet_display}{C.RESET}")
        cprint(f"  {C.SUCCESS}Taps/Ad  {C.RESET}: {C.LAVENDER}{self.taps_since_ad}/{self.ad_break_taps}{C.RESET}")
        cprint(f"  {C.SUCCESS}Runtime  {C.RESET}: {C.LAVENDER}{h:02d}:{m:02d}:{s:02d}{C.RESET}")
        line_eq()

    # ---------- Auto farm ----------
    def auto_farm(self, tap_batch=20, max_refill=5):
        print()
        line_eq()
        cprint(f"  🚀 {C.BOLD}{C.GREEN_M}AUTO FARM STARTED{C.RESET}", C.GREEN_M)
        line_eq()
        cprint(f"  {C.SUCCESS}Tap batch      {C.RESET}: {C.GREEN_L}{tap_batch}x per request{C.RESET}")
        cprint(f"  {C.SUCCESS}Auto turbo     {C.RESET}: {C.GREEN_L}YES (when energy < 30%){C.RESET}")
        cprint(f"  {C.SUCCESS}Max refill     {C.RESET}: {C.GREEN_L}{max_refill}x{C.RESET}")
        print()
        cprint(f"  {C.WARN}⏹️  Tekan Ctrl+C untuk stop{C.RESET}")
        print()

        # Initial state
        pulse_animation("Fetching initial state...", 1.2)
        if not self.get_state():
            cprint(f"  {C.ERROR}✗ Gagal fetch state!{C.RESET}")
            return
        cprint(f"  {C.SUCCESS}✓ State OK{C.RESET} | Bal: {C.GOLD}{self.balance:,}{C.RESET} | Energy: {C.LAVENDER}{self.energy}/{self.energy_max}{C.RESET}")
        time.sleep(0.5)

        refill_count = 0
        cycle = 0

        while True:
            cycle += 1

            # Cek energy
            if self.energy < self.energy_per_tap * tap_batch:
                cprint(f"\n  {C.WARN}⚠ Energy rendah ({self.energy}){C.RESET}")

                # 1. Coba turbo dulu kalau belum aktif
                if not self.boost_active:
                    cprint(f"  {C.INFO}⚡ Activating turbo boost...{C.RESET}")
                    ok, msg = self.activate_turbo()
                    if ok:
                        cprint(f"  {C.SUCCESS}✓ Turbo ON! Energy: {self.energy}/{self.energy_max} x{self.boost_multiplier}{C.RESET}")
                        time.sleep(1)
                        continue

                # 2. Coba refill
                if refill_count < max_refill:
                    cprint(f"  {C.INFO}🔋 Refilling energy...{C.RESET}")
                    ok, msg = self.refill_energy()
                    if ok:
                        refill_count += 1
                        cprint(f"  {C.SUCCESS}✓ Refilled! {self.energy}/{self.energy_max} ({refill_count}/{max_refill}){C.RESET}")
                        time.sleep(1)
                        continue
                    else:
                        cprint(f"  {C.ERROR}✗ Refill gagal: {msg}{C.RESET}")

                # Energy habis
                if self.energy < self.energy_per_tap:
                    cprint(f"  {C.ERROR}✗ Energy habis. Tunggu 60s...{C.RESET}")
                    time.sleep(60)
                    self.get_state()
                    refill_count = 0
                    continue
                else:
                    taps = min(self.energy // self.energy_per_tap, tap_batch)
            else:
                taps = tap_batch

            # Cek ad break
            if self.taps_since_ad + taps >= self.ad_break_taps:
                remaining = self.ad_break_taps - self.taps_since_ad
                if remaining > 0:
                    taps = remaining

            # Execute tap
            print(f"  {C.INFO}▶ Cycle #{cycle:02d}{C.RESET} — Tap {C.BOLD}{C.GREEN_L}{taps}x{C.RESET}...")
            ok, data = self.do_tap(taps)

            if not ok:
                cprint(f"  {C.ERROR}✗ Tap gagal: {data}{C.RESET}")
                time.sleep(random.uniform(3, 6))
                continue

            earned = taps * self.tap_reward
            self.total_taps += taps
            self.total_earned += earned
            self.claims += 1

            cprint(f"  {C.SUCCESS}✓ +{earned:,} PEPE{C.RESET} | "
                   f"Bal: {C.GOLD}{self.balance:,}{C.RESET} | "
                   f"Energy: {C.LAVENDER}{self.energy}/{self.energy_max}{C.RESET} | "
                   f"Ad: {C.DIM}{self.taps_since_ad}/{self.ad_break_taps}{C.RESET}")

            # Ad break
            if self.taps_since_ad >= self.ad_break_taps:
                cprint(f"  {C.WARN}🎬 Ad break required! Tunggu 30s...{C.RESET}")
                for i in range(30, 0, -1):
                    sys.stdout.write(f"\r  {C.WARN}⏳ Ad cooldown: {i:02d}s{C.RESET}   ")
                    sys.stdout.flush()
                    time.sleep(1)
                sys.stdout.write("\r" + " " * 40 + "\r")
                self.get_state()

            delay = random.uniform(1.5, 3.5)
            time.sleep(delay)

    def claim_task(self, task_id):
        """Claim task reward (link kind, pakai endpoint task)."""
        # Task claim endpoint belum diketahui, skip
        return False, "not implemented"


# ═══════════════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════════════
def setup_config(cfg):
    os.system("cls" if os.name == "nt" else "clear")
    print_logo()
    line_eq()
    cprint(f"  ⚙️ {C.BOLD}{C.GREEN_M}SETUP CONFIGURATION{C.RESET}", C.GREEN_M)
    line_eq()
    print()

    cprint(f"  {C.GREEN_L}Init Data (Telegram WebApp){C.RESET}")
    cprint(f"     {C.DIM}Ambil dari URL hash: #tgWebAppData=query_id%3D...{C.RESET}")
    cprint(f"     {C.DIM}Atau dari request POST body 'initData'{C.RESET}")
    print()
    current = cfg.get("init_data", "")
    if current:
        cprint(f"     {C.LAVENDER}Current: {current[:60]}...{C.RESET}")
    new = input(f"  {C.GREEN_M}▸ Paste init data (kosong untuk skip): {C.RESET}").strip()
    if new:
        if "query_id=" not in new:
            cprint(f"  {C.ERROR}[!] Harus mengandung 'query_id='.{C.RESET}")
        else:
            if "tma " in new.lower():
                new = new.split("tma ", 1)[1]
            # URL decode kalau masih encoded
            if "%3D" in new or "%26" in new:
                new = unquote(new)
            cfg["init_data"] = new
            cprint(f"  {C.SUCCESS}✓ Init data disimpan ({len(new)} chars){C.RESET}")
            save_config(cfg)

    print()
    input(f"  {C.GREEN_M}Tekan ENTER untuk kembali...{C.RESET}")


def main():
    os.system("cls" if os.name == "nt" else "clear")
    print_logo()

    cfg = load_config()

    while True:
        print()
        line_eq()
        cprint(f"  🎮 {C.BOLD}{C.GREEN_M}MAIN MENU{C.RESET}", C.GREEN_M)
        line_eq()
        cprint(f"  {C.GREEN_L}[1]{C.RESET} 🚀  Auto Farm (Tap + Turbo + Refill)")
        cprint(f"  {C.GREEN_L}[2]{C.RESET} 📊  Check State / Status")
        cprint(f"  {C.GREEN_L}[3]{C.RESET} ⚡  Activate Turbo Boost (manual)")
        cprint(f"  {C.GREEN_L}[4]{C.RESET} 🔋  Refill Energy (manual)")
        cprint(f"  {C.GREEN_L}[5]{C.RESET} ⚙️   Setup Init Data")
        cprint(f"  {C.ERROR}[0]{C.RESET} ❌  Exit")
        line_eq()
        print()

        init_ok = f"{C.SUCCESS}✓{C.RESET}" if cfg.get("init_data") else f"{C.ERROR}✗{C.RESET}"
        cprint(f"  {C.DIM}Status: init={init_ok}{C.RESET}")
        print()

        choice = input(f"  {C.GREEN_M}▸ Pilih: {C.RESET}").strip()

        if choice == "0":
            glitch_text("SHUTTING DOWN...", 0.6)
            cprint(f"\n  {C.GREEN_M}👋 Bye!{C.RESET}")
            sys.exit(0)

        elif choice == "1":
            if not cfg.get("init_data"):
                cprint(f"\n  {C.ERROR}✗ Init data belum di-set! Pilih [5]{C.RESET}")
                input("  Tekan ENTER...")
                continue
            bot = PepeTapBot(cfg["init_data"], cfg.get("session_id", ""))
            try:
                bot.auto_farm(tap_batch=20, max_refill=5)
            except KeyboardInterrupt:
                print()
                cprint(f"\n  {C.WARN}⏹️  Auto farm dihentikan.{C.RESET}")
                bot.show_status()
                input("  Tekan ENTER...")

        elif choice == "2":
            if not cfg.get("init_data"):
                cprint(f"\n  {C.ERROR}✗ Init data belum di-set!{C.RESET}")
                input("  Tekan ENTER...")
                continue
            bot = PepeTapBot(cfg["init_data"], cfg.get("session_id", ""))
            loading_bar("Fetching state", 1.2)
            if bot.get_state():
                bot.show_status()
            else:
                cprint(f"  {C.ERROR}✗ Gagal fetch state!{C.RESET}")
            input("\n  Tekan ENTER...")

        elif choice == "3":
            if not cfg.get("init_data"):
                cprint(f"\n  {C.ERROR}✗ Init data belum di-set!{C.RESET}")
                input("  Tekan ENTER...")
                continue
            bot = PepeTapBot(cfg["init_data"], cfg.get("session_id", ""))
            loading_bar("Activating turbo", 1.0)
            ok, data = bot.activate_turbo()
            if ok:
                cprint(f"  {C.SUCCESS}✓ Turbo activated!{C.RESET}")
                cprint(f"  {C.LAVENDER}  Energy : {data.get('energy')}{C.RESET}")
                cprint(f"  {C.LAVENDER}  Until  : {data.get('boostUntil')}{C.RESET}")
                cprint(f"  {C.LAVENDER}  Multi  : x{data.get('boostMultiplier')}{C.RESET}")
            else:
                cprint(f"  {C.ERROR}✗ Gagal: {data}{C.RESET}")
            input("\n  Tekan ENTER...")

        elif choice == "4":
            if not cfg.get("init_data"):
                cprint(f"\n  {C.ERROR}✗ Init data belum di-set!{C.RESET}")
                input("  Tekan ENTER...")
                continue
            bot = PepeTapBot(cfg["init_data"], cfg.get("session_id", ""))
            loading_bar("Refilling energy", 1.0)
            ok, data = bot.refill_energy()
            if ok:
                cprint(f"  {C.SUCCESS}✓ Energy refilled!{C.RESET}")
                cprint(f"  {C.LAVENDER}  Energy : {data.get('energy')}{C.RESET}")
            else:
                cprint(f"  {C.ERROR}✗ Gagal: {data}{C.RESET}")
            input("\n  Tekan ENTER...")

        elif choice == "5":
            setup_config(cfg)
            cfg = load_config()

        else:
            cprint(f"  {C.ERROR}Pilihan tidak valid.{C.RESET}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        hacking_boot()
        loading_bar("Loading core modules", 1.0)
        matrix_rain(width=58, height=4, duration=0.8)
        scan_animation("Handshake with Lovable server", 1.0)
        time.sleep(0.3)
        main()
    except KeyboardInterrupt:
        print()
        glitch_text("SYSTEM SHUTDOWN...", 0.6)
        cprint(f"\n  {C.WARN}👋 Keluar.{C.RESET}")
        sys.exit(0)
