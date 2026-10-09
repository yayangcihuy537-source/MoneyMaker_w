#!/usr/bin/env python3
"""
CryptoCrops Auto Farm
Plant + Harvest + Faucet + Claim Mission
Solver: Altcha (LOCAL PBKDF2 PoW) — no external API needed
Prioritas tanam: base_points tertinggi
Auto-pause tiap 5 jam run selama 30 menit + summary
"""

import json
import os
import sys
import time
import uuid
import base64
import hashlib
import random
import threading
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install dulu: pip install requests")
    sys.exit(1)

# ==================== PATH ====================
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "cconfig.json"

DEFAULT_CONFIG = {
    "cookie": "",
    "loop_delay": 5,
    "human_delay_min": 60,
    "human_delay_max": 120,
    "enable_harvest": True,
    "enable_plant": True,
    "enable_faucet": True,
    "enable_mission": True,
}

# === AUTO-PAUSE CONFIG ===
RUN_HOURS_BEFORE_PAUSE = 5      # jam jalan sebelum pause
PAUSE_MINUTES          = 30     # menit pause

# ==================== GLOBAL STATS ====================
STATS = {
    "started_at": time.time(),
    "cycles": 0,
    "harvested": 0,
    "planted": 0,
    "faucet_claims": 0,
    "faucet_coins": 0,
    "mission_claims": 0,
    "mission_xp": 0,
    "checkpoint_ok": 0,
    "errors": 0,
    "solver_success": 0,
    "solver_failed": 0,
    "pause_count": 0,
}

# ==================== COLORS / UI ====================
class C:
    R = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    CYAN = "\033[96m"
    MAGENTA = "\033[95m"
    BLUE = "\033[94m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
_spin_idx = 0
_spin_lock = threading.Lock()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


def now_str():
    return datetime.now().strftime("%H:%M:%S")


def fmt_duration(seconds):
    """Format detik jadi HH:MM:SS."""
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def banner():
    clear()
    art = f"""
{C.GREEN}{C.BOLD}
   ██████╗██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗  ██████╗██████╗  ██████╗ ██████╗ ███████╗
  ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗██╔════╝██╔══██╗██╔═══██╗██╔══██╗██╔════╝
  ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║██║     ██████╔╝██║   ██║██████╔╝███████╗
  ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║██║     ██╔══██╗██║   ██║██╔═══╝ ╚════██║
  ╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝╚██████╗██║  ██║╚██████╔╝██║     ███████║
   ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝  ╚═════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚══════╝
{C.R}
{C.CYAN}        Auto Farm · Faucet · Mission  |  Sort by Base Points  |  Altcha Local{C.R}
{C.MAGENTA}                              By MoneyMaker_w{C.R}
{C.CYAN}                 Telegram Group: https://t.me/+RInZ35ML2GhjM2I1{C.R}
{C.GRAY}────────────────────────────────────────────────────────────────────────────────{C.R}
"""
    print(art)


def log(msg, level="info"):
    icons = {
        "info": f"{C.CYAN}ℹ{C.R}",
        "ok": f"{C.GREEN}✔{C.R}",
        "warn": f"{C.YELLOW}⚠{C.R}",
        "err": f"{C.RED}✖{C.R}",
        "farm": f"{C.GREEN}🌱{C.R}",
        "coin": f"{C.YELLOW}🪙{C.R}",
        "mission": f"{C.MAGENTA}🎯{C.R}",
        "captcha": f"{C.BLUE}🔐{C.R}",
        "wait": f"{C.GRAY}⏳{C.R}",
        "pause": f"{C.MAGENTA}⏸{C.R}",
    }
    icon = icons.get(level, icons["info"])
    print(f"{C.GRAY}[{now_str()}]{C.R} {icon}  {msg}")


def section(title):
    print(f"\n{C.BOLD}{C.GREEN}▸ {title}{C.R}")
    print(f"{C.GRAY}{'─' * 48}{C.R}")


