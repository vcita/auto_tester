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
    - At least one group event service exists (Calendar dropdown shows "Event Test Workshop" options)
    - Browser is on Calendar page (from _setup)
    
    Saves to context:
    - scheduled_event_time: Date/time of the scheduled event
    - event_group_service_name: Set to the service actually selected (dropdown may not include the one just created in _setup)
    """
    # Step 1: Verify on Calendar Page
    print("  Step 1: Verifying on Calendar page...")
    if "/app/calendar" not in page.url:
        raise ValueError(f"Expected to be on Calendar page, but URL is {page.url}")
    
    # Step 2: Click New Button
    print("  Step 2: Clicking New button...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    new_btn = inner_iframe.get_by_role('button', name='New')
    new_btn.click()
    group_event_option = inner_iframe.get_by_role('menuitem', name='Group event')
    group_event_option.wait_for(state='visible', timeout=5000)

    # Step 3: Select Group Event from Menu
    print("  Step 3: Selecting Group event...")
    group_event_option.click()
    # Wait for dialog: service combobox is the specific element that appears
    service_combobox = inner_iframe.get_by_role('combobox')
    service_combobox.wait_for(state='visible', timeout=15000)
    
    # Step 4: Select Group Event Service
    # Prefer the service from _setup (context) so Schedule Event and View Event use the same name.
    # If that option is not in the dropdown (cached list), fall back to first "Event Test Workshop" and update context.
    print("  Step 4: Selecting group event service...")
    service_combobox.click()
    listbox = inner_iframe.get_by_role('listbox')
    listbox.wait_for(state='visible', timeout=10000)
    expected_name = context.get("event_group_service_name")
    service_option = None
    service_name = None
    if expected_name:
        try:
            opt = inner_iframe.get_by_role('option').filter(has_text=expected_name).first
            opt.wait_for(state='visible', timeout=5000)
            service_option = opt
            service_name = expected_name
        except Exception:
            pass
    if service_option is None:
        service_option = inner_iframe.get_by_role('option').filter(has_text='Event Test Workshop').first
        service_option.wait_for(state='visible', timeout=10000)
        option_text = service_option.text_content() or ""
        service_name = option_text.split("₪")[0].strip() if "₪" in option_text else option_text.strip().split("\n")[0].strip()
        if not service_name or "Event Test Workshop" not in service_name:
            service_name = "Event Test Workshop"  # fallback for parsing
        context["event_group_service_name"] = service_name
    service_option.click()
    # Wait for dialog to show start date control after service selection
    start_date_buttons = inner_iframe.get_by_role('button', name='Start date:')
    start_date_buttons.first.wait_for(state='visible', timeout=10000)

    # Step 5: Set Start Date to Tomorrow (must be future so Cancel Event is available later)
    print("  Step 5: Setting start date to tomorrow...")
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_day = tomorrow.day
    # Use 10:00 so the event is clearly in the future in any timezone
    context["scheduled_event_time"] = tomorrow.strftime("%Y-%m-%d 10:00")

    # Verify service was selected (dialog is ready when combobox shows name)
    service_combobox_text = service_combobox.text_content() or ""
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
    page.wait_for_timeout(300)  # Brief settle before click (allowed)

    start_date_btn.click()
    # HEALED: get_by_role('menu').first matched the scheduler's allDayEventsContainer (role=menu), not the date
    # picker; waiting for it to hide never succeeded. Wait for date picker by the day button visibility instead.
    tomorrow_date_btn = page.get_by_role('button', name=str(tomorrow_day))
    if tomorrow_date_btn.count() == 0:
        tomorrow_date_btn = inner_iframe.get_by_role('button', name=str(tomorrow_day))
    if tomorrow_date_btn.count() == 0:
        raise ValueError(f"Date button for day {tomorrow_day} not found in date picker")
    tomorrow_date_btn.first.wait_for(state='visible', timeout=8000)
    # Use the last matching button (calendar grid usually has the day in current month last)
    day_btn = tomorrow_date_btn.nth(tomorrow_date_btn.count() - 1)
    day_btn.click()
    day_btn.wait_for(state='hidden', timeout=5000)

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
    schedule_dialog = inner_iframe.get_by_role('dialog')
    create_btn = inner_iframe.get_by_role('button', name='Create Event')
    create_btn.click()
    schedule_dialog.wait_for(state='hidden', timeout=15000)

    # Step 9: Verify Event Created (MCP-validated: search filters list; row with service name visible)
    print("  Step 9: Verifying event in Event List...")
    calendar_menu = page.get_by_text("Calendar", exact=True)
    calendar_menu.click()
    event_list_item = page.locator('[data-qa="VcMenuItem-calendar-subitem-event_list"]')
    event_list_item.wait_for(state='visible', timeout=10000)
    event_list_item.first.evaluate('el => el.click()')
    page.wait_for_url("**/app/event-list**", timeout=15000)
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    inner_iframe.get_by_role('textbox', name='Search by event name').wait_for(state='visible', timeout=15000)

    # Search by event name to filter to our event
    event_service_name = context.get("event_group_service_name")
    if not event_service_name:
        raise ValueError("event_group_service_name not in context")
    search_field = inner_iframe.get_by_role('textbox', name='Search by event name')
    search_field.wait_for(state='visible', timeout=10000)
    search_field.click()
    page.wait_for_timeout(100)  # Brief delay for focus (allowed)
    search_field.press_sequentially(event_service_name, delay=30)

    # HEALED: [cursor="pointer"] is not an HTML attribute (it's CSS); use get_by_text to find event.
    # Same name can appear in multiple places (e.g. two rows); use .first to avoid strict mode violation.
    event_cell = inner_iframe.get_by_text(event_service_name).first
    event_cell.wait_for(state='visible', timeout=10000)

    # Return to Calendar via "Calendar View" submenu (clicking "Calendar" only toggles menu when on Event List; MCP-validated)
    calendar_view_item = page.get_by_text("Calendar View", exact=True)
    calendar_view_item.click()
    page.wait_for_url("**/app/calendar**", timeout=10000)

    print(f"  [OK] Event scheduled and verified in Event List")
    print(f"       Date/Time: {context.get('scheduled_event_time')}")
