# CP Multi-Booking — Category Setup

## Objective
Prepare a fresh isolated account for the client-portal multi-booking scenarios: enable the
`multi_appointment_client_booking` feature flag, create the shared client and base services
(service1, service2), create Staff1/Staff2, and enable client-portal multi booking.

## Prerequisites
- Isolated account provisioned by the runner (username/password in context).

## Steps
1. Enable feature flag `multi_appointment_client_booking` via API.
2. Create client "Chuck Norris" via API.
3. Create service `service1` (duration 20, appointment, business location "TLV") via API.
4. Create service `service2` (duration 40, appointment, business location "TLV") via API.
5. Create staff `Staff1` (role user) via Platform API.
6. Create staff `Staff2` (role user) via Platform API.
7. Enable client-portal multi booking via API (allow_client_multi_booking = true) and read it back.
8. Log in to the isolated account (business session, for parity with the legacy background).

## Expected Result
- Feature flag enabled; client, service1, service2, Staff1, Staff2 exist; CP multi booking enabled.

## Context Updates
- Save `mb.service1`, `mb.service2`, `mb.staff2`, `mb.client` for the tests.
