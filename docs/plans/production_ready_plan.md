# Production-Ready Test System Plan

This plan defines what is required for the test suite to run in production: any environment, on a CI/CD system, within a 1-hour window, with stuck detection, team notifications, and account connection config supplied outside the project (not in a config file in the repo).

---

## 1. Ability to run on every environment

**Goal**: The same test code and runner must work in dev, staging, production, or any other environment without code changes. Configuration is environment-specific, not hardcoded.

**Requirements**:

- **Single entry point**: One way to run tests (e.g. `python main.py run` or equivalent) that reads configuration and runs against the configured target.
- **Environment-driven config**:
  - **Base URL** per environment (e.g. `https://app.vcita.com`, `https://app.meet2know.com`, fenv, custom).
  - **Auth** (username/password or tokens) supplied per environment—never in repo; use env vars or a secure config store.
  - Optional: **Feature flags or env markers** if some tests must be skipped in certain environments (e.g. skip payment-gateway tests in prod).
- **No hardcoded URLs or credentials**: All target URLs and auth come from config or env (e.g. `TARGET_BASE_URL`, `TARGET_AUTH_USERNAME`, `TARGET_AUTH_PASSWORD`). Defaults in `config.yaml` for local dev only; CI and other envs override via env or CI secrets.
- **Documentation**: Document which env vars (or config keys) define “the environment” so any team can run against their env by setting those only.

**Deliverables**:

- Config loading that merges: default `config.yaml` + env overrides (and optionally env-specific file or secret).
- README or `docs/` section: “Running in different environments” with the list of variables and how to set them in Jenkins/GitHub Actions/etc.

---

## 2. Parallel runner on a CI/CD system (Jenkins or alternatives)

**Goal**: Run the full test suite in parallel on a CI/CD platform so that total wall time stays within the 1-hour cap. The runner must integrate with the chosen system (jobs, agents, artifacts, status).

**Options** (examples; pick one or support multiple):

- **Jenkins**: Pipeline with parallel stages or parallel job matrix. Each “slot” runs a subset of categories (shard). Parameters: `TARGET_BASE_URL`, auth secrets, optional `SHARD_INDEX` / `SHARD_TOTAL`. Publish JUnit XML and artifacts (videos, screenshots) from each slot; optional Slack notification post-build.
- **GitHub Actions**: Matrix strategy with `SHARD_INDEX` / `SHARD_TOTAL`; each job runs one shard. Secrets for `TARGET_*`; artifacts for reports and run output; Slack (or Teams) via existing actions or webhook.

**Requirements**:

- **Sharding**: Orchestrator or CI job must split work so each “run” (single process or one CI job) executes a subset of categories. Sharding is by category (e.g. `shard_index = hash(category) % shard_total`) so that no single run gets all categories. Combined with in-process parallel workers (see existing plan), each CI job can run multiple categories in parallel within its slot, and the whole suite is split across N jobs.
- **Single command per job**: Each CI job runs one command (e.g. `python main.py run`) with env set (shard index/total, target URL, auth). No need for the runner to “know” Jenkins vs GitHub; it just reads env and config.
- **Artifacts**: JUnit XML (and optionally HTML report) plus run output (e.g. `_runs/` or equivalent) so the CI system can publish test results and failure artifacts. Optional: only upload artifacts on failure to save space.
- **Status**: Exit code 0 only when all tests in that run passed; non-zero on failure so CI marks the build/job as failed.

**Deliverables**:

- Documented “CI setup” for at least one system (e.g. Jenkinsfile or GitHub Actions workflow) showing:
  - How to set `TARGET_BASE_URL` and auth (secrets).
  - How to set `SHARD_INDEX` and `SHARD_TOTAL` (e.g. matrix).
  - How to run the runner and publish JUnit + artifacts.
- Runner supports reading `SHARD_INDEX` / `SHARD_TOTAL` (or equivalent) and running only the categories for that shard.

---

## 3. Hard 1-hour cap: every run must finish within one hour

**Goal**: Every hour a new “all runs” cycle starts. Therefore no single run (whether one process or one CI job) may exceed 1 hour. If it would, it must be stopped or split so that the next cycle can start on time.

**Requirements**:

