# Source: tests/sales/sales_widget/empty_state/script.md
# Migrated from automation-js/features/salsa/sales_widget.feature (VCITA2-13854)

from playwright.sync_api import Page

from tests.salsa.sales.sales_widget.sales_widget_helpers import (
    assert_empty_state,
    goto_new_dashboard,
    open_payment_wizard,
)


def test_empty_state(page: Page, context: dict) -> None:
    """On a fresh account the Sales widget shows its empty state, and clicking
    'Start accepting payments' opens the payment wizard."""
    print("  Step 1: Open the new dashboard")
    goto_new_dashboard(page, context)

    print("  Step 2: Sales widget shows the empty state")
    assert_empty_state(page)

    print("  Step 3: Click 'Start accepting payments' -> payment wizard is displayed")
    open_payment_wizard(page)

    print("  [OK] empty state + payment wizard verified")
