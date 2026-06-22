# Packages (BO) — Subcategory Teardown

## Objective
Leave the isolated account clean: delete the packages and client-packages created by the
tests, and cancel any appointments scheduled during the run.

## Steps
1. Delete every package created during the run via API (CRUD: created packages are deleted).
2. Delete every client-package assignment created during the run via API.
3. Cancel any appointments that were scheduled by the UI tests (cannot be deleted; cancelled).

## Notes
- Services, taxes and products live on the isolated account and are removed when the account
  is torn down by the runner; only package/client-package/appointment objects are cleaned here
  to keep the account list minimal across iterations.

## Expected Result
- No leftover packages or client-packages remain from this run.