- **Global run timeout**: A run (one process or one CI job) has a **maximum wall-clock time** (e.g. 55 minutes to leave a buffer before the next cycle). When the timeout is reached:
  - Stop dispatching new categories (if using an in-process parallel runner).
  - Optionally: signal or kill in-progress work so the process exits within the cap (e.g. 60 minutes job timeout in CI + 55-minute internal limit).
- **Sharding and worker count**: Size shards and workers so that **each run’s total work fits in &lt; 1 hour**:
  - Either: enough parallel workers so that `(sum of category durations in that run) / workers < 1 hour`.
  - Or: enough CI shards so that each shard runs a subset that completes in &lt; 1 hour.
- **CI job timeout**: The CI job itself must have a timeout (e.g. 60 or 65 minutes) so the platform kills the job if something hangs. This is the last line of defense.

**Deliverables**:

- Config or env: `max_run_time_seconds` (e.g. 3300 for 55 minutes). Orchestrator enforces it and stops/cancels when exceeded.
- CI configuration: job timeout set to 60 (or 65) minutes.
- Documentation: “Why 1 hour” and how sharding + timeouts ensure the next cycle can always start.

---

## 4. System to trigger the accountable team (e.g. Slack)

**Goal**: When a run fails (or when critical regressions occur), the team responsible is notified so they can act. Notification can continue to be delivered via Slack (or similar).

**Requirements**:

- **Trigger on failure**: On run failure (non-zero exit, or JUnit/test result indicating failures), trigger a notification.
- **Recipient**: The “accountable team”—e.g. channel or group that owns the product under test. Configurable (e.g. Slack channel, webhook URL, or email list) so it can be set per env or per project.
- **Content**: Notification should include at least:
  - Run identifier (e.g. build number, run id, branch, commit).
  - Summary: failed vs passed, and which categories/tests failed.
  - Link to the run (CI job URL, artifact URL, or dashboard) so the team can open failures and videos/screenshots.
- **Delivery mechanism**: Prefer existing channels; you mentioned Slack—use Slack webhook or Slack CI integration (e.g. “Slack Notification” in Jenkins, or “slack-notify” in GitHub Actions). Optional: same payload to Teams or email if needed later.

**Deliverables**:

- **Notification step** in CI (or in the runner as a post-run hook): on failure, call Slack webhook (or equivalent) with a structured message (run id, branch, failed categories/tests, link to results).
- **Configuration**: Slack webhook URL (or channel id) and optional “notify on success” flag come from env or secrets (e.g. `SLACK_WEBHOOK_URL`, `SLACK_CHANNEL`). Not in repo.
- **Docs**: How to set up the webhook and what the message contains so the accountable team can configure their channel.

---

## 5. Stuck detection: stop a run after a few seconds of no progress

**Goal**: If a run is stuck (e.g. browser hang, infinite wait), it must be detected and stopped within a few seconds so that other parallel runs (or the next hourly cycle) are not blocked. “Few seconds” is configurable (e.g. 30–60 seconds of no progress).

**Requirements**:

- **Definition of “stuck”**: No progress = no test completion (no new test or step finished) for a continuous period (e.g. `stuck_timeout_seconds`).
- **Scope**: Apply per category or per test (or both):
  - **Per test**: If a single test does not complete within `test_activity_timeout_seconds`, consider it stuck and fail it (then continue or stop the category according to policy).
  - **Per category**: If the category run has had no test completion for `stuck_timeout_seconds`, consider the category stuck and abort it (mark failed/timeout), release resources, and continue with other categories if in parallel.
- **Action on stuck**: Mark the test or category as failed (e.g. “timeout” or “stuck”), stop the browser/process for that slot, and continue the rest of the run (other categories or workers) so others get CPU/time.
- **Configuration**: `stuck_timeout_seconds` (and optionally `test_activity_timeout_seconds`) in config or env so ops can tune (e.g. 30–60 seconds for “few seconds” in your requirement).

**Deliverables**:

- **Activity watchdog**: A component that observes “last completion time” (last test or step finished). If `now - last_completion > stuck_timeout_seconds`, trigger “stuck” handling.
- **Integration**: Watchdog runs in the same process as the runner (or in the orchestrator); when stuck is detected, it signals the running category/test to stop (e.g. set a flag, or kill the worker process), marks the result as timeout/stuck, and allows other workers to continue.
- **Config**: `stuck_timeout_seconds` (default e.g. 60) and optional per-test `test_activity_timeout_seconds` in `config.yaml` or env.
- **Reporting**: Stuck/timeout appears in JUnit and in run summary (e.g. “Category X: timeout (stuck)”).

