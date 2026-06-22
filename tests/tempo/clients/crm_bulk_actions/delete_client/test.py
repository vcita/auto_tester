import time

from playwright.sync_api import Page

from tests.account_api import create_client
from tests.tempo.clients.crm_bulk_actions.crm_bulk_helpers import (
    bulk_delete,
    open_clients_list,
    select_client,
    verify_client_deleted,
)


def test_delete_client(page: Page, context: dict) -> None:
    """Bulk-delete a CRM client; verify it is gone and the other client remains.

    Migrates automation-js `crm-bulk-actions.feature` scenario `Delete client from CRM`.
    """
    token = str(int(time.time() * 1000))
    remaining_query = f"first01_{token}"
    deleted_query = f"first02_{token}"
    print("  Step 1: Creating 2 clients via API...")
    remaining = create_client(context, remaining_query, "last01", f"test01+{token}@vmeetme.com")
    to_delete = create_client(context, deleted_query, "last02", f"test02+{token}@vmeetme.com")

    print(f"  Step 2: Opening clients list and selecting '{to_delete['full_name']}'...")
    open_clients_list(page)
    select_client(page, to_delete["full_name"])

    print("  Step 3: Bulk-deleting the selected client...")
    bulk_delete(page)

    print("  Step 4: Verifying the deleted client is gone and the other remains...")
    verify_client_deleted(
        page,
        remaining_query=remaining_query,
        remaining_name=remaining["full_name"],
        deleted_query=deleted_query,
    )

    print(f"  [OK] Bulk delete verified - only '{remaining['full_name']}' remains")
