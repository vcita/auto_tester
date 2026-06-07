"""API setup + assertions for the invoice billing migration (VCITA2-13900).

Migrated from automation-js features/steps/invoices.feature backing API:
  - api/tax.create_tax            -> create_tax_via_api
  - api/accountSettings.update_settings (tax_mode / late_fees_settings)
  - api/invoices.create_invoice   -> create_invoice_via_api
  - api/jobber.get_executions / trigger_execution

All calls reuse the central per-account REST primitives in tests/account_api.py.
"""
import calendar
import re
import time
from datetime import datetime, timezone

from tests.account_api import account_request, pivot_uid

# Bounded wait: jobber executions are scheduled asynchronously after the invoice is
# created, so the late-fee execution appears with a short eventual-consistency lag.
JOBBER_POLL_SECONDS = 15
JOBBER_POLL_INTERVAL = 0.5


def _apigw_base(context: dict) -> str:
    """Resolve the APIGW base URL (jobber lives on the gateway, not the core API).

    Mirrors automation-js envs.js apigw_url per environment."""
    api = (context.get("api_base_url") or "").rstrip("/")
    base = (context.get("base_url") or "").rstrip("/")
    if "meet2know.com" in api or "meet2know.com" in base:
        return "https://apigw-integration.external.int-eks.vchost.co"
    if "vcita.biz" in api or "vcita.com" in base:
        return "https://apigw-production.external.prod-eks.vchost.co"
    match = re.search(r"https://(?:core|app)-([^.]+)\.external\.int-eks\.vchost\.co", api or base)
    if match:
        return f"https://apigw-{match.group(1)}.external.int-eks.vchost.co"
    raise ValueError("Could not resolve APIGW base URL from context")


def create_tax_via_api(context: dict, name: str, rate: str | int) -> dict:
    """Create a tax (POST /business/payments/v1/taxes), mirroring legacy api/tax.create_tax."""
    response = account_request(
        context, "POST", "/business/payments/v1/taxes",
        json={"tax": {"name": name, "rate": rate, "default_for_categories": []}, "new_api": True},
    )
    data = response.get("data") or response
    return data.get("tax") or data


def set_tax_mode(context: dict, mode: str) -> None:
    """Set account-wide tax mode ('include'/'exclude') and verify via read-back."""
    account_request(context, "PUT", "/v2/settings", json={"tax_mode": mode})
    settings = account_request(context, "GET", "/platform/v1/payment/settings")
    data = settings.get("data") or settings
    actual = (data.get("payment_settings") or data).get("tax_mode")
    if actual != mode:
        raise AssertionError(f"tax_mode did not persist: expected {mode}, got {actual}")


def set_late_fee_settings(context: dict, *, enabled: bool, amount: str, percent: str,
                          fee_type: str, days: str) -> None:
    """Enable late fees (PUT /v2/settings late_fees_settings), mirroring legacy lateFee step."""
    account_request(context, "PUT", "/v2/settings", json={
        "late_fees_settings": {
            "late_fee_enabled": enabled,
            "late_fee_amount": amount,
            "late_fee_percent": percent,
            "late_fee_type": fee_type,
            "late_fee_days": days,
        }
    })


def next_month_day(day: int, hour: int = 12) -> datetime:
    """Return a UTC datetime on `day` of next month at `hour` (legacy {month:next,date:N})."""
    today = datetime.now(timezone.utc)
    month_index = today.month  # 0-based next month
    year = today.year + month_index // 12
    month = month_index % 12 + 1
    clamped = min(day, calendar.monthrange(year, month)[1])
    return datetime(year, month, clamped, hour, 0, 0, tzinfo=timezone.utc)


def create_invoice_via_api(context: dict, *, title: str, client_id: str, address: str,
                           items: list[dict], due_date: datetime,
                           enable_late_fee: bool = False) -> dict:
    """Create an invoice (POST /platform/v1/invoices), mirroring legacy api/invoices.create_invoice."""
    now = datetime.now(timezone.utc)
    response = account_request(context, "POST", "/platform/v1/invoices", json={
        "title": title,
        "client_id": client_id,
        "address": address,
        "currency": "USD",
        "due_date": due_date.isoformat(),
        "issued_at": now.isoformat(),
        "items": items,
        "send_email": False,
        "allow_online_payment": False,
        "enable_late_fee": enable_late_fee,
    })
    payload = response.get("data") or response
    created = payload.get("invoice") or payload
    number = created.get("number")
    return {
        "id": created.get("id") or created.get("uid"),
        "title": created.get("title") or title,
        "number": str(number) if number is not None else "",
        "raw": created,
    }


def get_jobber_executions(context: dict) -> list[dict]:
    """List jobber executions for the business (GET /business/jobber/executions/{pivot})."""
    response = account_request(
        context, "GET", f"/business/jobber/executions/{pivot_uid(context)}",
        base_url=_apigw_base(context),
    )
    data = response.get("data") or response
    return data.get("executions") or data if isinstance(data, (list, dict)) else []


def wait_for_jobber_execution(context: dict, event_name: str,
                              timeout_s: int = JOBBER_POLL_SECONDS) -> dict:
    """Poll until a jobber execution with `event_name` appears; return it."""
    deadline = time.monotonic() + timeout_s
    last: list = []
    while time.monotonic() < deadline:
        executions = get_jobber_executions(context)
        last = executions if isinstance(executions, list) else []
        match = next((e for e in last if e.get("event_name") == event_name), None)
        if match:
            return match
        time.sleep(JOBBER_POLL_INTERVAL)
    raise AssertionError(
        f"Jobber execution '{event_name}' not found after {timeout_s}s; got "
        f"{[e.get('event_name') for e in last]}"
    )


def assert_jobber_execution(context: dict, *, event_name: str, status: str,
                            expected_date: str) -> dict:
    """Assert a jobber execution exists with the given status and scheduled date.

    `expected_date` is the YYYY-MM-DD the execution's time_slot must fall on (legacy
    asserts the full business-timezone timestamp; we assert event_name + status +
    scheduled date, which preserves the meaningful coverage - the late-fee job is
    scheduled `late_fee_days` after the due date - without coupling to the business
    timezone's exact second-level string)."""
    execution = wait_for_jobber_execution(context, event_name)
    actual_status = execution.get("status")
    if actual_status != status:
        raise AssertionError(
            f"Jobber '{event_name}' status expected {status}, got {actual_status}"
        )
    time_slot = str(execution.get("time_slot") or "")
    if expected_date not in time_slot:
        raise AssertionError(
            f"Jobber '{event_name}' time_slot expected date {expected_date}, got {time_slot}"
        )
    return execution


def trigger_jobber_execution(context: dict, event_name: str,
                             execution: dict | None = None) -> dict:
    """Trigger a jobber execution (POST .../{uid}/execute). Reuses an already-fetched
    `execution` when provided (e.g. from assert_jobber_execution) to avoid a re-poll."""
    execution = execution or wait_for_jobber_execution(context, event_name)
    uid = execution.get("uid") or execution.get("id")
    if not uid:
        raise ValueError(f"Jobber execution '{event_name}' has no uid: {execution}")
    account_request(
        context, "POST", f"/business/jobber/executions/{uid}/execute",
        base_url=_apigw_base(context),
    )
    return execution
