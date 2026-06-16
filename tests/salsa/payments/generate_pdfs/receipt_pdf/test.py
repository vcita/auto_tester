from playwright.sync_api import Page

from tests.salsa.payments.generate_pdfs.generate_pdfs_api import (
    assert_pdf_generated,
    create_invoice_via_api,
    get_receipt_pdf,
    record_payment,
)


def test_receipt_pdf(page: Page, context: dict) -> None:
    client_id = context["pdf_client_id"]

    print("  Step 1: Create invoice 'invoice' via API ($20 item) for the shared client")
    invoice = create_invoice_via_api(
        context, title="invoice", client_id=client_id, address="persepolis, persia",
    )

    print(f"  Step 2: Record a $20 Cash payment against {invoice['title']}")
    payment = record_payment(
        context, paying_for=invoice["title"], client_id=client_id, amount="20",
        subject_id=invoice["id"], subject_type="Invoice",
    )

    print("  Step 3: Generate the receipt PDF via the billboard API (keyed by payment id)")
    pdf = get_receipt_pdf(context, payment["payment_id"])

    print("  Step 4: Assert the receipt PDF was generated")
    assert_pdf_generated(pdf, "receipt")
