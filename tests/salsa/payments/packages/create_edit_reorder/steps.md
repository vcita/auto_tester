# Create, edit and reorder packages with products

## Objective
Exercise core back-office package management: create two packages (each with a product
add-on), verify they appear in the Settings/Packages list, edit one (rename + disable the
add-on), verify the updated list, reorder the packages, and verify the new list order.

## Prerequisites
- Setup created `service`, `service2`, `r2p_event` and connected the mock gateway.

## Steps
1. Create a product `payable_item1` ($10) via API.
2. Create a fresh client via API.
3. Create package `package_1` via the UI: service `service`, 2 credits, price 150,
   product `payable_item1` x2, add-ons enabled.
4. Create package `package_2` via the UI: event `r2p_event`, 3 credits, price 250,
   product `payable_item1` x3, add-ons enabled.
5. Verify the packages list shows `package_1`, `package_2` (in that order).
6. Edit `package_1` via the UI: rename to `package_3`, disable add-ons.
7. Verify the packages list shows `package_3`, `package_2`.
8. Reorder the packages via API (reverse the active order).
9. Verify the packages list shows `package_2`, `package_3`.

## Expected Result
- Both packages are created and listed.
- After edit, the renamed package replaces the original in the list.
- After reorder, the list order is reversed.
