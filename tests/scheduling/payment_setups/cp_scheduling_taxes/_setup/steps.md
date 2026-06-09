# CP Scheduling With Taxes Setup

## Objective
Prepare a fresh account with a default tax and a taxed service for the CP-scheduling scenario.

## Prerequisites
- Isolated account provisioned by the runner (username/password in context).

## Steps
1. Create a `default_tax` (10%, default for services) via API.
2. Create a `suggest2pay` service ($100) with the default tax via API.
3. Log in to the isolated account.

## Expected Result
- Logged in; a default tax and a taxed `suggest2pay` service exist.

## Context Updates
- Save `ps.service` (name) for the test.
