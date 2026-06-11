# Source: tests/payments/payments_emails/estimate_mail_cp/estimate_mail_cp/script.md
# Migrated from automation-js/features/salsa/payments-emails.feature (VCITA2-14027)

from playwright.sync_api import Page

from tests.email_api import email_link, wait_for_email
from tests.payments.payments_emails.payments_emails_api import create_estimate_email_action
from tests.payments.payments_emails.payments_emails_confirm import assert_cp_estimate_from_email

ESTIMATE_EMAIL_PREFIX = "New estimate from "


def test_estimate_mail_cp(page: Page, context: dict) -> None:
    """Estimate creation mails the client; the email link opens the CP estimate page."""
    print("  Step 1: Create estimate 'bestimate' via API (send_email=true)")
    create_estimate_email_action(context, title="bestimate", address="Babylon, persia")

    print("  Step 2: Verify 'New estimate from ...' email")
    email = wait_for_email(context, ESTIMATE_EMAIL_PREFIX, match="prefix")

    print("  Step 3: Open CP from the email link and assert the estimate page")
    assert_cp_estimate_from_email(
        page, email_link(email),
        title="bestimate", number="#0000001", price="10", client="first last",
        items=[{"name": "product21", "description": "description for payable item21",
                "price": "10"}],
        status_actions=["APPROVE", "REJECT"],
    )
    print("  [OK] estimate email + CP estimate page verified")
