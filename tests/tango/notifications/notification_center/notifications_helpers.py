"""API + UI helpers for the notification_center subcategory (VCITA2-14247).

Migrated from automation-js:
  api/notificationCenter.js  (notification metadata + send notification, on apigw)
  api/apps.js                (create app, /oauth/service/token app token, assign to business)
  api/api.js                 (apigw_api / admin_api / generate_app_token; token plumbing)
  helpers/NotificationsHelper.js (get_authorization_token: directory vs app token)
  pages/desktop/Frontage/toolbar.js          (notification badge + counter)
  pages/desktop/Frontage/notification_pane.js (pane rows / empty states / toggles)
  pages/desktop/Frontage/notification_settings.js (settings page checkboxes)
  pages/desktop/Frontage/staffs.js           (impersonate "Log in as")

Token landscape (verified live on integration 2026-06-19):
  - App token:   admin POST /platform/v1/apps -> client_id/client_secret ->
                 admin POST /oauth/service/token -> token (Bearer on apigw).
  - Directory:   the integration directory 970 (kmy47p5x88kqlv6f) token; used as Bearer
                 on apigw. Default below matches the directory autotester provisions on.
  - core_internal_app: integration service creds -> admin POST /oauth/service/token.
Notification metadata + send run on the apigw (apigw-integration...), NOT core_url.

Frame topology: the Notification Center *settings* page renders inside iframe
`#vue_iframe_layout` (legacy `vue_iframe_layout`). The notification *pane* and the toolbar
badge are top-level POV (no iframe).

All UI/element waits are capped at 5s (UI_TIMEOUT) per project policy. The badge counter
and pane-count reads use a bounded re-check (<=2 retries) because counter propagation lags
the send API (legacy retried this read up to 10x; 2 retries is enough on integration).
"""

from __future__ import annotations

import os
import time

import requests
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page, expect

from tests._functions.login.test import fn_login
from tests.account_api import pivot_uid, resolve_api_base_url

UI_TIMEOUT = 5000
REQUEST_TIMEOUT = 30
# Bounded read re-check for async pane propagation (legacy retried 10x).
READ_RECHECK_RETRIES = 2
RECHECK_INTERVAL_S = 1.0
# The toolbar badge counter is updated by an asynchronous push that lags the send API,
# especially when several notifications are sent back to back (the count climbs as each
# arrives). This is eventual consistency, not a flaky selector: the legacy step retried this
# exact read up to 10x. We poll the counter as a single bounded read wait, capped at 5s
# (re-reading every 0.5s) — no action is retried, only the value is re-read.
BADGE_POLL_TIMEOUT_S = 5.0
BADGE_POLL_INTERVAL_S = 0.5

# --- Integration directory + core_internal_app credential fallbacks ---
# FLAG (documented in changelog.md): these are static integration-only credentials (the
# directory 970 token + the core_internal service creds) that scenarios 2 and 3 use as the
# Bearer on the apigw. Unlike the admin token (`VCITA_ADMIN_TOKEN`, env-only) and the account
# owner credentials, there is NO context- or account-derived source for them: the directory
# token is a long-lived directory secret, and the core_internal creds are a fixed platform
# service identity — neither is provisioned per-run, so they cannot be read from `context`,
# `account_api`, or the account factory. They are therefore env-first with an integration
# fallback (same env-or-default shape account_factory uses for its operator credentials).
# Set VCITA_DIRECTORY_TOKEN / VCITA_DIRECTORY_UID / VCITA_CORE_INTERNAL_SERVICE_ID /
# VCITA_CORE_INTERNAL_SERVICE_SECRET to override (required on any non-integration env). The
# fallbacks below are integration-only and grant no production access; they match the legacy
# `directory 970` ("recurly") the runner provisions on.
DEFAULT_DIRECTORY_TOKEN = "ff333ad7960d32e873d48d5de772f826"
DEFAULT_DIRECTORY_UID = "kmy47p5x88kqlv6f"
DEFAULT_CORE_INTERNAL_SERVICE_ID = (
    "211b207b230f77065a8e42d422270535cf3310368c0e39e11b88ad2f3bb1d56c"
)
DEFAULT_CORE_INTERNAL_SERVICE_SECRET = (
    "bcba9f904cbee07e8cf40da619977cc9cffb3fd520ee2cf6e77e575c86e8ab11"
)

# ---------------- Toolbar badge (top-level POV) ----------------
# The badge wrapper is `[data-qa='VcWideTopMenuBar-notificationsBadge']` (a div.VcBadge);
# inside it the clickable button is `[data-qa='VcWideTopMenuBar-notifications']` and the
# numeric counter is the Vuetify `.v-badge__badge` span (hidden via display:none at 0).
# Verified live on integration 2026-06-19.
BADGE_BUTTON = "[data-qa='VcWideTopMenuBar-notifications']"
BADGE_WRAPPER = "[data-qa='VcWideTopMenuBar-notificationsBadge']"
BADGE_COUNTER = "[data-qa='VcWideTopMenuBar-notificationsBadge'] .v-badge__badge"

