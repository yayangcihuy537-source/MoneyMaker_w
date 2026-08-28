import requests
import time
import json
import sys
import random
import os
from datetime import datetime

# ==================== COLOR CODES ====================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    WHITE = '\033[37m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    DIM = '\033[2m'

# ==================== CLEAR SCREEN ====================
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ==================== MAIN CLASS ====================
class NotBuxBot:
    def __init__(self, init_data):
        self.init_data = init_data
        self.base_url = "https://notbux.click/api"
        self.headers = self._build_headers()
        self.user_info = None
        self.total_claimed = 0
        self.running = True
        self.cycle = 0
        self.balance_coins = 0
        self.balance_ton = 0.0
        
        # Cooldown per ad (detik)
        self.bonus_ad_cooldowns = {
            'earn_adsgram': 10,
            'earn_monetag': 60,
            'earn_onclicka': 60,
            'earn_adexium': 60
        }
        self.last_claim_time = {}
        self.ad_watch_delay = (30, 35)
        self.ad_order = ['earn_adsgram', 'earn_monetag', 'earn_onclicka']
        self.ad_display = {
            'earn_adsgram': 'Adsgram',
            'earn_monetag': 'Monetag',
            'earn_onclicka': 'Onclicka',
            'earn_adexium': 'Adexium'
        }
    
    def _build_headers(self):
        return {
            "authorization": f"tma {self.init_data}",
            "user-agent": "Mozilla/5.0 (Linux; Android 12; K) AppleWebKit/537.36 Chrome/150.0.7871.181 Mobile Safari/537.36 Telegram-Android/12.9.2",
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "https://notbux.click",
            "referer": "https://notbux.click/",
            "sec-ch-ua-platform": '"Android"',
            "x-requested-with": "org.telegram.messenger"
        }
    
    def _api_request(self, endpoint, method='GET', data=None, retry=3):
        for attempt in range(retry):
            try:
                url = f"{self.base_url}{endpoint}"
                time.sleep(random.uniform(0.3, 0.8))
                if method == 'GET':
                    resp = requests.get(url, headers=self.headers, timeout=15)
                else:
                    resp = requests.post(url, headers=self.headers, json=data, timeout=15)
                if resp.status_code == 200:
                    return resp.json()
                elif resp.status_code == 429:
                    wait = 10 + (attempt * 5)
                    time.sleep(wait)
                    continue
                else:
                    time.sleep(2)
                    continue
            except:
                time.sleep(3)
                continue
        return None
    
    def get_user_info(self):
        data = self._api_request('/me')
        if data and data.get('status') == 'success':
            self.user_info = data.get('user', {})
            self.balance_coins = self.user_info.get('balance_coins', 0)
            self.balance_ton = self.user_info.get('balance_ton', 0.0)
            return self.user_info
        return None
    
    def get_earn_status(self):
        data = self._api_request('/earn/status')
        if data and data.get('status') == 'success':
            return data
        return None
    
    def get_ad_cooldown(self, status, ad_type):
        key = ad_type.replace('earn_', '') + '_cooldown'
        return status.get(key, 0)
    
    def get_ad_limit(self, status, ad_type):
        ads_data = status.get('ads', {})
        key = ad_type.replace('earn_', '')
        used = ads_data.get(key, 0)
        return max(0, 10 - used)
    
    def watch_ad(self, ad_type):
        # Cek cooldown lokal
        if ad_type in self.last_claim_time:
            elapsed = time.time() - self.last_claim_time[ad_type]
            needed = self.bonus_ad_cooldowns.get(ad_type, 30)
            if elapsed < needed:
                remaining = needed - elapsed
                print(f"{Colors.YELLOW}⏳ Cooldown {ad_type}: {remaining:.0f}s lagi{Colors.RESET}")
                time.sleep(remaining)
        
        duration = random.randint(self.ad_watch_delay[0], self.ad_watch_delay[1])
        print(f"{Colors.CYAN}🎬 Nonton {ad_type} selama {duration}s{Colors.RESET}")
        
        # Progress bar tanpa clear screen - pakai \r
        bar_len = 30
        for i in range(duration, 0, -1):
            if not self.running:
                return False
            prog = duration - i
            filled = int((prog / duration) * bar_len)
            bar = '█' * filled + '░' * (bar_len - filled)
            print(f"\r   [{Colors.GREEN}{bar}{Colors.RESET}] {i}s tersisa", end='')
            time.sleep(1)
        print(f"\r   [{Colors.GREEN}{'█' * bar_len}{Colors.RESET}] selesai!    ")
        
        # Kirim request claim
        data = self._api_request('/earn/watch_ad', 'POST', {'ad_type': ad_type})
        self.last_claim_time[ad_type] = time.time()
        
        if data and data.get('status') == 'success':
            reward = data.get('reward', 0)
            self.total_claimed += reward
            self.balance_coins += reward
            print(f"{Colors.GREEN}✅ +{reward} coins! Total: {self.balance_coins}{Colors.RESET}")
            return True
        else:
            print(f"{Colors.RED}❌ Gagal claim{Colors.RESET}")
            return False
    
    def claim_bonus_ads_cycle(self):
        claimed = 0
        status = self.get_earn_status()
        if not status:
            return claimed
        
        for ad_type in self.ad_order:
            if not self.running:
                break
            remaining = self.get_ad_limit(status, ad_type)
            if remaining <= 0:
                continue
            cooldown = self.get_ad_cooldown(status, ad_type)
            if cooldown > 0:
                print(f"{Colors.YELLOW}⏳ {ad_type} cooldown server {cooldown}s{Colors.RESET}")
                time.sleep(cooldown)
                continue
            if self.watch_ad(ad_type):
                claimed += 1
            time.sleep(random.uniform(1, 3))
            # Refresh status setelah watch
            status = self.get_earn_status()
            if not status:
                break
        return claimed
    
    def render_ui(self):
        clear_screen()
        # Header
        print(f"{Colors.CYAN}╭──────────────────────────────────────────────────────────────╮{Colors.RESET}")
        print(f"{Colors.CYAN}│{Colors.WHITE}                    🍀 NOTBUX BOT                           {Colors.CYAN}│{Colors.RESET}")
        print(f"{Colors.CYAN}│{Colors.WHITE}                  ⚡ AUTO EARN • v3.0                         {Colors.CYAN}│{Colors.RESET}")
        print(f"{Colors.CYAN}├──────────────────────────────────────────────────────────────┤{Colors.RESET}")
        
        # User
        print(f"{Colors.CYAN}│{Colors.WHITE} 👤 USER                                                       {Colors.CYAN}│{Colors.RESET}")
        uid = self.user_info.get('tg_id', 'N/A') if self.user_info else 'N/A'
        print(f"{Colors.CYAN}│{Colors.WHITE}    ID        : {Colors.YELLOW}{uid}{Colors.WHITE}{' ' * (47 - len(str(uid)))}{Colors.CYAN}│{Colors.RESET}")
        coins_str = f"{self.balance_coins:,}"
        print(f"{Colors.CYAN}│{Colors.WHITE}    💰 Coins  : {Colors.GREEN}{coins_str}{Colors.WHITE}{' ' * (47 - len(coins_str))}{Colors.CYAN}│{Colors.RESET}")
        ton_str = f"{self.balance_ton:.4f}"
        print(f"{Colors.CYAN}│{Colors.WHITE}    💎 TON    : {Colors.GREEN}{ton_str}{Colors.WHITE}{' ' * (47 - len(ton_str))}{Colors.CYAN}│{Colors.RESET}")
        print(f"{Colors.CYAN}├──────────────────────────────────────────────────────────────┤{Colors.RESET}")
        
        # Bonus Ads status
        print(f"{Colors.CYAN}│{Colors.WHITE} 📺 BONUS ADS                                                  {Colors.CYAN}│{Colors.RESET}")
        status = self.get_earn_status()
        for ad_type in self.ad_order:
            name = self.ad_display.get(ad_type, ad_type)
            if status:
                remaining = self.get_ad_limit(status, ad_type)
                cooldown = self.get_ad_cooldown(status, ad_type)
                if remaining > 0 and cooldown == 0:
                    color = Colors.GREEN
                    txt = f"{remaining} ads ready"
                elif remaining > 0 and cooldown > 0:
                    color = Colors.YELLOW
                    txt = f"{remaining} ads, cd {cooldown}s"
                else:
                    color = Colors.YELLOW
                    txt = "limit reached"
            else:
                color = Colors.YELLOW
                txt = "checking..."
            icon = '🟢' if color == Colors.GREEN else '🟡' if color == Colors.YELLOW else '🔴'
            print(f"{Colors.CYAN}│{Colors.WHITE}    {icon} {name:<10} {txt:<20}{' ' * (47 - len(name) - 10 - len(txt))}{Colors.CYAN}│{Colors.RESET}")
        print(f"{Colors.CYAN}├──────────────────────────────────────────────────────────────┤{Colors.RESET}")
        
        # Session
        print(f"{Colors.CYAN}│{Colors.WHITE} 📊 SESSION                                                    {Colors.CYAN}│{Colors.RESET}")
        print(f"{Colors.CYAN}│{Colors.WHITE}    Cycle       : #{Colors.YELLOW}{self.cycle}{Colors.WHITE}{' ' * (47 - len(str(self.cycle)))}{Colors.CYAN}│{Colors.RESET}")
        claimed_str = f"+{self.total_claimed} coins"
        print(f"{Colors.CYAN}│{Colors.WHITE}    Claimed     : {Colors.GREEN}{claimed_str}{Colors.WHITE}{' ' * (47 - len(claimed_str))}{Colors.CYAN}│{Colors.RESET}")
        status_icon = '🟢 RUNNING' if self.running else '🔴 STOPPED'
        color_status = Colors.GREEN if self.running else Colors.RED
        print(f"{Colors.CYAN}│{Colors.WHITE}    Status      : {color_status}{status_icon}{Colors.WHITE}{' ' * (47 - len(status_icon))}{Colors.CYAN}│{Colors.RESET}")
        print(f"{Colors.CYAN}├──────────────────────────────────────────────────────────────┤{Colors.RESET}")
        
        # Watching - idle state
        print(f"{Colors.CYAN}│{Colors.WHITE} 🎬 IDLE - menunggu iklan...{' ' * (47 - 28)}{Colors.CYAN}│{Colors.RESET}")
        print(f"{Colors.CYAN}│{Colors.WHITE}    [{' ' * 30}] {' ' * 3}{Colors.CYAN}│{Colors.RESET}")
        print(f"{Colors.CYAN}│{Colors.WHITE}    Reward     : -{Colors.WHITE}{' ' * (47 - 14)}{Colors.CYAN}│{Colors.RESET}")
        print(f"{Colors.CYAN}╰──────────────────────────────────────────────────────────────╯{Colors.RESET}")
    
    def run(self):
        self.get_user_info()
        while self.running:
            self.cycle += 1
            self.render_ui()
            
            # Claim ads
            status = self.get_earn_status()
            if not status:
                time.sleep(5)
                continue
            
            # Update user info
            self.get_user_info()
            
            print(f"\n{Colors.YELLOW}🚀 Siklus #{self.cycle} - mulai claim...{Colors.RESET}")
            claimed = self.claim_bonus_ads_cycle()
            print(f"{Colors.GREEN}✅ Selesai siklus #{self.cycle}, total +{self.total_claimed} coins{Colors.RESET}")
            
            # Cek apakah semua iklan habis
            status = self.get_earn_status()
            all_done = True
            if status:
                for ad_type in self.ad_order:
                    remaining = self.get_ad_limit(status, ad_type)
                    if remaining > 0:
                        all_done = False
                        break
                    # Cek cooldown lokal
                    if ad_type in self.last_claim_time:
                        elapsed = time.time() - self.last_claim_time[ad_type]
                        needed = self.bonus_ad_cooldowns.get(ad_type, 30)
                        if elapsed < needed:
                            all_done = False
                            break
            
            if all_done:
                print(f"{Colors.GREEN}✅ Semua iklan sudah habis! Bot berhenti.{Colors.RESET}")
                self.running = False
                break  # keluar dari loop
            else:
                time.sleep(random.uniform(2, 5))
    
    def stop(self):
        self.running = False

