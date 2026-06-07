"""UI flow for the vcita-payments onboarding wizard (gateway_setups scenarios 1-3).

Opens the payment onboarding wizard from the Getting-Started checklist and drives the
Vue wizard that renders inside the nested ``vue_wizard_iframe`` (POV -> Angular ->
Vue wizard). Because the wizard is 3 iframes deep, controls are resolved by scanning the
page and every frame for the legacy ``data-qa`` selectors instead of switching frames
manually (Playwright exposes a flat frame list at any depth).

Covers: open wizard, advance the get-paid step, read / fill the preliminary profession
(Vuetify autocomplete), read the currency-step next-button disabled state, try to connect
a gateway (funnel-v1 upgrade path), and assert the upgrade / MCC dialog is shown.

Waits are capped at 5s for element interactions; the wizard mount (3-level iframe load)
gets a bounded 20s readiness budget.
"""

from __future__ import annotations

import time

from playwright.sync_api import Page

FAST_UI_TIMEOUT = 5000
WIZARD_LOAD_TIMEOUT = 20000

# Getting-Started checklist (Angular BO)
CHECKLIST_BUTTON = '[name="checklist"]'
WIZARD_OPEN_MARKER = "body.wizard-open"
CHECKLIST_PAYMENTS_ITEM = "[data-qa='payments_settings']"
OPEN_PAYMENT_WIZARD = "[data-qa='open-payment-wizard-action']"

# Vue wizard (vue_wizard_iframe)
GET_PAID_NEXT = "[data-qa='get-paid-next']"
SET_CURRENCY_NEXT = "[data-qa='set-currency-next']"
CONFIRM_BUTTON = "[data-qa='vc-btn']"
THIRD_PARTY_GATEWAYS_LINK = "[data-qa='third-party-gateways-link']"
STRIPE_CONNECT = "[data-qa='stripe-connect']"
PROFESSION_AUTOCOMPLETE = "[data-qa='profession-autocomplete']"
PROFESSION_OPTION = ".v-list-item__title"
WIZARD_APP_ROOT = "#app"

# Bounded number of business-details / MCC clarification interstitials to click through
# while walking toward the third-party gateways step.
MAX_INTERSTITIALS = 3


def _scan(page: Page, selector: str, timeout: int = FAST_UI_TIMEOUT):
    """Return the first visible match for `selector` across the page and every frame."""
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
        time.sleep(0.15)
    return None


def _require(page: Page, selector: str, label: str, timeout: int = FAST_UI_TIMEOUT):
    control = _scan(page, selector, timeout=timeout)
    if control is None:
        raise AssertionError(f"{label} did not appear ({selector})")
    return control


def _click(page: Page, selector: str, label: str, timeout: int = FAST_UI_TIMEOUT) -> None:
    control = _require(page, selector, label, timeout=timeout)
    try:
        control.click(timeout=FAST_UI_TIMEOUT)
    except Exception:
        control.evaluate("(element) => element.click()")


def open_payment_wizard(page: Page) -> None:
    """Open the payment onboarding wizard from the Getting-Started checklist."""
    _click(page, CHECKLIST_BUTTON, "Getting-Started checklist button", timeout=WIZARD_LOAD_TIMEOUT)
    _require(page, WIZARD_OPEN_MARKER, "Wizard-open body marker", timeout=WIZARD_LOAD_TIMEOUT)
    _click(page, CHECKLIST_PAYMENTS_ITEM, "Payments checklist item", timeout=WIZARD_LOAD_TIMEOUT)
    _click(page, OPEN_PAYMENT_WIZARD, "Open payment wizard action", timeout=WIZARD_LOAD_TIMEOUT)
    # Wait for the Vue wizard get-paid step to mount inside vue_wizard_iframe.
    _require(page, GET_PAID_NEXT, "Get-paid step (wizard mount)", timeout=WIZARD_LOAD_TIMEOUT)


def advance_get_paid_step(page: Page) -> None:
    _click(page, GET_PAID_NEXT, "Get-paid step next button")


def read_preliminary_profession(page: Page) -> str:
    """Advance to the preliminary step and read the prepopulated profession value."""
    advance_get_paid_step(page)
    _click(page, PROFESSION_AUTOCOMPLETE, "Profession autocomplete")
    option = _require(page, PROFESSION_OPTION, "Profession dropdown value")
    return (option.inner_text(timeout=FAST_UI_TIMEOUT) or "").strip()


