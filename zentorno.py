#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Zentorno MiniApp — Auto Task Completer (py3)
- Banner SOUU Engine box style
- Auto IP check
- Telethon session (login sekali)
- initData: paste-once-cache / bot_token (HMAC) / fallback
- Auto-reff via Telethon
- Auto-join channel + verify task
"""

import os, sys, json, time, random, binascii, hashlib, hmac, urllib.parse, re
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

try:
    import requests
except ImportError:
    print("[!] pip install requests")
    sys.exit(1)

try:
    from telethon.sync import TelegramClient
    from telethon.tl.functions.channels import JoinChannelRequest
    from telethon.tl.functions.messages import ImportChatInviteRequest
    from telethon.tl.functions.messages import StartBotRequest
    from telethon.errors import (
        UserAlreadyParticipantError, InviteHashExpiredError,
        ChannelPrivateError, FloodWaitError, UsernameNotOccupiedError
    )
    TELETHON_OK = True
except ImportError:
    TELETHON_OK = False

# ═══════════════════════════════════════════════════════════
BASE = "https://zentorno-gram-bot.ih0st.app"
TID  = 1006
VERIFY_PATH = f"/miniapp/cloudminer/task?tid={TID}"

REF_BOT  = "zentorno_gram_bot"
REF_CODE = "6894031790"

UA = ("Mozilla/5.0 (Linux; Android 16; K) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/152.0.7977.87 Mobile Safari/537.36 "
      "Telegram-Android/12.9.2 (Samsung SM-A556E; Android 16; SDK 36; HIGH)")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_PATH = os.path.join(SCRIPT_DIR, "zentorno_session")
CONFIG_FILE  = os.path.join(SCRIPT_DIR, "zentorno_config.json")

# ═══════════════════════════════════════════════════════════
#  RICH ANSI
# ═══════════════════════════════════════════════════════════
def fg(code): return f"\033[38;5;{code}m"
def bold(s): return f"\033[1m{s}\033[22m"
def dim(s):  return f"\033[2m{s}\033[22m"
RST = "\033[0m"

ANSI_RE = re.compile(r'\x1b\[[0-9;]*m')

def ansi_len(s):
    plain = ANSI_RE.sub('', s)
    width = 0
    for ch in plain:
        cp = ord(ch)
        if (0x1F300 <= cp <= 0x1F9FF or
            0x2600  <= cp <= 0x27BF  or
            0x2B00  <= cp <= 0x2BFF  or
            0x25A0  <= cp <= 0x25FF  or
            0x2580  <= cp <= 0x259F):
            width += 2
        else:
            width += 1
    return width

def ansi_pad(s, length):
    pad = length - ansi_len(s)
    return s + (" " * pad if pad > 0 else "")

def gradient(text, start=51, end=196):
    if len(text) <= 1:
        return f"{fg(start)}{text}{RST}"
    out = ""
    n = len(text)
    for i, ch in enumerate(text):
        t = i / (n - 1)
        c = int(round(start + (end - start) * t))
        out += f"{fg(c)}{ch}"
    return out + RST

def box_line(content):
    return f"{fg(51)}║  {RST}{ansi_pad(content, 60)}{fg(51)}║{RST}"

def box_div():
    return f"{fg(51)}╠{'═'*62}╣{RST}"

# ═══════════════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════════════
LOGS = []
ACC  = {"user": "?", "balance": "?", "stage": "INIT"}
NET  = {"ip": "?", "country": "?", "isp": "?"}

def push_log(msg, tag="i"):
    icons = {
        "i":  f"{fg(51)}●{RST}",
        "ok": f"{fg(46)}✔{RST}",
        "er": f"{fg(196)}✖{RST}",
        "wr": f"{fg(208)}◈{RST}",
        "in": f"{fg(213)}◉{RST}",
        "g":  f"{fg(226)}◆{RST}",
    }
    ts = time.strftime("%H:%M:%S")
    line = f"{dim('['+ts+']')} {icons.get(tag, '●')} {msg}"
    LOGS.append(line)
    if len(LOGS) > 5:
        LOGS.pop(0)

# ═══════════════════════════════════════════════════════════
#  IP
# ═══════════════════════════════════════════════════════════
def check_ip():
    if NET["ip"] != "?":
        return
    try:
        r = requests.get("http://ip-api.com/json", timeout=8)
        j = r.json()
        NET["ip"]      = j.get("query", "?")
        NET["country"] = f"{j.get('country','?')} / {j.get('city','?')}"
        NET["isp"]     = j.get("isp", "?")
    except Exception:
        NET["ip"] = "unknown"

# ═══════════════════════════════════════════════════════════
#  BANNER
# ═══════════════════════════════════════════════════════════
def display_banner(stage=None, extra=None):
    if stage:
        ACC["stage"] = stage
    if extra:
        ACC.update(extra)

    check_ip()
    os.system("clear" if os.name != "nt" else "cls")

    print(f"{fg(51)}╔{'═'*62}╗{RST}")
    print(box_line(gradient("ZENTORNO AUTO TASK", 51, 213)))
    print(box_line(dim("─────── SOUU ENGINE ───────")))
    print(box_div())

    print(box_line(f"{fg(213)}{bold('NETWORK')}{RST}"))
    print(box_line(f"{fg(51)}├─ IP         : {RST}{fg(226)}{NET['ip']}{RST}"))
    print(box_line(f"{fg(51)}├─ Country    : {RST}{fg(226)}{NET['country']}{RST}"))
    print(box_line(f"{fg(51)}└─ ISP        : {RST}{fg(226)}{NET['isp']}{RST}"))
    print(box_div())

    print(box_line(f"{fg(213)}{bold('SESSION')}{RST}"))
    print(box_line(f"{fg(51)}├─ Stage      : {RST}{fg(208)}{ACC['stage']}{RST}"))
    print(box_line(f"{fg(51)}├─ User       : {RST}{fg(226)}{ACC['user']}{RST}"))
    print(box_line(f"{fg(51)}└─ Balance    : {RST}{fg(46)}{ACC['balance']}{RST}"))
    print(box_div())

    print(box_line(f"{fg(213)}{bold('LIVE LOG')}{RST}"))
    for i in range(5):
        if i < len(LOGS):
            print(box_line(f"{fg(252)}{LOGS[i]}{RST}"))
        else:
            print(f"{fg(51)}║{' '*62}║{RST}")

    print(f"{fg(51)}╚{'═'*62}╝{RST}")
    print()
    print(f"   {gradient('BOT RUNNING', 46, 226)} {fg(250)}• {time.strftime('%H:%M:%S')}{RST}")
    print(f"   {dim('By Power ')}{fg(213)}@SouuXso{RST}{dim(' • ')}{fg(46)}Zentorno Edition{RST}")
    print()

def refresh_banner():
    display_banner()

# ═══════════════════════════════════════════════════════════
#  TIMER
# ═══════════════════════════════════════════════════════════
def timer(seconds):
    if not seconds or not isinstance(seconds, (int, float)):
        seconds = 5
    total = int(seconds)
    start = time.time()
    bar_len = 20

    while True:
        elapsed = int(time.time() - start)
        left = total - elapsed
        if left < 1:
            break

        pct = min(1, elapsed / max(1, total))
        fill = int(round(pct * bar_len))
        empty = bar_len - fill

        bar_full  = "█" * fill
        bar_empty = "░" * empty

        if left >= 3600:
            time_str = f"{left//3600}:{(left%3600)//60:02d} Jam"
        elif left >= 60:
            time_str = f"{left//60}:{left%60:02d} Menit"
        else:
            time_str = f"{left} Detik"

        pct_str = f"{int(round(pct*100)):>3}%"
        time_str = f"{time_str:>12}"

        line = (f"{fg(226)}LOADING{RST} "
                f"{fg(51)}[{RST}"
                f"{fg(46)}{bar_full}{RST}"
                f"{fg(240)}{bar_empty}{RST}"
                f"{fg(51)}] {RST}"
                f"{fg(250)}{pct_str}{RST} "
                f"{fg(208)}{time_str}{RST}")

        sys.stdout.write("\r" + line + " " * 20)
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write("\r" + " " * 90 + "\r")
    sys.stdout.flush()

# ═══════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════
def ask(prompt):
    try:
        return input(f"{RST}{prompt}").strip()
    except (EOFError, KeyboardInterrupt):
        print(); sys.exit(0)

def make_fp():
    return {
        "uid": binascii.hexlify(os.urandom(16)).decode(),
        "sw": 384, "sh": 832, "dpr": 2.8125,
        "cd": 24, "tz": "Asia/Jakarta", "tzo": -420,
        "lang": "id", "langs": "id,id-ID,en-US",
        "plat": "Linux aarch64", "hc": 8, "dm": 8, "tp": 5,
        "webgl": "Samsung Electronics Co., Ltd.|ANGLE ((Samsung Xclipse 530) on Vulkan 1.3.279)",
        "cv": "7S+uUQAAAAZJREFUAwCxiYdbdTPkbgAAAABJRU5ErkJggg==",
    }

def req(path, method="POST", data=None, timeout=30):
    url = BASE + path
    headers = {
        "User-Agent": UA,
        "Accept": "*/*",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "x-requested-with": "org.telegram.messenger.web",
        "Origin": BASE,
        "Referer": f"{BASE}/",
        "sec-ch-ua": '"Chromium";v="152", "Not?A_Brand";v="24", "Android WebView";v="152"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
    }
    if method == "POST":
        headers["Content-Type"] = "application/json"
    try:
        r = requests.request(method, url, data=data, headers=headers,
                             timeout=timeout, verify=False)
        return r.status_code, r.text
    except requests.RequestException as e:
        return 0, str(e)

# ═══════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        push_log(f"save config gagal: {e}", "wr")

# ═══════════════════════════════════════════════════════════
#  TELETHON SETUP
# ═══════════════════════════════════════════════════════════
def session_exists():
    return os.path.exists(SESSION_PATH + ".session")

def setup_telethon():
    if not TELETHON_OK:
        push_log("telethon belum install", "er")
        return None

    cfg = load_config()
    api_id   = cfg.get("api_id")
    api_hash = cfg.get("api_hash")
    phone    = cfg.get("phone")

    has_session = session_exists()

    if has_session:
        push_log("session ketemu", "ok")
        if not api_id or not api_hash:
            push_log("api_id/api_hash hilang", "er")
            push_log(f"rm {SESSION_PATH}.session buat login ulang", "wr")
            return None
        try:
            client = TelegramClient(SESSION_PATH, int(api_id), api_hash)
            client.connect()
            if not client.is_user_authorized():
                push_log("session unauthorized, login ulang", "wr")
                client.disconnect()
                return None
            me = client.get_me()
            push_log(f"login: @{me.username or me.id}", "ok")
            return client
        except Exception as e:
            push_log(f"connect gagal: {e}", "er")
            return None

    push_log("session kosong, setup awal", "wr")
    refresh_banner()
    print(f"{fg(208)}  Setup Telethon (sekali):{RST}")
    print(f"{fg(252)}  Ambil api_id/api_hash di https://my.telegram.org{RST}\n")

    if not api_id:
        api_id = ask(f"  {fg(226)}TG api_id   : {RST}")
    else:
        push_log(f"api_id dari config: {api_id}", "i")
    if not api_hash:
        api_hash = ask(f"  {fg(226)}TG api_hash : {RST}")
    if not phone:
        phone = ask(f"  {fg(226)}TG phone    : {RST}")

    if not (api_id and api_hash and phone):
        push_log("data login kurang", "er")
        return None

    try:
        client = TelegramClient(SESSION_PATH, int(api_id), api_hash)
        client.start(phone=phone)
        me = client.get_me()
        push_log(f"login ok: @{me.username or me.id}", "ok")

        save_config({"api_id": int(api_id), "api_hash": api_hash, "phone": phone})
        push_log("config tersimpan", "ok")
        return client
    except Exception as e:
        push_log(f"login gagal: {e}", "er")
        return None

# ═══════════════════════════════════════════════════════════
#  AUTO REFERRAL
# ═══════════════════════════════════════════════════════════
def auto_referral(client):
    if not client:
        return False

    push_log(f"auto-reff: {REF_BOT}?start={REF_CODE}", "in")
    try:
        client(StartBotRequest(
            bot=REF_BOT,
            peer=REF_BOT,
            start_param=REF_CODE,
        ))
        push_log("auto-reff: /start dikirim", "ok")
        return True
    except FloodWaitError as e:
        push_log(f"auto-reff: flood {e.seconds}s", "wr")
        return False
    except Exception as e:
        push_log(f"auto-reff: {type(e).__name__}: {str(e)[:60]}", "wr")
        return False

# ═══════════════════════════════════════════════════════════
#  INIT DATA — PASTE ONCE, CACHE 24H
# ═══════════════════════════════════════════════════════════
def is_initdata_valid(id_):
    """Basic validation — must contain user=, auth_date=, hash="""
    if not id_:
        return False
    return ("user=" in id_ and "hash=" in id_ and "auth_date=" in id_)

def get_init_data(client):
    """
    1. cache (<24 jam) → return
    2. prompt user: paste initData (from mini app devtools)
    """
    cfg = load_config()

    # 1. cache
    cache    = cfg.get("init_data_cache")
    cache_ts = cfg.get("init_data_ts", 0)
    age      = time.time() - cache_ts

    if cache and is_initdata_valid(cache) and age < 86400:
        hours_left = int((86400 - age) / 3600)
        push_log(f"initData dari cache ({hours_left}h tersisa)", "ok")
        return cache

    if cache and age >= 86400:
        push_log("cache expired, paste ulang", "wr")
    elif cache:
        push_log("cache invalid, paste ulang", "wr")

    # 2. prompt
    display_banner("INIT DATA")
    push_log("butuh initData — paste dari devtools", "wr")
    refresh_banner()
    print()

    print(f"{fg(208)}  Cara dapet initData:{RST}")
    print(f"{fg(252)}  1. Buka MiniApp Zentorno di HP via Telegram{RST}")
    print(f"{fg(252)}  2. Aktifkan remote debugging (chrome://inspect){RST}")
    print(f"{fg(252)}  3. Di console, ketik:{RST}")
    print(f"{fg(226)}     window.Telegram.WebApp.initData{RST}")
    print(f"{fg(252)}  4. Copy hasilnya (mulai dari 'query_id=' atau 'user=' sampai 'hash=...'){RST}")
    print(f"{fg(252)}  5. Paste di bawah (auto-cache 24 jam){RST}\n")

    init_data = ask(f"  {fg(226)}initData : {RST}").strip()

    if not is_initdata_valid(init_data):
        push_log("initData invalid (harus ada user=, auth_date=, hash=)", "er")
        return None

    cfg["init_data_cache"] = init_data
    cfg["init_data_ts"]    = time.time()
    save_config(cfg)
    push_log(f"initData cached (len={len(init_data)})", "ok")
    return init_data

# ═══════════════════════════════════════════════════════════
#  TELEGRAM JOIN
# ═══════════════════════════════════════════════════════════
def telethon_join(client, target_url):
    if not target_url:
        return False, "no target"
    url = target_url.strip()
    if "t.me/" in url and "_bot" in url:
        return False, "bot (skip)"

    username = None
    invite_hash = None

    if "t.me/" in url:
        path = url.split("t.me/", 1)[1].split("?")[0].split("/")[0]
        if path.startswith("+"):
            invite_hash = path[1:]
        else:
            username = path
    else:
        username = url.lstrip("@")

    try:
        if invite_hash:
            try:
                client(ImportChatInviteRequest(invite_hash))
                return True, "joined (invite)"
            except UserAlreadyParticipantError:
                return True, "already in"
            except InviteHashExpiredError:
                return False, "invite expired"
            except ChannelPrivateError:
                return False, "private"
        elif username:
            try:
                entity = client.get_entity(username)
                client(JoinChannelRequest(entity))
                return True, "joined"
            except UserAlreadyParticipantError:
                return True, "already in"
            except UsernameNotOccupiedError:
                return False, "not found"
            except ChannelPrivateError:
                return False, "private"
        return False, "unparseable"
    except FloodWaitError as e:
        return False, f"flood {e.seconds}s"
    except Exception as e:
        return False, f"{type(e).__name__}: {str(e)[:40]}"

# ═══════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════
def main():
    display_banner("INIT")

    if not TELETHON_OK:
        push_log("telethon belum install", "er")
        push_log("pip install telethon", "wr")
        refresh_banner()
        return 1

    # ─── Telethon login ───
    display_banner("AUTH")
    push_log("telethon setup...", "in")
    refresh_banner()

    tg_client = setup_telethon()
    if not tg_client:
        push_log("telethon gagal, exit", "er")
        refresh_banner()
        return 1

    me = tg_client.get_me()
    ACC["user"] = f"@{me.username or me.id}"
    push_log(f"user: {ACC['user']}", "ok")
    refresh_banner()

    # ─── Auto-reff ───
    display_banner("REFERRAL")
    push_log(f"auto-reff {REF_CODE}", "in")
    refresh_banner()

    ok = auto_referral(tg_client)
    if ok:
        push_log("referral terkirim", "g")
    else:
        push_log("referral gagal / udah pernah", "wr")
    refresh_banner()
    time.sleep(2)

    # ─── initData ───
    display_banner("INIT DATA")
    push_log("resolve initData...", "in")
    refresh_banner()

    init_data = get_init_data(tg_client)
    if not init_data:
        push_log("initData gagal", "er")
        refresh_banner()
        tg_client.disconnect()
        return 1

    push_log(f"initData len={len(init_data)}", "ok")
    refresh_banner()
    time.sleep(1)

    # ─── Auth API ───
    display_banner("AUTH API")
    push_log("auth ke server...", "in")
    refresh_banner()

    auth_body = json.dumps({"initData": init_data, "tid": TID, "fp": make_fp()})
    code, body = req(f"/miniapp/auth?tid={TID}", "POST", auth_body)
    try: auth = json.loads(body)
    except: auth = {}

    if not isinstance(auth, dict) or not auth.get("ok"):
        push_log(f"auth fail (HTTP {code})", "er")
        push_log(body[:80], "wr")
        refresh_banner()

        # invalid initData → clear cache
        if "invalid" in body.lower() or "unauthorized" in body.lower():
            cfg = load_config()
            cfg.pop("init_data_cache", None)
            cfg.pop("init_data_ts", None)
            save_config(cfg)
            push_log("cache dibersihin, run ulang", "wr")

        tg_client.disconnect()
        return 1

    user = auth.get("user", {})
    ACC["user"]    = f"@{user.get('username','?')}"
    ACC["balance"] = str(user.get("balance", 0))
    push_log(f"auth ok — id: {user.get('telegram_id','?')}", "ok")
    refresh_banner()

    # ─── Fetch state ───
    display_banner("STATE")
    push_log("fetch state...", "in")
    refresh_banner()

    state_body = json.dumps({"initData": init_data, "tid": TID})
    code, body = req(f"/miniapp/cloudminer/state?tid={TID}", "POST", state_body)
    try: state = json.loads(body)
    except: state = {}

    tasks = state.get("tasks", [])
    if not tasks:
        push_log("tasks kosong, coba config...", "wr")
        code, body = req(f"/miniapp/config?tid={TID}", "GET")
        try: config = json.loads(body)
        except: config = {}
        tasks = config.get("tasks", [])

    if not tasks:
        push_log("gak ada task", "er")
        refresh_banner()
        tg_client.disconnect()
        return 1

    available = [t for t in tasks if t.get("available")]
    push_log(f"tasks: {len(tasks)} total, {len(available)} available", "g")
    refresh_banner()

    if not available:
        push_log("gak ada task available", "wr")
        refresh_banner()
        tg_client.disconnect()
        return 0

    time.sleep(2)

    # ─── Loop ───
    done, fail, skipped = 0, 0, 0

    for t in available:
        tid_   = t.get("id", 0)
        kind   = t.get("kind", "?")
        title  = (t.get("title") or "?")[:40]
        target = t.get("target", "") or ""
        rwd    = t.get("reward", {}).get("ghs", 0)
        visit_sec = int(t.get("visitSeconds", 5))

        display_banner(f"TASK #{tid_}")
        push_log(f"#{tid_} [{kind}] {title} (+{rwd})", "in")
        refresh_banner()

        if kind == "channel" and tg_client:
            push_log(f"  join {target[:40]}", "in")
            refresh_banner()
            ok, msg = telethon_join(tg_client, target)
            if ok:
                push_log(f"  ✓ {msg}", "ok")
            else:
                push_log(f"  ✗ {msg}", "wr")
                refresh_banner()
                if "expired" in msg or "not found" in msg or "private" in msg:
                    skipped += 1
                    continue
            time.sleep(random.uniform(2, 4))

        elif kind == "visit":
            if visit_sec > 0:
                push_log(f"  tunggu {visit_sec}s...", "wr")
                refresh_banner()
                timer(visit_sec)

        elif kind == "bot":
            push_log("  bot task — skip", "wr")
            refresh_banner()

        else:
            time.sleep(random.uniform(2, 4))

        # Verify
        push_log("  verify...", "in")
        refresh_banner()

        verify_body = json.dumps({
            "taskId": tid_,
            "initData": init_data,
        }, separators=(",", ":"))

        vcode, vbody = req(VERIFY_PATH, "POST", verify_body)
        try:
            vj = json.loads(vbody)
        except:
            push_log(f"  HTTP {vcode} raw: {vbody[:60]}", "wr")
            fail += 1
            continue

        if isinstance(vj, dict) and vj.get("ok"):
            push_log(f"  ✓ verified", "ok")
            done += 1
        else:
            err = vj.get("error") or vj.get("message") or json.dumps(vj)[:80]
            push_log(f"  ✗ {err}", "er")
            if "not_verified" in str(err).lower() or "not joined" in str(err).lower():
                skipped += 1
            else:
                fail += 1

        refresh_banner()
        time.sleep(random.uniform(3, 5))

    # ─── Claim ───
    display_banner("CLAIM")
    push_log("claim mining reward...", "in")
    refresh_banner()

    claim_body = json.dumps({"initData": init_data, "tid": TID})
    ccode, cbody = req(f"/miniapp/claim?tid={TID}", "POST", claim_body)
    try: cj = json.loads(cbody)
    except: cj = {}

    if isinstance(cj, dict) and cj.get("ok"):
        push_log("claim ok", "ok")
    else:
        push_log(f"claim skip: {cbody[:60]}", "wr")

    # ─── Final state ───
    code, body = req(f"/miniapp/cloudminer/state?tid={TID}", "POST", state_body)
    try: final = json.loads(body)
    except: final = {}

    if isinstance(final, dict) and "user" in final:
        u = final["user"]
        ACC["balance"] = str(u.get("balance", 0))
        push_log(f"balance: {u.get('balance',0)}", "g")

    # ─── Summary ───
    display_banner("DONE")
    push_log(f"done={done} fail={fail} skip={skipped}", "g")
    refresh_banner()

    if tg_client:
        tg_client.disconnect()
    print(f"\n{fg(250)}  ~ done{RST}\n")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{fg(208)}  interrupted{RST}")
        sys.exit(130)
