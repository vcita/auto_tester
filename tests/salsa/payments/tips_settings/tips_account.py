"""Account preparation helpers for the tips_settings subcategories.

Handles feature-flag management (before login), login, and persisting tips via
``POST /platform/v1/payment/settings`` (the endpoint the POV Save uses). The
feature flag that gates the tips tab is ``rollout.payments.tips_settings``;
``rollout.payments.gateway_platform`` is denied for the no-gateway scenario so
the tips tab shows the connect-provider alert.

Feature-flag and account-token helpers live in :mod:`tests.account_api` and are
re-exported here for the subcategory setup steps.
"""

import time

import requests
from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import (  # re-exported for subcategory setups
    REQUEST_TIMEOUT,
    account_token,
    api_base,
    deny_features,
    enable_features,
)

__all__ = [
    "TIPS_FEATURE_FLAG",
    "GATEWAY_PLATFORM_FLAG",
    "enable_features",
    "deny_features",
    "set_tips_via_api",
    "post_tips",
    "login",
]

TIPS_FEATURE_FLAG = "rollout.payments.tips_settings"
GATEWAY_PLATFORM_FLAG = "rollout.payments.gateway_platform"

PAYMENT_SETTINGS_PATH = "/platform/v1/payment/settings"
PERSIST_POLL_SECONDS = 10
PERSIST_POLL_INTERVAL = 0.5


def _payment_settings_tips(context: dict) -> list:
    """GET payment settings and return the persisted tip values (independent read, not the POST echo)."""
    response = requests.get(
        f"{api_base(context)}{PAYMENT_SETTINGS_PATH}",
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    tips = response.json().get("data", {}).get("payment_settings", {}).get("tips") or []
    values = []
    for tip in tips:
        value = tip.get("value")
        if value is not None:
            values.append(int(value))
    return values


def post_tips(context: dict, tip_values: list) -> None:
    """Single POST of percent tips to the payment-settings route (no read-back poll)."""
    payload = {
        "payment_settings": {
            "tips": [{"type": "percent", "value": int(v)} for v in tip_values]
        }
    }
    requests.post(
        f"{api_base(context)}{PAYMENT_SETTINGS_PATH}",
        json=payload,
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    ).raise_for_status()


def set_tips_via_api(context: dict, tip_values: list) -> None:
    """Persist percent tips through the endpoint the POV Save uses, confirmed by an independent read.

    The tips tab reads ``payment_settings.tips`` from ``POST /platform/v1/payment/settings``
    (paymentSettingsService.saveSettings). A flat ``PUT /v2/settings`` returns 200 but drops the
    tips field. The POST response echoes the payload, so persistence is confirmed with a separate
    GET poll (payment settings read can lag the write); the POST is retried once if the read lags.
    """
    expected = [int(value) for value in tip_values]
    post_tips(context, tip_values)
    deadline = time.monotonic() + PERSIST_POLL_SECONDS
    reposted = False
    while time.monotonic() < deadline:
        if _payment_settings_tips(context) == expected:
            return
        time.sleep(PERSIST_POLL_INTERVAL)
        if not reposted and time.monotonic() > deadline - PERSIST_POLL_SECONDS / 2:
            post_tips(context, tip_values)
            reposted = True
    raise AssertionError(
        f"Tips not persisted on payment settings after {PERSIST_POLL_SECONDS}s: "
        f"GET returned {_payment_settings_tips(context)}, expected {expected}"
    )


def login(page: Page, context: dict) -> None:
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username and password are missing from context")
    fn_login(page, context, username=username, password=password)
