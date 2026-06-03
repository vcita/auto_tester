"""Shared account-scoped API helpers for isolated-account tests.

Centralizes the admin feature-flag management and the per-account token/base-url
accessors that were previously duplicated across subcategory account helpers.
"""

import os
from datetime import datetime, timedelta, timezone

import requests

REQUEST_TIMEOUT = 30
# Account-scoped REST calls follow the project's 5s wait policy (see project.mdc
# "5-second max state waits"); the longer REQUEST_TIMEOUT above is only for the
# admin feature-flag management calls.
ACCOUNT_API_TIMEOUT = 5
APPOINTMENT_LEAD_DAYS = 30


def admin_headers() -> dict:
    admin_token = os.environ.get("VCITA_ADMIN_TOKEN")
    if not admin_token:
        raise ValueError("VCITA_ADMIN_TOKEN is not set; cannot manage feature flags")
    return {"Authorization": f"Admin {admin_token}"}


def api_base(context: dict) -> str:
    api_base_url = context.get("api_base_url")
    if not api_base_url:
        raise ValueError("api_base_url missing from context")
    return api_base_url.rstrip("/")


def account_user_id(context: dict) -> str:
    user_id = (context.get("auto_account") or {}).get("user_id")
    if not user_id:
        raise ValueError("auto_account user_id missing for feature-flag management")
    return user_id


def account_token(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    token = auto_account.get("api_token") or auto_account.get("auth_token")
    if not token:
        raise ValueError("auto_account api_token missing from context")
    return token


def reset_features_cache(context: dict) -> None:
    requests.get(
        f"{api_base(context)}/infra/automation/reset_features_table_cache",
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )


def _set_features(context: dict, features: str, action: str) -> None:
    response = requests.post(
        f"{api_base(context)}/admin/feature_flags/{account_user_id(context)}/{action}",
        json={"features": features},
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    reset_features_cache(context)


def enable_features(context: dict, features: str) -> None:
    """Whitelist (enable) one or more comma-separated feature flags, then reset the cache."""
    _set_features(context, features, "add_user_features")


def deny_features(context: dict, features: str) -> None:
    """Blacklist (deny) one or more comma-separated feature flags, then reset the cache."""
    _set_features(context, features, "blacklist_user_features")


def create_client(context: dict, first_name: str, last_name: str, email: str) -> dict:
    """Create a client and capture the client-portal JWT `token` returned alongside it.

    The portal token (returned next to the client object, not inside it) is what
    opens the client portal as that client (`?client_jwt=<token>`), mirroring the
    legacy `scenarioContext.clients[email].token`.
    """
    response = requests.post(
        f"{api_base(context)}/platform/v1/clients",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "source_name": "automation",
        },
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    body = response.json()
    payload = body.get("data") or body
    client = payload.get("client") or payload
    client["token"] = payload.get("token") or body.get("token")
    if not client.get("token"):
        raise ValueError(f"Client API response did not include a portal token: {body}")
    client["id"] = client.get("id") or client.get("uid")
    client["full_name"] = f"{first_name} {last_name}"
    return client


# --------------------------------------------------------------------------- #
# Shared account-scoped REST primitives
#
# Centralized here so isolated-account subcategories reuse one implementation
# instead of each copying its own `_account_request` / staff / service / booking
# helpers (this module's whole reason to exist).
# --------------------------------------------------------------------------- #
def resolve_api_base_url(context: dict) -> str:
    api_base_url = context.get("api_base_url")
    if api_base_url:
        return api_base_url.rstrip("/")

    base_url = (context.get("base_url") or "").rstrip("/")
    if "meet2know.com" in base_url:
        return "https://api2.meet2know.com"
    if "vcita.com" in base_url:
        return "https://api.vcita.biz"
    if "app-" in base_url and ".external.int-eks.vchost.co" in base_url:
        return base_url.replace("https://app-", "https://core-", 1)

    raise ValueError("api_base_url is missing from context and could not be inferred")


def account_headers(context: dict) -> dict:
    return {"Authorization": f"Bearer {account_token(context)}"}


def account_request(context: dict, method: str, path: str, **kwargs) -> dict:
    base_url = kwargs.pop("base_url", None) or resolve_api_base_url(context)
    headers = kwargs.pop("headers", None) or account_headers(context)
    response = requests.request(
        method,
        f"{base_url}{path}",
        headers=headers,
        timeout=ACCOUNT_API_TIMEOUT,
        **kwargs,
    )
    if not response.ok:
        raise requests.HTTPError(
            f"{response.status_code} {response.reason} for {path}: {response.text[:500]}",
            response=response,
        )
    return response.json() if response.text else {}


def pivot_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    value = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not value:
        raise ValueError("auto_account pivot_uid is missing from context")
    return value


def last_category_uid(context: dict) -> str:
    response = account_request(
        context, "GET", f"/platform/v1/categories?business_id={pivot_uid(context)}"
    )
    categories = response.get("data", {}).get("categories", [])
    if not categories:
        raise ValueError("No service categories returned for auto account")
    return categories[-1]["id"]


def first_staff_uid(context: dict) -> str:
    """Resolve and cache the account owner (first) staff uid.

    Call this BEFORE creating any additional staff so callers that need the
    original owner (e.g. seeding an owner-assigned appointment) stay deterministic
    regardless of staff-list ordering once more staff exist.
    """
    cached = context.get("account_first_staff_uid")
    if cached:
        return cached
    response = account_request(
        context, "GET", f"/platform/v1/businesses/{pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for auto account")
    context["account_first_staff_uid"] = staffs[0].get("id") or staffs[0].get("uid")
    return context["account_first_staff_uid"]


def create_service_via_api(context: dict, service_name: str) -> dict:
    payload = {
        "category": {"uid": last_category_uid(context)},
        "staff_data": [{"uid": first_staff_uid(context), "enabled": True}],
        "name": service_name,
        "service_type": "appointment",
        "currency": "USD",
        "duration": 60,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": "free",
        "display": "true",
        "max_attendance": 2,
    }
    response = account_request(context, "POST", "/v2/settings/services", json=payload)
    service = response.get("data") or response
    service_id = service.get("id") or service.get("uid")
    if not service_id:
        raise ValueError(f"Service API response did not include an id: {response}")
    return {"id": service_id, "name": service.get("name") or service_name}


def future_appointment_start_time(lead_days: int = APPOINTMENT_LEAD_DAYS) -> str:
    start_time = datetime.now(timezone.utc) + timedelta(days=lead_days)
    start_time = start_time.replace(minute=0, second=0, microsecond=0)
    return start_time.isoformat().replace("+00:00", "Z")


def create_appointment_via_api(
    context: dict, service: dict, client: dict, staff_uid: str | None = None
) -> dict:
    payload = {
        "business_id": pivot_uid(context),
        "staff_id": staff_uid or first_staff_uid(context),
        "start_time": future_appointment_start_time(),
        "service_id": service["id"],
        "client_id": client["id"],
    }
    response = account_request(context, "POST", "/business/scheduling/v1/bookings", json=payload)
    data = response.get("data") or response
    return data.get("booking") or data
