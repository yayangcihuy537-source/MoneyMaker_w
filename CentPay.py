#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════════╗
║              ⚡ C E N T P A Y   A U T O   C L A I M ⚡           ║
║   🔥 SOUU ENGINE UI • NO CACHE • MANUAL PASTE                  ║
╚═══════════════════════════════════════════════════════════════════╝
"""

import requests, time, os, re
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
#  STATE
# ═══════════════════════════════════════════════════════════════════════════
state = {
    'mode':       'IDLE',
    'status':     'INIT',
    'success':    0,
    'failed':     0,
    'max_claim':  0,
    'total_usdt': 0.0,
    'last_usdt':  '0.00000',
    'cookie':     '',
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

def print_banner():
    elapsed = time.time() - state['start_time']

    out = []
    out.append(box_top())
    out.append(box_line(gradient("CENTPAY AUTO CLAIM")))
    out.append(box_line(f"{DIM}─────── SOUU ENGINE ───────{RESET}"))
    out.append(box_div())

    out.append(box_line(f"{MAGENTA}{BOLD}SESSION{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Mode       : {RESET}{YELLOW}{state['mode']}{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Status     : {RESET}{state_status_color()}{state['status']}{RESET}"))
    out.append(box_line(f"\033[38;5;51m└─ Progress   : {RESET}{YELLOW}{state['success']} / {state['max_claim']}{RESET}"))
    out.append(box_div())

    out.append(box_line(f"{MAGENTA}{BOLD}INCOME{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Total      : {RESET}{GREEN}+{state['total_usdt']:.5f} USDT{RESET}"))
    out.append(box_line(f"\033[38;5;51m└─ Last       : {RESET}{GREEN}+{state['last_usdt']} USDT{RESET}"))
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
    out.append(f"   {DIM}By Power {RESET}{MAGENTA}@SouuXso{RESET}{DIM} • {RESET}{GREEN}CentPay Edition{RESET}\n\n")

    clear()
    print(''.join(out), end='')

def state_status_color():
    s = state['status'].upper()
    if 'BERHASIL' in s or 'SUCCESS' in s or 'FINISH' in s:
        return GREEN
    if 'FAIL' in s or 'VAILED' in s or 'SALAH' in s or 'MATI' in s:
        return RED
    if 'WAIT' in s or 'COOLDOWN' in s:
        return ORANGE
    return YELLOW

# ═══════════════════════════════════════════════════════════════════════════
#  PARSERS
# ═══════════════════════════════════════════════════════════════════════════
def get_val(raw):
    raw = raw.strip()
    if "faas_session=" in raw:
        try: return raw.split("faas_session=")[1].split(";")[0].strip()
        except: return raw
    return raw.replace(";", "").strip()

def get_usdt(text):
    try:
        m = re.search(r'([0-9]+\.[0-9]+)\s*USDT', text, re.I)
        if m: return m.group(1)
        m = re.search(r'"reward":\s*"?([0-9.]+)', text)
        if m: return m.group(1)
        m = re.search(r'([0-9]+\.[0-9]+)', text)
        if m: return m.group(1)
    except: pass
    return "0.00000"

# ═══════════════════════════════════════════════════════════════════════════
#  SETUP MENU
# ═══════════════════════════════════════════════════════════════════════════
def setup_screen(cookie_preview=''):
    out = []
    out.append(box_top())
    out.append(box_line(gradient("CENTPAY AUTO CLAIM")))
    out.append(box_line(f"{DIM}─────── SOUU ENGINE ───────{RESET}"))
    out.append(box_div())
    out.append(box_line(f"{MAGENTA}{BOLD}SESSION{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Website    : {RESET}{YELLOW}https://centpay.online{RESET}"))
    out.append(box_line(f"\033[38;5;51m├─ Mode       : {RESET}{YELLOW}NO SAVE (manual paste){RESET}"))
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
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════
def main():
    # ── Input cookie ──
    setup_screen('')

    print(f"\n   {gradient('PASTE COOKIE BARU', 46, 226)}\n")
    print(f"  {CYAN}┌─[ {YELLOW}faas_session{CYAN} ]{RESET}")
    print(f"  {CYAN}└──> {RESET}", end='')
    raw = input().strip()
    cookie = get_val(raw)
    if not cookie:
        print(f"{RED}  ✖ Cookie kosong, exit.{RESET}")
        return

    state['cookie'] = cookie[:16] + '...' + cookie[-8:] if len(cookie) > 24 else cookie

    # ── Pilih mode ──
    setup_screen(state['cookie'])
    print(f"\n  {CYAN}PILIH > {RESET}", end='')
    pilih = input().strip()

    if pilih == "1":   max_claim = 10;      mode = '10x claim'
    elif pilih == "2": max_claim = 25;      mode = '25x claim'
    elif pilih == "3": max_claim = 50;      mode = '50x claim'
    elif pilih == "4": max_claim = 999999;  mode = 'Unlimited'
    else:              max_claim = 10;      mode = '10x claim'

    state['max_claim'] = max_claim
    state['mode']      = mode

    # ── Loop ──
    url = "https://centpay.online/claim"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://centpay.online/"}
    cookies = {"faas_session": cookie}

    push_log(f"mode: {mode} | max: {max_claim}", 'g')
    print_banner()

    while state['success'] < max_claim:
        try:
            r = requests.post(url, headers=headers, cookies=cookies, timeout=20)
            txt = r.text
            txt_low = txt.lower()

            if "success" in txt_low or "claimed" in txt_low or "reward" in txt_low or "has been" in txt_low:
                state['success'] += 1
                usdt = get_usdt(txt)
                try:
                    state['total_usdt'] += float(usdt)
                except: pass
                state['last_usdt'] = usdt
                state['status'] = f'BERHASIL #{state["success"]}'
                push_log(f"+{usdt} USDT | success: {state['success']}/{max_claim}", 'ok')
                print_banner()

                if state['success'] >= max_claim: break

                # Cooldown 60s
                for i in range(60, 0, -1):
                    state['status'] = f'COOLDOWN {i}s'
                    # Update cuma baris bawah biar gak full redraw
                    print(f"\r   {ORANGE}◈ cooldown {i}s → next {state['success']+1}/{max_claim}{RESET}    ", end='')
                    time.sleep(1)
                print()
            else:
                state['failed'] += 1
                is_login = "login" in txt_low
                state['status'] = 'COOKIE SALAH/MATI' if is_login else f'VAILED #{state["failed"]}'
                push_log(f"failed #{state['failed']}" + (" (cookie mati)" if is_login else ""), 'er')
                print_banner()

                if is_login:
                    push_log("cookie mati — paste ulang", 'er')
                    print_banner()
                    break

                for i in range(5, 0, -1):
                    state['status'] = f'RETRY {i}s'
                    print(f"\r   {YELLOW}◈ retry in {i}s{RESET}    ", end='')
                    time.sleep(1)
                print()
        except Exception as e:
            state['failed'] += 1
            state['status'] = 'ERROR'
            push_log(f"error: {str(e)[:50]}", 'er')
            print_banner()
            time.sleep(2)

    # ── Finish ──
    state['status'] = 'FINISH'
    push_log(f"selesai | sukses={state['success']} failed={state['failed']} total={state['total_usdt']:.5f} USDT", 'g')
    print_banner()
    print(f"\n   {gradient('SELESAI', 46, 226)} {WHITE}• sukses {state['success']} | failed {state['failed']}{RESET}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Dihentikan.{RESET}")
