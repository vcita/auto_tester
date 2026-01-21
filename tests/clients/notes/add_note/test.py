"""
Add Note Test

Adds a note to an existing matter to verify note creation functionality.
"""

import time
from playwright.sync_api import Page, expect


def test_add_note(page: Page, context: dict):
    """Add a note to the matter created by create_matter test."""
    
    # Get matter info from context
    matter_id = context.get("created_matter_id")
    matter_name = context.get("created_matter_name")
    
    if not matter_id:
        raise ValueError("No created_matter_id in context - create_matter test must run first")
    
    print(f"  Adding note to matter: {matter_name} (ID: {matter_id})")
    
    # Generate unique note content
    timestamp = int(time.time())
    note_content = f"Automated test note - Created at {timestamp}"
    
    # Step 1: Verify we're on the matter page (from previous test - edit_contact)
    # Real users don't type URLs - they navigate via UI. Since this test runs after
    # edit_contact, the browser should already be on the matter detail page.
    print(f"  Step 1: Verifying we're on the matter page...")
    if matter_id not in page.url:
        raise ValueError(f"Expected to be on matter page {matter_id}, but URL is {page.url}. "
                        "This test expects to run after edit_contact which should leave browser on matter page.")
    
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
    
    # Step 4: Click Add note button
    print(f"  Step 3: Clicking Add note button...")
    add_note_button = outer_iframe.get_by_role("button", name="Add note")
    add_note_button.click()
    page.wait_for_timeout(1000)
    
    # Step 5: Enter note content
    print(f"  Step 4: Entering note content...")
    wizard_iframe = outer_iframe.frame_locator('#vue_wizard_iframe')
    
    # The note area is a rich text editor - we need to click on it first, then it becomes editable
    # The placeholder "Add your note here" is shown initially
    note_area = wizard_iframe.locator('div[contenteditable="true"]').or_(
        wizard_iframe.get_by_text("Add your note here")
    )
    note_area.first.click()
    page.wait_for_timeout(500)
    
    # Now fill the content using keyboard
    page.keyboard.type(note_content)
    page.wait_for_timeout(500)
    
    # Step 6: Save note
    print(f"  Step 5: Saving note...")
    save_button = wizard_iframe.get_by_role("button", name="Save")
    save_button.click()
    page.wait_for_timeout(2000)
    
    # Step 7: Verify note appears in list
    print(f"  Step 6: Verifying note was created...")
    # Use first 30 chars to match since the list truncates
    note_item = inner_iframe.get_by_role("listitem").filter(has_text=note_content[:30])
    expect(note_item).to_be_visible(timeout=10000)
    
    # Update context with note content for edit/delete tests
    context["created_note_content"] = note_content
    context["created_note_timestamp"] = timestamp
    
    print(f"  [OK] Successfully added note to matter: {matter_name}")
    print(f"     Note content: {note_content[:50]}...")
