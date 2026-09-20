import hashlib
from curl_cffi import requests
import json, time, re, sys, os, traceback, random
from datetime import datetime

HOST         = "https://pitasks.com"
WARYONO_IN   = "https://api.waryono.my.id/in.php"
WARYONO_RES  = "https://api.waryono.my.id/res.php"
CONFIG_FILE  = "config.json"

DEF_UA = ("Mozilla/5.0 (Linux; Android 16; 23076RN4BI) AppleWebKit/537.36 "
          "Chrome/134.0.6998.135 Mobile Safari/537.36")

BLK="\033[0;30m"; RED="\033[0;31m"; GRN="\033[0;32m"; YEL="\033[0;33m"
BLU="\033[0;34m"; MAG="\033[0;35m"; CYN="\033[0;36m"; WHT="\033[0;37m"
RST="\033[0m"; BOLD="\033[1m"

CLR = "\r\033[2K"

def clear():
    os.system('clear' if os.name == 'posix' else 'cls')

def mask_email(email):
    if '@' not in email: return email
    user, domain = email.split('@', 1)
    if len(user) <= 4: return user[:1] + "****@" + domain
    return user[:2] + "****" + user[-2:] + "@" + domain

def log(msg, tag="i", end="\n"):
    icons = {"i": f"{CYN}»{RST}", "ok": f"{GRN}✓{RST}", "er": f"{RED}✗{RST}",
             "wr": f"{YEL}⚠{RST}", "in": f"{BLU}●{RST}", "cf": f"{CYN}◇{RST}",
             "bi": f"{GRN}₹{RST}"}
    icon = icons.get(tag, f"{CYN}»{RST}")
    ts = datetime.now().strftime("%H:%M:%S")
    sys.stdout.write(CLR + f"{WHT}[{ts}]{RST} {icon} {msg}")
    if end:
        sys.stdout.write(end)
    sys.stdout.flush()

def tmr(seconds, label="Countdown"):
    symbols    = list(reversed(['🌑','🌒','🌓','🌔','🌕','🌖','🌗','🌘']))
    spinners   = ['⣾⣽','⣽⣻','⣻⢿','⢿⡿','⡿⣟','⣟⣯','⣯⣷','⣷⣾']
    spinners1  = ['▁⣾','▂⣽','▃⣻','▄⢿','▅⡿','▆⣟','▇⣯','█⣷','▇⣾','▆⣽','▅⣻','▄⢿','▃⡿','▂⣟','▁⣯']
    dots       = ['▪', '▪▪', '▪▪▪', '▪▪▪▪']

    total = int(seconds)
    if total < 1: return
    start = time.time()
    i = 0
    while True:
        elapsed = int(time.time() - start)
        remaining = max(0, total - elapsed)
        pct = round(((total - remaining) / total) * 100)
        mm, ss = divmod(remaining, 60)

        symbol = symbols[i % len(symbols)]
        sp     = spinners[i % len(spinners)]
        sp1    = spinners1[i % len(spinners1)]
        dot    = dots[elapsed % len(dots)]
        i += 1

        c1 = random.randint(1, 7)
        c2 = random.randint(1, 7)

        sys.stdout.write(
            f"{CLR} \033[1;3{c1}m {sp}\033[1;37m {label} "
            f"\033[1;31m{mm}:{ss:02d}\033[1;3{c2}m {symbol} {sp1}"
            f"\033[1;37m {pct}%\033[1;33m {dot}"
        )
        sys.stdout.flush()

        if remaining <= 0: break
        time.sleep(0.1)

    sys.stdout.write(CLR)
    sys.stdout.flush()

def load_session():
    return requests.Session(impersonate="chrome110")

def safe_request(sess, url, method='GET', data=None, headers=None):
    attempt = 0
    while True:
        attempt += 1
        try:
            opts = {"timeout": 45, "allow_redirects": True}
            if headers: opts["headers"] = headers
            if method == 'POST':
                r = sess.post(url, data=data, **opts)
            else:
                r = sess.get(url, **opts)
            return r.text
        except Exception as e:
            msg = str(e)
            sys.stdout.write(CLR + f"{YEL}⚠ [NET] gagal (#{attempt}): {msg[:60]}, retry 8s...{RST}")
            sys.stdout.flush()
            time.sleep(8)

