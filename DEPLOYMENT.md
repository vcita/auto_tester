# Deploying auto_tester to a feature environment

This service packages the auto_tester runner so it can run inside the cluster:

- **Primary:** a k8s **CronJob** that runs the full suite against a target env and exits.
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
  auto-tester run --headless --env integration
```

## Secrets

`VCITA_ADMIN_TOKEN` and `VCITA_DIRECTORY_ID` are synced from AWS SSM
(`/<environment>/<release>/auto-tester-creds`) into a k8s Secret by the External
Secrets Operator and injected as env vars (`helm_chart/templates/externalSecret.yaml`).
Never commit them.

## CronJob

Defined in `helm_chart/values_integration.yaml` (job `full-run`):
`python3 main.py run --headless --env $(TARGET_ENV)`, `squad: salsa`, nightly.

Validate locally:

```bash
helm lint helm_chart -f helm_chart/values_integration.yaml
helm template auto-tester helm_chart -f helm_chart/values_integration.yaml
```

Run on demand from a deployed CronJob:

```bash
kubectl create job --from=cronjob/auto-tester-full-run auto-tester-manual-1 -n <namespace>
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
