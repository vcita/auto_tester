# Changelog: take_via_pos (POS tips)

## 2026-06-07 - Migrate tips.feature scenario 2 (VCITA2-13899)

- Migrated from `automation-js/features/salsa/tips.feature` scenario "edit tips
  options & take payment with tips via Point of Sale" into
  `tests/payments/tips_checkout/pos_payment_tips`.
- Setup (API): shared `seed_balance_tip_account(deny_pos=False)` - tips app, BO tips
  55,66,77, client + suggest-to-pay $100 service + specific package ($150, assigned)
  + past appointment. point_of_sale stays ENABLED so Quick Actions exposes the POS
  Take payment large action. Login last (Account model loads tips).
- Test (UI): `tips_checkout_pos` - POS sale from open requests (Record ACH + 55% tip,
  asserts Sale #1 $387.50, tip $137.50, items package,service), then a custom-item POS
  sale (Record ACH + Custom $4.50 tip, asserts Sale #2 some_item, tip $4.50).
- Reuses the Angular take-payment dialog primitives (`_select_md_option`, `_apply_tip`,
  `_confirm_and_close`) from `tips_checkout_bo`; the tip picker has no product data-qa,
  so the stable legacy `md-select[name='tip_option']` selectors are reused.
- POS quick action selector: the DS `VcLargeQuickAction` binds its own (empty) `dataQa`
  on the root, which overrides the parent's `VcLargeQuickAction-point_of_sale`, so that
  data-qa never renders. Target the large action by `.VcLargeQuickAction:has-text("Take
  payment")` (POS is the only large Take payment action).
- The large actions load asynchronously (skeletons first), so the POS action is awaited
  with the 15s load budget (5s was occasionally too short). Re-clicking the menu button
  toggles it closed, so the menu is opened once (one re-open only if not showing).
  Validated 3/3 clean runs on integration (~47s each).
