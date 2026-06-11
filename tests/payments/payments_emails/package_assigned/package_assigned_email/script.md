# Script: Package assigned to client

Playwright-oriented HOW for `package_assigned_email`. Reuses payments_emails_api
(assign_seeded_package -> account_api.assign_package_to_client) and email_api.

## Preconditions (from _setup)

- Isolated account, logged in.
- Client "first last", suggest-to-pay $100 service "service", package "package"
  (specific, 2 credits, $150) created but not assigned.

## Actions and assertions

1. `assign_seeded_package(context)`
   - POST /platform/v1/payment/client_packages assigning the package to the client
     (the platform sends the client the package-information email on assignment).
2. `wait_for_email(context, 'Your new "package" package information and details')`
   (exact subject).

## Notes / waits

- The assignment is the action under test, performed via API (the legacy assigns
  via the client-card UI dialog; the platform sends the same client email either
  way). If a future backend change stops sending the email on the API assign, fall
  back to the UI assign (Client card -> Payments -> add package).
- Email delivery is async; verified via the bounded `email_api` poll. No UI waits.
