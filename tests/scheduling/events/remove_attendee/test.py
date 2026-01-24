# Auto-generated from script.md
# Last updated: 2026-01-24
# Source: tests/scheduling/events/remove_attendee/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
from playwright.sync_api import Page, expect


def test_remove_attendee(page: Page, context: dict) -> None:
    """
    Test: Remove Attendee
    
    Removes a client from a scheduled group event's attendee list.
    
    Prerequisites:
    - User is logged in
    - A scheduled event exists and is open (context: scheduled_event_id)
    - An attendee exists on the event (context: event_attendee_id)
    - Browser is on event detail page (from add_attendee test)
    
    Saves to context:
    - None (attendee removed)
    """
    # Step 1: Navigate to Event List and Open Event
    print("  Step 1: Navigating to Event List and opening event...")
    # If not on event detail page, navigate via Event List
    if "/app/events/" not in page.url:
        # Navigate to Calendar menu first
        calendar_menu = page.get_by_text("Calendar", exact=True)
        calendar_menu.click()
        page.wait_for_timeout(500)  # Allow menu to expand
        
        # Click Event List sub-item
        event_list_item = page.locator('[data-qa="VcMenuItem-calendar-subitem-event_list"]')
        event_list_item.wait_for(state='visible', timeout=10000)
        event_list_item.click()
        page.wait_for_url("**/app/event-list**", timeout=10000)
        page.wait_for_timeout(2000)  # Allow event list to load
        
        # Find the event with the attendee (look for "1 / 10 Registered" or similar)
        page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
        outer_iframe = page.frame_locator('iframe[title="angularjs"]')
        inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
        
        # Get service name and event ID from context to find the right event
        service_name = context.get("event_group_service_name", "")
        event_id = context.get("scheduled_event_id", "")
        
        if not service_name:
            raise ValueError("No event_group_service_name in context. Run _setup first.")
        
        # Find event by service name (most reliable)
        # Events are clickable rows in the list - look for the service name
        event_rows = inner_iframe.locator('[cursor="pointer"]').filter(has_text=service_name)
        event_count = event_rows.count()
        
        if event_count == 0:
            # Fallback: look for events showing "1 / 10 Registered" (has attendee)
            event_rows = inner_iframe.locator('[cursor="pointer"]').filter(has_text=re.compile(r'1\s*/\s*10', re.IGNORECASE))
            event_count = event_rows.count()
        
        if event_count == 0:
            raise ValueError(f"Event '{service_name}' not found in Event List")
        
        # Click the first matching event (should be the most recent one)
        event_rows.first().click()
        page.wait_for_timeout(2000)  # Allow event to open
        
        # Check if we're on event detail page or preview panel
        # If preview panel, we might need to click "View" or the event name to open full page
        if "/app/events/" not in page.url:
            # Still on event-list page - might be preview panel
            # Try clicking a "View" button or the event name again to open full page
            try:
                view_btn = inner_iframe.get_by_role('button', name=re.compile(r'View|Open', re.IGNORECASE))
                if view_btn.count() > 0:
                    view_btn.first().click()
                    page.wait_for_url("**/app/events/**", timeout=10000)
            except:
                pass
        
        # Ensure we're on the full event detail page
        page.wait_for_url("**/app/events/**", timeout=10000)
        page.wait_for_timeout(2000)  # Allow event detail page to fully load
    
    # Step 2: Navigate to Attendees Tab
    print("  Step 2: Navigating to Attendees tab...")
    # Ensure we're on the full event detail page, not just preview
    if "/app/events/" not in page.url:
        raise ValueError(f"Expected to be on event detail page after Step 1, but URL is {page.url}")
    
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    
    # Click Attendees tab - use same pattern as add_attendee test
    # Find all tabs and filter for Attendees
    all_tabs = inner_iframe.get_by_role('tab')
    tab_count = all_tabs.count()
    attendees_tab = None
    
    # Find the Attendees tab by checking text content
    for i in range(tab_count):
        tab = all_tabs.nth(i)
        tab_text = tab.text_content() or ""
        if 'Attendees' in tab_text:
            attendees_tab = tab
            break
    
    if not attendees_tab:
        raise ValueError("Attendees tab not found")
    
    attendees_tab.wait_for(state='visible', timeout=10000)
    attendees_tab.click()
    page.wait_for_timeout(500)  # Allow tab content to load
    
    # Step 3: Find Attendee in List
    print("  Step 3: Finding attendee in list...")
    # Get client name from context
    client_name = context.get("event_client_name")
    if not client_name:
        raise ValueError("No event_client_name in context. Run _setup first.")
    
    # Wait for attendees list to load - wait for the tab content
    # Wait for the attendees list to actually appear
    try:
        # Wait for either "Not paid" or "Paid" section to appear (indicates list loaded)
        # Use filter(has_text) instead of get_by_text with exact=False
        inner_iframe.locator('*').filter(has_text="Not paid").first().wait_for(state='visible', timeout=10000)
        page.wait_for_timeout(2000)  # Additional wait for list items to render
    except:
        try:
            inner_iframe.locator('*').filter(has_text="Paid").first().wait_for(state='visible', timeout=10000)
            page.wait_for_timeout(2000)
        except:
            # If neither section appears, wait a bit more and continue
            page.wait_for_timeout(3000)
    
    # Find the attendee in the list
    # Based on MCP: get_by_text works in JavaScript with exact=False
    # In Python Playwright, use filter(has_text=...) for partial matching
    # Re-establish iframe references to ensure they're fresh
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    
    attendee_item = None
    attendee_count = 0
    
    # Strategy 1: Use get_by_text - try exact match first
    # Based on MCP: get_by_text works in JavaScript with exact=False
    # In Python Playwright, get_by_text without parameters does exact match
    # Since client_name should match exactly, this should work
    page.wait_for_timeout(1000)
    try:
        attendee_items = inner_iframe.get_by_text(client_name)
        attendee_count = attendee_items.count()
        if attendee_count > 0:
            attendee_item = attendee_items.first()
            print(f"  Found attendee using get_by_text: {attendee_count} matches")
    except Exception as e:
        print(f"  get_by_text failed: {type(e).__name__}: {str(e)}")
        attendee_count = 0
    
    # Strategy 2: Use locator with filter(has_text) - for partial matching
    # This is the Python Playwright way to do partial text matching
    if attendee_count == 0:
        try:
            # Try with generic locator - filter will find elements containing the text
            attendee_items = inner_iframe.locator('*').filter(has_text=client_name)
            attendee_count = attendee_items.count()
            if attendee_count > 0:
                attendee_item = attendee_items.first()
                print(f"  Found attendee using filter(has_text): {attendee_count} matches")
        except Exception as e:
            print(f"  Filter has_text failed: {type(e).__name__}: {str(e)}")
    
    # Strategy 3: Try finding by partial name match (last part)
    if attendee_count == 0:
        try:
            # Extract last name part (after "Event ")
            name_parts = client_name.split()
            if len(name_parts) > 1:
                last_part = name_parts[-1]  # e.g., "TestClient1769275425"
                attendee_items = inner_iframe.get_by_text(last_part)
                attendee_count = attendee_items.count()
                if attendee_count > 0:
                    attendee_item = attendee_items.first()
                    print(f"  Found attendee using partial name get_by_text: {attendee_count} matches")
        except Exception as e:
            print(f"  Partial name get_by_text failed: {type(e).__name__}: {str(e)}")
    
    if attendee_count == 0 or not attendee_item:
        raise ValueError(f"Attendee '{client_name}' not found in attendees list after trying multiple search strategies")
    
    attendee_item.wait_for(state='visible', timeout=10000)
    
    # Step 4: Click 3 Dots Menu and Select "Cancel Registration"
    print("  Step 4: Clicking 3 dots menu and selecting Cancel Registration...")
    # The remove action is in a 3 dots menu on the registrant name
    # IMPORTANT: Buttons are only visible when hovering over the attendee name
    # First, hover over the attendee name to reveal the buttons
    attendee_item.hover()
    page.wait_for_timeout(1500)  # Wait for buttons to appear after hover
    
    # Find the 3 dots menu button near the attendee
    # Based on MCP exploration: The 3-dots button is in the same container as the attendee
    # The attendee text is at level 0, parent container (attendance-item) is at level 2
    # Strategy: Find button with both "three-dots" AND "activator-container" classes
    # MCP verified: go up 2 levels from attendee text to find container with buttons
    menu_btn = None
    
    # Find the attendee's parent container - go up 2 levels (verified with MCP)
    attendee_container = attendee_item.locator('xpath=ancestor::*[position()=2]')
    container_count = attendee_container.count()
    
    if container_count == 0:
        # Fallback: try attendance-item class
        attendee_container = attendee_item.locator('xpath=ancestor::*[contains(@class, "attendance-item")][1]')
        container_count = attendee_container.count()
    
    if container_count == 0:
        raise ValueError(f"Could not find attendee container for '{client_name}'")
    
    # Look for all buttons in the container
    buttons = attendee_container.locator('button')
    btn_count = buttons.count()
    
    # Check each button to find the 3 dots menu (NOT the bill/payment icon)
    # MCP verified: button must have BOTH "three-dots" AND "activator-container" classes
    for i in range(btn_count):
        try:
            btn = buttons.nth(i)
            btn_class = btn.get_attribute('class') or ""
            
            # Skip bill/payment icon
            is_bill_icon = "take-payment-button" in btn_class
            if is_bill_icon:
                continue
            
            # 3 dots menu: must have BOTH "three-dots" AND "activator-container" classes
            has_three_dots = "three-dots" in btn_class
            has_activator = "activator-container" in btn_class
            
            if has_three_dots and has_activator:
                menu_btn = btn
                break
        except:
            continue
    
    if not menu_btn:
        raise ValueError(f"3 dots menu button not found for attendee '{client_name}'. Button must have both 'three-dots' and 'activator-container' classes.")
    
    # Click the 3 dots menu button
    # Use evaluate to force-click and scroll into view (handles visibility issues)
    # Based on MCP: button is visible after hover, but use evaluate for reliability
    menu_btn.evaluate("""
        (el) => {
            el.scrollIntoView({ behavior: 'instant', block: 'center' });
            el.click();
        }
    """)
    page.wait_for_timeout(2000)  # Wait for menu to appear
    
    # Step 4a: Click "Cancel Registration" option in the menu
    print("  Step 4a: Clicking Cancel Registration option...")
    # Look for the menu that appeared - it might be in the iframe or in the document
    menu = None
    menu_found = False
    
    # Try inner iframe first
    try:
        menu = inner_iframe.get_by_role('menu')
        if menu.count() > 0:
            menu.first().wait_for(state='visible', timeout=3000)
            menu_found = True
    except:
        pass
    
    # If not found in inner iframe, try outer iframe
    if not menu_found:
        try:
            menu = outer_iframe.get_by_role('menu')
            if menu.count() > 0:
                menu.first().wait_for(state='visible', timeout=3000)
                menu_found = True
        except:
            pass
    
    # If still not found, try document
    if not menu_found:
        try:
            menu = page.get_by_role('menu')
            if menu.count() > 0:
                menu.first().wait_for(state='visible', timeout=3000)
                menu_found = True
        except:
            pass
    
    if not menu_found or menu is None or menu.count() == 0:
        raise ValueError("Menu did not appear after clicking 3 dots button")
    
    # Find "Cancel Registration" option in the menu
    # Use the first menu if multiple found
    menu_to_use = menu.first() if menu.count() > 0 else menu
    
    # Based on MCP: menu item text is "Cancel registration" (lowercase 'r')
    cancel_option = menu_to_use.get_by_text(re.compile(r'Cancel.*[Rr]egistration', re.IGNORECASE))
    if cancel_option.count() == 0:
        # Try exact match with lowercase
        # Use filter for partial matching instead of exact=False
        cancel_option = menu_to_use.locator('*').filter(has_text='Cancel registration')
    
    if cancel_option.count() == 0:
        raise ValueError("'Cancel registration' option not found in menu")
    
    cancel_option.first().wait_for(state='visible', timeout=5000)
    cancel_option.first().click()
    page.wait_for_timeout(2000)  # Wait for confirmation dialog to appear
    
    # Step 5: Submit Confirmation Dialog
    print("  Step 5: Submitting confirmation dialog...")
    # Based on MCP: After clicking "Cancel registration", a dialog appears with "Submit" button
    # The dialog is in the outer iframe (not inner)
    page.wait_for_timeout(1000)  # Wait for dialog to appear
    
    # Look for Submit button in outer iframe first (where dialog appears)
    confirmation_clicked = False
    try:
        submit_btn = outer_iframe.get_by_role('button', name='Submit')
        if submit_btn.count() > 0:
            submit_btn.first().wait_for(state='visible', timeout=5000)
            submit_btn.first().click()
            confirmation_clicked = True
            page.wait_for_timeout(2000)
    except:
        pass
    
    # Also try in main page
    if not confirmation_clicked:
        try:
            submit_btn = page.get_by_role('button', name='Submit')
            if submit_btn.count() > 0:
                submit_btn.first().wait_for(state='visible', timeout=5000)
                submit_btn.first().click()
                confirmation_clicked = True
                page.wait_for_timeout(2000)
        except:
            pass
    
    # Fallback: try alternative button names
    if not confirmation_clicked:
        for confirm_text in ['Confirm', 'Yes', 'Remove', 'Delete', 'OK']:
            try:
                confirm_btn = outer_iframe.get_by_role('button', name=confirm_text)
                if confirm_btn.count() > 0:
                    confirm_btn.first().wait_for(state='visible', timeout=2000)
                    confirm_btn.first().click()
                    confirmation_clicked = True
                    page.wait_for_timeout(2000)
                    break
            except:
                continue
    
    # Step 6: Verify Attendee Removed
    print("  Step 6: Verifying attendee was removed...")
    # Wait for list to update after removal
    page.wait_for_timeout(3000)  # Allow list to refresh
    
    # Verify attendee is no longer in the list
    # Re-query to get fresh locator
    attendee_items = inner_iframe.get_by_text(client_name)
    attendee_count = attendee_items.count()
    
    if attendee_count > 0:
        # Attendee still exists - removal might have failed or needs more time
        page.wait_for_timeout(2000)  # Wait a bit more
        attendee_count = attendee_items.count()
    
    if attendee_count > 0:
        raise ValueError(f"Attendee '{client_name}' was not removed. Still found {attendee_count} instance(s).")
    
    # Verify attendees count decreased
    attendees_tab = inner_iframe.get_by_role('tab', name=re.compile(r'Attendees'))
    attendees_count_text = attendees_tab.first().text_content()
    # Should show "Attendees (0)" or decreased count
    
    print(f"  [OK] Attendee removed successfully")
    print(f"       Attendees tab: {attendees_count_text}")
