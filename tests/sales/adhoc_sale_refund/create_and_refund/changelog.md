# Changelog: create_and_refund

## Initial creation (VCITA2-13849)
**Phase**: steps.md, script.md, test.py
**Reason**: Migrate `automation-js/features/salsa/sales.feature` scenario
"Create ad-hoc sale - refund" into auto_tester.

**Decisions**:
- New isolated-account subcategory `tests/sales/adhoc_sale_refund`
  (`account_profile: isolated`, `cleanup: always`) so the order/payment are
  deterministically named `Sale #1 - meeting` / `Payment for Sale #1 - meeting`,
  matching the legacy fresh-account assumption.
- `_setup` mirrors the legacy Background (API login + create client "first last").
- Mock gateway connected via the existing `tips_gateway.connect_mock_gateway`
  (setup prerequisite, UI, mirrors legacy `configureMockPaymentGateway`).
- Client-portal public make-payment form, mock-gateway popup, and success-page
  assertions implemented in `adhoc_sale_helpers.py`; the popup pattern mirrors
  the proven deposits flow.
- Orders status filter and the nested Sale-detail reader reuse the legacy stable
  Angular selectors (no data-qa exists yet — flagged for product code).
- Success page asserts title (Payment confirmed), amount ($20.00), and subtitle
  (confirmation email) — preserving the legacy three-field assertion.
- Added an extra `assert_sale_state(... CANCELLED)` after the legacy
  Orders-CANCELLED assertion for a stronger, unambiguous post-refund state check
  (no scope loss).

**Waits**: element/dialog/state waits capped at 5s; `NAV_TIMEOUT`/`POPUP_TIMEOUT`
(20s) only for portal navigation and the external mock-gateway popup; reload
retries capped at 2 for orders/payments indexing lag.

## Stabilization (VCITA2-13849)
**Phase**: test.py / adhoc_sale_helpers.py / script.md
**Reason**: First focused run failed in `pay_via_mock_gateway` with
`Failed to find frame for selector "#cp_iframe ... label="Email"`.
**Root cause** (ground-truthed with a one-off DOM dump of the live make-payment
form): the form renders inside `#cp_iframe` as a navigation-level load that takes
~6s, so the original 5s field wait fired before the frame attached; the submit
control is a **CHECKOUT** button (`data-qa="vc-btn"`, not unique) rather than a
`payButton`, and Email is `[data-qa="email-input"]`.
**Fix**:
- Wait for the Email field with `NAV_TIMEOUT` (frame load), not the 5s element cap.
- Email via `[data-qa="email-input"]`; First Name via `get_by_label`.
- Submit via the CHECKOUT button matched by accessible name (`get_by_role`).
**Validation**: 3/3 clean focused runs on integration (≈82s, 81s, 83s).
