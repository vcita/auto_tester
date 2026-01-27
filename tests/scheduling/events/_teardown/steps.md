# Events Teardown

## Objective

Clean up test data created during the events tests:
1. Delete the test client created in _setup
2. Delete the group event service created in _setup

## Prerequisites

- Tests have been run
- Group event service and test client exist from _setup

## Steps

1. Delete the test client using the `delete_client` function
2. Delete the group event service using the `delete_service` function

## Context Variables Cleared

- `event_group_service_name`
- `event_client_id`
- `event_client_name`
- `event_client_email`
- `created_client_id` (from fn_create_client)
- `created_client_name` (from fn_create_client)
- `created_client_email` (from fn_create_client)

## Success Criteria

- Test client is deleted
- Group event service is deleted
- Context variables are cleared
