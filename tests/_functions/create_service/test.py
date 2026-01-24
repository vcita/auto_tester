# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/_functions/create_service/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
import time
from playwright.sync_api import Page, expect


def fn_create_service(page: Page, context: dict, **params) -> None:
    """
    Create a minimal 1-on-1 service for test setup purposes.
    
    Creates a free service with Face to Face location and default 1 hour duration.
    
    Parameters:
    - name (required): Name of the service to create (should include timestamp for uniqueness)
    
    Saves to context:
    - created_service_id: ID of the created service
    - created_service_name: Name of the service
    """
    name = params.get("name")
    if not name:
        timestamp = int(time.time())
        name = f"Test Service {timestamp}"
    
    # Step 1: Navigate to Settings
    print("  Step 1: Navigating to Settings...")
    # First ensure we're on a vcita page and sidebar is loaded
    if "vcita.com" not in page.url:
        page.goto("https://app.vcita.com/app/dashboard")
        page.wait_for_load_state("domcontentloaded")
    
    # Wait for sidebar to be available
    settings_menu = page.get_by_text('Settings')
    settings_menu.wait_for(state='visible', timeout=30000)
    settings_menu.click()
    page.wait_for_url("**/app/settings", timeout=10000)
    
    # Step 2: Click Services button
    print("  Step 2: Opening Services section...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    iframe.get_by_role('button', name='Define the services your').click()
    page.wait_for_url("**/app/settings/services", timeout=10000)
    
    # Step 3: Click New Service dropdown
    print("  Step 3: Opening New service menu...")
    new_service_btn = iframe.get_by_role('button', name='New service icon-caret-down')
    new_service_btn.click()
    menu = iframe.get_by_role('menu')
    menu.wait_for(state='visible', timeout=5000)
    
    # Step 4: Select 1 on 1 appointment
    print("  Step 4: Selecting 1 on 1 appointment...")
    one_on_one_option = iframe.get_by_role('menuitem', name='on 1 appointment')
    one_on_one_option.click()
    dialog = iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=10000)
    
    # Step 5: Enter Service Name
    print(f"  Step 5: Entering service name: {name}")
    name_field = iframe.get_by_role('textbox', name='Service name *')
    name_field.click()
    page.wait_for_timeout(100)
    name_field.press_sequentially(name, delay=30)
    
    # Step 6: Select Face to Face Location
    print("  Step 6: Selecting Face to face location...")
    face_to_face_btn = iframe.get_by_role('button', name='icon-Home Face to face')
    face_to_face_btn.click()
    # Address radio group appears - "My business address" is selected by default
    
    # Step 7: Select No Fee (Free Service)
    print("  Step 7: Selecting No fee pricing...")
    no_fee_btn = iframe.get_by_role('button', name='No fee')
    no_fee_btn.click()
    
    # Step 8: Click Create Button
    print("  Step 8: Clicking Create...")
    dialog = iframe.get_by_role('dialog')
    create_btn = iframe.get_by_role('button', name='Create')
    create_btn.click()
    dialog.wait_for(state='hidden', timeout=15000)
    
    # Step 9: Refresh Services List (BUG WORKAROUND)
    print("  Step 9: Refreshing services list...")
    settings_menu = page.get_by_text('Settings', exact=True)
    settings_menu.click()
    page.wait_for_url("**/app/settings", timeout=10000)
    
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state='visible', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    services_btn = iframe.get_by_role('button', name='Define the services your')
    services_btn.click()
    page.wait_for_url("**/app/settings/services", timeout=10000)
    
    # Step 10: Click on Service to Get ID
    print("  Step 10: Verifying service was created...")
    # CRITICAL: Handle virtual scrolling - scroll to bottom of list first
    # New services appear at the bottom and may not be rendered until scrolled into view
    add_service_btn = iframe.get_by_role('button', name='Add 1 on 1 Appointment')
    add_service_btn.scroll_into_view_if_needed()
    page.wait_for_timeout(500)  # Allow list to render
    
    service_in_list = iframe.get_by_role('button').filter(has_text=name)
    service_in_list.wait_for(state='visible', timeout=10000)
    service_in_list.click()
    page.wait_for_url("**/app/settings/services/**", timeout=10000)
    
    # Step 11: Extract Service ID from URL
    url = page.url
    service_id_match = re.search(r'/services/([a-z0-9]+)', url)
    service_id = service_id_match.group(1) if service_id_match else None
    
    print(f"  [OK] Service created with ID: {service_id}")
    
    # Step 12: Navigate Back to Services List
    print("  Step 12: Navigating back to services list...")
    settings_menu = page.get_by_text('Settings', exact=True)
    settings_menu.click()
    page.wait_for_url("**/app/settings", timeout=10000)
    
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state='visible', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    services_btn = iframe.get_by_role('button', name='Define the services your')
    services_btn.click()
    page.wait_for_url("**/app/settings/services", timeout=10000)
    
    services_heading = iframe.get_by_role('heading', name='Settings / Services')
    services_heading.wait_for(state='visible', timeout=10000)
    
    # Save to context
    context["created_service_id"] = service_id
    context["created_service_name"] = name
    
    print(f"  [OK] Successfully created service: {name}")
    print(f"       Service ID: {service_id}")
