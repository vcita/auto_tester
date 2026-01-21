# Changelog - Login Function

## [2.0.0] - 2026-01-21

### Changed
- **Complete rewrite** based on Playwright MCP exploration
- Updated to handle login form inside `#vue_iframe` iframe
- Changed button locator from `name="Login"` to `name="Log In"` (with space)
- Added proper iframe content frame handling

### Added
- Cloudflare security check handling with extended timeout
- reCAPTCHA detection and warning message
- Debug print statements for troubleshooting
- "Already logged in" check to skip unnecessary login

### Fixed
- Correct iframe selector (`#vue_iframe`)
- Correct button text ("Log In" not "Login")
- Proper wait conditions for login form inside iframe

## [1.0.0] - 2024-01-20

### Added
- Initial implementation
- Basic login flow: navigate → fill email → fill password → click login
- Cloudflare wait handling
- Context save for `logged_in_user`
