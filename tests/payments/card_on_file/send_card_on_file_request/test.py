"""Send a card-on-file request and verify it on the client and via email.

Migrates automation-js features/salsa/card-on-file.feature
(scenario: user sends request to add card on file).
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from playwright.sync_api import Page

from tests.payments.card_on_file.card_on_file_api import wait_for_email_subject
from tests.payments.card_on_file.card_on_file_ui import (
    read_card_request_text,
    send_card_on_file_request,
)

# The runner pins the business and browser to US Eastern, so the request date
# rendered on the client card is deterministic in this zone.
BUSINESS_TZ = ZoneInfo("America/New_York")
REQUEST_TEXT_PREFIX = "Card request sent on"
EMAIL_SUBJECT = "Confirm your preferred payment method"


def _expected_date_labels() -> list:
    """Today's date as the card label renders it ('Jun 01'), with a no-pad fallback."""
    now = datetime.now(BUSINESS_TZ)
    return [now.strftime("%b %d"), now.strftime("%b ") + str(now.day)]


def test_send_card_on_file_request(page: Page, context: dict) -> None:
    client_id = context["card_on_file_client_id"]

    print("  Step 1: Send a card-on-file request to the client...")
    send_card_on_file_request(page, context, client_id)

    print("  Step 2: Verify the client card shows the pending request...")
    request_text = read_card_request_text(page)
    expected_dates = _expected_date_labels()
    assert request_text.startswith(REQUEST_TEXT_PREFIX), (
        f"Expected card request label to start with '{REQUEST_TEXT_PREFIX}', got '{request_text}'"
    )
    assert any(date in request_text for date in expected_dates), (
        f"Card request label '{request_text}' did not contain today's date {expected_dates}"
    )
    print(f"    [OK] client card shows: '{request_text}'")

    print("  Step 3: Verify the client receives the confirmation email...")
    wait_for_email_subject(context, EMAIL_SUBJECT)
    print(f"    [OK] client received email: '{EMAIL_SUBJECT}'")
