# Script — Send Message From CRM (Bulk Action)

Playwright-oriented HOW for `test.py`. Helpers live in
`tests/clients/crm_bulk_actions/crm_bulk_helpers.py`.

## API setup
- `account_api.create_client(context, first, last, email)` ×2 → `POST /platform/v1/clients`.
  Names/emails carry a per-test run token; the message targets the 2nd client
  (legacy `first02 last02`).

## UI flow (CRM top-level POV page at `/app/clients`)
- `open_clients_list`.
- `select_client(full_name)` → row `[data-qa="CrmTable-All"] tbody tr` filtered by the
  client's full name → click the rendered checkbox wrapper
  `.v-input--selection-controls__input` (Vuetify hides the real input behind an icon);
  wait `[data-qa="summary-text"]` contains `SELECTED`.
- `bulk_send_message("hi", "hello")` → `[data-qa="bulk-action-button-message"]`;
  dialog in `iframe[title="angularjs"] -> #vue_wizard_iframe`:
  fill `[data-qa="message-dialog-subject"]`, focus the contenteditable body
  `[data-testid="conversation-input-dialog-message-page_textarea"]` and type the content,
  click `.message-dialog button.send-btn`, wait it hidden.

## Assertions
- `open_client_card(client_id)` → goto `/app/clients/{id}`, wait `.conversation-content`
  in `#vue_iframe_layout`.
- `assert_last_message_bubble(subject, content)` → last `.bubble-row`: `.bubble-header`
  equals `hi`, `.bubble-text-row` equals `hello` (bounded reload-recheck for async
  communication propagation).

## Selector / wait policy
- `data-qa` first, then stable CSS (`.message-dialog`, `.bubble-row`, `.bubble-header`,
  `.bubble-text-row`) carried over from the legacy page objects and verified live.
- All UI waits ≤5s; no fixed sleeps; bubble propagation uses bounded
  reload-and-recheck (≤2 retries).
