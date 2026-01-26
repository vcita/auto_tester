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
    page.wait_for_timeout(100)  # Brief delay for focus (allowed)
    search_field.press_sequentially(client_name, delay=30)

    # Step 4: Select Client from Results
    print("  Step 4: Selecting client from results...")
    dialog = outer_iframe.get_by_role('dialog')
    # HEALED: Wait for search results to show client (newly created client may take a moment to appear in list).
    client_locator = dialog.get_by_text(client_name, exact=False)
    try:
        client_locator.first.wait_for(state='visible', timeout=15000)
    except Exception:
        client_email = context.get("event_client_email")
        if client_email:
            print(f"  Client by name not found, trying by email: {client_email}")
            client_locator = dialog.get_by_text(client_email, exact=False)
            client_locator.first.wait_for(state='visible', timeout=10000)
        else:
            raise ValueError(f"Client '{client_name}' not found in search results.")
    client_locator.first.click()
    continue_btn = outer_iframe.get_by_role('button', name='Continue')
    continue_btn.wait_for(state='visible', timeout=5000)

    # Step 5: Click Continue to Register
    print("  Step 5: Clicking Continue to register client...")
    continue_btn = outer_iframe.get_by_role('button', name='Continue')
    continue_btn.wait_for(state='visible', timeout=10000)
    continue_btn.click()
    # Step 5a: Confirmation dialog – click Send to complete registration (MCP-verified)
    print("  Step 5a: Clicking Send to complete registration...")
    send_btn = outer_iframe.get_by_role('button', name='Send')
    send_btn.wait_for(state='visible', timeout=10000)
    send_btn.click()
    # Wait for dialog to close: event page returns when Register Clients is visible again
    register_btn = outer_iframe.get_by_role('button', name='Register Clients')
    register_btn.wait_for(state='visible', timeout=15000)

    # Step 6: Verify Client Added to Attendees
    print("  Step 6: Verifying client was added to attendees...")
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    attendees_tab = inner_iframe.get_by_role('tab', name=re.compile(r'Attendees'))
    attendees_tab.wait_for(state='visible', timeout=10000)
    inner_iframe.get_by_text(client_name).first.wait_for(state='visible', timeout=10000)
    attendees_count_text = attendees_tab.first.text_content()
    context["event_attendee_id"] = context.get("event_client_id")
    
    print(f"  [OK] Client added as attendee successfully")
    print(f"       Client: {client_name}")
    print(f"       Attendees tab: {attendees_count_text}")
