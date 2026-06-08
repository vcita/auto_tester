from playwright.sync_api import Page

from tests.payments.payment_settings.payment_settings_api import set_allow_view_payments
from tests.payments.payment_settings.payment_settings_cp import payments_action_visible


def test_deny_payments_view(page: Page, context: dict) -> None:
    token = context["cp_client_token"]

    print("  Step 1: Verify the Payments action is available in the client portal by default")
    if not payments_action_visible(page, context, token):
        raise AssertionError("Payments action was not visible by default (expected it before denying)")

    print("  Step 2: Deny clients from viewing payments in the client portal (API)")
    set_allow_view_payments(context, False)

    print("  Step 3: Verify the Payments action is no longer shown in the client portal")
    if payments_action_visible(page, context, token):
        raise AssertionError("Payments action is still visible after denying view payments")
