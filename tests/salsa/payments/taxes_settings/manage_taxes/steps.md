# Manage Taxes - Steps

## Objective
Create, edit, and delete tax rates in Billing & Invoicing settings, and switch the
tax mode to "include", verifying the taxes list and selected mode after each change.

Migrates automation-js `taxes-settings.feature` scenario `Create, update & delete taxes`.

## Prerequisites
- Logged in to the isolated account (from `_setup`).
- No taxes configured yet.

## Steps
1. Open the Taxes settings tab.
2. Create two taxes: `taylor swift 1` at `13` and `taylor swift 2` at `13.13131`; save.
3. Verify the taxes list shows exactly `taylor swift 1 (13)` and `taylor swift 2 (13.13131)`.
4. Edit `taylor swift 1 (13)` to `taylor swift 13 (13.14)`; save.
5. Verify the taxes list shows exactly `taylor swift 13 (13.14)` and `taylor swift 2 (13.13131)`.
6. Delete `taylor swift 13 (13.14)`; save.
7. Verify the taxes list shows exactly `taylor swift 2 (13.13131)`.
8. Change the tax mode to "include"; save.
9. Verify the selected tax mode is "include".

## Expected Result
- Each list verification matches the exact expected set of taxes.
- The tax mode is "include" after the change.
