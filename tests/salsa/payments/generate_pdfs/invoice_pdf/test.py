from playwright.sync_api import Page

from tests.salsa.payments.generate_pdfs.generate_pdfs_api import (
    assert_pdf_generated,
    create_invoice_via_api,
    get_invoice_pdf,
)


def test_invoice_pdf(page: Page, context: dict) -> None:
    print("  Step 1: Create invoice 'invoice' via API ($20 item) for the shared client")
    invoice = create_invoice_via_api(
        context, title="invoice", client_id=context["pdf_client_id"],
        address="persepolis, persia",
    )

    print(f"  Step 2: Generate the invoice PDF via the billboard API ({invoice['title']})")
    pdf = get_invoice_pdf(context, invoice["id"])

    print("  Step 3: Assert the invoice PDF was generated")
    assert_pdf_generated(pdf, "invoice")