# ═══════════════════════════════════════════════════════════
# TURNSTILE SOLVER — WARYONO FORMAT
# ═══════════════════════════════════════════════════════════
def solve_turnstile(apikey, sitekey, pageurl):
    symbols    = list(reversed(['🌑','🌒','🌓','🌔','🌕','🌖','🌗','🌘']))
    spinners   = ['⣾⣽','⣽⣻','⣻⢿','⢿⡿','⡿⣟','⣟⣯','⣯⣷','⣷⣾']
    spinners1  = ['▁⣾','▂⣽','▃⣻','▄⢿','▅⡿','▆⣟','⣇⣯','█⣷','▇⣾','▆⣽','▅⣻','▄⢿','▃⡿','▂⣟','▁⣯']
    dots       = ['▪', '▪▪', '▪▪▪', '▪▪▪▪']
    global_attempt = 0

    while True:
        global_attempt += 1
        log(f"Submit Turnstile (attempt #{global_attempt})...", "cf")

        # Submit via Waryono (JSON body)
        payload = {
            "apikey": apikey,
            "methods": "turnstile",
            "domain": pageurl,
            "sitekey": sitekey,
            "action": "login",
            "cdata": "",
        }

        try:
            r = requests.post(WARYONO_IN, json=payload,
                              impersonate="chrome110", timeout=30)
            body = r.text.strip()
        except Exception as e:
            log(f"submit error: {str(e)[:60]}", "er")
            time.sleep(5); continue

        # Response bisa JSON atau plain "OK|12345"
        task_id = None
        if body.startswith("{"):
            try:
                j = json.loads(body)
                if j.get("status") == 1:
                    task_id = j.get("request")
                else:
                    err = j.get("request", "")
                    if err in ("ERROR_WRONG_USER_KEY", "ERROR_KEY_DOES_NOT_EXIST",
                               "ERROR_ZERO_BALANCE", "ERROR_IP_NOT_ALLOWED"):
                        log(f"API error: {err}", "er")
                        time.sleep(30); continue
                    log(f"submit: {err}", "wr")
                    time.sleep(3); continue
            except Exception:
                time.sleep(3); continue
        elif body.startswith("OK|"):
            task_id = body[3:].strip()

        if not task_id:
            time.sleep(3); continue

        log(f"Task ID: {task_id}", "ok")

        # Poll
        poll_start = time.time()
        need_resubmit = False
        i = 0
        total = 180

        while True:
            elapsed = int(time.time() - poll_start)
            if elapsed > total:
                sys.stdout.write(CLR); sys.stdout.flush()
                need_resubmit = True; break

            remaining = max(0, total - elapsed)
            pct = round(((total - remaining) / total) * 100)
            mm, ss = divmod(elapsed, 60)

            symbol = symbols[i % len(symbols)]
            sp     = spinners[i % len(spinners)]
            sp1    = spinners1[i % len(spinners1)]
            dot    = dots[elapsed % len(dots)]
            i += 1

            c1 = random.randint(1, 7)
            c2 = random.randint(1, 7)

            sys.stdout.write(
                f"{CLR} \033[1;3{c1}m {sp}\033[1;37m Solving "
                f"\033[1;31m{mm}:{ss:02d}\033[1;3{c2}m {symbol} {sp1}"
                f"\033[1;37m {pct}%\033[1;33m {dot}"
            )
            sys.stdout.flush()
            time.sleep(0.5)

            # Poll every ~2.5s
            if (time.time() - poll_start) % 2.5 < 0.5:
                try:
                    pr = requests.get(
                        WARYONO_RES,
                        params={"apikey": apikey, "id": task_id, "action": "get", "json": 1},
                        impersonate="chrome110", timeout=30,
                    )
                    res_body = pr.text.strip()
                except Exception:
                    continue

                # OK|token
                if res_body.startswith("OK|"):
                    token = res_body[3:].strip()
                    sys.stdout.write(CLR); sys.stdout.flush()
                    log(f"Solved in {elapsed}s", "ok")
                    return token

                # JSON
                if res_body.startswith("{"):
                    try:
                        res = json.loads(res_body)
                    except Exception:
                        continue

                    if res.get("status") == 1:
                        token = res.get("request", "")
                        sys.stdout.write(CLR); sys.stdout.flush()
                        log(f"Solved in {elapsed}s", "ok")
                        return token

                    req = res.get("request", "")
                    if req == "CAPCHA_NOT_READY":
                        continue
                    if req.startswith("ERROR"):
                        sys.stdout.write(CLR); sys.stdout.flush()
                        log(f"Solver error: {req}", "er")
                        need_resubmit = True
                        break

        if need_resubmit:
            continue

