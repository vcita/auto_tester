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
        event_rows.first.click()
        page.wait_for_timeout(2000)  # Allow event to open
        
        # Check if we're on event detail page or preview panel
        # If preview panel, we might need to click "View" or the event name to open full page
        if "/app/events/" not in page.url:
            # Still on event-list page - might be preview panel
            # Try clicking a "View" button or the event name again to open full page
            try:
                view_btn = inner_iframe.get_by_role('button', name=re.compile(r'View|Open', re.IGNORECASE))
                if view_btn.count() > 0:
                    view_btn.first.click()
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
    
    # Wait for tab bar to be ready (inner iframe may load after navigation)
    inner_iframe.get_by_role('tab').first.wait_for(state='visible', timeout=15000)
    page.wait_for_timeout(500)
    
    # Click Attendees: try button name (e.g. "Attendees (0)" or "Attendees (1)"), then tab, then text
    attendees_btn = inner_iframe.get_by_role('button', name=re.compile(r'Attendees\s*\(\d+\)', re.IGNORECASE))
    if attendees_btn.count() > 0:
        attendees_btn.first.scroll_into_view_if_needed(timeout=5000)
        try:
            attendees_btn.first.click(timeout=10000)
        except Exception:
            # Element may be covered (e.g. panel transition); force click
            attendees_btn.first.click(force=True, timeout=5000)
    else:
        attendees_tab = inner_iframe.get_by_role('tab', name=re.compile(r'Attendees', re.IGNORECASE))
        if attendees_tab.count() > 0:
            attendees_tab.first.scroll_into_view_if_needed(timeout=5000)
            try:
                attendees_tab.first.click(timeout=10000)
            except Exception:
                attendees_tab.first.click(force=True, timeout=5000)
        else:
            # Last resort: click by text (tab or button with "Attendees")
            by_text = inner_iframe.get_by_text(re.compile(r'Attendees\s*\(\d+\)', re.IGNORECASE))
            if by_text.count() == 0:
                raise ValueError("Attendees tab not found")
            by_text.first.scroll_into_view_if_needed(timeout=5000)
            by_text.first.click(force=True, timeout=5000)
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
        inner_iframe.locator('*').filter(has_text="Not paid").first.wait_for(state='visible', timeout=10000)
        page.wait_for_timeout(2000)  # Additional wait for list items to render
    except:
        try:
            inner_iframe.locator('*').filter(has_text="Paid").first.wait_for(state='visible', timeout=10000)
            page.wait_for_timeout(2000)
        except:
            # If neither section appears, wait a bit more and continue
            page.wait_for_timeout(3000)
    
    # Re-establish iframe references to ensure they're fresh
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    
    # Find the attendee in the list - get_by_text works reliably (verified in MCP)
    attendee_item = inner_iframe.get_by_text(client_name)
    page.wait_for_timeout(2000)  # Allow list to render
    if attendee_item.count() == 0:
        raise ValueError(
            f"No attendee '{client_name}' in list. Add Attendee may not have completed "
            "(e.g. event has fee — check for payment/skip dialog after Continue)."
        )
    attendee_item.first.wait_for(state='visible', timeout=8000)
    
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
    # IMPORTANT: Re-establish iframe references right before looking for menu
    # This ensures they're fresh and not stale
    print("  [DEBUG] Re-establishing iframe references...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    # Wait a bit for iframe content to be ready
    page.wait_for_timeout(500)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    print("  [DEBUG] Iframe references established")
    
    # Instead of looking for the menu role, wait for the "Cancel registration" menu item directly
    # MCP inspection showed: menu items are DIV elements with class "v-list-item" and role="menuitem"
    # Use get_by_text which is more reliable than get_by_role for nested iframes
    cancel_option = None
    menu_found = False
    
    # DEBUG: Check if menu exists by role first
    print("  [DEBUG] Checking for menu by role in inner_iframe...")
    try:
        menu_by_role = inner_iframe.get_by_role('menu')
        menu_count = menu_by_role.count()
        print(f"  [DEBUG] Menu by role count in inner_iframe: {menu_count}")
        if menu_count > 0:
            menu_info = menu_by_role.first
            try:
                menu_class = menu_info.get_attribute('class')
                print(f"  [DEBUG] Menu class: {menu_class}")
            except:
                print("  [DEBUG] Could not get menu class")
    except Exception as e:
        print(f"  [DEBUG] Error checking menu by role: {e}")
    
    # Try inner iframe first - use get_by_text (most reliable for nested iframes)
    print("  [DEBUG] Trying inner_iframe.get_by_text('Cancel registration')...")
    try:
        cancel_option = inner_iframe.get_by_text('Cancel registration')
        # Poll until menu item appears (check count every 500ms, up to 5 seconds)
        count = 0
        for attempt in range(10):
            count = cancel_option.count()
            print(f"  [DEBUG] Attempt {attempt + 1}/10: cancel_option.count() = {count}")
            if count > 0:
                break
            page.wait_for_timeout(500)  # Wait 500ms between checks
        
        print(f"  [DEBUG] Final count after polling: {count}")
        if count > 0:
            # Menu item exists - click will auto-wait for it to be actionable
            print("  [DEBUG] Menu item found (count > 0), will click directly")
            menu_found = True
        else:
            print("  [DEBUG] Menu item count is still 0 after polling")
    except Exception as e:
        print(f"  [DEBUG] Exception in inner_iframe.get_by_text: {type(e).__name__}: {e}")
        # Try alternative: use locator with filter for partial match
        print("  [DEBUG] Trying alternative: locator('*').filter(has_text='Cancel registration')...")
        try:
            cancel_option = inner_iframe.locator('*').filter(has_text='Cancel registration')
            count = 0
            for attempt in range(10):
                count = cancel_option.count()
                print(f"  [DEBUG] Filter attempt {attempt + 1}/10: count = {count}")
                if count > 0:
                    break
                page.wait_for_timeout(500)
            print(f"  [DEBUG] Filter final count: {count}")
            if count > 0:
                menu_found = True
                print("  [DEBUG] Menu item found using filter!")
        except Exception as e2:
            print(f"  [DEBUG] Exception in filter approach: {type(e2).__name__}: {e2}")
    
    # If not found in inner iframe, try outer iframe (using get_by_text)
    if not menu_found:
        print("  [DEBUG] Trying outer_iframe.get_by_text('Cancel registration')...")
        try:
            cancel_option = outer_iframe.get_by_text('Cancel registration')
            count = 0
            for attempt in range(10):
                count = cancel_option.count()
                print(f"  [DEBUG] Outer iframe attempt {attempt + 1}/10: count = {count}")
                if count > 0:
                    break
                page.wait_for_timeout(500)
            print(f"  [DEBUG] Outer iframe final count: {count}")
            if count > 0:
                menu_found = True
                print("  [DEBUG] Menu item found in outer_iframe!")
        except Exception as e:
            print(f"  [DEBUG] Exception in outer_iframe: {type(e).__name__}: {e}")
    
    # If still not found, try document (using get_by_text)
    if not menu_found:
        print("  [DEBUG] Trying page.get_by_text('Cancel registration')...")
        try:
            cancel_option = page.get_by_text('Cancel registration')
            count = 0
            for attempt in range(10):
                count = cancel_option.count()
                print(f"  [DEBUG] Document attempt {attempt + 1}/10: count = {count}")
                if count > 0:
                    break
                page.wait_for_timeout(500)
            print(f"  [DEBUG] Document final count: {count}")
            if count > 0:
                menu_found = True
                print("  [DEBUG] Menu item found in document!")
        except Exception as e:
            print(f"  [DEBUG] Exception in document: {type(e).__name__}: {e}")
    
    # DEBUG: Try to inspect DOM structure using evaluate
    if not menu_found:
        print("  [DEBUG] Menu not found - inspecting DOM structure...")
        try:
            dom_info = page.evaluate("""
                () => {
                    const outerIframe = document.querySelector('iframe[title="angularjs"]');
                    if (!outerIframe || !outerIframe.contentDocument) return {error: 'outer iframe not accessible'};
                    
                    const innerIframe = outerIframe.contentDocument.querySelector('#vue_iframe_layout');
                    if (!innerIframe || !innerIframe.contentDocument) return {error: 'inner iframe not accessible'};
                    
                    const innerDoc = innerIframe.contentDocument;
                    
                    // Find menu
                    const menu = innerDoc.querySelector('[role="menu"]');
                    const menuInfo = menu ? {
                        found: true,
                        tagName: menu.tagName,
                        className: menu.className,
                        id: menu.id,
                        visible: menu.offsetParent !== null
                    } : {found: false};
                    
                    // Find "Cancel registration" text
                    const allElements = innerDoc.querySelectorAll('*');
                    const cancelElements = Array.from(allElements).filter(el => 
                        el.textContent && el.textContent.includes('Cancel registration')
                    );
                    
                    return {
                        menu: menuInfo,
                        cancelElementsCount: cancelElements.length,
                        cancelElements: cancelElements.slice(0, 3).map(el => ({
                            tagName: el.tagName,
                            className: el.className,
                            role: el.getAttribute('role'),
                            visible: el.offsetParent !== null,
                            textContent: el.textContent?.trim().substring(0, 50)
                        }))
                    };
                }
            """)
            print(f"  [DEBUG] DOM inspection result: {dom_info}")
        except Exception as e:
            print(f"  [DEBUG] Error inspecting DOM: {type(e).__name__}: {e}")
    
    if not menu_found or cancel_option is None or cancel_option.count() == 0:
        raise ValueError("'Cancel registration' menu item did not appear after clicking 3 dots button")
    
    # We found the cancel option, now click it
    # IMPORTANT: first is a property, not a method - use .first.click() not .first().click()
    cancel_option.first.click()
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
            submit_btn.first.wait_for(state='visible', timeout=5000)
            submit_btn.first.click()
            confirmation_clicked = True
            page.wait_for_timeout(2000)
    except:
        pass
    
    # Also try in main page
    if not confirmation_clicked:
        try:
            submit_btn = page.get_by_role('button', name='Submit')
            if submit_btn.count() > 0:
                submit_btn.first.wait_for(state='visible', timeout=5000)
                submit_btn.first.click()
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
                    confirm_btn.first.wait_for(state='visible', timeout=2000)
                    confirm_btn.first.click()
                    confirmation_clicked = True
                    page.wait_for_timeout(2000)
                    break
            except:
                continue
    
    # Step 6: Verify Attendee Removed
    print("  Step 6: Verifying attendee was removed...")
    # Wait for list to update after removal
    page.wait_for_timeout(3000)  # Allow list to refresh
    
    # IMPORTANT: We validate removal by checking BOTH:
    # 1. The attendees count is 0 (attendee no longer counted as active)
    # 2. The attendee shows "Canceled by" indicator (confirms it's in canceled state)
    # Both conditions must be true for removal to be confirmed
    
    # Step 6a: Verify attendees count is 0
    attendees_tab = inner_iframe.get_by_role('tab', name=re.compile(r'Attendees'))
    attendees_count_text = attendees_tab.first.text_content()
    count_match = re.search(r'\((\d+)\)', attendees_count_text or "")
    attendees_count = int(count_match.group(1)) if count_match else -1
    
    # Step 6b: Find the attendee by name and check if it's in canceled state
    attendee_items = inner_iframe.get_by_text(client_name)
    attendee_count = attendee_items.count()
    
    # Both validations must pass:
    # 1. Count must be 0
    # 2. If attendee exists in DOM, it must show "Canceled by" indicator
    
    count_is_zero = attendees_count == 0
    has_canceled_indicator = False
    
    if attendee_count == 0:
        # Attendee name not found in DOM - completely removed
        # This is acceptable as long as count is also 0
        print(f"  [INFO] Attendee completely removed from DOM")
    else:
        # Attendee name found in DOM - MUST have "Canceled by" indicator
        attendee_element = attendee_items.first
        # Get parent container (should contain both name and cancellation indicator)
        container = attendee_element.locator('xpath=ancestor::*[position()=2]')
        container_text = container.text_content()
        
        # Check for "Canceled by" indicator in container text
        has_canceled_text = "Canceled by" in (container_text or "")
        
        # Also verify cancellation indicator element exists within container
        canceled_indicator = container.locator('*').filter(has_text=re.compile(r'Canceled by', re.IGNORECASE))
        canceled_indicator_count = canceled_indicator.count()
        
        has_canceled_indicator = has_canceled_text and canceled_indicator_count > 0
        
        if not has_canceled_indicator:
            raise ValueError(f"Attendee '{client_name}' exists in DOM but does NOT show 'Canceled by' indicator. Removal may have failed. Container text: {container_text[:100]}")
    
    # Re-check count if needed (in case UI is still updating)
    if not count_is_zero:
        page.wait_for_timeout(2000)
        attendees_count_text = attendees_tab.first.text_content()
        count_match = re.search(r'\((\d+)\)', attendees_count_text or "")
        attendees_count = int(count_match.group(1)) if count_match else -1
        count_is_zero = attendees_count == 0
    
    # Both conditions must be true
    if not count_is_zero:
        raise ValueError(f"Attendees count is {attendees_count} (expected 0). Removal may have failed.")
    
    # If attendee exists in DOM, it must have canceled indicator (already checked above)
    # If attendee doesn't exist in DOM, that's fine as long as count is 0
    
    print(f"  [OK] Attendee removed successfully")
    print(f"       Attendees tab: {attendees_count_text} (count: {attendees_count})")
    if attendee_count > 0:
        print(f"       Canceled indicator: Found")
    else:
        print(f"       Canceled indicator: N/A (attendee removed from DOM)")