def spinner_line(text):
    global _spin_idx
    with _spin_lock:
        frame = SPINNER[_spin_idx % len(SPINNER)]
        _spin_idx += 1
    sys.stdout.write(f"\r{C.CYAN}{frame}{C.R}  {text}   ")
    sys.stdout.flush()


def clear_spinner():
    sys.stdout.write("\r" + " " * 90 + "\r")
    sys.stdout.flush()


def human_delay(min_s, max_s, label="human delay"):
    """Delay random biar keliatan human-like."""
    try:
        min_s = float(min_s); max_s = float(max_s)
    except (TypeError, ValueError):
        return
    if max_s <= 0 or max_s < min_s:
        return
    d = random.uniform(min_s, max_s)
    log(f"{label}: {int(d)}s", "wait")
    end = time.time() + d
    while time.time() < end:
        left = int(end - time.time())
        spinner_line(f"{label} — {left}s left (Ctrl+C stop)")
        time.sleep(0.5)
    clear_spinner()


def solver_human_delay(label="solver pause"):
    """Delay random pendek di dalam solver (biar ga instan / suspicious)."""
    d = random.uniform(0.8, 2.8)
    log(f"{label}: {d:.1f}s", "wait")
    time.sleep(d)


# ==================== CONFIG ====================
def ensure_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        changed = False
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
                changed = True
        if "waryono_apikey" in cfg:
            cfg.pop("waryono_apikey", None)
            changed = True
        if changed:
            save_config(cfg)
        return cfg

    banner()
    section("Setup Config Pertama Kali")
    print(f"{C.YELLOW}File cconfig.json belum ada. Isi data di bawah:{C.R}\n")

    cookie = input(f"  {C.CYAN}Cookie browser{C.R}    : ").strip()
    delay = input(f"  {C.CYAN}Loop delay detik{C.R}  (enter=5): ").strip()

    cfg = dict(DEFAULT_CONFIG)
    cfg["cookie"] = cookie
    if delay.isdigit():
        cfg["loop_delay"] = int(delay)

    save_config(cfg)
    print(f"\n{C.GREEN}✔ cconfig.json tersimpan di {CONFIG_PATH}{C.R}\n")
    time.sleep(1.0)
    return cfg


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# ==================== ALTCHA LOCAL SOLVER ====================
def solve_altcha(params, verbose=True):
    """
    Solve altcha PBKDF2 PoW lokal.
    Ada random human delay sebelum & sesudah solve.
    """
    algorithm = params["algorithm"]
    cost = int(params["cost"])
    key_length = int(params.get("keyLength", 32))
    key_prefix = params["keyPrefix"].lower()
    nonce = bytes.fromhex(params["nonce"])
    salt = bytes.fromhex(params["salt"])

    algo_map = {
        "PBKDF2/SHA-256": "sha256",
        "PBKDF2/SHA-384": "sha384",
        "PBKDF2/SHA-512": "sha512",
    }
    if algorithm not in algo_map:
        raise Exception(f"Algo altcha unsupported: {algorithm}")
    py_algo = algo_map[algorithm]

    if verbose:
        log(f"Altcha {algorithm} cost={cost} prefix={key_prefix[:16]}...", "captcha")

    # Random delay SEBELUM mulai hitung (mimic human pikir)
    solver_human_delay("pre-solve delay")

    counter = 0
    start = time.time()
    max_iter = 500000

    while counter < max_iter:
        password = nonce + counter.to_bytes(4, byteorder="big")
        derived = hashlib.pbkdf2_hmac(py_algo, password, salt, cost, dklen=key_length)
        hex_str = derived.hex()

        if hex_str.startswith(key_prefix):
            elapsed_ms = round((time.time() - start) * 1000, 1)
            if verbose:
                clear_spinner()
                log(f"Altcha solved: counter={counter} ({elapsed_ms}ms)", "ok")
            STATS["solver_success"] += 1

            # Random delay SETELAH solve (mimic human submit form)
            solver_human_delay("post-solve delay")

            return {"counter": counter, "derivedKey": hex_str, "time": elapsed_ms}

        counter += 1
        if verbose and counter % 200 == 0:
            elapsed = round((time.time() - start) * 1000, 0)
            spinner_line(f"Altcha searching counter={counter} ({elapsed}ms)")

    clear_spinner()
    STATS["solver_failed"] += 1
    return None


