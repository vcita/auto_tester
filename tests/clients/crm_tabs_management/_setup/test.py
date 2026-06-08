"""Setup for the crm_tabs_management subcategory (isolated account).

Mirrors the legacy crm-tabs-management.feature Background: a self-client (owner email ->
"(You as a client)") is created via API, and the owner logs in. The livesite leave-details
submission is out-of-scope setup data; it is reproduced via API client creation plus an
API appointment booking, which is what makes the client "recently active" (the legacy
form submission registered the same recent activity).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_appointment_via_api, create_service_via_api
from tests.clients.crm_tabs_management.crm_tabs_helpers import create_self_client


def setup_crm_tabs_management(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to the isolated account as owner")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 2: Create self-client 'form_first form_last' via API (owner email)")
    client = create_self_client(context, "form_first", "form_last", username)

    print("  Setup Step 3: Book an appointment via API so the client is recently active")
    service = create_service_via_api(context, f"CRM Tabs Service {int(time.time())}")
    create_appointment_via_api(context, service, client)

    context["self_client_label"] = client["label"]
    print(f"  [OK] crm_tabs_management setup complete - self-client '{client['label']}'")
