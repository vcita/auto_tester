# Script: Client receives estimate mail, and opens CP page

Playwright-oriented HOW for `estimate_mail_cp`. Reuses payments_emails_api
(create_estimate_email_action -> deposits_api.create_estimate_via_api) and email_api,
and the CP estimate assertion in payments_emails_confirm.assert_cp_estimate_from_email.

## Preconditions (from _setup)

- Isolated account, logged in.
- Client "first last"; product "product21" ($10, "description for payable item21").

## Actions and assertions

1. `create_estimate_email_action(context, title="bestimate", address="Babylon, persia")`
   - POST /platform/v1/estimates with send_email=true (platform mails the client).
2. `wait_for_email(context, "New estimate from ", match="prefix")` -> capture the email.
   - Business name suffix is dynamic on isolated accounts (`Auto_<category>_<ts>`),
     so only the stable prefix is asserted.
3. `email_link(email)` -> extract the CP estimate URL (carries the client JWT).
4. `assert_cp_estimate_from_email(page, url, title="bestimate", number="#0000001",
   price="10", client="first last", items=[{product21, desc, 10}],
   status_actions=["APPROVE", "REJECT"])`.

## CP estimate page locators (from legacy CPsEstimatePage)

- iframe `#cp_iframe`; entity page `.payment-entity-page` / `span.payment-title`.
- Asserted by visible text on the entity body (title, #number, $price, client name,
  item name/description/$price). pending_client_action -> APPROVE / REJECT actions
  (legacy `_getStatus` maps pending_client_action -> ['APPROVE','REJECT'] with no
  deposit); matched case-insensitively.

## Notes / waits

- #0000001 is deterministic: the isolated account's first (only) estimate.
- Email delivery is async -> bounded `email_api` poll. CP page load waits on the
  entity page being visible plus a bounded text-settle loop (no fixed sleeps).
- A fresh browser context opens the CP link so the BO session does not leak in.
