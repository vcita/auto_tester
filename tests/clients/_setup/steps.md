# Clients Category Setup

> **Type**: Setup
> **Status**: Active
> **Last Updated**: 2024-01-20

## Purpose
Setup procedure for the Clients test category. Ensures user is logged in before running client-related tests.

## Steps
1. Call: login
   - username: {from config or environment}
   - password: {from config or environment}

## Success Criteria
- User is logged in
- Dashboard or app page is accessible
- Context contains `logged_in_user`

## Notes
- This setup runs once before all tests in the clients category
- Uses the shared login function from `_functions/login`
