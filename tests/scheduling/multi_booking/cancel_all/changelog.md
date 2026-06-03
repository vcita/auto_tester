# Changelog — cancel_all

## Initial migration (VCITA2-13793)
- Migrated from automation-js `features/tempo/multi-booking-appointments.feature`
  scenario "Cancel all multi-booking appointment".
- Reuses the shared `multi_booking_ui.py` / `multi_booking_api.py` helpers and the
  isolated `_setup` (3 services + client created via API).
- Cancel-all path uses the bulk-cancel dialog with the default (all) option, then
  verifies all three appointments are Cancelled and reads the cancelled
  linked-booking bubble from the client conversation timeline.
