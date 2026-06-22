# Changelog — Create Client Through All Channels

## 2026-06-09 — Initial migration scaffolding (VCITA2-14007)
- Migrated from `automation-js/features/steps/client-create-new-CRM.feature`
  (Scenario: "creation of a client - new CRM").
- New subcategory `tests/clients/client_create_paths` (isolated account). `_setup`
  logs in to the business owner account; the test exercises all four channels.
- Helpers:
  - `client_create_helpers.py` — new-CRM dialog create, CRM All-tab search (bounded
    retry for search-index lag), and email delivery via the internal infra automation
    endpoint (directory token minted via admin `POST /platform/v1/tokens`), matching
    legacy `api/email.js`.
  - `client_create_channels.py` — Vitrage livesite leave-details (`cp_iframe`) and the
    client-portal conversation assertion.
  - Contact-form widget submit reused from the C3 `contact_form_helpers`.
- Channels covered: new-CRM dialog, API, livesite leave-details (client + business
  emails), contact-form widget (client + business emails); each verified searchable
  in the CRM.
- Client-portal conversation assertion (legacy line 33) faithfully replicated: opens
  the Client Portal editor (`/app/client-portal-editor`), clicks "View as demo client"
  (captures the popup window via `expect_page`), opens the conversation page
  (`[data-qa="headerChatBtn"]`), and asserts a `[data-qa="bubble-header"]` titled
  "Hi Contact Request". This is a positive assertion (must find the title), so it
  cannot pass vacuously. Frame lookups scan `page.frames` to tolerate angular/vue
  iframe nesting and name changes.
- Validation: 3 clean focused runs (78s, 73s, 71s) on integration with the full
  scope (4 create channels, 4 email assertions, 4 CRM searches, 1 portal conversation).

## 2026-06-09 — Code-review fixes (Bugbot)
- Fixed fenv livesite host: `vitrage_base` now follows the shared autotester convention
  (app-<name> → vitrage-<name> on fenv) instead of `live-<name>`, which only resolved on
  integration. Dropped the custom `_swap_subdomain`.
- Made the duplicate client "Thank you for your message" assertion non-vacuous: the widget
  pass now requires `min_count=2`, so it observes a new email rather than re-counting the
  livesite one.
