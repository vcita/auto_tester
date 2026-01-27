# Changelog - Logout Function

## [2.1.0] - 2026-01-26

### Fixed
- **Step 6 (verify logout)**: Sign-out worked but verification failed when login form was not inside `#vue_iframe`. On some hosts the form is in the main document. Now try `#vue_iframe` + "Log In to Your Account" first; on timeout fall back to `page.get_by_label("Email")` so we recognize the sign-in page either way.

## [2.0.0] - 2026-01-21

### Changed
- **Complete rewrite** based on Playwright MCP exploration
- Updated logout item locator to use `.logout-item` class (discovered via exploration)
- Added Cloudflare handling after logout redirect
- Updated verification to check login form inside iframe

### Added
- Cloudflare security check handling with 30-second timeout
- Better error handling and print statements
- Documented dropdown menu structure in script.md

### Fixed
- Correct logout menu item selector
- Proper handling of post-logout Cloudflare check
- Login form verification inside `#vue_iframe`

## [1.0.0] - 2024-01-20

### Added
- Initial implementation using UI actions only (no direct URL navigation)
- Click avatar → click Logout flow
- Context cleanup for `logged_in_user`
- Verification of login page after logout
