"""Mock payment-gateway connection for the tips_settings edit_persist setup.

Setup prerequisite (not the feature under test): mirrors the legacy
configureMockPaymentGateway flow. The payment providers dialog renders inside the
Angular child_app iframe. The mock provider is hidden until the "show all
providers" link is clicked, and the connect action opens an external gateway popup
window. The reveal link and Save button are zero-size inline Angular controls that
Playwright reports as not visible, so they are triggered via a DOM click. The popup
close + parent "Disconnect" transition is an external-gateway round trip, polled
(beyond the 5s UI cap) as eventual consistency.
"""

import time

from playwright.sync_api import Page

from tests.payments.tips_settings.tips_helpers import FAST_UI_TIMEOUT, scope_with

PROVIDERS_MENU_ITEM = '[data-qa="item-payment-providers"]'
PROVIDER_MOCK = '[data-qa="provider-name-mock"]'
PROVIDER_MOCK_CONNECT = '[data-qa="provider-name-mock"] .connection-button'
PROVIDERS_SAVE = '[data-qa="providers-dialog-save"]'
GATEWAY_CONNECT_TIMEOUT = 15000
GATEWAY_SAVE_SETTLE_TIMEOUT = 5000

PROVIDERS_MARKER = (
    '[data-qa^="provider-name-"], [data-qa="providers-dialog-save"], a:has-text("click here")'
)


def _providers_frame(page: Page, timeout: int = FAST_UI_TIMEOUT):
    """Return the Angular child_app iframe that holds the payment providers dialog."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            if "child_app" not in (frame.url or ""):
                continue
            try:
                if frame.locator(PROVIDERS_MARKER).count() > 0:
                    return frame
            except Exception:
                continue
        time.sleep(0.1)
    return None


def _open_providers_dialog(page: Page):
    """Open the payment providers dialog deterministically and return its iframe."""
    frame = _providers_frame(page, timeout=2000)
    if frame is not None:
        return frame
    menu_scope = scope_with(page, PROVIDERS_MENU_ITEM, timeout=FAST_UI_TIMEOUT)
    if menu_scope is not None:
        item = menu_scope.locator(PROVIDERS_MENU_ITEM).first
        try:
            item.click(timeout=FAST_UI_TIMEOUT)
        except Exception:
            item.evaluate("(el) => el.click()")
    return _providers_frame(page, timeout=FAST_UI_TIMEOUT)


def _js_click_all(frame, selector: str) -> int:
    """DOM-click every match (handles zero-size inline Angular controls). Returns count."""
    locator = frame.locator(selector)
    count = locator.count()
    for index in range(count):
        try:
            locator.nth(index).evaluate("(el) => el.click()")
        except Exception:
            continue
    return count


def _reveal_all_providers(frame) -> None:
    """Click the 'show all providers' link so the mock provider card renders."""
    deadline = time.monotonic() + FAST_UI_TIMEOUT / 1000
    while time.monotonic() < deadline:
        if frame.locator(PROVIDER_MOCK).count() > 0:
            return
        _js_click_all(frame, 'a:has-text("click here")')
        time.sleep(0.3)
    if frame.locator(PROVIDER_MOCK).count() == 0:
        raise AssertionError("Mock payment provider card did not appear after revealing providers")


def _submit_mock_popup(popup) -> None:
    popup.wait_for_load_state("domcontentloaded", timeout=GATEWAY_CONNECT_TIMEOUT)
    secret = popup.locator("#secret")
    secret.wait_for(state="visible", timeout=GATEWAY_CONNECT_TIMEOUT)
    secret.fill("bla", timeout=FAST_UI_TIMEOUT)
    popup.locator("#alias").fill("blu", timeout=FAST_UI_TIMEOUT)
    submit = popup.locator("button[type=submit]")
    submit.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    submit.click()


def _save_when_mock_connected(page: Page) -> None:
    """Poll until the mock card shows the connected (Disconnect) state, then save."""
    deadline = time.monotonic() + GATEWAY_CONNECT_TIMEOUT / 1000
    while time.monotonic() < deadline:
        frame = _providers_frame(page, timeout=1000)
        if frame is not None:
            connect_btn = frame.locator(PROVIDER_MOCK_CONNECT)
            if connect_btn.count() > 0 and "Disconnect" in (connect_btn.first.inner_text() or ""):
                _js_click_all(frame, PROVIDERS_SAVE)
                try:
                    page.wait_for_load_state("networkidle", timeout=GATEWAY_SAVE_SETTLE_TIMEOUT)
                except Exception:
                    pass
                return
        time.sleep(0.5)
    raise AssertionError("Mock gateway did not reach the connected state after submitting the popup")


def connect_mock_gateway(page: Page, context: dict) -> None:
    """Connect the mock payment provider so isCheckoutEnabled becomes true.

    Setup prerequisite (not the feature under test): mirrors the legacy
    configureMockPaymentGateway flow (reveal providers, connect mock via popup, save).
    """
    base = (context.get("base_url") or "").rstrip("/")
    page.goto(f"{base}/app/settings/payments", wait_until="domcontentloaded")

    frame = _open_providers_dialog(page)
    if frame is None:
        raise AssertionError("Payment providers dialog (Angular iframe) did not load")

    _reveal_all_providers(frame)
    frame.locator(PROVIDER_MOCK).first.evaluate("(el) => el.click()")

    _connect_mock_popup_with_retry(page, frame)
    _save_when_mock_connected(page)


def _connect_mock_popup_with_retry(page: Page, frame) -> None:
    """Open the external mock-gateway popup, fill + submit it, retrying once.

    The popup is an external-gateway round trip that can transiently load slowly
    (occasionally past the default nav budget), so a single failed open/submit is
    retried rather than failing the whole setup.
    """
    last_error: Exception | None = None
    for _ in range(2):
        popup = None
        try:
            with page.context.expect_page(timeout=GATEWAY_CONNECT_TIMEOUT) as popup_info:
                frame.locator(PROVIDER_MOCK_CONNECT).first.evaluate("(el) => el.click()")
            popup = popup_info.value
            _submit_mock_popup(popup)
            try:
                popup.wait_for_event("close", timeout=GATEWAY_CONNECT_TIMEOUT)
            except Exception:
                pass
            return
        except Exception as error:
            last_error = error
            if popup is not None and not popup.is_closed():
                try:
                    popup.close()
                except Exception:
                    pass
    raise AssertionError(f"Mock-gateway popup did not complete after 2 attempts: {last_error}")
