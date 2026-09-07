#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import random
import re
import urllib.parse
import requests

# ========== WARNA ==========
RESET = '\033[0m'
MERAH = '\033[91m'
HIJAU = '\033[92m'
KUNING = '\033[93m'
BIRU = '\033[94m'
CYAN = '\033[96m'
PUTIH = '\033[97m'

# ========== KONFIGURASI ==========
BASE_URL = "https://btc.tonrevenue.space"
GIGA_URL = "https://ad.gigapub.tech/v1/ad"
GIGA_PROJ = "5736"
GIGA_TOKEN = "CEEUHXgZVL184wyaDp6laEchjHQ7RNN3"
UA_TG = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.7922.199 Mobile Safari/537.36 Telegram-Android/12.9.1 (Xiaomi M2006C3LG; Android 10; SDK 29; AVERAGE)"
CONFIG_FILE = "btcton_config.json"

# ========== UTILITY ==========
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def timer(seconds, prefix="[!] please wait"):
    """Countdown timer dengan spinner, non-blocking."""
    if seconds < 1:
        return
    frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    i = 0
    while seconds > 0:
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        time_str = f"{h:02d}:{m:02d}:{s:02d}"
        spinner = frames[i % len(frames)]
        sys.stdout.write(f"\r{PUTIH}{prefix} {HIJAU}{time_str} {PUTIH}{spinner}\033[K")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
        i += 1
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()

def fmt(n):
    if n is None:
        return "0"
    return f"{float(n):.8f}".rstrip('0').rstrip('.')

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"initData": ""}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_init_data():
    config = load_config()
    if config.get('initData'):
        return config['initData']
    print(f"{PUTIH}initData (TG) : {KUNING}", end="")
    init_data = input().strip()
    if init_data:
        config['initData'] = init_data
        save_config(config)
        print(f"{HIJAU}Konfigurasi disimpan ke {CONFIG_FILE}{RESET}")
        return init_data
    return None

def refresh_initdata():
    print(f"{PUTIH}initData baru: {KUNING}", end="")
    new = input().strip()
    if not new:
        return False
    config = load_config()
    config['initData'] = new
    save_config(config)
    return True

# ========== NETWORK ==========
def is_init_error(j):
    msg = str(j.get('detail', '')) + ' ' + str(j.get('message', ''))
    return 'InitData' in msg or 'session expired' in msg

def http_json(url, payload, headers, timeout=20):
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        return resp.json()
    except:
        return {"error": "connection_failed"}

def tg_headers(extra=None):
    headers = {
        'user-agent': UA_TG,
        'content-type': 'application/json',
        'x-requested-with': 'org.telegram.messenger.web',
        'origin': BASE_URL,
        'referer': BASE_URL + '/tasks',
        'sec-ch-ua': '"Not=A?Brand";v="99", "Android WebView";v="151", "Chromium";v="151"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'en,id-ID;q=0.9,id;q=0.8'
    }
    if extra:
        headers.update(extra)
    return headers

def api(path, extra=None):
    global init_data
    for attempt in range(2):
        payload = {"initData": init_data}
        if extra:
            payload.update(extra)
        r = http_json(BASE_URL + path, payload, tg_headers())
        if attempt == 0 and is_init_error(r):
            if refresh_initdata():
                continue
        return r
    return r

def giga_call(body):
    headers = tg_headers({
        'authorization': f'Bearer {GIGA_TOKEN}',
        'project-id': GIGA_PROJ
    })
    return http_json(GIGA_URL, body, headers)

def giga_user():
    parsed = urllib.parse.parse_qs(init_data)
    user_str = parsed.get('user', ['{}'])[0]
    try:
        user = json.loads(user_str)
    except:
        user = {}
    return {'user': user, 'platform': 'android', 'version': '9.6', 'start_param': None}

def get_state():
    r = api("/api/tasks/ads/state")
    return r.get('tasks', [])

def get_init():
    global init_data
    for attempt in range(2):
        payload = {
            "initData": init_data,
            "start_param": None,
            "fingerprint": "aabbccddeeff00112233445566778899",
            "ua": UA_TG,
            "screen": "412x915",
            "lang": "id",
            "tz": "Asia/Jakarta",
            "platform": "Linux armv81",
            "tg_platform": "android",
            "viewport_width": 412,
            "viewport_height": 891,
            "max_touch_points": 5,
            "device_pixel_ratio": 2.625
        }
        r = http_json(BASE_URL + "/api/init", payload, tg_headers())
        if attempt == 0 and is_init_error(r):
            if refresh_initdata():
                continue
        return r
    return r

