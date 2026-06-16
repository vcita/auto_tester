"""Shared account-scoped API helpers for isolated-account tests.

Centralizes the admin feature-flag management and the per-account token/base-url
accessors that were previously duplicated across subcategory account helpers.
"""

import calendar
import os
import time
from datetime import date, datetime, timedelta, timezone

import requests

REQUEST_TIMEOUT = 30
# Account-scoped REST calls follow the project's 5s wait policy (see project.mdc
# "5-second max state waits"); the longer REQUEST_TIMEOUT above is only for the
# admin feature-flag management calls.
ACCOUNT_API_TIMEOUT = 5
APPOINTMENT_LEAD_DAYS = 30

# Brief server-side transients happen under load: the gateway occasionally 429s and
# endpoints can 5xx for a few seconds. Network-level hiccups (read timeouts, dropped
# connections) are the same class of transient. Retry a couple of times with linear
# backoff before failing (at most TRANSIENT_RETRY_MAX_ATTEMPTS requests total).
TRANSIENT_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
TRANSIENT_EXCEPTIONS = (
    requests.exceptions.ReadTimeout,
    requests.exceptions.ConnectionError,
)
TRANSIENT_RETRY_MAX_ATTEMPTS = 3
TRANSIENT_RETRY_BACKOFF_SECONDS = 2.0


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
    url = f"{base_url}{path}"

    attempt = 0
    response = None
    while True:
        attempt += 1
        try:
            response = requests.request(
                method, url, headers=headers, timeout=ACCOUNT_API_TIMEOUT, **kwargs
            )
        except TRANSIENT_EXCEPTIONS:
            # Network-level transient (read timeout / dropped connection). Retry on the
            # same budget as transient status codes; re-raise once the budget is spent.
            if attempt >= TRANSIENT_RETRY_MAX_ATTEMPTS:
                raise
            time.sleep(TRANSIENT_RETRY_BACKOFF_SECONDS * attempt)
            continue

        if response.ok:
            return response.json() if response.text else {}
        if (
            response.status_code not in TRANSIENT_STATUS_CODES
            or attempt >= TRANSIENT_RETRY_MAX_ATTEMPTS
        ):
            break
        time.sleep(TRANSIENT_RETRY_BACKOFF_SECONDS * attempt)

    raise requests.HTTPError(
        f"{response.status_code} {response.reason} for {path}: {response.text[:500]}",
        response=response,
    )


def pivot_uid(context: dict) -> str:
    auto_account = context.get("auto_account") or {}
    value = auto_account.get("pivot_uid") or auto_account.get("business_id")
    if not value:
        raise ValueError("auto_account pivot_uid is missing from context")
    return value


def get_business(context: dict) -> dict:
    """Return the account's business object (name, email, country, ...)."""
    response = account_request(
        context, "GET", f"/platform/v1/businesses/{pivot_uid(context)}"
    )
    data = response.get("data") or response
    return data.get("business") or data


