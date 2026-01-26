# Auto-generated from script.md
# Last updated: 2026-01-22
# Source: tests/scheduling/_setup/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import os
from playwright.sync_api import Page, expect

from tests._functions.login.test import fn_login


def setup_scheduling(page: Page, context: dict) -> None:
    """
    Setup for scheduling category tests.
    
    Logs in and navigates to Settings > Services page.
    
    Credentials: context (from config, injected by runner), then env VCITA_TEST_*, else defaults.
    
    Saves to context:
    - logged_in_user: The username that was logged in
    """
    # Prefer config (injected by runner into context), then env, then defaults
    username = context.get("username") or os.environ.get("VCITA_TEST_USERNAME", "itzik+autotest@vcita.com")
    password = context.get("password") or os.environ.get("VCITA_TEST_PASSWORD", "vcita123")
    
    # Step 1: Login
    print("  Step 1: Logging in...")
    fn_login(page, context, username=username, password=password)
    
    # Step 2: Navigate to Settings
    print("  Step 2: Navigating to Settings...")
    page.get_by_text('Settings').click()
    page.wait_for_url("**/app/settings**")
    
    # Step 3: Navigate to Services
    print("  Step 3: Navigating to Services...")
    # Wait for iframe to load
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=15000)
    
    # Get iframe and click Services
    iframe = page.frame_locator('iframe[title="angularjs"]')
    services_button = iframe.get_by_role("button", name="Define the services your")
    services_button.wait_for(state="visible", timeout=10000)
    services_button.click()
    page.wait_for_url("**/app/settings/services**")
    
    # Step 4: Verify Services page loaded
    print("  Step 4: Verifying Services page loaded...")
    heading = iframe.get_by_role("heading", name="Settings / Services")
    heading.wait_for(state="visible", timeout=10000)
    
    print(f"  Scheduling setup complete - on Services page")
