# Changelog - Create Matter

## [2.9.0] - 2026-01-30

### Fixed (Healed)
- **Could not find form frame with 'First Name' field** / **iframe reported hidden** (form never opened)
  - **Error**: `Exception: Could not find form frame with 'First Name' field`; later runs: `TimeoutError: Locator.wait_for: Timeout 30000ms exceeded` waiting for iframe to be visible or for Quick actions inside frame.
  - **Root cause**: (1) Click was on the inner text node; the click handler is on the parent (cursor=pointer). (2) Multiple iframes with `title="angularjs"` exist; the first can be hidden, so `frame_locator('iframe[title="angularjs"]')` attached to the wrong frame and content never became visible.
  - **Fix applied**:
    1. **Page-level Quick actions**: Use `page.get_by_text("Quick actions", exact=True).locator("../..")` so Playwright finds the visible panel in any frame (no dependency on which iframe).
    2. **Click parent**: Use `add_matter_locator.locator("..")` and click that; the parent is the clickable container (MCP confirmed ref=e238 opens form).
  - **Files updated**: test.py (Steps 2–3), script.md (Step 1).
  - **Verified**: Category run — Create Matter and full Clients category (7 tests) passed.

## [2.8.0] - 2026-01-27

### Fixed (Healed)
- **Could not find form frame with 'First Name' field** (recurring after 40 attempts)
  - **Error**: `Exception: Could not find form frame with 'First Name' field`; vue_iframe_layout stayed on `.../vue/#/pending?...` for full 40×1s poll.
  - **Root cause**: First click on Add matter sometimes does not open the form (e.g. vue stuck on pending). Retrying the click can open it.
  - **Fix applied**: If form not found after 40 attempts, click Add matter again (scroll into view + click), wait 5s, then poll up to 20×1s for form frame. Helper `_find_form_frame()` used for both passes.
  - **Files updated**: test.py (Step 4).
  - **Verified**: Full suite run — Create Matter passed (42.4s).

## [2.7.0] - 2026-01-27

### Fixed (Healed)
- **Could not find form frame with 'First Name' field** (recurring)
  - **Error**: `Exception: Could not find form frame with 'First Name' field` after 25×1s polling.
  - **Root cause**: Form can load in `angular-iframe` (fast) or `vue_iframe_layout`; when vue stays on `.../vue/#/pending?...`, the form appears later. MCP reproduced success (form in angular-iframe on first poll); failed run had vue at pending—timing variance.
  - **Fix applied**: Increased form-frame wait: 5s initial (was 3s) and 40×1s poll (was 25), ~45s total after Add matter click, so slow/vue-pending loads still succeed.
  - **Files updated**: test.py (Step 4), script.md (Initial State note).
  - **Verified**: Category run — Create Matter passed (47.1s).

## 2026-01-27 - Shorter matter name (avoid table truncation)
- **Reason**: Clients table shows names with ellipsis when long; delete_matter needs to find/verify the row. We already search so only the right client is shown; shorter names reduce truncation.
- **Change**: `last_name = f"Matter{timestamp % 1000000}"` (6-digit suffix, e.g. "Matter123456") instead of full timestamp. script.md, steps.md updated.

## [2.6.0] - 2026-01-26

### Fixed (Healed)
- **Could not find form frame with 'First Name' field**
  - **Error**: `Exception: Could not find form frame with 'First Name' field` after 10 attempts (500ms each).
  - **Root cause**: The Add matter form loads in a nested frame (vue_iframe_layout) asynchronously; 5s total polling was often not enough for the Vue app to navigate and render the "First Name" field. No navigation-rule violation; timing only.
  - **Fix applied**:
    1. After ensuring dashboard, add 2s settle time (matches create_client) so panel/vue iframe are ready.
    2. After clicking Add matter, wait 3s before starting form-frame polling.
    3. Increase form-frame polling to 25 attempts × 1s (up to ~28s total after click) so we find the frame once the form has loaded.
  - **Files updated**: test.py (Step 1 + Step 4), script.md (Initial State note).

## [2.5.0] - 2026-01-26

### Fixed (Healed)
- **Timeout waiting for "Add (property|client|...)" in Create Matter**
  - **Error**: `TimeoutError: Locator.wait_for: Timeout 10000ms exceeded. - waiting for get_by_text(re.compile(r"^Add (property|client|patient|student|pet)s?$", re.IGNORECASE)) to be visible`
  - **Root cause**: The Add-matter button was located with a page-wide `get_by_text(regex)`. On some runs/accounts the same text can exist elsewhere (or not yet visible), or the Quick actions panel content loads after the 3s wait. Scoping was missing.
  - **Fix applied**:
    1. Scope the "Add [entity]" lookup to the Quick actions panel: `page.get_by_text("Quick actions", exact=True).locator("..")` then find the button within that section.
    2. Use substring regex `Add\s+(property|client|patient|student|pet)s?` (no ^/$) to tolerate extra whitespace or nested text.
    3. Increased wait for the button to 15s.
  - **MCP**: Confirmed on dashboard the first quick action is "Add client"; clicking it opens the New client form. Scoped locator and substring regex ensure we match the visible panel action across verticals.
  - **Files updated**: test.py (Step 3), script.md (Step 1).

