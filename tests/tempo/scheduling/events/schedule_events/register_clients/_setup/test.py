"""Setup for scenario 1 "register clients to event" (isolated account).

Mirrors the legacy scheduling-events.feature Background for scenario 1: log in, then
create (via API) a "require to pay" $100 event service, a ``user_staff`` staff member,
and two clients. The event itself is scheduled through the back office in the test,
since the back-office scheduling UI is the in-scope behaviour being migrated.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, create_platform_staff_via_api
from tests.salsa.payments.event_payments.event_payments_api import create_event_service


def setup_register_clients(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    seq = int(time.time())

    # Service first (owner staff assigned), then user_staff, mirroring the legacy
    # Background order so the owner stays staffs[0] and user_staff is assigned in the UI.
    print("  Setup Step 2: Create '$100 require to pay' event service (API)")
    service = create_event_service(context, f"r2p_event{seq}", 100)

    print("  Setup Step 3: Create 'user_staff' staff member (API)")
    staff = create_platform_staff_via_api(
        context, name="user_staff", email=f"staff+user1+{seq}@vmeetme.com"
    )

    print("  Setup Step 4: Create two clients (API)")
    clients = {
        "silvan goodbye": create_client(context, "silvan", "goodbye", f"silvan{seq}@vmeetme.com"),
        "judi babish-moshe": create_client(context, "judi", "babish-moshe", f"judi{seq}@vmeetme.com"),
    }

    context.setdefault("schedule_events", {}).update(
        {"service": service, "staff": staff, "clients": clients}
    )
    print(f"  [OK] setup complete - event service '{service['name']}', staff '{staff['name']}', "
          f"clients {list(clients)}")
