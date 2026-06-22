# Auto-generated from script.md
# Last updated: 2026-01-23
# Source: tests/scheduling/appointments/_teardown/script.md
# DO NOT EDIT MANUALLY - Regenerate from script.md

from playwright.sync_api import Page

from tests._functions.delete_client.test import fn_delete_client
from tests._functions.delete_service.test import fn_delete_service


def teardown_appointments(page: Page, context: dict) -> None:
    """
    Teardown for appointments tests.
    
    Cleans up:
    - The test client created in _setup
    - The test service created in _setup
    
    Clears from context:
    - created_service_id
    - created_service_name
    - created_client_id
    - created_client_name
    - created_client_email
    """
    # Step 0: Ensure we're on dashboard (after appointments we're on calendar; sidebar not reliable from calendar)
    # HEALED 2026-01-31: Navigate to dashboard first so delete_client and delete_service can find sidebar
    print("  Teardown Step 0: Ensuring we're on dashboard...")
    if "/app/dashboard" not in page.url:
        print("  Teardown Step 0: Not on dashboard - navigating...")
        page.wait_for_load_state("domcontentloaded")
        # HEALED 2026-01-31: If a fullscreen iframe (e.g. after Reschedule failure) covers the sidebar,
        # click is intercepted. Dismiss any modal/overlay with Escape so Dashboard becomes clickable.
        for _ in range(3):
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
        page.wait_for_timeout(500)
        # Sidebar is in main document; scope to body so we don't match inside calendar iframe
        dashboard_link = page.locator("body").get_by_text("Dashboard", exact=True)
        dashboard_link.wait_for(state="visible", timeout=30000)
        dashboard_link.scroll_into_view_if_needed()
        page.wait_for_timeout(200)  # Brief settle (allowed)
        dashboard_link.click()
        page.wait_for_url("**/app/dashboard**", timeout=30000, wait_until="domcontentloaded")
        page.wait_for_load_state("domcontentloaded")
        # Same as login/create_matter: do NOT wait for iframe first (multiple iframes can exist,
        # first may be hidden). Wait for "Quick actions" at page level so Playwright finds the visible panel.
        page.get_by_text("Quick actions", exact=True).wait_for(state="visible", timeout=30000)
        print("  Teardown Step 0: Successfully navigated to dashboard")

    # Step 1: Delete Test Client (no try/except: if delete fails, teardown must fail per project rules)
    client_name = context.get("created_client_name")
    if client_name:
        print(f"  Teardown Step 1: Deleting test client: {client_name}...")
        fn_delete_client(page, context)
        print(f"    Client deleted: {client_name}")
    else:
        print("  Teardown Step 1: No client to delete (not in context)")

    # Step 2: Delete Test Service (no try/except: if delete fails, teardown must fail per project rules)
    service_name = context.get("created_service_name")
    if service_name:
        print(f"  Teardown Step 2: Deleting test service: {service_name}...")
        fn_delete_service(page, context)
        print(f"    Service deleted: {service_name}")
    else:
        print("  Teardown Step 2: No service to delete (not in context)")
    
    print("  [OK] Appointments teardown complete")
