# Auto-generated from script.md
# Last updated: 2026-01-24
# Source: tests/scheduling/events/edit_event/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
from playwright.sync_api import Page, expect


def test_edit_event(page: Page, context: dict) -> None:
    """
    Test: Edit Event
    
    Modifies details of a scheduled group event instance (e.g., max attendance).
    
    Prerequisites:
    - User is logged in
    - A scheduled event exists and is open (context: scheduled_event_id)
    - Browser is on event detail page (from view_event or add_attendee test)
    
    Saves to context:
    - None (event is modified)
    """
    # Step 1: Verify on Event Detail Page
    print("  Step 1: Verifying on event detail page...")
    if "/app/events/" not in page.url:
        raise ValueError(f"Expected to be on event detail page, but URL is {page.url}")
    
    # Step 2: Click Edit Button
    print("  Step 2: Clicking Edit button...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    # Find Edit button - loop through buttons to find one with "Edit" text
    all_buttons = outer_iframe.get_by_role('button')
    button_count = all_buttons.count()
    edit_btn = None
    for i in range(button_count):
        try:
            btn = all_buttons.nth(i)
            btn_text = btn.text_content() or ""
            if 'Edit' in btn_text:
                edit_btn = btn
                break
        except:
            continue
    if not edit_btn:
        raise ValueError("Edit button not found")
    edit_btn.click()
    # Wait for edit dialog to appear
    dialog = outer_iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=10000)
    
    # Step 3: Modify Event Details (Max Attendance)
    print("  Step 3: Modifying max attendance to 12...")
    # Modify max attendance from 10 to 12
    max_attendance_field = outer_iframe.get_by_role('spinbutton', name='Max attendance *')
    max_attendance_field.click()
    max_attendance_field.fill('12')  # fill is OK for number spinbutton
    page.wait_for_timeout(500)  # Brief settle after spinbutton (allowed)

    # Step 4: Click Save
    print("  Step 4: Clicking Save...")
    save_btn = outer_iframe.get_by_role('button', name='Save')
    save_btn.click()
    # Wait for dialog to close
    dialog.wait_for(state='hidden', timeout=10000)

    # Step 5: Verify Changes are Reflected
    print("  Step 5: Verifying changes are reflected...")
    registered_text = outer_iframe.get_by_text(re.compile(r'\d+\s*/\s*12(\s+Registered)?', re.IGNORECASE))
    registered_text.wait_for(state='visible', timeout=10000)
    expect(registered_text).to_be_visible()
    
    print(f"  [OK] Event edited successfully")
    print(f"       Max attendance updated to 12")
