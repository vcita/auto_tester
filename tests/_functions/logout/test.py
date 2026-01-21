# Auto-generated from script.md
# Last updated: 2026-01-21
# Source: tests/_functions/logout/script.md
# Verified with: Playwright MCP exploration

import re
from playwright.sync_api import Page, expect


def fn_logout(page: Page, context: dict, **params) -> None:
    """
    Logout from vcita via UI actions (click avatar -> click Logout)
    
    Parameters:
    - None required
    
    Clears from context:
    - logged_in_user: Removes the logged in user from context
    
    Note: This function uses ONLY UI actions, no direct URL navigation.
    The logout flow is:
    1. Click user avatar button (shows initials like "AU")
    2. Click "Logout" in the dropdown menu
    3. Wait for redirect to login page
    """
    # Step 1: Click User Avatar Button
    # The avatar shows user initials (e.g., "AU" for "Autotest")
    # It's a button with exactly 2 uppercase letters
    user_avatar = page.get_by_role("button", name=re.compile(r"^[A-Z]{2}$")).first
    user_avatar.click()
    
    # Step 2: Wait for Menu to Appear
    page.wait_for_selector("[role='menu']", timeout=5000)
    
    # Step 3: Click Logout Menu Item
    # Verified locator from Playwright MCP exploration:
    # The menu item has class "logout-item"
    logout_item = page.locator('.logout-item')
    logout_item.click()
    
    # Step 4: Wait for Login Page
    # The page will redirect to the login page after logout
    # URL pattern: https://www.vcita.com/login?sso=true
    page.wait_for_url("**/login**", timeout=15000)
    
    # Step 5: Handle Cloudflare if present
    # Cloudflare may show "Just a moment..." security check
    if "Just a moment" in page.title() or page.title() == "":
        print("  Waiting for Cloudflare check...")
        page.wait_for_function(
            "document.title && !document.title.includes('Just a moment')",
            timeout=30000
        )
    
    # Step 6: Verify Logout Success
    # After Cloudflare, the login page should show
    # The login form is inside an iframe
    page.wait_for_selector('#vue_iframe', timeout=15000)
    
    # Get the iframe content frame
    iframe = page.locator('#vue_iframe').content_frame()
    
    # Verify login form is visible
    expect(iframe.get_by_text("Log In to Your Account")).to_be_visible(timeout=10000)
    
    # Clear logged_in_user from context
    if "logged_in_user" in context:
        del context["logged_in_user"]
    
    print("  ✅ Logout successful")


# For standalone testing
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    import sys
    import os
    
    # Add parent directory to path to import login function
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from login.test import fn_login
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        context = {}
        
        # First login
        print("Step 1: Logging in...")
        fn_login(
            page, 
            context,
            username="itzik+autotest@vcita.com",
            password="vcita123"
        )
        print(f"  Logged in as: {context.get('logged_in_user')}")
        print(f"  Current URL: {page.url}")
        
        # Then logout via UI
        print("\nStep 2: Logging out via UI...")
        fn_logout(page, context)
        print(f"  Logged out successfully!")
        print(f"  Context after logout: {context}")
        print(f"  Current URL: {page.url}")
        
        print("\n=== Both login and logout functions work! ===")
        
        # Keep browser open for inspection
        input("\nPress Enter to close browser...")
        browser.close()
