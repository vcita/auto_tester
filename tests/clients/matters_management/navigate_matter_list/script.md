# Navigate Matter From List - Script

> Status: Verified live on integration 2026-06-08 (VCITA2-13952)

## Initial State
- After `nest_matter`: "matter client" is nested under "contact client", so the matter
  page lists "contact client" as a sibling matter row.

## Actions (`matters_helpers.click_matter_in_list` + `expect_title`)
1. Open the shared contact's page `/app/clients/{contact_client_id}` (after nesting it
   lists the whole family: contact client, matter_1, matter_2, matter client). The nested
   matter's own standalone URL no longer resolves, so navigate from the contact page.
2. Inner Vue frame: click `.matter-list-row` filtered by "matter client";
   assert `.matter-name-title` == "matter client".
3. Click `.matter-list-row` filtered by "contact client";
   assert inner `.matter-name-title` text == "contact client" (legacy `title shows`).
   The two-way navigation proves the list selection drives the title (the legacy single
   click was flaky — the title lagged the click and failed ~2/3 runs).

## Selector notes
- Matter list rows are `.matter-list-row`; the open-matter title is `.matter-name-title`
  (no data-qa); suggested product data-qa: `data-qa="matter-list-row"`, `data-qa="matter-title"`.
