import time

from playwright.sync_api import Page

from tests.clients.crm_filters.crm_filters_helpers import (
    add_first_name_filter,
    add_open_payments_filter,
    add_tags_filter,
    assert_counter,
    assert_displayed_filters,
    assert_filtered_clients,
    assign_product,
    clear_all_filters,
    create_client,
    create_product,
    edit_first_name_filter,
    open_clients_list,
    remove_filter,
    save_custom_view,
    save_fixed_as_new_view,
    select_tab,
    select_view,
)

TAG = "tag4"


def test_create_edit_filters(page: Page, context: dict) -> None:
    """Create/edit/remove CRM filters and save views.

    Migrates automation-js `crm-filters-create-and-edit.feature` scenario
    `User creates, edits and removes filters`.
    """
    ts = int(time.time())
    print("  Step 1: Creating 4 base clients (+tags) via API...")
    c1 = create_client(context, {"first_name": "first1", "last_name": "last1",
                                 "email": f"crm1.{ts}@vcita-test.com"})
    c2 = create_client(context, {"first_name": "first2", "last_name": "last2",
                                 "email": f"crm2.{ts}@vcita-test.com", "tags": TAG})
    c3 = create_client(context, {"first_name": "first3", "last_name": "last3",
                                 "email": f"crm3.{ts}@vcita-test.com", "tags": TAG})
    c4 = create_client(context, {"first_name": "no-tag", "last_name": "last4",
                                 "email": f"crm4.{ts}@vcita-test.com"})

    print("  Step 2: Creating product and assigning it to first3 (open payment)...")
    product = create_product(context, f"payable_item1_{ts}", 10)
    assign_product(context, c3["id"], product.get("id") or product.get("uid"), 10)

    print("  Step 3: Opening clients list...")
    open_clients_list(page)

    print("  Step 4: Selecting 'Recently active' view...")
    select_view(page, "Recently active")
    assert_displayed_filters(page, ["Last activity time"])
    assert_counter(page, "1 CLIENTS")

    print("  Step 5: Selecting 'All' tab...")
    select_tab(page, "All")
    assert_displayed_filters(page, [])
    assert_counter(page, "4 CLIENTS")

    print("  Step 6: Adding First Name='first' filter...")
    add_first_name_filter(page, "first")
    assert_displayed_filters(page, ["First Name"])
    assert_filtered_clients(page, [c1["name"], c2["name"], c3["name"]])

    print("  Step 7: Adding Tags='tag4' filter...")
    add_tags_filter(page, TAG)
    assert_displayed_filters(page, ["Tags", "First Name"])
    assert_filtered_clients(page, [c2["name"], c3["name"]])

    print("  Step 8: Editing First Name filter to 'first2'...")
    edit_first_name_filter(page, "first2")
    assert_displayed_filters(page, ["Tags", "First Name"])
    assert_filtered_clients(page, [c2["name"]])

    print("  Step 9: Removing First Name filter...")
    remove_filter(page, "First Name")
    assert_displayed_filters(page, ["Tags"])
    assert_filtered_clients(page, [c2["name"], c3["name"]])

    print("  Step 10: Adding Open payments filter + saving fixed-as-new view...")
    add_open_payments_filter(page)
    save_fixed_as_new_view(page, f"View with filters {ts}")
    assert_displayed_filters(page, ["Open payments", "Tags"])
    assert_filtered_clients(page, [c3["name"]])
    assert_counter(page, "1 CLIENTS")

    print("  Step 11: Clearing all filters + saving custom view...")
    clear_all_filters(page)
    save_custom_view(page)
    assert_displayed_filters(page, [])
    assert_filtered_clients(page, [c1["name"], c2["name"], c3["name"], c4["name"]])

    context["crm_base_clients"] = [c1["name"], c2["name"], c3["name"], c4["name"]]
    print("  [OK] CRM filter create/edit/remove + views verified")