def currency_next_disabled(page: Page) -> bool:
    """Advance the get-paid step and report whether the currency-step next button is disabled.

    Mirrors legacy ``getPreliminaryNextButtonDisableState`` (reads the ``disabled``
    attribute on ``set-currency-next``)."""
    advance_get_paid_step(page)
    button = _require(page, SET_CURRENCY_NEXT, "Set-currency next button")
    disabled = button.get_attribute("disabled", timeout=FAST_UI_TIMEOUT)
    return disabled is not None


def fill_preliminary_profession(page: Page, profession: str) -> None:
    """Fill the Vuetify profession autocomplete and advance past the preliminary step."""
    autocomplete = _require(page, PROFESSION_AUTOCOMPLETE, "Profession autocomplete")
    autocomplete.click(timeout=FAST_UI_TIMEOUT)
    autocomplete.fill(profession, timeout=FAST_UI_TIMEOUT)
    _click(page, PROFESSION_OPTION, "Profession dropdown value")
    _click(page, SET_CURRENCY_NEXT, "Set-currency next button")


def _affirm_interstitial(page: Page) -> bool:
    """Click a business-details / MCC clarification confirm button if one is showing.

    The funnel-v1 + legal_services flow surfaces a "Just one more thing" MCC clarification
    ("...Bankruptcy law related services" -> "Yes, these apply") between the currency step
    and the connect-to-providers step. Prefer the affirmative text, then the generic
    wizard confirm button. Returns True if something was clicked."""
    for scope in [page, *page.frames]:
        try:
            affirm = scope.get_by_role("button", name="Yes, these apply")
            if affirm.count() > 0 and affirm.first.is_visible():
                affirm.first.click(timeout=FAST_UI_TIMEOUT)
                return True
        except Exception:
            continue
    confirm = _scan(page, CONFIRM_BUTTON, timeout=1000)
    if confirm is not None:
        try:
            confirm.click(timeout=FAST_UI_TIMEOUT)
        except Exception:
            confirm.evaluate("(element) => element.click()")
        return True
    return False


def _advance_to_third_party_link(page: Page):
    """Reach the third-party gateways link, clicking through bounded interstitials."""
    for _ in range(MAX_INTERSTITIALS):
        link = _scan(page, THIRD_PARTY_GATEWAYS_LINK, timeout=FAST_UI_TIMEOUT)
        if link is not None:
            return link
        if not _affirm_interstitial(page):
            break
    return _require(page, THIRD_PARTY_GATEWAYS_LINK, "Third-party gateways link")


def try_connect_gateway(page: Page) -> None:
    """Walk the wizard toward connecting a third-party (Stripe) gateway.

    Mirrors legacy ``tryConnectToPaymentGateway``: get-paid-next -> set-currency-next ->
    (business-details / MCC clarification) -> third-party-gateways-link -> stripe-connect.
    On a funnel-v1 account this surfaces the upgrade dialog."""
    _click(page, GET_PAID_NEXT, "Get-paid step next button")
    _click(page, SET_CURRENCY_NEXT, "Set-currency next button")
    link = _advance_to_third_party_link(page)
    try:
        link.click(timeout=FAST_UI_TIMEOUT)
    except Exception:
        link.evaluate("(element) => element.click()")
    _click(page, STRIPE_CONNECT, "Stripe connect button")


def assert_wizard_dialog_present(page: Page, *, label: str) -> None:
    """Assert the wizard dialog (upgrade / MCC) is shown.

    Mirrors the legacy dialog steps, which assert the Vue wizard root (``#app``) is present
    inside ``vue_wizard_iframe`` after the action."""
    root = _scan(page, WIZARD_APP_ROOT, timeout=WIZARD_LOAD_TIMEOUT)
    if root is None:
        raise AssertionError(f"{label} dialog did not appear (wizard #app not present)")


def assert_mcc_dialog_present(page: Page) -> None:
    """Assert the MCC clarification dialog is shown (confirm button + wizard root)."""
    _require(page, CONFIRM_BUTTON, "MCC dialog confirm button", timeout=WIZARD_LOAD_TIMEOUT)
    assert_wizard_dialog_present(page, label="MCC")
