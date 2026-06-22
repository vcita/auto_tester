# Deploying autotester to a feature environment

This service packages the autotester runner so it can run inside the cluster:

- **Primary:** a set of k8s **CronJobs** (one per team/domain shard) that run their slice of the suite against a target env every 2 hours and exit.
- **Secondary:** the **GUI** (`python main.py gui`) for triggering/watching runs.

> **Scope note:** In Phase 0 the GUI is **local-only** (via `docker-compose` / `devspace`).
> `helm_chart/` deploys **only CronJobs** — there is no in-cluster GUI Deployment/Service yet.

The infra concepts are copied from [vcita/cronjobs](https://github.com/vcita/cronjobs)
(Docker + `shipit.yml` + `helm_chart/`) and [vcita/scrum-dashboard](https://github.com/vcita/scrum-dashboard)
(`docker-compose.yml` + `.dockerignore`), adapted to a Python + Playwright image.

## Files

| File | Purpose | Concept source |
|------|---------|----------------|
| `Dockerfile-base-image` | Heavy cached layer: Playwright base + `pip install` | cronjobs |
| `Dockerfile-to-deploy` | Light layer: copy source, default CMD = GUI | cronjobs / scrum-dashboard |
| `Dockerfile` | Single-stage image for local / compose | scrum-dashboard |
| `.dockerignore` | Exclude venv, run artifacts, secrets | scrum-dashboard |
| `docker-compose.yml`, `entrypoint_dev.sh` | Local run + env validation | scrum-dashboard |
| `helm_chart/` | Renders one CronJob per `jobs:` entry + External Secrets | cronjobs |
| `shipit.yml`, `jenkins-variables.yml` | CI build/deploy via Jenkins `common_build`/`common_deploy` | cronjobs |
| `devspace.yaml` | Local-against-cluster dev loop | - |

## Image

`mcr.microsoft.com/playwright/python:v1.40.0-jammy` (Chromium preinstalled, matches
`playwright==1.40.0`). The base differs from cronjobs (`python:3.11-alpine`) because
Chromium needs glibc + system libraries.

## Local

```bash
# Build + run the GUI on http://localhost:8080
docker compose up --build

# Run the full suite once against integration and exit
docker compose run --rm -e VCITA_ADMIN_TOKEN=... -e VCITA_DIRECTORY_ID=... \
  autotester run --headless --env integration
```

## Secrets

`VCITA_ADMIN_TOKEN` and `VCITA_DIRECTORY_ID` are synced from AWS SSM
(`/<environment>/<release>/autotester-creds`) into a k8s Secret by the External
Secrets Operator and injected as env vars (`helm_chart/templates/externalSecret.yaml`).
Never commit them.

## CronJobs (sharded nightly run)

The ~322-test suite is split across **12 CronJobs** in
`helm_chart/values_integration.yaml`. Each entry renders one CronJob → one pod,
and the pods run **in parallel** (the runner is sequential within a pod,
`parallel_tests: 1`), so every shard only needs to fit under its 1h
`activeDeadlineSeconds` cap. Shards target tests via `--team`, `--selection`,
or `--category` (see `main.py cmd_run`).

| Shard (CronJob) | Squad | Targets | ~Tests |
|---|---|---|---|
| `salsa-payments-core` | salsa | appointment + product + event payments | 44 |
| `salsa-payments-billing` | salsa | invoices + payments_emails + tips_checkout | 43 |
| `salsa-payments-gateways` | salsa | gateways, deposits, fees, refunds, records, pdfs, coupons_checkout | 41 |
| `salsa-payments-settings` | salsa | all payments settings/misc subcats | 28 |
| `salsa-commerce` | salsa | products + sales | 18 |
| `tempo-scheduling-booking` | tempo | appointments + events + multi_booking | 39 |
| `tempo-scheduling-calendar` | tempo | calendar(+settings) + services(+cats) + payment_setups | 29 |
| `tempo-clients` | tempo | clients | 43 |
| `tempo-misc` | tempo | documents + reviews + online_presence + settings | 13 |
| `maestro` | maestro | `--team maestro` | 8 |
| `spotlights` | spotlights | `--team spotlights` | 11 |
| `tango` | tango | `--team tango` | 2 |

Cadence is **every 2 hours** at even hours (`m */2 * * *`). The 2h interval is
larger than the 1h `activeDeadlineSeconds` cap, so consecutive runs never overlap.
Within each cycle the shards are staggered one minute apart (HH:00–HH:11) to
soften the burst of account-creation API calls (avoids 429 throttling); the long
shards still overlap and finish ~in parallel.

> **Account churn:** every-2h ⇒ up to 12 cycles/day ⇒ ~144 account batches/day
> (vs ~12 nightly). Make sure `cleanup_accounts` keeps pace and watch for 429s.

> Shard sizes are by **test count** — a proxy for time until we have real
> in-cluster timings. Rebalance the `jobs:` list after the first scheduled run
> if any shard approaches its 1h cap.

Validate locally:

```bash
helm lint helm_chart -f helm_chart/values_integration.yaml
helm template autotester helm_chart -f helm_chart/values_integration.yaml
```

Run a single shard on demand from its deployed CronJob:

```bash
kubectl create job --from=cronjob/autotester-salsa-payments-core autotester-manual-1 -n <namespace>
```

## Onboarding (Infra)

Tracked in **VCITA2-14113**. Infra must: create the ECR repo, wire `common_build`/`common_deploy`
for this repo, provision the SSM secret path, and add the project to shipit (integration).

### Open item: PodSecurity / non-root

The base image (`mcr.microsoft.com/playwright/python`) runs as **root** by default and the
CronJob pod template currently sets no `securityContext`. If the target namespaces enforce a
restricted/`runAsNonRoot` Pod Security Standard, the pods would be rejected at admission.
Confirm with Infra during VCITA2-14113 whether a `securityContext` (run as the image's `pwuser`,
uid 1000) is required — and validate that headless Chrome still launches under it (it may need
`--no-sandbox`, which is an app-side change in `src/runner/runner.py`). This is deferred until the
Tier-1 local image build can actually exercise Chrome.
