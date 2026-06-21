# Auto-generated from script.md
# Last updated: 2026-06-20
# Source: tests/tempo/clients/crm_mobile/_setup/script.md
# DO NOT EDIT MANUALLY - This file is regenerated from script.md

import time

from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.tempo.clients.crm_mobile.crm_mobile_helpers import seed_csv_clients


def setup_crm_mobile(page: Page, context: dict) -> None:
    """Setup for the crm_mobile subcategory (isolated account).

    Mirrors the legacy crm-mobile.feature Background: create the 10 clients from
    crm_mobile_clients.csv via API and log in as the owner.
    """
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    # Step 1: Log in to the isolated account as owner
    print("  Setup Step 1: Log in to the isolated account as owner")
    fn_login(page, context, username=username, password=password)

    # Step 2: Seed the 10 crm_mobile_clients.csv clients via API
    print("  Setup Step 2: Seed 10 clients from crm_mobile_clients.csv via API")
    seq = str(int(time.time()))
    clients = seed_csv_clients(context, seq)
    assert len(clients) == 10, f"Expected 10 seeded clients, got {len(clients)}"
    context["crm_mobile_seq"] = seq

    print(f"  [OK] crm_mobile setup complete - {len(clients)} clients seeded (seq={seq})")
