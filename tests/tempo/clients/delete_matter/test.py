# Auto-generated from script.md
# Last updated: 2026-04-06
# Source: tests/clients/delete_matter/script.md

import re
from playwright.sync_api import Page, expect

from tests._functions.login.test import fn_login


def _ensure_logged_in(page: Page, context: dict) -> None:
    """Re-login if session was lost (redirect to /login)."""
    if "/login" in page.url or "Login" in (page.title() or ""):
        print("  [!] Session lost - re-logging in...")
        fn_login(
            page, context,
            username=context.get("username"),
            password=context.get("password"),
        )


def test_delete_matter(page: Page, context: dict) -> None:
    """
    Test: Delete Matter from Clients List

    Deletes an existing matter from the clients/properties list
    and verifies the deletion was successful.

    Requires context from create_matter test:
    - created_matter_name: The full name of the matter to delete

    Clears from context after successful deletion:
    - created_matter_name, created_matter_email, created_matter_id
    """
    matter_name = context.get("created_matter_name")
    if not matter_name:
        raise ValueError("Context missing 'created_matter_name' - run create_matter test first")

    print(f"  Deleting matter: {matter_name}")

    _ensure_logged_in(page, context)

    # ========== PART 1: Navigate to Clients List ==========
    print("  Step 1: Navigating to Clients list...")
    properties_nav = page.locator('.menu-items-group > div:nth-child(4)')
    properties_nav.click()

    page.wait_for_url(re.compile(r"/app/clients"), timeout=10000)
    page.wait_for_load_state("domcontentloaded")

    # ========== PART 2: Find and Select the Matter ==========
    print(f"  Step 2: Searching for '{matter_name}'...")
    searchbox = page.get_by_role("searchbox", name="Search by name, email, or phone number")
    searchbox.click()
    searchbox.press_sequentially(matter_name, delay=30)

    name_prefix = matter_name[: min(30, len(matter_name))]
    matter_row = page.get_by_role("row").filter(has_text=name_prefix).first
    matter_row.wait_for(state="visible", timeout=10000)

    print("  Step 3: Selecting matter row...")
    checkbox_btn = matter_row.get_by_role("checkbox").locator("xpath=ancestor::button[1]")
    checkbox_btn.scroll_into_view_if_needed(timeout=5000)
    page.wait_for_timeout(200)
    checkbox_btn.click(force=True)

    selection_indicator = page.get_by_text(re.compile(r"1 SELECTED OF \d+"))
    selection_indicator.wait_for(state="visible", timeout=15000)
    print("  [OK] Row selected")

    # ========== PART 3: Delete the Matter ==========
    # Brief wait for bulk action bar to stabilize after re-render
    page.wait_for_timeout(1500)

    more_btn = page.get_by_role("button", name="More", exact=True)
    more_btn.wait_for(state="visible", timeout=10000)

    print("  Step 4: Clicking More button...")
    more_btn.click(timeout=12000)

    print("  Step 5: Clicking Delete option...")
    delete_option = page.get_by_role("menu").get_by_text("Delete")
    delete_option.wait_for(state="visible", timeout=8000)
    delete_option.click()

    dialog_title = page.get_by_text(re.compile(r"Delete .+\?", re.IGNORECASE))
    dialog_title.wait_for(state="visible", timeout=5000)

    print("  Step 6: Confirming deletion...")
    confirm_delete_btn = page.get_by_role("button", name="Delete")
    confirm_delete_btn.click()

    success_dialog_title = page.get_by_text(
        re.compile(r"(properties|clients|patients|students|pets)\s+deleted", re.IGNORECASE)
    )
    success_dialog_title.wait_for(state="visible", timeout=15000)

    print("  Step 7: Acknowledging success dialog...")
    ok_btn = page.get_by_role("button", name="OK")
    ok_btn.click()

    success_dialog_title.wait_for(state="hidden", timeout=10000)

    # ========== PART 4: Verify Deletion ==========
    print("  Step 8: Verifying matter was deleted...")
    matter_row_after = page.get_by_role("row").filter(has_text=name_prefix)
    expect(matter_row_after).to_have_count(0, timeout=10000)

    context.pop("created_matter_name", None)
    context.pop("created_matter_email", None)
    context.pop("created_matter_id", None)

    print(f"  [OK] Successfully deleted matter: {matter_name}")
    print(f"     Context cleared: created_matter_name, created_matter_email, created_matter_id")
