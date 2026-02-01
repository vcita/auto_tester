# Auto-generated from script.md
# Last updated: 2026-01-31
# Source: tests/_functions/delete_client/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
from typing import Callable, Optional

from playwright.sync_api import Page, expect

def _check_for_error_page(page: Page) -> tuple[bool, str]:
    """
    Check if the page has navigated to an error page.
    Returns: (is_error_page, details)
    """
    try:
        page.wait_for_load_state("domcontentloaded", timeout=1000)
        page_text = page.locator("body").text_content() or ""
        url = page.url
        title = page.title
        
        # Check for error indicators
        has_error_text = "This page is unavailable" in page_text or "page is unavailable" in page_text.lower()
        has_return_homepage = "Return to homepage" in page_text or "return to homepage" in page_text.lower()
        is_error_url = "/error" in url.lower() or "unavailable" in url.lower()
        
        # Additional context
        body_snippet = page_text[:200] if page_text else "(empty)"
        
        if has_error_text or has_return_homepage or is_error_url:
            return True, f"ERROR PAGE - URL: {url}, Title: {title}, Error text: {has_error_text}, Return link: {has_return_homepage}, Error URL: {is_error_url}, Body snippet: {body_snippet}"
        
        return False, f"OK - URL: {url}, Title: {title}, Body snippet: {body_snippet[:100]}"
    except Exception as e:
        return False, f"Check failed: {e}"


def fn_delete_client(
    page: Page, context: dict, step_callback: Optional[Callable[[str], None]] = None, **params
) -> None:
    """
    Delete a client (matter/property) by navigating to their detail page.
    
    Used for test teardown to clean up test data.
    
    Parameters:
    - name (optional): Name of the client to delete (defaults to context value)
    - id (optional): ID of the client to delete (defaults to context value)
    - step_callback (optional): If set, called with a short message before each minor action (for debugging).
    
    Clears from context:
    - created_client_id
    - created_client_name
    - created_client_email
    """
    name = params.get("name")
    client_id = params.get("id")
    
    # Try to get from context if not provided
    if not name:
        name = context.get("created_client_name")
    if not client_id:
        client_id = context.get("created_client_id")
    
    if not name:
        raise ValueError("Client name is required for deletion")
    # Use context["step_callback"] when set (e.g. by runner --debug-test) so teardown pauses after each action
    if step_callback is None:
        step_callback = context.get("step_callback")
    
    def _pause(msg: str) -> None:
        if step_callback:
            step_callback(msg)
        else:
            print(f"  {msg}")
    
    # Step 1: Navigate to matter list (Properties/Clients/Patients - sidebar label varies by vertical)
    # Entity-agnostic: use same sidebar position as delete_matter (.menu-items-group > div:nth-child(4))
    _pause("Step 1a: Ensure on dashboard (navigate via sidebar if needed)")
    # Ensure we're on dashboard first. Use UI only (no page.goto to internal URLs).
    if "/app/dashboard" not in page.url:
        page.wait_for_load_state("domcontentloaded")
        dashboard_link = page.locator("body").get_by_text("Dashboard", exact=True)
        dashboard_link.wait_for(state="visible", timeout=30000)
        dashboard_link.scroll_into_view_if_needed()
        page.wait_for_timeout(200)  # Brief settle (allowed)
        dashboard_link.click()
        page.wait_for_url("**/app/dashboard**", timeout=30000, wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_selector('iframe[title="angularjs"]', timeout=30000)
    
    _pause("Step 1b: Click matter list in sidebar (4th menu item)")
    # HEALED 2026-01-31: Longer timeout for sidebar when arriving from dashboard (e.g. after appointments teardown).
    matter_list_nav = page.locator(".menu-items-group > div:nth-child(4)")
    matter_list_nav.wait_for(state="visible", timeout=30000)
    matter_list_nav.click()
    _pause("Step 1c: Wait for clients URL")
    page.wait_for_url("**/app/clients", timeout=10000)
    
    # Wait for list toolbar so list searchbox is present (list searchbox has no/missing aria-label on Properties)
    _pause("Step 1d: Wait for list toolbar (Filters)")
    page.get_by_role("button", name="Filters").wait_for(state="visible", timeout=30000)
    
    _pause("Step 2a: Click search field")
    # Step 2: Search for Client (list filter searchbox is 2nd searchbox; 1st is global header "Search")
    # HEALED 2026-01-31: List searchbox has no "Search by name, email, or phone number" on Properties page
    search_field = page.get_by_role("searchbox").nth(1)
    search_field.click()
    page.wait_for_timeout(100)
    _pause("Step 2b: Type client name in search")
    search_field.press_sequentially(name, delay=30)
    page.wait_for_timeout(1000)  # Allow search results to update
    
    _pause("Step 3a: Click client row to open detail page")
    # Step 3: Click on Client in List
    client_row = page.get_by_role('row').filter(has_text=name)
    client_row.wait_for(state='visible', timeout=5000)
    client_row.click()
    _pause("Step 3b: Wait for client detail URL")
    page.wait_for_url("**/app/clients/**", timeout=10000)
    
    _pause("Step 4a: Wait for iframe, then click More button")
    # Step 4: Click More Dropdown (detail page: menu stays inside iframe, unlike list-page delete_matter)
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    more_btn = iframe.get_by_role('button', name='More icon-caret-down')
    more_btn.wait_for(state='visible', timeout=10000)
    more_btn.click()
    # Menu is in iframe on detail page (MCP: menuitem "Delete property" inside menu).
    menu = iframe.get_by_role('menu')
    menu.wait_for(state='visible', timeout=10000)
    delete_option = menu.get_by_text('Delete')
    delete_option.wait_for(state='visible', timeout=8000)
    delete_option.click()
    # Confirmation dialog: HEALED 2026-01-31 — dialog is INSIDE the same iframe as More/menu (screenshot showed
    # dialog visible but page.get_by_role("dialog") timed out). Use iframe for dialog and OK so we find it.
    _pause("Step 5b: Wait for confirm dialog")
    iframe.get_by_role("dialog").wait_for(state="visible", timeout=30000)
    _pause("Step 6a: Click confirm button in delete dialog")
    confirm_btn = iframe.get_by_role("dialog").get_by_role("button", name=re.compile(r"^(Delete|OK|Ok)$", re.IGNORECASE)).first
    confirm_btn.wait_for(state="visible", timeout=10000)
    confirm_btn.click()
    is_error, status = _check_for_error_page(page)
    if is_error:
        raise ValueError(f"Error page appeared after confirm: {status}")
    iframe.get_by_role("dialog").wait_for(state="hidden", timeout=10000)
    page.wait_for_load_state("domcontentloaded")

    # Clear from context
    if "created_client_id" in context:
        del context["created_client_id"]
    if "created_client_name" in context:
        del context["created_client_name"]
    if "created_client_email" in context:
        del context["created_client_email"]
    
    print(f"  [OK] Successfully deleted client: {name}")
