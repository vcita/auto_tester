# Script: External receipt - POS (setup)

`prepare_receipt_account(page, context, deny_pos=False)` in `gateway_setups_account.py`:

- `fn_login(page, context, username, password)` — isolated account UI login (POS enabled).
- `create_client(context, "simon", "bolivar", email)` → `receipt_client_*` context keys.
- `assign_app(context, "mockreceipts")` → admin-auth POST `/platform/v1/apps/mockreceipts/assign`.
