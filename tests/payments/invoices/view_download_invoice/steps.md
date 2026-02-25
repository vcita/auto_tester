# View and Download Invoice

## Objective
Verify a client can view and download an invoice from a single flow.

## Prerequisites
- An invoice exists and is sent
- Client portal access is available
- No payment gateway connected

## Steps
1. Open invoice details in Billing & Invoicing
2. Verify public/client view action is available
3. Open "View Invoice"
4. Click "Download" or "PDF"
5. Verify the download starts

## Expected Result
- Invoice view is accessible to the client when supported
- Invoice download is initiated when supported

## Context Updates
- Save `client_portal_status`
- Save `download_status`
