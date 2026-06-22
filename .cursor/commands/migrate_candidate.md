# Migrate Candidate

End-to-end workflow to pick a legacy `automation-js` candidate, open its Jira ticket, migrate it into `autotester` with zero scope/quality loss, review, stabilize, and keep the coverage tracker live at every step.

This command **orchestrates** existing skills and commands; it does not redefine their rules. Follow each referenced source as the authority.

The coverage tracker (Google Sheet + Confluence page `4690444289`) must reflect the **real** state of the migration as it progresses — not only at the end. Update it at each relevant step so the row `Status` always matches where the work actually is.

**Skills/commands to follow:**
- **Migration rules and DoD:** `migrate-automation-js-feature` skill (read its SKILL.md)
- **Subagent-per-test isolation & context management:** `.cursor/rules/subagent-test-isolation.mdc`
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

## Tracker status — keep it live

The `update-migration-coverage-tracker` skill is the authority for **how** to run the tracker tool (env, args, counting rules, full-row re-pass). This command only says **when** to update it and **which** status to set. Every update goes through the committed tool — **never** hand-edit the Sheet or Confluence page.

Map each step to the row `Status` (full lifecycle in the skill):

| After step | Status to set | Meaning |
|------------|---------------|---------|
| Step 2 (ticket + branch created) | `Proposed` | Candidate identified; implementation not started. |
| Step 3 (writing phase docs / `test.py`) | `In progress` | Implementation underway; stability gate not yet passed. |
| Step 3 end / Step 6 (runnable, runs not yet green) | `Needs stabilization` | Implemented and runnable, but focused/stress runs are not green. |
| Step 6 → Step 7 (stability gate passed, PR opened) | `In review` | The only status that counts toward progress while the PR is open. |
| After the PR merges to `master` | `Merged` | The only true "done". |
| Any step where work stalls | `Blocked` | Note the blocker in `Scope covered`. |

Rules that apply to every tracker update below:

- **Re-pass the full row on every upsert** (matched by `--feature`). The Sheet upsert rewrites the whole row, so any column you omit is blanked — carry forward every known field (`--scope`, `--original`, `--migrated`, `--improvement`, `--stability`, `--jira-*`, `--pr-*`).
- **Do not increment the progress counters** (`--ff-migrated` / `--sc-migrated`) until the row is `In review` or `Merged`. Early statuses (`Proposed`, `In progress`, `Needs stabilization`, `Blocked`) do not count toward progress.
- **Never jump straight to `In review`/`Merged`** from partial implementation, failed focused runs, unresolved heal requests, or guessed runtime data.

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
- **Summary:** `[autotester migration] <candidate scope>`
- **Sprint:** `sprint` (default active sprint)
- **Assignee:** `assignee` (default `Aviv`)
- **Proposed branch name:** `<ISSUE-KEY>_<short_candidate_description>`

Ask whether to proceed with these values or change the candidate, epic, sprint, or assignee. **Wait for an explicit answer before continuing.**

Once approved, use the `manage-jira-issues` skill to create the ticket:

- **Description:** legacy feature path, scope to migrate, and link back to the epic.
- **Assignee:** resolve `assignee` via `lookupJiraAccountId`.

Capture the created issue key (e.g. `VCITA2-XXXXX`) — it is needed for the branch name, PR, and tracker row. Then create the feature branch (alphanumeric, underscores, dashes only — `git-branch-naming`).

**Tracker:** once the ticket and branch exist, upsert the row at **`Proposed`** via the `update-migration-coverage-tracker` skill — `--feature`, `--path`, `--status "Proposed"`, `--scope` (planned scope), `--jira-key`/`--jira-url`, and `--latest-branch`. Leave run/stability columns and the progress counters empty (this status does not count toward progress).

---

## Step 3 — Migrate (zero scope/quality loss)

Follow the `migrate-automation-js-feature` skill end to end:

- Read the full legacy chain (feature, steps, page objects, API helpers) before writing code.
- Create `migration_mapping.md` (local, not committed) before `test.py`.
- Implement in strict phase order: `steps.md` → `script.md` → `test.py` → `changelog.md`; register in `_category.yaml`.
- **Isolate each migrated test's authoring in a subagent** (`subagent-test-isolation.mdc`): per test, `test-scaffolder` (sonnet) → `steps.md`, `test-explorer` (opus) → `script.md` (heavy MCP stays inside it), `test-codegen` (sonnet) → `test.py`. The orchestrator keeps the mapping, tracker state, and run/heal loop. When a candidate spans multiple scenarios/tests, **`/clear` between independent tests** — all durable state (mapping, phase files, `_category.yaml`) is on disk.
- Honor the **hard gate**: 3 clean focused runs, then re-verify scope and quality against the legacy test before any stress test.

