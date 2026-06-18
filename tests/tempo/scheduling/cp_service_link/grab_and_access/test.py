"""Grab and access scheduler links (CP service-link migration, VCITA2-14226).

Migrates the single legacy scenario `Grab and Access scheduler links` from
features/tempo/CP/service-link.feature. Sequential, state-dependent steps:

1. grab the general service link (UI) -> access -> staff-select shows [business, staff];
2. derive the staff-scoped link -> access -> calendar shows the service + that staff;
3. delete the staff (API) -> access general link -> calendar shows the service + business;
4. delete the service (API) -> access general link -> scheduler shows the default services.

The staff-scoped link is derived from the UI-grabbed general link's portal base (see
service_link_helpers for why the legacy Link Builder UI is not reproduced).
"""
from playwright.sync_api import Page

from tests.tempo.scheduling.cp_service_link.service_link_helpers import (
    access_link,
    assert_calendar,
    assert_services_page,
    assert_staff_select,
    delete_service_api,
    delete_staff_api,
    derive_staff_scoped_link,
    grab_general_service_link,
)

# Default seed services that remain after the custom service is deleted.
DEFAULT_SERVICES = [
    {"name": "In-office appointment", "duration": "1 hour"},
    {"name": "Introductory phone call", "duration": "30 min"},
]


def test_grab_and_access(page: Page, context: dict) -> None:
    service = context["sl_service_name"]
    staff = context["sl_staff_display"]
    staff_uid = context["sl_staff_uid"]
    business = context["sl_owner_display"]

    print("  Step 1: Grab the general service link (UI)...")
    general_link = grab_general_service_link(page, service, context["sl_app_base"])
    print(f"    general link: {general_link}")

    print("  Step 2: Access it -> staff-select page shows business + staff...")
    access_link(page, general_link)
    assert_staff_select(page, [business, staff])

    print("  Step 3: Derive the staff-scoped link, access it -> calendar shows service + staff...")
    staff_link = derive_staff_scoped_link(general_link, staff_uid)
    print(f"    staff-scoped link: {staff_link}")
    access_link(page, staff_link)
    assert_calendar(page, service_name=service, providing_staff=staff)

    print("  Step 4: Delete the staff (API) -> general link now shows business on calendar...")
    delete_staff_api(context, staff_uid)
    access_link(page, general_link)
    assert_calendar(page, service_name=service, providing_staff=business)

    print("  Step 5: Delete the service (API) -> general link shows the default services page...")
    delete_service_api(context, context["sl_service_uid"])
    access_link(page, general_link)
    assert_services_page(page, DEFAULT_SERVICES)

    print("  [OK] Scheduler links grabbed and access verified across all states")
