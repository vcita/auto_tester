# Create User - Detailed Script

> **Status**: Implemented from discovery
> **Discovery**: [docs/plans/create_user_discovery.md](../../../docs/plans/create_user_discovery.md)

## Initial state

- Browser may be on any page.
- Login URL: base_url + "/login", where base_url comes from params or config/context (e.g. `https://www.vcita.com`).

## Actions

### 1. Open login page and go to signup

- Navigate to `login_url`.
- Wait for page load (handle Cloudflare if present).
- Click link "Sign Up" at bottom (Don't have an account? **Sign Up**).
- Wait for Sign Up view: heading "Sign Up", form with Email, Your Name or Business Name, Password.

### 2. Fill signup form

- Fill **Email** (from params `email` or `username`).
- Fill **Your Name or Business Name** (from params `name` or default "Test User {timestamp}").
- Fill **Password** (from params `password` or default `vcita123`).
- Click button "Let's go".
- Wait for navigate: either to dashboard (success) or verification/error message.

### 3. Login (if not already on dashboard)

- If URL contains dashboard, skip. Otherwise call `fn_login(page, context, username=email, password=password)`. Login uses context.base_url (from config) for login URL.

### 4. Dismiss onboarding dialogs

- Loop: while a known onboarding dialog is visible (e.g. role=dialog, or text "Get started" / "Skip" / "Later"):
  - Click the dismiss action (Skip, Later, I'll do it later, Close, or X).
  - Wait 1–2 s.
- Exit loop when no dialog visible for 5–10 s (or max iterations).
- Documented dialogs and selectors: see discovery doc; extend as new dialogs are found.

### 5. Validate: logout and login again

- Call `fn_logout(page, context)`.
- Call `fn_login(page, context, username=email, password=password)`.
- Wait 10 s and assert no dialog appears (e.g. no `[role="dialog"]` visible, or no overlay with onboarding copy).
- If a dialog appears, fail assertion: "New user still has onboarding dialog on second login."

### 6. Done

- Optionally set context keys (e.g. `created_user_email`, `created_user_ready`).
- Do **not** write config; the `create_user` CLI command updates config after this function succeeds.

## Success verification

- After step 5, page is on dashboard (or main app) and no modal is visible for 10 s.
- Second login did not show any one-time setup popup.
