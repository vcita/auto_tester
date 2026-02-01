#!/usr/bin/env python3
"""
Standalone debug script skeleton for speeding up test debugging.

Usage:
  Copy this file to debug_<category>_<test_name>.py (e.g. debug_events_remove_attendee.py).
  Set TARGET_URL and fill in STEP_2 ... STEP_N from the failing test's test.py.
  Put the failing action/assertion in DEBUG_FOCUS with extra prints or variants.
  Run from project root: python debug_<category>_<test_name>.py

Uses same browser/context as the test runner for consistent behaviour.
"""

from playwright.sync_api import sync_playwright
import os
import sys
import yaml
from pathlib import Path

# Add project root to path to import login function
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from tests._functions.login.test import fn_login


def _load_credentials():
    """Load username/password from config.yaml only. No env or default fallbacks."""
    config_path = project_root / "config.yaml"
    if not config_path.exists():
        raise ValueError("config.yaml not found. Create it with target.auth.username and target.auth.password.")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    auth = (config.get("target") or {}).get("auth") or {}
    username = auth.get("username")
    password = auth.get("password")
    if not username or not password:
        raise ValueError(
            "Set target.auth.username and target.auth.password in config.yaml."
        )
    return username, password


# -----------------------------------------------------------------------------
# CONFIGURE FOR YOUR TEST (replace these)
# -----------------------------------------------------------------------------
# Page to open after login (e.g. event URL, dashboard, settings).
# Get from heal request, .context/*.json, or test's starting URL.
TARGET_URL = "https://app.vcita.com/app/dashboard"  # Example; set per test


def run_debug():
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(
            headless=False,
            channel='chrome',
            args=['--disable-blink-features=AutomationControlled'],
        )

        # Same settings as test runner
        bypass_string = "#vUC5wTG98Hq5=BW+D_1c29744b-38df-4f40-8830-a7558ccbfa6b"
        custom_user_agent = (
            f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 {bypass_string}"
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-US',
            timezone_id='America/New_York',
            user_agent=custom_user_agent,
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        page = context.new_page()

        try:
            # -----------------------------------------------------------------
            # STEP 1: LOGIN (same as runner)
            # -----------------------------------------------------------------
            print("=" * 60)
            print("STEP 1: LOGIN")
            print("=" * 60)
            login_context = {}
            username, password = _load_credentials()
            print(f"Logging in as: {username}")
            fn_login(page, login_context, username=username, password=password)
            print("  [OK] Login successful!")

            # -----------------------------------------------------------------
            # STEP 2: NAVIGATE TO TARGET (set TARGET_URL at top of file)
            # -----------------------------------------------------------------
            print("\n" + "=" * 60)
            print("STEP 2: NAVIGATE TO TARGET")
            print("=" * 60)
            print(f"Navigating to: {TARGET_URL}")
            page.goto(TARGET_URL, wait_until='domcontentloaded', timeout=30000)
            if 'login' in page.url:
                print("  [!] Redirected to login - waiting for redirect...")
                page.wait_for_url("**/app/**", timeout=60000)
                page.goto(TARGET_URL, wait_until='domcontentloaded', timeout=30000)
            page.wait_for_timeout(3000)
            print(f"  URL: {page.url}")

            # -----------------------------------------------------------------
            # STEP 3, 4, ... Copy from failing test's test.py
            # -----------------------------------------------------------------
            # Uncomment and fill from test.py (navigation, iframes, clicks, etc.)
            # page.wait_for_selector('iframe[title="angularjs"]', timeout=15000)
            # outer_iframe = page.frame_locator('iframe[title="angularjs"]')
            # inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
            # ...
            print("\n(Add STEP 3, 4, ... from test.py)")

            # -----------------------------------------------------------------
            # DEBUG_FOCUS: The failing action or assertion
            # -----------------------------------------------------------------
            # Repeat the exact failing step here; try multiple locators or
            # add print/screenshots to see what works.
            print("\n" + "=" * 60)
            print("DEBUG_FOCUS (failing step)")
            print("=" * 60)
            # Example: inner_iframe.get_by_text('Some button').first.click()
            # Add your failing step + variants and document what you see.
            print("(Add failing step and variants here)")

            # -----------------------------------------------------------------
            # Cleanup: browser stays open briefly for inspection
            # -----------------------------------------------------------------
            print("\n" + "=" * 60)
            print("Debug complete. Browser will close in 10 seconds.")
            print("For local use you can add input('Enter to close') above.")
            print("=" * 60)
            page.wait_for_timeout(10000)

        except Exception as e:
            print(f"\n[ERROR] {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            print("\nBrowser will close in 5 seconds...")
            page.wait_for_timeout(5000)

        finally:
            browser.close()


if __name__ == "__main__":
    run_debug()
