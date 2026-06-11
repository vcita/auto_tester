"""UI helpers for the document-templates-auth migration (VCITA2-14062).

Covers the legacy `document-templates-auth.feature` chain:
- Upload a document to My Documents (legacy Documents.uploadToMyDocuments +
  UploadDocumentDialog) and read the standard template list.
- Grab a document's public link (legacy Documents.copyLink + CopyLinkDialog) and
  verify a client can access the grabbed link (legacy `client accesses grabbed link`).

The upload flow + frame topology were verified live during the sibling
attach-document-to-invoice migration:
- Documents page / My Documents side pane: iframe[title="angularjs"] (Frontage frame).
- Upload dialog:                            iframe[title="angularjs"] -> #vue_wizard_iframe.
"""
from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

UI_TIMEOUT = 5_000
NAV_TIMEOUT = 20_000
# The legacy Angular actions menu and copy-link dialog are slow to render under
# full-suite load (passes well under 5s in isolation, but the kebab menu / dialog /
# link field were observed timing out at 5s during back-to-back runs). Use a wider
# bounded wait for that specific interaction.
GRAB_TIMEOUT = 15_000

UPLOAD_BTN = "//div[contains(@class, 'upload-button')]//button[@data-qa='add']"
DROPZONE = '[data-qa="vc-dropzone--input"]'
UPLOAD_CONFIRM = 'button[data-qa="vc-footer-Upload"]'
MY_DOCS_ITEM = ".side-pane-item"
MY_DOCS_NAME = ".side-pane-name"
# The desktop actions row has a Share button and a kebab (3-dots) menu; the kebab opens
# the actions menu that includes "Copy public link" (legacy action "grab").
DOC_ACTIONS_KEBAB = ".side-pane-actions button.my-documents-button:has(md-icon.icon-dots-three-vertical)"
COPY_LINK_OPTION = "Copy public link"

# CopyLinkDialog (legacy copyLinkDialog.js)
LINK_DIALOG = '[data-qa="vc-input-modal"]'
LINK_TEXT = ".link-container__link"
LINK_COPY_BTN = 'button[data-qa="vc-footer-Copy"], button[data-qa="vc-btn"]'


def _angular_frame(page: Page):
    return page.frame_locator('iframe[title="angularjs"]')


def _wizard_dialog_frame(page: Page):
    return page.frame_locator('iframe[title="angularjs"]').frame_locator("#vue_wizard_iframe")


def _app_base(page: Page) -> str:
    return page.url.split("/app/")[0] if "/app/" in page.url else page.url.rstrip("/")


def open_documents(page: Page) -> None:
    page.goto(f"{_app_base(page)}/app/documents", wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
    page.wait_for_url("**/app/documents**", timeout=NAV_TIMEOUT, wait_until="domcontentloaded")


def upload_to_my_documents(page: Page, file_path: str) -> None:
    """Upload a file to My Documents via the documents-page upload dialog (legacy
    uploadToMyDocuments)."""
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


def _standard_template(page: Page, file_name: str):
    return _angular_frame(page).locator(MY_DOCS_NAME).filter(has_text=file_name).first


def assert_in_standard_templates(page: Page, file_name: str) -> None:
    """Assert the uploaded file appears in the standard (My Documents) template list."""
    try:
        _standard_template(page, file_name).wait_for(state="visible", timeout=NAV_TIMEOUT)
    except PlaywrightTimeoutError as exc:
        raise AssertionError(
            f"Document template {file_name!r} not shown in the standard template list"
        ) from exc


def grab_document_link(page: Page, file_name: str) -> str:
    """Grab the public link of a My-Documents template (legacy copyLink): open the
    template's actions menu, choose "Copy public link", and read the link from the
    copy-link dialog."""
    angular = _angular_frame(page)
    item = angular.locator(MY_DOCS_ITEM).filter(has_text=file_name).first
    item.wait_for(state="visible", timeout=NAV_TIMEOUT)
    item.hover()
    kebab = item.locator(DOC_ACTIONS_KEBAB).first
    kebab.wait_for(state="visible", timeout=GRAB_TIMEOUT)
    kebab.click()
    copy_option = angular.get_by_role("menuitem", name=COPY_LINK_OPTION).first
    if copy_option.count() == 0:
        copy_option = angular.get_by_text(COPY_LINK_OPTION, exact=True).first
    copy_option.wait_for(state="visible", timeout=GRAB_TIMEOUT)
    copy_option.click()

    return _read_link_from_dialog(page)


def _read_link_from_dialog(page: Page) -> str:
    dialog = _wizard_dialog_frame(page).locator(LINK_DIALOG).first
    dialog.wait_for(state="visible", timeout=NAV_TIMEOUT)
    link_text = _wizard_dialog_frame(page).locator(LINK_TEXT).first
    link_text.wait_for(state="visible", timeout=GRAB_TIMEOUT)
    link = (link_text.inner_text() or "").strip()
    if not link:
        link = (link_text.get_attribute("value") or "").strip()
    if not link:
        raise AssertionError("Copy-link dialog did not expose a document link")
    return link


def assert_link_accessible(page: Page, link: str, file_name: str) -> None:
    """Verify a client (no business session) can access the grabbed public link
    (legacy `client accesses grabbed link`)."""
    context = page.context.browser.new_context()
    visitor = context.new_page()
    try:
        response = visitor.goto(link, wait_until="domcontentloaded", timeout=NAV_TIMEOUT)
        if response is not None and response.status >= 400:
            raise AssertionError(
                f"Grabbed link returned HTTP {response.status} for {link!r}"
            )
        body = (visitor.locator("body").inner_text(timeout=UI_TIMEOUT) or "").lower()
        error_markers = ("not found", "page not found", "404", "access denied", "unauthorized")
        if any(marker in body for marker in error_markers):
            raise AssertionError(f"Grabbed link {link!r} shows an error page")
    finally:
        context.close()
