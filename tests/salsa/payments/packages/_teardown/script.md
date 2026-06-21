# Packages (BO) Teardown — Detailed Script

## Initial State
- Tests have appended created package ids and client-package ids to
  `context["packages_cleanup"]` ({"packages": [...], "client_packages": [...]}).

## Actions

### Step 1: Delete client-packages created during the run (API)
- For each id in `context["packages_cleanup"]["client_packages"]`, call
  `delete_client_package(context, id)` (DELETE /platform/v1/payment/client_packages/{id}).

### Step 2: Delete packages created during the run (API)
- For each id in `context["packages_cleanup"]["packages"]`, call
  `delete_package(context, id)` (DELETE /platform/v1/payment/packages/{id}).

## Notes
- Best-effort: deletion failures are swallowed (the isolated account is torn down by the
  runner regardless; this keeps the account list minimal across stress iterations).
- Appointments scheduled by the UI tests are cancelled within those tests (scenario 8 cancels
  its own appointment); none remain active for teardown.

## Success Verification
- No created packages / client-packages remain.
