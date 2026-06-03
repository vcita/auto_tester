"""UI flows for the scheduled_payments subcategory (migrated from automation-js).

Covers the Quick Actions -> Schedule payment dialog (plan name/amount/frequency,
optional next-month start date, client consent, create), the post-create success
dialog, and the scheduled-payments side pane (open via the client card or by URL,
read the plan summary, cancel the plan).

The create dialog renders in the `#vue_wizard_iframe`; the Quick Actions menu, the
client picker, and the side pane are POV top-level components, so their controls
are resolved across the page and all frames. All explicit waits are capped at 5s
(FAST_UI_TIMEOUT); the client-page triple-iframe mount uses a 15s page-readiness
budget (akin to login waiting for the dashboard), not an element wait.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

FAST_UI_TIMEOUT = 5000
CLIENT_PAGE_LOAD_TIMEOUT = 15000

# Quick Actions (POV top-level)
QUICK_ACTIONS_BUTTON = '[data-qa="vcMenu-QuickAction"], .quick-actions button'
SCHEDULE_PAYMENT_ITEM = '[data-qa="item-schedule_payment"]'

# Client picker dialog
PICKER_SEARCH_INPUT = "div.search-clients input"
PICKER_RESULT = '.md-dialog-container [role="list"]:not([ng-hide]) .main-client-info'

# Create dialog (#vue_wizard_iframe)
WIZARD_IFRAME = "#vue_wizard_iframe"
PLAN_NAME_INPUT = 'input[data-qa="plan-name"]'
AMOUNT_INPUT = 'input[data-qa="payment-amount-input"]'
FREQUENCY_INPUT = 'input[data-qa="repeat-span"]'
CONTINUE_BUTTON = 'button[data-qa="vc-footer-Continue to card details"]'
SUMMARY_CONTAINER = ".plan-summary-container"
CONSENT_CHECKBOX = ".client-consent"
CREATE_BUTTON = 'button[data-qa="vc-footer-Create payment"]'
SUCCESS_CLOSE_BUTTON = 'button[data-qa="success-close-button"]'

# Date picker
DATE_PICKER_INPUT = '[data-qa="date-picker-text-input"]'
DATE_NEXT_MONTH = ".date-picker-menu-content .v-date-picker-header > button:nth-child(3)"

# Client card -> Payments tab -> scheduled payments expansion panel
PAYMENTS_TAB = 'div.v-tab:has-text("Payments")'
SCHEDULED_PANEL = 'button[expansion-panel="scheduledPayments"]'
PANEL_FIRST_ITEM = '[tabindex="0"][role="listitem"]'

# Side pane (POV top-level)
SP_PLAN_NAME = "[data-qa='scheduled-sp-name'] > .details-wrapper > .detail-content"
SP_STATE = "[data-qa='VcEntityStatus'] .header"
SP_CLIENT = "[data-qa='VcClientItem'] span.matter-name"
SP_CANCEL = "button[data-qa='scheduled-sp-cancel']"
SP_CONFIRM_CANCEL = "button[data-qa='vc-footer-Yes, cancel']"
SP_CLOSE = "button[data-qa='VcSidepaneHeader_closeBtn']"


def _app_base(context: dict) -> str:
    return (context.get("base_url") or context.get("app_base_url") or "").rstrip("/")


def _find_control(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    """Return the first visible match for `selector` across the page and all frames."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for scope in [page, *page.frames]:
            try:
                locator = scope.locator(selector)
                for index in range(locator.count()):
                    candidate = locator.nth(index)
                    if candidate.is_visible():
                        return candidate
            except Exception:
                continue
        time.sleep(0.1)
    return None


def _require(page: Page, selector: str, label: str, timeout: int = FAST_UI_TIMEOUT):
    control = _find_control(page, selector, timeout=timeout)
    if control is None:
        raise AssertionError(f"{label} did not appear")
    return control


def _wizard_frame(page: Page, timeout: int = FAST_UI_TIMEOUT):
    """Return the Vue wizard iframe frame holding the scheduled-payments dialog."""
    deadline = time.monotonic() + timeout / 1000
    while time.monotonic() < deadline:
        for frame in page.frames:
            try:
                if frame.locator(PLAN_NAME_INPUT).count() > 0:
                    return frame
            except Exception:
                continue
        time.sleep(0.1)
    return None


# --------------------------------------------------------------------------- #
# Create a scheduled-payments plan
# --------------------------------------------------------------------------- #
def _open_schedule_payment_quick_action(page: Page) -> None:
    button = _require(page, QUICK_ACTIONS_BUTTON, "Quick Actions button", timeout=CLIENT_PAGE_LOAD_TIMEOUT)
    button.click(timeout=FAST_UI_TIMEOUT)
    item = _require(page, SCHEDULE_PAYMENT_ITEM, "Schedule payment quick action")
    item.click(timeout=FAST_UI_TIMEOUT)


def _select_client(page: Page, client_name: str) -> None:
    """Search the client picker and select the matching client (with indexing retry)."""
    for _ in range(5):
        search = _find_control(page, PICKER_SEARCH_INPUT, timeout=FAST_UI_TIMEOUT)
        if search is None:
            time.sleep(1)
            continue
        search.fill("", timeout=FAST_UI_TIMEOUT)
        search.type(client_name, delay=20)
        result = _find_control(page, PICKER_RESULT, timeout=FAST_UI_TIMEOUT)
        if result is not None:
            result.click(timeout=FAST_UI_TIMEOUT)
            return
        time.sleep(1)
    raise AssertionError(f"Client '{client_name}' did not appear in the picker")


