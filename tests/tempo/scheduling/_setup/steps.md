# Scheduling Category Setup

## Objective
Login to vcita and navigate to the Services settings page to prepare for scheduling tests.

## Prerequisites
- Valid vcita account credentials (from config.yaml)
- Account has permission to manage services

## Steps

1. Login to vcita
   - Use the login function to authenticate
   - Wait for dashboard to load

2. Navigate to Settings
   - Click "Settings" in the sidebar navigation
   - Wait for Settings page to load

3. Navigate to Services
   - Click "Services" option under "Scheduling & Sales" section
   - Wait for Services list page to load
   - Verify "Settings / Services" heading is visible

## Expected Result
- User is logged in
- Browser is on the Services settings page
- Ready to create/edit/delete services

## Context Updates
- Save `logged_in_user` from login function

## Notes
- The Settings page loads in an iframe (title="angularjs")
- Services is under the "Scheduling & Sales" section in Settings
