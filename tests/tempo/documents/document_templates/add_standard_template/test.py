"""Upload a document to My Documents and verify it appears in the standard template
list.

Migrates automation-js `document-templates-auth.feature` scenario
`Adding standard and signature document template (authenticated)` (standard template;
the signature variant is commented out in the legacy feature).
"""
import os

from playwright.sync_api import Page

from tests.tempo.documents.document_templates.documents_helpers import (
    assert_in_standard_templates,
    upload_to_my_documents,
)

DOCUMENT = "clientDoc.pdf"
DOCUMENT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "resources", DOCUMENT)
)


def test_add_standard_template(page: Page, context: dict) -> None:
    print(f"  Step 1: Uploading {DOCUMENT} to My Documents...")
    upload_to_my_documents(page, DOCUMENT_PATH)

    print("  Step 2: Verifying it appears in the standard template list...")
    assert_in_standard_templates(page, DOCUMENT)

    print("  [OK] Document template appears in the standard template list")
