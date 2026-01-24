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
    # Step 1: Delete Test Client
    client_name = context.get("created_client_name")
    if client_name:
        print(f"  Teardown Step 1: Deleting test client: {client_name}...")
        try:
            fn_delete_client(page, context)
            print(f"    Client deleted: {client_name}")
        except Exception as e:
            print(f"    Warning: Could not delete client: {e}")
    else:
        print("  Teardown Step 1: No client to delete (not in context)")
    
    # Step 2: Delete Test Service
    service_name = context.get("created_service_name")
    if service_name:
        print(f"  Teardown Step 2: Deleting test service: {service_name}...")
        try:
            fn_delete_service(page, context)
            print(f"    Service deleted: {service_name}")
        except Exception as e:
            print(f"    Warning: Could not delete service: {e}")
    else:
        print("  Teardown Step 2: No service to delete (not in context)")
    
    print("  [OK] Appointments teardown complete")
