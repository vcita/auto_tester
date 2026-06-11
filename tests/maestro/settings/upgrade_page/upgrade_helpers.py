"""Shared helpers for the upgrade-page (Frontage) Recurly upgrade flow.

Migrated from automation-js pages/desktop/Frontage/upgradePage.js + recurly.js.
The upgrade page lives in the `vue_upgrade_page` iframe; clicking a plan's "Get it"
button opens Recurly checkout in a new tab. Recurly hosts the card fields in nested
iframes and submits via a jQuery click handler that triggers tokenization.
"""

import datetime
import re

from playwright.sync_api import Page

# Recurly's trust-seal badge script hangs DOMContentLoaded on the checkout page, so
# the hosted card-field iframes never mount. Aborting it lets Recurly configure.
TRUST_SEAL_GLOB = "**://sealserver.trustwave.com/**"
UPGRADE_PATH = "/app/settings/upgrade_page"
UPGRADE_IFRAME = "vue_upgrade_page"
SUCCESS_TITLE = "Account Successfully Upgraded"
DEFAULT_CARD = "4111111111111111"
POSTAL_CODE = "34241"
CVV = "325"
EXP_MONTH = "02"

# Bounded polls for genuinely external/async steps (documented in changelog.md).
IFRAME_MOUNT_TIMEOUT_S = 12
# Submit is retried (1 + 2): each attempt re-fills the card fields then tokenizes, so
# a dropped keystroke is corrected; each attempt waits SUBMIT_WAIT_S for the redirect.
SUBMIT_ATTEMPTS = 3
SUBMIT_WAIT_S = 8


def block_trust_seal(page: Page) -> None:
    """Abort the trust-seal script across the whole context (incl. the Recurly popup)."""
    page.context.route(TRUST_SEAL_GLOB, lambda route: route.abort())


def _click_get_it(page: Page, plan: str):
    """Click a plan's Get-it button and return the Recurly checkout popup.

    The `vue_upgrade_page` iframe is nested inside the POV/Angular iframes, so it is
    resolved recursively with `page.frame(name=...)` (a CSS frame_locator only sees
    top-level iframes). The Vue app re-renders the iframe after first paint, which can
    detach a frame snapshot mid-action, so the lookup + click is retried on a bounded
    loop, re-acquiring the frame each attempt.
    """
    selector = f"#auto_{plan} .get-it button"
    deadline = datetime.datetime.now() + datetime.timedelta(seconds=30)
    last_error = None
    while datetime.datetime.now() < deadline:
        frame = page.frame(name=UPGRADE_IFRAME)
        if frame:
            try:
                button = frame.locator(selector).first
                button.wait_for(state="visible", timeout=3000)
                # Short expect_page timeout so a click that fails to spawn the
                # Recurly tab (button re-rendered mid-click) retries quickly.
                with page.context.expect_page(timeout=6000) as popup_info:
                    button.click()
                return popup_info.value
            except Exception as exc:  # stale frame / re-render / missed popup
                last_error = exc
        page.wait_for_timeout(500)
    raise AssertionError(f"could not click Get-it for plan {plan!r}: {last_error}")


def upgrade_to_plan(
    page: Page,
    plan: str,
    first_name: str,
    last_name: str,
    base_url: str,
    card: str = DEFAULT_CARD,
) -> str:
    """Run the full upgrade UI flow and return the success-page package text.

    Opens the upgrade page, clicks the plan's Get-it button (opens Recurly in a new
    tab), fills the Recurly card form, submits, and reads the upgraded package name
    from the success page (mirrors legacy getPackageFromSuccessPage).
    """
    page.goto(base_url.rstrip("/") + UPGRADE_PATH, wait_until="domcontentloaded")
    print("    [upg] upgrade page loaded; clicking Get-it")
    recurly = _click_get_it(page, plan)
    print(f"    [upg] recurly popup opened url={recurly.url[:80]!r}")
    _wait_for_hosted_fields(recurly)
    print("    [upg] hosted fields mounted")
    _dismiss_cookie_banner(recurly)

    recurly.locator("#first_name").fill(first_name)
    recurly.locator("#last_name").fill(last_name)
    recurly.locator("#postal_code").fill(POSTAL_CODE)
    print("    [upg] billing name filled; submitting")

    _submit_and_wait_success(recurly, card)
    print("    [upg] reached success page")
    return _read_success_package(recurly)


def _fill_card_fields(recurly: Page, card: str) -> None:
    next_year = str((datetime.datetime.now().year + 1) % 100)
    _fill_hosted_field(recurly, "#number", card)
    _fill_hosted_field(recurly, "#month", EXP_MONTH)
    _fill_hosted_field(recurly, "#year", next_year)
    _fill_hosted_field(recurly, "#cvv", CVV)


