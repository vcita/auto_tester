# Source: tests/payments/payments_emails/package_assigned/package_assigned_email/script.md
# Migrated from automation-js/features/salsa/payments-emails.feature (VCITA2-14027)

from playwright.sync_api import Page

from tests.email_api import wait_for_email
from tests.salsa.payments.payments_emails.payments_emails_api import assign_seeded_package

PACKAGE_EMAIL = 'Your new "package" package information and details'


def test_package_assigned_email(page: Page, context: dict) -> None:
    """Assigning the package to the client sends the package-information email."""
    print("  Step 1: Assign 'package' to the client (API)")
    assign_seeded_package(context)

    print("  Step 2: Verify package-information email")
    wait_for_email(context, PACKAGE_EMAIL)

    print("  [OK] package-assigned email verified")
