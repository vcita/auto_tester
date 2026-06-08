"""Setup for the appointments-list scenarios (isolated account).

Mirrors the legacy appointments-list.feature Background: log in, then create one client
and one appointment service via API (each confirmed before the tests rely on it).
Appointment scheduling is left to the `list_states` test, interleaved with the list
assertions exactly as in the legacy scenario.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, create_service_via_api
from tests.scheduling.appointments.appointments_list.appointments_list_helpers import (
    verify_service_persisted,
)


def setup_appointments_list(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    seq = int(time.time())

    print("  Setup Step 2: Create client (API)")
    client = create_client(context, "first", "last", f"test+{seq}@vmeetme.com")

    print("  Setup Step 3: Create appointment service (API) + GET read-back")
    service = create_service_via_api(context, f"service{seq}")
    verify_service_persisted(context, service["id"], service["name"])

    context.setdefault("appointments_list", {}).update({"client": client, "service": service})
    print(f"  [OK] setup complete - client '{client['full_name']}', service '{service['name']}'")
