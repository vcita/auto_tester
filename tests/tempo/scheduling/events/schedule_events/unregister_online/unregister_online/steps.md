# Unregister from BO and CP, then pay online

Migrated from `automation-js/features/tempo/scheduling-events.feature` scenario 2
("create event and unregister clients from BO and CP", VCITA2-14026).

**Precondition (setup):** isolated account with `point_of_sale` denied, a `$100`
require-to-pay event service, a `user_staff` staff member, three clients
(`silvan goodbye`, `judi babish-moshe`, `nir karpin`), and the event scheduled via API.

## Steps

1. **Register three clients** to the event from the back office (Register Clients picker):
   `silvan goodbye`, `judi babish-moshe`, `nir karpin`.
   - **Expected:** attendees counter shows `3`; the attendee table lists all three as
     `unpaid` / `registered`, ordered most-recent first — `nir karpin` (1),
     `judi babish-moshe` (2), `silvan goodbye` (3).

2. **Unregister `judi babish-moshe`** from the back office (attendee menu → Cancel
   registration → Submit).
   - **Expected:** attendee table re-orders to `nir karpin` (1, registered),
     `silvan goodbye` (2, registered), `judi babish-moshe` (3, `unregistered`, commented
     "Canceled by &lt;staff&gt;"); attendees counter shows `2`.

3. **`silvan goodbye` self-cancels** the registration from the client portal (Bookings →
   meeting → Cancel → confirm).
   - **Expected:** attendee table shows `nir karpin` (1, registered),
     `silvan goodbye` (2, `unregistered`, "Canceled by client"),
     `judi babish-moshe` (3, `unregistered`, "Canceled by &lt;staff&gt;").

4. **Record an online `$100` payment** for `nir karpin` (attendee → payment status → take
   payment → record).
   - **Expected:** `nir karpin` moves to the paid list (`paid` / `registered`, index 1);
     the unpaid list keeps `silvan goodbye` (1, "Canceled by client") and
     `judi babish-moshe` (2, "Canceled by &lt;staff&gt;").
