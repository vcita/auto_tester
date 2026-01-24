# Auto-generated from script.md
# Last updated: 2026-01-24
# Source: tests/scheduling/events/cancel_event/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
from playwright.sync_api import Page, expect


def test_cancel_event(page: Page, context: dict) -> None:
    """
    Test: Cancel Event
    
    Cancels a scheduled group event instance.
    
    Prerequisites:
    - User is logged in
    - A scheduled event exists and is open (context: scheduled_event_id)
    - Browser is on event detail page (from edit_event test)
    
    Saves to context:
    - None (clears event context variables)
    """
    # Step 1: Verify on Event Detail Page
    print("  Step 1: Verifying on event detail page...")
    if "/app/events/" not in page.url:
        raise ValueError(f"Expected to be on event detail page, but URL is {page.url}")
    
    # Step 2: Click Cancel Event Button
    print("  Step 2: Clicking Cancel Event button...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    cancel_btn = outer_iframe.get_by_role('button', name='Cancel Event')
    cancel_btn.click()
    # Wait for cancellation dialog to appear
    dialog = outer_iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=10000)
    
    # Step 3: Fill Cancellation Message (Optional)
    print("  Step 3: Filling cancellation message...")
    # Fill optional cancellation message
    cancellation_message = "Test cancellation - event no longer needed"
    message_field = outer_iframe.get_by_role('textbox', name='Cancellation message')
    message_field.click()
    page.wait_for_timeout(100)
    message_field.press_sequentially(cancellation_message, delay=30)
    page.wait_for_timeout(500)  # Allow message to be entered
    
    # Step 4: Click Submit to Cancel
    print("  Step 4: Clicking Submit to cancel event...")
    submit_btn = outer_iframe.get_by_role('button', name='Submit')
    submit_btn.click()
    # Wait for dialog to close and navigation to calendar
    page.wait_for_url("**/app/calendar**", timeout=10000)
    
    # Step 5: Verify Event is Cancelled
    print("  Step 5: Verifying event was cancelled...")
    # Wait for calendar to load
    page.wait_for_timeout(2000)  # Allow calendar to update
    
    # Verify we're on calendar page
    expect(page).to_have_url(re.compile(r".*app/calendar.*"))
    
    # Clear event context variables
    context.pop("scheduled_event_id", None)
    context.pop("scheduled_event_time", None)
    context.pop("event_attendee_id", None)
    
    print(f"  [OK] Event cancelled successfully")
    print(f"       Navigated to calendar page")
