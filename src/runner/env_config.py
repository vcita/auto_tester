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
    },
    "integration": {
        "api_base_url": "https://api2.meet2know.com",
        "app_base_url": "https://app.meet2know.com",
    },
}

FEATURE_ENV_TEMPLATES = {
    "api_base_url": "https://core-{name}.external.int-eks.vchost.co",
    "app_base_url": "https://app-{name}.external.int-eks.vchost.co",
}


def resolve_urls(env: str) -> dict[str, str]:
    """
    Resolve an environment name to API and app base URLs.

    Args:
        env: 'production', 'integration', or a feature-env name (e.g. 'aviv').

    Returns:
        Dict with 'api_base_url' and 'app_base_url'.
    """
    if env in KNOWN_ENVS:
        return KNOWN_ENVS[env].copy()
    return {
        "api_base_url": FEATURE_ENV_TEMPLATES["api_base_url"].format(name=env),
        "app_base_url": FEATURE_ENV_TEMPLATES["app_base_url"].format(name=env),
    }


def resolve_api_base_url(env: str) -> str:
    """Shorthand: resolve only the API base URL for an environment."""
    return resolve_urls(env)["api_base_url"]
