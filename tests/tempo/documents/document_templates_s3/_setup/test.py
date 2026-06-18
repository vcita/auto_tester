"""Setup for the document_templates_s3 subcategory.

Mirrors the legacy document-templates-s3.feature Background: log in to the isolated
account using the default (AWS-S3) documents storage backend. Documents are uploaded
per-test (see each test's script.md).
"""

from playwright.sync_api import Page

from tests._functions.login.test import fn_login


def setup_document_templates_s3(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")

    print("  Setup: Log in to isolated account (s3 storage backend)")
    fn_login(page, context, username=username, password=password)
    print(f"  [OK] document_templates_s3 setup complete - logged in as {context.get('logged_in_user')}")
