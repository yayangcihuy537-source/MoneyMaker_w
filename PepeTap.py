#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════╗
║     🐸 PEPE TAP MINER • AUTO FARMER v1.0 💀                     ║
║                                                                   ║
║   🎯 Auto tap 20x per request                                    ║
║   ⚡ Auto activate turbo boost (5x multiplier)                   ║
║   🔋 Auto refill energy kalau habis                              ║
║   🎁 Auto claim task reward                                      ║
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
import urllib.parse
from datetime import datetime, timezone
from collections import deque


# ═══════════════════════════════════════════════════════════════
#  WARNA & ANIMASI
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
    PURPLE   = "\033[38;5;135m"
    PURPLE_B = "\033[38;5;141m"
    PURPLE_L = "\033[38;5;177m"
    PURPLE_D = "\033[38;5;93m"
    LAVENDER = "\033[38;5;183m"
    SUCCESS  = "\033[38;5;118m"
    ERROR    = "\033[38;5;196m"
    WARN     = "\033[38;5;220m"
    INFO     = "\033[38;5;51m"
    GOLD     = "\033[38;5;220m"
    GREEN_M  = "\033[38;5;46m"


def cprint(msg="", color=None, bold=False):
    c = color or ""
    b = C.BOLD if bold else ""
    print(f"{b}{c}{msg}{C.RESET}", flush=True)


def print_logo():
    print()
    cprint("     ██████╗ ███████╗██████╗ ███████╗", C.GREEN_M)
    cprint("     ██╔══██╗██╔════╝██╔══██╗██╔════╝", C.GREEN_M)
    cprint("     ██████╔╝█████╗  ██████╔╝█████╗  ", C.GREEN_M)
    cprint("     ██╔═══╝ ██╔══╝  ██╔═══╝ ██╔══╝  ", C.SUCCESS)
    cprint("     ██║     ███████╗██║     ███████╗", C.SUCCESS)
    cprint("     ╚═╝     ╚══════╝╚═╝     ╚══════╝", C.SUCCESS)
    print()
    cprint("           🐸 PEPE TAP MINER — AUTO FARMER 🐸", C.BOLD + C.GREEN_M)
    cprint("              👑 ScriptMaker: MoneyMaker_w", C.PURPLE_L)
    print()
    cprint("  " + "═" * 60, C.GREEN_M)


def line_eq(width=60, color=None):
    cprint("=" * width, color or C.GREEN_M)


def line_dash(width=60, color=None):
    cprint("─" * width, color or C.SUCCESS)


def loading_bar(label="INITIALIZING", duration=1.5):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    start = time.time()
    i = 0
    while time.time() - start < duration:
        progress = (time.time() - start) / duration
        bar_len = 28
        filled = int(bar_len * progress)
        bar = "█" * filled + "░" * (bar_len - filled)
        frame = frames[i % len(frames)]
        hex_noise = "".join(random.choices("0123456789ABCDEF", k=6))
        line = (f"\r{C.GREEN_M}┃{C.RESET} {C.SUCCESS}{frame}{C.RESET} "
                f"{C.GREEN_M}{label:<22}{C.RESET} {C.SUCCESS}[{bar}]{C.RESET} "
                f"{C.GREEN_M}{int(progress*100):>3}%{C.RESET} {C.DIM}0x{hex_noise}{C.RESET}")
        sys.stdout.write(line)
        sys.stdout.flush()
        time.sleep(0.05)
        i += 1
    sys.stdout.write("\r" + " " * 100 + "\r")
    sys.stdout.flush()


# ═══════════════════════════════════════════════════════════════
#  TSS SERIALIZATION (TanStack Start)
#  Format: binary JSON khusus Lovable app
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

    # primitive
    if t == 0:
        return node.get("s")
    if t == 1:
        return node.get("s")
    if t == 2:
        s = node.get("s")
        # 0=null, 1=true, 2=false
        return {0: None, 1: True, 2: False}.get(s, None)

    # array
    if t == 9:
        idx = node.get("i", -1)
        arr = [tss_decode(x, cache) for x in node.get("a", [])]
        if idx >= 0:
            cache[idx] = arr
        return arr

    # object
    if t == 10:
        idx = node.get("i", -1)
        p = node.get("p", {})
        keys = p.get("k", [])
        vals = p.get("v", [])
        obj = {keys[i]: tss_decode(vals[i], cache) for i in range(min(len(keys), len(vals)))}
        if idx >= 0:
            cache[idx] = obj
        return obj

    # reference
    if t == 11:
        idx = node.get("i", -1)
        return cache.get(idx)

    return node


