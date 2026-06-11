# Send Message From CRM (Bulk Action)

Migrated from `automation-js/features/steps/crm-bulk-actions.feature` scenario
**Send message from CRM** (VCITA2-13798).

## Goal
Verify that selecting a client in the CRM and using the bulk "Message" action
sends the message: it appears in the client's card conversation with the correct
subject and content.

## Preconditions (created via account API)
- Two clients: `first01 last01` and `first02 last02` (the message targets `first02 last02`).

## Steps
1. Open the clients list.
2. Select the client `first02 last02`.
3. Bulk-send a message with subject `hi` and content `hello` to the selected client.
4. Open the client's card → the last conversation message has subject `hi` and content `hello`.

## Expected results
- The client `first02 last02` receives a message whose subject is `hi` and content is `hello`.
