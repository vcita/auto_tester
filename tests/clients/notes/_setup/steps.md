# Notes Setup

## Objective
Prepare the notes subcategory to run independently by creating a matter through the API and opening its client detail page.

## Prerequisites
- Parent Clients setup has run and the browser is logged in.
- Auto-account API token is available in context.

## Steps
1. Create a client/matter through `/platform/v1/clients`.
2. Save the created matter ID, name, and email into context.
3. Navigate to `/app/clients/{created_matter_id}`.

## Expected Result
- Browser is on the created matter detail page.
- Context contains:
  - `created_matter_id`
  - `created_matter_name`
  - `created_matter_email`
