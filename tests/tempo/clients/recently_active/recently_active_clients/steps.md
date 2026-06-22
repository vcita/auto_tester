# Recently Active Clients

## Objective
Verify that the dashboard recently active clients widget starts empty and then lists clients with appointments, newest activity first.

## Prerequisites
- User is logged in from the clients category setup.
- A fresh auto-created account is available for the run.

## Steps
1. Create a service through the account API.
2. Create the first client through the account API.
3. Open the dashboard.
4. Verify the recently active clients widget shows the empty state.
5. Create an appointment for the first client through the account API.
6. Verify the recently active clients widget shows the first client.
7. Create a second client through the account API.
8. Create an appointment for the second client through the account API.
9. Verify the recently active clients widget shows the second client before the first client.

## Expected Result
- The dashboard initially reports that there are no recently active clients.
- After the first appointment, the first client appears in the widget.
- After the second appointment, both clients appear and the second client is listed first.

## Context Updates
- Save `recently_active_service_id` and `recently_active_service_name`.
- Save first and second recently active client IDs, names, and emails.
- Save created appointment payloads for debugging.
