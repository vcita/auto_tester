# Override Price Type Setup

## Objective
Prepare a fresh account with a client and six API-created services for the price-override scenario.

## Prerequisites
- Isolated account provisioned by the runner (username/password in context).

## Steps
1. Create a client `first1 last1` via API.
2. Create six services via API (require to pay $100, suggest to pay $50, display a fee $10, display for a fee, display free, dont display).
3. Log in to the isolated account.

## Expected Result
- Logged in; a client and the six services exist.

## Context Updates
- Save `ps.client` and `ps.services` for the test.
