# Notes Setup

## Objective
Prepare the notes subcategory by opening the full-category matter when available, or creating an API matter for isolated runs.

## Prerequisites
- Parent Clients setup has run and the browser is logged in.
- Auto-account API token is available in context.

## Steps
1. If `created_matter_id` exists, navigate to `/app/clients/{created_matter_id}` and reuse it.
2. If no matter exists, create one through `/platform/v1/clients`.
3. For isolated API setup, save both `created_matter_*` and `notes_setup_matter_*` keys.
4. Navigate to `/app/clients/{created_matter_id}`.

## Expected Result
- Browser is on the selected matter detail page.
- Context contains:
  - `created_matter_id`
  - `created_matter_name`
  - `created_matter_email`
- Isolated runs also contain `notes_setup_matter_id` for teardown.