def parse_response(resp_text):
    """Parse response text (bisa NDJSON atau JSON biasa)."""
    text = resp_text.strip()
    if not text:
        return None

    # Coba JSON biasa
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Coba NDJSON (baris per baris)
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

# Server function hashes (dari dump request)
FN_TAP     = "d6c34d4220c777cceb07dfc1cb576fc88f72e9825c48d9e89550cff0249a618e"
FN_STATE   = "61b5ecda5620dcf6c89aa3f75cbd73a5b50d96e6f83c5f81c6701e35244e9cf1"
FN_BOOST   = "e7511189ffe36241e50aa0fbb623585efa31d4fa1acba26871f611c182e2b32f"
FN_TASK    = ""   # belum diketahui, isi manual kalau ada
FN_REFILL  = ""   # belum diketahui, isi manual kalau ada

UA = ("Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 "
      "Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)")

CONFIG_FILE = "pepe_tap_config.json"


# ═══════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except:
            pass
    return {"init_data": "", "session_id": "", "refill_endpoint": "", "task_endpoint": ""}


def save_config(cfg):
    with open(CONFIG_FILE, "w") as f:
        json.dump(cfg, f, indent=2)


# ═══════════════════════════════════════════════════════════════
#  BOT
# ═══════════════════════════════════════════════════════════════
class PepeTapBot:
    def __init__(self, init_data, session_id="", refill_endpoint="", task_endpoint=""):
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

        # Set session cookie (kalau ada)
        if session_id:
            self.session.cookies.set("session-id", session_id, domain="pepeminertap.lovable.app")
        else:
            # Generate random session ID
            session_id = str(uuid.uuid4())
            self.session.cookies.set("session-id", session_id, domain="pepeminertap.lovable.app")
            self.session_id = session_id

        self.session_id = session_id
        self.refill_endpoint = refill_endpoint
        self.task_endpoint = task_endpoint

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

        # Stats
        self.total_taps = 0
        self.total_earned = 0
        self.claims = 0
        self.start_time = datetime.now()

    # ---------- HTTP helper ----------
    def _call_fn(self, fn_hash, data):
        """Call server function dengan TSS encoding."""
        url = f"{BASE_URL}/_serverFn/{fn_hash}"
        payload = build_server_fn_payload(data)
        try:
            r = self.session.post(url, json=payload, timeout=30)
            return r
        except Exception as e:
            return None

    def _call_tap(self, taps):
        return self._call_fn(FN_TAP, {
            "initData": self.init_data,
            "taps": taps,
        })

    def _call_state(self):
        return self._call_fn(FN_STATE, {
            "initData": self.init_data,
        })

    def _call_boost(self, kind="turbo"):
        return self._call_fn(FN_BOOST, {
            "initData": self.init_data,
            "kind": kind,
        })

    # ---------- Parse response ----------
    def _extract_result(self, resp):
        """Extract result dari response TSS."""
        if resp is None:
            return None
        if resp.status_code != 200:
            return {"__http_error__": resp.status_code, "__text__": resp.text[:200]}

        parsed = parse_response(resp.text)
        if not parsed:
            return None

        # Kalau list (NDJSON), ambil yang ada "result"
        if isinstance(parsed, list):
            for item in parsed:
                if isinstance(item, dict) and "result" in str(item)[:200]:
                    decoded = tss_decode(item)
                    if isinstance(decoded, dict) and "result" in decoded:
                        return decoded["result"]
            # Fallback: coba decode tiap item
            for item in parsed:
                decoded = tss_decode(item)
                if isinstance(decoded, dict) and "result" in decoded:
                    return decoded["result"]
            return parsed[0] if parsed else None

        # Kalau dict, decode langsung
        decoded = tss_decode(parsed)
        if isinstance(decoded, dict) and "result" in decoded:
            return decoded["result"]
        return decoded

    # ---------- Actions ----------
    def get_state(self):
        """Fetch account state."""
        resp = self._call_state()
        result = self._extract_result(resp)
        if not result or not isinstance(result, dict):
            return False

        player = result.get("player", {})
        settings = result.get("settings", {})

        if player:
            self.balance = player.get("balance", 0) or 0
            self.energy = player.get("energy", 0) or 0
            self.energy_max = player.get("energyMax", 1000) or 1000
            self.taps_since_ad = player.get("tapsSinceAd", 0) or 0
            self.wallet = player.get("wallet", "") or ""
            self.boost_active = bool(player.get("boostActive", False))
            self.boost_multiplier = player.get("boostMultiplier", 1) or 1
            self.boost_until = player.get("boostUntil")

        if settings:
            self.tap_reward = settings.get("tapReward", 500) or 500
            self.energy_per_tap = settings.get("energyPerTap", 5) or 5
            self.ad_break_taps = settings.get("adBreakTaps", 30) or 30

        return True

    def do_tap(self, taps=20):
        """Send tap request (batch 20x)."""
        resp = self._call_tap(taps)
        if resp is None:
            return False, "no response"

        if resp.status_code != 200:
            return False, f"HTTP {resp.status_code}"

        parsed = parse_response(resp.text)
        if not parsed:
            return False, "invalid JSON"

        # Cari result dalam list
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

    def activate_boost(self, kind="turbo"):
        """Activate turbo/full energy boost."""
        resp = self._call_boost(kind)
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

        self.energy = result.get("energy", self.energy)
        self.boost_until = result.get("boostUntil", self.boost_until)
        self.boost_multiplier = result.get("boostMultiplier", self.boost_multiplier)
        return True, result

    def refill_energy(self):
        """Refill energy via custom endpoint."""
        if not self.refill_endpoint:
            return False, "no endpoint"

        url = f"{BASE_URL}/_serverFn/{self.refill_endpoint}"
        payload = build_server_fn_payload({"initData": self.init_data})
        try:
            r = self.session.post(url, json=payload, timeout=30)
            if r.status_code != 200:
                return False, f"HTTP {r.status_code}"
            parsed = parse_response(r.text)
            dec = tss_decode(parsed[0] if isinstance(parsed, list) else parsed)
            result = dec.get("result") if isinstance(dec, dict) else None
            if result and isinstance(result, dict):
                self.energy = result.get("energy", self.energy)
                return True, result
            return False, "no result"
        except Exception as e:
            return False, str(e)

    # ---------- Display ----------
    def show_status(self):
        boost_str = "OFF"
        boost_color = C.DIM
        if self.boost_active:
            boost_str = f"ACTIVE x{self.boost_multiplier}"
            boost_color = C.SUCCESS

        wallet_display = (self.wallet[:14] + "...") if self.wallet else "(not set)"
        runtime = datetime.now() - self.start_time
        h, r = divmod(int(runtime.total_seconds()), 3600)
        m, s = divmod(r, 60)

        print()
        line_eq()
        cprint(f"  🐸 {C.BOLD}{C.GREEN_M}PEPE TAP MINER — STATUS{C.RESET}", C.GREEN_M)
        line_eq()
        cprint(f"  {C.SUCCESS}Balance  {C.RESET}: {C.BOLD}{C.GOLD}{self.balance:,}{C.RESET} PEPE")
        cprint(f"  {C.SUCCESS}Energy   {C.RESET}: {C.LAVENDER}{self.energy}/{self.energy_max}{C.RESET}")
        cprint(f"  {C.SUCCESS}Total Tap{C.RESET}: {C.LAVENDER}{self.total_taps}{C.RESET}")
        cprint(f"  {C.SUCCESS}Earned   {C.RESET}: {C.GOLD}{self.total_earned:,}{C.RESET} PEPE")
        cprint(f"  {C.SUCCESS}Claims   {C.RESET}: {C.LAVENDER}{self.claims}{C.RESET}")
        cprint(f"  {C.SUCCESS}Boost    {C.RESET}: {boost_color}{boost_str}{C.RESET}")
        cprint(f"  {C.SUCCESS}Wallet   {C.RESET}: {C.DIM}{wallet_display}{C.RESET}")
        cprint(f"  {C.SUCCESS}Taps/Ad  {C.RESET}: {C.LAVENDER}{self.taps_since_ad}/{self.ad_break_taps}{C.RESET}")
        cprint(f"  {C.SUCCESS}Runtime  {C.RESET}: {C.LAVENDER}{h:02d}:{m:02d}:{s:02d}{C.RESET}")
        line_eq()

    # ---------- Auto farm ----------
    def auto_farm(self, tap_batch=20, max_energy_refill=5):
        print()
        line_eq()
        cprint(f"  🚀 {C.BOLD}{C.GREEN_M}AUTO FARM STARTED{C.RESET}", C.GREEN_M)
        line_eq()
        cprint(f"  {C.SUCCESS}Tap batch{C.RESET}: {tap_batch}x per request")
        cprint(f"  {C.SUCCESS}Max refill{C.RESET}: {max_energy_refill}x")
        print()
        cprint(f"  {C.WARN}⏹️  Tekan Ctrl+C untuk stop{C.RESET}")
        print()
        time.sleep(1)

        # Fetch state awal
        if not self.get_state():
            cprint(f"  {C.ERROR}✗ Gagal fetch state!{C.RESET}")
            return
        cprint(f"  {C.SUCCESS}✓ State OK{C.RESET} | Balance: {C.GOLD}{self.balance:,}{C.RESET} | Energy: {C.LAVENDER}{self.energy}/{self.energy_max}{C.RESET}")
        time.sleep(0.5)

        refill_count = 0
        cycle = 0

        while True:
            cycle += 1

            # 1. Cek energy
            if self.energy < self.energy_per_tap * tap_batch:
                cprint(f"\n  {C.WARN}⚠ Energy rendah ({self.energy}){C.RESET}")

                # Coba refill dulu
                if refill_count < max_energy_refill:
                    if self.refill_endpoint:
                        cprint(f"  {C.INFO}🔋 Refill energy...{C.RESET}")
                        ok, msg = self.refill_energy()
                        if ok:
                            refill_count += 1
                            cprint(f"  {C.SUCCESS}✓ Energy refilled: {self.energy}/{self.energy_max} ({refill_count}/{max_energy_refill}){C.RESET}")
                            continue
                        else:
                            cprint(f"  {C.ERROR}✗ Refill gagal: {msg}{C.RESET}")
                    else:
                        cprint(f"  {C.WARN}⚠ Refill endpoint belum di-set (menu 4){C.RESET}")

                # Kalau gak bisa refill, tunggu regen atau stop
                if self.energy < self.energy_per_tap:
                    cprint(f"  {C.ERROR}✗ Energy habis. Tunggu 60s...{C.RESET}")
                    time.sleep(60)
                    self.get_state()
                    continue
                else:
                    # Bisa tap sedikit
                    taps = self.energy // self.energy_per_tap
                    taps = min(taps, tap_batch)

            else:
                taps = tap_batch

            # 2. Cek ad break
            if self.taps_since_ad + taps >= self.ad_break_taps:
                cprint(f"  {C.WARN}⚠ Ad break triggered ({self.taps_since_ad + taps}/{self.ad_break_taps}){C.RESET}")
                # Coba tap sampai ad break
                remaining = self.ad_break_taps - self.taps_since_ad
                if remaining > 0:
                    taps = remaining

            # 3. Execute tap
            cprint(f"\n  {C.INFO}▶ Cycle #{cycle:02d}{C.RESET} — Tap {C.BOLD}{taps}x{C.RESET}...")
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
                   f"Ad: {self.taps_since_ad}/{self.ad_break_taps}")

            # 4. Auto boost (turbo) kalau energy mau habis tapi boost belum aktif
            if not self.boost_active and self.energy < self.energy_max * 0.3:
                cprint(f"  {C.INFO}⚡ Trying to activate turbo boost...{C.RESET}")
                ok, bdata = self.activate_boost("turbo")
                if ok:
                    self.boost_active = True
                    cprint(f"  {C.SUCCESS}✓ Turbo boost activated! x{self.boost_multiplier}{C.RESET}")
                else:
                    cprint(f"  {C.DIM}  Boost tidak tersedia: {bdata}{C.RESET}")

            # 5. Kalau ad break triggered, pause
            if self.taps_since_ad >= self.ad_break_taps:
                cprint(f"  {C.WARN}🎬 Ad break required! Tunggu 30s untuk reset...{C.RESET}")
                time.sleep(30)
                # Refresh state
                self.get_state()

            # 6. Delay antar batch
            delay = random.uniform(1.5, 3.5)
            time.sleep(delay)

    def claim_task(self):
        """Claim task reward."""
        if not self.task_endpoint:
            return False, "no endpoint"

        url = f"{BASE_URL}/_serverFn/{self.task_endpoint}"
        payload = build_server_fn_payload({"initData": self.init_data})
        try:
            r = self.session.post(url, json=payload, timeout=30)
            if r.status_code != 200:
                return False, f"HTTP {r.status_code}"
            parsed = parse_response(r.text)
            dec = tss_decode(parsed[0] if isinstance(parsed, list) else parsed)
            result = dec.get("result") if isinstance(dec, dict) else None
            if result and isinstance(result, dict):
                return True, result
            return False, "no result"
        except Exception as e:
            return False, str(e)


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

    # Init Data
    cprint(f"  {C.SUCCESS}[1]{C.RESET} {C.BOLD}Init Data (Telegram WebApp){C.RESET}")
    cprint(f"     {C.DIM}Cara ambil: Buka https://pepeminertap.lovable.app/app via Telegram Desktop{C.RESET}")
    cprint(f"     {C.DIM}Cek URL hash: #tgWebAppData=query_id%3D...{C.RESET}")
    cprint(f"     {C.DIM}Copy nilai setelah 'tgWebAppData=' (url-decoded){C.RESET}")
    print()
    cprint(f"     {C.DIM}Atau copy dari request POST body:{C.RESET}")
    cprint(f"     {C.DIM}'initData': 'query_id=AAGuk-oa...' (sampai sebelum '&hash' TAPI sertakan hash){C.RESET}")
    print()
    current = cfg.get("init_data", "")
    if current:
        cprint(f"     {C.LAVENDER}Current: {current[:60]}...{C.RESET}")
    new = input(f"  {C.GREEN_M}▸ Paste init data (kosong untuk skip): {C.RESET}").strip()
    if new:
        if "query_id=" not in new:
            cprint(f"  {C.ERROR}[!] Harus mengandung 'query_id='.{C.RESET}")
        else:
            # Strip prefix kalau ada
            if "tma " in new.lower():
                new = new.split("tma ", 1)[1]
            cfg["init_data"] = new
            cprint(f"  {C.SUCCESS}✓ Init data disimpan ({len(new)} chars){C.RESET}")

    print()
    line_dash()
    print()

    # Refill Endpoint (opsional)
    cprint(f"  {C.SUCCESS}[2]{C.RESET} {C.BOLD}Refill Endpoint (opsional){C.RESET}")
    cprint(f"     {C.DIM}Server function hash untuk refill energy.{C.RESET}")
    cprint(f"     {C.DIM}Cek di network tab saat klik 'Refill Energy'.{C.RESET}")
    print()
    current = cfg.get("refill_endpoint", "")
    if current:
        cprint(f"     {C.LAVENDER}Current: {current[:40]}...{C.RESET}")
    new = input(f"  {C.GREEN_M}▸ Refill hash (kosong untuk skip): {C.RESET}").strip()
    if new:
        cfg["refill_endpoint"] = new
        cprint(f"  {C.SUCCESS}✓ Refill endpoint disimpan{C.RESET}")

    print()
    line_dash()
    print()

    # Task Endpoint (opsional)
    cprint(f"  {C.SUCCESS}[3]{C.RESET} {C.BOLD}Task Claim Endpoint (opsional){C.RESET}")
    cprint(f"     {C.DIM}Server function hash untuk claim task.{C.RESET}")
    print()
    current = cfg.get("task_endpoint", "")
    if current:
        cprint(f"     {C.LAVENDER}Current: {current[:40]}...{C.RESET}")
    new = input(f"  {C.GREEN_M}▸ Task hash (kosong untuk skip): {C.RESET}").strip()
    if new:
        cfg["task_endpoint"] = new
        cprint(f"  {C.SUCCESS}✓ Task endpoint disimpan{C.RESET}")

    save_config(cfg)
    print()
    cprint(f"  {C.SUCCESS}✓ Config saved to {CONFIG_FILE}{C.RESET}")
    input(f"\n  {C.GREEN_M}Tekan ENTER untuk kembali...{C.RESET}")


