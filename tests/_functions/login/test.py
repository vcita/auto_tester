# Auto-generated from script.md
# Last updated: 2026-01-21
# Source: tests/_functions/login/script.md
# Verified with: Playwright MCP exploration

import re
from playwright.sync_api import Page, expect


def fn_login(page: Page, context: dict, **params) -> None:
    """
    Login to vcita
    
    Parameters:
    - username: The username/email to login with (required)
    - password: The password for the account (required)
    
    Saves to context:
    - logged_in_user: The username that was logged in
    
    Notes:
    - Cloudflare may show a security check that requires manual solving
    - reCAPTCHA may appear and require manual solving
    """
    username = params.get("username")
    password = params.get("password")
    
    if not username or not password:
        raise ValueError("username and password are required parameters")
    
    # Step 1: Navigate to Login Page
    page.goto("https://www.vcita.com/login")
    
    # Wait for page to load - use 'load' instead of 'networkidle' 
    # because Cloudflare keeps polling and networkidle never completes
    page.wait_for_load_state("load", timeout=30000)
    
    # Debug: Print current page info
    print(f"  Page URL: {page.url}")
    print(f"  Page Title: {page.title()}")
    
    # If already on dashboard, we're already logged in
    if "dashboard" in page.url:
        context["logged_in_user"] = username
        print("  Already logged in, skipping login")
        return
    
    # Handle Cloudflare challenge - wait for it to complete or for user to solve it
    max_cloudflare_wait = 120  # 2 minutes for manual solving if needed
    if "Just a moment" in page.title() or page.title() == "":
        print("  [!] Cloudflare security check detected")
        print("  [>] Please click 'Verify you are human' checkbox if visible...")
        try:
            page.wait_for_function(
                """() => {
                    const title = document.title || '';
                    // Wait until title doesn't contain Cloudflare indicators
                    return !title.includes('Just a moment') && title !== '' && title.length > 0;
                }""",
                timeout=max_cloudflare_wait * 1000
            )
            print(f"  [OK] Cloudflare check passed!")
        except Exception as e:
            print(f"  [X] Cloudflare timeout - page title: {page.title()}")
            raise e
        print(f"  Page Title after wait: {page.title()}")
    
    # Wait for login form to be ready
    # Note: The login form is directly on the page (no iframe)
    page.wait_for_selector('text=Login to vcita', timeout=15000)
    
    # Step 2: Enter Email
    # The textbox has an associated label "Email" - use get_by_label
    email_input = page.get_by_label("Email", exact=True)
    email_input.click()
    page.wait_for_timeout(200)
    email_input.fill(username)  # Use fill instead of press_sequentially for reliability
    
    # Step 3: Enter Password
    password_input = page.get_by_label("Password", exact=True)
    password_input.click()
    page.wait_for_timeout(200)
    password_input.fill(password)
    
    # Step 4: Click Login Button
    login_button = page.get_by_role("button", name="Login")
    login_button.click()
    
    # Step 5: Wait for Dashboard to Load
    # Note: reCAPTCHA may appear here and require manual solving
    # Give 2 minutes for manual CAPTCHA solving if needed
    max_login_wait = 120  # seconds
    try:
        # First check if CAPTCHA appeared
        page.wait_for_timeout(2000)  # Wait for CAPTCHA to potentially appear
        
        # Check for reCAPTCHA presence
        captcha_present = page.locator("iframe[title*='reCAPTCHA']").count() > 0 or \
                         "captcha" in page.content().lower() or \
                         "select all" in page.content().lower()
        
        if captcha_present:
            print("  [!] reCAPTCHA detected - please solve it manually...")
            print(f"  [>] Waiting up to {max_login_wait} seconds for manual solving...")
        
        page.wait_for_url("**/app/dashboard**", timeout=max_login_wait * 1000)
    except Exception as e:
        # Check if we're stuck on CAPTCHA
        if "captcha" in page.url.lower() or "challenge" in page.content().lower() or "select all" in page.content().lower():
            print("  [X] CAPTCHA timeout - manual solving required but timed out")
        raise e
    
    # Verify dashboard loaded
    expect(page).to_have_title(re.compile(r"Dashboard"), timeout=10000)
    
    # Save to context
    context["logged_in_user"] = username
    print(f"  [OK] Login successful for: {username}")


# For standalone testing
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        context = {}
        
        print("Testing login function...")
        fn_login(
            page, 
            context,
            username="itzik+autotest@vcita.com",
            password="vcita123"
        )
        
        print(f"Login successful! User: {context.get('logged_in_user')}")
        print(f"Current URL: {page.url}")
        
        # Keep browser open for inspection
        input("Press Enter to close browser...")
        browser.close()
