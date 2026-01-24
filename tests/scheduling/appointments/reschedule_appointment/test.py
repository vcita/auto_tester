# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/scheduling/appointments/reschedule_appointment/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page, expect


def test_reschedule_appointment(page: Page, context: dict) -> None:
    """
    Test: Reschedule Appointment
    
    Reschedules an existing appointment to a different time slot.
    Verifies that the new time is saved and displayed correctly.
    
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
    page.wait_for_timeout(2000)  # Wait for calendar to load
    
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
    
    # Step 5: Get Current Time from Heading
    print("  Step 5: Reading current appointment time...")
    time_heading = outer_iframe.get_by_role('heading', level=2).first
    time_heading.wait_for(state='visible', timeout=5000)
    original_time = time_heading.text_content()
    print(f"       Original time: {original_time}")
    
    # Step 6: Click Reschedule Button
    print("  Step 6: Clicking Reschedule button...")
    reschedule_btn = outer_iframe.get_by_role('button', name='Reschedule').first
    reschedule_btn.wait_for(state='visible', timeout=5000)
    reschedule_btn.click()
    page.wait_for_timeout(1000)  # Wait for dialog to open
    
    # Step 7: Wait for Reschedule Dialog
    print("  Step 7: Waiting for reschedule dialog...")
    dialog = outer_iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=10000)
    
    # Step 8: Open Start Time Dropdown
    print("  Step 8: Opening time dropdown...")
    # Click on the select button to open the time dropdown
    # VERIFIED: The second "select" button (nth(1)) opens the time picker
    outer_iframe.get_by_role('button', name='select').nth(1).click()
    page.wait_for_timeout(500)  # Wait for dropdown to open
    
    # Step 9: Select New Time
    print("  Step 9: Selecting new time...")
    # VERIFIED: The dropdown contains option elements with time text like "8:00pm"
    # Select a time that's different from current - using 10:00am as a safe default
    # that's unlikely to conflict with current appointment time
    new_time_option = outer_iframe.get_by_text('10:00am', exact=True)
    new_time_option.click()
    page.wait_for_timeout(500)  # Wait for selection to apply
    
    # Step 10: Click Submit Button
    print("  Step 10: Submitting reschedule...")
    submit_btn = outer_iframe.get_by_role('button', name='Submit')
    submit_btn.click()
    page.wait_for_timeout(2000)  # Wait for reschedule to complete
    
    # Step 11: Verify Time Changed (Actual Data Verification)
    print("  Step 11: Verifying time was changed...")
    # Verify the time has changed by checking the h2 heading
    time_heading = outer_iframe.get_by_role('heading', level=2).first
    time_heading.wait_for(state='visible', timeout=10000)
    new_time = time_heading.text_content()
    print(f"       New time: {new_time}")
    
    # Also verify "Rescheduled from" section appears
    rescheduled_from = outer_iframe.get_by_text('Rescheduled from')
    rescheduled_from.wait_for(state='visible', timeout=5000)
    
    # Verify time actually changed
    if original_time == new_time:
        raise AssertionError(f"Time did not change! Still showing: {new_time}")
    
    # Step 12: Return to Calendar
    print("  Step 12: Returning to calendar...")
    back_btn = page.get_by_text('Back')
    back_btn.click()
    page.wait_for_url("**/app/calendar**", timeout=10000)
    
    print(f"  [OK] Successfully rescheduled appointment")
    print(f"       Client: {client_name}")
    print(f"       Original: {original_time}")
    print(f"       New: {new_time}")