def update_business_country(context: dict, country_name: str) -> dict:
    """Set the business country (e.g. 'Israel') via the admin API (mirrors legacy
    update_country, which the platform endpoint requires admin auth for)."""
    payload = {"business": {"business": {"country_name": country_name}}}
    response = requests.post(
        f"{resolve_api_base_url(context)}/platform/v1/businesses/{pivot_uid(context)}",
        json=payload,
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    body = response.json() if response.text else {}
    data = body.get("data") or body
    return data.get("business") or data


def wait_for_business_country(context: dict, expected_country: str, timeout_s: int = 10) -> str:
    """Poll the business API until the saved country == ``expected_country``.

    The country write (update_business_country) is eventually consistent: a GET issued
    immediately after the POST can still echo the old country. Read it back before the
    UI loads so the business-info page never renders a stale country (a flaky read the
    legacy account-creation-with-country setup avoided by setting it up front).
    """
    deadline = time.monotonic() + timeout_s
    actual = ""
    while time.monotonic() < deadline:
        details = get_business(context).get("business") or {}
        actual = details.get("country_name") or details.get("country") or ""
        if actual == expected_country:
            return actual
        time.sleep(0.5)
    raise AssertionError(
        f"business country expected {expected_country!r}, got {actual!r} after read-back"
    )


def get_business_admin(context: dict) -> dict:
    """Read the business object via the admin API (mirrors legacy get_business_data,
    which reads plan/package metadata with admin auth)."""
    response = requests.get(
        f"{resolve_api_base_url(context)}/platform/v1/businesses/{pivot_uid(context)}",
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json().get("data") or {}
    return data.get("business") or data


def wait_for_business_plan(context: dict, expected_plan: str, timeout_s: int = 15) -> str:
    """Poll the admin business API until meta.plan.plan_name == expected_plan.

    The plan change after an upgrade is eventually consistent: billing writes the
    new subscription asynchronously, so a read immediately after the success page
    can still echo the previous (Trial) plan. Bounded poll mirrors the legacy
    `business ... has plan` assertion (admin read of meta.plan.plan_name).
    """
    deadline = time.monotonic() + timeout_s
    actual = ""
    while time.monotonic() < deadline:
        plan = (get_business_admin(context).get("meta") or {}).get("plan") or {}
        actual = plan.get("plan_name") or ""
        if actual == expected_plan:
            return actual
        time.sleep(0.5)
    raise AssertionError(
        f"business plan expected {expected_plan!r}, got {actual!r} after read-back"
    )


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
    account_uid = pivot_uid(context)
    cached = context.get("account_first_staff_uid")
    if cached and context.get("account_first_staff_uid_pivot") == account_uid:
        return cached
    response = account_request(
        context, "GET", f"/platform/v1/businesses/{account_uid}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", [])
    if not staffs:
        raise ValueError("No staff returned for auto account")
    context["account_first_staff_uid"] = staffs[0].get("id") or staffs[0].get("uid")
    context["account_first_staff_uid_pivot"] = account_uid
    return context["account_first_staff_uid"]


def create_service_via_api(
    context: dict,
    service_name: str,
    staff_uids: list[str] | None = None,
    *,
    charge_type: str = "free",
    price: str | None = None,
    tax_uids: list[str] | None = None,
) -> dict:
    """Create an appointment service via API.

    `charge_type`/`price` default to the original free-service behavior so existing
    callers are unchanged. Pass `charge_type="paid_force"` + `price` to mirror the
    legacy "require to pay" service, or `charge_type="paid_non_secured"` for the
    legacy "display a fee" service (see automation-js api/service.js). `tax_uids` attaches
    business taxes to the service (legacy `tax_uids`), e.g. a default-for-services tax.
    """
    uids = staff_uids or [first_staff_uid(context)]
    payload = {
        "category": {"uid": last_category_uid(context)},
        "staff_data": [{"uid": uid, "enabled": True} for uid in uids],
        "name": service_name,
        "service_type": "appointment",
        "currency": "USD",
        "duration": 60,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": charge_type,
        "display": "true",
        "max_attendance": 2,
    }
    if price is not None:
        payload["price"] = price
    if tax_uids:
        payload["tax_uids"] = tax_uids
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
    context: dict, service: dict, client: dict, staff_uid: str | None = None,
    start_time: str | None = None,
) -> dict:
    payload = {
        "business_id": pivot_uid(context),
        "staff_id": staff_uid or first_staff_uid(context),
        "start_time": start_time or future_appointment_start_time(),
        "service_id": service["id"],
        "client_id": client["id"],
    }
    response = account_request(context, "POST", "/business/scheduling/v1/bookings", json=payload)
    data = response.get("data") or response
    return data.get("booking") or data


def create_package_via_api(
    context: dict,
    name: str,
    services: list[dict],
    total_bookings: int,
    price: str | int,
    *,
    description: str = "",
    expiration: str = "3",
    expiration_unit: str = "m",
    products: list[dict] | None = None,
) -> dict:
    """Create a payment package via API (mirrors automation-js api/packages.create_package).

    `services` is a list of service dicts (each needs id/name/price/currency); they are
    bundled into a single package item with `total_bookings` credits, matching the legacy
    "specific"/"any" package types. POST /platform/v1/payment/packages.
    """
    items = [
        {
            "services": [
                {
                    "name": svc["name"],
                    "price": svc["price"],
                    "currency": svc.get("currency", "USD"),
                    "id": svc["id"],
                }
                for svc in services
            ],
            "total_bookings": total_bookings,
        }
    ]
    payload = {
        "items": items,
        "products": products or [],
        "discount_unit": "p",
        "online_payment_enabled": True,
        "expiration": expiration,
        "expiration_unit": expiration_unit,
        "name": name,
        "description": description,
        "price": price,
        "id": None,
        "currency": "USD",
        "use_platform_api": True,
    }
    response = account_request(context, "POST", "/platform/v1/payment/packages", json=payload)
    data = response.get("data") or response
    package = data.get("package") or data
    package_id = package.get("id") or package.get("uid")
    if not package_id:
        raise ValueError(f"Package API response did not include an id: {response}")
    return {
        "id": package_id,
        "name": package.get("name") or name,
        "price": package.get("price", price),
    }


def _package_validity_window() -> tuple[str, str]:
    """Return (valid_from, valid_until) as YYYY-MM-DD, mirroring legacy api/packages.

    valid_from = yesterday; valid_until = +3 months then -1 day (legacy JS date math)."""
    today = datetime.now(timezone.utc).date()
    valid_from = (today - timedelta(days=1)).isoformat()
    month_index = today.month - 1 + 3
    year = today.year + month_index // 12
    month = month_index % 12 + 1
    day = min(today.day, calendar.monthrange(year, month)[1])
    valid_until = (date(year, month, day) - timedelta(days=1)).isoformat()
    return valid_from, valid_until


def assign_package_to_client(
    context: dict,
    client_id: str,
    package_id: str,
    price: str | int,
    *,
    tax_uids: list[str] | None = None,
) -> dict:
    """Assign a package to a client via API (mirrors automation-js api/packages.assign_package).

    POST /platform/v1/payment/client_packages with the legacy validity window."""
    valid_from, valid_until = _package_validity_window()
    payload = {
        "client_id": client_id,
        "package_id": package_id,
        "price": price,
        "valid_from": valid_from,
        "valid_until": valid_until,
        "tax_uids": tax_uids,
        "use_platform_api": True,
    }
    response = account_request(
        context, "POST", "/platform/v1/payment/client_packages", json=payload
    )
    data = response.get("data") or response
    return data.get("client_package") or data


def create_platform_staff_via_api(context: dict, name: str, email: str, role: str = "user") -> dict:
    """Create a Platform staff member and resolve its uid via the staff list.

    POST /platform/v1/businesses/{pivot}/staffs {staff:{display_name,email,role}}, then
    GET the staff list (shape ``data.staff``, same as ``first_staff_uid``) and match by
    display_name/email. Resolving via the list avoids depending on the create response
    body shape and mirrors the legacy ``get_staff`` lookup.
    """
    account_request(
        context,
        "POST",
        f"/platform/v1/businesses/{pivot_uid(context)}/staffs",
        json={"staff": {"display_name": name, "email": email, "role": role.lower()}},
    )
    response = account_request(
        context, "GET", f"/platform/v1/businesses/{pivot_uid(context)}/staffs?status=all"
    )
    staffs = response.get("data", {}).get("staff", []) if isinstance(response, dict) else []
    for staff in staffs:
        if staff.get("display_name") == name or staff.get("email") == email:
            return {
                "uid": staff.get("id") or staff.get("uid"),
                "name": staff.get("display_name") or name,
                "email": staff.get("email") or email,
            }
    raise ValueError(f"Created staff {name!r} ({email}) not found in staff list: {response}")
