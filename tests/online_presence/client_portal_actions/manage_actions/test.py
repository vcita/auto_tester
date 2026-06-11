# Auto-generated from script.md
# Source: tests/online_presence/client_portal_actions/manage_actions/script.md
# Migrated from automation-js/features/tempo/client-portal-actions.feature (VCITA2-14060)

from playwright.sync_api import Page

from tests.online_presence.client_portal_actions import cp_actions_helpers as cp


def test_manage_actions(page: Page, context: dict) -> None:
    """
    Add a Client Portal action and verify the livesite shows it, then edit, hide
    (verify gone), show, and delete (verify gone) it from the back-office editor.

    Prerequisites (setup):
    - Logged in to the isolated account.
    - Verification client created via API; its portal token is in context["cpa"].
    """
    portal_token = context["cpa"]["portal_token"]

    print("  Step 1: Open the Client Portal editor...")
    cp.open_editor(page, context)

    print("  Step 2: Add 'Contact us' action 'Leave details 1'...")
    cp.add_action(page, context, "Contact us", "Leave details 1")

    print("  Step 3: Client portal displays 'Leave details 1'...")
    cp.assert_cp_displays(page, context, portal_token, "Leave details 1")

    print("  Step 4: Rename action 'Leave details 1' -> 'Leave details 2'...")
    cp.edit_action(page, "Leave details 1", "Leave details 2")

    print("  Step 5: Hide action 'Leave details 2'...")
    cp.hide_action(page, "Leave details 2")

    print("  Step 6: Client portal no longer displays 'Leave details 2'...")
    cp.assert_cp_not_displays(page, context, portal_token, "Leave details 2")

    print("  Step 7: Show action 'Leave details 2' again...")
    cp.show_action(page, "Leave details 2")

    print("  Step 8: Delete action 'Leave details 2'...")
    cp.delete_action(page, "Leave details 2")

    print("  Step 9: Client portal no longer displays 'Leave details 2'...")
    cp.assert_cp_not_displays(page, context, portal_token, "Leave details 2")
