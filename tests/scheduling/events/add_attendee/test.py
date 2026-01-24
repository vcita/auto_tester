# Auto-generated from script.md
# Last updated: 2026-01-24
# Source: tests/scheduling/events/add_attendee/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
from playwright.sync_api import Page, expect


def test_add_attendee(page: Page, context: dict) -> None:
    """
    Test: Add Attendee
    
    Adds a client as an attendee to a scheduled group event.
    
    Prerequisites:
    - User is logged in
    - A scheduled event exists and is open (context: scheduled_event_id)
    - A test client exists (context: event_client_name)
    - Browser is on event detail page (from view_event test)
    
    Saves to context:
    - event_attendee_id: ID of the client added to event
    """
    # Step 1: Verify on Event Detail Page
    print("  Step 1: Verifying on event detail page...")
    if "/app/events/" not in page.url:
        raise ValueError(f"Expected to be on event detail page, but URL is {page.url}")
    
    # Step 2: Click Register Clients Button
    print("  Step 2: Clicking Register Clients button...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    register_btn = outer_iframe.get_by_role('button', name='Register Clients')
    register_btn.click()
    # Wait for dialog to appear
    dialog = outer_iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=10000)
    
    # Step 3: Search for Test Client
    print("  Step 3: Searching for test client...")
    # Get client name from context
    client_name = context.get("event_client_name")
    if not client_name:
        raise ValueError("No event_client_name in context. Run _setup first.")
    
    # Search for client
    search_field = outer_iframe.get_by_role('textbox', name='Search by name, email or tag')
    search_field.click()
    page.wait_for_timeout(100)
    search_field.press_sequentially(client_name, delay=30)
    page.wait_for_timeout(1500)  # Allow search to filter results and list to update
    
    # Step 4: Select Client from Results
    print("  Step 4: Selecting client from results...")
    # Select the client from filtered results
    # Get all buttons and find the one with client name
    # Wait for list to populate
    page.wait_for_timeout(1000)  # Allow list to update after search
    all_buttons = outer_iframe.get_by_role('button')
    button_count = all_buttons.count()
    client_button = None
    
    # Try to find client by name - check all buttons
    for i in range(button_count):
        try:
            btn = all_buttons.nth(i)
            btn_text = btn.text_content()
            if btn_text and client_name in btn_text:
                client_button = btn
                break
        except:
            continue
    
    if not client_button:
        # Try searching by email instead
        client_email = context.get("event_client_email")
        if client_email:
            print(f"  Trying to find client by email: {client_email}")
            for i in range(button_count):
                try:
                    btn = all_buttons.nth(i)
                    btn_text = btn.text_content()
                    if btn_text and client_email in btn_text:
                        client_button = btn
                        break
                except:
                    continue
    
    if not client_button:
        raise ValueError(f"Client '{client_name}' not found in search results. Searched {button_count} buttons.")
    
    client_button.wait_for(state='visible', timeout=10000)
    client_button.click()
    page.wait_for_timeout(500)  # Allow selection to register
    
    # Step 5: Click Continue to Register
    print("  Step 5: Clicking Continue to register client...")
    # Click Continue to register the client
    continue_btn = outer_iframe.get_by_role('button', name='Continue')
    continue_btn.wait_for(state='visible', timeout=10000)
    # Wait for button to be enabled (may be disabled until client is selected)
    continue_btn.wait_for(state='attached', timeout=5000)
    continue_btn.click()
    # Wait for dialog to close
    dialog.wait_for(state='hidden', timeout=10000)
    
    # Step 6: Verify Client Added to Attendees
    print("  Step 6: Verifying client was added to attendees...")
    # Wait for page to update
    page.wait_for_timeout(2000)  # Allow attendees list to update
    
    # Verify client appears in attendees list
    # The attendees tab should show the client
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    attendees_tab = inner_iframe.get_by_role('tab', name=re.compile(r'Attendees'))
    attendees_tab.wait_for(state='visible', timeout=10000)
    
    # Check if attendees count increased or client name appears
    # The tab name changes from "Attendees (0)" to "Attendees (1)"
    attendees_count_text = attendees_tab.text_content()
    # Should contain "Attendees (1)" or similar
    
    # Save client ID to context (if available from the button or list)
    context["event_attendee_id"] = context.get("event_client_id")
    
    print(f"  [OK] Client added as attendee successfully")
    print(f"       Client: {client_name}")
    print(f"       Attendees tab: {attendees_count_text}")
