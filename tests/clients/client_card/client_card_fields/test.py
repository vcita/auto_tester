# Source: tests/clients/client_card/client_card_fields/script.md
# Migrated from automation-js/features/steps/client-card.feature (VCITA2-13855)

import time

from playwright.sync_api import Page

from tests.clients.client_card.client_card_helpers import (
    add_card_field,
    add_field_filter,
    assert_filtered_clients,
    create_client,
    edit_card_field,
    open_clients_list,
)

FIELD_TYPE = "Single line text"


def test_client_card_fields(page: Page, context: dict) -> None:
    """Add a client custom field and a contact custom field via Client Card
    Settings, seed a client carrying each field's value via API, filter the CRM
    list by the field value (asserting the matching client), and rename each
    field. (The post-rename re-search is omitted upstream due to SUPPORT-6006, so
    only the rename action is verified, matching the legacy scenario.)"""
    ts = int(time.time() * 1000)

    print("  Step 1: Add 'client' field 'client_field' (Single line text)")
    add_card_field(page, "client", "client_field", FIELD_TYPE)

    print("  Step 2: Create client 'first last' with client_field='blublublu' via API")
    client_a = create_client(context, {
        "first_name": "first", "last_name": "last",
        "email": f"test+{ts}@vmeetme.com", "client_field": "blublublu",
    })

    print("  Step 3: Filter CRM by client_field='blublublu' -> shows 'first last'")
    open_clients_list(page)
    add_field_filter(page, "client_field", "blublublu")
    assert_filtered_clients(page, [client_a["name"]])

    print("  Step 4: Rename client field client_field -> client_field_1")
    edit_card_field(page, "client_field", "client_field_1")

    print("  Step 5: Add 'contact' field 'contact_field' (Single line text)")
    add_card_field(page, "contact", "contact_field", FIELD_TYPE)

    print("  Step 6: Create client 'first1 last1' with contact_field='test field' via API")
    client_b = create_client(context, {
        "first_name": "first1", "last_name": "last1",
        "email": f"test11+{ts}@vmeetme.com", "contact_field": "test field",
    })

    print("  Step 7: Filter CRM by contact_field='test field' -> shows 'first1 last1'")
    open_clients_list(page)
    add_field_filter(page, "contact_field", "test field")
    assert_filtered_clients(page, [client_b["name"]])

    print("  Step 8: Rename contact field contact_field -> contact_field_1")
    edit_card_field(page, "contact_field", "contact_field_1")

    print("  [OK] client/contact custom fields: add, filter, and rename verified")
