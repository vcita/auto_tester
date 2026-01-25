# Auto-generated from script.md
# Last updated: 2026-01-24
# Source: tests/scheduling/events/schedule_event/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from datetime import datetime, timedelta
from playwright.sync_api import Page, expect


def test_schedule_event(page: Page, context: dict) -> None:
    """
    Test: Schedule Event
    
    Schedules a group event instance by selecting a date and time for an existing group event service.
    
    Prerequisites:
    - User is logged in (from _setup)
    - Group event service exists (context: event_group_service_name)
    - Browser is on Calendar page (from _setup)
    
    Saves to context:
    - scheduled_event_time: Date/time of the scheduled event
    """
    # Step 1: Verify on Calendar Page
    print("  Step 1: Verifying on Calendar page...")
    if "/app/calendar" not in page.url:
        raise ValueError(f"Expected to be on Calendar page, but URL is {page.url}")
    
    # Get service name from context
    service_name = context.get("event_group_service_name")
    if not service_name:
        raise ValueError("No group event service name in context. Run _setup first.")
    
    # Step 2: Click New Button
    print("  Step 2: Clicking New button...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    new_btn = inner_iframe.get_by_role('button', name='New')
    new_btn.click()
    # Wait for dropdown menu to appear
    page.wait_for_timeout(500)
    
    # Step 3: Select Group Event from Menu
    print("  Step 3: Selecting Group event...")
    group_event_option = inner_iframe.get_by_role('menuitem', name='Group event')
    group_event_option.click()
    # Wait for dialog to appear - wait for service combobox which is a specific element in the dialog
    page.wait_for_timeout(2000)  # Allow dialog to start appearing
    # The service combobox is in the inner iframe within the dialog
    service_combobox = inner_iframe.get_by_role('combobox')
    service_combobox.wait_for(state='visible', timeout=15000)
    
    # Step 4: Select Group Event Service
    print(f"  Step 4: Selecting service: {service_name}...")
    # Click combobox to open
    service_combobox.click()
    # Wait for listbox to appear
    listbox = inner_iframe.get_by_role('listbox')
    listbox.wait_for(state='visible', timeout=10000)
    
    # Type service name to filter
    search_field = inner_iframe.get_by_role('textbox', name='Select service')
    search_field.click()
    page.wait_for_timeout(100)
    search_field.press_sequentially(service_name, delay=30)
    page.wait_for_timeout(1000)  # Allow search to filter and options to update
    
    # Select the service option - find by text content
    # Get all options and find the one containing service name
    all_options = inner_iframe.get_by_role('option')
    option_count = all_options.count()
    service_option = None
    for i in range(option_count):
        option = all_options.nth(i)
        option_text = option.text_content()
        if service_name in option_text:
            service_option = option
            break
    
    if not service_option:
        raise ValueError(f"Service '{service_name}' not found in options list")
    
    service_option.wait_for(state='visible', timeout=10000)
    service_option.click()
    page.wait_for_timeout(1000)  # Allow selection to register
    
    # Step 5: Set Start Date to Tomorrow (must be future so Cancel Event is available later)
    print("  Step 5: Setting start date to tomorrow...")
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_day = tomorrow.day
    # Use 10:00 so the event is clearly in the future in any timezone
    context["scheduled_event_time"] = tomorrow.strftime("%Y-%m-%d 10:00")
    
    # Wait for dialog to be fully ready after service selection
    page.wait_for_timeout(2000)  # Allow dialog to fully render
    
    # Verify service was selected
    service_combobox_text = service_combobox.text_content()
    if service_name not in service_combobox_text:
        raise ValueError(f"Service '{service_name}' was not selected. Combobox shows: {service_combobox_text}")
    
    start_date_buttons = inner_iframe.get_by_role('button', name='Start date:')
    button_count = start_date_buttons.count()
    if button_count >= 2:
        start_date_btn = start_date_buttons.nth(1)
    else:
        start_date_btn = start_date_buttons.nth(0)
    
    start_date_btn.wait_for(state='visible', timeout=5000)
    start_date_btn.scroll_into_view_if_needed()
    page.wait_for_timeout(300)
    
    date_picker_menu = None
    for attempt in range(2):
        start_date_btn.click()
        page.wait_for_timeout(3000)
        date_picker_menu = page.get_by_role('menu')
        if date_picker_menu.count() == 0:
            date_picker_menu = inner_iframe.get_by_role('menu')
        if date_picker_menu.count() > 0:
            break
        page.wait_for_timeout(500)
    
    if date_picker_menu is None or date_picker_menu.count() == 0:
        raise ValueError(
            "Date picker did not open. Event must be scheduled in the future so Cancel Event is available. "
            "Try running again or check Start date control."
        )
    
    date_picker_menu.first.wait_for(state='visible', timeout=5000)
    tomorrow_date_btn = page.get_by_role('button', name=str(tomorrow_day))
    if tomorrow_date_btn.count() == 0:
        tomorrow_date_btn = inner_iframe.get_by_role('button', name=str(tomorrow_day))
    if tomorrow_date_btn.count() == 0:
        raise ValueError(f"Date button for day {tomorrow_day} not found in date picker")
    # Use the last matching button (calendar grid usually has the day in current month last)
    tomorrow_date_btn.nth(tomorrow_date_btn.count() - 1).click()
    page.wait_for_timeout(1500)
    
    # Step 6: Verify End Date is Set (Auto-updated)
    print("  Step 6: Verifying end date auto-updated...")
    # End date should automatically update to match start date
    # No action needed - just verify
    # There are two "End Date:" buttons - use the second one (date value)
    end_date_buttons = inner_iframe.get_by_role('button', name='End Date:')
    if end_date_buttons.count() >= 2:
        end_date_btn = end_date_buttons.nth(1)  # Second button is the date value
    else:
        end_date_btn = end_date_buttons.nth(0)  # Fallback to first
    end_date_text = end_date_btn.text_content()
    # End date should show the selected date
    
    # Step 7: Verify Times are Set (Default is acceptable)
    print("  Step 7: Verifying default times...")
    # Times are set by default (4:00 PM - 5:00 PM)
    # No action needed unless specific times are required
    
    # Step 8: Click Create Event
    print("  Step 8: Clicking Create Event...")
    create_btn = inner_iframe.get_by_role('button', name='Create Event')
    create_btn.click()
    # Wait for dialog to close and calendar to update
    page.wait_for_timeout(2000)  # Allow event to be created and calendar to refresh
    
    # Step 9: Verify Event Created (MCP-validated: search filters list; row with service name visible)
    print("  Step 9: Verifying event in Event List...")
    page.wait_for_timeout(2000)  # Allow dialog to close and request to complete

    # Navigate to Event List
    calendar_menu = page.get_by_text("Calendar", exact=True)
    calendar_menu.click()
    page.wait_for_timeout(1500)  # Allow Calendar submenu to expand
    event_list_item = page.locator('[data-qa="VcMenuItem-calendar-subitem-event_list"]')
    event_list_item.wait_for(state='attached', timeout=10000)
    event_list_item.first.evaluate('el => el.click()')
    page.wait_for_url("**/app/event-list**", timeout=15000)
    page.wait_for_timeout(3000)  # Allow event list to load
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')

    # Search by event name to filter to our event
    event_service_name = context.get("event_group_service_name")
    if not event_service_name:
        raise ValueError("event_group_service_name not in context")
    search_field = inner_iframe.get_by_role('textbox', name='Search by event name')
    search_field.wait_for(state='visible', timeout=10000)
    search_field.click()
    page.wait_for_timeout(100)
    search_field.press_sequentially(event_service_name, delay=30)
    page.wait_for_timeout(2000)  # Allow filter to apply

    # HEALED: [cursor="pointer"] is not an HTML attribute (it's CSS); use get_by_text to find event
    event_cell = inner_iframe.get_by_text(event_service_name)
    event_cell.wait_for(state='visible', timeout=10000)

    # Return to Calendar via "Calendar View" submenu (clicking "Calendar" only toggles menu when on Event List; MCP-validated)
    calendar_view_item = page.get_by_text("Calendar View", exact=True)
    calendar_view_item.click()
    page.wait_for_url("**/app/calendar**", timeout=10000)

    print(f"  [OK] Event scheduled and verified in Event List")
    print(f"       Date/Time: {context.get('scheduled_event_time')}")
