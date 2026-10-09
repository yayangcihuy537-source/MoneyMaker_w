#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GainLTC.com Auto Bot v5.1
=========================
- Config disimpan di folder yg sama dengan script
- Bypass 6 captcha types TANPA Pillow
- Menu interaktif
- Auto faucet hCaptcha via Waryono
"""

import json
import os
import sys
import time
import random
import threading
import requests
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

try:
    import requests
except ImportError:
    print("ERROR: install dulu 'requests' → pip install requests")
    sys.exit(1)

# ==================== CONSTANTS ====================
BASE_DIR    = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "gainltc_config.json"

BASE       = "https://gainltc.com"
SOLVER_IN  = "https://api.waryono.my.id/in.php"
SOLVER_RES = "https://api.waryono.my.id/res.php"

DEFAULT_CONFIG = {
    "email": "",
    "password": "",
    "waryono_apikey": "",
    "hcaptcha_sitekey": "05e4f926-1cc6-4438-8018-3a388392ea26",
    "debug_challenge": True,
}

# ==================== COLORS ====================
class C:
    R = "\033[0m"; BOLD = "\033[1m"; DIM = "\033[2m"
    GREEN = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"
    CYAN = "\033[96m"; MAGENTA = "\033[95m"; BLUE = "\033[94m"
    WHITE = "\033[97m"; GRAY = "\033[90m"

SPINNER = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
_spin_idx = 0
_spin_lock = threading.Lock()

STATE = {
    "started_at": time.time(),
    "balance": None, "total_earned": None,
    "username": None, "user_id": None,
    "total_claims": 0, "total_reward": 0,
    "next_claim_at": 0.0, "csrf_token": None,
    "logged_in": False,
}

# ==================== UTILS ====================
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def now_str():
    return datetime.now().strftime("%H:%M:%S")


def fmt_duration(seconds):
    seconds = int(max(0, seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def banner():
    clear()
    print(f"""{C.CYAN}{C.BOLD}
   ╔══════════════════════════════════════════════════════════════╗
   ║           💰  G A I N L T C . C O M  💰                      ║
   ║    AUTO LOGIN · FAUCET · 6 Captcha Types (no Pillow)         ║
   ╚══════════════════════════════════════════════════════════════╝
{C.MAGENTA}                       By MoneyMaker_w{C.R}
{C.CYAN}          Telegram: https://t.me/+RInZ35ML2GhjM2I1{C.R}
{C.GRAY}   ────────────────────────────────────────────────────────{C.R}
""")


def log(msg, level="info"):
    icons = {
        "info":    f"{C.CYAN}ℹ{C.R}",
        "ok":      f"{C.GREEN}✔{C.R}",
        "warn":    f"{C.YELLOW}⚠{C.R}",
        "err":     f"{C.RED}✖{C.R}",
        "coin":    f"{C.YELLOW}🪙{C.R}",
        "auth":    f"{C.BLUE}🔐{C.R}",
        "captcha": f"{C.BLUE}🛡 {C.R}",
        "wait":    f"{C.GRAY}⏳{C.R}",
        "bal":     f"{C.GREEN}💰{C.R}",
        "dbg":     f"{C.MAGENTA}🐛{C.R}",
        "slider":  f"{C.MAGENTA}🎯{C.R}",
    }
    icon = icons.get(level, icons["info"])
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()
    print(f"{C.GRAY}[{now_str()}]{C.R} {icon}  {msg}")


def section(title):
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()
    print(f"\n{C.BOLD}{C.GREEN}▸ {title.upper()}{C.R}")
    print(f"{C.GRAY}{'─' * 60}{C.R}")


def spinner_line(text):
    global _spin_idx
    with _spin_lock:
        frame = SPINNER[_spin_idx % len(SPINNER)]
        _spin_idx += 1
    sys.stdout.write(f"\r\033[K{C.CYAN}{frame}{C.R}  {text}")
    sys.stdout.flush()


def clear_line():
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()


# ==================== CONFIG ====================
def load_config():
    if not CONFIG_PATH.exists():
        return None
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def save_config(cfg):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def ensure_config():
    cfg = load_config()
    if cfg and isinstance(cfg, dict):
        changed = False
        for k, v in DEFAULT_CONFIG.items():
            if k not in cfg:
                cfg[k] = v
                changed = True
        if changed:
            save_config(cfg)
        return cfg
    return dict(DEFAULT_CONFIG)


# ==================== MENU ====================
def menu():
    banner()

    print(f"{C.GRAY}Script :{C.R} {C.DIM}{Path(__file__).resolve()}{C.R}")
    print(f"{C.GRAY}Config :{C.R} {C.DIM}{CONFIG_PATH}{C.R}")
    print()

    cfg = load_config() or {}

    email    = cfg.get("email", "") or "(kosong)"
    password = cfg.get("password", "")
    apikey   = cfg.get("waryono_apikey", "")

    pass_display   = "✓ tersimpan" if password else "(kosong)"
    apikey_display = f"{apikey[:12]}..." if apikey else "(kosong)"

    print(f"{C.GRAY}Config saat ini:{C.R}")
    print(f"  {C.GRAY}Email   :{C.R} {C.CYAN}{email}{C.R}")
    print(f"  {C.GRAY}Password:{C.R} {C.CYAN}{pass_display}{C.R}")
    print(f"  {C.GRAY}API Key :{C.R} {C.CYAN}{apikey_display}{C.R}")
    print()
    print(f"{C.BOLD}{C.GREEN}MENU:{C.R}")
    print(f"  {C.YELLOW}[1]{C.R} Start Farming")
    print(f"  {C.YELLOW}[2]{C.R} Config Email")
    print(f"  {C.YELLOW}[3]{C.R} Config Password")
    print(f"  {C.YELLOW}[4]{C.R} Config Apikey")
    print(f"  {C.YELLOW}[0]{C.R} Exit")
    print()
    try:
        choice = input(f"{C.CYAN}Pilih → {C.R}").strip()
    except (EOFError, KeyboardInterrupt):
        return "0"
    return choice


def menu_config_field(field_name, key, secret=False):
    banner()
    section(f"Config {field_name}")
    print(f"{C.GRAY}File: {C.DIM}{CONFIG_PATH}{C.R}\n")

    cfg = load_config() or dict(DEFAULT_CONFIG)
    current = cfg.get(key, "")
    if current:
        if secret:
            print(f"{C.GRAY}Current: {C.CYAN}(tersimpan){C.R}")
        else:
            print(f"{C.GRAY}Current: {C.CYAN}{current}{C.R}")

    try:
        if secret:
            import getpass
            val = getpass.getpass(f"  {C.CYAN}{field_name} baru{C.R} (kosong=skip): ").strip()
        else:
            val = input(f"  {C.CYAN}{field_name} baru{C.R} (kosong=skip): ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    if val:
        cfg[key] = val
        save_config(cfg)
        print(f"\n{C.GREEN}✔ {field_name} tersimpan di {CONFIG_PATH}{C.R}")
    else:
        print(f"\n{C.YELLOW}Skip — tidak ada perubahan.{C.R}")
    time.sleep(1.5)


def menu_loop():
    while True:
        choice = menu()
        if choice == "1":
            cfg = load_config() or {}
            missing = []
            if not cfg.get("email"):           missing.append("Email")
            if not cfg.get("password"):        missing.append("Password")
            if not cfg.get("waryono_apikey"):  missing.append("API Key")
            if missing:
                banner()
                print(f"{C.RED}Config belum lengkap:{C.R} {', '.join(missing)}")
                print(f"{C.YELLOW}Silakan isi dulu lewat menu 2/3/4.{C.R}")
                time.sleep(2)
                continue
            return cfg
        elif choice == "2":
            menu_config_field("Email", "email", secret=False)
        elif choice == "3":
            menu_config_field("Password", "password", secret=True)
        elif choice == "4":
            menu_config_field("API Key", "waryono_apikey", secret=False)
        elif choice == "0":
            return None
        else:
            print(f"{C.RED}Pilihan tidak valid.{C.R}")
            time.sleep(1)


# ==================== SESSION ====================
def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": ("Mozilla/5.0 (Linux; Android 10; K) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/127.0.0.0 Mobile Safari/537.36"),
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "Origin": BASE,
        "Referer": f"{BASE}/",
    })
    return s


def refresh_csrf(session):
    try:
        r = session.get(f"{BASE}/api/csrf-token", timeout=30)
        if not r.ok:
            return None
        data = r.json()
        token = data.get("csrfToken") or data.get("token")
        if not token:
            token = session.cookies.get("csrf_token")
        if token:
            token = unquote(token)
            STATE["csrf_token"] = token
            return token
    except Exception:
        pass
    return None


def csrf_headers(token=None):
    if not token:
        token = STATE["csrf_token"]
    return {"x-csrf-token": token} if token else {}


# ==================== CAPTCHA SOLVERS ====================
def solve_emoji_slider(challenge):
    ghosts = challenge.get("ghosts") or []
    active_idx = int(challenge.get("activeGhostIndex", 0))
    tolerance = int(challenge.get("tolerance", 12))
    active_emoji = challenge.get("activeEmoji", "?")

    if not ghosts or active_idx >= len(ghosts):
        raise Exception("emoji-slider: challenge invalid")

    target = int(ghosts[active_idx].get("position", 0))
    jitter = max(1, tolerance // 3)
    answer = target + random.randint(-jitter, jitter)
    answer = max(0, min(100, answer))

    log(f"emoji-slider: {active_emoji} pos~{target} → {answer}", "slider")
    return [str(answer)]


def solve_count(challenge):
    grid = challenge.get("grid") or []
    winner = challenge.get("winner")

    if not grid or not winner:
        raise Exception("count: missing grid/winner")

    indices = [i for i, e in enumerate(grid) if e == winner]

    if not indices:
        raise Exception("count: winner tidak ada di grid")

    counts = Counter(grid)
    log(f"count: winner={winner} freq={counts[winner]} idx={indices}", "slider")
    return indices


def solve_sequence(challenge):
    target = challenge.get("target") or []
    grid = challenge.get("grid") or []

    if not target or not grid:
        raise Exception("sequence: missing target/grid")

    pos_map = {}
    for i, e in enumerate(grid):
        pos_map.setdefault(e, []).append(i)

    answer = []
    used = set()
    for t in target:
        for idx in pos_map.get(t, []):
            if idx not in used:
                answer.append(idx)
                used.add(idx)
                break
        else:
            raise Exception(f"sequence: '{t}' tidak ada di grid")

    log(f"sequence: {answer}", "slider")
    return answer


def solve_tap_target(challenge):
    target = challenge.get("target")
    taps = int(challenge.get("tapsRequired", 1))

    if not target:
        raise Exception("tap-target: missing target")

    answer = [target] * taps
    log(f"tap-target: {target} x{taps}", "slider")
    return answer


def solve_connect_pairs(challenge):
    emojis = challenge.get("emojis") or []
    left = challenge.get("leftOrder") or []
    right = challenge.get("rightOrder") or []

    if not emojis or not left or not right:
        raise Exception("connect-pairs: incomplete data")

    answer = []
    for e in emojis:
        try:
            l_idx = left.index(e)
            r_idx = right.index(e)
            answer.append(f"{l_idx}-{r_idx}")
        except ValueError:
            raise Exception(f"connect-pairs: '{e}' tidak ada di left/right")

    log(f"connect-pairs: {answer}", "slider")
    return answer


def solve_drag_order(challenge):
    items = challenge.get("items") or challenge.get("targets") or []
    order = challenge.get("correctOrder") or challenge.get("order") or challenge.get("sequence")

    if order:
        log(f"drag-order: pakai correctOrder", "slider")
        return [str(x) for x in order]

    if items:
        sorted_items = sorted(items, key=lambda x: x.get("order", x.get("index", 0)))
        answer = [str(it.get("id")) for it in sorted_items if it.get("id") is not None]
        if answer:
            log(f"drag-order: sorted by field", "slider")
            return answer

    raise Exception("drag-order: cannot determine order")


def solve_challenge(challenge):
    ctype = (challenge.get("type") or "").lower().strip()
    log(f"Challenge type: {ctype}", "captcha")

    solvers = {
        "emoji-slider":   solve_emoji_slider,
        "count":          solve_count,
        "sequence":       solve_sequence,
        "tap-target":     solve_tap_target,
        "connect-pairs":  solve_connect_pairs,
        "drag-order":     solve_drag_order,
    }

    fn = solvers.get(ctype)
    if not fn:
        raise Exception(f"Unknown challenge type: {ctype}")
    return fn(challenge)


# ==================== LOGIN ====================
def do_login(session, cfg):
    log("Login flow started", "auth")

    token = refresh_csrf(session)
    if not token:
        log("Gagal ambil CSRF token", "err")
        return False
    log(f"CSRF OK ({token[:20]}...)", "auth")

    try:
        r = session.post(
            f"{BASE}/api/captcha/generate",
            headers=dict(csrf_headers(token)),
            timeout=30,
        )
        if not r.ok:
            log(f"Captcha generate HTTP {r.status_code}", "err")
            log(f"Body: {r.text[:300]}", "dbg")
            return False
        cap = r.json()
    except Exception as e:
        log(f"Captcha generate error: {e}", "err")
        return False

    cap_token = cap.get("token")
    challenge = cap.get("challenge") or {}

    if not cap_token or not challenge:
        log(f"Captcha response invalid: {cap}", "err")
        return False

    if cfg.get("debug_challenge", False):
        log(f"Challenge keys: {list(challenge.keys())}", "dbg")

    try:
        answer = solve_challenge(challenge)
    except Exception as e:
        log(f"Solve error: {e}", "err")
        log(f"Challenge dump: {json.dumps(challenge)[:500]}", "dbg")
        return False

    if not answer:
        log("Solve result kosong", "err")
        return False

    log(f"Answer: {json.dumps(answer)[:200]}", "dbg")

    try:
        r = session.post(
            f"{BASE}/api/captcha/verify",
            json={
                "token": cap_token,
                "answer": answer,
                "type": challenge.get("type"),
            },
            headers={**csrf_headers(token), "Content-Type": "application/json"},
            timeout=30,
        )
        if not r.ok:
            log(f"Captcha verify HTTP {r.status_code}", "err")
            log(f"Body: {r.text[:300]}", "dbg")
            return False
        vres = r.json()
    except Exception as e:
        log(f"Captcha verify error: {e}", "err")
        return False

    verified_token = vres.get("verifiedToken")
    if not verified_token:
        log(f"Verify fail: {vres}", "err")
        return False
    log("Captcha verified ✓", "captcha")

    try:
        r = session.post(
            f"{BASE}/api/auth/login",
            json={
                "email": cfg["email"],
                "password": cfg["password"],
                "captchaToken": verified_token,
                "rememberMe": True,
            },
            headers={**csrf_headers(token), "Content-Type": "application/json"},
            timeout=30,
        )
        if not r.ok:
            log(f"Login HTTP {r.status_code}", "err")
            log(f"Body: {r.text[:300]}", "dbg")
            return False
        result = r.json()
    except Exception as e:
        log(f"Login error: {e}", "err")
        return False

    if not result.get("success"):
        log(f"Login failed: {result}", "err")
        return False

    user = result.get("user") or {}
    STATE["user_id"] = user.get("id")
    STATE["username"] = user.get("username")
    STATE["balance"] = user.get("balance")
    STATE["total_earned"] = user.get("totalEarned")
    STATE["logged_in"] = True

    log(f"Login ✓ as {STATE['username']} (#{STATE['user_id']})", "ok")
    log(f"Balance: {STATE['balance']} | Total earned: {STATE['total_earned']}", "bal")
    return True


def verify_session(session):
    try:
        r = session.get(f"{BASE}/api/auth/me",
                        headers=csrf_headers(),
                        timeout=30)
        if r.status_code == 401:
            STATE["logged_in"] = False
            return False
        if not r.ok:
            return False
        data = r.json()
        if data.get("success") and data.get("user"):
            u = data["user"]
            STATE["balance"] = u.get("balance")
            STATE["total_earned"] = u.get("totalEarned")
            STATE["logged_in"] = True
            return True
    except Exception:
        pass
    STATE["logged_in"] = False
    return False


# ==================== WARYONO HCAPTCHA ====================
def solve_hcaptcha(cfg, sitekey):
    apikey = cfg["waryono_apikey"]

    payload = {
        "apikey": apikey,
        "methods": "hcaptcha",
        "domain": BASE,
        "sitekey": sitekey,
        "json": 1,
    }

    try:
        r = requests.post(SOLVER_IN, json=payload, timeout=60)
    except Exception as e:
        raise Exception(f"submit network error: {e}")
    if not r.ok:
        raise Exception(f"submit HTTP {r.status_code}")

    try:
        res = r.json()
    except Exception:
        raise Exception(f"submit non-JSON: {r.text[:150]}")

    if res.get("status") != 1:
        raise Exception(f"submit fail: {res.get('request', res)}")

    task_id = res.get("request")
    log(f"hCaptcha task: {task_id}", "captcha")

    for i in range(100):
        time.sleep(3)
        try:
            check = requests.get(
                SOLVER_RES,
                params={"apikey": apikey, "id": task_id,
                        "action": "get", "json": 1},
                timeout=30,
            ).json()
        except Exception:
            continue

        if check.get("status") == 1:
            token = check.get("request")
            if not token:
                raise Exception(f"solved empty: {check}")
            clear_line()
            log(f"hCaptcha solved ({i*3}s)", "ok")
            return token

        req = str(check.get("request", ""))
        if req in ("CAPCHA_NOT_READY", "CAPTCHA_NOT_READY"):
            spinner_line(f"Polling hcaptcha... ({i*3}s)")
            continue

        clear_line()
        raise Exception(f"waryono error: {req}")

    clear_line()
    raise Exception("hcaptcha timeout")


# ==================== FAUCET ====================
def get_faucet_status(session):
    r = session.get(f"{BASE}/api/faucet/status",
                    headers=csrf_headers(),
                    timeout=30)
    if not r.ok:
        raise Exception(f"faucet/status HTTP {r.status_code}")
    return r.json()


def do_faucet_claim(session, cfg):
    log("Faucet claim started", "coin")

    status = get_faucet_status(session)
    if not status.get("canClaim"):
        next_at = status.get("nextClaimAt")
        if next_at:
            STATE["next_claim_at"] = int(next_at) / 1000.0
        raise Exception("FAUCET_COOLDOWN")

    sitekey = (status.get("captcha") or {}).get("siteKey") or cfg["hcaptcha_sitekey"]
    token = solve_hcaptcha(cfg, sitekey)

    r = session.post(
        f"{BASE}/api/faucet/claim",
        json={"captchaToken": token},
        headers={**csrf_headers(), "Content-Type": "application/json"},
        timeout=60,
    )
    if not r.ok:
        raise Exception(f"claim HTTP {r.status_code}: {r.text[:200]}")

    try:
        data = r.json()
    except Exception:
        raise Exception(f"claim non-JSON: {r.text[:200]}")

    if not data.get("success", True) and "reward" not in data:
        err = data.get("error") or data.get("message") or json.dumps(data)[:200]
        raise Exception(f"claim failed: {err}")

    reward = int(data.get("reward", 0))
    roll = data.get("roll", "?")
    new_balance = data.get("newBalance")
    next_at = data.get("nextClaimAt")

    STATE["total_claims"] += 1
    STATE["total_reward"] += reward
    if new_balance is not None:
        STATE["balance"] = new_balance
    if next_at:
        STATE["next_claim_at"] = int(next_at) / 1000.0

    log(f"Claim ✓ roll #{roll} +{reward} coins | balance: {new_balance}", "coin")
    return data


# ==================== DASHBOARD ====================
def dashboard_line():
    now = time.time()
    cd = STATE["next_claim_at"] - now
    cd_str = f"{C.GREEN}READY{C.R}" if cd <= 0 else f"{C.YELLOW}{fmt_duration(cd)}{C.R}"
    bal = STATE["balance"] if STATE["balance"] is not None else "---"
    runtime = fmt_duration(now - STATE["started_at"])
    return (
        f"{C.GRAY}[{now_str()}]{C.R} "
        f"👤{C.CYAN}{STATE['username'] or '?'}{C.R} "
        f"💰{C.GREEN}{bal}{C.R} "
        f"⏰{cd_str} "
        f"📊{STATE['total_claims']} "
        f"💵{C.YELLOW}{STATE['total_reward']}{C.R} "
        f"⏱{C.CYAN}{runtime}{C.R}"
    )


def wait_with_dashboard(target_ts, label="next claim"):
    print()
    last_sec = -1
    try:
        while True:
            left = target_ts - time.time()
            if left <= 0:
                break
            cur_sec = int(left)
            if cur_sec != last_sec:
                line = f"{dashboard_line()} {C.GRAY}💤{fmt_duration(left)}{C.R}"
                sys.stdout.write(f"\r\033[K{line}")
                sys.stdout.flush()
                last_sec = cur_sec
            time.sleep(min(left, 0.2))
    finally:
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()


# ==================== FARMING ====================
def start_farming(cfg):
    banner()
    log("Bot started", "ok")
    log(f"Config: {CONFIG_PATH}", "info")

    session = make_session()

    section("Auto Login")
    ok = False
    for attempt in range(8):
        try:
            if do_login(session, cfg):
                ok = True
                break
        except Exception as e:
            log(f"Login err ({attempt+1}/8): {e}", "err")
            time.sleep(2)
    if not ok:
        log("Login gagal total, kembali ke menu...", "err")
        time.sleep(2)
        return

    section("Initial Sync")
    try:
        status = get_faucet_status(session)
        if status.get("canClaim"):
            STATE["next_claim_at"] = time.time()
            log("Faucet READY", "ok")
        else:
            nxt = status.get("nextClaimAt")
            if nxt:
                STATE["next_claim_at"] = int(nxt) / 1000.0
                cd = STATE["next_claim_at"] - time.time()
                log(f"Faucet cooldown: {fmt_duration(cd)}", "wait")
    except Exception as e:
        log(f"Initial sync error: {e}", "warn")

    cycle = 0
    while True:
        cycle += 1
        try:
            if not verify_session(session):
                log("Session expired, re-login...", "warn")
                if not do_login(session, cfg):
                    log("Re-login gagal, kembali ke menu...", "err")
                    time.sleep(2)
                    return

            now = time.time()
            cd = STATE["next_claim_at"] - now

            if cd > 0:
                wait_with_dashboard(STATE["next_claim_at"], "next claim")
                continue

            section(f"Cycle #{cycle} — Faucet Claim")
            print(dashboard_line())
            print()

            try:
                do_faucet_claim(session, cfg)
            except Exception as e:
                err = str(e)
                if "FAUCET_COOLDOWN" in err:
                    log("Masih cooldown, tunggu...", "wait")
                    continue
                log(f"Claim error: {err}", "err")
                log("Refresh CSRF...", "info")
                refresh_csrf(session)
                time.sleep(5)
                continue

            verify_session(session)

            if STATE["next_claim_at"] <= time.time():
                STATE["next_claim_at"] = time.time() + 300

        except KeyboardInterrupt:
            print()
            log("Stopped — kembali ke menu.", "warn")
            time.sleep(1)
            return
        except Exception as e:
            log(f"Loop error: {e} (retry 10s)", "err")
            time.sleep(10)


# ==================== MAIN ====================
def main():
    while True:
        cfg = menu_loop()
        if cfg is None:
            clear()
            print(f"{C.YELLOW}Bye!{C.R}")
            return
        try:
            start_farming(cfg)
        except KeyboardInterrupt:
            print()
            print(f"{C.YELLOW}Kembali ke menu...{C.R}")
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}Stopped.{C.R}")
