"""Setup for the events-list scenario (isolated account).

Mirrors the legacy events-list.feature Background: log in, then create two event
services via API (require-to-pay + display-a-fee). Scheduling events from the list is
left to the test, since that is the in-scope UI behavior being migrated.
"""

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.tempo.scheduling.events.events_list.events_list_api import create_event_service


def setup_events_list(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup Step 1: Log in to isolated account")
    fn_login(page, context, username=username, password=password)

    seq = int(time.time())
    print("  Setup Step 2: Create 'require to pay' event service (API)")
    r2p = create_event_service(context, f"r2p_event{seq}", "require to pay", 1)

    print("  Setup Step 3: Create 'display a fee' event service (API)")
    daf = create_event_service(context, f"daf_event{seq}", "display a fee", 1)

    context.setdefault("events_list", {}).update({"r2p": r2p, "daf": daf})
    print(f"  [OK] setup complete - services '{r2p['name']}', '{daf['name']}'")