def build_altcha_token(altcha_block, solution):
    payload = {
        "challenge": {
            "parameters": altcha_block["parameters"],
            "signature": altcha_block["signature"],
        },
        "solution": {
            "counter": solution["counter"],
            "derivedKey": solution["derivedKey"],
            "time": solution["time"],
        },
    }
    raw = json.dumps(payload, separators=(",", ":"))
    return base64.b64encode(raw.encode()).decode()


# ==================== API ====================
BASE = "https://cryptocrops.net"


class FarmClient:
    RARITY_RANK = {
        "mythical": 6, "legendary": 5, "epic": 4,
        "rare": 3, "uncommon": 2, "common": 1,
    }

    def __init__(self, cfg):
        self.cfg = cfg
        self._catalog = {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Linux; Android 10; K) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/127.0.0.0 Mobile Safari/537.36"
            ),
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": BASE,
            "Referer": f"{BASE}/faucet/",
            "Cookie": cfg["cookie"],
        })

    def api(self, method, path, json_data=None, referer=None):
        headers = {}
        if referer:
            headers["Referer"] = referer
        r = self.session.request(
            method, BASE + path, json=json_data, headers=headers or None, timeout=45
        )
        try:
            data = r.json()
        except Exception:
            raise Exception(f"HTTP {r.status_code} | {r.text[:300]}")
        if r.status_code >= 400:
            err = data.get("error") or data.get("message") or str(data)
            raise Exception(err)
        return data

    def bootstrap(self):
        return self.api("GET", "/api/bootstrap")

    def load_catalog(self):
        if self._catalog:
            return self._catalog
        data = self.api("GET", "/api/catalog?version=3")
        seeds = data.get("seeds") or []
        self._catalog = {s["seed_id"]: s for s in seeds}
        return self._catalog

    def seed_priority(self, seed_id):
        cat = self.load_catalog()
        info = cat.get(seed_id) or {}
        points = int(info.get("base_points") or 0)
        rarity = str(info.get("rarity", "")).lower()
        rank = info.get("rarity_rank")
        if rank is None:
            rank = self.RARITY_RANK.get(rarity, 0)
        grow = int(info.get("grow_seconds") or 0)
        return (points, int(rank), grow)

    # ---------- CHECKPOINT ----------
    def handle_checkpoint(self, bootstrap):
        security = bootstrap.get("security") or {}
        farm = bootstrap.get("farm") or {}
        checkpoint = farm.get("farm_checkpoint") or {}

        if not security.get("farm_checkpoint_enabled"):
            return False
        if not checkpoint.get("required"):
            return False

        provider = security.get("farm_checkpoint_provider", "altcha")
        log(f"Farm checkpoint required (provider={provider})", "warn")

        if provider != "altcha":
            log(f"Provider bukan altcha ({provider}), skip", "warn")
            return False

        for endpoint in ("/api/farm-checkpoint/challenge", "/api/checkpoint/challenge"):
            try:
                chal = self.api("POST", endpoint, {}, referer=f"{BASE}/farm/")
            except Exception:
                continue

            altcha_block = chal.get("altcha") or {}
            if not altcha_block.get("parameters"):
                continue

            solution = solve_altcha(altcha_block["parameters"])
            if not solution:
                log("Altcha solve failed (skip checkpoint)", "err")
                return False

            token = build_altcha_token(altcha_block, solution)
            try:
                result = self.api(
                    "POST",
                    "/api/farm-checkpoint/verify",
                    {"captcha_token": token},
                    referer=f"{BASE}/farm/",
                )
                if result.get("verified"):
                    log("Checkpoint OK", "ok")
                    STATS["checkpoint_ok"] += 1
                    return True
                log(f"Verify checkpoint gagal: {result}", "warn")
                return False
            except Exception as e:
                log(f"Verify checkpoint error: {e}", "warn")
                return False

        log("Endpoint checkpoint challenge tidak ditemukan, skip", "warn")
        return False

    # ---------- HARVEST ----------
    def harvest(self, farm):
        now = int(time.time() * 1000)
        ready = []
        for crop in farm.get("crops", []):
            ready_at = crop.get("ready_at") or crop.get("harvest_ready_at") or 0
            if now >= ready_at or crop.get("status") == "ready":
                ready.append(crop)

        if not ready:
            log("Tidak ada crop ready", "wait")
            return 0

        count = 0
        for crop in ready:
            crop_id = crop.get("crop_id")
            try:
                res = self.api("POST", "/api/farm/harvest", {
                    "idempotency_key": str(uuid.uuid4()),
                    "crop_id": crop_id,
                })
                h = res.get("harvested", {})
                pts = h.get("point_value", "?")
                perfect = " (Perfect)" if h.get("perfect_harvest") else ""
                log(f"Harvest {crop.get('seed_id')} → {pts} pts{perfect}", "farm")
                count += 1
                STATS["harvested"] += 1
                time.sleep(random.uniform(0.8, 2.0))
            except Exception as e:
                if "FARM_CHECKPOINT_REQUIRED" in str(e):
                    raise
                log(f"Gagal harvest {crop_id}: {e} (skip)", "warn")
        return count

    # ---------- PLANT ----------
    def plant(self, farm):
        profile = farm.get("profile") or {}
        capacity = (
            profile.get("total_capacity")
            or profile.get("base_capacity")
            or 4
        )
        try:
            capacity = int(capacity)
        except (TypeError, ValueError):
            capacity = 4
        capacity = max(1, min(capacity, 24))

        used = {
            c.get("plot_index")
            for c in farm.get("crops", [])
            if c.get("plot_index") is not None
        }
        empty = [i for i in range(1, capacity + 1) if i not in used]

        planted_map = {}
        for c in farm.get("crops", []):
            sid = c.get("seed_id")
            planted_map[sid] = planted_map.get(sid, 0) + 1

        available = []
        for s in farm.get("seeds", []):
            sid = s["seed_id"]
            free = s.get("quantity", 0) - planted_map.get(sid, 0)
            if free > 0:
                available.append({"seed_id": sid, "free": free})

        log(f"Plot: {len(empty)} kosong / {capacity} total", "info")

        if not empty:
            log("Tidak ada plot kosong", "wait")
            return 0
        if not available:
            log("Tidak ada seed free", "wait")
            return 0

        available.sort(key=lambda x: self.seed_priority(x["seed_id"]), reverse=True)

        top = available[0]
        info = self.load_catalog().get(top["seed_id"], {})
        log(
            f"Prioritas tanam: {info.get('name', top['seed_id'])} "
            f"[{info.get('rarity', '?')}] "
            f"{int(info.get('base_points', 0))} pts · "
            f"grow {int(info.get('grow_seconds', 0)) // 3600}h",
            "farm",
        )

        count = 0
        for plot in empty:
            chosen = None
            for item in available:
                if item["free"] > 0:
                    chosen = item
                    break
            if not chosen:
                break

            seed_id = chosen["seed_id"]
            try:
                self.api("POST", "/api/farm/plant", {
                    "idempotency_key": str(uuid.uuid4()),
                    "seed_id": seed_id,
                    "plot_index": plot,
                })
                info = self.load_catalog().get(seed_id, {})
                name = info.get("name", seed_id)
                rarity = info.get("rarity", "?")
                pts = int(info.get("base_points", 0))
                log(f"Plant {name} [{rarity}] {pts} pts → plot {plot}", "farm")
                chosen["free"] -= 1
                count += 1
                STATS["planted"] += 1
                time.sleep(random.uniform(0.8, 2.0))
            except Exception as e:
                if "FARM_CHECKPOINT_REQUIRED" in str(e):
                    raise
                log(f"Gagal plant plot {plot}: {e} (skip)", "warn")
                break
        return count

    # ---------- FAUCET ----------
    def faucet(self, bootstrap):
        farm = bootstrap.get("farm") or {}
        faucet = farm.get("faucet") or {}

        if not faucet.get("available"):
            next_at = faucet.get("next_claim_at") or 0
            now = int(time.time() * 1000)
            if next_at > now:
                sisa = max(0, (next_at - now) // 1000)
                m, s = divmod(sisa, 60)
                log(f"Faucet cooldown {m:02d}:{s:02d}", "wait")
            else:
                log("Faucet tidak available", "wait")
            return False

        log("Ambil faucet challenge...", "coin")
        try:
            challenge_payload = self.api(
                "POST",
                "/api/earn/faucet-challenge",
                {},
                referer=f"{BASE}/faucet/",
            )
        except Exception as e:
            log(f"Faucet challenge error: {e} (skip)", "warn")
            return False

        challenge = challenge_payload.get("challenge") or {}
        challenge_id = str(challenge.get("challenge_id") or "")
        expires_at = int(challenge.get("expires_at") or 0)
        now_ms = int(time.time() * 1000)

        if not challenge_id or (expires_at and expires_at <= now_ms):
            log("Challenge kosong / expired (skip)", "warn")
            return False

        log(f"Challenge: {challenge_id[:18]}...", "coin")

        altcha_block = challenge_payload.get("altcha") or {}
        captcha_info = challenge_payload.get("captcha") or {}
        provider = captcha_info.get("provider", "altcha")

        if provider != "altcha":
            log(f"Provider bukan altcha ({provider}), skip", "warn")
            return False

        if not altcha_block.get("parameters"):
            log("Tidak ada altcha params, skip", "warn")
            return False

        try:
            solution = solve_altcha(altcha_block["parameters"])
        except Exception as e:
            log(f"Altcha solve error: {e} (skip)", "err")
            return False

        if not solution:
            log("Altcha solve failed (skip)", "err")
            return False

        token = build_altcha_token(altcha_block, solution)

        try:
            result = self.api(
                "POST",
                "/api/earn/faucet",
                {
                    "idempotency_key": str(uuid.uuid4()),
                    "faucet_challenge": challenge_id,
                    "captcha_token": token,
                },
                referer=f"{BASE}/faucet/",
            )
        except Exception as e:
            log(f"Faucet claim error: {e} (skip)", "warn")
            return False

        claimed = result.get("claimed") or result
        coins = claimed.get("total_coins") or claimed.get("coins") or 0
        log(f"Faucet claimed! +{coins} Farm Coins", "coin")
        STATS["faucet_claims"] += 1
        try:
            STATS["faucet_coins"] += int(coins)
        except (TypeError, ValueError):
            pass
        return True

    # ---------- MISSION ----------
    def claim_missions(self, farm):
        missions = farm.get("missions") or []
        ready = [m for m in missions if m.get("complete") and not m.get("claimed")]
        if not ready:
            log("Tidak ada mission siap claim", "wait")
            return 0

        count = 0
        for m in ready:
            mid = m.get("mission_id")
            title = m.get("title", mid)
            try:
                res = self.api(
                    "POST",
                    "/api/missions/claim",
                    {
                        "idempotency_key": str(uuid.uuid4()),
                        "mission_id": mid,
                    },
                    referer=f"{BASE}/missions/",
                )
                claimed = res.get("claimed") or {}
                xp = claimed.get("pass_xp_earned", m.get("pass_xp", "?"))
                fert = claimed.get("fertilizer_rarity")
                extra = f" + {fert} fertilizer" if fert else ""
                log(f"Mission: {title} → +{xp} Pass XP{extra}", "mission")
                count += 1
                STATS["mission_claims"] += 1
                try:
                    STATS["mission_xp"] += int(xp)
                except (TypeError, ValueError):
                    pass
                time.sleep(random.uniform(0.8, 2.0))
            except Exception as e:
                log(f"Gagal claim {title}: {e} (skip)", "warn")
        return count


# ==================== SUMMARY / PAUSE ====================
def show_summary(reason="AUTO-PAUSE"):
    """Tampilkan ringkasan aktivitas bot."""
    runtime = time.time() - STATS["started_at"]
    print()
    print(f"{C.MAGENTA}{C.BOLD}════════════════════════════════════════════════════════{C.R}")
    print(f"{C.MAGENTA}{C.BOLD}  📊  RINGKASAN AKTIVITAS BOT — {reason}{C.R}")
    print(f"{C.MAGENTA}{C.BOLD}════════════════════════════════════════════════════════{C.R}")
    print(f"  {C.WHITE}Runtime         :{C.R} {C.CYAN}{fmt_duration(runtime)}{C.R}")
    print(f"  {C.WHITE}Cycles          :{C.R} {C.CYAN}{STATS['cycles']}{C.R}")
    print(f"  {C.GREEN}🌱 Harvested    :{C.R} {C.CYAN}{STATS['harvested']}{C.R}")
    print(f"  {C.GREEN}🌱 Planted      :{C.R} {C.CYAN}{STATS['planted']}{C.R}")
    print(f"  {C.YELLOW}🪙 Faucet claims :{C.R} {C.CYAN}{STATS['faucet_claims']}{C.R}")
    print(f"  {C.YELLOW}🪙 Faucet coins  :{C.R} {C.CYAN}{STATS['faucet_coins']}{C.R}")
    print(f"  {C.MAGENTA}🎯 Mission claims:{C.R} {C.CYAN}{STATS['mission_claims']}{C.R}")
    print(f"  {C.MAGENTA}🎯 Mission XP    :{C.R} {C.CYAN}{STATS['mission_xp']}{C.R}")
    print(f"  {C.BLUE}🔐 Checkpoint OK :{C.R} {C.CYAN}{STATS['checkpoint_ok']}{C.R}")
    print(f"  {C.BLUE}🔐 Solver OK     :{C.R} {C.GREEN}{STATS['solver_success']}{C.R}  "
          f"{C.RED}Fail: {STATS['solver_failed']}{C.R}")
    print(f"  {C.RED}✖ Errors         :{C.R} {C.CYAN}{STATS['errors']}{C.R}")
    print(f"  {C.WHITE}Pause count     :{C.R} {C.CYAN}{STATS['pause_count']}{C.R}")
    print(f"{C.MAGENTA}{C.BOLD}════════════════════════════════════════════════════════{C.R}")
    print()


def auto_pause_countdown(minutes):
    """Pause selama X menit + countdown display."""
    total = int(minutes * 60)
    log(f"Auto-pause selama {minutes} menit (runtime limit tercapai)", "pause")
    end = time.time() + total
    while True:
        left = int(end - time.time())
        if left <= 0:
            break
        spinner_line(f"⏸ PAUSED — resume dalam {fmt_duration(left)} (Ctrl+C stop)")
        time.sleep(1)
    clear_spinner()
    log("Resume bot!", "ok")


def check_auto_pause():
    """
    Cek apakah sudah waktunya pause.
    Return True kalau baru selesai pause (biar stats direset optional).
    """
    runtime = time.time() - STATS["started_at"]
    if runtime >= RUN_HOURS_BEFORE_PAUSE * 3600:
        show_summary("AUTO-PAUSE")
        auto_pause_countdown(PAUSE_MINUTES)
        # Reset timer mulai dari sekarang
        STATS["started_at"] = time.time()
        STATS["pause_count"] += 1
        return True
    return False


# ==================== MAIN ====================
def status_bar(farm):
    profile = farm.get("profile") or {}
    coins = profile.get("farm_coins", 0)
    level = profile.get("farm_level", 1)
    crops = len(farm.get("crops") or [])
    cap = profile.get("total_capacity", 4)
    faucet = farm.get("faucet") or {}
    avail = "READY" if faucet.get("available") else "CD"
    runtime = fmt_duration(time.time() - STATS["started_at"])
    print(
        f"{C.GRAY}│{C.R} 🪙 {C.YELLOW}{coins}{C.R}  "
        f"⭐ Lv{level}  "
        f"🌱 {crops}/{cap}  "
        f"🚰 {C.GREEN if avail == 'READY' else C.GRAY}{avail}{C.R}  "
        f"⏱ {C.CYAN}{runtime}{C.R}"
    )


def main():
    cfg = ensure_config()

    if not cfg.get("cookie"):
        banner()
        log("cookie masih kosong di cconfig.json", "err")
        log(f"Edit file: {CONFIG_PATH}", "info")
        return

    banner()
    client = FarmClient(cfg)
    delay = int(cfg.get("loop_delay", 5))
    hd_min = float(cfg.get("human_delay_min", 60))
    hd_max = float(cfg.get("human_delay_max", 120))

    # Reset stats saat mulai (biar segar tiap launch)
    STATS["started_at"] = time.time()

    try:
        client.load_catalog()
        log(f"Catalog loaded: {len(client._catalog)} seeds", "ok")
    except Exception as e:
        log(f"Gagal load catalog: {e}", "warn")

    log("Bot started (Altcha local solver)", "ok")
    log(f"Human delay: {int(hd_min)}-{int(hd_max)}s per cycle", "info")
    log(f"Auto-pause: tiap {RUN_HOURS_BEFORE_PAUSE} jam → pause {PAUSE_MINUTES} menit", "info")
    log(f"Config: {CONFIG_PATH}", "info")
    print()

    cycle = 0
    while True:
        cycle += 1
        STATS["cycles"] = cycle
        try:
            section(f"Cycle #{cycle}")
            bootstrap = client.bootstrap()
            farm = bootstrap.get("farm") or {}
            status_bar(farm)

            # Checkpoint
            try:
                client.handle_checkpoint(bootstrap)
            except Exception as e:
                log(f"Checkpoint: {e} (skip)", "warn")
                STATS["errors"] += 1

            harvested = planted = claimed_m = 0

            # Harvest
            if cfg.get("enable_harvest", True):
                try:
                    harvested = client.harvest(farm)
                except Exception as e:
                    log(f"Harvest error: {e} (skip)", "warn")
                    STATS["errors"] += 1

            if harvested:
                try:
                    bootstrap = client.bootstrap()
                    farm = bootstrap.get("farm") or {}
                except Exception as e:
                    log(f"Refresh error: {e} (skip)", "warn")
                    STATS["errors"] += 1

            # Plant
            if cfg.get("enable_plant", True):
                try:
                    planted = client.plant(farm)
                except Exception as e:
                    log(f"Plant error: {e} (skip)", "warn")
                    STATS["errors"] += 1

            # Faucet
            if cfg.get("enable_faucet", True):
                try:
                    bootstrap = client.bootstrap()
                    client.faucet(bootstrap)
                except Exception as e:
                    log(f"Faucet error: {e} (skip)", "err")
                    STATS["errors"] += 1

            # Mission
            if cfg.get("enable_mission", True):
                try:
                    bootstrap = client.bootstrap()
                    claimed_m = client.claim_missions(bootstrap.get("farm") or {})
                except Exception as e:
                    log(f"Mission error: {e} (skip)", "warn")
                    STATS["errors"] += 1

            print()
            log(
                f"Selesai → harvest:{harvested}  plant:{planted}  mission:{claimed_m}",
                "ok",
            )

            # Cek auto-pause (setiap cycle)
            check_auto_pause()

            # Human delay antar cycle
            human_delay(hd_min, hd_max, "cycle human delay")

            if delay > 0:
                for left in range(delay, 0, -1):
                    spinner_line(f"Next cycle dalam {left}s (Ctrl+C stop)")
                    time.sleep(1)
                clear_spinner()
            print()

        except KeyboardInterrupt:
            print()
            log("Dihentikan user. Bye!", "warn")
            show_summary("MANUAL STOP")
            break
        except Exception as e:
            log(f"Loop error: {e} (skip, retry 15s)", "err")
            STATS["errors"] += 1
            time.sleep(15)


if __name__ == "__main__":
    main()
