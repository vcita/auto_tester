# Create Estimate With Sections

## Objective
Create an estimate with a top-level item plus a section grouping a second item
(migrated from automation-js scenario "Business creates estimate with sections").

## Prerequisites
- User logged in (Sales category _setup).
- Shared service ($100) and product ($10) created via API in _setup.

## Steps
1. Set account tax mode to `exclude`; create a client.
2. Create estimate `bestimate`: add `service` as a top-level item, add a section
   `section1`, then add `product2` (grouped under the section). Billing `susa, persia`. Send.
3. Open the back-office estimate page.

## Expected Result
- Price/total `$110.00`, state `SENT`, client name shown.
- Top-level item `service` ($100).
- Section `section1` total `$10.00` containing `product2` ($10).

## Context Updates
- `sections_estimate_title`
