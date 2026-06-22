# Script — no_payment_error

Phase 2 (HOW). Helpers in `payment_settings_api.py`, `payment_settings_ui.py`,
`payment_settings_cp.py`, and the reused `tips_gateway.connect_mock_gateway`.

## Step 1 — provider banner
```python
assert_provider_banner_displayed(page, context)  # [data-qa='online-payments-tab-banner']
```

## Step 2 — connect gateway
```python
connect_mock_gateway(page, context)  # reused, proven UI helper
```

## Step 3 — disable credit card (API)
```python
set_allow_credit_card(context, False)
# POST /platform/v1/payment/settings {payment_settings:{allow_credit_card:false}}
```

## Step 4 — CP make-payment → no-payment error
```python
submit_payment_and_expect_error(page, context, pay_for=..., amount="100", email=..., first_name="first1")
# open_payment_form (/site/{pivot}/make-payment?title=&amount=) -> fill -> checkout
# -> assert error dialog ([role='document'] / no-payment-method message)
```
