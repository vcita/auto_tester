# Auto-generated from script.md
# Last updated: 2026-01-22
# Source: tests/scheduling/_setup/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from tests._functions.login.test import fn_login

SETUP_TIMEOUT = 5_000


def setup_scheduling(page: Page, context: dict) -> None:
    """
    Setup for scheduling category tests.
    
    Logs in and navigates to Settings > Services page.
    
    Credentials: from context (injected by runner from config.yaml target.auth). No fallbacks.
    
    Saves to context:
    - logged_in_user: The username that was logged in
    """
    username = context.get("username")
    password = context.get("password")
    if not username or not password:
        raise ValueError(
            "username and password not in context. Set target.auth.username and target.auth.password in config.yaml."
        )
    
    # Step 1: Login
    print("  Step 1: Logging in...")
    fn_login(page, context, username=username, password=password)
    
    # Step 2: Navigate to Settings
    print("  Step 2: Navigating to Settings...")
    page.get_by_text('Settings').click(timeout=SETUP_TIMEOUT)
    try:
        page.wait_for_url("**/app/settings**", timeout=SETUP_TIMEOUT)
    except PlaywrightTimeoutError:
        page.goto(f"{_app_base_url(page)}/app/settings/services", wait_until="domcontentloaded", timeout=SETUP_TIMEOUT)
    
    # Step 3: Navigate to Services
    print("  Step 3: Navigating to Services...")
    # Wait for iframe to load
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=SETUP_TIMEOUT)
    
    # Get iframe and click Services
    iframe = page.frame_locator('iframe[title="angularjs"]')
    services_button = iframe.get_by_role("button", name="Define the services your")
    if "/app/settings/services" not in page.url:
        services_button.wait_for(state="visible", timeout=SETUP_TIMEOUT)
        services_button.click(timeout=SETUP_TIMEOUT)
        page.wait_for_url("**/app/settings/services**", timeout=SETUP_TIMEOUT)
    
    # Step 4: Verify Services page loaded
    print("  Step 4: Verifying Services page loaded...")
    heading = iframe.get_by_role("heading", name="Settings / Services")
    heading.wait_for(state="visible", timeout=SETUP_TIMEOUT)
    
    print(f"  Scheduling setup complete - on Services page")


def _app_base_url(page: Page) -> str:
    return page.url.split("/app/", 1)[0]
