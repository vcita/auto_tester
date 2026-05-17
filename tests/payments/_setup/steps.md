# Payments Category Setup

## Objective
Login to vcita and create the client required by invoice picker flows.

## Prerequisites
- Valid vcita account credentials (from config.yaml)
- Payment gateway is NOT connected for this stage

## Steps

1. Login to vcita
   - Use the login function to authenticate
   - Wait for dashboard to load
2. Create invoice picker client
   - Create `Appt TestClient`
   - Store the created client name as `invoice_client_search_term`

## Expected Result
- User is logged in
- Client picker has an existing client available for invoice flows

## Context Updates
- Save `logged_in_user` from login function
- Save `created_client_id`, `created_client_name`, `created_client_email`, and `invoice_client_search_term`

## Notes
- This category uses record payments only (no online payment collection)
