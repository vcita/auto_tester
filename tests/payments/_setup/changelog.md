# Changelog

## 2026-02-11 - Initial Build
**Phase**: Steps, script, test
**Author**: Cursor AI
**Reason**: Build payments setup to login and navigate to Billing & Invoicing
**Changes**:
- Added script.md with verified navigation steps
- Implemented test.py using login function and settings navigation

## 2026-02-11 - Target Visible Iframe
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Ensure Settings actions use the visible angular iframe
**Changes**:
- Use `iframe[title="angularjs"]:visible` in setup navigation
