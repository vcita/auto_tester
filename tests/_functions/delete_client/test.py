# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/_functions/delete_client/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

import re
from playwright.sync_api import Page, expect

from tests._functions._config import get_base_url


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


def fn_delete_client(page: Page, context: dict, **params) -> None:
    """
    Delete a client (matter/property) by navigating to their detail page.
    
    Used for test teardown to clean up test data.
    
    Parameters:
    - name (optional): Name of the client to delete (defaults to context value)
    - id (optional): ID of the client to delete (defaults to context value)
    
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
    
    # Step 1: Navigate to matter list (Properties/Clients/Patients - sidebar label varies by vertical)
    # Entity-agnostic: use same sidebar position as delete_matter (.menu-items-group > div:nth-child(4))
    base_url = get_base_url(context, params)
    print("  Step 1: Navigating to matter list...")
    # Ensure we're on app first
    if not (base_url in page.url and "/app/" in page.url):
        page.goto(f"{base_url}/app/dashboard")
        page.wait_for_load_state("domcontentloaded")
    
    matter_list_nav = page.locator(".menu-items-group > div:nth-child(4)")
    matter_list_nav.wait_for(state="visible", timeout=10000)
    matter_list_nav.click()
    page.wait_for_url("**/app/clients", timeout=10000)
    
    # Wait for the page to load
    page.wait_for_timeout(1000)
    
    # Step 2: Search for Client
    print(f"  Step 2: Searching for client: {name}")
    search_field = page.get_by_role('searchbox', name='Search by name, email, or phone number')
    search_field.click()
    page.wait_for_timeout(100)
    search_field.press_sequentially(name, delay=30)
    page.wait_for_timeout(1000)  # Allow search results to update
    
    # Step 3: Click on Client in List
    print("  Step 3: Opening client detail page...")
    client_row = page.get_by_role('row').filter(has_text=name)
    client_row.wait_for(state='visible', timeout=5000)
    client_row.click()
    page.wait_for_url("**/app/clients/**", timeout=10000)
    
    # Step 4: Click More Dropdown
    print("  Step 4: Opening More menu...")
    page.wait_for_selector('iframe[title="angularjs"]', timeout=10000)
    iframe = page.frame_locator('iframe[title="angularjs"]')
    more_btn = iframe.get_by_role('button', name='More icon-caret-down')
    more_btn.wait_for(state='visible', timeout=10000)
    more_btn.click()
    menu = iframe.get_by_role('menu')
    menu.wait_for(state='visible', timeout=5000)
    
    # Step 5: Select Delete <entity> (menuitem text varies: "Delete property", "Delete client", "Delete patient", etc.)
    print("  Step 5: Clicking Delete matter...")
    delete_option = iframe.get_by_role("menuitem").filter(has_text=re.compile(r"^Delete ", re.IGNORECASE))
    delete_option.first.click()
    dialog = iframe.get_by_role('dialog')
    dialog.wait_for(state='visible', timeout=5000)
    
    # Step 6: Confirm Deletion
    print("  Step 6: Confirming deletion...")
    
    # DEBUG: Wait and check before clicking Ok
    print("  [DEBUG] Waiting 5 seconds before clicking Ok button...")
    page.wait_for_timeout(5000)
    is_error, status = _check_for_error_page(page)
    print(f"  [DEBUG] Pre-Ok click check: {status}")
    if is_error:
        print(f"  [ERROR] Error page detected BEFORE clicking Ok! {status}")
        raise ValueError(f"Error page appeared before Ok click: {status}")
    
    ok_btn = iframe.get_by_role('button', name='Ok')
    ok_btn.click()
    
    # DEBUG: Wait and check after clicking Ok, before waiting for dialog to close
    print("  [DEBUG] Waiting 5 seconds after clicking Ok, before waiting for dialog to close...")
    page.wait_for_timeout(5000)
    is_error, status = _check_for_error_page(page)
    print(f"  [DEBUG] Post-Ok click check: {status}")
    if is_error:
        print(f"  [ERROR] Error page detected AFTER clicking Ok! {status}")
        raise ValueError(f"Error page appeared after Ok click: {status}")
    
    # Wait for dialog to close
    print("  [DEBUG] Waiting for dialog to close...")
    url_before_dialog_close = page.url
    dialog.wait_for(state='hidden', timeout=10000)
    
    # DEBUG: Immediate check after dialog closes (navigation might happen during dialog close)
    print("  [DEBUG] Immediate check right after dialog closed...")
    is_error, status = _check_for_error_page(page)
    url_after_dialog_close = page.url
    url_changed = url_before_dialog_close != url_after_dialog_close
    print(f"  [DEBUG] Immediate post-dialog-close check: {status}")
    print(f"  [DEBUG] URL changed during dialog close: {url_changed} (before: {url_before_dialog_close}, after: {url_after_dialog_close})")
    if is_error:
        print(f"  [ERROR] Error page detected IMMEDIATELY after dialog closed! {status}")
        raise ValueError(f"Error page appeared immediately after dialog closed: {status}")
    
    # DEBUG: Wait and check after dialog closes, before waiting for load state
    print("  [DEBUG] Waiting 5 seconds after dialog closed, before waiting for load state...")
    page.wait_for_timeout(5000)
    is_error, status = _check_for_error_page(page)
    print(f"  [DEBUG] Post-dialog-close check (after 5s wait): {status}")
    if is_error:
        print(f"  [ERROR] Error page detected AFTER dialog closed (after 5s wait)! {status}")
        raise ValueError(f"Error page appeared after dialog closed (after 5s wait): {status}")
    
    page.wait_for_load_state("domcontentloaded")
    
    # DEBUG: Final check after load state
    print("  [DEBUG] Final check after load state...")
    page.wait_for_timeout(5000)
    is_error, status = _check_for_error_page(page)
    print(f"  [DEBUG] Final check: {status}")
    if is_error:
        print(f"  [ERROR] Error page detected in final check! {status}")
        raise ValueError(f"Error page appeared in final check: {status}")
    
    # Clear from context
    if "created_client_id" in context:
        del context["created_client_id"]
    if "created_client_name" in context:
        del context["created_client_name"]
    if "created_client_email" in context:
        del context["created_client_email"]
    
    print(f"  [OK] Successfully deleted client: {name}")
