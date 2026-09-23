#!/usr/bin/env python3
"""
RapidGame AutoFaucet - USDT Only (Dashboard + Banner)
"""

import os
import re
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

import requests
from bs4 import BeautifulSoup
from rich.console import Console, Group
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich.align import Align

BASE_URL = "https://www.rapidgame.fun"
REQUEST_TIMEOUT = 20
USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 10; K) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/127.0.0.0 Mobile Safari/537.36"
)

# Cooldown USDT = 12s dari HTML + buffer
COOLDOWN_USDT = 15
console = Console()

BANNER = r"""
██████╗  █████╗ ██████╗ ██╗██████╗                  
██╔══██╗██╔══██╗██╔══██╗██║██╔══██╗                 
██████╔╝███████║██████╔╝██║██║  ██║                 
██╔══██╗██╔══██║██╔═══╝ ██║██║  ██║                 
██║  ██║██║  ██║██║     ██║██████╔╝                 
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝ https://t.me/gratisancrypt                 
                                                    
                 ██████╗  █████╗ ███╗   ███╗███████╗
                ██╔════╝ ██╔══██╗████╗ ████║██╔════╝
                ██║  ███╗███████║██╔████╔██║█████╗  
                ██║   ██║██╔══██║██║╚██╔╝██║██╔══╝  
                ╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗
                 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝
"""


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def get_user_input() -> str:
    console.print(Panel.fit("[bold cyan]RapidGame AutoFaucet — USDT[/bold cyan]"))
    while True:
        email = console.input("[bold]Masukkan email FaucetPay: [/bold]").strip()
        if "@" in email and "." in email:
            return email
        console.print("[red]Email tidak valid.[/red]")


