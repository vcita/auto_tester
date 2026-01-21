# Function: login

> **Type**: Function
> **Status**: Active
> **Last Updated**: 2024-01-20

## Purpose
Login to vcita with email and password credentials.

## Parameters
| Name | Type | Required | Description |
|------|------|----------|-------------|
| username | string | Yes | Email address for login |
| password | string | Yes | Account password |

## Returns
Saves to context:
- `logged_in_user`: The email that was used to login

## Steps
1. Navigate to vcita login page (https://www.vcita.com/login)
2. Wait for security check to complete (if present)
3. Enter email in the Email field
4. Enter password in the Password field
5. Click the Login button
6. Wait for dashboard to load
7. Verify successful login (dashboard visible)

## Success Criteria
- URL is https://app.vcita.com/app/dashboard
- Page title contains "Dashboard"
- Dashboard elements are visible (Quick Actions, Calendar, etc.)

## Notes
- Cloudflare security check may appear on page load (wait up to 5 seconds)
- reCAPTCHA is present but doesn't block automated logins in test environment
- If already logged in, function returns immediately
