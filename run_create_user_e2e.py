#!/usr/bin/env python3
"""
End-to-end test for the create_user function.

Usage (from project root):
  python run_create_user_e2e.py

  Optional env:
  - VCITA_CREATE_USER_EMAIL: email for signup (default: itzik+autotest.e2e.<timestamp>@vcita.com)
  - VCITA_TEST_PHONE: phone for Welcome dialog (default: 0526111116 for Israel)
"""
import os
import sys
import time

from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright


def main():
    email = os.environ.get(
        "VCITA_CREATE_USER_EMAIL",
        f"itzik+autotest.e2e.{int(time.time())}@vcita.com",
    )
    phone = os.environ.get("VCITA_TEST_PHONE", "0526111116")
    password = os.environ.get("VCITA_TEST_PASSWORD", "vcita123")

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
