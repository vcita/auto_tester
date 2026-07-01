"""
Environment URL resolution for the test runner.

Maps environment names (production, integration, feature-env) to API and app URLs.
Mirrors the known-envs pattern from automation-js/runtime/envs.js.
"""

from __future__ import annotations


KNOWN_ENVS = {
    "production": {
        "api_base_url": "https://api.vcita.biz",
        "app_base_url": "https://app.vcita.com",
        "directory_id": "16403",
    },
    "integration": {
        "api_base_url": "https://api2.meet2know.com",
        "app_base_url": "https://app.meet2know.com",
        "directory_id": "970",
    },
}

FEATURE_ENV_TEMPLATES = {
    # core service host (API). e.g. name="automation-aviv" ->
    # https://core-automation-aviv.external.int-eks.vchost.co
    "api_base_url": "https://core-{name}.external.int-eks.vchost.co",
    # The fenv UI is served by the frontage host (the legacy app-{name} host is
    # not provisioned -> dead origin / 526). Keep this the host ROOT only: route
    # helpers append "/app/..." themselves, and the "/login" entry point
    # redirects to "/app/login" in-browser. See the fenv-ui-login skill.
    "app_base_url": "https://frontage-{name}.external.int-eks.vchost.co",
}

# Directory the autotester provisions accounts on inside a feature env. Every
# fenv is cloned from the same base snapshot, so the "Auto sandbox WL" directory
# carries a stable uid (4umu6pzkmmiwgdr7) and a seed numeric id. The numeric id
# is per-DB (autoincrement), so it is NOT the integration directory (970) -- it
# resolves to 15 in the snapshot. We default to that seed but prefer resolving
# it at runtime by member email (see account_factory.discover_directory_id), so
# the suite still works if a future snapshot renumbers it. Mirrors the
# feature-env block in automation-js/runtime/envs.js.
FEATURE_ENV_DIRECTORY_EMAIL = "test1+auto.wl@vmeetme.com"
FEATURE_ENV_DIRECTORY_ID = "15"


def is_feature_env(env: str) -> bool:
    """True for per-developer feature envs (anything that isn't a known env)."""
    return bool(env) and env not in KNOWN_ENVS


def resolve_urls(env: str) -> dict[str, str]:
    """
    Resolve an environment name to API and app base URLs.

    Args:
        env: 'production', 'integration', or a feature-env name (e.g. 'aviv').

    Returns:
        Dict with 'api_base_url', 'app_base_url', and 'directory_id'.
    """
    if env in KNOWN_ENVS:
        return KNOWN_ENVS[env].copy()
    return {
        "api_base_url": FEATURE_ENV_TEMPLATES["api_base_url"].format(name=env),
        "app_base_url": FEATURE_ENV_TEMPLATES["app_base_url"].format(name=env),
        "directory_id": FEATURE_ENV_DIRECTORY_ID,
    }


def resolve_api_base_url(env: str) -> str:
    """Shorthand: resolve only the API base URL for an environment."""
    return resolve_urls(env)["api_base_url"]
