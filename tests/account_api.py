"""Shared account-scoped API helpers for isolated-account tests.

Centralizes the admin feature-flag management and the per-account token/base-url
accessors that were previously duplicated across subcategory account helpers.
"""

import os

import requests

REQUEST_TIMEOUT = 30


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


def _account_get(context: dict, path: str) -> dict:
    response = requests.get(
        f"{api_base(context)}{path}",
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    return response.json() if response.text else {}


def _pivot_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    pivot_uid = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not pivot_uid:
        raise ValueError("auto_account pivot_uid is missing from context")
    return pivot_uid


def last_category_uid(context: dict) -> str:
    response = _account_get(context, f"/platform/v1/categories?business_id={_pivot_uid(context)}")
    categories = response.get("data", {}).get("categories", [])
    if not categories:
        raise ValueError("No service categories returned for auto account")
    return categories[-1]["id"]


def first_staff_uid(context: dict) -> str:
    response = _account_get(context, f"/platform/v1/businesses/{_pivot_uid(context)}/staffs?status=all")
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for auto account")
    return staffs[0].get("id") or staffs[0].get("uid")


def create_service(
    context: dict, name: str, charge_type: str, price: str, service_type: str = "appointment"
) -> dict:
    """Create a service via the account API. `charge_type` maps the legacy payment_setting
    (e.g. "display a fee" -> `paid_non_secured`, "suggest to pay" -> `paid`)."""
    payload = {
        "category": {"uid": last_category_uid(context)},
        "staff_data": [{"uid": first_staff_uid(context), "enabled": True}],
        "name": name,
        "service_type": service_type,
        "currency": "USD",
        "duration": 60,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": charge_type,
        "price": price,
        "display": "true",
        "max_attendance": 2,
    }
    response = requests.post(
        f"{api_base(context)}/v2/settings/services",
        json=payload,
        headers={"Authorization": f"Bearer {account_token(context)}"},
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    body = response.json() if response.text else {}
    service = body.get("data") or body
    if service.get("id") and not service.get("uid"):
        service["uid"] = service["id"]
    return service


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
