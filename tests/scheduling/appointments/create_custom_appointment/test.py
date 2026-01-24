# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/scheduling/appointments/create_custom_appointment/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time
from playwright.sync_api import Page, expect


def test_create_custom_appointment(page: Page, context: dict) -> None:
    """
    Test: Create Custom Appointment
    
    Creates a custom 1-on-1 appointment without using a predefined service.
    This allows booking a meeting that doesn't fit any existing service template.
    
    Prerequisites:
    - User is logged in
    - Test client exists (context: created_client_name)
    
    Saves to context:
    - created_custom_appointment_client: Name of the client for this appointment
    - created_custom_appointment_title: Custom meeting title
    """
    # Get test data from context
    client_name = context.get("created_client_name")
    
    if not client_name:
        raise ValueError("No test client in context. Run _setup first.")
    
    # Generate unique custom meeting title
    custom_title = f"Custom Meeting {int(time.time())}"
    
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
    new_btn = inner_iframe.get_by_role('button', name='New')
    new_btn.wait_for(state='visible', timeout=10000)
    
    # Step 3: Click New Button
    print("  Step 3: Clicking New button...")
    new_btn.click()
    page.wait_for_timeout(500)  # Wait for dropdown menu
    
    # Step 4: Select Appointment from Menu
    print("  Step 4: Selecting Appointment...")
    # CRITICAL: Use exact=True to avoid matching calendar items
    appointment_option = inner_iframe.get_by_role('menuitem', name='Appointment', exact=True)
    appointment_option.wait_for(state='visible', timeout=5000)
    appointment_option.click()
    # Wait for client selection dialog
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
    page.wait_for_timeout(1000)  # Wait for service panel to load
    
    # Step 7: Click Custom Service Button
    print("  Step 7: Clicking Custom service button...")
    # Click "Custom service" button to create a custom meeting without predefined service
    custom_service_btn = inner_iframe.get_by_role('button', name='Custom service')
    custom_service_btn.wait_for(state='visible', timeout=5000)
    custom_service_btn.click()
    page.wait_for_timeout(1000)  # Wait for custom service form to load
    
    # Step 8: Enter Custom Meeting Title
    print(f"  Step 8: Entering custom title: {custom_title}...")
    title_field = inner_iframe.get_by_role('textbox', name='Appointment title')
    title_field.wait_for(state='visible', timeout=5000)
    title_field.fill(custom_title)
    
    # Step 9: Select Location
    print("  Step 9: Selecting location...")
    # VERIFIED: The location dropdown button is the one with ONLY "arrow_drop_down" as text
    # The Price dropdown has "No Fee arrow_drop_down" so using regex /^arrow_drop_down$/ distinguishes them
    location_dropdown = inner_iframe.get_by_role('button').filter(has_text=re.compile(r'^arrow_drop_down$'))
    location_dropdown.wait_for(state='visible', timeout=5000)
    location_dropdown.click()
    page.wait_for_timeout(500)  # Wait for dropdown to open
    
    # VERIFIED: Options are in inner_iframe, use get_by_role('option')
    my_business_option = inner_iframe.get_by_role('option', name='My business address')
    my_business_option.wait_for(state='visible', timeout=10000)
    my_business_option.click()
    page.wait_for_timeout(500)  # Wait for selection to apply
    
    # Step 10: Click Schedule Appointment
    print("  Step 10: Scheduling appointment...")
    schedule_btn = inner_iframe.get_by_role('button', name='Schedule appointment')
    schedule_btn.wait_for(state='visible', timeout=5000)
    schedule_btn.click()
    
    # Step 11: Verify Appointment in Calendar (Actual Data Verification)
    print("  Step 11: Verifying appointment appears in calendar...")
    page.wait_for_timeout(3000)  # Allow calendar to refresh
    
    # The custom appointment appears as a menuitem containing the custom title
    appointment_in_calendar = inner_iframe.get_by_role('menuitem').filter(has_text=custom_title)
    appointment_in_calendar.wait_for(state='visible', timeout=15000)
    
    # Save to context for potential subsequent tests
    context["created_custom_appointment_client"] = client_name
    context["created_custom_appointment_title"] = custom_title
    
    print(f"  [OK] Custom appointment created successfully")
    print(f"       Client: {client_name}")
    print(f"       Title: {custom_title}")
