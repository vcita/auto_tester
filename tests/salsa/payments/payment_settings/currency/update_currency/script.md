# Script — update_currency

Phase 2 (HOW). API-only; helpers in `payment_settings_api.py`. Endpoints confirmed
against frontage pov `paymentSettingsService.js`.

## Steps 1 & 4 — default currency read-back
```python
get_default_currency(context)  # GET /platform/v1/payment/settings -> payment_settings.currency
```

## Steps 2 & 5 — schedule + verify meeting currency
```python
meeting = create_appointment_via_api(context, service=..., client=...)
_booking_currency(context, meeting)  # booking.currency, else GET bookings/{id}
```

## Step 3 — set EUR
```python
set_default_currency(context, "EUR")
# POST /platform/v1/payment/settings {payment_settings:{currency:"EUR"}}
# PUT  /platform/v1/payment/settings/update_default_currency {}  (propagates to services)
```
