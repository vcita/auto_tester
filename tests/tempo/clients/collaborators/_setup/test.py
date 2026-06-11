"""Setup for the collaborators subcategory.

Mirrors the legacy add-remove-staff-in-matter.feature Background: log in to the
isolated account, create two staff (Staff B, Staff C) and one service via Platform
API, create the client "new client", and seed a future appointment for the client
assigned to Staff C.

The appointment is the precondition that triggers the removal warning later; the
legacy feature scheduled it via the back-office UI, but scheduling is not the
behavior under test (collaborator add/remove + warning), so it is created via API.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import (
    create_client,
    create_platform_staff_via_api,
    create_service_via_api,
    first_staff_uid,
)

STAFF_B_NAME = "Staff B"
STAFF_C_NAME = "Staff C"
CLIENT_FIRST_NAME = "new"
CLIENT_LAST_NAME = "client"
SERVICE_NAME = "service"


def setup_collaborators(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    stamp = int(time.time() * 1000)

    print("  Setup Step 2: Resolve account owner, then create Staff B and Staff C via Platform API")
    owner_uid = first_staff_uid(context)
    staff_b = create_platform_staff_via_api(context, STAFF_B_NAME, f"bb+{stamp}@vmeetme.com", role="user")
    staff_c = create_platform_staff_via_api(context, STAFF_C_NAME, f"cc+{stamp}@vmeetme.com", role="user")
    context["collab_staff_b"] = staff_b
    context["collab_staff_c"] = staff_c

    print("  Setup Step 3: Create service via API (offered by owner + Staff C)")
    service = create_service_via_api(context, SERVICE_NAME, staff_uids=[owner_uid, staff_c["uid"]])
    context["collab_service"] = service

    print("  Setup Step 4: Create client 'new client' via API")
    client = create_client(context, CLIENT_FIRST_NAME, CLIENT_LAST_NAME, f"aa+{stamp}@bb.cc")
    context["collab_client"] = client
    context["collab_client_id"] = client["id"]
    context["collab_client_name"] = client["full_name"]

    print(
        f"  [OK] collaborators setup complete - client '{client['full_name']}', "
        f"service '{service['name']}', staff B/C ready"
    )