def get_sitekey(html):
    m = re.search(r'data-sitekey="([^"]+)"', html) or re.search(r"data-sitekey='([^']+)'", html)
    return m.group(1) if m else None

def get_antibot(html):
    m = re.search(r'<div class="antibot-sequence">(.*?)</div>', html, re.S)
    if not m: return None
    seq = re.split(r'\s+', m.group(1).strip())
    seq = [s for s in seq if s and s not in ('→', '>') and '<' not in s]
    return ",".join(seq[:3]) if seq else None

def get_reward(html):
    m = re.search(r'<div class="alert alert-success">(.*?)</div>', html, re.S)
    if m: return re.sub(r'<[^>]+>', '', m.group(1)).strip()
    m = re.search(r'Claimed \$([\d.]+) successfully', html)
    if m: return f"Claimed ${m.group(1)} successfully!"
    return None

def get_balance(html):
    for pat in (r'<span class="value-style">([\d.]+)</span>',
                r'<div class="perf-value">([\d.]+)</div>',
                r'Available:\s*\$?([\d.]+)'):
        m = re.search(pat, html, re.I)
        if m: return m.group(1)
    return None

def get_cooldown(html):
    for pat in (r'let\s+remaining\s*=\s*(\d+)', r'var\s+wait\s*=\s*(\d+)',
                r'Please wait (\d+)\s*seconds?', r'wait\s+(\d+)\s*seconds'):
        m = re.search(pat, html, re.I)
        if m: return int(m.group(1))
    return None

def is_logged_in(html): return 'Logout' in html or 'Dashboard' in html
def is_locked(html):    return 'account has been locked' in html or '/locked' in html

