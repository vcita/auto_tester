#!/usr/bin/env bash
# Pre-start hook: validate required configuration, then hand off to main.py.
# No DB migration is needed for this service.
set -euo pipefail

if [[ -z "${VCITA_ADMIN_TOKEN:-}" ]]; then
  echo "[entrypoint] WARNING: VCITA_ADMIN_TOKEN is not set; per-category account creation will fail." >&2
fi

echo "[entrypoint] starting: python main.py $*"
exec python main.py "$@"
