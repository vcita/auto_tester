"""Setup for the schedule_appointments scenarios (isolated account).

Mirrors the legacy scheduling-appointments.feature Background: create service1, a staff
member (user_staff) and the client "Chuck Norris" via API, then log in. Per-scenario data
(inline new client/staff, arrival-window service2, additional recipients) is created inside
the tests, matching the in-scope UI behavior being migrated.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.tempo.scheduling.appointments.schedule_appointments.schedule_appointments_api import (
    create_appointment_service,
    create_client_with_readback,
    create_staff,
    get_owner_staff,
    set_account_arrival_window,
)

ACCOUNT_ARRIVAL_WINDOW_MINUTES = 45


def setup_schedule_appointments(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    seq = int(time.time())

    print("  Setup Step 1: Capture owner staff (before creating extra staff)")
    owner = get_owner_staff(context)

    print("  Setup Step 2: Create user_staff (role user) via API")
    user_staff = create_staff(context, "user_staff", f"staff+user1+{seq}@vmeetme.com", "user")

    # The legacy scenario creates this staff THROUGH the scheduling dialog's "create new staff"
    # button. In the current product that action persists the appointment and navigates to the
    # appointment page (it no longer creates the staff inline in the dialog), so the staff is
    # provisioned here via API and selected through the dialog's assigned-staff dropdown instead.
    print("  Setup Step 3: Create manager_staff via API (assigned-staff for scheduled/completed)")
    manager_staff = create_staff(
        context, "optimus_prime", f"staff+mgr+{seq}@vmeetme.com", "manager"
    )

    print("  Setup Step 4: Create client 'Chuck Norris' via API")
    client = create_client_with_readback(context, "Chuck", "Norris", f"testrg+{seq}@vmeetme.com")

    print("  Setup Step 5: Create 'service1' appointment service (API)")
    service = create_appointment_service(
        context, "service1", staff_uids=[owner["uid"], user_staff["uid"], manager_staff["uid"]]
    )

    print("  Setup Step 6: Set business arrival-window value (45m) via API")
    set_account_arrival_window(context, ACCOUNT_ARRIVAL_WINDOW_MINUTES)

    print("  Setup Step 7: Log in to isolated account (owner session)")
    fn_login(page, context, username=username, password=password)

    context.setdefault("schedule_appts", {}).update(
        {
            "owner": owner,
            "user_staff": user_staff,
            "manager_staff": manager_staff,
            "client": client,
            "service": service,
            "seq": seq,
        }
    )
    print(
        f"  [OK] setup complete - owner '{owner['display_name']}', staff "
        f"'{user_staff['name']}', manager '{manager_staff['name']}', "
        f"client '{client['full_name']}', service '{service['name']}'"
    )
