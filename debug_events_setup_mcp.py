#!/usr/bin/env python3
"""
Open browser at the start of Events _setup (on Services page) for MCP step-by-step exploration.

Run from project root:
  python debug_events_setup_mcp.py

Then use Playwright MCP in Cursor to run Events _setup steps 3–10 manually:
  Step 3: Click iframe button "New service icon-caret-down"
  Step 4: Click menuitem "Group event"
  Step 5: Fill textbox "Service name *" with e.g. "Event Test Workshop 1769454999"
  Step 6: Fill spinbutton "Max attendees ..." with 10
  Step 7: Click button "icon-Home Face to face"
  Step 8: Click "With fee", fill "Service price *" with 25
  Step 9: Click "Create", wait for create dialog (Service info) to be hidden
  Step 10: If "I'll do it later" visible, click it; wait for "Great. Now" dialog hidden
  Then: Check if the new service name appears in the page (iframe).

Uses config.yaml target.base_url and target.auth.
"""

import sys
import yaml
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from playwright.sync_api import sync_playwright
from tests._functions.login.test import fn_login


def load_config():
    path = project_root / "config.yaml"
    with open(path, "r") as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    target = config.get("target", {})
    base_url = (target.get("base_url") or "https://www.vcita.com").rstrip("/")
    auth = target.get("auth", {})
    username = auth.get("username")
    password = auth.get("password")
    if not username or not password:
        raise ValueError(
            "Set target.auth.username and target.auth.password in config.yaml."
        )

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--disable-blink-features=AutomationControlled"],
        )
        bypass = "#vUC5wTG98Hq5=BW+D_1c29744b-38df-4f40-8830-a7558ccbfa6b"
        ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 {bypass}"
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="en-US",
            user_agent=ua,
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )
        page = context.new_page()

        print("Step 0: Login...")
        fn_login(page, {}, username=username, password=password)
        print("  OK Logged in.\n")

        print("Step 1: Navigate to Settings...")
        page.get_by_text("Settings", exact=True).click()
        page.wait_for_url("**/app/settings**", timeout=20000)
        print("  OK On Settings.\n")

        print("Step 2: Navigate to Services...")
        page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
        iframe = page.frame_locator('iframe[title="angularjs"]')
        iframe.get_by_role("button", name="Define the services your").click()
        page.wait_for_url("**/app/settings/services**", timeout=20000)
        print("  OK On Services page.\n")

        print("=" * 60)
        print("Browser ready for Events _setup from Step 3.")
        print("Use Playwright MCP to run Steps 3–10 (New service → Group event → fill → Create → I'll do it later).")
        print("Then check if the new service appears in the list.")
        print("=" * 60)
        input("Press Enter to close browser...")
        browser.close()


if __name__ == "__main__":
    main()
