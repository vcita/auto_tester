# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/_functions/create_client/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md
# Note: This function is adapted from tests/clients/create_matter/test.py

import re
import time
from playwright.sync_api import Page, expect

from tests._functions._config import get_base_url


def fn_create_client(page: Page, context: dict, **params) -> None:
    """
    Create a minimal client (matter/property) for test setup purposes.
    
    Creates a client with only required fields (first name) plus optional last name and email.
    Note: "Matter" is vcita's general entity - called "Property" for Home Services vertical.
    
    Parameters:
    - first_name (optional): First name of the client (defaults to "Test")
    - last_name (optional): Last name (defaults to "Client{timestamp}")
    - email (optional): Email address (defaults to generated test email)
    
    Saves to context:
    - created_client_id: ID of the created client
    - created_client_name: Full name of the client
    - created_client_email: Email of the client
    """
    timestamp = int(time.time())
    first_name = params.get("first_name", "Test")
    last_name = params.get("last_name", f"Client{timestamp}")
    email = params.get("email", f"test_{timestamp}@vcita-test.com")
    full_name = f"{first_name} {last_name}"
    
    # Step 1: Navigate to Dashboard
    base_url = get_base_url(context, params)
    print("  Step 1: Navigating to dashboard...")
    page.goto(f"{base_url}/app/dashboard")
    page.wait_for_load_state("domcontentloaded")
    # Wait for page to fully load by checking for Quick actions panel
    page.wait_for_timeout(2000)  # Initial load time
    
    # Step 2: Wait for Quick Actions Panel
    print("  Step 2: Waiting for Quick actions panel...")
    page.get_by_text("Quick actions", exact=True).wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(3000)  # Wait for panel content to fully render
    
    # Step 3: Click Add Property
    print("  Step 3: Clicking Add property...")
    add_property_text = page.get_by_text("Add property", exact=True)
    add_property_text.wait_for(state="visible", timeout=10000)
    add_property_text.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    add_property_text.click()
    
    # Step 4: Find Form Frame
    print("  Step 4: Waiting for property form...")
    form_frame = None
    max_attempts = 10
    for attempt in range(max_attempts):
        page.wait_for_timeout(500)
        for frame in page.frames:
            try:
                if frame.locator('text=First Name').count() > 0:
                    form_frame = frame
                    break
            except:
                pass
        if form_frame:
            break
        print(f"    Attempt {attempt + 1}/{max_attempts}: Form not found yet...")
    
    if not form_frame:
        raise Exception("Could not find form frame with 'First Name' field")
    
    print("  Step 5: Waiting for form content (First Name field)...")
    form_frame.locator('text=First Name').wait_for(timeout=15000)
    
    # Step 6: Fill First Name (Required)
    print(f"  Step 6: Filling contact information...")
    first_name_field = form_frame.get_by_role("textbox", name="First Name *")
    first_name_field.click()
    first_name_field.press_sequentially(first_name, delay=50)
    
    # Step 7: Fill Last Name
    last_name_field = form_frame.get_by_role("textbox", name="Last Name")
    last_name_field.click()
    last_name_field.press_sequentially(last_name, delay=50)
    
    # Step 8: Fill Email (becomes combobox when focused)
    email_field = form_frame.get_by_role("textbox", name="Email")
    email_field.click()
    page.wait_for_timeout(100)  # Wait for field transformation
    form_frame.get_by_role("combobox", name="Email").press_sequentially(email, delay=30)
    
    # Step 9: Click Save
    print("  Step 7: Clicking Save...")
    save_btn = form_frame.get_by_role("button", name="Save")
    save_btn.click()
    # Wait for navigation - increase timeout and wait for URL pattern
    # The navigation may take time, so we wait up to 30 seconds
    page.wait_for_url(re.compile(r"/app/clients/"), timeout=30000)
    
    # Step 10: Extract Client ID
    url = page.url
    client_id_match = re.search(r'/app/clients/([^/]+)', url)
    client_id = client_id_match.group(1) if client_id_match else None
    
    # Verify creation
    expect(page).to_have_url(re.compile(r"/app/clients/[a-z0-9]+"), timeout=10000)
    
    # Wait for page content to load
    page.wait_for_load_state("domcontentloaded")
    
    # Verify the client name appears in the page title
    # Increase timeout as page title may take time to update
    expect(page).to_have_title(re.compile(re.escape(full_name)), timeout=20000)
    
    # Save to context
    context["created_client_id"] = client_id
    context["created_client_name"] = full_name
    context["created_client_email"] = email
    
    print(f"  [OK] Created client: {full_name}")
    print(f"       Email: {email}")
    print(f"       Client ID: {client_id}")
