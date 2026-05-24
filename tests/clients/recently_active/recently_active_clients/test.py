import time

from playwright.sync_api import Page

from tests.clients.recently_active.recently_active_helpers import (
    assert_no_recently_active_clients,
    assert_recently_active_clients,
    create_appointment_via_api,
    create_client_via_api,
    create_service_via_api,
    prepare_recently_active_clients_view,
)


def test_recently_active_clients(page: Page, context: dict) -> None:
    """
    Verify dashboard recently active clients empty, one-client, and ordering states.

    Migrates automation-js `clients-recently-active.feature`.
    """
    timestamp = int(time.time())
    service_name = f"Recently Active Service {timestamp}"
    first_client_data = {
        "first_name": "first",
        "last_name": "last",
        "email": f"recent.first.{timestamp}@vcita-test.com",
    }
    second_client_data = {
        "first_name": "first2",
        "last_name": "last2",
        "email": f"recent.second.{timestamp}@vcita-test.com",
    }

    print("  Step 1: Creating service via API...")
    service = create_service_via_api(context, service_name)
    context["recently_active_service_id"] = service["id"]
    context["recently_active_service_name"] = service["name"]

    print("  Step 2: Creating first client via API...")
    first_client = create_client_via_api(context, first_client_data)
    context["recently_active_first_client_id"] = first_client["id"]
    context["recently_active_first_client_name"] = first_client["name"]
    context["recently_active_first_client_email"] = first_client["email"]

    print("  Step 3: Verifying dashboard starts with no recently active clients...")
    prepare_recently_active_clients_view(page, context)
    assert_no_recently_active_clients(page)

    print("  Step 4: Creating first appointment via API...")
    first_booking = create_appointment_via_api(context, service, first_client)
    context["recently_active_first_booking"] = first_booking

    print("  Step 5: Verifying first client appears as recently active...")
    assert_recently_active_clients(page, [first_client["name"]])

    print("  Step 6: Creating second client via API...")
    second_client = create_client_via_api(context, second_client_data)
    context["recently_active_second_client_id"] = second_client["id"]
    context["recently_active_second_client_name"] = second_client["name"]
    context["recently_active_second_client_email"] = second_client["email"]

    print("  Step 7: Creating second appointment via API...")
    second_booking = create_appointment_via_api(context, service, second_client)
    context["recently_active_second_booking"] = second_booking

    print("  Step 8: Verifying newest recently active client appears first...")
    assert_recently_active_clients(page, [second_client["name"], first_client["name"]])

    print("  [OK] Recently active clients widget verified")
