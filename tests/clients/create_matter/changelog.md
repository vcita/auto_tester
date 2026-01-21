# Changelog - Create Matter

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