## [2.4.0] - 2026-01-26

### Fixed (Healed)
- **Wrong login page / dashboard URL: "This page is unavailable"**
  - **Error**: `TimeoutError: Locator.wait_for: Timeout 15000ms exceeded. - waiting for get_by_text("Quick actions", exact=True) to be visible`
  - **Root cause**: Test used `page.goto(base_url + "/app/dashboard")` with `base_url` from config (https://www.vcita.com). The app dashboard is served from **app.vcita.com**, not www. Navigating to www.vcita.com/app/dashboard shows "This page is unavailable", so "Quick actions" never appeared. Setup correctly leaves the browser on app.vcita.com/app/dashboard after login; the test was then navigating away to the broken URL.
  - **Fix applied**:
    1. Removed `page.goto(base_url + "/app/dashboard")` (also a navigation rule violation: no direct goto to internal URLs).
    2. If not already on dashboard (`/app/dashboard` not in page.url), navigate via UI: click sidebar "Dashboard", then wait for `**/app/dashboard**`.
    3. Then wait for "Quick actions" panel and continue as before.
  - **MCP**: Confirmed dashboard on app.vcita.com shows "Quick actions" and "Add client"/"Add property"; www.vcita.com/app/dashboard shows "This page is unavailable."
  - **Files updated**: test.py, script.md (Initial State + Step 0). steps.md unchanged.

## [2.3.0] - 2026-01-22

### Fixed (Healed)
- **UI Change: Quick Actions menu no longer exists**
  - **Error**: `TimeoutError: Locator.wait_for: Timeout 5000ms exceeded. - waiting for locator("#client") to be visible`
  - **Root cause**: vcita UI changed - the Quick Actions button in the sidebar no longer opens a dropdown menu with `#client` selector
  - **Discovery**: "Add property" is now directly visible in a static "Quick actions" panel on the right side of the dashboard
  - **Fix applied**:
    1. Navigate explicitly to dashboard (`page.goto`) instead of checking if already there
    2. Wait for "Quick actions" heading to be visible, then wait 3 seconds for async panel content
    3. Click "Add property" text directly using `get_by_text("Add property", exact=True)` with `scroll_into_view_if_needed()`
    4. Find form frame dynamically by iterating through `page.frames` looking for "First Name" field
    5. Use `form_frame` (Frame object) instead of `iframe` (FrameLocator) for all form interactions
  - **Debugging process**:
    - Created multiple debug scripts with CAPTCHA bypass user-agent
    - Discovered click on text element wasn't opening form consistently
    - Found that explicit navigation + longer wait + scroll into view was needed
    - Form opens in frame named 'angular-iframe', not `title="angularjs"`
  - Updated script.md with new flow
  - Completely rewrote test.py form opening logic
  - All 7 tests in clients category now pass

## [2.2.0] - 2026-01-21

### Changed
- **All text input now uses `press_sequentially()`** for better real-user simulation
  - Pattern: `field.click()` → `wait(100)` → `field.press_sequentially(value)`
  - Applied to ALL text fields, not just Email and Phone
  - More reliable and consistent behavior across all field types

## [2.1.0] - 2026-01-21

### Fixed
- **Email and Phone fields now work correctly**
  - Root cause: These fields are autocomplete comboboxes that don't work with `.fill()`
  - Solution: Click field first (transforms to combobox), then use `.press_sequentially()`
  - Updated test.py with correct approach
  - Updated script.md with documentation

## [2.0.0] - 2026-01-21

### Changed
- **Complete rewrite** based on Playwright MCP exploration
- Added comprehensive form fields:
  - Contact Information: First Name, Last Name, Email, Mobile phone, Address, Referred by
  - Property Details: Property address, Property type, Help request, Special instructions, Private notes
- Updated all locators based on actual DOM exploration
- Added proper iframe handling (`iframe[title="angularjs"]`)
- Added "Show more" click to expand all contact fields
- Added Property type dropdown selection
- Added comprehensive verification:
  - URL contains client ID
  - Page title contains property name
  - Contact information visible on card
  - Referred by field verified

### Added
- Context saves: `created_client_id` (extracted from URL)
- Detailed print statements showing all saved data
- Standalone testing with proper login function import

### Fixed
- Proper iframe content frame handling
- Dropdown selection using `get_by_role("option")`
- Verification using nested iframes (`#vue_iframe_layout`)

## [1.0.0] - 2024-01-20

### Added
- Initial implementation from exploration
- Basic form filling: Name, Email, Phone
- Quick Actions menu navigation
- Basic verification of property creation
