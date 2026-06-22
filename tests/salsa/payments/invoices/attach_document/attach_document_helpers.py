"""UI helpers for the attach-document-to-invoice migration (VCITA2-14061).

Covers the legacy `attach-document-to-invoice.feature` chain:
- Documents page "upload to My Documents" (legacy Documents.uploadToMyDocuments +
  UploadDocumentDialog): open the documents page, open the upload dialog, drop the
  file, confirm.
- Invoice wizard "Attached Documents" -> add from My Documents (legacy
  AddDocumentToInvoice.attachDocToInvoice + AddInternalDocumentDialog.addFromMyDocument).
- Save-draft / send actions on the POV itemizable wizard and the invoice-detail
  "attached document" assertion (legacy invoice.getDocumentNameAttachedToInvoice).

Reuses the migrated invoice wizard helpers in
tests/payments/invoices/invoice_billing_ui.py.

Frame topology (legacy + crm_bulk_actions precedent):
- Documents list:   iframe[title="angularjs"] -> #vue_iframe_main
- Upload / wizard dialogs: iframe[title="angularjs"] -> #vue_wizard_iframe
"""
import re
import time

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from tests.salsa.payments.invoices.invoice_billing_ui import (
    _app_base,
    _find_invoice,
    _page_text,
    add_existing_item,
    billing_scope,
    open_new_invoice,
    set_title,
)

UI_TIMEOUT = 5_000
NAV_TIMEOUT = 20_000
STATE_TIMEOUT = 15_000
POLL = 0.5

# Documents page (legacy Documents page object). Uploaded files land in the
# "MY DOCUMENTS" side pane (Angular Frontage frame), NOT the shared/internal list
# (#vue_iframe_main), so verification reads the side-pane template names.
UPLOAD_BTN = "//div[contains(@class, 'upload-button')]//button[@data-qa='add']"
DROPZONE = '[data-qa="vc-dropzone--input"]'
UPLOAD_CONFIRM = 'button[data-qa="vc-footer-Upload"]'
MY_DOCS_NAME = ".side-pane-name"

# Invoice wizard attach. The "Attached Documents" section is expanded by default and
# shows a "+ Add Document" button; clicking the header would collapse it, so we target
# the button directly and expand only if it is hidden.
ATTACH_SECTION_HEADER = "Attached Documents"
ADD_DOC_BUTTON = "Add Document"
# "Add/Share Document" dialog (in the wizard iframe): "FROM 'MY DOCUMENTS'" is the
# default mode; the file is chosen from a Material md-select, then confirmed with ADD.
PICK_DOC_SELECT = "md-select"
PICK_DOC_OPTION = "md-option"
PICK_DOC_CONFIRM = '[data-qa="confirm-button"]'
SAVE_DRAFT_BTN = "[data-qa='itemizable-dialog-secondary']"
SEND_BTN = "[data-qa='itemizable-dialog-main']"

# "From" billing address (required on a fresh account). Same toggle button enters edit
# and the From-fold header commits on collapse (legacy inputBillingAddress).
FROM_FOLD = '[data-qa="itemizable-from-fold"]'
FROM_ADDRESS_EDIT_BTN = '[data-qa="itemizable-from-business-address-edit-button"]'
FROM_ADDRESS_TEXTAREA = '[data-qa="itemizable-from-business-address-edit"] textarea'

# First-invoice numbering dialog (shown once on a fresh account, on the first save or
# send depending on the account's e-invoicing mode).
FIRST_INVOICE_DIALOG = '[data-qa="first-invoice-setup-dialog"]'
FIRST_INVOICE_CONFIRM = re.compile(r"^(Save|Confirm|Continue|OK|Done)$", re.I)

# Invoice detail attached-document (legacy invoice page object)
INVOICE_DOC_ITEM = ".invoice-document-item-content"
INVOICE_DOC_EMPTY = '[data-qa="document-list-empty"]'


def _angular_frame(page: Page):
    return page.frame_locator('iframe[title="angularjs"]')


