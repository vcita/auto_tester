"""
Add Note Test

Adds a note to an existing matter to verify note creation functionality.
"""

import re
import time
from playwright.sync_api import Page, expect

from tests._functions.login.test import fn_login
from tests.tempo.clients.notes.note_helpers import UI_TIMEOUT, navigate_to_matter_page


def _ensure_on_matter_page(page: Page, context: dict, matter_id: str) -> None:
    """Recover session and navigate to the matter page if needed."""
    page.wait_for_timeout(500)
    current_url = page.url

    if matter_id in current_url:
        return

    if "/login" in current_url or "Login" in (page.title() or ""):
        print("  [!] Session lost - re-logging in...")
        fn_login(
            page, context,
            username=context.get("username"),
            password=context.get("password"),
        )

    navigate_to_matter_page(page, context, matter_id)


def test_add_note(page: Page, context: dict):
    """Add a note to the matter created by create_matter test."""

    matter_id = context.get("created_matter_id")
    matter_name = context.get("created_matter_name")

    if not matter_id:
        raise ValueError("No created_matter_id in context - create_matter test must run first")

    print(f"  Adding note to matter: {matter_name} (ID: {matter_id})")

    timestamp = int(time.time())
    note_content = f"Automated test note - Created at {timestamp}"

    # Step 1: Ensure we're on the matter page (recover session if needed)
    print("  Step 1: Ensuring we're on the matter page...")
    _ensure_on_matter_page(page, context, matter_id)

    if matter_id not in page.url:
        raise ValueError(
            f"Expected to be on matter page {matter_id}, but URL is {page.url}."
        )

    page.wait_for_load_state("domcontentloaded")

    # Step 2: Wait for angular iframe
    print("  Step 2: Waiting for angular iframe...")
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=UI_TIMEOUT)

    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')

    # Step 3: Click Notes tab
    print("  Step 3: Clicking Notes tab...")
    notes_tab = inner_iframe.get_by_role("tab", name="Notes")
    notes_tab.click()

    add_note_button = outer_iframe.get_by_role("button", name="Add note")
    add_note_button.wait_for(state="visible", timeout=UI_TIMEOUT)

    # Step 4: Click Add note button
    print("  Step 4: Clicking Add note button...")
    add_note_button.click()

    # Check session wasn't lost after the click (server call may trigger 401 redirect)
    page.wait_for_timeout(1000)
    if "/login" in page.url:
        print("  [!] Session lost after clicking Add note - recovering...")
        _ensure_on_matter_page(page, context, matter_id)
        angular_iframe.wait_for(state="visible", timeout=UI_TIMEOUT)
        notes_tab = inner_iframe.get_by_role("tab", name="Notes")
        notes_tab.click()
        add_note_button = outer_iframe.get_by_role("button", name="Add note")
        add_note_button.wait_for(state="visible", timeout=UI_TIMEOUT)
        add_note_button.click()
        page.wait_for_timeout(1000)

    # Step 5: Enter note content in wizard iframe
    print("  Step 5: Entering note content...")
    wizard_iframe_locator = outer_iframe.locator('#vue_wizard_iframe')
    wizard_iframe_locator.wait_for(state="visible", timeout=UI_TIMEOUT)

    wizard_iframe = outer_iframe.frame_locator('#vue_wizard_iframe')

    page.wait_for_timeout(500)
    save_button = wizard_iframe.get_by_role("button", name="Save")
    save_button.wait_for(state="visible", timeout=UI_TIMEOUT)

    note_area = wizard_iframe.locator('div[contenteditable="true"]').or_(
        wizard_iframe.get_by_text("Add your note here")
    )
    note_area.first.click()
    page.wait_for_timeout(200)

    page.keyboard.type(note_content)

    # Step 6: Save note
    print("  Step 6: Saving note...")
    save_button.click()
    # Wait for the wizard iframe to close (more reliable than the button inside it)
    wizard_iframe_locator.wait_for(state="hidden", timeout=UI_TIMEOUT)

    # Step 7: Verify note appears in list
    print("  Step 7: Verifying note was created...")
    note_item = inner_iframe.get_by_role("listitem").filter(has_text=note_content[:30])
    note_item.wait_for(state="visible", timeout=UI_TIMEOUT)

    context["created_note_content"] = note_content
    context["created_note_timestamp"] = timestamp

    print(f"  [OK] Successfully added note to matter: {matter_name}")
    print(f"     Note content: {note_content[:50]}...")
