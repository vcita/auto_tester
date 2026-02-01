"""
Minimal script to reproduce suspected system bug: after creating a custom
appointment and cancelling it, the app may automatically navigate to an
error page instead of staying on calendar or appointment list.

Flow: Login → Create client → Calendar → Create custom appointment →
      Cancel appointment → Check if we land on error page.

Credentials and base URL: from config.yaml target.base_url and target.auth only.
Uses same user-agent + bypass string as runner/main.py to avoid captcha.
Run from project root: python reproduce_cancel_custom_appointment_error.py
"""

import re
import time
import yaml
from pathlib import Path
from playwright.sync_api import sync_playwright

from tests._functions.create_client.test import fn_create_client
from tests._functions.delete_client.test import fn_delete_client
from tests._functions.delete_service.test import fn_delete_service
from tests.debug_utils import step_callback_with_enter

_project_root = Path(__file__).resolve().parent


def _load_config():
    """Load target.base_url and target.auth from config.yaml."""
    with open(_project_root / "config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}
    target = config.get("target") or {}
    base_url = (target.get("base_url") or "").rstrip("/")
    auth = target.get("auth") or {}
    username, password = auth.get("username"), auth.get("password")
    if not base_url or not username or not password:
        raise ValueError("Set target.base_url and target.auth in config.yaml.")
    return base_url, username, password


BASE_URL, USERNAME, PASSWORD = _load_config()


def login(page):
    """Log in to vcita."""
    print("Step: Logging in...")
    page.goto(f"{BASE_URL}/login", wait_until="commit")
    page.wait_for_load_state("domcontentloaded")
    page.get_by_label("Email", exact=True).wait_for(state="visible", timeout=60000)
    page.get_by_label("Email", exact=True).fill(USERNAME)
    page.get_by_label("Password", exact=True).fill(PASSWORD)
    page.get_by_role("button", name="Login").click()
    page.wait_for_url("**/app/dashboard**", timeout=120000)
    page.wait_for_load_state("domcontentloaded")
    page.get_by_text("Quick actions", exact=True).wait_for(state="visible", timeout=30000)
    print("  [OK] Logged in\n")


def create_client(page, context):
    """Create one test client using project fn_create_client; returns client name."""
    timestamp = int(time.time())
    print("Step: Creating test client...")
    fn_create_client(
        page,
        context,
        first_name="Appt",
        last_name=f"TestClient{timestamp}",
    )
    client_name = context.get("created_client_name")
    print(f"  [OK] Created client: {client_name}\n")
    return client_name


def create_custom_appointment(page, client_name):
    """Create one custom appointment on calendar; returns custom title."""
    custom_title = f"Custom Meeting {int(time.time())}"
    print("Step: Creating custom appointment...")
    if "/app/calendar" not in page.url:
        page.get_by_text("Calendar", exact=True).click()
        page.wait_for_url("**/app/calendar**", timeout=10000)
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator('#vue_iframe_layout')
    inner.get_by_role('button', name='New').wait_for(state='visible', timeout=10000)
    inner.get_by_role('button', name='New').click()
    inner.get_by_role('menuitem', name='Appointment', exact=True).wait_for(state='visible', timeout=30000)
    inner.get_by_role('menuitem', name='Appointment', exact=True).click()
    outer.get_by_role('dialog').wait_for(state='visible', timeout=10000)
    search = outer.get_by_role('textbox', name='Search by name, email or tag')
    search.click()
    page.wait_for_timeout(100)
    search.press_sequentially(client_name, delay=30)
    outer.get_by_role('button').filter(has_text=client_name).wait_for(state='visible', timeout=30000)
    outer.get_by_role('button').filter(has_text=client_name).click()
    inner.get_by_role('button', name='Custom service').wait_for(state='visible', timeout=10000)
    inner.get_by_role('button', name='Custom service').click()
    inner.get_by_role('textbox', name='Appointment title').wait_for(state='visible', timeout=10000)
    inner.get_by_role('textbox', name='Appointment title').fill(custom_title)
    location_btn = inner.get_by_role('button').filter(has_text=re.compile(r'^arrow_drop_down$'))
    location_btn.click()
    inner.get_by_role('option', name='My business address').wait_for(state='visible', timeout=10000)
    inner.get_by_role('option', name='My business address').click()
    inner.get_by_role('button', name='Schedule appointment').wait_for(state='visible', timeout=10000)
    inner.get_by_role('button', name='Schedule appointment').click(force=True)
    inner.get_by_role('menuitem').filter(has_text=custom_title).wait_for(state='visible', timeout=15000)
    print(f"  [OK] Created custom appointment: {custom_title}\n")
    return custom_title


def cancel_custom_appointment(page, client_name):
    """Cancel the custom appointment (click it, then Cancel Appointment → Submit)."""
    print("Step: Cancelling custom appointment...")
    if "/app/calendar" not in page.url:
        page.get_by_text("Calendar", exact=True).click()
        page.wait_for_url("**/app/calendar**", timeout=10000)
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer = page.frame_locator('iframe[title="angularjs"]')
    inner = outer.frame_locator('#vue_iframe_layout')
    # Click the appointment (menuitem with client name - custom appointment shows client in calendar)
    appointment = inner.get_by_role('menuitem').filter(has_text=client_name)
    appointment.wait_for(state='visible', timeout=30000)
    appointment.click()
    page.wait_for_url("**/app/appointments/**", timeout=10000)
    outer.get_by_role('button', name='Cancel Appointment').wait_for(state='visible', timeout=5000)
    outer.get_by_role('button', name='Cancel Appointment').click()
    outer.get_by_role('dialog').wait_for(state='visible', timeout=30000)
    outer.get_by_role('button', name='Submit').click()
    outer.get_by_text('Cancelled', exact=True).wait_for(state='visible', timeout=30000)
    # Return to calendar (Back is where error page may appear instead of calendar)
    page.get_by_text('Back').click()
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)
    print("  [OK] Appointment cancelled, clicked Back\n")


