# Script — Setup (Invoice Items And Copy)

`setup_invoice_items_copy` calls `invoice_billing_setup.seed_invoice_account(page,
context, with_tax=True)`:
- `fn_login` with the isolated account credentials.
- `POST /platform/v1/clients` → `created_client_id`, `created_client_name` = "first last".
- `create_service_via_api(charge_type="paid_non_secured", price="100")` →
  `invoice_service_name`.
- `create_tax_via_api(name="TS<ts>", rate="13")` → `invoice_tax_name` / `invoice_tax_rate`.
