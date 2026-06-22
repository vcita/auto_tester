# Appointments Teardown

## Objective

Clean up test data created during the appointments tests:
1. Delete the test service created in setup
2. Delete the test client created in setup

## Prerequisites

- Tests have been run
- Test service and client exist from _setup

## Steps

1. Delete the test client using the `delete_client` function
2. Delete the test service using the `delete_service` function

## Context Variables Cleared

- `created_service_id`
- `created_service_name`
- `created_client_id`
- `created_client_name`
- `created_client_email`

## Success Criteria

- Test service is deleted
- Test client is deleted
- Context variables are cleared
