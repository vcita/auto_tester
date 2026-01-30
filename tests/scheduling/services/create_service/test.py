# Auto-generated from script.md
# Last updated: 2026-01-23
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
    
    # Step 1: Verify on Services page (navigate via UI if not - e.g. after Events subcategory we're on dashboard)
    print("  Step 1: Verifying on Services page...")
    if "/app/settings/services" not in page.url:
        # HEALED 2026-01-27: After Events teardown with error page recovery, we should be on dashboard.
        # Navigate via UI: Settings → Services button in iframe.
        print("  Step 1a: Not on Services page - navigating via Settings...")
        # HEALED 2026-01-27: After error page recovery, we're on dashboard. Settings should be visible.
        # Wait for page to be ready
        page.wait_for_load_state("domcontentloaded")
        
        # Find and click Settings link
        settings_link = page.get_by_text("Settings", exact=True)
        settings_link.wait_for(state="visible", timeout=30000)  # Long timeout for slow systems, continues immediately when visible
        # HEALED 2026-01-27: Ensure Settings link is actually clickable (not just visible)
        settings_link.wait_for(state="attached", timeout=10000)
        # Scroll into view if needed
        settings_link.scroll_into_view_if_needed()
        page.wait_for_timeout(200)  # Brief settle before click (allowed)
        
        # HEALED 2026-01-27: Verify current URL before clicking to understand state
        current_url_before = page.url
        print(f"  Step 1a: Current URL before Settings click: {current_url_before}")
        
        # Click Settings and wait for navigation
        settings_link.click()
        
        # HEALED 2026-01-27: Wait for navigation with multiple strategies
        # Strategy 1: Wait for URL change with domcontentloaded
        try:
            page.wait_for_url("**/app/settings**", timeout=30000, wait_until="domcontentloaded")  # Long timeout, continues immediately when URL matches
            print("  Step 1a: Successfully navigated to Settings")
        except Exception as url_error:
            # Strategy 2: Check if URL already changed (navigation might have been instant)
            page.wait_for_timeout(500)  # Brief wait for any pending navigation (allowed)
            current_url_after = page.url
            print(f"  Step 1a: URL after click: {current_url_after}")
            if "/app/settings" in current_url_after:
                print("  Step 1a: Already on settings page after click")
            else:
                # Strategy 3: Check if Settings link click opened a menu instead of navigating
                # If we're still on dashboard, Settings might be a menu that needs to be expanded
                if "/app/dashboard" in current_url_after:
                    print("  Step 1a: Still on dashboard - Settings might be a menu, trying to find Settings page link...")
                    # Try to find a Settings submenu item or direct Settings page link
                    try:
                        # Check if there's a Settings submenu that opened
                        settings_submenu = page.locator('[data-qa*="settings"], [href*="settings"]').first
                        if settings_submenu.count() > 0:
                            settings_submenu.click()
                            page.wait_for_url("**/app/settings**", timeout=30000, wait_until="domcontentloaded")
                        else:
                            raise url_error
                    except Exception:
                        raise url_error
                else:
                    raise url_error
        page.wait_for_selector('iframe[title="angularjs"]', timeout=15000)
        iframe = page.frame_locator('iframe[title="angularjs"]')
        services_button = iframe.get_by_role("button", name="Define the services your")
        services_button.wait_for(state="visible", timeout=15000)
        services_button.click()
        page.wait_for_url("**/app/settings/services**", timeout=30000, wait_until="domcontentloaded")  # Long timeout, continues immediately when URL matches

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
    price_field.fill("50")  # fill is OK for number spinbutton
    
    # Step 9: Click Create
    print("  Step 9: Clicking Create...")
    # Get reference to dialog before clicking create
    dialog = iframe.get_by_role("dialog")
    create_btn = iframe.get_by_role("button", name="Create")
    create_btn.click()
    # Wait for dialog to close (indicates creation completed)
    dialog.wait_for(state="hidden", timeout=15000)
    
    # HEALED 2026-01-27: Wait for dialog to close (indicates creation completed) instead of arbitrary timeout
    # The dialog closing is the event that indicates the service was saved
    dialog.wait_for(state="hidden", timeout=15000)
    
    # Step 10: Refresh Services List (Navigate away and back via UI)
    print("  Step 10: Refreshing services list...")
    # HEALED 2026-01-27: Replaced page.reload() with UI navigation to comply with navigation rules.
    # After service creation, navigate away and back to Services to refresh the list.
    # Navigate to Settings main page
    page.get_by_text("Settings", exact=True).click()
    page.wait_for_url("**/app/settings", timeout=10000)
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    # Navigate back to Services
    services_button = iframe.get_by_role("button", name="Define the services your")
    services_button.wait_for(state="visible", timeout=10000)
    services_button.click()
    page.wait_for_url("**/app/settings/services", timeout=10000)
    
    # Wait for Services heading to confirm page loaded
    services_heading = iframe.get_by_role("heading", name="Settings / Services")
    services_heading.wait_for(state="visible", timeout=10000)
    
    # Wait for "My Services" text to confirm list section loaded
    iframe.get_by_text("My Services").wait_for(state="visible", timeout=10000)
    
    # Step 11: Verify Service Created and Open Advanced Edit
    print("  Step 11: Verifying service was created...")
    # HEALED: Services list uses endless scroll - must scroll multiple times until end
    # Wait for "My Services" text to confirm the list section has loaded
    iframe.get_by_text("My Services").wait_for(state="visible", timeout=10000)
    
    # Scroll multiple times until no more services load (endless scroll pattern)
    # Scroll to bottom repeatedly until the service appears or we've scrolled enough times
    print("  Scrolling to load all services...")
    max_scrolls = 10
    previous_last_service_text = ""
    no_change_count = 0
    
    for scroll_attempt in range(max_scrolls):
        # First, try to find the service - if found, we're done
        # HEALED: Use get_by_text() instead of filter(has_text=...) - filter pattern doesn't work
        try:
            service_in_list = iframe.get_by_text(service_name)
            if service_in_list.count() > 0:
                print(f"  Found service after {scroll_attempt} scrolls")
                break
        except:
            pass
        
        # Get all service buttons to find the last one
        # Use a pattern that matches service buttons (not action buttons)
        all_services = iframe.get_by_role("button").filter(has_text=re.compile("Test Consultation|Appointment Test|Free estimate|Another Test|Test Debug|Test Group Workshop|Lawn mowing|On-site|MCP Test|UNIQUE TEST|SCROLL TEST"))
        
        try:
            # Get count of visible services
            service_count = all_services.count()
            
            if service_count > 0:
                # Get the last visible service and scroll it into view
                last_service = all_services.nth(service_count - 1)
                current_last_text = last_service.text_content()
                
                # If the last service text hasn't changed for 2 scrolls, we've reached the end
                if current_last_text == previous_last_service_text and previous_last_service_text != "":
                    no_change_count += 1
                    if no_change_count >= 2:
                        print(f"  Reached end of list after {scroll_attempt + 1} scrolls (no new items)")
                        break
                else:
                    no_change_count = 0
                    previous_last_service_text = current_last_text
                
                # Scroll the last service into view to trigger loading more
                last_service.scroll_into_view_if_needed()
                # Wait for new items to potentially load - check if service count increased
                # Use brief wait then check if we found the service (event-based check in loop)
                page.wait_for_timeout(300)  # Brief settle (allowed) - then check service in next iteration
            else:
                # No services found yet, scroll to "Add" button to trigger initial load
                add_button = iframe.get_by_role('button', name='Add 1 on 1 Appointment')
                add_button.scroll_into_view_if_needed()
                page.wait_for_timeout(300)  # Brief settle (allowed)
        except Exception as e:
            # If anything fails, scroll to Add button
            add_button = iframe.get_by_role('button', name='Add 1 on 1 Appointment')
            add_button.scroll_into_view_if_needed()
            page.wait_for_timeout(300)  # Brief settle (allowed)
    
    # NOW search for the specific service (all items should be loaded)
    # HEALED: Use get_by_text() instead of filter(has_text=...) - filter pattern doesn't work
    # get_by_text() correctly finds the service button even when it contains additional text
    service_in_list = iframe.get_by_text(service_name)
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
    
    # Step 14: Navigate Back to Services List (via UI, not direct URL)
    print("  Step 14: Navigating back to services list...")
    # Click Settings in sidebar to go to Settings main page
    settings_menu = page.get_by_text("Settings", exact=True)
    settings_menu.click()
    page.wait_for_url("**/app/settings", timeout=10000)
    
    # Re-acquire iframe reference after navigation
    angular_iframe = page.locator('iframe[title="angularjs"]')
    angular_iframe.wait_for(state="visible", timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    
    # Click Services button to navigate back to Services page
    services_btn = iframe.get_by_role("button", name="Define the services your")
    services_btn.click()
    page.wait_for_url("**/app/settings/services", timeout=10000)
    
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
