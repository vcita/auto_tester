"""Attach a My-Documents file to a saved-draft and a sent invoice, verifying the
attachment shows on each invoice.

Migrates automation-js `attach-document-to-invoice.feature` scenario
`Attach document to invoice`.
"""
import os
import time

from playwright.sync_api import Page

from tests.account_api import create_client, create_service_via_api
from tests.salsa.payments.invoices.attach_document.attach_document_helpers import (
    assert_document_attached,
    create_invoice_with_document,
    upload_to_my_documents,
)

DOCUMENT = "clientDoc.pdf"
DOCUMENT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "resources", DOCUMENT)
)


def test_attach_to_invoice(page: Page, context: dict) -> None:
    token = str(int(time.time() * 1000))
    client_first = f"first_{token}"
    client_name = f"{client_first} last"
    service_name = f"service_{token}"

    print("  Step 1: Creating client + 'display a fee' service via API...")
    create_client(context, client_first, "last", f"test+{token}@vmeetme.com")
    create_service_via_api(
        context, service_name, charge_type="paid_non_secured", price="10"
    )

    print(f"  Step 2: Uploading {DOCUMENT} to My Documents...")
    upload_to_my_documents(page, DOCUMENT_PATH, DOCUMENT)

    print("  Step 3: Creating + saving a draft invoice with the document attached...")
    create_invoice_with_document(
        page, context, name="saved_invoice", client_name=client_name,
        file_name=DOCUMENT, send=False, billing_address="blablablabla",
        existing_items=[service_name],
    )
    print("  Step 4: Verifying the document is attached to the saved invoice...")
    assert_document_attached(page, context, title="saved_invoice", number=1, file_name=DOCUMENT)

    print("  Step 5: Creating + sending an invoice with the document attached...")
    create_invoice_with_document(
        page, context, name="send_invoice", client_name=client_name,
        file_name=DOCUMENT, send=True, billing_address="blablablabla",
        existing_items=[service_name],
    )
    print("  Step 6: Verifying the document is attached to the sent invoice...")
    assert_document_attached(page, context, title="send_invoice", number=2, file_name=DOCUMENT)

    print("  [OK] Document attached to both saved and sent invoices")
