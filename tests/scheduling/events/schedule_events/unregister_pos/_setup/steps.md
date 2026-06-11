# Setup: Unregister POS (isolated account)

Prepares the isolated account for the back-office + client-portal unregistration and
Point-of-Sale payment flow.

## Steps

1. Log in to the isolated account (`point_of_sale` stays enabled — the default — so the
   remaining attendee is paid through Point of Sale).
2. Create a `$100` "require to pay" event service (API).
3. Create a `user_staff` staff member (API).
4. Create three clients (API): `silvan goodbye`, `judi babish-moshe`, `nir karpin` — each
   with a client-portal token for the CP self-cancel check.
5. Schedule the event instance for the service (API).

## Stored in context (`context["schedule_events"]`)

- `service` — event service (name, id, price).
- `staff` — `user_staff` staff member.
- `clients` — dict keyed by full name, each with `id`, `full_name`, `email`, `token`.
- `event_uid` — scheduled event instance uid.
