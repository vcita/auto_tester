# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/_functions/delete_service/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page, expect


def fn_delete_service(page: Page, context: dict, **params) -> None:
    """
    Delete a service by its name from the Services list.
    
    Used for test teardown to clean up test data.
    
    Parameters:
    - name (required): Name of the service to delete
    
    Clears from context:
    - created_service_id
    - created_service_name
    """
    name = params.get("name")
    if not name:
        # Try to get from context
        name = context.get("created_service_name")
    
    if not name:
        raise ValueError("Service name is required for deletion")
    
    # Step 1: Navigate to Settings
    print("  Step 1: Navigating to Settings...")
    page.get_by_text('Settings').click()
    page.wait_for_url("**/app/settings", timeout=10000)
    
    # Step 2: Click Services button
    print("  Step 2: Opening Services section...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    iframe.get_by_role('button', name='Define the services your').click()
    page.wait_for_url("**/app/settings/services", timeout=10000)
    
    # Step 3: Click on Service in List
    print(f"  Step 3: Finding service: {name}")
    service_in_list = iframe.get_by_role('button').filter(has_text=name)
    service_in_list.wait_for(state='visible', timeout=10000)
    service_in_list.click()
    page.wait_for_url("**/app/settings/services/**", timeout=10000)
    
    # Step 4: Click Delete Button
    print("  Step 4: Clicking Delete button...")
    delete_btn = iframe.get_by_role('button', name='Delete')
    delete_btn.click()
    dialog = iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=5000)
    
    # Step 5: Confirm Deletion
    print("  Step 5: Confirming deletion...")
    ok_btn = iframe.get_by_role('button', name='Ok')
    ok_btn.click()
    page.wait_for_url("**/app/settings/services", timeout=10000)
    
    # Step 6: Verify Service Removed
    print("  Step 6: Verifying service was deleted...")
    services_heading = iframe.get_by_role('heading', name='Settings / Services')
    services_heading.wait_for(state='visible', timeout=10000)
    
    # Verify service is no longer in the list
    service_in_list = iframe.get_by_role('button').filter(has_text=name)
    expect(service_in_list).to_have_count(0)
    
    # Clear from context
    if "created_service_id" in context:
        del context["created_service_id"]
    if "created_service_name" in context:
        del context["created_service_name"]
    
    print(f"  [OK] Successfully deleted service: {name}")