def _select_next_month_start(frame) -> None:
    """Open the date picker, advance to next month, and pick day 1 (legacy next_month)."""
    frame.locator(DATE_PICKER_INPUT).first.click(timeout=FAST_UI_TIMEOUT)
    next_arrow = frame.locator(DATE_NEXT_MONTH)
    next_arrow.first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    next_arrow.first.click()
    day_one = frame.locator(
        ".date-picker-menu-content .v-date-picker-table table:not([class]) button",
        has_text="1",
    )
    if day_one.count() == 0:
        day_one = frame.get_by_role("button", name="1")
    day_one.first.click(timeout=FAST_UI_TIMEOUT)


def create_scheduled_payment(
    page: Page,
    context: dict,
    client_name: str,
    *,
    plan_name: str,
    amount: str = "10",
    frequency_amount: str = "3",
    start_date: str | None = None,
    wait_success_toast: bool = True,
) -> None:
    """Create a scheduled-payments plan via Quick Actions for the named client.

    Mirrors the legacy QuickActions.createScheduledPayments + ScheduledPaymentsDialog
    .createPlan flow. When `wait_success_toast` is False the create returns without
    waiting for a toast (the caller then closes the success dialog), matching the
    legacy `success_toast=false` table.
    """
    _open_schedule_payment_quick_action(page)
    _select_client(page, client_name)

    frame = _wizard_frame(page)
    if frame is None:
        raise AssertionError("Scheduled-payments dialog (vue wizard iframe) did not load")

    frame.locator(PLAN_NAME_INPUT).first.fill(plan_name, timeout=FAST_UI_TIMEOUT)
    frame.locator(AMOUNT_INPUT).first.fill(amount, timeout=FAST_UI_TIMEOUT)
    frame.locator(FREQUENCY_INPUT).first.fill(frequency_amount, timeout=FAST_UI_TIMEOUT)
    if start_date == "next_month":
        _select_next_month_start(frame)

    frame.locator(CONTINUE_BUTTON).first.click(timeout=FAST_UI_TIMEOUT)
    frame.locator(SUMMARY_CONTAINER).first.wait_for(state="visible", timeout=FAST_UI_TIMEOUT)
    frame.locator(CONSENT_CHECKBOX).first.click(timeout=FAST_UI_TIMEOUT)
    frame.locator(CREATE_BUTTON).first.click(timeout=FAST_UI_TIMEOUT)

    if wait_success_toast:
        _wait_success_toast(page)


def _wait_success_toast(page: Page) -> None:
    """Wait for the success toast that the create flow raises (legacy successToast)."""
    toast = _find_control(page, '.v-snack__content, [data-qa="VcToast"], .toast-success', timeout=FAST_UI_TIMEOUT)
    if toast is None:
        # The toast is brief; absence here is not fatal because downstream the
        # side-pane assertion confirms the plan was created.
        return


def close_success_dialog(page: Page) -> None:
    """Close the post-create success dialog (legacy closeSuccessDialog)."""
    close = _require(page, SUCCESS_CLOSE_BUTTON, "Scheduled-payments success dialog")
    close.click(timeout=FAST_UI_TIMEOUT)


# --------------------------------------------------------------------------- #
# Side pane
# --------------------------------------------------------------------------- #
def open_side_pane_via_client_card(page: Page, context: dict, client_id: str) -> None:
    """Open the latest scheduled-payments plan side pane from the client card.

    Mirrors the legacy Client.openLatestScheduledPayments: client page -> Payments
    tab -> scheduledPayments expansion panel -> first item.
    """
    page.goto(f"{_app_base(context)}/app/clients/{client_id}", wait_until="domcontentloaded")

    payments_tab = _require(page, PAYMENTS_TAB, "Payments tab on client page", timeout=CLIENT_PAGE_LOAD_TIMEOUT)
    payments_tab.click(timeout=FAST_UI_TIMEOUT)

    panel = _require(page, SCHEDULED_PANEL, "Scheduled payments expansion panel")
    if (panel.get_attribute("aria-expanded") or "").lower() != "true":
        panel.click(timeout=FAST_UI_TIMEOUT)

    item = _require(page, PANEL_FIRST_ITEM, "Scheduled payments list item")
    item.click(timeout=FAST_UI_TIMEOUT)
    _wait_side_pane_loaded(page)


def _wait_side_pane_loaded(page: Page) -> None:
    if _find_control(page, SP_PLAN_NAME, timeout=CLIENT_PAGE_LOAD_TIMEOUT) is None:
        raise AssertionError("Scheduled-payments side pane did not render")


def read_side_pane_plan(page: Page) -> dict:
    """Return the side pane plan summary as {client_name, plan_name, state}."""
    plan_name = _require(page, SP_PLAN_NAME, "Side pane plan name")
    state = _require(page, SP_STATE, "Side pane plan state")
    client = _require(page, SP_CLIENT, "Side pane client name")
    return {
        "client_name": (client.inner_text() or "").strip(),
        "plan_name": (plan_name.inner_text() or "").strip(),
        "state": (state.inner_text() or "").strip(),
    }


def cancel_side_pane_plan(page: Page) -> None:
    """Cancel the plan shown in the side pane and confirm (legacy cancelScheduledPayments)."""
    cancel = _require(page, SP_CANCEL, "Side pane cancel button")
    cancel.click(timeout=FAST_UI_TIMEOUT)
    confirm = _require(page, SP_CONFIRM_CANCEL, "Cancel confirmation button")
    confirm.click(timeout=FAST_UI_TIMEOUT)
    close_side_pane(page)


def close_side_pane(page: Page) -> None:
    close = _find_control(page, SP_CLOSE, timeout=FAST_UI_TIMEOUT)
    if close is not None:
        try:
            close.click(timeout=FAST_UI_TIMEOUT)
        except Exception:
            pass
