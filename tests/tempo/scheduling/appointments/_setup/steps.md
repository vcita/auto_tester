# Appointments Setup

## Objective

Prepare the environment for appointment tests by:
1. Creating a test service (required for booking appointments)
2. Creating a test client (appointments need to be booked for someone)

## Prerequisites

- User is logged in (from scheduling category _setup)

## Steps

1. Create a test service using the `create_service` function
2. Create a test client using the `create_client` function
3. Navigate to the Calendar page (where appointments are created)

## Context Variables Set

- `created_service_id`: ID of the test service
- `created_service_name`: Name of the test service
- `created_client_id`: ID of the test client
- `created_client_name`: Full name of the test client
- `created_client_email`: Email of the test client

## Success Criteria

- Service exists in the system
- Client exists in the system
- Ready to create appointments
