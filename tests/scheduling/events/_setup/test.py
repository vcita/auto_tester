# Auto-generated from script.md
# Last updated: 2026-01-24
# Source: tests/scheduling/events/_setup/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import os
import re
import time
from playwright.sync_api import Page, expect

from tests._functions.login.test import fn_login
from tests._functions.create_client.test import fn_create_client


def _scroll_services_list_to_end(page: Page) -> None:
    """
    Scroll the services list container to the very end inside the app iframe so all items are loaded.

    Targets the scrollable element that contains "My Services" (the list panel), not the first
    scrollable div in the document (which may be something else). See .cursor/docs/mcp_debug_events_setup_scroll.md
    for MCP debugging if this fails.
    """
    el = page.locator('iframe[title="angularjs"]').element_handle()
    if not el:
        return
    frame = el.content_frame()
    if not frame:
        return
    # Find the scrollable container that wraps the services list and scroll it to the end.
    # We look for ancestors of "My Services" that have overflow-y auto/scroll; when the list is short,
    # scrollHeight can equal clientHeight so we don't require scrollHeight > clientHeight (MCP debug 2026-01-26).
    # Among those, pick the one with the largest clientHeight so we scroll the main content area (e.g.
    # settings-component) rather than the small list-header bar.
    _scroll_list_to_bottom = """
        () => {
            function getScrollableAncestors(el) {
                const list = [];
                while (el && el !== document.body) {
                    const style = getComputedStyle(el);
                    if (style.overflowY === 'auto' || style.overflowY === 'scroll' || style.overflowY === 'overlay')
                        list.push(el);
                    el = el.parentElement;
                }
                return list;
            }
            const all = document.querySelectorAll('*');
            let label = null;
            for (const el of all) {
                const t = (el.textContent || '').trim();
                if (t === 'My Services' || (t.startsWith('My Services') && t.length < 50)) {
                    label = el;
                    break;
                }
            }
            const candidates = label ? getScrollableAncestors(label) : [];
            let scrollable = null;
            let maxHeight = 0;
            for (const el of candidates) {
                if (el.clientHeight > maxHeight) {
                    maxHeight = el.clientHeight;
                    scrollable = el;
                }
            }
            if (!scrollable) return null;
            scrollable.scrollTop = scrollable.scrollHeight - scrollable.clientHeight;
            return { scrollHeight: scrollable.scrollHeight, clientHeight: scrollable.clientHeight };
        }
    """
    prev_height = None
    for _ in range(50):
        try:
            result = frame.evaluate(_scroll_list_to_bottom)
            if not result:
                break
            sh = result["scrollHeight"]
            if prev_height is not None and sh == prev_height:
                break
            prev_height = sh
        except Exception:
            break
        page.wait_for_timeout(300)  # Brief settle after scroll (allowed)


