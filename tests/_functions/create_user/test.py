# Create user and onboard (dismiss one-time dialogs, validate clean second login).
# See docs/plans/create_user_discovery.md and script.md.

import os
import re
import sys
import time
from playwright.sync_api import Page

from tests._functions._config import get_base_url
from tests._functions.login.test import fn_login
from tests._functions.logout.test import fn_logout

# Live terminal output (no buffering)
def _debug(msg: str) -> None:
    print(msg, flush=True)


DEFAULT_PASSWORD = "vcita123"
# Phone for onboarding dialog (server-validated; set VCITA_TEST_PHONE or pass phone= if needed)
DEFAULT_PHONE = "5550100"
# Address for Welcome dialog (optional field "Your business address"; set VCITA_TEST_ADDRESS or pass address=)
DEFAULT_ADDRESS = "123 Test Street"

# App is at base_url with /app/ path. Iframe may have id, title, or src set.
def _on_app_page(page: Page) -> bool:
    return "/app/" in page.url


# Resilient app iframe selector: iframe is injected after load; on www it may lack #angular-iframe initially.
APP_IFRAME_SELECTOR = (
    "iframe#angular-iframe, iframe[title=\"angularjs\"], iframe[src*=\"child_app=true\"]"
)


def fn_create_user(page: Page, context: dict, **params) -> None:
    """
    Create a new vcita user via signup (or onboard existing new user), dismiss
    one-time setup dialogs, and validate no dialog on second login.

    Parameters:
    - email: (required for signup) New user email.
    - password: (optional) Default vcita123.
    - name: (optional) Your Name or Business Name; default "Test User {timestamp}".
    - base_url: (optional) Target base URL from config/context; login URL = base_url + "/login".
    - onboarding_only: (optional) If True, skip signup and only login + dismiss + validate.
    - phone: (optional) Phone number for first-time "Welcome" dialog (server-validated). Default from VCITA_TEST_PHONE or 5550100.
    - address: (optional) Business address for "Welcome" dialog. Default from VCITA_TEST_ADDRESS or "123 Test Street".

    Saves to context:
    - created_user_email: The email used.
    - created_user_ready: True when validation passed.
    """
    email = params.get("email")
    password = params.get("password") or DEFAULT_PASSWORD
    name = params.get("name") or f"Test User {int(time.time())}"
    base_url = get_base_url(context, params)
    login_url = base_url + "/login"
    onboarding_only = params.get("onboarding_only", False)

    if not email:
        raise ValueError("email is required for create_user")

    if not onboarding_only:
        _do_signup(page, login_url, email, name, password)
        # Stay on app so we can spot the Welcome dialog; mark logged in so we don't navigate away in fn_login
        if "/app/" in page.url:
            context["logged_in_user"] = email

    # Ensure we're logged in (signup may land on dashboard, or we need to login)
    if context.get("logged_in_user") != email:
        fn_login(page, context, username=email, password=password)

    phone = params.get("phone") or os.environ.get("VCITA_TEST_PHONE") or DEFAULT_PHONE
    address = params.get("address") or os.environ.get("VCITA_TEST_ADDRESS") or DEFAULT_ADDRESS
    # Spot when Welcome to vcita window opens (inside angular iframe), then dismiss onboarding dialogs
    # Short timeouts for debugging first-login dialog detection (~30s wait + ~45s dismiss max)
    if not _wait_for_welcome_dialog(page, timeout_seconds=30.0):
        raise ValueError(
            "Welcome dialog did not appear after signup/login within 30s. "
            "Account may already be onboarded, or app/iframe failed to load."
        )
    _dismiss_onboarding_dialogs(
        page, phone=phone, address=address, min_wait_for_dialog_seconds=10.0, max_wait=45.0
    )

    # Validate: logout and login again; assert no onboarding dialog (account truly ready for tests)
    _debug("  [debug] Validating: logout then second login...")
    fn_logout(page, context)
    context.pop("logged_in_user", None)
    fn_login(page, context, username=email, password=password)
    _assert_no_dialog_after_login(page, timeout_seconds=10.0)

    context["created_user_email"] = email
    context["created_user_ready"] = True
    _debug(f"  [OK] Create user complete (first login + onboarding dismissed + validated): {email}.")


