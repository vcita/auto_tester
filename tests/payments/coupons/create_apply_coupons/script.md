# Create and Apply Coupons — Script

Pure back-office UI flow inside the Angular frontage iframe (Angular Material
`md-*` widgets). Setup provisions services/client/appointments via API. All waits
are condition-based and capped at 5s.

## Locators (legacy data-qa / Angular selectors, via `coupons_helpers.py`)

- Coupons settings: `[data-qa="action-button-coupons-new"]`; dialog `md-select[name="coupon_type"]`, `input[name="name"]`, `input[name="amount"]`, save `button[ng-click="save(clientForm)"]`; share dialog dismiss `md-dialog-actions button[ng-click="cancel()"]`.
- Coupon list item `.list-item`; title `div.titles .md-title .title`; discount `.additional-fields-container .additional-field`.
- Appointment payment card: more actions `[data-qa="ps-more-actions"]`; apply `[data-qa="apply_coupon"]`; coupon picker `md-select[ng-model="coupon"]`; save `md-dialog-actions button[ng-click="save()"]`; status `div.status-payment`; balance `div.balance-due-amount`.

## Steps

1. **Open settings** — `open_coupons_settings(page)` navigates to `/app/settings/coupons?tab=coupons` and waits for the create button.
2. **Create coupons** — for each `(type, name, amount)`, `create_coupon`:
   - click create, pick coupon type via the `md-select` option (by role `option`), fill name + amount, click save.
   - the share/promote dialog opening is the save confirmation; dismiss it ("Maybe later"), then wait for the named row to appear.
3. **Verify list** — `assert_coupons` polls the list (≤5s) until each name maps to its expected discount label.
4. **Apply + verify** — for each appointment alias:
   - `open_appointment(page, base_url, booking_id)` → `/app/appointments/{id}`, wait for the balance element.
   - `apply_coupon` opens more-actions → apply coupon → pick the coupon in the `md-select` → save → best-effort toast wait.
   - `assert_payment_request` asserts the status (`NOT YET DUE` / `PAID`) and the balance-due amount within 5s (updates reactively).

## Scope preservation vs legacy

- Coupons are created through the UI (legacy `user creates new coupon`), not the API shortcut.
- List discounts and all three payment-request states/amounts are asserted, matching the legacy `search coupons` and `appointment's payment request is` tables.