def _wait_for_hosted_fields(recurly: Page) -> None:
    """Wait for the Recurly hosted card-field iframes to mount.

    The checkout page redirects once on load, so early DOM reads can raise
    "Execution context was destroyed"; those transient errors are tolerated until the
    page settles and the `#number` field iframe appears.
    """
    deadline = datetime.datetime.now() + datetime.timedelta(seconds=IFRAME_MOUNT_TIMEOUT_S)
    while datetime.datetime.now() < deadline:
        try:
            if recurly.locator("#number iframe").count() > 0:
                # The iframe element existing is not enough; wait for its hosted
                # input to be interactable before the fill begins.
                recurly.frame_locator("#number iframe").locator(
                    "#recurly-hosted-field-input"
                ).wait_for(state="visible", timeout=2000)
                return
        except Exception:
            pass
        recurly.wait_for_timeout(500)
    raise AssertionError("Recurly hosted card fields did not mount")


def _dismiss_cookie_banner(recurly: Page) -> None:
    banner = recurly.locator("#onetrust-accept-btn-handler")
    if banner.count():
        try:
            banner.click(timeout=3000)
        except Exception:
            pass


def _fill_hosted_field(recurly: Page, container: str, value: str) -> None:
    """Clear and type into a Recurly hosted-field iframe character-by-character.

    The hosted inputs reject programmatic `.fill()`; tokenization only registers a
    value entered via real key events (press_sequentially). Focus is settled before
    typing and the field is cleared first (select-all + backspace) so a re-fill on a
    submit retry replaces any partial value rather than appending to it.
    """
    field = recurly.frame_locator(f"{container} iframe").locator("#recurly-hosted-field-input")
    field.click(timeout=5000)
    recurly.wait_for_timeout(150)
    field.press("Meta+a")
    field.press("Control+a")
    field.press("Backspace")
    field.press_sequentially(value, delay=70)


_TOKENIZE_AND_SUBMIT_JS = """() => new Promise((resolve) => {
  try {
    const btn = document.querySelector('button.pay');
    const form = (btn && btn.closest('form'))
      || document.querySelector('form.upgrade-container')
      || document.querySelector('form');
    if (!form || !window.recurly) { resolve('no-form-or-recurly'); return; }
    window.recurly.token(window.jQuery(form), function (err, token) {
      if (err) {
        const fields = (err.fields && err.fields.join(',')) || '';
        resolve('err:' + (err.message || err.code || 'unknown') + '|fields=' + fields);
        return;
      }
      try { form.submit(); } catch (e) {}
      resolve('ok:' + (token && token.id));
    });
    setTimeout(() => resolve('token-timeout'), 10000);
  } catch (e) { resolve('throw:' + String(e)); }
})"""


def _submit_and_wait_success(recurly: Page, card: str) -> None:
    """Fill the card fields, tokenize + submit, then wait for the success page.

    Recurly binds submission to a jQuery click handler that calls
    ``recurly.token(form, cb)`` then ``form.submit()`` on success. Driving that
    tokenization directly (instead of relying on the click event firing) is
    deterministic: ``recurly.token`` injects the hidden token field and the native
    ``form.submit()`` posts it. The card fields are (re)filled on each attempt so a
    dropped keystroke from a prior attempt is corrected. Retried ≤2 times; once
    navigation starts the evaluate can raise "Execution context was destroyed",
    which the success poll resolves.
    """
    last_result = None
    for attempt in range(SUBMIT_ATTEMPTS):
        try:
            _fill_card_fields(recurly, card)
            last_result = recurly.evaluate(_TOKENIZE_AND_SUBMIT_JS)
        except Exception as exc:
            # A transient hosted-field click timeout or a navigation that destroyed
            # the context during tokenize; the success poll below decides.
            last_result = f"fill-or-submit-error:{exc}"
        if _reached_success(recurly, SUBMIT_WAIT_S):
            return
        print(f"    [upg] submit attempt {attempt + 1} result={last_result!r}")
    raise AssertionError(
        f"upgrade did not reach the success page after submit retries; last={last_result!r}"
    )


def _reached_success(recurly: Page, timeout_s: float) -> bool:
    """Poll for the success-page title, tolerating context-destroyed reads."""
    deadline = datetime.datetime.now() + datetime.timedelta(seconds=timeout_s)
    while datetime.datetime.now() < deadline:
        try:
            if SUCCESS_TITLE in (recurly.title() or ""):
                return True
        except Exception:
            pass
        recurly.wait_for_timeout(500)
    return False


def _read_success_package(recurly: Page) -> str:
    package = recurly.locator("#main p em").first
    package.wait_for(state="visible", timeout=5000)
    return (package.inner_text() or "").strip()