class RenderCoins:
    def __init__(self, email: str):
        self.email = email
        self.currency = "usdt"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })
        self.logged_in = False
        self.total_claims = 0
        self.history: List[str] = []
        self.stats = {
            "balance": "-",
            "claims_left": "-",
            "cooldown": COOLDOWN_USDT,
            "next": 0,
            "total_claims": 0,
            "total_reward": 0.0,
            "next_claim_time": 0,
            "last_status": "idle",
        }
        self.lock = threading.Lock()

    # ─── LOGIN ───
    def login(self) -> bool:
        url = f"{BASE_URL}/auth/login"
        try:
            r = self.session.get(url, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            csrf_input = soup.find("input", {"name": "csrf_token_name"})
            if not csrf_input:
                return False
            csrf = csrf_input.get("value")

            data = {"wallet": self.email, "csrf_token_name": csrf}
            r = self.session.post(url, data=data, timeout=REQUEST_TIMEOUT, allow_redirects=True)
            r.raise_for_status()

            if "logout" in r.text.lower() or "dashboard" in r.url.lower() or "MultiCoin" in r.text:
                self.logged_in = True
                return True
            return False
        except Exception:
            return False

    # ─── GET ───
    def _get_page(self, url: str) -> Tuple[Optional[BeautifulSoup], str]:
        try:
            r = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if r.status_code == 403:
                time.sleep(120)
                return None, ""
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser"), r.text
        except Exception:
            return None, ""

    # ─── POST ───
    def _post_form(self, url: str, data: Dict[str, Any], referer: str = "") -> Tuple[bool, str, int]:
        headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": BASE_URL,
            "Referer": referer,
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        try:
            r = self.session.post(url, data=data, timeout=REQUEST_TIMEOUT,
                                  allow_redirects=True, headers=headers)
            return True, r.text, r.status_code
        except Exception:
            return False, "", 0

    # ─── PARSERS ───
    def _extract_swal(self, html: str) -> Tuple[Optional[str], Optional[str]]:
        """Return (icon, message). icon: 'success' / 'error' / None"""
        pattern = r"Swal\.fire\(\{[^}]*?(?:icon:\s*'([^']+)'[^}]*?)?html:\s*'([^']+)'"
        match = re.search(pattern, html, re.DOTALL)
        if match:
            return match.group(1), match.group(2)

        m = re.search(r'([\d.]+)\s+([A-Z]+)\s+has been sent', html)
        if m:
            return "success", f"{m.group(1)} {m.group(2)} has been sent"

        m2 = re.search(r"icon:\s*'error'[^}]*html:\s*'([^']+)'", html, re.DOTALL)
        if m2:
            return "error", m2.group(1)

        return None, None

    def _extract_amount(self, html: str) -> float:
        cur = self.currency.upper()
        m = re.search(r'([\d.]+)\s+' + cur + r'\s+has been sent', html)
        if m:
            return float(m.group(1))
        m = re.search(r'Claim\s+<strong>([\d.]+)\s+' + cur, html)
        if m:
            return float(m.group(1))
        return 0.0

    def _extract_balance(self, html: str) -> str:
        cur = self.currency.upper()
        m = re.search(r'Claim\s+<strong>([\d.]+)\s+' + cur, html)
        if m:
            return f"{m.group(1)} {cur}"
        return "-"

    def _extract_claims_left(self, html: str) -> str:
        m = re.search(r'(\d+)\s*/\s*(\d+)\s*claims', html, re.IGNORECASE)
        if m:
            return f"{m.group(1)}/{m.group(2)}"
        m = re.search(r'var\s+wait\s*=\s*Math\.max\(0,\s*Number\((\d+)\)\)', html)
        if m:
            return f"{m.group(1)}s wait"
        return "-"

    def _add_history(self, amount_str: str):
        with self.lock:
            line = f"{datetime.now().strftime('%H:%M:%S')}  {amount_str}"
            self.history.append(line)
            if len(self.history) > 10:
                self.history.pop(0)

    # ─── LOAD TOKEN ───
    def _load_token(self) -> Optional[Dict[str, str]]:
        url = f"{BASE_URL}/faucet/currency/{self.currency}"
        soup, html = self._get_page(url)
        if not soup or not html:
            return None

        with self.lock:
            self.stats["balance"] = self._extract_balance(html)
            self.stats["claims_left"] = self._extract_claims_left(html)

        auto_token = soup.find("input", {"name": "auto_faucet_token"})
        token = soup.find("input", {"name": "token"})
        csrf = soup.find("input", {"name": "csrf_token_name"})
        if not (auto_token and token and csrf):
            return None
        return {
            "auto_faucet_token": auto_token.get("value"),
            "token": token.get("value"),
            "csrf_token_name": csrf.get("value"),
            "referer": url,
        }

    # ─── CLAIM LOOP ───
    def claim_loop(self):
        if not self.login():
            with self.lock:
                self.stats["last_status"] = "login failed"
            return

        while True:
            token_data = self._load_token()
            if not token_data:
                with self.lock:
                    self.stats["last_status"] = "no token"
                time.sleep(10)
                continue

            cooldown = COOLDOWN_USDT
            with self.lock:
                self.stats["next_claim_time"] = time.time() + cooldown
                self.stats["last_status"] = "cooldown"
            for i in range(cooldown, 0, -1):
                with self.lock:
                    self.stats["next"] = i
                time.sleep(1)

            # POST verify — cuma 3 field
            data = {
                "auto_faucet_token": token_data["auto_faucet_token"],
                "csrf_token_name": token_data["csrf_token_name"],
                "token": token_data["token"],
            }
            verify_url = f"{BASE_URL}/faucet/verify/{self.currency}"
            ok, resp, status = self._post_form(verify_url, data, referer=token_data["referer"])

            if not ok:
                with self.lock:
                    self.stats["last_status"] = "post error"
                time.sleep(10)
                continue

            if status == 403:
                with self.lock:
                    self.stats["last_status"] = "403 blocked"
                time.sleep(120)
                continue

            icon, msg = self._extract_swal(resp)

            if icon == "success" or (msg and "has been sent" in msg):
                self.total_claims += 1
                amount = self._extract_amount(resp)
                with self.lock:
                    self.stats["total_claims"] += 1
                    self.stats["total_reward"] += amount
                    self.stats["last_status"] = "ok"
                amount_str = f"+{amount:.8f} USDT" if amount else "+? USDT"
                self._add_history(amount_str)

            elif icon == "error" or msg:
                with self.lock:
                    self.stats["last_status"] = (msg or "error")[:30]
                low = (msg or "").lower()
                if "wait" in low or "limit" in low or "too fast" in low:
                    time.sleep(COOLDOWN_USDT + 5)
                else:
                    time.sleep(20)
            else:
                with self.lock:
                    self.stats["last_status"] = "unknown resp"
                time.sleep(15)

    # ─── DASHBOARD ───
    def make_dashboard(self) -> Layout:
        layout = Layout()
        layout.split_column(
            Layout(name="banner", size=14),
            Layout(name="header", size=3),
            Layout(name="body"),
        )

        banner_text = Text(BANNER, style="bold cyan")
        layout["banner"].update(Align.center(banner_text))

        layout["header"].update(Panel.fit(
            f"[bold cyan]RapidGame USDT[/bold cyan] | Email: {self.email} | "
            f"Total Claims: {self.total_claims}",
            border_style="cyan"
        ))

        table = Table(title="USDT Faucet Status", border_style="blue")
        table.add_column("Coin", style="cyan")
        table.add_column("Reward", style="green")
        table.add_column("Claims Left", style="yellow")
        table.add_column("Cooldown", style="magenta")
        table.add_column("Next", style="red")
        table.add_column("Total Reward", style="white")
        table.add_column("Status", style="yellow")

        now = time.time()
        s = self.stats
        next_sec = max(0, int(s["next_claim_time"] - now))
        next_str = f"{next_sec}s" if next_sec > 0 else "Ready"
        reward_str = f"{s['total_reward']:.8f} USDT"
        table.add_row(
            "USDT",
            s["balance"],
            s["claims_left"],
            f"{s['cooldown']}s",
            next_str,
            reward_str,
            s["last_status"][:20],
        )

        hist_text = Text()
        hist_text.append("── History (last 10) ──\n", style="bold cyan")
        if self.history:
            for line in self.history[-10:]:
                hist_text.append(line + "\n")
        else:
            hist_text.append("(belum ada claim)\n", style="dim")

        layout["body"].update(Group(table, hist_text))
        return layout


def main():
    clear_screen()
    email = get_user_input()
    bot = RenderCoins(email)
    thread = threading.Thread(target=bot.claim_loop, daemon=True)
    thread.start()

    clear_screen()
    with Live(bot.make_dashboard(), refresh_per_second=2, screen=True) as live:
        try:
            while True:
                live.update(bot.make_dashboard())
                time.sleep(0.5)
        except KeyboardInterrupt:
            clear_screen()
            console.print("[bold red]Dihentikan.[/bold red]")


if __name__ == "__main__":
    main()
