"""
Shared test helpers for Rently API test suite.
"""
import requests
from colorama import init, Fore, Style

init(autoreset=True)

BASE_URL = "http://127.0.0.1:5000"
H_JSON = {"Content-Type": "application/json"}


class TestReport:
    """Collects test results for reporting."""
    
    def __init__(self, section_name):
        self.section = section_name
        self.results = []
        self.passed = 0
        self.failed = 0

    def log_pass(self, msg):
        self.passed += 1
        self.results.append({"status": "PASS", "message": msg})
        print(f"  {Fore.GREEN}✓ PASS{Style.RESET_ALL} {msg}")

    def log_fail(self, msg):
        self.failed += 1
        self.results.append({"status": "FAIL", "message": msg})
        print(f"  {Fore.RED}✗ FAIL{Style.RESET_ALL} {msg}")

    def check(self, condition, pass_msg, fail_msg):
        if condition:
            self.log_pass(pass_msg)
        else:
            self.log_fail(fail_msg)

    @property
    def total(self):
        return self.passed + self.failed

    @property
    def percentage(self):
        return (self.passed / self.total * 100) if self.total > 0 else 0

    def summary(self):
        return {
            "section": self.section,
            "total": self.total,
            "passed": self.passed,
            "failed": self.failed,
            "percentage": round(self.percentage, 1),
            "results": self.results
        }

    def print_summary(self):
        color = Fore.GREEN if self.percentage >= 90 else (Fore.YELLOW if self.percentage >= 70 else Fore.RED)
        print(f"\n  {color}[{self.section}] {self.passed}/{self.total} passed ({self.percentage:.0f}%){Style.RESET_ALL}")


def auth_header(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def auth_header_no_json(token):
    return {"Authorization": f"Bearer {token}"}


def login(identifier, password):
    r = requests.post(f"{BASE_URL}/auth/login", headers=H_JSON, json={
        "identifier": identifier, "password": password
    })
    if r.status_code == 200:
        return r.json().get("access_token"), r.json().get("user", {}).get("id")
    return None, None


def print_section(title):
    print(f"\n{Fore.CYAN}{'═' * 60}")
    print(f"  {title}")
    print(f"{'═' * 60}{Style.RESET_ALL}")