**Tracker:** when implementation starts (phase docs / `test.py` being written), upsert the same row to **`In progress`** (re-pass the known columns). Once the test is runnable but the focused/stress runs are not yet green, move it to **`Needs stabilization`**. Still no progress-counter increment at either status.

---

## Step 4 — Reduce waits and durations (without scope/quality loss)

Per the skill's "Reduce Waits And Duration" section: cut fixed sleeps, redundant navigation, and repeated logins; replace fixed sleeps with explicit condition waits; move out-of-scope prerequisites to API setup. **Never** trade scope, assertions, in-scope UI actions, or selector strength for speed — if a speedup would, skip it and report the trade-off.

---

## Step 5 — Code review and fix

Run `/codeReview` on the changes (it applies the `code-review-checklist` skill). Fix **all** surfaced issues, then re-run Phase 3.5 rule validation from `/implement_test` if any selectors/timing/navigation changed.

---

## Step 6 — Stress test

Run `/stress_test categories: <category/subcategory> iterations: <iterations>` (default 3) on `env`. Monitor to completion. Investigate and fix any non-infrastructure failures, then re-run until stable.

**Tracker:** keep the row at **`Needs stabilization`** while runs are still failing or being re-run. Do **not** advance to `In review` until the stability gate is genuinely passed. If work stalls on an external dependency, product bug, or missing selector, set **`Blocked`** and record the blocker in `--scope`.

---

## Step 7 — Compare and update tracker (`In review`, then `Merged`)

- Run both the original `automation-js` scope and the migrated `autotester` scope; report the comparison table from the `migrate-automation-js-feature` skill (command, result, duration, duration improvement, scope coverage, quality notes).
- Once the stability gate has passed and the PR is open, update the tracker via the `update-migration-coverage-tracker` skill with real run evidence, the Jira key, the branch/PR link, and refreshed progress totals. Set the row `Status` to **`In review`** (PR open, not merged) — never `Merged` at this stage. This is the first status that **counts toward progress**, so this is where you increment `--ff-migrated` / `--sc-migrated` (full scenario set only) and refresh the Summary/`--tracked-*`/`--latest-*` rows.
- **Sync the Jira ticket to the tracker status, and post a migration retrospective comment.** Whenever you advance the tracker row, transition the matching `VCITA2` ticket to the corresponding status via the `manage-jira-issues` skill (`transitionJiraIssue`): `In progress`/`Needs stabilization` → **In Progress** (transition id `11`), `In review` → **In Review** (id `31`), `Merged` → **Done** (id `51`), `Blocked` → **Blocked** (id `41`). **When you move the ticket to `In review`, also add a comment** (`addCommentToJiraIssue`, `contentFormat: markdown`) — a short **migration retrospective** of *what went well and what was hard*:
  - scenario→subtest mapping / scope notes (confirm zero scope loss) and helper reuse;
  - **stabilization challenges with their root cause and fix** — flaky selectors, cold-load/skeleton races, async propagation/eventual-consistency, onboarding-wizard/overlay interference, backend or UI behaviour changes vs legacy, and any mechanism/scope deviations (with the why);
  - the final stress result (e.g. `10/10 on <date>`) and how many runs/iterations it took to stabilize.

  Keep it tight and use **flat bullet lists** — nested/ordered lists do not survive the markdown→ADF conversion (they render as empty bullets). This makes each ticket a durable record for reviewers and a knowledge base for future migrations (especially the hard ones).
- **After the PR merges to `master`**, run the same upsert again for that `--feature` with `--status "Merged"` (re-pass every column). This is the only time a row should read `Merged`. Update **both** the Sheet and Confluence: pass `--refresh-confluence` and re-pass the current ff/sc totals (`--ff-*`/`--sc-*`) plus `--tracked-*`/`--validated-scopes`/`--latest-branch`, so the page reflects the merge and its "Latest" rows stay current without zeroing the bars (per the `update-migration-coverage-tracker` skill). Then transition the Jira ticket to **Done** (id `51`).

---

## Definition of Done

All of the `migrate-automation-js-feature` DoD checks pass **and**:

- Jira ticket created under the epic, in the sprint, assigned to `assignee`.
- `/codeReview` issues resolved.
- Stress test stable at `iterations` runs on `env`.
- Coverage tracker kept live across the run — the row advanced through `Proposed` → `In progress` → `Needs stabilization` → `In review` as the work actually progressed (using `Blocked` if it ever stalled), never skipping ahead of the real state.
- Coverage tracker updated with measured results, with the row `Status` set to `In review` (PR open); flipped to `Merged` only after the PR merges.
- Jira ticket transitioned to match the tracker status (**In Review** at PR-open, **Done** at merge), **and** a *migration retrospective* comment (what went well / what was hard, with stabilization root causes + fixes) posted on the ticket when it moved to `In review`.

Do not commit or push without explicit approval (per repo rules). Keep `migration_mapping.md`, `plan.md`, and `_health.json` churn out of any commit.
