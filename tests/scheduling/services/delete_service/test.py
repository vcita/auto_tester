# Auto-generated from script.md
# Last updated: 2026-01-22
# Source: tests/scheduling/services/delete_service/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page, expect


def test_delete_service(page: Page, context: dict) -> None:
    """
    Delete the test service to clean up test data.
    
    Prerequisites:
    - User is logged in (from category _setup)
    - Service exists with `created_service_id` and `created_service_name` in context
    - Browser is on Settings > Services page (from edit_service test)
    
    Clears from context:
    - created_service_id
    - created_service_name
    - created_service_description
    - created_service_duration
    - created_service_price
    - edited_service_duration
    - edited_service_price
    """
    
    # Step 1: Verify on Services page
    print("  Step 1: Verifying on Services page...")
    if "/app/settings/services" not in page.url:
        raise ValueError(f"Expected to be on Services page, but URL is {page.url}")
    
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    
    # Step 2: Find and open test service edit page
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
    
    # Step 3: Wait for edit page to load
    print("  Step 3: Waiting for edit page to load...")
    heading = iframe.get_by_role("heading", name="Settings / My services / Edit Service")
    heading.wait_for(state="visible", timeout=10000)
    
    # Step 4: Click Delete button
    print("  Step 4: Clicking Delete button...")
    delete_btn = iframe.get_by_role("button", name="Delete")
    delete_btn.click()
    
    # Wait for confirmation dialog to appear
    dialog = iframe.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=5000)
    
    # Step 5: Confirm deletion
    print("  Step 5: Confirming deletion...")
    ok_btn = iframe.get_by_role("button", name="Ok")
    ok_btn.click()
    
    # Wait for dialog to close
    dialog.wait_for(state="hidden", timeout=10000)
    
    # Wait for redirect to services list
    page.wait_for_url("**/app/settings/services", timeout=15000)
    
    # Step 6: Verify service was deleted
    print("  Step 6: Verifying service was deleted...")
    
    # Wait for services list to load
    services_heading = iframe.get_by_role("heading", name="Settings / Services")
    services_heading.wait_for(state="visible", timeout=10000)
    
    # BUG WORKAROUND: Refresh list by navigating away and back (same bug as create_service)
    settings_menu = page.get_by_text("Settings", exact=True)
    settings_menu.click()
    page.wait_for_url("**/app/settings", timeout=10000)
    
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    services_btn = iframe.get_by_role("button", name="Define the services your")
    services_btn.click()
    page.wait_for_url("**/app/settings/services", timeout=10000)
    
    services_heading = iframe.get_by_role("heading", name="Settings / Services")
    services_heading.wait_for(state="visible", timeout=10000)
    
    # Verify service is no longer in the list
    service_in_list = iframe.get_by_role("button").filter(has_text=service_name)
    expect(service_in_list).to_have_count(0)
    
    print(f"  [OK] Service '{service_name}' successfully deleted")
    
    # Clear service-related context variables
    context.pop("created_service_id", None)
    context.pop("created_service_name", None)
    context.pop("created_service_description", None)
    context.pop("created_service_duration", None)
    context.pop("created_service_price", None)
    context.pop("edited_service_duration", None)
    context.pop("edited_service_price", None)
    
    print("  [OK] Context cleared")


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
    from tests.scheduling.services.edit_service.test import test_edit_service
    
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
            
            # Edit the service
            print("\nEditing service...")
            test_edit_service(page, context)
            print("Service edited!")
            
            # Run the delete test
            print("\nDeleting service...")
            test_delete_service(page, context)
            print("\n[OK] Test passed!")
            
            # Keep browser open for inspection
            input("\nPress Enter to close browser...")
            
        except Exception as e:
            print(f"\n[FAIL] Test failed: {e}")
            page.screenshot(path="delete_service_error.png")
            raise
        finally:
            browser.close()
