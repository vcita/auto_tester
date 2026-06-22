"""UI helpers for the coupons subcategory.

Coupons settings and the appointment payment-status card both render in the
legacy Angular frontage iframe (Angular Material `md-*` widgets). All waits are
condition-based and capped at 5s per the autotester wait policy.
"""

import re
import time

from playwright.sync_api import Page, expect

UI_TIMEOUT = 5000
PAGE_TIMEOUT = 20000
LIST_SETTLE_SECONDS = 5

CREATE_COUPON_BUTTON = '[data-qa="action-button-coupons-new"]'
COUPON_TYPE_SELECT = 'md-select[name="coupon_type"]'
COUPON_NAME_INPUT = 'input[name="name"]'
COUPON_AMOUNT_INPUT = 'input[name="amount"]'
SAVE_COUPON_BUTTON = 'button[ng-click="save(clientForm)"]'
# The post-save share/promote dialog's "Maybe later" button. Targeted by its own
# translate key so it never collides with the create dialog's generic cancel button.
PROMOTE_DISMISS_BUTTON = 'md-dialog-actions button[translate="settings.coupons.coupon_ready.close"]'

LIST_ITEM = ".list-item"
COUPON_TITLE = "div.titles .md-title .title"
COUPON_DISCOUNT = ".additional-fields-container .additional-field"

# The appointment page has two `ps-more-actions` buttons (appointment header and
# payment card). Scope to the payment card (the one showing the balance) so the
# correct menu — the one containing "Apply coupon" — opens.
PS_MORE_ACTIONS = '.details-card:has(div.balance-due-amount) [data-qa="ps-more-actions"]'
APPLY_COUPON_ACTION = '[data-qa="apply_coupon"]'
COUPON_PICKER = 'md-select[ng-model="coupon"]'
APPLY_SAVE_BUTTON = 'md-dialog-actions button[ng-click="save()"]'
PS_STATUS = "div.status-payment"
PS_BALANCE = "div.balance-due-amount"


def angular_scope(page: Page):
    page.locator('iframe[title="angularjs"]').first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return page.frame_locator('iframe[title="angularjs"]')


def app_base_url(page: Page) -> str:
    if "/app/" not in page.url:
        raise ValueError(f"Cannot infer app base URL from current page URL: {page.url}")
    return page.url.split("/app/")[0]


def open_coupons_settings(page: Page):
    if "settings/coupons" not in page.url:
        page.goto(
            f"{app_base_url(page)}/app/settings/coupons?tab=coupons",
            wait_until="domcontentloaded",
            timeout=PAGE_TIMEOUT,
        )
        page.wait_for_url("**/settings/coupons**", timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
    scope = angular_scope(page)
    scope.locator(CREATE_COUPON_BUTTON).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return scope


def _pick_option(scope, select_locator: str, option_text: str) -> None:
    scope.locator(select_locator).first.click()
    option = scope.get_by_role("option", name=re.compile(re.escape(option_text), re.I))
    option.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.first.click()


def create_coupon(page: Page, scope, coupon_type: str, name: str, amount: str) -> None:
    """Create one coupon through Settings/Coupons and dismiss the share dialog.

    The post-save share dialog opening is the save confirmation. The coupons list
    behind it does not refresh live, so creation is confirmed by the dialog rather
    than by reading the (stale) list here; the list is reloaded in `assert_coupons`.
    """
    scope.locator(CREATE_COUPON_BUTTON).first.click()
    _pick_option(scope, COUPON_TYPE_SELECT, coupon_type)
    scope.locator(COUPON_NAME_INPUT).first.fill(name)
    scope.locator(COUPON_AMOUNT_INPUT).first.fill(amount)
    scope.locator(SAVE_COUPON_BUTTON).first.click()

    dismiss = scope.locator(PROMOTE_DISMISS_BUTTON).first
    dismiss.wait_for(state="visible", timeout=UI_TIMEOUT)
    dismiss.click()
    dismiss.wait_for(state="hidden", timeout=UI_TIMEOUT)


def list_coupons(scope) -> dict:
    items = scope.locator(LIST_ITEM)
    coupons = {}
    for index in range(items.count()):
        item = items.nth(index)
        title = item.locator(COUPON_TITLE)
        discount = item.locator(COUPON_DISCOUNT)
        if title.count() == 0 or discount.count() == 0:
            continue
        coupons[title.first.inner_text().strip()] = discount.first.inner_text().strip()
    return coupons


def assert_coupons(page: Page, expected: dict) -> None:
    """Reload the coupons list (it does not refresh live after creation), then poll
    until every expected name -> discount is present."""
    page.reload(wait_until="domcontentloaded", timeout=PAGE_TIMEOUT)
    scope = open_coupons_settings(page)
    scope.locator(LIST_ITEM).first.wait_for(state="visible", timeout=UI_TIMEOUT)

    deadline = time.monotonic() + LIST_SETTLE_SECONDS
    actual = {}
    while time.monotonic() < deadline:
        actual = list_coupons(angular_scope(page))
        if all(actual.get(name) == discount for name, discount in expected.items()):
            return
        time.sleep(0.5)
    raise AssertionError(f"Expected coupons {expected}, got {actual}")


def open_appointment(page: Page, base_url: str, booking_id: str):
    page.goto(
        f"{base_url}/app/appointments/{booking_id}",
        wait_until="domcontentloaded",
        timeout=PAGE_TIMEOUT,
    )
    page.wait_for_url("**/app/appointments/**", timeout=PAGE_TIMEOUT, wait_until="domcontentloaded")
    scope = angular_scope(page)
    scope.locator(PS_BALANCE).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    return scope


def apply_coupon(page: Page, scope, coupon_name: str) -> None:
    """Apply a coupon to the open appointment through the payment-status card.

    The save dialog closing is the only client-side signal; the updated balance is
    verified reactively by `assert_payment_request`, which polls, so no extra
    success-toast wait is needed here.
    """
    scope.locator(PS_MORE_ACTIONS).first.click()
    apply_action = scope.locator(APPLY_COUPON_ACTION).first
    apply_action.wait_for(state="visible", timeout=UI_TIMEOUT)
    apply_action.click()

    _pick_option(scope, COUPON_PICKER, coupon_name)
    save_button = scope.locator(APPLY_SAVE_BUTTON).first
    save_button.click()
    save_button.wait_for(state="hidden", timeout=UI_TIMEOUT)


def assert_payment_request(page: Page, state: str, amount: str) -> None:
    scope = angular_scope(page)
    expect(scope.locator(PS_STATUS).first).to_contain_text(state, timeout=UI_TIMEOUT)
    expect(scope.locator(PS_BALANCE).first).to_contain_text(amount, timeout=UI_TIMEOUT)
