# Changelog: Pay for event via Point of Sale

## 2026-06-06 — Initial migration (VCITA2-13856)
- Migrated event-payments.feature scenario 2b "paying for event via Point of Sale".
- Isolated subcategory `pay_via_pos` (point_of_sale enabled).
- Reuses the event-payment-request navigation and the POV POS checkout controls
  (mirrors the deposits POS record flow); adds frame-scan Orders status-filter and
  Sale-page readers, plus Payments Received search and the CP conversation check.
