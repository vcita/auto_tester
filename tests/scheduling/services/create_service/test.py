# Auto-generated from script.md
# Last updated: 2026-01-22
# Source: tests/scheduling/services/create_service/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time
from playwright.sync_api import Page, expect


def test_create_service(page: Page, context: dict) -> None:
    """
    Create a new 1-on-1 service with name, duration, and price.
    After creation, navigate to advanced edit to add a description.
    
    Prerequisites:
    - User is logged in (from category _setup)
    - Browser is on Settings > Services page (from category _setup)
    
    Saves to context:
    - created_service_id: ID of the created service
    - created_service_name: Name of the created service
    - created_service_description: Description of the service
    - created_service_duration: Duration in minutes
    - created_service_price: Price of the service
    """
    
    # Step 1: Verify on Services page
    print("  Step 1: Verifying on Services page...")
    if "/app/settings/services" not in page.url:
        raise ValueError(f"Expected to be on Services page, but URL is {page.url}")
    
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    
    # Generate unique service name
    timestamp = int(time.time())
    service_name = f"Test Consultation {timestamp}"
    service_description = "Professional consultation service for testing purposes."
    
    # Step 2: Click New Service dropdown
    print("  Step 2: Opening New service menu...")
    new_service_btn = iframe.get_by_role("button", name="New service icon-caret-down")
    new_service_btn.click()
    # Wait for dropdown menu to appear
    menu = iframe.get_by_role("menu")
    menu.wait_for(state="visible", timeout=5000)
    
    # Step 3: Select "1 on 1 appointment"
    print("  Step 3: Selecting 1 on 1 appointment...")
    one_on_one_option = iframe.get_by_role("menuitem", name="on 1 appointment")
    one_on_one_option.click()
    # Wait for dialog to appear
    dialog = iframe.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=10000)
    
    # Step 4: Fill Service Name
    print(f"  Step 4: Entering service name: {service_name}")
    name_field = iframe.get_by_role("textbox", name="Service name *")
    name_field.click()
    page.wait_for_timeout(100)  # Brief delay for field focus
    name_field.press_sequentially(service_name, delay=30)
    
    # Step 5: Select Location - Face to Face
    print("  Step 5: Selecting Face to face location...")
    face_to_face_btn = iframe.get_by_role("button", name="icon-Home Face to face")
    face_to_face_btn.click()
    # Wait for address options to appear (radiogroup)
    address_options = iframe.get_by_role("radiogroup")
    address_options.wait_for(state="visible", timeout=5000)
    
    # Step 6: Set Duration - Hours to 0
    print("  Step 6: Setting duration hours to 0...")
    hours_dropdown = iframe.get_by_role("listbox", name="Hours:")
    hours_dropdown.click()
    hours_option = iframe.get_by_role("option", name="0 Hours", exact=True)
    hours_option.wait_for(state="visible", timeout=5000)
    hours_option.click()
    
    # Step 7: Set Duration - Minutes to 30
    print("  Step 7: Setting duration minutes to 30...")
    minutes_dropdown = iframe.get_by_role("listbox", name="Minutes :")
    minutes_dropdown.click()
    minutes_option = iframe.get_by_role("option", name="30 Minutes")
    minutes_option.wait_for(state="visible", timeout=5000)
    minutes_option.click()
    
    # Step 8: Select "With fee" and Enter Price
    print("  Step 8: Setting price to 50...")
    with_fee_btn = iframe.get_by_role("button", name="icon-Credit-card With fee")
    with_fee_btn.click()
    price_field = iframe.get_by_role("spinbutton", name="Service price *")
    price_field.wait_for(state="visible", timeout=5000)
    price_field.click()
    price_field.fill("50")
    
    # Step 9: Click Create
    print("  Step 9: Clicking Create...")
    # Get reference to dialog before clicking create
    dialog = iframe.get_by_role("dialog")
    create_btn = iframe.get_by_role("button", name="Create")
    create_btn.click()
    # Wait for dialog to close (indicates creation completed)
    dialog.wait_for(state="hidden", timeout=15000)
    
    # Step 10: Refresh Services List (Workaround for UI Bug)
    print("  Step 10: Refreshing services list...")
    # BUG WORKAROUND: After service creation, the list doesn't refresh automatically
    # Navigate away and back to force a refresh
    settings_menu = page.get_by_text("Settings", exact=True)
    settings_menu.click()
    
    # Wait for Settings main page
    page.wait_for_url("**/app/settings", timeout=10000)
    
    # Navigate back to Services
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    services_btn = iframe.get_by_role("button", name="Define the services your")
    services_btn.click()
    
    # Wait for Services page to load
    page.wait_for_url("**/app/settings/services", timeout=10000)
    services_heading = iframe.get_by_role("heading", name="Settings / Services")
    services_heading.wait_for(state="visible", timeout=10000)
    
    # Step 11: Verify Service Created and Open Advanced Edit
    print("  Step 11: Verifying service was created...")
    # Wait for the service to appear in the list (should be visible after refresh)
    # Use the full service name to avoid matching other "Test Consultation" services
    service_in_list = iframe.get_by_role("button").filter(has_text=service_name)
    service_in_list.wait_for(state="visible", timeout=10000)
    
    # Click on service to open advanced edit
    service_in_list.click()
    page.wait_for_url("**/app/settings/services/**")
    
    # Wait for advanced edit page to load (Service name field visible)
    advanced_name_field = iframe.get_by_role("textbox", name="Service name *")
    advanced_name_field.wait_for(state="visible", timeout=10000)
    
    # Get service ID from URL
    url = page.url
    service_id_match = re.search(r'/services/([a-z0-9]+)', url)
    service_id = service_id_match.group(1) if service_id_match else None
    
    print(f"  [OK] Service created with ID: {service_id}")
    
    # Step 12: Add Service Description (Advanced Edit)
    print("  Step 12: Adding service description...")
    description_field = iframe.get_by_role("textbox", name="Service description (optional)")
    description_field.click()
    page.wait_for_timeout(100)  # Brief delay for field focus
    description_field.press_sequentially(service_description, delay=20)
    
    # Step 13: Save Advanced Edit
    print("  Step 13: Saving changes...")
    save_btn = iframe.get_by_role("button", name="Save")
    save_btn.click()
    # Wait for save to complete - the page refreshes, so wait for the name field to reappear
    advanced_name_field = iframe.get_by_role("textbox", name="Service name *")
    advanced_name_field.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(500)  # Brief settle time after save
    
    # Step 14: Navigate Back to Services List
    print("  Step 14: Navigating back to services list...")
    page.goto("https://app.vcita.com/app/settings/services")
    # Wait for services page to load
    services_heading = iframe.get_by_role("heading", name="Settings / Services")
    services_heading.wait_for(state="visible", timeout=15000)
    
    # Save to context
    context["created_service_id"] = service_id
    context["created_service_name"] = service_name
    context["created_service_description"] = service_description
    context["created_service_duration"] = 30
    context["created_service_price"] = 50
    
    print(f"  [OK] Successfully created service: {service_name}")
    print(f"     Service ID: {service_id}")
    print(f"     Description: {service_description}")
    print(f"     Duration: 30 minutes")
    print(f"     Price: 50")


# For standalone testing
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    import sys
    import os
    
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    sys.path.insert(0, project_root)
    
    from tests.scheduling._setup.test import setup_scheduling
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        browser_context = browser.new_context()
        page = browser_context.new_page()
        context = {}
        
        try:
            # Run setup first
            print("Running setup...")
            setup_scheduling(page, context)
            print("Setup complete!")
            
            # Run the test
            print("\nCreating service...")
            test_create_service(page, context)
            print("\n[OK] Test passed!")
            print(f"\nContext:")
            print(f"  - created_service_id: {context.get('created_service_id')}")
            print(f"  - created_service_name: {context.get('created_service_name')}")
            print(f"  - created_service_description: {context.get('created_service_description')}")
            
            # Keep browser open for inspection
            input("\nPress Enter to close browser...")
            
        except Exception as e:
            print(f"\n[FAIL] Test failed: {e}")
            page.screenshot(path="create_service_error.png")
            raise
        finally:
            browser.close()
