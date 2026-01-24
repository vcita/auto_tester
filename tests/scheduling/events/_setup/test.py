# Auto-generated from script.md
# Last updated: 2026-01-24
# Source: tests/scheduling/events/_setup/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import os
import time
from playwright.sync_api import Page, expect

from tests._functions.login.test import fn_login
from tests._functions.create_client.test import fn_create_client


def setup_events(page: Page, context: dict) -> None:
    """
    Setup for events tests.
    
    Performs login if needed, then creates:
    - A group event service for scheduling event instances
    - A test client to add as an attendee
    
    Then navigates to the Calendar page.
    
    Saves to context:
    - event_group_service_name: Name of the group event service
    - event_client_id: ID of the test client
    - event_client_name: Full name of the test client
    - event_client_email: Email of the test client
    """
    timestamp = int(time.time())
    
    # Step 0: Login if not already logged in
    if "logged_in_user" not in context:
        print("  Setup Step 0: Logging in...")
        username = os.environ.get("VCITA_TEST_USERNAME", "itzik+autotest@vcita.com")
        password = os.environ.get("VCITA_TEST_PASSWORD", "vcita123")
        fn_login(page, context, username=username, password=password)
    
    # Step 1: Navigate to Settings
    print("  Setup Step 1: Navigating to Settings...")
    settings_menu = page.get_by_text("Settings", exact=True)
    settings_menu.click()
    page.wait_for_url("**/app/settings**", timeout=10000)
    
    # Step 2: Navigate to Services
    print("  Setup Step 2: Navigating to Services...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    services_btn = iframe.get_by_role("button", name="Define the services your")
    services_btn.click()
    page.wait_for_url("**/app/settings/services**", timeout=10000)
    
    # Generate unique group event name
    group_event_name = f"Event Test Workshop {timestamp}"
    
    # Step 3: Open New Service Dropdown
    print("  Setup Step 3: Opening New service menu...")
    new_service_btn = iframe.get_by_role("button", name="New service icon-caret-down")
    new_service_btn.click()
    # Wait for dropdown menu to appear
    menu = iframe.get_by_role("menu")
    menu.wait_for(state="visible", timeout=5000)
    
    # Step 4: Select Group Event
    print("  Setup Step 4: Selecting Group event...")
    group_event_option = iframe.get_by_role("menuitem", name="Group event")
    group_event_option.click()
    # Wait for dialog to appear
    dialog = iframe.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=10000)
    
    # Step 5: Fill Service Name
    print(f"  Setup Step 5: Entering service name: {group_event_name}")
    name_field = iframe.get_by_role("textbox", name="Service name *")
    name_field.click()
    page.wait_for_timeout(100)  # Brief delay for field focus
    name_field.press_sequentially(group_event_name, delay=30)
    
    # Step 6: Set Max Attendees
    print("  Setup Step 6: Setting max attendees to 10...")
    max_attendees_field = iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")
    max_attendees_field.click()
    max_attendees_field.fill("10")  # fill is OK for number spinbutton
    
    # Step 7: Select Face to Face Location
    print("  Setup Step 7: Selecting Face to face location...")
    face_to_face_btn = iframe.get_by_role("button", name="icon-Home Face to face")
    face_to_face_btn.click()
    # Wait for address options to appear
    address_options = iframe.get_by_role("radiogroup")
    address_options.wait_for(state="visible", timeout=5000)
    # Default "My business address" is already selected - no action needed
    
    # Step 8: Select With Fee and Enter Price
    print("  Setup Step 8: Setting price to 25...")
    with_fee_btn = iframe.get_by_role("button", name="icon-Credit-card With fee")
    with_fee_btn.click()
    # Wait for price field to appear
    price_field = iframe.get_by_role("spinbutton", name="Service price *")
    price_field.wait_for(state="visible", timeout=5000)
    price_field.click()
    price_field.fill("25")  # fill is OK for number spinbutton
    
    # Step 9: Click Create
    print("  Setup Step 9: Clicking Create...")
    create_btn = iframe.get_by_role("button", name="Create")
    create_btn.click()
    
    # Step 10: Handle Event Times Dialog (Conditional)
    print("  Setup Step 10: Checking for event times dialog...")
    later_btn = iframe.get_by_role("button", name="I'll do it later")
    
    # Wait a short time to see if the dialog appears
    try:
        later_btn.wait_for(state="visible", timeout=3000)
        print("  Setup Step 10a: Event times dialog appeared - dismissing...")
        later_btn.click()
        page.wait_for_timeout(500)  # Brief settle time
    except:
        # Dialog didn't appear - this is OK, continue
        print("  Setup Step 10a: Event times dialog did not appear - continuing...")
    
    # Wait for any remaining dialogs to close
    page.wait_for_timeout(500)  # Brief settle time for dialogs to close
    
    # Step 11: Save Group Event Service Name
    print("  Setup Step 11: Saving group event service name...")
    context["event_group_service_name"] = group_event_name
    print(f"    Group event service created: {group_event_name}")
    
    # Step 12: Create Test Client
    print("  Setup Step 12: Creating test client...")
    fn_create_client(
        page, 
        context, 
        first_name="Event",
        last_name=f"TestClient{timestamp}"
    )
    
    # Save to context with event-specific names
    context["event_client_id"] = context.get("created_client_id")
    context["event_client_name"] = context.get("created_client_name")
    context["event_client_email"] = context.get("created_client_email")
    print(f"    Client created: {context.get('event_client_name')}")
    
    # Step 13: Navigate to Calendar
    print("  Setup Step 13: Navigating to Calendar...")
    calendar_menu = page.get_by_text("Calendar", exact=True)
    calendar_menu.click()
    page.wait_for_url("**/app/calendar**", timeout=10000)
    
    # Verify we're on the calendar page
    import re
    expect(page).to_have_url(re.compile(r".*app/calendar.*"))
    
    print("  [OK] Events setup complete")
    print(f"       Group Event Service: {context.get('event_group_service_name')}")
    print(f"       Client: {context.get('event_client_name')} ({context.get('event_client_id')})")
