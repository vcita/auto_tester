"""Setup for the multi_booking subcategory.

Mirrors the legacy multi-booking-appointments.feature Background: log in to the
isolated account, create three free 1-on-1 services via API (service1/2/3), and
create one client via API. The legacy Background also creates a staff member, but
neither scenario references that staff (no assigned_staff in the data tables), so
it is intentionally not recreated here.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, create_service_via_api

CLIENT_FIRST_NAME = "Chuck"
CLIENT_LAST_NAME = "Norris"
SERVICE_COUNT = 3


def setup_multi_booking(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    stamp = int(time.time() * 1000)

    print("  Setup Step 2: Create three services via API")
    service_names = []
    for index in range(1, SERVICE_COUNT + 1):
        name = f"service{index}-{stamp}"
        create_service_via_api(context, name)
        service_names.append(name)
    context["mb_service_names"] = service_names
    print(f"    Services created: {service_names}")

    print("  Setup Step 3: Create client via API")
    email = f"mb{stamp}@vmeetme.com"
    client = create_client(context, CLIENT_FIRST_NAME, f"{CLIENT_LAST_NAME}{stamp}", email)
    context["mb_client"] = client
    context["mb_client_id"] = client["id"]
    context["mb_client_name"] = client["full_name"]

    print(f"  [OK] multi_booking setup complete - client '{client['full_name']}', 3 services ready")
