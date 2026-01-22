# Auto-generated from script.md
# Last updated: 2026-01-22
# Source: tests/scheduling/services/edit_service/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page, expect


def test_edit_service(page: Page, context: dict) -> None:
    """
    Edit an existing service to modify duration (30->45 min) and price (50->75).
    
    Prerequisites:
    - User is logged in (from category _setup)
    - Service exists with `created_service_id` and `created_service_name` in context
    - Browser is on Settings > Services page (from create_service test)
    
    Saves to context:
    - edited_service_duration: New duration (45 minutes)
    - edited_service_price: New price (75)
    """
    
    # Step 1: Verify on Services page
    print("  Step 1: Verifying on Services page...")
    if "/app/settings/services" not in page.url:
        raise ValueError(f"Expected to be on Services page, but URL is {page.url}")
    
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    
    # Step 2: Find and click on test service
    print("  Step 2: Finding and opening test service...")
    service_name = context.get("created_service_name")
    if not service_name:
        raise ValueError("created_service_name not found in context - run create_service first")
    
    # Locate service in list and hover to reveal edit button
    service_row = iframe.get_by_role("button").filter(has_text=service_name)
    service_row.hover()
    
    # Wait for edit button to appear and click it
    edit_btn = iframe.get_by_role("button", name="icon-pencil-s")
    edit_btn.wait_for(state="visible", timeout=5000)
    edit_btn.click()
    
    # Wait for edit page to load
    page.wait_for_url("**/app/settings/services/**")
    
    # Step 3: Wait for edit form to load
    print("  Step 3: Waiting for edit form to load...")
    heading = iframe.get_by_role("heading", name="Settings / My services / Edit Service")
    heading.wait_for(state="visible", timeout=10000)
    
    name_field = iframe.get_by_role("textbox", name="Service name *")
    name_field.wait_for(state="visible", timeout=10000)
    
    # Step 4: Change duration from 30 to 45 minutes
    print("  Step 4: Changing duration to 45 minutes...")
    minutes_dropdown = iframe.get_by_role("listbox", name="Minutes :")
    minutes_dropdown.click()
    
    minutes_option = iframe.get_by_role("option", name="45 Minutes")
    minutes_option.wait_for(state="visible", timeout=5000)
    minutes_option.click()
    
    # Step 5: Change price from 50 to 75
    print("  Step 5: Changing price to 75...")
    price_field = iframe.get_by_role("spinbutton", name="Service price")
    price_field.click()
    price_field.fill("")  # Clear existing value
    price_field.fill("75")
    
    # Step 6: Save changes
    print("  Step 6: Saving changes...")
    save_btn = iframe.get_by_role("button", name="Save")
    save_btn.click()
    
    # Wait for save to complete - heading reappears after page refresh
    heading = iframe.get_by_role("heading", name="Settings / My services / Edit Service")
    heading.wait_for(state="visible", timeout=15000)
    
    # Step 7: Verify changes were saved
    print("  Step 7: Verifying changes were saved...")
    # Small delay to ensure form values are populated after refresh
    page.wait_for_timeout(500)
    
    minutes_dropdown = iframe.get_by_role("listbox", name="Minutes :")
    expect(minutes_dropdown).to_contain_text("45 Minutes")
    
    price_field = iframe.get_by_role("spinbutton", name="Service price")
    expect(price_field).to_have_value("75")
    
    print("  [OK] Changes verified: 45 minutes, price 75")
    
    # Step 8: Navigate back to Services list
    print("  Step 8: Navigating back to services list...")
    page.goto("https://app.vcita.com/app/settings/services")
    
    # Wait for services page to load
    services_heading = iframe.get_by_role("heading", name="Settings / Services")
    services_heading.wait_for(state="visible", timeout=15000)
    
    # Save to context
    context["edited_service_duration"] = 45
    context["edited_service_price"] = 75
    
    print(f"  [OK] Successfully edited service: {service_name}")
    print(f"     New duration: 45 minutes")
    print(f"     New price: 75")


# For standalone testing
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    import sys
    import os
    
    # Add project root to path
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    sys.path.insert(0, project_root)
    
    from tests.scheduling._setup.test import setup_scheduling
    from tests.scheduling.services.create_service.test import test_create_service
    
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
            
            # Create a service first
            print("\nCreating service...")
            test_create_service(page, context)
            print("Service created!")
            
            # Run the edit test
            print("\nEditing service...")
            test_edit_service(page, context)
            print("\n[OK] Test passed!")
            
            # Keep browser open for inspection
            input("\nPress Enter to close browser...")
            
        except Exception as e:
            print(f"\n[FAIL] Test failed: {e}")
            page.screenshot(path="edit_service_error.png")
            raise
        finally:
            browser.close()
