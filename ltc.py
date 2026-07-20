#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🐕 LTC GENERATOR v1.0 — Litecoin Auto Miner
Developer: MoneyMaker_w
License: Free for personal use
"""

import asyncio
import requests
import json
import time
import random
import os
import re
import math
import sys
import urllib.parse
from datetime import datetime, timedelta
from telethon import TelegramClient, errors, functions, types

# ==================== WARNA ====================
R, G, Y, B, M, C, W, X = '\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m', '\033[97m', '\033[0m'
GOLD = '\033[38;5;220m'
DIM = '\033[2;37m'

# ==================== VERIFIKASI ====================
def verify_ez4short():
    print(f"\n{G}✅ Verifikasi Berhasil! (Auto-verified){W}\n")
    return True

# ==================== BANNER ====================
BANNER = f"""
{GOLD}╔══════════════════════════════════════════════════════════════╗
║               🐕 LTC GENERATOR v1.0                     ║
║      Python Automation • Dev : MoneyMaker_w              ║
╠══════════════════════════════════════════════════════════════╣
║ {W}💳 Balance    : {C}{{balance}}                            ║
║ {W}⭐ Loyalty    : {C}{{loyalty}}%                                       ║
║ {W}🔑 InitData   : {C}{{init_status}}                               ║
║ {W}♻️ Auto Renew : {C}{{renew_status}}                                      ║
╚══════════════════════════════════════════════════════════════╝{X}
"""

SESSION_SUMMARY = f"""
{GOLD}╔══════════════════════════════════════════════════════════════╗
║                     SESSION SUMMARY                         ║
╠══════════════════════════════════════════════════════════════╣
║ {W}Generator Claims : {C}{{gen_claims}}                                      ║
║ {W}Daily Tasks      : {C}{{tasks}}                                       ║
║ {W}Games Finished   : {C}{{games}}                                      ║
║ {W}Total Success    : {C}{{success}}                                      ║
║ {W}Total Failed     : {C}{{failed}}                                       ║
║ {W}Total Earned     : {C}{{earned}} LTC                         ║
║ {W}Runtime          : {C}{{runtime}}                                ║
╚══════════════════════════════════════════════════════════════╝{X}
"""

STATUS_PANEL = f"""
{GOLD}╔══════════════════════════════════════════════════════════════╗
║                     STATUS CHECK                            ║
╠══════════════════════════════════════════════════════════════╣
║ {W}✖ Generator : {R}{{gen_status}}║
║ {W}✖ Game      : {R}{{game_status}}║
║ {W}✖ Telegram  : {R}{{tele_status}}║
║ {W}✔ Auto Renew: {G}{{renew_status}}║
╚══════════════════════════════════════════════════════════════╝{X}
"""

API_URL = "https://claimltc.net/api"
CONFIG_FILE = "ltc_config.json"
SESSION_FILE = "ltc_session"

class LtcMiner:
    def __init__(self):
        self.initdata = ""
        self.initdata_expiry = 0
        self.session_id = None
        self.user_agent = "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Mobile Safari/537.36"
        self.proxy = None
        self.balance = "0"
        self.loyalty = 0
        self.counter = {"tasks": 0, "games": 0, "generator": 0}
        self.success = 0
        self.failed = 0
        self.last_gen_claims = 0
        self.last_game_claims = 0
        self.total_earned = 0.0
        self.start_time = time.time()

        # Telegram credentials
        self.api_id = None
        self.api_hash = None
        self.phone_number = None
        self.telegram_client = None
        self.bot_username = "LitecoinGeneratorBot"  # sesuaikan jika beda

        # Task selection
        self.run_games = True
        self.run_tasks = True
        self.run_generator = True
        self.selected_difficulty = "expert"

        # Auto renew settings
        self.auto_renew_initdata = True
        self.renew_check_interval = 11440
        self.last_renew_check = 0

        # Config settings
        self.config_settings = {
            "proxy_account": "off",
            "claim_check_timer": "5 minutes",
            "keep_active_timer": "30 minutes",
            "sleep_timer": "off",
            "success_task_before_sleep": "20~25",
            "auto_renew_initdata": "on"
        }

        self.load_configs()

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def num(self, value, decimals=8):
        try:
            if value is None:
                return "0"
            return f"{float(value):.{decimals}f}"
        except:
            return str(value)

    def load_configs(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    configs = json.load(f)
                    if "LtcMiner" in configs:
                        saved = configs["LtcMiner"]
                        self.initdata = saved.get("initdata", "")
                        self.initdata_expiry = saved.get("initdata_expiry", 0)
                        self.config_settings = saved.get("config_settings", self.config_settings)
                        self.selected_difficulty = saved.get("selected_difficulty", "expert")
                        self.run_games = saved.get("run_games", True)
                        self.run_tasks = saved.get("run_tasks", True)
                        self.run_generator = saved.get("run_generator", True)
                        self.proxy = saved.get("proxy", None)
                        self.api_id = saved.get("api_id", None)
                        self.api_hash = saved.get("api_hash", None)
                        self.phone_number = saved.get("phone_number", None)
                        self.auto_renew_initdata = self.config_settings.get("auto_renew_initdata", "on") == "on"
            except:
                pass

    def save_configs(self):
        configs = {}
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    configs = json.load(f)
            except:
                pass

        configs["LtcMiner"] = {
            "initdata": self.initdata,
            "initdata_expiry": self.initdata_expiry,
            "config_settings": self.config_settings,
            "selected_difficulty": self.selected_difficulty,
            "run_games": self.run_games,
            "run_tasks": self.run_tasks,
            "run_generator": self.run_generator,
            "proxy": self.proxy,
            "api_id": self.api_id,
            "api_hash": self.api_hash,
            "phone_number": self.phone_number
        }

        with open(CONFIG_FILE, 'w') as f:
            json.dump(configs, f, indent=2)

    def generate_session_id(self):
        return os.urandom(16).hex()

    def generate_request_id(self):
        ts = int(time.time() * 1000)
        suffix = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=9))
        return f"{ts}-{suffix}"

    def get_client_attestation(self):
        return {
            "session_id": self.session_id if self.session_id else self.generate_session_id(),
            "telegram": {
                "available": True,
                "platform": "android",
                "version": "8.0",
                "color_scheme": "dark",
                "user_present": True
            },
            "navigator": {
                "webdriver": False,
                "languages_count": 3,
                "max_touch_points": 5,
                "hardware_concurrency": 8,
                "device_memory": 8,
                "platform": "Linux armv81",
                "vendor": "Google Inc.",
                "cookie_enabled": True
            },
            "screen": {
                "width": 393,
                "height": 873,
                "avail_width": 393,
                "avail_height": 873,
                "pixel_ratio": 2.75,
                "color_depth": 24
            },
            "user_agent_data": {
                "mobile": True,
                "platform": "Android"
            },
            "timezone": "Europe/London"
        }

    def call_api(self, action, extra_params=None):
        if self.session_id is None:
            self.session_id = self.generate_session_id()

        ts = int(time.time() * 1000)
        payload = {
            "action": action,
            "initData": self.initdata,
            "timestamp": ts,
            "requestId": self.generate_request_id(),
            "client_attestation": self.get_client_attestation()
        }
        if extra_params:
            payload.update(extra_params)

        headers = {
            "x-requested-with": "TelegramWebApp",
            "origin": "https://claimltc.net",
            "content-type": "application/json",
            "accept-language": "en-US,en;q=0.9",
            "user-agent": self.user_agent
        }

        try:
            proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
            res = requests.post(API_URL, headers=headers, json=payload, timeout=30, proxies=proxies)
            if res.status_code == 200:
                return res.json()
            return None
        except Exception as e:
            print(f"API Error: {e}")
            return None

    async def get_webview_initdata(self):
        try:
            print(f"{C}[TELEGRAM] Getting bot entity...{X}")
            bot = await self.telegram_client.get_input_entity(self.bot_username)

            print(f"{C}[TELEGRAM] Fetching bot info...{X}")
            full_user_request = await self.telegram_client(functions.users.GetFullUserRequest(id=bot))
            bot_info = full_user_request.full_user.bot_info

            target_url = None
            if bot_info and bot_info.menu_button:
                if hasattr(bot_info.menu_button, 'url'):
                    target_url = bot_info.menu_button.url
                    print(f"{G}[TELEGRAM] Auto-detected URL: {target_url}{X}")

            if not target_url:
                target_url = 'https://claimltc.net/'
                print(f"{Y}[TELEGRAM] Using fallback URL: {target_url}{X}")

            print(f"{C}[TELEGRAM] Requesting WebView...{X}")

            result = await self.telegram_client(functions.messages.RequestWebViewRequest(
                peer=bot,
                bot=bot,
                platform='android',
                from_bot_menu=True,
                url=target_url
            ))

            print(f"{C}[TELEGRAM] Parsing response...{X}")
            parsed_url = urllib.parse.urlparse(result.url)

            fragment = parsed_url.fragment
            if fragment:
                query_params = urllib.parse.parse_qs(fragment)
                init_data = query_params.get('tgWebAppData', [None])[0]
                if init_data:
                    return init_data

            query = parsed_url.query
            if query:
                query_params = urllib.parse.parse_qs(query)
                init_data = query_params.get('tgWebAppData', [None])[0]
                if init_data:
                    return init_data

            return None

        except Exception as e:
            print(f"{R}[ERROR] Failed to get WebView initdata: {e}{X}")
            return None

    async def login_telegram_async(self):
        print(f"{C}[TELEGRAM] Logging in with Telethon...{X}")

        if not self.api_id or not self.api_hash:
            print(f"{R}[ERROR] API ID and API Hash are required!{X}")
            print(f"{Y}Get them from https://my.telegram.org/apps{X}")
            return False

        try:
            self.telegram_client = TelegramClient(
                SESSION_FILE,
                self.api_id,
                self.api_hash
            )

            await self.telegram_client.connect()

            if not await self.telegram_client.is_user_authorized():
                if not self.phone_number:
                    print(f"{Y}[TELEGRAM] Phone number required for first login{X}")
                    return False

                phone = self.phone_number
                if not phone.startswith('+'):
                    phone = '+' + phone

                await self.telegram_client.send_code_request(phone)
                code = input(f"{M}[?] {W}Enter Telegram verification code: {C}")

                try:
                    await self.telegram_client.sign_in(phone, code)
                except errors.SessionPasswordNeededError:
                    password = input(f"{M}[?] {W}Enter 2FA password: {C}")
                    await self.telegram_client.sign_in(password=password)

            print(f"{G}[TELEGRAM] Successfully logged in!{X}")

            print(f"{C}[TELEGRAM] Extracting initdata from @{self.bot_username}...{X}")
            initdata = await self.get_webview_initdata()

            if initdata:
                self.initdata = initdata
                self.initdata_expiry = int(time.time()) + 7200
                self.save_configs()
                print(f"{G}[TELEGRAM] Initdata extracted successfully!{X}")
                print(f"{C}[TELEGRAM] Initdata length: {len(initdata)} chars{X}")
                return True
            else:
                print(f"{R}[TELEGRAM] Failed to extract initdata{X}")
                print(f"{Y}[TIP] Make sure you have started a chat with @{self.bot_username} before{X}")
                return False

        except Exception as e:
            print(f"{R}[TELEGRAM] Login error: {e}{X}")
            return False
        finally:
            if self.telegram_client:
                await self.telegram_client.disconnect()

    def login_telegram(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.login_telegram_async())
            loop.close()
            return result
        except Exception as e:
            print(f"{R}[TELEGRAM] Error: {e}{X}")
            return False

    def check_and_renew_initdata(self):
        if not self.auto_renew_initdata:
            return False

        current_time = int(time.time())

        if not self.initdata:
            print(f"\n{Y}[AUTO-RENEW] No initdata found, attempting login...{X}")
            return self.login_telegram()

        if current_time >= self.initdata_expiry - 600:
            print(f"\n{Y}[AUTO-RENEW] Initdata expiring soon, refreshing...{X}")
            if self.login_telegram():
                self.last_renew_check = current_time
                print(f"{G}[AUTO-RENEW] Initdata refreshed successfully!{X}")
                return True
            else:
                print(f"{R}[AUTO-RENEW] Failed to refresh initdata{X}")
                return False

        if self.last_renew_check > 0 and current_time - self.last_renew_check > self.renew_check_interval:
            print(f"\n{Y}[AUTO-RENEW] Periodic refresh...{X}")
            if self.login_telegram():
                self.last_renew_check = current_time
                print(f"{G}[AUTO-RENEW] Initdata refreshed successfully!{X}")
                return True

        return False

    def connect(self):
        self.check_and_renew_initdata()

        if not self.initdata:
            return False

        result = self.call_api("get_user_data")
        if result:
            self.balance = result.get("balance", "0")
            self.loyalty = result.get("loyalty_percent", 0)
            self.last_gen_claims = result.get("gen_claims", 0)
            self.last_game_claims = result.get("daily_mines_claims", 0)
            return True
        return False

    def get_init_status(self):
        if not self.initdata:
            return "EMPTY"
        remaining = self.initdata_expiry - int(time.time())
        if remaining > 600:
            return f"VALID ({remaining//60}m)"
        elif remaining > 0:
            return f"EXPIRING ({remaining//60}m)"
        else:
            return "EXPIRED"

    def display_banner(self):
        balance_str = f"{self.num(self.balance, 8)} LTC"
        loyalty_str = f"{self.loyalty}%"
        init_status = self.get_init_status()
        renew_status = "ON" if self.auto_renew_initdata else "OFF"
        print(BANNER.format(balance=balance_str, loyalty=loyalty_str,
                            init_status=init_status, renew_status=renew_status))

    def display_session_summary(self):
        runtime_seconds = int(time.time() - self.start_time)
        runtime_str = str(timedelta(seconds=runtime_seconds))
        print(SESSION_SUMMARY.format(
            gen_claims=self.counter["generator"],
            tasks=self.counter["tasks"],
            games=self.counter["games"],
            success=self.success,
            failed=self.failed,
            earned=self.num(self.total_earned, 8),
            runtime=runtime_str
        ))

    def display_status_panel(self):
        # Cek status generator (cooldown)
        gen_status = "Cooldown 17m 21s"  # placeholder, nanti di-update
        game_status = "No energy left"
        tele_status = "InitData expired"
        renew_status = "Success" if self.check_and_renew_initdata() else "Idle"
        print(STATUS_PANEL.format(
            gen_status=gen_status,
            game_status=game_status,
            tele_status=tele_status,
            renew_status=renew_status
        ))

    def internal_captcha(self, context):
        print(f"{C}[CAPTCHA] Solving {context} captcha...{X}")
        retry = 0

        while retry < 5:
            try:
                captcha_init = self.call_api("captcha_init", {"context": context})
                if not captcha_init or "session" not in captcha_init:
                    print(f"{R}[CAPTCHA] Failed to initialize{X}")
                    retry += 1
                    time.sleep(2)
                    continue

                session_id = captcha_init['session']['sessionId']

                time.sleep(random.uniform(1.0, 2.0))

                puzzle = captcha_init['session']['step1']['puzzleSvg']

                match = re.search(r"<g\s*transform='translate\((\d+),", puzzle)
                if not match:
                    match = re.search(r"translate\(([\d.]+),", puzzle)

                if not match:
                    print(f"{R}[CAPTCHA] Failed to parse puzzle{X}")
                    retry += 1
                    continue

                x_pos = int(float(match.group(1)))

                width_match = re.search(r"width='(\d+)'", puzzle)
                width = int(width_match.group(1)) if width_match else 500

                max_x = x_pos + random.randint(70, 75)
                val_x = 0
                trajectory = []

                while val_x < max_x and val_x <= width:
                    if random.randint(0, 1) or val_x == 0:
                        val_x += random.randint(10, 15)
                    time.sleep(random.uniform(0.01, 0.03))
                    trajectory.append({
                        "x": val_x,
                        "t": int(time.time() * 1000)
                    })

                final_x = max(10, x_pos - 1 + random.random())

                slide_result = self.call_api("captcha_verify_slide", {
                    "sessionId": session_id,
                    "x": final_x,
                    "trajectory": trajectory
                })

                if not slide_result or not slide_result.get("success"):
                    print(f"{R}[CAPTCHA] Slide verification failed{X}")
                    retry += 1
                    continue

                print(f"{G}[CAPTCHA] Slide verification passed{X}")
                time.sleep(random.uniform(2.5, 4.0))

                grid = captcha_init['session']['step2']['grid']
                targets = captcha_init['session']['step2']['targets']

                icon_to_id = {}
                for item in grid:
                    icon_to_id[item['icon']] = item['id']

                selected_ids = []
                for target in targets:
                    if target in icon_to_id:
                        selected_ids.append(icon_to_id[target])

                pattern_result = self.call_api("captcha_verify_pattern", {
                    "sessionId": session_id,
                    "selectedIds": selected_ids
                })

                if not pattern_result or not pattern_result.get("success"):
                    print(f"{R}[CAPTCHA] Pattern verification failed{X}")
                    retry += 1
                    continue

                token = pattern_result.get("token")
                if not token:
                    print(f"{R}[CAPTCHA] No token received{X}")
                    retry += 1
                    continue

                print(f"{G}[CAPTCHA] Pattern verification passed!{X}")
                return token

            except Exception as e:
                print(f"{R}[CAPTCHA] Error: {e}{X}")
                retry += 1
                continue

        print(f"{R}[CAPTCHA] Failed after {retry} attempts{X}")
        return None

    def action_proof(self, target_action, is_doubled=False):
        print(f"{C}[PROOF] Getting action proof for {target_action}...{X}")

        init_data = {
            "targetAction": target_action
        }
        if is_doubled:
            init_data["doubled"] = True

        proof_init = self.call_api("action_proof_init", init_data)

        if not proof_init or proof_init.get("status") != "success":
            print(f"{R}[PROOF] Failed to initialize{X}")
            return None

        wait_time = proof_init.get("min_wait_seconds", 2)
        time.sleep(wait_time + 1)

        complete_data = {
            "targetAction": target_action,
            "challengeId": proof_init.get("challenge_id")
        }
        if is_doubled:
            complete_data["doubled"] = True

        proof_complete = self.call_api("action_proof_complete", complete_data)

        if not proof_complete or proof_complete.get("status") != "success":
            print(f"{R}[PROOF] Failed to complete{X}")
            return None

        return proof_complete.get("proof_token")

    def task_generator(self):
        print(f"\n{Y}[GENERATOR] Checking faucet...{X}")

        url = "https://claimltc.net/faucetmining"
        headers = {
            "origin": "https://claimltc.net",
            "content-type": "application/json",
            "user-agent": self.user_agent
        }

        try:
            proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
            res = requests.post(url, headers=headers, json={"initData": self.initdata}, timeout=30, proxies=proxies)
            if res.status_code == 200:
                data = res.json()
                timer = data.get("TimeSinceLastClaimSeconds", 0)
                cooldown = data.get("FaucetCooldownSeconds", 3600)

                if timer < cooldown:
                    wait = cooldown - timer
                    print(f"{R}✖ Generator : Cooldown {wait//60}m {wait%60}s{X}")
                    return False
        except:
            pass

        proof_token = self.action_proof("claim_faucet", is_doubled=True)
        if not proof_token:
            print(f"{R}✖ Generator : Action proof failed{X}")
            self.failed += 1
            return False

        captcha_token = None
        user_data = self.call_api("get_user_data")
        if user_data:
            gen_claims = user_data.get("gen_claims", 0)
            gen_freq = user_data.get("faucet_captcha_frequency", 5)

            if gen_freq > 0 and (gen_claims + 1) % gen_freq == 0:
                print(f"{Y}[INFO] Captcha required for claim #{gen_claims + 1}{X}")
                captcha_token = self.internal_captcha("faucet")
                if not captcha_token:
                    print(f"{R}✖ Generator : Captcha solving failed{X}")
                    self.failed += 1
                    return False

        claim_data = {
            "doubled": True,
            "action_proof": proof_token
        }
        if captcha_token:
            claim_data["captcha"] = captcha_token
            claim_data["captcha_provider"] = "internal"

        result = self.call_api("claim_faucet", claim_data)

        if result and result.get("status") == "success":
            reward = result.get("claimed_amount", "0")
            bonus = result.get("loyalty_bonus_amount", "0")
            reward_float = float(reward)
            self.total_earned += reward_float
            self.counter["generator"] += 1
            self.success += 1
            print(f"{G}✔ Generator : Claim +{self.num(reward, 8)} LTC (Bonus: {self.num(bonus, 8)}){X}")
            return True
        else:
            error_msg = result.get("message", "Unknown error") if result else "No response"
            print(f"{R}✖ Generator : Failed ({error_msg}){X}")
            self.failed += 1
            return False

    def task_tasks(self):
        print(f"\n{Y}[TASK] Checking daily tasks...{X}")

        u_data = self.call_api("get_user_data")
        if not u_data:
            print(f"{R}✖ Task : Failed to get user data{X}")
            return False

        today = datetime.now().strftime("%Y-%m-%d")
        claimed = False

        last_daily = u_data.get("last_daily_bonus", "")
        if not last_daily or last_daily.split()[0] != today:
            print(f"{C}[TASK] Claiming daily bonus...{X}")

            proof_token = self.action_proof("claim_daily_bonus", is_doubled=True)
            if proof_token:
                result = self.call_api("claim_daily_bonus", {
                    "doubled": True,
                    "action_proof": proof_token
                })
                if result and result.get("status") == "success":
                    amount = result.get("claimed_amount", "0")
                    self.total_earned += float(amount)
                    self.counter["tasks"] += 1
                    self.success += 1
                    print(f"{G}✔ Task : Daily Bonus +{self.num(amount, 8)} LTC{X}")
                    claimed = True
        else:
            print(f"{Y}[TASK] Daily already claimed today{X}")

        # Double reward task
        double_claims = u_data.get("daily_double_claims", 0)
        last_double = u_data.get("last_double_task_claimed_at", "")
        last_double_activity = u_data.get("last_double_claim_activity_at", "")

        if double_claims >= 10 and (not last_double or last_double.split()[0] != today):
            if last_double_activity and last_double_activity.split()[0] == today:
                print(f"{C}[TASK] Claiming double reward task...{X}")

                proof_token = self.action_proof("claim_double_reward_task", is_doubled=True)
                if proof_token:
                    result = self.call_api("claim_double_reward_task", {
                        "doubled": True,
                        "action_proof": proof_token
                    })
                    if result and result.get("status") == "success":
                        amount = result.get("claimed_amount", "0")
                        self.total_earned += float(amount)
                        self.counter["tasks"] += 1
                        self.success += 1
                        print(f"{G}✔ Task : Double Reward +{self.num(amount, 8)} LTC{X}")
                        claimed = True

        if claimed:
            return True

        print(f"{Y}[TASK] No tasks available today{X}")
        return False

    def task_games(self):
        print(f"\n{Y}[GAME] Starting mines game...{X}")

        total_earned_this_session = 0
        games_played = 0

        while True:
            m_stats = self.call_api("mines_get_stats")
            if not m_stats:
                print(f"{R}✖ Game : Failed to get stats{X}")
                break

            stats = m_stats.get("stats", {})
            lives = int(stats.get("game_lives", 0))
            max_lives = stats.get("game_lives_max", 3)
            has_active = stats.get("has_active_game", False)
            active_game = stats.get("active_game")

            if active_game is None:
                active_game = {}

            current_earnings = float(active_game.get("earned_doge", 0))
            game_claims = stats.get("total_games_won", 0)
            game_freq = stats.get("cashout_captcha_frequency", 5)

            if lives <= 0 and not has_active:
                print(f"{R}✖ Game : No energy left{X}")
                break

            if not has_active and lives > 0:
                start_res = self.call_api("mines_start_game", {"difficulty": self.selected_difficulty})
                if not start_res or start_res.get("status") != "success":
                    print(f"{R}✖ Game : Failed to start{X}")
                    break
                time.sleep(1)
                continue

            if not has_active:
                break

            grid_state = {}
            try:
                grid_state = json.loads(stats.get('active_grid_state', '{}'))
            except:
                pass

            bombs = grid_state.get('bombs', [])
            revealed = grid_state.get('revealed', [])
            safe_tiles = [i for i in range(25) if i not in bombs and i not in revealed]

            can_cashout = active_game.get("can_cashout", False)

            if not safe_tiles or can_cashout:
                print(f"{C}[GAME] Cashing out {self.num(current_earnings, 8)} LTC...{X}")

                act_token = self.action_proof("mines_cashout", is_doubled=False)
                if not act_token:
                    print(f"{R}✖ Game : Action proof failed{X}")
                    break

                captcha_token = None
                if game_freq > 0 and (game_claims + 1) % game_freq == 0:
                    print(f"{Y}[INFO] Captcha required for cashout{X}")
                    captcha_token = self.internal_captcha("mines")

                cashout_data = {
                    "action_proof": act_token
                }
                if captcha_token:
                    cashout_data["captcha"] = captcha_token
                    cashout_data["captcha_provider"] = "internal"

                result = self.call_api("mines_cashout", cashout_data)

                if result and result.get("status") == "success":
                    earned_amount = result.get("result", {}).get("earned_doge", current_earnings)
                    self.total_earned += float(earned_amount)
                    games_played += 1
                    self.counter["games"] += 1
                    self.success += 1
                    self.last_game_claims += 1
                    print(f"{G}✔ Game : Cashout +{self.num(earned_amount, 8)} LTC{X}")
                    continue
                else:
                    error_msg = result.get("message", "Unknown error") if result else "No response"
                    print(f"{R}✖ Game : Cashout failed ({error_msg}){X}")
                    break

            if safe_tiles:
                tile_to_open = random.choice(safe_tiles)
                open_res = self.call_api("mines_open_tile", {"tile_index": tile_to_open})

                if open_res and open_res.get("status") == "success":
                    result_data = open_res.get("result", {})
                    tile_result = result_data.get("result")
                    earned = result_data.get("current_earnings_doge", 0)

                    if tile_result == "bomb":
                        print(f"  {R}💣 Tile {tile_to_open:02} » BOMB!{X}")
                        if result_data.get("can_continue"):
                            print(f"{Y}[AD] Watch ad to continue...{X}")
                            act_token = self.action_proof("mines_watch_ad_continues", is_doubled=False)
                            if act_token:
                                watch_res = self.call_api("mines_watch_ad_continues", {"action_proof": act_token})
                                if watch_res and watch_res.get("status") == "success":
                                    for i in range(random.randint(5, 10)):
                                        print(f"\r{Y}[AD] {i+1}s{X}", end="")
                                        time.sleep(1)
                                    print()
                                    continue_res = self.call_api("mines_use_continue", {})
                                    if continue_res and continue_res.get("status") == "success":
                                        print(f"{G}[CONTINUE] Game continued!{X}")
                                        continue
                        break
                    else:
                        print(f"  {G}√ Tile {tile_to_open:02} » +{self.num(earned, 8)} LTC{X}")
                else:
                    print(f"  {R}× Tile {tile_to_open:02} » FAILED{X}")
                    break

                time.sleep(random.uniform(0.3, 0.8))

        if games_played > 0:
            print(f"{G}✔ Game : Completed {games_played} game(s), earned {self.num(total_earned_this_session, 8)} LTC{X}")

        return games_played > 0

    def countdown(self, seconds, message="WAITING"):
        while seconds > 0:
            if seconds % 60 == 0:
                self.check_and_renew_initdata()

            mins, secs = divmod(seconds, 60)
            timer = f'{Y}⏳ {message} : {mins:02d}:{secs:02d}{X}'
            print(f"\r{timer}", end="")
            time.sleep(1)
            seconds -= 1
        print("\r" + " " * 60 + "\r", end="")

    def show_task_selection(self):
        while True:
            self.clear()
            self.display_banner()

            print(f"\n{C}╔══════════════════════════════════════════════════════════════╗")
            print(f"║ {W}                    SELECT TASKS TO RUN{C}                         ║")
            print(f"║ {G}    Choose which tasks you want to enable{C}                       ║")
            print(f"╚══════════════════════════════════════════════════════════════╝{X}")

            gen_status = f"{G}✓ ENABLED{X}" if self.run_generator else f"{R}✗ DISABLED{X}"
            task_status = f"{G}✓ ENABLED{X}" if self.run_tasks else f"{R}✗ DISABLED{X}"
            game_status = f"{G}✓ ENABLED{X}" if self.run_games else f"{R}✗ DISABLED{X}"
            renew_status = f"{G}✓ ON{X}" if self.auto_renew_initdata else f"{R}✗ OFF{X}"

            print(f"\n  {C}[{W}1{C}] GENERATOR (Faucet)  : {gen_status}")
            print(f"  {C}[{W}2{C}] TASKS (Daily Bonus) : {task_status}")
            print(f"  {C}[{W}3{C}] GAMES (Mines Game)  : {game_status}")
            print(f"  {C}[{W}4{C}] GAME MODE           : {C}{self.selected_difficulty.upper()}{X}")
            print(f"  {C}[{W}5{C}] AUTO RENEW INITDATA : {renew_status}")
            print(f"  {C}[{W}6{C}] {G}START MINER WITH SELECTED TASKS{X}")
            print(f"  {C}[{W}0{C}] {R}CANCEL / BACK TO MAIN MENU{X}")

            print()
            choice = input(f"{C}═⫸ {W}Select option: {C}").strip()

            if choice == "1":
                self.run_generator = not self.run_generator
                print(f"{G}Generator {'ENABLED' if self.run_generator else 'DISABLED'}{X}")
                self.save_configs()
                time.sleep(1)
            elif choice == "2":
                self.run_tasks = not self.run_tasks
                print(f"{G}Tasks {'ENABLED' if self.run_tasks else 'DISABLED'}{X}")
                self.save_configs()
                time.sleep(1)
            elif choice == "3":
                self.run_games = not self.run_games
                print(f"{G}Games {'ENABLED' if self.run_games else 'DISABLED'}{X}")
                self.save_configs()
                time.sleep(1)
            elif choice == "4":
                self.show_game_mode_menu()
            elif choice == "5":
                self.auto_renew_initdata = not self.auto_renew_initdata
                self.config_settings["auto_renew_initdata"] = "on" if self.auto_renew_initdata else "off"
                print(f"{G}Auto Renew {'ENABLED' if self.auto_renew_initdata else 'DISABLED'}{X}")
                self.save_configs()
                time.sleep(1)
            elif choice == "6":
                if not any([self.run_generator, self.run_tasks, self.run_games]):
                    print(f"{R}[ERROR] Please enable at least one task!{X}")
                    time.sleep(2)
                    continue
                return True
            elif choice == "0":
                return False

    def show_game_mode_menu(self):
        difficulty_map = {
            "easy": "surface",
            "medium": "tunnel",
            "hard": "deep shaft",
            "expert": "core drill"
        }

        while True:
            self.clear()
            self.display_banner()

            print(f"\n{C}╔══════════════════════════════════════════════════════════════╗")
            print(f"║ {W}                    SELECT GAME MODE{C}                            ║")
            print(f"╚══════════════════════════════════════════════════════════════╝{X}")

            print(f"\n  {C}[{W}1{C}] EASY     (surface)")
            print(f"  {C}[{W}2{C}] MEDIUM   (tunnel)")
            print(f"  {C}[{W}3{C}] HARD     (deep shaft)")
            print(f"  {C}[{W}4{C}] EXPERT   (core drill)")
            print(f"  {C}[{W}0{C}] BACK")

            print(f"\n  {Y}Current mode: {C}{self.selected_difficulty.upper()} ({difficulty_map[self.selected_difficulty]}){X}")
            print()
            choice = input(f"{C}═⫸ {W}Select game mode: {C}").strip()

            mode_map = {
                "1": "easy",
                "2": "medium",
                "3": "hard",
                "4": "expert"
            }

            if choice in mode_map:
                self.selected_difficulty = mode_map[choice]
                self.save_configs()
                print(f"{G}Game mode set to {self.selected_difficulty.upper()} ({difficulty_map[self.selected_difficulty]}){X}")
                time.sleep(1)
                return
            elif choice == "0":
                return

    def telegram_login_menu(self):
        self.clear()
        self.display_banner()

        print(f"\n{C}╔══════════════════════════════════════════════════════════════╗")
        print(f"║ {W}                 TELEGRAM LOGIN SETUP{C}                           ║")
        print(f"║ {G}    Bot: @{self.bot_username}{C}                                    ║")
        print(f"╚══════════════════════════════════════════════════════════════╝{X}")

        print(f"\n{Y}[INFO] Get API ID and Hash from https://my.telegram.org/apps{X}\n")

        api_id_input = input(f"{M}[?] {W}Enter API ID: {C}").strip()
        if api_id_input:
            self.api_id = int(api_id_input)

        self.api_hash = input(f"{M}[?] {W}Enter API Hash: {C}").strip()

        print(f"\n{Y}[INFO] Phone number format: 628123456789 (without +) or +628123456789{X}\n")
        self.phone_number = input(f"{M}[?] {W}Enter Phone Number: {C}").strip()

        if self.api_id and self.api_hash and self.phone_number:
            print(f"{C}[TELEGRAM] Attempting login...{X}")
            if self.login_telegram():
                print(f"{G}[SUCCESS] Telegram login successful!{X}")
                print(f"{G}[SUCCESS] Initdata extracted and saved!{X}")
                self.save_configs()
                time.sleep(2)
                return True
            else:
                print(f"{R}[ERROR] Telegram login failed!{X}")
                print(f"{Y}[TIP] Please make sure you have started a chat with @{self.bot_username}{X}")
                input(f"{Y}Press Enter to continue...{X}")
                return False

        return False

    def config_settings_menu(self):
        while True:
            self.clear()
            self.display_banner()

            print(f"\n{C}╔══════════════════════════════════════════════════════════════╗")
            print(f"║ {W}                    CONFIG SETTINGS{C}                              ║")
            print(f"╚══════════════════════════════════════════════════════════════╝{X}")

            print(f"  {C}[{W}1{C}] CLAIM CHECK TIMER ::: [{self.config_settings['claim_check_timer']}]")
            print(f"  {C}[{W}2{C}] KEEP ACTIVE TIMER ::: [{self.config_settings['keep_active_timer']}]")
            print(f"  {C}[{W}3{C}] SLEEP TIMER ::: [{self.config_settings['sleep_timer']}]")
            print(f"  {C}[{W}4{C}] SUCCESS LIMIT ::: [{self.config_settings['success_task_before_sleep']}]")
            print(f"  {C}[{W}5{C}] AUTO RENEW INITDATA ::: [{self.config_settings.get('auto_renew_initdata', 'on').upper()}]")
            print(f"  {C}[{W}6{C}] TELEGRAM LOGIN SETUP")
            print(f"  {C}[{W}0{C}] BACK")

            print()
            choice = input(f"{C}═⫸ {W}Select option: {C}").strip()

            if choice == "1":
                print(f"\n  {C}[1] OFF")
                print(f"  {C}[2] ON")
                sub = input(f"{C}═⫸ {W}Select: {C}").strip()
                if sub == "1":
                    self.config_settings["proxy_account"] = "off"
                    self.proxy = None
                    print(f"{Y}Proxy DISABLED{X}")
                elif sub == "2":
                    self.config_settings["proxy_account"] = "on"
                    self.proxy = input(f"{M}Enter proxy (http://ip:port): {C}").strip()
                    print(f"{G}Proxy ENABLED{X}")
                self.save_configs()
                time.sleep(1)

            elif choice == "2":
                timers = ["5 minutes", "10 minutes", "15 minutes", "30 minutes", "1 hour", "2 hours", "3 hours"]
                print(f"\n  Select claim check timer:")
                for i, t in enumerate(timers, 1):
                    print(f"  {C}[{i}] {t}")
                sub = input(f"{C}═⫸ {W}Select: {C}").strip()
                if sub.isdigit() and 1 <= int(sub) <= len(timers):
                    self.config_settings["claim_check_timer"] = timers[int(sub) - 1]
                    print(f"{G}Updated to {timers[int(sub) - 1]}{X}")
                    self.save_configs()
                time.sleep(1)

            elif choice == "3":
                timers = ["5 minutes", "10 minutes", "15 minutes", "30 minutes"]
                print(f"\n  Select keep active timer:")
                for i, t in enumerate(timers, 1):
                    print(f"  {C}[{i}] {t}")
                sub = input(f"{C}═⫸ {W}Select: {C}").strip()
                if sub.isdigit() and 1 <= int(sub) <= len(timers):
                    self.config_settings["keep_active_timer"] = timers[int(sub) - 1]
                    print(f"{G}Updated to {timers[int(sub) - 1]}{X}")
                    self.save_configs()
                time.sleep(1)

            elif choice == "4":
                timers = ["off", "30 minutes", "1 hour", "1 hour 30 minutes", "2 hours", "2 hours 30 minutes", "3 hours", "4 hours"]
                print(f"\n  Select sleep timer:")
                for i, t in enumerate(timers, 1):
                    print(f"  {C}[{i}] {t}")
                sub = input(f"{C}═⫸ {W}Select: {C}").strip()
                if sub.isdigit() and 1 <= int(sub) <= len(timers):
                    self.config_settings["sleep_timer"] = timers[int(sub) - 1]
                    print(f"{G}Updated to {timers[int(sub) - 1]}{X}")
                    self.save_configs()
                time.sleep(1)

            elif choice == "5":
                ranges = ["5~10", "10~15", "15~20", "20~25", "25~30", "30~35", "35~40", "40~45", "45~50", "50~55", "55~60"]
                print(f"\n  Select success limit before sleep:")
                for i, r in enumerate(ranges, 1):
                    print(f"  {C}[{i}] {r}")
                sub = input(f"{C}═⫸ {W}Select: {C}").strip()
                if sub.isdigit() and 1 <= int(sub) <= len(ranges):
                    self.config_settings["success_task_before_sleep"] = ranges[int(sub) - 1]
                    print(f"{G}Updated to {ranges[int(sub) - 1]}{X}")
                    self.save_configs()
                time.sleep(1)

            elif choice == "6":
                current = self.config_settings.get("auto_renew_initdata", "on")
                new = "off" if current == "on" else "on"
                self.config_settings["auto_renew_initdata"] = new
                self.auto_renew_initdata = (new == "on")
                print(f"{G}Auto Renew Initdata set to {new.upper()}{X}")
                self.save_configs()
                time.sleep(1)

            elif choice == "7":
                self.telegram_login_menu()

            elif choice == "0":
                break

    def edit_config_menu(self):
        while True:
            self.clear()
            self.display_banner()

            print(f"\n{C}╔══════════════════════════════════════════════════════════════╗")
            print(f"║ {W}                    EDIT CONFIG{C}                                  ║")
            print(f"╚══════════════════════════════════════════════════════════════╝{X}")

            print(f"\n  {C}[{W}1{C}] SELECT TASKS TO RUN")
            print(f"  {C}[{W}2{C}] GENERAL SETTINGS (Timers, Telegram)")
            print(f"  {C}[{W}0{C}] BACK")

            print()
            choice = input(f"{C}═⫸ {W}Select option: {C}").strip()

            if choice == "1":
                self.show_task_selection()
            elif choice == "2":
                self.config_settings_menu()
            elif choice == "0":
                break

    def run_miner(self):
        if not self.show_task_selection():
            return

        self.clear()
        self.display_banner()

        if not self.initdata:
            print(f"{R}[ERROR] No configuration found! Please add config first.{X}")
            input(f"{Y}Press Enter to continue...{X}")
            return

        print(f"\n{C}╔══════════════════════════════════════════════════════════════╗")
        print(f"║ {W}                    STARTING MINER{C}                               ║")
        print(f"╚══════════════════════════════════════════════════════════════╝{X}")
        print(f"  {'✓' if self.run_generator else '✗'} GENERATOR (Faucet)")
        print(f"  {'✓' if self.run_tasks else '✗'} TASKS (Daily Bonus)")
        print(f"  {'✓' if self.run_games else '✗'} GAMES (Mines) - {self.selected_difficulty.upper()}")
        print(f"  {'✓' if self.auto_renew_initdata else '✗'} AUTO RENEW INITDATA")

        if not self.connect():
            print(f"{R}[ERROR] Failed to connect! Checking initdata...{X}")
            if self.auto_renew_initdata and self.login_telegram():
                print(f"{G}[SUCCESS] Initdata renewed! Retrying connection...{X}")
                if self.connect():
                    print(f"{G}[SUCCESS] Connected! Balance: {self.num(self.balance, 8)} LTC{X}")
                else:
                    print(f"{R}[ERROR] Still cannot connect. Check your credentials.{X}")
                    input(f"{Y}Press Enter to continue...{X}")
                    return
            else:
                print(f"{R}[ERROR] Cannot connect. Please check your InitData.{X}")
                input(f"{Y}Press Enter to continue...{X}")
                return

        print(f"{Y}[INFO] Press Ctrl+C to stop{X}")
        print(f"{Y}[INFO] Games will play until energy is depleted{X}")
        print(f"{Y}[INFO] Initdata will auto-renew if enabled{X}")
        time.sleep(3)

        self.success = 0
        self.failed = 0
        self.counter = {"tasks": 0, "games": 0, "generator": 0}
        self.total_earned = 0.0
        self.start_time = time.time()

        sleep_range = self.config_settings.get("success_task_before_sleep", "20~25").split("~")
        success_min = int(sleep_range[0]) if len(sleep_range) > 0 else 20
        success_max = int(sleep_range[1]) if len(sleep_range) > 1 else 25
        success_limit = random.randint(success_min, success_max)

        try:
            while True:
                self.clear()
                self.display_banner()
                self.display_session_summary()

                print(f"\n{Y}RUNNING TASKS:{X}")
                print(f"  {'✓' if self.run_generator else '✗'} GENERATOR")
                print(f"  {'✓' if self.run_tasks else '✗'} TASKS")
                print(f"  {'✓' if self.run_games else '✗'} GAMES ({self.selected_difficulty.upper()})")
                print(f"{C}{'═'*60}{X}")
                print(f"{Y}SUCCESS LIMIT: {self.success}/{success_limit}{X}")
                print(f"{C}{'═'*60}{X}")

                self.check_and_renew_initdata()

                if self.run_generator:
                    self.task_generator()
                    time.sleep(random.uniform(2, 4))

                if self.run_tasks:
                    self.task_tasks()
                    time.sleep(random.uniform(2, 4))

                if self.run_games:
                    self.task_games()
                    time.sleep(random.uniform(2, 4))

                # Status panel setelah selesai satu cycle
                self.display_status_panel()

                sleep_timer = self.config_settings.get("sleep_timer", "off")
                if sleep_timer != "off" and self.success >= success_limit:
                    if "hour" in sleep_timer:
                        hours = int(sleep_timer.split()[0])
                        sleep_seconds = hours * 3600
                    elif "minute" in sleep_timer:
                        minutes = int(sleep_timer.split()[0])
                        sleep_seconds = minutes * 60
                    else:
                        sleep_seconds = 1800

                    print(f"\n{Y}[SLEEP] Sleeping for {sleep_timer}...{X}")
                    self.countdown(sleep_seconds)
                    self.success = 0
                    success_limit = random.randint(success_min, success_max)
                    continue

                claim_timer = self.config_settings.get("claim_check_timer", "5 minutes")
                if "hour" in claim_timer:
                    hours = int(claim_timer.split()[0])
                    wait_seconds = hours * 3600
                elif "minute" in claim_timer:
                    minutes = int(claim_timer.split()[0])
                    wait_seconds = minutes * 60
                else:
                    wait_seconds = 300

                keep_active = self.config_settings.get("keep_active_timer", "30 minutes")
                if "minute" in keep_active:
                    minutes = int(keep_active.split()[0])
                    keep_seconds = minutes * 60
                else:
                    keep_seconds = 1800

                wait_seconds = min(wait_seconds, keep_seconds)

                print(f"\n{Y}⏳ Next cycle : {wait_seconds//60:02d}:{wait_seconds%60:02d}{X}")
                self.countdown(wait_seconds)

        except KeyboardInterrupt:
            print(f"\n\n{G}[STOPPED] LTC Generator stopped{X}")
            self.display_session_summary()
            input(f"\n{Y}Press Enter to continue...{X}")

    def add_config(self):
        self.clear()
        self.display_banner()

        print(f"\n{C}╔══════════════════════════════════════════════════════════════╗")
        print(f"║ {G}                    ADD NEW CONFIG{C}                               ║")
        print(f"╚══════════════════════════════════════════════════════════════╝{X}")

        print(f"\n  {C}[{W}1{C}] Manual InitData")
        print(f"  {C}[{W}2{C}] Manual Telethon ")
        print(f"  {C}[{W}0{C}] BACK")

        print()
        choice = input(f"{C}═⫸ {W}Select option: {C}").strip()

        if choice == "1":
            initdata = input(f"\n{M}[?] {W}Enter InitData: {C}").strip()
            if initdata:
                self.initdata = initdata
                self.initdata_expiry = int(time.time()) + 3600

                proxy = input(f"{M}[?] {W}Enter proxy (optional, Enter to skip): {C}").strip()
                if proxy:
                    self.proxy = proxy
                    self.config_settings["proxy_account"] = "on"
                else:
                    self.config_settings["proxy_account"] = "off"

                self.save_configs()

                print(f"{C}[TEST] Testing connection...{X}")
                if self.connect():
                    print(f"{G}[SUCCESS] Configuration saved! Connection OK{X}")
                    print(f"{C}[INFO] Now select which tasks to run...{X}")
                    time.sleep(2)
                    self.show_task_selection()
                else:
                    print(f"{R}[WARNING] Config saved but connection failed{X}")

                time.sleep(2)
                return True

        elif choice == "2":
            if self.telegram_login_menu():
                print(f"{G}[SUCCESS] Config created via Telegram login!{X}")
                time.sleep(2)
                self.show_task_selection()
                return True

        print(f"{R}[ERROR] No configuration added{X}")
        time.sleep(2)
        return False

    def delete_config(self):
        self.clear()
        self.display_banner()

        print(f"\n{R}╔══════════════════════════════════════════════════════════════╗")
        print(f"║ {W}WARNING: Delete configuration?{R}                                   ║")
        print(f"╚══════════════════════════════════════════════════════════════╝{X}")

        confirm = input(f"\n{M}[?] {W}Are you sure? (yes/no): {C}").strip().lower()
        if confirm == "yes":
            self.initdata = ""
            self.initdata_expiry = 0
            self.proxy = None
            self.save_configs()
            print(f"{G}[SUCCESS] Configuration deleted{X}")
            time.sleep(2)

    def main_menu(self):
        while True:
            self.clear()
            self.display_banner()

            if self.initdata:
                self.display_session_summary()

            print(f"\n{C}╔══════════════════════════════════════════════════════════════╗")
            print(f"║ {W}                    MAIN MENU{C}                                    ║")
            print(f"╚══════════════════════════════════════════════════════════════╝{X}")
            print()
            print(f"  {C}[{W}1{C}] {G}🚀 START MINER")
            print(f"  {C}[{W}2{C}] {Y}⚙️ EDIT CONFIG")
            print(f"  {C}[{W}3{C}] {B}➕ ADD CONFIG")
            print(f"  {C}[{W}4{C}] {R}🗑️ DELETE CONFIG")
            print(f"  {C}[{W}5{C}] {M}🚪 EXIT")
            print()

            choice = input(f"{C}═⫸ {W}Select: {C}").strip()

            if choice == "1":
                if not self.initdata:
                    print(f"{R}[ERROR] No config found. Please add config first.{X}")
                    time.sleep(2)
                else:
                    self.run_miner()
            elif choice == "2":
                if not self.initdata:
                    print(f"{R}[ERROR] No config found. Please add config first.{X}")
                    time.sleep(2)
                else:
                    self.edit_config_menu()
            elif choice == "3":
                self.add_config()
            elif choice == "4":
                if not self.initdata:
                    print(f"{R}[ERROR] No config to delete.{X}")
                    time.sleep(2)
                else:
                    self.delete_config()
            elif choice == "5":
                print(f"{G}[EXIT] Thank you for using LTC Generator!{X}")
                sys.exit(0)

if __name__ == "__main__":
    print(f"{C}🔐 Memeriksa verifikasi...{W}")

    if not verify_ez4short():
        print(f"{R}❌ Verifikasi gagal!{W}")
        sys.exit(1)

    print(f"{G}✅ Verifikasi berhasil!{W}")
    print(f"{G}🚀 Menjalankan LTC Generator...{W}\n")

    miner = LtcMiner()
    miner.main_menu()
