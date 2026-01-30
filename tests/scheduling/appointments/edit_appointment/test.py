# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/scheduling/appointments/edit_appointment/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import time
from playwright.sync_api import Page, expect


def test_edit_appointment(page: Page, context: dict) -> None:
    """
    Test: Edit Appointment
    
    Adds a note to an existing appointment from the business calendar.
    Verifies that the note is saved and visible in the appointment details.
    
    Prerequisites:
    - User is logged in
    - An appointment exists (from create_appointment test)
    - Context has: created_appointment_client, created_appointment_service
    """
    # Get test data from context
    client_name = context.get("created_appointment_client")
    service_name = context.get("created_appointment_service")
    
    if not client_name:
        raise ValueError("No appointment client in context. Run create_appointment first.")
    if not service_name:
        raise ValueError("No appointment service in context. Run create_appointment first.")
    
    # Generate unique test note
    timestamp = int(time.time())
    test_note = f"Test note added at {timestamp}"
    
    # Step 1: Verify on Calendar Page
    print("  Step 1: Verifying on Calendar page...")
    if "/app/calendar" not in page.url:
        calendar_menu = page.get_by_text("Calendar", exact=True)
        calendar_menu.click()
        page.wait_for_url("**/app/calendar**", timeout=10000)
    
    # Step 2: Wait for Calendar to Load
    print("  Step 2: Waiting for Calendar to load...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    # Wait for calendar to load by waiting for appointment to be visible
    appointment = inner_iframe.get_by_role('menuitem').filter(has_text=client_name)
    appointment.wait_for(state='visible', timeout=10000)
    
    # Step 3: Click on Appointment in Calendar
    print(f"  Step 3: Clicking on appointment for client: {client_name}...")
    appointment = inner_iframe.get_by_role('menuitem').filter(has_text=client_name)
    appointment.wait_for(state='visible', timeout=10000)
    appointment.click()
    
    # Step 4: Wait for Appointment Details Page
    print("  Step 4: Waiting for appointment details page...")
    page.wait_for_url("**/app/appointments/**", timeout=10000)
    heading = outer_iframe.get_by_role('heading', name='Appointment').first
    heading.wait_for(state='visible', timeout=10000)
    
    # Step 5: Click Add Note Button
    print("  Step 5: Clicking Add note button...")
    add_note_btn = outer_iframe.get_by_role('button', name='Add note')
    add_note_btn.wait_for(state='visible', timeout=5000)
    add_note_btn.click()
    # Wait for note dialog to open (meaningful event: Save button in note iframe)
    note_iframe = outer_iframe.frame_locator('#vue_wizard_iframe')
    note_iframe.get_by_role('button', name='Save').wait_for(state='visible', timeout=30000)
    note_area = note_iframe.locator('[contenteditable="true"]')
    
    # Step 6: Enter Note Text
    print(f"  Step 6: Entering note: {test_note}...")
    # The note modal opens in a nested iframe with id vue_wizard_iframe
    note_area.click()
    page.wait_for_timeout(200)  # Brief settle for editor focus (allowed)
    page.keyboard.type(test_note)
    
    # Step 7: Save the Note
    print("  Step 7: Saving note...")
    save_btn = note_iframe.get_by_role('button', name='Save')
    save_btn.wait_for(state='visible', timeout=5000)
    save_btn.click()
    # Wait for save to complete by checking note appears in list
    # Step 8: Verify Note Saved (Actual Data Verification)
    print("  Step 8: Verifying note was saved...")
    # The note should appear as a button with the note text in the Internal note section
    saved_note = outer_iframe.get_by_role('button').filter(has_text=test_note)
    saved_note.wait_for(state='visible', timeout=10000)
    
    # Step 8: Verify Note Saved (Actual Data Verification)
    print("  Step 8: Verifying note was saved...")
    # The note should appear as a button with the note text in the Internal note section
    saved_note = outer_iframe.get_by_role('button').filter(has_text=test_note)
    saved_note.wait_for(state='visible', timeout=10000)
    
    # Step 9: Return to Calendar
    print("  Step 9: Returning to calendar...")
    back_btn = page.get_by_text('Back')
    back_btn.click()
    page.wait_for_url("**/app/calendar**", timeout=10000)
    
    # Save the note to context for potential verification
    context["last_appointment_note"] = test_note
    
    print(f"  [OK] Successfully edited appointment")
    print(f"       Client: {client_name}")
    print(f"       Note added: {test_note}")