def captcha_answer(ch):
    prompt = re.sub(r'[^a-zA-Z ]', '', ch.get('prompt', '')).strip().lower()
    want = None
    # coba cari kata setelah "the "
    m = re.search(r'the (\w+)', prompt)
    if m:
        want = m.group(1)
    else:
        # hapus "tap "
        want = re.sub(r'tap ', '', prompt).strip()
    for opt in ch.get('options', []):
        if opt.get('id', '').lower() == want or opt.get('label', '').lower() == want:
            return opt['id']
    return ''

def ensure_captcha():
    for _ in range(3):
        j = get_init()
        ch = j.get('user', {}).get('captcha_challenge')
        if not ch:
            return True
        ans = captcha_answer(ch)
        if not ans:
            print(f"{PUTIH}[CAPTCHA] {MERAH}jawaban gak ketemu untuk '{ch.get('prompt', '?')}'{RESET}")
            return False
        print(f"{PUTIH}[CAPTCHA] {KUNING}solve '{ch.get('prompt', '?')}' -> {ans}...{RESET}")
        r = api("/api/captcha/verify", {"challenge_id": ch['challenge_id'], "answer": ans})
        if r.get('status') == 'success':
            print(f"{PUTIH}[CAPTCHA] {HIJAU}OK{RESET}")
            return True
        print(f"{PUTIH}[CAPTCHA] {MERAH}{r.get('detail', r.get('message', 'gagal'))}{RESET}")
        time.sleep(2)
    return False

# ========== FARM ==========
def do_farm():
    notified_limit = {}
    max_cycles = 100  # safety, prevent infinite loop
    cycle = 0
    while cycle < max_cycles:
        cycle += 1
        tasks = get_state()
        if not tasks:
            print(f"{PUTIH}[STATE] {MERAH}kosong/gagal, coba captcha...{RESET}")
            ensure_captcha()
            tasks = get_state()
            if not tasks:
                timer(60, "  retry...")
                continue

        busy = 0
        tried_any = False
        claimed = False

        for t in tasks:
            prov = t.get('provider', '')
            if prov not in ['adexium', 'gigapubs']:
                continue
            rem = int(t.get('remaining_today', 0))
            cdl = int(t.get('cooldown_left', 0))
            cds = int(t.get('cooldown_seconds', 300))
            if rem <= 0:
                if prov not in notified_limit:
                    print(f"{PUTIH}[{CYAN}{prov}{PUTIH}] {KUNING}limit hari ini habis, skip{RESET}")
                    notified_limit[prov] = True
                continue
            if cdl > 0:
                busy = max(busy, cdl)
                continue

            tried_any = True
            st = api("/api/tasks/ads/start", {"provider": prov, "interaction": None})
            sid = st.get('session_uid', '')
            if not sid:
                print(f"{PUTIH}[{CYAN}{prov}{PUTIH}] {MERAH}{st.get('detail', st.get('message', 'start gagal'))}{RESET}")
                continue

            # Simulasi GigaPubs jika provider gigapubs
            if prov == 'gigapubs':
                tg = giga_user()
                giga_call({'method': 'init', 'args': {'user': tg}, 'version': 'v85', 'seconds': 9.9})
                uniq = f"{random.randint(100000000, 999999999)}.{random.randint(100000, 999999)}"
                any_data = {
                    'showDone': True,
                    'fallPriorityList': ['rich','rD','t','d','monetag','m1','o1','rB'],
                    'fallRotationType': 'priority',
                    'showCounter': 0,
                    'showTryCounter': 0,
                    'uniqShowId': uniq,
                    'readyNetsCount': 4,
                    'showTag': None
                }
                base = {'user': tg, 'placementId': 'main', 'transactionId': None, 'version': 'v85'}
                giga_call({'method': 'adShowTryStart', 'args': {**base, 'network': 't', 'rotationType': 'priority', 'showCounter': 0, 'anyData': any_data}})
                time.sleep(4)
                any2 = dict(any_data); any2['showDone'] = False; any2['showTryCounter'] = 1
                giga_call({'method': 'adShowed', 'args': {**base, 'network': 't', 'rotationType': 'priority', 'showCounter': 0, 'seconds': 18.7, 'anyData': any2}})
                any3 = dict(any_data); any3['showCounter'] = 1; any3['showTryCounter'] = 2
                giga_call({'method': 'adShowTryStart', 'args': {**base, 'network': 'd', 'rotationType': 'priority', 'showCounter': 1, 'anyData': any3}})
                time.sleep(4)
                any4 = dict(any3); any4['showDone'] = True
                giga_call({'method': 'adShowedX', 'args': {**base, 'network': 'd', 'rotationType': 'priority', 'showCounter': 2, 'seconds': 32.8, 'anyData': any4}})

            # Confirm
            cf = api("/api/tasks/ads/confirm", {"session_uid": sid})
            status = cf.get('status', '')
            if status in ['success', 'already_confirmed']:
                amt = cf.get('reward_sats', 0.2)
                nb = cf.get('new_balance', '?')
                used = int(cf.get('used_today', 0))
                rem2 = int(cf.get('remaining_today', rem))
                c = int(cf.get('cooldown', cds))
                print(f"{PUTIH}[{CYAN}{prov}{PUTIH}] +{HIJAU}{fmt(amt)}{PUTIH} sat - {BIRU}{used}/{used+rem2}{PUTIH} - balance {BIRU}{fmt(nb)}{PUTIH} sat{RESET}")
                busy = max(busy, c)
                claimed = True
                timer(random.randint(8, 10), "  wait...")
            elif status == 'pending_postback':
                print(f"{PUTIH}[{CYAN}{prov}{PUTIH}] {KUNING}pending postback{RESET}")
                busy = max(busy, cds)
            else:
                print(f"{PUTIH}[{CYAN}{prov}{PUTIH}] {MERAH}{cf.get('detail', cf.get('message', status or 'gagal'))}{RESET}")

        if busy > 0:
            timer(busy, "  next...")
            continue
        if not tried_any:
            print(f"{PUTIH}semua limit hari ini, exit...{RESET}")
            return
        if claimed:
            timer(5, "  wait...")
            continue
        timer(20, "  retry...")
    print(f"{PUTIH}Maksimal cycle tercapai, berhenti.{RESET}")

