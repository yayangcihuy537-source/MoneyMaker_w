#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║         ⚡ F R E E F L A R E C R Y P T O   A U T O   C L A I M ⚡║
║   🔥 SOUU ENGINE UI • NO CACHE • MANUAL PASTE COOKIE           ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import requests, time, os, re, json
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
#  COLOR
# ═══════════════════════════════════════════════════════════════════════════
RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[38;5;196m"
GREEN  = "\033[38;5;46m"
YELLOW = "\033[38;5;226m"
CYAN   = "\033[38;5;51m"
MAGENTA= "\033[38;5;213m"
BLUE   = "\033[38;5;39m"
WHITE  = "\033[38;5;250m"
GRAY   = "\033[38;5;245m"
ORANGE = "\033[38;5;208m"
PINK   = "\033[38;5;205m"

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')
def ansi_len(text): return len(ANSI_RE.sub('', text))

def clear():
    os.system("clear" if os.name != "nt" else "cls")

# ═══════════════════════════════════════════════════════════════════════════
#  SOUU BANNER HELPERS
# ═══════════════════════════════════════════════════════════════════════════
def gradient(text, start=51, end=213):
    if len(text) <= 1:
        return f"\033[38;5;{start}m{text}{RESET}"
    out = ''
    for i, ch in enumerate(text):
        t = i / (len(text) - 1)
        c = int(round(start + (end - start) * t))
        out += f"\033[38;5;{c}m{ch}"
    return out + RESET

def box_line(content, width=60):
    pad = width - ansi_len(content)
    if pad < 0: pad = 0
    return f"\033[38;5;51m║  {RESET}{content}{' ' * pad}\033[38;5;51m║{RESET}\n"

def box_div():
    return f"\033[38;5;51m╠{'═' * 62}╣{RESET}\n"

def box_top():
    return f"\033[38;5;51m╔{'═' * 62}╗{RESET}\n"

def box_bot():
    return f"\033[38;5;51m╚{'═' * 62}╝{RESET}\n"

# ═══════════════════════════════════════════════════════════════════════════
#  KONFIG (dari capture)
# ═══════════════════════════════════════════════════════════════════════════
BASE_URL       = "https://freeflarcrypto.com"
SESSION_URL    = f"{BASE_URL}/api/session"
CLAIM_URL      = f"{BASE_URL}/claim"

DEFAULT_INTERVAL = 1800  # 30 menit (dari capture)

# ═══════════════════════════════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════════════════════════════
state = {
    'mode':       'IDLE',
    'status':     'INIT',
    'success':    0,
    'failed':     0,
    'max_claim':  0,
    'total_reward': 0.0,
    'last_reward':  '0.000',
    'currency':   'DGB',
    'balance':    '0.00000000',
    'username':   'unknown',
    'cookie':     '',
    'interval':   DEFAULT_INTERVAL,
    'logs':       [],
    'start_time': time.time(),
}

MAX_LOGS = 6

def push_log(msg, tag='i'):
    icons = {'i': f'{CYAN}●{RESET}', 'ok': f'{GREEN}✔{RESET}', 'er': f'{RED}✖{RESET}',
             'wr': f'{ORANGE}◈{RESET}', 'in': f'{MAGENTA}⬢{RESET}', 'g': f'{YELLOW}◆{RESET}'}
    ts = datetime.now().strftime('%H:%M:%S')
    line = f"{GRAY}[{ts}]{RESET} {icons.get(tag, '●')} {msg}"
    state['logs'].append(line)
    if len(state['logs']) > MAX_LOGS:
        state['logs'].pop(0)

def fmt_uptime(s):
    s = int(s)
    return f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"

def state_status_color():
    s = state['status'].upper()
    if 'BERHASIL' in s or 'SUCCESS' in s or 'FINISH' in s:
        return GREEN
    if 'FAIL' in s or 'VAILED' in s or 'SALAH' in s or 'MATI' in s or 'ERROR' in s:
        return RED
    if 'WAIT' in s or 'COOLDOWN' in s:
        return ORANGE
    return YELLOW

# ═══════════════════════════════════════════════════════════════════════════
#  BANNER
# ═══════════════════════════════════════════════════════════════════════════
def print_banner():
    elapsed = time.time() - state['start_time']

    out = []
    out.append(box_top())
    out.append(box_line(gradient("FREEFLARE CRYPTO AUTO CLAIM")))
    out.append(box_line(f"{DIM}─────── SOUU ENGINE ───────{RESET}"))
    out.append(box_div())

    out.append(box_line(f"{MAGENTA}{BOLD}SESSION{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ User       : {RESET}{YELLOW}{state['username']}{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Mode       : {RESET}{YELLOW}{state['mode']}{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Status     : {RESET}{state_status_color()}{state['status']}{RESET}"))
    out.append(box_line(f"\033[38;5;51m└─ Progress   : {RESET}{YELLOW}{state['success']} / {state['max_claim']}{RESET}"))
    out.append(box_div())

    out.append(box_line(f"{MAGENTA}{BOLD}BALANCE{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Wallet     : {RESET}{GREEN}{state['balance']} {state['currency']}{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Total Earn : {RESET}{GREEN}+{state['total_reward']:.5f} {state['currency']}{RESET}"))
    out.append(box_line(f"\033[38;5;51m└─ Last Claim : {RESET}{GREEN}+{state['last_reward']} {state['currency']}{RESET}"))
    out.append(box_div())

    out.append(box_line(f"{MAGENTA}{BOLD}SYSTEM{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Success    : {RESET}{GREEN}{state['success']}{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Failed     : {RESET}{RED}{state['failed']}{RESET}"))
    out.append(box_line(f"\033[38;5;51m└─ Runtime    : {RESET}{YELLOW}{fmt_uptime(elapsed)}{RESET}"))
    out.append(box_div())

    for i in range(MAX_LOGS):
        if i < len(state['logs']):
            log_text = ANSI_RE.sub('', state['logs'][i])
            if len(log_text) > 58:
                log_text = log_text[:57] + "…"
            out.append(box_line(state['logs'][i]))
        else:
            out.append(f"\033[38;5;51m║{' ' * 62}║{RESET}\n")

    out.append(box_bot())
    out.append(f"\n   {gradient('BOT RUNNING', 46, 226)} {WHITE}• {datetime.now().strftime('%H:%M:%S')}{RESET}\n")
    out.append(f"   {DIM}By Power {RESET}{MAGENTA}@SouuXso{RESET}{DIM} • {RESET}{GREEN}FreeFlare Edition{RESET}\n\n")

    clear()
    print(''.join(out), end='')

# ═══════════════════════════════════════════════════════════════════════════
#  SETUP SCREEN
# ═══════════════════════════════════════════════════════════════════════════
def setup_screen(cookie_preview=''):
    out = []
    out.append(box_top())
    out.append(box_line(gradient("FREEFLARE CRYPTO AUTO CLAIM")))
    out.append(box_line(f"{DIM}─────── SOUU ENGINE ───────{RESET}"))
    out.append(box_div())
    out.append(box_line(f"{MAGENTA}{BOLD}SESSION{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Website    : {RESET}{YELLOW}https://freeflarcrypto.com{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Coin       : {RESET}{GREEN}DGB{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Cooldown   : {RESET}{YELLOW}30 menit / claim{RESET}"))
    out.append(box_line(f"\033[38;5;51m└─ Cookie     : {RESET}{GREEN}{cookie_preview or 'belum diisi'}{RESET}"))
    out.append(box_div())
    out.append(box_line(f"{MAGENTA}{BOLD}PILIH MODE CLAIM{RESET}"))
    out.append(box_line(f"  {CYAN}1.{RESET} {WHITE}10x claim{RESET}"))
    out.append(box_line(f"  {CYAN}2.{RESET} {WHITE}25x claim{RESET}"))
    out.append(box_line(f"  {CYAN}3.{RESET} {WHITE}50x claim{RESET}"))
    out.append(box_line(f"  {CYAN}4.{RESET} {ORANGE}Unlimited{RESET}"))
    out.append(box_bot())
    clear()
    print(''.join(out), end='')

# ═══════════════════════════════════════════════════════════════════════════
#  PARSERS
# ═══════════════════════════════════════════════════════════════════════════
def get_cookie(raw):
    """Extract faas_session dari input user."""
    raw = raw.strip()
    if "faas_session=" in raw:
        try:
            return raw.split("faas_session=")[1].split(";")[0].strip()
        except Exception:
            return raw
    return raw.replace(";", "").strip()

def parse_session_json(text):
    """Parse /api/session response."""
    try:
        j = json.loads(text)
        return {
            "balance":           j.get("balance", "0"),
            "currency":          j.get("balance_currency", "DGB"),
            "username":          j.get("name", "unknown"),
            "logged_in":         j.get("logged_in", False),
            "interval_seconds":  j.get("claim", {}).get("interval_seconds", DEFAULT_INTERVAL),
            "claim_amount":      j.get("claim", {}).get("amount", "0"),
        }
    except Exception:
        return None

def parse_claim_json(text):
    """Parse /claim response."""
    try:
        j = json.loads(text)
        return {
            "success":   j.get("success", False),
            "amount":    j.get("amount", "0"),
            "currency":  j.get("currency", "DGB"),
            "claim_id":  j.get("claim_id"),
            "payout_id": j.get("payout_id"),
            "raw":       j,
        }
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════════════════
#  API CALLS
# ═══════════════════════════════════════════════════════════════════════════
def build_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Mobile Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": f"{BASE_URL}/",
        "Origin": BASE_URL,
        "sec-fetch-site": "same-origin",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
    }

