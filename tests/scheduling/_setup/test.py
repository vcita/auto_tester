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
    
    Credentials are read from environment variables or use defaults.
    
    Saves to context:
    - logged_in_user: The username that was logged in
    """
    # Get credentials from environment or use defaults
    username = os.environ.get("VCITA_TEST_USERNAME", "itzik+autotest@vcita.com")
    password = os.environ.get("VCITA_TEST_PASSWORD", "vcita123")
    
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


# For standalone testing
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    import sys
    import os
    
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    sys.path.insert(0, project_root)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        browser_context = browser.new_context()
        page = browser_context.new_page()
        context = {}
        
        try:
            setup_scheduling(page, context)
            print("\n[OK] Setup complete!")
            print(f"Current URL: {page.url}")
            
            # Keep browser open for inspection
            input("\nPress Enter to close browser...")
            
        except Exception as e:
            print(f"\n[FAIL] Setup failed: {e}")
            page.screenshot(path="scheduling_setup_error.png")
            raise
        finally:
            browser.close()
