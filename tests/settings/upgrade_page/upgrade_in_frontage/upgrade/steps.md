# Upgrade Account In Frontage — Steps (WHAT)

Migrated from automation-js `features/maestro/upgrade_page.feature` scenario 1
("Upgrade account in Frontage").

## Preconditions (setup)
- A fresh **Trial** account exists (isolated, `package_subscription_id: 28`).
- Logged in to that account in Frontage.

## Steps
1. Open the upgrade page (`Settings → Upgrade your account`).
2. Choose the **enterprise_single** plan and click its "Get it" button.
3. On the Recurly checkout page, enter:
   - First name: `Automation`
   - Last name: `upgrade page`
   - Credit card: `4111 1111 1111 1111`, expiry `02 / next year`, CVV `325`, postal code `34241`.
4. Submit the payment / agree & subscribe.

## Expected results
- The success page reports the account package is **"vcita Platinum Single (Annual)"**.
- The business plan (read back via API) is **"Platinum Single"**.