def build_cookies():
    return {"faas_session": state['cookie']}

def api_session():
    """GET /api/session — return dict atau None."""
    try:
        r = requests.get(
            SESSION_URL,
            headers=build_headers(),
            cookies=build_cookies(),
            timeout=20,
        )
        if r.status_code != 200:
            return None
        return parse_session_json(r.text)
    except Exception as e:
        push_log(f"session err: {str(e)[:40]}", 'er')
        return None

def api_claim():
    """POST /claim — return dict atau None."""
    try:
        r = requests.post(
            CLAIM_URL,
            headers={**build_headers(), "Content-Type": "application/x-www-form-urlencoded"},
            cookies=build_cookies(),
            timeout=20,
        )
        return {
            "status_code": r.status_code,
            "json": parse_claim_json(r.text),
            "text": r.text[:300],
        }
    except Exception as e:
        push_log(f"claim err: {str(e)[:40]}", 'er')
        return None

# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    # ── Input cookie ──
    setup_screen('')

    print(f"\n   {gradient('PASTE COOKIE', 46, 226)}\n")
    print(f"  {CYAN}┌─[ {YELLOW}faas_session{CYAN} ]{RESET}")
    print(f"  {CYAN}└──> {RESET}", end='')
    raw = input().strip()
    cookie = get_cookie(raw)
    if not cookie:
        print(f"{RED}  ✖ Cookie kosong, exit.{RESET}")
        return

    state['cookie'] = cookie
    cookie_preview = cookie[:16] + '...' + cookie[-8:] if len(cookie) > 24 else cookie

    # ── Pilih mode ──
    setup_screen(cookie_preview)
    print(f"\n  {CYAN}PILIH > {RESET}", end='')
    pilih = input().strip()

    if pilih == "1":   max_claim = 10;      mode = '10x claim'
    elif pilih == "2": max_claim = 25;      mode = '25x claim'
    elif pilih == "3": max_claim = 50;      mode = '50x claim'
    elif pilih == "4": max_claim = 999999;  mode = 'Unlimited'
    else:              max_claim = 10;      mode = '10x claim'

    state['max_claim'] = max_claim
    state['mode']      = mode
    state['status']    = 'CHECKING'

    push_log(f"mode: {mode} | max: {max_claim}", 'g')

    # ── Verify session awal ──
    print_banner()
    sess = api_session()

    if not sess or not sess.get("logged_in"):
        state['status'] = 'COOKIE SALAH/MATI'
        push_log("cookie invalid — cek faas_session", 'er')
        print_banner()
        print(f"\n   {RED}✖ Cookie tidak valid. Ambil ulang dari browser.{RESET}\n")
        return

    state['username'] = sess['username']
    state['balance']  = sess['balance']
    state['currency'] = sess['currency']
    state['interval'] = sess.get('interval_seconds', DEFAULT_INTERVAL)

    push_log(f"login OK — {sess['username']}", 'ok')
    push_log(f"balance: {sess['balance']} {sess['currency']}", 'i')
    push_log(f"cooldown: {state['interval']}s", 'i')
    print_banner()

    # ── Loop claim ──
    while state['success'] < max_claim:
        try:
            # Cek session dulu (biar tau balance fresh + eligible)
            sess = api_session()
            if sess and sess.get("logged_in"):
                state['balance']  = sess['balance']
                state['currency'] = sess['currency']
                if sess.get('interval_seconds'):
                    state['interval'] = sess['interval_seconds']

            # Attempt claim
            state['status'] = f'CLAIM #{state["success"]+1}'
            print_banner()

            res = api_claim()

            if res is None:
                state['failed'] += 1
                state['status'] = f'VAILED #{state["failed"]}'
                push_log(f"claim request failed", 'er')
                print_banner()
                for i in range(5, 0, -1):
                    print(f"\r   {YELLOW}◈ retry in {i}s{RESET}    ", end='')
                    time.sleep(1)
                print()
                continue

            sc = res["status_code"]
            jd = res["json"]

            # SUCCESS
            if sc == 200 and jd and jd.get("success"):
                amount    = jd.get("amount", "0")
                currency  = jd.get("currency", state['currency'])
                claim_id  = jd.get("claim_id", "-")
                payout_id = jd.get("payout_id", "-")

                state['success']      += 1
                state['last_reward']   = amount
                state['currency']      = currency
                try:
                    state['total_reward'] += float(amount)
                except Exception:
                    pass
                state['status'] = f'BERHASIL #{state["success"]}'

                push_log(f"+{amount} {currency} | id {claim_id}", 'ok')
                push_log(f"payout {payout_id}", 'i')
                print_banner()

                if state['success'] >= max_claim:
                    break

                # Cooldown
                interval = state['interval']
                push_log(f"cooldown {interval}s", 'wr')
                print_banner()

                for i in range(interval, 0, -1):
                    state['status'] = f'COOLDOWN {i}s'
                    print(f"\r   {ORANGE}◈ cooldown {i}s → next {state['success']+1}/{max_claim}{RESET}    ", end='')
                    time.sleep(1)
                print()

            # COOKIE MATI
            elif sc in (401, 403) or (jd is None and "login" in res['text'].lower()):
                state['status'] = 'COOKIE SALAH/MATI'
                push_log("cookie mati — paste ulang", 'er')
                print_banner()
                break

            # CLAIM BELUM BISA (cooldown server-side)
            elif sc == 429 or "cooldown" in res['text'].lower() or "too soon" in res['text'].lower():
                state['status'] = 'SERVER COOLDOWN'
                push_log(f"server masih cooldown", 'wr')
                print_banner()

                # Ambil ulang interval + tunggu
                sess = api_session()
                wait = state['interval']
                for i in range(wait, 0, -1):
                    state['status'] = f'WAIT {i}s'
                    print(f"\r   {ORANGE}◈ server cooldown {i}s{RESET}    ", end='')
                    time.sleep(1)
                print()

            # FAILED GENERIC
            else:
                state['failed'] += 1
                state['status'] = f'VAILED #{state["failed"]}'
                push_log(f"HTTP {sc} | {res['text'][:40]}", 'er')
                print_banner()

                for i in range(5, 0, -1):
                    state['status'] = f'RETRY {i}s'
                    print(f"\r   {YELLOW}◈ retry in {i}s{RESET}    ", end='')
                    time.sleep(1)
                print()

        except KeyboardInterrupt:
            raise
        except Exception as e:
            state['failed'] += 1
            state['status'] = 'ERROR'
            push_log(f"error: {str(e)[:50]}", 'er')
            print_banner()
            time.sleep(2)

    # ── Finish ──
    state['status'] = 'FINISH'
    push_log(f"selesai | sukses={state['success']} failed={state['failed']} total={state['total_reward']:.5f} {state['currency']}", 'g')
    print_banner()
    print(f"\n   {gradient('SELESAI', 46, 226)} {WHITE}• sukses {state['success']} | failed {state['failed']} | total +{state['total_reward']:.5f} {state['currency']}{RESET}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Dihentikan.{RESET}")
