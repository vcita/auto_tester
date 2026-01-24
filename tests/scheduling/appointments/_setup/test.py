# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/scheduling/appointments/_setup/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import os
import time
from playwright.sync_api import Page, expect

from tests._functions.login.test import fn_login
from tests._functions.create_service.test import fn_create_service
from tests._functions.create_client.test import fn_create_client


def setup_appointments(page: Page, context: dict) -> None:
    """
    Setup for appointments tests.
    
    Performs login if needed, then creates:
    - A test service for booking appointments
    - A test client to book appointments for
    
    Then navigates to the Calendar page.
    
    Saves to context:
    - created_service_id: ID of the test service
    - created_service_name: Name of the test service
    - created_client_id: ID of the test client
    - created_client_name: Full name of the test client
    - created_client_email: Email of the client
    """
    timestamp = int(time.time())
    
    # Step 0: Login if not already logged in
    if "logged_in_user" not in context:
        print("  Setup Step 0: Logging in...")
        username = os.environ.get("VCITA_TEST_USERNAME", "itzik+autotest@vcita.com")
        password = os.environ.get("VCITA_TEST_PASSWORD", "vcita123")
        fn_login(page, context, username=username, password=password)
    
    # Step 1: Create Test Service
    print("  Setup Step 1: Creating test service...")
    service_name = f"Appointment Test Service {timestamp}"
    fn_create_service(page, context, name=service_name)
    print(f"    Service created: {context.get('created_service_name')}")
    
    # Step 2: Create Test Client
    print("  Setup Step 2: Creating test client...")
    fn_create_client(
        page, 
        context, 
        first_name="Appt",
        last_name=f"TestClient{timestamp}"
    )
    print(f"    Client created: {context.get('created_client_name')}")
    
    # Step 3: Navigate to Calendar
    print("  Setup Step 3: Navigating to Calendar...")
    calendar_menu = page.get_by_text("Calendar", exact=True)
    calendar_menu.click()
    page.wait_for_url("**/app/calendar**", timeout=10000)
    
    # Verify we're on the calendar page
    import re
    expect(page).to_have_url(re.compile(r".*app/calendar.*"))
    
    print("  [OK] Appointments setup complete")
    print(f"       Service: {context.get('created_service_name')} ({context.get('created_service_id')})")
    print(f"       Client: {context.get('created_client_name')} ({context.get('created_client_id')})")
