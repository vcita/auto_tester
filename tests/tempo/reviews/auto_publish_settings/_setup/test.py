"""Setup for the reviews auto_publish_settings subcategory.

Provisions two directory-scoped triples (no review site / with review site) via API,
mirroring the legacy reviews.feature scenario 2 & 3 preconditions:
`admin creates directory`, `user creates business in directory`, and
`user creates new client for business in directory`. UI login is deferred to each
test so the two scenarios (two different in-directory businesses) stay independent.
"""

from playwright.sync_api import Page

from tests.tempo.reviews.auto_publish_settings.directory_setup import provision_directory_business


def setup_auto_publish_settings(page: Page, context: dict) -> None:
    print("  Setup Step 1: Provision directory + business WITHOUT external review site (scenario 2)")
    context["auto_publish_no_site"] = provision_directory_business(
        context, with_review_site=False, slug="nosite"
    )
    print(f"    [OK] business {context['auto_publish_no_site']['email']} ready (no review site)")

    print("  Setup Step 2: Provision directory + business WITH external review site (scenario 3)")
    context["auto_publish_with_site"] = provision_directory_business(
        context, with_review_site=True, slug="withsite"
    )
    print(f"    [OK] business {context['auto_publish_with_site']['email']} ready (review site: vcita)")

    print("  [OK] auto_publish_settings setup complete")
