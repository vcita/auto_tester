# Upgrade Account With Long Country Name — Steps (WHAT)

Migrated from automation-js `features/maestro/upgrade_page.feature` scenario 2
("Upgrade account with long country name").

## Preconditions (setup)
- A fresh **Trial** account exists with the business country set to a long name:
  **"Bolivia, Plurinational State of"** and the `hide_register_wizard` feature flag.
- Logged in to that account in Frontage.

## Steps
1. Open the upgrade page (`Settings → Upgrade your account`).
2. Choose the **enterprise_single** plan and click its "Get it" button.
3. On the Recurly checkout page, enter:
   - First name: `Automation`
   - Last name: `long country`
   - Credit card: `4111 1111 1111 1111`, expiry `02 / next year`, CVV `325`, postal code `34241`.
4. Submit the payment / agree & subscribe.

## Expected results
- The success page reports the account package is **"vcita Platinum Single (Annual)"**,
  proving the long country name does not break the upgrade flow.