# ========== MAIN ==========
def main():
    global init_data
    clear()
    init_data = get_init_data()
    if not init_data:
        print(f"{MERAH}init_data tidak boleh kosong!{RESET}")
        sys.exit(1)

    while True:
        clear()
        print(f"{PUTIH}tonrevenue ad farm | Bypass ADS{RESET}\n")

        ensure_captcha()
        ib = get_init()
        if ib.get('user'):
            u = ib['user']
            acc = ib.get('access', {})
            print(f"{PUTIH}balance    : {BIRU}{fmt(u.get('balance', 0))}{PUTIH} sat{RESET}")
            if acc.get('mobile_only_blocked'):
                print(f"{PUTIH}status     : {MERAH}MOBILE ONLY BLOCKED{RESET}")
            elif u.get('is_blocked'):
                print(f"{PUTIH}status     : {MERAH}BLOCKED ({u.get('ban_reason', '?')}){RESET}")
            else:
                print(f"{PUTIH}status     : {HIJAU}clean{RESET}")
        else:
            print(f"{PUTIH}balance    : {MERAH}gagal fetch ({ib.get('detail', '?')}){RESET}")

        tasks = get_state()
        if tasks:
            for t in tasks:
                prov = t.get('provider', '')
                if prov not in ['adexium', 'gigapubs']:
                    continue
                used = int(t.get('daily_cap', 0)) - int(t.get('remaining_today', 0))
                print(f"{PUTIH}{prov:<10}: {BIRU}{used}/{t.get('daily_cap', '?')}{PUTIH} | reward {CYAN}{t.get('reward_sats', '?')}{PUTIH} sat | cooldown {CYAN}{t.get('cooldown_left', '?')}s{RESET}")
        else:
            print(f"{PUTIH}tasks      : {MERAH}gagal fetch state{RESET}")

        print("\n")
        print(f"{PUTIH}  1. {CYAN}Start Farm{RESET} (Adexium + GigaPubs)")
        print(f"{PUTIH}  0. {MERAH}Exit{RESET}")
        print(f"{PUTIH}pilih: {KUNING}", end="")
        opt = input().strip()
        if opt == '1':
            do_farm()
            print(f"\n{PUTIH}enter untuk kembali...{RESET}")
            input()
        elif opt == '0':
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{MERAH}Keluar.{RESET}")
        sys.exit(0)
