# Changelog - Create Matter

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
