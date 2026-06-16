from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import os
import time

import requests

from tests.account_api import admin_headers

REQUEST_TIMEOUT = 5
# The runner pins the browser context and the auto-account business timezone to
# US Eastern. Appointment start times are interpreted as UTC by the bookings API,
# so wall-clock times are localized to this zone before conversion.
BUSINESS_TZ = ZoneInfo("America/New_York")
WEEKDAY_INDEX = {
    "sunday": 0,
    "monday": 1,
    "tuesday": 2,
    "wednesday": 3,
    "thursday": 4,
    "friday": 5,
    "saturday": 6,
}


def create_client(context: dict, first_name: str, last_name: str, email: str) -> dict:
    response = account_request(
        context,
        "POST",
        "/platform/v1/clients",
        json={"first_name": first_name, "last_name": last_name, "email": email, "source_name": "automation"},
    )
    client = (response.get("data") or {}).get("client") or response.get("client") or response
    client["full_name"] = f"{client.get('first_name') or first_name} {client.get('last_name') or last_name}"
    return client


def create_platform_staff(context: dict, name: str, email: str, role: str = "user") -> dict:
    pivot_uid = get_pivot_uid(context)
    response = account_request(
        context,
        "POST",
        f"/platform/v1/businesses/{pivot_uid}/staffs",
        json={"staff": {"display_name": name, "email": email, "role": role.lower()}},
    )
    return ((response.get("data") or {}).get("staff") or [response])[0]


def create_v2_staff(context: dict, name: str, email: str, role: str, services: list[dict]) -> dict:
    response = account_request(
        context,
        "POST",
        "/v2/staffs_frontage",
        json={"display_name": name, "email": email, "role": role.lower(), "services": services},
    )
    staff = response.get("data") or response
    staff.setdefault("display_name", name)
    staff.setdefault("email", email)
    return staff


def get_sso_token(context: dict, staff: dict) -> str:
    staff_uid = staff.get("id") or staff.get("uid")
    if not staff_uid:
        raise ValueError(f"Staff UID is missing for {staff}")
    response = account_request(
        context,
        "GET",
        f"/v1/partners/sso/token?staff_uid={staff_uid}",
        base_url=resolve_partner_base_url(context),
        headers=partner_headers(context),
    )
    return response.get("sso_token") or response.get("token") or response.get("data", {}).get("sso_token")


def create_service(
    context: dict,
    name: str,
    duration: int = 60,
    service_type: str = "appointment",
    staff_uid: str | None = None,
) -> dict:
    payload = {
        "category": {"uid": get_last_category_uid(context)},
        "staff_data": [{"uid": staff_uid or get_first_staff_uid(context), "enabled": True}],
        "name": name,
        "service_type": service_type,
        "currency": "USD",
        "duration": duration,
        "interaction_type": "business_location",
        "meeting_interaction_details": "TLV",
        "charge_type": "free",
        "price": None,
        "display": "true",
        "max_attendance": 2,
    }
    response = account_request(context, "POST", "/v2/settings/services", json=payload)
    service = response.get("data") or response
    if service.get("id") and not service.get("uid"):
        service["uid"] = service["id"]
    return service


def get_service_color_id(service: dict) -> str | None:
    """Return the scheduler color id for a service, matching the rendered color-<id> class."""
    color_id = service.get("color_id")
    if color_id is None:
        color = service.get("color")
        color_id = color.get("id") if isinstance(color, dict) else color
    return str(color_id) if color_id is not None else None


def create_appointment_via_api(
    context: dict,
    service_name: str,
    client: dict,
    meeting_date: str,
    meeting_time: str,
    assigned_staff: str | None = None,
) -> dict:
    service = context["calendar_services"][service_name]
    response = account_request(
        context,
        "POST",
        "/business/scheduling/v1/bookings",
        json={
            "business_id": get_pivot_uid(context),
            "staff_id": get_staff_uid(context, assigned_staff),
            "start_time": resolve_api_datetime(context, meeting_date, meeting_time).isoformat(),
            "service_id": service.get("id") or service.get("uid"),
            "client_id": client.get("id") or client.get("uid"),
        },
    )
    return (response.get("data") or {}).get("booking") or response


