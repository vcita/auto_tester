from playwright.sync_api import Page

from tests.dashboard.quick_actions_widget.quick_actions_helpers import (
    assert_actions,
    assert_new_client_modal,
    click_action,
    open_dashboard,
)

DEFAULT_ACTIONS = ["client", "appointment", "point_of_sale", "invoice", "message", "estimate"]


def test_widget_actions(page: Page, context: dict) -> None:
    """Verify default quick actions and that the client action opens the new client modal.

    Migrates automation-js `quick_actions_widget.feature` scenario
    `Quick actions widget - actions`.
    """
    print("  Step 1: Opening dashboard and verifying default quick actions...")
    open_dashboard(page)
    assert_actions(page, DEFAULT_ACTIONS)

    print("  Step 2: Clicking the client quick action...")
    click_action(page, "client")
    assert_new_client_modal(page)
    print("  [OK] Default quick actions shown and client action opens the new client modal")
