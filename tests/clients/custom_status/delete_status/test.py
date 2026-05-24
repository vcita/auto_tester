import time

from playwright.sync_api import Page

from tests.clients.custom_status.status_helpers import (
    assert_client_status,
    assert_status_filter_options,
    attempt_delete_status_in_use,
    create_client_via_api,
    create_custom_status,
    delete_unused_status,
    open_client_from_list,
    set_client_status,
)


def test_delete_status(page: Page, context: dict) -> None:
    """
    Verify in-use custom statuses are protected and unused statuses can be deleted.

    Migrates automation-js `client-custom-status.feature` scenario `delete`.
    """
    timestamp = int(time.time())
    status_name = f"Delete Status {timestamp}"
    client_data = {
        "first_name": "StatusDelete",
        "last_name": str(timestamp),
        "email": f"status.delete.{timestamp}@vcita-test.com",
        "status": status_name,
    }

    print(f"  Step 1: Creating custom status '{status_name}'...")
    create_custom_status(page, status_name)

    print("  Step 2: Creating client with the custom status...")
    client = create_client_via_api(context, client_data)

    print("  Step 3: Verifying in-use status deletion is blocked...")
    attempt_delete_status_in_use(page, status_name)
    assert_status_filter_options(page, status_name, should_exist=True)

    print("  Step 4: Reassigning client to Lead...")
    open_client_from_list(page, client["name"], client["id"])
    set_client_status(page, "Lead")
    assert_client_status(page, "Lead")

    print("  Step 5: Deleting now-unused custom status...")
    delete_unused_status(page, status_name)
    assert_status_filter_options(page, status_name, should_exist=False)

    context["custom_status_delete_name"] = status_name
    context["custom_status_delete_client_id"] = client["id"]
    context["custom_status_delete_client_name"] = client["name"]
    context["custom_status_delete_client_email"] = client["email"]

    print("  [OK] Custom status deletion protections verified")
