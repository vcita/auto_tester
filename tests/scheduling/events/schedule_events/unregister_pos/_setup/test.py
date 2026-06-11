"""Setup for scenario 2B "unregister from BO + CP, pay via POS" (isolated account).

Mirrors the legacy scheduling-events.feature Background + scenario-2B preconditions:
point_of_sale stays enabled (the default), so the remaining attendee is paid through
Point of Sale. Creates (via API) a "require to pay" $100 event service, a ``user_staff``
staff member, three clients, and schedules the event instance. Registration itself is
done in the test through the back-office UI (the in-scope behaviour being migrated).
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import create_client, create_platform_staff_via_api
from tests.payments.event_payments.event_payments_api import (
    create_event_service,
    schedule_event,
)


def setup_unregister_pos(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account (point_of_sale enabled)")
    fn_login(page, context, username=username, password=password)

    seq = int(time.time())

    print("  Setup Step 2: Create '$100 require to pay' event service (API)")
    service = create_event_service(context, f"r2p_event{seq}", 100)

    print("  Setup Step 3: Create 'user_staff' staff member (API)")
    staff = create_platform_staff_via_api(
        context, name="user_staff", email=f"staff+user1+{seq}@vmeetme.com"
    )

    print("  Setup Step 4: Create three clients (API)")
    clients = {
        "silvan goodbye": create_client(context, "silvan", "goodbye", f"silvan{seq}@vmeetme.com"),
        "judi babish-moshe": create_client(context, "judi", "babish-moshe", f"judi{seq}@vmeetme.com"),
        "nir karpin": create_client(context, "nir", "karpin", f"nir{seq}@vmeetme.com"),
    }

    print("  Setup Step 5: Schedule the event instance (API)")
    event = schedule_event(context, service)

    context.setdefault("schedule_events", {}).update(
        {"service": service, "staff": staff, "clients": clients, "event_uid": event["uid"]}
    )
    print(f"  [OK] setup complete - event '{service['name']}' ({event['uid']}), staff "
          f"'{staff['name']}', clients {list(clients)}")
