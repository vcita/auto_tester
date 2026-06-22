# Changelog: estimate_mail_cp

## 2026-06-11 - Initial migration (VCITA2-14027)

Migrated from `automation-js/features/salsa/payments-emails.feature` scenario 6
("Client receives estimate mail, and opens CP page").

- **Setup** (API): client "first last"; product "product21" ($10,
  "description for payable item21").
- **Action**: `create_estimate_email_action` ->
  `deposits_api.create_estimate_via_api` (send_email=true). The platform mails the
  client the "New estimate from <business>" email.
- **Assertions**:
  - `wait_for_email("New estimate from ", match="prefix")` (dynamic business suffix).
  - `assert_cp_estimate_from_email`: opens the CP estimate link (client JWT) in a
    fresh context and asserts title "bestimate #0000001", price $10, client
    "first last", item product21 ("description for payable item21", $10), and the
    pending_client_action APPROVE/REJECT actions (legacy `_getStatus` mapping).

### Wait audit
- Email verified via bounded `email_api` poll (async-email exception).
- CP page: waits for the entity page visible + a bounded text-settle loop
  (<= CP nav timeout); no fixed sleeps; no retries beyond these bounded waits.

### Reuse
- `payments_emails_api.seed_client_and_product` / `create_estimate_email_action`.
- `deposits_api.create_estimate_via_api`, `deposits_api.create_product`.
- `email_api.wait_for_email` / `email_link`.
- `payments_emails_confirm.assert_cp_estimate_from_email` (CP estimate display,
  adapted from the legacy CPsEstimatePage parser).
