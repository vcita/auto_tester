# Setup: Unregister Online (isolated account)

Prepares the isolated account for the back-office + client-portal unregistration and
online-payment flow.

## Steps

1. Deny the `point_of_sale` feature flag (API) so the remaining attendee is paid through
   the legacy take-payment record dialog (not POS).
2. Log in to the isolated account.
3. Create a `$100` "require to pay" event service (API).
4. Create a `user_staff` staff member (API).
5. Create three clients (API): `silvan goodbye`, `judi babish-moshe`, `nir karpin` — each
   with a client-portal token for the CP self-cancel / conversation checks.
6. Schedule the event instance for the service (API).

## Stored in context (`context["schedule_events"]`)

- `service` — event service (name, id, price).
- `staff` — `user_staff` staff member.
- `clients` — dict keyed by full name, each with `id`, `full_name`, `email`, `token`.
- `event_uid` — scheduled event instance uid.
