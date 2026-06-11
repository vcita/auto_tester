# Changelog

## 2026-05-19 - Allow Default Tax Inheritance
**Phase**: Test
**Author**: Cursor AI
**Reason**: Payments workflow needed setup services and downstream invoice tests to work with default tax configured by settings tests.
**Changes**:
- Removed the explicit empty `tax_uids` payload so created services can inherit default taxes.
- Stabilized invoice flows to use the setup service from context and calculate totals with configured tax.
- Updated refunds and credits to create or reuse paid invoice prerequisites depending on standalone or workflow state.
- Recorded the successful payments category health result after the 10/10 stress run.

## 2026-05-17 - Create Paid Invoice Service Via API
**Phase**: Steps, script, test
**Author**: Cursor AI
**Reason**: Invoice creation was selecting existing zero-priced services, leaving invoice totals at `$0.00`.
**Changes**:
- Added payments setup API creation for a required-payment service (`charge_type=paid_force`, price `100`)
- Stored `invoice_service_name` and `invoice_service_price` in context for invoice tests
- Mirrored the automation-js `user creates new service via API` setup pattern

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
