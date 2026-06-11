# CP Scheduling With Taxes

## Objective
Verify that an anonymous client booking a taxed service through the client-portal scheduler sees the tax on the scheduler calendar and on the resulting client-portal meeting page.

## Prerequisites
- A default tax (10%) and a taxed `suggest2pay` service ($100) exist (from `_setup`).
- Logged in to the isolated account.

## Steps
1. Grab the public link of the `suggest2pay` service from the services list.
2. Open the grabbed link as an anonymous client.
3. Verify the client-portal scheduler calendar page shows: service `suggest2pay`, tax `+Tax`, price `$100.00`.
4. As the client, schedule a new appointment (first name `jimmy`, an email).
5. Verify the client-portal meeting page shows: meeting `suggest2pay`, price `100`, currency `USD`, tax `+Tax`.

## Expected Result
- The scheduler calendar and the client-portal meeting page both display the +Tax indication and the $100 price.

## Context Updates
- None (terminal scenario for this isolated subcategory).
