# New Notes (POV) Setup

## Objective
Prepare an isolated account so the new POV notes UI renders: enable the per-business
`rollout.clients.new_notes` flag before the app loads, then provide a client matter to
attach notes to.

## Prerequisites
- Isolated account created by the runner (`--env` + admin token); username/password in context.

## Steps
1. Enable `rollout.clients.new_notes` via the feature-flag API — **before login** (the SPA
   reads this per-business flag at app-load time; enabling it mid-session leaves the legacy
   notes dialog in place).
2. Log in to the isolated account.
3. Create one client matter via API (`/platform/v1/clients`).
4. Navigate to the matter detail page.

## Expected Result
- Browser is logged in and on the matter detail page.
- `rollout.clients.new_notes` is ON for this business; `rollout.ai.note_summary` is OFF (default).
- Context contains `created_matter_id`, `created_matter_name`, `created_matter_email`.
