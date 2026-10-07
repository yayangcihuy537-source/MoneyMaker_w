#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════
 NYXTAP.com Auto Claim Bot v4.7 (RATE LIMIT FIX)
 - FIX: rate-limit detect → langsung global backoff (5 menit default)
 - FIX: gak retry 7x lagi kalau kena "Too many attempts"
 - Emoji-match captcha solver via Pillow vision (LOCAL)
 - antibot_sig auto-extract dari HTML dump
═══════════════════════════════════════════════════════════════
"""

import base64
import io
import json
import os
import random
import re
import ssl
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime

import requests

# ═══════════════════════════════════════════════════════════════
#  PILLOW
# ═══════════════════════════════════════════════════════════════
HAS_PIL = False
PIL_ERR = None
try:
    from PIL import Image
    HAS_PIL = True
except ImportError as e:
    PIL_ERR = str(e)

# ═══════════════════════════════════════════════════════════════
#  DEBUG
# ═══════════════════════════════════════════════════════════════
DEBUG_MODE = False
DEBUG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_debug_nyxtap")

# ═══════════════════════════════════════════════════════════════
#  COLORS
# ═══════════════════════════════════════════════════════════════
RST  = "\033[0m"
BOLD = "\033[1m"
DIM  = "\033[2m"
RED  = "\033[38;5;196m"
GRN  = "\033[38;5;46m"
YEL  = "\033[38;5;226m"
CYN  = "\033[38;5;51m"
MAG  = "\033[38;5;201m"
ORG  = "\033[38;5;208m"
WHT  = "\033[38;5;15m"
GRY  = "\033[38;5;240m"
VIO  = "\033[38;5;141m"
NP   = "\033[38;5;201m"
NC   = "\033[38;5;51m"

# ═══════════════════════════════════════════════════════════════
#  CONST
# ═══════════════════════════════════════════════════════════════
UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/137.0.0.0 Mobile Safari/537.36")

NYX = "https://nyxtap.com"
PXC = "https://playnxc.com"
EMOJI_CDN = "https://cdn.jsdelivr.net/npm/emoji-datasource-google@14.0.0/img/google/64/{name}"
CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "nyxtap_emojis")

TG_GROUP = "t.me/+RInZ35ML2GhjM2I1"
TG_TAG   = "@MoneyMaker_w"

COINS = [
    "usdt", "eth", "usdc", "bnb", "sol", "xrp", "doge", "trx",
    "ltc", "bch", "dash", "pol", "xlm", "ada", "zec", "ton", "fey",
]

EMOJI_RE = re.compile(
    "["
    "\U0001F000-\U0001FAFF"
    "\U00002600-\U000027BF"
    "\U00002B00-\U00002BFF"
    "\U0000200D"
    "\U0000FE00-\U0000FE0F"
    "\U0001F1E6-\U0001F1FF"
    "]"
)

_CTX = ssl.create_default_context()

# ═══════════════════════════════════════════════════════════════
#  EXCEPTIONS
# ═══════════════════════════════════════════════════════════════
class RateLimitError(Exception):
    """Rate limit — bukan failure, cuma throttle. Trigger global backoff."""
    def __init__(self, msg, wait_sec=300):
        super().__init__(msg)
        self.wait_sec = wait_sec

# ═══════════════════════════════════════════════════════════════
#  ANTIBOT SIGNATURE
# ═══════════════════════════════════════════════════════════════
_SIG_SECRET_DEFAULT = "fcc29f0b0f826b4e"
_SIG_SECRET = _SIG_SECRET_DEFAULT

_FNV_PRIME  = 0x01000193
_FNV_SEED1  = 0x811C9DC5
_FNV_SEED2  = 0x050C5D1F

def _fnv1a_32(s: str, seed: int) -> int:
    h = seed & 0xFFFFFFFF
    for ch in s:
        h ^= ord(ch)
        h = (h * _FNV_PRIME) & 0xFFFFFFFF
    return h

def antibot_sig(nonce: str, flags: int = 3) -> str:
    payload = f"{_SIG_SECRET}|{nonce}|{flags}"
    h1 = _fnv1a_32(payload, _FNV_SEED1)
    h2 = _fnv1a_32(payload, _FNV_SEED2)
    return f"{h1:08x}{h2:08x}"

def extract_sig_secret_from_html(html: str):
    try:
        m = re.search(
            r'=\s*\[((?:\[\d+,\s*\d+,\s*\d+\]\s*,?\s*){16})\]',
            html
        )
        if not m:
            return None
        arr_text = "[" + m.group(1) + "]"
        try:
            arr = json.loads(arr_text)
        except Exception:
            pairs = re.findall(r'\[(\d+),\s*(\d+),\s*(\d+)\]', m.group(1))
            arr = [[int(a), int(b), int(c)] for a, b, c in pairs]
        if len(arr) != 16:
            return None
        chars = [''] * 16
        for item in arr:
            if len(item) != 3:
                continue
            idx, a, b = int(item[0]), int(item[1]), int(item[2])
            if 0 <= idx < 16:
                chars[idx] = chr(a ^ b)
        result = "".join(chars)
        if len(result) == 16 and re.match(r'^[0-9a-f]{16}$', result):
            return result
        return None
    except Exception:
        return None

# ═══════════════════════════════════════════════════════════════
#  DEBUG DUMP
# ═══════════════════════════════════════════════════════════════
def dump_file(label: str, content) -> str:
    if not DEBUG_MODE:
        return "(debug off)"
    try:
        os.makedirs(DEBUG_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if isinstance(content, (dict, list)):
            ext = "json"
            data = json.dumps(content, indent=2, ensure_ascii=False)
        elif isinstance(content, bytes):
            ext = "bin"
            data = content
        else:
            s = str(content)
            if s.lstrip().startswith("<!DOCTYPE") or s.lstrip().startswith("<html"):
                ext = "html"
            elif s.lstrip().startswith("{"):
                ext = "json"
            else:
                ext = "txt"
            data = s
        path = os.path.join(DEBUG_DIR, f"{ts}_{label}.{ext}")
        mode = "wb" if isinstance(data, bytes) else "w"
        kw = {} if isinstance(data, bytes) else {"encoding": "utf-8"}
        with open(path, mode, **kw) as f:
            f.write(data)
        return path
    except Exception as e:
        return f"(dump gagal: {e})"

# ═══════════════════════════════════════════════════════════════
#  STATE
# ═══════════════════════════════════════════════════════════════
STATE = {
    "user":          "Unknown",
    "email":         "-",
    "coins_mode":    "-",
    "claims":        0,
    "rewards":       0.0,
    "currency":      "USDT",
    "failures":      0,
    "max_failures":  6,
    "solve_attempt": 0,
    "max_solve":     10,
    "runtime_start": time.time(),
    "max_runtime":   3 * 3600,
    "logs":          [],
    "current_coin":  "-",
    "cooldowns":     {},
    "rate_limited_at": 0,   # timestamp terakhir kena rate limit
}

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

def cstrip(s):
    return ANSI_RE.sub("", str(s))

def slog(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    tags = {
        "OK":     GRN + "● OK    " + RST,
        "ERR":    RED + "● ERR   " + RST,
        "WARN":   YEL + "● WARN  " + RST,
        "INFO":   GRY + "● INFO  " + RST,
        "CLAIM":  MAG + "◉ CLAIM " + RST,
        "SOLVE":  CYN + "◉ SOLVER" + RST,
        "VERIFY": VIO + "◉ VERIFY" + RST,
        "CAP":    YEL + "◉ CAPTCHA" + RST,
        "WAIT":   ORG + "◉ WAIT  " + RST,
        "AUTH":   GRN + "● AUTH  " + RST,
        "LOGIN":  CYN + "◉ LOGIN " + RST,
        "CD":     ORG + "◉ COOLDN" + RST,
        "DEBUG":  GRY + "● DEBUG " + RST,
        "PIL":    MAG + "◉ PILLOW" + RST,
        "SIG":    CYN + "◉ SIG   " + RST,
        "RATE":   RED + "◉ RATE  " + RST,
    }
    tag = tags.get(level.upper(), tags["INFO"])
    STATE["logs"].append(GRY + f"[{ts}] " + RST + tag + " " + WHT + msg + RST)
    if len(STATE["logs"]) > 8:
        STATE["logs"].pop(0)

def fmt_dur(s):
    s = int(s)
    return f"{s // 3600:02d}:{(s % 3600) // 60:02d}:{s % 60:02d}"

# ═══════════════════════════════════════════════════════════════
#  PILLOW PREFLIGHT
# ═══════════════════════════════════════════════════════════════
def pillow_preflight(interactive=True):
    global HAS_PIL, PIL_ERR
    if HAS_PIL:
        return True
    print()
    print(RED + BOLD + "╔══════════════════════════════════════════════════════════╗" + RST)
    print(RED + BOLD + "║          ⚠  PILLOW BELUM TERINSTALL  ⚠                   ║" + RST)
    print(RED + BOLD + "╚══════════════════════════════════════════════════════════╝" + RST)
    print()
    print(CYN + "    pip install pillow" + RST)
    print()
    if PIL_ERR:
        print(GRY + f"  Detail: {PIL_ERR}" + RST)
    if not interactive:
        return False
    print(ORG + "  [1] " + RST + WHT + "Install otomatis" + RST)
    print(ORG + "  [2] " + RST + WHT + "Lanjut aja (random guess)" + RST)
    print(ORG + "  [0] " + RST + WHT + "Exit" + RST)
    try:
        pilih = input(GRY + "  >> " + RST).strip()
    except (EOFError, KeyboardInterrupt):
        return False
    if pilih == "1":
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pillow"],
                capture_output=True, text=True, timeout=180,
            )
            if result.returncode == 0:
                print(GRN + "  ✓ Pillow berhasil! Restart script." + RST)
                sys.exit(0)
        except Exception as e:
            print(RED + f"  ✗ {e}" + RST)
        input(GRY + "  ENTER untuk lanjut... " + RST)
        return False
    if pilih == "2":
        return True
    sys.exit(0)

# ═══════════════════════════════════════════════════════════════
#  RENDER
# ═══════════════════════════════════════════════════════════════
def render():
    W = 62
    bd = CYN
    def line(content):
        plain_len = len(cstrip(" " + content))
        pad = max(0, W - plain_len)
        return bd + "║" + RST + " " + content + " " * pad + bd + "║" + RST
    top = bd + "╔" + "═" * W + "╗" + RST
    mid = bd + "╠" + "═" * W + "╣" + RST
    bot = bd + "╚" + "═" * W + "╝" + RST
    print()
    print(top)
    print(line(BOLD + WHT + "NYXTAP AUTO CLAIM" + RST))
    print(line(DIM + "─────── SOUU ENGINE v4.7 ───────" + RST))
    print(mid)
    print(line(VIO + "CAPTCHA" + RST))
    print(line("├─ Type     : " + YEL + "EMOJI-MATCH (vision)" + RST))
    if HAS_PIL:
        print(line("├─ Solver   : " + GRN + "Pillow ✓" + RST + DIM + " (local)" + RST))
    else:
        print(line("├─ Solver   : " + RED + "Pillow ✗" + RST + DIM + " (random)" + RST))
    print(line("├─ Group    : " + NC + TG_GROUP + RST))
    if STATE["solve_attempt"] > 0:
        print(line("└─ Attempt  : " + YEL + f"{STATE['solve_attempt']}/{STATE['max_solve']}" + RST))
    else:
        print(line("└─ Attempt  : " + DIM + "-" + RST))
    print(mid)
    print(line(VIO + "ACCOUNT" + RST))
    print(line("├─ User     : " + CYN + STATE["user"] + RST))
    print(line("├─ Email    : " + WHT + STATE["email"] + RST))
    print(line("└─ Coin     : " + CYN + STATE["coins_mode"] + RST))
    print(mid)
    run = int(time.time() - STATE["runtime_start"])
    print(line(VIO + "SYSTEM" + RST))
    print(line("├─ Claims     : " + GRN + str(STATE["claims"]) + RST))
    print(line("├─ Rewards    : " + GRN + f"+{STATE['rewards']:.4f} {STATE['currency']}" + RST))
    print(line("├─ Failures   : " + RED + str(STATE["failures"]) + RST + " / " + str(STATE["max_failures"])))
    print(line("├─ Sig Secret : " + CYN + _SIG_SECRET + RST))
    print(line("└─ Runtime    : " + CYN + fmt_dur(run) + RST + " / " + DIM + fmt_dur(STATE["max_runtime"]) + RST))
    print(mid)
    logs = STATE["logs"]
    if not logs:
        print(line(DIM + "─ no activity yet ─" + RST))
    else:
        for l in logs:
            print(line(l))
    print(bot)
    now = datetime.now().strftime("%H:%M:%S")
    print()
    print("   " + GRN + BOLD + "BOT RUNNING" + RST + " " + DIM + "•" + RST + " " + CYN + now + RST)
    print("   " + DIM + "By Power " + NP + "@SouuXso" + RST + DIM + " • Nyxtap v4.7 | " + CYN + TG_TAG + RST)
    print()

def clear_render():
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")
    render()

def countdown_render(seconds_left, coins_cd, header="ALL COINS ON COOLDOWN"):
    W = 62
    bd = CYN
    def line(content):
        plain_len = len(cstrip(" " + content))
        pad = max(0, W - plain_len)
        return bd + "║" + RST + " " + content + " " * pad + bd + "║" + RST
    top = bd + "╔" + "═" * W + "╗" + RST
    mid = bd + "╠" + "═" * W + "╣" + RST
    bot = bd + "╚" + "═" * W + "╝" + RST
    print()
    print(top)
    print(line(BOLD + WHT + "NYXTAP AUTO CLAIM" + RST))
    print(line(DIM + "─────── SOUU ENGINE ───────" + RST))
    print(mid)
    print(line(ORG + BOLD + header + RST))
    print(line(""))
    mins = seconds_left // 60
    secs = seconds_left % 60
    big = f"{mins:02d}:{secs:02d}"
    inner = W - 2
    pad_l = (inner - len(big)) // 2
    pad_r = inner - len(big) - pad_l
    print(bd + "║" + RST + " " * pad_l + YEL + BOLD + big + RST + " " * pad_r + bd + "║" + RST)
    label = "next claim"
    pad_l = (inner - len(label)) // 2
    pad_r = inner - len(label) - pad_l
    print(bd + "║" + RST + " " * pad_l + DIM + label + RST + " " * pad_r + bd + "║" + RST)
    print(line(""))
    print(mid)
    for coin, cd in coins_cd:
        m = cd // 60
        s = cd % 60
        bar_len = 12
        filled = int(bar_len * (300 - cd) / 300) if cd <= 300 else bar_len
        filled = max(0, min(bar_len, filled))
        bar = GRN + "█" * filled + GRY + "░" * (bar_len - filled) + RST
        row = f"  {CYN}{coin.ljust(6)}{RST}  {bar}  {YEL}{m:02d}:{s:02d}{RST}"
        print(line(row))
    print(bot)
    now = datetime.now().strftime("%H:%M:%S")
    print()
    print("   " + ORG + BOLD + "BOT WAITING" + RST + " " + DIM + "•" + RST + " " + CYN + now + RST)
    print("   " + DIM + "By Power " + NP + "@SouuXso" + RST + DIM + " • Nyxtap v4.7 | " + CYN + TG_TAG + RST)
    print()

# ═══════════════════════════════════════════════════════════════
#  CONFIG
# ═══════════════════════════════════════════════════════════════
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nyxtap_config.json")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    try:
        with open(CONFIG_FILE, "r") as f:
            c = json.load(f)
        if not isinstance(c, dict) or not c.get("email"):
            return None
        c.pop("apikey", None)
        c.setdefault("max_tries", 10)
        return c
    except Exception:
        return None

def save_config(c):
    c.pop("apikey", None)
    with open(CONFIG_FILE, "w") as f:
        json.dump(c, f, indent=2)

def read_line(prompt=""):
    if prompt:
        sys.stdout.write(prompt)
        sys.stdout.flush()
    try:
        return input().strip()
    except (EOFError, KeyboardInterrupt):
        return ""

def setup():
    print()
    print(CYN + "═══ NYXTAP SETUP ═══" + RST)
    print()
    print(DIM + "Email buat terima reward. Solver captcha pake Pillow (lokal)." + RST)
    if not HAS_PIL:
        print(RED + "⚠ Pillow gak ke-detect." + RST)
    print()
    email = ""
    while "@" not in email:
        email = read_line(YEL + "FaucetPay Email : " + RST)
        if "@" not in email:
            print(RED + "  ✗ Email gak valid" + RST)
    print()
    return {"email": email, "max_tries": 10}

# ═══════════════════════════════════════════════════════════════
#  EMOJI SOLVER
# ═══════════════════════════════════════════════════════════════
_NOTO_TABLE = None

def _load_noto_table():
    NOTO_FONT = "/system/fonts/NotoColorEmoji.ttf"
    if not os.path.exists(NOTO_FONT):
        return None, None, None, None
    try:
        from fontTools.ttLib import TTFont
        font = TTFont(NOTO_FONT)
        cmap = font.getBestCmap()
        glyph_order = font.getGlyphOrder()
        cblc = font["CBLC"]
        strike = cblc.strikes[0]
        glyph_to_png = {}
        png_counter = 0
        for sub in strike.indexSubTables:
            names = getattr(sub, "names", None)
            first, last = sub.firstGlyphIndex, sub.lastGlyphIndex
            count = last - first + 1
            if names:
                for i in range(len(names)):
                    glyph_to_png[first + i] = png_counter
                    png_counter += 1
                png_counter += count - len(names)
            else:
                for i in range(count):
                    glyph_to_png[first + i] = png_counter
                    png_counter += 1
        with open(NOTO_FONT, "rb") as f:
            raw = f.read()
        pngs = []
        i = 0
        while i < len(raw) - 8:
            if raw[i:i+8] == b"\x89PNG\r\n\x1a\n":
                j = raw.find(b"IEND", i)
                if j >= 0:
                    pngs.append(raw[i:j+8])
                    i = j + 8
                    continue
            i += 1
        return cmap, glyph_order, glyph_to_png, pngs
    except Exception:
        return None, None, None, None

def _noto_table():
    global _NOTO_TABLE
    if _NOTO_TABLE is None:
        _NOTO_TABLE = _load_noto_table()
    return _NOTO_TABLE

def fetch_noto_emoji(cp):
    if not HAS_PIL:
        return None
    cmap, glyph_order, glyph_to_png, pngs = _noto_table()
    if cmap is None or cp not in cmap:
        return None
    gn = cmap[cp]
    gi = glyph_order.index(gn)
    pi = glyph_to_png.get(gi)
    if pi is None or pi >= len(pngs):
        return None
    try:
        im = Image.open(io.BytesIO(pngs[pi])).convert("RGBA")
        px = im.getpixel((0, 0))
        if px[3] == 255:
            bg = px[:3]
            data = im.tobytes()
            out = bytearray(len(data))
            for i in range(0, len(data), 4):
                r, g, b, a = data[i:i+4]
                if (r, g, b) == bg and a == 255:
                    out[i:i+4] = bytes([255, 255, 255, 0])
                else:
                    out[i:i+4] = bytes([r, g, b, a])
            im = Image.frombytes("RGBA", im.size, bytes(out))
        return im
    except Exception:
        return None

def emoji_filename(emoji):
    parts = []
    for ch in emoji:
        if ord(ch) in (0xFE0F, 0xFE0E):
            continue
        parts.append("%x" % ord(ch))
    return "%s.png" % "-".join(parts)

def extract_emoji(text):
    runs = []
    cur = []
    for ch in text:
        if EMOJI_RE.match(ch):
            cur.append(ch)
        else:
            if cur:
                runs.append("".join(cur))
                cur = []
    if cur:
        runs.append("".join(cur))
    if not runs:
        return None
    return max(runs, key=lambda r: (
        len(r),
        "\u200d" in r,
        any(ord(c) in (0xFE0F, 0xFE0E) for c in r),
    ))

def fetch_emoji_image(emoji):
    if not HAS_PIL:
        return None
    cp = 0
    for ch in emoji:
        o = ord(ch)
        if o > 0x2000:
            cp = o
            break
    img = fetch_noto_emoji(cp)
    if img is not None:
        return img
    os.makedirs(CACHE_DIR, exist_ok=True)
    name = emoji_filename(emoji)
    path = os.path.join(CACHE_DIR, name)
    if not os.path.exists(path):
        url = EMOJI_CDN.format(name=name)
        for _ in range(3):
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            try:
                with urllib.request.urlopen(req, timeout=20, context=_CTX) as r:
                    data = r.read()
                if data:
                    with open(path, "wb") as f:
                        f.write(data)
                    break
            except Exception:
                time.sleep(1)
        else:
            return None
    try:
        return Image.open(path).convert("RGBA")
    except Exception:
        return None

def glyph_data(im, size=64):
    im = im.convert("RGBA")
    if im.size != (size, size):
        im = im.resize((size, size), Image.LANCZOS)
    px = im.tobytes()
    mask = []
    colors = []
    for i in range(size * size):
        r, g, b, a = px[4*i:4*i+4]
        mx, mn = max(r, g, b), min(r, g, b)
        glyph = not (a < 40 or (mx > 232 and (mx-mn) < 40))
        mask.append(1 if glyph else 0)
        if glyph:
            colors.append((r, g, b))
    xs = [i % size for i, v in enumerate(mask) if v]
    ys = [i // size for i, v in enumerate(mask) if v]
    bbox = (min(xs), min(ys), max(xs), max(ys)) if xs else None
    return im, mask, colors, bbox

def norm_glyph_template(im, bbox, n=44):
    x0, y0, x1, y1 = bbox
    crop = im.crop((x0, y0, x1+1, y1+1)).convert("RGBA")
    crop = crop.resize((n, n), Image.LANCZOS)
    base = Image.new("RGB", (n, n), (255, 255, 255))
    base.paste(crop, (0, 0), crop)
    gray = bytearray(base.convert("L").tobytes())
    px = crop.tobytes()
    mask = bytearray(n * n)
    for i in range(n * n):
        r, g, b, a = px[4*i:4*i+4]
        mx, mn = max(r, g, b), min(r, g, b)
        if not (a < 40 or (mx > 232 and (mx-mn) < 40)):
            mask[i] = 1
    return mask, gray

def template_align(tm, tg, vm, vg, n=44, rng=6):
    best = 0.0
    for ay in range(-rng, rng+1):
        for ax in range(-rng, rng+1):
            inter = 0
            diff_sum = 0
            diff_cnt = 0
            tm_sum = 0
            vm_sum = 0
            for y in range(n):
                rv = y * n
                ty = y - ay
                if not (0 <= ty < n):
                    for x in range(n):
                        if vm[rv + x]:
                            vm_sum += 1
                    continue
                rt = ty * n
                for x in range(n):
                    tx = x - ax
                    v = vm[rv + x]
                    if v:
                        vm_sum += 1
                    if 0 <= tx < n:
                        tm_v = tm[rt + tx]
                        if tm_v:
                            tm_sum += 1
                        if v and tm_v:
                            inter += 1
                            diff_sum += abs(tg[rt + tx] - vg[rv + x])
                            diff_cnt += 1
                        elif v and not tm_v:
                            diff_sum += 255
                            diff_cnt += 1
            if tm_sum == 0 or vm_sum == 0:
                continue
            union = tm_sum + vm_sum - inter
            iou = inter / union if union else 0.0
            pixel_sim = 1.0 - (diff_sum / (diff_cnt * 255.0)) if diff_cnt else 0.0
            score = 0.6 * iou + 0.4 * pixel_sim
            if score > best:
                best = score
    return best

def color_hist(colors, bins=24):
    h = [0.0] * bins
    for r, g, b in colors:
        mx, mn = max(r, g, b), min(r, g, b)
        if mx == 0:
            continue
        sat = (mx - mn) / 255.0
        if sat < 0.15:
            continue
        delta = mx - mn
        if mx == r:
            hue = ((g - b) / delta) % 6
        elif mx == g:
            hue = (b - r) / delta + 2
        else:
            hue = (r - g) / delta + 4
        hh = int(hue / 6.0 * bins) % bins
        h[hh] += sat
    return h

def color_cos(a, b):
    na = sum(v*v for v in a) ** 0.5
    nb = sum(v*v for v in b) ** 0.5
    if not na or not nb:
        return 0.0
    return sum(x*y for x, y in zip(a, b)) / (na * nb)

def dump_captcha_images(challenge, target_im, scored, chosen):
    if not DEBUG_MODE or not HAS_PIL:
        return
    try:
        os.makedirs(DEBUG_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if target_im is not None:
            target_im.save(os.path.join(DEBUG_DIR, f"{ts}_target.png"))
        for t in challenge.get("tiles", []):
            try:
                b64 = t["image"].split(",", 1)[1]
                tim = Image.open(io.BytesIO(base64.b64decode(b64)))
                tim.save(os.path.join(DEBUG_DIR, f"{ts}_tile_{t['id']}.png"))
            except Exception:
                pass
        with open(os.path.join(DEBUG_DIR, f"{ts}_scores.txt"), "w") as f:
            f.write(f"chosen: {chosen}\n")
            for sc in scored:
                f.write(f"  #{sc[1]} total={sc[0]:.3f} shape={sc[2]:.3f} color={sc[3]:.3f}\n")
    except Exception:
        pass

# ═══════════════════════════════════════════════════════════════
#  RATE LIMIT DETECTION
# ═══════════════════════════════════════════════════════════════
_RATE_KEYWORDS = [
    "too many", "slow down", "rate limit", "too fast",
    "wait a while", "wait awhile", "try again later",
    "coba lagi", "terlalu cepat", "batas",
]

def is_rate_limit(msg: str) -> bool:
    m = (msg or "").lower()
    return any(k in m for k in _RATE_KEYWORDS)

def extract_wait_seconds(msg: str, default: int = 300) -> int:
    """Coba extract durasi dari message kayak 'wait 300 seconds'."""
    m = (msg or "").lower()
    # cari "wait N second/minute"
    mm = re.search(r'(\d+)\s*(s|sec|second|detik)', m)
    if mm:
        return max(30, int(mm.group(1)))
    mm = re.search(r'(\d+)\s*(m|min|minute|menit)', m)
    if mm:
        return max(60, int(mm.group(1)) * 60)
    return default

# ═══════════════════════════════════════════════════════════════
#  FAUCET CLAIMER
# ═══════════════════════════════════════════════════════════════
class FaucetClaimer:
    def __init__(self, email=None):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA})
        self.s.headers.update({"Accept": "*/*", "Accept-Language": "en-US,en;q=0.9"})
        self.email = email
        self.coin = None
        self.csrf = None
        self.sub_id = None
        self.return_url = None
        self.return_token = None
        self.last_prompt = ""
        self.captcha_html = ""

    def visit_faucet(self, coin):
        url = f"{NYX}/{coin}-faucet"
        slog(f"GET {url}", "INFO")
        for attempt in range(1, 5):
            try:
                r = self.s.get(url, allow_redirects=True, timeout=30)
                r.raise_for_status()
                break
            except requests.exceptions.RequestException as e:
                slog(f"retry {attempt}/4 — {str(e)[:40]}", "WARN")
                time.sleep(5)
        else:
            raise RuntimeError("faucet page gagal load")
        html = r.text
        if DEBUG_MODE:
            dump_file("faucet_page", html)
        m = re.search(r'var\s+csrf\s*=\s*"([0-9a-fA-F]+)"', html)
        self.csrf = m.group(1) if m else None
        if not self.csrf:
            raise RuntimeError("no csrf on faucet page")
        self.coin = coin
        return html

    def start_claim(self, delay=8):
        """
        v4.7: 
        - max 3 attempt (bukan 7)
        - rate-limit langsung raise RateLimitError, gak retry
        """
        body = {"csrf": self.csrf, "coin": self.coin, "website": ""}
        if self.email:
            body["email"] = self.email

        max_attempts = 3
        j = None
        for attempt in range(1, max_attempts + 1):
            slog(f"POST /api/claim ({attempt}/{max_attempts})", "INFO")
            try:
                r = self.s.post(f"{NYX}/api/claim", data=body, timeout=30)
                j = r.json()
            except (requests.exceptions.RequestException, ValueError) as e:
                slog(f"net error: {str(e)[:40]}", "ERR")
                if attempt < max_attempts:
                    time.sleep(8)
                    continue
                raise RuntimeError(f"net error: {e}")

            if not isinstance(j, dict):
                slog(f"resp bukan JSON: {str(j)[:40]}", "WARN")
                if attempt < max_attempts:
                    time.sleep(5)
                    continue
                raise RuntimeError("resp bukan JSON")

            if j.get("success"):
                break

            msg = j.get("message", "") or ""

            # ── RATE LIMIT: STOP, jangan retry ──
            if is_rate_limit(msg):
                wait_sec = extract_wait_seconds(msg, default=300)
                raise RateLimitError(msg[:80], wait_sec=wait_sec)

            # ── Other error ──
            slog(f"resp: {msg[:50]}", "WARN")
            if attempt < max_attempts:
                time.sleep(delay * attempt)
                continue
            raise RuntimeError(f"claim refused: {msg}")

        if not j or not j.get("success"):
            raise RuntimeError("claim refused (unknown)")

        d = j.get("data") or {}
        if DEBUG_MODE:
            dump_file("start_claim_resp", j)
        if d.get("redirect"):
            return j, d.get("solve_url"), (d.get("fields") or {})
        return j, None, d

    def enter_captcha(self, solve_url, fields):
        if fields and any(fields.values()):
            slog(f"POST captcha page", "INFO")
            r = self.s.post(solve_url, data=fields, allow_redirects=True)
        else:
            slog(f"GET captcha page", "INFO")
            r = self.s.get(solve_url, allow_redirects=True)
        html = r.text
        self.captcha_html = html
        if DEBUG_MODE:
            p = dump_file("captcha_page", html)
            slog(f"captcha dumped: {os.path.basename(p)}", "DEBUG")
        global _SIG_SECRET
        extracted = extract_sig_secret_from_html(html)
        if extracted:
            if extracted != _SIG_SECRET:
                slog(f"SECRET updated: {_SIG_SECRET} → {extracted}", "SIG")
                _SIG_SECRET = extracted
            else:
                slog(f"secret ok ({_SIG_SECRET[:8]}...)", "SIG")
        else:
            slog(f"secret extract gagal — pakai default", "WARN")
        m = re.search(r'var\s+CSRF\s*=\s*"([0-9a-fA-F]+)"', html)
        csrf = m.group(1) if m else None
        if not csrf:
            m = re.search(r'var\s+csrf\s*=\s*"([0-9a-fA-F]+)"', html)
            csrf = m.group(1) if m else None
        if not csrf:
            raise RuntimeError("no CSRF on captcha page")
        return csrf

    def load_challenge(self, csrf):
        r = self.s.post(f"{PXC}/api/captcha",
                        data={"action": "challenge", "csrf_token": csrf})
        try:
            j = r.json()
        except Exception:
            if DEBUG_MODE:
                dump_file("challenge_raw", r.text)
            raise RuntimeError("challenge bukan JSON")
        if DEBUG_MODE:
            dump_file("challenge_json", j)
        if not j.get("success"):
            raise RuntimeError(f"challenge failed: {j.get('message')}")
        return j["data"]["challenge"]

    def score_challenge(self, challenge, emoji, target_im):
        t_im, _, t_colors, t_bbox = glyph_data(target_im)
        if not t_bbox:
            return None
        t_norm_mask, t_gray = norm_glyph_template(t_im, t_bbox)
        t_hist = color_hist(t_colors)
        t_bytes = t_im.tobytes()
        scored = []
        exact = []
        for t in challenge.get("tiles", []):
            tid = t["id"]
            try:
                b64 = t["image"].split(",", 1)[1]
                tim = Image.open(io.BytesIO(base64.b64decode(b64)))
            except Exception:
                continue
            if tim.size == t_im.size and tim.tobytes() == t_bytes:
                exact.append(tid)
            _, _, colors, bbox = glyph_data(tim)
            if not bbox:
                scored.append((0.0, tid, 0.0, 0.0))
                continue
            v_norm_mask, v_gray = norm_glyph_template(tim, bbox)
            shape = template_align(t_norm_mask, t_gray, v_norm_mask, v_gray)
            csim = max(0.0, color_cos(t_hist, color_hist(colors)))
            total = 0.7 * shape + 0.3 * csim
            scored.append((total, tid, shape, csim))
        required = challenge.get("required", 1)
        if exact and len(exact) >= required:
            slog(f"EXACT match: {exact[:required]}", "CAP")
            for tid in exact[:required]:
                for i, s in enumerate(scored):
                    if s[1] == tid:
                        scored[i] = (1.0, s[1], 1.0, 1.0)
        scored.sort(key=lambda x: x[0], reverse=True)
        if scored:
            top3 = " | ".join(f"#{s[1]}={s[0]:.2f}" for s in scored[:3])
            slog(f"emoji={emoji} → top3 {top3}", "CAP")
        return scored

    def solve_challenge(self, challenge):
        required = challenge.get("required", 1)
        self.last_prompt = challenge.get("prompt", "")
        if DEBUG_MODE:
            dump_file("prompt_info", {
                "prompt": self.last_prompt,
                "prompt_repr": repr(self.last_prompt),
                "required": required,
                "tiles_count": len(challenge.get("tiles", [])),
                "tile_ids": [t.get("id") for t in challenge.get("tiles", [])],
                "nonce_k": challenge.get("k"),
            })
        target = None
        emoji = None
        if HAS_PIL:
            tgt = challenge.get("target")
            if isinstance(tgt, str) and tgt.startswith("data:image"):
                target = Image.open(io.BytesIO(base64.b64decode(tgt.split(",", 1)[1])))
                emoji = "(target image)"
            else:
                emoji = extract_emoji(self.last_prompt)
                if emoji:
                    target = fetch_emoji_image(emoji)
            if target is not None:
                scored = self.score_challenge(challenge, emoji or "", target)
                if scored:
                    chosen = [t[1] for t in scored[:required]]
                    dump_captcha_images(challenge, target, scored, chosen)
                    return chosen
        slog("no vision — guessing random", "WARN")
        ids = [t["id"] for t in challenge.get("tiles", [])]
        return random.sample(ids, min(required, len(ids)))

    def verify_captcha(self, csrf, challenge, chosen):
        clicks = []
        for tid in chosen:
            clicks.append(("antibot_order[]", tid))
            clicks.append(("antibot_click_ms[]", str(int(time.time() * 1000))))
        nonce = challenge.get("k", "")
        if not nonce:
            raise RuntimeError("no nonce (challenge.k)")
        sig = antibot_sig(nonce, flags=3)
        slog(f"sig={sig} nonce={nonce}", "SIG")
        body = (
            [("action", "verify"), ("csrf_token", csrf)]
            + clicks
            + [("antibot_sig", sig)]
        )
        if DEBUG_MODE:
            dump_file("verify_request", {
                "url": f"{PXC}/api/captcha",
                "csrf": csrf,
                "chosen": chosen,
                "nonce": nonce,
                "sig": sig,
                "flags": 3,
                "secret_used": _SIG_SECRET,
                "payload_str": "&".join(f"{k}={v}" for k, v in body),
            })
        r = self.s.post(f"{PXC}/api/captcha", data=body)
        if DEBUG_MODE:
            try:
                resp_j = r.json()
                dump_file("verify_response", {"status": r.status_code, "body": resp_j})
            except Exception:
                dump_file("verify_response_raw", r.text)
        try:
            j = r.json()
        except Exception:
            return None
        if j.get("success"):
            return j["data"]["redirect_url"]
        if j.get("errors") and j["errors"].get("locked"):
            raise RuntimeError("captcha locked")
        if j.get("message"):
            slog(f"verify resp: {j.get('message')[:45]}", "VERIFY")
        return None

    def confirm_and_claim(self):
        slog("POST /api/captcha-verify", "CLAIM")
        body = {
            "csrf": self.csrf,
            "sub_id": self.sub_id,
            "token": self.return_token,
            "status": "success",
        }
        r = self.s.post(f"{NYX}/api/captcha-verify", data=body)
        vj = r.json()
        if not vj.get("success"):
            raise RuntimeError(f"verify failed: {vj.get('message')}")
        if not vj["data"].get("verified"):
            time.sleep(2)
            return self.confirm_and_claim()
        slog("POST /api/captcha-claim", "CLAIM")
        r = self.s.post(f"{NYX}/api/captcha-claim", data=body)
        cj = r.json()
        if not cj.get("success"):
            raise RuntimeError(f"claim failed: {cj}")
        return cj

    def run(self, coin, max_tries=10):
        self.visit_faucet(coin)
        delay = random.randint(2, 4)
        slog(f"wait {delay}s human delay", "WAIT")
        time.sleep(delay)
        claim_j, solve_url, payload = self.start_claim()
        if not solve_url:
            return claim_j
        q = urllib.parse.urlparse(solve_url)
        qp = urllib.parse.parse_qs(q.query)
        fields = payload
        self.return_url = fields.get("return_url") or (qp.get("return_url") or [None])[0]
        self.sub_id = fields.get("sub_id") or (qp.get("sub_id") or [None])[0]
        if not self.sub_id:
            raise RuntimeError("no sub_id")
        csrf = self.enter_captcha(solve_url, fields)
        for attempt in range(1, max_tries + 1):
            STATE["solve_attempt"] = attempt
            slog(f"Solving ({attempt}/{max_tries})...", "SOLVE")
            clear_render()
            challenge = self.load_challenge(csrf)
            chosen = self.solve_challenge(challenge)
            redirect_url = self.verify_captcha(csrf, challenge, chosen)
            if redirect_url:
                m = re.search(r"[?&]token=([0-9a-fA-F]+)", redirect_url)
                if not m:
                    raise RuntimeError("no token in redirect_url")
                self.return_token = m.group(1)
                clear_render()
                return self.confirm_and_claim()
            slog(f"verify rejected (attempt {attempt})", "VERIFY")
            clear_render()
            time.sleep(1)
        raise RuntimeError(f"failed captcha in {max_tries} tries")

# ═══════════════════════════════════════════════════════════════
#  CLAIM WRAPPER
# ═══════════════════════════════════════════════════════════════
def claim_once(email, coin, max_tries):
    """
    Return: (status, result)
    status: True | False | "RATE_LIMIT"
    """
    claimer = FaucetClaimer(email=email)
    try:
        result = claimer.run(coin, max_tries=max_tries)
    except RateLimitError as e:
        # rate limit — bukan failure, jangan increment counter
        slog(f"RATE LIMIT: {str(e)[:50]} (wait {e.wait_sec}s)", "RATE")
        clear_render()
        return "RATE_LIMIT", e
    except (RuntimeError, requests.exceptions.RequestException) as e:
        STATE["failures"] += 1
        slog(f"{str(e)[:55]}", "ERR")
        clear_render()
        return False, None
    except Exception as e:
        STATE["failures"] += 1
        slog(f"unexpected: {str(e)[:45]}", "ERR")
        clear_render()
        return False, None

    if not isinstance(result, dict):
        STATE["failures"] += 1
        clear_render()
        return False, None
    d = result.get("data") if isinstance(result.get("data"), dict) else result
    coin_str = d.get("coin", coin) or coin
    amount   = d.get("coin_amount", "") or d.get("units", "") or "?"
    STATE["claims"] += 1
    STATE["failures"] = 0
    STATE["currency"] = str(coin_str).upper()
    try:
        STATE["rewards"] += float(str(amount).replace(",", "") or 0)
    except Exception:
        pass
    slog(f"CLAIMED +{amount} {str(coin_str).upper()}", "OK")
    clear_render()
    return True, result

# ═══════════════════════════════════════════════════════════════
#  COOLDOWN
# ═══════════════════════════════════════════════════════════════
def check_cooldown(coin):
    end = STATE["cooldowns"].get(coin.upper(), 0)
    left = end - time.time()
    return max(0, int(left))

def set_cooldown(coin, seconds):
    STATE["cooldowns"][coin.upper()] = time.time() + seconds

def set_all_cooldown(coins_list, seconds):
    for c in coins_list:
        set_cooldown(c, seconds)

def all_coins_cd(coins_list):
    for c in coins_list:
        if check_cooldown(c) <= 0:
            return False
    return True

def min_cooldown(coins_list):
    best = None
    for c in coins_list:
        cd = check_cooldown(c)
        if cd > 0:
            if best is None or cd < best:
                best = cd
    return best if best is not None else 0

# ═══════════════════════════════════════════════════════════════
#  RUNNER
# ═══════════════════════════════════════════════════════════════
def wait_all_cd(coins_list, header="ALL COINS ON COOLDOWN"):
    while all_coins_cd(coins_list):
        left = min_cooldown(coins_list)
        if left <= 0:
            break
        coins_cd = [(c.upper(), check_cooldown(c)) for c in coins_list]
        if os.name == "nt":
            os.system("cls")
        else:
            os.system("clear")
        countdown_render(left, coins_cd, header=header)
        time.sleep(1)

def run_claims(cfg, coins_list, mode_label):
    email = cfg.get("email", "")
    max_tries = int(cfg.get("max_tries", 10))
    if not email:
        print(RED + "email kosong. Edit config [3]" + RST)
        input("\n  ENTER...")
        return
    STATE["email"] = email
    STATE["coins_mode"] = mode_label
    STATE["claims"] = 0
    STATE["rewards"] = 0.0
    STATE["failures"] = 0
    STATE["runtime_start"] = time.time()
    STATE["logs"] = []
    STATE["cooldowns"] = {}
    STATE["solve_attempt"] = 0
    STATE["rate_limited_at"] = 0
    slog(f"Starting — {mode_label}", "AUTH")
    slog(f"Sig secret: {_SIG_SECRET}", "SIG")
    clear_render()
    round_n = 0
    try:
        while True:
            if (time.time() - STATE["runtime_start"]) >= STATE["max_runtime"]:
                slog("max runtime reached", "WARN")
                clear_render()
                break
            if STATE["failures"] >= STATE["max_failures"]:
                slog(f"max failures ({STATE['max_failures']})", "ERR")
                clear_render()
                break
            round_n += 1
            slog(f"Round #{round_n}", "INFO")
            clear_render()
            for c in coins_list:
                if (time.time() - STATE["runtime_start"]) >= STATE["max_runtime"]:
                    break
                if STATE["failures"] >= STATE["max_failures"]:
                    break
                cd = check_cooldown(c)
                if cd > 0:
                    STATE["current_coin"] = c.upper()
                    m = cd // 60
                    s = cd % 60
                    slog(f"{c.upper()} CD {m:02d}:{s:02d} — skip", "CD")
                    clear_render()
                    continue
                STATE["current_coin"] = c.upper()
                slog(f"Claim {c.upper()}", "INFO")
                clear_render()

                status, data = claim_once(email, c, max_tries)

                # ── RATE LIMIT: global backoff ──
                if status == "RATE_LIMIT":
                    wait_sec = getattr(data, "wait_sec", 300)
                    STATE["rate_limited_at"] = time.time()
                    slog(
                        f"Server rate-limit — semua coin CD {wait_sec}s",
                        "RATE"
                    )
                    clear_render()
                    set_all_cooldown(coins_list, wait_sec)
                    # Langsung tampilin countdown
                    wait_all_cd(coins_list, header="RATE LIMITED — COOLDOWN")
                    clear_render()
                    # Lanjut ke round berikutnya
                    break

                if status is True:
                    set_cooldown(c, 300)
                    if len(coins_list) > 1:
                        time.sleep(random.randint(3, 6))
                else:
                    set_cooldown(c, 60)

            if all_coins_cd(coins_list):
                left = min_cooldown(coins_list)
                m = left // 60
                s = left % 60
                slog(f"All CD — next claim in {m:02d}:{s:02d}", "WAIT")
                wait_all_cd(coins_list)
                clear_render()
            slog("Cycle done — sleep 3s", "WAIT")
            clear_render()
            for _ in range(3):
                time.sleep(1)
    except KeyboardInterrupt:
        slog("interrupted", "WARN")
        clear_render()
        time.sleep(1)
    clear_render()
    print()
    print("  " + CYN + "◉ Bot stopped." + RST)
    print("  " + DIM + f"Claims: {STATE['claims']}  |  Failures: {STATE['failures']}  |  Rewards: +{STATE['rewards']:.4f} {STATE['currency']}" + RST)
    print()

# ═══════════════════════════════════════════════════════════════
#  MENU
# ═══════════════════════════════════════════════════════════════
def show_menu(cfg):
    os.system("clear")
    W = 62
    def line(content):
        plain = len(cstrip(" " + content))
        pad = max(0, W - plain)
        return CYN + "║" + RST + " " + content + " " * pad + CYN + "║" + RST
    print()
    print(CYN + "╔" + "═" * W + "╗" + RST)
    title = BOLD + WHT + "NYXTAP AUTO CLAIM" + RST
    pad = (W - len(cstrip(title))) // 2
    print(CYN + "║" + RST + " " * pad + title + " " * (W - pad - len(cstrip(title))) + CYN + "║" + RST)
    sub = DIM + "─────── SOUU ENGINE v4.7 ───────" + RST
    pad = (W - len(cstrip(sub))) // 2
    print(CYN + "║" + RST + " " * pad + sub + " " * (W - pad - len(cstrip(sub))) + CYN + "║" + RST)
    print(CYN + "╠" + "═" * W + "╣" + RST)
    email_short = cfg.get("email", "?")
    if len(email_short) > 30:
        email_short = email_short[:16] + "..." + email_short[-10:]
    pil_str = (GRN + "✓ AKTIF" + RST) if HAS_PIL else (RED + "✗ TIDAK ADA" + RST)
    dbg_str = (GRN + "ON" + RST) if DEBUG_MODE else (DIM + "off" + RST)
    print(line("├─ Email    : " + CYN + email_short + RST))
    print(line("├─ Max tries: " + CYN + str(cfg.get("max_tries", 10)) + RST))
    print(line("├─ Pillow   : " + pil_str))
    print(line("├─ Sig Key  : " + CYN + _SIG_SECRET + RST))
    print(line("├─ Debug    : " + dbg_str))
    print(line("├─ Group    : " + NC + TG_GROUP + RST))
    print(line("└─ Credit   : " + NP + "@SouuXso" + RST + DIM + " / " + CYN + TG_TAG + RST))
    print(CYN + "╠" + "═" * W + "╣" + RST)
    print(line(ORG + "[1]" + RST + " Single coin"))
    print(line(ORG + "[2]" + RST + " All claim coins"))
    print(line(ORG + "[3]" + RST + " Edit config"))
    print(line(ORG + "[4]" + RST + " Reset config"))
    print(line(ORG + "[6]" + RST + " Toggle debug dump"))
    if not HAS_PIL:
        print(line(MAG + "[5]" + RST + " " + RED + "Install Pillow" + RST))
    print(line(GRY + "[0]" + RST + " Exit"))
    print(CYN + "╚" + "═" * W + "╝" + RST)
    print()
    try:
        return input("  " + GRY + ">> " + RST).strip()
    except (EOFError, KeyboardInterrupt):
        return "0"

def choose_coin():
    os.system("clear")
    print()
    print("  " + BOLD + WHT + "Pilih coin:" + RST)
    print()
    for i, c in enumerate(COINS, 1):
        print(f"    {CYN}[{i:2d}]{RST} {c.upper()}")
    print()
    inp = read_line("  " + GRY + "Nomor / kode [default USDT]: " + RST).lower()
    if not inp:
        return "usdt"
    if inp.isdigit():
        idx = int(inp) - 1
        if 0 <= idx < len(COINS):
            return COINS[idx]
        return "usdt"
    if inp in COINS:
        return inp
    return "usdt"

# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main():
    global DEBUG_MODE
    pillow_preflight(interactive=True)
    cfg = load_config()
    if cfg:
        os.system("clear")
        print()
        print("  " + GRN + "✓ Config found" + RST)
        print("  " + DIM + f"Email : {cfg['email']}" + RST)
        print("  " + DIM + f"Secret: " + CYN + _SIG_SECRET + RST)
        print()
        ans = read_line("  " + YEL + "Use saved? (y/n): " + RST).lower()
        if ans == "n":
            cfg = setup()
            save_config(cfg)
    else:
        cfg = setup()
        save_config(cfg)
    while True:
        choice = show_menu(cfg)
        if choice == "0":
            os.system("clear")
            print()
            print("  " + YEL + "Bye bos." + RST)
            print()
            return
        if choice == "5" and not HAS_PIL:
            pillow_preflight(interactive=True)
            continue
        if choice == "6":
            DEBUG_MODE = not DEBUG_MODE
            print()
            print("  " + (GRN + "✓ Debug ON" if DEBUG_MODE else YEL + "✓ Debug OFF") + RST)
            if DEBUG_MODE:
                print("  " + DIM + f"Dump folder: {DEBUG_DIR}" + RST)
            time.sleep(1.5)
            continue
        if choice == "3":
            try:
                os.remove(CONFIG_FILE)
            except FileNotFoundError:
                pass
            cfg = setup()
            save_config(cfg)
            continue
        if choice == "4":
            try:
                os.remove(CONFIG_FILE)
            except FileNotFoundError:
                pass
            print()
            print("  " + GRN + "✓ Config dihapus." + RST)
            time.sleep(1)
            cfg = setup()
            save_config(cfg)
            continue
        if choice == "1":
            coin = choose_coin()
            run_claims(cfg, [coin], f"SINGLE — {coin.upper()}")
            input("\n  Tekan ENTER untuk balik ke menu...")
            continue
        if choice == "2":
            run_claims(cfg, COINS[:], f"ALL — {len(COINS)} COINS")
            input("\n  Tekan ENTER untuk balik ke menu...")
            continue

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("  " + YEL + "Bye bos." + RST)
        print()
        sys.exit(0)
