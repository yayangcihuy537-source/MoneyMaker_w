#!/usr/bin/env python3
"""
RapidGame AutoFaucet - Dashboard Email Asli (Banner Custom)
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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

COOLDOWN = {"usdt": 12, "trx": 15}
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


def get_user_input() -> Dict[str, Any]:
    console.print(Panel.fit("[bold cyan]RapidGame AutoFaucet - Dashboard[/bold cyan]"))
    while True:
        email = console.input("[bold]Masukkan email FaucetPay: [/bold]").strip()
        if "@" in email and "." in email:
            break
        console.print("[red]Email tidak valid.[/red]")
    console.print("\n[bold]Pilih faucet:[/bold]")
    console.print("  1. USDT")
    console.print("  2. TRX")
    console.print("  3. Keduanya")
    while True:
        p = console.input("[bold]Pilihan (1/2/3): [/bold]").strip()
        if p == "1":
            faucets = ["usdt"]
            break
        elif p == "2":
            faucets = ["trx"]
            break
        elif p == "3":
            faucets = ["usdt", "trx"]
            break
        else:
            console.print("[red]Pilihan tidak valid.[/red]")
    return {"email": email, "faucets": faucets}


class RenderCoins:
    def __init__(self, email: str, faucets: List[str]):
        self.email = email
        self.faucets = faucets
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
        self.stats: Dict[str, Dict[str, Any]] = {
            c: {
                "balance": "-",
                "claims_left": "-",
                "cooldown": COOLDOWN[c],
                "next": 0,
                "total_claims": 0,
                "total_reward": 0.0,
                "next_claim_time": 0,
            } for c in faucets
        }
        self.lock = threading.Lock()

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

    def _get_page(self, url: str) -> Optional[Tuple[BeautifulSoup, str]]:
        try:
            r = self.session.get(url, timeout=REQUEST_TIMEOUT)
            if r.status_code == 403:
                time.sleep(120)
                return None, ""
            r.raise_for_status()
            return BeautifulSoup(r.text, "html.parser"), r.text
        except Exception:
            return None, ""

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
            r = self.session.post(url, data=data, timeout=REQUEST_TIMEOUT, allow_redirects=True, headers=headers)
            return True, r.text, r.status_code
        except Exception:
            return False, "", 0

    def _extract_swal_error(self, html: str) -> Optional[str]:
        pattern = r"Swal\.fire\(\{[^}]*icon:\s*'error'[^}]*html:\s*'([^']+)'"
        match = re.search(pattern, html, re.DOTALL)
        if match:
            return match.group(1)
        pattern2 = r"Swal\.fire\(\{[^}]*html:\s*'([^']+)'"
        match2 = re.search(pattern2, html, re.DOTALL)
        if match2:
            return match2.group(1)
        return None

    def _extract_balance(self, html: str, currency: str) -> str:
        m = re.search(r'<div class="reward">\+([\d.]+)\s*<span>' + currency.upper(), html)
        if m:
            return f"+{m.group(1)} {currency.upper()}"
        return "-"

    def _extract_amount(self, html: str, currency: str) -> float:
        m = re.search(r'<div class="reward">\+([\d.]+)\s*<span>' + currency.upper(), html)
        if m:
            return float(m.group(1))
        return 0.0

    def _extract_claims_left(self, html: str) -> str:
        m = re.search(r'(\d+)/(\d+)\s*</p>\s*<p[^>]*>claims left', html)
        if m:
            return f"{m.group(1)}/{m.group(2)}"
        return "-"

    def _add_history(self, coin: str, amount: str):
        with self.lock:
            line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  {amount}  {coin.upper()}"
            self.history.append(line)
            if len(self.history) > 10:
                self.history.pop(0)

    def _load_token(self, currency: str) -> Optional[Dict[str, str]]:
        url = f"{BASE_URL}/faucet/currency/{currency}"
        soup, html = self._get_page(url)
        if not soup:
            return None

        with self.lock:
            self.stats[currency]["balance"] = self._extract_balance(html, currency)
            self.stats[currency]["claims_left"] = self._extract_claims_left(html)

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

    def claim_loop(self):
        if not self.login():
            return

        while True:
            for currency in self.faucets:
                token_data = self._load_token(currency)
                if not token_data:
                    time.sleep(10)
                    continue

                cooldown = COOLDOWN[currency]
                with self.lock:
                    self.stats[currency]["next_claim_time"] = time.time() + cooldown
                for i in range(cooldown, 0, -1):
                    with self.lock:
                        self.stats[currency]["next"] = i
                    time.sleep(1)

                data = {
                    "auto_faucet_token": token_data["auto_faucet_token"],
                    "csrf_token_name": token_data["csrf_token_name"],
                    "token": token_data["token"],
                    "claim_mode": "manual",
                    "website": "",
                }
                verify_url = f"{BASE_URL}/faucet/verify/{currency}"
                ok, resp, status = self._post_form(verify_url, data, referer=token_data["referer"])
                if not ok:
                    time.sleep(10)
                    continue
                if status == 403:
                    time.sleep(120)
                    continue

                if "Success" in resp or "sent to your FaucetPay" in resp:
                    self.total_claims += 1
                    amount = self._extract_amount(resp, currency)
                    with self.lock:
                        self.stats[currency]["total_claims"] += 1
                        self.stats[currency]["total_reward"] += amount
                    self._add_history(currency, self.stats[currency]["balance"])
                else:
                    error_msg = self._extract_swal_error(resp)
                    if error_msg and "wait" in error_msg.lower():
                        time.sleep(COOLDOWN[currency])
                    else:
                        time.sleep(30)

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
            f"[bold cyan]RapidGame[/bold cyan] | Email: {self.email} | Total Claims: {self.total_claims}",
            border_style="cyan"
        ))

        table = Table(title="Faucet Status", border_style="blue")
        table.add_column("Coin", style="cyan")
        table.add_column("Balance", style="green")
        table.add_column("Claims Left", style="yellow")
        table.add_column("Cooldown", style="magenta")
        table.add_column("Next", style="red")
        table.add_column("Total Reward", style="white")

        now = time.time()
        for c in self.faucets:
            s = self.stats[c]
            next_sec = max(0, int(s["next_claim_time"] - now))
            next_str = f"{next_sec}s" if next_sec > 0 else "Ready"
            reward_str = f"{s['total_reward']:.8f} {c.upper()}"
            table.add_row(
                c.upper(),
                s["balance"],
                s["claims_left"],
                f"{s['cooldown']}s",
                next_str,
                reward_str,
            )

        hist_text = Text()
        hist_text.append("── History (last 10) ──\n", style="bold cyan")
        for line in self.history[-10:]:
            hist_text.append(line + "\n")

        layout["body"].update(Group(table, hist_text))
        return layout


def main():
    clear_screen()
    cfg = get_user_input()
    bot = RenderCoins(cfg["email"], cfg["faucets"])
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