def main():
    os.system("cls" if os.name == "nt" else "clear")
    print_logo()

    cfg = load_config()

    while True:
        print()
        line_eq()
        cprint(f"  🎮 {C.BOLD}{C.GREEN_M}MAIN MENU{C.RESET}", C.GREEN_M)
        line_eq()
        cprint(f"  {C.SUCCESS}[1]{C.RESET} 🚀  Auto Farm (Tap + Boost + Refill)")
        cprint(f"  {C.SUCCESS}[2]{C.RESET} 📊  Check State / Status")
        cprint(f"  {C.SUCCESS}[3]{C.RESET} ⚡  Activate Turbo Boost")
        cprint(f"  {C.SUCCESS}[4]{C.RESET} 🔋  Refill Energy")
        cprint(f"  {C.SUCCESS}[5]{C.RESET} ⚙️   Setup Config")
        cprint(f"  {C.ERROR}[0]{C.RESET} ❌  Exit")
        line_eq()
        print()

        # Show current config status
        init_ok = "✓" if cfg.get("init_data") else "✗"
        refill_ok = "✓" if cfg.get("refill_endpoint") else "○"
        cprint(f"  {C.DIM}Status: init={init_ok} refill={refill_ok}{C.RESET}")
        print()

        choice = input(f"  {C.GREEN_M}▸ Pilih: {C.RESET}").strip()

        if choice == "0":
            cprint(f"\n  {C.GREEN_M}👋 Bye!{C.RESET}")
            sys.exit(0)

        elif choice == "1":
            if not cfg.get("init_data"):
                cprint(f"\n  {C.ERROR}✗ Init data belum di-set! Pilih [5]{C.RESET}")
                input("  Tekan ENTER...")
                continue
            bot = PepeTapBot(
                init_data=cfg["init_data"],
                refill_endpoint=cfg.get("refill_endpoint", ""),
                task_endpoint=cfg.get("task_endpoint", ""),
            )
            try:
                bot.auto_farm(tap_batch=20, max_energy_refill=5)
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
            bot = PepeTapBot(cfg["init_data"])
            loading_bar("Fetching state", 1.0)
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
            bot = PepeTapBot(cfg["init_data"])
            loading_bar("Activating turbo", 1.0)
            ok, data = bot.activate_boost("turbo")
            if ok:
                cprint(f"  {C.SUCCESS}✓ Turbo boost activated!{C.RESET}")
                cprint(f"  {C.LAVENDER}  Energy   : {data.get('energy')}{C.RESET}")
                cprint(f"  {C.LAVENDER}  Until    : {data.get('boostUntil')}{C.RESET}")
                cprint(f"  {C.LAVENDER}  Multi    : x{data.get('boostMultiplier')}{C.RESET}")
            else:
                cprint(f"  {C.ERROR}✗ Gagal: {data}{C.RESET}")
            input("\n  Tekan ENTER...")

        elif choice == "4":
            if not cfg.get("refill_endpoint"):
                cprint(f"\n  {C.ERROR}✗ Refill endpoint belum di-set! Pilih [5]{C.RESET}")
                input("  Tekan ENTER...")
                continue
            bot = PepeTapBot(cfg["init_data"], refill_endpoint=cfg["refill_endpoint"])
            loading_bar("Refilling energy", 1.0)
            ok, data = bot.refill_energy()
            if ok:
                cprint(f"  {C.SUCCESS}✓ Energy refilled!{C.RESET}")
                cprint(f"  {C.LAVENDER}  Energy: {data.get('energy')}{C.RESET}")
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
        main()
    except KeyboardInterrupt:
        print()
        cprint(f"\n  {C.WARN}👋 Keluar.{C.RESET}")
        sys.exit(0)
