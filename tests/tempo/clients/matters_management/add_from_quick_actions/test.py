# Add Matter From Quick Actions
# Migrated from automation-js matters-management.feature (VCITA2-13952)
# Legacy: quickactions.js addClient -> newClientDialog.js createMatterUnderSuggestedContact
# Source: tests/clients/matters_management/add_from_quick_actions/script.md

from playwright.sync_api import Page

from tests.tempo.clients.matters_management.matters_helpers import (
    add_matter_from_quick_actions,
    assert_matter_under_contact,
)

MATTER_NAME = "matter_2"


def test_add_from_quick_actions(page: Page, context: dict) -> None:
    """Add matter_2 under the existing contact via the Quick Actions suggested-contact flow."""
    contact_id = context["contact_client_id"]
    contact_email = context["contact_client_email"]

    print(f"  Step 1: Adding matter {MATTER_NAME!r} via Quick Actions for {contact_email!r}...")
    add_matter_from_quick_actions(page, context, contact_email, MATTER_NAME)

    print(f"  Step 2: Verifying {MATTER_NAME!r} exists under the contact...")
    assert_matter_under_contact(page, context, contact_id, MATTER_NAME, contact_email)
