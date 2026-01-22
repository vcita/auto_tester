"""
Delete Note Test

Deletes a note from a matter to verify note deletion functionality.
"""

from playwright.sync_api import Page, expect


def test_delete_note(page: Page, context: dict):
    """Delete the note edited by edit_note test."""
    
    # Get matter info from context
    matter_id = context.get("created_matter_id")
    matter_name = context.get("created_matter_name")
    edited_content = context.get("edited_note_content")
    
    if not matter_id:
        raise ValueError("No created_matter_id in context - create_matter test must run first")
    if not edited_content:
        raise ValueError("No edited_note_content in context - edit_note test must run first")
    
    print(f"  Deleting note from matter: {matter_name} (ID: {matter_id})")
    
    # Step 1: Verify we're on the matter page (from previous test - edit_note)
    # Real users don't type URLs - they navigate via UI. Since this test runs after
    # edit_note, the browser should already be on the matter detail page.
    print(f"  Step 1: Verifying we're on the matter page...")
    if matter_id not in page.url:
        raise ValueError(f"Expected to be on matter page {matter_id}, but URL is {page.url}. "
                        "This test expects to run after edit_note which should leave browser on matter page.")
    
    # Wait for page to be ready
    page.wait_for_load_state("domcontentloaded")
    
    # Step 2: Set up iframe locators and wait for iframe
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=15000)
    
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    
    # Step 3: Click Notes tab (should already be active from edit_note, but click to ensure)
    print(f"  Step 2: Clicking Notes tab...")
    notes_tab = inner_iframe.get_by_role("tab", name="Notes")
    notes_tab.click()
    
    # Wait for the edited note to be visible in the list
    note_item = inner_iframe.get_by_role("listitem").filter(has_text="EDITED:")
    note_item.wait_for(state="visible", timeout=10000)
    
    # Step 4: Find the note and click three dots menu
    print(f"  Step 3: Opening note menu...")
    # Click the three dots menu icon (the "i" element inside the note)
    note_item.locator("i").click()
    
    # Step 5: Click Remove option
    print(f"  Step 4: Clicking Remove...")
    remove_option = inner_iframe.get_by_role("listitem").filter(has_text="Remove")
    remove_option.wait_for(state="visible", timeout=5000)
    remove_option.click()
    
    # Step 6: Confirm deletion - wait for OK button in confirmation dialog
    print(f"  Step 5: Confirming deletion...")
    ok_button = outer_iframe.get_by_role("button", name="Ok")
    ok_button.wait_for(state="visible", timeout=5000)
    ok_button.click()
    
    # Wait for confirmation dialog to close
    ok_button.wait_for(state="hidden", timeout=10000)
    
    # Step 7: Verify note is deleted
    print(f"  Step 6: Verifying note was deleted...")
    deleted_note = inner_iframe.get_by_role("listitem").filter(has_text="EDITED:")
    deleted_note.wait_for(state="hidden", timeout=10000)
    
    # Clean up note-related context
    if "created_note_content" in context:
        del context["created_note_content"]
    if "edited_note_content" in context:
        del context["edited_note_content"]
    if "created_note_timestamp" in context:
        del context["created_note_timestamp"]
    
    print(f"  [OK] Successfully deleted note from matter: {matter_name}")
    print(f"     Context cleaned: created_note_content, edited_note_content")
