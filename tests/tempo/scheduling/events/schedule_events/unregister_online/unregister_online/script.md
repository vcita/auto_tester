# Script: Unregister from BO and CP, then pay online

Playwright-oriented implementation notes for `test.py`. All UI helpers live in
`tests/scheduling/events/schedule_events/schedule_events_ui.py`; payment + CP selectors
are reused from `tests/payments/event_payments/event_payments_helpers.py`.

The event detail page renders in the Angular frontage iframe (`iframe[title="angularjs"]`)
with the attendee list nested in the Vue layout iframe (`#vue_iframe_layout`).

## Implementation

1. **Register clients** — `register_clients_ui(page, context, event_uid, [silvan, judi, nir])`.
   Opens the Register Clients picker, selects each client (re-locating + keyboard-clearing
   the search per client), Continue → confirmation **Send** (scoped to the dialog), then
   gates on the attendee list populating with all three names.

2. **Counter + table** — `attendees_counter(...)` reads the Attendees tab number;
   `read_attendees(...)` parses the unpaid list (`.solo-attendees-list`) then the paid list
   (`.attendees-list`), each `.attendance-item` → `{name, payment_status, state, comment,
   index_per_category}` (`.matter-name`, `.status-desc`). `find_attendee` matches by name.

3. **BO unregister** — `unregister_attendee_bo(page, context, event_uid, "judi babish-moshe")`
   hovers the attendee, opens the three-dots menu, Cancel registration → Submit.

4. **CP self-cancel** — `cp_self_cancel_meeting(page, context, silvan_token, service_name)`
   opens the client portal in a fresh browser context via `?client_jwt=<token>`, Bookings →
   meeting → Cancel → confirm.

5. **Online payment** — `pay_for_attendee_bo(page, context, event_uid, "nir karpin", "100",
   pos=False)` opens the attendee's payment status (`gotoPaymentStatus`) and records the
   payment through the take-payment record dialog.

## Comment assertion

`_assert_attendees` checks `payment_status`/`state`/`index_per_category` strictly and the
`comment` by canceller category: `""` (registered), `"Canceled by client"` (CP cancel), or
any `"Canceled by …"` (back-office/staff cancel) — verifying *who* cancelled without
hard-coding the rendered staff/business display name.
