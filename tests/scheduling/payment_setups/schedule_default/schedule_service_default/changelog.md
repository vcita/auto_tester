# Changelog — Schedule Service Default

## 2026-06-09 — Initial migration (VCITA2-14008, scenario 1/4)

Migrated `payment-setups.feature` scenario "Schedule service default" from automation-js.

**Built**
- `_setup/test.py`: create client via API, log in, connect mock payment gateway.
- `payment_setups_ui.py`: `create_service_ui` (advanced-editor service creation for all six
  payment settings), `read_meeting_price`, and an empty-state-safe `_open_new_service`.
- `payment_setups_common.py`: `EDITOR_OPTION`/`CHARGE_TYPE`/`LIST_PAYMENT_TYPE` mappings.
- `test.py`: create 6 services → verify services list → schedule 6 appointments → verify
  meeting prices.

**Scope/quality**
- Full legacy scope preserved: all six payment settings created via UI, services-list
  payment-type/price verified per service, all six appointments scheduled and their meeting
  prices verified (100/50/10/blank/Free/blank).

**Fixes during build (found via focused runs)**
- `EDITOR_OPTION["display a fee"]` corrected to the real label "Paid - No online payment at
  booking" (was a stale guess).
- Added mock-gateway connection to setup: "require to pay" degrades (blank price, no
  "required") without an online payment method; the legacy automation account has one.
- Empty-account handling: a fresh account has no category card, which the shared
  `goto_services` waits for; added a local `_open_new_service` that waits for the heading +
  New-service button (the first service auto-creates "My Services").
- Cold-load: the Angular services module can take >5s to render on the first navigation
  (right after the gateway-iframe flow); bounded that one wait to 20s (action waits stay 5s).
- New-service split button binds its handler late on cold load; the open is retried up to 3x.

**Run evidence**
- 2026-06-09 focused run: PASSED (2/2), body ~119s (6 UI service creations + 6 schedulings +
  6 meeting reads — inherent to scope).
