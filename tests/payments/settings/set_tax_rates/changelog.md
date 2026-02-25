# Changelog

## 2026-02-11 - Initial Build
**Phase**: Steps, script, test
**Author**: Cursor AI (exploration)
**Reason**: Built from steps.md via MCP exploration
**Changes**:
- Added script.md with verified locators
- Implemented test.py using press_sequentially for inputs

## 2026-02-11 - Stabilize Navigation
**Phase**: Test
**Author**: Cursor AI
**Reason**: Runner timeout while loading Settings and Billing & Invoicing
**Changes**:
- Increased navigation and iframe wait timeouts to 45s

## 2026-02-11 - Fix Taxes Tab Locator
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Taxes & Tips tab click did not switch content in runner
**Changes**:
- Use text-based locator for "Taxes & Tips"
- Wait for "Tax settings" heading before Add new tax

## 2026-02-11 - Target Visible Iframe
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Runner stayed on Invoices & Estimates tab; possible hidden iframe
**Changes**:
- Use `iframe[title="angularjs"]:visible` for Billing & Invoicing actions

## 2026-02-11 - Align Taxes Tab Label
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: UI shows "Taxes" tab label instead of "Taxes & Tips"
**Changes**:
- Click "Taxes" tab text in Settings / Billing & Invoicing

## 2026-02-11 - Use Taxes Tab Role
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Text locator may hit hidden tab label
**Changes**:
- Click `role=tab` for "Taxes" and scroll into view before clicking

## 2026-02-11 - Support Taxes Label Variants
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: UI alternates between "Taxes" and "Taxes & Tips"
**Changes**:
- Use regex `^Taxes` for tab locator

## 2026-02-11 - Use Taxes Shortcut Link
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Taxes tab role not found in runner layout
**Changes**:
- Click "Taxes" link in the right-side shortcuts panel

## 2026-02-11 - Use Page-Level Taxes Click
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Taxes controls not found inside iframe during runner
**Changes**:
- Click "Taxes" using page-level text locator

## 2026-02-11 - Use Taxes Shortcut Link Role
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Text-based locator still not found in runner
**Changes**:
- Use page-level link role for "Taxes" shortcut

## 2026-02-11 - Use Settings-Scope Taxes Text
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Taxes link role not found; tab text is inside settings scope
**Changes**:
- Click "Taxes" via settings-scope text locator

## 2026-02-11 - Resolve Taxes Strict Mode
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: "Taxes" text matches tab and shortcut link
**Changes**:
- Use `role=tab` with regex `^Taxes` to target the tab

## 2026-02-11 - Resolve Tax Input Strict Mode
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Multiple tax rows created in previous runs
**Changes**:
- Target the last Tax name and Tax rate inputs

## 2026-02-11 - Fix Save Button Scope
**Phase**: Test
**Author**: Cursor AI
**Reason**: NameError for settings_iframe after refactor
**Changes**:
- Use settings_scope for Save button

## 2026-02-11 - Adaptive Settings Scope
**Phase**: Script, test
**Author**: Cursor AI
**Reason**: Runner layout sometimes lacks angular/inner iframes
**Changes**:
- Use page-level scope when `iframe[title="angularjs"]` or `#vue-app-tab` is missing

## 2026-02-11 - Skip Redundant Navigation
**Phase**: Test
**Author**: Cursor AI
**Reason**: Setup already leaves browser on Billing & Invoicing
**Changes**:
- Skip Billing & Invoicing button click when already on target URL
