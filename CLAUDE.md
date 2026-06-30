# CLAUDE.md — vcita Test Agent (autotester)

This is an **AI-driven black-box browser test agent** for vcita. There is no access to
vcita's source code — the agent explores the app like a real user and generates
self-healing Playwright tests.

The authoritative project rules and skills live under **`.cursor/`** (Cursor format).
This file wires them into Claude Code: read the relevant file(s) below **before** doing
the matching work, and follow them as binding project rules.

---

## Rules (`.cursor/rules/*.mdc`) — read before the matching task

| Task | Read first |
|------|-----------|
| Anything in this repo (orientation) | `.cursor/rules/project.mdc` — architecture, folder structure, cross-cutting principles |
| Building / exploring / generating a test or function | `.cursor/rules/build.mdc` |
| Fixing / healing / repairing a failing test (or a `.cursor/heal_requests/` item) | `.cursor/rules/heal.mdc` |
| Writing or editing `steps.md` | `.cursor/rules/phase1_steps.mdc` |
| Writing or editing `script.md` | `.cursor/rules/phase2_script.mdc` |
| Generating or editing `test.py` | `.cursor/rules/phase3_code.mdc` |
| Planning a full module test suite | `.cursor/rules/module_planning.mdc` |
| Editing `script.md`/`test.py` (keep steps in sync) | `.cursor/rules/sync-steps-with-script-changes.mdc` |

### Always-apply rules (honor without being asked)

- **Never commit generated run artifacts** (`.cursor/rules/no-commit-generated-artifacts.mdc`):
  `tests/**/_health.json` churn, `reports/`, `**/_runs/*`, `runs_index/`, `migration_mapping.md`,
  root `plan.md`. Stage explicit source paths only — never `git add -A`. Discard incidental
  `_health.json` churn with `git checkout -- tests/<category>/_health.json`.
- **Orphan account cleanup** (`.cursor/rules/orphan-account-cleanup.mdc`): when asked to "find and
  delete orphan accounts" (incl. typos), run the cleanup flow without clarifying questions —
  dry-run → check for active runs → delete → verify. Default env is `integration` only if none named.
- **Snapshot-first, no-vision MCP authoring** (`.cursor/rules/snapshot-first-authoring.mdc`): while
  driving the Playwright MCP browser to author/debug tests, use `browser_snapshot` (not screenshots),
  snapshot once per page then read the region via `browser_evaluate`, verify with `browser_wait_for`,
  and pull console/network logs on demand only. MCP runs `--caps=core` (no vision). Keeps token cost down.

## Skills (`.cursor/skills/`) — apply when the trigger matches

- **prefer-data-qa-selectors** — when authoring/updating Playwright UI tests. Selector order:
  `data-qa` → semantic (`get_by_role`, labeled fields) → text/CSS last. Never swap a UI action
  for an API call when that action is the behavior under test.
- **generate-subcategory** — scaffolding a new subcategory / "add tests for" / "scaffold tests".
  Creates Phase 1 files only (`_category.yaml` + `steps.md`); Phase 2/3 need MCP exploration.
- **migrate-automation-js-feature** — migrating legacy `automation-js` Gherkin features into
  autotester. Read the full legacy chain, build `migration_mapping.md` first, no scope loss.
- **stabilize-autotester-e2e** — fixing unstable tests, reducing runtime, health checks.
  Includes standing approval to commit+push the fix on its `VCITA2-XXXX` branch and open/update
  the PR once validated.
- **update-migration-coverage-tracker** — after a migrated test is validated/stabilized; updates
  the Confluence/Sheet tracker via the committed tool (never hand-edit).
- **team-taxonomy** (`.cursor/skills/team-taxonomy.md`) — how to resolve a test's owning team from
  the Confluence "Squads responsibilities" page (pageId `2615410911`, source of truth).
- **create-test-from-template** — end-to-end: reads a filled Confluence design template and
  delivers a stable, stress-tested test with no manual steps. Use when the user says "build the
  test", "create test from template", or provides a Confluence template URL. Covers Phase 1→3,
  focused run, heal loop, stress test, and Confluence Section 7 update.

## Subagents (`.cursor/agents/`) — isolate each test's authoring (pinned model tiers)

When implementing/migrating tests, delegate each test's authoring to these pinned-model subagents
so heavy MCP exploration traffic stays out of the orchestrator's context (see
`.cursor/rules/subagent-test-isolation.mdc`). Each returns only a file path + short summary — never
raw snapshots. `/clear` between independent tests (durable state is all on disk).

- **test-scaffolder** (sonnet) — Phase 1: writes one test's `steps.md`. Mechanical, no browser.
- **test-explorer** (opus) — Phase 2: live Playwright MCP exploration → verified `script.md`. The
  heavy-MCP, hard-reasoning phase; all snapshot traffic lives and dies inside it.
- **test-codegen** (sonnet) — Phase 3: transcribes verified code → `test.py`. No browser.

(`.cursor/agents` is bridged to `.claude/agents` via a SessionStart symlink; registers natively
from the next session.)

---

## Core principles (from `project.mdc` — do not violate)

- **Strict phase order, never skip:** `steps.md` → `script.md` → `test.py`. No script without
  steps; no code without script. Changes cascade through all three; log every change in `changelog.md`.
- **Real user actions only:** click/fill/navigate via the UI. No direct URLs (except entry point
  `base_url + "/login"`), no hidden URLs (`/api/...`, `/users/logout`), no `page.reload()`.
- **No retries for actions:** wait for a readiness condition, then act once. Read re-checks
  (async-propagating lists/widgets) may reload-and-recheck, capped at **2 retries (3 attempts)**.
- **Single detection per step, no fallbacks:** one condition per step; if not found, the test fails.
  No try/except alternates for the same condition.
- **Timeout = failure:** never catch a timeout and continue.
- **5-second max state waits** (`timeout=5000`). No fixed sleeps unless genuinely unavoidable
  (then minimal + documented).
- **Matter-entity agnostic:** the matter label varies by vertical (Clients, Properties, Patients,
  Students, Pets…). Use regex / positional / role selectors and `tests/_params`; never hardcode one label.
- **Reuse first:** check `tests/_functions/_functions.yaml` before writing steps; use
  `Call: function_name`. Reuse patterns from similar working tests before re-exploring.
- **Cleanup:** each category leaves minimal leftovers (setup objects deleted in teardown; follow CRUD).
- **Find existing appointments/events via the list page**, not the calendar (calendar is for creating).

## Layout & teams

- Tests are organized **team-first**: `tests/<team>/<domain>/<subcategory>/<test>/`.
- Canonical teams: `backstage`, `maestro`, `salsa`, `spotlights`, `tango`, `tempo`.
- The **domain** (e.g. `payments`, `scheduling`, `clients`) is the account boundary, not the team.
- Each test folder has `steps.md`, `script.md`, `test.py`, `changelog.md`.
- `tests/_functions/` = global reusable functions. `.context/current_run.json` = per-run shared state.

## Common commands

```bash
python main.py run --category <domain>                 # run a category (auto-creates account)
python main.py run --category scheduling/appointments  # run one subcategory path
python main.py run --selection clients scheduling/events  # multiple paths
python main.py run --headless --category payments      # headless (CI)
python main.py list                                    # full test tree
python main.py health --category <domain>              # health snapshot
python main.py stress_test --categories <domain> --iterations N
```

Run results / status source of truth: `tests/**/_runs/*/run.json` (latest run per category).
