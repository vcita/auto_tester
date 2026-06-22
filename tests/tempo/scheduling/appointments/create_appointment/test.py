# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/scheduling/appointments/create_appointment/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
from datetime import datetime, timedelta
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, expect

from tests.tempo.scheduling.appointments.appointment_helpers import UI_TIMEOUT, open_calendar_page


def test_create_appointment(page: Page, context: dict) -> None:
    """
    Test: Create Appointment
    
    Manually creates a 1-on-1 appointment for a test client using a test service
    from the business calendar.
    
    Prerequisites:
    - User is logged in
    - Test service exists (context: created_service_name)
    - Test client exists (context: created_client_name)
    
    Saves to context:
    - created_appointment_client: Name of the client for this appointment
    - created_appointment_service: Name of the service used
    """
    # Get test data from context
    client_name = context.get("created_client_name")
    service_name = context.get("created_service_name")
    
    if not client_name:
        raise ValueError("No test client in context. Run _setup first.")
    if not service_name:
        raise ValueError("No test service in context. Run _setup first.")
    
    # Step 1: Verify on Calendar Page
    print("  Step 1: Verifying on Calendar page...")
    if "/app/calendar" not in page.url:
        open_calendar_page(page)
    
    # Step 2: Wait for Calendar to Load
    print("  Step 2: Waiting for Calendar to load...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=UI_TIMEOUT)
    outer_iframe = page.frame_locator('iframe[title="angularjs"]')
    inner_iframe = outer_iframe.frame_locator('#vue_iframe_layout')
    new_btn = inner_iframe.get_by_role('button', name='New')
    new_btn.wait_for(state='visible', timeout=UI_TIMEOUT)
    
    # Step 3: Click New Button
    print("  Step 3: Clicking New button...")
    new_btn.click()
    # Step 4: Select Appointment from Menu (wait for dropdown - meaningful event)
    print("  Step 4: Selecting Appointment...")
    appointment_option = inner_iframe.get_by_role('menuitem', name='Appointment', exact=True)
    appointment_option.wait_for(state='visible', timeout=UI_TIMEOUT)
    appointment_option.click(timeout=UI_TIMEOUT)
    dialog = outer_iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=UI_TIMEOUT)
    
    service_picker = _select_client_and_wait_for_service_picker(
        page,
        outer_iframe,
        inner_iframe,
        new_btn,
        client_name,
    )
    
    # Step 7: Search for the test service so only the intended row remains.
    print(f"  Step 7: Looking for service: {service_name}...")
    service_search = service_picker.get_by_role('searchbox', name='Search')
    service_search.click(timeout=UI_TIMEOUT)
    page.wait_for_timeout(100)  # Brief delay for focus (allowed)
    service_search.press_sequentially(service_name, delay=30)

    # Step 8: Select the Service by clicking its explicit row action.
    print("  Step 8: Selecting service...")
    service_row = service_picker.locator('.service-item').filter(has_text=service_name).first
    service_row.wait_for(state='visible', timeout=UI_TIMEOUT)
    service_row.locator('[data-qa="service-name"]').click(timeout=UI_TIMEOUT)
    service_picker.wait_for(state='hidden', timeout=UI_TIMEOUT)
    # Wait for service picker to close and appointment form to load.
    # Single detection: Schedule button by accessible name (regex) or "Schedule" only (one compound locator).
    schedule_btn = inner_iframe.get_by_role('button', name=re.compile(r'Schedule\s*appointment', re.IGNORECASE)).or_(
        inner_iframe.get_by_role('button', name=re.compile(r'^Schedule$', re.IGNORECASE))
    ).first
    schedule_btn.wait_for(state='visible', timeout=UI_TIMEOUT)

    try:
        _select_tomorrow_date(inner_iframe)
    except Exception:
        print("  [WARN] Could not change appointment date; continuing with available time selection")
    try:
        _select_start_time(inner_iframe, "10:00 AM")
    except Exception:
        print("  [WARN] Could not change start time; continuing with default appointment time")

    # HEALED 2026-01-31: Address field is not always visible (e.g. Location section collapsed or not in form).
    # Form ready = Schedule button visible. If Address is required, fill when visible; otherwise skip.
    # Use optional fill: only attempt if Address appears without blocking (count-based check, no timeout swallow).
    address_field = inner_iframe.get_by_role('textbox', name=re.compile(r'Address', re.IGNORECASE)).first
    if address_field.count() > 0:
        address_field.click()
        address_field.press_sequentially('123 Test Street', delay=30)
        page.wait_for_timeout(300)  # Brief settle (allowed)
        page.keyboard.press('Tab')
        page.wait_for_timeout(500)  # Brief settle for autocomplete to dismiss (allowed)

    # Step 9: Click Schedule Appointment (same single compound locator)
    print("  Step 9: Scheduling appointment...")
    schedule_btn = inner_iframe.get_by_role('button', name=re.compile(r'Schedule\s*appointment', re.IGNORECASE)).or_(
        inner_iframe.get_by_role('button', name=re.compile(r'^Schedule$', re.IGNORECASE))
    ).first
    schedule_btn.wait_for(state='visible', timeout=UI_TIMEOUT)
    schedule_btn.click(force=True)
    
    # Step 10: Verify Appointment in Calendar (actual data verification)
    # NOTE: We verify the appointment appears in the calendar, NOT by checking toast messages
    print("  Step 10: Verifying appointment appears in calendar...")
    # Wait for the appointment to appear in calendar instead of arbitrary timeout
    # The appointment appears as a menuitem in the calendar grid containing the client name
    appointment_in_calendar = inner_iframe.get_by_role('menuitem').filter(has_text=client_name)
    last_error = None
    for _ in range(3):
        try:
            appointment_in_calendar.wait_for(state='visible', timeout=UI_TIMEOUT)
            break
        except PlaywrightTimeoutError as exc:
            last_error = exc
            if outer_iframe.get_by_role('dialog').count() == 0:
                raise
    else:
        raise last_error or AssertionError("Appointment did not appear in calendar")
    
    # Save to context for subsequent tests
    context["created_appointment_client"] = client_name
    context["created_appointment_service"] = service_name
    
    print(f"  [OK] Appointment created successfully")
    print(f"       Client: {client_name}")
    print(f"       Service: {service_name}")