def create_event_via_api(
    context: dict,
    service_name: str,
    meeting_date: str,
    meeting_time: str,
    assigned_staff: str | None = None,
) -> dict:
    service = context["calendar_services"][service_name]
    start_time = resolve_api_datetime(context, meeting_date, meeting_time, is_event=True)
    end_time = start_time + timedelta(minutes=int(service.get("duration") or 60))
    return account_request(
        context,
        "POST",
        "/v2/event_instances",
        json={
            "title": service.get("name") or service_name,
            "event_service_id": service.get("id") or service.get("uid"),
            "interaction_type": service.get("interaction_type") or "business_location",
            "interaction_details": service.get("meeting_interaction_details") or "TLV",
            "max_attendance": service.get("max_attendance") or 2,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "charge_type": service.get("charge_type") or "free",
            "price": service.get("price"),
            "currency": service.get("currency") or "USD",
            "staff_id": get_staff_uid(context, assigned_staff),
            "duration": service.get("duration") or 60,
            "padding": service.get("padding"),
            "display": True,
        },
    )


def end_primary_staff_sessions(context: dict) -> None:
    primary_staff_uid = context["calendar_primary_staff_uid"]
    account_request(
        context,
        "DELETE",
        f"/platform/v1/businesses/{get_pivot_uid(context)}/staffs/{primary_staff_uid}/sessions",
    )


def staff_uid(staff: dict) -> str:
    uid = staff.get("id") or staff.get("uid")
    if not uid:
        raise ValueError(f"Staff UID is missing for {staff}")
    return uid


def get_staff_uid(context: dict, staff_name: str | None = None) -> str:
    if not staff_name:
        return get_first_staff_uid(context)
    for staff in context.get("calendar_staff", []):
        if staff.get("display_name") == staff_name or staff.get("name") == staff_name:
            return staff.get("id") or staff.get("uid")
    raise ValueError(f"Staff '{staff_name}' was not created in calendar context")


def service_refs(context: dict, names: list[str]) -> list[dict]:
    return [{"uid": context["calendar_services"][name].get("uid") or context["calendar_services"][name]["id"], "available": True} for name in names]


def resolve_api_datetime(context: dict, date_key: str, time_key: str, is_event: bool = False) -> datetime:
    """Resolve the datetime to send to the scheduling APIs for a desired wall-clock.

    The two endpoints interpret the value differently (verified empirically):
    - ``event_instances`` treats a timezone-less value as the business-local time to
      display, so the wall-clock is sent as-is.
    - ``bookings`` treats ``start_time`` as UTC, so the wall-clock is localized to the
      pinned business timezone (US Eastern) and converted to UTC.

    The previous implementation subtracted the test machine's local offset, which skewed
    every API-created item by the machine-vs-browser timezone gap.
    """
    target = _resolve_relative_date(date_key)
    hour, minute = [int(part) for part in time_key.split(":")]
    target = target.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if is_event:
        return target
    return target.replace(tzinfo=BUSINESS_TZ).astimezone(timezone.utc)


def account_request(context: dict, method: str, path: str, **kwargs) -> dict:
    base_url = kwargs.pop("base_url", resolve_api_base_url(context))
    headers = kwargs.pop("headers", account_headers(context))
    retry_allowed = method.upper() in {"GET", "HEAD", "OPTIONS"}
    for attempt in range(2):
        try:
            response = requests.request(
                method,
                f"{base_url}{path}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
                **kwargs,
            )
            break
        except (requests.ReadTimeout, requests.ConnectionError):
            if attempt == 1 or not retry_allowed:
                raise
            time.sleep(0.2)
    if not response.ok:
        raise requests.HTTPError(f"{response.status_code} {response.reason}: {response.text[:500]}", response=response)
    return response.json() if response.text else {}


def resolve_partner_base_url(context: dict) -> str:
    base_url = (context.get("base_url") or "").rstrip("/")
    if "app.meet2know.com" in base_url:
        return "https://api.meet2know.com"
    if "app.vcita.com" in base_url:
        return "https://api.vcita.com"
    if "app-" in base_url and ".external.int-eks.vchost.co" in base_url:
        return base_url.replace("https://app-", "https://vcita-", 1)
    if base_url:
        return base_url
    raise ValueError("base_url is missing from context and partner base URL could not be inferred")


