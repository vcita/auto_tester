# Delete Client From CRM (Bulk Action)

Migrated from `automation-js/features/steps/crm-bulk-actions.feature` scenario
**Delete client from CRM** (VCITA2-13798).

## Goal
Verify that selecting a client in the CRM and using the bulk "Delete" action
deletes that client: it no longer appears in the client list while the other
client remains.

## Preconditions (created via account API)
- Two clients: `first01 last01` and `first02 last02` (the deletion targets `first02 last02`).

## Steps
1. Open the clients list.
2. Select the client `first02 last02`.
3. Bulk-delete the selected client (confirm, then acknowledge the success dialog).
4. Search the clients list for this test's clients → only `first01 last01` remains.

## Expected results
- After deletion, the client list (scoped to this test's clients) shows exactly
  `first01 last01` (the deleted `first02 last02` is gone).