def _wizard_dialog_frame(page: Page):
    return page.frame_locator('iframe[title="angularjs"]').frame_locator("#vue_wizard_iframe")


# --------------------------------------------------------------------------- #
# Documents page: upload to My Documents
# --------------------------------------------------------------------------- #
def open_documents(page: Page) -> None:
    page.goto(f"{_app_base(page)}/app/documents", wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
    page.wait_for_url("**/app/documents**", timeout=NAV_TIMEOUT, wait_until="domcontentloaded")


def upload_to_my_documents(page: Page, file_path: str, file_name: str) -> None:
    """Open the documents page upload dialog, drop the file, confirm, and wait for
    the document to appear in the My Documents list (legacy uploadToMyDocuments)."""
    open_documents(page)
    upload_button = _angular_frame(page).locator(f"xpath={UPLOAD_BTN}").first
    upload_button.wait_for(state="visible", timeout=NAV_TIMEOUT)
    upload_button.click()

    dialog = _wizard_dialog_frame(page)
    dropzone = dialog.locator(DROPZONE)
    dropzone.wait_for(state="attached", timeout=UI_TIMEOUT)
    dropzone.set_input_files(file_path)
    confirm = dialog.locator(UPLOAD_CONFIRM)
    confirm.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.click()
    confirm.wait_for(state="hidden", timeout=NAV_TIMEOUT)
    _wait_doc_in_list(page, file_name)


def _wait_doc_in_list(page: Page, file_name: str) -> None:
    item = _angular_frame(page).locator(MY_DOCS_NAME).filter(has_text=file_name).first
    try:
        item.wait_for(state="visible", timeout=NAV_TIMEOUT)
    except PlaywrightTimeoutError as exc:
        raise AssertionError(
            f"Uploaded document {file_name!r} not shown in the My Documents side pane"
        ) from exc


# --------------------------------------------------------------------------- #
# Invoice wizard: attach a document from My Documents
# --------------------------------------------------------------------------- #
def attach_document(page: Page, wizard, file_name: str) -> None:
    """Attach a previously-uploaded My-Documents file to the open invoice wizard
    (legacy attachDocToInvoice -> addFromMyDocument)."""
    add_button = wizard.get_by_text(ADD_DOC_BUTTON, exact=False).first
    try:
        add_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    except PlaywrightTimeoutError:
        wizard.get_by_text(ATTACH_SECTION_HEADER, exact=False).first.click()
        add_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    add_button.click()
    _pick_from_my_documents(page, file_name)
    # After the picker closes the wizard renders the attached file name.
    wizard.get_by_text(file_name, exact=False).first.wait_for(state="visible", timeout=NAV_TIMEOUT)


def _pick_from_my_documents(page: Page, file_name: str) -> None:
    """Choose the file in the Angular Material "Add/Share Document" dialog (which lives
    in the angularjs frame, not the Vue wizard frame) and confirm with ADD."""
    dialog = _angular_frame(page)
    select = dialog.locator(f"md-dialog {PICK_DOC_SELECT}").first
    select.wait_for(state="visible", timeout=UI_TIMEOUT)
    select.click()
    # Material renders the md-select options in an overlay inside the same frame body.
    option = dialog.locator(PICK_DOC_OPTION).filter(has_text=file_name).first
    option.wait_for(state="visible", timeout=UI_TIMEOUT)
    option.click()
    confirm = dialog.locator(f"md-dialog {PICK_DOC_CONFIRM}").first
    if confirm.count() == 0:
        confirm = dialog.locator("md-dialog").get_by_role("button", name=re.compile(r"^Add$", re.I))
    confirm.first.wait_for(state="visible", timeout=UI_TIMEOUT)
    confirm.first.click()
    confirm.first.wait_for(state="hidden", timeout=NAV_TIMEOUT)


# --------------------------------------------------------------------------- #
# From billing address (required field)
# --------------------------------------------------------------------------- #
def _set_billing_address(wizard, address: str) -> None:
    """Set the required "From" billing address (legacy inputBillingAddress): expand the
    From fold, enter edit mode, type the address, then collapse the fold to commit."""
    fold = wizard.locator(FROM_FOLD).first
    fold.wait_for(state="visible", timeout=UI_TIMEOUT)
    fold.click()
    edit_button = wizard.locator(FROM_ADDRESS_EDIT_BTN).first
    edit_button.wait_for(state="visible", timeout=UI_TIMEOUT)
    edit_button.click()
    field = wizard.locator(FROM_ADDRESS_TEXTAREA).first
    field.wait_for(state="visible", timeout=UI_TIMEOUT)
    field.fill(address)
    # Collapsing the From fold commits the edited address (legacy clicks the header).
    fold.click()
    field.wait_for(state="hidden", timeout=UI_TIMEOUT)


# --------------------------------------------------------------------------- #
# Save / send + verify attachment
# --------------------------------------------------------------------------- #
def create_invoice_with_document(page: Page, context: dict, *, name: str, client_name: str,
                                 file_name: str, send: bool,
                                 billing_address: str | None = None,
                                 existing_items: list[str] | None = None) -> None:
    """Open a new invoice, set its title + billing address, add the line items, attach
    the My-Documents file, then save it as a draft (send=False) or send it (send=True).

    The "From" billing address is a required field on a fresh account, so it must be set
    before the invoice can be saved/sent (legacy passes billing_address="blablablabla")."""
    _, wizard = open_new_invoice(page, client_name)
    set_title(wizard, name)
    for item in existing_items or []:
        add_existing_item(wizard, item)
    if billing_address:
        _set_billing_address(wizard, billing_address)
    attach_document(page, wizard, file_name)
    button_selector = SEND_BTN if send else SAVE_DRAFT_BTN
    action = wizard.locator(button_selector).first
    action.wait_for(state="visible", timeout=UI_TIMEOUT)
    action.click()
    _dismiss_first_invoice_setup(billing_scope(page))
    page.wait_for_url("**/app/invoices/**", timeout=NAV_TIMEOUT, wait_until="domcontentloaded")


def _dismiss_first_invoice_setup(billing) -> None:
    """Dismiss the one-time first-invoice numbering dialog if it appears (accept the
    default #0000001). Stateless: safe to call after every save/send since the dialog
    can surface on either action depending on the account's e-invoicing mode."""
    dialog = billing.locator(FIRST_INVOICE_DIALOG).first
    try:
        dialog.wait_for(state="visible", timeout=2_000)
    except PlaywrightTimeoutError:
        return
    confirm = billing.get_by_role("button", name=FIRST_INVOICE_CONFIRM)
    if confirm.count() > 0:
        confirm.first.click(timeout=UI_TIMEOUT)
        dialog.wait_for(state="hidden", timeout=UI_TIMEOUT)


def assert_document_attached(page: Page, context: dict, *, title: str, number: int,
                             file_name: str) -> None:
    """Assert the invoice detail shows the attached document (legacy
    getDocumentNameAttachedToInvoice). Opens the invoice fresh by API id when needed."""
    display_name = f"{title} #{number:07d}"
    if display_name not in _page_text(page):
        invoice_id = _find_invoice(context, title).get("id")
        page.goto(f"{_app_base(page)}/app/invoices/{invoice_id}", wait_until="domcontentloaded")

    deadline = time.monotonic() + STATE_TIMEOUT / 1000
    last_text = ""
    while time.monotonic() < deadline:
        billing = billing_scope(page)
        doc_item = billing.locator(INVOICE_DOC_ITEM).filter(has_text=file_name).first
        try:
            if doc_item.is_visible():
                return
            last_text = (billing.locator(INVOICE_DOC_ITEM).first.text_content() or "").strip()
        except PlaywrightTimeoutError:
            pass
        time.sleep(POLL)
    raise AssertionError(
        f"Document {file_name!r} not attached to invoice {display_name!r}; saw: {last_text!r}"
    )
