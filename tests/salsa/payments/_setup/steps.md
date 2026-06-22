# Payments Category Setup

## Objective
Login to vcita, create the client required by invoice picker flows, and create a paid service for invoice line items.

## Prerequisites
- Valid vcita account credentials (from config.yaml)
- Payment gateway is NOT connected for this stage

## Steps

1. Login to vcita
   - Use the login function to authenticate
   - Wait for dashboard to load
2. Create invoice picker client
   - Create `Appt TestClient` via API
   - Store the created client name as `invoice_client_search_term`
3. Create required-payment service via API
   - Create a service with `paid_force` charge type and price `100`
   - Store the service name as `invoice_service_name`

## Expected Result
- User is logged in
- Client picker has an existing client available for invoice flows
- Invoice item picker has a non-zero paid service available

## Context Updates
- Save `logged_in_user` from login function
- Save `created_client_id`, `created_client_name`, `created_client_email`, and `invoice_client_search_term`
- Save `invoice_service`, `invoice_service_name`, and `invoice_service_price`

## Notes
- This category uses record payments only (no online payment collection)
