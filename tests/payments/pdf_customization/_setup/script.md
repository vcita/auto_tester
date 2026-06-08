# PDF Customization Setup - Script

## Initial State
- Runner created an isolated account; not yet logged in.

## Actions
1. Call `fn_login(page, context, username, password)` with the isolated-account credentials
   from `context`.

## Success Verification
- Login completes and the frontage app is loaded.

## Waits / Stability
- Login readiness is handled by the shared `fn_login` function.
