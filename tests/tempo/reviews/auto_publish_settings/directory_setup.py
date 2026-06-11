"""Directory + business-in-directory + client provisioning for the auto_publish_settings tests.

Scenarios 2 & 3 of the legacy `reviews.feature` require a DIRECTORY and a business
created INSIDE that directory (unlike the plain isolated auto account used by
scenario 1). The directory's `external_review_site` config is what drives the
auto-publish UI in both the back-office settings page and the client portal.

Kept local to this subcategory (instead of `tests/account_api.py`) to avoid
touching that shared module while it has open migration PRs. Endpoints mirror the
legacy automation-js `api/directories.js` + `api/accounts.js` + `api/clients.js`
chain and were verified on integration with an independent read-back (GET business
by email) before use.
"""

from __future__ import annotations

import time

import requests
from playwright.sync_api import Page

from tests._functions.login.test import fn_login
from tests.account_api import admin_headers, api_base, resolve_api_base_url

REQUEST_TIMEOUT = 30
TOO_MANY_REQUESTS = 429
RATE_LIMIT_WAIT = 60
MAX_RATE_LIMIT_RETRIES = 2

# Match the runner's automation flags so the in-directory business behaves like a
# normal auto account (no onboarding wizard, no first-run success toasts).
AUTOMATION_FEATURES = [
    "hide_register_wizard",
    "hide_payment_success_message",
    "hide_first_event_success_message",
    "hide_empty_state",
]
# The reviews page redirects to the dashboard without reviews_rollout + collect_reviews,
# and its fields stay disabled / save off without enable_reviews_auto_publishing. The CP
# review-settings-loaded marker also needs collect_reviews. Enable all three so the only
# thing that differs between the two scenarios is the directory's external review site.
REVIEW_FEATURES = [
    "reviews_rollout",
    "collect_reviews",
    "enable_reviews_auto_publishing",
]


def _api(context: dict) -> str:
    try:
        return api_base(context)
    except ValueError:
        return resolve_api_base_url(context)


def _post(url: str, headers: dict, json_body: dict) -> dict:
    last = None
    for attempt in range(MAX_RATE_LIMIT_RETRIES + 1):
        response = requests.post(url, json=json_body, headers=headers, timeout=REQUEST_TIMEOUT)
        last = response
        if response.status_code == TOO_MANY_REQUESTS and attempt < MAX_RATE_LIMIT_RETRIES:
            time.sleep(RATE_LIMIT_WAIT)
            continue
        if not response.ok:
            raise AssertionError(
                f"POST {url} failed: HTTP {response.status_code} {response.text[:400]}"
            )
        return response.json() if response.text else {}
    raise AssertionError(f"POST {url} rate-limited after retries: {last.text[:200] if last else ''}")


def create_directory(
    context: dict,
    *,
    name: str,
    business_name: str,
    email: str,
    password: str,
    review_site_url: str | None = None,
    review_site_display_name: str | None = None,
) -> dict:
    """Create a directory (Admin) and generate its directory token."""
    body = {
        "name": name,
        "business_name": business_name,
        "email": email,
        "password": password,
        "features": [],
        "branding": {"colors": {}},
        "settings": {
            "external_review_site": {
                "url": review_site_url,
                "label": review_site_display_name,
            }
        },
    }
    data = (_post(f"{_api(context)}/admin/directories/create", admin_headers(), body) or {}).get("data") or {}
    directory_id = data.get("directory_id")
    if not directory_id:
        raise AssertionError(f"Directory create returned no directory_id: {data}")

    token_data = (
        _post(f"{_api(context)}/platform/v1/tokens", admin_headers(), {"directory_id": directory_id}) or {}
    ).get("data") or {}
    directory_token = token_data.get("token")
    if not directory_token:
        raise AssertionError("Directory token generation returned no token")

    return {
        "directory_id": directory_id,
        "directory_uid": data.get("directory_uid"),
        "directory_token": directory_token,
    }


def create_business_in_directory(
    context: dict, directory_token: str, *, name: str, email: str, password: str
) -> dict:
    """Create a business inside the directory via the Platform API + confirm with a read-back."""
    headers = {"Authorization": f"Token {directory_token}"}
    body = {"admin_account": {"email": email, "password": password}, "business": {"name": name}, "meta": {}}
    data = (_post(f"{_api(context)}/platform/v1/businesses", headers, body) or {}).get("data") or {}
    outer = data.get("business") or {}
    business_uid = (outer.get("business") or {}).get("id")
    user_id = (outer.get("admin_account") or {}).get("user_id")
    if not (business_uid and user_id):
        raise AssertionError(f"Business create returned no uid/user_id: {data}")

    _assert_business_exists(context, email, business_uid)
    return {
        "business_uid": business_uid,
        "user_id": user_id,
        "email": email,
        "password": password,
        "name": name,
    }


