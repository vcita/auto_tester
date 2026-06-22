# Override Price Type

## Objective
Verify that overriding the price type while scheduling an appointment produces the expected meeting price, regardless of the service's configured payment setting.

## Prerequisites
- Logged in with a client `first1 last1` and six API-created services (from `_setup`).

## Steps
1. Schedule an appointment for each of three services, overriding the price type:
   - `require2pay` → override to "display free"
   - `suggest2pay` → override to "display for a fee"
   - `displayFee` → override to "dont display"
2. Schedule an appointment for each of three more services, overriding to a fixed price with an amount:
   - `variedPrice` → require to pay, amount 65
   - `displayFree` → display a fee, amount 97
   - `noDisplay` → suggest to pay, amount 25
3. Open each created appointment and verify the meeting price:
   - require2pay → Free, suggest2pay → (blank), displayFee → (blank)
   - variedPrice → 65 USD, displayFree → 97 USD, noDisplay → 25 USD

## Expected Result
- Each appointment reflects the overridden price type/amount, not the service default.

## Context Updates
- None (terminal scenario for this isolated subcategory).
