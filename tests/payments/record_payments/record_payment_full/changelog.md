# Changelog: record_payment_full

All changes to steps.md, script.md, and test.py are logged here.

---

## 2026-05-19 - Stabilize Workflow Navigation

**Phase**: Test
**Author**: Cursor AI
**Reason**: Record payment tests needed to pass both standalone and after previous payments workflow steps.

**Changes**:

- Added checkout navigation that handles both direct `/app/pos` navigation and expanded Sales submenu state.
- Reused the created setup client instead of selecting an arbitrary recently active client.
- Added invoice prerequisite creation for standalone partial, multiple, and mark-unpaid paths.
- Hardened record-payment dialog opening by re-querying controls, searching page and iframe scopes, and using DOM-click fallback.
- Calculated multiple-payment amounts from the actual invoice balance so taxed invoices remain valid.
- Waited for the first payment to update the remaining balance before recording the second payment.

## 2026-03-04 - Full Rebuild

**Phase**: All files (steps.md, script.md, test.py, changelog.md)
**Author**: Cursor AI (MCP exploration)
**Reason**: Rebuilt from scratch via Playwright MCP exploration to replace broken test with fallback/retry logic

**Changes**:

- **steps.md**: Updated flow to use Custom Item (no services with cost in environment). Removed reference to `data-qa` selector for navigation. Clarified prerequisites.
- **script.md**: Fully rewritten with LOCATOR DECISION tables and VERIFIED PLAYWRIGHT CODE blocks for every step. Flow: Sales sidebar → Checkout → Custom Item → Select client (iframe dialog) → Checkout → Record payment menu → Cash method → Record → Verify payment page.
- **test.py**: Regenerated from script.md. Clean single-flow implementation with no fallbacks, no try/except, no retry logic. Uses `frame_locator()` for iframe access (not `content_frame()`).
- **changelog.md**: Created.

**Key decisions**:
- Uses Custom Item instead of selecting a pre-existing service (all services have ₪0.00 price)
- Client selected from "Recently Active" section in iframe dialog
- Payment method selected via `get_by_role("listbox")` → `get_by_role("option")` pattern
- Verification checks URL (`/app/payments/transactions/`), "Paid" status, and "Cash" method in iframe

**Test run**: Passed in 9.7s on first run after rebuild.
