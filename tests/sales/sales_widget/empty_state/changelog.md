# Changelog — Sales Widget Empty State

## 2026-06-06 — Initial migration (VCITA2-13854)
- Migrated from `automation-js/features/salsa/sales_widget.feature` scenario
  "Sales widget - empty state - no payments set".
- Asserts the loaded Sales widget empty state and that "Start accepting payments"
  opens the get-paid-online payment wizard (Vue iframe).
- Selectors reuse the legacy data-qa where present; loaded-container, empty title,
  and wizard root use stable legacy CSS (no data-qa in product).
