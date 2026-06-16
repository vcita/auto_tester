"""Setup for the crm_views subcategory (isolated account).

Mirrors the legacy crm-view-create-and-edit.feature Background: create one user-role
staff via API, log in as the account owner (admin), and close the three default CRM
tabs. The owner and the created staff are stored for the SSO staff-switch in the test.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.tempo.clients.crm_views.crm_views_helpers import (
    capture_owner,
    close_tab,
    create_staff_user,
    open_clients_list,
)


def setup_crm_views(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Capture owner staff (before creating extra staff)")
    owner = capture_owner(context)

    seq = int(time.time())
    print("  Setup Step 2: Create 'Staff User' (role user) via API")
    staff_user = create_staff_user(context, "Staff User", f"staff+{seq}@vmeetme.com", "user")

    print("  Setup Step 3: Log in to the isolated account as admin (owner session)")
    fn_login(page, context, username=username, password=password)

    print("  Setup Step 4: Open clients list and close the 3 default tabs")
    open_clients_list(page)
    close_tab(page, "New inquiries")
    close_tab(page, "Open payments")
    close_tab(page, "All")

    context.setdefault("crm_views", {}).update({"owner": owner, "staff_user": staff_user})
    print(
        f"  [OK] crm_views setup complete - owner '{owner['display_name']}', "
        f"staff '{staff_user['name']}', default tabs closed"
    )
