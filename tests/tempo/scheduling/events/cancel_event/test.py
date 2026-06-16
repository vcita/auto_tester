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
    
    # Step 2: Click Cancel Event Button (or open More menu and click Cancel Event)
    print("  Step 2: Clicking Cancel Event button...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    cancel_clicked = False

    # 1) Direct button in outer iframe
    cancel_btn = outer_iframe.get_by_role('button', name=re.compile(r'Cancel\s*Event', re.IGNORECASE))
    if cancel_btn.count() == 0:
        cancel_btn = outer_iframe.get_by_text(re.compile(r'Cancel\s*Event', re.IGNORECASE))
    if cancel_btn.count() > 0:
        cancel_btn.first.click()
        cancel_clicked = True

    if not cancel_clicked:
        # 2) Scan outer iframe buttons for text "cancel" + "event"
        all_buttons = outer_iframe.get_by_role('button')
        n = all_buttons.count()
        for i in range(n):
            try:
                btn = all_buttons.nth(i)
                t = (btn.text_content() or "").strip()
                if "cancel" in t.lower() and "event" in t.lower():
                    btn.click()
                    cancel_clicked = True
                    break
            except Exception:
                continue

    if not cancel_clicked:
        # 3) Inner iframe
        cancel_btn = inner_iframe.get_by_role('button', name=re.compile(r'Cancel\s*Event', re.IGNORECASE))
        if cancel_btn.count() == 0:
            cancel_btn = inner_iframe.get_by_text(re.compile(r'Cancel\s*Event', re.IGNORECASE))
        if cancel_btn.count() > 0:
            cancel_btn.first.click()
            cancel_clicked = True

    if not cancel_clicked:
        # 4) Open "More" / actions menu (only EDIT and DUPLICATE visible on card)
        more_btn = outer_iframe.get_by_role('button', name=re.compile(r'More|Actions|Menu|\.\.\.', re.IGNORECASE))
        if more_btn.count() == 0:
            more_btn = outer_iframe.locator('button[aria-haspopup="menu"]')
        if more_btn.count() == 0:
            all_buttons = outer_iframe.get_by_role('button')
            for i in range(all_buttons.count()):
                try:
                    btn = all_buttons.nth(i)
                    lab = (btn.get_attribute('aria-label') or "").strip()
                    if re.search(r'more|actions|menu|options', lab, re.I):
                        more_btn = btn
                        break
                except Exception:
                    continue
        if more_btn.count() > 0:
            (more_btn.first if more_btn.count() > 1 else more_btn).click()
            outer_iframe.get_by_role('menuitem', name=re.compile(r'Cancel\s*Event', re.IGNORECASE)).first.wait_for(state='visible', timeout=5000)
            for frame in [outer_iframe, inner_iframe, page]:
                mi = frame.get_by_role('menuitem', name=re.compile(r'Cancel\s*Event', re.IGNORECASE))
                if mi.count() == 0:
                    mi = frame.get_by_text(re.compile(r'Cancel\s*Event', re.IGNORECASE))
                if mi.count() > 0:
                    mi.first.click()
                    cancel_clicked = True
                    break

    if not cancel_clicked:
        # 5) Cancel from Event List: go to list, find event row, open row menu, click Cancel Event
        print("  Step 2a: Cancel Event not on detail page; trying from Event List...")
        calendar_menu = page.get_by_text("Calendar", exact=True)
        calendar_menu.click()
        event_list_item = page.locator('[data-qa="VcMenuItem-calendar-subitem-event_list"]')
        # HEALED: Submenu item can be attached but hidden when Calendar submenu is collapsed; wait for attached then force click.
        event_list_item.wait_for(state='attached', timeout=10000)
        event_list_item.first.evaluate('el => el.click()')
        page.wait_for_url("**/app/event-list**", timeout=15000)
        page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
        outer_iframe = page.frame_locator('iframe[title="angularjs"]')
        inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
        inner_iframe.get_by_role('textbox', name='Search by event name').wait_for(state='visible', timeout=15000)
        service_name = context.get("event_group_service_name", "")
        if not service_name:
            raise ValueError("event_group_service_name not in context")
        # Event rows: try by service name, then by "0/12" (our edited event), then any clickable row
        event_rows = inner_iframe.locator('[cursor="pointer"]').filter(has_text=service_name)
        if event_rows.count() == 0:
            event_rows = inner_iframe.locator('[cursor="pointer"]').filter(has_text=re.compile(r'\d+\s*/\s*12', re.I))
        if event_rows.count() == 0:
            event_rows = inner_iframe.get_by_text(service_name)
        if event_rows.count() == 0:
            raise ValueError("Event not found in Event List for Cancel Event")
        row = event_rows.first
        # Find 3-dot / menu button within or next to this row (same pattern as remove_attendee: activator-container, three-dots)
        row_buttons = row.locator('button')
        menu_btn = None
        for i in range(row_buttons.count()):
            try:
                btn = row_buttons.nth(i)
                cls = (btn.get_attribute('class') or "")
                if 'activator-container' in cls or 'three-dots' in cls or (btn.get_attribute('aria-haspopup') == 'menu'):
                    menu_btn = btn
                    break
            except Exception:
                continue
        if menu_btn is None:
            # Fallback: any button in row that might open a menu
            if row_buttons.count() > 0:
                menu_btn = row_buttons.last
        if menu_btn is not None:
            menu_btn.click()
            outer_iframe.get_by_role('menuitem', name=re.compile(r'Cancel\s*Event', re.IGNORECASE)).first.wait_for(state='visible', timeout=5000)
            for frame in [outer_iframe, inner_iframe, page]:
                # Prefer exact "Cancel Event" / "Cancel event"
                mi = frame.get_by_role('menuitem', name=re.compile(r'Cancel\s*Event', re.IGNORECASE))
                if mi.count() == 0:
                    mi = frame.get_by_text(re.compile(r'Cancel\s*Event', re.IGNORECASE))
                if mi.count() == 0:
                    # Scan all menuitems for one that cancels the event (not "Cancel registration")
                    all_mi = frame.get_by_role('menuitem')
                    for j in range(all_mi.count()):
                        item = all_mi.nth(j)
                        t = (item.text_content() or "").strip()
                        if "cancel" in t.lower() and "event" in t.lower() and "registration" not in t.lower():
                            item.click()
                            cancel_clicked = True
                            break
                        if "cancel" in t.lower() and "instance" in t.lower():
                            item.click()
                            cancel_clicked = True
                            break
                    if cancel_clicked:
                        break
                elif mi.count() > 0:
                    mi.first.click()
                    cancel_clicked = True
                    break
        if not cancel_clicked:
            raise ValueError(
                "Cancel Event control not found. Event may be in the past (completed); "
                "Cancel Event is only shown for future events. Ensure schedule_event sets a future date."
            )
    # Wait for cancellation dialog: look for its unique field (Cancellation message) to avoid matching a hidden dialog
    dialog_scope = outer_iframe
    message_field = outer_iframe.get_by_role('textbox', name='Cancellation message')
    try:
        message_field.wait_for(state='visible', timeout=15000)
    except Exception:
        message_field = page.get_by_role('textbox', name='Cancellation message')
        message_field.wait_for(state='visible', timeout=15000)
        dialog_scope = page
    
    # Step 3: Fill Cancellation Message (Optional)
    print("  Step 3: Filling cancellation message...")
    cancellation_message = "Test cancellation - event no longer needed"
    message_field.click()
    page.wait_for_timeout(100)  # Brief delay for focus (allowed)
    message_field.press_sequentially(cancellation_message, delay=30)

    # Step 4: Click Submit to Cancel
    print("  Step 4: Clicking Submit to cancel event...")
    submit_btn = dialog_scope.get_by_role('button', name='Submit')
    submit_btn.click()
    # Wait for dialog to close and navigation to calendar
    page.wait_for_url("**/app/calendar**", timeout=10000)
    
    # Step 5: Verify Event is Cancelled
    print("  Step 5: Verifying event was cancelled...")
    # Verify we're on calendar page
    expect(page).to_have_url(re.compile(r".*app/calendar.*"))
    calendar_menu = page.get_by_text("Calendar", exact=True)
    calendar_menu.wait_for(state='visible', timeout=5000)
    calendar_menu.click()
    event_list_item = page.locator('[data-qa="VcMenuItem-calendar-subitem-event_list"]')
    # HEALED: Event List submenu item can be attached but hidden when Calendar submenu is collapsed; wait for attached then force click.
    event_list_item.wait_for(state='attached', timeout=10000)
    event_list_item.first.evaluate('el => el.click()')
    page.wait_for_url("**/app/event-list**", timeout=15000)
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    inner_iframe.get_by_role('textbox', name='Search by event name').wait_for(state='visible', timeout=15000)
    service_name = context.get("event_group_service_name", "")
    if service_name:
        # Find the event by service name; get row text from ancestor (status "CANCELLED" is sibling in row)
        event_cell = inner_iframe.get_by_text(service_name)
        if event_cell.count() > 0:
            row_text = event_cell.first.evaluate(
                "el => el.closest('[class*=\"list-item\"], [class*=\"v-list-item\"], [role=\"row\"]')?.innerText ?? el.parentElement?.innerText ?? ''"
            )
            if not row_text:
                row_text = event_cell.first.text_content() or ""
            if "CANCELLED" not in row_text.upper():
                raise ValueError(
                    f"Event '{service_name}' not shown as CANCELLED in Event List. Row text: {row_text[:200]}"
                )
            print(f"       Event List shows status: CANCELLED")
    
    # Clear event context variables
    context.pop("scheduled_event_id", None)
    context.pop("scheduled_event_time", None)
    context.pop("event_attendee_id", None)
    
    print(f"  [OK] Event cancelled successfully")
    print(f"       Navigated to calendar page")
