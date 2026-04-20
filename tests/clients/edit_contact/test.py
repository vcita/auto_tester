# Edit Contact Test
# Last updated: 2026-04-05
# Source: tests/clients/edit_contact/script.md
# Note: Edits CONTACT fields (name, address, referred by) - distinct from edit_matter

import re
import time
from playwright.sync_api import Page, expect


def generate_edit_data() -> dict:
    """Generate new values for editing contact fields.
    Uses short suffix (6 digits) so displayed name fits in table without ellipsis."""
    timestamp = int(time.time())
    return {
        "last_name": f"CE{timestamp % 1000000}",
        "address": f"EDITED: {timestamp % 1000} Updated Street, New City",
        "referred_by": f"EDITED: Test Referral - {timestamp}",
    }


def _clear_and_type(field, page: Page, value: str, delay: int = 30) -> None:
    """Clear a field reliably (cross-platform) then type new value."""
    field.click()
    field.fill("")
    field.press_sequentially(value, delay=delay)


def test_edit_contact(page: Page, context: dict) -> None:
    """
    Test: Edit Contact Information

    Edits contact fields of an existing matter and verifies changes.
    Adapts to available fields (Referred by may not exist on all verticals).

    Reads from context: created_matter_id, created_matter_name
    Saves to context: edited_last_name, edited_address, edited_referred_by, created_matter_name
    """
    if "created_matter_id" not in context:
        raise ValueError("Context missing 'created_matter_id' - create_matter test must run first")
    if "created_matter_name" not in context:
        raise ValueError("Context missing 'created_matter_name' - create_matter test must run first")

    matter_id = context["created_matter_id"]
    current_name = context["created_matter_name"]
    first_name = current_name.split()[0] if current_name else "Unknown"
    edit_data = generate_edit_data()

    print(f"  Editing contact for: {current_name} (ID: {matter_id})")

    # ========== STEP 1: Verify on matter detail page ==========
    print("  Step 1: Verifying on matter detail page...")
    if matter_id not in page.url:
        raise ValueError(
            f"Expected to be on matter page {matter_id}, but URL is {page.url}. "
            "Sequential test context violation."
        )
    expect(page).to_have_url(re.compile(rf"/app/clients/{re.escape(matter_id)}"))

    # ========== STEP 2: Wait for iframes ==========
    print("  Step 2: Waiting for iframes to load...")
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=15000)

    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')

    # ========== STEP 3: Open edit contact dialog ==========
    print("  Step 3: Opening edit contact dialog...")
    edit_contact_button = inner_iframe.locator(
        '.contact-header > .v-icon.notranslate.edit-button'
    )
    edit_contact_button.wait_for(state="visible", timeout=10000)
    edit_contact_button.click()

    dialog_title = outer_iframe.locator("text=Edit contact info")
    dialog_title.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(300)

    # ========== STEP 4: Edit Last Name ==========
    print(f"  Step 4: Editing Last Name to '{edit_data['last_name']}'...")
    last_name_field = outer_iframe.get_by_role("textbox", name="Last Name")
    _clear_and_type(last_name_field, page, edit_data["last_name"])

    # ========== STEP 5: Edit Address ==========
    print(f"  Step 5: Editing Address to '{edit_data['address']}'...")
    address_field = outer_iframe.get_by_role("textbox", name="Address")
    _clear_and_type(address_field, page, edit_data["address"])

    # Dismiss address autocomplete by clicking dialog title (avoids Birthday datepicker)
    outer_iframe.locator("text=Edit contact info").click()
    page.wait_for_timeout(300)

    # ========== STEP 6: Edit Referred By (if available) ==========
    referred_edited = False
    referred_field = outer_iframe.get_by_role("textbox", name="Referred by")
    try:
        if referred_field.count() > 0 and referred_field.is_visible(timeout=2000):
            print(f"  Step 6: Editing Referred by to '{edit_data['referred_by']}'...")
            _clear_and_type(referred_field, page, edit_data["referred_by"])
            referred_edited = True
        else:
            print("  Step 6: Referred by field not available, skipping...")
    except Exception:
        print("  Step 6: Referred by field not available, skipping...")

    # ========== STEP 7: Save ==========
    print("  Step 7: Saving changes...")
    save_button = outer_iframe.get_by_role("button", name=re.compile(r"Save|SAVE", re.IGNORECASE))
    save_button.click()

    dialog_title.wait_for(state="hidden", timeout=15000)

    # ========== STEP 8: Verify page title ==========
    print("  Step 8: Verifying page title updated...")
    expected_name = f"{first_name} {edit_data['last_name']}"
    expect(page).to_have_title(re.compile(re.escape(expected_name)), timeout=15000)

    # ========== STEP 9: Verify fields by reopening dialog ==========
    print("  Step 9: Re-opening dialog to verify field values...")
    edit_contact_button.click()
    dialog_title_verify = outer_iframe.locator("text=Edit contact info")
    dialog_title_verify.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(300)

    expect(outer_iframe.get_by_role("textbox", name="Last Name")).to_have_value(
        edit_data["last_name"], timeout=5000
    )
    expect(outer_iframe.get_by_role("textbox", name="Address")).to_have_value(
        edit_data["address"], timeout=5000
    )

    if referred_edited:
        expect(outer_iframe.get_by_role("textbox", name="Referred by")).to_have_value(
            edit_data["referred_by"], timeout=5000
        )

    outer_iframe.get_by_role("button", name=re.compile(r"Cancel|CANCEL", re.IGNORECASE)).click()
    dialog_title_verify.wait_for(state="hidden", timeout=10000)

    # ========== Update context ==========
    context["edited_last_name"] = edit_data["last_name"]
    context["edited_address"] = edit_data["address"]
    if referred_edited:
        context["edited_referred_by"] = edit_data["referred_by"]

    new_full_name = f"{first_name} {edit_data['last_name']}"
    context["created_matter_name"] = new_full_name

    print(f"  [OK] Successfully edited contact: {new_full_name}")
    print(f"     New last name: {edit_data['last_name']}")
    print(f"     New address: {edit_data['address']}")
    if referred_edited:
        print(f"     New referred by: {edit_data['referred_by']}")
