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
        # Navigate to dashboard via UI if needed
        # HEALED 2026-01-27: After cancel_event, we're on /app/event-list. Must navigate to dashboard first.
        print("  Teardown Step 0: Not on dashboard - navigating...")
        page.wait_for_load_state("domcontentloaded")
        try:
            dashboard_link = page.get_by_text("Dashboard", exact=True)
            dashboard_link.wait_for(state="visible", timeout=30000)  # Long timeout for slow systems, continues immediately when visible
            dashboard_link.scroll_into_view_if_needed()
            page.wait_for_timeout(200)  # Brief settle before click (allowed)
            dashboard_link.click()
            # HEALED 2026-01-27: Wait for navigation with domcontentloaded for faster completion
            page.wait_for_url("**/app/dashboard**", timeout=30000, wait_until="domcontentloaded")  # Long timeout, continues immediately when URL matches
            page.wait_for_load_state("domcontentloaded")
            print("  Teardown Step 0: Successfully navigated to dashboard")
        except Exception as e:
            # If Dashboard link not found, try Settings
            print(f"  Teardown Step 0: Dashboard navigation failed: {e}, trying Settings...")
            try:
                settings_link = page.get_by_text("Settings", exact=True)
                settings_link.wait_for(state="visible", timeout=30000)  # Long timeout for slow systems, continues immediately when visible
                settings_link.scroll_into_view_if_needed()
                page.wait_for_timeout(200)  # Brief settle before click (allowed)
                settings_link.click()
                page.wait_for_url("**/app/settings**", timeout=30000, wait_until="domcontentloaded")  # Long timeout, continues immediately when URL matches
                # Then navigate to dashboard from settings
                dashboard_link = page.get_by_text("Dashboard", exact=True)
                dashboard_link.wait_for(state="visible", timeout=30000)
                dashboard_link.click()
                page.wait_for_url("**/app/dashboard**", timeout=30000, wait_until="domcontentloaded")
                page.wait_for_load_state("domcontentloaded")
                print("  Teardown Step 0: Successfully navigated to dashboard via Settings")
            except Exception as e2:
                print(f"  Teardown Step 0: Warning - Could not navigate to dashboard: {e2}")
                # Continue anyway - delete functions will handle navigation, but may fail
                pass
    
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
            # HEALED 2026-01-27: After delete_service, check for error page and navigate away
            page.wait_for_load_state("domcontentloaded")
            page_text = page.locator("body").text_content() or ""
            if "This page is unavailable" in page_text or "page is unavailable" in page_text.lower():
                print("    Warning: Error page detected after service deletion, navigating to dashboard...")
                try:
                    homepage_link = page.get_by_text("Return to homepage", exact=False)
                    if homepage_link.count() > 0:
                        homepage_link.click()
                        page.wait_for_url("**/app/dashboard**", timeout=30000)
                    else:
                        # No direct goto to internal URLs - try UI navigation (Dashboard link)
                        dashboard_link = page.get_by_text("Dashboard", exact=True)
                        if dashboard_link.count() > 0:
                            dashboard_link.first.click()
                            page.wait_for_url("**/app/dashboard**", timeout=30000)
                        else:
                            print("    Warning: Could not find Return to homepage or Dashboard; staying on current page.")
                except Exception:
                    pass
        except Exception as e:
            print(f"    Warning: Could not delete service: {e}")
            # HEALED 2026-01-27: Even if delete fails, check for error page
            page.wait_for_load_state("domcontentloaded")
            page_text = page.locator("body").text_content() or ""
            if "This page is unavailable" in page_text or "page is unavailable" in page_text.lower():
                print("    Warning: Error page detected, navigating to dashboard...")
                try:
                    homepage_link = page.get_by_text("Return to homepage", exact=False)
                    if homepage_link.count() > 0:
                        homepage_link.click()
                        page.wait_for_url("**/app/dashboard**", timeout=30000)
                    else:
                        dashboard_link = page.get_by_text("Dashboard", exact=True)
                        if dashboard_link.count() > 0:
                            dashboard_link.first.click()
                            page.wait_for_url("**/app/dashboard**", timeout=30000)
                        else:
                            print("    Warning: Could not find Return to homepage or Dashboard; staying on current page.")
                except Exception:
                    pass
    else:
        print("  Teardown Step 2: No service to delete (not in context)")
    
    # HEALED 2026-01-27: Final check - ensure we're not on an error page before teardown completes
    # This ensures Services/Create Service starts on a valid page
    page.wait_for_load_state("domcontentloaded")
    page_text = page.locator("body").text_content() or ""
    if "This page is unavailable" in page_text or "page is unavailable" in page_text.lower():
        print("  Teardown Final: Error page detected, navigating to dashboard...")
        try:
            homepage_link = page.get_by_text("Return to homepage", exact=False)
            if homepage_link.count() > 0:
                homepage_link.click()
                page.wait_for_url("**/app/dashboard**", timeout=30000)
            else:
                dashboard_link = page.get_by_text("Dashboard", exact=True)
                if dashboard_link.count() > 0:
                    dashboard_link.first.click()
                    page.wait_for_url("**/app/dashboard**", timeout=30000)
                else:
                    print("  Teardown Final: Could not find Return to homepage or Dashboard; staying on current page.")
        except Exception:
            pass
    
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
