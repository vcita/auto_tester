"""Point-of-Sale tipping UI flows for the tips_checkout migration (VCITA2-13899).

Covers tips.feature scenario 2 ("take payment with tips via Point of Sale"):
- start a sale from Quick Actions -> Take payment (POS) for a client,
- add all open payment requests (the unpaid service + package), checkout -> Record
  payment with a tip (action 1),
- create a custom item, checkout -> Record payment with a custom tip (action 2).

The POS catalog/checkout is POV top-level; the take-payment dialog that opens from the
checkout Record action is the same Angular md-dialog used by close-balance, so the tip
picker / method picker / confirm primitives are reused from ``tips_checkout_bo``.
"""

from __future__ import annotations

from playwright.sync_api import Page

from tests.payments.deposits.deposits_invoice_ui import (
    FAST_UI_TIMEOUT,
    LOAD_TIMEOUT,
    QUICK_ACTIONS_BUTTON,
    _find_control,
    _require,
    _select_client,
)
from tests.payments.tips_checkout.tips_checkout_bo import (
    METHOD_OPTION,
    METHOD_SELECT,
    TIP_SELECT,
    _apply_tip,
    _confirm_and_close,
    _scope_with,
    _select_md_option,
)

# The DS VcLargeQuickAction overrides the parent's data-qa with its own (empty) dataQa
# prop, so `[data-qa=VcLargeQuickAction-point_of_sale]` never renders. Target the large
# action by its class + visible label (POS is the only large "Take payment" action).
POS_QUICK_ACTION = ('[data-qa="VcLargeQuickAction-point_of_sale"], '
                    '.VcLargeQuickAction:has-text("Take payment")')
ADD_UNPAID_BTN = '.client-details-container [role="alert"] [type="button"]'
CHECKOUT_ACTIVATOR = '[data-qa="checkout-actions-activator"]'
CHECKOUT_RECORD = '[data-qa="checkout-action-record"]'
CREATE_CUSTOM_ITEM_BTN = '[data-qa="pos-add-custom-item"]'
CUSTOM_ITEM_NAME = "[data-qa=item-name]"
CUSTOM_ITEM_PRICE = "[data-qa=custom-item-price]"
CUSTOM_ITEM_ADD = 'button[data-qa="vc-footer-Add"]'
POS_TAKE_PAYMENT_DIALOG = "md-dialog.take-payment-wrapper, md-dialog.close-balance-content"


def _open_pos_for_client(page: Page, client_name: str) -> None:
    """Open Quick Actions and click the POS Take payment large action.

    The large actions load asynchronously (skeletons first), so wait the full load
    budget for the POS action. Re-clicking the menu button toggles it closed, so the
    menu is opened exactly once and only re-opened if it is not currently showing."""
    button = _require(page, QUICK_ACTIONS_BUTTON, "Quick Actions button", timeout=LOAD_TIMEOUT)
    button.click(timeout=FAST_UI_TIMEOUT)
    pos = _find_control(page, POS_QUICK_ACTION, timeout=LOAD_TIMEOUT)
    if pos is None:
        # Menu may not have opened on the first click; toggle once more and wait.
        button = _require(page, QUICK_ACTIONS_BUTTON, "Quick Actions button", timeout=LOAD_TIMEOUT)
        button.click(timeout=FAST_UI_TIMEOUT)
        pos = _find_control(page, POS_QUICK_ACTION, timeout=LOAD_TIMEOUT)
    if pos is None:
        raise AssertionError("POS Take payment action did not appear in Quick Actions")
    pos.click(timeout=FAST_UI_TIMEOUT)
    _select_client(page, client_name)


def _checkout_record_with_tip(page: Page, *, record_type: str, tip_option: str,
                              tip_amount: str | None = None) -> None:
    _require(page, CHECKOUT_ACTIVATOR, "POS checkout activator", timeout=LOAD_TIMEOUT).click(
        timeout=FAST_UI_TIMEOUT)
    _require(page, CHECKOUT_RECORD, "POS record-payment action").click(timeout=FAST_UI_TIMEOUT)
    scope = _scope_with(page, TIP_SELECT) or page
    _select_md_option(scope, METHOD_SELECT, METHOD_OPTION, record_type)
    _apply_tip(scope, tip_option, tip_amount)
    _confirm_and_close(scope, POS_TAKE_PAYMENT_DIALOG)


def take_open_requests_via_pos(page: Page, context: dict, *, client_name: str,
                               record_type: str, tip_option: str) -> None:
    """Sale from open requests: POS for client -> add all unpaid items -> record + tip."""
    _open_pos_for_client(page, client_name)
    add_btn = _require(page, ADD_UNPAID_BTN, "POS add-unpaid-items button", timeout=LOAD_TIMEOUT)
    add_btn.click(timeout=FAST_UI_TIMEOUT)
    _checkout_record_with_tip(page, record_type=record_type, tip_option=tip_option)


def take_custom_item_via_pos(page: Page, context: dict, *, client_name: str, item_name: str,
                             amount: str, record_type: str, tip_option: str,
                             tip_amount: str | None = None) -> None:
    """Custom-item sale: POS for client -> add custom item -> record + tip."""
    _open_pos_for_client(page, client_name)
    _require(page, CREATE_CUSTOM_ITEM_BTN, "POS create custom item").click(timeout=FAST_UI_TIMEOUT)
    _require(page, CUSTOM_ITEM_NAME, "Custom item name field").fill(item_name, timeout=FAST_UI_TIMEOUT)
    _require(page, CUSTOM_ITEM_PRICE, "Custom item price field").fill(str(amount), timeout=FAST_UI_TIMEOUT)
    _require(page, CUSTOM_ITEM_ADD, "Custom item Add button").click(timeout=FAST_UI_TIMEOUT)
    _checkout_record_with_tip(page, record_type=record_type, tip_option=tip_option,
                              tip_amount=tip_amount)