---

## 6. Account connection config not in project config file

**Goal**: The configuration used to connect the test account (URL, username, password, or tokens) must **not** live in a config file that is part of the project (e.g. `config.yaml` in the repo). Credentials in the repo are a security risk and prevent safe use in CI and shared environments. Connection details must be supplied by a different, secure mechanism.

**Requirements**:

- **No account/connection secrets in repo**: The project must not contain any file (e.g. `config.yaml`, `config.local.yaml`, `.env` committed to git) that holds:
  - Target base URL (if it identifies a specific account or env),
  - Username / password or API tokens for the account under test.
- **Allowed in repo**: Non-secret defaults are fine (e.g. `target.base_url: ""` or a placeholder) so the app knows which keys to look for; the actual values must come from elsewhere.
- **Alternative ways to supply connection config** (implement at least one; support multiple):
  - **Environment variables**: e.g. `TARGET_BASE_URL`, `TARGET_AUTH_USERNAME`, `TARGET_AUTH_PASSWORD`. Set in the shell, in CI secrets, or in a `.env` file that is gitignored and never committed. Runner reads these and overrides any in-repo config.
  - **CI/CD secrets**: Jenkins credentials, GitHub Actions secrets, GitLab CI variables, etc. The CI job injects them as env vars (or writes a temporary config that is not in the repo). No secrets in the project tree.
  - **Secret manager / vault**: Optional integration with a secret store (e.g. HashiCorp Vault, AWS Secrets Manager, Azure Key Vault). At run start, the runner (or a small bootstrap script) fetches the connection config and passes it via env or a short-lived temp file that is not in the repo.
  - **External config file outside repo**: Config file path provided via env (e.g. `CONFIG_FILE=/secure/path/config.yaml`). The file lives on the machine or in a secure volume, not in the project directory; it is not committed. Runner loads from that path when set.
- **Local development**: For local runs, use one of the above (e.g. a gitignored `.env` or a local config path). Document clearly that `config.yaml` in the project must not contain real credentials and how to set connection config locally.

**Deliverables**:

- **Runner behavior**: Runner (and any code that needs account connection) reads connection config only from: env vars, optional external config path (env-specified), or optional secret-manager integration. It does **not** read username/password or sensitive URL from `config.yaml` (or any file under the project) when a secure source is available.
- **Config layout**: `config.yaml` in the project holds structure and non-secret defaults (e.g. timeouts, feature flags). Placeholders or empty values for `target.auth` and `target.base_url`; real values come from env or external source.
- **Documentation**: Document the supported ways to supply account connection (env vars, CI secrets, optional vault/external file) and that no credentials belong in the project config file.

---

## Implementation order (suggested)

| # | Item | Summary |
|--|------|--------|
| 1 | Run on every env | Config + env overrides for URL/auth; document env vars. |
| 2 | Parallel runner on CI | Sharding (SHARD_INDEX/TOTAL), one CI example (e.g. Jenkins or GitHub Actions), artifacts + JUnit. |
| 3 | 1-hour cap | max_run_time_seconds + CI job timeout; ensure shard/worker sizing. |
| 4 | Trigger accountable team | Slack (or webhook) on failure; configurable channel/URL; message with run id, failures, link. |
| 5 | Stuck detection | Watchdog for no progress; stop after stuck_timeout_seconds; mark timeout and free resources. |
| 6 | Account config not in project | Connection config (URL, auth) only from env, CI secrets, or external/vault; not in config file in repo. |

---

## Summary

- **1. Every env**: Config and env for URL/auth; no hardcoded credentials; docs for variables.
- **2. CI parallel**: Sharded runs on Jenkins (or GitHub Actions / GitLab CI); single command, JUnit + artifacts.
- **3. 1-hour max**: Global run timeout (e.g. 55 min) and CI job timeout (e.g. 60 min); sharding so each run fits.
- **4. Notifications**: On failure, notify accountable team via Slack (or webhook); configurable; message with failures and link.
- **5. Stuck detection**: No progress for N seconds → mark stuck/timeout, stop that run, let others continue; configurable N.
- **6. Account config not in project**: Connection (URL, auth) supplied only via env vars, CI secrets, secret manager, or external config path—never from a config file in the project repo.
