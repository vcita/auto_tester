import time

from playwright.sync_api import Page

from tests.clients.crm_filters.crm_filters_helpers import (
    add_column,
    add_custom_field_filter,
    add_dropdown_field_filter,
    assert_column_present,
    assert_displayed_filters,
    assert_filtered_clients,
    clear_all_filters,
    create_client,
    create_client_field_via_ui,
    create_field,
    open_clients_list,
    select_tab,
)

CLIENT_FIELD = "client_field"
DROPDOWN_FIELD = "dropdown_field"
TEXT_VALUE = "text_value"
DROPDOWN_OPTIONS = ["option_a", "option_b", "option_c"]


def _ensure_base_clients(context: dict) -> list[str]:
    base = context.get("crm_base_clients")
    if base:
        return base
    ts = int(time.time())
    base = []
    for fn, ln, tag in [("first1", "last1", None), ("first2", "last2", "tag4"),
                        ("first3", "last3", "tag4"), ("no-tag", "last4", None)]:
        payload = {"first_name": fn, "last_name": ln, "email": f"crmb{fn}.{ts}@vcita-test.com"}
        if tag:
            payload["tags"] = tag
        base.append(create_client(context, payload)["name"])
    context["crm_base_clients"] = base
    return base


def test_custom_field_filtering(page: Page, context: dict) -> None:
    """Show custom fields as CRM columns and filter by them.

    Migrates automation-js `crm-filters-create-and-edit.feature` scenario
    `Display and filter by custom field`.
    """
    base_clients = _ensure_base_clients(context)
    ts = int(time.time())

    print("  Step 1a: Creating matter singleline field 'client_field' via API...")
    create_field(context, "matter", CLIENT_FIELD, "singleline")

    print("  Step 1b: Creating client dropdown field 'dropdown_field' via UI...")
    # The /fields API rejects object_type=client, so the client dropdown is
    # created through the Client Card Settings UI, exactly like legacy.
    create_client_field_via_ui(page, DROPDOWN_FIELD, "Drop down list", options=DROPDOWN_OPTIONS)

    print("  Step 2: Creating 2 clients with custom-field values...")
    c5 = create_client(context, {"first_name": "first5", "last_name": "last5",
                                 "email": f"crm5.{ts}@vcita-test.com",
                                 CLIENT_FIELD: TEXT_VALUE, DROPDOWN_FIELD: "option_a"})
    c6 = create_client(context, {"first_name": "first6", "last_name": "last6",
                                 "email": f"crm6.{ts}@vcita-test.com",
                                 CLIENT_FIELD: TEXT_VALUE, DROPDOWN_FIELD: "option_b"})

    print("  Step 3: Opening clients list (All tab)...")
    open_clients_list(page)
    select_tab(page, "All")
    clear_all_filters(page)

    print("  Step 4: Adding 'client_field' column...")
    add_column(page, CLIENT_FIELD)
    assert_column_present(page, CLIENT_FIELD)

    print("  Step 5: Adding 'dropdown_field' column...")
    add_column(page, DROPDOWN_FIELD)
    assert_column_present(page, DROPDOWN_FIELD)

    print("  Step 6: Filtering by client_field='text_value'...")
    add_custom_field_filter(page, CLIENT_FIELD, TEXT_VALUE)
    assert_displayed_filters(page, [CLIENT_FIELD])
    assert_filtered_clients(page, [c5["name"], c6["name"]])

    print("  Step 7: Filtering by dropdown_field='option_b'...")
    add_dropdown_field_filter(page, DROPDOWN_FIELD, "option_b")
    assert_displayed_filters(page, [DROPDOWN_FIELD, CLIENT_FIELD])
    assert_filtered_clients(page, [c6["name"]])

    print("  Step 8: Clearing all filters...")
    clear_all_filters(page)
    assert_displayed_filters(page, [])
    assert_filtered_clients(page, [*base_clients, c5["name"], c6["name"]])

    print("  [OK] Custom-field column display + filtering verified")
