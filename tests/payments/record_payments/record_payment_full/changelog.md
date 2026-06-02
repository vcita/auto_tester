# Changelog: record_payment_full

All changes to steps.md, script.md, and test.py are logged here.

---

## 2026-06-02 - Fix flaky client selection (VCITA2-13776)

**Phase**: Test (test.py, script.md)
**Author**: Cursor AI
**Reason**: `Record Full Payment` failed with a 30s TimeoutError on "Click Checkout". The May client-by-name selector (`get_by_text(client_name).first`) clicked a non-selectable text node, dismissing the picker without choosing a client, so Checkout stayed disabled.

**Changes**:

- Select an actual client **row** (`md-list-item[role=listitem]`), targeting the named row or the first real client (one with an email), never the "New Client" action row.
- When the client is not in "Recently Active" (e.g. a freshly created client), switch to the **"ALL CLIENTS"** view and **search** by name.
- **Verify the Checkout button becomes enabled** after selection (reliable signal), retrying the picker up to 3 times.
- On failure, raise an explicit message instead of a blind 30s click timeout.
- Picker structure confirmed via CDP: rows are Angular Material `md-list-item[role=listitem]`; `get_by_role("list")` does not match.

**Test run**: `payments/record_payments` subcategory PASSED 5/5 (headless), Record Full Payment 11.5s.

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
