#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ART AIRDROP - ADS Bot (Final Version)
- Auto-login via Telethon + start_param referral
- Full GigaPub flow + Ads claim
- Random delay panjang (anti-deteksi)
- Max sleep 6-12 jam (pola natural)
- Multi-akun ready
"""

import asyncio
import requests
import json
import os
import sys
import time
import random
import urllib.parse
import re
from datetime import datetime
from telethon import TelegramClient, errors
from telethon.tl.functions.messages import RequestWebViewRequest

# ==================== KONFIGURASI ====================
API_ID = 28752231
API_HASH = 'ec1c1f2c30e2f1855c3edee7e348480b'
BOT_USERNAME = 'ART_AIRDROP_BOT'
SESSION_NAME = "art_ads_session"
BASE_URL = "https://art.tamimdev.dev"
WEBAPP_URL = "https://art.tamimdev.dev/"

# 🔥 REFERRAL — ID user yang mau dijadikan referrer
# Kosongkan ("") kalau tidak mau pakai referral
REFERRAL_ID = "6048943114"

# GigaPub
GIGA_ANALYTICS_URL = "https://ad.gigapub.tech/v1/ad"
GIGA_BIDNET_BASE   = "https://bid-net.gigapub.tech"
GIGA_PROJECT_ID    = "8198"
GIGA_PLACEMENT_ID  = "36785"
GIGA_BEARER_TOKEN  = "CEEUHXgZVL184wyaDp6laEchjHQ7RNN3"
GIGA_VERSION       = "v87"
GIGA_X_VERSION     = "v33"

# Simulasi nonton
WATCH_DURATION_SEC = 16
WATCH_TICK_SEC     = 5

# 🔥 RANDOM DELAY PANJANG (natural)
ADS_DELAY_MIN = 20
ADS_DELAY_MAX = 90
CYCLE_JITTER_MIN = 60
CYCLE_JITTER_MAX = 300

# 🔥 SMART SLEEP — MAX 6-12 JAM
MIN_SLEEP      = 600
MAX_SLEEP      = 43200
DEFAULT_SLEEP  = 10800
SLEEP_JITTER   = 1800

SLEEP_AFTER_ALL_DONE_MIN = 21600   # 6 jam
SLEEP_AFTER_ALL_DONE_MAX = 43200   # 12 jam

# ==================== WARNA ====================
RED    = "\033[38;5;196m"
YELLOW = "\033[1;93m"
GREEN  = "\033[1;92m"
CYAN   = "\033[1;96m"
DIM    = "\033[90m"
WHITE  = "\033[1;97m"
RESET  = "\033[0m"

# ==================== UTILITY ====================
def countdown_timer(seconds, message="⏳ Menunggu"):
    frames = ['⣾', '⣽', '⣻', '⢿', '⡿', '⣟', '⣯', '⣷']
    idx = 0
    while seconds > 0:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        t = f"{h:02d}:{m:02d}:{s:02d}" if h > 0 else f"{m:02d}:{s:02d}"
        sys.stdout.write(f"\r{YELLOW}{message}: {t}  {frames[idx]}{RESET}")
        sys.stdout.flush()
        time.sleep(1)
        seconds -= 1
        idx = (idx + 1) % len(frames)
    print(f"\r{YELLOW}{message}: selesai ✅{RESET}")

def fmt_duration(seconds):
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}j {m}m"
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"

def print_banner():
    print(f"""
{CYAN}{'='*60}
{YELLOW}           📺  ART ADS BOT
{CYAN}{'='*60}
{GREEN}🤖  Bot        : @ART_AIRDROP_BOT
{GREEN}👤  Session    : {SESSION_NAME}
{GREEN}📺  Ads Source : GigaPub RTB
{GREEN}🎯  Slot       : 10 / 24h
{GREEN}⏱️   Delay      : {ADS_DELAY_MIN}-{ADS_DELAY_MAX}s antar slot
{GREEN}💤  Sleep      : {SLEEP_AFTER_ALL_DONE_MIN//3600}-{SLEEP_AFTER_ALL_DONE_MAX//3600}h setelah selesai
{CYAN}{'='*60}{RESET}
""")

# ==================== INITDATA PARSER ====================
def parse_init_data(raw_url: str):
    init_data_raw = None

    if 'tgWebAppData=' in raw_url:
        try:
            init_data_raw = raw_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]
        except Exception:
            pass

    if not init_data_raw and '#' in raw_url and 'tgWebAppData=' in raw_url:
        try:
            frag = raw_url.split('#', 1)[1]
            init_data_raw = frag.split('tgWebAppData=')[1].split('&')[0]
        except Exception:
            pass

    if not init_data_raw:
        m = re.search(r'tgWebAppData=([^&#]+)', raw_url)
        if m:
            init_data_raw = m.group(1)

    if not init_data_raw:
        return None, None, None, None, None

    try:
        init_data = urllib.parse.unquote(init_data_raw)
    except Exception:
        init_data = init_data_raw

    user_obj = None
    for target in (init_data, init_data_raw):
        m = re.search(r'user=([^&]+)', target)
        if not m:
            continue
        raw_user = m.group(1)
        for parser in (
            lambda x: json.loads(urllib.parse.unquote(x)),
            lambda x: json.loads(x),
            lambda x: json.loads(urllib.parse.unquote(urllib.parse.unquote(x))),
        ):
            try:
                obj = parser(raw_user)
                if isinstance(obj, dict) and obj.get("id"):
                    user_obj = obj
                    break
            except Exception:
                continue
        if user_obj:
            break

    if not user_obj:
        try:
            parsed = urllib.parse.parse_qs(init_data)
            if 'user' in parsed:
                user_obj = json.loads(parsed['user'][0])
        except Exception:
            pass

    sig = None
    for target in (init_data, init_data_raw):
        m = re.search(r'signature=([^&]+)', target)
        if m:
            try:
                sig = urllib.parse.unquote(m.group(1))
            except Exception:
                sig = m.group(1)
            break

    auth_date = None
    m = re.search(r'auth_date=(\d+)', init_data)
    if m:
        auth_date = m.group(1)

    query_id = None
    m = re.search(r'query_id=([^&]+)', init_data)
    if m:
        try:
            query_id = urllib.parse.unquote(m.group(1))
        except Exception:
            query_id = m.group(1)

    return init_data, user_obj, sig, auth_date, query_id

# ==================== TELEGRAM ====================
async def get_telegram_initdata():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        print(f"{YELLOW}➤ Login Telegram required{RESET}")
        phone = input(f"{CYAN}📱 Phone (+code): {RESET}")
        await client.send_code_request(phone)
        otp = input(f"{CYAN}🔑 OTP Code: {RESET}")
        try:
            await client.sign_in(phone, otp)
        except errors.SessionPasswordNeededError:
            password = input(f"{RED}🔒 2FA Password: {RESET}")
            await client.sign_in(password=password)

    bot = await client.get_input_entity(BOT_USERNAME)

    webview = None
    if REFERRAL_ID:
        try:
            webview = await client(RequestWebViewRequest(
                peer=bot,
                bot=bot,
                platform='android',
                url=WEBAPP_URL,
                start_param=REFERRAL_ID,
            ))
        except TypeError:
            url_with_ref = f"{WEBAPP_URL}?ref={REFERRAL_ID}"
            webview = await client(RequestWebViewRequest(
                peer=bot, bot=bot, platform='android', url=url_with_ref
            ))
    else:
        webview = await client(RequestWebViewRequest(
            peer=bot, bot=bot, platform='android', url=WEBAPP_URL
        ))

    init_data, user_obj, sig, auth_date, query_id = parse_init_data(webview.url)
    await client.disconnect()

    if not init_data:
        print(f"{RED}❌ tgWebAppData tidak ditemukan{RESET}")
        return None, None, None, None, None

    if not user_obj:
        print(f"{RED}❌ Gagal parse user object{RESET}")
        return None, None, None, None, None

    return init_data, user_obj, sig, auth_date, query_id

# ==================== ADS BOT ====================
class AdsBot:
    def __init__(self, init_data, user_obj, sig, auth_date, query_id):
        self.init_data = init_data
        self.user_obj = user_obj or {}
        self.user_id = str(self.user_obj.get("id", ""))
        self.username = (self.user_obj.get("username")
                         or self.user_obj.get("first_name")
                         or "N/A")
        self.sig = sig or ""
        self.auth_date = auth_date or ""
        self.query_id = query_id or ""

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/151.0.7922.202 Mobile Safari/537.36 "
                          "Telegram-Android/12.9.1",
            "Accept": "*/*",
            "Content-Type": "application/json",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
            "X-Requested-With": "org.telegram.messenger.web",
            "x-telegram-init-data": init_data,
        })

        self.bidnet_headers = {
            "Content-Type": "application/json",
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/151.0.7922.202 Mobile Safari/537.36 "
                          "Telegram-Android/12.9.1",
            "x-requested-with": "org.telegram.messenger.web",
            "x-version": GIGA_X_VERSION,
            "project-id": GIGA_PROJECT_ID,
            "placement-id": GIGA_PLACEMENT_ID,
        }

        self.giga_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GIGA_BEARER_TOKEN}",
            "project-id": GIGA_PROJECT_ID,
            "Origin": BASE_URL,
            "Referer": f"{BASE_URL}/",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/151.0.7922.202 Mobile Safari/537.36 "
                          "Telegram-Android/12.9.1",
            "x-requested-with": "org.telegram.messenger.web",
        }

        user_json_min = json.dumps(self.user_obj, separators=(',', ':'), ensure_ascii=False)
        dcs = (f"auth_date={self.auth_date}\n"
               f"query_id={self.query_id}\n"
               f"user={user_json_min}")
        self.tg_proof = {"dcs": dcs, "sig": self.sig}

        self.user = None
        self.settings = None
        self.total_claimed = 0
        self.total_reward = 0
        self.cycle_count = 0
        self._last_error = None
        self.show_counter = 0
        self.uniq_show_id = None

    def log(self, msg, level="INFO"):
        t = datetime.now().strftime("%H:%M:%S")
        p = {"INFO": CYAN, "SUCCESS": GREEN, "WARNING": YELLOW,
             "ERROR": RED, "DIM": DIM}.get(level, WHITE)
        print(f"{p}[{t}] {msg}{RESET}")

    # ==================== ART API ====================
    def _req(self, method, endpoint, data=None):
        url = f"{BASE_URL}{endpoint}"
        try:
            if method == "GET":
                r = self.session.get(url, timeout=15)
            else:
                r = self.session.post(url, json=data, timeout=15)
            if r.status_code in (200, 304):
                try:
                    return r.json()
                except Exception:
                    return {"_raw": r.text}
            try:
                e = r.json()
                self._last_error = e.get("error") or e.get("message") or r.text[:120]
            except Exception:
                self._last_error = r.text[:120]
            return None
        except Exception as e:
            self._last_error = str(e)
            return None

    def get_user(self, with_ref: bool = False):
        endpoint = f"/api/user/{self.user_id}"
        if with_ref and REFERRAL_ID:
            endpoint += f"?referredBy={REFERRAL_ID}"

        data = self._req("GET", endpoint)
        if data and data.get("user"):
            self.user = data["user"]
            self.settings = data.get("settings", self.settings)
            return True
        return False

    def ads_status(self):
        return self._req("GET", f"/api/ads/status/{self.user_id}")

    def claim_ads_art(self):
        payload = {"userId": self.user_id}
        data = self._req("POST", "/api/ads/claim", payload)
        if data and data.get("success"):
            reward = data.get("reward", 0)
            if data.get("user"):
                self.user = data["user"]
            return True, reward, data
        return False, 0, None

    # ==================== GIGAPUB ====================
    def _giga_user_block(self):
        return {
            "user": self.user_obj,
            "platform": "android",
            "version": "9.6",
            "start_param": REFERRAL_ID if REFERRAL_ID else None
        }

    def giga_analytics(self, method, extra=None):
        body = {
            "method": method,
            "args": {
                "user": self._giga_user_block(),
                "version": GIGA_VERSION,
                **(extra or {})
            }
        }
        try:
            r = requests.post(GIGA_ANALYTICS_URL, json=body,
                              headers=self.giga_headers, timeout=10)
            return r.json() if r.text else {"_ok": True}
        except Exception:
            return None

    def bidnet_init(self):
        try:
            r = requests.post(f"{GIGA_BIDNET_BASE}/v1/init",
                              json={"projectId": int(GIGA_PROJECT_ID)},
                              headers=self.bidnet_headers, timeout=10)
            return r.json() if r.text else None
        except Exception:
            return None

    def bidnet_get_rtb(self):
        body = {"user": self._giga_user_block(), "tg_proof": self.tg_proof}
        try:
            r = requests.post(f"{GIGA_BIDNET_BASE}/v1/get-rtb",
                              json=body, headers=self.bidnet_headers, timeout=15)
            return r.json() if r.text else None
        except Exception:
            return None

    def bidnet_ad_event(self, transaction_id, passed_time_ms):
        body = {
            "data": {"passedTime": passed_time_ms, "stackId": None, "stackIndex": 0},
            "userData": self._giga_user_block(),
        }
        h = {**self.bidnet_headers, "transaction-id": str(transaction_id)}
        try:
            r = requests.post(f"{GIGA_BIDNET_BASE}/v1/ad-event",
                              json=body, headers=h, timeout=10)
            return r.json() if r.text else None
        except Exception:
            return None

    def bidnet_ad_showed(self, transaction_id, passed_time_ms):
        body = {
            "data": {"passedTime": passed_time_ms, "stackId": None, "stackIndex": 0},
            "userData": self._giga_user_block(),
        }
        h = {**self.bidnet_headers, "transaction-id": str(transaction_id)}
        try:
            r = requests.post(f"{GIGA_BIDNET_BASE}/v1/ad-showed",
                              json=body, headers=h, timeout=10)
            return r.json() if r.text else None
        except Exception:
            return None

    def watch_one_ad(self, slot_index):
        self.show_counter += 1
        self.uniq_show_id = f"{int(time.time()*1000)}.{random.randint(0, 999999)}"
        fall_list = ["rich", "mc", "rD", "monetag", "rB"]

        self.giga_analytics("adShowTryStart", {
            "placementId": "main",
            "network": "b",
            "rotationType": "chanceOrder",
            "showCounter": slot_index - 1,
            "transactionId": None,
            "anyData": {
                "fallPriorityList": fall_list,
                "fallRotationType": "chanceOrder",
                "showCounter": slot_index - 1,
                "showTryCounter": slot_index,
                "uniqShowId": self.uniq_show_id,
                "readyNetsCount": 6,
                "showTag": None,
            }
        })
        time.sleep(0.3)

        rtb = self.bidnet_get_rtb()
        if not rtb or not rtb.get("ads"):
            return False, None, "no_rtb"

        ad = rtb["ads"][0]
        tid = ad.get("tId")
        if not tid:
            return False, None, "no_tid"

        start_ts = time.time()
        ticks = max(1, WATCH_DURATION_SEC // WATCH_TICK_SEC)
        for i in range(ticks):
            time.sleep(WATCH_TICK_SEC)
            passed = int((time.time() - start_ts) * 1000)
            self.bidnet_ad_event(tid, passed)

        final_ms = int((time.time() - start_ts) * 1000)
        self.bidnet_ad_showed(tid, final_ms)

        self.giga_analytics("adShowed", {
            "placementId": "main",
            "network": "b",
            "rotationType": "bid",
            "showCounter": slot_index,
            "transactionId": None,
            "seconds": final_ms / 1000.0,
            "anyData": {
                "showDone": False,
                "fallPriorityList": fall_list,
                "fallRotationType": "chanceOrder",
                "showCounter": slot_index - 1,
                "showTryCounter": slot_index + 1,
                "uniqShowId": self.uniq_show_id,
                "readyNetsCount": 6,
                "showTag": None,
            }
        })
        time.sleep(0.2)
        self.giga_analytics("adShowedX", {
            "placementId": "main",
            "network": "b",
            "rotationType": "chanceOrder",
            "showCounter": slot_index + 1,
            "transactionId": None,
            "seconds": final_ms / 1000.0,
            "anyData": {
                "showDone": True,
                "fallPriorityList": fall_list,
                "fallRotationType": "chanceOrder",
                "showCounter": slot_index,
                "showTryCounter": slot_index + 2,
                "uniqShowId": self.uniq_show_id,
                "readyNetsCount": 6,
                "showTag": None,
            }
        })

        return True, tid, "ok"

    # ==================== ADS CYCLE ====================
    def run_ads_cycle(self):
        self.log("📺 Cek status ads...", "INFO")
        status = self.ads_status()

        if not status:
            self.log(f"⚠️  Gagal ambil status: {str(self._last_error)[:50]}", "WARNING")
            return 0, 0, DEFAULT_SLEEP

        if not status.get("enabled"):
            self.log("ℹ️  Ads disabled oleh admin", "DIM")
            return 0, 0, DEFAULT_SLEEP

        remaining = status.get("remaining", 0)
        watched = status.get("watched", 0)
        limit = status.get("limit", 10)
        reward_per = status.get("rewardAtf", 10)
        reset_s = status.get("resetsInSeconds", 86400)

        self.log(f"📊 Slot: {watched}/{limit} | Sisa: {remaining} | "
                 f"Reward: +{reward_per}/iklan | Reset: {fmt_duration(reset_s)}", "INFO")

        if remaining <= 0:
            self.log(f"✅ Semua slot sudah terpakai", "SUCCESS")
            return 0, 0, reset_s

        init_resp = self.bidnet_init()
        self.giga_analytics("init", {"seconds": round(random.uniform(1, 10), 3)})

        claimed = 0
        reward_total = 0
        rtb_ok = 0
        rtb_fail = 0

        for i in range(remaining):
            st = self.ads_status()
            if not st or st.get("remaining", 0) <= 0:
                self.log("⏭️  Limit habis", "WARNING")
                break

            slot_no = watched + i + 1
            self.log(f"▶️  Slot {slot_no}/{limit}...", "INFO")

            watched_ok, tid, reason = self.watch_one_ad(slot_no)
            if watched_ok:
                rtb_ok += 1
            else:
                rtb_fail += 1

            ok, rew, _ = self.claim_ads_art()
            if ok:
                claimed += 1
                reward_total += rew
                pool = self.user.get("poolWallet", 0) if self.user else 0
                tag = "📺+" if watched_ok else "⚡+"
                self.log(f"   {tag} {rew} ART | Pool: {pool:.2f} ART", "SUCCESS")
            else:
                err = str(self._last_error)
                if "LIMIT" in err.upper() or "DISABLED" in err.upper():
                    self.log(f"   ⏭️  {err[:50]}", "WARNING")
                    break
                elif "USER_NOT_FOUND" in err.upper():
                    self.log(f"   ❌ User tidak ditemukan", "ERROR")
                    break
                else:
                    self.log(f"   ⚠️  {err[:50]}", "WARNING")

            if i < remaining - 1:
                delay = random.uniform(ADS_DELAY_MIN, ADS_DELAY_MAX)
                self.log(f"   ⏱️  Delay {delay:.0f}s...", "DIM")
                time.sleep(delay)

        self.log(f"📊 Statistik RTB: {rtb_ok} berhasil, {rtb_fail} gagal", "DIM")

        st_final = self.ads_status()
        next_reset = st_final.get("resetsInSeconds", DEFAULT_SLEEP) if st_final else DEFAULT_SLEEP
        if next_reset <= 0:
            next_reset = DEFAULT_SLEEP

        return claimed, reward_total, next_reset

    # ==================== SLEEP CALCULATOR ====================
    def calculate_sleep(self, reset_s, all_claimed):
        if all_claimed and reset_s > 3600:
            sleep_sec = random.randint(SLEEP_AFTER_ALL_DONE_MIN, SLEEP_AFTER_ALL_DONE_MAX)
            return sleep_sec, f"sudah selesai semua, reset {fmt_duration(reset_s)}"

        if reset_s > 0 and reset_s < DEFAULT_SLEEP:
            sleep_sec = max(MIN_SLEEP, reset_s + random.randint(-60, 300))
            return min(sleep_sec, MAX_SLEEP), "tunggu reset"

        sleep_sec = DEFAULT_SLEEP + random.randint(-SLEEP_JITTER, SLEEP_JITTER)
        return max(MIN_SLEEP, min(sleep_sec, MAX_SLEEP)), "default"

    # ==================== MAIN RUN ====================
    def run(self):
        print(f"{GREEN}✅ Login sukses!{RESET}")
        print(f"{CYAN}👤 User  : {self.username} (ID: {self.user_id}){RESET}")

        if not self.get_user(with_ref=True):
            print(f"{RED}❌ Gagal load user: {str(self._last_error)[:60]}{RESET}")
            return

        pool = self.user.get("poolWallet", 0)
        watched = self.user.get("adsWatchedCount", 0)
        print(f"{CYAN}💰 Pool   : {pool:.4f} ART{RESET}")
        print(f"{CYAN}📊 Watched: {watched}{RESET}\n")

        while True:
            try:
                self.cycle_count += 1
                now = datetime.now().strftime("%H:%M:%S")
                print(f"\n{CYAN}{'─'*55}{RESET}")
                print(f"{CYAN}🔄 Cycle #{self.cycle_count} — {now}{RESET}")
                print(f"{CYAN}{'─'*55}{RESET}")

                self.get_user()

                if self.cycle_count > 1:
                    jitter = random.randint(CYCLE_JITTER_MIN, CYCLE_JITTER_MAX)
                    self.log(f"🎲 Jitter {fmt_duration(jitter)} sebelum mulai...", "DIM")
                    time.sleep(jitter)

                claimed, reward, reset_s = self.run_ads_cycle()

                self.get_user()
                pool = self.user.get("poolWallet", 0) if self.user else 0

                self.log(f"✅ Cycle #{self.cycle_count}: {claimed} slot | +{reward} ART", "SUCCESS")
                self.log(f"💼 Pool: {pool:.4f} ART", "INFO")

                all_claimed = (claimed >= 10) or (reset_s > 3600 and claimed > 0)
                wait_sec, reason = self.calculate_sleep(reset_s, all_claimed)

                self.log(f"💤 Sleep {fmt_duration(wait_sec)} ({reason})", "INFO")
                countdown_timer(wait_sec, "💤 Sleeping")

            except KeyboardInterrupt:
                print()
                self.log("🛑 Dihentikan oleh user", "WARNING")
                self.log(f"📊 Total cycles: {self.cycle_count}", "INFO")
                self.log(f"📺 Total ads: {self.total_claimed}", "SUCCESS")
                self.log(f"💰 Total reward: {self.total_reward} ART", "SUCCESS")
                break
            except Exception as e:
                self.log(f"❌ Error: {e}", "ERROR")
                self.log("⏳ Retry in 60s...", "WARNING")
                time.sleep(60)

# ==================== MAIN ====================
async def main():
    os.system('clear' if os.name == 'posix' else 'cls')
    print_banner()

    print(f"{CYAN}🔐 Login ke Telegram...{RESET}")
    try:
        init_data, user_obj, sig, auth_date, query_id = await get_telegram_initdata()
    except Exception as e:
        print(f"{RED}❌ Login gagal: {e}{RESET}")
        return

    if not init_data or not user_obj:
        print(f"{RED}❌ InitData tidak valid{RESET}")
        return

    bot = AdsBot(init_data, user_obj, sig, auth_date, query_id)
    bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}👋 Bye!{RESET}")
        sys.exit(0)
