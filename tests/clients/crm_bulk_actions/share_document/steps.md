# Share Document From CRM (Bulk Action)

Migrated from `automation-js/features/steps/crm-bulk-actions.feature` scenario
**Share document from CRM** (VCITA2-13798).

## Goal
Verify that selecting all clients in the CRM and using the bulk "Share document"
action shares the document with the selected clients: the document appears in a
client's card conversation and its status is "Pending review".

## Preconditions (created via account API)
- Two clients: `first01 last01` and `first02 last02` (the second is the
  "current client" whose conversation is verified).

## Steps
1. Open the clients list.
2. Select all clients (all pages).
3. Bulk-share the document `clientDoc.pdf` to the selected clients (notify by email).
4. Open the current client's card → the document `clientDoc.pdf` is shown in the conversation.
5. Open the documents page → the document `clientDoc.pdf` status is "Pending review".

## Expected results
- `clientDoc.pdf` appears in the current client's card conversation.
- `clientDoc.pdf` status is "PENDING REVIEW" on the documents page.
