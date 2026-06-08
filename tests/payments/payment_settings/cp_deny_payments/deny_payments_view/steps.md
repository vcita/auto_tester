# Client Portal - deny clients from viewing their payments

Migrated from `automation-js/features/salsa/payments_settings.feature` scenario 3
("Client Portal - deny clients from viewing their payments in client portal").

## Objective
Deny clients from viewing payments in the client portal and verify the "Payments" action
is no longer available.

## Preconditions (from _setup)
- Client created via API (with portal token).

## Steps
1. Open the client portal as the client and verify the **Payments** action is present by default.
2. Deny clients from viewing payments via the payment settings API (`allow_view_payments=false`).
3. Re-open the client portal and verify the **Payments** action is no longer shown.

## Notes
- The legacy only asserted absence; this migration first confirms presence by default,
  making the absence assertion robust (no false positive).
