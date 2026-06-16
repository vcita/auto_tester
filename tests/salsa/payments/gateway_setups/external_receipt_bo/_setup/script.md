# Script: External receipt - back office (setup)

`prepare_receipt_account(page, context, deny_pos=True)` in `gateway_setups_account.py`:

- `deny_features(context, "point_of_sale")` before login (flags are read into the session
  at login time).
- `fn_login(page, context, username, password)` — isolated account UI login.
- `create_client(context, "simon", "bolivar", email)` (`tests/account_api.py`) → stores
  `receipt_client_id` / `receipt_client_name` / `receipt_client_email`.
- `assign_app(context, "mockreceipts")` (`tips_checkout_api.assign_app`) → admin-auth
  POST `/platform/v1/apps/mockreceipts/assign`.