# ---------------- New-account onboarding wizard (the real flakiness source) ----------------
# Freshly-created accounts can pop a business-setup wizard (an Angular md-dialog) that puts
# the POV `.angular-iframe` wrapper into `isModalMode`/`isFullscreen`, which renders a
# full-viewport iframe overlay ON TOP of the whole toolbar — including the notification
# badge — so a badge click is intercepted by the iframe and times out (the classic
# "TimeoutError: Timeout 5000ms exceeded" with a blank loading-spinner screenshot).
#
# The runner suppresses this wizard with the `hide_register_wizard` feature flag (set at
# account creation), but that flag propagates asynchronously, so on a cold first POV load the
# wizard can still win the race (~30% of runs) before the flag takes effect. Verified live on
# integration 2026-06-19: a flagged account never shows the wizard, while the overlay class is
# `.angular-iframe.isModalMode` whenever it does. The toolbar is only interactable once that
# modal overlay is gone, so it is the deterministic readiness signal before any badge click.
MODAL_OVERLAY = ".angular-iframe.isModalMode"

# ---------------- POV toolbar skeleton placeholders (the dominant late-flow flake) ----------------
# On a cold POV bootstrap (initial dashboard load, every `goto_dashboard` badge refresh, and
# especially the impersonation SSO re-login) the whole top menu bar `[data-qa='VcWideTopMenuBar']`
# first renders as Vuetify SKELETON placeholders — a row of `.v-skeleton-loader` bones
# (`data-qa='VcSkeleton'`) where the search box, AI button, notification badge, help and account
# icons go — while a centered content spinner shows below. This is exactly the failure screenshot:
# the owner dashboard with grey skeleton dots top-right and no real toolbar.
#
# Verified live on integration 2026-06-19 (chrome channel, 1440x900 — the runner's size), the
# cold mount sequence is deterministic:
#   t+0.0  : no VcWideTopMenuBar host yet; ~21 page skeletons.
#   t+0.5  : VcWideTopMenuBar host present but its icons are 8 visible `.v-skeleton-loader`s;
#            the real badge button `data-qa='VcWideTopMenuBar-notifications'` does NOT exist yet.
#   t+1.2  : the skeletons are swapped for the REAL badge button — at the SAME tick the toolbar's
#            own skeletons drop to 0 (badge-present and toolbar-skeleton-gone are coincident).
#   t+2.25 : the last sidebar/content skeletons clear (0 visible page skeletons); badge clicks open
#            the pane cleanly.
# So `badge visible` alone is insufficient as a readiness gate: the prior wait could resolve on a
# briefly-mounted badge while the page was still settling its cold bootstrap, and the immediately
# following `.click()`/counter read then raced a re-render and timed out at 5s. The deterministic
# "toolbar fully mounted" signal is: the real badge button is visible AND there is NO visible
# `.v-skeleton-loader` left on the page (the whole cold bootstrap has finished). That is strictly
# stronger than badge-visible and is reached well inside one 5s wait (~2.3s cold).
SKELETON_LOADER = ".v-skeleton-loader"

# ---------------- Notification pane ----------------
# The badge opens the pane as a Vuetify `.v-menu__content` dropdown anchored to the toolbar,
# with `.notification-pane` as its content container and a transparent overlay scrim
# (`.v-overlay__scrim.transparent`) behind it. Verified live on integration 2026-06-19 at the
# runner's window width (1440, `no_viewport` + `--window-size=1440,900`): the dropdown is the
# variant that renders. `.notification-pane` is the stable content marker (it is also present
# in the narrow bottom-sheet variant, so it stays correct if the breakpoint ever shifts).
# Close is a single deterministic action: click the transparent scrim (Escape does NOT
# dismiss the dropdown variant — verified live — so it is not used).
PANE_OVERLAY = ".notification-pane"
PANE_SCRIM = ".v-overlay__scrim.transparent"
PANE_BODY = ".notification-pane__body"
PANE_ROW = ".pane-row"
PANE_TITLE = ".pane-row__body__title"
PANE_DESC = ".pane-row__body__description"
PANE_TIME = "[data-qa='vc-time-since']"
PANE_UNREAD = ".pane-row__body--active"
PANE_READ = ".pane-row__body--inactive"
PANE_DOT = "div.pane-row__body__dot"
PANE_EMPTY = "[data-qa='empty-state-no-notifications']"
PANE_EMPTY_READ_ALL = "[data-qa='empty-state-read-all']"
PANE_ONLY_UNREAD_TOGGLE = ".notification-pane .v-input--selection-controls__input"
PANE_MARK_ALL = ".notification-pane__header [data-qa='VcLink']"
PANE_SETTINGS_BUTTON = "[data-qa='notifications-settings']"

# ---------------- Settings page (doubly-nested iframe) ----------------
# /app/notification_settings renders inside iframe#angular-iframe, which itself nests
# iframe#vue_iframe_layout (the actual Vue settings app). Verified live 2026-06-19; the
# legacy single `vue_iframe_layout` switch is now reached only through the angular frame.
SETTINGS_PATH = "/app/notification_settings"
SETTINGS_OUTER_IFRAME = "#angular-iframe"
SETTINGS_IFRAME = "#vue_iframe_layout"
SETTINGS_CONTAINER = ".notification"
SETTINGS_NAME_TITLES = ".notification__description--name"
CLIENTS_PATH = "/app/clients"

# ---------------- Staff settings / impersonate (Angular iframe) ----------------
# /app/settings/staff renders the legacy Angular staff list inside iframe#angular-iframe.
# Each staff row is a `.list-item`; its actions menu opens via the per-row
# `button[aria-haspopup='true'][aria-expanded='false']`; the menu then exposes the
# "Log in as" item. Verified live 2026-06-19.
STAFF_PATH = "/app/settings/staff"
STAFF_IFRAME = "#angular-iframe"
STAFF_LIST_ITEM = ".list-item"
STAFF_ROW_MENU_BTN = "button[aria-haspopup='true'][aria-expanded='false']"
STAFF_LOGIN_AS_TEXT = "Log in as"
# Dashboard welcome subtitle (top-level POV) — shows "Welcome back, <staff>" after the
# impersonation reload. Used to confirm the logged-in staff (legacy getLoggedStaffsName)
# without opening the account menu (whose overlay would otherwise block the next pane open).
DASHBOARD_WELCOME = ".VcHeader--subtitle"