def resolve_api_base_url(context: dict) -> str:
    if context.get("api_base_url"):
        return context["api_base_url"].rstrip("/")
    base_url = (context.get("base_url") or "").rstrip("/")
    if "meet2know.com" in base_url:
        return "https://api2.meet2know.com"
    if "vcita.com" in base_url:
        return "https://api.vcita.biz"
    if "app-" in base_url and ".external.int-eks.vchost.co" in base_url:
        return base_url.replace("https://app-", "https://core-", 1)
    raise ValueError("api_base_url is missing from context and could not be inferred")


def account_headers(context: dict) -> dict:
    token = (context.get("auto_account") or {}).get("api_token") or (context.get("auto_account") or {}).get("auth_token")
    if not token:
        raise ValueError("auto_account api_token is missing from context")
    return {"Authorization": f"Bearer {token}"}


def partner_headers(context: dict) -> dict:
    return {"Authorization": f'Token token="{resolve_directory_token(context)}"'}


def resolve_directory_token(context: dict) -> str:
    """Resolve the directory token used for partner SSO calls.

    Prefer an explicit ``VCITA_DIRECTORY_TOKEN`` override; otherwise generate (or
    reuse) one at runtime from the admin token + directory id, mirroring the
    legacy automation-js flow (``POST/GET /platform/v1/tokens``). This avoids
    requiring a separately provisioned secret in every run environment.
    """
    env_token = os.environ.get("VCITA_DIRECTORY_TOKEN")
    if env_token:
        return env_token

    directory_id = context.get("directory_id") or os.environ.get("VCITA_DIRECTORY_ID")
    if not directory_id:
        raise ValueError(
            "Cannot resolve a directory token for partner SSO: set VCITA_DIRECTORY_TOKEN, "
            "or provide a directory_id (context/VCITA_DIRECTORY_ID) plus VCITA_ADMIN_TOKEN."
        )

    headers = admin_headers()
    existing = account_request(
        context, "GET", "/platform/v1/tokens", params={"directory_id": directory_id}, headers=headers
    )
    tokens = (existing.get("data") or {}).get("tokens") or []
    if tokens and tokens[0].get("token"):
        return tokens[0]["token"]

    created = account_request(
        context, "POST", "/platform/v1/tokens", json={"directory_id": directory_id}, headers=headers
    )
    token = (created.get("data") or {}).get("token") or created.get("token")
    if not token:
        raise ValueError(f"Directory token generation returned no token: {created}")
    return token


def get_pivot_uid(context: dict) -> str:
    pivot_uid = (context.get("auto_account") or {}).get("pivot_uid") or (context.get("auto_account") or {}).get("business_id")
    if not pivot_uid:
        raise ValueError("auto_account pivot_uid is missing from context")
    return pivot_uid


def get_last_category_uid(context: dict) -> str:
    response = account_request(context, "GET", f"/platform/v1/categories?business_id={get_pivot_uid(context)}")
    categories = response.get("data", {}).get("categories", [])
    if not categories:
        raise ValueError("No service categories returned for auto account")
    return categories[-1]["id"]


def get_first_staff_uid(context: dict) -> str:
    if context.get("calendar_primary_staff_uid"):
        return context["calendar_primary_staff_uid"]
    response = account_request(context, "GET", f"/platform/v1/businesses/{get_pivot_uid(context)}/staffs?status=all")
    staff = response.get("data", {}).get("staff", [])
    if not staff:
        raise ValueError("No staff returned for auto account")
    context["calendar_primary_staff_uid"] = staff[0].get("id") or staff[0].get("uid")
    return context["calendar_primary_staff_uid"]


def _resolve_relative_date(date_key: str) -> datetime:
    today = datetime.now()
    parts = date_key.split("_")
    if parts[0] == "next" and parts[1] == "day":
        return today + timedelta(days=int(parts[2]))
    if parts[0] == "previous" and parts[1] == "day":
        return today - timedelta(days=int(parts[2]))
    raise ValueError(f"Unsupported API date key: {date_key}")


def unique_email(prefix: str) -> str:
    return f"{prefix}+{int(time.time() * 1000)}@vmeetme.com"
