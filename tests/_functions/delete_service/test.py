# Auto-generated from script.md
# Last updated: 2026-01-31
# Source: tests/_functions/delete_service/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
from typing import Callable, Optional

from playwright.sync_api import Page, expect

UI_TIMEOUT = 5_000


def fn_delete_service(
    page: Page, context: dict, step_callback: Optional[Callable[[str], None]] = None, **params
) -> None:
    """
    Delete a service by its name from the Services list.
    
    Used for test teardown to clean up test data.
    
    Parameters:
    - name (required): Name of the service to delete
    - step_callback (optional): If set, called with a short message before each minor action (for debugging).
    
    Clears from context:
    - created_service_id
    - created_service_name
    """
    name = params.get("name")
    if not name:
        # Try to get from context
        name = context.get("created_service_name")
    
    if not name:
        raise ValueError("Service name is required for deletion")
    # Use context["step_callback"] when set (e.g. by runner --debug-test) so teardown pauses after each action
    if step_callback is None:
        step_callback = context.get("step_callback")
    
    def _pause(msg: str) -> None:
        if step_callback:
            step_callback(msg)
        else:
            print(f"  {msg}")

    _pause("Step 1a: Ensure on app (if on calendar, navigate to dashboard first)")
    page.wait_for_load_state("domcontentloaded", timeout=UI_TIMEOUT)
    if "/app/calendar" in page.url:
        _pause("Step 1b: On calendar - click Dashboard in sidebar")
        dashboard_link = page.locator("body").get_by_text("Dashboard", exact=True)
        dashboard_link.wait_for(state="visible", timeout=UI_TIMEOUT)
        dashboard_link.scroll_into_view_if_needed()
        page.wait_for_timeout(200)  # Brief settle (allowed)
        dashboard_link.click(timeout=UI_TIMEOUT)
        page.wait_for_url("**/app/dashboard**", timeout=UI_TIMEOUT, wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded", timeout=UI_TIMEOUT)

    _pause("Step 1c: Click Settings in sidebar")
    # Sidebar may be in main frame or app iframe; use page so all frames are searched.
    settings_link = page.get_by_text("Settings", exact=True)
    settings_link.wait_for(state="visible", timeout=UI_TIMEOUT)
    settings_link.scroll_into_view_if_needed()
    page.wait_for_timeout(200)  # Brief settle (allowed)
    settings_link.click(timeout=UI_TIMEOUT)
    _pause("Step 1d: Wait for settings URL")
    page.wait_for_url("**/app/settings**", timeout=UI_TIMEOUT)

    _pause("Step 2a: Wait for iframe, then click Services button")
    # Step 2: Click Services button
    page.wait_for_selector('iframe[title="angularjs"]', timeout=UI_TIMEOUT)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    iframe.get_by_role('button', name='Define the services your').click(timeout=UI_TIMEOUT)
    _pause("Step 2b: Wait for services URL")
    page.wait_for_url("**/app/settings/services", timeout=UI_TIMEOUT)
    
    # HEALED 2026-01-31: Services list uses endless scroll (same as delete_service category test).
    # Scroll until the service button is in view or we reach the end of the list.
    _pause("Step 2c: Wait for My Services list to load")
    iframe.get_by_text("My Services").wait_for(state="visible", timeout=UI_TIMEOUT)
    _pause("Step 3a: Scroll to find service in list")
    max_scrolls = 10
    previous_last_text = ""
    no_change_count = 0
    for scroll_attempt in range(max_scrolls):
        try:
            service_row = iframe.get_by_role("button").filter(has_text=name)
            if service_row.count() > 0:
                break
        except Exception:
            pass
        try:
            all_services = iframe.get_by_role("button").filter(has_text=re.compile("Test Consultation|Appointment Test|Free estimate|Another Test|Test Debug|Test Group Workshop|Lawn mowing|On-site|MCP Test|UNIQUE TEST|SCROLL TEST"))
            service_count = all_services.count()
            if service_count > 0:
                last_service = all_services.nth(service_count - 1)
                current_last_text = (last_service.text_content() or "")[:200]
                if current_last_text == previous_last_text and previous_last_text != "":
                    no_change_count += 1
                    if no_change_count >= 2:
                        break
                else:
                    no_change_count = 0
                    previous_last_text = current_last_text
                last_service.scroll_into_view_if_needed()
                page.wait_for_timeout(300)  # Brief settle after scroll (allowed)
            else:
                add_btn = iframe.get_by_role("button", name="Add 1 on 1 Appointment")
                add_btn.scroll_into_view_if_needed()
                page.wait_for_timeout(300)  # Brief settle (allowed)
        except Exception:
            add_btn = iframe.get_by_role("button", name="Add 1 on 1 Appointment")
            add_btn.scroll_into_view_if_needed()
            page.wait_for_timeout(300)  # Brief settle (allowed)
    # Step 3: Click on Service in List
    service_in_list = iframe.get_by_role("button").filter(has_text=name)
    service_in_list.wait_for(state="visible", timeout=UI_TIMEOUT)
    service_in_list.click(timeout=UI_TIMEOUT)
    _pause("Step 3b: Wait for service detail URL")
    page.wait_for_url("**/app/settings/services/**", timeout=UI_TIMEOUT)
    
    _pause("Step 4: Click Delete button")
    # Step 4: Click Delete Button
    delete_clicked = False
    last_delete_error: Exception | None = None
    for attempt in range(2):
        if attempt == 1:
            _pause("Step 4a: Reload service detail page before retrying Delete")
            page.reload(wait_until="domcontentloaded", timeout=UI_TIMEOUT)
            page.wait_for_url("**/app/settings/services/**", timeout=UI_TIMEOUT)
            page.wait_for_selector('iframe[title="angularjs"]', timeout=UI_TIMEOUT)
            iframe = page.frame_locator('iframe[title="angularjs"]')

        try:
            # The legacy Angular toolbar does not consistently expose this action
            # to role/text locators, but its top-bar position is stable.
            page.wait_for_timeout(4_500)
            page.mouse.click(602, 82)
        except Exception as exc:
            last_delete_error = exc
            continue

        for scope in [iframe, *page.frames]:
            try:
                scope.get_by_role('dialog').wait_for(state='visible', timeout=UI_TIMEOUT)
                iframe = scope
                delete_clicked = True
                break
            except Exception as exc:
                last_delete_error = exc
            if delete_clicked:
                break
        if delete_clicked:
            break
    if not delete_clicked:
        raise last_delete_error or AssertionError("Could not click Delete button")
    
    _pause("Step 5: Click Ok in confirm dialog")
    # Step 5: Confirm Deletion
    ok_btn = iframe.get_by_role('button', name='Ok')
    ok_btn.click(timeout=UI_TIMEOUT)
    page.wait_for_url("**/app/settings/services", timeout=UI_TIMEOUT)
    
    _pause("Step 6: Verify service was deleted")
    # Step 6: Verify Service Removed
    services_heading = iframe.get_by_role('heading', name='Settings / Services')
    services_heading.wait_for(state='visible', timeout=UI_TIMEOUT)
    
    # Verify service is no longer in the list
    service_in_list = iframe.get_by_role('button').filter(has_text=name)
    expect(service_in_list).to_have_count(0)
    
    _clear_created_service_context(context)
    
    print(f"  [OK] Successfully deleted service: {name}")


def _clear_created_service_context(context: dict) -> None:
    context.pop("created_service_id", None)
    context.pop("created_service_name", None)
