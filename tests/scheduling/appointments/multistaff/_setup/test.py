"""Setup for the multistaff scenarios (isolated account).

Mirrors the legacy multistaff.feature Background: enable multistaff, create two staff, a
client and a require-to-pay service via API, then log in. Scheduling and the staff switch
are left to the tests (the in-scope UI / SSO behavior being migrated).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import enable_features
from tests.scheduling.appointments.multistaff.multistaff_api import (
    create_appointment_service,
    create_client_with_readback,
    create_staff,
    get_owner_staff,
)


def setup_multistaff(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Enable multistaff on the fresh account")
    enable_features(context, "multistaff_features")

    print("  Setup Step 2: Capture owner staff (before creating extra staff)")
    owner = get_owner_staff(context)

    seq = int(time.time())
    user_name, manager_name = f"user_staff{seq}", f"manager_staff{seq}"
    print("  Setup Step 3: Create user_staff (role user) + manager_staff (role manager) via API")
    user_staff = create_staff(context, user_name, f"test11+{seq}@vmeetme.com", "user")
    manager_staff = create_staff(context, manager_name, f"test2+{seq}@vmeetme.com", "manager")

    print("  Setup Step 4: Create client 'rina success' via API")
    client = create_client_with_readback(context, "rina", "success", f"testrte+{seq}@vmeetme.com")

    print("  Setup Step 5: Create 'require to pay' appointment service (API)")
    service = create_appointment_service(
        context,
        f"r2p_appointment{seq}",
        staff_uids=[owner["uid"], user_staff["uid"], manager_staff["uid"]],
    )

    print("  Setup Step 6: Log in to isolated account (owner session)")
    fn_login(page, context, username=username, password=password)

    context.setdefault("multistaff", {}).update(
        {
            "owner": owner,
            "user_staff": user_staff,
            "manager_staff": manager_staff,
            "client": client,
            "service": service,
        }
    )
    print(
        f"  [OK] setup complete - owner '{owner['display_name']}', staff "
        f"'{user_staff['name']}'/'{manager_staff['name']}', client '{client['full_name']}', "
        f"service '{service['name']}'"
    )
