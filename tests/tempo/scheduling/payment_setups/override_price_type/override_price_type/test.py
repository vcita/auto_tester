"""Update payment type during scheduling (VCITA2-14008).

Migrated from payment-setups.feature scenario "Update payment type during scheduling":
six services exist (created via API in _setup); when scheduling each appointment the price
type is overridden in the dialog, and the resulting meeting price is verified.
"""

from playwright.sync_api import Page

from tests.tempo.scheduling.appointments.multistaff.multistaff_helpers import (
    schedule_appointment,
)
from tests.tempo.scheduling.payment_setups.payment_setups_common import APPT_FEE_TYPE
from tests.tempo.scheduling.payment_setups.payment_setups_ui import read_meeting_price

# (service, override price_type, override amount, expected meeting price)
OVERRIDES = [
    ("require2pay", "display free", None, "Free"),
    ("suggest2pay", "display for a fee", None, ""),
    ("displayFee", "dont display", None, ""),
    ("variedPrice", "require to pay", "65", "65"),
    ("displayFree", "display a fee", "97", "97"),
    ("noDisplay", "suggest to pay", "25", "25"),
]


def test_override_price_type(page: Page, context: dict) -> None:
    client_name = context["ps"]["client"]["name"]

    for name, price_type, amount, expected in OVERRIDES:
        override = {"fee_type": APPT_FEE_TYPE[price_type], "amount": amount}
        appt_id = schedule_appointment(page, context, client_name, name, price_override=override)
        actual = read_meeting_price(page, appt_id)
        if expected == "Free":
            assert actual == "Free", f"{name}: expected Free meeting, got {actual!r}"
        elif expected == "":
            assert "$" not in actual, f"{name}: expected no price, got {actual!r}"
        else:
            assert expected in actual, f"{name}: expected price {expected!r} in {actual!r}"
    print("  [OK] Each overridden appointment shows the expected meeting price")
