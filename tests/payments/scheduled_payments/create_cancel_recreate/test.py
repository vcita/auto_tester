"""Create, cancel and recreate a scheduled-payments plan.

Migrates automation-js features/salsa/scheduled_payments.feature
(scenario: user with saved credit card create scheduled payment).
"""

from playwright.sync_api import Page

from tests.payments.scheduled_payments.scheduled_payments_ui import (
    cancel_side_pane_plan,
    close_side_pane,
    close_success_dialog,
    create_scheduled_payment,
    open_side_pane_via_client_card,
    read_side_pane_plan,
)

DEFAULT_PLAN_NAME = "Scheduled Payments Plan Name"
SECOND_PLAN_NAME = "sppn"


def _assert_plan(actual: dict, *, plan_name: str, state: str, client_name: str) -> None:
    expected = {"client_name": client_name, "plan_name": plan_name, "state": state}
    assert actual == expected, f"Side pane plan mismatch: expected {expected}, got {actual}"


def test_create_cancel_recreate(page: Page, context: dict) -> None:
    client_id = context["sp_client_id"]
    client_name = context["sp_client_name"]

    print("  Phase A: Create scheduled payments plan (no success toast)")
    create_scheduled_payment(
        page, context, client_name, plan_name=DEFAULT_PLAN_NAME, wait_success_toast=False
    )
    print("  Phase A: Close the creation success dialog")
    close_success_dialog(page)

    print("  Phase A: Verify the side pane shows the plan Active")
    open_side_pane_via_client_card(page, context, client_id)
    _assert_plan(
        read_side_pane_plan(page),
        plan_name=DEFAULT_PLAN_NAME,
        state="Active",
        client_name=client_name,
    )
    close_side_pane(page)

    print("  Phase B: Cancel the plan from the side pane")
    open_side_pane_via_client_card(page, context, client_id)
    cancel_side_pane_plan(page)

    print("  Phase B: Verify the side pane shows the plan Canceled")
    open_side_pane_via_client_card(page, context, client_id)
    _assert_plan(
        read_side_pane_plan(page),
        plan_name=DEFAULT_PLAN_NAME,
        state="Canceled",
        client_name=client_name,
    )
    close_side_pane(page)

    print("  Phase C: Create a second plan with a next-month start date")
    create_scheduled_payment(
        page,
        context,
        client_name,
        plan_name=SECOND_PLAN_NAME,
        amount="10",
        start_date="next_month",
        wait_success_toast=True,
    )

    print("  Phase C: Verify the side pane shows the second plan Active")
    open_side_pane_via_client_card(page, context, client_id)
    _assert_plan(
        read_side_pane_plan(page),
        plan_name=SECOND_PLAN_NAME,
        state="Active",
        client_name=client_name,
    )
    close_side_pane(page)
    print("  Scheduled payments create/cancel/recreate verified")
