from playwright.sync_api import Page

from tests.dashboard.quick_actions_widget.quick_actions_helpers import (
    add_actions,
    assert_actions,
    assert_actions_in_order,
    open_dashboard,
    remove_actions,
    reorder_actions,
    save_all_actions_expecting_error,
)


def test_edit_actions(page: Page, context: dict) -> None:
    """Edit the quick-actions set, reorder, and verify min/max validation errors.

    Migrates automation-js `quick_actions_widget.feature` scenario
    `Quick actions widget - edit actions and error messages`.
    """
    open_dashboard(page)

    print("  Step 1: Removing invoice + point_of_sale, adding event...")
    remove_actions(page, ["invoice", "point_of_sale"])
    add_actions(page, ["event"])
    assert_actions(page, ["client", "appointment", "message", "estimate", "event"])

    print("  Step 2: Reordering message before client...")
    reorder_actions(page, "message", "client")
    assert_actions_in_order(page, "message,client")

    print("  Step 3: Unchecking all actions -> expect validation error...")
    save_all_actions_expecting_error(page, checked=False)

    print("  Step 4: Checking all actions -> expect validation error...")
    save_all_actions_expecting_error(page, checked=True)
    print("  [OK] Edit, reorder, and min/max validation errors verified")
