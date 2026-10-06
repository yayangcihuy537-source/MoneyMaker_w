#!/usr/bin/env python3
"""
CryptoCrops Auto Farm
Plant + Harvest + Faucet + Claim Mission
Solver: Waryono Turnstile
Prioritas tanam: base_points tertinggi
"""


import json
import os
import sys
import time
import uuid
import threading
from datetime import datetime
from pathlib import Path

try:
    import requests
except ImportError:
    print("Install dulu: pip install requests ansicon")
    sys.exit(1)

# ==================== PATH ====================
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "cconfig.json"

DEFAULT_CONFIG = {
    "waryono_apikey": "",
    "cookie": "",
    "loop_delay": 30,
    "enable_harvest": True,
    "enable_plant": True,
    "enable_faucet": True,
    "enable_mission": True,
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
{C.CYAN}         Auto Plant · Harvest · Faucet · Mission  |  Sort by Base Points  |  Waryono{C.R}
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
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()


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
        if changed:
            save_config(cfg)
        return cfg

    banner()
    section("Setup Config Pertama Kali")
    print(f"{C.YELLOW}File config.json belum ada. Isi data di bawah:{C.R}\n")

    apikey = input(f"  {C.CYAN}Waryono API Key{C.R}  : ").strip()
    cookie = input(f"  {C.CYAN}Cookie browser{C.R}    : ").strip()
    delay = input(f"  {C.CYAN}Loop delay detik{C.R}  (enter=30): ").strip()

    cfg = dict(DEFAULT_CONFIG)
    cfg["waryono_apikey"] = apikey
    cfg["cookie"] = cookie
    if delay.isdigit():
        cfg["loop_delay"] = int(delay)

    save_config(cfg)
    print(f"\n{C.GREEN}✔ config.json tersimpan di {CONFIG_PATH}{C.R}\n")
    time.sleep(1.0)
    return cfg


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


# ==================== API ====================
BASE = "https://cryptocrops.net"


class FarmClient:
    RARITY_RANK = {
        "mythical": 6,
        "legendary": 5,
        "epic": 4,
        "rare": 3,
        "uncommon": 2,
        "common": 1,
    }

    def __init__(self, cfg):
        self.cfg = cfg
        self._catalog = {}
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Origin": BASE,
            "Referer": f"{BASE}/farm/",
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
        """
        Prioritas tanam (tinggi = ditanam duluan):
        1. base_points tertinggi
        2. rarity tertinggi
        3. grow_seconds terlama
        """
        cat = self.load_catalog()
        info = cat.get(seed_id) or {}
        points = int(info.get("base_points") or 0)
        rarity = str(info.get("rarity", "")).lower()
        rank = info.get("rarity_rank")
        if rank is None:
            rank = self.RARITY_RANK.get(rarity, 0)
        grow = int(info.get("grow_seconds") or 0)
        return (points, int(rank), grow)

    def solve_turnstile(self, sitekey, action, cdata=None):
        log(f"Solve Turnstile [{action}]", "captcha")
        payload = {
            "apikey": self.cfg["waryono_apikey"],
            "methods": "turnstile",
            "sitekey": sitekey,
            "domain": "https://cryptocrops.net",
            "action": action,
            "json": 1,
        }
        if cdata:
            payload["cdata"] = cdata

        r = requests.post("https://api.waryono.my.id/in.php", json=payload, timeout=60)
        res = r.json()
        if res.get("status") != 1:
            raise Exception(f"Waryono submit gagal: {res}")

        task_id = res["request"]
        log(f"Task ID: {task_id}", "captcha")

        for i in range(50):
            spinner_line(f"Menunggu captcha... ({i * 3}s)")
            time.sleep(3)
            check = requests.get(
                f"https://api.waryono.my.id/res.php"
                f"?apikey={self.cfg['waryono_apikey']}&id={task_id}&action=get&json=1",
                timeout=30,
            ).json()
            if check.get("status") == 1:
                clear_spinner()
                log("Captcha solved!", "ok")
                return check["request"]
            req = str(check.get("request", ""))
            if req not in ("CAPCHA_NOT_READY", "CAPTCHA_NOT_READY"):
                clear_spinner()
                raise Exception(f"Waryono error: {check}")
        clear_spinner()
        raise Exception("Timeout captcha")

    def handle_checkpoint(self, bootstrap):
        security = bootstrap.get("security") or {}
        farm = bootstrap.get("farm") or {}
        checkpoint = farm.get("farm_checkpoint") or {}

        if not security.get("farm_checkpoint_enabled"):
            return False
        if not checkpoint.get("required"):
            return False

        sitekey = security.get("turnstile_site_key")
        if not sitekey:
            raise Exception("Tidak ada turnstile_site_key")

        log("Farm Checkpoint required", "warn")
        token = self.solve_turnstile(sitekey, "farm_checkpoint")
        result = self.api("POST", "/api/farm-checkpoint/verify", {"turnstile_token": token})
        if result.get("verified"):
            log("Checkpoint OK", "ok")
            return True
        raise Exception(f"Verify checkpoint gagal: {result}")

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
                time.sleep(0.7)
            except Exception as e:
                if "FARM_CHECKPOINT_REQUIRED" in str(e):
                    raise
                log(f"Gagal harvest {crop_id}: {e}", "err")
        return count

    # ---------- PLANT (base_points tertinggi dulu) ----------
    def plant(self, farm):
        capacity = farm.get("profile", {}).get("total_capacity", 4)
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

        if not empty:
            log("Tidak ada plot kosong", "wait")
            return 0
        if not available:
            log("Tidak ada seed free", "wait")
            return 0

        # sort: base_points desc → rarity desc → grow_seconds desc
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
                time.sleep(0.7)
            except Exception as e:
                if "FARM_CHECKPOINT_REQUIRED" in str(e):
                    raise
                log(f"Gagal plant plot {plot}: {e}", "err")
                break
        return count

    # ---------- FAUCET ----------
    def faucet(self, bootstrap):
        farm = bootstrap.get("farm") or {}
        faucet = farm.get("faucet") or {}
        security = bootstrap.get("security") or {}

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

        sitekey = security.get("turnstile_site_key")
        turnstile_enabled = security.get("turnstile_enabled", True)

        log("Ambil faucet challenge...", "coin")
        challenge_payload = self.api(
            "POST",
            "/api/earn/faucet-challenge",
            {},
            referer=f"{BASE}/faucet/",
        )
        challenge = challenge_payload.get("challenge") or {}
        challenge_id = str(challenge.get("challenge_id") or "")
        expires_at = int(challenge.get("expires_at") or 0)
        now_ms = int(time.time() * 1000)

        if not challenge_id or (expires_at and expires_at <= now_ms):
            raise Exception("Faucet challenge kosong / sudah expired")

        log(f"Challenge: {challenge_id[:18]}...", "coin")

        token = ""
        if turnstile_enabled:
            if not sitekey:
                raise Exception("Tidak ada turnstile_site_key")
            token = self.solve_turnstile(sitekey, "faucet_claim", cdata=challenge_id)

        result = self.api(
            "POST",
            "/api/earn/faucet",
            {
                "idempotency_key": str(uuid.uuid4()),
                "faucet_challenge": challenge_id,
                "turnstile_token": token,
            },
            referer=f"{BASE}/faucet/",
        )
        claimed = result.get("claimed") or result
        coins = claimed.get("total_coins") or claimed.get("coins") or "?"
        log(f"Faucet claimed! +{coins} Farm Coins", "coin")
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
                time.sleep(0.7)
            except Exception as e:
                log(f"Gagal claim {title}: {e}", "err")
        return count


# ==================== MAIN ====================
def status_bar(farm):
    profile = farm.get("profile") or {}
    coins = profile.get("farm_coins", 0)
    level = profile.get("farm_level", 1)
    crops = len(farm.get("crops") or [])
    cap = profile.get("total_capacity", 4)
    faucet = farm.get("faucet") or {}
    avail = "READY" if faucet.get("available") else "CD"
    print(
        f"{C.GRAY}│{C.R} 🪙 {C.YELLOW}{coins}{C.R}  "
        f"⭐ Lv{level}  "
        f"🌱 {crops}/{cap}  "
        f"🚰 {C.GREEN if avail == 'READY' else C.GRAY}{avail}{C.R}"
    )


def main():
    cfg = ensure_config()

    if not cfg.get("waryono_apikey") or not cfg.get("cookie"):
        banner()
        log("waryono_apikey / cookie masih kosong di config.json", "err")
        log(f"Edit file: {CONFIG_PATH}", "info")
        return

    banner()
    client = FarmClient(cfg)
    delay = int(cfg.get("loop_delay", 30))

    try:
        client.load_catalog()
        log(f"Catalog loaded: {len(client._catalog)} seeds", "ok")
    except Exception as e:
        log(f"Gagal load catalog: {e}", "warn")

    log("Bot started", "ok")
    log(f"Config: {CONFIG_PATH}", "info")
    print()

    cycle = 0
    while True:
        cycle += 1
        try:
            section(f"Cycle #{cycle}")
            bootstrap = client.bootstrap()
            farm = bootstrap.get("farm") or {}
            status_bar(farm)

            try:
                client.handle_checkpoint(bootstrap)
            except Exception as e:
                log(f"Checkpoint: {e}", "warn")

            harvested = planted = claimed_m = 0

            if cfg.get("enable_harvest", True):
                try:
                    harvested = client.harvest(farm)
                except Exception as e:
                    if "FARM_CHECKPOINT_REQUIRED" in str(e):
                        bootstrap = client.bootstrap()
                        client.handle_checkpoint(bootstrap)
                        harvested = client.harvest(bootstrap.get("farm") or {})
                    else:
                        log(f"Harvest error: {e}", "err")

            if harvested:
                bootstrap = client.bootstrap()
                farm = bootstrap.get("farm") or {}

            if cfg.get("enable_plant", True):
                try:
                    planted = client.plant(farm)
                except Exception as e:
                    if "FARM_CHECKPOINT_REQUIRED" in str(e):
                        bootstrap = client.bootstrap()
                        client.handle_checkpoint(bootstrap)
                        planted = client.plant(bootstrap.get("farm") or {})
                    else:
                        log(f"Plant error: {e}", "err")

            if cfg.get("enable_faucet", True):
                try:
                    bootstrap = client.bootstrap()
                    client.faucet(bootstrap)
                except Exception as e:
                    log(f"Faucet error: {e}", "err")

            if cfg.get("enable_mission", True):
                try:
                    bootstrap = client.bootstrap()
                    claimed_m = client.claim_missions(bootstrap.get("farm") or {})
                except Exception as e:
                    log(f"Mission error: {e}", "err")

            print()
            log(
                f"Selesai → harvest:{harvested}  plant:{planted}  mission:{claimed_m}",
                "ok",
            )

            for left in range(delay, 0, -1):
                spinner_line(f"Cycle berikutnya dalam {left}s  (Ctrl+C stop)")
                time.sleep(1)
            clear_spinner()
            print()

        except KeyboardInterrupt:
            print()
            log("Dihentikan user. Bye!", "warn")
            break
        except Exception as e:
            log(f"Loop error: {e}", "err")
            time.sleep(15)


if __name__ == "__main__":
    main()
