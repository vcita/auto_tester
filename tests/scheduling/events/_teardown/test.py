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
    # Step 0: Ensure we're on a navigable page (after cancel_event we might be on calendar)
    # Navigate to dashboard first so delete functions can navigate from there
    print("  Teardown Step 0: Ensuring we're on a navigable page...")
    if "/app/dashboard" not in page.url:
        # Navigate to dashboard via UI if needed
        try:
            dashboard_link = page.get_by_text("Dashboard", exact=True)
            dashboard_link.wait_for(state="visible", timeout=30000)  # Long timeout for slow systems, continues immediately when visible
            dashboard_link.click()
            page.wait_for_url("**/app/dashboard**", timeout=30000)  # Long timeout, continues immediately when URL matches
        except Exception:
            # If Dashboard link not found, try Settings
            try:
                settings_link = page.get_by_text("Settings", exact=True)
                settings_link.wait_for(state="visible", timeout=30000)  # Long timeout for slow systems, continues immediately when visible
                settings_link.click()
                page.wait_for_url("**/app/settings**", timeout=30000)  # Long timeout, continues immediately when URL matches
            except Exception:
                pass  # Continue anyway - delete functions will handle navigation
    
    # Step 1: Delete Test Client
    client_name = context.get("event_client_name") or context.get("created_client_name")
    if client_name:
        print(f"  Teardown Step 1: Deleting test client: {client_name}...")
        try:
            fn_delete_client(page, context)
            print(f"    Client deleted: {client_name}")
        except Exception as e:
            print(f"    Warning: Could not delete client: {e}")
    else:
        print("  Teardown Step 1: No client to delete (not in context)")
    
    # Step 2: Delete Group Event Service
    service_name = context.get("event_group_service_name")
    if service_name:
        print(f"  Teardown Step 2: Deleting group event service: {service_name}...")
        try:
            # Set created_service_name so delete_service function can find it
            context["created_service_name"] = service_name
            fn_delete_service(page, context)
            print(f"    Service deleted: {service_name}")
        except Exception as e:
            print(f"    Warning: Could not delete service: {e}")
    else:
        print("  Teardown Step 2: No service to delete (not in context)")
    
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
