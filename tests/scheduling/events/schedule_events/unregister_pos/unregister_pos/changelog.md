# Changelog: Unregister POS

## 2026-06-10 — Initial migration (VCITA2-14026)

Migrated from `automation-js/features/tempo/scheduling-events.feature` scenario 2B
("create event and pays with POS").

- Isolated account with `point_of_sale` **enabled** (default) so the remaining attendee is
  paid through Point of Sale.
- Event service, `user_staff`, three clients, and the event instance are created via API in
  `_setup`; registration of the three clients is done through the back-office UI.
- Same flow as the sibling `unregister_online` (register three, BO unregister, CP self-cancel,
  attendee-table + counter assertions at each stage) except the final payment for the
  remaining attendee is taken through Point of Sale (`pay_for_attendee_bo(..., pos=True)`).
