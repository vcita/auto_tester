# Changelog — Override Price Type

## 2026-06-09 — Initial migration (VCITA2-14008, scenario 2/4)

Migrated `payment-setups.feature` scenario "Update payment type during scheduling".

**Built**
- `_setup/test.py`: create client + six payment-setting services via API, log in.
- Extended the shared `multistaff_helpers.schedule_appointment` with a backward-compatible
  `price_override` parameter + `_apply_price_override`/`_open_price_panel`/`_select_fee_type`
  (price expansion panel, fee-type select, amount input).
- `payment_setups_common.APPT_FEE_TYPE`: price_type → appointment fee-type label.
- `test.py`: schedule six appointments with per-appointment price overrides and verify the
  resulting meeting prices.

**Scope/quality**
- Full legacy scope preserved: all six overrides (3 type-only, 3 fixed-price-with-amount) and
  their expected meeting prices (Free/blank/blank/65/97/25 USD).

**Fixes during build (found via focused run)**
- Fee-type menu items are Vuetify list items whose accessible name includes the description
  line; exact option-name matching failed. Now matches the `.v-list-item__title` text.

**Run evidence**
- 2026-06-09 focused run: PASSED (2/2), body ~69s (6 schedulings with overrides + meeting reads).
