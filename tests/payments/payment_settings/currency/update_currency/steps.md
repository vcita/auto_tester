# Currency - update default currency

Migrated from `automation-js/features/salsa/payments_settings.feature` scenario 1
("Currency - update default currency").

## Objective
Update the business default currency (USD -> EUR) and verify it is reflected on newly
scheduled meetings.

## Preconditions (from _setup)
- Isolated US account (default currency USD).
- $100 service `test service` and client `first1 last1` created via API.

## Steps
1. Assert the default currency is **USD**.
2. Schedule a meeting and verify its currency is **USD**.
3. Set the default currency to **EUR** (propagated to existing services).
4. Assert the default-currency read-back is **EUR**.
5. Schedule another meeting and verify it reflects **EUR**.

## Notes
- The legacy scenario only asserted the meeting was created (the currency column was a
  no-op without `meeting_price`, see AUTO-772). This migration is strictly stronger: it
  verifies the default-currency change via API read-back and on the scheduled meeting.
