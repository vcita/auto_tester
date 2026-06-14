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
    
    page.goto(login_url, wait_until="domcontentloaded")
    page.wait_for_timeout(2000)

    print(f"  Page URL: {page.url}")
    print(f"  Page Title: {page.title()}")

    if "dashboard" in page.url:
        context["logged_in_user"] = username
        print("  Already logged in, waiting for dashboard to be ready...")
        page.wait_for_load_state("domcontentloaded")
        page.get_by_text("Quick actions", exact=True).wait_for(state="visible", timeout=30000)
        print("  [OK] Dashboard ready")
        return

    # Handle Cloudflare challenge - wait for it to complete or for user to solve it
    max_cloudflare_wait = 120  # 2 minutes for manual solving if needed
    title = page.title()
    is_cloudflare = "Just a moment" in title or page.locator("#challenge-form, #cf-challenge-running, .cf-turnstile").count() > 0
    if is_cloudflare:
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

    # The login page runs an SSO check that can redirect to ?sso=true and reload the
    # Vue login iframe shortly after it first renders. Filling before that reload
    # silently discards the typed credentials, so the submit never authenticates and
    # we stay on /login. Fast path first (no extra waits when the form is stable); only
    # pay the settle cost on retry, when a discarded submit leaves us on /login.
    print("  Submitting login form...")
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            if attempt > 0:
                # The iframe reloaded under us: let it settle before retrying.
                try:
                    page.wait_for_load_state("networkidle", timeout=30000)
                except Exception:
                    pass
                page.wait_for_timeout(1500)

            ctx = _get_login_context(page)
            email_field = ctx.locator('input[type="email"]').first
            email_field.wait_for(state="visible", timeout=60000)

            # Re-resolve right before filling in case the iframe was just swapped.
            ctx = _get_login_context(page)
            email_field = ctx.locator('input[type="email"]').first
            email_field.fill(username)
            ctx.locator('input[type="password"]').first.fill(password)

            if email_field.input_value() != username:
                raise RuntimeError("login form reset before submit (iframe reloaded)")

            ctx.get_by_role("button", name="Log In", exact=True).first.click()

            # Confirm the submit took: a discarded fill leaves us on /login. Detect that
            # quickly and retry with a settle, rather than waiting out the full dashboard
            # timeout below.
            try:
                page.wait_for_url(lambda url: "/login" not in url, timeout=10000)
            except Exception:
                if "/login" in page.url:
                    raise RuntimeError("still on /login after submit (credentials discarded)")

            print("  [OK] Login form submitted")
            last_error = None
            break
        except Exception as exc:
            if "dashboard" in page.url:
                context["logged_in_user"] = username
                print("  Already logged in (redirected to dashboard), skipping login")
                return
            last_error = exc
            print(f"  [retry {attempt + 1}/3] login form unstable: {repr(exc)[:120]}")
    if last_error is not None:
        print(f"  [X] Login form interaction failed - stuck on: {page.url}")
        raise last_error
    
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
    
    page.wait_for_load_state("domcontentloaded")
    print("  Waiting for dashboard to be ready...")
    dashboard_indicator = page.get_by_text("Quick actions").or_(page.locator("text=Welcome to"))
    try:
        dashboard_indicator.first.wait_for(state="visible", timeout=30000)
    except Exception:
        pass
    print("  [OK] Dashboard ready")

    # Save to context
    context["logged_in_user"] = username
    print(f"  [OK] Login successful for: {username}")


def _get_login_context(page: Page):
    """Return the frame/page that contains the login form (handles vue_iframe)."""
    if page.locator('input[type="email"]').count() > 0:
        return page
    for frame in page.frames:
        if frame.name == "vue_iframe":
            try:
                frame.wait_for_load_state("domcontentloaded", timeout=15000)
                return frame
            except Exception:
                pass
    return page
