# Event payment request: create, edit, cancel

Migrated from `automation-js/features/salsa/event-payments.feature` — scenario
"payment request for created, edited, and canceled event" (VCITA2-13856).

## Steps
1. The registered attendee's event payment request is **DUE / $10.00 / first last / r2p_event**.
2. Edit the payment request amount to **50** → request is **DUE / $50.00**.
3. Cancel (waive) the payment request → request is **CANCELLED / $50.00**.

## Notes
- The event, attendee and "require to pay" $10 service are seeded via API in setup.
- Editing/cancelling operate on the first (only) attendee, matching the legacy flow.
