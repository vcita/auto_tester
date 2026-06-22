"""Upload a document (AWS-S3 backend), grab its public link, verify the link is served
from S3, and verify a client can access it.

Migrates automation-js `document-templates-s3.feature` scenario `Grab document link (s3)`.

Reuses the shared grab-link/access helpers from the sibling authenticated migration and
adds the s3 storage-signal assertion (`fileStorageType=AWS-S3`), which is the defining
distinction of the legacy s3 feature.
"""
import os

from playwright.sync_api import Page

from tests.tempo.documents.document_templates.documents_helpers import (
    assert_link_accessible,
    grab_document_link,
    upload_to_my_documents,
)
from tests.tempo.documents.document_templates_s3.documents_s3_helpers import (
    assert_link_is_s3,
)

DOCUMENT = "clientDoc.pdf"
DOCUMENT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "resources", DOCUMENT)
)


def test_grab_document_link(page: Page, context: dict) -> None:
    print(f"  Step 1: Uploading {DOCUMENT} to My Documents (s3 backend)...")
    upload_to_my_documents(page, DOCUMENT_PATH)

    print("  Step 2: Grabbing the document's public link...")
    link = grab_document_link(page, DOCUMENT)
    print(f"  Grabbed link: {link}")

    print("  Step 3: Verifying the link is served from the AWS-S3 backend...")
    assert_link_is_s3(link)

    print("  Step 4: Verifying a client can access the grabbed link...")
    assert_link_accessible(page, link, DOCUMENT)

    print("  [OK] Client can access the grabbed S3 document link")
