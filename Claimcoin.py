#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ClaimCoin.in Auto Claim Bot — v5 (Antibot Waryono, imgN parser fixed)
"""

import json
import os
import re
import sys
import time
import random
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ═══════════════════════ COLORS ═══════════════════════
RESET = "\033[0m"
BOLD  = "\033[1m"
RED   = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW= "\033[1;33m"
CYAN  = "\033[1;36m"
WHITE = "\033[1;37m"
GRAY  = "\033[0;90m"
NEON  = "\033[38;5;46m"
NEON_Y= "\033[38;5;226m"

# ═══════════════════════ CONFIG ═══════════════════════
API_URL    = "https://claimcoin.in"
SOLVER_IN  = "https://api.waryono.my.id/in.php"
SOLVER_OUT = "https://api.waryono.my.id/res.php"
SITEKEY    = "0x4AAAAAAB6ZWSg9eOY7OVRl"
DEFAULT_UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36")

CONFIG_FILE              = "config.json"
MAX_SOLVER_RETRY         = 5
MAX_CONSEC_ERROR         = 6
MAX_CLAIM_PER_RUN        = 200
MAX_UNKNOWN_BEFORE_STOP  = 3

# ═══════════════════════ UI HELPERS ═══════════════════════

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def short_cookie(c):
    return c if len(c) <= 40 else c[:20] + "..." + c[-15:]

def log_info(tag, msg): print(f"  {CYAN}[{tag}]{RESET} {msg}")
def log_ok(tag, msg):   print(f"  {GREEN}[{tag}]{RESET} {GREEN}{msg}{RESET}")
def log_warn(tag, msg): print(f"  {YELLOW}[{tag}]{RESET} {YELLOW}{msg}{RESET}")
def log_err(tag, msg):  print(f"  {RED}[{tag}]{RESET} {RED}{msg}{RESET}")

def line_center(text, lw=62):
    plain = re.sub(r'\033\[[0-9;]*m', '', text)
    l = (lw - len(plain)) // 2
    return GRAY + "║" + RESET + " "*max(0,l) + text + " "*max(0, lw-len(plain)-l) + GRAY + "║" + RESET

def line_lr(left, right, lw=62):
    pl = re.sub(r'\033\[[0-9;]*m', '', left)
    pr = re.sub(r'\033\[[0-9;]*m', '', right)
    pad = max(0, lw - len(pl) - len(pr) - 2)
    return GRAY + "║" + RESET + " " + left + " "*pad + right + " " + GRAY + "║" + RESET

def print_header(title="CLAIMCOIN.IN — AUTO CLAIM BOT [WARYONO]"):
    print()
    print(NEON + "  ╔" + "═"*60 + "╗" + RESET)
    print(line_center(NEON + BOLD + title + RESET))
    print(line_center(GRAY + "PyPort by Kyriel | All-in Waryono Solver" + RESET))
    print(NEON + "  ╚" + "═"*60 + "╝" + RESET)

def round_header(n, t):
    print()
    print(CYAN + "  ╭" + "─"*55 + "╮" + RESET)
    print(CYAN + "  │  " + WHITE + BOLD + f"─── ROUND #{n} ─── {t} ───" + RESET)
    print(CYAN + "  ╰" + "─"*55 + "╯" + RESET)

def round_footer():
    print(CYAN + "  ╰" + "─"*55 + "╯" + RESET)

def timer(seconds, prefix="  waiting"):
    seconds = int(seconds)
    if seconds < 1: return
    frames = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷']
    fc, cf = len(frames), 0
    t = seconds
    while t > 0:
        start = time.time()
        while time.time() - start < 1:
            hh = t // 3600
            mm = (t % 3600) // 60
            ss = t % 60
            sys.stdout.write(f"  {GRAY}{prefix}{RESET} {NEON_Y}{hh:02d}:{mm:02d}:{ss:02d}{RESET} {CYAN}{frames[cf]}{RESET}\r")
            sys.stdout.flush()
            time.sleep(0.1)
            cf = (cf + 1) % fc
            if time.time() - start >= 1: break
        t -= 1
    sys.stdout.write("\r" + " "*60 + "\r")
    sys.stdout.flush()

def dump_html(html, label="faucet"):
    fn = f"debug_{label}_{time.strftime('%Y%m%d_%H%M%S')}.html"
    try:
        with open(fn, "w", encoding="utf-8", errors="ignore") as f:
            f.write(html)
        log_info("DEBUG", f"HTML dumped → {GRAY}{fn}{RESET} ({len(html)} bytes)")
        return fn
    except Exception:
        return None

# ═══════════════════════ CONFIG LOAD/SAVE ═══════════════════════

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_config():
    if not os.path.exists(CONFIG_FILE):
        print()
        print(NEON + "  ╔" + "═"*60 + "╗" + RESET)
        print(line_center(YELLOW + BOLD + "SETUP AWAL — COOKIE MODE" + RESET))
        print(NEON + "  ╚" + "═"*60 + "╝" + RESET + "\n")
        print(f"  {GRAY}Cara ambil cookies:{RESET}")
        print(f"  {GRAY}  1. Login claimcoin.in di browser{RESET}")
        print(f"  {GRAY}  2. F12 → Application → Cookies → https://claimcoin.in{RESET}")
        print(f"  {GRAY}  3. Copy semua jadi format: name=value; name=value; ...{RESET}\n")
        apikey  = input(f"  {WHITE}Solver API Key{GRAY} : {RESET}").strip()
        cookies = input(f"  {WHITE}Cookies       {GRAY} : {RESET}").strip()
        ua      = input(f"  {WHITE}User-Agent    {GRAY} (blank=default): {RESET}").strip()
        if not ua: ua = DEFAULT_UA
        data = {"apikey": apikey, "cookies": cookies, "user_agent": ua}
        save_config(data)
        print(f"\n  {GREEN}✓ Config saved → {CONFIG_FILE}{RESET}")
        time.sleep(1)
        return data
    with open(CONFIG_FILE) as f:
        return json.load(f)

# ═══════════════════════ HTTP CLIENT ═══════════════════════

class Client:
    def __init__(self, cookies_raw, user_agent):
        self.cookies_raw = cookies_raw
        self.user_agent  = user_agent
        self.session     = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        for pair in cookies_raw.split(";"):
            if "=" in pair:
                k, v = pair.strip().split("=", 1)
                self.session.cookies.set(k, v)

    def sync_csrf(self, csrf):
        if not csrf: return
        if re.search(r'csrf_cookie_name=[^;]*', self.cookies_raw):
            self.cookies_raw = re.sub(r'csrf_cookie_name=[^;]*', 'csrf_cookie_name=' + csrf, self.cookies_raw)
        else:
            self.cookies_raw += "; csrf_cookie_name=" + csrf
        self.session.cookies.set("csrf_cookie_name", csrf)

    def request(self, method, url, headers=None, data=None, json_data=None,
                allow_redirects=True, timeout=30):
        h = dict(headers or {})
        try:
            r = self.session.request(
                method, url, headers=h, data=data, json=json_data,
                allow_redirects=allow_redirects, timeout=timeout,
            )
            return {
                "status": r.status_code,
                "body":   r.text,
                "headers": dict(r.headers),
                "raw_headers": "\n".join(f"{k}: {v}" for k, v in r.headers.items()),
                "url":    r.url,
            }
        except requests.RequestException as e:
            return {"status": 0, "body": "", "headers": {}, "raw_headers": "", "error": str(e)}

# ═══════════════════════ HEADERS ═══════════════════════

def base_headers(extra=None):
    h = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "upgrade-insecure-requests": "1",
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "navigate",
        "sec-fetch-dest": "document",
        "dnt": "1",
    }
    if extra: h.update(extra)
    return h

def ajax_headers(extra=None):
    h = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "priority": "u=1, i",
    }
    if extra: h.update(extra)
    return h

def detect_cf(html):
    if not html: return False
    return any(x in html for x in [
        "Just a moment", "cf-challenge", "challenge-platform",
        "_cf_chl_opt", "cf-browser-verification"
    ])

# ═══════════════════════ PARSERS ═══════════════════════

def extract_csrf(html):
    for pat in [
        r'name="csrf_token_name"\s+value="([^"]+)"',
        r'name="csrf_token_name"\s+id="[^"]*"\s+value="([^"]+)"',
        r'"csrf_token_name"\s*:\s*"([^"]+)"',
    ]:
        m = re.search(pat, html, re.I)
        if m: return m.group(1)
    return None

def extract_sitekey(html):
    m = re.search(r'data-sitekey="([^"]+)"', html, re.I)
    if m: return m.group(1)
    m = re.search(r'sitekey["\']?\s*[:=]\s*["\']([^"\']+)["\']', html, re.I)
    if m: return m.group(1)
    return SITEKEY

def extract_instruction_image(html):
    m = re.search(r'id="atb-instruction".*?<img[^>]+src="data:image/[^;]+;base64,([A-Za-z0-9+/=]+)"',
                  html, re.S | re.I)
    if m: return m.group(1)
    m = re.search(r'class="alert[^"]*alert-warning[^"]*"[^>]*>(.*?)</div>',
                  html, re.S | re.I)
    if m:
        im = re.search(r'data:image/[^;]+;base64,([A-Za-z0-9+/=]+)', m.group(1))
        if im: return im.group(1)
    return None

def _js_unescape(s):
    def repl_uni(m):
        try: return chr(int(m.group(1), 16))
        except Exception: return m.group(0)
    s = re.sub(r'\\u([0-9a-fA-F]{4})', repl_uni, s)
    s = s.replace('\\/', '/').replace('\\"', '"').replace("\\'", "'")
    s = s.replace('\\n', '\n').replace('\\r', '\r').replace('\\t', '\t')
    s = s.replace('\\\\', '\\')
    return s

def extract_antibot_links(html):
    m = re.search(r'var\s+links\s*=\s*\[(.*?)\]\s*;', html, re.S)
    if not m:
        m = re.search(r'var\s+links\s*=\s*\[(.*?)\]', html, re.S)
    if not m:
        return []
    array_content = m.group(1)
    items = re.findall(r'"((?:[^"\\]|\\.)*)"', array_content)
    results = []
    for raw in items:
        s = _js_unescape(raw)
        tok_m = re.search(r'data-antibot-token="([a-f0-9]{32})"', s, re.I)
        img_m = re.search(r'<img[^>]+src="data:image/[^;]+;base64,([A-Za-z0-9+/=]+)"', s, re.I)
        if tok_m and img_m:
            results.append({"token": tok_m.group(1), "image_b64": img_m.group(1)})
    seen = set()
    uniq = []
    for r in results:
        if r["token"] not in seen:
            seen.add(r["token"])
            uniq.append(r)
    return uniq

# ═══════════════════════ SOLVER RESPONSE PARSER ═══════════════════════

def parse_solver_response(raw):
    raw = (raw or "").strip()
    if not raw: return {"status":"error","id":"","code":"EMPTY_RESPONSE"}
    try:
        j = json.loads(raw)
        if isinstance(j, dict):
            req = str(j.get("request", "")).strip()
            st  = int(j.get("status", 0)) if j.get("status") is not None else None
            if st == 0 or req.startswith("ERROR_"):
                return {"status":"error","id":"","code":req or "UNKNOWN"}
            if req and not req.startswith("ERROR_") and "CAPCHA_NOT_READY" not in req:
                return {"status":"ok","id":req,"code":""}
            if "CAPCHA_NOT_READY" in req:
                return {"status":"error","id":"","code":"CAPCHA_NOT_READY"}
            return {"status":"error","id":"","code":"UNKNOWN_JSON"}
    except Exception:
        pass
    if raw.startswith("OK|"):
        return {"status":"ok","id":raw[3:].strip(),"code":""}
    if raw.startswith("ERROR_"):
        return {"status":"error","id":"","code":raw.split("|")[0]}
    if "CAPCHA_NOT_READY" in raw:
        return {"status":"error","id":"","code":"CAPCHA_NOT_READY"}
    return {"status":"error","id":"","code":raw}

# ═══════════════════════ ANTIBOT PARSER FIXED ═══════════════════════

def _parse_antibot_result(result, tokens):
    """
    Parse hasil solver. Support:
    - Format Waryono: "img3,img1,img2,..." ← PRIORITAS
    - Angka: "1 2 3" / "123" / "2,3,1"
    - Token hex 32-char
    """
    n = len(tokens)

    # ═══ PRIORITY 1: pola "imgN" ═══
    img_order = re.findall(r'\bimg(\d+)\b', result, re.I)
    if len(img_order) >= n:
        img_order = img_order[:n]
        nums = [int(x) for x in img_order]
        # 1-based (img1, img2, img3)
        if all(1 <= i <= n for i in nums) and len(set(nums)) == n:
            return [tokens[i-1] for i in nums]
        # 0-based (img0, img1, img2)
        if all(0 <= i < n for i in nums) and len(set(nums)) == n:
            return [tokens[i] for i in nums]

    # ═══ PRIORITY 2: token hex langsung ═══
    found_tokens = re.findall(r'\b([a-f0-9]{32})\b', result, re.I)
    if len(found_tokens) == n:
        if set(t.lower() for t in found_tokens) == set(t.lower() for t in tokens):
            mapped = []
            for ft in found_tokens:
                for orig in tokens:
                    if orig.lower() == ft.lower():
                        mapped.append(orig)
                        break
            if len(mapped) == n:
                return mapped

    # ═══ PRIORITY 3: angka murni ═══
    clean = re.sub(r'\bimg\d+\b', '', result, flags=re.I)
    clean = re.sub(r'\b(image|answer)\d+\b', '', clean, flags=re.I)
    nums = [int(x) for x in re.findall(r'\d+', clean)]
    if len(nums) == n:
        if all(1 <= i <= n for i in nums) and len(set(nums)) == n:
            return [tokens[i-1] for i in nums]
        if all(0 <= i < n for i in nums) and len(set(nums)) == n:
            return [tokens[i] for i in nums]

    return None


# ═══════════════════════ ANTIBOT SOLVER (WARYONO) ═══════════════════════

def solve_antibot_waryono(client, apikey, html):
    instruction_b64 = extract_instruction_image(html)
    if not instruction_b64:
        log_warn("ANTIBOT", "instruction image tidak ditemukan")
        return None

    links = extract_antibot_links(html)
    if not links:
        log_warn("ANTIBOT", "antibot links tidak ditemukan")
        return None

    tokens = [l["token"] for l in links]
    imgs = [l["image_b64"] for l in links]

    log_info("ANTIBOT", f"solver request: main + {len(imgs)} images")
    log_info("ANTIBOT", "img mapping: " + ", ".join(f"img{i+1}={tokens[i][:8]}" for i in range(len(tokens))))

    payload = {
        "apikey": apikey,
        "methods": "antibot",
        "main": instruction_b64,
        "json": 1,
    }
    for i, img in enumerate(imgs):
        payload[f"img{i+1}"] = img

    r = client.request("POST", SOLVER_IN,
                       headers={"Content-Type": "application/json"},
                       json_data=payload)
    p = parse_solver_response(r["body"])

    if p["status"] == "error":
        log_err("ANTIBOT", f"solver submit error: {p['code']}")
        log_info("ANTIBOT", f"raw: {GRAY}{r['body'][:200]}{RESET}")
        return None

    task_id = p["id"]
    if not task_id:
        log_err("ANTIBOT", f"solver no id, resp: {r['body'][:200]}")
        return None

    log_info("ANTIBOT", f"task id = {CYAN}{task_id}{RESET}")

    for poll in range(1, 41):
        timer(5, f"  poll {poll} ")
        url = f"{SOLVER_OUT}?apikey={requests.utils.quote(apikey)}&action=get&id={requests.utils.quote(task_id)}&json=1"
        r = client.request("GET", url)
        p = parse_solver_response(r["body"])

        if p["status"] == "error":
            e = p["code"]
            if e in ("CAPCHA_NOT_READY", "CAPTCHA_NOT_READY"):
                continue
            log_err("ANTIBOT", f"solver poll error: {e}")
            return None

        raw_result = p.get("id", "").strip()
        if not raw_result:
            continue

        log_info("ANTIBOT", f"raw result: {GRAY}{raw_result[:200]}{RESET}")

        ordered = _parse_antibot_result(raw_result, tokens)
        if ordered:
            log_ok("ANTIBOT", f"solver order → {[t[:8] for t in ordered]}")
            return ordered

        log_warn("ANTIBOT", f"result ga bisa di-parse: {raw_result[:120]}")
        return None

    log_err("ANTIBOT", "solver poll timeout")
    return None

# ═══════════════════════ TURNSTILE SOLVER ═══════════════════════

def solve_captcha(client, apikey, method, sitekey, action="", attempt=1):
    if attempt > MAX_SOLVER_RETRY:
        log_err("solver", f"retry limit reached ({MAX_SOLVER_RETRY}x) — stop")
        return None
    body = {"apikey": apikey, "methods": method, "domain": "https://claimcoin.in",
            "sitekey": sitekey, "json": 1}
    if action: body["action"] = action

    r = client.request("POST", SOLVER_IN,
                       headers={"Content-Type": "application/json"},
                       json_data=body)
    p = parse_solver_response(r["body"])

    if p["status"] == "error":
        e = p["code"]
        fatal = {"ERROR_WRONG_USER_KEY","ERROR_KEY_DOES_NOT_EXIST","ERROR_ZERO_BALANCE",
                 "ERROR_WRONG_METHOD","ERROR_METHOD_NOT_SPECIFIED","ERROR_NO_SUCH_METHOD",
                 "ERROR_BAD_PARAMETERS","ERROR_EMPTY_IMAGE","ERROR_DATABASE_CONNECTION_FAILED","ERROR_UNKNOWN"}
        if e in fatal:
            log_err("solver", e)
            return None
        if e == "ERROR_TOO_MANY_REQUESTS":
            log_warn("solver", f"TOO_MANY_REQUESTS, retry ({attempt}/{MAX_SOLVER_RETRY})")
            time.sleep(3)
            return solve_captcha(client, apikey, method, sitekey, action, attempt+1)
        log_warn("solver", f"err: {e}, retry ({attempt}/{MAX_SOLVER_RETRY})")
        time.sleep(3)
        return solve_captcha(client, apikey, method, sitekey, action, attempt+1)

    task_id = p["id"]
    if not task_id:
        log_err("solver", "no id in response")
        time.sleep(3)
        return solve_captcha(client, apikey, method, sitekey, action, attempt+1)

    log_info("solver", f"task id = {CYAN}{task_id}{RESET}")
    for poll in range(1, 41):
        timer(5, f"  poll {poll} ")
        url = f"{SOLVER_OUT}?apikey={requests.utils.quote(apikey)}&action=get&id={requests.utils.quote(task_id)}&json=1"
        r = client.request("GET", url)
        p = parse_solver_response(r["body"])
        if p["status"] == "error":
            e = p["code"]
            if e in ("CAPCHA_NOT_READY", "CAPTCHA_NOT_READY"):
                continue
            if e == "ERROR_CAPTCHA_UNSOLVABLE":
                log_warn("solver", f"UNSOLVABLE, retry ({attempt}/{MAX_SOLVER_RETRY})")
                time.sleep(1)
                return solve_captcha(client, apikey, method, sitekey, action, attempt+1)
            if e in ("WRONG_CAPTCHA_ID","ERROR_SOLVE_PENDING","ERROR_BAD_REQUEST",
                     "INTENAL_SERVER_ERROR","INTERNAL_SERVER_ERROR"):
                log_warn("solver", f"{e}, retry ({attempt}/{MAX_SOLVER_RETRY})")
                time.sleep(1)
                return solve_captcha(client, apikey, method, sitekey, action, attempt+1)
            if e in ("ERROR_BAD_PARAMETERS","ERROR_WRONG_USER_KEY",
                     "ERROR_KEY_DOES_NOT_EXIST","ERROR_ZERO_BALANCE"):
                log_err("solver", f"fatal: {e}")
                return None
            log_warn("solver", f"poll err: {e}, retry ({attempt}/{MAX_SOLVER_RETRY})")
            time.sleep(1)
            return solve_captcha(client, apikey, method, sitekey, action, attempt+1)
        if p["id"]:
            return p["id"]
    log_err("solver", "poll timeout")
    return None

# ═══════════════════════ BYPASS FETCH ═══════════════════════

def try_fetch(client, path, extra=None, label=""):
    url = API_URL + path
    for hdrs in [
        base_headers(extra or {}),
        ajax_headers(extra or {}),
        {**{"accept": "*/*", "x-requested-with": "XMLHttpRequest"}, **(extra or {})},
    ]:
        r = client.request("GET", url, headers=hdrs)
        if r["body"] and not detect_cf(r["body"]):
            return r
    if label:
        log_err("BYPASS", f"{label} → semua attempt kena CF")
    return None

# ═══════════════════════ BALANCE / REWARD ═══════════════════════

def parse_reward(html):
    for pat in [
        r"'([\d.]+)\s*tokens has been added to your balance'",
        r'Good job!.*?([\d.]+)\s*tokens',
        r'([\d.]+)\s*tokens has been added',
    ]:
        m = re.search(pat, html, re.I|re.S)
        if m: return m.group(1)
    return None

def parse_balance(html):
    for pat in [
        r'Available Balance</span>\s*<h3>([\d.,]+)\s*tokens?</h3>',
        r'Available Balance.*?([\d.,]+)\s*tokens?',
        r'balance[^0-9]{1,20}([\d.,]+)\s*tokens?',
    ]:
        m = re.search(pat, html, re.I|re.S)
        if m: return m.group(1)
    return None

def is_limit_reached(html):
    needles = [
        'reached the daily limit','you have reached the daily limit','daily faucet limit reached',
        'you have reached your limit','faucet daily limit reached','daily claim limit reached',
        'no more claims today','come back tomorrow','limit for today has been reached',
        'you reached your daily','exceeded your daily','exceeded the daily','daily limit exceeded',
        'out of tokens for today','faucet is empty for today',
    ]
    return any(n in html.lower() for n in needles)

def parse_faucet_state(html):
    if not html:
        return {"ready": False, "wait": 0, "unknown": True, "reason": "empty_body"}

    if ('Earn Crypto' in html and 'Every Day' in html
            and ('href="login"' in html or 'href="register"' in html)):
        return {"ready": False, "wait": -1, "unauthed": True,
                "reason": "landing_page"}

    if ('name="password"' in html and 'name="email"' in html) \
            or "cc-auth-body" in html:
        return {"ready": False, "wait": -1, "unauthed": True,
                "reason": "login_page"}

    m = re.search(
        r'<b[^>]*id=["\']minute["\'][^>]*>(\d+)</b>\s*[:.]\s*'
        r'<b[^>]*id=["\']second["\'][^>]*>(\d+)</b>',
        html, re.I|re.S)
    if m:
        wait = int(m.group(1)) * 60 + int(m.group(2))
        return {"ready": False, "wait": wait, "pattern": "b minute/second"}

    m = re.search(
        r'id=["\']minute["\'][^>]*>(\d+)<[^>]*>.*?id=["\']second["\'][^>]*>(\d+)',
        html, re.I|re.S)
    if m:
        wait = int(m.group(1)) * 60 + int(m.group(2))
        return {"ready": False, "wait": wait, "pattern": "id minute/second"}

    m = re.search(r'var\s+wait\s*=\s*(\d+)\s*-\s*1', html, re.I)
    if m:
        return {"ready": False, "wait": int(m.group(1)), "pattern": "var wait"}

    m = re.search(r'data-countdown=["\'](\d+)["\']', html, re.I)
    if m:
        return {"ready": False, "wait": int(m.group(1)), "pattern": "data-countdown"}

    if re.search(r'<h4[^>]*class="[^"]*cc-countdown-ready[^"]*"[^>]*>\s*READY\b', html, re.I):
        return {"ready": True, "wait": 0, "pattern": "h4.cc-countdown-ready"}
    if re.search(r'<h4[^>]*>\s*READY\s*</h4>', html, re.I):
        return {"ready": True, "wait": 0, "pattern": "h4 READY text"}

    return {"ready": False, "wait": 0, "unknown": True, "reason": "no_pattern_matched"}

def fetch_balance(client, max_retry=3):
    for attempt in range(1, max_retry + 1):
        r = try_fetch(client, "/dashboard",
                      {"referer": API_URL + "/faucet"}, "/dashboard")
        if r is None:
            if attempt < max_retry:
                log_warn("BALANCE", f"CF challenge, retry in 3s... ({attempt}/{max_retry})")
                time.sleep(3)
                continue
            return {"ok": False, "reason": "cf"}
        if ('Earn Crypto' in r["body"] and 'Every Day' in r["body"]) \
                or "cc-auth-body" in r["body"] \
                or 'name="password"' in r["body"]:
            return {"ok": False, "reason": "unauthed"}
        bal = parse_balance(r["body"])
        if bal is None:
            return {"ok": True, "reason": "ok", "balance": None, "balance_missing": True}
        return {"ok": True, "reason": "ok", "balance": bal}
    return {"ok": False, "reason": "cf"}

def _to_float(b):
    try: return float(str(b).replace(',', ''))
    except Exception: return None

# ═══════════════════════ ANTIBOT CLICK ═══════════════════════

def click_one_antibot(client, token, csrf):
    payload = {"antibot_token": token, "csrf_token_name": csrf}
    headers = ajax_headers({
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "origin": API_URL,
        "referer": API_URL + "/",
    })
    r = client.request("POST", API_URL + "/faucet/antibot_click",
                       headers=headers, data=payload)
    try:
        return json.loads(r["body"])
    except Exception:
        log_err("ANTIBOT", f"non-JSON response: {r['body'][:200]}")
        return {"ok": False}

def click_antibot_ordered(client, ordered_tokens, csrf):
    remaining = list(ordered_tokens)
    total = len(ordered_tokens)
    for step in range(total):
        tried_order = list(remaining)
        succeeded = False
        for token in tried_order:
            r = click_one_antibot(client, token, csrf)
            if r.get("csrf_hash"):
                csrf = r["csrf_hash"]
                client.sync_csrf(csrf)
            if r.get("ok") is True:
                remaining.remove(token)
                succeeded = True
                log_info("ANTIBOT", f"step {step+1}/{total} ok (token {token[:8]}...) complete={r.get('complete')}")
                if r.get("complete"):
                    return csrf
                time.sleep(0.4)
                break
            else:
                log_info("ANTIBOT", f"step {step+1}: token {token[:8]}... rejected")
        if not succeeded:
            log_err("ANTIBOT", f"step {step+1}/{total}: semua token sisa ditolak")
            return False
    return csrf

# ═══════════════════════ CLAIM ═══════════════════════

def post_verify(client, payload):
    log_info("POST", "/faucet/verify (ajax)")
    last_r = None
    for hdrs in [
        ajax_headers({"content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                      "origin": API_URL, "referer": API_URL + "/faucet"}),
        {"accept": "*/*", "content-type": "application/x-www-form-urlencoded",
         "origin": API_URL, "referer": API_URL + "/faucet",
         "x-requested-with": "XMLHttpRequest"},
        {"content-type": "application/x-www-form-urlencoded",
         "x-requested-with": "XMLHttpRequest"},
        {"content-type": "application/x-www-form-urlencoded",
         "accept": "application/json, text/plain, */*",
         "origin": API_URL, "x-requested-with": "XMLHttpRequest"},
    ]:
        r = client.request("POST", API_URL + "/faucet/verify",
                           headers=hdrs, data=payload)
        last_r = r
        if not detect_cf(r["body"]):
            return r
    return last_r


def _check_balance_after_verify(client, bal_before, reason_tag):
    log_info("CLAIM", f"konfirmasi via balance check ({reason_tag})...")
    time.sleep(3)
    for attempt in range(1, 4):
        b = fetch_balance(client, max_retry=2)
        if b.get("ok") and b.get("balance") is not None:
            bnum = _to_float(b["balance"])
            if bnum is not None and bal_before is not None and bnum > bal_before:
                diff = bnum - bal_before
                log_ok("CLAIM", f"✓ balance naik +{diff:.4f} → sukses")
                return {"state": "claimed", "reward": f"{diff:.4f}"}
            if attempt < 3:
                log_warn("CLAIM", f"balance belum naik (attempt {attempt}/3), tunggu 5s...")
                time.sleep(5)
                continue
            log_err("CLAIM", "balance ga naik → gagal")
            return {"state": "error"}
        if attempt < 3:
            log_warn("CLAIM", f"balance not parseable (attempt {attempt}/3), retry 5s...")
            time.sleep(5)
    log_err("CLAIM", "gagal verifikasi balance")
    return {"state": "error"}


def claim_once(client, apikey, bal_before=None):
    log_info("GET", "/faucet")
    r = try_fetch(client, "/faucet", {"referer": API_URL + "/dashboard"}, "/faucet")
    if r is None:
        return {"state": "cf"}

    html = r["body"]
    st = parse_faucet_state(html)

    if st.get("unauthed"):
        reason = st.get("reason", "unknown")
        if reason == "landing_page":
            log_err("FAUCET", "session expired — server redirect ke landing page")
        elif reason == "login_page":
            log_err("FAUCET", "session expired — server redirect ke /login")
        else:
            log_err("FAUCET", "session expired / not logged in")
        return {"state": "unauthed"}

    if st.get("unknown"):
        log_warn("FAUCET", f"parser tidak mengenali HTML (reason: {st.get('reason','?')})")
        dump_html(html, "faucet_unknown")
        return {"state": "unknown"}

    if not st["ready"]:
        if st["wait"] > 0:
            w = max(3, int(st["wait"]))
            log_warn("FAUCET", f"COOLDOWN | next in {w}s (pattern: {st.get('pattern','?')})")
            print(f"  {GRAY}Cooldown: {RESET}{NEON_Y}{w//60:02d}:{w%60:02d}{RESET}")
            timer(w + 2, "  waiting ")
            return {"state": "notready"}
        if is_limit_reached(html):
            log_warn("FAUCET", "Daily limit reached")
            return {"state": "limit"}
        log_warn("FAUCET", "not ready, wait 10s (fallback)")
        timer(12, "  waiting ")
        return {"state": "notready"}

    csrf = extract_csrf(html)
    if not csrf:
        m = re.search(r'csrf_cookie_name=([a-f0-9]{32})', r["raw_headers"], re.I)
        if m: csrf = m.group(1)
    if not csrf:
        log_err("FAUCET", "csrf not found")
        dump_html(html, "faucet_nocsrf")
        return {"state": "error"}

    client.sync_csrf(csrf)
    sitekey = extract_sitekey(html)

    log_ok("FAUCET", "status: READY" + (f" (pattern: {st.get('pattern')})" if st.get("pattern") else ""))
    log_info("FAUCET", f"csrf   : {GRAY}{csrf[:16]}...{RESET}")
    log_info("FAUCET", f"sitekey: {GRAY}{sitekey}{RESET}")

    # ═══ ANTIBOT via Waryono solver ═══
    links = extract_antibot_links(html)
    if links:
        log_info("ANTIBOT", f"found {len(links)} tokens")
        ordered_tokens = solve_antibot_waryono(client, apikey, html)
        if not ordered_tokens:
            log_warn("ANTIBOT", "solver gagal, fallback coba urutan asli")
            ordered_tokens = [l["token"] for l in links]

        new_csrf = click_antibot_ordered(client, ordered_tokens, csrf)
        if new_csrf is False:
            log_err("ANTIBOT", "failed to complete anti-bot links")
            return {"state": "error"}
        csrf = new_csrf
        log_ok("ANTIBOT", "all links completed, csrf updated")
    else:
        log_warn("ANTIBOT", "no tokens found (mungkin udah done / layout beda)")
        if "var links" in html or "antibotlink" in html:
            dump_html(html, "faucet_antibot_parsefail")

    # ═══ TURNSTILE ═══
    log_info("FAUCET", f"method : {CYAN}turnstile{RESET}")
    token = solve_captcha(client, apikey, "turnstile", sitekey, "faucet")
    if not token:
        log_err("CAPTCHA", "failed")
        return {"state": "error"}

    payload = {
        "csrf_token_name": csrf,
        "captcha": "turnstile",
        "cf-turnstile-response": token,
    }

    res = post_verify(client, payload)
    rbody = res["body"]
    rstatus = res["status"]

    if detect_cf(rbody):
        log_err("CLAIM", "CF challenge di verify")
        return _check_balance_after_verify(client, bal_before, "cf-verify")

    if is_limit_reached(rbody):
        return {"state": "limit"}

    reward = parse_reward(rbody)
    if reward is not None:
        return {"state": "claimed", "reward": reward}

    err_m = re.search(r"Swal\.fire\(\s*'[^']*'\s*,\s*'([^']+)'", rbody, re.I)
    if err_m:
        msg = err_m.group(1)[:120]
        log_err("CLAIM", f"server pesan: {msg}")
        if "wait" in msg.lower() or "cooldown" in msg.lower():
            return {"state": "notready"}
        return {"state": "error"}

    if not rbody or len(rbody.strip()) < 50:
        log_warn("CLAIM", f"verify response empty/kecil (status={rstatus}, len={len(rbody)})")
        return _check_balance_after_verify(client, bal_before, "empty-verify")

    st2 = parse_faucet_state(rbody)
    if st2.get("unauthed"):
        return {"state": "unauthed"}
    if st2.get("ready") and reward is None:
        log_warn("CLAIM", "verify return READY tanpa reward — cek balance")
        return _check_balance_after_verify(client, bal_before, "ready-no-reward")
    if not st2["ready"] and st2["wait"] > 0:
        return {"state": "notready", "wait": st2["wait"]}

    log_err("CLAIM", "unknown response")
    dump_html(rbody, "verify_unknown")
    return _check_balance_after_verify(client, bal_before, "unknown-verify")

# ═══════════════════════ MENU ═══════════════════════

def main_menu(cookie_preview):
    print()
    print(f"  {WHITE}{BOLD}Solver{RESET} : {CYAN}WARYONO (turnstile + antibot){RESET}")
    print(f"  {WHITE}{BOLD}Cookie{RESET} : {CYAN}{cookie_preview}{RESET}")
    print(f"  {GRAY}{'─'*58}{RESET}")
    print(f"    {NEON}[1]{RESET} Lanjut")
    print(f"    {NEON}[2]{RESET} Edit config")
    print(f"    {NEON}[3]{RESET} Reset")
    return input(f"  {GRAY}>> {RESET}").strip()

# ═══════════════════════ MAIN ═══════════════════════

def main():
    clear()
    config = get_config()

    while True:
        apikey     = config["apikey"]
        cookies    = config.get("cookies", "")
        user_agent = config.get("user_agent", DEFAULT_UA)

        client = Client(cookies, user_agent)

        print_header()
        choice = main_menu(short_cookie(cookies))

        if choice == "2":
            try: os.remove(CONFIG_FILE)
            except Exception: pass
            config = get_config()
            continue
        if choice == "3":
            try: os.remove(CONFIG_FILE)
            except Exception: pass
            print(f"\n  {GREEN}✓ Config dihapus.{RESET}")
            time.sleep(1)
            clear()
            config = get_config()
            continue

        clear()
        print_header()
        print(f"\n  {WHITE}{BOLD}Solver{RESET} : {CYAN}WARYONO{RESET}")
        print(f"  {WHITE}{BOLD}Cookie{RESET} : {CYAN}{short_cookie(cookies)}{RESET}\n")

        has_session = "ci_session=" in cookies
        has_cf      = "cf_clearance=" in cookies
        has_csrf    = "csrf_cookie_name=" in cookies
        if not (has_session and has_cf and has_csrf):
            log_warn("START",
                f"cookie incomplete → "
                f"ci_session={'✓' if has_session else '✗'} "
                f"cf_clearance={'✓' if has_cf else '✗'} "
                f"csrf_cookie_name={'✓' if has_csrf else '✗'}")

        log_info("START", "cek balance dulu sebelum faucet")
        bal = fetch_balance(client)

        if not bal["ok"]:
            if bal["reason"] == "cf":
                print(f"\n  {RED}✗ Cloudflare challenge di /dashboard.{RESET}")
                print(f"  {GRAY}Update cookie dengan yang fresh dari browser.{RESET}")
            elif bal["reason"] == "unauthed":
                print(f"\n  {RED}✗ ci_session expired / belum login.{RESET}")
                print(f"  {GRAY}Login ulang di browser, copy cookie baru.{RESET}")
            else:
                print(f"\n  {RED}✗ Unknown error.{RESET}")
            input(f"\n  {GRAY}Tekan ENTER balik ke menu...{RESET}")
            clear()
            continue

        balance = bal.get("balance")
        bal_missing = bal.get("balance_missing")

        print()
        print(NEON + "  ╔" + "═"*60 + "╗" + RESET)
        print(line_center(GREEN + BOLD + "✓ SESSION VALID" + RESET))
        print(NEON + "  ╠" + "═"*60 + "╣" + RESET)
        print(line_lr(WHITE + "Mode    " + RESET + " : " + CYAN + "COOKIE + WARYONO" + RESET, ""))
        print(line_lr(WHITE + "Solver  " + RESET + " : " + CYAN + "WARYONO" + RESET, ""))
        print(line_lr(WHITE + "Antibot " + RESET + " : " + CYAN + "waryono/antibot" + RESET, ""))
        print(line_lr(WHITE + "Cookie  " + RESET + " : " + GRAY + short_cookie(cookies) + RESET, ""))
        if bal_missing:
            print(line_lr(WHITE + "Balance " + RESET + " : " + YELLOW + "not parsed" + RESET, ""))
        else:
            bstr = "?" if balance is None else f"{_to_float(balance):,.2f} tokens"
            print(line_lr(WHITE + "Balance " + RESET + " : " + NEON_Y + bstr + RESET, ""))
        print(NEON + "  ╚" + "═"*60 + "╝" + RESET + "\n")

        total_claims = 0
        consec_err   = 0
        consec_unk   = 0
        rnd = 0
        cur_bal = _to_float(balance)

        while True:
            if total_claims >= MAX_CLAIM_PER_RUN:
                log_warn("MAIN", f"cap {MAX_CLAIM_PER_RUN} claims tercapai, exit.")
                break

            rnd += 1
            round_header(rnd, time.strftime("%H:%M:%S"))

            r = claim_once(client, apikey, bal_before=cur_bal)
            state = r.get("state")

            if state == "claimed":
                total_claims += 1
                consec_unk = 0
                reward = r.get("reward")
                rstr = "?" if reward == "?" else f"{float(reward):.4f}"
                b = fetch_balance(client)
                if b.get("ok") and b.get("balance") is not None:
                    cur_bal = _to_float(b["balance"])
                    bstr = f"{cur_bal:,.2f} tokens"
                else:
                    bstr = "(not parsed)"
                print()
                log_ok("CLAIM", f"✓ +{rstr} tokens | balance: {bstr}")
                log_info("TOTAL", f"claims: {GREEN}{total_claims}{RESET}")
                round_footer()
                consec_err = 0
                timer(random.randint(2, 4), "  cooldown ")

            elif state == "notready":
                round_footer()
                consec_err = 0
                consec_unk = 0

            elif state == "unknown":
                round_footer()
                consec_unk += 1
                log_warn("MAIN", f"unknown state (x{consec_unk}/{MAX_UNKNOWN_BEFORE_STOP})")
                if consec_unk >= MAX_UNKNOWN_BEFORE_STOP:
                    log_warn("MAIN", "HTML berubah. Balik ke menu.")
                    input(f"  {GRAY}Tekan ENTER...{RESET}")
                    clear()
                    break
                timer(10, "  retry ")

            elif state == "limit":
                round_footer()
                print()
                log_warn("MAIN", "─"*40)
                log_warn("MAIN", "DAILY LIMIT REACHED — STOP")
                log_warn("MAIN", f"Total claims: {YELLOW}{total_claims}{RESET}")
                log_warn("MAIN", "─"*40)
                input(f"\n  {GRAY}Tekan ENTER balik ke menu...{RESET}")
                clear()
                break

            elif state == "unauthed":
                round_footer()
                print()
                log_err("MAIN", "══════════════════════════════════════════")
                log_err("MAIN", "SESSION EXPIRED — UPDATE COOKIE DULU")
                log_err("MAIN", "══════════════════════════════════════════")
                print(f"  {GRAY}Langkah:{RESET}")
                print(f"  {GRAY}  1. Buka claimcoin.in di browser, login ulang{RESET}")
                print(f"  {GRAY}  2. F12 → Application → Cookies → https://claimcoin.in{RESET}")
                print(f"  {GRAY}  3. Copy semua cookies{RESET}")
                print(f"  {GRAY}  4. Pilih menu [2] Edit config, paste cookie baru{RESET}")
                input(f"\n  {GRAY}Tekan ENTER balik ke menu...{RESET}")
                clear()
                break

            elif state == "cf":
                round_footer()
                print()
                log_err("MAIN", "cf challenge — update cookie")
                time.sleep(3)
                break

            else:
                round_footer()
                consec_err += 1
                log_err("MAIN", f"error (x{consec_err}/{MAX_CONSEC_ERROR}), retry 15s")
                if consec_err >= MAX_CONSEC_ERROR:
                    log_warn("MAIN", "terlalu banyak error, balik ke menu")
                    consec_err = 0
                    break
                timer(15, "  retry ")

        clear()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {YELLOW}Interrupted. Bye.{RESET}\n")
        sys.exit(0)
