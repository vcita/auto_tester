# Changelog: Unregister Online

## 2026-06-10 — Initial migration (VCITA2-14026)

Migrated from `automation-js/features/tempo/scheduling-events.feature` scenario 2
("create event and unregister clients from BO and CP").

- Isolated account with `point_of_sale` **denied** (online take-payment record path).
- Event service, `user_staff`, three clients, and the event instance are created via API
  in `_setup`; registration of the three clients is done through the back-office UI.
- Verifies the attendee table (registered/unregistered, paid/unpaid, per-category index,
  canceller comment) and the attendees counter at each stage: after registration, after a
  back-office unregister, after a client-portal self-cancel, and after recording an online
  payment for the remaining attendee.
- New helper `pay_for_attendee_bo(..., pos=False)` reaches the attendee's payment status
  from the event page (`gotoPaymentStatus`) and reuses the event_payments take-payment
  record flow. `find_attendee` matches attendee rows by name.