def _select_client_and_wait_for_service_picker(page: Page, outer_iframe, inner_iframe, new_btn, client_name: str):
    last_error: Exception | None = None
    for attempt in range(2):
        if attempt == 1:
            print("  [WARN] Service picker did not open after client selection; retrying appointment flow")
            new_btn.wait_for(state='visible', timeout=UI_TIMEOUT)
            new_btn.click(timeout=UI_TIMEOUT)
            appointment_option = inner_iframe.get_by_role('menuitem', name='Appointment', exact=True)
            appointment_option.wait_for(state='visible', timeout=UI_TIMEOUT)
            appointment_option.click(timeout=UI_TIMEOUT)
            outer_iframe.get_by_role('dialog').wait_for(state='visible', timeout=UI_TIMEOUT)

        print(f"  Step 5: Searching for client: {client_name}...")
        search_field = outer_iframe.get_by_role('textbox', name='Search by name, email or tag')
        search_field.click(timeout=UI_TIMEOUT)
        page.wait_for_timeout(100)  # Brief delay for focus (allowed)
        search_field.press_sequentially(client_name, delay=30)
        client_option = outer_iframe.get_by_role('button').filter(has_text=client_name)
        client_option.wait_for(state='visible', timeout=UI_TIMEOUT)

        print("  Step 6: Selecting client...")
        client_option.click(timeout=UI_TIMEOUT)
        service_picker = inner_iframe.locator('[data-qa="service-picker-modal"]:visible')
        try:
            service_picker.wait_for(state='visible', timeout=UI_TIMEOUT)
            inner_iframe.get_by_text('My Services').wait_for(state='visible', timeout=UI_TIMEOUT)
            return service_picker
        except Exception as exc:
            last_error = exc

    raise last_error or AssertionError("Service picker did not open after client selection")


def _select_tomorrow_date(inner_iframe) -> None:
    tomorrow = datetime.now() + timedelta(days=1)
    current_year = datetime.now().year
    current_month = datetime.now().strftime("%B")

    date_field = inner_iframe.get_by_text(re.compile(rf"\d{{1,2}}\s+{current_month}\s+{current_year}")).first
    date_field.click(timeout=UI_TIMEOUT)

    day_button = inner_iframe.get_by_role("button", name=str(tomorrow.day)).last
    day_button.wait_for(state='visible', timeout=UI_TIMEOUT)
    day_button.click(timeout=UI_TIMEOUT)


def _select_start_time(inner_iframe, time_text: str) -> None:
    start_time_input = inner_iframe.locator('[data-qa="service-start-time-input"] input').first
    start_time_input.wait_for(state='visible', timeout=UI_TIMEOUT)
    start_time_input.click(timeout=UI_TIMEOUT)
    time_option = inner_iframe.locator(f'[data-qa="item-{time_text}"]').first
    time_option.wait_for(state='visible', timeout=UI_TIMEOUT)
    time_option.click(timeout=UI_TIMEOUT)
