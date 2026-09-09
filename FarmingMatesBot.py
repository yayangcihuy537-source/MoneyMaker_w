import requests
import json
import time
import os
import random
import sys
from datetime import datetime
from colorama import init, Fore, Back, Style

init(autoreset=True)

# ==================== BANNER ====================
BANNER = f"""
{Fore.CYAN}{Style.BRIGHT}==================================================
              🌾 FARMING MATES BOT
==================================================
              @FarmingMatesBot
           ScriptMaker: @MoneyMaker_w
=================================================={Style.RESET_ALL}
"""

# ==================== CLASS ====================
class FarmingMatesBot:
    def __init__(self):
        self.base_url = "https://api.farmingmates.site/api"
        self.init_data = None
        self.device_id = "dev_" + str(int(time.time()))
        self.token = None
        self.profile = None
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; K) Telegram-Android/12.10.1",
            "Accept": "*/*",
            "Origin": "https://farmingmates.site",
            "Referer": "https://farmingmates.site/",
            "X-Requested-With": "org.telegram.messenger"
        }
        self.stats = {
            'total_watched': 0,
            'total_earned': 0,
            'start_time': datetime.now()
        }

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_login_success(self):
        print(f"{Fore.GREEN}[✓] Login berhasil{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[👤] @{self.profile.get('username')}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[💰] Balance : {self.profile.get('coins', 0)}{Style.RESET_ALL}")
        print(f"{Fore.BLUE}[⚡] Energy  : {self.profile.get('energy', 0)}/{self.profile.get('energyMax', 0)}{Style.RESET_ALL}")

    def print_header(self, text):
        print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[{text}]{Style.RESET_ALL}")

    def print_error(self, text):
        print(f"{Fore.RED}[✗] {text}{Style.RESET_ALL}")

    def print_success(self, text):
        print(f"{Fore.GREEN}[✓] {text}{Style.RESET_ALL}")

    def print_warning(self, text):
        print(f"{Fore.YELLOW}[⚠] {text}{Style.RESET_ALL}")

    def print_info(self, text):
        print(f"{Fore.CYAN}[ℹ] {text}{Style.RESET_ALL}")

    # ==================== REQUEST WITH RETRY ====================
    def request_with_retry(self, method, url, headers=None, json_data=None, data=None, max_retries=3, timeout=30):
        """Request dengan retry jika timeout"""
        for attempt in range(1, max_retries + 1):
            try:
                if method.upper() == 'GET':
                    response = requests.get(url, headers=headers, json=json_data, timeout=timeout)
                elif method.upper() == 'POST':
                    response = requests.post(url, headers=headers, json=json_data, data=data, timeout=timeout)
                else:
                    return None
                return response
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    print(f"{Fore.YELLOW}[⏳] Timeout, retry {attempt}/{max_retries}...{Style.RESET_ALL}")
                    time.sleep(2)
                    continue
                else:
                    self.print_error(f"Request timeout setelah {max_retries} percobaan")
                    return None
            except Exception as e:
                self.print_error(f"Request error: {e}")
                return None
        return None

    # ==================== LOGIN ====================
    def login(self):
        print(f"\n{Fore.YELLOW}⏳ Logging in...{Style.RESET_ALL}")

        if not self.init_data:
            self.print_error("InitData tidak ditemukan!")
            return False

        data = {
            "initData": self.init_data,
            "deviceId": self.device_id
        }

        response = self.request_with_retry(
            'POST',
            f"{self.base_url}/auth/telegram",
            headers=self.headers,
            json_data=data,
            timeout=30
        )

        if response is None:
            self.print_error("Tidak ada response dari server")
            return False

        if response.status_code == 200:
            try:
                result = response.json()
                if result.get('ok'):
                    self.token = result.get('token')
                    self.profile = result.get('profile')
                    self.headers["Authorization"] = f"Bearer {self.token}"
                    self.print_login_success()
                    return True
                else:
                    self.print_error(f"Login gagal: {result.get('message')}")
                    return False
            except:
                self.print_error("Gagal parse response login")
                return False
        else:
            self.print_error(f"HTTP {response.status_code}")
            return False

    # ==================== FARMING ====================
    def get_slots(self, task_id):
        response = self.request_with_retry(
            'GET',
            f"{self.base_url}/tasks/{task_id}/slots",
            headers=self.headers,
            timeout=30
        )

        if response is None:
            return {"ok": False}

        if response.status_code == 200:
            try:
                return response.json()
            except:
                return {"ok": False}
        else:
            return {"ok": False}

    def watch_ad(self, task_id, slot_index, slot_total, current_slot, provider, reward):
        # Buat session
        session_resp = self.request_with_retry(
            'POST',
            f"{self.base_url}/ads/task/{task_id}/session",
            headers=self.headers,
            json_data={"slotIndex": slot_index},
            timeout=30
        )

        if session_resp is None:
            self.print_error(f"Gagal buat session slot {slot_index+1}")
            return None

        if session_resp.status_code != 200:
            self.print_error(f"Gagal buat session (HTTP {session_resp.status_code})")
            return None

        try:
            session_data = session_resp.json()
            if not session_data.get('ok'):
                self.print_error(f"Session error: {session_data.get('message')}")
                return None
        except:
            self.print_error("Gagal parse session response")
            return None

        session_id = session_data.get('sessionId')
        watch_duration = random.randint(8, 12)

        print(f"\n{Fore.CYAN}[{current_slot:02d}/{slot_total:02d}] ▶ Watching...{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}[🌐] Provider : {provider.upper()}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[💰] Reward   : {reward} Koin{Style.RESET_ALL}")

        # Progress bar
        bar_width = 24
        for i in range(watch_duration):
            percent = (i + 1) / watch_duration
            filled = int(bar_width * percent)
            bar = f"{Fore.GREEN}{'█' * filled}{Fore.WHITE}{'░' * (bar_width - filled)}{Style.RESET_ALL}"
            sys.stdout.write(f"\r[{bar}] {int(percent * 100)}%")
            sys.stdout.flush()
            time.sleep(1)
        print()

        # Complete
        complete_resp = self.request_with_retry(
            'POST',
            f"{self.base_url}/ads/task/{task_id}/complete",
            headers=self.headers,
            json_data={
                "sessionId": session_id,
                "slotIndex": slot_index,
                "provider": provider,
                "clicked": True
            },
            timeout=30
        )

        if complete_resp is None:
            self.print_error("Timeout saat complete ads")
            return None

        if complete_resp.status_code == 200:
            try:
                data = complete_resp.json()
                if data.get('ok'):
                    reward_got = data.get('reward', 0)
                    coins = data.get('profile', {}).get('coins', 0)
                    xp = data.get('xp', {})

                    self.stats['total_watched'] += 1
                    self.stats['total_earned'] += reward_got

                    print(f"{Fore.GREEN}[✓] +{reward_got} koin (Total: {coins:,}){Style.RESET_ALL}")
                    print(f"{Fore.MAGENTA}[⭐] XP: {xp.get('xp', 0)}/{xp.get('xpMax', 0)}{Style.RESET_ALL}")

                    if data.get('profile'):
                        self.profile = data.get('profile')

                    return data
                else:
                    self.print_error(f"Gagal complete: {data.get('message')}")
                    return None
            except:
                self.print_error("Gagal parse complete response")
                return None
        else:
            self.print_error(f"Complete failed (HTTP {complete_resp.status_code})")
            return None

    def watch_ads(self, task_id, task_name, total_slots=10):
        print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[{task_id:02d}] {task_name.upper()}{Style.RESET_ALL}")

        slots_data = self.get_slots(task_id)
        if not slots_data.get('ok'):
            self.print_error("Gagal cek slot")
            print(f"{Fore.CYAN}[⏳] Next task dalam 3s...{Style.RESET_ALL}")
            time.sleep(3)
            return 0, 0

        ready = slots_data.get('ready', 0)
        total = slots_data.get('total', total_slots)
        per_slot = slots_data.get('perSlotReward', 0)

        if ready == 0:
            self.print_warning("Tidak ada slot siap")
            print(f"{Fore.CYAN}[⏳] Next task dalam 3s...{Style.RESET_ALL}")
            time.sleep(3)
            return 0, 0

        print(f"{Fore.GREEN}[✓] Slot     : {ready}/{total}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[💰] Reward   : {per_slot}/slot{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[💎] Potential: {per_slot * ready} Koin{Style.RESET_ALL}")

        watched = 0
        total_reward = 0

        for idx, slot in enumerate(slots_data.get('slots', [])):
            if slot['status'] != 'ready':
                continue

            slot_index = slot['index']
            provider = slot.get('provider', 'unknown')
            reward = slot.get('reward', per_slot)

            result = self.watch_ad(task_id, slot_index, ready, idx + 1, provider, reward)
            if result:
                watched += 1
                total_reward += result.get('reward', 0)
                if result.get('profile'):
                    self.profile = result.get('profile')

            if idx < ready - 1:
                print(f"{Fore.CYAN}[⏳] Delay 3 detik...{Style.RESET_ALL}")
                time.sleep(3)

        print(f"\n{Fore.GREEN}[✓] Selesai {task_name.upper()}: {watched} iklan, {total_reward} Koin{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[⏳] Next task dalam 3s...{Style.RESET_ALL}")
        time.sleep(3)

        return watched, total_reward

    # ==================== RUN ALL ====================
    def run_all(self):
        print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[🚜] AUTO FARMING{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[⏰] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")

        tasks = [
            {"id": 2, "name": "Adsgram", "slots": 10},
            {"id": 3, "name": "Monetag", "slots": 10},
            {"id": 7, "name": "Gigapub", "slots": 10},
            {"id": 9, "name": "Adexium", "slots": 10}
        ]

        total_watched = 0
        total_earned = 0

        for task in tasks:
            print(f"\n{Fore.MAGENTA}{'=' * 50}{Style.RESET_ALL}")
            watched, earned = self.watch_ads(task['id'], task['name'], task['slots'])
            total_watched += watched
            total_earned += earned

        # Summary
        print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[📊] FARMING SUMMARY{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[✓] Watched : {total_watched}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[💰] Earned  : {total_earned} Koin{Style.RESET_ALL}")
        if self.profile:
            print(f"{Fore.GREEN}[💰] Balance : {self.profile.get('coins', 0)} Koin{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[⏱️] Time    : {(datetime.now() - self.stats['start_time']).seconds // 60} menit{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")

    # ==================== MENU ====================
    def config_menu(self):
        print(f"\n{Fore.CYAN}🔐 Konfigurasi InitData{Style.RESET_ALL}")
        if self.init_data:
            print(f"{Fore.YELLOW}InitData saat ini: {Fore.WHITE}{self.init_data[:30]}...{Style.RESET_ALL}")
        new_init = input(f"\n{Fore.GREEN}Masukkan InitData baru (kosongkan untuk batal): {Style.RESET_ALL}").strip()
        if new_init:
            self.init_data = new_init
            self.print_success("InitData berhasil diatur")
        else:
            self.print_info("Tidak ada perubahan")

    def main_menu(self):
        while True:
            self.clear_screen()
            print(BANNER)

            print(f"{Fore.CYAN}  [1] 🚜 Start Farming")
            print(f"  [2] 🔐 Config InitData")
            print(f"  [0] 🚪 Exit")
            print(f"\n{Fore.YELLOW}================================================")
            print(f"  ➜ Pilih menu :{Style.RESET_ALL}", end="")

            choice = input().strip()

            if choice == "1":
                if not self.init_data:
                    self.print_warning("InitData belum diatur!")
                    self.config_menu()
                    if not self.init_data:
                        continue

                if not self.login():
                    input(f"\n{Fore.CYAN}Tekan Enter untuk kembali...{Style.RESET_ALL}")
                    continue

                self.run_all()
                input(f"\n{Fore.CYAN}Tekan Enter untuk kembali ke menu...{Style.RESET_ALL}")

            elif choice == "2":
                self.config_menu()
                input(f"\n{Fore.CYAN}Tekan Enter untuk kembali...{Style.RESET_ALL}")

            elif choice == "0":
                print(f"\n{Fore.GREEN}Terima kasih telah menggunakan bot ini! 🚀{Style.RESET_ALL}")
                break
            else:
                self.print_error("Pilihan tidak valid!")

# ==================== MAIN ====================
if __name__ == "__main__":
    try:
        bot = FarmingMatesBot()
        bot.main_menu()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.GREEN}Program dihentikan oleh user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Error: {e}{Style.RESET_ALL}")
        import traceback
        traceback.print_exc()
        input(f"\n{Fore.CYAN}Tekan Enter untuk keluar...{Style.RESET_ALL}")
