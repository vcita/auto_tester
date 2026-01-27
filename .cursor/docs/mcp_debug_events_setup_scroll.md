# MCP Debug: Events _setup – scroll Services list to find new service

**Goal:** In a **new Playwright MCP session**, understand how to scroll the Services page list so the newly created group event service becomes visible (and can be found by the test).

**Why:** The test used to pass when we had "skip nav when already on Services"; after removing that and relying on scroll-to-end, the scroll was not moving the list (we were likely scrolling the wrong element). We need the exact scrollable container and behavior.

---

## 1. Get to the right page (in MCP)

- **Option A:** Start a **new** MCP browser. Log in (config/auth). Go to **Settings** → **Services** (click "Define the services your" in the iframe). You should see the Settings / Services page with a list of services.
- **Option B:** Run `python debug_events_setup_mcp.py` to open a Python-launched browser on the Services page, then **in MCP start a new browser** and navigate to the same URL (from the Python window) so you have the same state in MCP. Remember: MCP cannot drive the Python-launched browser.

---

## 2. Inspect DOM (in MCP)

- Take a snapshot of the page (or inspect the iframe content).
- Find:
  - The **"My Services"** heading or label.
  - The **scrollable container** that holds the list of service rows (cards). It is likely a `div` with `overflow: auto` or `overflow-y: scroll` that is an **ancestor** of "My Services" or wraps the list below it.
- Note: The current code scrolls the **first** scrollable `div` in the iframe document. That may be something else (e.g. sidebar, layout wrapper), not the list. Confirm which element actually scrolls the service list.

---

## 3. Scroll the list in MCP

- In the iframe’s document, find the scrollable element that contains the services list (e.g. the one that has "My Services" inside it or right above the list).
- Run JS in that frame to:
  - Set `element.scrollTop = element.scrollHeight - element.clientHeight` (scroll to bottom).
  - Wait ~400–500 ms.
  - Repeat until `scrollHeight` stops increasing (infinite scroll loaded).
- Or use MCP to scroll that element (e.g. wheel or keyboard) and confirm that new rows appear and the list actually moves.

---

## 4. Document for the test

- **Selector or rule** for the correct scrollable element (e.g. “ancestor of the node that contains text ‘My Services’ and has `overflow-y: auto`” or a specific class/attribute).
- **Exact sequence** that loads the full list (e.g. “scroll to bottom N times with 400 ms wait until scrollHeight stable”).
- Update `_scroll_services_list_to_end()` in `tests/scheduling/events/_setup/test.py` to use this element and sequence.

---

## MCP debug result (2026-01-26)

- **Problem:** `findScrollable()` required both `overflow-y: auto/scroll` and `scrollHeight > clientHeight`. When the Services list is short (e.g. 3 items), the main content container has identical dimensions (868x868), so no scrollable was found and we never scrolled.
- **DOM:** "My Services" has multiple scrollable ancestors: (1) `MD-CONTENT.list-header` (69x69), (2) `MD-CONTENT.settings-component.services-container` (868x868), (3) `MD-CONTENT.content-section` (868x868). The first match was the tiny header; the real list is in the main content.
- **Fix applied in test.py:** (1) Do not require `scrollHeight > clientHeight`; treat any ancestor with `overflow-y: auto/scroll/overlay` as a candidate. (2) Among those, pick the one with the **largest** `clientHeight` so we scroll the main content (e.g. settings-component) instead of the list-header bar. (3) Scroll that element to bottom in a loop until height stabilizes.

---

## What changed (why it used to work yesterday)

- **Before:** Events _setup had a **conditional**: if already on `/app/settings/services`, skip navigating (Settings → Services). So after parent setup we stayed on the same Services view; the list was already in a state where the new service sometimes appeared without extra scroll.
- **Change:** We removed the conditional (no navigation in Events _setup). We still assume parent leaves us on Services, but we now **only** rely on scroll-to-end to find the new service.
- **Bug:** The scroll helper used the **first** scrollable `div` in the iframe. That is likely **not** the services list container, so we were not scrolling the list at all. Hence “you were not scroll down at all.”
- **Fix direction:** Target the scrollable container that actually wraps the “My Services” list (e.g. find “My Services” and use its scrollable ancestor), then scroll that to the end.