def teardown_phase_navigate_to_dashboard(page):
    """
    Same as appointments _teardown Step 0: from calendar, try to navigate to Dashboard.
    This is where the sidebar (Dashboard/Settings) can fail or we land on error page.
    """
    # Step 0: Ensure we're on dashboard (after appointments we're on calendar; sidebar not reliable from calendar)
    print("  Teardown Step 0: Ensuring we're on dashboard...")
    if "/app/dashboard" not in page.url:
        print("  Teardown Step 0: Not on dashboard - navigating...")
        page.wait_for_load_state("domcontentloaded")
        try:
            # Sidebar is in main document; scope to body so we don't match inside calendar iframe
            dashboard_link = page.locator("body").get_by_text("Dashboard", exact=True)
            dashboard_link.wait_for(state="visible", timeout=30000)
            dashboard_link.scroll_into_view_if_needed()
            page.wait_for_timeout(200)  # Brief settle (allowed)
            dashboard_link.click()
            page.wait_for_url("**/app/dashboard**", timeout=30000, wait_until="domcontentloaded")
            page.wait_for_load_state("domcontentloaded")
            # Same as login/create_matter: do NOT wait for iframe first (first iframe may be hidden).
            # Wait for "Quick actions" at page level so Playwright finds the visible panel. Timeout = fail.
            page.get_by_text("Quick actions", exact=True).wait_for(state="visible", timeout=30000)
            print("  Teardown Step 0: Successfully navigated to dashboard")
        except Exception as e:
            print(f"  Teardown Step 0: Warning - Could not navigate to dashboard: {e}")
            # Continue anyway - delete_client/delete_service may fail or show error page


