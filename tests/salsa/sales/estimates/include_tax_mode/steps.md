# Create Estimate In Tax Mode Include

## Objective
With the account tax mode set to `include`, custom taxed items must produce a
tax-inclusive total (migrated from automation-js scenario
"Business creates estimate in mode 'include'").

## Prerequisites
- User logged in (Sales category _setup).
- Shared tax (13%) created via API in _setup.

## Steps
1. Set account tax mode to `include`; create a client.
2. Create estimate `bestimate` with custom items `desired_item1` ($50, tax 13%, not saved)
   + `desired_item2` ($20, saved), billing `susa, persia`, and send it.
3. Open the back-office estimate page.

## Expected Result
- Price/total is `$70.00` (tax included: 50 + 20), not `$76.50` (the exclude-mode value).
- Items `desired_item1` ($50) and `desired_item2` ($20) are listed.

## Context Updates
- `include_mode_estimate_title`
