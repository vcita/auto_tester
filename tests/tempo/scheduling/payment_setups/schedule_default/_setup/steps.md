# Schedule Service Default Setup

## Objective
Prepare a fresh account with a client for the schedule-service-default scenario.

## Prerequisites
- Isolated account provisioned by the runner (username/password in context).

## Steps
1. Create a client `first1 last1` via API (the appointment attendee).
2. Log in to the isolated account.

## Expected Result
- Logged in as the business owner; a client `first1 last1` exists.

## Context Updates
- Save `ps.client` (id, name) for the test.
