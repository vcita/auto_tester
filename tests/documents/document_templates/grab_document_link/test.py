"""Upload a document, grab its public link, and verify a client can access it.

Migrates automation-js `document-templates-auth.feature` scenario
`Grab document link (authenticated)`.
"""
import os

from playwright.sync_api import Page

from tests.documents.document_templates.documents_helpers import (
    assert_link_accessible,
    grab_document_link,
    upload_to_my_documents,
)

DOCUMENT = "clientDoc.pdf"
DOCUMENT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "resources", DOCUMENT)
)


def test_grab_document_link(page: Page, context: dict) -> None:
    print(f"  Step 1: Uploading {DOCUMENT} to My Documents...")
    upload_to_my_documents(page, DOCUMENT_PATH)

    print("  Step 2: Grabbing the document's public link...")
    link = grab_document_link(page, DOCUMENT)
    print(f"  Grabbed link: {link}")

    print("  Step 3: Verifying a client can access the grabbed link...")
    assert_link_accessible(page, link, DOCUMENT)

    print("  [OK] Client can access the grabbed document link")
