# Create, cancel and recreate scheduled payments — Steps

Precondition (from setup): an isolated account with the payments checkout flags
enabled, a mock payment gateway connected, a client (`first last`) created via
API, and a credit card saved on the client.

## Phase A — create and verify Active
1. Open Quick Actions and choose "Schedule payment".
2. Pick the client in the client picker.
3. In the scheduled-payments dialog, set the plan name "Scheduled Payments Plan Name", amount 10, frequency 3, continue to the summary, accept the client consent, and create the plan (no success toast in this path).
4. Close the creation success dialog.
5. Open the plan side pane from the client card (Payments tab -> Scheduled payments panel -> first item) and verify it shows the client, the plan name, and state Active.

## Phase B — cancel and verify Canceled
6. Cancel the plan from the side pane (opened by URL) and confirm the cancellation.
7. Reopen the side pane from the client card and verify the same plan now shows state Canceled.

## Phase C — recreate with a future start date and verify Active
8. Open Quick Actions and create a second scheduled-payments plan "sppn", amount 10, starting next month.
9. Open the latest plan side pane from the client card and verify it shows the client, plan name "sppn", and state Active.
