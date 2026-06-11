"""Setup for the clients_quota subcategory.

Mirrors the legacy clients-quota.feature prerequisites: log in to the isolated
(11-client-capped) account and seed 10 clients via API so the test starts at 10/11.
The operator package + capped account are provisioned by the runner
(see _category.yaml account_profile.operator_package).
"""

import time

from playwright.sync_api import Page

from tests import account_api
from tests._functions.login.test import fn_login

SEED_COUNT = 10


def setup_clients_quota(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated 11-client-capped account")
    fn_login(page, context, username=username, password=password)

    seq = int(time.time())
    clients = []
    for i in range(1, SEED_COUNT + 1):
        first = f"first{i:02d}"
        last = f"last{i:02d}"
        email = f"test{i:02d}+{seq}@vmeetme.com"
        account_api.create_client(context, first_name=first, last_name=last, email=email)
        clients.append({"first_name": first, "last_name": last, "email": email,
                        "name": f"{first} {last}"})
    print(f"  [OK] Seeded {len(clients)} clients via API (account now at {SEED_COUNT}/11)")

    context["clients_quota"] = {"seq": seq, "clients": clients}
