# Send Card on File Request — Script

Back-office UI flow on the client page (POV > Angular > Vue nesting; the payment
methods box and the add-payment-method dialog live in the inner Vue iframe), plus
an API email check. Setup connects the mock gateway and creates the client. All
UI waits are condition-based and capped at 5s (the client-page load uses a 15s
page-readiness budget for the triple-iframe mount).

## Locators (legacy data-qa, via `card_on_file_ui.py`)

- Client Payments tab: `div.v-tab:has-text("Payments")`.
- Add-card empty-state CTA: `div.empty-state-cta.empty-state-content`.
- Add-payment-method dialog: `[data-qa="add-payment-method-dialog"]`.
- "Request card" segment: `[data-qa="VcSegmentedControl-item-1"]` (defaults to the email channel, prefilled with the client's email).
- Send button: `[data-qa="vc-footer-Send request"]`.
- Pending-request label: `.card-request__description > div`.

Setup-gated by feature flags: the redesigned dialog needs the payments checkout/
gateway rollout flags, and the request is server-gated by `cof_invite` (without it
the request returns HTTP 422, shown as a misleading "Invalid email" toast).

## Steps

1. **Send request** — `send_card_on_file_request(page, context, client_id)`:
   navigate to `/app/clients/{id}`, open the Payments tab, click the add-card CTA,
   wait for the dialog, select the "Request card" segment, click "Send request".
2. **Verify on client** — `read_card_request_text(page)` resolves the
   `.card-request__description > div` label across frames (its appearance is the
   request-sent readiness signal). Assert it starts with `Card request sent on`
   and contains today's date in US Eastern (`%b %d`, e.g. `Jun 01`).
3. **Verify email** — `wait_for_email_subject(context, "Confirm your preferred payment method")`
   polls `GET /infra/automation/message/content?business_uid=<pivot_uid>` until the
   confirmation email arrives. The inbox is directory-scoped, so it authenticates with
   a directory token minted from `context["directory_id"]` via `POST /platform/v1/tokens`.

## Scope preservation vs legacy

- The request is sent through the UI (legacy `sends a new request to save card on file`).
- The client-card pending-request label and the confirmation email are both
  asserted, matching the legacy `client card displays requested card on file` and
  `client gets email with subject` steps.
- Legacy compared the label to `Card request sent on <Mon DD>` in the business
  timezone; the same date is asserted (US Eastern), with a no-leading-zero fallback.
