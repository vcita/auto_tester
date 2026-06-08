# Migrate Candidate

End-to-end workflow to pick a legacy `automation-js` candidate, open its Jira ticket, migrate it into `auto_tester` with zero scope/quality loss, review, stabilize, and update the coverage tracker.

This command **orchestrates** existing skills and commands; it does not redefine their rules. Follow each referenced source as the authority.

**Skills/commands to follow:**
- **Migration rules and DoD:** `migrate-automation-js-feature` skill (read its SKILL.md)
- **Coverage tracker:** `update-migration-coverage-tracker` skill
- **Jira ticket creation/assignment:** `manage-jira-issues` skill
- **Code review:** `/codeReview` command (runs the `code-review-checklist` skill)
- **Stress/stability:** `/stress_test` command

---

## Parameters

Parse these from the user's input; fall back to the defaults when not given. Do not ask for anything that has a default.

- `epic` — parent epic. **Default: `VCITA2-12727`**
- `sprint` — target sprint. **Default: current active sprint** (ask only if no active sprint can be resolved)
- `assignee` — **Default: `Aviv`** (resolve via `lookupJiraAccountId`)
- `candidate` — specific feature/scenario to migrate. **Default: auto-select** (see Step 1)
- `env` — **Default: `integration`**
- `iterations` — stress-test iterations. **Default: `3`**

---

## Step 1 — Select candidate

If the user named a candidate, use it. Otherwise auto-select:

1. Read the Confluence coverage tracker (page `4690444289`) via the `update-migration-coverage-tracker` skill to see what is already migrated and what remains.
2. From `automation-js/features`, propose one **not-yet-migrated** feature/scenario. Prefer self-contained, high-value flows with low cross-dependency.
3. State the chosen candidate and a one-line rationale before proceeding. Do not silently skip categories.

---

## Step 2 — Confirm ticket details, then open the Jira ticket

**STOP. Do not create the ticket yet.** Present the proposed ticket for confirmation and ask the user to approve or adjust:

- **Selected candidate** (from Step 1) and one-line rationale.
- **Parent epic:** `epic` (default `VCITA2-12727`)
- **Summary:** `[auto_tester migration] <candidate scope>`
- **Sprint:** `sprint` (default active sprint)
- **Assignee:** `assignee` (default `Aviv`)
- **Proposed branch name:** `<ISSUE-KEY>_<short_candidate_description>`

Ask whether to proceed with these values or change the candidate, epic, sprint, or assignee. **Wait for an explicit answer before continuing.**

Once approved, use the `manage-jira-issues` skill to create the ticket:

- **Description:** legacy feature path, scope to migrate, and link back to the epic.
- **Assignee:** resolve `assignee` via `lookupJiraAccountId`.

Capture the created issue key (e.g. `VCITA2-XXXXX`) — it is needed for the branch name, PR, and tracker row. Then create the feature branch (alphanumeric, underscores, dashes only — `git-branch-naming`).

---

## Step 3 — Migrate (zero scope/quality loss)

Follow the `migrate-automation-js-feature` skill end to end:

- Read the full legacy chain (feature, steps, page objects, API helpers) before writing code.
- Create `migration_mapping.md` (local, not committed) before `test.py`.
- Implement in strict phase order: `steps.md` → `script.md` → `test.py` → `changelog.md`; register in `_category.yaml`.
- Honor the **hard gate**: 3 clean focused runs, then re-verify scope and quality against the legacy test before any stress test.

---

## Step 4 — Reduce waits and durations (without scope/quality loss)

Per the skill's "Reduce Waits And Duration" section: cut fixed sleeps, redundant navigation, and repeated logins; replace fixed sleeps with explicit condition waits; move out-of-scope prerequisites to API setup. **Never** trade scope, assertions, in-scope UI actions, or selector strength for speed — if a speedup would, skip it and report the trade-off.

---

## Step 5 — Code review and fix

Run `/codeReview` on the changes (it applies the `code-review-checklist` skill). Fix **all** surfaced issues, then re-run Phase 3.5 rule validation from `/implement_test` if any selectors/timing/navigation changed.

---

## Step 6 — Stress test

Run `/stress_test categories: <category/subcategory> iterations: <iterations>` (default 3) on `env`. Monitor to completion. Investigate and fix any non-infrastructure failures, then re-run until stable.

---

## Step 7 — Compare and update tracker

- Run both the original `automation-js` scope and the migrated `auto_tester` scope; report the comparison table from the `migrate-automation-js-feature` skill (command, result, duration, duration improvement, scope coverage, quality notes).
- Update the Confluence coverage tracker via the `update-migration-coverage-tracker` skill with real run evidence, the Jira key, the branch/PR link, and refreshed progress totals. Set the row `Status` to `In review` (PR open, not merged) — never `Merged` at this stage. Flip it to `Merged` only after the PR lands on `master`.

---

## Definition of Done

All of the `migrate-automation-js-feature` DoD checks pass **and**:

- Jira ticket created under the epic, in the sprint, assigned to `assignee`.
- `/codeReview` issues resolved.
- Stress test stable at `iterations` runs on `env`.
- Coverage tracker updated with measured results, with the row `Status` set to `In review` (PR open); flipped to `Merged` only after the PR merges.

Do not commit or push without explicit approval (per repo rules). Keep `migration_mapping.md`, `plan.md`, and `_health.json` churn out of any commit.
