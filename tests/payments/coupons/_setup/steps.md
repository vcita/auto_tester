# Coupons Setup — Steps

Prepares an isolated account so the coupon test starts from a deterministic state.

1. Log in to the isolated account.
2. Create three paid "suggest to pay" appointment services priced at $100 (`appointment_1`, `appointment_2`, `appointment_3`).
3. Create one client (`first last`).
4. Schedule one future appointment per service for that client, so each appointment shows a `NOT YET DUE` $100 payment request.

Saves to context: `coupon_services`, `coupon_client`, `created_client_name`, `coupon_bookings` (alias → appointment id).
