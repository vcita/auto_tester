# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/scheduling/appointments/view_appointment/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page, expect


def test_view_appointment(page: Page, context: dict) -> None:
    """
    Test: View Appointment
    
    Opens and views the details of an existing appointment from the business calendar.
    Verifies that client name, service name, and date/time are displayed correctly.
    
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
    # Wait for calendar grid to load by waiting for appointment to be visible
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
    # Wait for details panel to load - use .first as there may be multiple "Appointment" headings
    heading = outer_iframe.get_by_role('heading', name='Appointment').first
    heading.wait_for(state='visible', timeout=10000)
    
    # Step 5: Verify Client Name (actual data verification)
    print(f"  Step 5: Verifying client name: {client_name}...")
    client_text = outer_iframe.get_by_text(client_name)
    client_text.wait_for(state='visible', timeout=5000)
    
    # Step 6: Verify Service Name matches what we created (actual data verification)
    print(f"  Step 6: Verifying service name: {service_name}...")
    # The first h3 heading in the details panel is the service name
    service_heading = outer_iframe.get_by_role('heading', level=3).first
    service_heading.wait_for(state='visible', timeout=5000)
    # Get the service name that's actually displayed and verify it matches
    actual_service = service_heading.text_content().strip()
    print(f"       Displayed service: {actual_service}")
    if service_name not in actual_service:
        raise AssertionError(f"Service mismatch! Expected '{service_name}' but found '{actual_service}'")
    
    # Step 7: Verify Date/Time Displayed
    print("  Step 7: Verifying date/time is displayed...")
    # The date/time appears in an h2 heading within the details
    date_time_heading = outer_iframe.get_by_role('heading', level=2)
    date_time_heading.wait_for(state='visible', timeout=5000)
    
    # Step 8: Click Back to Return to Calendar
    print("  Step 8: Returning to calendar...")
    back_btn = page.get_by_text('Back')
    back_btn.click()
    page.wait_for_url("**/app/calendar**", timeout=10000)
    
    print(f"  [OK] Successfully viewed appointment")
    print(f"       Client: {client_name}")
    print(f"       Service: {service_name}")