def _do_signup(page: Page, login_url: str, email: str, name: str, password: str) -> None:
    """Navigate to signup, fill form, submit. Selectors aligned with MCP snapshot (signup page has #new_user, #user_email, #user_password)."""
    signup_url = login_url.rstrip("/").replace("/login", "/signup")
    if signup_url == login_url.rstrip("/"):
        signup_url = login_url.rstrip("/") + "/signup"
    page.goto(signup_url, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_load_state("domcontentloaded")

    # Wait for any Cloudflare/challenge to finish
    if "Just a moment" in page.title() or page.title() == "":
        page.wait_for_function(
            "document.title && !document.title.includes('Just a moment')",
            timeout=60000,
        )

    # Wait for signup view: "Sign Up" heading then the visible signup form (#new_user or "Let's go")
    page.get_by_role("heading", name="Sign Up").wait_for(state="visible", timeout=20000)
    lets_go = page.get_by_role("button", name="Let's go")
    try:
        lets_go.wait_for(state="visible", timeout=8000)
    except Exception:
        page.get_by_role("link", name=re.compile(r"Sign up", re.I)).or_(
            page.locator('a[href="/signup"]')
        ).first.click()
        page.wait_for_timeout(2000)
        lets_go.wait_for(state="visible", timeout=15000)
    # Scope to signup form so we target the visible one (form role may be absent; use id)
    signup_form = page.locator("#new_user")
    email_input = signup_form.get_by_role("textbox", name=re.compile(r"Email", re.I)).or_(
        signup_form.locator("#user_email")
    ).first
    email_input.wait_for(state="visible", timeout=5000)
    email_input.fill(email, force=True)
    signup_form.get_by_role("textbox", name=re.compile(r"Your Name or Business Name", re.I)).or_(
        signup_form.locator("#user_pivot_attributes_business_name")
    ).first.fill(name, force=True)
    signup_form.get_by_role("textbox", name=re.compile(r"Password", re.I)).or_(
        signup_form.locator("#user_password")
    ).first.fill(password, force=True)
    lets_go.click()
    page.wait_for_url("**/app/**", timeout=30000)
    page.wait_for_load_state("domcontentloaded")


def _wait_for_welcome_dialog(page: Page, timeout_seconds: float = 30.0) -> bool:
    """Wait until the 'Welcome to vcita' onboarding dialog is visible in the angular iframe.
    Returns True when dialog is spotted, False on timeout.
    No URL check: always attempt to find iframe and dialog.
    """
    deadline = time.time() + timeout_seconds
    phase1_ms = int(timeout_seconds * 0.6) * 1000
    _debug("  [debug] Phase 1: waiting for app iframe...")
    try:
        page.wait_for_selector(APP_IFRAME_SELECTOR, state="visible", timeout=phase1_ms)
        _debug("  [OK] App iframe visible.")
    except Exception as e:
        _debug(f"  [fail] Phase 1: app iframe did not become visible within {phase1_ms/1000:.0f}s. URL: {page.url[:80]!r} — {e}")
        return False
    remaining_ms = max(5000, int((deadline - time.time()) * 1000))
    _debug("  [debug] Phase 2: waiting for Welcome dialog in frame...")
    frame = page.frame_locator(APP_IFRAME_SELECTOR)
    welcome = (
        frame.locator("#dialogContent_1")
        .or_(frame.locator(".onboarding-dialog"))
        .or_(frame.locator(".md-dialog-container"))
        .or_(frame.locator('[role="dialog"]').filter(has_text="Welcome to vcita"))
    ).first
    try:
        welcome.wait_for(state="visible", timeout=remaining_ms)
        _debug("  [OK] Spotted Welcome to vcita dialog.")
        return True
    except Exception as e:
        _debug(f"  [fail] Phase 2: Welcome dialog did not appear in frame within {remaining_ms/1000:.0f}s. URL: {page.url[:80]!r} — {e}")
        return False


def _dismiss_onboarding_dialogs(
    page: Page,
    idle_seconds: float = 6.0,
    phone: str = DEFAULT_PHONE,
    address: str = DEFAULT_ADDRESS,
    max_wait: float = 120.0,
    min_wait_for_dialog_seconds: float = 0.0,
) -> None:
    """Dismiss all first-time setup dialogs in order. See docs/plans/create_user_discovery.md.
    When min_wait_for_dialog_seconds > 0, do not exit due to idle until at least that many seconds have passed (use on first login when dialog can be slow to appear).
    """
    dismiss_buttons = [
        "Skip",
        "Later",
        "I'll do it later",
        "Close",
        "Get started",
        "Maybe later",
        "Not now",
    ]
    start_time = time.time()
    last_dismissed = time.time()
    deadline = time.time() + max_wait

    while time.time() < deadline:
        found = False

        if _on_app_page(page):
            frame = page.frame_locator(APP_IFRAME_SELECTOR)
            frame_alt = page.frame_locator(APP_IFRAME_SELECTOR)
            try:
                # Try checklist close first every time (handles "Get the app" / post-onboarding checklist)
                try:
                    close_btn = frame_alt.locator("#auto-checklist-close-btn").first
                    if close_btn.is_visible():
                        close_btn.click(timeout=10000)
                        last_dismissed = time.time()
                        found = True
                        page.wait_for_timeout(1000)
                except Exception:
                    pass
                if not found:
                    dialog = frame.locator('[role="dialog"], .md-dialog').first
                    if dialog.is_visible():
                        inner = dialog.inner_text()
                        # 1) Welcome to vcita — Business size, Phone, Continue
                        if "Welcome to vcita" in inner or "Just a few basic questions" in inner:
                            try:
                                # MCP: listbox aria-label is "Business size" (no colon); first listbox is Country code
                                _debug("  [debug] Welcome dialog: opening Business size listbox...")
                                bs = frame.get_by_role("listbox", name=re.compile(r"Business size\s*:?")).last
                                bs.click()
                                page.wait_for_timeout(1200)
                                _debug("  [debug] Business size listbox opened.")
                                opt = frame.get_by_role("option", name="I do not have a business").or_(
                                    frame.get_by_text("I do not have a business", exact=False)
                                ).first
                                _debug("  [debug] Clicking 'I do not have a business'...")
                                opt.scroll_into_view_if_needed(timeout=5000)
                                page.wait_for_timeout(300)
                                opt.click(force=True)
                                page.wait_for_timeout(500)
                                _debug("  [debug] Selected 'I do not have a business'.")
                                _debug(f"  [debug] Filling Phone * with {phone!r}...")
                                frame.get_by_role("textbox", name="Phone *").fill(phone)
                                page.wait_for_timeout(400)
                                # Optional: Your business address (same Welcome dialog; Google Places autocomplete shows dropdown – dismiss it so Continue works)
                                address_filled = False
                                try:
                                    addr_field = frame.get_by_role("textbox", name="Your business address")
                                    addr_field.wait_for(state="visible", timeout=2000)
                                    _debug(f"  [debug] Filling address with {address!r}...")
                                    addr_field.fill(address)
                                    page.wait_for_timeout(800)  # Let Google Places dropdown appear
                                    # Dismiss address dropdown (MCP-validated: Escape closes it; typed text kept; Continue clickable)
                                    page.keyboard.press("Escape")
                                    page.wait_for_timeout(300)
                                    address_filled = True
                                except Exception:
                                    try:
                                        addr_field = frame.locator('input[name="address"]')
                                        addr_field.wait_for(state="visible", timeout=1000)
                                        _debug(f"  [debug] Filling address (input[name=address]) with {address!r}...")
                                        addr_field.fill(address)
                                        page.wait_for_timeout(800)
                                        # Same as above: Escape closes Google Places dropdown (MCP-validated)
                                        page.keyboard.press("Escape")
                                        page.wait_for_timeout(300)
                                        address_filled = True
                                    except Exception:
                                        _debug("  [debug] Address field not found, skipping.")
                                if address_filled:
                                    _debug("  [debug] Address filled (dropdown dismissed).")
                                _debug("  [debug] Clicking Continue.")
                                frame.get_by_role("button", name=re.compile(r"continue", re.I)).click()
                                last_dismissed = time.time()
                                found = True
                                _debug("  [OK] Welcome dialog: submitted (business size + phone" + (" + address" if address_filled else "") + " + Continue).")
                                page.wait_for_timeout(2000)
                            except Exception as e:
                                _debug(f"  [debug] Welcome dialog fill/continue failed: {e}")
                        # 2) What does your business do? — Landscaper then Continue
                        if not found and "What does your business do?" in inner:
                            try:
                                _debug("  [debug] Wizard: selecting Landscaper...")
                                frame.get_by_role("button", name="Landscaper").click()
                                page.wait_for_timeout(400)
                                _debug("  [debug] Wizard: clicking Continue.")
                                frame.get_by_role("button", name="Continue").click()
                                last_dismissed = time.time()
                                found = True
                                _debug("  [OK] Wizard: profession step done.")
                                page.wait_for_timeout(1500)
                            except Exception as e:
                                _debug(f"  [debug] Wizard profession step failed: {e}")
                        # 3) What are your business needs? — pick one then Continue (card may have label overlay; use force)
                        if not found and "What are your business needs?" in inner:
                            try:
                                _debug("  [debug] Wizard: selecting 'Managing clients'...")
                                frame.get_by_text("Managing clients", exact=False).first.click(force=True)
                                page.wait_for_timeout(400)
                                _debug("  [debug] Wizard: clicking Continue.")
                                frame.get_by_role("button", name="Continue").click()
                                last_dismissed = time.time()
                                found = True
                                _debug("  [OK] Wizard: business needs step done.")
                                page.wait_for_timeout(1500)
                            except Exception as e:
                                _debug(f"  [debug] Wizard business needs step failed: {e}")
                        # 4) What do your clients pay for? — pick one then Continue (card may have overlay; use force)
                        if not found and "What do your clients pay for?" in inner:
                            try:
                                _debug("  [debug] Wizard: selecting 'Individual sessions'...")
                                frame.get_by_text("Individual sessions", exact=False).first.click(force=True)
                                page.wait_for_timeout(400)
                                _debug("  [debug] Wizard: clicking Continue.")
                                frame.get_by_role("button", name="Continue").click()
                                last_dismissed = time.time()
                                found = True
                                _debug("  [OK] Wizard: clients pay for step done.")
                                page.wait_for_timeout(1500)
                            except Exception as e:
                                _debug(f"  [debug] Wizard clients pay step failed: {e}")
                        # 5) You're ready for takeoff! — click GO (match by substring; apostrophe may be Unicode)
                        if not found and "ready for takeoff" in inner and "Sit tight" in inner:
                            try:
                                _debug("  [debug] Wizard: clicking GO.")
                                frame.get_by_role("button", name="GO").click()
                                last_dismissed = time.time()
                                found = True
                                _debug("  [OK] Wizard: takeoff step done.")
                                page.wait_for_timeout(2000)
                                # Wait for "Let's personalize your account" dialog to appear (MCP: shown after GO)
                                _debug("  [debug] Waiting for getting-started (personalize) dialog...")
                                for _ in range(16):
                                    try:
                                        d = frame.locator("[role=\"dialog\"], .md-dialog").first
                                        if d.is_visible():
                                            t = d.inner_text()
                                            if "personalize" in t or "Add your clients" in t or "1/3" in t:
                                                _debug("  [OK] Getting-started dialog visible.")
                                                break
                                    except Exception:
                                        pass
                                    page.wait_for_timeout(500)
                            except Exception as e:
                                _debug(f"  [debug] Wizard GO step failed: {e}")
                        # 6) Getting started / Let's personalize (MCP: 1/3 one Skip, 2/3 two Skips, then #auto-checklist-close-btn)
                        getting_started = (
                            "personalize your account" in inner
                            or "Add your clients" in inner
                            or "Add your client and contact" in inner
                            or "You got this!" in inner
                            or "1/3" in inner
                            or "2/3" in inner
                            or "3/3 completed" in inner
                        )
                        if not found and getting_started:
                            try:
                                # First page (1/3 or "Add your clients"): one Skip
                                if "1/3" in inner or "Add your clients" in inner:
                                    _debug("  [debug] Getting started page 1/3: clicking Skip.")
                                    skip_btn = frame.get_by_role("button", name="Skip").first
                                    if skip_btn.is_visible():
                                        skip_btn.click()
                                        last_dismissed = time.time()
                                        found = True
                                        _debug("  [OK] Getting started: page 1 skipped.")
                                        page.wait_for_timeout(1200)
                                # Second page (2/3): two Skips in sequence
                                elif "2/3" in inner:
                                    _debug("  [debug] Getting started page 2/3: clicking Skip (1st).")
                                    skip_btn = frame.get_by_role("button", name="Skip").first
                                    if skip_btn.is_visible():
                                        skip_btn.click()
                                        page.wait_for_timeout(800)
                                    _debug("  [debug] Getting started page 2/3: clicking Skip (2nd).")
                                    skip_btn2 = frame.get_by_role("button", name="Skip").first
                                    if skip_btn2.is_visible():
                                        skip_btn2.click()
                                    last_dismissed = time.time()
                                    found = True
                                    _debug("  [OK] Getting started: page 2 skipped (two Skips).")
                                    page.wait_for_timeout(1200)
                                # 3/3 or final step: close with X
                                elif "3/3" in inner or "Get the mobile app" in inner or "Invite team members" in inner or "Congratulations" in inner:
                                    _debug("  [debug] Getting started: clicking X to close.")
                                    close_btn = frame_alt.locator("#auto-checklist-close-btn").first
                                    if close_btn.is_visible():
                                        close_btn.click(timeout=10000)
                                        last_dismissed = time.time()
                                        found = True
                                        _debug("  [OK] Getting started: closed with X.")
                                        page.wait_for_timeout(1000)
                                else:
                                    # Fallback: try Skip if visible, else X
                                    skip_btn = frame.get_by_role("button", name="Skip").first
                                    if skip_btn.is_visible():
                                        skip_btn.click()
                                        last_dismissed = time.time()
                                        found = True
                                        page.wait_for_timeout(1000)
                                    else:
                                        close_btn = frame_alt.locator("#auto-checklist-close-btn").first
                                        if close_btn.is_visible():
                                            close_btn.click(timeout=10000)
                                            last_dismissed = time.time()
                                            found = True
                                            page.wait_for_timeout(1000)
                            except Exception as e:
                                _debug(f"  [debug] Getting started step failed: {e}")
                        # Catch-all: any dialog still visible in frame — try checklist close then Escape
                        if not found and dialog.is_visible():
                            try:
                                close_btn = frame_alt.locator("#auto-checklist-close-btn").first
                                if close_btn.is_visible():
                                    close_btn.click(timeout=5000)
                                    last_dismissed = time.time()
                                    found = True
                                    page.wait_for_timeout(800)
                            except Exception:
                                pass
                            if not found:
                                page.keyboard.press("Escape")
                                last_dismissed = time.time()
                                found = True
                                page.wait_for_timeout(500)
                        # Generic Continue in iframe
                        if not found:
                            cont = frame.get_by_role("button", name=re.compile(r"continue", re.I)).first
                            if cont.is_visible():
                                cont.click()
                                last_dismissed = time.time()
                                found = True
                                page.wait_for_timeout(1500)
            except Exception:
                pass

        if found:
            page.wait_for_timeout(500)
            continue

        for text in dismiss_buttons:
            try:
                btn = page.get_by_role("button", name=text).first
                if btn.is_visible():
                    btn.click(timeout=2000)
                    last_dismissed = time.time()
                    found = True
                    page.wait_for_timeout(800)
                    break
            except Exception:
                pass
        if found:
            continue

        if _on_app_page(page):
            try:
                frame = page.frame_locator(APP_IFRAME_SELECTOR)
                for text in dismiss_buttons:
                    try:
                        btn = frame.get_by_role("button", name=text).first
                        if btn.is_visible():
                            btn.click(timeout=2000)
                            last_dismissed = time.time()
                            found = True
                            page.wait_for_timeout(800)
                            break
                    except Exception:
                        pass
            except Exception:
                pass
        if found:
            continue

        try:
            # Top-level page: checklist close or generic dialog close
            close_btn = page.locator("#auto-checklist-close-btn").first
            if close_btn.is_visible():
                close_btn.click(timeout=2000)
                last_dismissed = time.time()
                found = True
        except Exception:
            pass
        if not found:
            try:
                dialog = page.locator('[role="dialog"]').first
                if dialog.is_visible():
                    close_btn = dialog.get_by_role("button").first
                    if close_btn.is_visible():
                        close_btn.click(timeout=2000)
                        last_dismissed = time.time()
                        found = True
                    if not found:
                        page.keyboard.press("Escape")
                        last_dismissed = time.time()
            except Exception:
                pass

        if not found:
            elapsed = time.time() - start_time
            min_waited = min_wait_for_dialog_seconds <= 0 or elapsed >= min_wait_for_dialog_seconds
            if min_waited and (time.time() - last_dismissed >= idle_seconds):
                break
        page.wait_for_timeout(500)


# Phrases that identify first-time onboarding dialogs (not e.g. "Service info" or feature tips).
_ONBOARDING_PHRASES = (
    "Welcome to vcita",
    "Just a few basic questions",
    "What does your business do",
    "What are your business needs",
    "What do your clients pay for",
    "You're ready for takeoff",
    "Let's personalize your account",
    "Get the mobile app",
    "Invite team members",
    "Congratulations! You're done!",
)


def _is_onboarding_dialog(page: Page) -> bool:
    """True if a visible dialog contains known onboarding text (main page or frame)."""
    try:
        dialog = page.locator('[role="dialog"]').first
        if dialog.is_visible():
            text = dialog.inner_text()
            if any(p in text for p in _ONBOARDING_PHRASES):
                return True
    except Exception:
        pass
    try:
        if _on_app_page(page):
            frame = page.frame_locator(APP_IFRAME_SELECTOR)
            dialog = frame.locator('[role="dialog"], .md-dialog').first
            if dialog.is_visible():
                text = dialog.inner_text()
                if any(p in text for p in _ONBOARDING_PHRASES):
                    return True
    except Exception:
        pass
    return False


def _get_visible_dialog_text(page: Page) -> str:
    """Return inner text of any visible dialog (main or frame) for error messages."""
    try:
        dialog = page.locator('[role="dialog"]').first
        if dialog.is_visible():
            return dialog.inner_text()[:500]
    except Exception:
        pass
    try:
        if _on_app_page(page):
            frame = page.frame_locator(APP_IFRAME_SELECTOR)
            dialog = frame.locator('[role="dialog"], .md-dialog').first
            if dialog.is_visible():
                return dialog.inner_text()[:500]
    except Exception:
        pass
    return "(no dialog text)"


def _assert_no_dialog_after_login(page: Page, timeout_seconds: float = 10.0) -> None:
    """Assert no onboarding dialog appears for timeout_seconds after login."""
    deadline = time.time() + timeout_seconds
    dialog_seen_count = 0
    need_consecutive = 5
    last_seen_text = ""
    while time.time() < deadline:
        seen = _is_onboarding_dialog(page)
        if seen:
            last_seen_text = _get_visible_dialog_text(page)
            dialog_seen_count += 1
            if dialog_seen_count >= need_consecutive:
                raise AssertionError(
                    "New user still has onboarding dialog on second login. "
                    "Dismiss all one-time dialogs before validating. "
                    f"Dialog text (first 500 chars): {last_seen_text!r}"
                )
        else:
            dialog_seen_count = 0
        page.wait_for_timeout(500)
