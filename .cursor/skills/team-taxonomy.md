# Team Taxonomy & Placement (auto_tester)

Shared reference for placing every test under its owning team. Both
`generate-subcategory` and `migrate-automation-js-feature` follow this.

## Canonical teams

`backstage`, `maestro`, `salsa`, `spotlights`, `tango`, `tempo`.

A test always belongs to exactly one of these. `backstage` may have no tests
yet; its folder is created only when a test lands there.

## Folder rule (team-first)

```
tests/<team>/<domain>/<subcategory>/<test>/
```

- `<team>` — one of the canonical teams above (a "team group": organizational
  only, no `_setup`, no account of its own).
- `<domain>` — the product area and the **account boundary**: the runner creates
  one fresh isolated account per domain (e.g. `tempo/scheduling`,
  `salsa/payments`), never per team. A domain may be owned by one team, or split
  so different subcategories live under different teams (e.g. `payments` exists
  as both `salsa/payments` and `tempo/payments`).
- `<subcategory>` / `<test>` — unchanged from the legacy layout.

## `_category.yaml` requirements

- **Team root** (`tests/<team>/_category.yaml`): minimal group marker.
  ```yaml
  name: <Team Title>
  team: <team>
  team_group: true
  description: Team group for <Team Title>-owned tests (organizational only; no account).
  ```
- **Domain / subcategory** `_category.yaml`: include an explicit `team: <team>`
  field. Deeper subcategories inherit the team from the nearest ancestor that
  declares it, so a `team:` on the domain (account-boundary) config is enough;
  add it to a subcategory only when it overrides the parent.

Discovery resolves a category's team as: explicit `team:` > derived from the
top-level team folder name > inherited from the parent. `team_group: true` (or a
top-level canonical-team folder) marks a non-account team group.

## Source of truth — Confluence "Squads responsibilities"

The authoritative owner of every product component is the company Confluence
page **"Squads responsibilities"** (space `PS`, pageId `2615410911`):
<https://myvcita.atlassian.net/wiki/spaces/PS/pages/2615410911/Squads+responsibilities>.
It is a `Component -> Squad` table and changes over time, so **read the live
page** (via the Atlassian MCP `getConfluencePage`, pageId `2615410911`) when
placing a new test — do not rely on memory or on the provenance comment alone.

How to read it:

- Identify the product **component(s)** the test exercises (e.g. "Invoices",
  "Estimates", "Calendar", "Quick Actions", "Staff Roles and Permissions",
  "Business Info", "Take Payment").
- Look that component up in the table; its **Squad** is the owning team.
- The old `Steps` squad was dissolved — rows show `~~Steps~~ <NewTeam>`; use the
  new team (its invoicing/estimates work went to **Salsa**, its
  CRM/clients/documents work went to **Tempo**).
- The page lists `spotlight`-style names as **Spotlights** in auto_tester (always
  plural).
- Only the six canonical teams own auto_tester tests. If a component maps to a
  non-product squad (e.g. `BI`, `Professional Solutions`, `Production`,
  `Jira Security`), it is not a UI-test owner — ask the user.

Key disambiguations confirmed from the page (verify against the live page; these
can change): Invoices / Estimates / Invoice Templates -> **Salsa**; all
gateway/checkout/tips/coupons/POS/taxes payments -> **Salsa**; Products -> **Salsa**;
Dashboard + Quick Actions -> **Spotlights** (but Dashboard *sales* widget -> Salsa,
*clients/scheduling* widgets -> Tempo, *campaigns* widget -> Tango); Staff Roles
and Permissions -> **Spotlights**; CRM / Notes / Multiple Matters / Documents /
Import-Export Clients -> **Tempo**; Business Info / Reviews / Client Portal /
Calendar / Services / Bookings -> **Tempo**; Staff UI / Upgrade Page / My Account
-> **Maestro**; Inbox / Conversations / Campaigns / Spam Protection -> **Tango**.

## Choosing the team

1. **Confluence "Squads responsibilities" (authoritative)** — map the test's
   product component to its squad on the live page (above). This wins over every
   other signal.
2. **Existing sibling** — if the domain/subcategory already lives under a team
   and that matches the page, keep it consistent.
3. **Migration provenance (hint only)** — the source
   `automation-js/features/<squad>/...` folder, recorded in `Migrated from ...`
   comments, is a useful starting guess but is **subordinate to the Confluence
   page** (e.g. provenance `steps`/`tempo` for invoices is overridden to `salsa`).
4. **Ask** — if the component is ambiguous, spans squads, or maps to a
   non-product squad, ask the user rather than guessing silently.

## Provenance squad → team mapping (fallback hint)

Use only as a starting guess; the Confluence page overrides it.

| automation-js squad | auto_tester team |
|---|---|
| `backstage` | `backstage` |
| `maestro` | `maestro` |
| `salsa` | `salsa` |
| `spotlight` / `spotlights` | `spotlights` (always plural) |
| `tango` | `tango` |
| `tempo` | `tempo` |
| `steps` | dissolved — look up the component on Confluence (salsa or tempo) |

## Verify placement

- `python main.py list` — top level shows only team groups.
- `python main.py list --team <team>` — the new domain appears under its team.
- Reference categories by full team-prefixed path (e.g.
  `tempo/scheduling/services`) when running or listing.
