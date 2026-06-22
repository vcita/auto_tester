# Script — deny_payments_view

Phase 2 (HOW). Helpers in `payment_settings_api.py` / `payment_settings_cp.py`.

## Steps 1 & 3 — Payments action presence in CP
```python
payments_action_visible(page, context, token)
# open_portal (reused) -> #cp_iframe -> [data-qa='client-area-menu-payments'] count > 0
```

## Step 2 — deny view payments (API)
```python
set_allow_view_payments(context, False)
# POST /platform/v1/payment/settings {payment_settings:{allow_view_payments:false}}
```