def get_init_data():
    clear_screen()
    print(f"{Colors.CYAN}╔════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.CYAN}║{Colors.WHITE}            NOTBUX BOT - LOGIN              {Colors.CYAN}║{Colors.RESET}")
    print(f"{Colors.CYAN}╚════════════════════════════════════════════════╝{Colors.RESET}")
    print(f"\n{Colors.YELLOW}Masukkan init data Telegram:{Colors.RESET}")
    print(f"  {Colors.DIM}(query_id=xxx&user=xxx&auth_date=xxx&signature=xxx&hash=xxx){Colors.RESET}\n")
    data = input(f"{Colors.GREEN}🔑 Init data: {Colors.RESET}").strip()
    if not data:
        print(f"{Colors.RED}❌ Tidak boleh kosong!{Colors.RESET}")
        return None
    if not data.startswith('query_id='):
        print(f"{Colors.RED}⚠️ Harus dimulai dengan 'query_id='{Colors.RESET}")
        return None
    return data

def main():
    try:
        data = get_init_data()
        if not data:
            return
        bot = NotBuxBot(data)
        bot.run()
        print(f"{Colors.CYAN}Bot selesai. Sampai jumpa!{Colors.RESET}")
    except KeyboardInterrupt:
        print(f"\n{Colors.RED}🛑 Dihentikan user{Colors.RESET}")
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")

if __name__ == "__main__":
    main()
