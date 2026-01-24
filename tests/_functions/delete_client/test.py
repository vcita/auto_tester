# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/_functions/delete_client/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page, expect


def fn_delete_client(page: Page, context: dict, **params) -> None:
    """
    Delete a client (matter/property) by navigating to their detail page.
    
    Used for test teardown to clean up test data.
    
    Parameters:
    - name (optional): Name of the client to delete (defaults to context value)
    - id (optional): ID of the client to delete (defaults to context value)
    
    Clears from context:
    - created_client_id
    - created_client_name
    - created_client_email
    """
    name = params.get("name")
    client_id = params.get("id")
    
    # Try to get from context if not provided
    if not name:
        name = context.get("created_client_name")
    if not client_id:
        client_id = context.get("created_client_id")
    
    if not name:
        raise ValueError("Client name is required for deletion")
    
    # Step 1: Navigate to Properties List
    print("  Step 1: Navigating to Properties list...")
    # Ensure we're on a vcita page first
    if "vcita.com" not in page.url:
        page.goto("https://app.vcita.com/app/dashboard")
        page.wait_for_load_state("domcontentloaded")
    
    properties_menu = page.get_by_text('Properties').first
    properties_menu.wait_for(state='visible', timeout=10000)
    properties_menu.click()
    page.wait_for_url("**/app/clients", timeout=10000)
    
    # Wait for the page to load
    page.wait_for_timeout(1000)
    
    # Step 2: Search for Client
    print(f"  Step 2: Searching for client: {name}")
    search_field = page.get_by_role('searchbox', name='Search by name, email, or phone number')
    search_field.click()
    page.wait_for_timeout(100)
    search_field.press_sequentially(name, delay=30)
    page.wait_for_timeout(1000)  # Allow search results to update
    
    # Step 3: Click on Client in List
    print("  Step 3: Opening client detail page...")
    client_row = page.get_by_role('row').filter(has_text=name)
    client_row.wait_for(state='visible', timeout=5000)
    client_row.click()
    page.wait_for_url("**/app/clients/**", timeout=10000)
    
    # Step 4: Click More Dropdown
    print("  Step 4: Opening More menu...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    more_btn = iframe.get_by_role('button', name='More icon-caret-down')
    more_btn.wait_for(state='visible', timeout=10000)
    more_btn.click()
    menu = iframe.get_by_role('menu')
    menu.wait_for(state='visible', timeout=5000)
    
    # Step 5: Select Delete Property
    print("  Step 5: Clicking Delete property...")
    delete_option = iframe.get_by_role('menuitem', name='Delete property')
    delete_option.click()
    dialog = iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=5000)
    
    # Step 6: Confirm Deletion
    print("  Step 6: Confirming deletion...")
    ok_btn = iframe.get_by_role('button', name='Ok')
    ok_btn.click()
    
    # Wait for redirect to Properties list - the URL should not have a client ID
    # Use a more flexible wait - just wait for dialog to close and page to stabilize
    dialog.wait_for(state='hidden', timeout=10000)
    page.wait_for_timeout(2000)  # Allow page to stabilize
    
    # Clear from context
    if "created_client_id" in context:
        del context["created_client_id"]
    if "created_client_name" in context:
        del context["created_client_name"]
    if "created_client_email" in context:
        del context["created_client_email"]
    
    print(f"  [OK] Successfully deleted client: {name}")
