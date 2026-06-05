import time

from playwright.sync_api import Page

from tests.account_api import create_client
from tests.clients.crm_bulk_actions.crm_bulk_helpers import (
    assert_last_message_bubble,
    bulk_send_message,
    open_client_card,
    open_clients_list,
    select_client,
)

SUBJECT = "hi"
CONTENT = "hello"


def test_send_message(page: Page, context: dict) -> None:
    """Bulk-send a message to a CRM client; verify it in the client card conversation.

    Migrates automation-js `crm-bulk-actions.feature` scenario `Send message from CRM`.
    """
    token = str(int(time.time() * 1000))
    print("  Step 1: Creating 2 clients via API...")
    create_client(context, f"first01_{token}", "last01", f"test01+{token}@vmeetme.com")
    target = create_client(context, f"first02_{token}", "last02", f"test02+{token}@vmeetme.com")

    print(f"  Step 2: Opening clients list and selecting '{target['full_name']}'...")
    open_clients_list(page)
    select_client(page, target["full_name"])

    print(f"  Step 3: Bulk-sending message subject='{SUBJECT}' content='{CONTENT}'...")
    bulk_send_message(page, SUBJECT, CONTENT)

    print("  Step 4: Verifying the message in the client's conversation...")
    open_client_card(page, target["id"])
    assert_last_message_bubble(page, target["id"], SUBJECT, CONTENT)

    print("  [OK] Bulk send message verified (subject + content in conversation)")
