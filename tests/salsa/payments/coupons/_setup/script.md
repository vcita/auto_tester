# Coupons Setup — Script

All prerequisites are provisioned via the account API (mirrors the legacy
`coupons.feature` Background, which is `via API`). The feature under test
(coupon create/apply) is exercised through the UI in the test itself.

## Steps

1. **Login** — `fn_login(page, context, username, password)` with the isolated account credentials injected by the runner.
2. **Services** — for each of `appointment_1/2/3`, `coupons_api.create_paid_service(context, name)`:
   - `POST /v2/settings/services` with `charge_type="paid"`, `price="100"`, `service_type="appointment"`, last category uid, first staff uid.
3. **Client** — `coupons_api.create_client(context, "first", "last", unique_email("test"))`:
   - `POST /platform/v1/clients` with `source_name="automation"`.
4. **Appointments** — for each service, `coupons_api.create_appointment(context, service, client, days_ahead)`:
   - `POST /business/scheduling/v1/bookings` with `business_id`, `staff_id`, future `start_time` (localized US Eastern → UTC), `service_id`, `client_id`.
   - The booking inherits the service price/charge_type, producing a `NOT YET DUE` $100 payment request. Store `booking["id"]`.

## Context outputs

- `coupon_services`: alias → service dict
- `coupon_client`: client dict (with `full_name`)
- `coupon_bookings`: alias → appointment id
