# Function: logout

> **Type**: Function
> **Status**: Active
> **Last Updated**: 2024-01-20

## Purpose
Logout from vcita by clicking the user menu and selecting Logout.

## Parameters
None required.

## Returns
Clears from context:
- `logged_in_user`: Removes the logged in user

## Steps
1. Click on the user avatar button (shows user initials like "AU") in the top-right header
2. Wait for the dropdown menu to appear
3. Click "Logout" in the dropdown menu
4. Wait for redirect to login page
5. Verify login form is visible

## Success Criteria
- URL contains "vcita.com/login"
- Page title is "Login to vcita"
- Login form is visible (Email field, Password field, Login button)

## Notes
- This function uses ONLY visible UI elements - no direct URL navigation
- The user avatar displays the user's initials (first letters of first and last name)
- "Logout" is the last item in the user dropdown menu
- There may be a brief Cloudflare security check after logout before the login page loads
