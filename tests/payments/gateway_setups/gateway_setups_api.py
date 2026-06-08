"""API seeds for the vcita-payments onboarding wizard scenarios (1-3).

The wizard scenarios need feature flags + an optional business_category applied to the
isolated account BEFORE login (the wizard, preliminary profession step, funnel-v1 upgrade
path and MCC dialog are all gated by those flags, and the prepopulated profession is read
from the business_category set at account level). Mirrors the legacy
``create_account_via_platform`` row (business_category + feature_flags) using the runner's
isolated account instead of a brand-new Platform business.
"""

import time

import requests

from tests.account_api import (
    REQUEST_TIMEOUT,
    admin_headers,
    enable_features,
    get_business,
    pivot_uid,
    resolve_api_base_url,
)

# Flags shared by every wizard scenario (hide_register_wizard is already an automation
# default). These expose the vcita-payments onboarding wizard + preliminary profession step.
WIZARD_FLAGS = (
    "vcita_payments_preliminary_step,vcitaPayments_wizard,"
    "merchant_vcita_payments_onboarding_wizard"
)
# Scenario 1 additionally puts the account on payment funnel v1 (forces the upgrade dialog
# when trying to connect a gateway) and disables direct gateway config.
FUNNEL_V1_FLAGS = "vp_payment_conversion_one,payment_gateways_disabled"

CATEGORY_POLL_SECONDS = 10
CATEGORY_POLL_INTERVAL = 0.5


def set_business_category(context: dict, business_category: str) -> None:
    """Set the business_category via the admin businesses endpoint, confirmed by read-back.

    Uses the same nested ``business.business`` payload shape as the runner's country/
    timezone updates. The prepopulated-profession wizard step reads this value.
    """
    payload = {"business": {"business": {"business_category": business_category}}}
    response = requests.post(
        f"{resolve_api_base_url(context)}/platform/v1/businesses/{pivot_uid(context)}",
        json=payload,
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()

    deadline = time.monotonic() + CATEGORY_POLL_SECONDS
    actual = ""
    while time.monotonic() < deadline:
        details = get_business(context).get("business") or {}
        actual = details.get("business_category") or details.get("category") or ""
        if actual == business_category:
            return
        time.sleep(CATEGORY_POLL_INTERVAL)
    raise AssertionError(
        f"business_category expected {business_category!r}, got {actual!r} after read-back"
    )


def enable_wizard_flags(context: dict, *, funnel_v1: bool = False) -> None:
    """Enable the onboarding-wizard feature flags (plus funnel-v1 flags when requested)."""
    flags = WIZARD_FLAGS
    if funnel_v1:
        flags = f"{flags},{FUNNEL_V1_FLAGS}"
    enable_features(context, flags)
