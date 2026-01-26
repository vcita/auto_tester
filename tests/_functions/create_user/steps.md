# Create User (and onboard)

## Objective

Create a new vcita user via the signup flow (or onboard an existing new user), dismiss all one-time setup dialogs, and validate that a second login shows no dialog so the account is ready for other tests.

## Prerequisites

- Browser on any page (function will navigate to login).
- For signup: a valid email that is not already registered (or use onboarding-only mode with existing new user credentials).

## Steps

1. Navigate to login page (base_url + "/login", from config or params: `base_url`).
2. Click the **Sign Up** link at the bottom of the login page.
3. Fill the signup form: Email, Your Name or Business Name, Password (default `vcita123` if not provided).
4. Click **Let's go** and wait for redirect (e.g. to dashboard or verification step).
5. If in onboarding-only mode (credentials provided but no signup), skip to step 6.
6. Log in with the new credentials (reuse `fn_login`).
7. Dismiss one-time dialogs: in a loop, detect known onboarding dialogs (from [create_user_discovery](../../../docs/plans/create_user_discovery.md)), click Skip / Later / Close until no dialog appears for a short period (e.g. 5–10 s).
8. Log out (`fn_logout`), then log in again with the same credentials.
9. Assert that no setup dialog appears within 10 s (validation).
10. Account is ready; optionally return credentials for config update.

## Expected result

- New user exists and is logged in after step 6.
- After step 9, no modal/dialog on second login.
- Context may be updated; config is updated by the **create_user** CLI command after this function succeeds.

## Test data

- Email: from params or env.
- Password: from params or env; default **vcita123**.
- Name: from params or generated (e.g. "Test User {timestamp}").