# ===================================================================== #
# Base URLs
# ===================================================================== #
def app_base(context: dict) -> str:
    base = (context.get("base_url") or "").rstrip("/")
    if not base:
        raise ValueError("base_url missing from context")
    return base


def _wait_toolbar_mounted(page: Page) -> None:
    """Wait until the POV toolbar is FULLY MOUNTED (not its skeleton placeholder) on the CURRENT
    page: the real badge button is visible, every `.v-skeleton-loader` cold-bootstrap placeholder
    is gone, AND the new-account onboarding wizard's modal iframe overlay is gone.

    `badge visible` alone is NOT sufficient (two distinct ways it loses the race):
      - Skeleton bootstrap: the whole top menu bar first renders as `.v-skeleton-loader` bones
        (search/AI/badge/help/account); while any page skeleton is still visible the cold mount
        is mid-flight and a badge click/counter read races a re-render and times out at 5s (the
        skeleton-toolbar failure screenshot). Waiting for zero visible skeletons gates on the
        whole bootstrap finishing — strictly stronger than badge-visible, ~2.3s cold (see
        SKELETON_LOADER). `wait_for(state="hidden")` on the `.first` skeleton resolves the
        instant the last one detaches; when none ever render it resolves immediately.
      - Onboarding wizard: the badge can render UNDER the wizard's full-viewport
        `.angular-iframe.isModalMode` overlay, so a click is intercepted (see MODAL_OVERLAY).
    This is a single readiness wait (no re-navigation): callers that own a page they can reload
    (goto_dashboard) recover the wizard/cold-boot race themselves; callers landing via in-app
    navigation rely on the flag already having propagated by then."""
    page.locator(BADGE_BUTTON).first.wait_for(state="visible", timeout=UI_TIMEOUT)
    # Gate on the WHOLE cold bootstrap finishing: zero visible skeleton placeholders left. A
    # `.first` hidden-wait is not safe here (skeletons detach in DOM order, so the first could
    # clear while later ones are still visible), so poll the visible skeleton count to 0. Single
    # bounded readiness wait capped at UI_TIMEOUT (5s); ~2.3s cold — no action is retried.
    deadline = time.monotonic() + (UI_TIMEOUT / 1000.0)
    while page.locator(f"{SKELETON_LOADER}:visible").count() > 0:
        if time.monotonic() >= deadline:
            raise PlaywrightError("toolbar still showing skeleton placeholders after 5s")
        page.wait_for_timeout(100)
    page.locator(MODAL_OVERLAY).first.wait_for(state="hidden", timeout=UI_TIMEOUT)