def teardown_phase_delete_client_and_service(page, context):
    """
    Same as appointments _teardown Step 1 & 2: delete client then delete service.
    "This page is unavailable" often appears when these run after Step 0 failed (iframe hidden).
    Uses step_callback to pause before each minor action and show what we're about to do.
    """
    client_name = context.get("created_client_name")
    if client_name:
        print(f"\n  Teardown Step 1: Deleting test client: {client_name}")
        try:
            fn_delete_client(page, context, step_callback=step_callback_with_enter)
            print(f"    Client deleted: {client_name}")
        except Exception as e:
            print(f"    Warning: Could not delete client: {e}")
    else:
        print("  Teardown Step 1: No client to delete (not in context)")
    service_name = context.get("created_service_name")
    if service_name:
        print(f"\n  Teardown Step 2: Deleting test service: {service_name}")
        try:
            fn_delete_service(page, context, step_callback=step_callback_with_enter)
            print(f"    Service deleted: {service_name}")
        except Exception as e:
            print(f"    Warning: Could not delete service: {e}")
    else:
        print("  Teardown Step 2: No service to delete (not in context)")


def teardown_phase_full(page, context):
    """
    Same as appointments _teardown: Step 0 (navigate to dashboard) then Step 1 (delete client)
    then Step 2 (delete service). The "This page is unavailable" error often appears when
    running Step 1 or Step 2 after Step 0 failed (iframe hidden).
    """
    teardown_phase_navigate_to_dashboard(page)
    teardown_phase_delete_client_and_service(page, context)


def check_for_error_page(page):
    """Check if current page is the error page. Returns True if error page detected."""
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(2000)
    url = page.url
    body_text = (page.locator("body").text_content() or "").lower()
    has_error_text = "page is unavailable" in body_text or "this page is unavailable" in body_text
    has_return_home = "return to homepage" in body_text
    has_error_url = "/error" in url or "unavailable" in url.lower()
    return bool(has_error_text or has_return_home or has_error_url), url, body_text[:300]


def main():
    print("=" * 60)
    print("Reproduce: Error page after cancel custom appointment?")
    print("=" * 60)
    print("Flow: Login -> Create client -> Create custom appointment -> Cancel -> Back -> Teardown (Calendar -> Dashboard -> delete client -> delete service) -> Check URL/content\n")

    # Same user-agent + bypass string as runner/main.py to avoid captcha
    bypass_string = "#vUC5wTG98Hq5=BW+D_1c29744b-38df-4f40-8830-a7558ccbfa6b"
    custom_user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 " + bypass_string
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            locale="en-US",
            timezone_id="America/New_York",
            user_agent=custom_user_agent,
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
        )
        page = context.new_page()

        try:
            login(page)
            run_context = {}
            client_name = create_client(page, run_context)
            # Go to calendar
            page.get_by_text("Calendar", exact=True).click()
            page.wait_for_url("**/app/calendar**", timeout=10000)
            page.wait_for_timeout(1000)
            create_custom_appointment(page, client_name)
            cancel_custom_appointment(page, client_name)

            # Teardown phase: Step 0 only, then wait for Enter before Step 1 and Step 2.
            teardown_phase_navigate_to_dashboard(page)
            print("\n  Step 0 done. Waiting for Enter to continue with Step 1 (delete client) and Step 2 (delete service)...")
            input()
            teardown_phase_delete_client_and_service(page, run_context)

            # Check if we landed on error page (after Back, or after any teardown step)
            print("Step: Checking for error page...")
            is_error, url, snippet = check_for_error_page(page)
            print(f"  URL: {url}")
            print(f"  Body snippet: {snippet!r}")

            print("\n" + "=" * 60)
            if is_error:
                print("[BUG] Error page detected (after cancel+Back or after teardown Calendar->Dashboard).")
                print("Expected: dashboard or calendar. Actual: error/unavailable page.")
                page.screenshot(path="reproduce_cancel_custom_error.png", full_page=True)
                print("Screenshot: reproduce_cancel_custom_error.png")
            else:
                print("[OK] No error page detected. Current URL looks normal.")
            print("=" * 60)

            print("\nBrowser will stay open 15s...")
            page.wait_for_timeout(15000)
        except Exception as e:
            print(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            page.wait_for_timeout(15000)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