def setup_events(page: Page, context: dict) -> None:
    """
    Setup for events tests.

    Assumes parent (Scheduling) setup has already run and left the browser on
    Settings > Services. This setup only creates the group event service and
    test client, then navigates to Calendar.

    Performs login if needed, then creates:
    - A group event service for scheduling event instances
    - A test client to add as an attendee

    Then navigates to the Calendar page.

    Saves to context:
    - event_group_service_name: Name of the group event service
    - event_client_id: ID of the test client
    - event_client_name: Full name of the test client
    - event_client_email: Email of the test client
    """
    timestamp = int(time.time())

    # Step 0: Login if not already logged in
    if "logged_in_user" not in context:
        print("  Setup Step 0: Logging in...")
        username = context.get("username")
        password = context.get("password")
        if not username or not password:
            raise ValueError(
                "username and password not in context. Set target.auth.username and target.auth.password in config.yaml."
            )
        fn_login(page, context, username=username, password=password)

    # Parent (Scheduling) setup leaves us on Settings > Services; ensure iframe is ready
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')

    # Generate unique group event name
    group_event_name = f"Event Test Workshop {timestamp}"

    # Step 1: Open New Service Dropdown
    print("  Setup Step 1: Opening New service menu...")
    new_service_btn = iframe.get_by_role("button", name="New service icon-caret-down")
    new_service_btn.click()
    # Wait for dropdown menu to appear
    menu = iframe.get_by_role("menu")
    menu.wait_for(state="visible", timeout=5000)
    
    # Step 2: Select Group Event
    print("  Setup Step 2: Selecting Group event...")
    group_event_option = iframe.get_by_role("menuitem", name="Group event")
    group_event_option.click()
    # Wait for dialog to appear
    dialog = iframe.get_by_role("dialog")
    dialog.wait_for(state="visible", timeout=10000)
    
    # Step 3: Fill Service Name
    print(f"  Setup Step 3: Entering service name: {group_event_name}")
    name_field = iframe.get_by_role("textbox", name="Service name *")
    name_field.click()
    page.wait_for_timeout(100)  # Brief delay for field focus
    name_field.press_sequentially(group_event_name, delay=30)
    
    # Step 4: Set Max Attendees
    print("  Setup Step 4: Setting max attendees to 10...")
    max_attendees_field = iframe.get_by_role("spinbutton", name="Max attendees icon-q-mark-s *")
    max_attendees_field.click()
    max_attendees_field.fill("10")  # fill is OK for number spinbutton
    
    # Step 5: Select Face to Face Location
    print("  Setup Step 5: Selecting Face to face location...")
    face_to_face_btn = iframe.get_by_role("button", name="icon-Home Face to face")
    face_to_face_btn.click()
    # Wait for address options to appear
    address_options = iframe.get_by_role("radiogroup")
    address_options.wait_for(state="visible", timeout=5000)
    # Default "My business address" is already selected - no action needed
    
    # Step 6: Select With Fee and Enter Price
    print("  Setup Step 6: Setting price to 25...")
    with_fee_btn = iframe.get_by_role("button", name="icon-Credit-card With fee")
    with_fee_btn.click()
    # Wait for price field to appear
    price_field = iframe.get_by_role("spinbutton", name="Service price *")
    price_field.wait_for(state="visible", timeout=5000)
    price_field.click()
    price_field.fill("25")  # fill is OK for number spinbutton
    
    # Step 7: Click Create
    print("  Setup Step 7: Clicking Create...")
    # HEALED: Wait for the create (service) dialog specifically; get_by_role("dialog") would match
    # the next dialog ("Great. Now enter your event dates & times") and never become hidden.
    create_dialog = iframe.get_by_role("dialog", name=re.compile(r"Service info", re.IGNORECASE))
    create_btn = iframe.get_by_role("button", name="Create")
    create_btn.click()
    create_dialog.wait_for(state="hidden", timeout=15000)

    # Step 8: Handle Event Times Dialog (Conditional)
    print("  Setup Step 8: Checking for event times dialog...")
    later_btn = iframe.get_by_role("button", name="I'll do it later")
    try:
        later_btn.wait_for(state="visible", timeout=5000)
        print("  Setup Step 8a: Event times dialog appeared - dismissing...")
        later_btn.click()
        # Wait for the event-times dialog to close
        iframe.get_by_role("dialog", name=re.compile(r"Great\. Now", re.IGNORECASE)).wait_for(state="hidden", timeout=5000)
    except Exception:
        print("  Setup Step 8a: Event times dialog did not appear - continuing...")

    # HEALED: Known UI issue – new service does not appear in the list until we navigate away and back to Services.
    # Use UI navigation (Settings → back to Services) so the list refreshes; same pattern as create_group_event.
    print("  Setup Step 8b: Refreshing Services list (navigate away and back)...")
    page.get_by_text("Settings", exact=True).click()
    page.wait_for_url("**/app/settings**", timeout=10000)
    page.wait_for_selector('iframe[title="angularjs"]', state="visible", timeout=5000)
    iframe.get_by_role("button", name="Define the services your").click()
    page.wait_for_url("**/app/settings/services**", timeout=10000)
    iframe.get_by_role("heading", name="Settings / Services").wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(500)  # Brief settle after navigation (allowed)

    # Scroll the services list to the end so every item is loaded, then find the new service.
    _scroll_services_list_to_end(page)
    page.wait_for_timeout(500)  # Brief settle after scroll (allowed)

    # Validate service actually appears on Services page (so Schedule Event can find it in dropdown)
    try:
        iframe.get_by_text(group_event_name).first.wait_for(state="visible", timeout=20000)
    except Exception as e:
        raise AssertionError(
            f"Setup could not confirm group event service was created: '{group_event_name}' not found on Services page. "
            "Create dialog closed but service may not have been saved. Check run video/screenshot."
        ) from e

    # Step 9: Save Group Event Service Name
    print("  Setup Step 9: Saving group event service name...")
    context["event_group_service_name"] = group_event_name
    print(f"    Group event service created: {group_event_name}")
    
    # Step 10: Create Test Client
    print("  Setup Step 10: Creating test client...")
    fn_create_client(
        page, 
        context, 
        first_name="Event",
        last_name=f"TestClient{timestamp}"
    )
    
    # Save to context with event-specific names
    context["event_client_id"] = context.get("created_client_id")
    context["event_client_name"] = context.get("created_client_name")
    context["event_client_email"] = context.get("created_client_email")
    print(f"    Client created: {context.get('event_client_name')}")
    
    # Step 11: Navigate to Calendar
    print("  Setup Step 11: Navigating to Calendar...")
    calendar_menu = page.get_by_text("Calendar", exact=True)
    calendar_menu.click()
    page.wait_for_url("**/app/calendar**", timeout=10000)
    
    # Verify we're on the calendar page
    expect(page).to_have_url(re.compile(r".*app/calendar.*"))
    
    print("  [OK] Events setup complete")
    print(f"       Group Event Service: {context.get('event_group_service_name')}")
    print(f"       Client: {context.get('event_client_name')} ({context.get('event_client_id')})")
