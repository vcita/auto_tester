# Matters Management Setup

## Objective
Prepare the isolated account for matters-management tests: log in and create the two
background contacts the scenario operates on.

## Prerequisites
- Isolated auto-account created by the runner (username/password in context).

## Steps
1. Log in to the isolated account.
2. Create the "matter client" contact via API (a standalone contact that will later be nested).
3. Create the "contact client" contact via API (the contact that matters are added under).

## Expected Result
- User is logged in and on the dashboard.
- Two distinct contacts exist with distinct names ("matter client", "contact client").

## Context Updates
- Save `matter_client_id`, `matter_client_name`, `matter_client_email`.
- Save `contact_client_id`, `contact_client_name`, `contact_client_email`.
