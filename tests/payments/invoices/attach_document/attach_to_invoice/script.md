# Script: Attach Document to Saved and Sent Invoice

Implemented in `attach_document_helpers.py` (frames + actions) and `invoice_billing_ui.py`
(invoice wizard, reused).

## Frames

- Documents list: `iframe[title="angularjs"] -> #vue_iframe_main`.
- Upload / wizard dialogs: `iframe[title="angularjs"] -> #vue_wizard_iframe`.
- Invoice wizard: `iframe[title="angularjs"] -> #vue_wizard_iframe` (via `open_new_invoice`).
- Invoice detail: `iframe[title="angularjs"]` (`billing_scope`).

## Setup (API)

- `create_client` and `create_service_via_api(charge_type="paid_non_secured", price="10")`.

## Actions

1. `upload_to_my_documents(page, path, name)` → open `/app/documents`, click upload
   button `//div[contains(@class,'upload-button')]//button[@data-qa='add']`, drop the
   file on `[data-qa="vc-dropzone--input"]` (wizard dialog frame), confirm with
   `button[data-qa="vc-footer-Upload"]`, wait for the `.list-item` with the file name.
2. `create_invoice_with_document(...)` → `open_new_invoice` (Billing > New > Invoice >
   pick client), `set_title`, `add_existing_item` for the service, then
   `attach_document`:
   - expand the `Attached Documents` section,
   - click the add-icon `i.add-icon`,
   - pick the file from My Documents (`md-select` → option by file name → confirm
     `[data-qa="confirm-button"]`),
   - save draft `[data-qa='itemizable-dialog-secondary']` or send
     `[data-qa='itemizable-dialog-main']`,
   - wait for navigation to `**/app/invoices/**`.
3. `assert_document_attached(...)` → open the invoice (by API id if needed) and assert a
   `.invoice-document-item-content` row contains the file name (legacy
   `getDocumentNameAttachedToInvoice`).

## Waits

- `NAV_TIMEOUT` (20s) for angularjs + wizard iframe (re)mounts and invoice navigation.
- `STATE_TIMEOUT` (15s) polling for the attached-document row to render on the detail.
- No fixed sleeps; all waits are conditional.