def goto_dashboard(page: Page, context: dict) -> None:
    """Navigate to the dashboard and wait for the toolbar to be interactable.

    The live badge-counter push is reliably connected on a normal POV page (dashboard); on
    the heavy notification_settings page (Angular -> Vue iframe) the toolbar's push
    subscription can be stale after repeated iframe navigations, so the badge does not update
    live there. Landing on the dashboard gives the next badge read a freshly-mounted toolbar
    that reflects the current server-side unread count. The toolbar is only interactable once the
    cold-bootstrap skeleton placeholders AND the new-account onboarding wizard's modal overlay (if
    any) have cleared, so wait on that fully-mounted signal before returning. Verified live
    2026-06-19."""
    dashboard_url = f"{app_base(context)}/app/dashboard"
    overlay = page.locator(MODAL_OVERLAY).first
    # Navigate ONCE, then bounded-re-check the FULLY-MOUNTED toolbar readiness on the SAME page.
    # Two distinct late-flow failure modes share the skeleton/blank-spinner symptom and must be
    # handled differently (verified live 2026-06-19 against the ~30-40% late-flow flake):
    #   (a) Cold POV bootstrap (initial load, every badge-refresh re-nav, and the "Log in as"
    #       impersonation SSO re-login). The toolbar first renders as `.v-skeleton-loader`
    #       placeholders, then mounts the real badge ~2.3s in. A fresh `page.goto` here RESTARTS
    #       the bootstrap and never catches up — so for this case we KEEP WAITING on the booting
    #       page, not re-navigate. Three bounded 5s waits (<=15s) cover the cold boot.
    #   (b) The new-account onboarding wizard won the `hide_register_wizard` flag-propagation
    #       race, so its modal overlay covers the toolbar. Here the flag has since propagated
    #       server-side, so re-navigating reloads the POV WITHOUT the wizard. We only re-navigate
    #       when the overlay is actually present.
    # `_wait_toolbar_mounted` is the shared fully-mounted signal (badge visible + zero visible
    # skeletons + overlay gone). Each individual wait stays <=5s; re-navigation (case b only) is
    # bounded to <=2.
    page.goto(dashboard_url, wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    for attempt in range(READ_RECHECK_RETRIES + 1):
        try:
            _wait_toolbar_mounted(page)
            return
        except PlaywrightError:
            if attempt >= READ_RECHECK_RETRIES:
                raise
            # Case (b): wizard overlay up -> re-navigate so the propagated flag takes effect.
            # Case (a): still booting (no overlay) -> do NOT re-navigate; loop to keep waiting
            # on the same in-progress bootstrap for the next bounded interval.
            if overlay.is_visible():
                page.goto(dashboard_url, wait_until="domcontentloaded", timeout=UI_TIMEOUT)


def ensure_owner_session(page: Page, context: dict) -> None:
    """Re-login as the isolated account owner after clearing any prior session.

    The runner reuses one browser context across the tests in this subcategory, so the
    notification_flow test's "Log in as" impersonation (it ends logged in as "Staff Admin")
    leaks its POV session into the next test. Each settings test starts by forcing a clean
    owner session so it runs as the account owner — mirrors the proven reviews `fresh_login`
    pattern and the legacy per-scenario `user logged in to automatic account`."""
    base = app_base(context)
    username = context.get("username")
    password = context.get("password")
    if not (username and password):
        raise ValueError("Isolated account username/password missing from context")
    # Best-effort session clear before the fresh login. A Playwright error here (e.g. the
    # login navigation being interrupted by an immediate auth redirect) is non-fatal — the
    # fn_login below is the real owner-session guard — but log it instead of silently
    # swallowing every exception, so a genuine failure is still visible.
    try:
        page.context.clear_cookies()
        page.goto(f"{base}/app/login", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
        page.evaluate("() => { try { localStorage.clear(); sessionStorage.clear(); } catch (e) {} }")
        page.context.clear_cookies()
    except PlaywrightError as exc:
        print(f"  [ensure_owner_session] session clear was interrupted (continuing to login): {exc}")
    fn_login(page, context, username=username, password=password)


def core_base(context: dict) -> str:
    """Core API base (admin + oauth + apps live here). e.g. https://api2.meet2know.com."""
    return resolve_api_base_url(context)


def apigw_base(context: dict) -> str:
    """Notification metadata + send live on the apigw.

    Integration core (api2.meet2know.com) maps to apigw-integration. Allow an env override
    for other environments. Mirrors legacy envs().urls.apis.apigw_url.
    """
    override = os.environ.get("VCITA_APIGW_URL")
    if override:
        return override.rstrip("/")
    core = core_base(context)
    if "meet2know.com" in core:
        return "https://apigw-integration.external.int-eks.vchost.co"
    if "core-" in core and ".external.int-eks.vchost.co" in core:
        # feature-env: core-<name>... -> apigw-<name>...
        return core.replace("https://core-", "https://apigw-", 1)
    raise ValueError(f"Cannot derive apigw url from core base {core!r}; set VCITA_APIGW_URL")


def admin_headers() -> dict:
    token = os.environ.get("VCITA_ADMIN_TOKEN")
    if not token:
        raise ValueError("VCITA_ADMIN_TOKEN is not set; cannot create apps / service tokens")
    return {"Authorization": f"Admin {token}"}


# ===================================================================== #
# Tokens (mirror NotificationsHelper.get_authorization_token + apps.js)
# ===================================================================== #
def directory_token(context: dict) -> str:
    return os.environ.get("VCITA_DIRECTORY_TOKEN") or DEFAULT_DIRECTORY_TOKEN


def directory_uid(context: dict) -> str:
    return os.environ.get("VCITA_DIRECTORY_UID") or DEFAULT_DIRECTORY_UID


def _service_token(context: dict, service_id: str, service_secret: str) -> str:
    """admin POST /oauth/service/token {service_id, service_secret} -> token."""
    response = requests.post(
        f"{core_base(context)}/oauth/service/token",
        json={"service_id": service_id, "service_secret": service_secret},
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    token = ((response.json() or {}).get("data") or {}).get("token")
    if not token:
        raise ValueError(f"oauth/service/token returned no token: {response.text[:200]}")
    return token


def core_internal_app_token(context: dict) -> str:
    service_id = os.environ.get("VCITA_CORE_INTERNAL_SERVICE_ID") or DEFAULT_CORE_INTERNAL_SERVICE_ID
    service_secret = (
        os.environ.get("VCITA_CORE_INTERNAL_SERVICE_SECRET")
        or DEFAULT_CORE_INTERNAL_SERVICE_SECRET
    )
    return _service_token(context, service_id, service_secret)


# ===================================================================== #
# App lifecycle (mirror api/apps.js create_app / refresh_app_token / assign)
# ===================================================================== #
def create_app(context: dict, code: str, name: str) -> dict:
    """admin POST /platform/v1/apps. Name must be 3..25 chars. Returns the app data
    (client_id/client_secret). Records the code in context for teardown."""
    payload = {
        "app_code_name": code,
        "name": name,
        "redirect_uri": "https://noendpoint.no.place",
        "description": {"text": "Created by Automation - notification_center (VCITA2-14247)"},
    }
    response = requests.post(
        f"{core_base(context)}/platform/v1/apps",
        json=payload,
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = (response.json() or {}).get("data") or {}
    if not (data.get("client_id") and data.get("client_secret")):
        raise ValueError(f"App create returned no client creds: {response.text[:200]}")
    context.setdefault("nc_apps", []).append(code)
    return data


def app_service_token(context: dict, app: dict) -> str:
    """Generate an app token from the app's client_id/client_secret
    (legacy refresh_app_token: admin POST /oauth/service/token)."""
    return _service_token(context, app["client_id"], app["client_secret"])


def assign_app_to_account(context: dict, code: str) -> None:
    """admin POST /platform/v1/apps/<code>/assign {business_uid, directoryUid}
    (legacy assign_unassign_app_to_business)."""
    response = requests.post(
        f"{core_base(context)}/platform/v1/apps/{code}/assign",
        json={"business_uid": pivot_uid(context), "directoryUid": directory_uid(context)},
        headers=admin_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()


def delete_app(context: dict, code: str) -> None:
    """Best-effort admin DELETE /platform/v1/apps/<code> (teardown)."""
    try:
        requests.delete(
            f"{core_base(context)}/platform/v1/apps/{code}",
            headers=admin_headers(),
            timeout=REQUEST_TIMEOUT,
        )
    except Exception as exc:  # noqa: BLE001 - teardown best-effort
        print(f"  [teardown] Failed to delete app {code}: {exc}")


# ===================================================================== #
# Notification metadata + send (mirror api/notificationCenter.js, on apigw)
# ===================================================================== #
_APIGW_TRANSIENT_CODES = frozenset({429, 500, 502, 503, 504})
_APIGW_RETRIES = 2
_APIGW_BACKOFF_S = 1.5


def _apigw_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _apigw_request(method: str, url: str, token: str, json_body: dict | None = None):
    """Issue an apigw request, retrying brief server transients (429/5xx).

    The apigw occasionally 5xx's for a moment under load (observed a one-off 500 on the
    notifications send during a 10-iteration stress). This is the same transient class
    account_api.account_request retries; bounded to <=2 retries with linear backoff."""
    last: requests.Response | None = None
    for attempt in range(_APIGW_RETRIES + 1):
        response = requests.request(
            method, url, json=json_body, headers=_apigw_headers(token), timeout=REQUEST_TIMEOUT
        )
        if response.ok:
            return response
        last = response
        if response.status_code in _APIGW_TRANSIENT_CODES and attempt < _APIGW_RETRIES:
            time.sleep(_APIGW_BACKOFF_S * (attempt + 1))
            continue
        break
    last.raise_for_status()  # type: ignore[union-attr]
    return last


def create_notification_template(
    context: dict,
    token: str,
    *,
    code: str,
    notification_type: str,
    channel: dict,
    deep_link: str,
    text: dict,
    show_in_settings: bool | None = None,
) -> dict:
    """apigw POST /business/notificationscenter/v1/notificationsmetadata/.

    Records (code, token) in context for teardown deletion (legacy pushed to
    scenarioContext.notifications)."""
    payload: dict = {
        "notification_code_name": code,
        "notification_type": notification_type,
        "channel": channel,
        "deep_link": deep_link,
        "text": text,
    }
    if show_in_settings is not None:
        payload["show_in_settings"] = show_in_settings
    response = _apigw_request(
        "POST",
        f"{apigw_base(context)}/business/notificationscenter/v1/notificationsmetadata/",
        token,
        payload,
    )
    context.setdefault("nc_templates", []).append((code, token))
    return (response.json() or {}).get("data") or {}


def update_notification_template(context: dict, token: str, code: str, fields: dict) -> dict:
    """apigw PUT /business/notificationscenter/v1/notificationsmetadata/<code>."""
    response = _apigw_request(
        "PUT",
        f"{apigw_base(context)}/business/notificationscenter/v1/notificationsmetadata/{code}",
        token,
        fields,
    )
    return (response.json() or {}).get("data") or {}


def delete_notification_template(context: dict, token: str, code: str) -> None:
    """Best-effort apigw DELETE (teardown). Legacy tolerates a 401 here too."""
    try:
        requests.delete(
            f"{apigw_base(context)}/business/notificationscenter/v1/notificationsmetadata/{code}",
            headers=_apigw_headers(token),
            timeout=REQUEST_TIMEOUT,
        )
    except Exception as exc:  # noqa: BLE001 - teardown best-effort
        print(f"  [teardown] Failed to delete notification template {code}: {exc}")


def send_notification(
    context: dict, token: str, code: str, staff_uid: str, params: dict | None = None
) -> None:
    """apigw POST /business/notificationscenter/v1/notifications/
    {staff_uid, notification_code_name, params}."""
    _apigw_request(
        "POST",
        f"{apigw_base(context)}/business/notificationscenter/v1/notifications/",
        token,
        {"staff_uid": staff_uid, "notification_code_name": code, "params": params},
    )


# ===================================================================== #
# Toolbar badge (top-level POV)
# ===================================================================== #
PANE_CONTENT_MARKER = f"{PANE_ROW}, {PANE_EMPTY}, {PANE_EMPTY_READ_ALL}"


def open_pane(page: Page) -> None:
    """Open the notification pane via the toolbar badge, then wait for the pane overlay AND
    its content to settle (a notification row or an empty state) so the following assertion
    starts from a rendered pane.

    Readiness-then-act-once (no action retry): the badge click is unreliable while the toolbar
    is still rendering its `.v-skeleton-loader` cold-bootstrap placeholders, or while the
    new-account onboarding wizard's `.angular-iframe.isModalMode` overlay covers the badge
    (the two root causes of the prior flakiness). `_wait_toolbar_mounted` waits for the
    deterministic fully-mounted signal — real badge visible AND zero visible skeletons AND that
    modal overlay gone — so the badge is genuinely hittable, then it is clicked exactly once. If
    the pane does not then appear, the test fails (no retry, no fallback)."""
    _wait_toolbar_mounted(page)
    page.locator(BADGE_BUTTON).first.click(timeout=UI_TIMEOUT)
    pane = page.locator(PANE_OVERLAY).first
    pane.wait_for(state="visible", timeout=UI_TIMEOUT)
    pane.locator(PANE_CONTENT_MARKER).first.wait_for(state="visible", timeout=UI_TIMEOUT)


def close_pane(page: Page) -> None:
    """Close the pane with a single deterministic action: click the transparent overlay
    scrim, then wait once for the pane to hide.

    The pane opens as a `.v-menu__content` dropdown with a transparent overlay scrim behind
    it; clicking that scrim dismisses the dropdown (verified live on integration 2026-06-19 at
    the runner's window width). Escape does NOT dismiss this variant — even after a row
    interaction moves focus — so it is not used (no alternate dismissal path for the same
    end-state). Idempotent: if the pane is already closed (e.g. it auto-dismissed on a
    deep-link navigation) this returns without acting."""
    pane = page.locator(PANE_OVERLAY).first
    if not pane.is_visible():
        return
    page.locator(PANE_SCRIM).first.click(timeout=UI_TIMEOUT)
    pane.wait_for(state="hidden", timeout=UI_TIMEOUT)


def _badge_counter_text(page: Page) -> str:
    """Return the visible badge counter text, or '' if not shown.

    The `.v-badge__badge` span is hidden (display:none / not in layout) when the count is
    0, mirroring the legacy noCounterIndicator (`span` with `display: none`)."""
    counter = page.locator(BADGE_COUNTER).first
    if counter.count() == 0 or not counter.is_visible():
        return ""
    return (counter.inner_text() or "").strip()


def _poll_badge_counter(page: Page, expected: str) -> tuple[bool, str]:
    """Bounded poll of the badge counter text until it equals `expected` (eventual
    consistency; see BADGE_POLL_TIMEOUT_S). Returns (matched, last_value)."""
    deadline = time.monotonic() + BADGE_POLL_TIMEOUT_S
    actual = ""
    while True:
        actual = _badge_counter_text(page)
        if actual == expected:
            return True, actual
        if time.monotonic() >= deadline:
            return False, actual
        page.wait_for_timeout(int(BADGE_POLL_INTERVAL_S * 1000))


def assert_badge_counter(page: Page, expected: str) -> None:
    """Assert the badge counter == expected (bounded eventual-consistency poll)."""
    matched, actual = _poll_badge_counter(page, expected)
    if not matched:
        raise AssertionError(f"badge counter expected {expected!r}, got {actual!r}")


def assert_no_badge_counter(page: Page) -> None:
    """Assert the badge counter is not shown (bounded eventual-consistency poll)."""
    matched, actual = _poll_badge_counter(page, "")
    if not matched:
        raise AssertionError(f"badge counter expected hidden, got {actual!r}")


# ===================================================================== #
# Notification pane assertions / actions
# ===================================================================== #
def assert_pane_empty(page: Page) -> None:
    page.locator(PANE_OVERLAY).locator(PANE_EMPTY).first.wait_for(
        state="visible", timeout=UI_TIMEOUT
    )


def assert_pane_read_all_empty(page: Page) -> None:
    page.locator(PANE_OVERLAY).locator(PANE_EMPTY_READ_ALL).first.wait_for(
        state="visible", timeout=UI_TIMEOUT
    )


def _row_by_body(page: Page, body: str):
    """Return the pane row locator whose description == body (legacy finds by body)."""
    return page.locator(PANE_ROW).filter(
        has=page.locator(PANE_DESC, has_text=body)
    ).first


def assert_notification_displayed(
    page: Page, *, title: str, body: str, timestamp: str, status: str
) -> None:
    """Match a pane row by body, then assert title/timestamp/status (legacy `notification displays`)."""
    page.locator(PANE_OVERLAY).locator(PANE_ROW).first.wait_for(
        state="visible", timeout=UI_TIMEOUT
    )
    row = _row_by_body(page, body)
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    expect(row.locator(PANE_TITLE).first).to_have_text(title, timeout=UI_TIMEOUT)
    expect(row.locator(PANE_DESC).first).to_have_text(body, timeout=UI_TIMEOUT)
    expect(row.locator(PANE_TIME).first).to_have_text(timestamp, timeout=UI_TIMEOUT)
    state_locator = PANE_UNREAD if status == "unread" else PANE_READ
    expect(row.locator(state_locator).first).to_be_visible(timeout=UI_TIMEOUT)


def assert_notification_status(page: Page, status: str) -> None:
    """Assert the (single) notification row is read/unread (legacy `notification is`)."""
    locator = PANE_UNREAD if status == "unread" else PANE_READ
    page.locator(PANE_OVERLAY).locator(locator).first.wait_for(
        state="visible", timeout=UI_TIMEOUT
    )


def click_notification(page: Page) -> None:
    page.locator(PANE_ROW).first.click(timeout=UI_TIMEOUT)


def toggle_read_status(page: Page) -> None:
    """Click the blue dot to flip read/unread (legacy clickOnBlueDot)."""
    page.locator(PANE_DOT).first.click(timeout=UI_TIMEOUT)


def toggle_only_unread(page: Page) -> None:
    """Click the show-only-unread switch (legacy clickOnToggle)."""
    page.locator(PANE_ONLY_UNREAD_TOGGLE).first.click(timeout=UI_TIMEOUT)


def mark_all_as_read(page: Page) -> None:
    page.locator(PANE_MARK_ALL).first.click(timeout=UI_TIMEOUT)


def assert_pane_count(page: Page, expected: int) -> None:
    """Assert the pane shows exactly `expected` notification rows. Bounded re-check."""
    pane_body = page.locator(PANE_OVERLAY).locator(PANE_BODY).first
    actual = -1
    for attempt in range(READ_RECHECK_RETRIES + 1):
        actual = pane_body.locator(PANE_ROW).count()
        if actual == expected:
            return
        if attempt < READ_RECHECK_RETRIES:
            page.wait_for_timeout(int(RECHECK_INTERVAL_S * 1000))
    raise AssertionError(f"pane notification count expected {expected}, got {actual}")


def assert_redirected_to_clients(page: Page) -> None:
    """After clicking a notification with deep_link app/clients, the new Clients page loads."""
    page.wait_for_url(f"**{CLIENTS_PATH}**", timeout=UI_TIMEOUT)


# ===================================================================== #
# Notification settings page (inside #vue_iframe_layout)
# ===================================================================== #
def _settings_frame(page: Page):
    """Frame locator for the Vue settings app, nested inside the Angular frame."""
    return page.frame_locator(SETTINGS_OUTER_IFRAME).frame_locator(SETTINGS_IFRAME)


def _wait_settings_loaded(page: Page) -> None:
    """Wait for the settings content through the doubly-nested iframe chain.

    The page is a heavy Angular shell (#angular-iframe) that boots a Vue app
    (#vue_iframe_layout); on a cold POV load the chain can take longer than a single 5s
    wait to mount. Wait in stages, each its own 5s readiness wait tied to a real signal
    (outer frame body -> inner notification container -> a rendered notification name),
    rather than one inflated timeout. The whole sequence is bounded re-checked (<=2 retries)
    to absorb a cold first paint without masking a genuinely missing page."""
    for attempt in range(READ_RECHECK_RETRIES + 1):
        try:
            page.locator(SETTINGS_OUTER_IFRAME).first.wait_for(state="attached", timeout=UI_TIMEOUT)
            frame = _settings_frame(page)
            frame.locator(SETTINGS_CONTAINER).first.wait_for(state="visible", timeout=UI_TIMEOUT)
            frame.locator(SETTINGS_NAME_TITLES).first.wait_for(state="visible", timeout=UI_TIMEOUT)
            return
        except Exception:
            if attempt >= READ_RECHECK_RETRIES:
                raise
            page.wait_for_timeout(int(RECHECK_INTERVAL_S * 1000))


def goto_settings(page: Page, context: dict) -> None:
    """Navigate to the Notification Center settings page and wait for it to render.

    'Refresh the page' in the legacy scenarios = re-navigate here (real navigation,
    not page.reload, which the project forbids)."""
    page.goto(
        f"{app_base(context)}{SETTINGS_PATH}",
        wait_until="domcontentloaded",
        timeout=UI_TIMEOUT,
    )
    _wait_settings_loaded(page)


def _row(page: Page, code: str):
    return _settings_frame(page).locator(f"[data-qa='{code}']").first


def assert_template_in_settings(page: Page, code: str, *, display_name: str, description: str) -> None:
    row = _row(page, code)
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    expect(row.locator(".notification__description--name").first).to_have_text(
        display_name, timeout=UI_TIMEOUT
    )
    expect(row.locator(".notification__description--sub").first).to_have_text(
        description, timeout=UI_TIMEOUT
    )


def assert_template_not_in_settings(page: Page, code: str) -> None:
    """Assert the settings row for `code` is absent (legacy length == 0)."""
    if _settings_frame(page).locator(f"[data-qa='{code}']").count() != 0:
        raise AssertionError(f"notification {code} unexpectedly shows in settings")


def _checkbox_value(page: Page, code: str, channel: str) -> str:
    """Return the channel checkbox state: 'true'/'false' from aria-checked, or 'hidden' if
    the checkbox element is absent (legacy findSettingCheckbox)."""
    checkbox = _settings_frame(page).locator(f"[data-qa='checkbox-{channel}-{code}']")
    if checkbox.count() == 0:
        return "hidden"
    return checkbox.first.get_attribute("aria-checked", timeout=UI_TIMEOUT) or "hidden"


def assert_channel_values(page: Page, code: str, expected: dict) -> None:
    """Assert each channel's checkbox value (legacy `settings for notification ... are`)."""
    for channel, value in expected.items():
        actual = _checkbox_value(page, code, channel)
        assert actual == value, (
            f"channel {channel!r} for {code} expected {value!r}, got {actual!r}"
        )


def set_channel_checkbox(page: Page, code: str, channel: str, *, checked: bool) -> None:
    """Toggle a channel checkbox to the desired state and save (legacy updateCheckboxValue).

    The Vuetify checkbox is a 16x16 <input> whose normal click is intercepted by the ripple
    overlay, so toggle it with a JS-level click (legacy `_clickElementByJS`). Save enables
    only after a change, so it is only clicked when the state actually changes."""
    frame = _settings_frame(page)
    checkbox = frame.locator(f"[data-qa='checkbox-{channel}-{code}']").first
    checkbox.wait_for(state="visible", timeout=UI_TIMEOUT)
    current = (checkbox.get_attribute("aria-checked", timeout=UI_TIMEOUT) or "false") == "true"
    if current == checked:
        return
    checkbox.dispatch_event("click")
    # The checkbox flips aria-checked, which enables the Save button; wait for the new state.
    expect(checkbox).to_have_attribute(
        "aria-checked", "true" if checked else "false", timeout=UI_TIMEOUT
    )
    frame.locator("[data-qa='VcPageHeader-saveButton']").first.click(timeout=UI_TIMEOUT)


def open_notification_settings(page: Page) -> None:
    """Open the pane and click the settings button; assert the settings page loaded
    (legacy `user opens notification settings` + `notification settings are displayed`)."""
    open_pane(page)
    page.locator(PANE_SETTINGS_BUTTON).first.click(timeout=UI_TIMEOUT)
    _wait_settings_loaded(page)


# ===================================================================== #
# Staff impersonation ("Log in as") + logged-staff verification
# ===================================================================== #
def impersonate_staff(page: Page, context: dict, staff_name: str) -> None:
    """Impersonate a staff via the Angular staff list "Log in as" action, then verify the
    logged staff name (legacy `user impersonates staff`).

    Navigates to the staff settings page, opens the target row's actions menu, clicks
    "Log in as", waits for the SSO impersonation to LAND on its own as the new staff, then
    waits for the toolbar to be fully mounted for the subsequent pane open.

    Why we must NOT `page.goto` straight after the click (verified live 2026-06-19, the residual
    late-flow flake): "Log in as" triggers a full SSO re-login that navigates to the dashboard
    as the new staff by itself. A manual `page.goto('/app/dashboard')` issued immediately RACES
    that in-flight SSO redirect — it can reload the dashboard as the ORIGINAL OWNER before the
    impersonation token swap completes. The toolbar then mounts cleanly (badge + no skeleton) as
    the owner, so a toolbar-only readiness wait passes, but the welcome subtitle still shows the
    owner and the per-staff assertion fails. So here we let the redirect settle on its own and
    gate on the impersonated-staff welcome subtitle, which is the deterministic "impersonation
    landed" signal; only then do we wait for toolbar mount."""
    page.goto(f"{app_base(context)}{STAFF_PATH}", wait_until="domcontentloaded", timeout=UI_TIMEOUT)
    frame = page.frame_locator(STAFF_IFRAME)
    row = frame.locator(STAFF_LIST_ITEM).filter(has_text=staff_name).first
    row.wait_for(state="visible", timeout=UI_TIMEOUT)
    # Open the row's actions menu, then click "Log in as" once the menu item is actionable.
    # The menu button is revealed on hover; the menu item is rendered after a short Angular
    # menu animation, so wait for it visible before the single click (no action retry).
    row.hover(timeout=UI_TIMEOUT)
    row.locator(STAFF_ROW_MENU_BTN).first.click(timeout=UI_TIMEOUT)
    login_as = frame.get_by_text(STAFF_LOGIN_AS_TEXT, exact=True).first
    login_as.wait_for(state="visible", timeout=UI_TIMEOUT)
    # Fire the click via dispatch_event, NOT .click() (verified live 2026-06-19): the Angular
    # md-menu item renders `visible` immediately but its overlay/animation blocks pointer-event
    # actionability for ~4.5s, so a real `.click()` spends that whole time in the actionability
    # retry and intermittently exceeds the 5s cap (the residual ~30% flake). A JS-level click
    # fires the ng-click handler directly and instantly — same pattern the settings checkbox uses
    # (legacy `_clickElementByJS`). It is a single click; the SSO landing wait below is the guard.
    login_as.dispatch_event("click")
    # Let the SSO impersonation land on its own (no racing navigation). Wait for the dashboard
    # URL the redirect ends on, then for the impersonated-staff welcome subtitle. Both are read
    # re-checks of a real signal, bounded to <=2 retries (<=~15s) to absorb a slow SSO re-login;
    # each individual wait stays <=5s and we never re-navigate (that would reset the swap).
    _wait_impersonation_landed(page, staff_name)
    # Now that we are confirmed logged in as the new staff, wait for the toolbar to be fully
    # mounted (badge + skeletons gone + no onboarding overlay) before the subsequent pane open.
    _wait_toolbar_mounted(page)


def _wait_impersonation_landed(page: Page, staff_name: str) -> None:
    """Bounded wait for the SSO impersonation to land as `staff_name`.

    "Log in as" triggers a full SSO logout + re-login as the new staff; the redirect lands on
    `/app/dashboard` by itself. Verified live 2026-06-19 that this SSO chain is SLOW and variable:
    the dashboard URL is reached ~4.5-6.5s after the click, which can EXCEED a single 5s wait, so
    the URL wait must be bounded-re-checked. We never re-navigate (a fresh `page.goto` would race
    and reset the token swap and reload as the owner) — we only keep waiting on the in-flight SSO
    redirect. First bounded-wait the dashboard URL (without it, a welcome-subtitle wait would poll
    the still-current staff-settings DOM and burn its whole timeout), then bounded-wait the
    impersonated-staff welcome subtitle. Both are read re-checks of a real signal, bounded to
    <=READ_RECHECK_RETRIES retries (<=~15s); each individual wait stays <=UI_TIMEOUT (5s)."""
    last_exc: PlaywrightError | None = None
    for attempt in range(READ_RECHECK_RETRIES + 1):
        try:
            page.wait_for_url("**/app/dashboard**", timeout=UI_TIMEOUT)
            break
        except PlaywrightError as exc:
            last_exc = exc
    else:
        if last_exc is not None:
            raise last_exc
    welcome = page.locator(DASHBOARD_WELCOME, has_text=f"Welcome back, {staff_name}").first
    last_exc = None
    for attempt in range(READ_RECHECK_RETRIES + 1):
        try:
            welcome.wait_for(state="visible", timeout=UI_TIMEOUT)
            return
        except PlaywrightError as exc:
            last_exc = exc
    if last_exc is not None:
        raise last_exc


def assert_logged_staff(page: Page, staff_name: str) -> None:
    """Confirm the impersonated staff via the dashboard welcome subtitle
    ("Welcome back, <staff>"), legacy getLoggedStaffsName. This is a top-level element that
    verifies the staff without opening the account menu (whose overlay would block the next
    pane open).

    `impersonate_staff` already waits for this exact subtitle (impersonation-landed signal), so
    a single 5s confirmation wait is enough here (timeout = failure)."""
    page.locator(DASHBOARD_WELCOME, has_text=f"Welcome back, {staff_name}").first.wait_for(
        state="visible", timeout=UI_TIMEOUT
    )
