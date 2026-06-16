import time

from playwright.sync_api import Page

from tests.tempo.clients.custom_status.status_helpers import (
    apply_status_filter,
    assert_filtered_clients,
    clear_filters,
    create_client_via_api,
    create_custom_status,
    open_client_from_list,
    set_client_status,
)


def test_create_filter_status(page: Page, context: dict) -> None:
    """
    Create a custom client status, assign it to clients, and verify CRM filtering.

    Migrates automation-js `client-custom-status.feature` scenario `create`.
    """
    timestamp = int(time.time())
    status_name = f"Auto Status {timestamp}"
    first_client_data = {
        "first_name": "StatusOne",
        "last_name": str(timestamp),
        "email": f"status.one.{timestamp}@vcita-test.com",
    }
    second_client_data = {
        "first_name": "StatusTwo",
        "last_name": str(timestamp),
        "email": f"status.two.{timestamp}@vcita-test.com",
        "status": status_name,
    }

    print(f"  Step 1: Creating custom status '{status_name}'...")
    create_custom_status(page, status_name)

    print("  Step 2: Creating first client without the custom status...")
    first_client = create_client_via_api(context, first_client_data)

    print("  Step 3: Verifying status filter starts empty...")
    apply_status_filter(page, status_name)
    assert_filtered_clients(page, [])

    print("  Step 4: Assigning custom status to first client...")
    open_client_from_list(page, first_client["name"], first_client["id"])
    set_client_status(page, status_name)

    print("  Step 5: Verifying filter shows only first client...")
    apply_status_filter(page, status_name)
    assert_filtered_clients(page, [first_client["name"]])

    print("  Step 6: Creating second client with the custom status...")
    second_client = create_client_via_api(context, second_client_data)
    open_client_from_list(page, second_client["name"], second_client["id"])
    set_client_status(page, status_name)
    clear_filters(page)
    apply_status_filter(page, status_name)
    assert_filtered_clients(page, [first_client["name"], second_client["name"]])

    context["custom_status_filter_name"] = status_name
    context["custom_status_first_client_id"] = first_client["id"]
    context["custom_status_first_client_name"] = first_client["name"]
    context["custom_status_first_client_email"] = first_client["email"]
    context["custom_status_second_client_id"] = second_client["id"]
    context["custom_status_second_client_name"] = second_client["name"]
    context["custom_status_second_client_email"] = second_client["email"]

    print("  [OK] Custom status creation, assignment, and filtering verified")