def do_login(sess, apikey, email, password):
    masked = mask_email(email)
    log(f"Login: {masked}", "in")
    base_hdr = {"user-agent": DEF_UA,
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9"}

    tries = 0
    while True:
        tries += 1
        sitekey = None
        for _ in range(5):
            html = safe_request(sess, f"{HOST}/login", headers=base_hdr)
            if is_locked(html):
                log("AKUN DI-LOCK", "er"); return "LOCKED"
            sitekey = get_sitekey(html)
            if sitekey: break
            time.sleep(3)

        if not sitekey:
            time.sleep(5); continue

        token = solve_turnstile(apikey, sitekey, f"{HOST}/login")

        post_hdr = {
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": DEF_UA,
            "referer": f"{HOST}/login",
        }
        resp = safe_request(sess, f"{HOST}/login", method="POST", headers=post_hdr, data={
            "login_input": email, "password": password,
            "cf-turnstile-response": token,
        })

        if is_locked(resp):
            log("AKUN DI-LOCK", "er"); return "LOCKED"
        if is_logged_in(resp):
            log("Login berhasil!", "ok")
            return resp

        log(f"Login gagal (#{tries}), retry 5s...", "wr")
        time.sleep(5)

def print_success_banner(reward_text, new_bal, diff):
    line1 = f"✓ {reward_text}"
    if new_bal:
        if diff is not None and diff > 0:
            line2 = f"New Balance : ${new_bal}  (+${diff:.6f})"
        else:
            line2 = f"New Balance : ${new_bal}"
    else:
        line2 = None

    ansi = re.compile(r'\033\[[0-9;]*m')
    w1 = len(ansi.sub('', line1))
    w2 = len(ansi.sub('', line2)) if line2 else 0
    inner = max(w1, w2) + 2

    print(f"{GRN}  ╭{'─' * inner}╮{RST}")
    print(f"{GRN}  │{RST} {GRN}{BOLD}{line1}{RST}{' ' * (inner - w1 - 1)}{GRN}│{RST}")
    if line2:
        print(f"{GRN}  │{RST} {WHT}{line2}{RST}{' ' * (inner - w2 - 1)}{GRN}│{RST}")
    print(f"{GRN}  ╰{'─' * inner}╯{RST}")

def compute_diff(old_balance, new_bal):
    if old_balance and new_bal:
        try:
            return float(new_bal) - float(old_balance)
        except Exception:
            return None
    return None

def run_faucet(sess, apikey, old_balance=None):
    base_hdr = {"user-agent": DEF_UA,
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9"}
    outer = 0

    while True:
        outer += 1
        html = safe_request(sess, f"{HOST}/faucet", headers=base_hdr)

        if is_locked(html):
            log("AKUN DI-LOCK, stop", "er"); return "LOCKED"
        if not is_logged_in(html):
            return -1

        cd = get_cooldown(html)
        if cd and cd > 0:
            log(f"Cooldown {cd//60:02d}:{cd%60:02d}", "wr")
            tmr(cd, "Waiting")
            continue

        sitekey = get_sitekey(html)
        if not sitekey:
            log("Sitekey tidak ditemukan, retry 3s", "wr"); time.sleep(3); continue

        antibot = get_antibot(html)
        if not antibot:
            log("Antibot tidak ditemukan, retry 3s", "wr"); time.sleep(3); continue

        log(f"Antibot: {antibot}", "i")
        token = solve_turnstile(apikey, sitekey, f"{HOST}/faucet")

        post_hdr = {
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": DEF_UA,
            "referer": f"{HOST}/faucet",
            "origin": HOST,
        }
        resp = safe_request(sess, f"{HOST}/faucet", method="POST", headers=post_hdr, data={
            "adblock_status": "clean",
            "antibot_sequence": antibot,
            "cf-turnstile-response": token,
            "claim": "",
        })

        if is_locked(resp):
            log("AKUN DI-LOCK", "er"); return "LOCKED"

        reward = get_reward(resp)
        if reward:
            dash = safe_request(sess, f"{HOST}/dashboard", headers=base_hdr)
            new_bal = get_balance(dash)
            diff = compute_diff(old_balance, new_bal)
            print_success_banner(reward, new_bal, diff)
            return 605

        cd2 = get_cooldown(resp)
        if cd2 and cd2 > 0:
            dash = safe_request(sess, f"{HOST}/dashboard", headers=base_hdr)
            new_bal = get_balance(dash)
            diff = compute_diff(old_balance, new_bal)

            if diff is not None and diff > 0:
                print_success_banner("Claim success!", new_bal, diff)
            else:
                log(f"Cooldown {cd2//60:02d}:{cd2%60:02d}", "wr")
                tmr(cd2, "Waiting")
                continue

            return cd2

        clean = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', resp))
        log(f"✗ Gagal claim (#{outer}), retry 5s...", "er")
        log(f"Preview: {clean[:300]}", "wr")
        time.sleep(5)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        clear(); banner_main()
        print(f"{WHT}  ⚙  PiTasks Configuration Setup{RST}")
        print(f"{WHT}  ─────────────────────────────{RST}")
        print(f"{WHT}  Email    : {RST}", end=""); email = input().strip()
        print(f"{WHT}  Password : {RST}", end=""); password = input().strip()
        print(f"{WHT}  Waryono API Key : {RST}", end=""); apikey = input().strip()
        cfg = {"email": email, "password": password, "apikey": apikey}
        with open(CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=2)
        log("Config tersimpan", "ok"); time.sleep(1)
        return cfg

    with open(CONFIG_FILE) as f: cfg = json.load(f)
    cfg.setdefault("email", "")
    cfg.setdefault("password", "")
    cfg.setdefault("apikey", "")
    return cfg

def save_config(cfg):
    with open(CONFIG_FILE, "w") as f: json.dump(cfg, f, indent=2)

def banner_main():
    print(f"{WHT}═══════════════════════════════════════════════{RST}")
    print(f"{YEL}        BOT PITASKS.COM{RST}")
    print(f"{WHT}═══════════════════════════════════════════════{RST}")

def banner_account(email):
    print(f"{WHT}═══════════════════════════════════════════════{RST}")
    print(f"{WHT}Akun : {CYN}{mask_email(email)}{RST}")
    print(f"{WHT}───────────────────────────────────────────────{RST}")

def check_balance(cfg):
    try:
        sess = load_session()
    except Exception as e:
        print(f"{RED}Session error: {e}{RST}"); time.sleep(2); return
    hdr = {"user-agent": DEF_UA, "accept": "text/html,application/xhtml+xml,application/xml;q=0.9"}
    print(f"{WHT}[{mask_email(cfg['email'])}] {RST}", end="")
    try:
        dash = safe_request(sess, f"{HOST}/dashboard", headers=hdr)
    except Exception as e:
        print(f"{RED}ERROR: {e}{RST}"); return
    if is_locked(dash):
        print(f"{RED}LOCKED{RST}"); return
    if not is_logged_in(dash):
        print(f"{YEL}login...{RST}", end="")
        try:
            r = do_login(sess, cfg["apikey"], cfg["email"], cfg["password"])
        except Exception as e:
            print(f"{RED} {e}{RST}"); return
        if r == "LOCKED": return
        if not r: print(f"{RED} gagal.{RST}"); return
        dash = safe_request(sess, f"{HOST}/dashboard", headers=hdr)
    bal = get_balance(dash)
    print(f"{GRN}Balance: ${bal or '?'}{RST}")
    print(f"\n{WHT}Tekan Enter...{RST}", end=""); input()

def edit_config(cfg):
    clear(); banner_main()
    print(f"{WHT} EDIT CONFIG{RST}\n")
    print(f"{WHT}Email    [{mask_email(cfg['email'])}]: {RST}", end="")
    e = input().strip()
    if e: cfg["email"] = e
    print(f"{WHT}Password [****]      : {RST}", end="")
    p = input().strip()
    if p: cfg["password"] = p
    print(f"{WHT}API Key  [{cfg['apikey'][:8]}...]: {RST}", end="")
    a = input().strip()
    if a: cfg["apikey"] = a
    save_config(cfg)
    log("Config disimpan", "ok"); time.sleep(1)

def main():
    cfg = load_config()
    while True:
        clear(); banner_main()
        print(f"{WHT}Email: {GRN}{mask_email(cfg['email'])}{RST}")
        print(f"{WHT}───────────────────────────────────────────────{RST}")
        print(f"{CYN}[1]{WHT} Auto Claim Faucet{RST}")
        print(f"{CYN}[2]{WHT} Cek Balance{RST}")
        print(f"{CYN}[3]{YEL} Edit Config{RST}")
        print(f"{CYN}[0]{WHT} Keluar{RST}")
        print(f"{WHT}───────────────────────────────────────────────{RST}")
        print(f"{WHT}Pilih: {RST}", end=""); c = input().strip()
        if c == '0': print(f"{WHT}Bye!{RST}"); return
        elif c == '3': edit_config(cfg)
        elif c == '2': check_balance(cfg)
        elif c == '1':
            if not cfg["email"] or not cfg["password"] or not cfg["apikey"]:
                print(f"{RED}Config belum lengkap. Edit dulu (menu 3).{RST}")
                time.sleep(2); continue
            run_loop(cfg)

def run_loop(cfg):
    clear(); banner_main()
    print(f"{WHT}Start auto claim{RST}")
    print(f"{WHT}───────────────────────────────────────────────{RST}")

    while True:
        try:
            sess = load_session()
        except Exception as e:
            print(f"{RED}Session error: {e}{RST}"); time.sleep(5); continue

        hdr = {"user-agent": DEF_UA, "accept": "text/html,application/xhtml+xml,application/xml;q=0.9"}
        banner_account(cfg["email"])

        try:
            dash = safe_request(sess, f"{HOST}/dashboard", headers=hdr)
            if is_locked(dash):
                print(f"{RED}⛔ AKUN DI-LOCK, stop.{RST}"); return
            if not is_logged_in(dash):
                r = do_login(sess, cfg["apikey"], cfg["email"], cfg["password"])
                if r == "LOCKED": return
                if not r:
                    print(f"{RED}Login gagal, retry 30s.{RST}"); time.sleep(30); continue
                dash = safe_request(sess, f"{HOST}/dashboard", headers=hdr)
                if not is_logged_in(dash):
                    print(f"{RED}Sesi invalid, retry 30s.{RST}"); time.sleep(30); continue

            bal = get_balance(dash)
            if bal: log(f"Balance: ${bal}", "bi")

            result = run_faucet(sess, cfg["apikey"], old_balance=bal)

            if result == "LOCKED":
                print(f"{RED}⛔ LOCKED. Stop.{RST}"); return
            if result == -1:
                print(f"{RED}Session hilang, re-login...{RST}")
                r = do_login(sess, cfg["apikey"], cfg["email"], cfg["password"])
                if r == "LOCKED" or not r:
                    time.sleep(30); continue
                run_faucet(sess, cfg["apikey"], old_balance=None)

        except Exception as e:
            print(f"{RED}[ERROR] {e}{RST}")
            traceback.print_exc()
            time.sleep(5); continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{YEL}Dihentikan user.{RST}")
