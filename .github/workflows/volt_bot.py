import requests
import json
import time
import random
import hashlib
import base64
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

class VoltAPIBot:
    def __init__(self, base_url: str = "https://volt.crowntasks.xyz"):
        self.base_url = base_url
        self.session = requests.Session()
        
        # YOUR REFERRER ID - FIXED
        self.REFERRER_ID = "7807541360"
        
        self.common_headers = {
            "Connection": "keep-alive",
            "sec-ch-ua-platform": "Android",
            "sec-ch-ua": '"Not)A;Brand";v="8", "Chromium";v="138", "Android WebView";v="138"',
            "Content-Type": "application/json",
            "sec-ch-ua-mobile": "?1",
            "Accept": "*/*",
            "X-Requested-With": "org.telegram.messenger.web",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "en,id-ID;q=0.9,id;q=0.8,en-US;q=0.7"
        }
        
        self.first_names = [
            "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Kavya", 
            "Ananya", "Diya", "Pari", "Aadhya", "Rohan", "Riya", "Aisha",
            "Aryan", "Ishaan", "Naina", "Kiran", "Neha", "Rahul"
        ]
        
        self.last_names = [
            "Sharma", "Verma", "Patel", "Singh", "Rao", "Reddy", "Gupta",
            "Kumar", "Das", "Joshi", "Mehta", "Shah", "Desai", "Nair"
        ]
        
        # Track stats
        self.success_count = 0
        self.fail_count = 0
        self.total_tokens = 0
        self.lock = threading.Lock()

    def generate_wallet_address(self, user_id: int) -> str:
        """Generate valid TON wallet address"""
        seed = str(user_id) + str(time.time()) + str(random.randint(1, 999999))
        hash_obj = hashlib.sha256(seed.encode())
        hash_bytes = hash_obj.digest()
        b64 = base64.b64encode(hash_bytes).decode('utf-8')
        cleaned = ''.join(c for c in b64 if c.isalnum())
        prefix = random.choice(['EQ', 'UQ'])
        address = prefix + cleaned[:46]
        while len(address) < 48:
            address += random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')
        return address[:48]

    def generate_telegram_user(self) -> Dict:
        """Generate realistic Telegram user"""
        user_id = random.randint(7000000000, 7999999999)
        return {
            "id": user_id,
            "first_name": random.choice(self.first_names),
            "last_name": random.choice(self.last_names),
            "language_code": random.choice(["en", "id", "hi", "ta", "te"]),
            "allows_write_to_pm": True,
            "photo_url": f"https://t.me/i/userpic/320/{''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=40))}.svg"
        }

    def get_headers(self) -> Dict:
        """Get headers with random User-Agent"""
        headers = self.common_headers.copy()
        mobile_models = ["Samsung SM-A305F", "Xiaomi Redmi Note 9", "OnePlus Nord", "Realme 7", "Vivo Y20"]
        headers["User-Agent"] = f"Mozilla/5.0 (Linux; Android {random.choice(['9','10','11'])}; {random.choice(mobile_models)}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.179 Mobile Safari/537.36 Telegram-Android/12.6.4"
        headers["Referer"] = f"https://volt.crowntasks.xyz/?startapp=ref_{self.REFERRER_ID}"
        return headers

    def sync_user(self, user_data: Dict) -> Dict:
        """Sync user with Volt API - ALWAYS uses your referrer ID"""
        payload = {
            "telegramUser": user_data,
            "referredBy": self.REFERRER_ID
        }
        try:
            response = self.session.post(
                f"{self.base_url}/api/user/sync", 
                json=payload, 
                headers=self.get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {"success": True}
            return {"success": False}
        except:
            return {"success": False}

    def sync_wallet(self, user_id: int, wallet_address: str) -> Dict:
        """Sync wallet with Volt API"""
        payload = {
            "telegramId": user_id,
            "walletAddress": wallet_address,
            "walletBalance": 0
        }
        try:
            response = self.session.post(
                f"{self.base_url}/api/user/wallet",
                json=payload,
                headers=self.get_headers(),
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return {"success": True}
            return {"success": False}
        except:
            return {"success": False}

    def create_account(self, account_num: int) -> bool:
        """Create one account with wallet - ALWAYS uses your referrer"""
        user = self.generate_telegram_user()
        wallet = self.generate_wallet_address(user["id"])
        
        # Sync user
        user_sync = self.sync_user(user)
        
        # Sync wallet if user sync successful
        if user_sync["success"]:
            wallet_sync = self.sync_wallet(user["id"], wallet)
            if wallet_sync["success"]:
                with self.lock:
                    self.success_count += 1
                    self.total_tokens += 25
                return True
        with self.lock:
            self.fail_count += 1
        return False

    def run_fast(self, count: int = 400, max_workers: int = 700) -> None:
        """Run bot at MAXIMUM SPEED - NO JSON SAVING"""
        print(f"\n{'='*60}")
        print(f"🚀 STARTING BOT - Creating {count} accounts")
        print(f"📌 REFERRER ID: {self.REFERRER_ID}")
        print(f"⚡ Workers: {max_workers} parallel threads")
        print(f"⚡ NO JSON SAVING - MAX SPEED")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # Create all threads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            futures = {executor.submit(self.create_account, i): i for i in range(count)}
            
            # Track progress
            completed = 0
            for future in as_completed(futures):
                completed += 1
                
                # Update progress every 10 accounts
                if completed % 10 == 0 or completed == count:
                    elapsed = time.time() - start_time
                    speed = completed / elapsed if elapsed > 0 else 0
                    tokens = self.total_tokens
                    
                    # Clear line and show progress
                    progress_bar = "█" * int((completed / count) * 40)
                    print(f"\r📊 Progress: [{progress_bar:<40}] {completed}/{count} | Tokens: {tokens} | Speed: {speed:.1f} acc/s", end="")
        
        elapsed = time.time() - start_time
        
        # Final Summary
        print(f"\n\n{'='*60}")
        print(f"📊 FINAL SUMMARY:")
        print(f"   ✅ Success: {self.success_count}/{count}")
        print(f"   ❌ Failed: {self.fail_count}")
        print(f"   🪙 Total tokens: {self.total_tokens}")
        print(f"   ⏱️  Time: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"   ⚡ Speed: {count/elapsed:.2f} accounts/sec")
        print(f"   📌 Referrer: {self.REFERRER_ID}")
        print(f"{'='*60}\n")
        
        # Show what you earned
        print(f"🎯 TARGET: 10,000 tokens")
        print(f"✅ EARNED: {self.total_tokens} tokens")
        if self.total_tokens >= 10000:
            print(f"🎉 ACHIEVED! You got {self.total_tokens} tokens!")
        else:
            remaining = 10000 - self.total_tokens
            need = remaining // 25 + 1
            print(f"📌 Need {remaining} more tokens ({need} more accounts)")
        print()

# QUICK START - NO JSON SAVING!
if __name__ == "__main__":
    bot = VoltAPIBot()
    
    # Run 400 accounts = 10,000 tokens in ~10-15 seconds!
    bot.run_fast(count=40000, max_workers=100)
    
    # Show final stats
    stats = {
        "success": bot.success_count,
        "failed": bot.fail_count,
        "tokens": bot.total_tokens,
        "referrer": bot.REFERRER_ID
    }
    print(f"📈 FINAL STATS: {json.dumps(stats, indent=2)}")
