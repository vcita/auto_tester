# Register clients to an event

User-facing steps (what the test verifies). Migrated from
`automation-js/features/tempo/scheduling-events.feature` scenario 1
"create a single event and register multiple clients to it" (VCITA2-14026).

## Background (API setup)
- Logged in to a fresh isolated account.
- A "require to pay" $100 event service exists (`r2p_event...`).
- A staff member `user_staff` exists.
- Two clients exist: `silvan goodbye` and `judi babish-moshe`.

## Steps
1. Schedule a new event from the back office for the require-to-pay service, on the
   10th of next month, assigned to `user_staff`.
2. The event instance is created and shows:
   - location `TLV`
   - the next-month, day-10 date
   - state `SCHEDULED`
   - price `$100.00` (USD)
   - assigned staff `user_staff`
   - registration availability "Available on service menu"
   - attendance summary `0/ 2 Registered`
   - no attendees yet.
3. Register the two clients (`silvan goodbye`, `judi babish-moshe`) to the event.
4. The event attendee list now shows both `silvan goodbye` and `judi babish-moshe`.
5. The registered client `silvan goodbye` has a client-portal conversation whose title
   includes "Event Registration: <event>".
