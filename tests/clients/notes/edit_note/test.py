"""
Edit Note Test

Edits an existing note on a matter to verify note editing functionality.
"""

import time
from playwright.sync_api import Page, expect


def test_edit_note(page: Page, context: dict):
    """Edit the note created by add_note test."""
    
    # Get matter and note info from context
    matter_id = context.get("created_matter_id")
    matter_name = context.get("created_matter_name")
    original_content = context.get("created_note_content")
    
    if not matter_id:
        raise ValueError("No created_matter_id in context - create_matter test must run first")
    if not original_content:
        raise ValueError("No created_note_content in context - add_note test must run first")
    
    print(f"  Editing note on matter: {matter_name} (ID: {matter_id})")
    
    # Generate new note content
    timestamp = int(time.time())
    new_content = f"EDITED: Updated note at {timestamp}"
    
    # Step 1: Verify we're on the matter page (from previous test - add_note)
    # Real users don't type URLs - they navigate via UI. Since this test runs after
    # add_note, the browser should already be on the matter detail page.
    print(f"  Step 1: Verifying we're on the matter page...")
    if matter_id not in page.url:
        raise ValueError(f"Expected to be on matter page {matter_id}, but URL is {page.url}. "
                        "This test expects to run after add_note which should leave browser on matter page.")
    
    # Wait for page to be ready
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_timeout(1000)
    
    # Step 2: Set up iframe locators
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    
    # Step 3: Click Notes tab
    print(f"  Step 2: Clicking Notes tab...")
    notes_tab = inner_iframe.get_by_role("tab", name="Notes")
    notes_tab.click()
    page.wait_for_timeout(1000)
    
    # Step 4: Click on note to open dialog
    print(f"  Step 3: Opening note dialog...")
    note_item = inner_iframe.get_by_role("listitem").filter(has_text=original_content[:30])
    note_item.click()
    page.wait_for_timeout(1000)
    
    # Step 5: Click on note content to activate editor
    print(f"  Step 4: Activating editor...")
    note_content_button = outer_iframe.get_by_role("button").filter(has_text=original_content[:30])
    note_content_button.click()
    page.wait_for_timeout(500)
    
    # Step 6: Clear and enter new content
    print(f"  Step 5: Editing note content...")
    page.keyboard.press("Control+a")
    page.keyboard.type(new_content)
    page.wait_for_timeout(500)
    
    # Step 7: Save and close dialog
    print(f"  Step 6: Saving changes...")
    # The dialog has SAVE button (not Close) when in edit mode
    save_button = outer_iframe.get_by_role("button", name="Save")
    save_button.click()
    page.wait_for_timeout(1500)
    
    # Step 8: Verify edit was saved
    print(f"  Step 7: Verifying edit was saved...")
    edited_note = inner_iframe.get_by_role("listitem").filter(has_text="EDITED:")
    expect(edited_note).to_be_visible(timeout=10000)
    
    # Update context with edited content for delete test
    context["edited_note_content"] = new_content
    
    print(f"  [OK] Successfully edited note on matter: {matter_name}")
    print(f"     New content: {new_content}")
