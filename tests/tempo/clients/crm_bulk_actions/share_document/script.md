# Script — Share Document From CRM (Bulk Action)

Playwright-oriented HOW for `test.py`. Helpers live in
`tests/clients/crm_bulk_actions/crm_bulk_helpers.py`.

## API setup
- `account_api.create_client(context, first, last, email)` ×2 → `POST /platform/v1/clients`.
  Names/emails carry a per-test run token so rows are unique on the shared
  isolated account. The 2nd client is the "current client" (legacy `this.currentClient`).

## UI flow (CRM is the POV Vue page at `/app/clients`; top-level, no iframe)
- `open_clients_list` → goto `/app/clients`, wait `.table-actions__filter` + no skeleton.
- `select_all_pages` → `[data-qa="checkbox-dropdown-icon"]` → `[data-qa="item-all"]`;
  wait `[data-qa="summary-text"]` contains `SELECTED`.
- `bulk_share_document(file_path)` →
  `[data-qa="bulk-action-button-more"]` → `[data-qa="item-share_document"]`;
  the dialog is in `iframe[title="angularjs"] -> #vue_wizard_iframe`:
  `set_input_files` on `[data-qa="vc-dropzone--input"]`, check `[data-qa="notify-by-email"]`,
  click `[data-qa="vc-footer-Share"]` (wait enabled), then wait the Share button hidden
  (POV routes to `/app/documents` on success).

## Assertions
- `open_client_card(client_id)` → goto `/app/clients/{id}`, wait `.conversation-content`
  in `#vue_iframe_layout`.
- `assert_conversation_has_document` → `.conversation-content .file-name` contains
  `clientDoc.pdf` (bounded reload-recheck for async communication propagation).
- `assert_document_status` → goto `/app/documents`; in `#vue_iframe_main`, the
  `.list-item` containing `clientDoc.pdf` → `[data-qa="docuform-status"]` equals
  `PENDING REVIEW` (case-insensitive; rendered uppercase via CSS).

## Selector / wait policy
- `data-qa` first, then stable CSS (`.conversation-content`, `.file-name`,
  `.list-item`) carried over from the legacy page objects and verified live.
- All UI waits ≤5s; no fixed sleeps. Conversation/document propagation uses a
  bounded reload-and-recheck loop (≤2 retries) for the async communication index.
