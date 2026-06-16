# Source: tests/scheduling/services_categories/manage_categories_services/script.md
# Migrated from automation-js/features/tempo/ServiceSetups/categories-and-services.feature (VCITA2-13993)

from playwright.sync_api import Page

from tests.tempo.scheduling.services_categories.services_categories_actions import (
    clone_service,
    create_appointment_service,
    create_category,
    create_event_service,
    delete_category,
    delete_service,
    edit_service_category,
    edit_service_name,
    move_category_up,
    rename_category,
)
from tests.tempo.scheduling.services_categories.services_categories_helpers import (
    assert_categories,
    assert_service_details,
)

MY_SERVICES = "My Services"
CATEGORY_ONE = "category_one"
NEW_NAME = "New_name"
DEMO = "Demo class / event"
IN_OFFICE = "In-office appointment"
INTRO = "Introductory phone call"
R2P_EVENT = "r2p_event"
GONG = "Gong"
SERVICE_ONE = "service_one"
COPY_SERVICE_ONE = "Copy of service_one"


def test_manage_categories_services(page: Page, context: dict) -> None:
    """Full categories-and-services management flow on the Services index page:
    create/rename/move/delete categories, create/edit/clone/delete services, and verify
    the category->service mapping (and service payment details) at each stage."""

    print("  Step 1: Create category and verify defaults + empty new category")
    create_category(page, CATEGORY_ONE)
    assert_categories(page, [
        {"name": MY_SERVICES, "services": [DEMO, IN_OFFICE, INTRO]},
        {"name": CATEGORY_ONE, "services": []},
    ])

    print("  Step 2: Create a require-to-pay event service and a service in the category")
    create_event_service(page, R2P_EVENT, price="100", max_attendees=10)
    create_appointment_service(page, GONG, category=CATEGORY_ONE)
    assert_service_details(page, R2P_EVENT, contains=["$100", "10 attendees"])
    assert_service_details(page, GONG, contains=["1 on 1"], excludes=["$"])

    print("  Step 3: Move In-office appointment into the category")
    edit_service_category(page, IN_OFFICE, category=CATEGORY_ONE)
    assert_categories(page, [
        {"name": MY_SERVICES, "services": [R2P_EVENT, DEMO, INTRO]},
        {"name": CATEGORY_ONE, "services": [GONG, IN_OFFICE]},
    ])

    print("  Step 4: Rename the category and delete a default service")
    rename_category(page, CATEGORY_ONE, NEW_NAME)
    delete_service(page, INTRO)
    assert_categories(page, [
        {"name": MY_SERVICES, "services": [R2P_EVENT, DEMO]},
        {"name": NEW_NAME, "services": [GONG, IN_OFFICE]},
    ])

    print("  Step 5: Move the category up and rename a service")
    move_category_up(page, NEW_NAME)
    edit_service_name(page, IN_OFFICE, SERVICE_ONE)
    assert_categories(page, [
        {"name": NEW_NAME, "services": [GONG, SERVICE_ONE]},
        {"name": MY_SERVICES, "services": [R2P_EVENT, DEMO]},
    ])

    print("  Step 6: Clone the renamed service")
    clone_service(page, SERVICE_ONE)
    assert_categories(page, [
        {"name": NEW_NAME, "services": [GONG, SERVICE_ONE, COPY_SERVICE_ONE]},
        {"name": MY_SERVICES, "services": [R2P_EVENT, DEMO]},
    ])

    print("  Step 7: Delete a category and verify its services merge into the remaining one")
    delete_category(page, MY_SERVICES)
    assert_categories(page, [
        {"name": NEW_NAME, "services": [GONG, SERVICE_ONE, COPY_SERVICE_ONE, R2P_EVENT, DEMO]},
    ])

    print("  [OK] categories and services management verified end-to-end")
