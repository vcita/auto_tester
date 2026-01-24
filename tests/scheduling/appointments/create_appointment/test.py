# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/scheduling/appointments/create_appointment/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page, expect


def test_create_appointment(page: Page, context: dict) -> None:
    """
    Test: Create Appointment
    
    Manually creates a 1-on-1 appointment for a test client using a test service
    from the business calendar.
    
    Prerequisites:
    - User is logged in
    - Test service exists (context: created_service_name)
    - Test client exists (context: created_client_name)
    
    Saves to context:
    - created_appointment_client: Name of the client for this appointment
    - created_appointment_service: Name of the service used
    """
    # Get test data from context
    client_name = context.get("created_client_name")
    service_name = context.get("created_service_name")
    
    if not client_name:
        raise ValueError("No test client in context. Run _setup first.")
    if not service_name:
        raise ValueError("No test service in context. Run _setup first.")
    
    # Step 1: Verify on Calendar Page
    print("  Step 1: Verifying on Calendar page...")
    if "/app/calendar" not in page.url:
        # Navigate to Calendar if not already there
        calendar_menu = page.get_by_text("Calendar", exact=True)
        calendar_menu.click()
        page.wait_for_url("**/app/calendar**", timeout=10000)
    
    # Step 2: Wait for Calendar to Load
    print("  Step 2: Waiting for Calendar to load...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    new_btn = inner_iframe.get_by_role('button', name='New')
    new_btn.wait_for(state='visible', timeout=10000)
    
    # Step 3: Click New Button
    print("  Step 3: Clicking New button...")
    new_btn.click()
    # Wait for the dropdown menu to appear
    page.wait_for_timeout(500)
    
    # Step 4: Select Appointment from Menu
    print("  Step 4: Selecting Appointment...")
    # CRITICAL: Use exact=True to avoid matching calendar items that contain "Appointment" in their text
    # Without exact=True, it matches both the menu item AND calendar appointment entries
    appointment_option = inner_iframe.get_by_role('menuitem', name='Appointment', exact=True)
    appointment_option.wait_for(state='visible', timeout=5000)
    appointment_option.click()
    dialog = outer_iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=10000)
    
    # Step 5: Search for Test Client
    print(f"  Step 5: Searching for client: {client_name}...")
    search_field = outer_iframe.get_by_role('textbox', name='Search by name, email or tag')
    search_field.click()
    page.wait_for_timeout(100)
    search_field.press_sequentially(client_name, delay=30)
    page.wait_for_timeout(500)  # Allow search results to update
    
    # Step 6: Select the Client
    print(f"  Step 6: Selecting client...")
    client_option = outer_iframe.get_by_role('button').filter(has_text=client_name)
    client_option.wait_for(state='visible', timeout=5000)
    client_option.click()
    page.wait_for_timeout(1000)  # Allow service panel to load
    
    # Step 7: Wait for Service panel and find service
    print(f"  Step 7: Looking for service: {service_name}...")
    # Wait for service selection panel to fully load
    page.wait_for_timeout(2000)
    # Wait for "My Services" label to confirm the list loaded
    inner_iframe.get_by_text('My Services').wait_for(state='visible', timeout=5000)
    
    # Step 8: Select the Service by clicking on it
    print(f"  Step 8: Selecting service...")
    # CRITICAL: Use .service-item class to click on the service ROW, not just the text
    # Using get_by_text() would match multiple elements (tooltip activator AND service label)
    # The service row has class "service-item" and is the clickable container
    service_row = inner_iframe.locator('.service-item').filter(has_text=service_name)
    service_row.wait_for(state='visible', timeout=5000)
    service_row.click()
    page.wait_for_timeout(2000)  # Allow service picker to close and appointment form to load
    
    # Verify the service picker closed by checking if Schedule button is now accessible
    schedule_btn = inner_iframe.get_by_role('button', name='Schedule appointment')
    schedule_btn.wait_for(state='visible', timeout=10000)
    
    # Step 9: Click Schedule Appointment
    print("  Step 9: Scheduling appointment...")
    # schedule_btn is already located in Step 8
    schedule_btn.click()
    
    # Step 10: Verify Appointment in Calendar (actual data verification)
    # NOTE: We verify the appointment appears in the calendar, NOT by checking toast messages
    print("  Step 10: Verifying appointment appears in calendar...")
    # Wait for the calendar to update and show the new appointment
    page.wait_for_timeout(3000)  # Allow calendar to refresh
    
    # The appointment appears as a menuitem in the calendar grid containing the client name
    appointment_in_calendar = inner_iframe.get_by_role('menuitem').filter(has_text=client_name)
    appointment_in_calendar.wait_for(state='visible', timeout=15000)
    
    # Save to context for subsequent tests
    context["created_appointment_client"] = client_name
    context["created_appointment_service"] = service_name
    
    print(f"  [OK] Appointment created successfully")
    print(f"       Client: {client_name}")
    print(f"       Service: {service_name}")