def _assert_business_exists(context: dict, email: str, expected_uid: str) -> None:
    encoded = email.replace("+", "%2B")
    response = requests.get(
        f"{_api(context)}/platform/v1/businesses?email={encoded}",
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    uids = (response.json() or {}).get("data", {}).get("businesses", [])
    if expected_uid not in uids:
        raise AssertionError(f"Read-back did not find business {expected_uid} for {email}: {uids}")


def enable_business_features(context: dict, user_id, features: list[str]) -> None:
    feats = ",".join(features)
    _post(
        f"{_api(context)}/admin/feature_flags/{user_id}/add_user_features",
        admin_headers(),
        {"features": feats},
    )
    requests.get(
        f"{_api(context)}/infra/automation/reset_features_table_cache",
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )


def create_client_in_directory(
    context: dict, directory_token: str, business_uid: str, *, first_name: str, last_name: str, email: str
) -> dict:
    """Create a client for the in-directory business and capture its client-portal JWT token."""
    headers = {"Authorization": f"Token {directory_token}", "X-On-Behalf-Of": business_uid}
    body = {"first_name": first_name, "last_name": last_name, "email": email, "source_name": "automation"}
    data = _post(f"{_api(context)}/platform/v1/clients", headers, body)
    payload = data.get("data") or data
    client = payload.get("client") or {}
    token = payload.get("token")
    if not token:
        raise AssertionError(f"Client create returned no portal token: {data}")
    client["token"] = token
    client["id"] = client.get("id") or client.get("uid")
    client["full_name"] = f"{first_name} {last_name}"
    return client


def delete_business(context: dict, business_uid: str) -> None:
    """Best-effort admin delete of an in-directory business (teardown only)."""
    try:
        requests.get(
            f"{_api(context)}/admin/users/{business_uid}/delete_business",
            headers=admin_headers(),
            timeout=REQUEST_TIMEOUT,
        )
    except Exception as exc:  # noqa: BLE001 - teardown best-effort
        print(f"  [teardown] Failed to delete business {business_uid}: {exc}")


def fresh_login(page: Page, context: dict, *, username: str, password: str) -> None:
    """Log in as `username` after clearing any prior session.

    The runner reuses one browser context across the tests in a category, so a prior
    test's POV session (cookies + localStorage staff JWT) leaks into the next. Without a
    clean slate, fn_login sees an existing session and POV keeps using the previous
    business' staff token — landing the second test on the wrong (no-review-site)
    business. Logging out and clearing storage forces a real re-login as `username`.
    """
    base = (context.get("base_url") or "").rstrip("/")
    try:
        page.context.clear_cookies()
        # Land on the app domain (cookies already cleared, so this shows the login page,
        # not the dashboard) to clear the persisted staff JWT, then drop cookies again.
        page.goto(f"{base}/app/login", wait_until="domcontentloaded")
        page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} }")
        page.context.clear_cookies()
    except Exception:
        pass
    fn_login(page, context, username=username, password=password)


def activate_business(context: dict, triple_key: str) -> dict:
    """Point the shared review helpers at one provisioned in-directory business.

    The reviews CP/settings helpers read `context["auto_account"]["pivot_uid"]` and
    `context["review_client"]`, so each test selects its own business before running.
    """
    triple = context[triple_key]
    context["auto_account"] = {
        "pivot_uid": triple["business_uid"],
        "business_id": triple["business_uid"],
        "user_id": triple["user_id"],
        "email": triple["email"],
        "password": triple["password"],
        "name": triple["name"],
    }
    context["review_client"] = triple["client"]
    return triple


def provision_directory_business(context: dict, *, with_review_site: bool, slug: str) -> dict:
    """Provision a directory + in-directory business + client; enable reviews flags.

    Returns: {directory, business_uid, user_id, email, password, name, client}.
    """
    timestamp = int(time.time() * 1000)
    review_site = (
        {"review_site_url": "https://www.vcita.com", "review_site_display_name": "vcita"}
        if with_review_site
        else {}
    )

    directory = create_directory(
        context,
        name="review dir",
        business_name="Review dir",
        email=f"review+dir-{slug}-{timestamp}@vmeetme.com",
        password="123456",
        **review_site,
    )
    business = create_business_in_directory(
        context,
        directory["directory_token"],
        name="Automation review",
        email=f"auto-review-{slug}-{timestamp}@vmeetme.com",
        password="123456",
    )
    enable_business_features(context, business["user_id"], AUTOMATION_FEATURES + REVIEW_FEATURES)
    client = create_client_in_directory(
        context,
        directory["directory_token"],
        business["business_uid"],
        first_name="first",
        last_name="last",
        email=f"reviewer+{slug}-{timestamp}@vmeetme.com",
    )

    return {"directory": directory, "client": client, **business}
