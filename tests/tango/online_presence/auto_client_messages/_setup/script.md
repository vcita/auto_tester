# Setup — Auto Client Messages (Detailed Script)

## Initial State
- Fresh isolated automatic account (created by the runner from `_category.yaml`
  `account_profile`).

## Actions

### Step 1: Log in to the isolated account
- **Action**: Call function
- **Function**: `fn_login`
- **Parameters**: `username`, `password` from context (isolated account creds)
- **Expected**: Dashboard ready; `logged_in_user` set in context.

## Success Verification
- User is on the dashboard (handled inside `fn_login`).
