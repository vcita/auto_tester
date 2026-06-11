# Changelog: package_assigned_email

## 2026-06-11 - Initial migration (VCITA2-14027)

Migrated from `automation-js/features/salsa/payments-emails.feature` scenario 5
("Package assigned to client").

- **Setup** (API): client "first last"; suggest-to-pay $100 service "service";
  specific-service package "package" (2 credits, $150), created not assigned.
- **Action**: `assign_seeded_package` -> `account_api.assign_package_to_client`
  (API). The platform sends the client the package-information email on assignment.
- **Assertion**: `wait_for_email` for exact subject
  `Your new "package" package information and details`.

### Wait audit
- No UI waits. Email verified via bounded `email_api` poll (async-email exception).
- No fixed sleeps; no retries beyond the email poll.

### Reuse
- `payments_emails_api.seed_client_and_service` / `seed_package` /
  `assign_seeded_package` (wrapping `account_api` package + assignment helpers).
- `email_api.wait_for_email`.
