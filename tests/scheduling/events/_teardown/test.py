# Auto-generated from script.md
# Last updated: 2026-01-27
# Source: tests/scheduling/events/_teardown/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page

from tests._functions.delete_client.test import fn_delete_client
from tests._functions.delete_service.test import fn_delete_service


def teardown_events(page: Page, context: dict) -> None:
    """
    Teardown for events tests.
    
    Cleans up:
    - The test client created in _setup
    - The group event service created in _setup
    
    Clears from context:
    - event_group_service_name
    - event_client_id
    - event_client_name
    - event_client_email
    - created_client_id
    - created_client_name
    - created_client_email
    """
    # Step 0: Ensure we're on a navigable page (after cancel_event we're on event-list)
    # Navigate to dashboard first so delete functions can navigate from there
    # HEALED 2026-01-27: Must ensure we're on dashboard before delete_client, otherwise navigation to matter list fails
    print("  Teardown Step 0: Ensuring we're on a navigable page...")
    if "/app/dashboard" not in page.url:
        # Navigate to dashboard via UI (no try/except: if nav fails, teardown must fail per project rules)
        print("  Teardown Step 0: Not on dashboard - navigating...")
        page.wait_for_load_state("domcontentloaded")
        dashboard_link = page.get_by_text("Dashboard", exact=True)
        dashboard_link.wait_for(state="visible", timeout=30000)
        dashboard_link.scroll_into_view_if_needed()
        page.wait_for_timeout(200)  # Brief settle before click (allowed)
        dashboard_link.click()
        page.wait_for_url("**/app/dashboard**", timeout=30000, wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        print("  Teardown Step 0: Successfully navigated to dashboard")

    # Step 1: Delete Test Client (no try/except: if delete fails, teardown must fail per project rules)
    client_name = context.get("event_client_name") or context.get("created_client_name")
    if client_name:
        print(f"  Teardown Step 1: Deleting test client: {client_name}...")
        fn_delete_client(page, context)
        print(f"    Client deleted: {client_name}")
    else:
        print("  Teardown Step 1: No client to delete (not in context)")

    # Step 2: Delete Group Event Service (no try/except: if delete fails, teardown must fail per project rules)
    service_name = context.get("event_group_service_name")
    if service_name:
        print(f"  Teardown Step 2: Deleting group event service: {service_name}...")
        context["created_service_name"] = service_name
        fn_delete_service(page, context)
        print(f"    Service deleted: {service_name}")
        page.wait_for_load_state("domcontentloaded")
        page_text = page.locator("body").text_content() or ""
        if "This page is unavailable" in page_text or "page is unavailable" in page_text.lower():
            homepage_link = page.get_by_text("Return to homepage", exact=False)
            if homepage_link.count() > 0:
                homepage_link.click()
                page.wait_for_url("**/app/dashboard**", timeout=30000)
            else:
                dashboard_link = page.get_by_text("Dashboard", exact=True)
                dashboard_link.wait_for(state="visible", timeout=10000)
                dashboard_link.first.click()
                page.wait_for_url("**/app/dashboard**", timeout=30000)
    else:
        print("  Teardown Step 2: No service to delete (not in context)")

    # Final check: must not be on error page when teardown completes (fail if we cannot navigate away)
    page.wait_for_load_state("domcontentloaded")
    page_text = page.locator("body").text_content() or ""
    if "This page is unavailable" in page_text or "page is unavailable" in page_text.lower():
        homepage_link = page.get_by_text("Return to homepage", exact=False)
        if homepage_link.count() > 0:
            homepage_link.click()
            page.wait_for_url("**/app/dashboard**", timeout=30000)
        else:
            dashboard_link = page.get_by_text("Dashboard", exact=True)
            dashboard_link.wait_for(state="visible", timeout=10000)
            dashboard_link.first.click()
            page.wait_for_url("**/app/dashboard**", timeout=30000)
    
    # Clear context variables
    context.pop("event_group_service_name", None)
    context.pop("event_client_id", None)
    context.pop("event_client_name", None)
    context.pop("event_client_email", None)
    context.pop("created_client_id", None)
    context.pop("created_client_name", None)
    context.pop("created_client_email", None)
    context.pop("created_service_name", None)
    
    print("  [OK] Events teardown complete")
