"""UI helpers for the payment_setups migration (VCITA2-14008).

Service creation for all six payment settings goes through the Angular advanced service
editor (serviceEditor.js): open the New-service dialog, set a literal address, route to
the advanced editor, pick the payment type from the price dropdown (and price where the
type takes one), then Save. Selectors reuse the proven categories-and-services flow and
the legacy ``serviceEditor.js`` page object.
"""

from __future__ import annotations

import re

from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from tests.tempo.scheduling.appointments.multistaff.multistaff_helpers import (
    meeting_text,
    open_meeting_page,
)
from tests.tempo.scheduling.payment_setups.payment_setups_common import EDITOR_OPTION
from tests.tempo.scheduling.services_categories.services_categories_actions import (
    _save_editor,
    _set_other_address,
    _wait_editor,
)
from tests.tempo.scheduling.services_categories.services_categories_helpers import (
    SERVICES_PATH,
    UI_TIMEOUT,
    app_base,
    frame,
)

# Advanced editor (serviceEditor.js) price controls.
EDITOR_PRICE_SELECT = "div.service-price md-select-value"
EDITOR_PRICE_INPUT = "div.service-price div.paid-service input"
# Settings-input style price input fallback (some editor versions).
EDITOR_PRICE_INPUT_ALT = 'div.service-price input[type="number"]'


NEW_SERVICE_BTN = re.compile("New service")
# Cold first navigation to the Angular services module (right after the gateway-iframe
# setup) can take longer than the 5s action cap to render; bounded for SPA module load.
SERVICES_LOAD_TIMEOUT = 20_000


def _open_new_service(page: Page, option_label: str):
    """Open the New-service dialog without requiring a pre-existing category card.

    The shared services helper waits for a category card before any action, but a fresh
    account starts with no category (only "+ Add category"). Service creation auto-creates
    the default "My Services" category, so here we only wait for the page heading and the
    always-present "New service" button. The New-service split button occasionally needs a
    second click when Angular has not yet bound its handler right after navigation, so the
    open is retried until the service-type option surfaces.
    """
    page.goto(
        f"{app_base(page)}{SERVICES_PATH}",
        wait_until="domcontentloaded",
        timeout=SERVICES_LOAD_TIMEOUT,
    )
    ng = frame(page)
    ng.get_by_role("heading", name="Settings / Services").wait_for(
        state="visible", timeout=SERVICES_LOAD_TIMEOUT
    )
    new_btn = ng.get_by_role("button", name=NEW_SERVICE_BTN)
    new_btn.wait_for(state="visible", timeout=UI_TIMEOUT)
    option = ng.get_by_role("menuitem", name=re.compile(option_label))

    last_error: Exception | None = None
    for _ in range(3):
        try:
            new_btn.click()
            option.wait_for(state="visible", timeout=2_000)
            option.click()
            ng.get_by_role("dialog").wait_for(state="visible", timeout=UI_TIMEOUT)
            return ng
        except PlaywrightTimeoutError as exc:
            last_error = exc
            page.wait_for_timeout(500)
    raise last_error or AssertionError("New-service menu did not open")


def _set_editor_payment(page: Page, ng, payment_setting: str, price: str | None) -> None:
    """Pick the payment type in the advanced editor and fill the price when applicable."""
    select = ng.locator(EDITOR_PRICE_SELECT).first
    select.wait_for(state="visible", timeout=UI_TIMEOUT)
    select.evaluate("el => el.click()")
    option = ng.get_by_role("option", name=EDITOR_OPTION[payment_setting])
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.evaluate("el => el.click()")
    if price is not None:
        price_input = ng.locator(EDITOR_PRICE_INPUT).first
        if price_input.count() == 0:
            price_input = ng.locator(EDITOR_PRICE_INPUT_ALT).first
        price_input.wait_for(state="visible", timeout=UI_TIMEOUT)
        price_input.fill(str(price))


WITH_FEE_BTN = re.compile("With fee", re.I)
QUICK_PRICE_INPUT = 'input[name="price"]'
# WITH-FEE shows "+N% tax  Edit"; the Edit link (legacy enableTaxFlow) opens the tax picker.
EDIT_TAXES_LINK = "a[ng-click='enableTaxFlow()']"


def _add_taxes(page: Page, ng, taxes: list[tuple[str, int]]) -> None:
    """Add extra tax(es) via the quick-dialog tax picker (default tax stays selected).

    Click the "Edit" tax link to reveal the Tax multi-select, open it, check each extra
    tax by ``[data-qa="tax-{name}-{rate}"]``, then Escape to commit and close it.
    """
    link = ng.locator(EDIT_TAXES_LINK).first
    link.wait_for(state="visible", timeout=UI_TIMEOUT)
    link.evaluate("el => el.click()")
    select = ng.locator("md-select").filter(has_text=re.compile("default_tax")).first
    select.wait_for(state="visible", timeout=UI_TIMEOUT)
    select.evaluate("el => el.click()")
    for tax_name, rate in taxes:
        option = ng.locator(f'[data-qa="tax-{tax_name}-{rate}"]').first
        option.wait_for(state="visible", timeout=UI_TIMEOUT)
        option.evaluate("el => el.click()")
    page.keyboard.press("Escape")


def create_service_ui(
    page: Page,
    name: str,
    payment_setting: str,
    price: str | None,
    taxes: list[tuple[str, int]] | None = None,
) -> None:
    """Create a 1-on-1 appointment service with the given payment setting via the UI.

    Taxed services take the WITH-FEE quick path (the tax link only renders with a fee),
    add their taxes, then route to the advanced editor to set the precise payment type.
    Untaxed services take the NO-FEE path. The default-for-services tax is auto-applied by
    the product, so only extra (non-default) taxes need to be passed in ``taxes``.
    """
    ng = _open_new_service(page, "1 on 1 appointment")
    ng.get_by_role("textbox", name="Service name *").fill(name)
    _set_other_address(page, ng)
    if taxes:
        ng.get_by_role("button", name=WITH_FEE_BTN).click()
        if price is not None:
            quick_price = ng.locator(QUICK_PRICE_INPUT).first
            quick_price.wait_for(state="visible", timeout=UI_TIMEOUT)
            quick_price.fill(str(price))
        _add_taxes(page, ng, taxes)
    else:
        ng.locator('button[data-qa="no-fee"]').click()
    ng.locator("md-dialog-actions button[ng-click='saveNewService(\"advanced\")']").click()
    _wait_editor(ng)
    _set_editor_payment(page, ng, payment_setting, price)
    _save_editor(page, ng)


def read_meeting_price(page: Page, appointment_id: str) -> str:
    """Read the meeting price from the appointment page (mirrors legacy getMeetingData).

    Returns "Free" for a free-labeled meeting, otherwise the balance-due text (e.g.
    "$100.00" or "$110.00 ($100.00 + Tax)"), or "" when no price/tax is shown."""
    outer = open_meeting_page(page, appointment_id)
    free = meeting_text(outer, "appointment-free")
    if free:
        return "Free"
    amount = meeting_text(outer, "balance-due-amount")
    return " ".join(amount.split())
