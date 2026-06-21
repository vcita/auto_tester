# Create + assign taxed package (include mode) — Detailed Script

Same UI flow as `create_assign_exclude` (helpers in packages_helpers.py); the only difference
is the account tax mode is set to `include` before assigning, so the displayed total equals
the package price.

## Actions
1. Create two taxes via API (`create_tax_via_api`).
2. Set tax mode to include via API (`set_tax_mode_include`, PUT v2/settings tax_mode=include).
3. Create a fresh client via API (`make_client`).
4. Create package via UI (`create_package`, service, 2cr, $150, tax 13%).
5. Assign via the client card (`assign_package_via_client_card`, taxes 13% + 13.13%).
6. Assert client-package request: state DUE, amount $150.00, client first last, package package.

## Success Verification
- Client-package DUE $150.00 (tax folded into the price by include mode).
