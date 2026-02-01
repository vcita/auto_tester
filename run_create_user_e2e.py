#!/usr/bin/env python3
"""
End-to-end test for the create_user function.

Usage (from project root):
  python run_create_user_e2e.py

Uses config.yaml for base_url and target.auth.password. New user email is generated (itzik+autotest.e2e.<timestamp>@vcita.com).
"""
import sys
import time
import yaml
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright


def _load_config():
    path = project_root / "config.yaml"
    if not path.exists():
        raise ValueError("config.yaml not found.")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def main():
    config = _load_config()
    target = config.get("target") or {}
    auth = target.get("auth") or {}
    password = auth.get("password") or "vcita123"
    email = f"itzik+autotest.e2e.{int(time.time())}@vcita.com"
    phone = "0526111116"

    def out(msg, end="\n"):
        print(msg, end=end, flush=True)
    out("=" * 60)
    out("Create user E2E test")
    out("=" * 60)
    out(f"  Email:  {email}")
    out(f"  Phone:  {phone}")
    out("  (Signup + first-login onboarding)")
    out("=" * 60)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
        )
        bypass_string = "#vUC5wTG98Hq5=BW+D_1c29744b-38df-4f40-8830-a7558ccbfa6b"
        custom_user_agent = (
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 {bypass_string}"
        )
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
            timezone_id="America/New_York",
            user_agent=custom_user_agent,
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        page = context.new_page()

        try:
            from tests._functions.create_user.test import fn_create_user

            run_context = {}
            fn_create_user(
                page,
                run_context,
                email=email,
                phone=phone,
                password=password,
            )
            out("\n" + "=" * 60)
            out("[PASS] Create user E2E completed successfully.")
            out("=" * 60)
            return 0
        except Exception as e:
            out(f"\n[FAIL] {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return 1
        finally:
            browser.close()


if __name__ == "__main__":
    sys.exit(main())
