import os
import time

from playwright.sync_api import Page

from tests.account_api import create_client
from tests.tempo.clients.crm_bulk_actions.crm_bulk_helpers import (
    assert_conversation_has_document,
    assert_document_status,
    bulk_share_document,
    open_client_card,
    open_clients_list,
    select_all_pages,
)

DOCUMENT = "clientDoc.pdf"
DOCUMENT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "resources", DOCUMENT)
)


def test_share_document(page: Page, context: dict) -> None:
    """Bulk-share a document to all CRM clients; verify it in the client card
    conversation and that its status is "PENDING REVIEW".

    Migrates automation-js `crm-bulk-actions.feature` scenario `Share document from CRM`.
    """
    token = str(int(time.time() * 1000))
    print("  Step 1: Creating 2 clients via API...")
    create_client(context, f"first01_{token}", "last01", f"test01+{token}@vmeetme.com")
    current = create_client(context, f"first02_{token}", "last02", f"test02+{token}@vmeetme.com")

    print("  Step 2: Opening clients list and selecting all pages...")
    open_clients_list(page)
    select_all_pages(page)

    print(f"  Step 3: Bulk-sharing {DOCUMENT} to selected clients...")
    bulk_share_document(page, DOCUMENT_PATH)

    print("  Step 4: Verifying document in current client's conversation...")
    open_client_card(page, current["id"])
    assert_conversation_has_document(page, current["id"], DOCUMENT)

    print("  Step 5: Verifying document status is PENDING REVIEW...")
    assert_document_status(page, DOCUMENT)

    print("  [OK] Bulk share document verified (conversation + PENDING REVIEW status)")
