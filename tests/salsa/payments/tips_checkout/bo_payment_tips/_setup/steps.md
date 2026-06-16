# Setup: BO Payment With Tips

Prepares a fresh isolated account for the back-office tipping scenario
(`tips.feature` scenario 1), with Point of Sale denied so payment uses the
legacy close-balance / record-payment dialogs.

## Steps

1. Deny the **point_of_sale** feature flag.
2. Enable the tips feature flags (tips settings, BO follow-up tip, checkout v2,
   gateway platform).
3. Log in to the isolated account.
4. Assign the **tips** app to the account (API).
5. Set tip options **55, 66, 77** with **tips enabled for back office** (API).
6. Create the client **first last** (API).
7. Create a **suggest to pay** service **service** priced **$100** (API).
8. Create a **specific** package **package** (2 credits of **service**) priced
   **$150** and assign it to **first last** (API).
9. Schedule a past appointment (previous month, day 10) for **first last** on
   **service** (API) so the service + package balances are payable.
