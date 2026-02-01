# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/scheduling/appointments/cancel_appointment/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page, expect


def test_cancel_appointment(page: Page, context: dict) -> None:
    """
    Test: Cancel Appointment
    
    Cancels an existing appointment from the business calendar.
    Verifies that the appointment status changes to "Cancelled".
    
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
    
    # Step 5: Click Cancel Appointment Button
    print("  Step 5: Clicking Cancel Appointment button...")
    cancel_btn = outer_iframe.get_by_role('button', name='Cancel Appointment')
    cancel_btn.wait_for(state='visible', timeout=5000)
    cancel_btn.click()
    # Wait for dialog to open instead of arbitrary timeout
    dialog = outer_iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=10000)
    
    # Step 6: Wait for Cancel Dialog
    print("  Step 6: Waiting for cancel dialog...")
    
    # Step 7: Click Submit Button
    print("  Step 7: Confirming cancellation...")
    submit_btn = outer_iframe.get_by_role('button', name='Submit')
    submit_btn.click()
    # Wait for cancellation to complete by checking for cancelled status
    # Step 8: Verify Appointment is Cancelled (Actual Data Verification)
    print("  Step 8: Verifying appointment is cancelled...")
    # Verify the status changed to "Cancelled" (actual data verification)
    cancelled_status = outer_iframe.get_by_text('Cancelled', exact=True)
    cancelled_status.wait_for(state='visible', timeout=15000)
    cancelled_status.wait_for(state='visible', timeout=10000)
    
    # Step 9: Return to Calendar
    print("  Step 9: Returning to calendar...")
    back_btn = page.get_by_text('Back')
    back_btn.click()
    page.wait_for_url("**/app/calendar**", timeout=10000)
    
    # Clear appointment context after cancellation (Rule 2.10)
    context.pop("created_appointment_client", None)
    context.pop("created_appointment_service", None)
    
    print(f"  [OK] Successfully cancelled appointment")
    print(f"       Client: {client_name}")
    print(f"       Service: {service_name}")
