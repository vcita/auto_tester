# Auto-generated from script.md
# Last updated: 2026-01-24
# Source: tests/scheduling/events/view_event/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
from datetime import datetime
from playwright.sync_api import Page, expect


def test_view_event(page: Page, context: dict) -> None:
    """
    Test: View Event
    
    Opens and views the details of a scheduled group event instance.
    
    Prerequisites:
    - User is logged in
    - A scheduled event exists (context: scheduled_event_time)
    - Browser is on Calendar page (from schedule_event test)
    
    Saves to context:
    - scheduled_event_id: ID of the event (extracted from URL)
    """
    # Step 1: Verify on Calendar Page or Event Page
    print("  Step 1: Verifying page state...")
    # After schedule_event, we might be on the event detail page
    # If on event page, we're already viewing it - just extract ID and return
    if "/app/events/" in page.url:
        print("  Already on event detail page from previous test")
        # Extract event ID from URL
        url = page.url
        event_id_match = re.search(r'/app/events/([a-z0-9]+)', url)
        if event_id_match:
            context["scheduled_event_id"] = event_id_match.group(1)
            service_name = context.get("event_group_service_name", "Unknown")
            print(f"  [OK] Event viewed successfully (already on page)")
            print(f"       Event ID: {context.get('scheduled_event_id')}")
            print(f"       Service: {service_name}")
            return  # Already viewing the event, no need to navigate
    
    # If not on event page, should be on calendar
    if "/app/calendar" not in page.url:
        raise ValueError(f"Expected to be on Calendar or Event page, but URL is {page.url}")
    
    # Step 2: Navigate to Event Date
    print("  Step 2: Navigating to event date...")
    # Get event date from context
    event_time_str = context.get("scheduled_event_time")
    if not event_time_str:
        raise ValueError("No scheduled_event_time in context. Run schedule_event first.")
    
    # Parse the date (format: "YYYY-MM-DD HH:MM")
    event_date = datetime.strptime(event_time_str.split()[0], "%Y-%m-%d")
    event_day = event_date.day
    
    # Wait for calendar to load
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    
    # Get service name from context
    service_name = context.get("event_group_service_name")
    if not service_name:
        raise ValueError("No event_group_service_name in context. Run _setup first.")

    # Navigate to the event date - click day in mini calendar (complementary + exact=True to avoid "January 2026")
    date_btn = inner_iframe.get_by_role('complementary').first.get_by_role('button', name=str(event_day), exact=True)
    date_btn.click()

    # Step 3: Find Event in Calendar Grid (wait for calendar to show event for that date)
    # Use .first so we match exactly one when multiple menuitems have the same service name (e.g. multi-slot).
    print("  Step 3: Finding event in calendar...")
    event_menuitem = inner_iframe.get_by_role('menuitem').filter(has_text=service_name).first
    event_menuitem.wait_for(state='visible', timeout=15000)
    
    # Step 4: Click Event to Open Details
    print("  Step 4: Clicking event to open details...")
    event_menuitem.click()
    # Wait for event detail page to load
    page.wait_for_url("**/app/events/**", timeout=10000)
    
    # Step 5: Verify Event Details are Displayed
    print("  Step 5: Verifying event details...")
    # Verify we're on event detail page
    expect(page).to_have_url(re.compile(r"/app/events/[a-z0-9]+"))
    
    # Verify event name is displayed
    event_name_heading = outer_iframe.get_by_role('heading', level=3).filter(has_text=service_name)
    expect(event_name_heading).to_be_visible()
    
    # Verify date/time is displayed
    date_time_heading = outer_iframe.get_by_role('heading', level=2)
    expect(date_time_heading).to_be_visible()
    
    # Extract event ID from URL for context
    url = page.url
    event_id_match = re.search(r'/app/events/([a-z0-9]+)', url)
    if event_id_match:
        context["scheduled_event_id"] = event_id_match.group(1)
        print(f"  [OK] Event viewed successfully")
        print(f"       Event ID: {context.get('scheduled_event_id')}")
        print(f"       Service: {service_name}")
    else:
        raise ValueError(f"Could not extract event ID from URL: {url}")
