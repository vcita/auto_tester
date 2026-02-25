# Payments Category Setup

## Objective
Login to vcita so payments tests start from an authenticated state.

## Prerequisites
- Valid vcita account credentials (from config.yaml)
- Payment gateway is NOT connected for this stage

## Steps

1. Login to vcita
   - Use the login function to authenticate
   - Wait for dashboard to load

## Expected Result
- User is logged in
- Dashboard is loaded and ready for test-level navigation

## Context Updates
- Save `logged_in_user` from login function

## Notes
- This category uses record payments only (no online payment collection)
