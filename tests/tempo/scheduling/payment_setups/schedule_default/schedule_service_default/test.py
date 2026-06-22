"""Schedule service default (VCITA2-14008).

Migrated from payment-setups.feature scenario "Schedule service default": create the six
payment-setting services via the UI, verify each on the services list, schedule an
appointment for each, and verify the meeting price.
"""

from playwright.sync_api import Page

from tests.tempo.scheduling.payment_setups.payment_setups_ui import (
    create_service_ui,
    read_meeting_price,
)
from tests.tempo.scheduling.services_categories.services_categories_helpers import (
    assert_service_details,
)
from tests.tempo.scheduling.appointments.multistaff.multistaff_helpers import schedule_appointment

# (service_name, payment_setting, price)
SERVICES = [
    ("require2pay", "require to pay", "100"),
    ("suggest2pay", "suggest to pay", "50"),
    ("displayFee", "display a fee", "10"),
    ("variedPrice", "display for a fee", None),
    ("displayFree", "display free", None),
    ("noDisplay", "dont display", None),
]

# Expected services-list tokens (payment type + price).
LIST_CONTAINS = {
    "require2pay": ["$100"],
    "suggest2pay": ["$50"],
    "displayFee": ["$10"],
    "variedPrice": ["For a fee"],
    "displayFree": ["Free"],
}

# Expected meeting price per service (legacy meeting_price column).
MEETING_PRICE = {
    "require2pay": "100",
    "suggest2pay": "50",
    "displayFee": "10",
    "variedPrice": "",
    "displayFree": "Free",
    "noDisplay": "",
}


def test_schedule_service_default(page: Page, context: dict) -> None:
    client_name = context["ps"]["client"]["name"]

    for name, setting, price in SERVICES:
        create_service_ui(page, name, setting, price)
    print("  [OK] Created six payment-setting services via UI")

    for name, tokens in LIST_CONTAINS.items():
        assert_service_details(page, name, contains=tokens)
    assert_service_details(page, "noDisplay", contains=[], excludes=["$"])
    print("  [OK] Services list shows the expected payment type/price per service")

    for name, _setting, _price in SERVICES:
        appt_id = schedule_appointment(page, context, client_name, name)
        actual = read_meeting_price(page, appt_id)
        expected = MEETING_PRICE[name]
        if expected == "Free":
            assert actual == "Free", f"{name}: expected Free meeting, got {actual!r}"
        elif expected == "":
            assert "$" not in actual, f"{name}: expected no price, got {actual!r}"
        else:
            assert expected in actual, f"{name}: expected price {expected!r} in {actual!r}"
    print("  [OK] Each scheduled appointment shows the expected meeting price")
