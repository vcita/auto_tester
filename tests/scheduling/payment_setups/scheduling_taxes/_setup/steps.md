# Scheduling With Taxes Setup

## Objective
Prepare a fresh account with a client for the scheduling-with-taxes scenario.

## Prerequisites
- Isolated account provisioned by the runner (username/password in context).

## Steps
1. Create a client `first1 last1` via API.
2. Log in to the isolated account.

## Expected Result
- Logged in; a client `first1 last1` exists.

## Context Updates
- Save `ps.client` for the test (taxes and services are created in the test body).
