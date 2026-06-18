"""Setup for the CP multi-booking scenarios (isolated account).

Mirrors the legacy Background: enable the multi_appointment_client_booking feature flag,
create the shared client and base services (service1 20m, service2 40m), create Staff1/Staff2,
enable client-portal multi booking, and log in to the business. The anonymous client-portal
scheduling and assertions happen in the test bodies.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import (
    create_client,
    create_platform_staff_via_api,
    account_request,
    create_service_via_api,
    enable_features,
    first_staff_uid,
    pivot_uid,
)
from tests.tempo.scheduling.cp_multi_booking.cp_multi_booking_helpers import enable_multi_booking


def setup_cp_multi_booking(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    seq = int(time.time())

    print("  Setup Step 1: Enable feature flag multi_appointment_client_booking")
    enable_features(context, "multi_appointment_client_booking")

    # Cache the account-owner staff uid before adding more staff so service creation /
    # event scheduling stay deterministic regardless of staff-list ordering. Capture the
    # owner display name too: the CP scheduler summary shows the default providing staff as
    # "With <owner display name>" (the legacy account was literally "Automation test
    # business"; the auto_tester account name varies per run, so resolve it dynamically).
    first_staff_uid(context)
    staff_list = account_request(
        context, "GET", f"/platform/v1/businesses/{pivot_uid(context)}/staffs?status=all"
    )
    owner = (staff_list.get("data", {}).get("staff") or [{}])[0]
    owner_display_name = owner.get("display_name") or owner.get("name") or ""

    print("  Setup Step 2: Create client Chuck Norris via API")
    client = create_client(context, "Chuck", "Norris", f"test23+{seq}@vmeetme.com")

    print("  Setup Step 3: Create service1 (20m) via API")
    service1 = create_service_via_api(context, "service1", duration=20)
    print("  Setup Step 4: Create service2 (40m) via API")
    service2 = create_service_via_api(context, "service2", duration=40)

    print("  Setup Step 5: Create Staff1 via Platform API")
    create_platform_staff_via_api(context, "Staff1", f"staff1+{seq}@vmeetme.com", role="user")
    print("  Setup Step 6: Create Staff2 via Platform API")
    staff2 = create_platform_staff_via_api(context, "Staff2", f"staff2+{seq}@vmeetme.com", role="user")

    print("  Setup Step 7: Enable client-portal multi booking via API")
    enable_multi_booking(context)

    print("  Setup Step 8: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    mb = context.setdefault("mb", {})
    mb["client"] = client
    mb["service1"] = service1
    mb["service2"] = service2
    mb["staff2"] = staff2
    mb["owner_display_name"] = owner_display_name
    mb["seq"] = seq
    print("  [OK] setup complete - FF + client + service1/service2 + Staff1/Staff2 + CP multi booking")
