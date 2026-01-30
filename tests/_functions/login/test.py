# Auto-generated from script.md
# Last updated: 2026-01-21
# Source: tests/_functions/login/script.md
# Verified with: Playwright MCP exploration

import re
from playwright.sync_api import Page, expect

from tests._functions._config import get_base_url


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
    - Login URL is base_url + "/login" from context or config (see get_base_url).
    """
    username = params.get("username")
    password = params.get("password")
    
    if not username or not password:
        raise ValueError("username and password are required parameters")
    
    base_url = get_base_url(context, params)
    login_url = base_url + "/login"
    
    # Step 1: Navigate to Login Page (once; no retries for actions)
    page.goto(login_url, wait_until="commit")
    page.wait_for_load_state("domcontentloaded")

    print(f"  Page URL: {page.url}")
    print(f"  Page Title: {page.title()}")

    # If already on dashboard, wait for it to be ready then return
    if "dashboard" in page.url:
        context["logged_in_user"] = username
        print("  Already logged in, waiting for dashboard to be ready...")
        page.wait_for_load_state("domcontentloaded")
        page.get_by_text("Quick actions", exact=True).wait_for(state="visible", timeout=30000)
        print("  [OK] Dashboard ready")
        return

    # Handle Cloudflare challenge - wait for it to complete or for user to solve it
    max_cloudflare_wait = 120  # 2 minutes for manual solving if needed
    if "Just a moment" in page.title() or page.title() == "":
        print("  [!] Cloudflare security check detected")
        print("  [>] Please click 'Verify you are human' checkbox if visible...")
        page.wait_for_function(
            """() => {
                const title = document.title || '';
                return !title.includes('Just a moment') && title !== '' && title.length > 0;
            }""",
            timeout=max_cloudflare_wait * 1000
        )
        print(f"  [OK] Cloudflare check passed!")
        print(f"  Page Title after wait: {page.title()}")

    # Wait for login form or dashboard to appear
    print(f"  Waiting for login page or dashboard...")
    try:
        email_field = page.get_by_label("Email", exact=True)
        email_field.wait_for(state="visible", timeout=60000)
        print(f"  [OK] Login form is ready")
    except Exception as wait_error:
        if "dashboard" in page.url:
            context["logged_in_user"] = username
            print("  Already logged in (redirected to dashboard), skipping login")
            return
        print(f"  Current URL: {page.url}")
        print(f"  Current Title: {page.title()}")
        raise wait_error
    
    # Step 2: Enter Email
    # The textbox has an associated label "Email" - use get_by_label
    email_input = page.get_by_label("Email", exact=True)
    email_input.click()
    page.wait_for_timeout(100)  # Brief delay for field focus
    email_input.fill(username)  # Use fill for login - more reliable with autofill
    
    # Step 3: Enter Password
    password_input = page.get_by_label("Password", exact=True)
    password_input.click()
    page.wait_for_timeout(100)  # Brief delay for field focus
    password_input.fill(password)
    
    # Step 4: Click Login Button
    login_button = page.get_by_role("button", name="Login")
    login_button.click()
    
    # Step 5: Wait for Dashboard to Load
    # After clicking login, the page will navigate. Don't try to interact with the page
    # during navigation - just wait for the final destination.
    # Note: reCAPTCHA may appear here and require manual solving
    max_login_wait = 120  # seconds
    
    try:
        # Wait for either dashboard URL or CAPTCHA to appear
        # Use wait_for_url with a pattern that matches the dashboard
        page.wait_for_url("**/app/dashboard**", timeout=max_login_wait * 1000)
    except Exception as e:
        # If we timed out, check what page we're on
        current_url = page.url
        
        # Check if we're stuck on CAPTCHA
        if "captcha" in current_url.lower():
            print("  [!] reCAPTCHA detected - please solve it manually...")
            print(f"  [>] Waiting up to {max_login_wait} seconds for manual solving...")
            # Wait again for dashboard after manual solving
            page.wait_for_url("**/app/dashboard**", timeout=max_login_wait * 1000)
        elif "challenge" in current_url.lower():
            print("  [X] Challenge page detected - manual intervention required")
            raise e
        else:
            # Check if we actually made it to dashboard despite the error
            if "dashboard" in current_url:
                print("  [OK] Made it to dashboard despite navigation hiccup")
            else:
                print(f"  [X] Login failed - stuck on: {current_url}")
                raise e
    
    # Verify dashboard loaded: DOM first, then key UI so tests don't wait again
    page.wait_for_load_state("domcontentloaded")
    # Wait for dashboard to be usable (Quick actions panel). Without this, setup
    # "completes" but the first test (e.g. create_matter) then waits here, which
    # looks like a long pause after the dashboard with no visible action.
    print("  Waiting for dashboard to be ready (Quick actions)...")
    page.get_by_text("Quick actions", exact=True).wait_for(state="visible", timeout=30000)
    print("  [OK] Dashboard ready")

    # Save to context
    context["logged_in_user"] = username
    print(f"  [OK] Login successful for: {username}")
