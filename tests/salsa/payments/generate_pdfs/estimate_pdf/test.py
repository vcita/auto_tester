from playwright.sync_api import Page

from tests.salsa.payments.generate_pdfs.generate_pdfs_api import (
    assert_pdf_generated,
    create_estimate_via_api,
    get_estimate_pdf,
)


def test_estimate_pdf(page: Page, context: dict) -> None:
    print("  Step 1: Create estimate 'estimate' via API ($20 item) for the shared client")
    estimate = create_estimate_via_api(
        context, title="estimate", client_id=context["pdf_client_id"],
        address="persepolis, persia",
    )

    print(f"  Step 2: Generate the estimate PDF via the billboard API ({estimate['title']})")
    pdf = get_estimate_pdf(context, estimate["id"])

    print("  Step 3: Assert the estimate PDF was generated")
    assert_pdf_generated(pdf, "estimate")
